from __future__ import annotations

import sys
from pathlib import Path

import pytest

from curriculum_contract.beta_staging_contract import (
    StagedRecord,
    StagedRecordKind,
    StagingManifest,
    StagingPackage,
    _package_content_hash,
)
from services.beta8_1_staging_authority import (
    Beta8_1StagingAuthorityBridge,
    StagingAuthorityError,
)


def _package(*, source_revision: str = "synthetic:beta8-1:revision-1") -> StagingPackage:
    records = (
        StagedRecord(
            record_id="synthetic-unit-1",
            kind=StagedRecordKind.UNIT,
            student_public={"unit_id": "synthetic-unit-1", "title": "Synthetic unit"},
            system_internal={
                "source_revision": source_revision,
                "source_path": "synthetic://beta8-1/unit",
                "source_sha256": "a" * 64,
            },
        ),
    )
    payload_hash = _package_content_hash(records, (), (), (), (), ())
    manifest = StagingManifest(
        batch_id=f"beta5-{payload_hash[:32]}",
        source_revision=source_revision,
        source_manifest_sha256="b" * 64,
        payload_sha256=payload_hash,
        contract_version="synthetic/beta8-1/1",
        converter_version="synthetic/beta8-1/1",
        unit_ids=("synthetic-unit-1",),
        record_count=1,
        project_artifact_count=0,
        warning_count=0,
    )
    return StagingPackage(manifest=manifest, records=records)


def test_runtime_iam_import_is_inert_until_explicit_use() -> None:
    import services.beta8_1_runtime_iam  # noqa: F401

    assert "database" not in sys.modules
    assert "security" not in sys.modules


def test_staging_candidate_binds_complete_payload_hash() -> None:
    bridge = Beta8_1StagingAuthorityBridge(None, None, track_id="beta8-track-synthetic-test")
    package = _package()

    candidate = bridge.candidate_for(package)

    assert candidate.source_revision == f"synthetic:stage:{package.manifest.payload_sha256}"
    assert candidate.source_revision.endswith(package.manifest.payload_sha256)


def test_staging_candidate_rejects_non_synthetic_source() -> None:
    bridge = Beta8_1StagingAuthorityBridge(None, None, track_id="beta8-track-synthetic-test")

    with pytest.raises(StagingAuthorityError):
        bridge.candidate_for(_package(source_revision="curriculum:phase-1:revision-1"))


def test_normal_server_startup_does_not_install_preview_capability() -> None:
    backend = Path(__file__).resolve().parents[1]
    server_source = (backend / "server.py").read_text(encoding="utf-8")

    assert "beta8_1_editorial_runtime" not in server_source
    assert "Beta8_1EditorialRuntime" not in server_source
