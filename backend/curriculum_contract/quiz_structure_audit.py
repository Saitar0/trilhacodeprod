"""Offline classification of quizzes that the objective converter blocks.

The audit records provenance and structural evidence only. It deliberately
never serializes prompts, answer keys, explanations, or private content.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

from curriculum_contract.models import AnswerKeyBlock, QuizBlock

from .bulk_import import CurriculumImportBundle
from .experimental_quiz_converter import QuizConversionOutcome

QuizClassification = Literal[
    "multiple_choice_recoverable",
    "multiple_choice_incomplete",
    "open_response",
    "discursive_exercise",
    "review_question",
    "unidentified",
    "ambiguous_answer_key",
]

_MULTIPLE_CHOICE_LABEL = re.compile(
    r"(?i)m[uú]ltipla\s+escolha|marque\s+uma\s+alternativa|assinale\s+uma\s+alternativa"
)
_REVIEW_HEADING = re.compile(
    r"(?im)^\s*#{1,6}\s+[^\n]*(?:perguntas?\s+de\s+revis[aã]o|revis[aã]o\s+das?\s+decis[oõ]es)"
)
_DISCURSIVE_DIRECTIVE = re.compile(
    r"(?i)\b(?:explique|justifique|compare|discuta|analise|argumente|proponha|"
    r"elabore|descreva|desenhe|represente|escreva|cite|liste|responda|"
    r"d[eê]\s+(?:ao\s+menos\s+)?\d+|verdadeiro\s+ou\s+falso)\b"
)
_SHORT_RESPONSE_LABEL = re.compile(r"(?i)\bresposta\s+curta\b")
_MATCHING_DIRECTIVE = re.compile(r"(?i)\b(?:associe|relacione)\b")
_ORDERING_DIRECTIVE = re.compile(r"(?i)\b(?:ordene|ordena[cç][aã]o|sequ[eê]ncia)\b")
_IDENTIFY_DIRECTIVE = re.compile(r"(?i)\b(?:identifique|determine|calcule)\b")
_QUESTION_LINE = re.compile(r"^\s*\d+[.)]\s+\S")


@dataclass(frozen=True, slots=True)
class QuizStructureAudit:
    phase: int
    quiz_ref: str
    question_source_id: str
    migrated_quiz_file: str
    quiz_source_sha256: str
    answer_key_ref: str
    answer_key_source_id: str
    migrated_answer_key_file: str
    answer_key_source_sha256: str
    original_source_file: str
    original_question_line: int
    original_answer_line: int
    answer_line_evidence: str
    previous_status: str
    current_status: str
    conversion_change: str
    classification: QuizClassification
    source_format_signal: str
    reason_code: str
    rationale: str
    alternative_count: int | None
    answer_text_included: Literal["no"] = "no"


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\r", " ")).strip()


def original_unit_source_path(repo_root: Path, migrated_source_file: str) -> tuple[str, Path]:
    """Resolve a migrated quiz/key path to its one official source unit page."""
    source = PurePosixPath(migrated_source_file)
    parts = source.parts
    try:
        marker = parts.index("Conteudos_migrado")
    except ValueError as exc:
        raise ValueError("quiz provenance is outside Conteudos_migrado") from exc
    if marker < 3 or len(parts) <= marker + 2:
        raise ValueError("quiz provenance does not identify a phase and unit")
    phase_dir, unit_dir = parts[marker + 1 : marker + 3]
    if not re.fullmatch(r"Fase_(?:[1-9]|10)", phase_dir):
        raise ValueError("quiz provenance has an invalid phase directory")
    if not unit_dir or unit_dir in {".", ".."} or "/" in unit_dir:
        raise ValueError("quiz provenance has an invalid unit directory")
    original = PurePosixPath(*parts[:marker], "Conteudos", phase_dir, f"{unit_dir}.md")
    resolved = (repo_root / Path(*original.parts)).resolve()
    if not resolved.is_relative_to(repo_root.resolve()):
        raise ValueError("resolved source page escapes the repository")
    if not resolved.is_file():
        raise FileNotFoundError(f"official source page is missing: {original.as_posix()}")
    return original.as_posix(), resolved


def _question_source_line(prompt: str, source_text: str) -> int:
    question_line = next(
        (line.strip() for line in prompt.splitlines() if _QUESTION_LINE.match(line)), None
    )
    if question_line is None:
        raise ValueError("quiz prompt has no explicit numbered source question")
    needle = _normalize(question_line)
    for line_number, line in enumerate(source_text.splitlines(), start=1):
        if needle in _normalize(line):
            return line_number
    raise ValueError("question block could not be matched to its official source line")


def _answer_source_line(
    expected_answer: str | None,
    source_text: str,
    question_line: int,
    answer_source_id: str,
) -> tuple[int, str]:
    if not expected_answer:
        raise ValueError("answer-key source has no expected answer text")
    expected = _normalize(expected_answer)
    lines = source_text.splitlines()
    response_label = re.compile(r"(?i)(?:\*\*)?resposta(?:\*\*)?\s*:")

    # Newer sources place the answer inline with the question; require its
    # explicit label so a short value such as "B" cannot match an option label.
    for index in range(max(0, question_line - 1), min(len(lines), question_line + 8)):
        line = lines[index]
        match = response_label.search(line)
        if match and expected in _normalize(line[match.end() :]):
            return index + 1, "inline_labeled_answer"

    number_match = re.search(r"(\d+)$", answer_source_id)
    if number_match:
        target_number = int(number_match.group(1))
        headings = [
            (index, len(match.group(1)))
            for index, line in enumerate(lines[question_line:], start=question_line)
            if (match := re.match(r"^\s*(#{1,6})\s+[^\n]*gabarito", line, re.IGNORECASE))
        ]
        if headings:
            heading_index, heading_level = headings[0]
            section_end = len(lines)
            for index in range(heading_index + 1, len(lines)):
                next_heading = re.match(r"^\s*(#{1,6})\s+", lines[index])
                if next_heading and len(next_heading.group(1)) <= heading_level:
                    section_end = index
                    break
            numbered_answer = re.compile(rf"^\s*{target_number}[.)]\s+\S")
            for index in range(heading_index + 1, section_end):
                if numbered_answer.match(lines[index]):
                    entry_end = section_end
                    for next_index in range(index + 1, section_end):
                        if re.match(r"^\s*\d+[.)]\s+\S", lines[next_index]):
                            entry_end = next_index
                            break
                    entry_text = _normalize("\n".join(lines[index:entry_end]))
                    if expected in entry_text:
                        return index + 1, "numbered_gabarito_entry"
                    return 0, "numbered_entry_does_not_match_key_text"

    # Long, unique inline answer text can still be traced without guessing a
    # line for one-character labels or common tokens.
    if len(expected) >= 20:
        normalized_source = _normalize(source_text)
        if normalized_source.count(expected) == 1:
            prefix = expected[: min(48, len(expected))]
            for index, line in enumerate(lines, start=1):
                if prefix in _normalize(line):
                    return index, "unique_answer_text"
    return 0, "source_line_not_unambiguously_resolved"


def classify_blocked_quiz(
    outcome: QuizConversionOutcome,
    quiz: QuizBlock,
    answer_key: AnswerKeyBlock,
    *,
    previous_status: str,
) -> tuple[QuizClassification, str, str]:
    """Classify one item using explicit source structure, never answer meaning."""
    if outcome.status == "converted_candidate":
        return (
            "multiple_choice_recoverable",
            "multiple_choice",
            "Alternativas explícitas e ordenadas; chave vinculada a uma opção única.",
        )
    if outcome.status == "blocked_gabarito":
        return (
            "ambiguous_answer_key",
            "multiple_choice",
            "A associação da chave ao quiz existe, mas não há referência inequívoca a uma opção.",
        )
    if outcome.reason_code in {
        "DUPLICATE_OPTION_TEXT",
        "ALTERNATIVE_MARKERS_AMBIGUOUS_OR_OUT_OF_ORDER",
        "OPTION_TEXT_EMPTY",
    } or _MULTIPLE_CHOICE_LABEL.search(quiz.prompt):
        return (
            "multiple_choice_incomplete",
            "multiple_choice_incomplete",
            "A fonte indica múltipla escolha ou marcadores de alternativas, mas o conjunto não é avaliável com segurança.",
        )
    if _REVIEW_HEADING.search(quiz.prompt):
        return (
            "review_question",
            "review",
            "O cabeçalho original classifica o item como revisão; não há alternativas para correção objetiva.",
        )
    if _SHORT_RESPONSE_LABEL.search(quiz.prompt):
        return (
            "open_response",
            "short_answer",
            "A fonte identifica resposta curta; o corretor atual não avalia respostas textuais.",
        )
    if _MATCHING_DIRECTIVE.search(quiz.prompt):
        return (
            "unidentified",
            "matching_unsupported",
            "A fonte pede associação entre elementos; o avaliador atual não representa esse formato sem extensão.",
        )
    if _ORDERING_DIRECTIVE.search(quiz.prompt):
        return (
            "unidentified",
            "ordering_unsupported",
            "A fonte pede ordenação ou sequência; o avaliador atual não representa esse formato sem extensão.",
        )
    if _DISCURSIVE_DIRECTIVE.search(quiz.prompt):
        return (
            "discursive_exercise",
            "discursive",
            "O enunciado solicita justificativa, explicação, comparação ou produção textual não suportada pelo corretor objetivo.",
        )
    if _IDENTIFY_DIRECTIVE.search(quiz.prompt):
        return (
            "open_response",
            "short_answer",
            "O enunciado pede identificação textual sem alternativas; o avaliador atual não corrige a resposta aberta.",
        )
    if "?" in quiz.prompt:
        return (
            "open_response",
            "short_answer",
            "Pergunta textual sem alternativas explícitas; resposta aberta não é corrigida pelo avaliador atual.",
        )
    if previous_status == "converted_candidate":
        return (
            "unidentified",
            "regression_requires_review",
            "A candidata anterior não foi reconhecida na execução atual; requer investigação antes de qualquer conversão.",
        )
    return (
        "unidentified",
        "unidentified",
        "A estrutura não permite identificar com segurança um formato avaliável.",
    )


def audit_quiz_items(
    bundle: CurriculumImportBundle,
    outcomes: list[QuizConversionOutcome],
    previous_statuses: dict[tuple[int, str], str],
    repo_root: Path,
) -> list[QuizStructureAudit]:
    """Join each keyed quiz to its prior result and verify original provenance."""
    quiz_map: dict[str, tuple[int, QuizBlock]] = {}
    key_map: dict[str, AnswerKeyBlock] = {}
    for phase_entry in bundle.phases:
        for block in phase_entry.contract.blocks:
            if isinstance(block, QuizBlock):
                quiz_map[block.ref] = (phase_entry.phase, block)
            elif isinstance(block, AnswerKeyBlock):
                key_map[block.ref] = block

    records: list[QuizStructureAudit] = []
    seen: set[tuple[int, str]] = set()
    for outcome in sorted(outcomes, key=lambda item: (item.phase, item.quiz_ref)):
        previous = previous_statuses.get((outcome.phase, outcome.quiz_ref))
        if previous is None:
            raise ValueError(f"quiz is missing from the 14C baseline: {outcome.quiz_ref}")
        if outcome.quiz_ref not in quiz_map:
            raise ValueError(f"quiz outcome has no source block: {outcome.quiz_ref}")
        phase_number, quiz = quiz_map[outcome.quiz_ref]
        if phase_number != outcome.phase:
            raise ValueError(f"quiz phase does not match its provenance: {outcome.quiz_ref}")
        if not quiz.answer_key_required or not quiz.answer_key_ref:
            continue
        key = key_map.get(quiz.answer_key_ref)
        if key is None:
            raise ValueError(f"required answer key is missing: {quiz.ref}")
        if key.question_ref != quiz.ref or key.ref != outcome.answer_key_ref:
            raise ValueError(f"answer-key association is inconsistent: {quiz.ref}")

        original_path, source_path = original_unit_source_path(
            repo_root, quiz.provenance.source_file
        )
        source_text = source_path.read_text(encoding="utf-8")
        question_line = _question_source_line(quiz.prompt, source_text)
        answer_line, answer_line_evidence = _answer_source_line(
            key.expected_answer,
            source_text,
            question_line,
            key.provenance.source_id or "",
        )
        classification, source_format_signal, rationale = classify_blocked_quiz(
            outcome, quiz, key, previous_status=previous
        )

        key_id = (outcome.phase, outcome.quiz_ref)
        if key_id in seen:
            raise ValueError(f"duplicate quiz outcome: {outcome.quiz_ref}")
        seen.add(key_id)
        if previous == "converted_candidate" and outcome.status != "converted_candidate":
            change = "regressed_candidate"
        elif previous != "converted_candidate" and outcome.status == "converted_candidate":
            change = "new_candidate"
        elif previous == outcome.status:
            change = "unchanged"
        else:
            change = "status_changed_still_blocked"

        records.append(
            QuizStructureAudit(
                phase=outcome.phase,
                quiz_ref=quiz.ref,
                question_source_id=quiz.provenance.source_id or "",
                migrated_quiz_file=quiz.provenance.source_file,
                quiz_source_sha256=quiz.provenance.source_sha256,
                answer_key_ref=key.ref,
                answer_key_source_id=key.provenance.source_id or "",
                migrated_answer_key_file=key.provenance.source_file,
                answer_key_source_sha256=key.provenance.source_sha256,
                original_source_file=original_path,
                original_question_line=question_line,
                original_answer_line=answer_line,
                answer_line_evidence=answer_line_evidence,
                previous_status=previous,
                current_status=outcome.status,
                conversion_change=change,
                classification=classification,
                source_format_signal=source_format_signal,
                reason_code=outcome.reason_code,
                rationale=rationale,
                alternative_count=outcome.detected_alternative_count,
            )
        )

    expected = {
        key for key, status in previous_statuses.items() if status != "unscored_review_pending"
    }
    if seen != expected:
        missing = sorted(expected - seen)[:1]
        unexpected = sorted(seen - expected)[:1]
        raise ValueError(f"audit coverage mismatch; missing={missing}, unexpected={unexpected}")
    return records


def classification_csv(records: list[QuizStructureAudit]) -> str:
    """Serialize per-ID classification and provenance without answer content."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "phase",
            "quiz_ref",
            "question_source_id",
            "original_source_file",
            "original_question_line",
            "migrated_quiz_file",
            "quiz_source_sha256",
            "answer_key_ref",
            "answer_key_source_id",
            "original_answer_line",
            "answer_line_evidence",
            "migrated_answer_key_file",
            "answer_key_source_sha256",
            "previous_14c_status",
            "current_14d_status",
            "conversion_change",
            "classification",
            "source_format_signal",
            "diagnostic_code",
            "alternative_count",
            "rationale",
            "answer_text_included",
            "publishable",
        ]
    )
    for item in sorted(records, key=lambda value: (value.phase, value.quiz_ref)):
        writer.writerow(
            [
                item.phase,
                item.quiz_ref,
                item.question_source_id,
                item.original_source_file,
                item.original_question_line,
                item.migrated_quiz_file,
                item.quiz_source_sha256,
                item.answer_key_ref,
                item.answer_key_source_id,
                item.original_answer_line,
                item.answer_line_evidence,
                item.migrated_answer_key_file,
                item.answer_key_source_sha256,
                item.previous_status,
                item.current_status,
                item.conversion_change,
                item.classification,
                item.source_format_signal,
                item.reason_code,
                "" if item.alternative_count is None else item.alternative_count,
                item.rationale,
                item.answer_text_included,
                "no",
            ]
        )
    return output.getvalue()


def previous_statuses_from_csv(csv_text: str) -> dict[tuple[int, str], str]:
    rows = csv.DictReader(io.StringIO(csv_text))
    statuses: dict[tuple[int, str], str] = {}
    for row in rows:
        key = (int(row["phase"]), row["quiz_ref"])
        if key in statuses:
            raise ValueError(f"duplicate quiz in 14C baseline: {key[1]}")
        statuses[key] = row["conversion_status"]
    return statuses
