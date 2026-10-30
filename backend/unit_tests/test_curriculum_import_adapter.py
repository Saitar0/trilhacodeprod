"""Offline contract tests for the versioned import adapter planner."""

from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from curriculum_contract.import_adapter import (
    AdapterValidationError,
    ExistingEntitySnapshot,
    OperationState,
    build_dry_run_plan,
    canonical_plan_json,
    classify_snapshot_state,
    parse_bundle_bytes,
    read_and_validate_bundle,
    validate_package,
)
from curriculum_contract.models import AnswerKeyBlock, QuizBlock

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "docs/courses/trilhacode/trilha-code-bulk-import.json"


@pytest.fixture(scope="session")
def package():
    return read_and_validate_bundle(BUNDLE_PATH, repo_root=REPO_ROOT)


@pytest.fixture(scope="session")
def plan(package):
    return build_dry_run_plan(package)


def _diagnostic_codes(error: AdapterValidationError) -> set[str]:
    return {item.code for item in error.diagnostics}


def test_full_versioned_package_and_integrity_are_valid(package) -> None:
    assert package.bundle.schema_version == "trilhacode.import_bundle/1.0"
    assert (
        package.bundle_sha256 == "43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2"
    )
    assert len(package.bundle.phases) == 10
    assert package.repository_checks["integrity_sidecars"]["sidecars_verified"] == 12
    assert package.repository_checks["migration_inventory"]["migration_mapping_rows"] == 4311


def test_package_reconciles_files_mappings_and_structural_exceptions(package) -> None:
    checks = package.repository_checks
    assert checks["migration_inventory"]["migrated_files"] == 2890
    assert checks["migration_inventory"]["unique_physical_migration_destinations"] == 2879
    assert checks["migration_inventory"]["removal_sentinel_rows"] == 2
    assert checks["migration_inventory"]["authorized_unmapped_structural_files"] == 11
    assert checks["source_mappings"]["records"] == 2889
    assert checks["source_mappings"]["source_file_hashes_verified"] == 2889
    assert checks["source_mappings"]["destination_refs_not_in_bundle"] == 0
    assert checks["migration_inventory"]["preserved_unmapped_editorial_sources"] == [
        "docs/courses/trilhacode/Conteudos/Fase_7/37.1_Servicos_gerenciados.md",
        "docs/courses/trilhacode/Conteudos/Fase_7/37.2_Kubernetes_basico.md",
    ]


def test_unknown_bundle_version_is_rejected_before_schema_parsing() -> None:
    with pytest.raises(AdapterValidationError) as caught:
        parse_bundle_bytes(b'{"schema_version":"trilhacode.import_bundle/9.9"}')
    assert "UNKNOWN_BUNDLE_VERSION" in _diagnostic_codes(caught.value)


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(AdapterValidationError) as caught:
        parse_bundle_bytes(b"{not json")
    assert "JSON_INVALID" in _diagnostic_codes(caught.value)


def test_duplicate_json_keys_are_rejected() -> None:
    with pytest.raises(AdapterValidationError) as caught:
        parse_bundle_bytes(b'{"schema_version":"a","schema_version":"b"}')
    assert "DUPLICATE_JSON_KEY" in _diagnostic_codes(caught.value)


def test_duplicate_entity_ids_are_rejected(package) -> None:
    changed = copy.deepcopy(package.bundle)
    changed.phases[0].contract.nodes[1].ref = changed.phases[0].contract.nodes[0].ref
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert "DUPLICATE_ENTITY_ID" in _diagnostic_codes(caught.value)


def test_broken_curriculum_reference_is_rejected(package) -> None:
    changed = copy.deepcopy(package.bundle)
    relation = changed.phases[0].contract.relations[0]
    relation.target_ref = "f1-node-does-not-exist"
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert "RELATION_NODE_MISSING" in _diagnostic_codes(caught.value)


