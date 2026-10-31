"""Read-only pilot converter from one reviewed Markdown unit to C16 import shape.

This is a narrow Beta 2 experiment. It does not replace the migration
intermediate contract or invoke the operational importer by itself. The only
write path is an explicit, separately isolated test harness.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

CONVERTER_VERSION = "beta2-unit-adapter/1.0"
BACKEND_IMPORT_SHAPE = "track/options/nodes/relations"
_SECTION_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
_SUBSECTION_RE = re.compile(r"(?m)^###\s+(.+?)\s*$")
_H1_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
_QUESTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
_OPTION_RE = re.compile(r"^\s*-\s*([A-H])\.\s+(.+)$")
_ANSWER_RE = re.compile(r"^(\d+)\.\s+\*\*([A-H])\.\*\*\s*(.*)$")


class CurriculumConversionError(ValueError):
    """The source does not match the bounded pilot grammar."""


@dataclass(frozen=True)
class QuizQuestion:
    source_number: int
    prompt: str
    options: tuple[tuple[str, str], ...]
    correct_letter: str
    explanation: str
    stable_ref: str


@dataclass(frozen=True)
class ManualExercise:
    source_number: int
    title: str
    student_prompt: str
    instructor_reference: str | None
    criteria: tuple[str, ...]
    stable_ref: str


@dataclass(frozen=True)
class Reference:
    title: str
    url: str
    description: str
    raw: str
    stable_ref: str


@dataclass(frozen=True)
class PilotUnit:
    source_id: str
    source_path: str
    source_revision: str
    source_sha256: str
    source_sha256_lf: str
    frontmatter: dict[str, Any]
    title: str
    objective: str
    theory: str
    summary: str
    quiz: tuple[QuizQuestion, ...]
    exercises: tuple[ManualExercise, ...]
    completion_criteria: str
    connections: str
    references: tuple[Reference, ...]
    raw_sections: dict[str, str]
    unsupported_destinations: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_manifest(self) -> dict[str, Any]:
        """Return non-content provenance and mapping diagnostics."""
        payload = self.to_import_payload()
        unit_node = payload["nodes"][0]
        blocks = unit_node["blocks"]
        counts: dict[str, int] = {}
        for block in blocks:
            counts[block["type"]] = counts.get(block["type"], 0) + 1
        return {
            "manifest_schema": "trilhacode.beta2.pilot-manifest/1.0",
            "converter_version": CONVERTER_VERSION,
            "backend_import_shape": BACKEND_IMPORT_SHAPE,
            "source": {
                "id": self.source_id,
                "path": self.source_path,
                "revision": self.source_revision,
                "sha256_raw": self.source_sha256,
                "sha256_lf_normalized": self.source_sha256_lf,
                "frontmatter_status": self.frontmatter.get("status"),
            },
            "destination": {
                "track_slug": payload["track"]["slug"],
                "node_ref": unit_node["ref"],
                "block_refs": [block["ref"] for block in blocks],
                "block_counts": counts,
                "status": "draft",
            },
            "source_counts": {
                "quiz_questions": len(self.quiz),
                "manual_exercises": len(self.exercises),
                "references": len(self.references),
            },
            "field_mappings": [
                {"source": "frontmatter.key/title", "destination": "node.ref/title", "status": "mapped"},
                {"source": "frontmatter.status=rascunho", "destination": "track/node/block status=draft", "status": "mapped; publication prohibited"},
                {"source": "frontmatter.tipo/carater/profundidade", "destination": "node.pedagogical_type/requirement/depth", "status": "mapped; backend taxonomy validates values"},
                {"source": "frontmatter.tags/estimativa_minutos", "destination": "node.tags/estimated_minutes", "status": "mapped"},
                {"source": "Objetivo", "destination": "node.description", "status": "mapped"},
                {"source": "Teoria", "destination": "content_blocks.theory_text.data.body", "status": "mapped as one block; topic segmentation not retained"},
                {"source": "Resumo", "destination": "content_blocks.summary.data.body", "status": "mapped"},
                {"source": "Quiz questions and answer key", "destination": "versioned quiz data; answer fields remain private until publication projection", "status": "mapped with legacy-editor warnings"},
                {"source": "Practice prompts and autocorrection criteria", "destination": "exercise_open.data.prompt/criteria", "status": "mapped"},
                {"source": "Instructor answer references", "destination": None, "status": "withheld; no private destination proven"},
                {"source": "Completion criterion", "destination": None, "status": "unsupported by current import schema"},
                {"source": "Reference title and URL", "destination": "reference.data.citation/url", "status": "mapped"},
                {"source": "Reference description", "destination": None, "status": "unsupported; not persisted"},
                {"source": "Internal/cross-unit connections", "destination": None, "status": "unresolved; references outside the pilot payload"},
            ],
            "unsupported_destinations": list(self.unsupported_destinations),
            "warnings": list(self.warnings),
            "no_source_write": True,
            "no_publication": True,
        }

    def to_import_payload(self) -> dict[str, Any]:
        """Map supported fields to the current C16 legacy import contract.

        The payload intentionally creates a private, draft-only synthetic track.
        Completion criteria and internal connections remain in this typed result
        and are reported as unsupported; they are never silently reassigned.
        """
        token = _stable_token(self.source_id)
        blocks: list[dict[str, Any]] = []
        if self.theory:
            blocks.append({
                "ref": f"{token}-theory-001",
                "type": "theory_text",
                "title": "Teoria",
                "status": "draft",
                "data": {"body": self.theory},
            })
        if self.summary:
            blocks.append({
                "ref": f"{token}-summary-001",
                "type": "summary",
                "title": "Resumo",
                "status": "draft",
                "data": {"body": self.summary},
            })
        for question in self.quiz:
            option_ids = {letter: f"option-{letter.lower()}" for letter, _ in question.options}
            explanation = question.explanation
            blocks.append({
                "ref": question.stable_ref,
                "type": "quiz",
                "title": f"Questão {question.source_number}",
                "status": "draft",
                "data": {
                    "activity_schema_version": 1,
                    "prompt": question.prompt,
                    "options": [
                        {"id": option_ids[letter], "label": label}
                        for letter, label in question.options
                    ],
                    "correct_option_id": option_ids[question.correct_letter],
                    "feedback": {"correct": explanation, "incorrect": explanation},
                },
            })
        for exercise in self.exercises:
            data: dict[str, Any] = {
                "prompt": exercise.student_prompt,
                "grading": "manual",
            }
            if exercise.criteria:
                data["criteria"] = list(exercise.criteria)
            blocks.append({
                "ref": exercise.stable_ref,
                "type": "exercise_open",
                "title": exercise.title,
                "status": "draft",
                "data": data,
            })
        for reference in self.references:
            blocks.append({
                "ref": reference.stable_ref,
                "type": "reference",
                "title": reference.title,
                "status": "draft",
                "data": {"citation": reference.title, "url": reference.url},
            })

        estimated_minutes = _as_nonnegative_int(self.frontmatter.get("estimativa_minutos"))
        tags = self.frontmatter.get("tags", [])
        node: dict[str, Any] = {
            "ref": f"{token}-unit",
            "kind": "submodule",
            "title": self.title,
            "status": "draft",
            "description": self.objective,
            "pedagogical_type": self.frontmatter.get("tipo", ""),
            "requirement": self.frontmatter.get("carater", ""),
            "depth": self.frontmatter.get("profundidade", ""),
            "tags": tags if isinstance(tags, list) else [],
            "blocks": blocks,
        }
        if estimated_minutes is not None:
            node["estimated_minutes"] = estimated_minutes
        return {
            "track": {
                "title": f"[Beta 2 isolada] {self.title}",
                "slug": f"beta2-pilot-{token}",
                "description": "Registro sintético para prova de importação; permanece em draft.",
                "visibility": "private",
                "hierarchy": ["phase", "module", "submodule", "topic"],
            },
            "options": {"create_missing_tags": True},
            "nodes": [node],
            "relations": [],
        }


def convert_markdown_unit(
    source: bytes | str,
    *,
    source_path: str,
    source_revision: str,
) -> PilotUnit:
    """Parse the bounded first-phase Markdown shape without modifying source."""
    normalized_path = _validate_source_path(source_path)
    if not source_revision.strip():
        raise CurriculumConversionError("source_revision é obrigatório")
    raw_bytes = source if isinstance(source, bytes) else source.encode("utf-8")
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CurriculumConversionError("a fonte deve ser UTF-8 válido") from exc
    if "\x00" in text:
        raise CurriculumConversionError("a fonte contém NUL")

    frontmatter, body = _parse_frontmatter(text)
    title_match = _H1_RE.search(body)
    if not title_match:
        raise CurriculumConversionError("título H1 ausente")
    title = title_match.group(1).strip()
    source_id = str(frontmatter.get("key", "")).strip()
    if not source_id:
        raise CurriculumConversionError("frontmatter.key ausente")

    sections = _split_h2(body)
    required = ("Objetivo", "Teoria", "Resumo", "Verificação — quiz", "Prática — três níveis", "Critério de conclusão", "Referências")
    missing = [name for name in required if name not in sections]
    if missing:
        raise CurriculumConversionError(f"seções obrigatórias ausentes: {', '.join(missing)}")

    questions = _parse_quiz(sections["Verificação — quiz"], source_id)
    exercises = _parse_exercises(sections["Prática — três níveis"], source_id)
    references = _parse_references(sections["Referências"], source_id)
    known = set(required) | {"Conexões"}
    unknown = sorted(set(sections) - known)
    warnings = []
    if unknown:
        warnings.append("Seções H2 não mapeadas: " + ", ".join(unknown))
    if not references:
        warnings.append("A seção de referências não contém entradas reconhecidas; o texto bruto foi preservado.")
    unsupported = ["completion_criteria: sem campo ou bloco equivalente no importador C16"]
    if sections.get("Conexões"):
        unsupported.append("connections: links curriculares não resolvidos no escopo de uma unidade")
    if any(exercise.instructor_reference for exercise in exercises):
        unsupported.append(
            "exercise instructor_reference: sem destino privado de instrutor comprovado; não persistido"
        )
    if any(reference.description for reference in references):
        unsupported.append("reference.description: bloco C16 reference só declara citation e url; não persistida")
    return PilotUnit(
        source_id=source_id,
        source_path=normalized_path,
        source_revision=source_revision,
        source_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        source_sha256_lf=hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        frontmatter=frontmatter,
        title=title,
        objective=sections["Objetivo"],
        theory=sections["Teoria"],
        summary=sections["Resumo"],
        quiz=questions,
        exercises=exercises,
        completion_criteria=sections["Critério de conclusão"],
        connections=sections.get("Conexões", ""),
        references=references,
        raw_sections=sections,
        unsupported_destinations=tuple(unsupported),
        warnings=tuple(warnings),
    )


def _validate_source_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise CurriculumConversionError("source_path deve ser POSIX, relativo e normalizado")
    return path.as_posix()


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise CurriculumConversionError("frontmatter YAML delimitado ausente")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise CurriculumConversionError("frontmatter sem delimitador final") from exc
    metadata: dict[str, Any] = {}
    current_list: str | None = None
    for line in lines[1:end]:
        if line.startswith("  - ") and current_list:
            metadata[current_list].append(_unquote(line[4:].strip()))
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key, raw_value = key.strip(), raw_value.strip()
        if not key:
            raise CurriculumConversionError("chave vazia no frontmatter")
        if not raw_value:
            metadata[key] = []
            current_list = key
        else:
            metadata[key] = _unquote(raw_value)
            current_list = None
    return metadata, "\n".join(lines[end + 1 :])


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _split_h2(text: str) -> dict[str, str]:
    matches = list(_SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        if heading in sections:
            raise CurriculumConversionError(f"seção H2 duplicada: {heading}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[heading] = text[match.end() : end].strip()
    return sections


def _find_subsection(text: str, label: str) -> str:
    matches = list(_SUBSECTION_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip() == label:
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            return text[match.end() : end].strip()
    raise CurriculumConversionError(f"subseção H3 ausente: {label}")


def _parse_quiz(text: str, source_id: str) -> tuple[QuizQuestion, ...]:
    question_text = _find_subsection(text, "Questões")
    answer_text = _find_subsection(text, "Gabarito comentado")
    parsed: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active_option: str | None = None
    for line in question_text.splitlines():
        question_match = _QUESTION_RE.match(line.strip())
        option_match = _OPTION_RE.match(line)
        if question_match:
            if current:
                parsed.append(current)
            current = {"number": int(question_match.group(1)), "prompt": [question_match.group(2)], "options": []}
            active_option = None
        elif option_match and current:
            current["options"].append([option_match.group(1), option_match.group(2)])
            active_option = option_match.group(1)
        elif current and line.strip():
            if active_option:
                current["options"][-1][1] += "\n" + line.strip()
            else:
                current["prompt"].append(line.strip())
    if current:
        parsed.append(current)
    answers: dict[int, tuple[str, str]] = {}
    active_answer: int | None = None
    for line in answer_text.splitlines():
        answer_match = _ANSWER_RE.match(line.strip())
        if answer_match:
            number = int(answer_match.group(1))
            answers[number] = (answer_match.group(2), answer_match.group(3).strip())
            active_answer = number
        elif active_answer is not None and line.strip():
            letter, explanation = answers[active_answer]
            answers[active_answer] = (letter, (explanation + "\n" + line.strip()).strip())
    if not parsed:
        raise CurriculumConversionError("nenhuma questão reconhecida")
    numbers = [item["number"] for item in parsed]
    if len(numbers) != len(set(numbers)):
        raise CurriculumConversionError("número de questão duplicado")
    if set(numbers) != set(answers):
        raise CurriculumConversionError("questões e gabarito não correspondem exatamente")
    result = []
    for item in parsed:
        options = tuple((letter, label.strip()) for letter, label in item["options"])
        if len(options) < 2 or len({letter for letter, _ in options}) != len(options):
            raise CurriculumConversionError(f"alternativas ausentes ou duplicadas na questão {item['number']}")
        correct, explanation = answers[item["number"]]
        if correct not in {letter for letter, _ in options}:
            raise CurriculumConversionError(f"gabarito fora das alternativas na questão {item['number']}")
        result.append(QuizQuestion(
            source_number=item["number"],
            prompt="\n".join(item["prompt"]).strip(),
            options=options,
            correct_letter=correct,
            explanation=explanation,
            stable_ref=f"{_stable_token(source_id)}-quiz-{item['number']:03d}",
        ))
    return tuple(result)


def _parse_exercises(text: str, source_id: str) -> tuple[ManualExercise, ...]:
    matches = list(_SUBSECTION_RE.finditer(text))
    exercises: list[ManualExercise] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        numbered = re.match(r"^(\d+)\.\s+(.+)$", heading)
        if not numbered:
            continue
        number = int(numbered.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_body = text[match.end() : end].strip()
        prompt, instructor_reference = _extract_instructor_reference(section_body)
        criteria = _extract_criteria(section_body)
        exercises.append(ManualExercise(
            source_number=number,
            title=numbered.group(2).strip(),
            student_prompt=prompt,
            instructor_reference=instructor_reference,
            criteria=tuple(criteria),
            stable_ref=f"{_stable_token(source_id)}-exercise-{number:03d}",
        ))
    if not exercises:
        raise CurriculumConversionError("nenhuma prática numerada foi reconhecida")
    numbers = [item.source_number for item in exercises]
    if len(numbers) != len(set(numbers)):
        raise CurriculumConversionError("número de prática duplicado")
    return tuple(exercises)


def _extract_instructor_reference(text: str) -> tuple[str, str | None]:
    anchors = ("**Gabarito comentado**", "**Referência para autocorreção**")
    matches = [(text.find(anchor), anchor) for anchor in anchors if text.find(anchor) >= 0]
    if not matches:
        return text.strip(), None
    offset, anchor = min(matches)
    return text[:offset].strip(), text[offset + len(anchor) :].strip() or None


def _extract_criteria(text: str) -> list[str]:
    marker = re.search(r"(?m)^\*\*Critérios de autocorreção[^\n]*\*\*\s*$", text)
    if not marker:
        return []
    section = text[marker.end() :]
    values = []
    for line in section.splitlines():
        stripped = line.strip()
        bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", stripped)
        if bullet:
            values.append(bullet.group(1).strip())
    return values


def _parse_references(text: str, source_id: str) -> tuple[Reference, ...]:
    result: list[Reference] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw.startswith("-"):
            continue
        match = re.match(r"^-\s+\*\*(.+?)\*\*\s*·\s*(https?://\S+)\s*·\s*(.*)$", raw)
        if not match:
            continue
        title, url, description = match.groups()
        result.append(Reference(
            title=title.strip(),
            url=url.rstrip(".,)"),
            description=description.strip(),
            raw=raw,
            stable_ref=f"{_stable_token(source_id)}-reference-{len(result) + 1:03d}",
        ))
    return tuple(result)


def _stable_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not token:
        raise CurriculumConversionError("source id não pode gerar identificador vazio")
    return token


def _as_nonnegative_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
