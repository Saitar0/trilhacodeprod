from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from curriculum_contract.beta7_2_assessment import (
    AssessmentBlocked,
    AssessmentCommand,
    AssessmentOutcome,
    CriterionEvidence,
    proposed_rubric_from_project,
    validate_assessment_decision,
)
from curriculum_contract.beta7_2_completion import (
    CompletionRequirement,
    RequirementResult,
    RequirementState,
    ScopeCompletion,
    project_completion,
    project_curriculum_completion,
)
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
from curriculum_contract.beta_project_contract import (
    ProjectArtifact,
    ProjectArtifactKind,
    ProjectPackage,
    ProjectRubric,
    ProjectStep,
)

SHA = "a" * 64


def _provenance() -> RubricProvenance:
    return RubricProvenance(
        source_revision="synthetic-fixture-v1",
        source_path="fixtures/project/rubric.md",
        source_artifact_id="synthetic-rubric",
        source_sha256=SHA,
        source_state="synthetic-only",
        source_section="synthetic criterion",
    )


def _approved_synthetic_rubric() -> VersionedRubric:
    provenance = _provenance()
    criterion = RubricCriterion(
        criterion_id="synthetic:criterion-1",
        description="Synthetic criterion; not derived from Trilha Code source.",
        definition_state=DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
        required=True,
        provenance=provenance,
        descriptors=tuple(PerformanceDescriptor(score=score, description=f"synthetic level {score}")
                          for score in range(5)),
        observable_evidence=("synthetic evidence reference",),
    )
    rubric = VersionedRubric(
        rubric_id="synthetic-rubric",
        project_id="synthetic-project",
        version="synthetic-v1",
        state=RubricState.PEDAGOGICALLY_APPROVED,
        provenance=provenance,
        criteria=(criterion,),
        decision_rule=RubricDecisionRule(
            required_criterion_ids=(criterion.criterion_id,), minimum_score=3,
        ),
        approval=RubricApproval(
            approved_by="synthetic-fixture-owner",
            approval_record_id="synthetic-approval-record",
            approved_at=datetime(2026, 1, 1, tzinfo=UTC),
            decision_record="synthetic test fixture only",
        ),
        synthetic_fixture=True,
    )
    return rubric.model_copy(update={"canonical_sha256": rubric.content_hash()})


def _command(rubric: VersionedRubric, *, score: int = 3) -> AssessmentCommand:
    criterion_id = rubric.criteria[0].criterion_id
    return AssessmentCommand(
        submission_id="submission-1",
        project_id=rubric.project_id,
        project_version="project-v1",
        rubric_id=rubric.rubric_id,
        rubric_version=rubric.version,
        expected_revision=0,
        outcome=AssessmentOutcome.APPROVED,
        feedback="synthetic feedback",
        criteria=(CriterionEvidence(
            criterion_id=criterion_id, score=score,
            evidence_text="Evidence from synthetic fixture.", evidence_reference="fixture://evidence",
        ),),
    )


