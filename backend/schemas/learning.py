# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict, Field


class NoteIn(BaseModel):
    node_id: str
    block_id: str | None = None
    body: str = Field(max_length=50_000)
    expected_version: int | None = Field(default=None, ge=0)


class NoteDeletedOut(BaseModel):
    deleted: bool
    version: int


class ReviewIn(BaseModel):
    node_id: str
    block_id: str | None = None
    when: str = "soon"
    due_at: str | None = None
    note: str = ""


class ReviewDone(BaseModel):
    outcome: str = "ok"
    reschedule: str | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str


class ReviewOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
