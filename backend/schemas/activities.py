"""Strict request and response models for student activity attempts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ActivityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AttemptCreateIn(ActivityRequest):
    published_version_id: str = Field(min_length=1, max_length=64)


class DraftUpdateIn(ActivityRequest):
    selected_option_id: str | None = Field(default=None, min_length=1, max_length=64)
    expected_revision: int = Field(ge=0)


class AttemptSubmitIn(ActivityRequest):
    selected_option_id: str = Field(min_length=1, max_length=64)
    expected_revision: int = Field(ge=0)


class ActivityOptionOut(BaseModel):
    id: str
    label: str


class PublishedActivityOut(BaseModel):
    activity_id: str
    activity_schema_version: int
    published_version_id: str
    activity_revision: int
    prompt: str
    options: list[ActivityOptionOut]
    completion_policy: Literal["responded"]
    max_attempts: int
    evaluator_version: str


class AttemptResultOut(BaseModel):
    is_correct: bool
    score: int
    evaluator_version: str


class AttemptOut(BaseModel):
    id: str
    user_id: str
    track_id: str
    node_id: str
    activity_id: str
    published_version_id: str
    activity_revision: int
    attempt_number: int
    state: Literal["draft", "submitted", "evaluated"]
    response: dict | None = None
    revision: int
    result: AttemptResultOut | None = None
    feedback: str | None = None
    projection_status: Literal["pending", "complete"]
    created_at: str
    updated_at: str
    submitted_at: str | None = None
    evaluated_at: str | None = None
    activity: PublishedActivityOut


class AttemptListOut(BaseModel):
    items: list[AttemptOut]
    limit: int
    skip: int
    total: int