def _source_project() -> ProjectPackage:
    artifacts = [ProjectArtifact(
        artifact_id="synthetic-brief", kind=ProjectArtifactKind.PROJECT_BRIEF,
        purpose="project instructions", source_path="brief.md", content_sha256="b" * 64,
        order=0, project_id="3.5", phase_id="1", student_content="brief", classification="STUDENT_PUBLIC",
    )]
    steps = []
    for order in range(1, 5):
        artifact_id = f"milestone-{order}"
        checklist_id = f"checklist-{order}"
        artifacts.extend([
            ProjectArtifact(
                artifact_id=artifact_id, kind=ProjectArtifactKind.MILESTONE,
                purpose="milestone instructions", source_path=f"m{order}.md", content_sha256=str(order) * 64,
                order=order, project_id="3.5", phase_id="1",
                student_content=(
                    f"Milestone {order}\n\n**Evidência:** entrega observável do marco {order}.\n\n"
                    f"**Verificação:** conferência manual prevista no marco {order}."
                ),
                classification="STUDENT_PUBLIC",
            ),
            ProjectArtifact(
                artifact_id=checklist_id, kind=ProjectArtifactKind.CHECKLIST,
                purpose="acceptance checklist", source_path=f"c{order}.md", content_sha256="c" * 64,
                order=order + 4, project_id="3.5", phase_id="1", restricted_content="checklist",
                classification="INSTRUCTOR_RESTRICTED",
            ),
        ])
        steps.append(ProjectStep(
            step_id=f"M{order:02}", order=order,
            instruction_artifact_id=artifact_id, acceptance_artifact_id=checklist_id,
        ))
    rubric_id = "source-rubric"
    rubric_content = (
        "Rubrica comum para cada marco (0–4): 4 = evidências completas e verificação aprovada; "
        "3 = entrega aprovada com uma lacuna menor; 2 = artefato existe, mas falta evidência ou uma verificação importante; "
        "1 = entrega incompleta ou difícil de usar; 0 = sem evidência avaliável. "
        "Os marcos 3 e 4 não são aceitos enquanto houver credencial real ou dado pessoal versionado."
    )
    artifacts.append(ProjectArtifact(
        artifact_id=rubric_id, kind=ProjectArtifactKind.RUBRIC, purpose="evaluation rubric",
        source_path="rubric.md", content_sha256=SHA, order=0, project_id="3.5", phase_id="1",
        restricted_content=rubric_content, classification="INSTRUCTOR_RESTRICTED",
    ))
    return ProjectPackage(
        title="Synthetic source project", source_sha256="d" * 64,
        source_revision="synthetic-source-revision", artifacts=tuple(artifacts), steps=tuple(steps),
        rubrics=(ProjectRubric(artifact_id=rubric_id, raw_content=rubric_content),),
    )


def test_source_rubric_is_preserved_as_proposed_and_has_no_active_decision_rule() -> None:
    rubric = proposed_rubric_from_project(
        _source_project(), source_revision="migration@fixture", source_state="rascunho",
    )
    assert rubric.state == RubricState.PROPOSED
    assert rubric.decision_rule is None
    assert rubric.approval is None
    assert len(rubric.criteria) == 4
    assert all(item.required is None for item in rubric.criteria)
    assert [item.score for item in rubric.criteria[0].descriptors] == [4, 3, 2, 1, 0]
    assert rubric.criteria[0].observable_evidence == (
        "Evidência: entrega observável do marco 1.",
        "Verificação: conferência manual prevista no marco 1.",
    )
    assert rubric.criteria[0].provenance.source_artifact_id == "milestone-1"
    assert rubric.criteria[0].provenance.source_path == "m1.md"
    assert rubric.criteria[0].provenance.source_sha256 == "1" * 64
    assert len(rubric.constraints) == 1
    assert rubric.constraints[0].definition_state == DefinitionState.SOURCE_DEFINED
    assert rubric.constraints[0].blocks_acceptance_when_violated is True
    assert rubric.constraints[0].applies_to_criterion_ids == ("3.5:M03", "3.5:M04")
    with pytest.raises(AssessmentBlocked, match="aprovação pedagógica"):
        validate_assessment_decision(rubric, _command(rubric))


def test_synthetic_approved_rubric_can_demonstrate_mechanics_without_source_approval() -> None:
    rubric = _approved_synthetic_rubric()
    assert rubric.synthetic_fixture is True
    validate_assessment_decision(rubric, _command(rubric, score=3))
    with pytest.raises(AssessmentBlocked, match="não atingem"):
        validate_assessment_decision(rubric, _command(rubric, score=2))


def test_unapproved_rubric_cannot_carry_decision_policy_or_approval() -> None:
    provenance = _provenance()
    criterion = RubricCriterion(
        criterion_id="source:criterion", description="source criterion",
        definition_state=DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
        required=None, provenance=provenance,
    )
    with pytest.raises(ValidationError, match="não pode carregar regra decisória ativa"):
        VersionedRubric(
            rubric_id="source", project_id="3.5", version="v1", state=RubricState.PROPOSED,
            provenance=provenance, criteria=(criterion,),
            decision_rule=RubricDecisionRule(required_criterion_ids=(criterion.criterion_id,), minimum_score=3),
        )


