"""Fail-closed converter from the migrated Markdown tree to contract 1.2.

This module is deliberately separate from the production importer. It reads
repo-relative Markdown and YAML, builds the existing 12A Pydantic models, and
does not write files or contact a database.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

import yaml
from pydantic import ValidationError

from .models import (
    CONTRACT_VERSION,
    AcceptanceCriteriaBlock,
    AnswerKeyBlock,
    BlockStatus,
    ChecklistBlock,
    ChecklistItem,
    CompletionCriteriaBlock,
    ContentBlock,
    CurriculumNode,
    CurriculumRelation,
    FeedbackBlock,
    FlashcardBlock,
    InstructorNoteBlock,
    IntermediateContract,
    ObjectiveBlock,
    PracticeBlock,
    ProjectDecisionBlock,
    ProjectDelivery,
    ProjectMilestone,
    ProjectReviewBlock,
    ProjectScenarioBlock,
    ProjectSpec,
    ProjectVariant,
    QuizBlock,
    ReferenceBlock,
    RelationKind,
    RubricBlock,
    RubricDimension,
    ScoreScale,
    SharedPlacement,
    SolutionBlock,
    SourceManifest,
    SourceProvenance,
    SummaryBlock,
    TheoryBlock,
    canonical_json,
)
from .validation import Diagnostic, DiagnosticSeverity, validate_contract, verify_source_hash

CONVERTER_VERSION = "12c.1"
HIDDEN_ANSWER_ORDER = 1_000_000
HIDDEN_SOLUTION_ORDER = 2_000_000
HIDDEN_FEEDBACK_ORDER = 3_000_000


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class SourceMapping:
    """Trace one source file to every contract entity derived from it."""

    source_file: str
    source_id: str
    source_type: str
    source_sha256: str
    destination_refs: tuple[str, ...]
    normalizations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConversionResult:
    contract: IntermediateContract | None
    diagnostics: tuple[Diagnostic, ...]
    mappings: tuple[SourceMapping, ...]
    converted_unit_keys: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.contract is not None and not any(
            item.severity == DiagnosticSeverity.ERROR for item in self.diagnostics
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "converted_unit_keys": list(self.converted_unit_keys),
            "mappings": [asdict(item) for item in self.mappings],
            "diagnostics": [item.model_dump(mode="json") for item in self.diagnostics],
            "contract": self.contract.model_dump(mode="json") if self.contract else None,
        }

    def canonical_json(self) -> str:
        if not self.ok or self.contract is None:
            raise ValueError("conversion has blocking diagnostics; no contract may be serialized")
        return canonical_json(self.contract)


@dataclass(frozen=True)
class _ParsedFile:
    path: Path
    repo_path: str
    raw: bytes
    text: str
    frontmatter: dict[str, Any]
    body: str
    sha256: str

    @property
    def file_id(self) -> str:
        value = self.frontmatter.get("arquivo_id")
        return value if isinstance(value, str) else ""

    @property
    def source_type(self) -> str:
        value = self.frontmatter.get("tipo_arquivo")
        return value if isinstance(value, str) else ""


def _diag(
    code: str,
    message: str,
    *,
    source_file: str | None = None,
    entity_ref: str | None = None,
    field: str | None = None,
    reference: str | None = None,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    remediation: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=severity,
        source_file=source_file,
        entity_ref=entity_ref,
        field=field,
        reference=reference,
        message=message,
        remediation=remediation,
    )


def _repo_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _safe_path(root: Path, relative: str) -> Path:
    candidate = PurePosixPath(relative)
    if (
        candidate.is_absolute()
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise ValueError(f"unsafe repository-relative path: {relative!r}")
    resolved = (root / Path(*candidate.parts)).resolve()
    resolved.relative_to(root.resolve())
    return resolved


def _load_yaml_mapping(text: str, *, label: str) -> dict[str, Any]:
    value = yaml.load(text, Loader=_UniqueKeyLoader)
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be a YAML mapping with string keys")
    return value


def _read_frontmatter(path: Path, root: Path) -> _ParsedFile:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0] not in {"---\n", "---\r\n"}:
        raise ValueError("Markdown file has no opening YAML frontmatter delimiter")
    closing = next(
        (index for index in range(1, len(lines)) if lines[index] in {"---\n", "---\r\n", "---"}),
        None,
    )
    if closing is None:
        raise ValueError("Markdown file has no closing YAML frontmatter delimiter")
    fm_text = "".join(lines[1:closing])
    body = "".join(lines[closing + 1 :])
    fm = _load_yaml_mapping(fm_text, label="frontmatter")
    return _ParsedFile(
        path=path,
        repo_path=_repo_path(path, root),
        raw=raw,
        text=text,
        frontmatter=fm,
        body=body,
        sha256=hashlib.sha256(raw).hexdigest(),
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"frontmatter value {type(value).__name__} is not JSON-compatible")


def _phase_number(phase: Any) -> int:
    if not isinstance(phase, str) or not phase.startswith("Fase_"):
        raise ValueError("manifest 'fase' must have form Fase_N")
    value = phase.removeprefix("Fase_")
    if not value.isdigit() or not 1 <= int(value) <= 10:
        raise ValueError(f"invalid phase identifier {phase!r}")
    return int(value)


def _stable_token(value: str) -> str:
    result: list[str] = []
    separator = False
    for char in value.casefold():
        if char.isascii() and char.isalnum():
            if separator and result:
                result.append("-")
            result.append(char)
            separator = False
        elif char in "-_ .":
            separator = True
    return "".join(result).strip("-")


def _status(value: Any) -> tuple[BlockStatus, bool]:
    if value in {"rascunho", "draft", "em_revisao", "em revisão"}:
        return "draft", False
    if value in {"publicado", "published", "ativo", "active"}:
        return "published", False
    if value in {"arquivado", "archived"}:
        return "archived", False
    # Phase-page status is learner progress (for example, "nao-iniciada"),
    # not the contract's publication status. Keep the original under metadata.
    return "draft", True


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise ValueError("expected a string or a list of strings")


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return None


def _manifest_file_paths(value: Any) -> Iterable[tuple[str, str | None]]:
    """Yield (path, declared arquivo_id) from manifest file specifications."""
    if isinstance(value, str) and value.endswith(".md"):
        yield value, None
        return
    if isinstance(value, Mapping):
        path = value.get("path")
        file_id = value.get("arquivo_id")
        if isinstance(path, str) and path.endswith(".md"):
            yield path, file_id if isinstance(file_id, str) else None
            return
        for child in value.values():
            yield from _manifest_file_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from _manifest_file_paths(child)


def _declared_unit_files(
    manifest: Mapping[str, Any], unit: Mapping[str, Any]
) -> tuple[dict[str, str | None], set[str]]:
    """Return known files and required files for one topic.

    `arquivos_comuns` defines reusable names, not a guarantee that every unit
    has every common document. Only files listed for this unit are required.
    """
    paths: dict[str, str | None] = {"README.md": None}
    required = {"README.md"}
    for spec in manifest.get("arquivos_comuns", {}).values():
        for path, file_id in _manifest_file_paths(spec):
            previous = paths.get(path)
            if previous is not None and file_id is not None and previous != file_id:
                raise ValueError(f"manifest declares conflicting IDs for {path}")
            paths[path] = file_id or previous
    for spec in unit.get("arquivos", {}).values():
        for path, file_id in _manifest_file_paths(spec):
            previous = paths.get(path)
            if previous is not None and file_id is not None and previous != file_id:
                raise ValueError(f"manifest declares conflicting IDs for {path}")
            paths[path] = file_id or previous
            required.add(path)
    return paths, required


def _unit_subject_specs(unit: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Normalize the approved manifest's string and structured subject forms."""
    raw_subjects = unit.get("assuntos", [])
    title_map = unit.get("titulo_assuntos", {})
    subjects: list[tuple[str, str]] = []
    if not isinstance(raw_subjects, list):
        return subjects
    for item in raw_subjects:
        if isinstance(item, str):
            title = title_map.get(item, item) if isinstance(title_map, Mapping) else item
            subjects.append((item, str(title)))
        elif isinstance(item, Mapping):
            slug = item.get("slug")
            title = item.get("titulo", item.get("title", slug))
            if isinstance(slug, str) and isinstance(title, str):
                subjects.append((slug, title))
    return subjects


_COMMA_DELIMITED_ITEM_IDS = re.compile(r"\s*[A-Za-z]+\d+(?:\s*,\s*[A-Za-z]+\d+)+\s*")


def _source_item_labels(frontmatter: Mapping[str, Any]) -> list[str]:
    """Return literal item labels as declared in source frontmatter."""
    return _string_list(frontmatter.get("itens_origem"))


def _source_item_ids(frontmatter: Mapping[str, Any]) -> list[str]:
    """Expand only explicitly comma-delimited lists of item IDs."""
    labels = _source_item_labels(frontmatter)
    item_ids: list[str] = []
    for label in labels:
        if _COMMA_DELIMITED_ITEM_IDS.fullmatch(label):
            item_ids.extend(part.strip() for part in label.split(","))
        else:
            item_ids.append(label)
    return item_ids


def _item_number(source_id: str) -> int | None:
    token = _item_key(source_id)
    match = re.fullmatch(r"[A-Z]+(\d+)", token)
    return int(match.group(1)) if match else None


def _item_entity_ref(parsed: _ParsedFile, source_id: str, role: str) -> str:
    if len(_source_item_ids(parsed.frontmatter)) == 1:
        return parsed.file_id
    return f"{parsed.file_id}-{role}-{_stable_token(source_id)}"


def _split_at_offsets(body: str, offsets: Sequence[int]) -> list[str]:
    if not offsets:
        return [body]
    boundaries = [0, *offsets[1:], len(body)]
    return [body[boundaries[index] : boundaries[index + 1]] for index in range(len(offsets))]


def _split_quiz_items(parsed: _ParsedFile) -> list[tuple[str, str]]:
    """Split only on explicit line or bold-inline markers matching source IDs."""
    source_ids = _source_item_ids(parsed.frontmatter)
    if len(source_ids) <= 1:
        return [(source_ids[0] if source_ids else parsed.file_id, parsed.body)]

    if parsed.source_type == "project_review_questions":
        if not all(re.fullmatch(r"R\d+", _item_key(item)) for item in source_ids):
            raise ValueError("project review IDs must use the explicit R<number> form")
        expected_review_numbers = [int(_item_key(item)[1:]) for item in source_ids]
        bullets = list(re.finditer(r"(?m)^[ \t]*-[ \t]+", parsed.body))
        if len(bullets) == len(source_ids):
            pieces = _split_at_offsets(parsed.body, [match.start() for match in bullets])
            if len(pieces) == len(source_ids) and "".join(pieces) == parsed.body:
                return list(zip(source_ids, pieces, strict=True))

        # Project reviews also occur as numbered questions, including source
        # blocks where the original Markdown renderer placed all questions on
        # one physical line. Accept only the exact R-number sequence declared
        # by itens_origem; the delimiter after a preceding question mark keeps
        # prose such as HTTP 404 from being mistaken for a question boundary.
        numbered = list(re.finditer(r"(?m)(?:^[ \t]*|(?<=\?)[ \t]*)(\d+)\.[ \t]+", parsed.body))
        if [int(match.group(1)) for match in numbered] != expected_review_numbers:
            raise ValueError("project review boundaries do not exactly match itens_origem")
        pieces = _split_at_offsets(parsed.body, [match.start() for match in numbered])
        if len(pieces) != len(source_ids) or "".join(pieces) != parsed.body:
            raise ValueError(
                "project review boundary reconstruction did not preserve the source body"
            )
        return list(zip(source_ids, pieces, strict=True))

    expected: list[int] = []
    for item in source_ids:
        number = _item_number(item)
        if number is None:
            raise ValueError("multi-question quiz IDs must contain a numeric suffix")
        expected.append(number)

    # A line-start marker is primary. Some migrated quiz files keep a selected
    # set of numbered questions inline, separated by the preceding question's
    # literal `?`; this same exact sequence check keeps numbers such as HTTP
    # 404 embedded in prose from becoming boundaries.
    matches = list(re.finditer(r"(?m)^[ \t]*(\d+)\.[ \t]+", parsed.body))
    if [int(match.group(1)) for match in matches] != expected:
        # Source-backed quiz files can be a non-contiguous subset of the
        # original numbered quiz. Accept inline numbering only immediately
        # after a question mark (or after its closing bold delimiter) and only
        # when every marker matches the exact ordered IDs declared by
        # itens_origem.
        matches = list(
            re.finditer(
                r"(?m)(?:^[ \t]*|(?<=\?)[ \t]*|(?<=\?\*\*)[ \t]*)(\d+)\.[ \t]+",
                parsed.body,
            )
        )
    if [int(match.group(1)) for match in matches] != expected:
        raise ValueError("numbered question boundaries do not exactly match itens_origem")
    offsets = [match.start() for match in matches]
    pieces = _split_at_offsets(parsed.body, offsets)
    if len(pieces) != len(source_ids) or "".join(pieces) != parsed.body:
        raise ValueError("question boundary reconstruction did not preserve the source body")
    return list(zip(source_ids, pieces, strict=True))


