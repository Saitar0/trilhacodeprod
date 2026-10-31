"""Loss-accounted criteria-of-completion contract for isolated curriculum work."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CriterionKind(StrEnum):
    READING_COMPLETED = "reading_completed"
    QUIZ_ANSWERED = "quiz_answered"
    QUIZ_PASSED = "quiz_passed"
    EXERCISE_SUBMITTED = "exercise_submitted"
    EXERCISE_GRADED = "exercise_graded"
    PROJECT_EVALUATED = "project_evaluated"
    MASTERY_DEMONSTRATED = "mastery_demonstrated"
    UNIT_COMPLETED = "unit_completed"
    UNSTRUCTURED = "unstructured"


class EvaluationMode(StrEnum):
    AUTOMATIC = "automatic"
    HUMAN = "human"
    SOURCE_TEXT_ONLY = "source_text_only"
    DECISION_REQUIRED = "decision_required"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class CompletionRule(_StrictModel):
    criterion_id: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    kind: CriterionKind = CriterionKind.UNSTRUCTURED
    evaluation: EvaluationMode = EvaluationMode.SOURCE_TEXT_ONLY
    activity_id: str | None = None
    evidence_required: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    requires_human_review: bool = True
    automated_threshold: None = None
    provenance_artifact_id: str | None = None
    provenance_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def conservative_automation(self) -> CompletionRule:
        if self.evaluation in {EvaluationMode.SOURCE_TEXT_ONLY, EvaluationMode.DECISION_REQUIRED}:
            if not self.requires_human_review:
                raise ValueError("Critério textual ou ambíguo não pode ser automaticamente conclusivo")
        if self.kind == CriterionKind.UNSTRUCTURED and self.automated_threshold is not None:
            raise ValueError("Critério semântico não aceita limiar automático inventado")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError("Dependências duplicadas no critério")
        return self


class CompletionCriteriaContract(_StrictModel):
    contract_version: str = "trilhacode.beta5.completion/1.0"
    unit_id: str = Field(min_length=1)
    rules: tuple[CompletionRule, ...] = ()
    source_absent: bool = False

    @model_validator(mode="after")
    def validate_scope(self) -> CompletionCriteriaContract:
        ids = [rule.criterion_id for rule in self.rules]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de critério duplicados")
        if any(rule.unit_id != self.unit_id for rule in self.rules):
            raise ValueError("Critério associado a outra unidade")
        if self.source_absent and self.rules:
            raise ValueError("Origem marcada ausente não pode conter critérios")
        return self
