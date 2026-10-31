# ruff: noqa: EXE002
import json
import re
from hashlib import sha256
from typing import Any

from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core_utils import now
from database import db
from integrity import can_view_node
from learning import assert_unlocked
from permissions import has_permission, is_staff
from serialization import oid
from services.learning_scopes import (
    GRADE_SUBMISSIONS,
    READ_SUBMISSIONS,
    authorized_track_ids,
    require_track_scope,
)
from services.nodes import _student_block
from services.progress import set_progress

OPEN_STATUSES = ["draft", "submitted", "returned"]
STAFF_STATUSES = ["submitted", "in_review", "graded", "returned"]
_SUBMISSION_OPERATION_KEY = re.compile(r"[A-Za-z0-9._:\-]{8,128}\Z")
_STUDENT_SUBMISSION_FIELDS = {
    "user_id", "user_name", "track_id", "node_id", "node_title", "block_id", "block_type",
    "block_title", "attempt", "status", "answer", "grading", "history", "reviewer_name",
    "orphaned", "created_at", "updated_at", "submitted_at", "activity_version",
}
_REVIEWER_SUBMISSION_FIELDS = _STUDENT_SUBMISSION_FIELDS | {"grading", "history"}
_REVIEWER_BLOCK_FIELDS = {
    "_id", "node_id", "track_id", "type", "title", "order", "status", "schema_version", "data",
}
_REVIEWER_BLOCK_DATA_FIELDS = {
    "prompt", "question", "options", "instructions", "starter_code", "language", "acceptance",
    "grading", "criteria", "rubric", "answer", "reference_answer", "solution", "instructor_notes",
    "allow_resubmit", "activity_schema_version",
}


def _activity_version(block: dict) -> str:
    payload = {"type": block.get("type"), "title": block.get("title"), "data": block.get("data", {}),
               "schema_version": block.get("schema_version", 1)}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _student_submission(document: dict) -> dict:
    """Project only explicitly supported fields into student-facing responses."""
    safe = {key: document[key] for key in _STUDENT_SUBMISSION_FIELDS if key in document}
    grading = safe.get("grading")
    if isinstance(grading, dict):
        safe["grading"] = {key: value for key, value in grading.items() if key in {
            "result", "feedback", "score", "graded_by_name", "graded_at",
        }}
    history = safe.get("history")
    if isinstance(history, list):
        safe["history"] = [
            {key: value for key, value in item.items() if key in {"status", "at", "by_name", "result"}}
            for item in history if isinstance(item, dict)
        ]
    safe.pop("_id", None)
    safe["id"] = str(document.get("_id", document.get("id", "")))
    return safe


def _reviewer_submission(document: dict) -> dict:
    """Project a scoped reviewer response without returning system-only fields."""
    safe = {key: document[key] for key in _REVIEWER_SUBMISSION_FIELDS if key in document}
    safe["id"] = str(document.get("_id", document.get("id", "")))
    history = safe.get("history")
    if isinstance(history, list):
        safe["history"] = [
            {key: item[key] for key in ("status", "at", "by_name", "result") if key in item}
            for item in history if isinstance(item, dict)
        ]
    grading = safe.get("grading")
    if isinstance(grading, dict):
        safe["grading"] = {key: value for key, value in grading.items() if key in {
            "result", "feedback", "criteria", "score", "graded_by_name", "graded_at",
        }}
    return safe


def _reviewer_block(block: dict) -> dict:
    """Allowlist the assessment fields needed by an authorized reviewer."""
    safe = {key: block[key] for key in _REVIEWER_BLOCK_FIELDS if key in block}
    data = block.get("data")
    if isinstance(data, dict):
        safe["data"] = {key: value for key, value in data.items() if key in _REVIEWER_BLOCK_DATA_FIELDS}
    return safe


def _grading_context(block: dict[str, Any]) -> dict[str, Any]:
    raw_data = block.get("data")
    data: dict[str, Any] = raw_data if isinstance(raw_data, dict) else {}
    return {key: data[key] for key in (
        "criteria", "rubric", "answer", "reference_answer", "solution", "instructor_notes",
    ) if key in data}


