import ast
import asyncio
import hashlib
import json
import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from curriculum_contract.beta_staging_contract import (
    CompletionRule,
    StagedRecord,
    StagedRecordKind,
    StagingContractError,
    StagingManifest,
    StagingPackage,
    _package_content_hash,
    staging_package_from_first_phase,
)
from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase
from services.beta_curriculum_staging import CurriculumStagingService, StagingError


def test_staged_public_records_reject_reserved_keys_and_unknown_metadata():
    with pytest.raises(ValidationError):
        StagedRecord(
            record_id="quiz:synthetic:q1",
            kind=StagedRecordKind.QUIZ_QUESTION,
            student_public={
                "question_id": "q1",
                "order": 1,
                "topic_id": None,
                "prompt": "SYNTHETIC",
                "options": [{"id": "a", "label": "A", "correct_option_id": "a"}],
                "schema_version": 1,
            },
            system_internal={"source_revision": "synthetic"},
        )
    with pytest.raises(ValidationError):
        StagedRecord(
            record_id="quiz:synthetic:q2",
            kind=StagedRecordKind.QUIZ_QUESTION,
            student_public={
                "question_id": "q2", "order": 1, "prompt": "SYNTHETIC",
                "options": [{"id": "a", "label": "A", "correctOptionId": "a"}],
                "schema_version": 1,
            },
            system_internal={"source_revision": "synthetic"},
        )
    with pytest.raises(ValidationError):
        StagedRecord(
            record_id="unit:synthetic",
            kind=StagedRecordKind.UNIT,
            student_public={"unit_id": "synthetic", "gabarito": "SYNTHETIC PRIVATE"},
            system_internal={"source_revision": "synthetic"},
        )


def test_package_hash_and_manifest_are_validated_before_persistence():
    with pytest.raises(ValidationError):
        StagingPackage.model_validate({
            "manifest": {
                "batch_id": "beta5-" + "a" * 32,
                "source_revision": "synthetic",
                "source_manifest_sha256": "a" * 64,
                "payload_sha256": "b" * 64,
                "contract_version": "synthetic/1",
                "converter_version": "synthetic/1",
                "unit_ids": ["1.synthetic"],
                "record_count": 1,
                "project_artifact_count": 0,
                "warning_count": 0,
            },
            "records": [{
                "record_id": "unit:1.synthetic",
                "kind": "unit",
                "student_public": {"unit_id": "1.synthetic"},
                "system_internal": {"source_revision": "synthetic"},
            }],
        })


