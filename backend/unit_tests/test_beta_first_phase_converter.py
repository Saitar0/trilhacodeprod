"""Offline source-backed and strict-contract checks for Beta 4 conversion."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from curriculum_contract.experimental_beta_first_phase_converter import (
    ConvertedUnit,
    FirstPhaseBatch,
    convert_first_phase,
)
from import_payload import validate_import_shape

SOURCE_ROOT = os.environ.get("TRILHACODE_BETA4_SOURCE_ROOT")
pytestmark = pytest.mark.skipif(not SOURCE_ROOT, reason="fonte curricular externa não configurada")


@pytest.fixture(scope="module")
def batch():
    assert SOURCE_ROOT
    return convert_first_phase(Path(SOURCE_ROOT))


def test_full_phase_inventory_and_real_source_counts(batch) -> None:
    manifest = batch.to_manifest()
    assert [unit.provenance.source_id for unit in batch.units] == [
        "1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5",
    ]
    assert manifest["module_count"] == 3
    assert manifest["unit_count"] == 10
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
    assert sum(len(unit.source_artifacts) for unit in batch.units) == 221
    assert batch.conversion_status == "CONVERSION_SUCCESS_WITH_WARNINGS"
    assert manifest["duplicate_generated_ids"] == []


def test_theory_topics_segments_and_project_variation_are_preserved(batch) -> None:
    pilot = batch.units[0]
    assert len(pilot.topics) == 5
    assert sum(len(topic.segments) for topic in pilot.topics) == 8
    assert [topic.order for topic in pilot.topics] == [1, 2, 3, 4, 5]
    assert all(segment.markdown_body.strip() for topic in pilot.topics for segment in topic.segments)
    assert len(batch.units[-1].project_materials) == 11
    assert not batch.units[-1].quiz_questions
    assert not batch.units[-1].manual_exercises
    assert all("project" in field.source.casefold() or "marco" in field.reason.casefold()
               for field in batch.units[-1].field_dispositions
               if field.source == "Brief, marcos e rubricas de projeto")


def test_quiz_answers_are_restricted_and_student_projection_is_redacted(batch) -> None:
    for unit in batch.units:
        for question in unit.quiz_questions:
            student = question.student_projection()
            restricted = question.restricted_projection()
            assert "correct_option_id" not in student
            assert "explanation" not in student
            assert "correct_option_id" in restricted
            assert "explanation" in restricted
            assert question.correct_option_id in {option.id for option in question.options}
    manifest_text = json.dumps(batch.to_manifest(), ensure_ascii=False)
    payload = batch.to_import_payload()
    persisted_prompts = {block["data"].get("prompt") for block in _walk_blocks(payload["nodes"])}
    for unit in batch.units:
        for material in unit.private_materials:
            assert material.content not in manifest_text
        for exercise in unit.manual_exercises:
            assert exercise.grader_reference is None
            assert not exercise.grader_criteria
            assert exercise.student_prompt in persisted_prompts


def test_payload_uses_real_import_shape_and_keeps_draft_private(batch) -> None:
    payload = batch.to_import_payload()
    assert payload["track"]["visibility"] == "private"
    assert payload["track"]["hierarchy"] == ["phase", "module", "submodule", "topic"]
    assert validate_import_shape(payload) == []
    assert all(node["status"] == "draft" for node in _walk_nodes(payload["nodes"]))
    assert all(block["status"] == "draft" for block in _walk_blocks(payload["nodes"]))
    assert not any("criterion" in block["data"] for block in _walk_blocks(payload["nodes"]))
    assert not any("rubric" in block["data"] or "answer" in block["data"]
                   for block in _walk_blocks(payload["nodes"]))


def test_conversion_is_deterministic_and_manifest_aggregates_unit_manifests(batch) -> None:
    second = convert_first_phase(Path(SOURCE_ROOT))
    first_payload = batch.to_import_payload()
    second_payload = second.to_import_payload()
    first_manifest = batch.to_manifest()
    second_manifest = second.to_manifest()
    assert first_payload == second_payload
    assert first_manifest == second_manifest
    assert first_manifest["canonical_manifest_sha256"]
    for unit in batch.units:
        assert len(unit.provenance.source_sha256) == 64
        assert len(unit.provenance.source_sha256_lf) == 64
        for artifact in unit.source_artifacts:
            source_file = Path(SOURCE_ROOT) / artifact.relative_path
            source_text = source_file.read_bytes().decode("utf-8-sig", errors="strict")
            normalized = source_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
            assert artifact.sha256 == hashlib.sha256(source_file.read_bytes()).hexdigest()
            assert artifact.sha256_lf == hashlib.sha256(normalized).hexdigest()
    for key in first_manifest["counts"]:
        assert first_manifest["counts"][key] == sum(
            unit["counts"][key] for unit in first_manifest["units"]
        )


def test_contract_rejects_duplicate_or_missing_unit_identity(batch) -> None:
    first = batch.units[0]
    with pytest.raises(ValidationError):
        ConvertedUnit.model_validate({**first.model_dump(), "unexpected": "value"})
    with pytest.raises(ValidationError):
        FirstPhaseBatch.model_validate({
            **batch.model_dump(), "units": [first.model_dump(), first.model_dump()],
        })


def _walk_nodes(nodes: list[dict]):
    for node in nodes:
        yield node
        yield from _walk_nodes(node.get("children", []))


def _walk_blocks(nodes: list[dict]):
    for node in _walk_nodes(nodes):
        yield from node.get("blocks", [])
