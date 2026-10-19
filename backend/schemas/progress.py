# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict


class ProgressIn(BaseModel):
    node_id: str
    status: str
    block_id: str | None = None
    data: dict = {}


class VisitIn(BaseModel):
    node_id: str


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
