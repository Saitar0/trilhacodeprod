"""Unit tests for the isolated, database-independent curriculum contract."""

from __future__ import annotations

import copy
import hashlib
import json

from curriculum_contract import (
    CONTRACT_VERSION,
    LEGACY_CONTRACT_VERSION,
    ChangeState,
    QuizBlock,
    RubricBlock,
    canonical_json,
    classify_changes,
    student_quiz_view,
    validate_contract,
    verify_source_hash,
)
from curriculum_contract.validation import BaselineFingerprint

SHA = "a" * 64


def provenance(path: str = "Conteudos/Fase_1/1.1.md") -> dict[str, str]:
    return {
        "source_file": path,
        "source_sha256": SHA,
        "manifest_ref": "f1-unidade-1",
        "source_role": "source_block",
    }


def node(ref: str, kind: str, parent: str | None, order: int, path: str) -> dict:
    return {
        "ref": ref,
        "kind": kind,
        "parent_ref": parent,
        "title": ref,
        "order": order,
        "status": "published",
        "estimated_minutes": None,
        "source_metadata": {"original_key": ref},
        "tags": [],
        "provenance": provenance(path),
    }


def valid_payload() -> dict:
    phase = "f1-fase-1"
    module = "f1-modulo-1"
    unit = "f1-unidade-1"
    topic_a = "f1-assunto-a"
    topic_b = "f1-assunto-b"
    quiz = "f1-quiz-1"
    answer_key = "f1-gabarito-1"
    shared_practice = "f1-pratica-compartilhada"
    project = "f1-projeto-1"
    return {
        "schema_version": CONTRACT_VERSION,
        "source": {
            "manifest_path": "docs/migracao/mapa_de_migracao_fase1.yml",
            "manifest_sha256": SHA,
            "source_revision": "147dc68b81169f66b0ba3802fa2f26e5130923a3",
            "converter_version": "0.1.0",
        },
        "nodes": [
            node(phase, "phase", None, 0, "docs/courses/trilhacode/Fase_1.md"),
            node(module, "module", phase, 0, "docs/courses/trilhacode/Fase_1.md"),
            node(unit, "submodule", module, 0, "Conteudos/Fase_1/1.1.md"),
            node(topic_a, "topic", unit, 0, "Conteudos/Fase_1/1.1.md"),
            node(topic_b, "topic", unit, 1, "Conteudos/Fase_1/1.1.md"),
        ],
        "blocks": [
            {
                "ref": quiz,
                "type": "quiz",
                "owner_ref": topic_a,
                "order": 0,
                "title": "Questão 1",
                "status": "published",
                "shared": False,
                "provenance": provenance(),
                "prompt": "Qual opção representa a resposta correta?",
                "format": "multiple_choice",
                "options": [
                    {"ref": "a", "text": "Alternativa A"},
                    {"ref": "b", "text": "Alternativa B"},
                ],
                "answer_key_required": True,
                "answer_key_ref": answer_key,
            },
            {
                "ref": answer_key,
                "type": "answer_key",
                "owner_ref": topic_a,
                "order": 1,
                "title": "Gabarito da questão 1",
                "status": "published",
                "shared": False,
                "provenance": provenance(),
                "question_ref": quiz,
                "correct_option_ref": "a",
                "accepted_answers": [],
                "expected_answer": None,
                "explanation": "A alternativa A é a correta conforme a fonte.",
                "source_markdown": "**Resposta:** A\n",
            },
            {
                "ref": shared_practice,
                "type": "practice",
                "owner_ref": None,
                "order": 0,
                "title": "Prática integradora",
                "status": "published",
                "shared": True,
                "provenance": provenance(),
                "prompt": "Aplique os dois assuntos em uma atividade.",
                "language": None,
                "starter_code": None,
                "acceptance": ["A atividade preserva a entrega original."],
            },
            {
                "ref": "f1-teoria-1",
                "type": "theory",
                "owner_ref": topic_a,
                "order": 2,
                "title": "Conceito",
                "status": "published",
                "shared": False,
                "provenance": provenance(),
                "body": "Texto de teoria de exemplo.",
                "microtopic": "Conceito básico",
            },
        ],
        "relations": [],
        "shared_placements": [
            {
                "ref": "f1-colocacao-a",
                "block_ref": shared_practice,
                "subject_ref": topic_a,
                "order": 3,
                "progress_scope": "undecided",
                "provenance": provenance(),
            },
            {
                "ref": "f1-colocacao-b",
                "block_ref": shared_practice,
                "subject_ref": topic_b,
                "order": 0,
                "progress_scope": "undecided",
                "provenance": provenance(),
            },
        ],
        "projects": [
            {
                "ref": project,
                "unit_ref": unit,
                "title": "Projeto sem marcos formais",
                "scope": "Projeto de unidade descrito sem entregas formais.",
                "has_formal_deliveries": False,
                "deliveries": [],
                "has_formal_milestones": False,
                "milestones": [],
                "variants": [],
                "checklist_refs": [],
                "rubric_refs": [],
                "stack_options": [],
                "stack_selected": None,
                "source_metadata": {},
                "provenance": provenance(),
            }
        ],
        "editorial_pendings": [],
        "vault_root_confirmed": False,
    }


