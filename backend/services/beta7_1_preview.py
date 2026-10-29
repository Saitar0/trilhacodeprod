"""Isolated, fail-closed preview repository for Beta 7.1.

This module is imported only by the explicit test-support ASGI launcher. It
uses a dedicated Mongo database namespace and never writes to learning or
editorial collections. It is not registered by ``server:app``.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError

from curriculum_contract.experimental_beta_first_phase_converter import ConvertedUnit
from database import client
from settings import settings

preview_db = client[f"{settings.db_name}_beta7_1_preview"]
_IDEMPOTENCY_KEY = re.compile(r"[A-Za-z0-9._:-]{8,128}\Z")
_REVIEW_OPERATION = "preview.project.review"
_READ_OPERATION = "preview.curriculum.read"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _safe_idempotency(value: str | None) -> str:
    if not isinstance(value, str) or not _IDEMPOTENCY_KEY.fullmatch(value):
        raise HTTPException(status_code=422, detail="Idempotency-Key inválida")
    return value


def _json_unit(document: dict[str, Any]) -> ConvertedUnit:
    payload = {key: value for key, value in document.items() if key not in {"_id", "batch_id", "unit_id"}}
    try:
        return ConvertedUnit.model_validate(payload)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Conteúdo da prévia não passou na validação") from exc


async def require_preview(batch_id: str, user: dict[str, Any], operation: str = _READ_OPERATION) -> dict:
    """Require an active synthetic grant and a prepared batch owned by this run."""
    if not isinstance(user.get("id"), str) or not user["id"]:
        raise HTTPException(status_code=401, detail="Não autenticado")
    batch = await preview_db.preview_batches.find_one({
        "_id": batch_id,
        "state": "PREPARED",
        "run_id": settings.db_name.removeprefix("beta7_1_"),
    })
    if batch is None:
        raise HTTPException(status_code=404, detail="Prévia não encontrada")
    grant = await preview_db.preview_grants.find_one({
        "batch_id": batch_id,
        "user_id": user["id"],
        "state": "active",
        "operations": operation,
    })
    if grant is None:
        raise HTTPException(status_code=404, detail="Prévia não encontrada")
    return batch


async def require_reviewer(batch_id: str, user: dict[str, Any]) -> dict:
    from constants import PERMISSIONS

    if "submissions.grade" not in PERMISSIONS.get(user.get("role", ""), set()):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    return await require_preview(batch_id, user, _REVIEW_OPERATION)


async def unit_for(batch_id: str, unit_id: str) -> ConvertedUnit:
    document = await preview_db.preview_units.find_one({"batch_id": batch_id, "unit_id": unit_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    return _json_unit(document)


def public_unit(unit: ConvertedUnit) -> dict[str, Any]:
    """Closed allowlist: never serialize the full authoring model to students."""
    criterion = unit.completion_criterion
    return {
        "id": unit.provenance.source_id,
        "title": unit.title,
        "module_id": unit.module_id,
        "module_order": unit.module_order,
        "unit_order": unit.unit_order,
        "objective": unit.objective,
        "version": unit.provenance.source_sha256,
        "topics": [{
            "id": topic.ref,
            "title": topic.title,
            "order": topic.order,
            "segments": [{
                "id": segment.ref,
                "title": segment.source_heading,
                "order": segment.order,
                "body": segment.markdown_body,
            } for segment in topic.segments],
        } for topic in unit.topics],
        "summary": unit.summary,
        "references": [{
            "id": item.ref,
            "order": item.order,
            "title": item.title,
            "description": item.description,
            "url": item.url,
        } for item in unit.references],
        "quizzes": [{
            "id": question.ref,
            "order": question.order,
            "version": unit.provenance.source_sha256,
            "prompt": question.prompt,
            "options": [{"id": option.id, "label": option.label} for option in question.options],
        } for question in unit.quiz_questions],
        "exercises": [{
            "id": exercise.ref,
            "order": exercise.order,
            "title": exercise.title,
            "prompt": exercise.student_prompt,
            "version": exercise.source_sha256,
        } for exercise in unit.manual_exercises],
        "criterion": ({
            "source_text": criterion.source_text,
            "state": "REQUIRES_PEDAGOGICAL_DECISION",
            "automated": False,
        } if criterion else {"source_text": None, "state": "SOURCE_ABSENT", "automated": False}),
        "relations": [{
            "kind": relation.source_kind,
            "target": relation.target_path,
            "label": relation.display_label,
            "enforced": False,
        } for relation in unit.relations],
        "status": "PRIVATE_EXPERIMENTAL_PREVIEW",
    }


async def phase_tree(batch_id: str, user: dict[str, Any]) -> dict[str, Any]:
    batch = await require_preview(batch_id, user)
    documents = await preview_db.preview_units.find({"batch_id": batch_id}).sort(
        [("module_order", 1), ("unit_order", 1)],
    ).to_list(100)
    modules: dict[str, dict[str, Any]] = {}
    for document in documents:
        unit = _json_unit(document)
        module = modules.setdefault(unit.module_id, {
            "id": unit.module_id,
            "order": unit.module_order,
            "title": f"Módulo {unit.module_id}",
            "units": [],
        })
        module["units"].append({
            "id": unit.provenance.source_id,
            "title": unit.title,
            "order": unit.unit_order,
        })
    return {
        "id": batch_id,
        "title": "Fase 1 — prévia curricular isolada",
        "state": batch["state"],
        "modules": list(modules.values()),
    }


async def _activity_records(collection: str, query: dict) -> list[dict]:
    return await preview_db[collection].find(query).sort("created_at", 1).to_list(10_000)


async def progress_view(batch_id: str, user: dict[str, Any]) -> dict[str, Any]:
    await require_preview(batch_id, user)
    units = await preview_db.preview_units.find({"batch_id": batch_id}).sort(
        [("module_order", 1), ("unit_order", 1)],
    ).to_list(100)
    quizzes = await _activity_records("preview_quiz_attempts", {"batch_id": batch_id, "user_id": user["id"]})
    exercises = await _activity_records("preview_exercise_submissions", {"batch_id": batch_id, "user_id": user["id"]})
    projects = await _activity_records("preview_project_submissions", {"batch_id": batch_id, "user_id": user["id"]})
    quiz_by_unit: dict[str, list[dict]] = {}
    exercise_by_unit: dict[str, list[dict]] = {}
    project_by_unit: dict[str, list[dict]] = {}
    for row in quizzes:
        quiz_by_unit.setdefault(row["unit_id"], []).append(row)
    for row in exercises:
        exercise_by_unit.setdefault(row["unit_id"], []).append(row)
    for row in projects:
        project_by_unit.setdefault(row["unit_id"], []).append(row)

    unit_rows: list[dict[str, Any]] = []
    module_rows: dict[str, dict[str, Any]] = {}
    totals = {"quizzes_answered": 0, "exercises_submitted": 0, "awaiting_review": 0, "approved": 0}
    for document in units:
        unit = _json_unit(document)
        unit_quizzes = quiz_by_unit.get(unit.provenance.source_id, [])
        unit_exercises = exercise_by_unit.get(unit.provenance.source_id, [])
        unit_projects = project_by_unit.get(unit.provenance.source_id, [])
        latest_exercises: dict[str, dict] = {}
        for exercise in unit_exercises:
            latest = latest_exercises.get(exercise["activity_id"])
            if latest is None or exercise["created_at"] > latest["created_at"]:
                latest_exercises[exercise["activity_id"]] = exercise
        quiz_done = len({row["question_id"] for row in unit_quizzes})
        exercise_done = len(latest_exercises)
        pending = sum(row["state"] == "AWAITING_REVIEW" for row in latest_exercises.values())
        approved = sum(row["state"] == "APPROVED" for row in latest_exercises.values())
        project_pending = sum(row["state"] == "AWAITING_REVIEW" for row in unit_projects)
        row = {
            "unit_id": unit.provenance.source_id,
            "module_id": unit.module_id,
            "quizzes_answered": quiz_done,
            "quizzes_total": len(unit.quiz_questions),
            "exercises_submitted": exercise_done,
            "exercises_total": len(unit.manual_exercises),
            "awaiting_review": pending + project_pending,
            "approved": approved,
            "criterion_state": "REQUIRES_PEDAGOGICAL_DECISION" if unit.completion_criterion else "SOURCE_ABSENT",
            "unit_completion": "NOT_CONCLUDED",
            "mastery": "NOT_ASSESSED",
        }
        unit_rows.append(row)
        aggregate = module_rows.setdefault(unit.module_id, {
            "module_id": unit.module_id,
            "units": 0,
            "quizzes_answered": 0,
            "quizzes_total": 0,
            "exercises_submitted": 0,
            "exercises_total": 0,
            "awaiting_review": 0,
            "approved": 0,
            "completion": "NOT_CONCLUDED",
        })
        aggregate["units"] += 1
        for key in ("quizzes_answered", "quizzes_total", "exercises_submitted", "exercises_total", "awaiting_review", "approved"):
            aggregate[key] += row[key]
        for key in totals:
            totals[key] += row[key]
    return {
        "batch_id": batch_id,
        "units": unit_rows,
        "modules": list(module_rows.values()),
        "phase": {
            **totals,
            "units": len(unit_rows),
            "completion": "BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA",
            "mastery": "NOT_ASSESSED",
            "project_3_5_required_review": True,
        },
    }


def _question(unit: ConvertedUnit, question_id: str):
    for item in unit.quiz_questions:
        if item.ref == question_id:
            return item
    raise HTTPException(status_code=404, detail="Questão não encontrada")


async def submit_quiz_attempt(
    batch_id: str, unit_id: str, question_id: str, selected_option_id: str,
    source_sha256: str, operation_key: str | None, user: dict[str, Any],
) -> dict[str, Any]:
    await require_preview(batch_id, user)
    key = _safe_idempotency(operation_key)
    unit = await unit_for(batch_id, unit_id)
    if source_sha256 != unit.provenance.source_sha256:
        raise HTTPException(status_code=409, detail="A revisão curricular mudou; recarregue a unidade.")
    question = _question(unit, question_id)
    if selected_option_id not in {option.id for option in question.options}:
        raise HTTPException(status_code=422, detail="Alternativa inexistente")
    fingerprint = _canonical_hash({
        "batch_id": batch_id, "unit_id": unit_id, "question_id": question_id,
        "source_sha256": source_sha256, "selected_option_id": selected_option_id,
    })
    record_id = _canonical_hash({"user_id": user["id"], "operation_key": key})
    existing = await preview_db.preview_quiz_attempts.find_one({"_id": record_id})
    if existing:
        if existing["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Chave de operação reutilizada com outros dados")
        return _quiz_receipt(existing)
    document = {
        "_id": record_id,
        "batch_id": batch_id,
        "unit_id": unit_id,
        "question_id": question_id,
        "source_sha256": source_sha256,
        "user_id": user["id"],
        "selected_option_id": selected_option_id,
        "is_correct": selected_option_id == question.correct_option_id,
        "fingerprint": fingerprint,
        "operation_key": key,
        "created_at": _utcnow(),
    }
    try:
        await preview_db.preview_quiz_attempts.insert_one(document)
    except DuplicateKeyError:
        existing = await preview_db.preview_quiz_attempts.find_one({"_id": record_id})
        if not existing or existing["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Conflito de tentativa concorrente") from None
        document = existing
    return _quiz_receipt(document)


def _quiz_receipt(document: dict) -> dict[str, Any]:
    return {
        "id": document["_id"],
        "unit_id": document["unit_id"],
        "question_id": document["question_id"],
        "source_sha256": document["source_sha256"],
        "state": "ANSWERED",
        "feedback_state": "PENDING_PEDAGOGICAL_POLICY",
        "created_at": document["created_at"].isoformat(),
    }


def _exercise(unit: ConvertedUnit, exercise_id: str):
    for item in unit.manual_exercises:
        if item.ref == exercise_id:
            return item
    raise HTTPException(status_code=404, detail="Exercício não encontrado")


def _student_submission(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": document["_id"],
        "unit_id": document["unit_id"],
        "activity_id": document.get("activity_id", document.get("project_id")),
        "source_sha256": document["source_sha256"],
        "attempt": document["attempt"],
        "state": document["state"],
        "feedback": document.get("feedback"),
        "created_at": document["created_at"].isoformat(),
        "review_revision": document.get("revision", 0),
    }


async def submit_exercise(
    batch_id: str, unit_id: str, exercise_id: str, answer_text: str,
    source_sha256: str, unit_source_sha256: str,
    operation_key: str | None, user: dict[str, Any],
) -> dict[str, Any]:
    await require_preview(batch_id, user)
    key = _safe_idempotency(operation_key)
    unit = await unit_for(batch_id, unit_id)
    exercise = _exercise(unit, exercise_id)
    if (unit_source_sha256 != unit.provenance.source_sha256
            or source_sha256 != exercise.source_sha256):
        raise HTTPException(status_code=409, detail="A revisão curricular mudou; recarregue a unidade.")
    fingerprint = _canonical_hash({"batch_id": batch_id, "unit_id": unit_id,
                                   "exercise_id": exercise_id, "source_sha256": source_sha256,
                                   "unit_source_sha256": unit_source_sha256,
                                   "answer_text": answer_text})
    record_id = _canonical_hash({"user_id": user["id"], "operation_key": key})
    existing = await preview_db.preview_exercise_submissions.find_one({"_id": record_id})
    if existing:
        if existing["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Chave de operação reutilizada com outros dados")
        return _student_submission(existing)
    attempt = await preview_db.preview_exercise_submissions.count_documents({
        "batch_id": batch_id, "unit_id": unit_id, "activity_id": exercise_id, "user_id": user["id"],
    }) + 1
    document = {
        "_id": record_id, "batch_id": batch_id, "unit_id": unit_id,
        "activity_id": exercise_id, "source_sha256": source_sha256,
        "unit_source_sha256": unit_source_sha256,
        "user_id": user["id"], "answer_text": answer_text, "attempt": attempt,
        "state": "AWAITING_REVIEW", "feedback": None, "revision": 0,
        "operation_key": key, "fingerprint": fingerprint, "history": [], "created_at": _utcnow(),
    }
    try:
        await preview_db.preview_exercise_submissions.insert_one(document)
    except DuplicateKeyError:
        existing = await preview_db.preview_exercise_submissions.find_one({"_id": record_id})
        if not existing or existing["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Conflito de submissão concorrente") from None
        document = existing
    return _student_submission(document)


async def my_exercise_submissions(batch_id: str, unit_id: str | None, user: dict[str, Any]) -> list[dict]:
    await require_preview(batch_id, user)
    query: dict[str, Any] = {"batch_id": batch_id, "user_id": user["id"]}
    if unit_id:
        query["unit_id"] = unit_id
    records = await preview_db.preview_exercise_submissions.find(query).sort("created_at", -1).to_list(500)
    return [_student_submission(row) for row in records]


def public_project_projection(unit: ConvertedUnit) -> dict[str, Any]:
    sources = {item.artifact_id: item for item in unit.source_artifacts}
    artifacts = []
    for item in sorted(unit.project_materials, key=lambda value: value.order):
        # A student projection is an allowlist. Pending milestones and
        # unclassified checklists are omitted entirely; even their titles and
        # identifiers can disclose internal evaluation structure.
        if item.kind != "project_brief":
            continue
        source = sources.get(item.artifact_id)
        if source is None:
            raise HTTPException(status_code=503, detail="Inventário do projeto não passou na validação")
        artifacts.append({
            "id": item.artifact_id, "kind": item.kind, "order": item.order,
            "title": source.title or item.artifact_id, "visibility": "STUDENT_PUBLIC_PREVIEW",
            "content": item.content,
        })
    return {"id": "3.5", "title": unit.title, "version": unit.provenance.source_sha256,
            "artifacts": artifacts, "completion": "BLOCKED_BY_PEDAGOGICAL_REVIEW"}


async def public_project(batch_id: str, user: dict[str, Any]) -> dict[str, Any]:
    await require_preview(batch_id, user)
    return public_project_projection(await unit_for(batch_id, "3.5"))


async def restricted_project(batch_id: str, user: dict[str, Any]) -> dict[str, Any]:
    await require_reviewer(batch_id, user)
    unit = await unit_for(batch_id, "3.5")
    return {
        "project_id": "3.5",
        "materials": [{
            "id": item.artifact_id,
            "kind": item.kind,
            "order": item.order,
            "content": item.content,
            "classification": "INSTRUCTOR_RESTRICTED" if item.kind in {"rubric", "checklist"}
            else "STUDENT_PUBLIC_OR_RELEASE_PENDING",
        } for item in sorted(unit.project_materials, key=lambda value: value.order)],
    }


async def submit_project(
    batch_id: str, delivery_text: str, source_sha256: str, operation_key: str | None,
    user: dict[str, Any],
) -> dict[str, Any]:
    await require_preview(batch_id, user)
    key = _safe_idempotency(operation_key)
    unit = await unit_for(batch_id, "3.5")
    if source_sha256 != unit.provenance.source_sha256:
        raise HTTPException(status_code=409, detail="A versão do projeto mudou; recarregue as instruções.")
    fingerprint = _canonical_hash({"batch_id": batch_id, "project_id": "3.5",
                                   "source_sha256": source_sha256, "delivery_text": delivery_text})
    record_id = _canonical_hash({"user_id": user["id"], "operation_key": key})
    prior = await preview_db.preview_project_submissions.find_one({"_id": record_id})
    if prior:
        if prior["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Chave de operação reutilizada com outros dados")
        return _student_submission(prior)
    attempt = await preview_db.preview_project_submissions.count_documents({
        "batch_id": batch_id, "unit_id": "3.5", "user_id": user["id"],
    }) + 1
    document = {
        "_id": record_id, "batch_id": batch_id, "unit_id": "3.5", "project_id": "3.5",
        "source_sha256": source_sha256, "user_id": user["id"], "delivery_text": delivery_text,
        "attempt": attempt, "state": "AWAITING_REVIEW", "feedback": None, "revision": 0,
        "operation_key": key, "fingerprint": fingerprint, "history": [], "created_at": _utcnow(),
    }
    try:
        await preview_db.preview_project_submissions.insert_one(document)
    except DuplicateKeyError:
        prior = await preview_db.preview_project_submissions.find_one({"_id": record_id})
        if not prior or prior["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Conflito de entrega concorrente") from None
        document = prior
    return _student_submission(document)


async def my_project_submissions(batch_id: str, user: dict[str, Any]) -> list[dict]:
    await require_preview(batch_id, user)
    records = await preview_db.preview_project_submissions.find({
        "batch_id": batch_id, "user_id": user["id"],
    }).sort("created_at", -1).to_list(100)
    return [_student_submission(row) for row in records]


async def reviewer_project_queue(batch_id: str, user: dict[str, Any]) -> list[dict]:
    await require_reviewer(batch_id, user)
    records = await preview_db.preview_project_submissions.find({
        "batch_id": batch_id, "state": {"$in": ["AWAITING_REVIEW", "NEEDS_REVISION"]},
    }).sort("created_at", 1).to_list(500)
    return [{
        "id": row["_id"], "unit_id": row["unit_id"], "project_id": row["project_id"],
        "learner_id": row["user_id"], "answer": row["delivery_text"], "state": row["state"],
        "revision": row["revision"], "attempt": row["attempt"],
    } for row in records]


async def project_submission_detail(batch_id: str, submission_id: str, user: dict[str, Any]) -> dict:
    await require_reviewer(batch_id, user)
    row = await preview_db.preview_project_submissions.find_one({"_id": submission_id, "batch_id": batch_id})
    if row is None:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    restricted = await restricted_project(batch_id, user)
    return {
        "id": row["_id"], "project_id": row["project_id"], "learner_id": row["user_id"],
        "answer": row["delivery_text"], "state": row["state"], "revision": row["revision"],
        "history": row.get("history", []), "restricted_materials": restricted["materials"],
    }


async def revoke_preview_reviewer(batch_id: str, user_id: str) -> bool:
    """Harness-only revocation primitive. No HTTP route exposes grant mutation."""
    result = await preview_db.preview_grants.update_one({
        "batch_id": batch_id, "user_id": user_id, "state": "active",
    }, {"$set": {"state": "revoked", "revoked_at": _utcnow()}, "$inc": {"revision": 1}})
    return result.modified_count == 1


async def grade_project_submission(
    batch_id: str,
    submission_id: str,
    *,
    user: dict[str, Any],
    expected_revision: int,
    operation_key: str,
    outcome: str,
    feedback: str,
    before_grant_fence: Callable[[], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    """Atomically fence the synthetic grant, CAS the delivery, and append audit.

    The shared grant document is written in the same replica-set transaction as
    the review. Revocation writes the same document, creating a conflict that
    gives both actions a database-level linearization order.
    """
    batch = await require_reviewer(batch_id, user)
    del batch
    operation_key = _safe_idempotency(operation_key)
    if outcome not in {"feedback_only", "needs_revision"}:
        raise HTTPException(status_code=422, detail="Resultado de revisão não permitido nesta prévia")
    fingerprint = _canonical_hash({"submission_id": submission_id, "expected_revision": expected_revision,
                                   "outcome": outcome, "feedback": feedback})
    prior = await preview_db.preview_project_reviews.find_one({
        "batch_id": batch_id, "reviewer_id": user["id"], "operation_key": operation_key,
    })
    if prior:
        if prior["fingerprint"] != fingerprint:
            raise HTTPException(status_code=409, detail="Chave de correção reutilizada com outros dados")
        current = await preview_db.preview_project_submissions.find_one({"_id": submission_id})
        return _student_submission(current) if current else {"id": submission_id, "state": "REVIEWED"}

    scope = await preview_db.preview_grants.find_one({
        "batch_id": batch_id, "user_id": user["id"], "state": "active", "operations": _REVIEW_OPERATION,
    })
    if scope is None:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    try:
        async with client.start_session() as session:
            async with await session.start_transaction():
                grant = await preview_db.preview_grants.find_one({
                    "_id": scope["_id"], "state": "active", "operations": _REVIEW_OPERATION,
                }, session=session)
                if grant is None:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")
                if before_grant_fence is not None:
                    await before_grant_fence()
                fenced = await preview_db.preview_grants.update_one({
                    "_id": grant["_id"], "state": "active", "revision": grant.get("revision", 0),
                }, {"$inc": {"revision": 1}, "$set": {"last_review_operation": operation_key}}, session=session)
                if fenced.matched_count != 1:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")
                current = await preview_db.preview_project_submissions.find_one({
                    "_id": submission_id, "batch_id": batch_id,
                }, session=session)
                if current is None:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")
                same_operation = next((item for item in current.get("history", [])
                                       if item.get("operation_key") == operation_key), None)
                if same_operation:
                    if same_operation.get("fingerprint") != fingerprint:
                        raise HTTPException(status_code=409, detail="Chave de correção reutilizada com outros dados")
                    return _student_submission(current)
                if current.get("revision", 0) != expected_revision or current["state"] not in {
                    "AWAITING_REVIEW", "NEEDS_REVISION",
                }:
                    raise HTTPException(status_code=409, detail="A entrega foi alterada por outra avaliação")
                now = _utcnow()
                history_entry = {
                    "review_id": _canonical_hash({"submission_id": submission_id, "operation_key": operation_key}),
                    "operation_key": operation_key,
                    "fingerprint": fingerprint,
                    "reviewer_id": user["id"],
                    "outcome": outcome,
                    "feedback": feedback,
                    "at": now,
                    "revision": expected_revision + 1,
                }
                new_state = "NEEDS_REVISION" if outcome == "needs_revision" else "REVIEWED_FEEDBACK_ONLY"
                updated = await preview_db.preview_project_submissions.update_one({
                    "_id": submission_id,
                    "batch_id": batch_id,
                    "revision": expected_revision,
                    "state": current["state"],
                }, {"$set": {
                    "state": new_state,
                    "feedback": feedback,
                    "last_reviewer_id": user["id"],
                    "updated_at": now,
                }, "$inc": {"revision": 1}, "$push": {"history": history_entry}}, session=session)
                if updated.matched_count != 1:
                    raise HTTPException(status_code=409, detail="A entrega foi alterada por outra avaliação")
                await preview_db.preview_project_reviews.insert_one({
                    "_id": history_entry["review_id"],
                    "batch_id": batch_id,
                    "submission_id": submission_id,
                    "reviewer_id": user["id"],
                    "operation_key": operation_key,
                    "fingerprint": fingerprint,
                    "outcome": outcome,
                    "at": now,
                }, session=session)
        saved = await preview_db.preview_project_submissions.find_one({"_id": submission_id})
        if saved is None:
            raise HTTPException(status_code=503, detail="A avaliação aguarda reconciliação")
        return _student_submission(saved)
    except HTTPException:
        raise
    except PyMongoError as exc:
        # Transaction/write-conflict failures are visible as a conflict; no
        # partial review or progress event is committed by MongoDB.
        raise HTTPException(status_code=409, detail="Conflito de avaliação ou autorização; recarregue a entrega") from exc


async def student_project_reviews(batch_id: str, user: dict[str, Any]) -> list[dict]:
    await require_preview(batch_id, user)
    records = await preview_db.preview_project_submissions.find({
        "batch_id": batch_id, "user_id": user["id"],
    }).sort("created_at", -1).to_list(100)
    return [_student_submission(row) for row in records]
