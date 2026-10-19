# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict


class TaxonomyIn(BaseModel):
    group: str
    key: str
    label: str
    description: str = ""
    color: str = "slate"
    order: float = 0


class TaxonomyUpdate(BaseModel):
    label: str | None = None
    description: str | None = None
    color: str | None = None
    order: float | None = None


class TagIn(BaseModel):
    name: str
    color: str = "slate"


class BlockTypeIn(BaseModel):
    key: str
    label: str
    category: str = "recurso"
    icon: str = "Square"
    description: str = ""
    fields: list[dict] = []
    capabilities: list[str] = []
    enabled: bool = True


class BlockTypeUpdate(BaseModel):
    label: str | None = None
    category: str | None = None
    icon: str | None = None
    description: str | None = None
    fields: list[dict] | None = None
    capabilities: list[str] | None = None
    enabled: bool | None = None


class TaxonomyOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str


class MetaOut(BaseModel):
    taxonomies: dict[str, list[TaxonomyOut]]
    block_types: list[TaxonomyOut]
    tags: list[TaxonomyOut]
    statuses: list[str]
    progress_statuses: list[str]
    roles: list[str]
    default_hierarchy: list[str]
    default_labels: dict[str, str]