def _split_answer_items(parsed: _ParsedFile) -> list[tuple[str, str]]:
    """Split answer text only at explicit labels or source-aligned numbered lines."""
    source_ids = _source_item_ids(parsed.frontmatter)
    if len(source_ids) <= 1:
        return [(source_ids[0] if source_ids else parsed.file_id, parsed.body)]

    source_keys = [_item_key(source_id) for source_id in source_ids]
    if len(source_keys) != len(set(source_keys)):
        if parsed.source_type == "answer_key_pratica" and len(set(source_keys)) == 1:
            # The migration manifest explicitly separates subsegments of one
            # practice answer. Keep one canonical solution and the whole body.
            return [(source_ids[0], parsed.body)]
        raise ValueError("duplicate answer item IDs do not define distinct answer targets")

    label = "**Resposta:"
    label_offsets: list[int] = []
    search_at = 0
    while (offset := parsed.body.find(label, search_at)) >= 0:
        label_offsets.append(offset)
        search_at = offset + len(label)
    if len(label_offsets) == len(source_ids):
        pieces = _split_at_offsets(parsed.body, label_offsets)
        return list(zip(source_ids, pieces, strict=True))

    expected = [_item_number(item) for item in source_ids]
    numbered = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", parsed.body))
    if (
        all(number is not None for number in expected)
        and [int(match.group(1)) for match in numbered] == expected
    ):
        pieces = _split_at_offsets(parsed.body, [match.start() for match in numbered])
        return list(zip(source_ids, pieces, strict=True))

    # Some reviewed project answers are one bold paragraph per line without a
    # label. Accept only exact line-start boundaries and an exact item count.
    bold_offsets: list[int] = []
    cursor = 0
    for line in parsed.body.splitlines(keepends=True):
        if line.lstrip().startswith("**"):
            bold_offsets.append(cursor + len(line) - len(line.lstrip()))
        cursor += len(line)
    if len(bold_offsets) == len(source_ids):
        pieces = _split_at_offsets(parsed.body, bold_offsets)
        return list(zip(source_ids, pieces, strict=True))

    # A reviewed source can place one complete answer paragraph on each
    # physical line without a label. Accept only an exact line-to-ID count;
    # blank/continuation lines make this representation unsupported.
    lines = parsed.body.splitlines(keepends=True)
    if lines and all(line.strip() for line in lines) and len(lines) == len(source_ids):
        offsets: list[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line)
        pieces = _split_at_offsets(parsed.body, offsets)
        if len(pieces) == len(source_ids) and "".join(pieces) == parsed.body:
            return list(zip(source_ids, pieces, strict=True))

    # Frontmatter parsing retains the structural blank line after `---`.
    # Preserve that prefix in the first answer while pairing only when the
    # remaining non-empty physical lines map one-to-one to declared IDs.
    nonempty_indices = [index for index, line in enumerate(lines) if line.strip()]
    if (
        len(nonempty_indices) == len(source_ids)
        and nonempty_indices
        and nonempty_indices == list(range(nonempty_indices[0], len(lines)))
    ):
        starts: list[int] = []
        cursor = 0
        for line in lines:
            starts.append(cursor)
            cursor += len(line)
        offsets = [0, *(starts[index] for index in nonempty_indices[1:])]
        pieces = _split_at_offsets(parsed.body, offsets)
        if len(pieces) == len(source_ids) and "".join(pieces) == parsed.body:
            return list(zip(source_ids, pieces, strict=True))
    raise ValueError("answer boundaries do not exactly match itens_origem")


def _item_key(value: str) -> str:
    token = "".join(char for char in value.upper() if char.isalnum())
    split = 0
    while split < len(token) and token[split].isalpha():
        split += 1
    prefix, number = token[:split], token[split:]
    if number.isdecimal():
        return f"{prefix}{int(number)}"
    return token


def _coverage_subjects(unit: Mapping[str, Any], item_ids: Sequence[str]) -> list[str]:
    subjects = [slug for slug, _title in _unit_subject_specs(unit)]
    coverage = unit.get("cobertura", {})
    wanted = {_item_key(item) for item in item_ids}
    matched: list[str] = []

    def visit(value: Any, subject: str | None = None) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                key_text = str(key)
                if key_text == "compartilhados" and isinstance(child, Mapping):
                    for item, consumers in child.items():
                        if _item_key(str(item)) in wanted and isinstance(consumers, list):
                            matched.extend(str(item) for item in consumers if str(item) in subjects)
                elif key_text == "exclusivos" and isinstance(child, Mapping):
                    for owner, items in child.items():
                        if isinstance(items, list) and any(
                            _item_key(str(item)) in wanted for item in items
                        ):
                            if str(owner) in subjects:
                                matched.append(str(owner))
                elif key_text.endswith("_compartilhados") and isinstance(child, list):
                    if subject is not None and any(
                        _item_key(str(item)) in wanted for item in child
                    ):
                        matched.append(subject)
                elif key_text.endswith("_exclusivos") and isinstance(child, list):
                    if subject is not None and any(
                        _item_key(str(item)) in wanted for item in child
                    ):
                        matched.append(subject)
                elif key_text == "por_assunto" and isinstance(child, Mapping):
                    for owner, details in child.items():
                        if str(owner) in subjects:
                            visit(details, str(owner))
                elif key_text in subjects and isinstance(child, (Mapping, list)):
                    visit(child, key_text)
                else:
                    visit(child, subject)
        elif isinstance(value, list):
            return

    visit(coverage)
    ordered: list[str] = []
    for subject in subjects:
        if subject in matched and subject not in ordered:
            ordered.append(subject)
    return ordered


def _phase_page(
    repo_root: Path, phase_number: int
) -> tuple[Path, dict[str, Any], str, dict[int, tuple[int, str]]]:
    course_root = repo_root / "docs" / "courses" / "trilhacode"
    for path in sorted(course_root.glob("*.md")):
        try:
            parsed = _read_frontmatter(path, repo_root)
        except (UnicodeDecodeError, ValueError, yaml.YAMLError):
            continue
        fm = parsed.frontmatter
        if fm.get("tipo") == "fase" and _integer(fm.get("ordem")) == phase_number:
            modules: dict[int, tuple[int, str]] = {}
            order = 0
            for line in parsed.body.splitlines():
                if not line.startswith("## Módulo "):
                    continue
                header = line.removeprefix("## Módulo ")
                if " — " not in header:
                    continue
                number_text, title = header.split(" — ", 1)
                if number_text.isdecimal():
                    order += 1
                    modules[int(number_text)] = (order, title)
            return path, fm, parsed.sha256, modules
    raise ValueError(f"official phase page not found for phase {phase_number}")


def _first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title
    return None


def _title(parsed: _ParsedFile) -> str:
    for field in ("titulo_marco", "title", "titulo"):
        value = parsed.frontmatter.get(field)
        if isinstance(value, str) and value:
            return value
    return _first_heading(parsed.body) or parsed.path.stem


def _provenance(
    parsed: _ParsedFile, source_role: str, source_id: str | None = None
) -> SourceProvenance:
    return SourceProvenance(
        source_file=parsed.repo_path,
        source_sha256=parsed.sha256,
        manifest_ref=parsed.frontmatter.get("parent_key", "migrated-markdown"),
        source_role=source_role,
        source_id=source_id or (parsed.file_id or None),
    )


def _frontmatter_node(
    repo_root: Path,
    phase_number: int,
    manifest: Mapping[str, Any],
    unit_key: str,
    unit: Mapping[str, Any],
    order: int,
) -> tuple[CurriculumNode, _ParsedFile]:
    destination_root = _safe_path(repo_root, str(manifest["destino_raiz"]))
    unit_root = _safe_path(destination_root, str(unit["pasta"]))
    parsed = _read_frontmatter(unit_root / "README.md", repo_root)
    fm = parsed.frontmatter
    if not parsed.file_id:
        raise ValueError(f"{parsed.repo_path}: README lacks arquivo_id")
    if fm.get("key") not in {None, unit_key}:
        raise ValueError(f"{parsed.repo_path}: key does not match manifest unit {unit_key}")
    status, _ = _status(fm.get("status"))
    raw_tags = fm.get("tags", [])
    tags = (
        [str(item) for item in raw_tags]
        if isinstance(raw_tags, list)
        else ([str(raw_tags)] if raw_tags else [])
    )
    module_number = int(unit_key.split(".", 1)[0])
    return (
        CurriculumNode(
            ref=parsed.file_id,
            kind="submodule",
            parent_ref=f"f{phase_number}-module-{module_number}",
            title=str(fm.get("title") or unit.get("titulo_original") or unit_key),
            order=order,
            status=status,
            estimated_minutes=_integer(fm.get("estimativa_minutos")),
            source_metadata=_json_safe(fm),
            tags=tags,
            provenance=_provenance(parsed, "unit-index-frontmatter", parsed.file_id),
        ),
        parsed,
    )


def _unit_status(parsed: _ParsedFile) -> BlockStatus:
    return _status(parsed.frontmatter.get("status"))[0]


def _project_steps(project: ProjectSpec) -> list[ProjectDelivery | ProjectMilestone]:
    return [*project.deliveries, *project.milestones]


def _frontmatter_paths_match(
    root: Path,
    unit_root: Path,
    unit: Mapping[str, Any],
    manifest: Mapping[str, Any],
    diagnostics: list[Diagnostic],
) -> dict[str, _ParsedFile]:
    expected, required = _declared_unit_files(manifest, unit)
    actual_paths = {
        path.relative_to(unit_root).as_posix(): path
        for path in unit_root.rglob("*.md")
        if path.is_file()
    }
    for relative in sorted(required - set(actual_paths)):
        diagnostics.append(
            _diag(
                "SOURCE_FILE_MISSING",
                "Manifest declares a Markdown file that does not exist.",
                source_file=(unit_root / relative).relative_to(root).as_posix(),
                field="arquivos",
                reference=relative,
                remediation="Restore the source-backed migrated file or correct the manifest before conversion.",
            )
        )
    for relative in sorted(set(actual_paths) - set(expected)):
        diagnostics.append(
            _diag(
                "SOURCE_FILE_UNDECLARED",
                "Unit directory contains a Markdown file not declared by the manifest.",
                source_file=actual_paths[relative].relative_to(root).as_posix(),
                field="arquivos",
                reference=relative,
                remediation="Declare the existing file in the approved manifest; do not ignore it silently.",
            )
        )
    parsed_files: dict[str, _ParsedFile] = {}
    for relative, path in sorted(actual_paths.items()):
        try:
            parsed = _read_frontmatter(path, root)
        except (UnicodeDecodeError, ValueError, yaml.YAMLError) as error:
            diagnostics.append(
                _diag(
                    "FRONTMATTER_INVALID",
                    str(error),
                    source_file=path.relative_to(root).as_posix(),
                    remediation="Correct the YAML frontmatter in the migrated source; the converter will not guess its fields.",
                )
            )
            continue
        declared_id = expected.get(relative)
        if declared_id and parsed.file_id != declared_id:
            diagnostics.append(
                _diag(
                    "MANIFEST_FRONTMATTER_ID_MISMATCH",
                    "arquivo_id in Markdown differs from the manifest declaration.",
                    source_file=parsed.repo_path,
                    entity_ref=parsed.file_id or None,
                    field="arquivo_id",
                    reference=declared_id,
                    remediation="Reconcile the approved manifest and migrated frontmatter without changing content implicitly.",
                )
            )
        if not parsed.file_id:
            diagnostics.append(
                _diag(
                    "SOURCE_ID_MISSING",
                    "Content file has no arquivo_id.",
                    source_file=parsed.repo_path,
                    field="arquivo_id",
                    remediation="Use the source-backed stable file ID already declared by the migration manifest.",
                )
            )
        parsed_files[relative] = parsed
    return parsed_files


