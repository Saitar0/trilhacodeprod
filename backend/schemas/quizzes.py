"""Public and private API shapes for versioned quizzes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuizAPIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class QuizAnswerIn(QuizAPIModel):
    question_id: str = Field(min_length=1, max_length=100)
    option_id: str = Field(min_length=1, max_length=100)


class QuizAttemptIn(QuizAPIModel):
    version_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")
    answers: list[QuizAnswerIn] = Field(max_length=250)


class QuizRecoveryIn(QuizAPIModel):
    version_id: str = Field(pattern=r"^[0-9a-fA-F]{24}$")
    idempotency_key: str | None = Field(default=None, min_length=16, max_length=128)


class QuizOptionOut(QuizAPIModel):
    option_id: str
    text: str


class QuizQuestionOut(QuizAPIModel):
    question_id: str
    order: int
    prompt: str
    options: list[QuizOptionOut]


class QuizPublicOut(QuizAPIModel):
    quiz_id: str
    version_id: str
    curriculum_ref: str | None
    title: str
    questions: list[QuizQuestionOut]
    attempts_used: int = Field(ge=0, le=3)
    attempts_remaining: int = Field(ge=0, le=3)
    passed: bool
    best_score_percent: float | None
    review_available: bool


class QuizAttemptOut(QuizAPIModel):
    attempt_id: str
    quiz_id: str
    version_id: str
    attempt_number: int = Field(ge=1, le=3)
    total_questions: int = Field(ge=1)
    score_percent: float = Field(ge=0, le=100)
    passed: bool
    attempts_used: int = Field(ge=1, le=3)
    attempts_remaining: int = Field(ge=0, le=2)
    best_score_percent: float = Field(ge=0, le=100)
    review_available: bool
    submitted_at: datetime


class QuizRecoveryOut(QuizAPIModel):
    state: Literal["confirmed", "latest_confirmed", "unknown"]
    quiz_id: str
    version_id: str
    attempts_used: int = Field(ge=0, le=3)
    attempts_remaining: int = Field(ge=0, le=3)
    review_available: bool
    attempt: QuizAttemptOut | None
    may_still_be_processing: bool


class QuizHistoryOut(QuizAPIModel):
    items: list[QuizAttemptOut]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=500)
    skip: int = Field(ge=0)


class QuizReviewOptionOut(QuizAPIModel):
    option_id: str
    text: str
    correct: bool


class QuizReviewQuestionOut(QuizAPIModel):
    question_id: str
    order: int
    prompt: str
    options: list[QuizReviewOptionOut]
    explanation: str | None


class QuizReviewOut(QuizAPIModel):
    quiz_id: str
    version_id: str
    title: str
    questions: list[QuizReviewQuestionOut]


class QuizVersionPublishedOut(QuizAPIModel):
    quiz_id: str
    version_id: str
    title: str
    question_count: int = Field(ge=1)
    created_at: datetime