def codes(report) -> set[str]:
    return {diagnostic.code for diagnostic in report.diagnostics}


def rubric_payload(target_refs: list[str]) -> dict:
    return {
        "ref": "f1-rubrica-multialvo",
        "type": "rubric",
        "owner_ref": "f1-assunto-a",
        "order": 4,
        "title": "Rubrica com alvos explícitos",
        "status": "published",
        "shared": False,
        "provenance": provenance(),
        "target_ref": target_refs[0],
        "target_refs": target_refs,
        "scale": {"minimum": 0, "maximum": 2},
        "dimensions": [
            {
                "ref": "evidencia",
                "title": "Evidência",
                "weight": 1.0,
                "descriptors": {"0": "Ausente", "2": "Completa"},
            }
        ],
        "threshold": None,
        "source_markdown": "Rubrica original.\n",
        "source_item_labels": ["P01", "P02"],
    }


def test_minimal_contract_is_valid_and_serializable() -> None:
    report = validate_contract(valid_payload())
    assert report.ok, report.as_dict()
    assert report.contract is not None
    assert report.contract.schema_version == CONTRACT_VERSION
    round_trip = validate_contract(json.loads(canonical_json(report.contract)))
    assert round_trip.ok
    assert round_trip.contract is not None
    assert canonical_json(round_trip.contract) == canonical_json(report.contract)


def test_acceptance_criteria_can_target_an_existing_shared_practice() -> None:
    payload = valid_payload()
    acceptance_ref = "f1-practice-acceptance"
    payload["blocks"].append(
        {
            "ref": acceptance_ref,
            "type": "acceptance_criteria",
            "owner_ref": None,
            "order": 4,
            "title": "Aceite da prática compartilhada",
            "status": "published",
            "shared": True,
            "provenance": provenance(),
            "delivery_ref": None,
            "milestone_ref": None,
            "practice_ref": "f1-pratica-compartilhada",
            "items": [{"ref": "aceite-p1", "text": "Evidência conferível."}],
            "body": "Evidência conferível.\n",
            "source_item_labels": ["P01"],
        }
    )
    for suffix, subject_ref, order in (("a", "f1-assunto-a", 4), ("b", "f1-assunto-b", 1)):
        payload["shared_placements"].append(
            {
                "ref": f"f1-aceite-placement-{suffix}",
                "block_ref": acceptance_ref,
                "subject_ref": subject_ref,
                "order": order,
                "progress_scope": "undecided",
                "provenance": provenance(),
            }
        )

    report = validate_contract(payload)
    assert report.ok, report.as_dict()


