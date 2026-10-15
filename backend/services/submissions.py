# ruff: noqa: EXE002
import re

from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core import PERMISSIONS, db, is_staff, now, oid
from learning import assert_unlocked

OPEN_STATUSES = ["draft", "submitted", "returned"]
STAFF_STATUSES = ["submitted", "in_review", "graded", "returned"]


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
        "history": [_hist("draft", user)], "created_at": now(), "updated_at": now(), "submitted_at": None,
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
    return await db.submissions.find(query).sort([("block_id", 1), ("attempt", -1)]).to_list(1000)


async def save_draft(block_id: str, answer: dict, user: dict) -> dict:
    block, node = await _submittable_block(block_id, is_staff(user))
    await assert_unlocked(node, user)
    submission = await _open_attempt(user, block, node)
    result = await db.submissions.update_one(
        {"_id": submission["_id"], "status": {"$in": OPEN_STATUSES}},
        {"$set": {"answer": answer, "updated_at": now()}},
    )
    if not result.matched_count:
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    return await db.submissions.find_one({"_id": submission["_id"]})


async def submit_answer(block_id: str, answer: dict, user: dict) -> dict:
    block, node = await _submittable_block(block_id, is_staff(user))
    await assert_unlocked(node, user)
    if not any(str(value).strip() for value in answer.values()):
        raise HTTPException(status_code=400, detail="A resposta está vazia")
    submission = await _open_attempt(user, block, node)
    result = await db.submissions.update_one(
        {"_id": submission["_id"], "status": {"$in": OPEN_STATUSES}},
        {
            "$set": {"answer": answer, "status": "submitted", "submitted_at": now(), "updated_at": now()},
            "$push": {"history": _hist("submitted", user)},
        },
    )
    if not result.matched_count:
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    await db.learning_events.insert_one({
        "user_id": user["id"], "track_id": block["track_id"], "node_id": block["node_id"],
        "block_id": block_id, "type": "submission:submitted", "data": {}, "at": now(),
    })
    await db.progress.update_one(
        {"user_id": user["id"], "node_id": block["node_id"], "block_id": block_id},
        {
            "$set": {"status": "in_progress", "track_id": block["track_id"], "scope": "block", "updated_at": now()},
            "$setOnInsert": {"started_at": now()},
        },
        upsert=True,
    )
    return await db.submissions.find_one({"_id": submission["_id"]})


async def list_submissions(
    track_id: str | None, node_id: str | None, user_id: str | None, block_type: str | None,
    status: str | None, query_text: str | None,
) -> dict:
    query = {"status": {"$in": STAFF_STATUSES}}
    for key, value in (("track_id", track_id), ("node_id", node_id), ("user_id", user_id), ("block_type", block_type)):
        if value:
            query[key] = value
    base = {key: value for key, value in query.items() if key != "status"}
    if status:
        query["status"] = status
    if query_text:
        query["$or"] = [
            {"user_name": {"$regex": re.escape(query_text), "$options": "i"}},
            {"node_title": {"$regex": re.escape(query_text), "$options": "i"}},
        ]
    items = await db.submissions.find(query, {"history": 0}).sort("submitted_at", 1).to_list(500)
    counts = await db.submissions.aggregate([
        {"$match": base}, {"$group": {"_id": "$status", "n": {"$sum": 1}}}
    ]).to_list(20)
    return {"items": items, "counts": {count["_id"]: count["n"] for count in counts}}


async def get_submission(submission_id: str, user: dict) -> dict:
    submission = await db.submissions.find_one({"_id": oid(submission_id)})
    staff = "submissions.grade" in PERMISSIONS.get(user["role"], set())
    if not submission or (submission["user_id"] != user["id"] and not staff):
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    block = await db.content_blocks.find_one({"_id": oid(submission["block_id"])})
    attempts = await db.submissions.find(
        {"user_id": submission["user_id"], "block_id": submission["block_id"]}, {"history": 0}
    ).sort("attempt", -1).to_list(50)
    return {"submission": submission, "block": block, "attempts": attempts}


async def claim_submission(submission_id: str, user: dict) -> dict:
    submission = await db.submissions.find_one_and_update(
        {"_id": oid(submission_id), "status": "submitted"},
        {
            "$set": {"status": "in_review", "reviewer_id": user["id"], "reviewer_name": user.get("name", ""), "updated_at": now()},
            "$push": {"history": _hist("in_review", user)},
        },
        return_document=ReturnDocument.AFTER,
    )
    if not submission:
        raise HTTPException(status_code=409, detail="Esta submissão já está em correção ou não está mais aguardando")
    return submission


async def grade_submission(submission_id: str, data: dict, user: dict) -> dict:
    result_name = data["result"]
    if result_name not in ("approved", "rejected", "returned"):
        raise HTTPException(status_code=400, detail="Resultado inválido")
    submission = await db.submissions.find_one({"_id": oid(submission_id)})
    if not submission or submission["status"] not in ("submitted", "in_review"):
        raise HTTPException(status_code=409, detail="Esta submissão não está aguardando correção")
    if result_name != "approved" and not data["feedback"].strip():
        raise HTTPException(status_code=400, detail="Escreva um feedback ao reprovar ou devolver")
    status = "returned" if result_name == "returned" else "graded"
    grading = {**data, "graded_by": user["id"], "graded_by_name": user.get("name", ""), "graded_at": now()}
    update = await db.submissions.update_one(
        {"_id": submission["_id"], "status": {"$in": ["submitted", "in_review"]}},
        {
            "$set": {"status": status, "grading": grading, "updated_at": now()},
            "$push": {"history": {**_hist(status, user), "result": result_name}},
        },
    )
    if not update.modified_count:
        raise HTTPException(status_code=409, detail="Outra pessoa corrigiu esta submissão ao mesmo tempo")
    if result_name == "approved":
        await db.progress.update_one(
            {"user_id": submission["user_id"], "node_id": submission["node_id"], "block_id": submission["block_id"]},
            {
                "$set": {"status": "completed", "completed_at": now(), "updated_at": now(),
                         "track_id": submission["track_id"], "scope": "block"}
            },
            upsert=True,
        )
    await db.learning_events.insert_one({
        "user_id": submission["user_id"], "track_id": submission["track_id"], "node_id": submission["node_id"],
        "block_id": submission["block_id"], "type": f"submission:{result_name}", "data": {}, "at": now(),
    })
    return await db.submissions.find_one({"_id": submission["_id"]})