def test_answer_key_without_its_question_is_rejected(package) -> None:
    changed = copy.deepcopy(package.bundle)
    contract = changed.phases[0].contract
    key = next(block for block in contract.blocks if isinstance(block, AnswerKeyBlock))
    contract.blocks.remove(key)
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert {"QUIZ_ANSWER_KEY_MISMATCH", "QUIZ_ANSWER_KEY_MISSING"} & _diagnostic_codes(caught.value)


def test_incomplete_project_reference_is_rejected(package) -> None:
    changed = copy.deepcopy(package.bundle)
    changed.phases[0].contract.projects[0].unit_ref = "f1-unit-not-in-the-bundle"
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert "PROJECT_UNIT_REFERENCE_INVALID" in _diagnostic_codes(caught.value)


def test_shared_placement_with_missing_block_is_rejected(package) -> None:
    changed = copy.deepcopy(package.bundle)
    changed.phases[0].contract.shared_placements[0].block_ref = "f1-missing-shared-block"
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert "SHARED_PLACEMENT_REFERENCE_INVALID" in _diagnostic_codes(caught.value)


def test_mapping_destination_must_resolve_to_a_bundle_entity(package) -> None:
    changed = copy.deepcopy(package.bundle)
    changed.source_mappings["mappings"][0]["destination_refs"] = ["f1-nonexistent-destination"]
    with pytest.raises(AdapterValidationError) as caught:
        validate_package(changed)
    assert "MAPPING_DESTINATION_UNKNOWN" in _diagnostic_codes(caught.value)


def test_unknown_block_type_is_not_coerced_to_theory() -> None:
    raw = BUNDLE_PATH.read_bytes()
    changed = raw.replace(b'"type": "theory"', b'"type": "mystery"', 1)
    assert changed != raw
    with pytest.raises(AdapterValidationError) as caught:
        parse_bundle_bytes(changed)
    assert "UNKNOWN_BLOCK_TYPE" in _diagnostic_codes(caught.value)


def test_plan_is_deterministic_even_if_phase_read_order_is_reversed(package) -> None:
    first = build_dry_run_plan(package)
    reversed_bundle = copy.deepcopy(package.bundle)
    reversed_bundle.phases.reverse()
    reversed_package = copy.copy(package)
    object.__setattr__(reversed_package, "bundle", reversed_bundle)
    second = build_dry_run_plan(reversed_package)
    assert canonical_plan_json(first) == canonical_plan_json(second)


def test_plan_is_deterministic_across_repeated_runs(package) -> None:
    assert canonical_plan_json(build_dry_run_plan(package)) == canonical_plan_json(
        build_dry_run_plan(package)
    )


def test_plan_exposes_non_executable_dependency_order(package) -> None:
    order = build_dry_run_plan(package)["execution_order"]
    assert order["mode"] == "dependency_order_proposal_only"
    assert order["executable"] is False
    assert [step["step"] for step in order["sequence"]] == list(range(1, 8))
    assert order["sequence"][3]["key"] == "quiz_versions_and_private_answer_keys"
    assert order["sequence"][3]["status"] == "blocked"


def test_offline_plan_does_not_claim_database_state_or_write(package, monkeypatch) -> None:
    def fail_write(*_args, **_kwargs):
        raise AssertionError("planner attempted filesystem output")

    monkeypatch.setattr(Path, "write_bytes", fail_write)
    monkeypatch.setattr(Path, "write_text", fail_write)
    generated = build_dry_run_plan(package)
    assert generated["database_access"] == "none"
    assert generated["writes_performed"] is False
    assert generated["snapshot_supplied"] is False
    assert generated["counts"]["operations_by_state"]["create"] == 0
    assert generated["counts"]["operations_by_state"]["update"] == 0


def test_adapter_has_no_database_client_or_production_import_dependency() -> None:
    source_path = REPO_ROOT / "backend/curriculum_contract/import_adapter.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    assert not ({"database", "pymongo", "motor", "routes_import", "services"} & imported_roots)