def test_actual_beta4_sources_preserve_all_units_project_artifacts_and_privacy():
    source_root = os.environ.get("BETA5_CURRICULUM_SOURCE")
    if not source_root:
        pytest.skip("fonte curricular autorizada não foi fornecida para este teste offline")
    batch = convert_first_phase(Path(source_root))
    beta4_manifest = json.loads(
        (Path(__file__).parents[2] / "docs" / "beta" / "beta4-first-phase-manifest.json").read_text(encoding="utf-8")
    )
    current = batch.to_manifest()
    expected = {item["unit_id"]: item for item in beta4_manifest["units"]}
    for unit in current["units"]:
        assert unit["source_artifacts"] == expected[unit["unit_id"]]["source_artifacts"]
        assert unit["source"]["source_sha256"] == expected[unit["unit_id"]]["source"]["source_sha256"]

    package = staging_package_from_first_phase(batch)
    incompatible = batch.model_copy(update={"converter_version": "unknown/future"})
    with pytest.raises(StagingContractError, match="não compatível"):
        staging_package_from_first_phase(incompatible)
    assert package.manifest.unit_ids == tuple(item.provenance.source_id for item in batch.units)
    assert package.manifest.project_artifact_count == 11
    assert package.manifest.record_count == len(package.records)
    assert package.manifest.private_payloads_in_manifest is False
    repeated = staging_package_from_first_phase(convert_first_phase(Path(source_root)))
    assert repeated.model_dump(mode="json") == package.model_dump(mode="json")
    assert repeated.manifest.payload_sha256 == package.manifest.payload_sha256
    assert len(package.projects) == 1 and package.projects[0].project_id == "3.5"
    project_records = [item for item in package.records if item.kind == StagedRecordKind.PROJECT_ARTIFACT]
    assert len(project_records) == 11
    assert all(item.student_projection().keys() == {"id", "kind"} for item in project_records)
    project_contracts = [item for item in package.records if item.kind == StagedRecordKind.PROJECT_PACKAGE]
    assert len(project_contracts) == 1
    assert project_contracts[0].student_projection().keys() == {"id", "kind"}

    public_quizzes = [record.student_projection() for record in package.records if record.kind == StagedRecordKind.QUIZ_QUESTION]
    assert len(public_quizzes) == 44
    assert all("correct_option_id" not in json.dumps(item) for item in public_quizzes)
    assert all(
        "raw_source_body" in record.system_internal
        for record in package.records if record.kind == StagedRecordKind.SOURCE_ARTIFACT
    )
    beta5_path = Path(__file__).parents[2] / "docs" / "beta" / "beta5-first-phase-manifest.json"
    beta5_manifest = json.loads(beta5_path.read_text(encoding="utf-8"))
    manifest_hash = beta5_manifest.pop("manifest_sha256")
    canonical = json.dumps(beta5_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == manifest_hash
    assert beta5_manifest["batch_id"] == package.manifest.batch_id
    assert beta5_manifest["payload_sha256"] == package.manifest.payload_sha256
    assert beta5_manifest["counts"] == current["counts"]
    assert beta5_manifest["unit_count"] == len(batch.units)
    assert beta5_manifest["project_artifact_count"] == 11
    assert beta5_manifest["private_payloads_in_manifest"] is False
    assert "correct_option_id" not in json.dumps(beta5_manifest)
    assert "raw_source_body" not in json.dumps(beta5_manifest)


def _minimal_package() -> StagingPackage:
    record = StagedRecord(
        record_id="unit:synthetic",
        kind=StagedRecordKind.UNIT,
        student_public={"unit_id": "synthetic"},
        system_internal={"source_revision": "synthetic"},
    )
    records = (record,)
    projects = ()
    criteria: tuple[CompletionRule, ...] = ()
    references = ()
    relations = ()
    warnings = ()
    payload_hash = _package_content_hash(records, projects, criteria, references, relations, warnings)
    manifest = StagingManifest(
        batch_id=f"beta5-{payload_hash[:32]}",
        source_revision="synthetic",
        source_manifest_sha256="a" * 64,
        payload_sha256=payload_hash,
        contract_version="synthetic/1",
        converter_version="synthetic/1",
        unit_ids=("synthetic",),
        record_count=1,
        project_artifact_count=0,
        warning_count=0,
    )
    return StagingPackage(manifest=manifest, records=records)


def test_staging_refuses_wrong_database_name_or_missing_owner_marker_before_writes():
    run_id = "b" * 32
    owner_token = "owner-token-" + "z" * 40

    class Collection:
        def __init__(self, marker):
            self.marker = marker
            self.writes = 0

        async def find_one(self, _query):
            return self.marker

        async def create_index(self, *_args, **_kwargs):
            self.writes += 1

    class Database:
        def __init__(self, name, marker):
            self.name = name
            self.marker = marker
            self.collections = {}

        def __getitem__(self, collection_name):
            return self.collections.setdefault(collection_name, Collection(self.marker))

    with pytest.raises(ValueError, match="banco exclusivo"):
        CurriculumStagingService(
            Database("trilhacode", None), execution_id=run_id, owner_token=owner_token,
        )

    database = Database(f"beta5_{run_id}", {"_id": "owner", "run_id": run_id, "owner_token": "wrong"})
    service = CurriculumStagingService(database, execution_id=run_id, owner_token=owner_token)
    with pytest.raises(StagingError, match="marcador de propriedade"):
        asyncio.run(service.prepare(_minimal_package()))
    assert all(collection.writes == 0 for collection in database.collections.values())


def test_same_batch_identity_cannot_be_reused_for_different_payload():
    package = _minimal_package()
    changed_record = package.records[0].model_copy(update={
        "student_public": {"unit_id": "different-synthetic-unit"},
    })
    changed_records = (changed_record,)
    new_hash = _package_content_hash(
        changed_records, package.projects, package.completion_criteria,
        package.references, package.relations, package.warnings,
    )
    altered = package.model_dump(mode="python")
    altered["records"] = changed_records
    altered["manifest"]["payload_sha256"] = new_hash
    # Keep the former batch ID. Validation rejects before any database handle exists.
    with pytest.raises(ValidationError, match="derivar do hash canônico"):
        StagingPackage.model_validate(altered)


def test_staging_service_has_no_operational_database_reader_or_promotion_imports():
    source_path = Path(__file__).parents[1] / "services" / "beta_curriculum_staging.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden_import_roots = {"database", "routes_content", "server", "startup", "workers"}
    assert imported.isdisjoint(forbidden_import_roots)
    assert "get_track_tree" not in source_path.read_text(encoding="utf-8")
    assert "get_node" not in source_path.read_text(encoding="utf-8")
    assert "PUBLISHED" not in source_path.read_text(encoding="utf-8")
