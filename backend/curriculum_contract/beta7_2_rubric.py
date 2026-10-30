"""Versioned, fail-closed rubric contracts for the isolated Beta 7.2 workflow.

Validation proves structural consistency only. It never constitutes human
pedagogical approval of a rubric.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RubricState(StrEnum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    PEDAGOGICALLY_APPROVED = "PEDAGOGICALLY_APPROVED"
    RETIRED = "RETIRED"


class VersionCompatibility(StrEnum):
    UNASSESSED = "UNASSESSED"
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class DefinitionState(StrEnum):
    SOURCE_DEFINED = "SOURCE_DEFINED"
    SOURCE_DEFINED_BUT_AMBIGUOUS = "SOURCE_DEFINED_BUT_AMBIGUOUS"
    FORMALIZED_WITHOUT_SEMANTIC_CHANGE = "FORMALIZED_WITHOUT_SEMANTIC_CHANGE"
    PROPOSED_REQUIRES_APPROVAL = "PROPOSED_REQUIRES_APPROVAL"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_VERIFIED = "NOT_VERIFIED"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class RubricProvenance(_StrictModel):
    source_revision: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    source_artifact_id: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_state: str = Field(min_length=1)
    source_section: str = Field(min_length=1)


class PerformanceDescriptor(_StrictModel):
    score: int = Field(ge=0, le=4)
    description: str = Field(min_length=1)


class RubricCriterion(_StrictModel):
    criterion_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    definition_state: DefinitionState
    required: bool | None
    provenance: RubricProvenance
    descriptors: tuple[PerformanceDescriptor, ...] = ()
    observable_evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_descriptor_identity(self) -> RubricCriterion:
        scores = [item.score for item in self.descriptors]
        if len(scores) != len(set(scores)):
            raise ValueError("Descritores de rubrica possuem pontuações duplicadas")
        if self.required is None and self.definition_state == DefinitionState.SOURCE_DEFINED:
            raise ValueError("Critério definido na fonte precisa registrar sua obrigatoriedade")
        if self.definition_state in {
            DefinitionState.SOURCE_DEFINED_BUT_AMBIGUOUS,
            DefinitionState.PROPOSED_REQUIRES_APPROVAL,
            DefinitionState.NOT_VERIFIED,
        } and self.required is True:
            raise ValueError("Obrigatoriedade ambígua ou proposta não pode ser afirmada como fonte")
        return self


class RubricConstraint(_StrictModel):
    """A source rule that constrains acceptance without inventing a score rule."""

    constraint_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    definition_state: DefinitionState
    applies_to_criterion_ids: tuple[str, ...] = ()
    blocks_acceptance_when_violated: bool
    provenance: RubricProvenance


class RubricDecisionRule(_StrictModel):
    required_criterion_ids: tuple[str, ...] = Field(min_length=1)
    minimum_score: int = Field(ge=0, le=4)
    combination: str = "all_required_criteria_meet_minimum"


class RubricApproval(_StrictModel):
    approved_by: str = Field(min_length=1)
    approval_record_id: str = Field(min_length=1)
    approved_at: datetime
    decision_record: str = Field(min_length=1)


class VersionedRubric(_StrictModel):
    contract_version: str = "trilhacode.beta7_2.rubric/1.0"
    rubric_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    state: RubricState
    provenance: RubricProvenance
    criteria: tuple[RubricCriterion, ...] = Field(min_length=1)
    constraints: tuple[RubricConstraint, ...] = ()
    decision_rule: RubricDecisionRule | None = None
    approval: RubricApproval | None = None
    supersedes_version: str | None = None
    compatibility_with_previous: VersionCompatibility = VersionCompatibility.UNASSESSED
    canonical_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    synthetic_fixture: bool = False

    @model_validator(mode="after")
    def validate_version_policy(self) -> VersionedRubric:
        ids = [item.criterion_id for item in self.criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de critérios duplicados na rubrica")
        constraint_ids = [item.constraint_id for item in self.constraints]
        if len(constraint_ids) != len(set(constraint_ids)):
            raise ValueError("IDs de restrições duplicados na rubrica")
        if any(not set(item.applies_to_criterion_ids) <= set(ids) for item in self.constraints):
            raise ValueError("Restrição da rubrica referencia critério inexistente")
        provenance_rows = [item.provenance for item in (*self.constraints, *self.criteria)]
        if any(item.source_revision != self.provenance.source_revision
               or item.source_state != self.provenance.source_state for item in provenance_rows):
            raise ValueError("Critério ou restrição diverge da revisão/estado editorial da rubrica")
        if self.state in {RubricState.PEDAGOGICALLY_APPROVED, RubricState.RETIRED}:
            if self.state == RubricState.RETIRED and (self.approval is None) != (self.decision_rule is None):
                raise ValueError("Rubrica retirada deve preservar aprovação e regra em conjunto")
            if self.state == RubricState.RETIRED and self.approval is None:
                return self
            if self.approval is None or self.decision_rule is None:
                raise ValueError("Rubrica aprovada ou retirada exige decisão humana rastreável e regra explícita")
            if self.decision_rule.combination != "all_required_criteria_meet_minimum":
                raise ValueError("Regra de decisão desconhecida")
            criterion_map = {item.criterion_id: item for item in self.criteria}
            required = self.decision_rule.required_criterion_ids
            if not required or len(required) != len(set(required)) or not set(required) <= set(ids):
                raise ValueError("A regra da rubrica referencia critérios ausentes ou duplicados")
            if any(criterion_map[item].definition_state not in {
                DefinitionState.SOURCE_DEFINED,
                DefinitionState.FORMALIZED_WITHOUT_SEMANTIC_CHANGE,
            } for item in required):
                raise ValueError("Rubrica aprovada não pode depender de critérios indefinidos")
            if any(criterion_map[item].required is not True for item in required):
                raise ValueError("Regra de decisão só pode exigir critérios marcados como obrigatórios")
            if any(not criterion_map[item].descriptors for item in required):
                raise ValueError("Rubrica aprovada exige descritores para todos os critérios obrigatórios")
        elif self.approval is not None or self.decision_rule is not None:
            raise ValueError("Rubrica sem aprovação pedagógica não pode carregar regra decisória ativa")
        return self

    def content_hash(self) -> str:
        """Hash canonical content excluding the stored hash itself."""
        payload = self.model_dump(mode="json", exclude={"canonical_sha256"}, exclude_none=True)
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()


def can_approve(rubric: VersionedRubric) -> bool:
    """A proposal or draft can never authorize an approval decision."""
    return (
        rubric.state == RubricState.PEDAGOGICALLY_APPROVED
        and rubric.approval is not None
        and rubric.decision_rule is not None
        and (rubric.canonical_sha256 is None or rubric.canonical_sha256 == rubric.content_hash())
    )