def test_acceptance_criteria_reject_missing_practice_target() -> None:
    payload = valid_payload()
    payload["blocks"].append(
        {
            "ref": "f1-practice-acceptance",
            "type": "acceptance_criteria",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Aceite da prática",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "delivery_ref": None,
            "milestone_ref": None,
            "practice_ref": "f1-pratica-inexistente",
            "items": [{"ref": "aceite-p1", "text": "Evidência conferível."}],
            "body": "Evidência conferível.\n",
            "source_item_labels": ["P01"],
        }
    )
    assert "ACCEPTANCE_PRACTICE_NOT_FOUND" in codes(validate_contract(payload))


def test_invalid_schema_returns_structured_diagnostic() -> None:
    payload = valid_payload()
    payload["nodes"][0]["title"] = ""
    report = validate_contract(payload)
    assert not report.ok
    diagnostic = report.diagnostics[0]
    assert diagnostic.code == "SCHEMA_INVALID"
    assert diagnostic.severity.value == "error"
    assert diagnostic.source_file == "docs/courses/trilhacode/Fase_1.md"
    assert diagnostic.entity_ref == "f1-fase-1"
    assert diagnostic.field
    assert diagnostic.remediation


def test_global_duplicate_id_is_rejected() -> None:
    payload = valid_payload()
    payload["blocks"].append(
        {
            "ref": "f1-fase-1",
            "type": "theory",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Duplicado",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "body": "Conteúdo",
            "microtopic": None,
        }
    )
    assert "DUPLICATE_ID" in codes(validate_contract(payload))


def test_missing_parent_is_rejected() -> None:
    payload = valid_payload()
    payload["nodes"][2]["parent_ref"] = "f1-modulo-ausente"
    assert "PARENT_NOT_FOUND" in codes(validate_contract(payload))


def test_hierarchy_cycle_is_reported() -> None:
    payload = valid_payload()
    payload["nodes"][1]["parent_ref"] = "f1-unidade-1"
    payload["nodes"][2]["parent_ref"] = "f1-modulo-1"
    assert "HIERARCHY_CYCLE" in codes(validate_contract(payload))


def test_unknown_block_type_is_not_coerced_to_theory() -> None:
    payload = valid_payload()
    payload["blocks"][0]["type"] = "answer_key_v2"
    assert "UNKNOWN_BLOCK_TYPE" in codes(validate_contract(payload))


def test_required_answer_key_must_exist() -> None:
    payload = valid_payload()
    payload["blocks"][0]["answer_key_ref"] = None
    assert "QUIZ_ANSWER_KEY_MISSING" in codes(validate_contract(payload))


def test_answer_key_must_match_its_quiz() -> None:
    payload = valid_payload()
    second_quiz = copy.deepcopy(payload["blocks"][0])
    second_quiz["ref"] = "f1-quiz-2"
    second_quiz["order"] = 3
    second_quiz["answer_key_ref"] = "f1-gabarito-2"
    second_key = copy.deepcopy(payload["blocks"][1])
    second_key["ref"] = "f1-gabarito-2"
    second_key["order"] = 4
    second_key["question_ref"] = "f1-quiz-2"
    payload["blocks"].extend([second_quiz, second_key])
    payload["blocks"][0]["answer_key_ref"] = "f1-gabarito-2"
    assert "ANSWER_KEY_ASSOCIATION_MISMATCH" in codes(validate_contract(payload))


def test_shared_placement_requires_existing_subject() -> None:
    payload = valid_payload()
    payload["shared_placements"][0]["subject_ref"] = "f1-assunto-ausente"
    assert "SHARED_SUBJECT_NOT_FOUND" in codes(validate_contract(payload))


def test_shared_placement_requires_existing_canonical_block() -> None:
    payload = valid_payload()
    payload["shared_placements"][0]["block_ref"] = "f1-bloco-compartilhado-ausente"
    assert "SHARED_BLOCK_NOT_FOUND" in codes(validate_contract(payload))


def test_shared_block_cannot_have_duplicate_placement_in_same_subject() -> None:
    payload = valid_payload()
    duplicate = copy.deepcopy(payload["shared_placements"][0])
    duplicate["ref"] = "f1-colocacao-duplicada"
    duplicate["order"] = 4
    payload["shared_placements"].append(duplicate)
    assert "DUPLICATE_PLACEMENT" in codes(validate_contract(payload))


