"""Tests for the isolated, non-persisting quiz conversion prototype."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Literal

from bson import ObjectId

from curriculum_contract.bulk_import import CurriculumImportBundle
from curriculum_contract.experimental_quiz_converter import (
    _split_options,
    analyze_bundle_quizzes,
    convert_quiz_block,
    coverage_csv,
)
from curriculum_contract.models import AnswerKeyBlock, QuizBlock, SourceProvenance
from curriculum_contract.quiz_structure_audit import (
    audit_quiz_items,
    classification_csv,
    previous_statuses_from_csv,
)
from services.quizzes import _question_snapshot, grade_quiz_questions

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "docs/courses/trilhacode/trilha-code-bulk-import.json"
EXPECTED_BUNDLE_SHA256 = "43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2"
EXPECTED_14C_COVERAGE_SHA256 = "bd8487357aab3e6aa6b4831362ee52b88fa230d1f78c1bc136ae95be60fab89b"
SOURCE_FORMAT_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "quiz_formats_14d.json"


def _provenance(source_id: str, role: str = "quiz") -> SourceProvenance:
    return SourceProvenance(
        source_file=f"docs/fixtures/{source_id}.md",
        source_sha256="a" * 64,
        manifest_ref="1.1",
        source_role=role,
        source_id=source_id,
    )


def _question(
    prompt: str = "Múltipla escolha. Pergunta? A) Primeira opção. B) Segunda opção. C) Terceira opção.",
    *,
    ref: str = "f1-test-topic-q01",
    answer_key_ref: str = "f1-test-topic-q01-answer",
    order: int = 17,
    required: bool = True,
    format: Literal[
        "multiple_choice", "true_false", "short_answer", "ordering", "fill_code", "other"
    ] = "other",
    options: list | None = None,
) -> QuizBlock:
    return QuizBlock(
        ref=ref,
        type="quiz",
        owner_ref=None,
        order=order,
        title="Q1",
        status="draft",
        shared=False,
        provenance=_provenance("Q1"),
        prompt=prompt,
        format=format,
        options=options or [],
        answer_key_required=required,
        answer_key_ref=answer_key_ref if required else None,
    )


def _answer_key(
    quiz: QuizBlock,
    *,
    expected: str | None = "B.",
    question_ref: str | None = None,
    correct_option_ref: str | None = None,
    explanation: str | None = "PRIVATE_EXPLANATION_SENTINEL",
    accepted_answers: list[str] | None = None,
    source_markdown: str | None = "**Resposta: B.**",
) -> AnswerKeyBlock:
    return AnswerKeyBlock(
        ref=quiz.answer_key_ref or "f1-test-topic-q01-answer",
        type="answer_key",
        owner_ref=None,
        order=quiz.order + 1000000,
        title="Gabarito Q1",
        status="draft",
        shared=False,
        provenance=_provenance("Q1-answer", "quiz-answer-key"),
        question_ref=question_ref or quiz.ref,
        correct_option_ref=correct_option_ref,
        accepted_answers=accepted_answers or [],
        expected_answer=expected,
        explanation=explanation,
        source_markdown=source_markdown,
    )


def test_valid_question_converts_to_public_and_private_backend_shapes():
    quiz = _question()
    key = _answer_key(quiz)

    outcome = convert_quiz_block(quiz, key, phase=1)

    assert outcome.status == "converted_candidate"
    assert outcome.candidate is not None
    candidate = outcome.candidate
    assert candidate.public_question.question_id == quiz.ref
    assert candidate.public_question.order == 17
    assert [option.option_id for option in candidate.public_question.options] == ["a", "b", "c"]
    assert candidate.private_answer_key.correct_option_id == "b"
    assert candidate.answer_key_ref == key.ref
    assert candidate.public_payload() == candidate.public_question.model_dump(mode="json")
    assert "correct_option_id" not in candidate.public_payload()
    assert "explanation" not in candidate.public_payload()
    graded = grade_quiz_questions(
        [candidate.grader_record()], [{"question_id": quiz.ref, "option_id": "b"}]
    )
    assert graded["passed"] is True
    assert graded["score_percent"] == 100
    snapshot = _question_snapshot(
        candidate.backend_source_block(str(ObjectId("000000000000000000000001"))), order=17
    )
    assert snapshot["question_id"] == quiz.ref
    assert snapshot["correct_option_id"] == "b"
    assert snapshot["answer_key_ref"] == key.ref


def test_ambiguous_or_out_of_order_alternative_markers_are_blocked():
    quiz = _question("Pergunta? A) Uma. C) Três. B) Duas.")

    outcome = convert_quiz_block(quiz, _answer_key(quiz))

    assert outcome.status == "blocked_alternatives"
    assert outcome.reason_code == "ALTERNATIVE_MARKERS_AMBIGUOUS_OR_OUT_OF_ORDER"
    assert outcome.candidate is None


def test_missing_alternatives_are_blocked_without_guessing_format():
    quiz = _question("Explique o comportamento observado.")

    outcome = convert_quiz_block(quiz, _answer_key(quiz))

    assert outcome.status == "blocked_alternatives"
    assert outcome.reason_code == "ALTERNATIVES_NOT_EXPLICIT"


def test_numbered_question_ordinals_are_not_inferred_as_answer_choices():
    quiz = _question("1. O que precisa ser verificado?\n1) primeiro passo\n2) segundo passo")

    outcome = convert_quiz_block(quiz, _answer_key(quiz, expected="uma resposta textual"))

    assert outcome.status == "blocked_alternatives"
    assert outcome.reason_code == "ALTERNATIVES_NOT_EXPLICIT"
    assert outcome.candidate is None


def test_sanitized_source_derived_format_fixtures_contain_no_answer_keys():
    fixture = json.loads(SOURCE_FORMAT_FIXTURE_PATH.read_text(encoding="utf-8"))
    items = fixture["items"]
    assert len(items) == 8
    assert {item["fixture_kind"] for item in items} == {
        "case_distinct_options",
        "incomplete_multiple_choice",
        "open_response",
        "discursive",
        "review_question",
        "matching",
        "ordering",
        "ambiguous_answer_key",
    }
    assert all(
        not any("answer_key" in key or "explanation" in key for key in item) for item in items
    )

    by_kind = {item["fixture_kind"]: item for item in items}
    _stem, case_options, case_error = _split_options(by_kind["case_distinct_options"]["prompt"])
    assert case_error is None
    assert len(case_options) == 4
    assert case_options[0][1] != case_options[1][1]
    _stem, ambiguous_options, ambiguous_error = _split_options(
        by_kind["ambiguous_answer_key"]["prompt"]
    )
    assert ambiguous_error is None
    assert len(ambiguous_options) == 3
    for kind in (
        "incomplete_multiple_choice",
        "open_response",
        "discursive",
        "review_question",
        "matching",
        "ordering",
    ):
        _stem, options, error = _split_options(by_kind[kind]["prompt"])
        assert options == []
        assert error == "ALTERNATIVES_NOT_EXPLICIT"


def test_duplicate_option_text_is_blocked():
    quiz = _question("Múltipla escolha. Pergunta? A) Mesmo texto. B) Mesmo texto. C) Outra opção.")

    outcome = convert_quiz_block(quiz, _answer_key(quiz))

    assert outcome.status == "blocked_alternatives"
    assert outcome.reason_code == "DUPLICATE_OPTION_TEXT"


def test_case_distinct_source_code_options_are_not_duplicates():
    quiz = _question("Pergunta? **A)** `String`. **B)** `string`. **C)** `Text`. **D)** `object`.")

    outcome = convert_quiz_block(quiz, _answer_key(quiz, expected="B"))

    assert outcome.status == "converted_candidate"
    assert outcome.candidate is not None
    assert [option.text for option in outcome.candidate.public_question.options] == [
        "`String`.",
        "`string`.",
        "`Text`.",
        "`object`.",
    ]


def test_real_case_distinct_question_is_recovered_without_regressing_prior_candidates():
    bundle_bytes = BUNDLE_PATH.read_bytes()
    assert hashlib.sha256(bundle_bytes).hexdigest() == EXPECTED_BUNDLE_SHA256
    bundle = CurriculumImportBundle.model_validate_json(bundle_bytes)
    quizzes = {
        block.ref: (phase.phase, block)
        for phase in bundle.phases
        for block in phase.contract.blocks
        if isinstance(block, QuizBlock)
    }
    keys = {
        block.ref: block
        for phase in bundle.phases
        for block in phase.contract.blocks
        if isinstance(block, AnswerKeyBlock)
    }
    outcomes = analyze_bundle_quizzes(bundle)
    current = {(item.phase, item.quiz_ref): item for item in outcomes}
    baseline_bytes = (REPO_ROOT / "docs/migracao/COBERTURA_CONVERSAO_QUIZZES_14C.csv").read_bytes()
    assert hashlib.sha256(baseline_bytes).hexdigest() == EXPECTED_14C_COVERAGE_SHA256
    with (REPO_ROOT / "docs/migracao/COBERTURA_CONVERSAO_QUIZZES_14C.csv").open(
        encoding="utf-8", newline=""
    ) as csv_file:
        previous = list(csv.DictReader(csv_file))

    previous_candidates = [
        row for row in previous if row["conversion_status"] == "converted_candidate"
    ]
    assert len(previous_candidates) == 142
    assert all(
        current[(int(row["phase"]), row["quiz_ref"])].status == "converted_candidate"
        for row in previous_candidates
    )

    recovered = [
        item
        for item in outcomes
        if item.status == "converted_candidate"
        and item.source_id == "Q1"
        and item.phase == 3
        and "`String`" in quizzes[item.quiz_ref][1].prompt
        and "`string`" in quizzes[item.quiz_ref][1].prompt
    ]
    assert len(recovered) == 1
    recovered_item = recovered[0]
    source_quiz = quizzes[recovered_item.quiz_ref][1]
    assert source_quiz.answer_key_ref is not None
    candidate = recovered_item.candidate
    assert candidate is not None
    assert candidate.private_answer_key.correct_option_id in {
        option.option_id for option in candidate.public_question.options
    }
    assert keys[source_quiz.answer_key_ref].question_ref == source_quiz.ref
    assert sum(item.status == "converted_candidate" for item in outcomes) == 143


def test_unparseable_answer_key_is_blocked_without_emitting_its_text():
    quiz = _question()
    key = _answer_key(quiz, expected="ANSWER_TEXT_PRIVATE_SENTINEL")

    outcome = convert_quiz_block(quiz, key)

    assert outcome.status == "blocked_gabarito"
    assert outcome.reason_code == "ANSWER_KEY_NOT_UNAMBIGUOUS_OPTION_REFERENCE"
    assert "ANSWER_TEXT_PRIVATE_SENTINEL" not in repr(outcome)


def test_answer_key_for_another_question_is_blocked():
    quiz = _question()
    key = _answer_key(quiz, question_ref="f1-other-topic-q02")

    outcome = convert_quiz_block(quiz, key)

    assert outcome.status == "blocked_gabarito"
    assert outcome.reason_code == "ANSWER_KEY_POINTS_TO_DIFFERENT_QUESTION"


def test_missing_explanation_is_valid_and_not_synthesized():
    quiz = _question()
    key = _answer_key(quiz, explanation=None)

    outcome = convert_quiz_block(quiz, key)

    assert outcome.status == "converted_candidate"
    assert outcome.candidate is not None
    assert outcome.candidate.private_answer_key.explanation is None
    assert outcome.candidate.private_answer_key.source_markdown == "**Resposta: B.**"


def test_unsupported_accepted_answers_block_lossy_conversion():
    quiz = _question()
    key = _answer_key(quiz, accepted_answers=["alternate form"])

    outcome = convert_quiz_block(quiz, key)

    assert outcome.status == "blocked_gabarito"
    assert outcome.reason_code == "ACCEPTED_ANSWERS_NOT_SUPPORTED_BY_OPTION_GRADER"


def test_markdown_source_order_provenance_and_full_prompt_are_preserved():
    source = "## Quiz\n\n1. **Múltipla escolha.** Pergunta?\n- A. Primeiro.\n- B. Segundo.\n- C. Terceiro.\n"
    quiz = _question(source)
    key = _answer_key(quiz, expected="B")

    outcome = convert_quiz_block(quiz, key, phase=1)

    assert outcome.status == "converted_candidate"
    assert outcome.candidate is not None
    assert outcome.candidate.source_markdown == source
    assert outcome.candidate.public_question.order == quiz.order
    assert [option.text for option in outcome.candidate.public_question.options] == [
        "Primeiro.",
        "Segundo.",
        "Terceiro.",
    ]
    assert outcome.candidate.quiz_provenance == quiz.provenance
    assert outcome.candidate.private_answer_key.provenance == key.provenance


def test_inline_code_markers_are_not_treated_as_alternatives():
    quiz = _question("Execute `A) exemplo` e depois descreva o resultado.")

    outcome = convert_quiz_block(quiz, _answer_key(quiz))

    assert outcome.status == "blocked_alternatives"
    assert outcome.reason_code == "ALTERNATIVES_NOT_EXPLICIT"


def test_candidate_version_and_coverage_serialization_are_deterministic_and_private():
    quiz = _question()
    key = _answer_key(quiz)
    first = convert_quiz_block(quiz, key)
    second = convert_quiz_block(quiz, key)

    assert first.candidate is not None and second.candidate is not None
    assert first.candidate.content_version_sha256 == second.candidate.content_version_sha256
    csv_text = coverage_csv([first])
    assert csv_text == coverage_csv([second])
    assert "PRIVATE_EXPLANATION_SENTINEL" not in csv_text
    assert "ANSWER_TEXT_PRIVATE_SENTINEL" not in csv_text
    assert "correct_option_id" not in csv_text


def test_five_real_unkeyed_review_questions_remain_unscored():
    bundle = CurriculumImportBundle.model_validate_json(BUNDLE_PATH.read_text(encoding="utf-8"))
    outcomes = analyze_bundle_quizzes(bundle)
    unkeyed = [item for item in outcomes if item.status == "unscored_review_pending"]

    assert len(unkeyed) == 5
    assert {item.source_id for item in unkeyed} == {"R1", "R2", "R3", "R4", "R5"}
    assert all(item.candidate is None for item in unkeyed)
    assert all(item.reason_code == "UNKEYED_REVIEW_REQUIRES_EDITORIAL_POLICY" for item in unkeyed)


def test_real_package_coverage_and_all_converted_candidates_match_backend_contract():
    bundle_bytes = BUNDLE_PATH.read_bytes()
    assert hashlib.sha256(bundle_bytes).hexdigest() == EXPECTED_BUNDLE_SHA256
    bundle = CurriculumImportBundle.model_validate_json(bundle_bytes)
    outcomes = analyze_bundle_quizzes(bundle)
    counts = Counter(item.status for item in outcomes)
    source_blocks = [block for phase in bundle.phases for block in phase.contract.blocks]
    source_quizzes = [block for block in source_blocks if isinstance(block, QuizBlock)]
    source_keys = {block.ref: block for block in source_blocks if isinstance(block, AnswerKeyBlock)}

    assert len(outcomes) == 506
    assert sum(item.status != "unscored_review_pending" for item in outcomes) == 501
    assert sum(quiz.answer_key_required for quiz in source_quizzes) == 501
    assert len(source_keys) == 501
    assert sum(key.explanation is not None for key in source_keys.values()) == 99
    assert all(
        source_keys[quiz.answer_key_ref].question_ref == quiz.ref
        for quiz in source_quizzes
        if quiz.answer_key_required and quiz.answer_key_ref is not None
    )
    assert counts == {
        "converted_candidate": 143,
        "blocked_alternatives": 347,
        "blocked_gabarito": 11,
        "unscored_review_pending": 5,
    }
    candidates = [item.candidate for item in outcomes if item.candidate is not None]
    assert len(candidates) == 143
    for candidate in candidates:
        assert candidate is not None
        assert set(candidate.public_payload()) == {"question_id", "order", "prompt", "options"}
        grade_quiz_questions([candidate.grader_record()], [])
        assert candidate.answer_key_ref == candidate.private_answer_key.ref


def test_json_bundle_sha_and_source_provenance_remain_unchanged():
    data = BUNDLE_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_BUNDLE_SHA256
    bundle = CurriculumImportBundle.model_validate_json(data)
    outcomes = analyze_bundle_quizzes(bundle)

    assert all(item.source_file and len(item.source_sha256) == 64 for item in outcomes)
    assert all(
        not item.answer_key_source_sha256 or len(item.answer_key_source_sha256) == 64
        for item in outcomes
    )


def test_structure_audit_covers_every_keyed_quiz_against_official_markdown():
    bundle_bytes = BUNDLE_PATH.read_bytes()
    assert hashlib.sha256(bundle_bytes).hexdigest() == EXPECTED_BUNDLE_SHA256
    bundle = CurriculumImportBundle.model_validate_json(bundle_bytes)
    outcomes = analyze_bundle_quizzes(bundle)
    baseline_bytes = (REPO_ROOT / "docs/migracao/COBERTURA_CONVERSAO_QUIZZES_14C.csv").read_bytes()
    assert hashlib.sha256(baseline_bytes).hexdigest() == EXPECTED_14C_COVERAGE_SHA256
    baseline = baseline_bytes.decode("utf-8")
    previous = previous_statuses_from_csv(baseline)

    records = audit_quiz_items(bundle, outcomes, previous, REPO_ROOT)
    output = classification_csv(records)
    counts = Counter(record.classification for record in records)

    assert len(records) == 501
    assert all(record.original_question_line > 0 for record in records)
    assert all(record.original_answer_line > 0 for record in records)
    assert all(record.answer_text_included == "no" for record in records)
    assert counts["multiple_choice_recoverable"] == 143
    assert counts["ambiguous_answer_key"] == 11
    assert counts["multiple_choice_incomplete"] == 1
    assert "correct_option_id" not in output
    assert "expected_answer" not in output
    assert "explanation" not in output
    assert "ANSWER_TEXT_PRIVATE_SENTINEL" not in output
    assert all(row["publishable"] == "no" for row in csv.DictReader(output.splitlines()))


def test_structure_audit_uses_real_review_discursive_and_open_response_sources():
    bundle = CurriculumImportBundle.model_validate_json(BUNDLE_PATH.read_bytes())
    outcomes = analyze_bundle_quizzes(bundle)
    previous = previous_statuses_from_csv(
        (REPO_ROOT / "docs/migracao/COBERTURA_CONVERSAO_QUIZZES_14C.csv").read_text(
            encoding="utf-8"
        )
    )
    records = audit_quiz_items(bundle, outcomes, previous, REPO_ROOT)
    by_phase_source = {(item.phase, item.question_source_id): item for item in records}

    assert by_phase_source[(4, "R1")].classification == "review_question"
    assert by_phase_source[(4, "Q1")].classification == "open_response"
    assert by_phase_source[(6, "Q02")].classification == "discursive_exercise"
    assert by_phase_source[(9, "Q01")].classification == "multiple_choice_incomplete"
    assert {item.source_format_signal for item in records} >= {
        "matching_unsupported",
        "ordering_unsupported",
    }
