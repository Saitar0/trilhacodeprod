"""Typed relationships and full reference metadata for isolated staging."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RelationScope(StrEnum):
    INTERNAL_TO_BATCH = "INTERNAL_TO_BATCH"
    EXTERNAL_NOT_LOADED = "EXTERNAL_NOT_LOADED"
    UNRESOLVED_SOURCE_REFERENCE = "UNRESOLVED_SOURCE_REFERENCE"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class CurricularRelation(_StrictModel):
    relation_id: str = Field(min_length=1)
    source_unit_id: str = Field(min_length=1)
    source_kind: str = Field(min_length=1)
    target_source_path: str = Field(min_length=1)
    target_unit_id: str | None = None
    target_anchor: str | None = None
    display_label: str | None = None
    scope: RelationScope
    enforced: bool = False
    provenance_artifact_id: str | None = None

    @model_validator(mode="after")
    def scope_consistency(self) -> CurricularRelation:
        if self.scope == RelationScope.INTERNAL_TO_BATCH and self.target_unit_id is None:
            raise ValueError("Relação interna deve resolver a unidade de destino")
        if self.scope != RelationScope.INTERNAL_TO_BATCH and self.enforced:
            raise ValueError("Relação externa ou não resolvida não pode ser pré-requisito ativo")
        return self


class CurricularReference(_StrictModel):
    reference_id: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    topic_id: str | None = None
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    description: str = ""
    url: str = Field(min_length=1)
    origin: str = Field(min_length=1)
    provenance_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