def test_invalid_rubric_scale_is_rejected() -> None:
    payload = valid_payload()
    payload["blocks"].append(
        {
            "ref": "f1-rubrica-1",
            "type": "rubric",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Rubrica",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "target_ref": "f1-pratica-compartilhada",
            "target_refs": ["f1-pratica-compartilhada"],
            "scale": {"minimum": 1, "maximum": 1},
            "dimensions": [
                {
                    "ref": "qualidade",
                    "title": "Qualidade",
                    "weight": 1.0,
                    "descriptors": {"1": "Atende"},
                }
            ],
            "threshold": None,
            "source_markdown": "Rubrica original.\n",
            "source_item_labels": ["P01"],
        }
    )
    assert "RUBRIC_SCALE_INVALID" in codes(validate_contract(payload))


def test_rubric_threshold_cannot_exceed_maximum_score() -> None:
    payload = valid_payload()
    payload["blocks"].append(
        {
            "ref": "f1-rubrica-1",
            "type": "rubric",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Rubrica",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "target_ref": "f1-pratica-compartilhada",
            "target_refs": ["f1-pratica-compartilhada"],
            "scale": {"minimum": 0, "maximum": 4},
            "dimensions": [
                {
                    "ref": "qualidade",
                    "title": "Qualidade",
                    "weight": 1.0,
                    "descriptors": {"0": "Não atende", "4": "Supera"},
                }
            ],
            "threshold": 5.0,
            "source_markdown": "Rubrica original.\n",
            "source_item_labels": ["P01"],
        }
    )
    assert "RUBRIC_THRESHOLD_OUT_OF_RANGE" in codes(validate_contract(payload))


def test_rubric_accepts_one_explicit_target_in_contract_1_1() -> None:
    payload = valid_payload()
    payload["blocks"].append(rubric_payload(["f1-pratica-compartilhada"]))
    report = validate_contract(payload)
    assert report.ok, report.as_dict()
    assert report.contract is not None
    rubric = next(block for block in report.contract.blocks if isinstance(block, RubricBlock))
    assert rubric.target_ref == "f1-pratica-compartilhada"
    assert rubric.target_refs == ["f1-pratica-compartilhada"]


def test_rubric_accepts_multiple_ordered_targets() -> None:
    payload = valid_payload()
    payload["blocks"].append(rubric_payload(["f1-pratica-compartilhada", "f1-assunto-b"]))
    report = validate_contract(payload)
    assert report.ok, report.as_dict()
    assert report.contract is not None
    rubric = next(block for block in report.contract.blocks if isinstance(block, RubricBlock))
    assert rubric.target_refs == ["f1-pratica-compartilhada", "f1-assunto-b"]


def test_rubric_rejects_missing_target_reference() -> None:
    payload = valid_payload()
    payload["blocks"].append(rubric_payload(["f1-pratica-compartilhada", "f1-alvo-ausente"]))
    assert "RUBRIC_TARGET_NOT_FOUND" in codes(validate_contract(payload))


def test_rubric_rejects_duplicate_targets() -> None:
    payload = valid_payload()
    payload["blocks"].append(
        rubric_payload(["f1-pratica-compartilhada", "f1-pratica-compartilhada"])
    )
    assert "RUBRIC_TARGET_DUPLICATE" in codes(validate_contract(payload))


def test_contract_1_1_requires_explicit_rubric_targets_and_source() -> None:
    payload = valid_payload()
    rubric = rubric_payload(["f1-pratica-compartilhada"])
    rubric["target_refs"] = []
    rubric["source_markdown"] = None
    payload["blocks"].append(rubric)
    diagnostic_codes = codes(validate_contract(payload))
    assert "RUBRIC_TARGETS_MISSING" in diagnostic_codes
    assert "RUBRIC_SOURCE_MARKDOWN_MISSING" in diagnostic_codes


