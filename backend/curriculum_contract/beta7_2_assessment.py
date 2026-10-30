"""Version-bound project assessment records and decision checks (Beta 7.2)."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from curriculum_contract.beta7_2_rubric import (
    DefinitionState,
    PerformanceDescriptor,
    RubricConstraint,
    RubricCriterion,
    RubricProvenance,
    RubricState,
    VersionedRubric,
)
from curriculum_contract.beta_project_contract import ProjectPackage


class AssessmentOutcome(StrEnum):
    NEEDS_REVISION = "NEEDS_REVISION"
    APPROVED = "APPROVED"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class CriterionEvidence(_StrictModel):
    criterion_id: str = Field(min_length=1)
    score: int = Field(ge=0, le=4)
    evidence_text: str = Field(min_length=1, max_length=8_000)
    evidence_reference: str | None = Field(default=None, max_length=2_000)


class AssessmentCommand(_StrictModel):
    submission_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    project_version: str = Field(min_length=1)
    rubric_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    expected_revision: int = Field(ge=0)
    outcome: AssessmentOutcome
    feedback: str = Field(min_length=1, max_length=20_000)
    criteria: tuple[CriterionEvidence, ...] = ()

    @model_validator(mode="after")
    def unique_criteria(self) -> AssessmentCommand:
        ids = [item.criterion_id for item in self.criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("Evidências duplicadas para o mesmo critério")
        return self


class AssessmentRecord(_StrictModel):
    assessment_id: str = Field(min_length=1)
    operation_key: str = Field(min_length=8, max_length=128)
    submission_id: str = Field(min_length=1)
    learner_id: str = Field(min_length=1)
    reviewer_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    project_version: str = Field(min_length=1)
    rubric_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_revision: int = Field(ge=0)
    outcome: AssessmentOutcome
    feedback: str = Field(min_length=1)
    criteria: tuple[CriterionEvidence, ...] = ()
    previous_state: str = Field(min_length=1)
    resulting_state: str = Field(min_length=1)
    decided_at: datetime


class AssessmentBlocked(ValueError):
    """A pedagogical or versioning precondition prevents a decision."""


def validate_assessment_decision(rubric: VersionedRubric, command: AssessmentCommand) -> None:
    """Raise when an approval cannot be grounded in an approved exact rubric.

    Feedback and revision requests remain possible against a proposed rubric;
    approval is the only transition that requires an approved decision rule.
    """
    if command.project_id != rubric.project_id or command.rubric_id != rubric.rubric_id:
        raise AssessmentBlocked("A rubrica não corresponde ao projeto informado")
    if command.rubric_version != rubric.version:
        raise AssessmentBlocked("A versão da rubrica não corresponde à avaliação")
    if command.outcome != AssessmentOutcome.APPROVED:
        return
    from curriculum_contract.beta7_2_rubric import can_approve

    if not can_approve(rubric) or rubric.decision_rule is None:
        raise AssessmentBlocked("A aprovação está bloqueada até a aprovação pedagógica da rubrica")
    rule = rubric.decision_rule
    criterion_map = {item.criterion_id: item for item in command.criteria}
    if set(criterion_map) != set(rule.required_criterion_ids):
        raise AssessmentBlocked("A aprovação exige evidência para cada critério obrigatório")
    if any(not criterion_map[key].evidence_text.strip() for key in rule.required_criterion_ids):
        raise AssessmentBlocked("Há evidência obrigatória ausente")
    if any(criterion_map[key].score < rule.minimum_score for key in rule.required_criterion_ids):
        raise AssessmentBlocked("Um ou mais critérios não atingem a regra aprovada")


def proposed_rubric_from_project(
    project: ProjectPackage,
    *,
    source_revision: str,
    source_state: str,
) -> VersionedRubric:
    """Map the actual source descriptors without inventing an overall pass rule."""
    if len(project.rubrics) != 1:
        raise ValueError("Projeto deve conter exatamente uma rubrica de origem")
    source = project.rubrics[0]
    artifact = next((item for item in project.artifacts if item.artifact_id == source.artifact_id), None)
    if artifact is None:
        raise ValueError("Rubrica sem artefato de proveniência")
    markdown = source.raw_content
    descriptors: dict[int, str] = {}
    for match in re.finditer(r"(?<!\d)([0-4])\s*=\s*([^;.]+)", markdown):
        descriptors[int(match.group(1))] = match.group(2).strip()
    descriptor_rows = tuple(
        PerformanceDescriptor(score=score, description=descriptors[score])
        for score in range(4, -1, -1) if score in descriptors
    )
    if len(descriptor_rows) != 5:
        raise ValueError("Descritores 0–4 não foram integralmente encontrados na fonte")
    provenance = RubricProvenance(
        source_revision=source_revision,
        source_path=artifact.source_path,
        source_artifact_id=artifact.artifact_id,
        source_sha256=artifact.content_sha256,
        source_state=source_state,
        source_section="Rubrica comum para cada marco (0–4)",
    )
    criteria_rows: list[RubricCriterion] = []
    for step in project.steps:
        milestone = next((item for item in project.artifacts
                         if item.artifact_id == step.instruction_artifact_id), None)
        if milestone is None:
            raise ValueError(f"Marco {step.step_id} sem artefato de instruções verificável")
        evidence_rows: list[str] = []
        source_text = milestone.student_content or ""
        for label in ("Evidência", "Verificação"):
            evidence_match = re.search(
                rf"\*\*{label}:\*\*\s*(.*?)(?=\n\s*\n|\Z)", source_text, re.DOTALL,
            )
            if evidence_match:
                evidence_rows.append(f"{label}: {evidence_match.group(1).strip()}")
        milestone_provenance = RubricProvenance(
            source_revision=source_revision,
            source_path=milestone.source_path,
            source_artifact_id=milestone.artifact_id,
            source_sha256=milestone.content_sha256,
            source_state=source_state,
            source_section=f"Marco {step.step_id} — evidência e verificação",
        )
        criteria_rows.append(RubricCriterion(
            criterion_id=f"{project.project_id}:{step.step_id}",
            description=f"Rubrica fonte aplicada a {step.title or milestone.title or step.step_id}",
            definition_state=DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
            required=None,
            provenance=milestone_provenance,
            descriptors=descriptor_rows,
            observable_evidence=tuple(evidence_rows),
        ))
    criteria = tuple(criteria_rows)
    if not criteria:
        raise ValueError("Rubrica sem marcos associados")
    constraints: tuple[RubricConstraint, ...] = ()
    sensitive_data_rule = "Os marcos 3 e 4 não são aceitos enquanto houver credencial real ou dado pessoal versionado."
    if sensitive_data_rule.casefold() in markdown.casefold():
        criterion_by_step = {step.step_id: f"{project.project_id}:{step.step_id}" for step in project.steps}
        applies_to = tuple(
            criterion_by_step[step_id]
            for step_id in ("M03", "M04") if step_id in criterion_by_step
        )
        constraints = (RubricConstraint(
            constraint_id=f"{project.project_id}:source-sensitive-data-acceptance",
            description=sensitive_data_rule,
            definition_state=DefinitionState.SOURCE_DEFINED,
            applies_to_criterion_ids=applies_to,
            blocks_acceptance_when_violated=True,
            provenance=provenance,
        ),)
    return VersionedRubric(
        rubric_id=source.artifact_id,
        project_id=project.project_id,
        version=f"source-{artifact.content_sha256[:16]}",
        state=RubricState.PROPOSED,
        provenance=provenance,
        criteria=criteria,
        constraints=constraints,
        decision_rule=None,
        approval=None,
        synthetic_fixture=False,
    )