async def _sync_progress(submission: dict[str, Any]) -> dict[str, Any]:
    """Project a durable submission state to progress with a replayable operation ID."""
    current = await db.submissions.find_one({"_id": submission["_id"]})
    if not current or current.get("progress_projection_status") != "pending":
        return current or submission
    owner = await db.users.find_one({"_id": oid(current["user_id"])}, {"role": 1})
    if not owner:
        raise HTTPException(status_code=503, detail="O progresso aguarda a recuperação da conta do aluno.")
    approved = current.get("status") == "graded" and (current.get("grading") or {}).get("result") == "approved"
    projection_revision = current.get("progress_projection_revision", 1)
    result_name = (current.get("grading") or {}).get("result") if current.get("status") == "graded" else None
    event_type = f"submission:{result_name}" if result_name else f"submission:{current['status']}"
    event_id = f"submission:{current['_id']}:{event_type}:{projection_revision}"
    await db.learning_events.update_one({"_id": event_id}, {"$setOnInsert": {
        "_id": event_id, "user_id": current["user_id"], "track_id": current["track_id"],
        "node_id": current["node_id"], "block_id": current["block_id"],
        "type": event_type, "data": {}, "at": now(),
    }}, upsert=True)
    await set_progress({
        "node_id": current["node_id"],
        "block_id": current["block_id"],
        "status": "completed" if approved else "in_progress",
        "data": {"submission_id": str(current["_id"]), "review_state": "approved" if approved else current["status"]},
        "operation_id": f"submission:{current['_id']}:{projection_revision}",
    }, {"id": current["user_id"], "role": owner.get("role", "student")})
    await db.submissions.update_one({
        "_id": current["_id"], "progress_projection_revision": projection_revision,
    }, {"$set": {"progress_projection_status": "complete", "progress_projected_at": now()}})
    saved = await db.submissions.find_one({"_id": current["_id"]})
    return saved if saved is not None else current


async def _submittable_block(block_id: str, staff_ok: bool = False):
    block = await db.content_blocks.find_one({"_id": oid(block_id)})
    if not block:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    if block.get("status") != "published" and not staff_ok:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    block_type = await db.block_types.find_one({"key": block["type"]})
    if not block_type or "submission" not in (block_type.get("capabilities") or []):
        raise HTTPException(status_code=400, detail="Este bloco não aceita respostas")
    node = await db.nodes.find_one({"_id": oid(block["node_id"])})
    return block, node


async def _current(user_id: str, block_id: str):
    return await db.submissions.find_one({"user_id": user_id, "block_id": block_id}, sort=[("attempt", -1)])


def submission_revision_filter(submission: dict) -> dict:
    return {"revision": submission["revision"]} if "revision" in submission else {"revision": {"$exists": False}}


def _hist(status: str, user: dict) -> dict:
    return {"status": status, "at": now(), "by": user["id"], "by_name": user.get("name", "")}


async def _open_attempt(user: dict, block: dict, node: dict):
    current = await _current(user["id"], str(block["_id"]))
    if current and current["status"] in OPEN_STATUSES:
        return current
    if current and current["status"] == "in_review":
        raise HTTPException(status_code=409, detail="Sua resposta está em correção e não pode ser editada")
    if current and current["status"] == "graded":
        approved = (current.get("grading") or {}).get("result") == "approved"
        if approved or not block.get("data", {}).get("allow_resubmit", True):
            raise HTTPException(status_code=409, detail="Este exercício já foi corrigido e não aceita nova tentativa")
    document = {
        "user_id": user["id"], "user_name": user.get("name", ""), "track_id": block["track_id"],
        "node_id": block["node_id"], "node_title": node["title"] if node else "", "block_id": str(block["_id"]),
        "block_type": block["type"], "block_title": block.get("title", ""),
        "attempt": current["attempt"] + 1 if current else 1, "status": "draft", "answer": {}, "grading": None,
        "history": [_hist("draft", user)], "answer_history": [], "grading_history": [],
        "revision": 0,
        "activity_version": _activity_version(block), "grading_context": _grading_context(block),
        "progress_projection_status": "complete", "progress_projection_revision": 0,
        "created_at": now(), "updated_at": now(), "submitted_at": None,
    }
    try:
        result = await db.submissions.insert_one(document)
    except DuplicateKeyError:
        return await _current(user["id"], str(block["_id"]))
    document["_id"] = result.inserted_id
    return document


async def my_submissions(node_id: str | None, user: dict) -> list[dict]:
    query = {"user_id": user["id"], "orphaned": {"$ne": True}}
    if node_id:
        query["node_id"] = node_id
    items = await db.submissions.find(query).sort([("block_id", 1), ("attempt", -1)]).to_list(1000)
    for item in items:
        if item.get("progress_projection_status") == "pending":
            await _sync_progress(item)
    items = await db.submissions.find(query).sort([("block_id", 1), ("attempt", -1)]).to_list(1000)
    return [_student_submission(item) for item in items]


