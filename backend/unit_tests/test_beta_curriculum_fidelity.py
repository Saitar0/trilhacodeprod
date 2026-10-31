"""Offline fidelity and privacy contract tests for the Beta 3 pilot."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_beta_curriculum_converter import (  # noqa: E402
    convert_markdown_unit,
)
from curriculum_contract.experimental_beta_curriculum_fidelity import (  # noqa: E402
    CurriculumFidelityUnit,
    convert_fidelity_unit,
)
from import_payload import validate_import_shape  # noqa: E402
from services.activity_publications import (  # noqa: E402
    ActivityDefinitionError,
    normalize_quiz,
    public_activity,
)
from services.nodes import _student_block  # noqa: E402

FIXTURE = BACKEND / "integration_tests" / "fixtures" / "beta2" / "unit_1_1_computacao_e_software.source.md"
SOURCE_PATH = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
SOURCE_REVISION = "migracao@147dc68:tracked-clean-file"
SOURCE_SHA256 = "db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4"


def convert(source: bytes | str | None = None):
    content = FIXTURE.read_bytes() if source is None else source
    return convert_fidelity_unit(
        content,
        source_path=SOURCE_PATH,
        source_revision=SOURCE_REVISION,
        expected_source_sha256=SOURCE_SHA256,
    )


def test_preserves_five_topics_eight_sections_and_exact_source_order() -> None:
    raw = FIXTURE.read_bytes()
    pilot = convert_markdown_unit(raw, source_path=SOURCE_PATH, source_revision=SOURCE_REVISION)
    unit = convert(raw)
    segments = [segment for topic in unit.topics for segment in topic.segments]

    assert unit.title == "1.1 — Computação e software"
    assert unit.objective == pilot.objective
    assert unit.summary == pilot.summary
    assert unit.provenance.source_revision == SOURCE_REVISION
    assert unit.provenance.source_sha256_lf == (
        "21736a209b840406169d88862f793e848952a402a01a37ae22d974d7bd59e513"
    )
    assert len(unit.topics) == 5
    assert len(segments) == 8
    assert [segment.source_heading for segment in segments] == [
        "Do problema ao programa",
        "Aplicações locais e aplicações web",
        "Frontend, backend e banco de dados",
        "Cliente e servidor",
        "O que acontece ao abrir uma página",
        "Requisição e resposta HTTP",
        "APIs: uma interface de comunicação",
        "Uma visão integrada",
    ]
    assert "".join(segment.source_markdown for segment in segments) == pilot.theory
    assert [topic.order for topic in unit.topics] == [1, 2, 3, 4, 5]
    assert all(segment.markdown_body for segment in segments)
    assert all(segment.source_sha256 == hashlib.sha256(segment.source_markdown.encode()).hexdigest()
               for segment in segments)


def test_preserves_five_quiz_items_and_restricts_answer_projection() -> None:
    unit = convert()
    source = convert_markdown_unit(FIXTURE.read_bytes(), source_path=SOURCE_PATH,
                                   source_revision=SOURCE_REVISION)
    assert len(unit.quiz_questions) == len(source.quiz) == 5
    for question, original in zip(unit.quiz_questions, source.quiz, strict=True):
        assert question.prompt == original.prompt
        assert [option.label for option in question.options] == [label for _, label in original.options]
        assert question.correct_option_id.endswith(original.correct_letter.lower())
        assert question.explanation == original.explanation
        student = question.student_projection()
        restricted = question.restricted_projection()
        assert "correct_option_id" not in student and "explanation" not in student
        assert restricted["correct_option_id"] == question.correct_option_id
        assert restricted["explanation"] == question.explanation

        block = next(item for item in unit.to_import_payload()["nodes"][0]["blocks"]
                     if item["ref"] == question.ref)
        block["_id"] = "synthetic-quiz"
        private_definition = normalize_quiz(block, "draft-only-test", 1)
        assert private_definition is not None
        public = public_activity(private_definition)
        public_block = _student_block(block)
        assert "correct_option_id" not in public
        assert "feedback" not in public
        assert "correct_option_id" not in public_block["data"]
        assert "feedback" not in public_block["data"]
        corrupted = {**block, "data": {**block["data"], "untrusted-secret": "answer-leak"}}
        with pytest.raises(ActivityDefinitionError) as invalid:
            normalize_quiz(corrupted, "draft-only-test", 1)
        assert "answer-leak" not in str(invalid.value)


def test_preserves_three_manual_exercises_without_persisting_grader_secrets() -> None:
    unit = convert()
    parsed = convert_markdown_unit(FIXTURE.read_bytes(), source_path=SOURCE_PATH,
                                   source_revision=SOURCE_REVISION)
    assert len(unit.manual_exercises) == len(parsed.exercises) == 3
    payload = unit.to_import_payload()
    exercise_blocks = [block for block in payload["nodes"][0]["blocks"]
                       if block["type"] == "exercise_open"]
    assert len(exercise_blocks) == 3
    for exercise, original, block in zip(unit.manual_exercises, parsed.exercises,
                                         exercise_blocks, strict=True):
        assert exercise.student_prompt == original.student_prompt
        assert exercise.grader_reference == original.instructor_reference
        assert exercise.grader_criteria == original.criteria
        assert block["data"] == {"prompt": exercise.student_prompt, "grading": "manual"}
        student = exercise.student_projection()
        grader = exercise.restricted_projection()
        assert "reference_answer" not in student and "criteria" not in student
        assert grader["reference_answer"] == exercise.grader_reference
        assert grader["criteria"] == list(exercise.grader_criteria)


def test_completion_relations_reference_descriptions_and_losses_are_explicit() -> None:
    unit = convert()
    manifest = unit.to_manifest()
    assert unit.completion_criterion.source_text
    assert unit.completion_criterion.automated_rule is None
    assert unit.completion_criterion.requires_human_policy_decision is True
    assert len(unit.relations) == 3
    assert all(not relation.enforced and relation.target_node_ref is None for relation in unit.relations)
    assert len(unit.references) == 2
    assert all(reference.title and reference.description and reference.url for reference in unit.references)
    assert any("critério de conclusão" in item["source"].lower()
               for item in manifest["field_dispositions"])
    assert any("descrição" in item["source"].lower()
               and item["status"] == "REQUIRES_ADAPTER"
               for item in manifest["field_dispositions"])
    assert manifest["destination"]["block_counts"] == {
        "theory_text": 8, "summary": 1, "quiz": 5, "exercise_open": 3, "reference": 2,
    }


def test_conversion_manifest_and_ids_are_deterministic_and_import_shape_valid() -> None:
    first, second = convert(), convert()
    payload = first.to_import_payload()
    manifest = first.to_manifest()
    assert payload == second.to_import_payload()
    assert manifest == second.to_manifest()
    assert manifest["source"]["source_sha256"] == hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert len(manifest["destination"]["payload_sha256"]) == 64
    assert validate_import_shape(payload) == []
    refs = [block["ref"] for block in payload["nodes"][0]["blocks"]]
    assert len(refs) == len(set(refs)) == 19
    assert payload["nodes"][0]["tags"] == ["fundamentos", "web"]
    assert payload["nodes"][0]["estimated_minutes"] == 90
    assert payload["nodes"][0]["pedagogical_type"] == "integrado"
    assert payload["nodes"][0]["requirement"] == "obrigatorio"
    assert payload["nodes"][0]["depth"] == "media"
    assert payload["track"]["visibility"] == "private"
    assert payload["nodes"][0]["status"] == "draft"
    assert all(block["status"] == "draft" for block in payload["nodes"][0]["blocks"])
    assert "grader_reference" not in json.dumps(payload, ensure_ascii=False)
    assert "grader_criteria" not in json.dumps(payload, ensure_ascii=False)


def test_source_hash_drift_and_unknown_heading_fail_or_report_without_silent_loss() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        convert(FIXTURE.read_bytes() + b"\n")

    raw = FIXTURE.read_text(encoding="utf-8")
    augmented = raw.replace("## Referências\n", "## Nota experimental\n\nExtra sem destino.\n\n## Referências\n", 1)
    unit = convert_fidelity_unit(
        augmented, source_path=SOURCE_PATH, source_revision=SOURCE_REVISION,
        expected_source_sha256=hashlib.sha256(augmented.encode("utf-8")).hexdigest(),
    )
    manifest = unit.to_manifest()
    assert unit.unmapped_sections == (("Nota experimental", "Extra sem destino."),)
    assert any(item["name"] == "Nota experimental" and not item["included_in_import_payload"]
               for item in manifest["unmapped_sections"])
    assert any("Nota experimental" in item["source"] for item in manifest["field_dispositions"])
    assert "Extra sem destino." not in json.dumps(manifest, ensure_ascii=False)


def test_pydantic_contract_rejects_unknown_fields_and_duplicate_question_ids() -> None:
    unit = convert()
    with pytest.raises(ValidationError) as error:
        type(unit).model_validate({**unit.model_dump(), "client_capability": "private-answer-secret"})
    assert "private-answer-secret" not in str(error.value)

    model = unit.model_dump()
    model["quiz_questions"][1]["ref"] = model["quiz_questions"][0]["ref"]
    with pytest.raises(ValidationError, match="IDs de conteúdo duplicados"):
        CurriculumFidelityUnit.model_validate(model)

    model = unit.model_dump()
    model["quiz_questions"][0]["topic_ref"] = "missing-topic"
    with pytest.raises(ValidationError, match="questão referencia tópico inexistente"):
        CurriculumFidelityUnit.model_validate(model)


def test_original_beta2_fixture_is_not_modified() -> None:
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == SOURCE_SHA256