@pytest.mark.parametrize(
    ("current", "last_imported", "expected"),
    [
        (None, None, OperationState.CREATE),
        ("a" * 64, "a" * 64, OperationState.UPDATE),
        ("b" * 64, "a" * 64, OperationState.UNCHANGED),
        ("c" * 64, "a" * 64, OperationState.CONFLICT),
    ],
)
def test_read_only_snapshot_classification(current, last_imported, expected) -> None:
    desired = "b" * 64
    existing = (
        ExistingEntitySnapshot("f1-topic-example", current, last_imported) if current else None
    )
    assert classify_snapshot_state("f1-topic-example", desired, existing) == expected


def test_snapshot_extra_records_are_never_proposed_for_deletion(package) -> None:
    snapshot = {"db-only-ref": ExistingEntitySnapshot("db-only-ref", "a" * 64, "a" * 64)}
    generated = build_dry_run_plan(package, snapshot=snapshot)
    assert generated["snapshot_only_records"] == {
        "count": 1,
        "refs": ["db-only-ref"],
        "deletions_proposed": 0,
    }
    assert generated["deletions_proposed"] == 0


def test_editorial_pendings_and_relations_remain_explicit(plan) -> None:
    assert plan["counts"]["editorial_pendings"] == 214
    assert plan["relation_semantics"]["pending_quiz_or_content_classification"] == 35
    assert plan["counts"]["operations_by_state"]["pending_decision"] == 265


def test_answer_key_content_is_never_serialized_into_the_plan(package, plan) -> None:
    answer = next(
        block
        for phase in package.bundle.phases
        for block in phase.contract.blocks
        if isinstance(block, AnswerKeyBlock) and block.expected_answer
    )
    serialized = canonical_plan_json(plan)
    assert answer.expected_answer is not None
    assert answer.expected_answer not in serialized
    assert answer.explanation is None or answer.explanation not in serialized
    assert plan["security"]["answer_key_content_included"] is False


def test_quiz_format_incompatibility_is_reported_without_rewriting(package, plan) -> None:
    quizzes = [
        block
        for phase in package.bundle.phases
        for block in phase.contract.blocks
        if isinstance(block, QuizBlock)
    ]
    assert len(quizzes) == 506
    assert {quiz.format for quiz in quizzes} == {"other"}
    assert sum(len(quiz.options) for quiz in quizzes) == 0
    quiz_rows = plan["block_dispositions"]["quiz"]
    assert quiz_rows["blocked"] == 501
    assert quiz_rows["pending_decision"] == 5


def test_all_package_entities_are_planned_or_explicitly_blocked(plan) -> None:
    counts = plan["counts"]["operations_by_state"]
    assert sum(counts.values()) == 5344
    assert plan["counts"]["unique_entity_ids"] == 5344
    assert counts["pending_database_snapshot"] == 2063
    assert counts["blocked"] == 3016
    assert counts["pending_decision"] == 265
    assert plan["counts"]["projects"]["projects"] == 15
    assert plan["counts"]["shared_placements"] == 1001
    assert plan["counts"]["relations"] == 55
    assert plan["deletions_proposed"] == 0


def test_provenance_and_hashes_are_present_for_each_operation(plan) -> None:
    operations = plan["operations_detail"]
    assert len(operations) == 5344
    assert all(
        operation["entity_ref"].startswith(f"f{operation['phase']}-") for operation in operations
    )
    assert all(
        operation["source_file"]
        for operation in operations
        if operation["entity_type"] != "editorial_pending"
    )
    assert all(
        not operation["content_sha256"]
        for operation in operations
        if operation["entity_type"] == "block" and operation["private"]
    )


def test_progress_relations_are_not_reinterpreted_as_quiz_passed(plan) -> None:
    enforced_prerequisites = [
        operation
        for operation in plan["operations_detail"]
        if operation["entity_type"] == "relation"
        and operation["reason_code"] == "PREREQUISITE_KIND_NOT_EXPLICIT; DO_NOT_INFER_QUIZ_PASSED"
    ]
    assert len(enforced_prerequisites) == 35
    assert all(operation["operation"] == "pending_decision" for operation in enforced_prerequisites)