async def save_draft(block_id: str, answer: dict, user: dict) -> dict:
    block, node = await _submittable_block(block_id, is_staff(user))
    await assert_unlocked(node, user)
    submission = await _open_attempt(user, block, node)
    update_document = {"$set": {"answer": answer, "updated_at": now()}}
    if submission.get("status") == "returned":
        update_document["$push"] = {"answer_history": {
            "answer": submission.get("answer", {}), "grading": submission.get("grading"),
            "at": now(), "reason": "returned_answer_revised",
        }}
    update_document["$inc"] = {"revision": 1}
    revision_filter = ({"revision": submission["revision"]} if "revision" in submission
                       else {"revision": {"$exists": False}})
    result = await db.submissions.update_one(
        {"_id": submission["_id"], "status": {"$in": OPEN_STATUSES}, **revision_filter}, update_document,
    )
    if not result.matched_count:
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    saved = await db.submissions.find_one({"_id": submission["_id"]})
    if saved is None:
        raise HTTPException(status_code=503, detail="O rascunho aguarda reconciliação.")
    return _student_submission(saved)


async def submit_answer(block_id: str, answer: dict, user: dict, operation_id: str | None = None) -> dict:
    request_fingerprint = sha256(json.dumps(
        {"block_id": block_id, "answer": answer}, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    if operation_id is not None and not _SUBMISSION_OPERATION_KEY.fullmatch(operation_id):
        raise HTTPException(status_code=422, detail="Idempotency-Key inválida")
    block, node = await _submittable_block(block_id, is_staff(user))
    await assert_unlocked(node, user)
    if not any(str(value).strip() for value in answer.values()):
        raise HTTPException(status_code=400, detail="A resposta está vazia")
    if operation_id:
        prior = await db.submissions.find_one({
            "user_id": user["id"], "submission_operations.id": operation_id,
        })
        if prior:
            operation: dict[str, Any] = next((item for item in prior.get("submission_operations", [])
                                              if item.get("id") == operation_id), {})
            if operation.get("fingerprint") != request_fingerprint:
                raise HTTPException(status_code=409, detail="Chave de operação reutilizada com outros dados")
            if prior.get("answer") != answer:
                raise HTTPException(status_code=409, detail="A resposta foi alterada após esta operação")
            if prior.get("progress_projection_status") == "pending":
                prior = await _sync_progress(prior)
            return _student_submission(prior)
    submission = await _open_attempt(user, block, node)
    update_document = {
        "$set": {
            "answer": answer, "status": "submitted", "submitted_at": now(), "updated_at": now(),
            "progress_projection_status": "pending",
        },
        "$inc": {"progress_projection_revision": 1, "revision": 1},
        "$push": {"history": _hist("submitted", user)},
    }
    if operation_id:
        update_document["$push"]["submission_operations"] = {
            "id": operation_id, "fingerprint": request_fingerprint, "at": now(),
        }
    if submission.get("status") == "returned":
        update_document["$push"]["answer_history"] = {
            "answer": submission.get("answer", {}), "grading": submission.get("grading"),
            "at": now(), "reason": "returned_answer_resubmitted",
        }
        if submission.get("grading"):
            update_document["$push"]["grading_history"] = submission["grading"]
        update_document["$unset"] = {"grading": ""}
    revision_filter = ({"revision": submission["revision"]} if "revision" in submission
                       else {"revision": {"$exists": False}})
    result = await db.submissions.update_one(
        {"_id": submission["_id"], "status": {"$in": OPEN_STATUSES}, **revision_filter}, update_document,
    )
    if not result.matched_count:
        if operation_id:
            prior = await db.submissions.find_one({
                "user_id": user["id"], "submission_operations.id": operation_id,
            })
            if prior:
                saved_operation: dict[str, Any] = next((item for item in prior.get("submission_operations", [])
                                                        if item.get("id") == operation_id), {})
                if saved_operation.get("fingerprint") == request_fingerprint and prior.get("answer") == answer:
                    return _student_submission(prior)
                raise HTTPException(status_code=409, detail="Chave de operação reutilizada com outros dados")
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    saved = await db.submissions.find_one({"_id": submission["_id"]})
    if saved is None:
        raise HTTPException(status_code=503, detail="A submissão aguarda reconciliação.")
    saved = await _sync_progress(saved)
    return _student_submission(saved)


async def list_submissions(
    track_id: str | None, node_id: str | None, user_id: str | None, block_type: str | None,
    status: str | None, query_text: str | None, user: dict, limit: int = 500, skip: int = 0,
) -> dict:
    track_ids = await authorized_track_ids(user, READ_SUBMISSIONS)
    if not track_ids:
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    query: dict[str, Any] = {"status": {"$in": STAFF_STATUSES}, "track_id": {"$in": track_ids}}
    for key, value in (("track_id", track_id), ("node_id", node_id), ("user_id", user_id), ("block_type", block_type)):
        if value:
            if key == "track_id" and value not in track_ids:
                return {"items": [], "counts": {}}
            query[key] = value
    base: dict[str, Any] = {key: value for key, value in query.items() if key != "status"}
    if status:
        query["status"] = status
    if query_text:
        query["$or"] = [
            {"user_name": {"$regex": re.escape(query_text), "$options": "i"}},
            {"node_title": {"$regex": re.escape(query_text), "$options": "i"}},
        ]
    page_size = min(max(limit, 1), 500)
    items = await db.submissions.find(query, {"history": 0}).sort("submitted_at", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    cursor = await db.submissions.aggregate([
        {"$match": base}, {"$group": {"_id": "$status", "n": {"$sum": 1}}}
    ])
    counts = await cursor.to_list(20)
    return {
        "items": [_reviewer_submission(item) for item in items],
        "counts": {count["_id"]: count["n"] for count in counts},
    }


async def get_submission(submission_id: str, user: dict) -> dict:
    submission = await db.submissions.find_one({"_id": oid(submission_id)})
    if not submission:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    student_owner = submission["user_id"] == user["id"]
    staff = has_permission(user, "submissions.grade")
    if staff:
        await require_track_scope(user, submission["track_id"], READ_SUBMISSIONS)
    if not student_owner and not staff:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    if student_owner and submission.get("progress_projection_status") == "pending":
        submission = await _sync_progress(submission)
    block = await db.content_blocks.find_one({"_id": oid(submission["block_id"])})
    if block and not staff:
        node = await db.nodes.find_one({"_id": oid(block["node_id"])})
        if not node or not await can_view_node(node, user):
            block = None
        else:
            block = _student_block(block)
    attempts = await db.submissions.find(
        {"user_id": submission["user_id"], "block_id": submission["block_id"]}, {"history": 0}
    ).sort("attempt", -1).to_list(50)
    if not staff:
        submission = _student_submission(submission)
        attempts = [_student_submission(item) for item in attempts]
    if staff:
        submission = _reviewer_submission(submission)
        attempts = [_reviewer_submission(item) for item in attempts]
        block = _reviewer_block(block) if block else None
    return {"submission": submission, "block": block, "attempts": attempts}


async def claim_submission(submission_id: str, user: dict) -> dict:
    existing = await db.submissions.find_one({"_id": oid(submission_id)}, {"track_id": 1, "revision": 1})
    if not existing:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    await require_track_scope(user, existing["track_id"], GRADE_SUBMISSIONS)
    submission = await db.submissions.find_one_and_update(
        {
            "_id": oid(submission_id), "status": "submitted", **submission_revision_filter(existing),
        },
        {
            "$set": {"status": "in_review", "reviewer_id": user["id"], "reviewer_name": user.get("name", ""), "updated_at": now()},
            "$push": {"history": _hist("in_review", user)},
            "$inc": {"revision": 1},
        },
        return_document=ReturnDocument.AFTER,
    )
    if not submission:
        raise HTTPException(status_code=409, detail="Esta submissão já está em correção ou não está mais aguardando")
    return _reviewer_submission(submission)


async def grade_submission(submission_id: str, data: dict, user: dict) -> dict:
    result_name = data["result"]
    if result_name not in ("approved", "rejected", "returned"):
        raise HTTPException(status_code=400, detail="Resultado inválido")
    submission = await db.submissions.find_one({"_id": oid(submission_id)})
    if not submission:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    await require_track_scope(user, submission["track_id"], GRADE_SUBMISSIONS)
    if submission["status"] not in ("submitted", "in_review"):
        raise HTTPException(status_code=409, detail="Esta submissão não está aguardando correção")
    if result_name != "approved" and not data["feedback"].strip():
        raise HTTPException(status_code=400, detail="Escreva um feedback ao reprovar ou devolver")
    status = "returned" if result_name == "returned" else "graded"
    grading = {**data, "graded_by": user["id"], "graded_by_name": user.get("name", ""), "graded_at": now()}
    next_projection_revision = submission.get("progress_projection_revision", 0) + 1
    update = await db.submissions.update_one(
        {
            "_id": submission["_id"], "status": {"$in": ["submitted", "in_review"]},
            **submission_revision_filter(submission),
        },
        {
            "$set": {
                "status": status, "grading": grading, "updated_at": now(),
                "progress_projection_status": "pending",
                "progress_projection_revision": next_projection_revision,
            },
            "$push": {"history": {**_hist(status, user), "result": result_name}},
            "$inc": {"revision": 1},
        },
    )
    if not update.modified_count:
        raise HTTPException(status_code=409, detail="Outra pessoa corrigiu esta submissão ao mesmo tempo")
    saved = await db.submissions.find_one({"_id": submission["_id"]})
    if saved is None:
        raise HTTPException(status_code=503, detail="A correção aguarda reconciliação.")
    return _reviewer_submission(await _sync_progress(saved))
