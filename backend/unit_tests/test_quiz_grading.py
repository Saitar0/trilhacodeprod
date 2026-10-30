from decimal import Decimal

from bson import ObjectId

from curriculum_contract import AnswerKeyBlock, QuizBlock, SourceProvenance, student_quiz_view
from curriculum_contract.models import QuizOption
from services.quizzes import (
    QuizSourceError,
    _question_snapshot,
    _result_payload,
    grade_quiz_questions,
)


def _questions(count: int = 2) -> list[dict]:
    return [
        {
            "question_id": f"q{index}",
            "order": index,
            "prompt": f"Pergunta {index}",
            "options": [
                {"option_id": "a", "text": "Correta"},
                {"option_id": "b", "text": "Incorreta"},
            ],
            "correct_option_id": "a",
        }
        for index in range(count)
    ]


def test_correct_and_incorrect_answers_are_graded_on_server():
    result = grade_quiz_questions(
        _questions(),
        [
            {"question_id": "q0", "option_id": "a"},
            {"question_id": "q1", "option_id": "b"},
        ],
    )
    assert result["correct_answers"] == 1
    assert result["total_questions"] == 2
    assert result["score_percent"] == 50
    assert result["passed"] is False


def test_omitted_answers_are_incorrect_and_empty_submission_is_valid():
    result = grade_quiz_questions(_questions(), [])
    assert result["correct_answers"] == 0
    assert result["passed"] is False


def test_exactly_seventy_percent_passes_without_rounding():
    questions = _questions(10)
    result = grade_quiz_questions(
        questions,
        [{"question_id": f"q{index}", "option_id": "a"} for index in range(7)],
    )
    assert result["score_percent"] == 70
    assert result["passed"] is True


def test_score_below_seventy_does_not_pass():
    result = grade_quiz_questions(
        _questions(3),
        [
            {"question_id": "q0", "option_id": "a"},
            {"question_id": "q1", "option_id": "b"},
        ],
    )
    assert result["score_percent"] == Decimal("100") / Decimal("3")
    assert result["passed"] is False


def test_invalid_option_is_rejected():
    try:
        grade_quiz_questions(_questions(), [{"question_id": "q0", "option_id": "missing"}])
    except QuizSourceError as exc:
        assert "Alternativa" in str(exc)
    else:
        raise AssertionError("Alternativa inexistente aceita")


def test_unknown_question_is_rejected():
    try:
        grade_quiz_questions(_questions(), [{"question_id": "foreign", "option_id": "a"}])
    except QuizSourceError as exc:
        assert "não pertence" in str(exc)
    else:
        raise AssertionError("Questão externa aceita")


def test_duplicate_answer_for_same_question_is_rejected():
    try:
        grade_quiz_questions(
            _questions(),
            [
                {"question_id": "q0", "option_id": "a"},
                {"question_id": "q0", "option_id": "b"},
            ],
        )
    except QuizSourceError as exc:
        assert "mais de uma resposta" in str(exc)
    else:
        raise AssertionError("Respostas duplicadas aceitas")


def test_quiz_without_evaluable_questions_is_rejected():
    try:
        grade_quiz_questions([], [])
    except QuizSourceError as exc:
        assert "sem questões avaliáveis" in str(exc)
    else:
        raise AssertionError("Quiz vazio aceito")


def test_explicit_weights_are_rejected_until_supported_and_validated():
    block = {
        "_id": "000000000000000000000001",
        "data": {
            "question": "Pergunta",
            "options": ["A", "B"],
            "correct_index": 0,
            "weight": 2,
        },
    }
    try:
        _question_snapshot(block, 0)
    except QuizSourceError as exc:
        assert "Pesos" in str(exc)
    else:
        raise AssertionError("Peso explícito ignorado")


