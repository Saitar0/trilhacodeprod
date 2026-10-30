"""Offline tests for the lossless ten-phase import bundle serializer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from curriculum_contract.bulk_import import (
    BULK_IMPORT_SCHEMA,
    build_import_bundle,
    canonical_import_bundle_json,
    validate_import_bundle_json,
)
from import_payload import validate_import_shape

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_full_bundle_contains_all_ten_phases_and_approved_counts() -> None:
    bundle = build_import_bundle(REPO_ROOT)
    payload = bundle.model_dump(mode="json")

    assert payload["schema_version"] == BULK_IMPORT_SCHEMA
    assert len(payload["phases"]) == 10
    assert sum(len(phase["contract"]["nodes"]) for phase in payload["phases"]) == 572
    assert sum(len(phase["contract"]["blocks"]) for phase in payload["phases"]) == 3431
    assert sum(len(phase["contract"]["projects"]) for phase in payload["phases"]) == 15
    assert sum(len(phase["contract"]["shared_placements"]) for phase in payload["phases"]) == 1001
    assert sum(len(phase["contract"]["relations"]) for phase in payload["phases"]) == 55
    assert payload["integrity"]["global_counts"]["unique_entity_ids"] == 5344
    assert len(payload["source_mappings"]["mappings"]) == 2889
    assert len(payload["diagnostics"]["diagnostics"]) == 1225
    assert len(payload["structural_artifacts"]) == 1
    assert len(payload["integrity"]["artifact_sha256"]) == 12


def test_unmapped_structural_file_is_preserved_literally() -> None:
    bundle = build_import_bundle(REPO_ROOT)
    artifact = bundle.structural_artifacts[0]
    source = REPO_ROOT / artifact.path

    assert (
        artifact.path == "docs/courses/trilhacode/Conteudos_migrado/Fase_2/Projeto_incremental.md"
    )
    assert artifact.content.encode("utf-8") == source.read_bytes()


def test_bundle_serialization_is_deterministic_when_phase_read_order_changes() -> None:
    forward = build_import_bundle(REPO_ROOT, phase_order=list(range(1, 11)))
    reverse = build_import_bundle(REPO_ROOT, phase_order=list(range(10, 0, -1)))

    assert canonical_import_bundle_json(forward) == canonical_import_bundle_json(reverse)


def test_persisted_bundle_round_trips_through_strict_schema() -> None:
    serialized = canonical_import_bundle_json(build_import_bundle(REPO_ROOT))
    restored = validate_import_bundle_json(serialized)

    assert restored.schema_version == BULK_IMPORT_SCHEMA
    assert [phase.phase for phase in restored.phases] == list(range(1, 11))


def test_legacy_importer_fails_closed_on_versioned_bundle() -> None:
    bundle = json.loads(canonical_import_bundle_json(build_import_bundle(REPO_ROOT)))

    diagnostics = validate_import_shape(bundle)

    assert any(item["path"] == "schema_version" for item in diagnostics)
    assert any("evitar importação parcial" in item["message"] for item in diagnostics)


def test_bundle_builder_rejects_unverified_legacy_json(tmp_path: Path) -> None:
    # A legacy-shaped file is accepted only when it is the exact verified source.
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps({"track": {}, "options": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="legacy import JSON differs"):
        build_import_bundle(REPO_ROOT, legacy_json_path=changed)


def test_bundle_builder_rejects_changed_versioned_track_metadata(tmp_path: Path) -> None:
    payload = json.loads(canonical_import_bundle_json(build_import_bundle(REPO_ROOT)))
    payload["track"]["title"] = "Changed title"
    changed = tmp_path / "changed-versioned.json"
    changed.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="track/options differ"):
        build_import_bundle(REPO_ROOT, legacy_json_path=changed)


def test_bundle_builder_reproduces_from_its_versioned_output(tmp_path: Path) -> None:
    first = build_import_bundle(REPO_ROOT)
    persisted = tmp_path / "bundle.json"
    persisted.write_text(canonical_import_bundle_json(first), encoding="utf-8")

    reproduced = build_import_bundle(REPO_ROOT, legacy_json_path=persisted)

    assert canonical_import_bundle_json(reproduced) == canonical_import_bundle_json(first)