def _base_order(parsed: _ParsedFile) -> int:
    order = _integer(parsed.frontmatter.get("ordem"))
    if order is None:
        raise ValueError(f"{parsed.repo_path}: ordem must be a non-negative integer")
    # Source order is scoped independently by file type in the migrated tree.
    # Add a stable type lane so theory/Q/P blocks with the same `ordem` remain
    # ordered but do not collide in the contract's per-context order key.
    lane = {
        "objetivo": 1,
        "theory": 10,
        "quiz": 20,
        "project_review_questions": 21,
        "flashcard": 30,
        "flashcards": 30,
        "practice": 40,
        "checklist": 50,
        "project_decisions": 51,
        "project_scenarios": 52,
        "project_review": 53,
        "instructor_note": 54,
        "acceptance_criteria": 60,
        "rubric": 70,
        "resumo": 80,
        "criterio": 81,
        "referencias": 90,
        "milestone": 0,
        "project_milestone": 0,
    }.get(parsed.source_type)
    if lane is None:
        raise ValueError(
            f"{parsed.repo_path}: no explicit order lane for source type {parsed.source_type!r}"
        )
    return order * 100 + lane


def _line_items(body: str) -> list[tuple[str, bool | None]]:
    """Extract list text and checkbox state while retaining source Markdown elsewhere."""
    result: list[tuple[str, bool | None]] = []
    for line in body.splitlines():
        text = line.strip()
        if text.startswith("- [ ] "):
            result.append((text[6:], False))
        elif text.startswith(("- [x] ", "- [X] ")):
            result.append((text[6:], True))
        elif text.startswith("- ") or text.startswith("* "):
            result.append((text[2:], None))
        else:
            prefix, separator, rest = text.partition(". ")
            if separator and prefix.isdecimal():
                result.append((rest, None))
    return result


def _checklist_items(body: str, file_id: str) -> list[ChecklistItem]:
    entries = _line_items(body)
    if not entries:
        entries = [(body, None)]
    return [
        ChecklistItem(
            ref=f"item-{index:03d}-{_stable_token(file_id)}",
            text=text,
            checked=checked,
        )
        for index, (text, checked) in enumerate(entries, start=1)
    ]


def _extract_answer(body: str) -> tuple[str, str | None, tuple[str, ...]]:
    """Split only the source's explicit numbered-bold-answer marker."""
    for line in body.splitlines():
        stripped = line.lstrip()
        prefix, separator, rest = stripped.partition(". **")
        if not separator or not prefix.isdecimal():
            continue
        answer, closing_marker, explanation = rest.partition("**")
        if closing_marker and answer:
            return (
                f"**{answer}**",
                explanation,
                ("numbered answer marker moved to source_id order",),
            )
    response_label = "**Resposta:"
    label_at = body.find(response_label)
    if label_at >= 0:
        value_start = label_at + len(response_label)
        answer_end = body.find("**", value_start)
        if answer_end >= 0:
            answer = body[value_start:answer_end].strip()
            if answer:
                surrounding = body[:label_at] + body[answer_end + 2 :]
                answer_explanation = surrounding.strip() or None
                return (
                    answer,
                    answer_explanation,
                    ("explicit Resposta label mapped to expected_answer",),
                )
    return (
        body,
        None,
        (
            "answer and explanation retained together because no recognized literal separator exists",
        ),
    )


def _flashcard_parts(line: str) -> tuple[str, str, str | None] | None:
    text = line.strip()
    if text.startswith("- **Pergunta:** "):
        question_marker = "- **Pergunta:** "
        response_marker = " **Resposta:** "
        feedback_marker = " **Feedback:** "
        response_at = text.find(response_marker)
        feedback_at = text.find(feedback_marker)
        if response_at < 0:
            return None
        front = text[len(question_marker) : response_at]
        if feedback_at >= 0:
            back = text[response_at + len(response_marker) : feedback_at]
            feedback = text[feedback_at + len(feedback_marker) :]
        else:
            back = text[response_at + len(response_marker) :]
            feedback = None
        if front and back:
            return front, back, feedback
    if text.startswith("- **"):
        close = text.find("**", 4)
        if close > 4:
            front = text[4:close]
            back = text[close + 2 :].lstrip()
            if front and back:
                return front, back, None
    return None


def _flashcards(parsed: _ParsedFile) -> list[tuple[str, str, str | None, str]]:
    source_ids = _source_item_ids(parsed.frontmatter)
    lines = [line for line in parsed.body.splitlines() if line.strip()]
    cards: list[tuple[str, str, str | None, str]] = []
    for index, line in enumerate(lines, start=1):
        parts = _flashcard_parts(line)
        if parts is None:
            if line.startswith("#"):
                continue
            raise ValueError(f"{parsed.repo_path}: unrecognized flashcard line {line!r}")
        if index - 1 < len(source_ids):
            source_id = source_ids[index - 1]
        elif len(source_ids) == 1:
            source_id = source_ids[0]
        else:
            source_id = f"card{index:02d}"
        front, back, feedback = parts
        cards.append((source_id, front, feedback, back))
    if not cards:
        raise ValueError(f"{parsed.repo_path}: no flashcard entries found")
    if source_ids and len(source_ids) != len(cards):
        raise ValueError(
            f"{parsed.repo_path}: {len(source_ids)} itens_origem but {len(cards)} flashcard entries"
        )
    return cards


def _rubric_scale(body: str, frontmatter: Mapping[str, Any]) -> tuple[int, int] | None:
    raw_scale = frontmatter.get("escala_rubrica")
    candidates = [str(raw_scale)] if raw_scale is not None else []
    candidates.extend(line for line in body.splitlines() if "0–" in line or "0-" in line)
    for text in candidates:
        for separator in ("–", "-"):
            if separator in text:
                left, right = text.split(separator, 1)
                start = "".join(char for char in left if char.isdigit())
                end = "".join(char for char in right if char.isdigit())
                if start.isdecimal() and end.isdecimal():
                    return int(start), int(end)
    # Matrix headers may carry the scale even if no frontmatter scale exists.
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        scores: list[int] = []
        for cell in cells[1:]:
            label = cell.split("—", 1)[0].split("-", 1)[0].strip()
            if label.isdecimal():
                scores.append(int(label))
        if len(scores) >= 2 and scores == list(range(scores[0], scores[-1] + 1)):
            return scores[0], scores[-1]
    return None


def _rubric_dimensions(
    body: str, scale: tuple[int, int] | None, file_id: str
) -> tuple[list[RubricDimension], float | None, str | None]:
    table_rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped[1:-1].split("|")]
            if all(not cell or set(cell) <= {"-", ":", " "} for cell in cells):
                continue
            table_rows.append(cells)
    dimensions: list[RubricDimension] = []
    threshold = _threshold(body)
    note = _rubric_notes(body, table_rows)
    if table_rows and scale is not None:
        header = table_rows[0]
        score_columns: list[tuple[int, str]] = []
        for index, cell in enumerate(header[1:], start=1):
            score_text = cell.split("—", 1)[0].split("-", 1)[0].strip()
            if score_text.isdecimal():
                label = cell.split("—", 1)[1].strip() if "—" in cell else ""
                score_columns.append((int(score_text), label))
        for row_index, row in enumerate(table_rows[1:], start=1):
            if len(row) != len(header) or not row[0]:
                continue
            descriptors: dict[str, str] = {}
            for cell_index, (score, label) in enumerate(score_columns, start=1):
                value = row[cell_index]
                if label:
                    value = f"{label}\n{value}"
                if value:
                    descriptors[str(score)] = value
            dimensions.append(
                RubricDimension(
                    ref=f"dimension-{row_index:03d}-{_stable_token(file_id)}",
                    title=row[0],
                    weight=1.0,
                    descriptors=descriptors,
                )
            )
    if not dimensions:
        criterion_texts: list[str] = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                criterion_texts.append(stripped[2:])
        if not criterion_texts:
            criterion_texts = [body]
        dimensions = [
            RubricDimension(
                ref=f"dimension-{index:03d}-{_stable_token(file_id)}",
                title=text,
                weight=1.0,
                descriptors={},
            )
            for index, text in enumerate(criterion_texts, start=1)
        ]
    return dimensions, threshold, note


def _threshold(body: str) -> float | None:
    for line in body.splitlines():
        lowered = line.casefold()
        if not any(
            marker in lowered for marker in ("limiar", "pelo menos", "mínimo", "aceite somente")
        ):
            continue
        match = re.search(r"(\d+)\s*/\s*(\d+)", line)
        if match:
            return float(int(match.group(1)))
    return None


def _rubric_notes(body: str, table_rows: Sequence[Sequence[str]]) -> str | None:
    notes: list[str] = []
    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        if not table_rows and (
            stripped.startswith("- ") or re.match(r"^\d+\.\s+\*\*", stripped) is not None
        ):
            continue
        if stripped:
            notes.append(line)
    note = "".join(notes)
    return note if note.strip() else None


def _reference_line(line: str) -> tuple[str, str | None, str | None]:
    """Return (label, URL, target token) without rewriting the source line."""
    label = line.strip()
    if "**" in label:
        start = label.find("**")
        end = label.find("**", start + 2)
        if end > start:
            label = label[start + 2 : end]
    for scheme in ("https://", "http://"):
        start = line.find(scheme)
        if start >= 0:
            url = line[start:].split()[0].rstrip(".,;)")
            return label, url, None
    if "[[" in line and "]]" in line:
        start = line.find("[[") + 2
        end = line.find("]]", start)
        if end > start:
            return label, None, line[start:end]
    marker = "]("
    start = line.find(marker)
    if start >= 0:
        end = line.find(")", start + len(marker))
        if end > start:
            return label, None, line[start + len(marker) : end]
    return label, None, None


def _source_relations(unit: Mapping[str, Any]) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for field in ("conexoes", "relacoes_curriculares_fonte", "pre_requisitos_declarados"):
        raw = unit.get(field)
        if isinstance(raw, list):
            relations.extend(item for item in raw if isinstance(item, dict))
        elif isinstance(raw, dict):
            relations.extend(item for item in raw.values() if isinstance(item, dict))
    return relations


def _relation_kind(value: Any) -> tuple[RelationKind, bool]:
    text = str(value or "").casefold().replace("-", "_")
    if "pre" in text and "requisito" in text:
        return "prerequisite", True
    if "complement" in text:
        return "complement", False
    if "revisit" in text or "revisita" in text:
        return "revisit", False
    return "related", False


def _relation_target(item: Mapping[str, Any]) -> str | None:
    for key in ("destino", "target", "target_key", "unidade", "key"):
        value = item.get(key)
        if isinstance(value, str):
            return value
    return None


def _relation_line(lines: Sequence[str], target: str) -> str | None:
    for line in lines:
        if target in line and ("[[" in line or "](" in line):
            return line
    return None


def _target_path(repo_root: Path, source_file: str, target: str) -> Path | None:
    if target.startswith("http://") or target.startswith("https://"):
        return None
    if "#" in target:
        target = target.split("#", 1)[0]
    if not target:
        return None
    base = _safe_path(repo_root, source_file).parent
    try:
        return (base / target).resolve()
    except (OSError, ValueError):
        return None


def _add_mapping(
    mappings: list[SourceMapping],
    parsed: _ParsedFile,
    destination_refs: Iterable[str],
    normalizations: Iterable[str] = (),
) -> None:
    mappings.append(
        SourceMapping(
            source_file=parsed.repo_path,
            source_id=parsed.file_id,
            source_type=parsed.source_type,
            source_sha256=parsed.sha256,
            destination_refs=tuple(dict.fromkeys(destination_refs)),
            normalizations=tuple(normalizations),
        )
    )


