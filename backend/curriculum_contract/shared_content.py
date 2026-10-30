"""Offline, read-only projection of canonical shared blocks and topic placements.

This module adapts the existing intermediate contract for inspection and safe
presentation. It performs no filesystem, database, API, publication, or progress
writes. Canonical payloads are stored once in each internal projection; placement
records retain references and contextual metadata only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .models import (
    ContentBlock,
    CurriculumNode,
    FlashcardBlock,
    IntermediateContract,
    PracticeBlock,
    QuizBlock,
    SharedPlacement,
    student_quiz_view,
)
from .validation import Diagnostic, DiagnosticSeverity, validate_contract


class SharedContentValidationError(ValueError):
    """A contract validation failure with diagnostics that omit content text."""

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        self.diagnostics = diagnostics
        codes = sorted({diagnostic.code for diagnostic in diagnostics})
        super().__init__("Shared-content contract is invalid: " + ", ".join(codes))


class SharedContentReferenceError(ValueError):
    """A missing or structurally invalid subject reference."""

    def __init__(self, code: str, reference: str) -> None:
        self.code = code
        self.reference = reference
        super().__init__(f"{code}: {reference}")


class PublicProjectionPolicyError(ValueError):
    """A shared type has no explicitly approved public projection policy."""

    def __init__(self, code: str, block_ref: str) -> None:
        self.code = code
        self.block_ref = block_ref
        super().__init__(f"{code}: {block_ref}")


def _freeze_json(value: Any) -> Any:
    """Return a recursively immutable JSON-shaped value."""
    if isinstance(value, dict):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError("Contract projection contains a non-JSON value")


def _thaw_json(value: Any) -> Any:
    """Return ordinary JSON containers from an immutable projection snapshot."""
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class SharedSubjectProjection:
    """Immutable in-memory snapshot for one existing topic and its placements."""

    schema_version: str
    subject_ref: str
    source_manifest: Mapping[str, Any]
    subject: Mapping[str, Any]
    placements: tuple[Mapping[str, Any], ...]
    canonical_blocks: Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True)
class PublicPlacementProjection:
    """Allowlisted presentation data; withheld types contain no block payload."""

    placement_ref: str
    block_ref: str
    subject_ref: str
    order: int
    block_type: str
    content: Mapping[str, Any] | None


@dataclass(frozen=True)
class PublicSubjectProjection:
    subject_ref: str
    placements: tuple[PublicPlacementProjection, ...]


@dataclass(frozen=True)
class SharedContentIndex:
    """Read-only lookup over validated contract entities."""

    _schema_version: str
    _source_manifest: Mapping[str, Any]
    _nodes: Mapping[str, CurriculumNode]
    _shared_blocks: Mapping[str, ContentBlock]
    _placements_by_subject: Mapping[str, tuple[SharedPlacement, ...]]

    @property
    def shared_block_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._shared_blocks))

    @property
    def subject_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._placements_by_subject))

    @property
    def placement_count(self) -> int:
        return sum(len(items) for items in self._placements_by_subject.values())

    def for_subject(self, subject_ref: str) -> SharedSubjectProjection:
        subject = self._nodes.get(subject_ref)
        if subject is None:
            raise SharedContentReferenceError("SHARED_SUBJECT_NOT_FOUND", subject_ref)
        if subject.kind != "topic":
            raise SharedContentReferenceError("SHARED_SUBJECT_NOT_TOPIC", subject_ref)

        placements = self._placements_by_subject.get(subject_ref, ())
        block_refs = sorted({placement.block_ref for placement in placements})
        canonical_blocks = {
            block_ref: _freeze_json(self._shared_blocks[block_ref].model_dump(mode="json"))
            for block_ref in block_refs
        }
        return SharedSubjectProjection(
            schema_version=self._schema_version,
            subject_ref=subject_ref,
            source_manifest=self._source_manifest,
            subject=_freeze_json(subject.model_dump(mode="json")),
            placements=tuple(
                _freeze_json(placement.model_dump(mode="json")) for placement in placements
            ),
            canonical_blocks=MappingProxyType(canonical_blocks),
        )


def build_shared_content_index(contract: IntermediateContract) -> SharedContentIndex:
    """Validate and index the existing intermediate model without mutating it."""
    report = validate_contract(contract)
    errors = tuple(
        diagnostic
        for diagnostic in report.diagnostics
        if diagnostic.severity == DiagnosticSeverity.ERROR
    )
    if errors:
        raise SharedContentValidationError(errors)

    nodes = {node.ref: node for node in contract.nodes}
    shared_blocks = {block.ref: block for block in contract.blocks if block.shared}
    placements_by_subject: dict[str, list[SharedPlacement]] = {}
    for placement in contract.shared_placements:
        placements_by_subject.setdefault(placement.subject_ref, []).append(placement)

    ordered_placements = {
        subject_ref: tuple(sorted(items, key=lambda item: (item.order, item.ref)))
        for subject_ref, items in placements_by_subject.items()
    }
    return SharedContentIndex(
        _schema_version=contract.schema_version,
        _source_manifest=_freeze_json(contract.source.model_dump(mode="json")),
        _nodes=MappingProxyType(nodes),
        _shared_blocks=MappingProxyType(shared_blocks),
        _placements_by_subject=MappingProxyType(ordered_placements),
    )


def internal_projection_payload(projection: SharedSubjectProjection) -> dict[str, Any]:
    """Return a full-fidelity internal payload with canonical content stored once.

    This payload includes source provenance and complete typed block data. It is
    not a student/public response and must not be logged or exposed by an API.
    """
    return {
        "schema_version": projection.schema_version,
        "source_manifest": _thaw_json(projection.source_manifest),
        "subject": _thaw_json(projection.subject),
        "canonical_blocks": [
            _thaw_json(projection.canonical_blocks[block_ref])
            for block_ref in sorted(projection.canonical_blocks)
        ],
        "placements": [_thaw_json(placement) for placement in projection.placements],
    }


def serialize_internal_projection(projection: SharedSubjectProjection) -> str:
    """Serialize an internal projection deterministically; never use as public output."""
    return json.dumps(
        internal_projection_payload(projection),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def public_projection_for_subject(
    index: SharedContentIndex, subject_ref: str
) -> PublicSubjectProjection:
    """Build a fail-closed, field-allowlisted presentation projection."""
    return public_projection_from_snapshot(index.for_subject(subject_ref))


def public_projection_from_snapshot(
    internal: SharedSubjectProjection,
) -> PublicSubjectProjection:
    """Project an internal snapshot using an explicit type-and-field allowlist.

    Quiz answers, practice acceptance criteria, flashcard backs, rubrics,
    feedback, checklists, and acceptance criteria are not exposed here.
    """
    entries: list[PublicPlacementProjection] = []
    for placement in internal.placements:
        placement_ref = str(placement["ref"])
        block_ref = str(placement["block_ref"])
        block_record = internal.canonical_blocks.get(block_ref)
        if block_record is None:
            raise SharedContentReferenceError("SHARED_BLOCK_NOT_FOUND", block_ref)
        block_type = str(block_record.get("type", ""))

        content: dict[str, Any] | None
        if block_type == "quiz":
            quiz_block = QuizBlock.model_validate(_thaw_json(block_record))
            presentation = student_quiz_view(quiz_block).model_dump(mode="json")
            content = {
                field: presentation[field] for field in ("title", "prompt", "format", "options")
            }
        elif block_type == "practice":
            practice_block = PracticeBlock.model_validate(_thaw_json(block_record))
            content = {
                "prompt": practice_block.prompt,
                "language": practice_block.language,
                "starter_code": practice_block.starter_code,
            }
        elif block_type == "flashcard":
            flashcard_block = FlashcardBlock.model_validate(_thaw_json(block_record))
            content = {"front": flashcard_block.front}
        elif block_type in {
            "rubric",
            "feedback",
            "checklist",
            "acceptance_criteria",
        }:
            content = None
        else:
            raise PublicProjectionPolicyError("PUBLIC_TYPE_POLICY_UNDEFINED", block_ref)

        entries.append(
            PublicPlacementProjection(
                placement_ref=placement_ref,
                block_ref=block_ref,
                subject_ref=internal.subject_ref,
                order=int(placement["order"]),
                block_type=block_type,
                content=_freeze_json(content) if content is not None else None,
            )
        )
    return PublicSubjectProjection(
        subject_ref=internal.subject_ref,
        placements=tuple(entries),
    )


def public_projection_payload(projection: PublicSubjectProjection) -> dict[str, Any]:
    """Return only fields explicitly approved by the offline presentation policy."""
    return {
        "subject_ref": projection.subject_ref,
        "placements": [
            {
                "placement_ref": item.placement_ref,
                "block_ref": item.block_ref,
                "subject_ref": item.subject_ref,
                "order": item.order,
                "block_type": item.block_type,
                "content": _thaw_json(item.content) if item.content is not None else None,
            }
            for item in projection.placements
        ],
    }


def serialize_public_projection(projection: PublicSubjectProjection) -> str:
    return json.dumps(
        public_projection_payload(projection),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