def test_project_without_formal_milestones_remains_valid() -> None:
    report = validate_contract(valid_payload())
    assert report.ok
    assert "PROJECT_DELIVERIES_NOT_IN_SOURCE" not in codes(report)
    assert "PROJECT_DELIVERIES_MISSING" not in codes(report)


def test_formal_project_milestone_and_variant_are_preserved_as_typed_entities() -> None:
    payload = valid_payload()
    project = payload["projects"][0]
    project["has_formal_milestones"] = True
    project["stack_options"] = ["Django/DRF"]
    project["variants"] = [
        {
            "ref": "f1-variante-django",
            "title": "Variação Django",
            "order": 0,
            "description": "Opção literal do projeto.",
            "delivery_refs": [],
            "stack_option": "Django/DRF",
            "provenance": provenance(),
        }
    ]
    milestone_ref = "f1-marco-1"
    acceptance_ref = "f1-aceite-marco-1"
    project["milestones"] = [
        {
            "ref": milestone_ref,
            "title": "Marco original",
            "body": "## Marco original\n\nDescrição do marco.\n",
            "order": 0,
            "acceptance_refs": [acceptance_ref],
            "checklist_refs": [],
            "rubric_refs": [],
            "content_refs": [],
            "provenance": provenance(),
        }
    ]
    payload["blocks"].append(
        {
            "ref": acceptance_ref,
            "type": "acceptance_criteria",
            "owner_ref": milestone_ref,
            "order": 0,
            "title": "Aceite do marco",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "delivery_ref": None,
            "milestone_ref": milestone_ref,
            "items": [{"ref": "aceite-1", "text": "Critério existente."}],
            "body": "Critério existente.\n",
            "source_item_labels": ["M01"],
        }
    )
    report = validate_contract(payload)
    assert report.ok, report.as_dict()
    assert report.contract is not None
    assert report.contract.projects[0].milestones[0].ref == milestone_ref
    assert report.contract.projects[0].variants[0].stack_option == "Django/DRF"
    assert report.contract.projects[0].stack_selected is None


def test_missing_provenance_is_a_structured_error() -> None:
    payload = valid_payload()
    del payload["nodes"][0]["provenance"]
    report = validate_contract(payload)
    assert not report.ok
    assert "SOURCE_METADATA_MISSING" in codes(report)


def test_invalid_source_hash_is_rejected() -> None:
    payload = valid_payload()
    payload["blocks"][0]["provenance"]["source_sha256"] = "not-a-hash"
    assert "INVALID_SHA256" in codes(validate_contract(payload))


def test_manifest_path_must_be_repository_relative() -> None:
    payload = valid_payload()
    payload["source"]["manifest_path"] = "../outside/manifest.yml"
    report = validate_contract(payload)
    assert "SOURCE_PATH_INVALID" in codes(report)


def test_unresolved_obsidian_reference_is_retained_as_nonblocking_warning() -> None:
    payload = valid_payload()
    pending_ref = "f1-pending-vault-root"
    source_path = "Conteudos/Fase_1/1.1.md"
    payload["editorial_pendings"] = [
        {
            "ref": pending_ref,
            "kind": "obsidian_vault_root_unknown",
            "source_file": source_path,
            "entity_ref": "f1-assunto-a",
            "reference_text": "[[Destino original]]",
            "destination_ref": None,
            "blocking": False,
            "note": "A raiz do vault ainda não foi confirmada.",
            "provenance": provenance(source_path),
        }
    ]
    payload["blocks"].append(
        {
            "ref": "f1-referencia-obsidian",
            "type": "reference",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Referência Obsidian",
            "status": "published",
            "shared": False,
            "provenance": provenance(source_path),
            "target_kind": "obsidian",
            "label": "Destino original",
            "citation": "",
            "url": None,
            "target_ref": None,
            "raw_text": "[[Destino original]]",
            "pending_ref": pending_ref,
        }
    )
    report = validate_contract(payload)
    assert report.ok
    assert "OBSIDIAN_ROOT_UNCONFIRMED" in codes(report)
    assert "EDITORIAL_PENDING_BLOCKING" not in codes(report)


