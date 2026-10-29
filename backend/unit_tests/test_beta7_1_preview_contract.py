from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase
from services.beta7_1_preview import _quiz_receipt, public_project_projection, public_unit
from test_support.beta5_mongo_target import MongoTargetError
from test_support.beta7_1_internal_target import validate_internal_target

SOURCE_ROOT = os.environ.get("TRILHACODE_BETA4_SOURCE_ROOT", "")


def _batch():
    if not SOURCE_ROOT:
        pytest.skip("Fonte Beta 4 não foi montada em modo somente leitura")
    return convert_first_phase(Path(SOURCE_ROOT), source_revision="migration@147dc68:tracked-clean-first-phase-files")


def test_all_real_units_keep_structural_counts_and_stable_source_hashes():
    batch = _batch()
    manifest = batch.to_manifest()
    assert len(batch.units) == 10
    assert manifest["module_count"] == 3
    assert manifest["counts"] == {
        "topics": 30,
        "theory_segments": 42,
        "quiz_files": 30,
        "quiz_questions": 44,
        "manual_exercises": 26,
        "project_materials": 11,
        "references": 39,
        "relations": 30,
        "persisted_blocks": 161,
    }
    assert len({unit.provenance.source_sha256 for unit in batch.units}) == 10
    assert len({unit.provenance.source_id for unit in batch.units}) == 10


def test_student_unit_projection_preserves_structure_without_private_assessment_data():
    batch = _batch()
    projected = [public_unit(unit) for unit in batch.units]
    assert sum(len(unit["topics"]) for unit in projected) == 30
    assert sum(len(topic["segments"]) for unit in projected for topic in unit["topics"]) == 42
    assert sum(len(unit["quizzes"]) for unit in projected) == 44
    assert sum(len(unit["exercises"]) for unit in projected) == 26

    serialized = json.dumps(projected, ensure_ascii=False)
    for forbidden in (
        "correct_option_id", "reference_answer", "restricted_content", "private_materials",
        "internal_content", "rubric", "answer_key", "explanation",
    ):
        assert forbidden not in serialized
    for unit in batch.units:
        for material in unit.private_materials:
            assert material.content not in serialized
        public = next(row for row in projected if row["id"] == unit.provenance.source_id)
        assert [question["order"] for question in public["quizzes"]] == list(range(1, len(public["quizzes"]) + 1))


def test_project_projection_defaults_pending_materials_to_deny():
    unit = next(row for row in _batch().units if row.provenance.source_id == "3.5")
    projection = public_project_projection(unit)
    assert len(projection["artifacts"]) == 1
    assert projection["completion"] == "BLOCKED_BY_PEDAGOGICAL_REVIEW"
    assert sum(item["kind"] == "project_brief" and item["content"] is not None for item in projection["artifacts"]) == 1
    serialized = str(projection).casefold()
    assert "rubric" not in serialized
    assert "rubrica" not in serialized
    assert "checklist" not in serialized
    assert "milestone" not in serialized
    assert not any(item["content"] in {material.content for material in unit.private_materials}
                   for item in projection["artifacts"] if item["content"])


def test_quiz_receipt_does_not_expose_answer_or_explanation():
    receipt = _quiz_receipt({
        "_id": "receipt", "unit_id": "1.1", "question_id": "question-1",
        "source_sha256": "a" * 64, "is_correct": True,
        "created_at": __import__("datetime").datetime(2026, 1, 1),
        "correct_option_id": "secret-option", "explanation": "private explanation",
    })
    assert receipt["state"] == "ANSWERED"
    assert receipt["feedback_state"] == "PENDING_PEDAGOGICAL_POLICY"
    assert "is_correct" not in receipt
    assert "correct_option_id" not in receipt
    assert "explanation" not in receipt


def _valid_target_env() -> dict[str, str]:
    run_id = "a" * 32
    return {
        "BETA7_1_TEST_ISOLATION_GATE": "beta7-1:" + "b" * 64,
        "BETA7_1_TEST_MONGO_URI": f"mongodb://beta7_1_{run_id[:10]}:{'c' * 64}@tc-beta7-1-mongo-{run_id[:12]}:27017/beta7_1_{run_id}?authSource=admin&replicaSet=rs0",
        "BETA7_1_TEST_MONGO_DATABASE": f"beta7_1_{run_id}",
        "BETA7_1_TEST_RUN_ID": run_id,
        "BETA7_1_TEST_OWNER_TOKEN": "d" * 64,
        "BETA7_1_TEST_CONTAINER_ID": "e" * 64,
        "BETA7_1_TEST_NETWORK_ID": "f" * 64,
        "BETA7_1_TEST_RUNNER_ID": "1" * 64,
        "BETA7_1_TEST_MONGO_HOST": f"tc-beta7-1-mongo-{run_id[:12]}",
        "BETA7_1_TEST_NETWORK_NAME": f"tc-beta7-1-{run_id[:12]}",
        "BETA7_1_TEST_RUNNER_NAME": f"tc-beta7-1-runner-{run_id[:12]}",
    }


def test_internal_target_requires_full_owned_disposable_identity():
    environment = _valid_target_env()
    target = validate_internal_target(environment)
    assert target.database == environment["BETA7_1_TEST_MONGO_DATABASE"]
    assert target.phase == "beta7-1"
    for name, value in (
        ("BETA7_1_TEST_MONGO_URI", ""),
        ("BETA7_1_TEST_OWNER_TOKEN", "missing"),
        ("BETA7_1_TEST_RUNNER_ID", "bad"),
    ):
        invalid = dict(environment, **{name: value})
        with pytest.raises(MongoTargetError):
            validate_internal_target(invalid)


def test_internal_target_rejects_loopback_or_mismatched_credentials():
    environment = _valid_target_env()
    environment["BETA7_1_TEST_MONGO_URI"] = environment["BETA7_1_TEST_MONGO_URI"].replace(
        environment["BETA7_1_TEST_MONGO_HOST"], "127.0.0.1",
    )
    with pytest.raises(MongoTargetError):
        validate_internal_target(environment)


def test_preview_is_not_mounted_by_operational_app():
    source = (Path(__file__).parents[1] / "server.py").read_text(encoding="utf-8")
    assert "beta7_1_preview_router" not in source
    assert "beta7-1/preview" not in source
