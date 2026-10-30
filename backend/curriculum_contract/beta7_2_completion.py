"""Deterministic completion projections which fail closed on undefined rules."""

from __future__ import annotations

from enum import StrEnum
from typing import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field

from curriculum_contract.beta7_2_rubric import DefinitionState


class RequirementState(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    APPROVED = "APPROVED"
    BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA = "BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA"


class ScopeCompletion(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA = "BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA"
    COMPLETED = "COMPLETED"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CompletionRequirement(_StrictModel):
    requirement_id: str = Field(min_length=1)
    definition_state: DefinitionState
    required: bool | None
    source_artifact_id: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    activity_version: str | None = None


class RequirementResult(_StrictModel):
    requirement_id: str
    state: RequirementState
    assessed_version: str | None = None


class CompletionProjection(_StrictModel):
    scope_id: str
    state: ScopeCompletion
    required_count: int = Field(ge=0)
    approved_count: int = Field(ge=0)
    unresolved_requirement_ids: tuple[str, ...] = ()
    pending_requirement_ids: tuple[str, ...] = ()


def project_completion(
    scope_id: str,
    requirements: Sequence[CompletionRequirement],
    results: Mapping[str, RequirementResult],
) -> CompletionProjection:
    """Aggregate a unit/module/phase without treating missing policy as success."""
    ids = [item.requirement_id for item in requirements]
    if len(ids) != len(set(ids)):
        raise ValueError("Requisitos duplicados na projeção de conclusão")

    unresolved = tuple(sorted(
        item.requirement_id for item in requirements
        if item.required is None or item.definition_state in {
            DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
            DefinitionState.PROPOSED_REQUIRES_APPROVAL,
            DefinitionState.UNSUPPORTED,
            DefinitionState.NOT_VERIFIED,
        }
    ))
    applicable = [item for item in requirements if item.required is True]
    pending = tuple(sorted(
        item.requirement_id for item in applicable
        if (result := results.get(item.requirement_id)) is None
        or result.state != RequirementState.APPROVED
        or (item.activity_version is not None and result.assessed_version != item.activity_version)
    ))
    approved = len(applicable) - len(pending)
    if unresolved:
        state = ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
    elif pending:
        state = ScopeCompletion.INCOMPLETE
    else:
        # Empty policy cannot mean completion; require at least one defined item.
        state = ScopeCompletion.COMPLETED if applicable else ScopeCompletion.BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA
        if not applicable and not unresolved:
            unresolved = ("NO_DEFINED_REQUIREMENTS",)
    return CompletionProjection(
        scope_id=scope_id,
        state=state,
        required_count=len(applicable),
        approved_count=approved,
        unresolved_requirement_ids=unresolved,
        pending_requirement_ids=pending,
    )


def source_unit_requirement(unit) -> CompletionRequirement:
    """Preserve a source completion statement while requiring human operationalization.

    The source artifact defines a pedagogical target but does not provide a
    machine-verifiable evidence/decision protocol. It therefore cannot produce
    completion by itself.
    """
    if unit.completion_criterion is None:
        raise ValueError(f"Unidade {unit.provenance.source_id} não possui critério de origem")
    artifact = next((item for item in unit.source_artifacts if item.kind in {"criterion", "criterio"}), None)
    if artifact is None:
        raise ValueError(f"Critério da unidade {unit.provenance.source_id} não possui proveniência")
    return CompletionRequirement(
        requirement_id=f"unit:{unit.provenance.source_id}:completion-criterion",
        definition_state=DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
        required=True,
        source_artifact_id=artifact.artifact_id,
        source_sha256=artifact.sha256,
        activity_version=unit.provenance.source_sha256,
    )


def source_project_rubric_requirement(unit) -> CompletionRequirement:
    """The phase cannot complete without a source-linked project assessment."""
    material = next((item for item in unit.project_materials if item.kind == "rubric"), None)
    if material is None:
        raise ValueError("Projeto 3.5 sem rubrica de origem verificável")
    return CompletionRequirement(
        requirement_id="project:3.5:approved-rubric-assessment",
        definition_state=DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
        required=None,
        source_artifact_id=material.artifact_id,
        source_sha256=material.sha256,
        activity_version=f"source-{material.sha256[:16]}",
    )


def project_curriculum_completion(
    units: Sequence,
    results: Mapping[str, RequirementResult],
) -> dict[str, object]:
    """Project unit, module, and phase state from source-linked requirements."""
    if not units:
        raise ValueError("Não é possível projetar uma formação sem unidades")
    project_unit = next((unit for unit in units if unit.provenance.source_id == "3.5"), None)
    if project_unit is None:
        raise ValueError("A fase curricular precisa incluir o projeto 3.5")
    unit_requirements: dict[str, list[CompletionRequirement]] = {}
    for unit in units:
        requirements = [source_unit_requirement(unit)]
        if unit.provenance.source_id == "3.5":
            requirements.append(source_project_rubric_requirement(unit))
        unit_requirements[unit.provenance.source_id] = requirements
    unit_rows = {
        unit_id: project_completion(unit_id, requirements, results)
        for unit_id, requirements in unit_requirements.items()
    }
    modules: dict[str, list[CompletionRequirement]] = {}
    for unit in units:
        modules.setdefault(unit.module_id, []).extend(unit_requirements[unit.provenance.source_id])
    module_rows = {
        module_id: project_completion(f"module:{module_id}", requirements, results)
        for module_id, requirements in sorted(modules.items())
    }
    phase_requirements = [requirement for requirements in unit_requirements.values() for requirement in requirements]
    phase = project_completion("phase:1", phase_requirements, results)
    return {"units": unit_rows, "modules": module_rows, "phase": phase}
