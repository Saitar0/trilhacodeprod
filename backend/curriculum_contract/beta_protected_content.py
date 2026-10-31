"""Experimental field-level privacy contracts for staged curriculum content.

These DTOs are not an operational ACL. No route or runtime reader imports this
module. Student projections use explicit allowlists and never serialize the
restricted or system portions of a record.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataClassification(StrEnum):
    STUDENT_PUBLIC = "STUDENT_PUBLIC"
    INSTRUCTOR_RESTRICTED = "INSTRUCTOR_RESTRICTED"
    SYSTEM_INTERNAL = "SYSTEM_INTERNAL"


class DisclosurePolicy(StrEnum):
    PENDING_DECISION = "PENDING_DECISION"
    NEVER = "NEVER"
    AFTER_SUBMISSION = "AFTER_SUBMISSION"
    AFTER_HUMAN_GRADING = "AFTER_HUMAN_GRADING"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class PublicOption(_StrictModel):
    id: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=2000)


class StudentQuizQuestion(_StrictModel):
    question_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    prompt: str = Field(min_length=1, max_length=20_000)
    options: tuple[PublicOption, ...] = Field(min_length=2, max_length=8)
    schema_version: int = Field(ge=1)

    @model_validator(mode="after")
    def unique_options(self) -> StudentQuizQuestion:
        ids = [option.id for option in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de alternativa duplicados")
        return self


class RestrictedQuizAnswer(_StrictModel):
    question_id: str = Field(min_length=1)
    correct_option_id: str = Field(min_length=1)
    explanation: str = ""
    disclosure: DisclosurePolicy = DisclosurePolicy.PENDING_DECISION


class ProjectionGrantEvidence(_StrictModel):
    """Synthetic contract input; this is not a replacement for the active IAM."""

    subject_id: str = Field(min_length=1)
    grant_id: str = Field(min_length=1)
    grant_track_id: str = Field(min_length=1)
    operations: tuple[str, ...]


class ProtectedQuizQuestion(_StrictModel):
    track_id: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    student: StudentQuizQuestion
    instructor: RestrictedQuizAnswer
    classification: DataClassification = DataClassification.STUDENT_PUBLIC

    @model_validator(mode="after")
    def matching_private_answer(self) -> ProtectedQuizQuestion:
        if self.student.question_id != self.instructor.question_id:
            raise ValueError("Resposta restrita pertence a outra questão")
        option_ids = {option.id for option in self.student.options}
        if self.instructor.correct_option_id not in option_ids:
            raise ValueError("Gabarito não corresponde às alternativas públicas")
        return self

    def student_projection(self) -> dict:
        return self.student.model_dump(mode="json")

    def instructor_projection(self, evidence: ProjectionGrantEvidence) -> dict:
        if (
            evidence.grant_track_id != self.track_id
            or "curriculum.read_restricted" not in evidence.operations
        ):
            raise PermissionError("Autorização de leitura restrita ausente para esta trilha")
        return {**self.student_projection(), **self.instructor.model_dump(mode="json")}


class StudentExercise(_StrictModel):
    exercise_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    instructions: tuple[str, ...] = ()


class RestrictedExerciseGuidance(_StrictModel):
    exercise_id: str = Field(min_length=1)
    reference_answer: str | None = None
    rubric: tuple[str, ...] = ()
    disclosure: DisclosurePolicy = DisclosurePolicy.PENDING_DECISION


class ProtectedManualExercise(_StrictModel):
    track_id: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    student: StudentExercise
    instructor: RestrictedExerciseGuidance
    classification: DataClassification = DataClassification.STUDENT_PUBLIC

    @model_validator(mode="after")
    def matching_restricted_guidance(self) -> ProtectedManualExercise:
        if self.student.exercise_id != self.instructor.exercise_id:
            raise ValueError("Rubrica pertence a outro exercício")
        return self

    def student_projection(self) -> dict:
        return self.student.model_dump(mode="json")

    def instructor_projection(self, evidence: ProjectionGrantEvidence) -> dict:
        if (
            evidence.grant_track_id != self.track_id
            or "curriculum.read_restricted" not in evidence.operations
        ):
            raise PermissionError("Autorização de leitura restrita ausente para esta trilha")
        return {**self.student_projection(), **self.instructor.model_dump(mode="json")}
