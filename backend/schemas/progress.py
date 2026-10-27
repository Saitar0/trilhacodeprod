# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict, Field


class ProgressIn(BaseModel):
    node_id: str
    status: str
    block_id: str | None = None
    data: dict = Field(default_factory=dict)
    operation_id: str | None = Field(default=None, min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    attempt_id: str | None = Field(default=None, min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    expected_revision: int | None = Field(default=None, ge=0)


class VisitIn(BaseModel):
    node_id: str
    operation_id: str | None = Field(default=None, min_length=16, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


class ProgressOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str


class TrackProgressOut(BaseModel):
    nodes: dict[str, ProgressOut]
    blocks: dict[str, ProgressOut]
    state: dict | None = None
    locks: dict = {}


class ProgressOverviewOut(BaseModel):
    states: list[dict]
    completed: dict[str, int]
