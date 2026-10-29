"""Persisted replica-set race proving grant revocation versus review commit order."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime

from pymongo import MongoClient

from test_support.beta7_1_internal_target import connect_internal_verified_target


async def _run(batch_id: str) -> dict[str, object]:
    from services import beta7_1_preview as preview

    reviewer_grant = await preview.preview_db.preview_grants.find_one({
        "batch_id": batch_id, "operations": "preview.project.review", "state": "active",
    })
    student_grant = await preview.preview_db.preview_grants.find_one({
        "batch_id": batch_id, "operations": "preview.curriculum.read", "state": "active",
    })
    unscoped_grant = await preview.preview_db.preview_grants.find_one({
        "batch_id": batch_id, "operations": [], "state": "active",
    })
    if not reviewer_grant or not student_grant or not unscoped_grant:
        raise RuntimeError("Grants sintéticos esperados não estão disponíveis")

    async def make_submission(suffix: str) -> str:
        submission_id = f"beta71-review-race-{suffix}"
        await preview.preview_db.preview_project_submissions.insert_one({
            "_id": submission_id,
            "batch_id": batch_id,
            "unit_id": "3.5",
            "project_id": "3.5",
            "source_sha256": "a" * 64,
            "user_id": student_grant["user_id"],
            "delivery_text": "Submissão sintética de concorrência.",
            "attempt": 99,
            "state": "AWAITING_REVIEW",
            "feedback": None,
            "revision": 0,
            "history": [],
            "created_at": datetime.now(UTC),
        })
        return submission_id

    first_id = await make_submission("revoked-before-commit")
    authorized = {"id": reviewer_grant["user_id"], "role": "editor"}
    reached_fence = asyncio.Event()
    continue_grade = asyncio.Event()

    async def barrier() -> None:
        reached_fence.set()
        await asyncio.wait_for(continue_grade.wait(), timeout=10)

    pending_grade = asyncio.create_task(preview.grade_project_submission(
        batch_id, first_id, user=authorized, expected_revision=0,
        operation_key="beta71-race-revoke-before", outcome="needs_revision",
        feedback="Esta decisão deve ser rejeitada pela revogação anterior ao commit.",
        before_grant_fence=barrier,
    ))
    await asyncio.wait_for(reached_fence.wait(), timeout=10)
    revoked_first = await preview.revoke_preview_reviewer(batch_id, authorized["id"])
    if not revoked_first:
        continue_grade.set()
        raise RuntimeError("Não foi possível confirmar a revogação concorrente")
    continue_grade.set()
    try:
        await pending_grade
    except Exception as exc:
        from fastapi import HTTPException

        if not isinstance(exc, HTTPException) or exc.status_code != 409:
            raise
    else:
        raise AssertionError("Correção foi confirmada após a revogação do escopo")
    rejected = await preview.preview_db.preview_project_submissions.find_one({"_id": first_id})
    first_audit_count = await preview.preview_db.preview_project_reviews.count_documents({"submission_id": first_id})
    if rejected["state"] != "AWAITING_REVIEW" or rejected.get("history") or first_audit_count:
        raise AssertionError("A correção rejeitada deixou estado ou auditoria parcial")

    # For the opposite serialization order, activate a second synthetic grant,
    # confirm the review transaction first, and only then revoke that grant.
    grant_id = unscoped_grant["_id"]
    await preview.preview_db.preview_grants.update_one(
        {"_id": grant_id, "state": "active"},
        {"$set": {"operations": ["preview.curriculum.read", "preview.project.review"]}, "$inc": {"revision": 1}},
    )
    second_id = await make_submission("commit-before-revoke")
    second_actor = {"id": unscoped_grant["user_id"], "role": "editor"}
    confirmed = await preview.grade_project_submission(
        batch_id, second_id, user=second_actor, expected_revision=0,
        operation_key="beta71-race-commit-before", outcome="needs_revision",
        feedback="Decisão confirmada antes da revogação efetiva.",
    )
    revoked_after = await preview.revoke_preview_reviewer(batch_id, second_actor["id"])
    persisted = await preview.preview_db.preview_project_submissions.find_one({"_id": second_id})
    audit_count = await preview.preview_db.preview_project_reviews.count_documents({"submission_id": second_id})
    if not revoked_after or confirmed["state"] != "NEEDS_REVISION" or persisted["state"] != "NEEDS_REVISION" or audit_count != 1:
        raise AssertionError("A ordem commit-antes-da-revogação não preservou decisão e auditoria")

    return {
        "status": "PERSISTENCE_VERIFIED",
        "revocation_before_commit": "review_conflicted_no_partial_write",
        "commit_before_revocation": "review_and_audit_preserved",
        "first_partial_review_count": first_audit_count,
        "second_audit_count": audit_count,
        "synthetic_race_records": 2,
    }


def main() -> int:
    target, owner = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    marker = owner[f"{target.database}_beta7_1_preview"]["_beta7-1_test_owner"].find_one({"_id": "owner"})
    if not marker or any(marker.get(key) != value for key, value in {
        "run_id": target.run_id, "owner_token": target.owner_token,
        "container_id": target.container_id, "network_id": target.network_id,
        "database": f"{target.database}_beta7_1_preview", "parent_database": target.database,
    }.items()):
        owner.close()
        raise RuntimeError("Namespace de prévia sem marcador de propriedade Beta 7.1")
    owner.close()
    result = asyncio.run(_run(os.environ["BETA7_1_E2E_BATCH_ID"]))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
