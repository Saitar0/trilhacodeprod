"""Persistent synthetic assessment proof behind the verified Beta 7.1 Docker gate."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime

from pymongo import MongoClient

from test_support.beta7_1_internal_target import connect_internal_verified_target


def _synthetic_rubric():
    from curriculum_contract.beta7_2_rubric import (
        DefinitionState,
        PerformanceDescriptor,
        RubricApproval,
        RubricCriterion,
        RubricDecisionRule,
        RubricProvenance,
        RubricState,
        VersionedRubric,
    )

    provenance = RubricProvenance(
        source_revision="beta7-2-synthetic-only",
        source_path="test_support/synthetic_project_rubric.json",
        source_artifact_id="beta7-2-synthetic-rubric",
        source_sha256="a" * 64,
        source_state="SYNTHETIC_FIXTURE_NOT_CURRICULUM",
        source_section="synthetic criterion",
    )
    criterion = RubricCriterion(
        criterion_id="synthetic-project:observable-evidence",
        description="Synthetic-only test criterion; not derived from the reviewed curriculum.",
        definition_state=DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
        required=True,
        provenance=provenance,
        descriptors=tuple(PerformanceDescriptor(score=i, description=f"synthetic level {i}") for i in range(5)),
        observable_evidence=("synthetic fixture evidence",),
    )
    rubric = VersionedRubric(
        rubric_id="beta7-2-synthetic-rubric",
        project_id="synthetic-project",
        version="synthetic-v1",
        state=RubricState.PEDAGOGICALLY_APPROVED,
        provenance=provenance,
        criteria=(criterion,),
        decision_rule=RubricDecisionRule(
            required_criterion_ids=(criterion.criterion_id,), minimum_score=3,
        ),
        approval=RubricApproval(
            approved_by="beta7-2-test-fixture",
            approval_record_id="synthetic-approval-only",
            approved_at=datetime(2026, 1, 1, tzinfo=UTC),
            decision_record="Synthetic test fixture; no curricular authority.",
        ),
        synthetic_fixture=True,
    )
    return rubric.model_copy(update={"canonical_sha256": rubric.content_hash()})


async def _run(batch_id: str, run_id: str) -> dict[str, object]:
    from fastapi import HTTPException

    from curriculum_contract.beta7_2_assessment import (
        AssessmentCommand,
        AssessmentOutcome,
        CriterionEvidence,
    )
    from curriculum_contract.beta7_2_completion import (
        CompletionRequirement,
        RequirementResult,
        RequirementState,
        project_completion,
    )
    from curriculum_contract.beta7_2_rubric import DefinitionState
    from services import beta7_2_assessment as assessment
    from services.beta7_1_preview import preview_db
    batch = await preview_db.preview_batches.find_one({"_id": batch_id, "state": "PREPARED"})
    if batch is None or batch.get("run_id") != run_id:
        raise RuntimeError("Lote não pertence à execução descartável atestada")
    reviewer_grant = await preview_db.preview_grants.find_one({
        "batch_id": batch_id, "state": "active", "operations": "preview.project.review",
    })
    student_grant = await preview_db.preview_grants.find_one({
        "batch_id": batch_id, "state": "active", "operations": "preview.curriculum.read",
    })
    if reviewer_grant is None or student_grant is None:
        raise RuntimeError("Grants sintéticos da prova persistente não foram preparados")

    synthetic_student_id = f"beta7-2-synthetic-learner-{run_id[:12]}"
    synthetic_grant_id = f"{batch_id}:{synthetic_student_id}"
    if await preview_db.preview_grants.find_one({"_id": synthetic_grant_id}):
        raise RuntimeError("Grant de aluno sintético preexistente detectado; recurso preservado")
    await preview_db.preview_grants.insert_one({
        "_id": synthetic_grant_id,
        "batch_id": batch_id,
        "user_id": synthetic_student_id,
        "state": "active",
        "operations": ["preview.curriculum.read"],
        "revision": 0,
        "source": "synthetic_beta7_2_persistence_fixture_only",
    })

    rubric = _synthetic_rubric()
    rubric_id = f"{batch_id}:synthetic-only:{rubric.version}"
    submission_id = f"{batch_id}:synthetic-assessment-submission"
    if await assessment.assessment_db.beta7_2_rubrics.find_one({"_id": rubric_id}):
        raise RuntimeError("Rubrica sintética preexistente detectada; recurso preservado")
    if await preview_db.preview_project_submissions.find_one({"_id": submission_id}):
        raise RuntimeError("Submissão sintética preexistente detectada; recurso preservado")

    await assessment.assessment_db.beta7_2_rubrics.insert_one({
        "_id": rubric_id, "batch_id": batch_id, **rubric.model_dump(mode="python"),
    })
    await preview_db.preview_project_submissions.insert_one({
        "_id": submission_id,
        "batch_id": batch_id,
        "unit_id": "synthetic-project",
        "project_id": rubric.project_id,
        "source_sha256": "b" * 64,
        "user_id": synthetic_student_id,
        "delivery_text": "Synthetic-only delivery for persistence verification.",
        "attempt": 1,
        "state": "AWAITING_REVIEW",
        "feedback": None,
        "revision": 0,
        "operation_key": "beta7-2-synthetic-delivery",
        "fingerprint": "synthetic-only",
        "history": [],
        "created_at": datetime.now(UTC),
    })
    command = AssessmentCommand(
        submission_id=submission_id,
        project_id=rubric.project_id,
        project_version="b" * 64,
        rubric_id=rubric.rubric_id,
        rubric_version=rubric.version,
        expected_revision=0,
        outcome=AssessmentOutcome.APPROVED,
        feedback="Synthetic approval used only to exercise state transitions.",
        criteria=(CriterionEvidence(
            criterion_id=rubric.criteria[0].criterion_id,
            score=3,
            evidence_text="Synthetic evidence attached to the test fixture.",
            evidence_reference="fixture://beta7-2/evidence",
        ),),
    )
    reviewer = {"id": reviewer_grant["user_id"], "role": "editor"}
    receipt = await assessment.assess_project(
        batch_id, submission_id, user=reviewer, command=command,
        operation_key="beta7-2-synthetic-assessment-v1",
    )
    replay = await assessment.assess_project(
        batch_id, submission_id, user=reviewer, command=command,
        operation_key="beta7-2-synthetic-assessment-v1",
    )
    if receipt["assessment_id"] != replay["assessment_id"] or receipt["state"] != "APPROVED":
        raise RuntimeError("Retry idempotente da avaliação sintética divergiu")
    if await assessment.assessment_db.beta7_2_assessments.count_documents({"submission_id": submission_id}) != 1:
        raise RuntimeError("Retry criou avaliação sintética duplicada")

    divergent = command.model_copy(update={"feedback": "Different payload for the same operation key."})
    try:
        await assessment.assess_project(
            batch_id, submission_id, user=reviewer, command=divergent,
            operation_key="beta7-2-synthetic-assessment-v1",
        )
    except HTTPException as exc:
        if exc.status_code != 409:
            raise
    else:
        raise RuntimeError("Payload divergente reutilizou chave de operação")

    requirement = CompletionRequirement(
        requirement_id="synthetic-project-approved",
        definition_state=DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
        required=True,
        source_artifact_id=rubric.provenance.source_artifact_id,
        source_sha256=rubric.provenance.source_sha256,
        activity_version=rubric.version,
    )
    completion = project_completion("synthetic-project-only", (requirement,), {
        requirement.requirement_id: RequirementResult(
            requirement_id=requirement.requirement_id,
            state=RequirementState.APPROVED,
            assessed_version=rubric.version,
        ),
    })
    concurrent_submission_id = f"{batch_id}:synthetic-concurrent-assessment-submission"
    reviewer_two_id = f"beta7-2-concurrent-reviewer-{run_id[:12]}"
    reviewer_two_grant_id = f"{batch_id}:{reviewer_two_id}"
    if await preview_db.preview_project_submissions.find_one({"_id": concurrent_submission_id}):
        raise RuntimeError("Submissão concorrente sintética preexistente detectada; recurso preservado")
    if await preview_db.preview_grants.find_one({"_id": reviewer_two_grant_id}):
        raise RuntimeError("Grant concorrente sintético preexistente detectado; recurso preservado")
    await preview_db.preview_grants.insert_one({
        "_id": reviewer_two_grant_id,
        "batch_id": batch_id,
        "user_id": reviewer_two_id,
        "state": "active",
        "operations": ["preview.project.review"],
        "revision": 0,
        "source": "synthetic_beta7_2_concurrency_fixture_only",
    })
    await preview_db.preview_project_submissions.insert_one({
        "_id": concurrent_submission_id,
        "batch_id": batch_id,
        "unit_id": "synthetic-project",
        "project_id": rubric.project_id,
        "source_sha256": "b" * 64,
        "user_id": synthetic_student_id,
        "delivery_text": "Concurrent synthetic-only delivery.",
        "attempt": 1,
        "state": "AWAITING_REVIEW",
        "feedback": None,
        "revision": 0,
        "operation_key": "beta7-2-synthetic-concurrent-delivery",
        "fingerprint": "synthetic-concurrent-only",
        "history": [],
        "created_at": datetime.now(UTC),
    })
    concurrent_command = command.model_copy(update={
        "submission_id": concurrent_submission_id,
        "feedback": "Concurrent synthetic-only decision.",
    })
    barrier = asyncio.Barrier(2)

    async def concurrent_review(reviewer_id: str, operation_key: str):
        await barrier.wait()
        try:
            return await assessment.assess_project(
                batch_id, concurrent_submission_id,
                user={"id": reviewer_id, "role": "editor"},
                command=concurrent_command,
                operation_key=operation_key,
            )
        except HTTPException as exc:
            return exc

    concurrent_results = await asyncio.gather(
        concurrent_review(reviewer["id"], "beta7-2-concurrent-reviewer-one"),
        concurrent_review(reviewer_two_id, "beta7-2-concurrent-reviewer-two"),
    )
    successful_reviews = [row for row in concurrent_results if isinstance(row, dict)]
    conflicts = [row for row in concurrent_results if isinstance(row, HTTPException) and row.status_code == 409]
    if len(successful_reviews) != 1 or len(conflicts) != 1:
        raise RuntimeError("Duas decisões concorrentes não resultaram em uma confirmação e um conflito")
    concurrent_saved = await preview_db.preview_project_submissions.find_one({"_id": concurrent_submission_id})
    concurrent_events = await assessment.assessment_db.beta7_2_assessments.count_documents({
        "submission_id": concurrent_submission_id,
    })
    if concurrent_saved is None or concurrent_saved["revision"] != 1 or len(concurrent_saved["history"]) != 1 or concurrent_events != 1:
        raise RuntimeError("A disputa concorrente duplicou ou sobrescreveu o histórico")

    persisted = await preview_db.preview_project_submissions.find_one({"_id": submission_id})
    if persisted is None or persisted["state"] != "APPROVED" or len(persisted["history"]) != 1:
        raise RuntimeError("Estado ou histórico da prova sintética não foi persistido")
    if completion.state.value != "COMPLETED":
        raise RuntimeError("Política sintética válida não alcançou estado técnico concluído")

    next_version = rubric.model_copy(update={"version": "synthetic-v2", "canonical_sha256": None})
    next_version = next_version.model_copy(update={"canonical_sha256": next_version.content_hash()})
    next_version_id = f"{batch_id}:synthetic-only:{next_version.version}"
    if await assessment.assessment_db.beta7_2_rubrics.find_one({"_id": next_version_id}):
        raise RuntimeError("Nova versão sintética preexistente detectada; recurso preservado")
    await assessment.assessment_db.beta7_2_rubrics.insert_one({
        "_id": next_version_id, "batch_id": batch_id, **next_version.model_dump(mode="python"),
    })
    historical_assessment = await assessment.assessment_db.beta7_2_assessments.find_one({
        "_id": receipt["assessment_id"],
    })
    if (historical_assessment is None
            or historical_assessment["rubric_version"] != rubric.version
            or historical_assessment["rubric_sha256"] != rubric.content_hash()):
        raise RuntimeError("Nova versão da rubrica alterou avaliação histórica")
    return {
        "kind": "synthetic-only",
        "assessment_state": persisted["state"],
        "assessment_events": await assessment.assessment_db.beta7_2_assessments.count_documents({
            "submission_id": submission_id,
        }),
        "retry_same_operation": "single-event",
        "divergent_retry": "409",
        "new_version_preserved_history": {
            "new_version": next_version.version,
            "historical_version": historical_assessment["rubric_version"],
        },
        "concurrent_review": {
            "decisions_confirmed": len(successful_reviews),
            "conflicts": len(conflicts),
            "assessment_events": concurrent_events,
            "submission_revision": concurrent_saved["revision"],
        },
        "synthetic_completion": completion.state.value,
        "real_curriculum_changed": False,
    }


def main() -> int:
    target, owner = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    try:
        collections = set(owner[target.database].list_collection_names())
        if not collections or "_beta7-1_test_owner" not in collections:
            raise RuntimeError("Banco de teste sem marcador de propriedade confirmado")
        batch_id = os.environ.get("BETA7_1_E2E_BATCH_ID", "")
        if not batch_id:
            raise RuntimeError("Identidade do lote da prova não informada")
    finally:
        owner.close()
    result = asyncio.run(_run(batch_id, target.run_id))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