def test_approval_requires_one_evidence_record_per_required_criterion() -> None:
    rubric = _approved_synthetic_rubric()
    command = _command(rubric).model_copy(update={"criteria": ()})
    with pytest.raises(AssessmentBlocked, match="evidência para cada critério"):
        validate_assessment_decision(rubric, command)


def test_completion_blocks_ambiguous_rules_and_requires_exact_activity_version() -> None:
    requirements = (
        CompletionRequirement(
            requirement_id="source-project", definition_state=DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
            required=None, source_artifact_id="criterion", source_sha256=SHA,
        ),
        CompletionRequirement(
            requirement_id="unit-1", definition_state=DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
            required=True, source_artifact_id="criterion-1", source_sha256=SHA, activity_version="unit-v2",
        ),
    )
    result = RequirementResult(
        requirement_id="unit-1", state=RequirementState.APPROVED, assessed_version="unit-v1",
    )
    projection = project_completion("phase-1", requirements, {"unit-1": result})
    assert projection.state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
    assert projection.pending_requirement_ids == ("unit-1",)


def test_fully_defined_synthetic_scope_can_complete_deterministically() -> None:
    requirement = CompletionRequirement(
        requirement_id="synthetic-project", definition_state=DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
        required=True, source_artifact_id="synthetic-rubric", source_sha256=SHA, activity_version="synthetic-v1",
    )
    result = RequirementResult(
        requirement_id="synthetic-project", state=RequirementState.APPROVED, assessed_version="synthetic-v1",
    )
    first = project_completion("synthetic-phase", (requirement,), {requirement.requirement_id: result})
    second = project_completion("synthetic-phase", (requirement,), {requirement.requirement_id: result})
    assert first == second
    assert first.state == ScopeCompletion.COMPLETED


def test_empty_completion_policy_is_blocked_instead_of_success() -> None:
    projection = project_completion("phase", (), {})
    assert projection.state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
    assert projection.unresolved_requirement_ids == ("NO_DEFINED_REQUIREMENTS",)


def test_assessment_is_pinned_to_the_exact_rubric_version() -> None:
    rubric = _approved_synthetic_rubric()
    command = _command(rubric).model_copy(update={"rubric_version": "synthetic-v2"})
    with pytest.raises(AssessmentBlocked, match="versão da rubrica"):
        validate_assessment_decision(rubric, command)


def test_real_first_phase_criteria_remain_blocked_when_no_policy_is_approved() -> None:
    import os
    from pathlib import Path

    source = os.environ.get("TRILHACODE_BETA4_SOURCE_ROOT", "").strip()
    if not source:
        pytest.skip("Fonte curricular revisada não foi montada em modo somente leitura")
    from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase

    batch = convert_first_phase(Path(source), source_revision="migration@147dc68:tracked-clean-first-phase-files")
    assert len(batch.units) == 10
    projection = project_curriculum_completion(batch.units, {})
    assert set(projection["units"]) == {unit.provenance.source_id for unit in batch.units}
    assert len(projection["modules"]) == 3
    assert all(row.state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
               for row in projection["units"].values())
    assert all(row.state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
               for row in projection["modules"].values())
    assert projection["phase"].state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
    project_row = projection["units"]["3.5"]
    assert "project:3.5:approved-rubric-assessment" in project_row.unresolved_requirement_ids
    source_project = next(unit for unit in batch.units if unit.provenance.source_id == "3.5")
    project_rubric = next(item for item in source_project.project_materials if item.kind == "rubric")
    expected_rubric_version = f"source-{project_rubric.sha256[:16]}"
    rubric_result = RequirementResult(
        requirement_id="project:3.5:approved-rubric-assessment",
        state=RequirementState.APPROVED,
        assessed_version=expected_rubric_version,
    )
    completed = project_curriculum_completion(
        batch.units,
        {"project:3.5:approved-rubric-assessment": rubric_result},
    )
    assert completed["phase"].state == ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA


def test_phase_completion_requires_the_project_35_unit() -> None:
    unit = type("SyntheticUnit", (), {
        "provenance": type("SyntheticProvenance", (), {"source_id": "1.1"})(),
    })()
    with pytest.raises(ValueError, match="precisa incluir o projeto 3.5"):
        project_curriculum_completion((unit,), {})
