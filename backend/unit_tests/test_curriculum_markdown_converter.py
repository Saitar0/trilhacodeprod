"""Isolated Markdown-to-contract converter tests using migrated source samples."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from curriculum_contract.converter import convert_manifest_samples
from curriculum_contract.models import (
    AcceptanceCriteriaBlock,
    AnswerKeyBlock,
    ChecklistBlock,
    CompletionCriteriaBlock,
    FeedbackBlock,
    FlashcardBlock,
    InstructorNoteBlock,
    PracticeBlock,
    ProjectDecisionBlock,
    ProjectReviewBlock,
    ProjectScenarioBlock,
    QuizBlock,
    ReferenceBlock,
    RubricBlock,
    SolutionBlock,
    TheoryBlock,
)
from curriculum_contract.validation import DiagnosticSeverity

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATED_ROOT = Path("docs/courses/trilhacode/Conteudos_migrado")
SOURCE_REVISION = "147dc68b81169f66b0ba3802fa2f26e5130923a3"
SAMPLE_UNITS: dict[int, list[str]] = {
    1: ["1.1"],
    2: ["4.1"],
    3: ["8.5"],
    4: ["16.2"],
    5: ["24.3"],
    6: ["31.2"],
    7: ["36.2"],
    8: ["37.1", "39.2"],
    9: ["46.1", "46.2"],
    10: ["52.1"],
}


def _manifest_path(phase: int) -> str:
    return (
        "docs/migracao/mapa_de_migracao.yml"
        if phase == 1
        else f"docs/migracao/mapa_de_migracao_fase{phase}.yml"
    )


def _convert(phase: int, unit_keys: list[str] | None = None):
    return convert_manifest_samples(
        REPO_ROOT,
        _manifest_path(phase),
        unit_keys or SAMPLE_UNITS[phase],
        source_revision=SOURCE_REVISION,
    )


def _source_body(repo_path: str) -> str:
    return _source_body_at(REPO_ROOT, repo_path)


def _source_body_at(root: Path, repo_path: str) -> str:
    raw_text = (root / Path(*repo_path.split("/"))).read_bytes().decode("utf-8")
    lines = raw_text.splitlines(keepends=True)
    closing = next(
        index for index in range(1, len(lines)) if lines[index] in {"---\n", "---\r\n", "---"}
    )
    return "".join(lines[closing + 1 :])


@pytest.fixture(scope="module")
def converted_samples():
    results = {phase: _convert(phase) for phase in SAMPLE_UNITS}
    failures = {
        phase: [item for item in result.diagnostics if item.severity == DiagnosticSeverity.ERROR]
        for phase, result in results.items()
        if not result.ok
    }
    assert not failures, failures
    return results


def _blocks(result: Any, block_type: type[Any], source_contains: str | None = None):
    assert result.contract is not None
    return [
        block
        for block in result.contract.blocks
        if isinstance(block, block_type)
        and (source_contains is None or source_contains in block.provenance.source_file)
    ]


def _write_md(root: Path, relative: str, frontmatter: dict[str, Any], body: str) -> None:
    path = root / Path(*relative.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).rstrip()
    path.write_text(f"---\n{header}\n---\n{body}", encoding="utf-8")


def _minimal_repo(
    root: Path, extra_files: list[tuple[str, dict[str, Any], str]] | None = None
) -> Path:
    """Create a tiny source-backed repo for negative converter cases."""
    destination = "docs/courses/trilhacode/Conteudos_migrado/Fase_1"
    _write_md(
        root,
        "docs/courses/trilhacode/Fase_1_Mini.md",
        {"title": "Fase 1 — Mini", "tipo": "fase", "ordem": 1, "status": "published"},
        "## Módulo 1 — Mini\n",
    )
    topic_root = f"{destination}/1.1_Mini"
    _write_md(
        root,
        f"{topic_root}/README.md",
        {
            "arquivo_id": "f1-topic-11-mini",
            "key": "1.1",
            "title": "1.1 — Mini",
            "tipo": "topic",
            "carater": "obrigatorio",
            "profundidade": "basico",
            "estimativa_minutos": 20,
            "tags": ["mini"],
            "status": "published",
            "tipo_arquivo": "topic_index",
        },
        "# 1.1 — Mini\n",
    )

    files: dict[str, str] = {"T01": "01_conceito/01_teoria.md"}
    _write_md(
        root,
        f"{topic_root}/{files['T01']}",
        {
            "arquivo_id": "f1-topic-11-theory",
            "parent_key": "1.1",
            "tipo_arquivo": "theory",
            "assunto": "01_conceito",
            "ordem": 1,
            "itens_origem": ["Conceito"],
        },
        "## Teoria\n\nTexto original.\n",
    )
    for index, (alias, frontmatter, body) in enumerate(extra_files or [], start=1):
        relative = f"01_conceito/{index + 1:02d}_{alias.lower()}.md"
        files[alias] = relative
        _write_md(root, f"{topic_root}/{relative}", frontmatter, body)

    manifest = {
        "versao_esquema": 1,
        "fase": "Fase_1",
        "destino_raiz": destination,
        "ordem_unidades": ["1.1"],
        "arquivos_comuns": {},
        "unidades": {
            "1.1": {
                "pasta": "1.1_Mini",
                "origem": "Conteudos/Fase_1/1.1_Mini.md",
                "assuntos": ["01_conceito"],
                "arquivos": files,
            }
        },
    }
    manifest_path = root / "docs/migracao/mapa_de_migracao.yml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return manifest_path


def _convert_mini(root: Path):
    return convert_manifest_samples(
        root,
        "docs/migracao/mapa_de_migracao.yml",
        ["1.1"],
        source_revision="test-fixture-revision",
    )


def _minimal_project_repo(root: Path, delivery_body: str) -> tuple[Path, str]:
    manifest_path = _minimal_repo(root)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    unit_root = "docs/courses/trilhacode/Conteudos_migrado/Fase_1/1.1_Mini"
    scope_id = "f1-mini-project-scope"
    delivery_id = "f1-mini-project-delivery"
    scope_path = "01_conceito/10_escopo.md"
    delivery_path = "01_conceito/11_entrega.md"
    _write_md(
        root,
        f"{unit_root}/{scope_path}",
        {
            "arquivo_id": scope_id,
            "parent_key": "1.1",
            "tipo_arquivo": "project_scope",
            "ordem": 10,
        },
        "Escopo original do projeto.\n",
    )
    _write_md(
        root,
        f"{unit_root}/{delivery_path}",
        {
            "arquivo_id": delivery_id,
            "parent_key": "1.1",
            "tipo_arquivo": "milestone",
            "titulo_marco": "Entrega 1 — Conteúdo literal",
            "ordem": 11,
            "itens_origem": ["M01"],
        },
        delivery_body,
    )
    unit = manifest["unidades"]["1.1"]
    unit["arquivos"]["SCP"] = {
        "path": scope_path,
        "arquivo_id": scope_id,
        "tipo": "project_scope",
    }
    unit["arquivos"]["M01"] = {
        "path": delivery_path,
        "arquivo_id": delivery_id,
        "tipo": "milestone",
    }
    manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return manifest_path, delivery_path


def test_converts_conventional_unit_and_preserves_markdown(converted_samples) -> None:
    result = converted_samples[1]
    theories = _blocks(result, TheoryBlock, "/Fase_1/1.1_Computacao_e_software/")
    assert len(theories) == 5
    for block in theories:
        assert block.body == _source_body(block.provenance.source_file)


def test_preserves_code_blocks_verbatim(converted_samples) -> None:
    result = converted_samples[1]
    solutions = _blocks(result, SolutionBlock, "/Fase_1/1.1_Computacao_e_software/")
    source_with_code = next(
        block for block in solutions if "```" in _source_body(block.provenance.source_file)
    )
    assert source_with_code.body == _source_body(source_with_code.provenance.source_file)
    assert "```text" in source_with_code.body


def test_quiz_and_answer_key_have_stable_bidirectional_links(converted_samples) -> None:
    result = converted_samples[2]
    quizzes = _blocks(result, QuizBlock, "/Fase_2/4.1_Estrutura_de_documento/")
    keys = _blocks(result, AnswerKeyBlock, "/Fase_2/4.1_Estrutura_de_documento/")
    by_ref = {key.ref: key for key in keys}
    assert len(quizzes) == len(keys) == 5
    for quiz in quizzes:
        assert quiz.answer_key_required
        assert quiz.answer_key_ref in by_ref
        assert by_ref[quiz.answer_key_ref].question_ref == quiz.ref
    answer_files = {key.provenance.source_file for key in keys}
    for source_file in answer_files:
        source_keys = sorted(
            (key for key in keys if key.provenance.source_file == source_file),
            key=lambda key: key.order,
        )
        assert all(key.source_markdown is not None for key in source_keys)
        assert "".join(key.source_markdown or "" for key in source_keys) == _source_body(
            source_file
        )


def test_multi_question_split_reconstructs_each_source_file(converted_samples) -> None:
    result = converted_samples[2]
    assert result.contract is not None
    quiz_files = {
        mapping.source_file
        for mapping in result.mappings
        if mapping.source_type == "quiz"
        and "/Fase_2/4.1_Estrutura_de_documento/" in mapping.source_file
    }
    for source_file in quiz_files:
        prompts = sorted(
            (
                item
                for item in _blocks(result, QuizBlock)
                if item.provenance.source_file == source_file
            ),
            key=lambda item: item.order,
        )
        assert "".join(item.prompt for item in prompts) == _source_body(source_file)


def test_practice_solution_is_associated_and_verbatim(converted_samples) -> None:
    result = converted_samples[1]
    practices = _blocks(result, PracticeBlock, "/Fase_1/1.1_Computacao_e_software/")
    solutions = _blocks(result, SolutionBlock, "/Fase_1/1.1_Computacao_e_software/")
    assert practices and solutions
    practice_refs = {item.ref for item in practices}
    for solution in solutions:
        assert solution.practice_ref in practice_refs
        assert solution.body == _source_body(solution.provenance.source_file)


def test_flashcards_convert_from_single_and_plural_files(converted_samples) -> None:
    f6_cards = _blocks(converted_samples[6], FlashcardBlock)
    f8_cards = _blocks(converted_samples[8], FlashcardBlock, "/Fase_8/37.1_")
    assert len(f6_cards) == 3
    assert len(f8_cards) == 3
    assert all(card.front and card.back for card in [*f6_cards, *f8_cards])
    for card in [*f6_cards, *f8_cards]:
        assert card.source_markdown == _source_body(card.provenance.source_file)


def test_shared_content_has_one_canonical_block_and_context_placements(converted_samples) -> None:
    result = converted_samples[7]
    assert result.contract is not None
    shared_practices = [
        block
        for block in result.contract.blocks
        if isinstance(block, PracticeBlock) and block.shared
    ]
    assert shared_practices
    placements = result.contract.shared_placements
    for block in shared_practices:
        matching = [item for item in placements if item.block_ref == block.ref]
        assert len(matching) >= 2
        assert len({item.subject_ref for item in matching}) == len(matching)


def test_project_with_formal_milestones_and_acceptance(converted_samples) -> None:
    result = converted_samples[5]
    assert result.contract is not None
    project = result.contract.projects[0]
    assert project.has_formal_milestones
    assert len(project.milestones) == 4
    assert sum(len(item.acceptance_refs) for item in project.milestones) == 4


def test_project_deliveries_preserve_stack_choice_and_checklists(converted_samples) -> None:
    result = converted_samples[9]
    assert result.contract is not None
    project = next(item for item in result.contract.projects if "46-2" in item.ref)
    assert project.has_formal_deliveries
    assert len(project.deliveries) == 4
    assert all(delivery.checklist_refs for delivery in project.deliveries)
    assert project.stack_options == ["42.1", "43.1", "44.1", "45.1"]
    assert project.stack_selected is None
    assert project.source_metadata["project_manifest"]["stack_mode"] == "alternativa"
    assert project.source_metadata["project_manifest"]["escolha_do_aluno"] is True
    assert not any(
        item.code == "PROJECT_STEP_BODY_MAPPED_TO_PRACTICE" for item in result.diagnostics
    )
    for delivery in project.deliveries:
        assert delivery.body == _source_body(delivery.provenance.source_file)


def test_reference_links_and_pending_editorial_targets_preserve_source_text(
    converted_samples,
) -> None:
    result = converted_samples[9]
    references = [
        block
        for block in _blocks(result, ReferenceBlock)
        if "46.2_Projeto_incremental" in block.provenance.source_file
    ]
    assert references
    local_guide = next(block for block in references if block.target_kind == "editorial")
    assert local_guide.raw_text is not None
    assert "Guia de Projetos e Rotação" in local_guide.raw_text
    assert local_guide.pending_ref is not None
    source_body = _source_body(local_guide.provenance.source_file)
    assert local_guide.raw_text in source_body


def test_project_without_formal_milestones_remains_without_them(converted_samples) -> None:
    result = converted_samples[8]
    assert result.contract is not None
    project = result.contract.projects[0]
    assert not project.has_formal_milestones
    assert project.milestones == []
    assert not project.has_formal_deliveries
    assert not project.checklist_refs
    assert any(
        isinstance(block, ProjectScenarioBlock) for block in _blocks(result, ProjectScenarioBlock)
    )


def test_rubric_scale_and_threshold_are_preserved(converted_samples) -> None:
    result = converted_samples[10]
    rubric = next(
        block
        for block in _blocks(result, RubricBlock)
        if block.provenance.source_file.endswith("/91_rubrica_final.md")
    )
    assert rubric.scale is not None
    assert (rubric.scale.minimum, rubric.scale.maximum) == (0, 2)
    assert rubric.threshold == 13
    assert len(rubric.dimensions) == 8


def test_hierarchy_and_ordering_are_deterministic(converted_samples) -> None:
    contract = converted_samples[1].contract
    assert contract is not None
    by_ref = {node.ref: node for node in contract.nodes}
    assert len(by_ref) == len(contract.nodes)
    phases = [node for node in contract.nodes if node.kind == "phase"]
    modules = [node for node in contract.nodes if node.kind == "module"]
    submodules = [node for node in contract.nodes if node.kind == "submodule"]
    topics = [node for node in contract.nodes if node.kind == "topic"]
    assert len(phases) == 1 and modules and submodules and topics
    assert all(node.parent_ref in by_ref for node in [*modules, *submodules, *topics])
    assert [node.order for node in modules] == sorted(node.order for node in modules)


def test_unit_frontmatter_metadata_is_preserved(converted_samples) -> None:
    result = converted_samples[1]
    assert result.contract is not None
    index_path = REPO_ROOT / MIGRATED_ROOT / "Fase_1/1.1_Computacao_e_software/README.md"
    text = index_path.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---", maxsplit=2)[1])
    unit_node = next(
        node
        for node in result.contract.nodes
        if node.kind == "submodule" and node.source_metadata.get("key") == "1.1"
    )
    assert unit_node.source_metadata == frontmatter


def test_provenance_hashes_cover_real_source_bytes(converted_samples) -> None:
    for result in converted_samples.values():
        for mapping in result.mappings:
            source = REPO_ROOT / Path(*mapping.source_file.split("/"))
            assert source.is_file()
            assert hashlib.sha256(source.read_bytes()).hexdigest() == mapping.source_sha256
        assert result.contract is not None
        assert result.contract.source.manifest_sha256


def test_literal_missing_phase_references_remain_editorial_pendings() -> None:
    result = _convert(10, ["47.1"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    pending_text = "\n".join(item.reference_text for item in result.contract.editorial_pendings)
    assert "47.2" in pending_text and "47.3" in pending_text
    rubrics = [block for block in result.contract.blocks if isinstance(block, RubricBlock)]
    assert len(rubrics) == 1
    rubric = rubrics[0]
    assert rubric.source_item_labels == ["P01", "P02", "P03"]
    assert rubric.target_refs == [
        block.ref
        for block in result.contract.blocks
        if isinstance(block, PracticeBlock) and block.provenance.source_id in {"P01", "P02", "P03"}
    ]
    assert rubric.source_markdown == _source_body(rubric.provenance.source_file)
    assert result.canonical_json()


def test_conversion_is_identical_when_selected_units_are_requested_in_reverse_order() -> None:
    forward = _convert(1, ["1.1", "1.2"])
    reverse = _convert(1, ["1.2", "1.1"])

    assert forward.ok and reverse.ok
    assert forward.converted_unit_keys == reverse.converted_unit_keys == ("1.1", "1.2")
    assert forward.to_dict() == reverse.to_dict()
    assert forward.canonical_json() == reverse.canonical_json()


def test_unmapped_connection_bullet_is_retained_even_if_another_unit_reuses_its_text() -> None:
    manifest = yaml.safe_load((REPO_ROOT / _manifest_path(3)).read_text(encoding="utf-8"))
    result = convert_manifest_samples(
        REPO_ROOT,
        _manifest_path(3),
        manifest["ordem_unidades"],
        source_revision=SOURCE_REVISION,
    )
    assert result.contract is not None

    source_file = (
        "docs/courses/trilhacode/Conteudos_migrado/Fase_3/8.3_Configuracao_e_uso/03_conexoes.md"
    )
    body = _source_body(source_file)
    expected_lines = [line for line in body.splitlines() if line.lstrip().startswith(("- ", "* "))]
    represented_lines = [
        relation.note
        for relation in result.contract.relations
        if relation.provenance.source_file == source_file
    ]
    represented_lines.extend(
        pending.reference_text
        for pending in result.contract.editorial_pendings
        if pending.source_file == source_file
    )

    assert expected_lines
    assert all(line in represented_lines for line in expected_lines)


def test_connection_prose_is_retained_without_inferred_relation_targets() -> None:
    result = _convert(10, ["47.1"])
    assert result.contract is not None

    source_file = (
        "docs/courses/trilhacode/Conteudos_migrado/Fase_10/47.1_Uso_assistido/03_conexoes.md"
    )
    source_body = _source_body(source_file)
    prose = next(
        pending
        for pending in result.contract.editorial_pendings
        if pending.source_file == source_file
        and pending.note == "Literal connection prose retained; no structured relation inferred."
    )
    mapping = next(item for item in result.mappings if item.source_file == source_file)

    assert prose.reference_text == (
        "Relaciona-se a Git/GitHub em 3.3, tipos de teste em 24.1 e qualidade em 24.x; "
        "prepara as unidades 47.2 e 47.3 sobre contexto e avaliação do uso de IA.\n"
    )
    assert prose.reference_text in source_body
    assert prose.destination_ref is None
    assert prose.ref in mapping.destination_refs
    assert not any(
        relation.provenance.source_file == source_file for relation in result.contract.relations
    )


def test_completion_criteria_keep_distinct_type_and_exact_source_text(converted_samples) -> None:
    result = converted_samples[1]
    criteria = [
        block
        for block in _blocks(result, CompletionCriteriaBlock)
        if "/Fase_1/1.1_Computacao_e_software/" in block.provenance.source_file
    ]
    assert criteria
    for block in criteria:
        assert block.body == _source_body(block.provenance.source_file)
        assert block.type == "completion_criteria"


def test_project_decisions_remain_distinct_and_verbatim(converted_samples) -> None:
    result = converted_samples[5]
    decisions = [
        block
        for block in _blocks(result, ProjectDecisionBlock)
        if "24.3_Projeto_incremental" in block.provenance.source_file
    ]
    assert len(decisions) == 1
    assert decisions[0].body == _source_body(decisions[0].provenance.source_file)


def test_project_scenarios_remain_distinct_and_verbatim(converted_samples) -> None:
    result = converted_samples[8]
    scenarios = [
        block
        for block in _blocks(result, ProjectScenarioBlock)
        if "39.2_Projeto_incremental" in block.provenance.source_file
    ]
    assert len(scenarios) == 1
    assert scenarios[0].body == _source_body(scenarios[0].provenance.source_file)
    assert "Cenário" in scenarios[0].body or "cenário" in scenarios[0].body


def test_project_review_remains_distinct(converted_samples) -> None:
    result = _convert(5, ["24.4"])
    assert result.ok, result.to_dict()
    reviews = [block for block in _blocks(result, ProjectReviewBlock)]
    assert reviews
    assert all(block.body == _source_body(block.provenance.source_file) for block in reviews)


def test_acceptance_criteria_keep_literal_body_and_item_projection(converted_samples) -> None:
    result = converted_samples[5]
    acceptances = [block for block in _blocks(result, AcceptanceCriteriaBlock)]
    assert acceptances
    for block in acceptances:
        source = _source_body(block.provenance.source_file)
        assert block.body == source
        assert block.source_item_labels
        assert block.items


def test_f2_51_duplicate_practice_labels_make_one_lossless_solution() -> None:
    result = _convert(2, ["5.1"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    solutions = [
        block
        for block in _blocks(result, SolutionBlock)
        if block.provenance.source_file.endswith(
            "90_integracao/02_resposta_esperada_pratica_independente.md"
        )
    ]
    assert len(solutions) == 1
    assert solutions[0].provenance.source_id == "P2"
    assert solutions[0].body == _source_body(solutions[0].provenance.source_file)
    assert (
        sum(
            isinstance(block, PracticeBlock) and block.provenance.source_id == "P2"
            for block in result.contract.blocks
        )
        == 1
    )


def test_phase3_quiz_boundaries_ignore_http_status_numbers() -> None:
    result = _convert(3, ["7.3"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    quizzes = [
        block
        for block in _blocks(result, QuizBlock)
        if "7.3_Dados_e_comunicacao/02_requisicao_async_resposta_erros/02_quiz.md"
        in block.provenance.source_file
    ]
    assert len(quizzes) == 5
    assert [block.provenance.source_id for block in quizzes] == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    quizzes = sorted(quizzes, key=lambda block: block.order)
    assert "".join(block.prompt for block in quizzes) == _source_body(
        quizzes[0].provenance.source_file
    )
    assert "HTTP 404" in quizzes[0].prompt
    keys = [
        block
        for block in _blocks(result, AnswerKeyBlock)
        if "7.3_Dados_e_comunicacao" in block.provenance.source_file
    ]
    assert {block.question_ref for block in keys} == {block.ref for block in quizzes}
    keys = sorted(keys, key=lambda block: block.order)
    assert "".join(block.source_markdown or "" for block in keys) == _source_body(
        keys[0].provenance.source_file
    )


def test_phase3_quiz_network_status_numbers_do_not_create_boundaries() -> None:
    result = _convert(3, ["7.5"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    quizzes = [
        block
        for block in _blocks(result, QuizBlock)
        if "7.5_Depuracao_no_navegador/02_network_requisicoes" in block.provenance.source_file
    ]
    assert [block.provenance.source_id for block in quizzes] == ["Q1", "Q4", "Q5"]
    quizzes = sorted(quizzes, key=lambda block: block.order)
    assert "".join(block.prompt for block in quizzes) == _source_body(
        quizzes[0].provenance.source_file
    )
    assert any("status 404" in block.prompt for block in quizzes)
    answer_keys = sorted(
        [
            block
            for block in _blocks(result, AnswerKeyBlock)
            if "7.5_Depuracao_no_navegador/02_network_requisicoes" in block.provenance.source_file
        ],
        key=lambda block: block.order,
    )
    assert len(answer_keys) == 3
    assert "".join(block.source_markdown or "" for block in answer_keys) == _source_body(
        answer_keys[0].provenance.source_file
    )


def test_project_review_bullets_keep_five_literal_review_items() -> None:
    result = _convert(4, ["16.3"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    reviews = [
        block
        for block in _blocks(result, QuizBlock)
        if block.provenance.source_file.endswith("Q01_revisao_decisoes.md")
    ]
    assert [block.provenance.source_id for block in reviews] == ["R1", "R2", "R3", "R4", "R5"]
    assert "".join(block.prompt for block in reviews) == _source_body(
        reviews[0].provenance.source_file
    )
    assert all(not block.answer_key_required for block in reviews)


def test_f4_162_numbered_review_items_pair_with_existing_answers() -> None:
    result = _convert(4, ["16.2"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    source_file = next(
        mapping.source_file
        for mapping in result.mappings
        if mapping.source_type == "project_review_questions"
        and mapping.source_file.endswith("Q01_revisao_decisoes.md")
    )
    reviews = sorted(
        (
            block
            for block in _blocks(result, QuizBlock)
            if block.provenance.source_file == source_file
        ),
        key=lambda block: block.order,
    )
    keys = sorted(
        (
            block
            for block in _blocks(result, AnswerKeyBlock)
            if block.provenance.source_id in {"R1", "R2", "R3"}
        ),
        key=lambda block: block.order,
    )
    assert [block.provenance.source_id for block in reviews] == ["R1", "R2", "R3"]
    assert [block.question_ref for block in keys] == [block.ref for block in reviews]
    assert "".join(block.prompt for block in reviews) == _source_body(source_file)
    answer_file = keys[0].provenance.source_file
    assert "".join(block.source_markdown or "" for block in keys) == _source_body(answer_file)


def test_f4_91_acceptance_criteria_target_the_existing_practice() -> None:
    result = _convert(4, ["9.1"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    criteria = [
        block
        for block in _blocks(result, AcceptanceCriteriaBlock)
        if block.provenance.source_file.endswith("C01_criterios_aceite.md")
    ]
    assert len(criteria) == 1
    assert criteria[0].practice_ref is not None
    target = next(
        block for block in _blocks(result, PracticeBlock) if block.ref == criteria[0].practice_ref
    )
    assert target.provenance.source_id == "P1"
    assert criteria[0].body == _source_body(criteria[0].provenance.source_file)


def test_f5_191_plain_answer_lines_are_paired_by_explicit_ids() -> None:
    result = _convert(5, ["19.1"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    quizzes = {
        block.provenance.source_id: block
        for block in _blocks(result, QuizBlock)
        if "19.1_ORM_e_acesso_a_dados/02_consultas_relacoes_custo" in block.provenance.source_file
    }
    keys = {
        block.question_ref: block
        for block in _blocks(result, AnswerKeyBlock)
        if "19.1_ORM_e_acesso_a_dados/02_consultas_relacoes_custo" in block.provenance.source_file
    }
    source_ids = ("Q2", "Q3")
    answer_bodies = [keys[quizzes[source_id].ref].source_markdown for source_id in source_ids]
    source_body = _source_body(keys[quizzes["Q2"].ref].provenance.source_file)
    quiz_file = quizzes["Q2"].provenance.source_file
    assert "".join(
        block.prompt for block in sorted(quizzes.values(), key=lambda block: block.order)
    ) == _source_body(quiz_file)
    assert "".join(answer_bodies) == source_body
    assert answer_bodies[0].endswith(
        "Uma consulta inicial seguida de consultas relacionadas que crescem proporcionalmente "
        "ao número de itens processados.\n"
    )
    assert answer_bodies[1] == (
        "Pode aumentar linhas, colunas e memória ou criar joins caros, mesmo reduzindo o número "
        "de chamadas.\n"
    )
    for source_id in source_ids:
        quiz = quizzes[source_id]
        assert keys[quiz.ref].question_ref == quiz.ref


def test_f5_233_instructor_note_remains_instructor_only_and_verbatim() -> None:
    result = _convert(5, ["23.3"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    notes = [
        block
        for block in _blocks(result, InstructorNoteBlock)
        if block.provenance.source_file.endswith("Nota_do_instrutor.md")
    ]
    assert len(notes) == 1
    assert notes[0].audience == "instructor_only"
    assert notes[0].body == _source_body(notes[0].provenance.source_file)
    assert not any(
        block.provenance.source_file.endswith("Nota_do_instrutor.md")
        for block in _blocks(result, FeedbackBlock)
    )


def test_phase6_compact_rubric_ids_resolve_to_three_ordered_practices() -> None:
    result = _convert(6, ["27.3", "27.4"])
    assert result.ok, result.to_dict()
    assert result.contract is not None
    rubrics = [
        block
        for block in _blocks(result, RubricBlock)
        if block.provenance.source_file.endswith("RUB_rubrica_praticas.md")
    ]
    assert len(rubrics) == 2
    for rubric in rubrics:
        assert rubric.source_markdown == _source_body(rubric.provenance.source_file)
        practices = [
            block for block in _blocks(result, PracticeBlock) if block.ref in rubric.target_refs
        ]
        practices_by_ref = {block.ref: block for block in practices}
        assert [
            practices_by_ref[practice_ref].provenance.source_id
            for practice_ref in rubric.target_refs
        ] == ["P01", "P02", "P03"]
        assert rubric.source_item_labels == ["P01,P02,P03"]


def test_inline_quiz_boundary_fallback_fails_closed_when_sequence_is_incomplete(
    tmp_path: Path,
) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "quiz",
                {
                    "arquivo_id": "f1-mini-quiz",
                    "parent_key": "1.1",
                    "tipo_arquivo": "quiz",
                    "assunto": "01_conceito",
                    "ordem": 2,
                    "itens_origem": ["Q1", "Q2"],
                },
                "1. **Questão 1?** O valor contém 404 respostas.\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    diagnostic = next(
        item for item in result.diagnostics if item.code == "QUIZ_BOUNDARY_UNSUPPORTED"
    )
    assert diagnostic.reference is None


def test_answer_lines_with_internal_blank_boundary_fail_closed(tmp_path: Path) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "quiz",
                {
                    "arquivo_id": "f1-mini-quiz",
                    "parent_key": "1.1",
                    "tipo_arquivo": "quiz",
                    "assunto": "01_conceito",
                    "ordem": 2,
                    "itens_origem": ["Q1", "Q2"],
                },
                "1. **Questão 1?**\n2. **Questão 2?**\n",
            ),
            (
                "answer",
                {
                    "arquivo_id": "f1-mini-answer",
                    "parent_key": "1.1",
                    "tipo_arquivo": "answer_key",
                    "assunto": "01_conceito",
                    "ordem": 3,
                    "itens_origem": ["Q1", "Q2"],
                },
                "\nResposta de Q1.\n\nResposta de Q2.\n",
            ),
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    assert any(item.code == "ANSWER_BOUNDARY_UNSUPPORTED" for item in result.diagnostics)


def test_checklist_preserves_literal_markdown_and_checkbox_state(converted_samples) -> None:
    result = converted_samples[9]
    checklists = [block for block in _blocks(result, ChecklistBlock)]
    assert checklists
    for block in checklists:
        assert block.source_markdown == _source_body(block.provenance.source_file)
        source = block.source_markdown
        if "- [ ] " in source:
            assert any(item.checked is False for item in block.items)
        if "- [x] " in source or "- [X] " in source:
            assert any(item.checked is True for item in block.items)


def test_rubric_target_resolution_fails_on_real_ambiguity(tmp_path: Path) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "practice-a",
                {
                    "arquivo_id": "f1-mini-practice-a",
                    "parent_key": "1.1",
                    "tipo_arquivo": "practice",
                    "assunto": "01_conceito",
                    "ordem": 2,
                    "itens_origem": ["P01"],
                },
                "Prática A.\n",
            ),
            (
                "practice-b",
                {
                    "arquivo_id": "f1-mini-practice-b",
                    "parent_key": "1.1",
                    "tipo_arquivo": "practice",
                    "assunto": "01_conceito",
                    "ordem": 3,
                    "itens_origem": ["P01"],
                },
                "Prática B.\n",
            ),
            (
                "rubric",
                {
                    "arquivo_id": "f1-mini-rubric",
                    "parent_key": "1.1",
                    "tipo_arquivo": "rubric",
                    "assunto": "01_conceito",
                    "ordem": 4,
                    "itens_origem": ["P01"],
                },
                "Rubrica de P01.\n",
            ),
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    assert any(item.code == "RUBRIC_TARGET_AMBIGUOUS" for item in result.diagnostics)


def test_rubric_with_unresolved_explicit_target_fails_closed(tmp_path: Path) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "practice",
                {
                    "arquivo_id": "f1-mini-practice",
                    "parent_key": "1.1",
                    "tipo_arquivo": "practice",
                    "assunto": "01_conceito",
                    "ordem": 2,
                    "itens_origem": ["P01"],
                },
                "Prática P01.\n",
            ),
            (
                "rubric",
                {
                    "arquivo_id": "f1-mini-rubric",
                    "parent_key": "1.1",
                    "tipo_arquivo": "rubric",
                    "assunto": "01_conceito",
                    "ordem": 3,
                    "itens_origem": ["P99"],
                },
                "Rubrica sem alvo correspondente.\n",
            ),
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    diagnostic = next(item for item in result.diagnostics if item.code == "RUBRIC_TARGET_NOT_FOUND")
    assert diagnostic.reference == "P99"
    assert diagnostic.source_file is not None
    assert diagnostic.field == "itens_origem"


def test_rubric_without_source_target_fails_closed(tmp_path: Path) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "rubric",
                {
                    "arquivo_id": "f1-mini-rubric",
                    "parent_key": "1.1",
                    "tipo_arquivo": "rubric",
                    "assunto": "01_conceito",
                    "ordem": 2,
                },
                "Rubrica sem alvo declarado.\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    diagnostic = next(item for item in result.diagnostics if item.code == "RUBRIC_TARGET_MISSING")
    assert diagnostic.source_file is not None
    assert diagnostic.entity_ref == "f1-mini-rubric"
    assert diagnostic.field == "itens_origem"


def test_project_delivery_keeps_markdown_and_code_fence_verbatim(tmp_path: Path) -> None:
    delivery_body = (
        "## Entrega 1 — Conteúdo literal\n\n"
        "Descrição com **ênfase** e uma referência `inline`.\n\n"
        "```python\nprint('keep')\n```\n\n"
        "- evidência existente\n"
    )
    manifest, delivery_path = _minimal_project_repo(tmp_path, delivery_body)
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert result.ok, result.to_dict()
    assert result.contract is not None
    project = result.contract.projects[0]
    assert len(project.deliveries) == 1
    assert project.deliveries[0].body == _source_body_at(
        tmp_path, project.deliveries[0].provenance.source_file
    )
    assert "```python" in project.deliveries[0].body
    assert "print('keep')" in project.deliveries[0].body
    assert "```" in project.deliveries[0].body
    assert not any(
        isinstance(block, PracticeBlock) and block.provenance.source_file.endswith(delivery_path)
        for block in result.contract.blocks
    )


def test_conversion_refuses_duplicate_ids(tmp_path: Path) -> None:
    manifest = _minimal_repo(
        tmp_path,
        [
            (
                "summary",
                {
                    "arquivo_id": "f1-topic-11-theory",
                    "parent_key": "1.1",
                    "tipo_arquivo": "resumo",
                    "ordem": 1,
                },
                "## Resumo\nTexto.\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    assert any(item.code == "DUPLICATE_ID" for item in result.diagnostics)


def test_unresolved_relative_reference_is_explicitly_pending(tmp_path: Path) -> None:
    _minimal_repo(
        tmp_path,
        [
            (
                "references",
                {
                    "arquivo_id": "f1-topic-11-references",
                    "parent_key": "1.1",
                    "tipo_arquivo": "referencias",
                    "ordem": 1,
                },
                "- [Guia relacionado](guia-ausente.md)\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    assert result.ok and result.contract is not None
    pending = [
        item for item in result.contract.editorial_pendings if "guia-ausente" in item.reference_text
    ]
    assert len(pending) == 1
    assert pending[0].kind == "unresolved_reference"
    assert not pending[0].blocking


def test_unknown_source_type_fails_closed(tmp_path: Path) -> None:
    _minimal_repo(
        tmp_path,
        [
            (
                "unknown",
                {
                    "arquivo_id": "f1-topic-11-unknown",
                    "parent_key": "1.1",
                    "tipo_arquivo": "future_magic_block",
                    "assunto": "01_conceito",
                    "ordem": 2,
                },
                "Conteúdo não tipado.\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    assert not result.ok
    assert any(item.code == "UNSUPPORTED_SOURCE_TYPE" for item in result.diagnostics)


def test_invalid_frontmatter_returns_structured_diagnostic(tmp_path: Path) -> None:
    manifest = _minimal_repo(tmp_path)
    theory = (
        tmp_path
        / "docs/courses/trilhacode/Conteudos_migrado/Fase_1/1.1_Mini/01_conceito/01_teoria.md"
    )
    theory.write_text("---\narquivo_id: [unterminated\n", encoding="utf-8")
    result = _convert_mini(tmp_path)
    assert manifest.is_file()
    assert not result.ok
    diagnostic = next(item for item in result.diagnostics if item.code == "FRONTMATTER_INVALID")
    assert diagnostic.source_file is not None
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.remediation


def test_serialization_is_deterministic(converted_samples) -> None:
    first = converted_samples[1].canonical_json()
    second = _convert(1).canonical_json()
    assert first == second
    assert json.loads(first)["schema_version"] == "trilhacode.intermediate/1.2"


def test_diagnostics_expose_stable_codes_and_context(tmp_path: Path) -> None:
    _minimal_repo(
        tmp_path,
        [
            (
                "unknown",
                {
                    "arquivo_id": "f1-topic-11-unknown",
                    "parent_key": "1.1",
                    "tipo_arquivo": "not_supported",
                    "assunto": "01_conceito",
                    "ordem": 2,
                },
                "Texto.\n",
            )
        ],
    )
    result = _convert_mini(tmp_path)
    diagnostic = next(item for item in result.diagnostics if item.code == "UNSUPPORTED_SOURCE_TYPE")
    payload = diagnostic.model_dump(mode="json")
    assert payload["severity"] == "error"
    assert payload["source_file"].endswith("02_unknown.md")
    assert payload["field"] == "tipo_arquivo"
    assert payload["remediation"]
