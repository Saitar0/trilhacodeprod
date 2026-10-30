"""Isolated quiz API contract tests; this module is not production logic."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from curriculum_contract import (
    AnswerKeyBlock,
    QuizBlock,
    QuizPresentation,
    SourceProvenance,
    student_quiz_view,
)
from curriculum_contract.models import QuizOption


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PublicOption(StrictModel):
    ref: str
    text: str


class PublicQuiz(StrictModel):
    quiz_ref: str
    quiz_revision_ref: str
    type: Literal["quiz"]
    title: str
    order: int
    prompt: str
    format: Literal[
        "multiple_choice", "true_false", "short_answer", "ordering", "fill_code", "other"
    ]
    options: list[PublicOption]


class ChoiceResponse(StrictModel):
    kind: Literal["choice"]
    option_ref: str


class AttemptRequest(StrictModel):
    quiz_revision_ref: str
    placement_ref: str
    response: ChoiceResponse
    idempotency_key: UUID


class AnswerReveal(StrictModel):
    correct_option_ref: str
    explanation: str | None


class AttemptResult(StrictModel):
    attempt_ref: str
    quiz_ref: str
    quiz_revision_ref: str
    attempt_number: int
    status: Literal["recorded"]
    correct: bool | None
    answer_reveal: AnswerReveal | None


class StudentHistory(StrictModel):
    attempts: list[AttemptResult]


class ContractFailure(Exception):
    """Expected HTTP-like failure from the test-only contract simulator."""

    def __init__(self, status_code: int, code: str) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code


@dataclass(frozen=True)
class QuizRevision:
    quiz: QuizBlock
    answer_key: AnswerKeyBlock
    revision_ref: str


class InMemoryQuizContract:
    """Test fixture only: proposed contract behavior, with no route or database."""

    def __init__(
        self,
        quiz: QuizBlock,
        answer_key: AnswerKeyBlock,
        *,
        revision_ref: str = "f1-revisao-1",
        max_attempts: int = 2,
        reveal_policy: Literal["after_submission", "after_attempt_limit", "never"] = (
            "after_attempt_limit"
        ),
    ) -> None:
        if quiz.answer_key_ref != answer_key.ref:
            raise ValueError("quiz answer-key reference is not reciprocal")
        if answer_key.question_ref != quiz.ref:
            raise ValueError("answer key points to another question")
        if answer_key.correct_option_ref not in {option.ref for option in quiz.options}:
            raise ValueError("answer key option is not present in the quiz")
        self._current = QuizRevision(quiz, answer_key, revision_ref)
        self._max_attempts = max_attempts
        self._reveal_policy = reveal_policy
        self._history: dict[str, list[AttemptResult]] = {}
        self._idempotency: dict[tuple[str, UUID], tuple[str, AttemptResult]] = {}

    def public_quiz(self) -> PublicQuiz:
        presentation: QuizPresentation = student_quiz_view(self._current.quiz)
        return PublicQuiz(
            quiz_ref=presentation.ref,
            quiz_revision_ref=self._current.revision_ref,
            type=presentation.type,
            title=presentation.title,
            order=presentation.order,
            prompt=presentation.prompt,
            format=presentation.format,
            options=[
                PublicOption(ref=option.ref, text=option.text) for option in presentation.options
            ],
        )

    def submit(
        self,
        request: AttemptRequest,
        *,
        principal_id: str | None,
        unlocked: bool = True,
    ) -> AttemptResult:
        if not principal_id:
            raise ContractFailure(401, "AUTHENTICATION_REQUIRED")
        if not unlocked:
            raise ContractFailure(403, "QUIZ_LOCKED")
        fingerprint = json.dumps(
            request.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        idempotency_ref = (principal_id, request.idempotency_key)
        prior = self._idempotency.get(idempotency_ref)
        if prior is not None:
            if prior[0] != fingerprint:
                raise ContractFailure(409, "IDEMPOTENCY_KEY_REUSED")
            return prior[1]
        revision = self._current
        if request.quiz_revision_ref != revision.revision_ref:
            raise ContractFailure(409, "QUIZ_REVISION_STALE")
        if revision.quiz.format != "multiple_choice":
            raise ContractFailure(422, "QUIZ_FORMAT_NOT_SUPPORTED")
        valid_options = {option.ref for option in revision.quiz.options}
        selected = request.response.option_ref
        if selected not in valid_options:
            raise ContractFailure(422, "OPTION_NOT_IN_QUIZ")
        attempts = self._history.setdefault(principal_id, [])
        if len(attempts) >= self._max_attempts:
            raise ContractFailure(409, "ATTEMPTS_EXHAUSTED")
        attempt_number = len(attempts) + 1
        reached_reveal = self._reveal_policy == "after_submission" or (
            self._reveal_policy == "after_attempt_limit" and attempt_number >= self._max_attempts
        )
        is_correct = selected == revision.answer_key.correct_option_ref
        answer_reveal = None
        if reached_reveal and self._reveal_policy != "never":
            correct_option_ref = revision.answer_key.correct_option_ref
            if correct_option_ref is None:
                raise ContractFailure(422, "ANSWER_KEY_INVALID")
            answer_reveal = AnswerReveal(
                correct_option_ref=correct_option_ref,
                explanation=revision.answer_key.explanation,
            )
        result = AttemptResult(
            attempt_ref=f"{revision.quiz.ref}-tentativa-{attempt_number}",
            quiz_ref=revision.quiz.ref,
            quiz_revision_ref=revision.revision_ref,
            attempt_number=attempt_number,
            status="recorded",
            correct=is_correct if reached_reveal else None,
            answer_reveal=answer_reveal,
        )
        attempts.append(result)
        self._idempotency[idempotency_ref] = (fingerprint, result)
        return result

    def student_history(self, principal_id: str) -> StudentHistory:
        return StudentHistory(attempts=list(self._history.get(principal_id, [])))

    def admin_answer_key(self, *, permissions: set[str]) -> AnswerKeyBlock:
        if "quiz.answer_key.read" not in permissions:
            raise ContractFailure(403, "ANSWER_KEY_PERMISSION_REQUIRED")
        return self._current.answer_key

    def publish_revision(self, revision_ref: str) -> None:
        self._current = QuizRevision(self._current.quiz, self._current.answer_key, revision_ref)


def provenance() -> SourceProvenance:
    return SourceProvenance(
        source_file="Conteudos_migrado/Fase_1/1.1_Teste/01_conceito/01_teoria.md",
        source_sha256="a" * 64,
        manifest_ref="f1-unidade-1",
        source_role="quiz_contract_fixture",
    )


def quiz_block(
    format_: Literal[
        "multiple_choice", "true_false", "short_answer", "ordering", "fill_code", "other"
    ] = "multiple_choice",
) -> QuizBlock:
    return QuizBlock(
        ref="f1-quiz-relacoes",
        type="quiz",
        owner_ref="f1-assunto-relacoes",
        order=1,
        title="Questão 1",
        status="published",
        shared=False,
        provenance=provenance(),
        prompt="Qual opção representa a resposta correta?",
        format=format_,
        options=[
            QuizOption(ref="op-a", text="Alternativa A"),
            QuizOption(ref="op-b", text="Alternativa B"),
        ],
        answer_key_required=True,
        answer_key_ref="f1-gabarito-relacoes",
    )


def answer_key(question_ref: str = "f1-quiz-relacoes") -> AnswerKeyBlock:
    return AnswerKeyBlock(
        ref="f1-gabarito-relacoes",
        type="answer_key",
        owner_ref="f1-assunto-relacoes",
        order=2,
        title="Gabarito da questão 1",
        status="published",
        shared=False,
        provenance=provenance(),
        question_ref=question_ref,
        correct_option_ref="op-b",
        accepted_answers=[],
        expected_answer=None,
        explanation="A alternativa B corresponde ao conceito apresentado.",
        source_markdown="**Resposta:** B\n",
    )


def service(
    *,
    max_attempts: int = 2,
    reveal_policy: Literal["after_submission", "after_attempt_limit", "never"] = (
        "after_attempt_limit"
    ),
) -> InMemoryQuizContract:
    return InMemoryQuizContract(
        quiz_block(),
        answer_key(),
        max_attempts=max_attempts,
        reveal_policy=reveal_policy,
    )


def request(
    *,
    revision: str = "f1-revisao-1",
    option: str = "op-a",
    key: str = "00000000-0000-0000-0000-000000000001",
) -> AttemptRequest:
    return AttemptRequest(
        quiz_revision_ref=revision,
        placement_ref="f1-colocacao-relacoes",
        response=ChoiceResponse(kind="choice", option_ref=option),
        idempotency_key=UUID(key),
    )


def test_intermediate_quiz_and_answer_key_are_reciprocal() -> None:
    question = quiz_block()
    key = answer_key()
    assert question.answer_key_ref == key.ref
    assert key.question_ref == question.ref
    assert [option.ref for option in question.options] == ["op-a", "op-b"]


def test_public_view_is_allowlisted_and_preserves_option_order() -> None:
    public = service().public_quiz()
    payload = public.model_dump(mode="json")
    assert [option["ref"] for option in payload["options"]] == ["op-a", "op-b"]
    forbidden = {
        "answer_key_ref",
        "correct_option_ref",
        "accepted_answers",
        "expected_answer",
        "explanation",
        "correct",
        "is_correct",
    }
    assert forbidden.isdisjoint(payload)


def test_public_schema_rejects_answer_key_fields() -> None:
    payload = service().public_quiz().model_dump(mode="json")
    payload["correct_option_ref"] = "op-b"
    with pytest.raises(ValidationError):
        PublicQuiz.model_validate(payload)


def test_submission_contract_forbids_client_identity_and_result() -> None:
    payload = request().model_dump(mode="json")
    payload["user_id"] = "forged"
    payload["is_correct"] = True
    with pytest.raises(ValidationError):
        AttemptRequest.model_validate(payload)


def test_server_grading_is_deterministic_and_does_not_mark_completion() -> None:
    grader = service(max_attempts=1)
    result = grader.submit(request(option="op-b"), principal_id="student-1")
    assert result.correct is True
    assert result.answer_reveal is not None
    assert result.answer_reveal.correct_option_ref == "op-b"
    assert "completed" not in result.model_dump(mode="json")


def test_invalid_option_is_rejected_without_recording_attempt() -> None:
    grader = service()
    with pytest.raises(ContractFailure) as exc:
        grader.submit(request(option="op-nao-existe"), principal_id="student-1")
    assert exc.value.status_code == 422
    assert grader.student_history("student-1").attempts == []


def test_same_idempotency_key_and_body_returns_same_result() -> None:
    grader = service()
    body = request()
    first = grader.submit(body, principal_id="student-1")
    replay = grader.submit(body, principal_id="student-1")
    assert replay == first
    assert len(grader.student_history("student-1").attempts) == 1


def test_reused_idempotency_key_with_different_body_conflicts() -> None:
    grader = service()
    grader.submit(request(option="op-a"), principal_id="student-1")
    with pytest.raises(ContractFailure) as exc:
        grader.submit(request(option="op-b"), principal_id="student-1")
    assert exc.value.status_code == 409
    assert exc.value.code == "IDEMPOTENCY_KEY_REUSED"


def test_answer_and_explanation_stay_hidden_until_attempt_limit() -> None:
    grader = service(max_attempts=2)
    first = grader.submit(request(option="op-a"), principal_id="student-1")
    assert first.correct is None
    assert first.answer_reveal is None
    final = grader.submit(
        request(option="op-b", key="00000000-0000-0000-0000-000000000002"),
        principal_id="student-1",
    )
    assert final.correct is True
    assert final.answer_reveal is not None
    assert final.answer_reveal.explanation == (
        "A alternativa B corresponde ao conceito apresentado."
    )


def test_attempt_limit_does_not_create_an_extra_attempt() -> None:
    grader = service(max_attempts=1)
    grader.submit(request(), principal_id="student-1")
    with pytest.raises(ContractFailure) as exc:
        grader.submit(
            request(key="00000000-0000-0000-0000-000000000002"),
            principal_id="student-1",
        )
    assert exc.value.status_code == 409
    assert len(grader.student_history("student-1").attempts) == 1


def test_stale_revision_is_rejected_and_prior_history_is_preserved() -> None:
    grader = service(max_attempts=3)
    grader.submit(request(), principal_id="student-1")
    grader.publish_revision("f1-revisao-2")
    with pytest.raises(ContractFailure) as exc:
        grader.submit(
            request(key="00000000-0000-0000-0000-000000000002"),
            principal_id="student-1",
        )
    assert exc.value.code == "QUIZ_REVISION_STALE"
    history = grader.student_history("student-1").attempts
    assert len(history) == 1
    assert history[0].quiz_revision_ref == "f1-revisao-1"


def test_history_is_scoped_to_student_and_has_no_early_answer_fields() -> None:
    grader = service()
    grader.submit(request(), principal_id="student-1")
    assert grader.student_history("student-2").attempts == []
    serialized = json.dumps(grader.student_history("student-1").model_dump(mode="json"))
    assert "correct_option_ref" not in serialized
    assert "explanation" not in serialized


def test_admin_correction_requires_separate_permission() -> None:
    grader = service()
    with pytest.raises(ContractFailure) as exc:
        grader.admin_answer_key(permissions={"progress.write"})
    assert exc.value.status_code == 403
    assert (
        grader.admin_answer_key(permissions={"quiz.answer_key.read"}).correct_option_ref == "op-b"
    )


def test_unsupported_formats_fail_closed() -> None:
    grader = InMemoryQuizContract(quiz_block("short_answer"), answer_key())
    with pytest.raises(ContractFailure) as exc:
        grader.submit(request(), principal_id="student-1")
    assert exc.value.status_code == 422
    assert exc.value.code == "QUIZ_FORMAT_NOT_SUPPORTED"


def test_mismatched_answer_key_is_not_associated_by_position() -> None:
    with pytest.raises(ValueError, match="another question"):
        InMemoryQuizContract(quiz_block(), answer_key("f1-quiz-diferente"))


def test_unauthenticated_or_locked_quiz_cannot_be_submitted() -> None:
    grader = service()
    with pytest.raises(ContractFailure) as unauthenticated:
        grader.submit(request(), principal_id=None)
    assert unauthenticated.value.status_code == 401
    with pytest.raises(ContractFailure) as locked:
        grader.submit(request(), principal_id="student-1", unlocked=False)
    assert locked.value.status_code == 403
    assert grader.student_history("student-1").attempts == []


def test_never_reveal_policy_keeps_key_and_explanation_private() -> None:
    grader = service(max_attempts=1, reveal_policy="never")
    result = grader.submit(request(), principal_id="student-1")
    assert result.correct is None
    assert result.answer_reveal is None
