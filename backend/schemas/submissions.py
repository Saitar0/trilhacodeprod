# ruff: noqa: EXE002

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnswerIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_id: str = Field(min_length=1, max_length=64)
    answer: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    @field_validator("answer")
    @classmethod
    def validate_answer_size(cls, value):
        if set(value) - {"text", "code", "choice"}:
            raise ValueError("A resposta contém campos não permitidos")
        if any(isinstance(item, str) and len(item) > 25_000 for item in value.values()):
            raise ValueError("A resposta excede o limite permitido")
        if len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > 64_000:
            raise ValueError("A resposta excede o limite permitido")
        return value


class CriterionGrade(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion: str = Field(min_length=1, max_length=300)
    met: bool | None = None
    comment: str = Field(default="", max_length=2_000)
    score: float | None = None


class GradeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: Literal["approved", "rejected", "returned"]
    feedback: str = Field(default="", max_length=10_000)
    criteria: list[CriterionGrade] = Field(default_factory=list, max_length=50)
    score: float | None = None


class SubmissionHistoryOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    at: str | None = None
    by_name: str | None = None
    result: str | None = None


class SubmissionGradeOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: Literal["approved", "rejected", "returned"]
    feedback: str = ""
    criteria: list[CriterionGrade] | None = None
    score: float | None = None
    graded_by_name: str = ""
    graded_at: str | None = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str | None = None
    user_name: str | None = None
    track_id: str | None = None
    node_id: str | None = None
    node_title: str | None = None
    block_id: str | None = None
    block_type: str | None = None
    block_title: str | None = None
    attempt: int | None = None
    status: str | None = None
    answer: dict[str, object] | None = None
    grading: SubmissionGradeOut | None = None
    history: list[SubmissionHistoryOut] | None = None
    reviewer_name: str | None = None
    orphaned: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    submitted_at: str | None = None
    activity_version: str | None = None


class SubmissionListOut(BaseModel):
    items: list[SubmissionOut]
    counts: dict[str, int]


class SubmissionDetailOut(BaseModel):
    submission: SubmissionOut
    block: dict | None = None
    attempts: list[SubmissionOut]
