"""Offline reader, validator, and deterministic planner for import bundles.

This module deliberately has no database, network, migration, or production
importer dependency. It validates a versioned package and describes a possible
future application plan; it never executes that plan.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from pydantic import ValidationError

from .bulk_import import (
    BULK_IMPORT_SCHEMA,
    CurriculumImportBundle,
    canonical_import_bundle_json,
)
from .models import (
    AnswerKeyBlock,
    CurriculumNode,
    QuizBlock,
    ReferenceBlock,
    canonical_json,
)
from .validation import Diagnostic, DiagnosticSeverity, validate_contract

PLAN_SCHEMA_VERSION = "trilhacode.import_adapter.dry_run/1.0"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PHASE_NAME_RE = re.compile(r"^Fase_(?:[1-9]|10)$")
MIGRATED_ROOT = "docs/courses/trilhacode/Conteudos_migrado"
EXPECTED_BLOCK_TYPES = {
    "acceptance_criteria",
    "answer_key",
    "checklist",
    "completion_criteria",
    "feedback",
    "flashcard",
    "instructor_note",
    "objective",
    "practice",
    "project_decision",
    "project_review",
    "project_scenario",
    "quiz",
    "reference",
    "rubric",
    "solution",
    "summary",
    "theory",
}


class OperationState(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    CONFLICT = "conflict"
    BLOCKED = "blocked"
    PENDING_DECISION = "pending_decision"
    PENDING_DATABASE_SNAPSHOT = "pending_database_snapshot"


class AdapterValidationError(ValueError):
    """A package error with stable, machine-readable diagnostics."""

    def __init__(self, diagnostics: Iterable[Diagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        summary = "; ".join(f"{item.code}: {item.message}" for item in self.diagnostics)
        super().__init__(summary or "Import bundle validation failed")

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "diagnostics": [item.model_dump(mode="json") for item in self.diagnostics],
        }


@dataclass(frozen=True, slots=True)
class ExistingEntitySnapshot:
    """Caller-supplied read-only state; this adapter never fetches it itself."""

    curriculum_ref: str
    current_sha256: str
    last_imported_sha256: str | None


@dataclass(frozen=True, slots=True)
class PlannedOperation:
    entity_ref: str
    entity_type: str
    phase: int
    operation: OperationState
    target: str | None
    candidate_action: str | None
    reason_code: str
    dependencies: tuple[str, ...] = ()
    source_file: str | None = None
    private: bool = False
    content_sha256: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "entity_ref": self.entity_ref,
            "entity_type": self.entity_type,
            "phase": self.phase,
            "operation": self.operation.value,
            "target": self.target,
            "candidate_action": self.candidate_action,
            "reason_code": self.reason_code,
            "dependencies": list(self.dependencies),
            "source_file": self.source_file,
            "private": self.private,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, slots=True)
class ValidatedPackage:
    bundle: CurriculumImportBundle
    bundle_sha256: str
    path: Path | None
    repository_checks: dict[str, Any]


def _diagnostic(
    code: str,
    message: str,
    *,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    source_file: str | None = None,
    entity_ref: str | None = None,
    field: str | None = None,
    reference: str | None = None,
    remediation: str = "Correct the package or resolve the documented compatibility decision.",
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


class _DuplicateJsonKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_bundle_bytes(raw: bytes) -> CurriculumImportBundle:
    """Parse a strict UTF-8 bundle, rejecting duplicate JSON keys and versions."""
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise AdapterValidationError(
            [_diagnostic("INVALID_UTF8", f"Bundle is not valid UTF-8: {exc}")]
        ) from exc
    try:
        payload = json.loads(text, object_pairs_hook=_unique_object)
    except _DuplicateJsonKey as exc:
        raise AdapterValidationError([_diagnostic("DUPLICATE_JSON_KEY", str(exc))]) from exc
    except json.JSONDecodeError as exc:
        raise AdapterValidationError(
            [_diagnostic("JSON_INVALID", f"Invalid JSON at line {exc.lineno}, column {exc.colno}.")]
        ) from exc
    if not isinstance(payload, dict):
        raise AdapterValidationError(
            [_diagnostic("BUNDLE_ROOT_INVALID", "The JSON root must be an object.")]
        )
    version = payload.get("schema_version")
    if version != BULK_IMPORT_SCHEMA:
        raise AdapterValidationError(
            [
                _diagnostic(
                    "UNKNOWN_BUNDLE_VERSION",
                    f"Unsupported import bundle version: {version!r}.",
                    field="schema_version",
                    remediation=f"Use the supported schema version {BULK_IMPORT_SCHEMA!r}.",
                )
            ]
        )
    try:
        return CurriculumImportBundle.model_validate(payload)
    except ValidationError as exc:
        diagnostics: list[Diagnostic] = []
        for issue in exc.errors(include_url=False):
            location = tuple(issue.get("loc", ()))
            code = (
                "UNKNOWN_BLOCK_TYPE"
                if "union_tag" in str(issue.get("type", ""))
                else "BUNDLE_SCHEMA_INVALID"
            )
            diagnostics.append(
                _diagnostic(
                    code,
                    str(issue.get("msg", "Invalid bundle schema.")),
                    field=".".join(str(part) for part in location) or None,
                    remediation="Repair the field according to trilhacode.import_bundle/1.0; unknown content types require an explicit adapter mapping.",
                )
            )
        raise AdapterValidationError(diagnostics) from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_repo_path(root: Path, raw_path: str) -> Path:
    if (
        not raw_path
        or "\\" in raw_path
        or PurePosixPath(raw_path).is_absolute()
        or any(part in {"", ".", ".."} for part in raw_path.split("/"))
        or (len(raw_path) > 1 and raw_path[1] == ":")
    ):
        raise ValueError(f"unsafe repository-relative path: {raw_path!r}")
    resolved_root = root.resolve()
    resolved_path = (resolved_root / Path(*PurePosixPath(raw_path).parts)).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {raw_path!r}") from exc
    return resolved_path


def _iter_contract_entities(
    bundle: CurriculumImportBundle,
) -> list[tuple[int, str, str, Any, tuple[str, ...]]]:
    entities: list[tuple[int, str, str, Any, tuple[str, ...]]] = []
    for phase in bundle.phases:
        contract = phase.contract
        for node in contract.nodes:
            dependencies = (node.parent_ref,) if node.parent_ref else ()
            entities.append((phase.phase, "node", node.ref, node, dependencies))
        for block in contract.blocks:
            block_dependencies: tuple[str, ...] = tuple(
                ref
                for ref in (
                    block.owner_ref,
                    getattr(block, "answer_key_ref", None),
                    getattr(block, "question_ref", None),
                    getattr(block, "practice_ref", None),
                    getattr(block, "target_ref", None),
                )
                if ref
            )
            entities.append((phase.phase, "block", block.ref, block, block_dependencies))
        for relation in contract.relations:
            entities.append(
                (
                    phase.phase,
                    "relation",
                    relation.ref,
                    relation,
                    (relation.source_ref, relation.target_ref),
                )
            )
        for placement in contract.shared_placements:
            entities.append(
                (
                    phase.phase,
                    "shared_placement",
                    placement.ref,
                    placement,
                    (placement.block_ref, placement.subject_ref),
                )
            )
        for project in contract.projects:
            entities.append((phase.phase, "project", project.ref, project, (project.unit_ref,)))
            for delivery in project.deliveries:
                deps = (
                    project.ref,
                    *delivery.acceptance_refs,
                    *delivery.checklist_refs,
                    *delivery.rubric_refs,
                    *delivery.content_refs,
                )
                entities.append((phase.phase, "project_delivery", delivery.ref, delivery, deps))
            for milestone in project.milestones:
                deps = (
                    project.ref,
                    *milestone.acceptance_refs,
                    *milestone.checklist_refs,
                    *milestone.rubric_refs,
                    *milestone.content_refs,
                )
                entities.append((phase.phase, "project_milestone", milestone.ref, milestone, deps))
            for variant in project.variants:
                entities.append(
                    (
                        phase.phase,
                        "project_variant",
                        variant.ref,
                        variant,
                        (project.ref, *variant.delivery_refs),
                    )
                )
        for pending in contract.editorial_pendings:
            pending_dependencies: tuple[str, ...] = tuple(
                ref for ref in (pending.entity_ref, pending.destination_ref) if ref
            )
            entities.append(
                (phase.phase, "editorial_pending", pending.ref, pending, pending_dependencies)
            )
    return entities


def _canonical_entity_hash(entity: Any) -> str:
    payload = entity.model_dump(mode="json")
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256(canonical.encode("utf-8"))


def _compare_integrity_counts(bundle: CurriculumImportBundle) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    declared = bundle.integrity.get("global_counts")
    if not isinstance(declared, dict):
        return [
            _diagnostic("INTEGRITY_COUNTS_MISSING", "integrity.global_counts must be an object.")
        ]

    contracts = [phase.contract for phase in bundle.phases]
    entities = _iter_contract_entities(bundle)
    block_counts = Counter(block.type for contract in contracts for block in contract.blocks)
    diagnostic_counts = Counter(
        item.get("severity")
        for item in bundle.diagnostics.get("diagnostics", [])
        if isinstance(item, dict)
    )
    calculated: dict[str, Any] = {
        "phases": len(bundle.phases),
        "active_units": sum(
            node.kind == "submodule" for contract in contracts for node in contract.nodes
        ),
        "nodes": sum(len(contract.nodes) for contract in contracts),
        "blocks": sum(len(contract.blocks) for contract in contracts),
        "projects": sum(len(contract.projects) for contract in contracts),
        "relations": sum(len(contract.relations) for contract in contracts),
        "shared_placements": sum(len(contract.shared_placements) for contract in contracts),
        "editorial_pendings": sum(len(contract.editorial_pendings) for contract in contracts),
        "unique_entity_ids": len({item[2] for item in entities}),
        "source_mapping_records": len(bundle.source_mappings.get("mappings", [])),
        "block_types": dict(sorted(block_counts.items())),
        "diagnostics": {
            severity: diagnostic_counts.get(severity, 0)
            for severity in declared.get("diagnostics", {})
        },
    }
    for field, value in calculated.items():
        if declared.get(field) != value:
            findings.append(
                _diagnostic(
                    "INTEGRITY_COUNT_MISMATCH",
                    f"Declared {field}={declared.get(field)!r}, calculated {value!r}.",
                    field=f"integrity.global_counts.{field}",
                )
            )
    if diagnostic_counts.get("error", 0):
        findings.append(
            _diagnostic(
                "PACKAGE_DIAGNOSTIC_ERRORS_PRESENT",
                f"The package carries {diagnostic_counts['error']} error diagnostics.",
                field="diagnostics.diagnostics",
            )
        )
    if len({item[2] for item in entities}) != len(entities):
        findings.append(
            _diagnostic("DUPLICATE_ENTITY_ID", "Entity references are not globally unique.")
        )
    return findings


def _validate_global_references(bundle: CurriculumImportBundle) -> list[Diagnostic]:
    findings: list[Diagnostic] = []
    contracts = [phase.contract for phase in bundle.phases]
    nodes: dict[str, CurriculumNode] = {
        node.ref: node for contract in contracts for node in contract.nodes
    }
    blocks = {block.ref: block for contract in contracts for block in contract.blocks}
    all_refs = {item[2] for item in _iter_contract_entities(bundle)}

    for phase_number, _entity_type, ref, entity, _dependencies in _iter_contract_entities(bundle):
        provenance = getattr(entity, "provenance", None)
        source_file = getattr(provenance, "source_file", None)
        if not ref.startswith(f"f{phase_number}-"):
            findings.append(
                _diagnostic(
                    "ID_PHASE_PREFIX_MISMATCH",
                    "Entity ID prefix does not match its containing phase.",
                    entity_ref=ref,
                    source_file=source_file,
                    field="ref",
                )
            )
        if provenance is not None and not SHA256_RE.fullmatch(provenance.source_sha256):
            findings.append(
                _diagnostic(
                    "PROVENANCE_HASH_INVALID",
                    "Entity provenance source_sha256 is not a lowercase SHA-256 digest.",
                    entity_ref=ref,
                    source_file=source_file,
                    field="provenance.source_sha256",
                )
            )

    for phase in bundle.phases:
        contract = phase.contract
        for node in contract.nodes:
            if node.parent_ref and node.parent_ref not in nodes:
                findings.append(
                    _diagnostic(
                        "PARENT_REFERENCE_MISSING",
                        "Node parent does not exist in the complete bundle.",
                        entity_ref=node.ref,
                        source_file=node.provenance.source_file,
                        field="parent_ref",
                        reference=node.parent_ref,
                    )
                )
        for block in contract.blocks:
            if block.owner_ref and block.owner_ref not in nodes and block.owner_ref not in all_refs:
                findings.append(
                    _diagnostic(
                        "BLOCK_OWNER_MISSING",
                        "Block owner does not exist in the complete bundle.",
                        entity_ref=block.ref,
                        source_file=block.provenance.source_file,
                        field="owner_ref",
                        reference=block.owner_ref,
                    )
                )
            if isinstance(block, QuizBlock) and block.answer_key_ref:
                answer_key = blocks.get(block.answer_key_ref)
                if (
                    not isinstance(answer_key, AnswerKeyBlock)
                    or answer_key.question_ref != block.ref
                ):
                    findings.append(
                        _diagnostic(
                            "QUIZ_ANSWER_KEY_MISMATCH",
                            "Quiz answer_key_ref does not point to its own typed answer key.",
                            entity_ref=block.ref,
                            source_file=block.provenance.source_file,
                            field="answer_key_ref",
                            reference=block.answer_key_ref,
                        )
                    )
        for relation in contract.relations:
            for field, target in (
                ("source_ref", relation.source_ref),
                ("target_ref", relation.target_ref),
            ):
                if target not in nodes:
                    findings.append(
                        _diagnostic(
                            "RELATION_NODE_MISSING",
                            "Curriculum relation endpoint does not exist in the complete bundle.",
                            entity_ref=relation.ref,
                            source_file=relation.provenance.source_file,
                            field=field,
                            reference=target,
                        )
                    )
        for placement in contract.shared_placements:
            target_block = blocks.get(placement.block_ref)
            target_node = nodes.get(placement.subject_ref)
            if target_block is None or target_node is None or target_node.kind != "topic":
                findings.append(
                    _diagnostic(
                        "SHARED_PLACEMENT_REFERENCE_INVALID",
                        "Shared placement must target an existing block and topic node.",
                        entity_ref=placement.ref,
                        source_file=placement.provenance.source_file,
                        field="block_ref/subject_ref",
                        reference=f"{placement.block_ref} -> {placement.subject_ref}",
                    )
                )
        for project in contract.projects:
            unit = nodes.get(project.unit_ref)
            if unit is None or unit.kind != "submodule":
                findings.append(
                    _diagnostic(
                        "PROJECT_UNIT_REFERENCE_INVALID",
                        "Project unit_ref must target an existing unit node.",
                        entity_ref=project.ref,
                        source_file=project.provenance.source_file,
                        field="unit_ref",
                        reference=project.unit_ref,
                    )
                )
    return findings


def _validate_source_mappings(
    bundle: CurriculumImportBundle, repo_root: Path | None
) -> tuple[list[Diagnostic], dict[str, Any]]:
    findings: list[Diagnostic] = []
    mappings = bundle.source_mappings.get("mappings")
    if bundle.source_mappings.get("schema_version") != bundle.phases[0].contract.schema_version:
        findings.append(
            _diagnostic(
                "MAPPING_SCHEMA_MISMATCH",
                "Source mapping schema version does not match phase contracts.",
            )
        )
    if not isinstance(mappings, list):
        return [
            _diagnostic("SOURCE_MAPPINGS_INVALID", "source_mappings.mappings must be a list.")
        ], {}

    entity_refs = {item[2] for item in _iter_contract_entities(bundle)}
    destination_refs: set[str] = set()
    mapping_identities: set[tuple[str, str, str]] = set()
    source_paths: set[str] = set()
    source_hashes_verified = 0
    for index, row in enumerate(mappings):
        if not isinstance(row, dict):
            findings.append(
                _diagnostic("SOURCE_MAPPING_INVALID", f"Mapping row {index} is not an object.")
            )
            continue
        required = {
            "destination_refs",
            "normalizations",
            "phase",
            "source_file",
            "source_id",
            "source_sha256",
            "source_type",
        }
        if set(row) != required:
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_FIELDS_INVALID",
                    f"Mapping row {index} fields differ from the approved shape.",
                )
            )
            continue
        phase_name, source_file, source_id = row["phase"], row["source_file"], row["source_id"]
        identity = (str(phase_name), str(source_file), str(source_id))
        if identity in mapping_identities:
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_DUPLICATE", f"Duplicate source mapping identity at row {index}."
                )
            )
        mapping_identities.add(identity)
        if not isinstance(phase_name, str) or not PHASE_NAME_RE.fullmatch(phase_name):
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_PHASE_INVALID", f"Invalid phase label at mapping row {index}."
                )
            )
        if not isinstance(source_file, str) or not isinstance(source_id, str) or not source_id:
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_SOURCE_INVALID",
                    f"Invalid source identity at mapping row {index}.",
                )
            )
        digest = row["source_sha256"]
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_HASH_INVALID", f"Invalid source SHA-256 at mapping row {index}."
                )
            )
        refs = row["destination_refs"]
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) for ref in refs):
            findings.append(
                _diagnostic(
                    "SOURCE_MAPPING_DESTINATIONS_INVALID",
                    f"Missing or invalid destinations at mapping row {index}.",
                )
            )
        else:
            destination_refs.update(refs)
            for ref in refs:
                if ref not in entity_refs:
                    findings.append(
                        _diagnostic(
                            "MAPPING_DESTINATION_UNKNOWN",
                            f"Mapping row {index} references unknown entity {ref!r}.",
                            field="destination_refs",
                            reference=ref,
                        )
                    )
        if isinstance(source_file, str):
            source_paths.add(source_file)
            if repo_root is not None:
                try:
                    path = _safe_repo_path(repo_root, source_file)
                    if not path.is_file():
                        findings.append(
                            _diagnostic(
                                "MAPPING_SOURCE_MISSING",
                                f"Mapped source file does not exist: {source_file}.",
                                source_file=source_file,
                            )
                        )
                    elif (
                        isinstance(digest, str)
                        and SHA256_RE.fullmatch(digest)
                        and _sha256(path.read_bytes()) != digest
                    ):
                        findings.append(
                            _diagnostic(
                                "MAPPING_SOURCE_HASH_MISMATCH",
                                f"Mapped source hash differs from disk: {source_file}.",
                                source_file=source_file,
                            )
                        )
                    else:
                        source_hashes_verified += 1
                except (OSError, ValueError) as exc:
                    findings.append(
                        _diagnostic(
                            "MAPPING_SOURCE_PATH_INVALID", str(exc), source_file=source_file
                        )
                    )

    # The approved source mapping maps all authored block/relationship/placement
    # and project records. Phase/module/topic nodes and generated root pendings
    # are structural derivations, not omitted authored blocks.
    expected_mapped_refs = {
        ref
        for phase, entity_type, ref, _entity, _deps in _iter_contract_entities(bundle)
        if entity_type
        in {
            "block",
            "relation",
            "shared_placement",
            "project",
            "project_delivery",
            "project_milestone",
            "project_variant",
        }
        or (
            entity_type == "node"
            and next(
                node for node in bundle.phases[phase - 1].contract.nodes if node.ref == ref
            ).kind
            == "submodule"
        )
    }
    missing_expected = expected_mapped_refs - destination_refs
    if missing_expected:
        findings.append(
            _diagnostic(
                "MAPPING_COVERAGE_GAP",
                f"{len(missing_expected)} authored entity references are not covered by source mappings.",
                reference=", ".join(sorted(missing_expected)[:8]),
            )
        )

    unmapped_generated = entity_refs - destination_refs
    unmapped_kinds: Counter[str] = Counter()
    entity_by_ref = {
        ref: (entity_type, entity)
        for _phase, entity_type, ref, entity, _deps in _iter_contract_entities(bundle)
    }
    for ref in unmapped_generated:
        entity_type, entity = entity_by_ref[ref]
        if entity_type == "node" and entity.kind in {"phase", "module", "topic"}:
            unmapped_kinds[f"derived_node:{entity.kind}"] += 1
        elif entity_type == "editorial_pending" and entity.kind in {
            "unresolved_reference",
            "obsidian_vault_root_unknown",
        }:
            unmapped_kinds[f"generated_pending:{entity.kind}"] += 1
        else:
            findings.append(
                _diagnostic(
                    "UNMAPPED_ENTITY_UNCLASSIFIED",
                    f"Entity {ref} has no source mapping and is not an approved structural derivation.",
                    entity_ref=ref,
                )
            )

    expected_record_count = bundle.integrity.get("global_counts", {}).get("source_mapping_records")
    if len(mappings) != expected_record_count:
        findings.append(
            _diagnostic(
                "SOURCE_MAPPING_COUNT_MISMATCH",
                f"Source mapping rows={len(mappings)}, expected={expected_record_count}.",
            )
        )
    if len(source_paths) != len(mappings):
        findings.append(
            _diagnostic(
                "SOURCE_MAPPING_PATH_COLLISION",
                "Source mapping rows do not have unique source files.",
            )
        )
    return findings, {
        "records": len(mappings),
        "unique_source_files": len(source_paths),
        "unique_destination_entity_refs": len(destination_refs),
        "unmapped_approved_structural_refs": len(unmapped_generated),
        "unmapped_approved_structural_kinds": dict(sorted(unmapped_kinds.items())),
        "destination_refs_not_in_bundle": 0,
        "source_file_hashes_verified": source_hashes_verified,
    }


def _validate_integrity_sidecars(
    bundle: CurriculumImportBundle, repo_root: Path
) -> tuple[list[Diagnostic], dict[str, Any]]:
    findings: list[Diagnostic] = []
    source = bundle.source
    manifest_path_text = source.get("integrity_manifest")
    expected_manifest_sha = source.get("integrity_manifest_sha256")
    if not isinstance(manifest_path_text, str) or not isinstance(expected_manifest_sha, str):
        return [
            _diagnostic(
                "INTEGRITY_MANIFEST_REFERENCE_MISSING",
                "Bundle source must identify the integrity manifest and its SHA-256.",
            )
        ], {}
    try:
        manifest_path = _safe_repo_path(repo_root, manifest_path_text)
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256(manifest_bytes)
        if manifest_sha != expected_manifest_sha:
            findings.append(
                _diagnostic(
                    "INTEGRITY_MANIFEST_HASH_MISMATCH",
                    "Integrity manifest hash differs from the package reference.",
                    source_file=manifest_path_text,
                )
            )
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _diagnostic(
                "INTEGRITY_MANIFEST_UNREADABLE",
                f"Could not validate integrity manifest: {exc}",
                source_file=manifest_path_text,
            )
        ], {}

    if not isinstance(manifest, dict):
        return [
            _diagnostic(
                "INTEGRITY_MANIFEST_INVALID",
                "Integrity manifest root must be an object.",
                source_file=manifest_path_text,
            )
        ], {}

    manifest_artifacts = manifest.get("artifacts", [])
    expected_artifacts: dict[str, str] = {}
    if not isinstance(manifest_artifacts, list):
        findings.append(
            _diagnostic(
                "SIDECAR_ARTIFACT_INDEX_INVALID",
                "Integrity manifest artifacts must be an array.",
                source_file=manifest_path_text,
            )
        )
        manifest_artifacts = []
    for item in manifest_artifacts:
        if not isinstance(item, dict):
            findings.append(
                _diagnostic(
                    "SIDECAR_ARTIFACT_ENTRY_INVALID",
                    "Integrity artifact entries must be objects.",
                    source_file=manifest_path_text,
                )
            )
            continue
        artifact_path = item.get("path")
        artifact_sha = item.get("sha256")
        if not isinstance(artifact_path, str) or not isinstance(artifact_sha, str):
            findings.append(
                _diagnostic(
                    "SIDECAR_ARTIFACT_ENTRY_INVALID",
                    "Integrity artifact entries require string path and sha256 fields.",
                    source_file=manifest_path_text,
                )
            )
            continue
        if artifact_path in expected_artifacts:
            findings.append(
                _diagnostic(
                    "SIDECAR_ARTIFACT_PATH_DUPLICATE",
                    f"Integrity manifest repeats artifact path {artifact_path!r}.",
                    source_file=manifest_path_text,
                )
            )
            continue
        expected_artifacts[artifact_path] = artifact_sha
    if bundle.integrity.get("artifact_sha256") != expected_artifacts:
        findings.append(
            _diagnostic(
                "SIDECAR_HASH_INDEX_MISMATCH",
                "Bundle artifact_sha256 differs from the integrity manifest.",
            )
        )
    verified_artifacts = 0
    contract_root = manifest_path.parent
    for relative_path, expected_sha in sorted(expected_artifacts.items()):
        try:
            sidecar = _safe_repo_path(contract_root, relative_path)
            content = sidecar.read_bytes()
            if _sha256(content) != expected_sha:
                findings.append(
                    _diagnostic(
                        "SIDECAR_HASH_MISMATCH",
                        f"Integrity artifact hash mismatch: {relative_path}.",
                        source_file=relative_path,
                    )
                )
                continue
            if relative_path.startswith("fase_") and relative_path.endswith(".contract.json"):
                number = int(relative_path[5:7])
                phase = next((item for item in bundle.phases if item.phase == number), None)
                if (
                    phase is None
                    or _sha256(canonical_json(phase.contract).encode("utf-8")) != expected_sha
                ):
                    findings.append(
                        _diagnostic(
                            "PHASE_SIDECAR_MISMATCH",
                            f"Bundle phase {number} differs from its validated sidecar.",
                        )
                    )
                    continue
            elif relative_path == "source_mappings.json":
                if json.loads(content.decode("utf-8")) != bundle.source_mappings:
                    findings.append(
                        _diagnostic(
                            "MAPPING_SIDECAR_MISMATCH",
                            "Package source mappings differ from the validated sidecar.",
                        )
                    )
                    continue
            elif relative_path == "diagnostics.json":
                if json.loads(content.decode("utf-8")) != bundle.diagnostics:
                    findings.append(
                        _diagnostic(
                            "DIAGNOSTICS_SIDECAR_MISMATCH",
                            "Package diagnostics differ from the validated sidecar.",
                        )
                    )
                    continue
            verified_artifacts += 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings.append(
                _diagnostic(
                    "SIDECAR_UNREADABLE",
                    f"Could not validate {relative_path}: {exc}",
                    source_file=relative_path,
                )
            )

    base_commit = manifest.get("base_commit")
    if source.get("base_commit") != base_commit:
        findings.append(
            _diagnostic(
                "BASE_COMMIT_MISMATCH", "Bundle base commit differs from the integrity manifest."
            )
        )
    if source.get("branch") != manifest.get("branch"):
        findings.append(
            _diagnostic(
                "BASE_BRANCH_MISMATCH", "Bundle branch differs from the integrity manifest."
            )
        )
    return findings, {
        "integrity_manifest": manifest_path_text,
        "integrity_manifest_sha256": manifest_sha,
        "sidecars_verified": verified_artifacts,
        "sidecars_expected": len(expected_artifacts),
        "base_commit": base_commit,
        "branch": manifest.get("branch"),
    }


def _validate_migration_inventory(
    bundle: CurriculumImportBundle, repo_root: Path
) -> tuple[list[Diagnostic], dict[str, Any]]:
    findings: list[Diagnostic] = []
    all_rows: list[tuple[int, dict[str, str]]] = []
    rows_by_phase: Counter[int] = Counter()
    expected_rows = bundle.integrity.get("global_counts", {}).get("migration_mapping_rows")
    for phase_number in range(1, 11):
        report_path = Path("docs/migracao") / f"relatorio_mapeamento_fase{phase_number}.csv"
        path = repo_root / report_path
        if not path.is_file():
            findings.append(
                _diagnostic(
                    "MIGRATION_REPORT_MISSING",
                    f"Migration mapping report is missing: {report_path.as_posix()}.",
                    source_file=report_path.as_posix(),
                )
            )
            continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
        except (OSError, UnicodeError, csv.Error) as exc:
            findings.append(
                _diagnostic(
                    "MIGRATION_REPORT_INVALID", f"Could not parse {report_path.as_posix()}: {exc}"
                )
            )
            continue
        rows_by_phase[phase_number] = len(rows)
        all_rows.extend((phase_number, row) for row in rows)

    migrated_root = repo_root / MIGRATED_ROOT
    actual_files = (
        {
            path.relative_to(repo_root).as_posix()
            for path in migrated_root.rglob("*")
            if path.is_file()
        }
        if migrated_root.is_dir()
        else set()
    )
    mapped_destinations: set[str] = set()
    sentinels: list[str] = []
    origin_paths: set[str] = set()
    checked_origin_paths: set[str] = set()
    for phase_number, row in all_rows:
        destination = row.get("destino", "")
        if destination.startswith("sem destino"):
            sentinels.append(destination)
        elif destination.startswith(f"{MIGRATED_ROOT}/"):
            try:
                _safe_repo_path(repo_root, destination)
                mapped_destinations.add(destination)
            except ValueError as exc:
                findings.append(
                    _diagnostic("MIGRATION_DESTINATION_UNSAFE", str(exc), source_file=destination)
                )
        else:
            findings.append(
                _diagnostic(
                    "MIGRATION_DESTINATION_INVALID",
                    f"Unexpected mapping destination: {destination!r}.",
                )
            )
        origin = row.get("origem", "")
        if origin:
            origin_paths.add(origin)
            if origin in checked_origin_paths:
                continue
            checked_origin_paths.add(origin)
            try:
                origin_relative = (
                    origin
                    if origin.startswith("docs/courses/trilhacode/")
                    else f"docs/courses/trilhacode/{origin}"
                )
                origin_path = _safe_repo_path(repo_root, origin_relative)
                if not origin_path.is_file():
                    findings.append(
                        _diagnostic(
                            "MIGRATION_ORIGIN_MISSING",
                            f"Original source does not exist: {origin_relative}.",
                            source_file=origin_relative,
                        )
                    )
            except ValueError as exc:
                findings.append(
                    _diagnostic("MIGRATION_ORIGIN_UNSAFE", str(exc), source_file=origin)
                )

    if len(all_rows) != expected_rows:
        findings.append(
            _diagnostic(
                "MIGRATION_MAPPING_COUNT_MISMATCH",
                f"Migration report rows={len(all_rows)}, expected={expected_rows}.",
            )
        )
    declared = bundle.integrity.get("global_counts", {})
    if len(sentinels) != declared.get("migration_removal_sentinels"):
        findings.append(
            _diagnostic(
                "MIGRATION_SENTINEL_COUNT_MISMATCH",
                f"Removal sentinel rows={len(sentinels)}, expected={declared.get('migration_removal_sentinels')}.",
            )
        )
    missing_destinations = mapped_destinations - actual_files
    if missing_destinations:
        findings.append(
            _diagnostic(
                "MIGRATION_DESTINATION_MISSING",
                f"{len(missing_destinations)} mapped physical files are missing.",
                reference=", ".join(sorted(missing_destinations)[:8]),
            )
        )
    mapped_present = mapped_destinations & actual_files
    extras = actual_files - mapped_destinations
    expected_files = declared.get("migrated_files")
    expected_destinations = declared.get("unique_physical_migration_destinations")
    expected_structural = declared.get("authorized_structural_files_outside_mapped_destinations")
    if len(actual_files) != expected_files:
        findings.append(
            _diagnostic(
                "MIGRATED_FILE_COUNT_MISMATCH",
                f"Migrated tree files={len(actual_files)}, expected={expected_files}.",
            )
        )
    if len(mapped_present) != expected_destinations:
        findings.append(
            _diagnostic(
                "MAPPED_DESTINATION_COUNT_MISMATCH",
                f"Unique physical destinations={len(mapped_present)}, expected={expected_destinations}.",
            )
        )
    if len(extras) != expected_structural:
        findings.append(
            _diagnostic(
                "STRUCTURAL_FILE_COUNT_MISMATCH",
                f"Unmapped structural files={len(extras)}, expected={expected_structural}.",
            )
        )

    original_root = repo_root / "docs/courses/trilhacode/Conteudos"
    original_sources = (
        {
            path.relative_to(repo_root).as_posix()
            for path in original_root.rglob("*.md")
            if path.is_file()
        }
        if original_root.is_dir()
        else set()
    )
    source_markdown_count = len(original_sources)
    if source_markdown_count != declared.get("source_markdown_files_found"):
        findings.append(
            _diagnostic(
                "ORIGINAL_SOURCE_COUNT_MISMATCH",
                f"Original Markdown sources={source_markdown_count}, expected={declared.get('source_markdown_files_found')}.",
            )
        )
    reported_origin_paths = {
        origin
        if origin.startswith("docs/courses/trilhacode/")
        else f"docs/courses/trilhacode/{origin}"
        for origin in origin_paths
    }
    unmapped_original_sources = original_sources - reported_origin_paths
    expected_editorial_copies = {
        "docs/courses/trilhacode/Conteudos/Fase_7/37.1_Servicos_gerenciados.md",
        "docs/courses/trilhacode/Conteudos/Fase_7/37.2_Kubernetes_basico.md",
    }
    if unmapped_original_sources != expected_editorial_copies:
        findings.append(
            _diagnostic(
                "ORIGINAL_SOURCE_MAPPING_GAP",
                "Original Markdown sources outside active migration mappings differ from the two documented Fase 7 copies.",
                reference=", ".join(sorted(unmapped_original_sources)),
                remediation="Resolve editorial scope explicitly; do not delete or merge source copies in the adapter.",
            )
        )

    phase_files: dict[str, int] = {}
    for phase_number in range(1, 11):
        phase_dir = migrated_root / f"Fase_{phase_number}"
        count = (
            sum(1 for path in phase_dir.rglob("*") if path.is_file()) if phase_dir.is_dir() else 0
        )
        phase_files[f"Fase_{phase_number}"] = count

    return findings, {
        "migration_mapping_rows": len(all_rows),
        "rows_by_phase": {f"Fase_{number}": rows_by_phase[number] for number in range(1, 11)},
        "unique_physical_migration_destinations": len(mapped_present),
        "removal_sentinel_rows": len(sentinels),
        "removal_sentinel_values": dict(Counter(sentinels)),
        "authorized_unmapped_structural_files": len(extras),
        "unmapped_structural_paths": sorted(extras),
        "migrated_files": len(actual_files),
        "files_by_phase": phase_files,
        "original_markdown_files": source_markdown_count,
        "unique_original_source_paths_in_reports": len(origin_paths),
        "preserved_unmapped_editorial_sources": sorted(unmapped_original_sources),
    }


def validate_package(
    bundle: CurriculumImportBundle,
    *,
    repo_root: Path | None = None,
    bundle_sha256: str | None = None,
    bundle_path: Path | None = None,
) -> ValidatedPackage:
    """Validate contract references and, optionally, the repository evidence."""
    findings = _compare_integrity_counts(bundle)
    for phase in bundle.phases:
        contract_report = validate_contract(phase.contract)
        findings.extend(
            item
            for item in contract_report.diagnostics
            if item.severity == DiagnosticSeverity.ERROR
        )
    findings.extend(_validate_global_references(bundle))
    mapping_findings, mapping_summary = _validate_source_mappings(bundle, repo_root)
    findings.extend(mapping_findings)

    repository_checks: dict[str, Any] = {
        "source_mappings": mapping_summary,
        "integrity_sidecars": None,
        "migration_inventory": None,
        "database_access": "none",
        "writes_performed": False,
    }
    if repo_root is not None:
        sidecar_findings, sidecar_summary = _validate_integrity_sidecars(bundle, repo_root)
        findings.extend(sidecar_findings)
        repository_checks["integrity_sidecars"] = sidecar_summary
        migration_findings, migration_summary = _validate_migration_inventory(bundle, repo_root)
        findings.extend(migration_findings)
        repository_checks["migration_inventory"] = migration_summary
        actual_phase_summaries: dict[str, dict[str, int]] = {}
        for phase in bundle.phases:
            phase_name = f"Fase_{phase.phase}"
            actual_phase_summaries[phase_name] = {
                "files": migration_summary["files_by_phase"].get(phase_name, -1),
                "units": sum(node.kind == "submodule" for node in phase.contract.nodes),
                "nodes": len(phase.contract.nodes),
                "blocks": len(phase.contract.blocks),
                "projects": len(phase.contract.projects),
                "relations": len(phase.contract.relations),
                "shared_placements": len(phase.contract.shared_placements),
                "editorial_pendings": len(phase.contract.editorial_pendings),
            }
        for phase_summary in bundle.integrity.get("phase_summaries", []):
            raw_phase_name = phase_summary.get("phase") if isinstance(phase_summary, dict) else None
            if not isinstance(raw_phase_name, str):
                findings.append(
                    _diagnostic(
                        "PHASE_SUMMARY_INVALID",
                        "Integrity phase summaries require a string phase name.",
                    )
                )
                continue
            phase_name = raw_phase_name
            actual = actual_phase_summaries.get(phase_name)
            if actual is None or any(
                phase_summary.get(key) != value for key, value in actual.items()
            ):
                findings.append(
                    _diagnostic(
                        "PHASE_SUMMARY_MISMATCH",
                        f"Integrity summary differs from calculated package/tree values for {phase_name!r}.",
                    )
                )
        structural_paths = {artifact.path for artifact in bundle.structural_artifacts}
        for artifact in bundle.structural_artifacts:
            try:
                path = _safe_repo_path(repo_root, artifact.path)
                if not path.is_file():
                    findings.append(
                        _diagnostic(
                            "STRUCTURAL_ARTIFACT_MISSING",
                            f"Structural artifact is missing: {artifact.path}.",
                            source_file=artifact.path,
                        )
                    )
                elif path.read_bytes() != artifact.content.encode("utf-8"):
                    findings.append(
                        _diagnostic(
                            "STRUCTURAL_ARTIFACT_CONTENT_MISMATCH",
                            f"Structural artifact differs from repository file: {artifact.path}.",
                            source_file=artifact.path,
                        )
                    )
            except (OSError, ValueError) as exc:
                findings.append(
                    _diagnostic(
                        "STRUCTURAL_ARTIFACT_PATH_INVALID", str(exc), source_file=artifact.path
                    )
                )
        expected_unrepresented = set(bundle.integrity.get("unrepresented_structural_files", []))
        if structural_paths != expected_unrepresented:
            findings.append(
                _diagnostic(
                    "STRUCTURAL_INDEX_MISMATCH",
                    "Packaged structural artifacts differ from the authorized unrepresented-file index.",
                )
            )

        legacy_path = bundle.integrity.get("global_counts", {}).get("legacy_json_path")
        if isinstance(legacy_path, str) and bundle_path is not None:
            try:
                actual_path = _safe_repo_path(repo_root, legacy_path)
                if actual_path.resolve() == bundle_path.resolve():
                    actual_sha = _sha256(bundle_path.read_bytes())
                    repository_checks["current_bundle_sha256"] = actual_sha
                    repository_checks["legacy_json_sha256_before_conversion"] = bundle.source.get(
                        "legacy_json_sha256_before_conversion"
                    )
                    if bundle.source.get(
                        "legacy_json_sha256_before_conversion"
                    ) != bundle.integrity.get("global_counts", {}).get("legacy_json_sha256"):
                        findings.append(
                            _diagnostic(
                                "LEGACY_SOURCE_HASH_METADATA_MISMATCH",
                                "The pre-conversion JSON SHA differs between bundle source and integrity counts.",
                            )
                        )
            except (OSError, ValueError) as exc:
                findings.append(
                    _diagnostic("LEGACY_JSON_PATH_INVALID", str(exc), source_file=legacy_path)
                )

    if findings:
        raise AdapterValidationError(findings)
    if bundle_sha256 is None:
        bundle_sha256 = _sha256(canonical_import_bundle_json(bundle).encode("utf-8"))
    return ValidatedPackage(
        bundle=bundle,
        bundle_sha256=bundle_sha256,
        path=bundle_path,
        repository_checks=repository_checks,
    )


def read_and_validate_bundle(
    bundle_path: Path,
    *,
    repo_root: Path | None = None,
) -> ValidatedPackage:
    path = bundle_path.resolve()
    raw = path.read_bytes()
    bundle = parse_bundle_bytes(raw)
    return validate_package(
        bundle,
        repo_root=repo_root.resolve() if repo_root else None,
        bundle_sha256=_sha256(raw),
        bundle_path=path,
    )


def _compatibility_for_block(
    block: Any,
) -> tuple[OperationState, str | None, str, str | None, bool]:
    """Return status, target, reason, candidate action, and protected-content flag."""
    block_type = block.type
    if block_type == "theory":
        return (
            OperationState.PENDING_DATABASE_SNAPSHOT,
            "content_blocks:theory_text",
            "LOSSLESS_THEORY_TRANSFORM",
            "upsert_by_curriculum_ref",
            False,
        )
    if block_type == "summary":
        return (
            OperationState.PENDING_DATABASE_SNAPSHOT,
            "content_blocks:summary",
            "NATIVE_SUMMARY_TYPE",
            "upsert_by_curriculum_ref",
            False,
        )
    if block_type == "practice":
        return (
            OperationState.PENDING_DATABASE_SNAPSHOT,
            "content_blocks:practical_challenge",
            "LOSSLESS_PRACTICE_TRANSFORM",
            "upsert_by_curriculum_ref",
            False,
        )
    if block_type == "flashcard":
        return (
            OperationState.PENDING_DATABASE_SNAPSHOT,
            "content_blocks:flashcard",
            "NATIVE_FLASHCARD_TYPE",
            "upsert_by_curriculum_ref",
            False,
        )
    if isinstance(block, ReferenceBlock):
        if (
            block.target_kind == "external"
            and block.url
            and block.label
            and block.raw_text is not None
            and block.citation == block.raw_text
            and block.target_ref is None
            and block.pending_ref is None
        ):
            return (
                OperationState.PENDING_DATABASE_SNAPSHOT,
                "content_blocks:external_link",
                "LOSSLESS_EXTERNAL_REFERENCE_TRANSFORM",
                "upsert_by_curriculum_ref",
                False,
            )
        return (
            OperationState.PENDING_DECISION,
            None,
            "REFERENCE_DESTINATION_OR_RENDERING_UNRESOLVED",
            None,
            False,
        )
    if isinstance(block, QuizBlock):
        if block.format != "multiple_choice" or not block.options:
            if not block.answer_key_required:
                return (
                    OperationState.PENDING_DECISION,
                    None,
                    "UNSCORED_REVIEW_QUESTION_POLICY_UNDECIDED",
                    None,
                    True,
                )
            return OperationState.BLOCKED, None, "QUIZ_FORMAT_NOT_SUPPORTED_BY_GRADER", None, True
        return (
            OperationState.BLOCKED,
            "quiz_versions:private_snapshot",
            "VERSIONED_QUIZ_BUNDLE_PUBLISHER_REQUIRED",
            None,
            True,
        )
    if isinstance(block, AnswerKeyBlock):
        return (
            OperationState.BLOCKED,
            "quiz_versions:private_snapshot",
            "PRIVATE_ANSWER_KEY_IMPORT_PATH_REQUIRED",
            None,
            True,
        )
    if block_type == "checklist":
        return (
            OperationState.BLOCKED,
            None,
            "CHECKLIST_ITEM_ID_AND_PROGRESS_SEMANTICS_REQUIRE_EXTENSION",
            None,
            False,
        )
    if block_type == "instructor_note":
        return (
            OperationState.BLOCKED,
            None,
            "INSTRUCTOR_ONLY_VISIBILITY_NOT_ENFORCED_BY_STUDENT_READ_PATH",
            None,
            True,
        )
    return (
        OperationState.BLOCKED,
        None,
        f"NO_LOSSLESS_NATIVE_MAPPING:{block_type}",
        None,
        block_type in {"solution", "feedback"},
    )


def _operation_for_entity(
    phase: int,
    entity_type: str,
    ref: str,
    entity: Any,
    dependencies: tuple[str, ...],
    snapshot: Mapping[str, ExistingEntitySnapshot] | None,
) -> PlannedOperation:
    operation = OperationState.PENDING_DATABASE_SNAPSHOT
    target: str | None = None
    candidate: str | None = "upsert_by_curriculum_ref"
    reason = "DATABASE_STATE_NOT_READ"
    private = False
    if entity_type == "node":
        target = "nodes"
        candidate = "upsert_by_meta_import_ref"
        reason = "GENERIC_NODE_SCHEMA_COMPATIBLE; UNIQUE_EXTERNAL_REF_INDEX_REQUIRED"
    elif entity_type == "block":
        operation, target, reason, candidate, private = _compatibility_for_block(entity)
    elif entity_type == "relation":
        target = "relations"
        if entity.kind == "prerequisite" and entity.enforced:
            operation = OperationState.PENDING_DECISION
            candidate = None
            reason = "PREREQUISITE_KIND_NOT_EXPLICIT; DO_NOT_INFER_QUIZ_PASSED"
        else:
            candidate = "upsert_by_source_target_kind"
            reason = "GENERIC_RELATION_SCHEMA_COMPATIBLE; DATABASE_STATE_NOT_READ"
    elif entity_type == "shared_placement":
        operation = OperationState.BLOCKED
        target = None
        candidate = None
        reason = "NO_CANONICAL_SHARED_PLACEMENT_MODEL"
    elif entity_type in {"project", "project_delivery", "project_milestone", "project_variant"}:
        operation = OperationState.BLOCKED
        target = None
        candidate = None
        reason = "STRUCTURED_PROJECT_MODEL_AND_RENDERER_REQUIRED"
    elif entity_type == "editorial_pending":
        operation = OperationState.PENDING_DECISION
        target = "audit_sidecar"
        candidate = None
        reason = "EDITORIAL_PENDING_MUST_REMAIN_VISIBLE_AND_UNRESOLVED"

    content_hash = _canonical_entity_hash(entity)
    if snapshot is not None and operation == OperationState.PENDING_DATABASE_SNAPSHOT:
        operation = classify_snapshot_state(ref, content_hash, snapshot.get(ref))
        reason = {
            OperationState.CREATE: "ABSENT_FROM_AUTHORIZED_SNAPSHOT",
            OperationState.UPDATE: "SOURCE_CHANGED_AND_EXISTING_CONTENT_UNMODIFIED",
            OperationState.UNCHANGED: "CANONICAL_CONTENT_MATCHES_SNAPSHOT",
            OperationState.CONFLICT: "LOCAL_AND_SOURCE_CONTENT_DIVERGED",
            OperationState.PENDING_DATABASE_SNAPSHOT: "DATABASE_STATE_NOT_READ",
            OperationState.BLOCKED: reason,
            OperationState.PENDING_DECISION: reason,
        }[operation]
        candidate = {
            OperationState.CREATE: "create",
            OperationState.UPDATE: "update",
            OperationState.UNCHANGED: None,
            OperationState.CONFLICT: None,
            OperationState.PENDING_DATABASE_SNAPSHOT: "upsert_by_curriculum_ref",
            OperationState.BLOCKED: None,
            OperationState.PENDING_DECISION: None,
        }[operation]

    return PlannedOperation(
        entity_ref=ref,
        entity_type=entity_type,
        phase=phase,
        operation=operation,
        target=target,
        candidate_action=candidate
        if operation
        in {OperationState.PENDING_DATABASE_SNAPSHOT, OperationState.CREATE, OperationState.UPDATE}
        else None,
        reason_code=reason,
        dependencies=tuple(sorted(set(dependencies))),
        source_file=getattr(getattr(entity, "provenance", None), "source_file", None),
        private=private,
        content_sha256=content_hash
        if operation not in {OperationState.BLOCKED, OperationState.PENDING_DECISION}
        or entity_type == "editorial_pending"
        else None,
    )


def classify_snapshot_state(
    curriculum_ref: str,
    desired_sha256: str,
    existing: ExistingEntitySnapshot | None,
) -> OperationState:
    """Classify against an explicitly supplied snapshot without reading a DB."""
    if not SHA256_RE.fullmatch(desired_sha256):
        raise ValueError("desired_sha256 must be a lowercase SHA-256 digest")
    if existing is None:
        return OperationState.CREATE
    if existing.curriculum_ref != curriculum_ref:
        return OperationState.CONFLICT
    if not SHA256_RE.fullmatch(existing.current_sha256):
        return OperationState.CONFLICT
    if existing.current_sha256 == desired_sha256:
        return OperationState.UNCHANGED
    if (
        existing.last_imported_sha256 is not None
        and existing.current_sha256 == existing.last_imported_sha256
    ):
        return OperationState.UPDATE
    return OperationState.CONFLICT


def build_dry_run_plan(
    package: ValidatedPackage,
    *,
    snapshot: Mapping[str, ExistingEntitySnapshot] | None = None,
) -> dict[str, Any]:
    """Return a canonical plan. No snapshot means no create/update claim."""
    bundle = package.bundle
    operations = [
        _operation_for_entity(phase, kind, ref, entity, dependencies, snapshot)
        for phase, kind, ref, entity, dependencies in _iter_contract_entities(bundle)
    ]
    operations.sort(key=lambda item: (item.phase, item.entity_type, item.entity_ref))
    operation_counts = Counter(item.operation.value for item in operations)
    block_type_counts = Counter(
        block.type for phase in bundle.phases for block in phase.contract.blocks
    )
    block_dispositions: dict[str, dict[str, int]] = {}
    for operation in operations:
        if operation.entity_type == "block":
            block = next(
                block
                for phase in bundle.phases
                for block in phase.contract.blocks
                if block.ref == operation.entity_ref
            )
            dispositions = block_dispositions.setdefault(block.type, {})
            dispositions[operation.operation.value] = (
                dispositions.get(operation.operation.value, 0) + 1
            )

    relation_semantics = Counter(
        "pending_quiz_or_content_classification"
        if relation.kind == "prerequisite" and relation.enforced
        else relation.kind
        for phase in bundle.phases
        for relation in phase.contract.relations
    )
    project_counts = {
        "projects": sum(len(phase.contract.projects) for phase in bundle.phases),
        "deliveries": sum(
            len(project.deliveries)
            for phase in bundle.phases
            for project in phase.contract.projects
        ),
        "milestones": sum(
            len(project.milestones)
            for phase in bundle.phases
            for project in phase.contract.projects
        ),
        "variants": sum(
            len(project.variants) for phase in bundle.phases for project in phase.contract.projects
        ),
        "formal_delivery_projects": sum(
            project.has_formal_deliveries
            for phase in bundle.phases
            for project in phase.contract.projects
        ),
        "formal_milestone_projects": sum(
            project.has_formal_milestones
            for phase in bundle.phases
            for project in phase.contract.projects
        ),
    }
    editorial_counts = Counter(
        pending.kind for phase in bundle.phases for pending in phase.contract.editorial_pendings
    )
    structural_artifacts = [
        {
            "path": artifact.path,
            "sha256": artifact.sha256,
            "operation": OperationState.PENDING_DECISION.value,
            "reason_code": "STRUCTURAL_ARTIFACT_DESTINATION_NOT_DEFINED",
            "content_included_in_plan": False,
        }
        for artifact in sorted(bundle.structural_artifacts, key=lambda item: item.path)
    ]
    package_refs = {operation.entity_ref for operation in operations}
    snapshot_only_refs = sorted(set(snapshot or {}) - package_refs) if snapshot is not None else []
    track_operation = {
        "identity_key": "trilhacode:track",
        "operation": OperationState.PENDING_DATABASE_SNAPSHOT.value,
        "target": "tracks",
        "candidate_action": "upsert_by_slug",
        "reason_code": "DATABASE_STATE_NOT_READ",
    }

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "bundle_schema_version": bundle.schema_version,
        "bundle_sha256": package.bundle_sha256,
        "base_commit": bundle.source.get("base_commit"),
        "branch": bundle.source.get("branch"),
        "mode": "offline_validation_and_planning_only",
        "database_access": "none",
        "writes_performed": False,
        "migrations_executed": False,
        "publication_performed": False,
        "deletions_proposed": 0,
        "snapshot_supplied": snapshot is not None,
        "snapshot_only_records": {
            "count": len(snapshot_only_refs),
            "refs": snapshot_only_refs,
            "deletions_proposed": 0,
        },
        "counts": {
            "phases": len(bundle.phases),
            "units": sum(
                node.kind == "submodule" for phase in bundle.phases for node in phase.contract.nodes
            ),
            "nodes": sum(len(phase.contract.nodes) for phase in bundle.phases),
            "blocks": sum(len(phase.contract.blocks) for phase in bundle.phases),
            "block_types": dict(sorted(block_type_counts.items())),
            "projects": project_counts,
            "shared_placements": sum(
                len(phase.contract.shared_placements) for phase in bundle.phases
            ),
            "relations": sum(len(phase.contract.relations) for phase in bundle.phases),
            "unique_entity_ids": len(_iter_contract_entities(bundle)),
            "source_mapping_records": len(bundle.source_mappings.get("mappings", [])),
            "editorial_pendings": sum(
                len(phase.contract.editorial_pendings) for phase in bundle.phases
            ),
            "operations": len(operations),
            "operations_by_state": {
                state.value: operation_counts.get(state.value, 0) for state in OperationState
            },
        },
        "mapping_coverage": package.repository_checks.get("source_mappings"),
        "migration_inventory": package.repository_checks.get("migration_inventory"),
        "integrity_sidecars": package.repository_checks.get("integrity_sidecars"),
        "relation_semantics": dict(sorted(relation_semantics.items())),
        "execution_order": {
            "mode": "dependency_order_proposal_only",
            "executable": False,
            "sequence": [
                {
                    "step": 1,
                    "key": "track",
                    "depends_on": [],
                    "status": OperationState.PENDING_DATABASE_SNAPSHOT.value,
                    "ordering": "stable curriculum identity; database comparison required",
                },
                {
                    "step": 2,
                    "key": "hierarchy_nodes",
                    "depends_on": ["track", "parent_node"],
                    "status": OperationState.PENDING_DATABASE_SNAPSHOT.value,
                    "ordering": "phase, then phase/module/submodule/topic ancestry, then stable ref",
                },
                {
                    "step": 3,
                    "key": "supported_content_blocks",
                    "depends_on": ["owner_node"],
                    "status": OperationState.PENDING_DATABASE_SNAPSHOT.value,
                    "ordering": "owner node, block order, stable ref",
                },
                {
                    "step": 4,
                    "key": "quiz_versions_and_private_answer_keys",
                    "depends_on": ["owner_node", "quiz", "answer_key"],
                    "status": OperationState.BLOCKED.value,
                    "ordering": "publish each quiz and its private key atomically after grader compatibility is resolved",
                },
                {
                    "step": 5,
                    "key": "relations_and_shared_placements",
                    "depends_on": ["referenced_nodes", "canonical_blocks"],
                    "status": OperationState.PENDING_DECISION.value,
                    "ordering": "only after reference targets and relationship semantics are approved",
                },
                {
                    "step": 6,
                    "key": "projects_and_components",
                    "depends_on": ["owner_node", "deliveries", "criteria", "rubrics", "checklists"],
                    "status": OperationState.BLOCKED.value,
                    "ordering": "project container before its source-defined components",
                },
                {
                    "step": 7,
                    "key": "editorial_audit_sidecars",
                    "depends_on": ["source_entities"],
                    "status": OperationState.PENDING_DECISION.value,
                    "ordering": "retain as administrative audit data; never publish as learner content",
                },
            ],
        },
        "block_dispositions": {
            key: dict(sorted(value.items())) for key, value in sorted(block_dispositions.items())
        },
        "editorial_pending_kinds": dict(sorted(editorial_counts.items())),
        "track_operation": track_operation,
        "structural_artifacts": structural_artifacts,
        "identity_strategy": {
            "curriculum_id_is_mongo_id": False,
            "stable_key_proposal": "trilhacode:{curriculum_ref}",
            "existing_node_lookup": "meta.import_ref; unique index is not currently defined",
            "existing_block_lookup": "owner curriculum ref + block curriculum ref; unique registry/index is not currently defined",
            "mongo_object_id_resolution": "deferred until an authorized read-only snapshot/import stage",
            "order_dependent_identity": False,
        },
        "security": {
            "answer_key_content_included": False,
            "answer_key_refs_included": True,
            "publication_performed": False,
            "progress_written": False,
            "unknown_block_fallback": False,
        },
        "operations_detail": [operation.as_dict() for operation in operations],
        "diagnostics": [
            {
                "code": "DATABASE_SNAPSHOT_NOT_READ",
                "severity": "info",
                "message": "Create/update/unchanged/conflict states require an authorized read-only database snapshot; no database was contacted.",
                "remediation": "A separate approved step must provide a sanitized snapshot before these states can be classified.",
            },
            {
                "code": "LEGACY_IMPORTER_FAILS_CLOSED",
                "severity": "warning",
                "message": "The existing /api/import/track path rejects schema_version bundles; this planner did not invoke it.",
                "remediation": "Implement and approve a dedicated versioned adapter execution path before any import.",
            },
        ],
    }


def canonical_plan_json(plan: Mapping[str, Any]) -> str:
    """Deterministic JSON without timestamps or answer-key content."""
    return json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_plan_exclusive(plan: Mapping[str, Any], output_path: Path) -> None:
    """Write only a new report path; refuse to overwrite any existing file."""
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_plan_json(plan).encode("utf-8")
    try:
        with output_path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
    except FileExistsError:
        raise FileExistsError(f"refusing to overwrite existing dry-run report: {output_path}")
    except Exception:
        try:
            output_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and plan a Trilha Code import bundle offline."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--bundle", type=Path, default=Path("docs/courses/trilhacode/trilha-code-bulk-import.json")
    )
    parser.add_argument(
        "--output", type=Path, help="write a new report file; existing files are never overwritten"
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    bundle_path = args.bundle if args.bundle.is_absolute() else repo_root / args.bundle
    try:
        package = read_and_validate_bundle(bundle_path, repo_root=repo_root)
        plan = build_dry_run_plan(package)
    except AdapterValidationError as exc:
        sys.stderr.write(json.dumps(exc.as_dict(), ensure_ascii=False, indent=2) + "\n")
        return 2
    report = canonical_plan_json(plan)
    if args.output:
        target = args.output if args.output.is_absolute() else repo_root / args.output
        try:
            write_plan_exclusive(plan, target)
        except (OSError, FileExistsError) as exc:
            sys.stderr.write(f"Could not create report: {exc}\n")
            return 2
        sys.stdout.write(f"Dry-run report created: {target.resolve()}\n")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
