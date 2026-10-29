"""Typed, provenance-preserving project contract based on the Beta 4 source."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from curriculum_contract.beta_protected_content import DataClassification


class ProjectArtifactKind(StrEnum):
    PROJECT_BRIEF = "project_brief"
    MILESTONE = "milestone"
    RUBRIC = "rubric"
    CHECKLIST = "checklist"
    THEORY = "theory"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class ProjectArtifactReference(_StrictModel):
    """Provenance-only inventory entry; it contains no curricular body."""

    artifact_id: str = Field(min_length=1)
    kind: ProjectArtifactKind
    source_path: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    order: int = Field(ge=0)
    source_item_ids: tuple[str, ...] = ()


class ProjectArtifact(_StrictModel):
    artifact_id: str = Field(min_length=1)
    kind: ProjectArtifactKind
    purpose: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    order: int = Field(ge=0)
    project_id: str = Field(min_length=1)
    phase_id: str = Field(min_length=1)
    source_item_ids: tuple[str, ...] = ()
    title: str | None = None
    student_content: str | None = None
    restricted_content: str | None = None
    internal_content: str | None = None
    classification: DataClassification
    visibility_decision: str = "PENDING_OWNER_REVIEW"

    @model_validator(mode="after")
    def content_classification_is_exclusive(self) -> ProjectArtifact:
        nonempty = [
            self.student_content is not None,
            self.restricted_content is not None,
            self.internal_content is not None,
        ]
        if sum(nonempty) != 1:
            raise ValueError("Artefato deve ter exatamente uma classificação de conteúdo")
        if self.classification == DataClassification.STUDENT_PUBLIC and self.student_content is None:
            raise ValueError("Conteúdo público deve estar no campo público")
        if self.classification == DataClassification.INSTRUCTOR_RESTRICTED and self.restricted_content is None:
            raise ValueError("Material restrito deve estar no campo do instrutor")
        if self.classification == DataClassification.SYSTEM_INTERNAL and self.internal_content is None:
            raise ValueError("Conteúdo interno deve estar no campo de sistema")
        return self


class ProjectInstruction(_StrictModel):
    artifact_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    classification: DataClassification = DataClassification.STUDENT_PUBLIC
    visibility_decision: str = "PENDING_OWNER_REVIEW"


class ProjectStep(_StrictModel):
    step_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    instruction_artifact_id: str = Field(min_length=1)
    acceptance_artifact_id: str | None = None
    title: str | None = None


class ProjectDeliverable(_StrictModel):
    deliverable_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required_evidence: tuple[str, ...] = ()
    source_artifact_id: str | None = None
    evaluation_required: bool = True


class ProjectRubric(_StrictModel):
    artifact_id: str = Field(min_length=1)
    raw_content: str = Field(min_length=1)
    classification: DataClassification = DataClassification.INSTRUCTOR_RESTRICTED
    criteria: tuple[str, ...] = ()
    criteria_parsed: bool = False


class ProjectCompletionRule(_StrictModel):
    source_artifact_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    automated: bool = False
    human_decision_required: bool = True


class ProjectSubmissionEvidence(_StrictModel):
    """Shape for a future submission; it contains no learner identity or content."""

    evidence_id: str = Field(min_length=1)
    artifact_kind: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    submitted_at: str | None = None
    evaluation_state: str = "NOT_EVALUATED"


class ProjectPackage(_StrictModel):
    contract_version: str = "trilhacode.beta5.project/1.0"
    project_id: str = "3.5"
    phase_id: str = "1"
    title: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_revision: str = Field(min_length=1)
    artifacts: tuple[ProjectArtifact, ...] = Field(min_length=1)
    steps: tuple[ProjectStep, ...] = ()
    deliverables: tuple[ProjectDeliverable, ...] = ()
    rubrics: tuple[ProjectRubric, ...] = ()
    completion_rules: tuple[ProjectCompletionRule, ...] = ()
    visibility_decision: str = "PENDING_OWNER_REVIEW"

    @model_validator(mode="after")
    def validate_artifact_graph(self) -> ProjectPackage:
        ids = [artifact.artifact_id for artifact in self.artifacts]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de artefato de projeto duplicados")
        if any(
            artifact.project_id != self.project_id or artifact.phase_id != self.phase_id
            for artifact in self.artifacts
        ):
            raise ValueError("Artefato associado a outro projeto ou fase")
        known = set(ids)
        for step in self.steps:
            if step.instruction_artifact_id not in known:
                raise ValueError("Etapa referencia instrução inexistente")
            if step.acceptance_artifact_id and step.acceptance_artifact_id not in known:
                raise ValueError("Etapa referencia checklist inexistente")
        if [step.order for step in self.steps] != list(range(1, len(self.steps) + 1)):
            raise ValueError("Ordem das etapas do projeto deve ser contínua")
        return self


def project_package_from_converted_unit(unit) -> ProjectPackage:
    """Adapt Beta 4's 3.5 ProjectMaterial records without rewriting their body."""
    if unit.provenance.source_id != "3.5":
        raise ValueError("Projeto 3.5 exige a unidade curricular de origem 3.5")
    artifacts: list[ProjectArtifact] = []
    source_by_id = {item.artifact_id: item for item in unit.source_artifacts}
    for material in unit.project_materials:
        source = source_by_id.get(material.artifact_id)
        if source is None:
            raise ValueError("Material de projeto sem artefato de origem correspondente")
        restricted = material.kind in {"rubric", "checklist"}
        kind = ProjectArtifactKind(material.kind)
        purpose = {
            ProjectArtifactKind.PROJECT_BRIEF: "project_instructions",
            ProjectArtifactKind.MILESTONE: "milestone_instructions",
            ProjectArtifactKind.RUBRIC: "evaluation_rubric",
            ProjectArtifactKind.CHECKLIST: "acceptance_checklist",
            ProjectArtifactKind.THEORY: "project_context",
        }[kind]
        artifacts.append(ProjectArtifact(
            artifact_id=material.artifact_id,
            kind=kind,
            purpose=purpose,
            source_path=material.relative_path,
            content_sha256=material.sha256,
            order=material.order,
            project_id="3.5",
            phase_id="1",
            source_item_ids=material.source_item_ids,
            student_content=None if restricted else material.content,
            restricted_content=material.content if restricted else None,
            classification=(
                DataClassification.INSTRUCTOR_RESTRICTED if restricted
                else DataClassification.STUDENT_PUBLIC
            ),
            visibility_decision="PENDING_OWNER_REVIEW",
        ))

    artifact_ids = {artifact.artifact_id for artifact in artifacts}
    steps: list[ProjectStep] = []
    for material in sorted(unit.project_materials, key=lambda item: item.order):
        milestone_ids = [item for item in material.source_item_ids if re.fullmatch(r"M\d{2}", item)]
        if material.kind != "milestone" or not milestone_ids:
            continue
        milestone_id = milestone_ids[0]
        checklist = next((
            candidate for candidate in unit.project_materials
            if candidate.kind == "checklist" and milestone_id in candidate.source_item_ids
        ), None)
        steps.append(ProjectStep(
            step_id=milestone_id,
            order=len(steps) + 1,
            instruction_artifact_id=material.artifact_id,
            acceptance_artifact_id=checklist.artifact_id if checklist else None,
        ))
    rubric = next((artifact for artifact in artifacts if artifact.kind == ProjectArtifactKind.RUBRIC), None)
    rubric_rows = (ProjectRubric(
        artifact_id=rubric.artifact_id,
        raw_content=rubric.restricted_content or "",
        classification=DataClassification.INSTRUCTOR_RESTRICTED,
        criteria=(),
        criteria_parsed=False,
    ),) if rubric else ()
    checklist_ids = {
        artifact.artifact_id for artifact in artifacts if artifact.kind == ProjectArtifactKind.CHECKLIST
    }
    if not checklist_ids.issubset(artifact_ids):
        raise ValueError("Checklist de projeto não possui artefato tipado")
    return ProjectPackage(
        project_id="3.5",
        phase_id="1",
        title=unit.title,
        source_sha256=unit.provenance.source_sha256,
        source_revision=unit.provenance.source_revision,
        artifacts=tuple(artifacts),
        steps=tuple(steps),
        rubrics=rubric_rows,
        completion_rules=tuple(
            ProjectCompletionRule(
                source_artifact_id=item.artifact_id,
                source_text=item.body,
                automated=False,
                human_decision_required=True,
            )
            for item in source_by_id.values() if item.kind == "criterio"
        ),
    )