def test_typed_curriculum_quiz_and_answer_key_preserve_identity_order_and_provenance():
    provenance = SourceProvenance(
        source_file="docs/courses/trilhacode/Conteudos_migrado/Fase_1/1.1/quiz.md",
        source_sha256="a" * 64,
        manifest_ref="f1-quiz-example",
        source_role="quiz",
    )
    quiz = QuizBlock(
        ref="f1-quiz-example",
        type="quiz",
        owner_ref="f1-topic-example",
        order=4,
        title="Quiz de exemplo",
        status="published",
        shared=False,
        provenance=provenance,
        prompt="Selecione a resposta correta.",
        format="multiple_choice",
        options=[
            QuizOption(ref="option-a", text="Alternativa A"),
            QuizOption(ref="option-b", text="Alternativa B"),
        ],
        answer_key_required=True,
        answer_key_ref="f1-answer-example",
    )
    answer_key = AnswerKeyBlock(
        ref="f1-answer-example",
        type="answer_key",
        owner_ref="f1-topic-example",
        order=4,
        title="Gabarito",
        status="published",
        shared=False,
        provenance=provenance,
        question_ref=quiz.ref,
        correct_option_ref="option-b",
        accepted_answers=[],
        expected_answer=None,
        explanation="A alternativa B corresponde à resposta.",
    )
    public_view = student_quiz_view(quiz)
    assert [option.ref for option in public_view.options] == ["option-a", "option-b"]
    assert not hasattr(public_view, "answer_key_ref")

    source_id = ObjectId()
    snapshot = _question_snapshot(
        {
            "_id": source_id,
            "data": {
                "import_ref": quiz.ref,
                "prompt": quiz.prompt,
                "format": quiz.format,
                "options": [option.model_dump() for option in quiz.options],
                "answer_key_required": quiz.answer_key_required,
                "answer_key_ref": quiz.answer_key_ref,
                "answer_key": {
                    **answer_key.model_dump(),
                    "provenance": answer_key.provenance.model_dump(),
                },
                "provenance": quiz.provenance.model_dump(),
            },
        },
        quiz.order,
    )
    assert snapshot["question_id"] == quiz.ref
    assert snapshot["source_block_id"] == str(source_id)
    assert [option["option_id"] for option in snapshot["options"]] == ["option-a", "option-b"]
    assert snapshot["answer_key_ref"] == answer_key.ref
    assert snapshot["source_provenance"]["manifest_ref"] == quiz.provenance.manifest_ref
    assert snapshot["answer_key_provenance"]["manifest_ref"] == answer_key.provenance.manifest_ref
    result = grade_quiz_questions([snapshot], [{"question_id": quiz.ref, "option_id": "option-b"}])
    assert result["passed"] is True
    assert snapshot["explanation"] == answer_key.explanation


def test_typed_answer_key_for_another_question_is_rejected():
    try:
        _question_snapshot(
            {
                "_id": ObjectId(),
                "data": {
                    "import_ref": "f1-question-example",
                    "prompt": "Selecione a resposta correta.",
                    "format": "multiple_choice",
                    "options": [
                        {"ref": "option-a", "text": "Alternativa A"},
                        {"ref": "option-b", "text": "Alternativa B"},
                    ],
                    "answer_key_ref": "f1-answer-example",
                    "answer_key": {
                        "ref": "f1-answer-example",
                        "question_ref": "f1-another-question",
                        "correct_option_ref": "option-a",
                    },
                },
            },
            0,
        )
    except QuizSourceError as exc:
        assert "associado a outra questão" in str(exc)
    else:
        raise AssertionError("Gabarito de outra questão foi aceito")


def test_typed_answer_key_without_evaluable_option_is_rejected_even_with_legacy_index():
    try:
        _question_snapshot(
            {
                "_id": ObjectId(),
                "data": {
                    "import_ref": "f1-question-example",
                    "prompt": "Selecione a resposta correta.",
                    "format": "multiple_choice",
                    "options": [
                        {"ref": "option-a", "text": "Alternativa A"},
                        {"ref": "option-b", "text": "Alternativa B"},
                    ],
                    "correct_index": 0,
                    "answer_key_ref": "f1-answer-example",
                    "answer_key": {
                        "ref": "f1-answer-example",
                        "question_ref": "f1-question-example",
                        "correct_option_ref": None,
                    },
                },
            },
            0,
        )
    except QuizSourceError as exc:
        assert "sem alternativa correta avaliável" in str(exc)
    else:
        raise AssertionError("Índice legado substituiu gabarito tipado incompleto")


def test_attempt_result_allowlist_does_not_expose_correct_answer_count():
    payload = _result_payload(
        {
            "attempt_id": ObjectId(),
            "submitted_at": "2026-10-27T00:00:00Z",
            "result": {
                "quiz_id": "quiz-1",
                "version_id": "version-1",
                "attempt_number": 1,
                "correct_answers": 1,
                "total_questions": 1,
                "score_percent": 100,
                "passed": True,
                "attempts_used": 1,
                "attempts_remaining": 2,
                "best_score_percent": 100,
                "review_available": False,
            },
        }
    )
    assert "correct_answers" not in payload
    assert payload["score_percent"] == 100
