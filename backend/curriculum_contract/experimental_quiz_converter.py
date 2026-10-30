"""Offline-only, fail-closed quiz conversion prototype.

This module does not persist converted candidates, publish quizzes, or access
MongoDB. The private answer key is kept separate from the public question
projection and is excluded from repr/coverage output.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic import ValidationError

from schemas.quizzes import QuizOptionOut, QuizQuestionOut

from .bulk_import import CurriculumImportBundle
from .models import AnswerKeyBlock, QuizBlock, SourceProvenance

ConversionStatus = Literal[
    "converted_candidate",
    "blocked_enunciado",
    "blocked_alternatives",
    "blocked_gabarito",
    "blocked_incompatibility",
    "blocked_other",
    "unscored_review_pending",
]


@dataclass(frozen=True, slots=True)
class QuizConversionDiagnostic:
    code: str
    message: str
    source_file: str
    entity_ref: str


@dataclass(frozen=True, slots=True)
class PrivateAnswerKeyCandidate:
    ref: str
    question_ref: str
    correct_option_id: str
    expected_answer: str = field(repr=False)
    accepted_answers: tuple[str, ...] = field(repr=False)
    explanation: str | None = field(repr=False)
    source_markdown: str = field(repr=False)
    provenance: SourceProvenance


@dataclass(frozen=True, slots=True)
class ExperimentalQuizCandidate:
    """In-memory projection; never serialize this whole object to a student."""

    public_question: QuizQuestionOut
    answer_key_ref: str
    private_answer_key: PrivateAnswerKeyCandidate = field(repr=False)
    content_version_sha256: str = field(repr=False)
    source_markdown: str = field(repr=False)
    quiz_provenance: SourceProvenance

    def public_payload(self) -> dict:
        """Return the exact public question schema by allowlist."""
        return self.public_question.model_dump(mode="json")

    def grader_record(self) -> dict:
        """Build the private shape consumed by the existing pure grader."""
        return {
            **self.public_payload(),
            "correct_option_id": self.private_answer_key.correct_option_id,
            "explanation": self.private_answer_key.explanation,
            "answer_key_ref": self.private_answer_key.ref,
        }

    def backend_source_block(self, source_block_id: str) -> dict:
        """Build a private source-block shape for the backend snapshot parser.

        The caller must supply an already-resolved Mongo ObjectId string. This
        method never creates or persists an identity.
        """
        from bson import ObjectId

        if not ObjectId.is_valid(source_block_id):
            raise ValueError("source block ID must be a valid, externally resolved ObjectId")
        return {
            "_id": source_block_id,
            "data": {
                "format": "multiple_choice",
                "import_ref": self.public_question.question_id,
                "question": self.public_question.prompt,
                "options": [
                    {"ref": option.option_id, "text": option.text}
                    for option in self.public_question.options
                ],
                "answer_key_ref": self.private_answer_key.ref,
                "answer_key": {
                    "ref": self.private_answer_key.ref,
                    "question_ref": self.private_answer_key.question_ref,
                    "correct_option_ref": self.private_answer_key.correct_option_id,
                    "explanation": self.private_answer_key.explanation,
                    "provenance": self.private_answer_key.provenance.model_dump(mode="json"),
                },
                "provenance": self.quiz_provenance.model_dump(mode="json"),
            },
        }


@dataclass(frozen=True, slots=True)
class QuizConversionOutcome:
    phase: int
    quiz_ref: str
    source_id: str
    source_file: str
    source_sha256: str
    status: ConversionStatus
    category: str
    reason_code: str
    message: str
    detected_alternative_count: int | None
    answer_key_ref: str | None
    answer_key_source_id: str | None
    answer_key_source_file: str | None
    answer_key_source_sha256: str | None
    candidate: ExperimentalQuizCandidate | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True)
class _OptionMarker:
    label: str
    start: int
    end: int


_BOLD_MARKER = re.compile(r"(?<![A-Za-z0-9])\*\*([A-D])[.)]\*\*[ \t]*")
_LIST_MARKER = re.compile(r"(?m)^[ \t]*[-*+][ \t]+([A-D])[.)][ \t]+")
_LINE_MARKER = re.compile(r"(?m)^[ \t]*([A-D])[.)][ \t]+")
_INLINE_MARKER = re.compile(r"(?<![A-Za-z0-9])([A-D])\)[ \t]+")
_LETTER_ANSWER = re.compile(r"(?i)^\s*(?:\*\*)?(?:resposta\s*:\s*)?([A-D])(?:[.)])?(?:\*\*)?\s*$")
_ANY_OPTION_MARKER = re.compile(r"(?<![A-Za-z0-9])(?:\*\*)?\(?([A-D])\)?(?:\*\*)?[.)]")
_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.*?)\1(?!`)", re.DOTALL)


def _code_ranges(markdown: str) -> list[tuple[int, int]]:
    """Return fenced and inline code spans so code examples cannot become choices."""
    ranges: list[tuple[int, int]] = []
    offset = 0
    fence_start: int | None = None
    fence_char = ""
    fence_size = 0
    for line in markdown.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        fence_match = re.match(r"(`{3,}|~{3,})", stripped) if indent <= 3 else None
        if fence_start is None and fence_match:
            fence_start = offset
            fence_char = fence_match.group(1)[0]
            fence_size = len(fence_match.group(1))
        elif fence_start is not None and indent <= 3:
            closing = re.match(
                re.escape(fence_char) + r"{" + str(fence_size) + r",}[ \t]*$",
                stripped.rstrip("\r\n"),
            )
            if closing:
                ranges.append((fence_start, offset + len(line)))
                fence_start = None
                fence_char = ""
                fence_size = 0
        offset += len(line)
    if fence_start is not None:
        ranges.append((fence_start, len(markdown)))

    for match in _INLINE_CODE.finditer(markdown):
        if not any(start <= match.start() < end for start, end in ranges):
            ranges.append((match.start(), match.end()))
    return sorted(ranges)


def _is_code(position: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)


def _valid_label_sequence(markers: list[_OptionMarker]) -> bool:
    labels = [marker.label for marker in markers]
    return labels in (["A", "B", "C"], ["A", "B", "C", "D"])


def _markers_from_pattern(
    markdown: str, pattern: re.Pattern[str], code: list[tuple[int, int]]
) -> list[_OptionMarker]:
    markers: list[_OptionMarker] = []
    for match in pattern.finditer(markdown):
        if _is_code(match.start(), code):
            continue
        markers.append(_OptionMarker(match.group(1), match.start(), match.end()))
    return markers


def _extract_markers(markdown: str) -> tuple[list[_OptionMarker] | None, str | None]:
    code = _code_ranges(markdown)
    patterns = (_BOLD_MARKER, _LIST_MARKER, _LINE_MARKER)
    for pattern in patterns:
        markers = _markers_from_pattern(markdown, pattern, code)
        if markers and _valid_label_sequence(markers):
            return markers, None

    # Inline A)/B)/C) is accepted only in an explicitly identified
    # multiple-choice prompt and only when the complete set is on one line.
    if "múltipla escolha" in markdown.casefold():
        markers = _markers_from_pattern(markdown, _INLINE_MARKER, code)
        if markers and _valid_label_sequence(markers):
            first_line = markdown.count("\n", 0, markers[0].start)
            last_line = markdown.count("\n", 0, markers[-1].start)
            if first_line == last_line:
                return markers, None

    any_markers = [
        match
        for match in _ANY_OPTION_MARKER.finditer(markdown)
        if not _is_code(match.start(), code)
    ]
    if any_markers:
        return None, "ALTERNATIVE_MARKERS_AMBIGUOUS_OR_OUT_OF_ORDER"
    return None, "ALTERNATIVES_NOT_EXPLICIT"


def _has_stem(stem: str) -> bool:
    content = re.sub(r"(?m)^[ \t]{0,3}#{1,6}[ \t]+[^\n]*(?:\n|$)", "", stem)
    content = re.sub(r"(?m)^[ \t]*\d+[.)][ \t]*$", "", content)
    content = content.strip(" \t\r\n#*_-")
    return bool(content)


def _split_options(markdown: str) -> tuple[str, list[tuple[str, str]], str | None]:
    markers, marker_error = _extract_markers(markdown)
    if markers is None:
        return "", [], marker_error
    stem = markdown[: markers[0].start].strip()
    if not _has_stem(stem):
        return stem, [], "QUESTION_STEM_MISSING_OR_AMBIGUOUS"
    options: list[tuple[str, str]] = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start if index + 1 < len(markers) else len(markdown)
        text = markdown[marker.end : end].strip()
        if not text:
            return stem, [], "OPTION_TEXT_EMPTY"
        options.append((marker.label, text))
    # Option text is content, not a case-insensitive identifier. For example,
    # ``String`` and ``string`` are distinct values in source code questions.
    # Normalize layout whitespace only; case-folding here can reject valid
    # alternatives and hide a uniquely mapped answer key.
    normalized = [re.sub(r"\s+", " ", text) for _, text in options]
    if len(normalized) != len(set(normalized)):
        return stem, [], "DUPLICATE_OPTION_TEXT"
    return stem, options, None


def _failure(
    quiz: QuizBlock,
    status: ConversionStatus,
    category: str,
    code: str,
    message: str,
    *,
    answer_key: AnswerKeyBlock | None = None,
    alternative_count: int | None = None,
) -> QuizConversionOutcome:
    phase_match = re.match(r"^f(10|[1-9])-", quiz.ref)
    return QuizConversionOutcome(
        phase=int(phase_match.group(1)) if phase_match else 0,
        quiz_ref=quiz.ref,
        source_id=quiz.provenance.source_id or "",
        source_file=quiz.provenance.source_file,
        source_sha256=quiz.provenance.source_sha256,
        status=status,
        category=category,
        reason_code=code,
        message=message,
        detected_alternative_count=alternative_count,
        answer_key_ref=answer_key.ref if answer_key else quiz.answer_key_ref,
        answer_key_source_id=answer_key.provenance.source_id if answer_key else None,
        answer_key_source_file=answer_key.provenance.source_file if answer_key else None,
        answer_key_source_sha256=answer_key.provenance.source_sha256 if answer_key else None,
    )


def _version_hash(
    quiz: QuizBlock,
    key: AnswerKeyBlock,
    prompt: str,
    options: list[QuizOptionOut],
    correct_option_id: str,
) -> str:
    private_version_content = {
        "quiz_ref": quiz.ref,
        "answer_key_ref": key.ref,
        "order": quiz.order,
        "prompt": prompt,
        "options": [option.model_dump(mode="json") for option in options],
        "correct_option_id": correct_option_id,
        "expected_answer": key.expected_answer,
        "accepted_answers": key.accepted_answers,
        "explanation": key.explanation,
        "source_markdown": key.source_markdown,
        "quiz_source_sha256": quiz.provenance.source_sha256,
        "answer_key_source_sha256": key.provenance.source_sha256,
    }
    canonical = json.dumps(
        private_version_content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def convert_quiz_block(
    quiz: QuizBlock,
    answer_key: AnswerKeyBlock | None,
    *,
    phase: int = 0,
) -> QuizConversionOutcome:
    """Convert only a provably single-answer multiple-choice item.

    The result is an in-memory candidate. It is not a publishable/importable
    QuizVersion: no Mongo ObjectIds, node association, or persistence is made.
    """
    if not quiz.answer_key_required and answer_key is None:
        return _failure(
            quiz,
            "unscored_review_pending",
            "no_answer_key",
            "UNKEYED_REVIEW_REQUIRES_EDITORIAL_POLICY",
            "A pergunta sem gabarito foi preservada no pacote e não recebeu nota.",
            alternative_count=len(quiz.options) or None,
        )
    if not quiz.answer_key_required:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "UNEXPECTED_ANSWER_KEY_FOR_UNKEYED_ITEM",
            "A questão não declara exigir gabarito, mas recebeu uma chave associada.",
            answer_key=answer_key,
        )
    if answer_key is None:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "REQUIRED_ANSWER_KEY_MISSING",
            "A questão exige gabarito e a referência não resolve.",
        )
    if not quiz.answer_key_ref or quiz.answer_key_ref != answer_key.ref:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "ANSWER_KEY_REFERENCE_MISMATCH",
            "A referência do gabarito não corresponde à questão.",
            answer_key=answer_key,
        )
    if answer_key.question_ref != quiz.ref:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "ANSWER_KEY_POINTS_TO_DIFFERENT_QUESTION",
            "O gabarito aponta para outra questão.",
            answer_key=answer_key,
        )
    if answer_key.accepted_answers:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "ACCEPTED_ANSWERS_NOT_SUPPORTED_BY_OPTION_GRADER",
            "A chave contém respostas aceitas que o corretor de alternativas não representa.",
            answer_key=answer_key,
        )
    if len(quiz.ref) > 100:
        return _failure(
            quiz,
            "blocked_incompatibility",
            "backend_incompatibility",
            "QUESTION_ID_EXCEEDS_API_LIMIT",
            "O identificador ultrapassa o limite do contrato de submissão do backend.",
            answer_key=answer_key,
        )

    if quiz.format == "other" and not quiz.options:
        prompt, extracted, parse_error = _split_options(quiz.prompt)
        if parse_error:
            if parse_error == "QUESTION_STEM_MISSING_OR_AMBIGUOUS":
                return _failure(
                    quiz,
                    "blocked_enunciado",
                    "enunciado",
                    parse_error,
                    "Não foi possível separar um enunciado inequívoco das alternativas.",
                    answer_key=answer_key,
                )
            category = "alternatives"
            return _failure(
                quiz,
                "blocked_alternatives",
                category,
                parse_error,
                "As alternativas não podem ser identificadas sem ambiguidade.",
                answer_key=answer_key,
            )
        if not prompt.strip() or len(extracted) < 2:
            return _failure(
                quiz,
                "blocked_enunciado",
                "enunciado",
                "QUESTION_STEM_MISSING_OR_AMBIGUOUS",
                "O enunciado não contém texto avaliável separado das alternativas.",
                answer_key=answer_key,
                alternative_count=len(extracted),
            )
        option_items = [
            QuizOptionOut(option_id=label.casefold(), text=text) for label, text in extracted
        ]
        format_source = "parsed_markdown"
    elif quiz.format == "multiple_choice" and quiz.options:
        prompt = quiz.prompt
        option_items = [
            QuizOptionOut(option_id=option.ref, text=option.text) for option in quiz.options
        ]
        format_source = "typed_options"
    else:
        return _failure(
            quiz,
            "blocked_incompatibility",
            "backend_incompatibility",
            "QUESTION_FORMAT_NOT_SUPPORTED_BY_CURRENT_GRADER",
            "O formato não pode ser convertido sem uma extensão explícita do avaliador.",
            answer_key=answer_key,
            alternative_count=len(quiz.options) or None,
        )

    if len(option_items) < 2 or len({item.option_id for item in option_items}) != len(option_items):
        return _failure(
            quiz,
            "blocked_alternatives",
            "alternatives",
            "ALTERNATIVE_IDS_MISSING_OR_DUPLICATED",
            "As identidades das alternativas estão ausentes ou duplicadas.",
            answer_key=answer_key,
            alternative_count=len(option_items),
        )
    if any(len(item.option_id) > 100 for item in option_items):
        return _failure(
            quiz,
            "blocked_incompatibility",
            "backend_incompatibility",
            "OPTION_ID_EXCEEDS_API_LIMIT",
            "Uma identidade de alternativa excede o limite do contrato do backend.",
            answer_key=answer_key,
            alternative_count=len(option_items),
        )

    key_label: str | None = None
    if answer_key.expected_answer:
        key_match = _LETTER_ANSWER.fullmatch(answer_key.expected_answer)
        if key_match:
            key_label = key_match.group(1).casefold()

    option_ids = {item.option_id for item in option_items}
    if answer_key.correct_option_ref is not None:
        if answer_key.correct_option_ref not in option_ids:
            return _failure(
                quiz,
                "blocked_gabarito",
                "answer_key",
                "CORRECT_OPTION_REFERENCE_NOT_FOUND",
                "A referência de alternativa correta não existe nesta questão.",
                answer_key=answer_key,
                alternative_count=len(option_items),
            )
        correct_option_id = answer_key.correct_option_ref
        if key_label is not None and key_label in option_ids and key_label != correct_option_id:
            return _failure(
                quiz,
                "blocked_gabarito",
                "answer_key",
                "ANSWER_KEY_SOURCES_CONFLICT",
                "A referência e o texto do gabarito indicam alternativas diferentes.",
                answer_key=answer_key,
                alternative_count=len(option_items),
            )
    elif key_label is not None and key_label in option_ids:
        correct_option_id = key_label
    else:
        return _failure(
            quiz,
            "blocked_gabarito",
            "answer_key",
            "ANSWER_KEY_NOT_UNAMBIGUOUS_OPTION_REFERENCE",
            "O gabarito não identifica exatamente uma alternativa disponível.",
            answer_key=answer_key,
            alternative_count=len(option_items),
        )

    try:
        public_question = QuizQuestionOut(
            question_id=quiz.ref,
            order=quiz.order,
            prompt=prompt,
            options=option_items,
        )
    except ValidationError:
        return _failure(
            quiz,
            "blocked_incompatibility",
            "backend_incompatibility",
            "PUBLIC_QUESTION_SCHEMA_REJECTED_CANDIDATE",
            "A projeção pública não satisfaz o schema de quiz do backend.",
            answer_key=answer_key,
            alternative_count=len(option_items),
        )

    candidate = ExperimentalQuizCandidate(
        public_question=public_question,
        answer_key_ref=answer_key.ref,
        private_answer_key=PrivateAnswerKeyCandidate(
            ref=answer_key.ref,
            question_ref=answer_key.question_ref,
            correct_option_id=correct_option_id,
            expected_answer=answer_key.expected_answer or "",
            accepted_answers=tuple(answer_key.accepted_answers),
            explanation=answer_key.explanation,
            source_markdown=answer_key.source_markdown or "",
            provenance=answer_key.provenance,
        ),
        content_version_sha256=_version_hash(
            quiz, answer_key, prompt, option_items, correct_option_id
        ),
        source_markdown=quiz.prompt,
        quiz_provenance=quiz.provenance,
    )

    try:
        # Exercise the exact pure grading contract, without persisting or
        # returning a score and without contacting the HTTP/API layer.
        from services.quizzes import grade_quiz_questions

        grade_quiz_questions([candidate.grader_record()], [])
    except (ImportError, ValueError, KeyError, TypeError):
        return _failure(
            quiz,
            "blocked_incompatibility",
            "backend_incompatibility",
            "CURRENT_GRADER_REJECTED_CANDIDATE",
            "O avaliador puro do backend rejeitou a projeção experimental.",
            answer_key=answer_key,
            alternative_count=len(option_items),
        )

    return QuizConversionOutcome(
        phase=phase,
        quiz_ref=quiz.ref,
        source_id=quiz.provenance.source_id or "",
        source_file=quiz.provenance.source_file,
        source_sha256=quiz.provenance.source_sha256,
        status="converted_candidate",
        category=format_source,
        reason_code="UNAMBIGUOUS_MULTIPLE_CHOICE_CANDIDATE",
        message="Candidato validado contra o schema público e o avaliador puro; não publicado.",
        detected_alternative_count=len(option_items),
        answer_key_ref=answer_key.ref,
        answer_key_source_id=answer_key.provenance.source_id,
        answer_key_source_file=answer_key.provenance.source_file,
        answer_key_source_sha256=answer_key.provenance.source_sha256,
        candidate=candidate,
    )


def analyze_bundle_quizzes(bundle: CurriculumImportBundle) -> list[QuizConversionOutcome]:
    """Analyze every quiz in stable phase/order/ref order, entirely in memory."""
    outcomes: list[QuizConversionOutcome] = []
    for phase_entry in sorted(bundle.phases, key=lambda item: item.phase):
        blocks = phase_entry.contract.blocks
        answer_keys = {block.ref: block for block in blocks if isinstance(block, AnswerKeyBlock)}
        quizzes = [block for block in blocks if isinstance(block, QuizBlock)]
        for quiz in sorted(quizzes, key=lambda item: (item.order, item.ref)):
            answer_key = answer_keys.get(quiz.answer_key_ref or "")
            outcome = convert_quiz_block(quiz, answer_key, phase=phase_entry.phase)
            outcomes.append(outcome)
    return outcomes


def coverage_csv(outcomes: list[QuizConversionOutcome]) -> str:
    """Serialize audit-safe coverage only; never include prompts or answer text."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "phase",
            "quiz_ref",
            "question_source_id",
            "source_file",
            "source_sha256",
            "answer_key_present",
            "answer_key_ref",
            "answer_key_source_id",
            "answer_key_source_file",
            "answer_key_source_sha256",
            "conversion_status",
            "category",
            "diagnostic_code",
            "alternative_count",
            "backend_question_schema",
            "publishable",
        ]
    )
    for outcome in sorted(outcomes, key=lambda item: (item.phase, item.quiz_ref)):
        converted = outcome.candidate is not None
        writer.writerow(
            [
                outcome.phase,
                outcome.quiz_ref,
                outcome.source_id,
                outcome.source_file,
                outcome.source_sha256,
                "yes" if outcome.answer_key_source_file else "no",
                outcome.answer_key_ref or "",
                outcome.answer_key_source_id or "",
                outcome.answer_key_source_file or "",
                outcome.answer_key_source_sha256 or "",
                outcome.status,
                outcome.category,
                outcome.reason_code,
                ""
                if outcome.detected_alternative_count is None
                else outcome.detected_alternative_count,
                "valid" if converted else "not_created",
                "no",
            ]
        )
    return output.getvalue()
