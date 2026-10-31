"""Offline contract tests for the narrow Beta 2 pilot converter."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_beta_curriculum_converter import (  # noqa: E402
    CurriculumConversionError,
    convert_markdown_unit,
)
from import_payload import validate_import_shape  # noqa: E402
from services.activity_publications import normalize_quiz, public_activity  # noqa: E402
from services.nodes import _student_block  # noqa: E402

FIXTURE = BACKEND / "integration_tests" / "fixtures" / "beta2" / "unit_1_1_computacao_e_software.source.md"
SOURCE_PATH = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
SOURCE_REVISION = "migracao@147dc68:tracked-clean-file"


def convert(source: bytes | str | None = None):
    content = FIXTURE.read_bytes() if source is None else source
    return convert_markdown_unit(
        content, source_path=SOURCE_PATH, source_revision=SOURCE_REVISION,
    )


def test_real_unit_preserves_curriculum_structure_and_source_fingerprint():
    original = FIXTURE.read_bytes()
    unit = convert(original)
    manifest = unit.to_manifest()

    assert unit.source_id == "1.1"
    assert unit.title == "1.1 — Computação e software"
    assert "Ao final" in unit.objective
    assert "Frontend, backend e banco de dados" in unit.theory
    assert "DNS ajuda a localizar" in unit.summary
    assert len(unit.quiz) == 5
    assert unit.quiz[0].correct_letter == "B"
    assert "Programa descreve instruções" in unit.quiz[0].explanation
    assert len(unit.exercises) == 3
    assert unit.exercises[0].instructor_reference
    assert unit.exercises[1].criteria
    assert len(unit.references) == 2
    assert "sem consultar o material" in unit.completion_criteria.lower()
    assert "Conexões" in unit.raw_sections
    assert manifest["source"]["sha256_raw"] == hashlib.sha256(original).hexdigest()
    assert manifest["no_source_write"] is True
    assert FIXTURE.read_bytes() == original
    assert any(item["status"].startswith("withheld") for item in manifest["field_mappings"])
    assert unit.completion_criteria not in repr(manifest)


def test_payload_is_deterministic_draft_only_and_explicit_about_unmapped_data():
    first, second = convert(), convert()
    assert first.to_import_payload() == second.to_import_payload()
    assert first.to_manifest() == second.to_manifest()

    payload = first.to_import_payload()
    node = payload["nodes"][0]
    assert payload["track"]["hierarchy"] == ["phase", "module", "submodule", "topic"]
    assert payload["track"]["visibility"] == "private"
    assert node["status"] == "draft"
    assert all(block["status"] == "draft" for block in node["blocks"])
    assert node["description"] == first.objective
    assert node["pedagogical_type"] == "integrado"
    assert node["requirement"] == "obrigatorio"
    assert node["depth"] == "media"
    assert [block["type"] for block in node["blocks"]] == [
        "theory_text", "summary", "quiz", "quiz", "quiz", "quiz", "quiz",
        "exercise_open", "exercise_open", "exercise_open", "reference", "reference",
    ]
    serialized = repr(payload)
    assert first.exercises[0].instructor_reference not in serialized
    assert "completion_criteria" not in node
    assert any("completion_criteria" in item for item in first.unsupported_destinations)
    assert any("instructor_reference" in item for item in first.unsupported_destinations)
    assert not any("frontmatter." in item for item in first.unsupported_destinations)
    assert validate_import_shape(payload) == []


def test_versioned_quiz_contract_keeps_answer_out_of_student_read_models():
    source_quiz = next(
        block for block in convert().to_import_payload()["nodes"][0]["blocks"]
        if block["type"] == "quiz"
    )
    source_quiz["_id"] = "synthetic-quiz-id"
    private_definition = normalize_quiz(source_quiz, "synthetic-published-version", 1)
    assert private_definition is not None
    public_definition = public_activity(private_definition)
    public_block = _student_block(source_quiz)

    assert "correct_option_id" not in public_definition
    assert "feedback" not in public_definition
    assert "correct_option_id" not in public_block["data"]
    assert "feedback" not in public_block["data"]
    assert public_definition["options"] == source_quiz["data"]["options"]


def test_unknown_sections_are_retained_and_reported():
    raw = FIXTURE.read_text(encoding="utf-8")
    augmented = raw.replace("## Referências\n", "## Nota experimental\n\nTexto sem destino.\n\n## Referências\n", 1)
    unit = convert(augmented)
    assert unit.raw_sections["Nota experimental"] == "Texto sem destino."
    assert any("Nota experimental" in warning for warning in unit.warnings)


@pytest.mark.parametrize("source_path", ["../private.md", "/absolute.md", "docs\\unit.md", ""])
def test_source_path_must_be_relative_posix_and_normalized(source_path: str):
    with pytest.raises(CurriculumConversionError):
        convert_markdown_unit(FIXTURE.read_bytes(), source_path=source_path, source_revision="rev")


def test_missing_required_section_and_duplicate_question_fail_closed():
    raw = FIXTURE.read_text(encoding="utf-8")
    missing = raw.replace("## Resumo\n", "## Visão geral\n", 1)
    with pytest.raises(CurriculumConversionError, match="seções obrigatórias ausentes"):
        convert(missing)

    duplicate = raw.replace(
        "5. Uma API web pode usar HTTP.",
        "1. Questão duplicada.\n   - A. Uma alternativa.\n   - B. Outra alternativa.\n\n5. Uma API web pode usar HTTP.",
        1,
    )
    with pytest.raises(CurriculumConversionError, match="questões e gabarito|duplicado"):
        convert(duplicate)
