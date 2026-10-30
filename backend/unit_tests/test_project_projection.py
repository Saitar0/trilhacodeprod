"""Offline tests for lossless, non-operational project projections."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from curriculum_contract.bulk_import import validate_import_bundle_json
from curriculum_contract.models import (
    AcceptanceCriteriaBlock,
    ChecklistBlock,
    IntermediateContract,
    ProjectSpec,
    RubricBlock,
    canonical_json,
)
from curriculum_contract.projects import (
    ProjectProjectionValidationError,
    ProjectReferenceError,
    build_project_index,
    public_project_payload,
    public_project_projection,
    serialize_internal_project,
    serialize_project_index,
    serialize_public_project,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "docs/courses/trilhacode/trilha-code-bulk-import.json"
EXPECTED_BUNDLE_SHA256 = "43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2"


@pytest.fixture(scope="module")
def bundle_bytes() -> bytes:
    return BUNDLE_PATH.read_bytes()


@pytest.fixture(scope="module")
def parsed_bundle(bundle_bytes: bytes):
    return validate_import_bundle_json(bundle_bytes.decode("utf-8"))


@pytest.fixture(scope="module")
def contracts(parsed_bundle: Any) -> tuple[IntermediateContract, ...]:
    return tuple(phase.contract for phase in parsed_bundle.phases)


@pytest.fixture(scope="module")
def project_index(contracts: tuple[IntermediateContract, ...]):
    return build_project_index(contracts)


def _plain_contract(contract: IntermediateContract) -> dict[str, Any]:
    return contract.model_dump(mode="json")


def _project_owner(contracts: tuple[IntermediateContract, ...], project_ref: str):
    for contract in contracts:
        for project in contract.projects:
            if project.ref == project_ref:
                return contract, project
    raise AssertionError("expected project fixture was not found")


def _diagnostic_codes(error: ProjectProjectionValidationError) -> set[str]:
    return {item.code for item in error.diagnostics}


def _synthetic_private_fixture() -> dict[str, Any]:
    """Sanitized fixture uses synthetic markers, never source answers or secrets."""
    source_path = "Conteudos/Fase_1/projeto-fixture.md"
    source_hash = "a" * 64

    def provenance() -> dict[str, str]:
        return {
            "source_file": source_path,
            "source_sha256": source_hash,
            "manifest_ref": "f1-projeto-fixture",
            "source_role": "project_fixture",
        }

    phase = "f1-fase-fixture"
    module = "f1-modulo-fixture"
    unit = "f1-unidade-fixture"
    topic = "f1-assunto-fixture"
    project = "f1-projeto-fixture"
    delivery = "f1-entrega-fixture"
    project_rubric = "f1-rubrica-projeto-fixture"
    step_rubric = "f1-rubrica-entrega-fixture"
    project_checklist = "f1-checklist-projeto-fixture"
    step_checklist = "f1-checklist-entrega-fixture"
    acceptance = "f1-aceite-entrega-fixture"
    context_block = "f1-conteudo-entrega-fixture"

    def node(ref: str, kind: str, parent_ref: str | None, order: int) -> dict[str, Any]:
        return {
            "ref": ref,
            "kind": kind,
            "parent_ref": parent_ref,
            "title": "Título de fixture",
            "order": order,
            "status": "draft",
            "estimated_minutes": None,
            "source_metadata": {},
            "tags": [],
            "provenance": provenance(),
        }

    def checklist(ref: str, owner_ref: str, order: int, marker: str) -> dict[str, Any]:
        return {
            "ref": ref,
            "type": "checklist",
            "owner_ref": owner_ref,
            "order": order,
            "title": "Checklist sintético",
            "status": "draft",
            "shared": False,
            "provenance": provenance(),
            "items": [{"ref": "item-fixture", "text": marker, "checked": None}],
            "source_markdown": "FIXTURE_PRIVATE_CHECKLIST_MARKDOWN_MARKER",
            "source_item_labels": [],
        }

    def rubric(ref: str, owner_ref: str, target_ref: str, order: int) -> dict[str, Any]:
        return {
            "ref": ref,
            "type": "rubric",
            "owner_ref": owner_ref,
            "order": order,
            "title": "Rubrica sintética",
            "status": "draft",
            "shared": False,
            "provenance": provenance(),
            "target_ref": target_ref,
            "target_refs": [target_ref],
            "scale": {"minimum": 0, "maximum": 2},
            "dimensions": [
                {
                    "ref": "dimension-fixture",
                    "title": "FIXTURE_PRIVATE_RUBRIC_MARKER",
                    "weight": 1.0,
                    "descriptors": {
                        "0": "FIXTURE_PRIVATE_RUBRIC_LOW_MARKER",
                        "2": "FIXTURE_PRIVATE_RUBRIC_HIGH_MARKER",
                    },
                }
            ],
            "threshold": None,
            "source_markdown": "FIXTURE_PRIVATE_RUBRIC_MARKER",
            "source_item_labels": [],
        }

    return {
        "schema_version": "trilhacode.intermediate/1.2",
        "source": {
            "manifest_path": "docs/migracao/projeto-fixture.yml",
            "manifest_sha256": source_hash,
            "source_revision": "offline-fixture-revision",
            "converter_version": "fixture-only",
        },
        "nodes": [
            node(phase, "phase", None, 0),
            node(module, "module", phase, 0),
            node(unit, "submodule", module, 0),
            node(topic, "topic", unit, 0),
        ],
        "blocks": [
            rubric(project_rubric, project, project, 0),
            checklist(
                project_checklist,
                project,
                1,
                "FIXTURE_PRIVATE_PROJECT_CHECKLIST_MARKER",
            ),
            {
                "ref": acceptance,
                "type": "acceptance_criteria",
                "owner_ref": delivery,
                "order": 0,
                "title": "Aceite sintético",
                "status": "draft",
                "shared": False,
                "provenance": provenance(),
                "delivery_ref": delivery,
                "milestone_ref": None,
                "practice_ref": None,
                "items": [
                    {
                        "ref": "aceite-fixture",
                        "text": "FIXTURE_PRIVATE_ACCEPTANCE_MARKER",
                        "checked": None,
                    }
                ],
                "body": "FIXTURE_PRIVATE_ACCEPTANCE_BODY_MARKER",
                "source_item_labels": [],
                "related_refs": [],
            },
            checklist(
                step_checklist,
                delivery,
                1,
                "FIXTURE_PRIVATE_STEP_CHECKLIST_MARKER",
            ),
            rubric(step_rubric, delivery, delivery, 2),
            {
                "ref": context_block,
                "type": "theory",
                "owner_ref": delivery,
                "order": 3,
                "title": "Contexto instrucional sintético",
                "status": "draft",
                "shared": False,
                "provenance": provenance(),
                "body": "Texto instrucional que não contém informação privada.",
                "microtopic": None,
            },
        ],
        "relations": [],
        "shared_placements": [],
        "projects": [
            {
                "ref": project,
                "unit_ref": unit,
                "title": "Projeto sintético",
                "scope": "Escopo instrucional sintético.",
                "has_formal_deliveries": True,
                "deliveries": [
                    {
                        "ref": delivery,
                        "title": "Entrega sintética",
                        "body": "Instrução sintética em Markdown.\n",
                        "order": 0,
                        "acceptance_refs": [acceptance],
                        "checklist_refs": [step_checklist],
                        "rubric_refs": [step_rubric],
                        "content_refs": [context_block],
                        "provenance": provenance(),
                    }
                ],
                "has_formal_milestones": False,
                "milestones": [],
                "variants": [],
                "checklist_refs": [project_checklist],
                "rubric_refs": [project_rubric],
                "stack_options": [],
                "stack_selected": None,
                "source_metadata": {"fixture": True},
                "provenance": provenance(),
            }
        ],
        "editorial_pendings": [],
        "vault_root_confirmed": False,
    }


def test_full_bundle_projects_and_formal_steps_are_preserved(project_index, contracts) -> None:
    projects = [project for contract in contracts for project in contract.projects]
    deliveries = [step for project in projects for step in project.deliveries]
    milestones = [step for project in projects for step in project.milestones]

    assert project_index.project_count == 15
    assert len(project_index.project_refs) == 15
    assert len(deliveries) == 20
    assert len(milestones) == 36
    assert sum(bool(project.deliveries) for project in projects) == 5
    assert sum(bool(project.milestones) for project in projects) == 9
    assert sum(not project.deliveries and not project.milestones for project in projects) == 1
    assert sum(bool(project.deliveries) and not project.milestones for project in projects) == 5
    assert sum(bool(project.milestones) and not project.deliveries for project in projects) == 9
    assert not any(project.deliveries and project.milestones for project in projects)
    all_refs = [project.ref for project in projects]
    all_refs.extend(step.ref for step in (*deliveries, *milestones))
    assert len(all_refs) == len(set(all_refs))


def test_projects_are_owned_by_existing_submodule_nodes(project_index, contracts) -> None:
    nodes = {node.ref: node for contract in contracts for node in contract.nodes}
    for project_ref in project_index.project_refs:
        projection = project_index.for_project(project_ref)
        owner_ref = str(projection.project["unit_ref"])
        assert nodes[owner_ref].kind == "submodule"
        assert projection.owner_unit["ref"] == owner_ref
        assert projection.owner_unit["kind"] == "submodule"
        assert project_index.for_unit(owner_ref)


def test_project_lookup_is_stable_and_missing_refs_fail_closed(project_index) -> None:
    ref = project_index.project_refs[0]
    assert project_index.for_project(ref) is project_index.for_project(ref)
    with pytest.raises(ProjectReferenceError) as missing:
        project_index.for_project("f10-projeto-inexistente")
    assert missing.value.code == "PROJECT_NOT_FOUND"


def test_unit_lookup_rejects_topics_and_preserves_empty_project_units(
    project_index, contracts
) -> None:
    topic_ref = next(
        node.ref for contract in contracts for node in contract.nodes if node.kind == "topic"
    )
    with pytest.raises(ProjectReferenceError) as wrong_kind:
        project_index.for_unit(topic_ref)
    assert wrong_kind.value.code == "PROJECT_UNIT_NOT_SUBMODULE"

    no_project_unit = next(
        node.ref
        for contract in contracts
        for node in contract.nodes
        if node.kind == "submodule" and not project_index._projects_by_unit.get(node.ref)
    )
    assert project_index.for_unit(no_project_unit) == ()


def test_delivery_and_milestone_order_is_deterministic(project_index) -> None:
    for project_ref in project_index.project_refs:
        project = project_index.for_project(project_ref).project
        for field in ("deliveries", "milestones", "variants"):
            steps = project[field]
            keys = [(item["order"], item["ref"]) for item in steps]
            assert keys == sorted(keys)
        assert not (
            set(item["ref"] for item in project["deliveries"])
            & set(item["ref"] for item in project["milestones"])
        )


def test_internal_projection_round_trips_project_text_references_and_provenance(
    project_index, contracts
) -> None:
    originals = {
        project.ref: project.model_dump(mode="json")
        for contract in contracts
        for project in contract.projects
    }
    original_blocks = {
        block.ref: block.model_dump(mode="json")
        for contract in contracts
        for block in contract.blocks
    }
    for project_ref in project_index.project_refs:
        payload = json.loads(serialize_internal_project(project_index.for_project(project_ref)))
        restored = ProjectSpec.model_validate(payload["project"])
        assert restored.model_dump(mode="json") == originals[project_ref], (
            "project fields, Markdown text, references, or provenance changed"
        )
        assert payload["owner_unit"]["ref"] == restored.unit_ref
        assert payload["source_manifest"]["manifest_path"]
        assert {block["ref"] for block in payload["referenced_blocks"]} == set(
            project_index.for_project(project_ref).referenced_blocks
        )
        assert all(
            block == original_blocks[block["ref"]] for block in payload["referenced_blocks"]
        ), "project-related Markdown, references, or block provenance changed"


def test_project_index_serialization_is_deterministic_across_phase_order(
    contracts, project_index
) -> None:
    forward = serialize_project_index(project_index)
    reversed_index = build_project_index(tuple(reversed(contracts)))
    reverse = serialize_project_index(reversed_index)
    assert forward == reverse, "project index serialization depends on input phase order"
    assert forward == serialize_project_index(project_index)


def test_stack_options_and_unselected_state_are_preserved_without_variant_inference(
    contracts, project_index
) -> None:
    projects = [project for contract in contracts for project in contract.projects]
    assert sum(len(project.stack_options) for project in projects) == 8
    assert sum(bool(project.stack_options) for project in projects) == 2
    assert all(project.stack_selected is None for project in projects)
    assert all(project.variants == [] for project in projects)
    for project in projects:
        payload = json.loads(serialize_internal_project(project_index.for_project(project.ref)))
        projected = ProjectSpec.model_validate(payload["project"])
        assert projected.stack_options == project.stack_options
        assert projected.stack_selected is None
        assert projected.variants == []


def test_project_block_roles_resolve_to_the_expected_typed_blocks(contracts, project_index) -> None:
    expected = {"acceptance_criteria": 16, "checklist": 36, "rubric": 13}
    observed: dict[str, int] = {}
    for project_ref in project_index.project_refs:
        projection = project_index.for_project(project_ref)
        internal_payload = json.loads(serialize_internal_project(projection))
        for block in internal_payload["referenced_blocks"]:
            block_type = str(block["type"])
            if block_type == "acceptance_criteria":
                observed[block_type] = observed.get(block_type, 0) + 1
                assert AcceptanceCriteriaBlock.model_validate(block).ref == block["ref"]
            elif block_type == "checklist":
                observed[block_type] = observed.get(block_type, 0) + 1
                assert ChecklistBlock.model_validate(block).ref == block["ref"]
            elif block_type == "rubric":
                observed[block_type] = observed.get(block_type, 0) + 1
                assert RubricBlock.model_validate(block).ref == block["ref"]
    assert observed == expected
    assert sum(
        len(project_index.for_project(ref).referenced_blocks) for ref in project_index.project_refs
    ) >= sum(expected.values())


def test_reference_ids_are_deduplicated_in_each_project_snapshot(project_index) -> None:
    for project_ref in project_index.project_refs:
        snapshot = project_index.for_project(project_ref)
        assert len(snapshot.referenced_blocks) == len(set(snapshot.referenced_blocks))


def test_public_projection_uses_allowlist_and_omits_private_assessments(
    project_index, contracts
) -> None:
    target_ref = next(
        ref
        for ref in project_index.project_refs
        if project_index.for_project(ref).referenced_blocks
    )
    snapshot = project_index.for_project(target_ref)
    payload = public_project_payload(public_project_projection(snapshot))
    encoded = serialize_public_project(public_project_projection(snapshot))

    assert set(payload) == {
        "project_ref",
        "unit_ref",
        "title",
        "scope",
        "deliveries",
        "milestones",
    }
    assert all(
        set(step) == {"ref", "title", "body", "order"}
        for step in (*payload["deliveries"], *payload["milestones"])
    )
    forbidden_fields = {
        "source_metadata",
        "provenance",
        "checklist_refs",
        "rubric_refs",
        "acceptance_refs",
        "content_refs",
        "stack_options",
        "stack_selected",
        "variants",
        "score",
        "passed",
        "submission",
        "answer_key_ref",
        "correct_option_ref",
        "explanation",
        "feedback",
    }
    assert not (forbidden_fields & set(payload))
    assert all(name not in encoded for name in forbidden_fields)
    assert len(snapshot.referenced_blocks) > 0


def test_sanitized_fixture_private_project_material_never_enters_public_payload() -> None:
    index = build_project_index(_synthetic_private_fixture())
    public = public_project_payload(
        public_project_projection(index.for_project("f1-projeto-fixture"))
    )
    encoded = serialize_public_project(
        public_project_projection(index.for_project("f1-projeto-fixture"))
    )
    private_markers = (
        "FIXTURE_PRIVATE_RUBRIC_MARKER",
        "FIXTURE_PRIVATE_PROJECT_CHECKLIST_MARKER",
        "FIXTURE_PRIVATE_STEP_CHECKLIST_MARKER",
        "FIXTURE_PRIVATE_CHECKLIST_MARKDOWN_MARKER",
        "FIXTURE_PRIVATE_ACCEPTANCE_MARKER",
        "FIXTURE_PRIVATE_ACCEPTANCE_BODY_MARKER",
        "FIXTURE_PRIVATE_RUBRIC_LOW_MARKER",
        "FIXTURE_PRIVATE_RUBRIC_HIGH_MARKER",
    )
    assert all(marker not in encoded for marker in private_markers), (
        "public project projection included a synthetic private assessment marker"
    )
    assert public["deliveries"][0]["body"] == "Instrução sintética em Markdown.\n"


def test_public_projection_preserves_only_source_instruction_fields(project_index) -> None:
    for project_ref in project_index.project_refs:
        snapshot = project_index.for_project(project_ref)
        public = public_project_payload(public_project_projection(snapshot))
        assert public["project_ref"] == snapshot.project["ref"]
        assert public["unit_ref"] == snapshot.project["unit_ref"]
        assert public["title"] == snapshot.project["title"]
        assert public["scope"] == snapshot.project["scope"]
        for field in ("deliveries", "milestones"):
            original = snapshot.project[field]
            rendered = public[field]
            assert len(original) == len(rendered)
            assert all(
                (out["ref"], out["title"], out["body"], out["order"])
                == (src["ref"], src["title"], src["body"], src["order"])
                for src, out in zip(original, rendered, strict=True)
            )


def test_no_formal_steps_are_not_replaced_by_generated_steps(project_index, contracts) -> None:
    project = next(
        project
        for contract in contracts
        for project in contract.projects
        if not project.deliveries and not project.milestones
    )
    projection = project_index.for_project(project.ref)
    assert projection.project["has_formal_deliveries"] is False
    assert projection.project["has_formal_milestones"] is False
    assert projection.project["deliveries"] == ()
    assert projection.project["milestones"] == ()
    public = public_project_payload(public_project_projection(projection))
    assert public["deliveries"] == []
    assert public["milestones"] == []


def test_duplicate_project_step_reference_list_is_rejected(contracts) -> None:
    raw = _plain_contract(contracts[0])
    project = next(
        project
        for project in raw["projects"]
        if any(step["checklist_refs"] for step in (*project["deliveries"], *project["milestones"]))
    )
    step = next(
        step for step in (*project["deliveries"], *project["milestones"]) if step["checklist_refs"]
    )
    step["checklist_refs"].append(step["checklist_refs"][0])
    with pytest.raises(ProjectProjectionValidationError) as rejected:
        build_project_index(raw)
    assert "PROJECT_REFERENCE_DUPLICATE" in _diagnostic_codes(rejected.value)


def test_missing_project_block_reference_is_rejected(contracts) -> None:
    raw = next(
        _plain_contract(contract)
        for contract in contracts
        if any(project.rubric_refs for project in contract.projects)
    )
    project = next(project for project in raw["projects"] if project["rubric_refs"])
    project["rubric_refs"][0] = "f10-rubrica-ausente"
    with pytest.raises(ProjectProjectionValidationError) as rejected:
        build_project_index(raw)
    assert {
        "PROJECT_RUBRIC_REFERENCE_INVALID",
        "PROJECT_BLOCK_REFERENCE_NOT_FOUND",
    } & _diagnostic_codes(rejected.value)


def test_incompatible_project_block_type_is_rejected(contracts) -> None:
    raw = next(
        _plain_contract(contract)
        for contract in contracts
        if any(project.rubric_refs for project in contract.projects)
    )
    project = next(project for project in raw["projects"] if project["rubric_refs"])
    other_block_ref = next(block["ref"] for block in raw["blocks"] if block["type"] != "rubric")
    project["rubric_refs"][0] = other_block_ref
    with pytest.raises(ProjectProjectionValidationError) as rejected:
        build_project_index(raw)
    assert "PROJECT_RUBRIC_REFERENCE_INVALID" in _diagnostic_codes(rejected.value)


def test_project_must_reference_an_existing_submodule(contracts) -> None:
    raw = _plain_contract(contracts[0])
    raw["projects"][0]["unit_ref"] = "f10-unit-absent"
    with pytest.raises(ProjectProjectionValidationError) as rejected:
        build_project_index(raw)
    assert "PROJECT_UNIT_INVALID" in _diagnostic_codes(rejected.value)


def test_duplicate_ids_across_phase_contracts_are_rejected(contracts) -> None:
    duplicate_contract = copy.deepcopy(contracts[0])
    with pytest.raises(ProjectProjectionValidationError) as rejected:
        build_project_index((contracts[0], duplicate_contract))
    assert "PROJECT_PACKAGE_ENTITY_ID_DUPLICATE" in _diagnostic_codes(rejected.value)


def test_project_snapshot_is_detached_from_mutable_source_contract(contracts) -> None:
    mutable = copy.deepcopy(contracts[0])
    original_ref = mutable.projects[0].ref
    index = build_project_index(mutable)
    mutable.projects[0].title = "mutated only in caller object"
    assert index.for_project(original_ref).project["title"] != mutable.projects[0].title


def test_bundle_bytes_and_contract_objects_are_not_mutated(bundle_bytes, parsed_bundle) -> None:
    before = canonical_json(parsed_bundle.phases[0].contract)
    raw_sha = hashlib.sha256(bundle_bytes).hexdigest()
    assert raw_sha == EXPECTED_BUNDLE_SHA256
    build_project_index(tuple(phase.contract for phase in parsed_bundle.phases))
    after = canonical_json(parsed_bundle.phases[0].contract)
    assert before == after, "project projection mutated an input contract"
    assert hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest() == EXPECTED_BUNDLE_SHA256


def test_internal_and_public_projections_have_distinct_field_surfaces(project_index) -> None:
    for project_ref in project_index.project_refs:
        internal = project_index.for_project(project_ref)
        public = public_project_payload(public_project_projection(internal))
        internal_payload = json.loads(serialize_internal_project(internal))
        assert "source_metadata" in internal_payload["project"]
        assert "source_metadata" not in public
        assert "referenced_blocks" in internal_payload
        assert "referenced_blocks" not in public
        assert not any(
            field in public
            for field in ("published", "submission", "grade", "passed", "attempts", "progress")
        )


def test_internal_snapshot_reference_block_keys_match_actual_refs(project_index) -> None:
    for project_ref in project_index.project_refs:
        snapshot = project_index.for_project(project_ref)
        project = snapshot.project
        expected_refs = set(project["checklist_refs"]) | set(project["rubric_refs"])
        for step in (*project["deliveries"], *project["milestones"]):
            for field in ("acceptance_refs", "checklist_refs", "rubric_refs", "content_refs"):
                expected_refs.update(step[field])
        assert set(snapshot.referenced_blocks) == expected_refs


def test_projection_roundtrip_does_not_duplicate_steps_as_blocks(project_index) -> None:
    for project_ref in project_index.project_refs:
        payload = json.loads(serialize_internal_project(project_index.for_project(project_ref)))
        step_refs = {
            step["ref"]
            for kind in ("deliveries", "milestones")
            for step in payload["project"][kind]
        }
        block_refs = {block["ref"] for block in payload["referenced_blocks"]}
        assert not (step_refs & block_refs), "a project step was recast as a generic content block"


def test_contract_project_models_are_reused_without_new_version_fields(project_index) -> None:
    for project_ref in project_index.project_refs:
        payload = internal_project_payload_for_test(project_index.for_project(project_ref))
        project = ProjectSpec.model_validate(payload["project"])
        assert project.ref == project_ref
        assert set(ProjectSpec.model_fields) == set(payload["project"])
        assert "project_version" not in payload["project"]
        assert "published_at" not in payload["project"]


def internal_project_payload_for_test(projection):
    # Local import keeps assertions on the public/private surfaces explicit.
    from curriculum_contract.projects import internal_project_payload

    return internal_project_payload(projection)