def _convert_manifest_samples_impl(
    repo_root: Path,
    manifest_path: str,
    unit_keys: Sequence[str],
    *,
    source_revision: str,
    converter_version: str = CONVERTER_VERSION,
) -> ConversionResult:
    """Convert selected units from one phase manifest into the 12A contract.

    The output is in-memory only. Callers may serialize only when ``result.ok``
    is true, and sample runs should write only to a temporary directory.
    """
    root = repo_root.resolve()
    diagnostics: list[Diagnostic] = []
    mappings: list[SourceMapping] = []
    requested_keys = tuple(dict.fromkeys(unit_keys))
    selected_keys = requested_keys
    try:
        manifest_file = _safe_path(root, manifest_path)
        manifest_bytes = manifest_file.read_bytes()
        manifest = _load_yaml_mapping(manifest_bytes.decode("utf-8"), label="migration manifest")
        phase_number = _phase_number(manifest.get("fase"))
        phase_key = f"Fase_{phase_number}"
        units: Mapping[str, Any] = manifest.get("unidades", {})
        if not units:
            raise ValueError("manifest has no units")
        order_units = _string_list(manifest.get("ordem_unidades"))
        if not order_units:
            raise ValueError("manifest has no ordem_unidades")
        for key in requested_keys:
            if key not in units:
                raise ValueError(f"selected unit {key!r} is absent from the manifest")
        requested_set = set(requested_keys)
        selected_keys = tuple(key for key in order_units if key in requested_set)
        if len(selected_keys) != len(requested_set):
            raise ValueError("manifest ordem_unidades contains duplicate unit keys")
        phase_page, phase_fm, phase_sha, modules = _phase_page(root, phase_number)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as error:
        diagnostic = _diag(
            "CONVERSION_INPUT_INVALID",
            str(error),
            source_file=manifest_path,
            remediation="Provide the verified phase manifest and source files; conversion fails closed on missing or invalid input.",
        )
        return ConversionResult(None, (diagnostic,), (), selected_keys)

    id_prefix = f"f{phase_number}"
    phase_ref = f"{id_prefix}-phase-{phase_number}"
    phase_provenance = SourceProvenance(
        source_file=_repo_path(phase_page, root),
        source_sha256=phase_sha,
        manifest_ref=manifest_path,
        source_role="official-phase-page",
        source_id=str(phase_fm.get("title", phase_key)),
    )
    phase_status, phase_status_defaulted = _status(phase_fm.get("status"))
    if phase_status_defaulted:
        diagnostics.append(
            _diag(
                "NODE_STATUS_TRANSLATED",
                "Phase progress status was not treated as publication status; contract node uses draft while source metadata retains the original value.",
                source_file=phase_provenance.source_file,
                entity_ref=phase_ref,
                field="status",
                severity=DiagnosticSeverity.INFO,
                remediation="Keep progress state and content publication state separate in a future platform schema.",
            )
        )
    nodes: list[CurriculumNode] = [
        CurriculumNode(
            ref=phase_ref,
            kind="phase",
            parent_ref=None,
            title=str(
                phase_fm.get("title")
                or _first_heading(phase_page.read_text(encoding="utf-8"))
                or phase_key
            ),
            order=phase_number,
            status=phase_status,
            estimated_minutes=None,
            source_metadata=_json_safe(phase_fm),
            tags=[str(item) for item in phase_fm.get("tags", [])]
            if isinstance(phase_fm.get("tags", []), list)
            else [],
            provenance=phase_provenance,
        )
    ]
    modules_in_use = sorted(
        {int(key.split(".", 1)[0]) for key in units},
        key=lambda item: modules[item][0] if item in modules else item,
    )
    module_refs: dict[int, str] = {}
    for module_number in modules_in_use:
        if module_number not in modules:
            diagnostics.append(
                _diag(
                    "MODULE_SOURCE_NOT_FOUND",
                    f"Module {module_number} from unit IDs is absent from the official phase page.",
                    source_file=phase_provenance.source_file,
                    reference=str(module_number),
                    remediation="Correct the source module reference or provide the official page that contains it.",
                )
            )
            continue
        module_order, module_title = modules[module_number]
        module_ref = f"{id_prefix}-module-{module_number}"
        module_refs[module_number] = module_ref
        nodes.append(
            CurriculumNode(
                ref=module_ref,
                kind="module",
                parent_ref=phase_ref,
                title=module_title,
                order=module_order,
                status="draft",
                estimated_minutes=None,
                source_metadata={"module_number": module_number},
                tags=[],
                provenance=phase_provenance.model_copy(
                    update={
                        "source_role": "official-module-heading",
                        "source_id": f"module-{module_number}",
                    }
                ),
            )
        )

    unit_node_by_key: dict[str, CurriculumNode] = {}
    unit_parsed_by_key: dict[str, _ParsedFile] = {}
    topic_ref_by_key_slug: dict[tuple[str, str], str] = {}
    origin_path_to_unit: dict[str, str] = {}
    module_positions: dict[str, int] = {}
    for position, unit_key in enumerate(order_units, start=1):
        unit = units.get(unit_key)
        if not isinstance(unit, dict):
            diagnostics.append(
                _diag(
                    "UNIT_MANIFEST_INVALID",
                    f"Unit {unit_key} is not a manifest mapping.",
                    source_file=manifest_path,
                    reference=unit_key,
                    remediation="Correct the unit entry in the approved manifest.",
                )
            )
            continue
        module_number = int(unit_key.split(".", 1)[0])
        module_positions[unit_key] = position
        try:
            node, readme = _frontmatter_node(root, phase_number, manifest, unit_key, unit, position)
            if module_number not in module_refs:
                raise ValueError(f"unit {unit_key} references missing module node {module_number}")
            node = node.model_copy(update={"parent_ref": module_refs[module_number]})
            unit_node_by_key[unit_key] = node
            unit_parsed_by_key[unit_key] = readme
            nodes.append(node)
            _add_mapping(
                mappings,
                readme,
                [node.ref],
                ("README frontmatter represented as submodule metadata",),
            )
            origin = unit.get("origem")
            if isinstance(origin, str):
                origin_path_to_unit[origin] = unit_key
            for subject_order, (subject, subject_title) in enumerate(
                _unit_subject_specs(unit), start=1
            ):
                topic_ref = f"{id_prefix}-topic-{_stable_token(unit_key)}-{_stable_token(subject)}"
                topic_ref_by_key_slug[(unit_key, subject)] = topic_ref
                nodes.append(
                    CurriculumNode(
                        ref=topic_ref,
                        kind="topic",
                        parent_ref=node.ref,
                        title=str(subject_title),
                        order=subject_order,
                        status=node.status,
                        estimated_minutes=None,
                        source_metadata={"manifest_subject_slug": subject},
                        tags=[],
                        provenance=_provenance(readme, "subject-index", subject),
                    )
                )
        except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError, ValidationError) as error:
            diagnostics.append(
                _diag(
                    "UNIT_INDEX_INVALID",
                    str(error),
                    source_file=str(unit.get("pasta", unit_key)),
                    entity_ref=unit_key,
                    remediation="Restore the source-backed README and hierarchy metadata before converting this phase.",
                )
            )

    selected_files: dict[str, list[_ParsedFile]] = {}
    for unit_key in selected_keys:
        unit = units[unit_key]
        unit_root = _safe_path(_safe_path(root, str(manifest["destino_raiz"])), str(unit["pasta"]))
        parsed_files = _frontmatter_paths_match(root, unit_root, unit, manifest, diagnostics)
        selected_files[unit_key] = [
            parsed for relative, parsed in sorted(parsed_files.items()) if relative != "README.md"
        ]

    blocks: list[Any] = []
    relations: list[CurriculumRelation] = []
    shared_placements: list[SharedPlacement] = []
    projects: list[ProjectSpec] = []
    editorial_pendings: list[Any] = []
    source_item_quizzes: dict[tuple[str, str], QuizBlock] = {}
    source_item_practices: dict[tuple[str, str], PracticeBlock] = {}
    source_item_practice_refs: dict[tuple[str, str], list[str]] = {}
    source_item_steps: dict[tuple[str, str], str] = {}
    project_by_unit: dict[str, ProjectSpec] = {}
    step_entries: dict[str, list[tuple[_ParsedFile, str, str, int]]] = {}
    file_aliases: dict[tuple[str, str], str] = {}
    file_destinations: dict[str, list[str]] = {}
    pending_occurrences: dict[str, int] = {}

    for unit_key in selected_keys:
        unit_files = units[unit_key].get("arquivos", {})
        if not isinstance(unit_files, Mapping):
            continue
        unit_root = _safe_path(
            _safe_path(root, str(manifest["destino_raiz"])), str(units[unit_key]["pasta"])
        )
        for alias, spec in unit_files.items():
            if not isinstance(alias, str):
                continue
            for relative_path, _ in _manifest_file_paths(spec):
                file_aliases[(unit_key, _repo_path(_safe_path(unit_root, relative_path), root))] = (
                    alias
                )

    # Index practice identities from explicit source labels before block
    # conversion, so an earlier rubric file can safely refer to later paths.
    for unit_key in selected_keys:
        for parsed in selected_files.get(unit_key, []):
            if parsed.source_type != "practice":
                continue
            practice_source_ids = _source_item_ids(parsed.frontmatter)
            if len(practice_source_ids) != 1:
                continue
            practice_source_id = practice_source_ids[0]
            practice_ref = _item_entity_ref(parsed, practice_source_id, "practice")
            source_item_practice_refs.setdefault(
                (unit_key, _item_key(practice_source_id)), []
            ).append(practice_ref)

    def add_pending(
        parsed: _ParsedFile,
        entity_ref: str | None,
        reference_text: str,
        note: str,
        *,
        kind: str = "unresolved_reference",
        blocking: bool = False,
        destination_ref: str | None = None,
    ) -> str:
        identity = "\0".join(
            (
                parsed.file_id or parsed.path.stem,
                entity_ref or "",
                kind,
                reference_text,
                destination_ref or "",
            )
        )
        occurrence = pending_occurrences.get(identity, 0) + 1
        pending_occurrences[identity] = occurrence
        identity_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
        ref = (
            f"{id_prefix}-pending-"
            f"{_stable_token(parsed.file_id or parsed.path.stem)}-"
            f"{identity_hash}-{occurrence:02d}"
        )
        editorial_pendings.append(
            {
                "ref": ref,
                "kind": kind,
                "source_file": parsed.repo_path,
                "entity_ref": entity_ref,
                "reference_text": reference_text or parsed.file_id,
                "destination_ref": destination_ref,
                "blocking": blocking,
                "note": note,
                "provenance": _provenance(parsed, "editorial-reference", parsed.file_id),
            }
        )
        return ref

    def topics_for(unit_key: str, parsed: _ParsedFile) -> tuple[list[str], bool]:
        unit = units[unit_key]
        item_ids = _source_item_ids(parsed.frontmatter)
        covered = _coverage_subjects(unit, item_ids)
        explicit = parsed.frontmatter.get("assuntos")
        if isinstance(parsed.frontmatter.get("assunto"), str):
            explicit_subjects = [str(parsed.frontmatter["assunto"])]
        elif isinstance(explicit, list) and all(isinstance(item, str) for item in explicit):
            explicit_subjects = list(explicit)
        else:
            explicit_subjects = []
        if covered:
            if explicit_subjects and set(explicit_subjects) != set(covered):
                diagnostics.append(
                    _diag(
                        "COVERAGE_FRONTMATTER_MISMATCH",
                        "Manifest coverage and file assuntos/assunto disagree.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="assuntos",
                        reference=", ".join(covered),
                        remediation="Reconcile the approved coverage map and the migrated frontmatter before conversion.",
                    )
                )
            return covered, len(covered) > 1
        if explicit_subjects:
            if any(
                (unit_key, subject) not in topic_ref_by_key_slug for subject in explicit_subjects
            ):
                diagnostics.append(
                    _diag(
                        "SUBJECT_NOT_FOUND",
                        "File references a subject absent from the unit manifest.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="assunto/assuntos",
                        reference=", ".join(explicit_subjects),
                        remediation="Use only the approved subject slugs for this unit.",
                    )
                )
            return explicit_subjects, len(explicit_subjects) > 1
        relative = parsed.path.relative_to(
            _safe_path(_safe_path(root, str(manifest["destino_raiz"])), str(unit["pasta"]))
        ).as_posix()
        first = relative.split("/", 1)[0]
        if first != "90_integracao" and first in {
            slug for slug, _title in _unit_subject_specs(unit)
        }:
            return [first], False
        return [], False

    def add_shared_placements(
        parsed: _ParsedFile,
        block_ref: str,
        subject_slugs: Sequence[str],
        order: int,
        source_item: str | None = None,
    ) -> list[str]:
        """Place one canonical block into each declared subject context."""
        if len(subject_slugs) < 2:
            return []
        placement_refs: list[str] = []
        unit_key = str(parsed.frontmatter.get("parent_key", ""))
        for placement_index, slug in enumerate(subject_slugs, start=1):
            topic_ref = topic_ref_by_key_slug.get((unit_key, slug))
            if topic_ref is None:
                diagnostics.append(
                    _diag(
                        "SHARED_SUBJECT_NOT_FOUND",
                        "Shared content names a subject that has no topic node.",
                        source_file=parsed.repo_path,
                        entity_ref=block_ref,
                        reference=slug,
                        remediation="Reconcile the manifest coverage with the unit's approved subject list.",
                    )
                )
                continue
            place_ref = f"{block_ref}-placement-{_stable_token(slug)}"
            shared_placements.append(
                SharedPlacement(
                    ref=place_ref,
                    block_ref=block_ref,
                    subject_ref=topic_ref,
                    order=order + placement_index - 1,
                    progress_scope="undecided",
                    provenance=_provenance(
                        parsed, "shared-placement", source_item or parsed.file_id
                    ),
                )
            )
            placement_refs.append(place_ref)
        return placement_refs

    # Create project specs and formal delivery/milestone records before their
    # acceptance/checklist blocks so every relationship has a stable target.
    for unit_key in selected_keys:
        files = selected_files.get(unit_key, [])
        project_files = [
            item for item in files if item.source_type in {"project_scope", "project_brief"}
        ]
        if not project_files:
            continue
        project_unit = units[unit_key]
        unit_node = unit_node_by_key[unit_key]
        project_file = project_files[0]
        project_ref = f"{id_prefix}-project-{_stable_token(unit_key)}"
        raw_project_metadata: Any = project_unit.get("projeto", project_unit.get("project", {}))
        if not isinstance(raw_project_metadata, dict):
            raw_project_metadata = {}
        project_manifest: dict[str, Any] = dict(raw_project_metadata)
        for field_name in (
            "stack_mode",
            "escolha_do_aluno",
            "stack_opcoes",
            "stack_options",
            "stack_selecionada",
            "stack_selected",
        ):
            if field_name in project_unit and field_name not in project_manifest:
                project_manifest[field_name] = project_unit[field_name]
        project = ProjectSpec(
            ref=project_ref,
            unit_ref=unit_node.ref,
            title=unit_node.title,
            scope=project_file.body,
            has_formal_deliveries=False,
            deliveries=[],
            has_formal_milestones=False,
            milestones=[],
            variants=[],
            checklist_refs=[],
            rubric_refs=[],
            stack_options=[],
            stack_selected=None,
            source_metadata={
                "unit_frontmatter": _json_safe(unit_parsed_by_key[unit_key].frontmatter),
                "project_manifest": _json_safe(project_manifest),
            },
            provenance=_provenance(project_file, "project-scope", project_file.file_id),
        )
        project_by_unit[unit_key] = project
        projects.append(project)
        _add_mapping(
            mappings,
            project_file,
            [project_ref],
            ("project scope stored as ProjectSpec.scope verbatim",),
        )
        step_entries[unit_key] = []
        for parsed in files:
            if parsed.source_type not in {"milestone", "project_milestone"}:
                continue
            heading = _first_heading(parsed.body)
            title = _title(parsed)
            if title.startswith("Marco ") or (heading and heading.startswith("### Marco ")):
                step_kind = "milestone"
            elif title.startswith("Entrega ") or (heading and heading.startswith("### Entrega ")):
                step_kind = "delivery"
            else:
                diagnostics.append(
                    _diag(
                        "PROJECT_STEP_KIND_UNCLEAR",
                        "Project step title is not explicitly marked as Entrega or Marco.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="titulo_marco",
                        remediation="Keep the source step unconverted until the project authoring type is explicit.",
                    )
                )
                continue
            source_ids = _source_item_ids(parsed.frontmatter)
            source_item = source_ids[0] if source_ids else parsed.file_id
            step_ref = (
                f"{id_prefix}-{step_kind}-{_stable_token(unit_key)}-{_stable_token(source_item)}"
            )
            step_order = _base_order(parsed)
            prov = _provenance(parsed, f"project-{step_kind}", source_item)
            if step_kind == "delivery":
                delivery_step = ProjectDelivery(
                    ref=step_ref,
                    title=title,
                    body=parsed.body,
                    order=step_order,
                    acceptance_refs=[],
                    checklist_refs=[],
                    rubric_refs=[],
                    content_refs=[],
                    provenance=prov,
                )
                project.deliveries.append(delivery_step)
                step_ref_for_source = delivery_step.ref
            else:
                milestone_step = ProjectMilestone(
                    ref=step_ref,
                    title=title,
                    body=parsed.body,
                    order=step_order,
                    acceptance_refs=[],
                    checklist_refs=[],
                    rubric_refs=[],
                    content_refs=[],
                    provenance=prov,
                )
                project.milestones.append(milestone_step)
                step_ref_for_source = milestone_step.ref
            for source_id in source_ids or [source_item]:
                source_item_steps[(unit_key, _item_key(source_id))] = step_ref_for_source
            step_entries[unit_key].append((parsed, step_kind, step_ref, step_order))
            _add_mapping(
                mappings,
                parsed,
                [step_ref],
                ("literal source Markdown retained in ProjectDelivery/ProjectMilestone.body",),
            )
        project.has_formal_deliveries = bool(project.deliveries)
        project.has_formal_milestones = bool(project.milestones)
        for option_key in ("stack_options", "opcoes_stack", "stacks_permitidas", "stack_opcoes"):
            if option_key in project_manifest:
                project.stack_options = _string_list(project_manifest[option_key])
                break
        for selected_key in ("stack_selected", "stack_selecionada"):
            selected = project_manifest.get(selected_key)
            if isinstance(selected, str):
                project.stack_selected = selected
                break
        raw_variants = project_manifest.get("variantes")
        if isinstance(raw_variants, list):
            for variant_index, raw_variant in enumerate(raw_variants, start=1):
                if not isinstance(raw_variant, dict):
                    diagnostics.append(
                        _diag(
                            "PROJECT_VARIANT_UNSUPPORTED",
                            "Project variant entry is not a mapping.",
                            source_file=manifest_path,
                            entity_ref=project.ref,
                            reference=str(variant_index),
                            remediation="Add only explicitly source-backed variant fields to the supported manifest shape.",
                        )
                    )
                    continue
                raw_title = raw_variant.get("title", raw_variant.get("titulo"))
                description = raw_variant.get("description", raw_variant.get("descricao", ""))
                if not isinstance(raw_title, str) or not isinstance(description, str):
                    diagnostics.append(
                        _diag(
                            "PROJECT_VARIANT_UNSUPPORTED",
                            "Variant lacks literal title or description fields.",
                            source_file=manifest_path,
                            entity_ref=project.ref,
                            reference=json.dumps(_json_safe(raw_variant), ensure_ascii=False),
                            remediation="Map the exact variant data only after its manifest shape is explicit.",
                        )
                    )
                    continue
                project.variants.append(
                    ProjectVariant(
                        ref=f"{project.ref}-variant-{variant_index}",
                        title=raw_title,
                        order=variant_index,
                        description=description,
                        delivery_refs=[],
                        stack_option=raw_variant.get("stack_option", raw_variant.get("stack")),
                        provenance=project.provenance,
                    )
                )

    # Build indices for question/practice answer association.
    answer_files_by_item: dict[tuple[str, str], _ParsedFile] = {}
    for unit_key in selected_keys:
        for parsed in selected_files.get(unit_key, []):
            item_ids = _source_item_ids(parsed.frontmatter)
            for source_id in item_ids:
                item_key = (unit_key, _item_key(source_id))
                if parsed.source_type in {"answer_key", "answer_key_review"}:
                    answer_files_by_item[item_key] = parsed

    # Convert ordinary typed blocks. Unsupported source types produce explicit
    # blocking diagnostics instead of being coerced to theory.
    for unit_key in selected_keys:
        unit = units[unit_key]
        selected_unit_node = unit_node_by_key.get(unit_key)
        if selected_unit_node is None:
            continue
        selected_project = project_by_unit.get(unit_key)
        selected_project_ref = selected_project.ref if selected_project else None
        for parsed in selected_files.get(unit_key, []):
            kind = parsed.source_type
            if kind in {
                "topic_index",
                "milestone",
                "project_milestone",
                "project_scope",
                "project_brief",
                "conexoes",
            }:
                continue
            if not kind:
                diagnostics.append(
                    _diag(
                        "SOURCE_TYPE_MISSING",
                        "Markdown frontmatter has no tipo_arquivo.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="tipo_arquivo",
                        remediation="Set the approved source block type; do not infer it from the filename.",
                    )
                )
                continue
            if kind in {"answer_key", "answer_key_pratica", "answer_key_review"}:
                continue
            source_ids = _source_item_ids(parsed.frontmatter)
            subject_slugs, is_shared = topics_for(unit_key, parsed)
            if kind in {
                "objetivo",
                "resumo",
                "criterio",
                "theory",
                "quiz",
                "project_review_questions",
                "practice",
                "flashcard",
                "flashcards",
                "checklist",
                "acceptance_criteria",
                "project_decisions",
                "project_scenarios",
                "project_review",
                "rubric",
                "referencias",
                "project_index",
                "project_milestone",
                "milestone",
                "instructor_note",
            }:
                pass
            elif kind not in {"project_scope", "project_brief", "conexoes"}:
                diagnostics.append(
                    _diag(
                        "UNSUPPORTED_SOURCE_TYPE",
                        f"Source type {kind!r} has no explicit converter mapping.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="tipo_arquivo",
                        remediation="Add an approved semantic mapping to an existing 12A type or extend the contract in a separately approved task; never coerce to theory.",
                    )
                )
                continue
            if kind == "project_index":
                diagnostics.append(
                    _diag(
                        "UNSUPPORTED_SOURCE_TYPE",
                        "project_index is outside a unit and is not part of the selected topic conversion.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="tipo_arquivo",
                        remediation="Keep phase-level project indexes outside unit sample conversion or add a dedicated source-backed contract mapping.",
                    )
                )
                continue
            if (
                kind
                in {
                    "referencias",
                    "project_review",
                    "project_decisions",
                    "project_scenarios",
                    "checklist",
                    "acceptance_criteria",
                    "rubric",
                    "instructor_note",
                }
                and not parsed.body.strip()
            ):
                diagnostics.append(
                    _diag(
                        "SOURCE_BODY_EMPTY",
                        "Typed source block has an empty body.",
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        remediation="Restore the source body before conversion.",
                    )
                )
                continue

            owner_refs: list[str] = []
            rubric_target_refs: list[str] = []
            acceptance_target_ref: str | None = None
            acceptance_target_kind: str | None = None
            if (
                kind
                in {
                    "project_decisions",
                    "project_scenarios",
                    "project_review",
                    "project_review_questions",
                }
                and selected_project_ref
            ):
                owner_refs = [selected_project_ref]
            elif kind == "acceptance_criteria":
                acceptance_item_key = _item_key(source_ids[0]) if source_ids else ""
                acceptance_step_ref = source_item_steps.get((unit_key, acceptance_item_key))
                practice_refs = source_item_practice_refs.get((unit_key, acceptance_item_key), [])
                if acceptance_step_ref is not None and practice_refs:
                    diagnostics.append(
                        _diag(
                            "ACCEPTANCE_TARGET_AMBIGUOUS",
                            "Acceptance source label matches both a project step and a practice.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            reference=", ".join(source_ids),
                            remediation="Keep the source unchanged and resolve the target only when the source metadata identifies one entity kind.",
                        )
                    )
                    continue
                if acceptance_step_ref is not None:
                    acceptance_target_ref = acceptance_step_ref
                    acceptance_target_kind = next(
                        step_kind
                        for _source, step_kind, ref, _order in step_entries.get(unit_key, [])
                        if ref == acceptance_step_ref
                    )
                    owner_refs = [acceptance_step_ref]
                elif len(practice_refs) == 1:
                    acceptance_target_ref = practice_refs[0]
                    acceptance_target_kind = "practice"
                    owner_refs = [] if is_shared else [selected_unit_node.ref]
                elif len(practice_refs) > 1:
                    diagnostics.append(
                        _diag(
                            "ACCEPTANCE_TARGET_AMBIGUOUS",
                            "Acceptance source label matches multiple practices.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            reference=", ".join(source_ids),
                            remediation="Keep the source unchanged and require one explicit practice target.",
                        )
                    )
                    continue
                else:
                    diagnostics.append(
                        _diag(
                            "PROJECT_ACCEPTANCE_TARGET_MISSING",
                            "Acceptance criteria do not match a source-backed practice, project delivery, or milestone.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            reference=", ".join(source_ids),
                            remediation="Match the acceptance block to its exact source-backed practice, delivery, or milestone ID.",
                        )
                    )
                    continue
            elif kind == "rubric":
                rubric_item_keys = [_item_key(source_id) for source_id in source_ids]
                if len(rubric_item_keys) != len(set(rubric_item_keys)):
                    diagnostics.append(
                        _diag(
                            "RUBRIC_TARGET_DUPLICATE_SOURCE",
                            "Rubric source metadata repeats a target label.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            reference=", ".join(source_ids),
                            remediation="Correct the source-backed target list; do not deduplicate labels silently.",
                        )
                    )
                    continue
                project_level_rubric = selected_project_ref is not None and (
                    not source_ids
                    or (
                        len(rubric_item_keys) == 1
                        and file_aliases.get((unit_key, parsed.repo_path), "").upper()
                        in {"R00", "R01", "R02", "RUB"}
                        and not source_item_steps.get((unit_key, rubric_item_keys[0]))
                        and not source_item_practice_refs.get((unit_key, rubric_item_keys[0]))
                    )
                )
                target_errors: list[tuple[str, str]] = []
                if project_level_rubric and selected_project_ref is not None:
                    rubric_target_refs = [selected_project_ref]
                    owner_refs = [selected_project_ref]
                elif source_ids:
                    for source_id, rubric_item_key in zip(
                        source_ids, rubric_item_keys, strict=True
                    ):
                        lookup_key = (unit_key, rubric_item_key)
                        rubric_step_ref_candidate = source_item_steps.get(lookup_key)
                        practice_refs = source_item_practice_refs.get(lookup_key, [])
                        if rubric_step_ref_candidate is not None and practice_refs:
                            target_errors.append(
                                (source_id, "matches both a project step and a practice")
                            )
                        elif rubric_step_ref_candidate is not None:
                            rubric_target_refs.append(rubric_step_ref_candidate)
                        elif len(practice_refs) == 1:
                            rubric_target_refs.append(practice_refs[0])
                        elif len(practice_refs) > 1:
                            target_errors.append((source_id, "matches multiple practices"))
                        else:
                            target_errors.append(
                                (
                                    source_id,
                                    "does not resolve to a source-backed practice or project step",
                                )
                            )
                    if not target_errors and len(rubric_target_refs) != len(
                        set(rubric_target_refs)
                    ):
                        diagnostics.append(
                            _diag(
                                "RUBRIC_TARGET_DUPLICATE",
                                "Multiple source labels resolve to the same rubric target.",
                                source_file=parsed.repo_path,
                                entity_ref=parsed.file_id,
                                field="itens_origem",
                                reference=", ".join(source_ids),
                                remediation="Keep the source unchanged and resolve duplicate target identities explicitly.",
                            )
                        )
                        continue
                    if target_errors:
                        code = (
                            "RUBRIC_TARGET_AMBIGUOUS"
                            if any(
                                "multiple" in reason or "both" in reason
                                for _, reason in target_errors
                            )
                            else "RUBRIC_TARGET_NOT_FOUND"
                        )
                        diagnostics.append(
                            _diag(
                                code,
                                "Rubric target labels cannot all be resolved unambiguously: "
                                + "; ".join(
                                    f"{label}: {reason}" for label, reason in target_errors
                                ),
                                source_file=parsed.repo_path,
                                entity_ref=parsed.file_id,
                                field="itens_origem",
                                reference=", ".join(source_ids),
                                remediation="Keep the rubric source unchanged and map only targets explicitly identified by its source metadata.",
                            )
                        )
                        continue
                    step_targets = [
                        source_item_steps[(unit_key, rubric_item_key)]
                        for rubric_item_key in rubric_item_keys
                        if (unit_key, rubric_item_key) in source_item_steps
                    ]
                    if len(step_targets) == len(rubric_target_refs):
                        owner_refs = list(dict.fromkeys(step_targets))
                else:
                    diagnostics.append(
                        _diag(
                            "RUBRIC_TARGET_MISSING",
                            "Rubric has no explicit source target and is not a source-backed project-level rubric.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            remediation="Add a source-backed target association before conversion; do not infer one from proximity.",
                        )
                    )
                    continue
            elif subject_slugs:
                owner_refs = [
                    topic_ref_by_key_slug[(unit_key, slug)]
                    for slug in subject_slugs
                    if (unit_key, slug) in topic_ref_by_key_slug
                ]
            else:
                owner_refs = [selected_unit_node.ref]

            if kind in {"quiz", "project_review_questions"}:
                try:
                    question_segments = _split_quiz_items(parsed)
                except ValueError as error:
                    diagnostics.append(
                        _diag(
                            "QUIZ_BOUNDARY_UNSUPPORTED",
                            str(error),
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            remediation="Add an explicit parser for the literal source boundaries; do not infer question splits from generic prose or filenames.",
                        )
                    )
                    continue
                for item_index, (source_item, quiz_prompt) in enumerate(question_segments):
                    quiz_item_key = (unit_key, _item_key(source_item))
                    answer_file = answer_files_by_item.get(quiz_item_key)
                    answer_ref = (
                        _item_entity_ref(answer_file, source_item, "answer")
                        if answer_file
                        else None
                    )
                    shared = is_shared
                    owner_ref = (
                        None
                        if shared
                        else (owner_refs[0] if owner_refs else selected_unit_node.ref)
                    )
                    quiz = QuizBlock(
                        ref=_item_entity_ref(parsed, source_item, "question"),
                        type="quiz",
                        owner_ref=owner_ref,
                        order=_base_order(parsed) + item_index,
                        title=_title(parsed),
                        status=_unit_status(unit_parsed_by_key[unit_key]),
                        shared=shared,
                        provenance=_provenance(parsed, "quiz", source_item),
                        prompt=quiz_prompt,
                        format="other",
                        options=[],
                        answer_key_required=answer_file is not None,
                        answer_key_ref=answer_ref,
                    )
                    blocks.append(quiz)
                    source_item_quizzes[quiz_item_key] = quiz
                    file_destinations.setdefault(parsed.repo_path, []).append(quiz.ref)
                    if shared:
                        file_destinations[parsed.repo_path].extend(
                            add_shared_placements(
                                parsed, quiz.ref, subject_slugs, quiz.order, source_item
                            )
                        )
                _add_mapping(mappings, parsed, file_destinations[parsed.repo_path])
                continue

            if kind == "practice":
                if len(source_ids) != 1:
                    diagnostics.append(
                        _diag(
                            "PRACTICE_SOURCE_ITEM_AMBIGUOUS",
                            "A practice file must declare exactly one source item ID in this converter version.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            remediation="Split only at explicit source boundaries; do not infer activity boundaries.",
                        )
                    )
                    continue
                source_item = source_ids[0]
                item_key = (unit_key, _item_key(source_item))
                shared = is_shared
                owner_ref = (
                    None if shared else (owner_refs[0] if owner_refs else selected_unit_node.ref)
                )
                practice = PracticeBlock(
                    ref=parsed.file_id,
                    type="practice",
                    owner_ref=owner_ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=_unit_status(unit_parsed_by_key[unit_key]),
                    shared=shared,
                    provenance=_provenance(parsed, "practice", source_item),
                    prompt=parsed.body,
                    language=None,
                    starter_code=None,
                    acceptance=[],
                )
                blocks.append(practice)
                source_item_practices[item_key] = practice
                file_destinations.setdefault(parsed.repo_path, []).append(practice.ref)
                if shared:
                    file_destinations[parsed.repo_path].extend(
                        add_shared_placements(
                            parsed, practice.ref, subject_slugs, practice.order, source_item
                        )
                    )
                _add_mapping(mappings, parsed, file_destinations[parsed.repo_path])
                continue

            if kind in {"flashcard", "flashcards"}:
                try:
                    cards = _flashcards(parsed)
                except ValueError as error:
                    diagnostics.append(
                        _diag(
                            "FLASHCARD_FORMAT_UNSUPPORTED",
                            str(error),
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="body",
                            remediation="Add a literal flashcard parser for the exact source labels before including this format.",
                        )
                    )
                    continue
                mapping_refs: list[str] = []
                for card_index, (source_item, front, feedback_text, back) in enumerate(
                    cards, start=1
                ):
                    card_ref = (
                        parsed.file_id
                        if len(cards) == 1
                        else f"{parsed.file_id}-card-{_stable_token(source_item)}"
                    )
                    shared = is_shared
                    owner_ref = (
                        None
                        if shared
                        else (owner_refs[0] if owner_refs else selected_unit_node.ref)
                    )
                    card = FlashcardBlock(
                        ref=card_ref,
                        type="flashcard",
                        owner_ref=owner_ref,
                        order=_base_order(parsed) + card_index - 1,
                        title=_title(parsed),
                        status=_unit_status(unit_parsed_by_key[unit_key]),
                        shared=shared,
                        provenance=_provenance(parsed, "flashcard", source_item),
                        front=front,
                        back=back,
                        source_markdown=parsed.body,
                    )
                    blocks.append(card)
                    mapping_refs.append(card.ref)
                    if shared:
                        mapping_refs.extend(
                            add_shared_placements(
                                parsed,
                                card.ref,
                                subject_slugs,
                                card.order,
                                source_item,
                            )
                        )
                    if feedback_text:
                        feedback_ref = f"{card.ref}-feedback"
                        blocks.append(
                            FeedbackBlock(
                                ref=feedback_ref,
                                type="feedback",
                                owner_ref=owner_ref,
                                order=HIDDEN_FEEDBACK_ORDER + _base_order(parsed) + card_index,
                                title="Feedback do flashcard",
                                status=card.status,
                                shared=False,
                                provenance=_provenance(parsed, "flashcard-feedback", source_item),
                                target_ref=card.ref,
                                body=feedback_text,
                            )
                        )
                        mapping_refs.append(feedback_ref)
                _add_mapping(
                    mappings,
                    parsed,
                    mapping_refs,
                    (
                        "literal Pergunta/Resposta/Feedback labels converted to typed flashcard fields",
                    ),
                )
                continue

            block: ContentBlock
            if kind == "objetivo":
                block = ObjectiveBlock(
                    ref=parsed.file_id,
                    type="objective",
                    owner_ref=selected_unit_node.ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=False,
                    provenance=_provenance(parsed, "unit-objective", parsed.file_id),
                    body=parsed.body,
                )
            elif kind == "resumo":
                block = SummaryBlock(
                    ref=parsed.file_id,
                    type="summary",
                    owner_ref=selected_unit_node.ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=False,
                    provenance=_provenance(parsed, "unit-summary", parsed.file_id),
                    body=parsed.body,
                )
            elif kind == "criterio":
                block = CompletionCriteriaBlock(
                    ref=parsed.file_id,
                    type="completion_criteria",
                    owner_ref=selected_unit_node.ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=False,
                    provenance=_provenance(parsed, "unit-completion-criterion", parsed.file_id),
                    body=parsed.body,
                    source_item_labels=source_ids,
                    related_refs=[],
                )
            elif kind == "theory":
                microtopic = source_ids[0] if len(source_ids) == 1 else None
                block = TheoryBlock(
                    ref=parsed.file_id,
                    type="theory",
                    owner_ref=owner_refs[0] if owner_refs else selected_unit_node.ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=False,
                    provenance=_provenance(parsed, "theory", parsed.file_id),
                    body=parsed.body,
                    microtopic=microtopic,
                )
            elif kind in {"checklist", "project_decisions", "project_scenarios", "project_review"}:
                checklist_step_ref = (
                    source_item_steps.get((unit_key, _item_key(source_ids[0])))
                    if source_ids
                    else None
                )
                owner_ref = (
                    None
                    if is_shared
                    else checklist_step_ref
                    or (
                        selected_project_ref
                        if kind in {"project_decisions", "project_scenarios", "project_review"}
                        and selected_project_ref
                        else (owner_refs[0] if owner_refs else selected_unit_node.ref)
                    )
                )
                if kind == "checklist":
                    block = ChecklistBlock(
                        ref=parsed.file_id,
                        type="checklist",
                        owner_ref=owner_ref,
                        order=_base_order(parsed) + 50,
                        title=_title(parsed),
                        status=selected_unit_node.status,
                        shared=is_shared,
                        provenance=_provenance(parsed, "checklist", parsed.file_id),
                        items=_checklist_items(parsed.body, parsed.file_id),
                        source_markdown=parsed.body,
                        source_item_labels=source_ids,
                    )
                else:
                    if kind == "project_decisions":
                        block = ProjectDecisionBlock(
                            ref=parsed.file_id,
                            type="project_decision",
                            owner_ref=owner_ref,
                            order=_base_order(parsed) + 50,
                            title=_title(parsed),
                            status=selected_unit_node.status,
                            shared=is_shared,
                            provenance=_provenance(parsed, kind, parsed.file_id),
                            body=parsed.body,
                            source_item_labels=source_ids,
                            related_refs=[],
                        )
                    elif kind == "project_scenarios":
                        block = ProjectScenarioBlock(
                            ref=parsed.file_id,
                            type="project_scenario",
                            owner_ref=owner_ref,
                            order=_base_order(parsed) + 50,
                            title=_title(parsed),
                            status=selected_unit_node.status,
                            shared=is_shared,
                            provenance=_provenance(parsed, kind, parsed.file_id),
                            body=parsed.body,
                            source_item_labels=source_ids,
                            related_refs=[],
                        )
                    else:
                        block = ProjectReviewBlock(
                            ref=parsed.file_id,
                            type="project_review",
                            owner_ref=owner_ref,
                            order=_base_order(parsed) + 50,
                            title=_title(parsed),
                            status=selected_unit_node.status,
                            shared=is_shared,
                            provenance=_provenance(parsed, kind, parsed.file_id),
                            body=parsed.body,
                            source_item_labels=source_ids,
                            related_refs=[],
                        )
                if kind == "checklist" and selected_project:
                    if checklist_step_ref:
                        for project_step in _project_steps(selected_project):
                            if project_step.ref == checklist_step_ref:
                                project_step.checklist_refs.append(block.ref)
                    elif owner_ref == selected_project.ref:
                        selected_project.checklist_refs.append(block.ref)
            elif kind == "acceptance_criteria":
                if acceptance_target_ref is None or acceptance_target_kind is None:
                    diagnostics.append(
                        _diag(
                            "ACCEPTANCE_TARGET_MISSING",
                            "Acceptance target could not be resolved from source-backed items.",
                            source_file=parsed.repo_path,
                            entity_ref=parsed.file_id,
                            field="itens_origem",
                            reference=", ".join(source_ids),
                            remediation="Do not create acceptance criteria without one verified source target.",
                        )
                    )
                    continue
                items = [
                    ChecklistItem(ref=f"item-001-{_stable_token(parsed.file_id)}", text=parsed.body)
                ]
                block = AcceptanceCriteriaBlock(
                    ref=parsed.file_id,
                    type="acceptance_criteria",
                    owner_ref=(
                        None
                        if is_shared
                        else acceptance_target_ref
                        if acceptance_target_kind in {"delivery", "milestone"}
                        else selected_unit_node.ref
                    ),
                    order=_base_order(parsed) + 80,
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=is_shared,
                    provenance=_provenance(parsed, "project-acceptance", source_ids[0]),
                    delivery_ref=(
                        acceptance_target_ref if acceptance_target_kind == "delivery" else None
                    ),
                    milestone_ref=(
                        acceptance_target_ref if acceptance_target_kind == "milestone" else None
                    ),
                    practice_ref=(
                        acceptance_target_ref if acceptance_target_kind == "practice" else None
                    ),
                    items=items,
                    body=parsed.body,
                    source_item_labels=source_ids,
                )
                if selected_project:
                    for project_step in _project_steps(selected_project):
                        if project_step.ref == acceptance_target_ref:
                            project_step.acceptance_refs.append(block.ref)
            elif kind == "rubric":
                scale = _rubric_scale(parsed.body, parsed.frontmatter)
                dimensions, threshold, note = _rubric_dimensions(parsed.body, scale, parsed.file_id)
                if scale is not None:
                    score_scale = ScoreScale(minimum=scale[0], maximum=scale[1])
                else:
                    score_scale = None
                block = RubricBlock(
                    ref=parsed.file_id,
                    type="rubric",
                    owner_ref=(
                        None
                        if is_shared
                        else owner_refs[0]
                        if owner_refs
                        else (selected_project_ref or selected_unit_node.ref)
                    ),
                    order=_base_order(parsed) + 60,
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=is_shared,
                    provenance=_provenance(parsed, "rubric", parsed.file_id),
                    target_ref=rubric_target_refs[0],
                    target_refs=rubric_target_refs,
                    scale=score_scale,
                    dimensions=dimensions,
                    threshold=threshold,
                    source_markdown=parsed.body,
                    source_item_labels=_source_item_labels(parsed.frontmatter),
                )
                if selected_project:
                    for project_step in _project_steps(selected_project):
                        if project_step.ref in rubric_target_refs:
                            project_step.rubric_refs.append(block.ref)
                    if selected_project.ref in rubric_target_refs:
                        selected_project.rubric_refs.append(block.ref)
                if note:
                    note_ref = f"{block.ref}-note"
                    note_block = FeedbackBlock(
                        ref=note_ref,
                        type="feedback",
                        owner_ref=None if block.shared else block.owner_ref,
                        order=HIDDEN_FEEDBACK_ORDER + _base_order(parsed),
                        title="Observações da rubrica",
                        status=selected_unit_node.status,
                        shared=block.shared,
                        provenance=_provenance(parsed, "rubric-note", parsed.file_id),
                        target_ref=block.ref,
                        body=note,
                    )
                    blocks.append(note_block)
                    file_destinations.setdefault(parsed.repo_path, []).append(note_ref)
                    if block.shared:
                        file_destinations[parsed.repo_path].extend(
                            add_shared_placements(
                                parsed,
                                note_ref,
                                subject_slugs,
                                note_block.order,
                                parsed.file_id,
                            )
                        )
            elif kind == "referencias":
                reference_lines = [
                    line
                    for line in parsed.body.splitlines(keepends=True)
                    if line.strip() and not line.lstrip().startswith("#")
                ]
                if not reference_lines:
                    reference_lines = [parsed.body]
                for reference_index, raw_line in enumerate(reference_lines, start=1):
                    ref_id = (
                        parsed.file_id
                        if len(reference_lines) == 1
                        else f"{parsed.file_id}-ref-{reference_index:03d}"
                    )
                    label, url, target = _reference_line(raw_line)
                    if url:
                        ref_block = ReferenceBlock(
                            ref=ref_id,
                            type="reference",
                            owner_ref=selected_project_ref or selected_unit_node.ref,
                            order=_base_order(parsed) + reference_index,
                            title=label,
                            status=selected_unit_node.status,
                            shared=False,
                            provenance=_provenance(parsed, "reference", parsed.file_id),
                            target_kind="external",
                            label=label,
                            citation=raw_line,
                            url=url,
                            target_ref=None,
                            raw_text=raw_line,
                            pending_ref=None,
                        )
                        blocks.append(ref_block)
                        file_destinations.setdefault(parsed.repo_path, []).append(ref_id)
                    elif target and target.startswith("[[") is False and "[[" in raw_line:
                        pending_ref = add_pending(
                            parsed,
                            selected_unit_node.ref,
                            raw_line,
                            "Obsidian target retained literally; vault root is not confirmed.",
                            kind="obsidian_vault_root_unknown",
                        )
                        ref_block = ReferenceBlock(
                            ref=ref_id,
                            type="reference",
                            owner_ref=selected_project_ref or selected_unit_node.ref,
                            order=_base_order(parsed) + reference_index,
                            title=label,
                            status=selected_unit_node.status,
                            shared=False,
                            provenance=_provenance(parsed, "obsidian-reference", parsed.file_id),
                            target_kind="obsidian",
                            label=label,
                            citation=raw_line,
                            url=None,
                            target_ref=None,
                            raw_text=raw_line,
                            pending_ref=pending_ref,
                        )
                        blocks.append(ref_block)
                        file_destinations.setdefault(parsed.repo_path, []).append(ref_id)
                    else:
                        pending_ref = add_pending(
                            parsed,
                            selected_unit_node.ref,
                            raw_line,
                            "Reference retained literally; the intermediate contract has no general local-document entity.",
                            kind="unresolved_reference",
                        )
                        ref_block = ReferenceBlock(
                            ref=ref_id,
                            type="reference",
                            owner_ref=selected_project_ref or selected_unit_node.ref,
                            order=_base_order(parsed) + reference_index,
                            title=label,
                            status=selected_unit_node.status,
                            shared=False,
                            provenance=_provenance(parsed, "local-reference", parsed.file_id),
                            target_kind="editorial",
                            label=label,
                            citation=raw_line,
                            url=None,
                            target_ref=None,
                            raw_text=raw_line,
                            pending_ref=pending_ref,
                        )
                        blocks.append(ref_block)
                        file_destinations.setdefault(parsed.repo_path, []).append(ref_id)
                _add_mapping(
                    mappings,
                    parsed,
                    file_destinations.get(parsed.repo_path, []),
                    (
                        "reference lines retained in raw_text; typed URL/target is additional metadata",
                    ),
                )
                continue
            elif kind == "instructor_note":
                block = InstructorNoteBlock(
                    ref=parsed.file_id,
                    type="instructor_note",
                    owner_ref=owner_refs[0] if owner_refs else selected_unit_node.ref,
                    order=_base_order(parsed),
                    title=_title(parsed),
                    status=selected_unit_node.status,
                    shared=False,
                    provenance=_provenance(parsed, "instructor-note", parsed.file_id),
                    audience="instructor_only",
                    body=parsed.body,
                )
            else:
                # This branch is intentionally unreachable for explicit maps;
                # unknown values have already emitted a blocking diagnostic.
                continue

            blocks.append(block)
            file_destinations.setdefault(parsed.repo_path, []).append(block.ref)
            if is_shared:
                file_destinations[parsed.repo_path].extend(
                    add_shared_placements(
                        parsed,
                        block.ref,
                        subject_slugs,
                        block.order,
                        source_ids[0] if source_ids else parsed.file_id,
                    )
                )
            if isinstance(block, ChecklistBlock) and selected_project:
                if (
                    block.owner_ref == selected_project.ref
                    and block.ref not in selected_project.checklist_refs
                ):
                    selected_project.checklist_refs.append(block.ref)
            if isinstance(block, RubricBlock) and selected_project:
                rubric_targets = block.target_refs or [block.target_ref]
                if (
                    selected_project.ref in rubric_targets
                    and block.ref not in selected_project.rubric_refs
                ):
                    selected_project.rubric_refs.append(block.ref)
            normalizations: tuple[str, ...] = ()
            if kind == "rubric":
                normalizations = (
                    "typed rubric dimensions coexist with source_markdown so the literal source layout remains lossless",
                )
            elif kind == "checklist":
                normalizations = (
                    "checklist items retain parsed checked state and the exact source Markdown",
                )
            _add_mapping(mappings, parsed, file_destinations[parsed.repo_path], normalizations)

    # Answer keys and practice solutions are built only after canonical quiz and
    # practice blocks exist; source IDs must resolve one-to-one.
    for unit_key in selected_keys:
        for parsed in selected_files.get(unit_key, []):
            kind = parsed.source_type
            if kind not in {"answer_key", "answer_key_review", "answer_key_pratica"}:
                continue
            source_ids = _source_item_ids(parsed.frontmatter)
            try:
                answer_segments = _split_answer_items(parsed)
            except ValueError as error:
                diagnostics.append(
                    _diag(
                        "ANSWER_BOUNDARY_UNSUPPORTED",
                        str(error),
                        source_file=parsed.repo_path,
                        entity_ref=parsed.file_id,
                        field="itens_origem",
                        remediation="Add a parser for the source's literal answer separators; do not infer answer boundaries from generic prose.",
                    )
                )
                continue
            subject_slugs, _ = topics_for(unit_key, parsed)
            for item_index, (source_item, answer_body) in enumerate(answer_segments):
                item_key = (unit_key, _item_key(source_item))
                if kind in {"answer_key", "answer_key_review"}:
                    question = source_item_quizzes.get(item_key)
                    if question is None:
                        diagnostics.append(
                            _diag(
                                "ANSWER_QUESTION_NOT_SELECTED",
                                "Answer key has no converted question with the same source item ID.",
                                source_file=parsed.repo_path,
                                entity_ref=parsed.file_id,
                                field="itens_origem",
                                reference=source_item,
                                remediation="Select its original quiz in the same conversion sample or keep this key out of the sample.",
                            )
                        )
                        continue
                    expected, explanation, normalizations = _extract_answer(answer_body)
                    key_order = HIDDEN_ANSWER_ORDER + question.order
                    answer_key_ref = _item_entity_ref(parsed, source_item, "answer")
                    answer_key_block = AnswerKeyBlock(
                        ref=answer_key_ref,
                        type="answer_key",
                        owner_ref=(
                            question.owner_ref
                            if question.owner_ref is not None
                            else unit_node_by_key[unit_key].ref
                        ),
                        order=key_order,
                        title=_title(parsed),
                        status=question.status,
                        shared=False,
                        provenance=_provenance(parsed, "quiz-answer-key", source_item),
                        question_ref=question.ref,
                        correct_option_ref=None,
                        accepted_answers=[],
                        expected_answer=expected,
                        explanation=explanation,
                        source_markdown=answer_body,
                    )
                    blocks.append(answer_key_block)
                    file_destinations.setdefault(parsed.repo_path, []).append(answer_key_block.ref)
                    _add_mapping(mappings, parsed, [answer_key_block.ref], normalizations)
                else:
                    source_practice = source_item_practices.get(item_key)
                    if source_practice is None:
                        diagnostics.append(
                            _diag(
                                "SOLUTION_PRACTICE_NOT_SELECTED",
                                "Practice solution has no converted practice with the same source item ID.",
                                source_file=parsed.repo_path,
                                entity_ref=parsed.file_id,
                                field="itens_origem",
                                reference=source_item,
                                remediation="Select its original practice in the same conversion sample or keep this solution out of the sample.",
                            )
                        )
                        continue
                    solution = SolutionBlock(
                        ref=_item_entity_ref(parsed, source_item, "solution"),
                        type="solution",
                        owner_ref=(
                            source_practice.owner_ref
                            if source_practice.owner_ref is not None
                            else unit_node_by_key[unit_key].ref
                        ),
                        order=HIDDEN_SOLUTION_ORDER + source_practice.order + item_index,
                        title=_title(parsed),
                        status=source_practice.status,
                        shared=False,
                        provenance=_provenance(parsed, "practice-solution", source_item),
                        practice_ref=source_practice.ref,
                        body=answer_body,
                        reveal_policy="not_decided",
                    )
                    blocks.append(solution)
                    file_destinations.setdefault(parsed.repo_path, []).append(solution.ref)
                    _add_mapping(mappings, parsed, [solution.ref])

    # Map connection bullets using the explicit manifest relationship entries.
    for unit_key in selected_keys:
        unit = units[unit_key]
        relation_unit_node = unit_node_by_key.get(unit_key)
        if relation_unit_node is None:
            continue
        for parsed in selected_files.get(unit_key, []):
            if parsed.source_type != "conexoes":
                continue
            bullet_lines = [
                line for line in parsed.body.splitlines() if line.lstrip().startswith(("- ", "* "))
            ]
            relation_entries = _source_relations(unit)
            mapped_refs: list[str] = []
            for relation_index, entry in enumerate(relation_entries, start=1):
                target_key = _relation_target(entry)
                if not target_key:
                    continue
                literal_line = _relation_line(bullet_lines, target_key)
                if literal_line is None:
                    continue
                target_node = unit_node_by_key.get(target_key)
                if target_node is None:
                    pending_ref = add_pending(
                        parsed,
                        relation_unit_node.ref,
                        literal_line,
                        "Cross-phase curriculum relation is retained literally; the target node is outside this phase-scoped contract.",
                        kind="unresolved_reference",
                    )
                    mapped_refs.append(pending_ref)
                    continue
                relation_type, enforced = _relation_kind(entry.get("tipo", entry.get("kind")))
                relation_ref = (
                    f"{id_prefix}-relation-{_stable_token(unit_key)}-{relation_index:03d}"
                )
                relations.append(
                    CurriculumRelation(
                        ref=relation_ref,
                        source_ref=relation_unit_node.ref,
                        target_ref=target_node.ref,
                        kind=relation_type,
                        enforced=enforced,
                        note=literal_line,
                        provenance=_provenance(parsed, "curriculum-relation", parsed.file_id),
                    )
                )
                mapped_refs.append(relation_ref)
                if "[[" in literal_line:
                    pending_ref = add_pending(
                        parsed,
                        relation_ref,
                        literal_line,
                        "Wikilink preserved; its resolution depends on the unconfirmed Obsidian vault root.",
                        kind="obsidian_vault_root_unknown",
                        destination_ref=target_node.ref,
                    )
                    mapped_refs.append(pending_ref)
            for line in bullet_lines:
                represented_as_relation = any(
                    relation.provenance.source_file == parsed.repo_path and relation.note == line
                    for relation in relations
                )
                represented_as_pending = any(
                    item.get("source_file") == parsed.repo_path
                    and item.get("reference_text") == line
                    for item in editorial_pendings
                )
                if not represented_as_relation and not represented_as_pending:
                    pending_ref = add_pending(
                        parsed,
                        relation_unit_node.ref,
                        line,
                        "Connection line has no unambiguous target entry in this phase manifest; retained literally.",
                        kind="unresolved_reference",
                    )
                    mapped_refs.append(pending_ref)
                elif represented_as_pending:
                    pending_item = next(
                        item
                        for item in editorial_pendings
                        if item.get("source_file") == parsed.repo_path
                        and item.get("reference_text") == line
                    )
                    pending_ref = pending_item.get("ref")
                    if isinstance(pending_ref, str):
                        mapped_refs.append(pending_ref)

            # Preserve connection paragraphs that are written as prose rather
            # than list items. Keep the exact text as an editorial pending and
            # do not infer relation targets from mentioned unit IDs.
            prose_lines: list[str] = []

            def flush_connection_prose() -> None:
                if not prose_lines:
                    return
                literal_prose = "".join(prose_lines)
                mapped_refs.append(
                    add_pending(
                        parsed,
                        relation_unit_node.ref,
                        literal_prose,
                        "Literal connection prose retained; no structured relation inferred.",
                        kind="unresolved_reference",
                    )
                )
                prose_lines.clear()

            for raw_line in parsed.body.splitlines(keepends=True):
                stripped = raw_line.lstrip()
                is_heading = stripped.startswith("#")
                is_bullet = stripped.startswith(("- ", "* "))
                if not raw_line.strip() or is_heading or is_bullet:
                    flush_connection_prose()
                else:
                    prose_lines.append(raw_line)
            flush_connection_prose()
            _add_mapping(
                mappings,
                parsed,
                mapped_refs,
                (
                    "literal connection bullets represented as curriculum relations or pending references",
                ),
            )

    # Add project-level lists/checklists to their ProjectSpec references after
    # the block pass, preserving only the original list items.
    for project in projects:
        project.checklist_refs = list(dict.fromkeys(project.checklist_refs))
        project.rubric_refs = list(dict.fromkeys(project.rubric_refs))

    # Any literal obsolete/unresolved references are retained as nonblocking
    # editorial records; no target is fabricated.
    all_unit_keys = set(units)
    for unit_key in selected_keys:
        pending_unit_node = unit_node_by_key.get(unit_key)
        if pending_unit_node is None:
            continue
        for parsed in selected_files.get(unit_key, []):
            if "47.2" in parsed.body or "47.3" in parsed.body:
                for missing in ("47.2", "47.3"):
                    if missing in parsed.body and missing not in all_unit_keys:
                        add_pending(
                            parsed,
                            pending_unit_node.ref,
                            missing,
                            "Literal editorial reference retained; no active unit with this ID exists in the current manifest.",
                            kind="unresolved_reference",
                        )

    # Source provenance is checked against exact file bytes as read.
    parsed_by_path: dict[str, _ParsedFile] = {}
    for unit_key in selected_keys:
        for parsed in selected_files.get(unit_key, []):
            parsed_by_path[parsed.repo_path] = parsed
    parsed_by_path[_repo_path(phase_page, root)] = _read_frontmatter(phase_page, root)
    for path in parsed_by_path.values():
        diagnostics.extend(
            verify_source_hash(
                _provenance(path, "converter-source-check", path.file_id or None),
                path.raw,
                entity_ref=path.file_id or None,
            )
        )

    # Explicit vault-root pending record is required while the
    # root remains unconfirmed, even if selected content has no wikilinks.
    phase_page_parsed = parsed_by_path[_repo_path(phase_page, root)]
    editorial_pendings.append(
        {
            "ref": f"{id_prefix}-pending-obsidian-root",
            "kind": "obsidian_vault_root_unknown",
            "source_file": phase_page_parsed.repo_path,
            "entity_ref": phase_ref,
            "reference_text": "Obsidian vault root",
            "destination_ref": None,
            "blocking": False,
            "note": "Vault root is not confirmed; wikilinks remain literal.",
            "provenance": _provenance(
                phase_page_parsed, "vault-root-pending", phase_page_parsed.file_id or None
            ),
        }
    )

    try:
        source_manifest = SourceManifest(
            manifest_path=manifest_file.relative_to(root).as_posix(),
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
            source_revision=source_revision,
            converter_version=converter_version,
        )
        built_contract = IntermediateContract(
            schema_version=CONTRACT_VERSION,
            source=source_manifest,
            nodes=nodes,
            blocks=blocks,
            relations=relations,
            shared_placements=shared_placements,
            projects=projects,
            editorial_pendings=editorial_pendings,
            vault_root_confirmed=False,
        )
        validation = validate_contract(built_contract)
        diagnostics.extend(validation.diagnostics)
        contract: IntermediateContract | None = (
            built_contract if validation.contract is not None else None
        )
    except (ValidationError, ValueError, TypeError) as error:
        contract = None
        diagnostics.append(
            _diag(
                "CONTRACT_BUILD_FAILED",
                str(error),
                source_file=manifest_path,
                remediation="Correct the source mapping or contract field explicitly; no output was serialized.",
            )
        )

    # De-duplicate mappings while preserving first-source order.
    mapping_by_file: dict[str, SourceMapping] = {}
    for item in mappings:
        previous = mapping_by_file.get(item.source_file)
        if previous is None:
            mapping_by_file[item.source_file] = item
        else:
            mapping_by_file[item.source_file] = SourceMapping(
                source_file=item.source_file,
                source_id=item.source_id,
                source_type=item.source_type,
                source_sha256=item.source_sha256,
                destination_refs=tuple(
                    dict.fromkeys((*previous.destination_refs, *item.destination_refs))
                ),
                normalizations=tuple(
                    dict.fromkeys((*previous.normalizations, *item.normalizations))
                ),
            )
    return ConversionResult(
        contract=contract,
        diagnostics=tuple(
            sorted(
                diagnostics,
                key=lambda item: (
                    item.source_file or "",
                    item.code,
                    item.entity_ref or "",
                    item.field or "",
                    item.reference or "",
                    item.message,
                ),
            )
        ),
        mappings=tuple(mapping_by_file[path] for path in sorted(mapping_by_file)),
        converted_unit_keys=selected_keys,
    )


def convert_manifest_samples(
    repo_root: Path,
    manifest_path: str,
    unit_keys: Sequence[str],
    *,
    source_revision: str,
    converter_version: str = CONVERTER_VERSION,
) -> ConversionResult:
    """Convert selected units, returning structured diagnostics for bad input."""
    selected_keys = tuple(dict.fromkeys(unit_keys))
    try:
        return _convert_manifest_samples_impl(
            repo_root,
            manifest_path,
            selected_keys,
            source_revision=source_revision,
            converter_version=converter_version,
        )
    except (
        OSError,
        UnicodeDecodeError,
        ValueError,
        yaml.YAMLError,
        ValidationError,
        TypeError,
        KeyError,
        IndexError,
    ) as error:
        diagnostic = _diag(
            "CONVERSION_ABORTED",
            str(error),
            source_file=manifest_path,
            remediation="Correct the source or manifest structure and rerun conversion; no partial contract is returned.",
        )
        return ConversionResult(None, (diagnostic,), (), selected_keys)
