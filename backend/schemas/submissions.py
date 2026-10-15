# ruff: noqa: EXE002

from pydantic import BaseModel, ConfigDict


class AnswerIn(BaseModel):
    block_id: str
    answer: dict = {}


class CriterionGrade(BaseModel):
    criterion: str
    met: bool | None = None
    comment: str = ""
    score: float | None = None


class GradeIn(BaseModel):
    result: str
    feedback: str = ""
    criteria: list[CriterionGrade] = []
    score: float | None = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str


class SubmissionListOut(BaseModel):
    items: list[SubmissionOut]
    counts: dict[str, int]


class SubmissionDetailOut(BaseModel):
    submission: SubmissionOut
    block: dict | None = None
    attempts: list[SubmissionOut]
