"""Strict HTTP input contracts for the isolated Beta 7.1 preview surface."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class QuizAttemptIn(_StrictInput):
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selected_option_id: str = Field(min_length=1, max_length=64)


class ExerciseSubmissionIn(_StrictInput):
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    unit_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answer_text: str = Field(min_length=1, max_length=40_000)


class ProjectDeliveryIn(_StrictInput):
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    delivery_text: str = Field(min_length=1, max_length=80_000)


class ProjectReviewIn(_StrictInput):
    expected_revision: int = Field(ge=0)
    outcome: Literal["feedback_only", "needs_revision"]
    feedback: str = Field(min_length=1, max_length=20_000)