def test_canonical_order_is_independent_of_input_list_order() -> None:
    payload = valid_payload()
    reversed_payload = copy.deepcopy(payload)
    reversed_payload["nodes"].reverse()
    reversed_payload["blocks"].reverse()
    reversed_payload["shared_placements"].reverse()
    first = validate_contract(payload)
    second = validate_contract(reversed_payload)
    assert first.contract is not None
    assert second.contract is not None
    assert canonical_json(first.contract) == canonical_json(second.contract)


def test_student_quiz_view_does_not_expose_answer_key() -> None:
    report = validate_contract(valid_payload())
    assert report.contract is not None
    quiz = next(block for block in report.contract.blocks if isinstance(block, QuizBlock))
    student_view = student_quiz_view(quiz).model_dump(mode="json")
    assert student_view["ref"] == "f1-quiz-1"
    assert "answer_key_ref" not in student_view
    assert "correct_option_ref" not in student_view


def test_version_1_0_single_target_rubric_remains_readable() -> None:
    payload = valid_payload()
    payload["schema_version"] = LEGACY_CONTRACT_VERSION
    payload["blocks"][1].pop("source_markdown")
    payload["blocks"].append(
        {
            "ref": "f1-rubrica-legada",
            "type": "rubric",
            "owner_ref": "f1-assunto-a",
            "order": 4,
            "title": "Rubrica legada",
            "status": "published",
            "shared": False,
            "provenance": provenance(),
            "target_ref": "f1-pratica-compartilhada",
            "scale": {"minimum": 0, "maximum": 2},
            "dimensions": [
                {
                    "ref": "evidencia",
                    "title": "Evidência",
                    "weight": 1.0,
                    "descriptors": {"0": "Ausente", "2": "Completa"},
                }
            ],
            "threshold": None,
        }
    )
    report = validate_contract(payload)
    assert report.ok, report.as_dict()
    assert report.contract is not None
    rubric = next(block for block in report.contract.blocks if block.type == "rubric")
    assert rubric.target_refs == []
    assert rubric.source_markdown is None


def test_source_hash_verification_uses_supplied_bytes_only() -> None:
    from curriculum_contract.models import SourceProvenance

    content = b"source block"
    item = SourceProvenance(
        source_file="Conteudos/Fase_1/1.1.md",
        source_sha256=hashlib.sha256(content).hexdigest(),
        manifest_ref="f1-unidade-1",
        source_role="theory",
    )
    assert verify_source_hash(item, content) == ()
    assert verify_source_hash(item, b"different")


def test_change_classification_is_deterministic_and_never_authorizes_deletion() -> None:
    same = "b" * 64
    old = "c" * 64
    changed = "d" * 64
    baseline = {
        "f1-unchanged": BaselineFingerprint(last_applied_sha256=same, current_sha256=same),
        "f1-conflict": BaselineFingerprint(last_applied_sha256=same, current_sha256=old),
        "f1-modified": BaselineFingerprint(last_applied_sha256=same, current_sha256=same),
        "f1-absent": BaselineFingerprint(last_applied_sha256=same, current_sha256=same),
    }
    records = classify_changes(
        {
            "f1-new": old,
            "f1-unchanged": same,
            "f1-conflict": old,
            "f1-modified": changed,
        },
        baseline,
    )
    assert [record.ref for record in records] == sorted(record.ref for record in records)
    by_ref = {record.ref: record for record in records}
    assert by_ref["f1-new"].state == ChangeState.NEW
    assert by_ref["f1-unchanged"].state == ChangeState.UNCHANGED
    assert by_ref["f1-conflict"].state == ChangeState.CONFLICT
    assert by_ref["f1-modified"].state == ChangeState.MODIFIED
    assert by_ref["f1-absent"].state == ChangeState.ABSENT
    assert by_ref["f1-conflict"].deletion_authorized is False
    assert by_ref["f1-unchanged"].deletion_authorized is False
    assert by_ref["f1-absent"].deletion_authorized is False
