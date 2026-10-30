"""Versioned project assessment store used only by the isolated Beta 7.2 app.

This module is deliberately absent from operational route/startup registries.
All writes target the Beta 7.1 disposable preview database namespace.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException
from pymongo.errors import PyMongoError

from curriculum_contract.beta7_2_assessment import (
    AssessmentBlocked,
    AssessmentCommand,
    AssessmentOutcome,
    AssessmentRecord,
    validate_assessment_decision,
)
from curriculum_contract.beta7_2_rubric import VersionedRubric
from database import client
from services import beta7_1_preview as preview
from settings import settings

assessment_db = client[f"{settings.db_name}_beta7_1_preview"]
_REVIEW_OPERATION = "preview.project.review"


def _now() -> datetime:
    return datetime.now(UTC)


def _rubric_document(document: dict[str, Any]) -> VersionedRubric:
    payload = {key: value for key, value in document.items() if key in VersionedRubric.model_fields}
    try:
        return VersionedRubric.model_validate(payload)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Versão de rubrica inválida") from exc


async def instructor_rubric(
    batch_id: str, user: dict[str, Any], version: str | None = None,
) -> dict[str, Any]:
    await preview.require_reviewer(batch_id, user)
    query: dict[str, Any] = {"batch_id": batch_id, "project_id": "3.5"}
    if version is not None:
        query["version"] = version
        document = await assessment_db.beta7_2_rubrics.find_one(query)
        if document is None:
            raise HTTPException(status_code=404, detail="Versão de rubrica não encontrada")
    else:
        versions = await assessment_db.beta7_2_rubrics.find(query).limit(2).to_list(2)
        if len(versions) > 1:
            raise HTTPException(status_code=409, detail="Informe a versão exata da rubrica")
        document = versions[0] if versions else None
    if document is None:
        raise HTTPException(status_code=404, detail="Rubrica não encontrada")
    return _rubric_document(document).model_dump(mode="json")


async def assess_project(
    batch_id: str,
    submission_id: str,
    *,
    user: dict[str, Any],
    command: AssessmentCommand,
    operation_key: str,
) -> dict[str, Any]:
    await preview.require_reviewer(batch_id, user)
    if command.submission_id != submission_id:
        raise HTTPException(status_code=422, detail="Identidade da entrega divergente")
    try:
        key = preview._safe_idempotency(operation_key)
    except HTTPException:
        raise
    rubric_doc = await assessment_db.beta7_2_rubrics.find_one({
        "batch_id": batch_id, "project_id": command.project_id, "rubric_id": command.rubric_id,
        "version": command.rubric_version,
    })
    if rubric_doc is None:
        raise HTTPException(status_code=409, detail="A versão da rubrica não está disponível")
    rubric = _rubric_document(rubric_doc)
    try:
        validate_assessment_decision(rubric, command)
    except AssessmentBlocked as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    fingerprint = preview._canonical_hash(command.model_dump(mode="json"))
    operation_id = preview._canonical_hash({
        "batch_id": batch_id, "submission_id": submission_id,
        "reviewer_id": user["id"], "operation_key": key,
    })
    prior = await assessment_db.beta7_2_assessments.find_one({"_id": operation_id})
    if prior is not None:
        if prior.get("fingerprint") != fingerprint:
            raise HTTPException(status_code=409, detail="Chave de avaliação reutilizada com dados diferentes")
        return await _review_receipt(batch_id, submission_id, prior)

    scope = await assessment_db.preview_grants.find_one({
        "batch_id": batch_id, "user_id": user["id"], "state": "active",
        "operations": _REVIEW_OPERATION,
    })
    if scope is None:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    try:
        async with client.start_session() as session:
            async with await session.start_transaction():
                # Grant revision is a serialization fence shared with revocation.
                grant = await assessment_db.preview_grants.find_one({
                    "_id": scope["_id"], "state": "active", "operations": _REVIEW_OPERATION,
                }, session=session)
                if grant is None:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")
                fenced = await assessment_db.preview_grants.update_one({
                    "_id": grant["_id"], "state": "active", "revision": grant.get("revision", 0),
                }, {"$inc": {"revision": 1}, "$set": {"last_assessment_operation": operation_id}}, session=session)
                if fenced.matched_count != 1:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")

                submission = await assessment_db.preview_project_submissions.find_one({
                    "_id": submission_id, "batch_id": batch_id,
                }, session=session)
                if submission is None:
                    raise HTTPException(status_code=404, detail="Entrega não encontrada")
                if submission.get("revision", 0) != command.expected_revision:
                    raise HTTPException(status_code=409, detail="A entrega foi alterada; atualize antes de avaliar")
                if submission.get("state") not in {"AWAITING_REVIEW", "NEEDS_REVISION"}:
                    raise HTTPException(status_code=409, detail="Estado da entrega não permite avaliação")
                if submission.get("source_sha256") != command.project_version:
                    raise HTTPException(status_code=409, detail="Versão do projeto divergente")

                resulting_state = (
                    "APPROVED" if command.outcome == AssessmentOutcome.APPROVED else "NEEDS_REVISION"
                )
                record = AssessmentRecord(
                    assessment_id=operation_id,
                    operation_key=key,
                    submission_id=submission_id,
                    learner_id=str(submission["user_id"]),
                    reviewer_id=str(user["id"]),
                    project_id=command.project_id,
                    project_version=command.project_version,
                    rubric_id=rubric.rubric_id,
                    rubric_version=rubric.version,
                    rubric_sha256=rubric.content_hash(),
                    expected_revision=command.expected_revision,
                    outcome=command.outcome,
                    feedback=command.feedback,
                    criteria=command.criteria,
                    previous_state=str(submission["state"]),
                    resulting_state=resulting_state,
                    decided_at=_now(),
                )
                record_doc = record.model_dump(mode="python")
                record_doc.update({"_id": operation_id, "batch_id": batch_id, "fingerprint": fingerprint})
                await assessment_db.beta7_2_assessments.insert_one(record_doc, session=session)
                updated = await assessment_db.preview_project_submissions.update_one({
                    "_id": submission_id, "batch_id": batch_id,
                    "revision": command.expected_revision, "state": submission["state"],
                }, {
                    "$set": {
                        "state": resulting_state,
                        "feedback": command.feedback,
                        "last_reviewer_id": str(user["id"]),
                        "last_assessment_id": operation_id,
                        "last_rubric_version": rubric.version,
                        "updated_at": record.decided_at,
                    },
                    "$inc": {"revision": 1},
                    "$push": {"history": {
                        "event_id": operation_id, "operation_key": key,
                        "state": resulting_state, "at": record.decided_at,
                        "rubric_version": rubric.version,
                    }},
                }, session=session)
                if updated.matched_count != 1:
                    raise HTTPException(status_code=409, detail="Conflito concorrente de avaliação")
    except HTTPException:
        raise
    except PyMongoError as exc:
        raise HTTPException(status_code=409, detail="Conflito de avaliação; recarregue a entrega") from exc
    saved = await assessment_db.beta7_2_assessments.find_one({"_id": operation_id})
    if saved is None:
        raise HTTPException(status_code=503, detail="Avaliação aguarda reconciliação")
    return await _review_receipt(batch_id, submission_id, saved)


async def _review_receipt(batch_id: str, submission_id: str, assessment: dict[str, Any]) -> dict[str, Any]:
    submission = await assessment_db.preview_project_submissions.find_one({
        "_id": submission_id, "batch_id": batch_id,
    })
    if submission is None:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    return {
        "assessment_id": assessment["_id"],
        "submission_id": submission_id,
        "state": submission["state"],
        "revision": submission["revision"],
        "feedback": submission.get("feedback"),
        "outcome": assessment["outcome"],
        "rubric_version": assessment["rubric_version"],
    }


async def learner_assessment_history(batch_id: str, user: dict[str, Any]) -> list[dict[str, Any]]:
    await preview.require_preview(batch_id, user)
    records = await assessment_db.beta7_2_assessments.find({
        "batch_id": batch_id, "learner_id": str(user["id"]),
    }).sort("decided_at", -1).to_list(100)
    return [{
        "assessment_id": row["_id"], "submission_id": row["submission_id"],
        "outcome": row["outcome"], "feedback": row["feedback"],
        "resulting_state": row["resulting_state"], "decided_at": row["decided_at"],
    } for row in records]
