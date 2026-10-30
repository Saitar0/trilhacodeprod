"""Deterministic, offline tests for canonical shared content projections."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from curriculum_contract.bulk_import import validate_import_bundle_json
from curriculum_contract.models import IntermediateContract
from curriculum_contract.shared_content import (
    PublicProjectionPolicyError,
    SharedContentReferenceError,
    SharedContentValidationError,
    build_shared_content_index,
    internal_projection_payload,
    public_projection_for_subject,
    public_projection_payload,
    serialize_internal_projection,
    serialize_public_projection,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "docs/courses/trilhacode/trilha-code-bulk-import.json"
EXPECTED_BUNDLE_SHA256 = "43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2"
SHARED_TYPE_COUNTS = {
    "practice": 180,
    "rubric": 90,
    "feedback": 90,
    "checklist": 26,
    "quiz": 17,
    "acceptance_criteria": 1,
    "flashcard": 2,
}
PUBLIC_FIELDS = {
    "quiz": {"title", "prompt", "format", "options"},
    "practice": {"prompt", "language", "starter_code"},
    "flashcard": {"front"},
}
WITHHELD_TYPES = {"rubric", "feedback", "checklist", "acceptance_criteria"}
PRIVATE_FIELD_NAMES = {
    "answer_key_ref",
    "correct_option_ref",
    "accepted_answers",
    "expected_answer",
    "explanation",
    "source_markdown",
    "acceptance",
    "back",
    "target_ref",
    "target_refs",
    "dimensions",
    "threshold",
    "source_file",
    "source_sha256",
    "manifest_ref",
    "source_role",
    "progress_scope",
}


@pytest.fixture(scope="module")
def bundle():
    return validate_import_bundle_json(BUNDLE_PATH.read_text(encoding="utf-8"))


def _contracts(bundle: Any) -> list[IntermediateContract]:
    return [phase.contract for phase in bundle.phases]


def _topic_with_multiple_placements(contract: IntermediateContract) -> str:
    counts = Counter(item.subject_ref for item in contract.shared_placements)
    return next(ref for ref, count in counts.items() if count > 1)


def _with_payload_change(contract: IntermediateContract, change: Any) -> IntermediateContract:
    payload = contract.model_dump(mode="json")
    change(payload)
    return IntermediateContract.model_validate(payload)


def _find_contract_with_placements(bundle: Any) -> IntermediateContract:
    return next(contract for contract in _contracts(bundle) if contract.shared_placements)


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_walk_keys(item))
    return keys


def test_bundle_contains_all_shared_entities_and_undecided_scopes(bundle: Any) -> None:
    contracts = _contracts(bundle)
    indexes = [build_shared_content_index(contract) for contract in contracts]
    block_refs = [ref for index in indexes for ref in index.shared_block_refs]
    placements = [item for contract in contracts for item in contract.shared_placements]
    consumers = {item.subject_ref for item in placements}

    assert len(block_refs) == 406
    assert len(set(block_refs)) == 406
    assert len(placements) == 1001
    assert len(consumers) == 284
    assert all(item.progress_scope == "undecided" for item in placements)
    assert sum(index.placement_count for index in indexes) == 1001


def test_seven_shared_types_are_accounted_for_without_private_output(bundle: Any) -> None:
    actual = Counter(
        block.type for contract in _contracts(bundle) for block in contract.blocks if block.shared
    )
    assert dict(actual) == SHARED_TYPE_COUNTS

    exposed = 0
    withheld = 0
    for contract in _contracts(bundle):
        index = build_shared_content_index(contract)
        for subject_ref in index.subject_refs:
            projection = public_projection_for_subject(index, subject_ref)
            for entry in projection.placements:
                if entry.block_type in WITHHELD_TYPES:
                    withheld += 1
                    assert entry.content is None
                else:
                    exposed += 1
                    assert entry.block_type in PUBLIC_FIELDS
                    assert entry.content is not None
                    assert set(entry.content) == PUBLIC_FIELDS[entry.block_type]
    assert exposed + withheld == 1001


@pytest.mark.parametrize(
    ("block_type", "is_public"),
    [
        ("practice", True),
        ("rubric", False),
        ("feedback", False),
        ("checklist", False),
        ("quiz", True),
        ("acceptance_criteria", False),
        ("flashcard", True),
    ],
)
def test_public_policy_is_explicit_for_each_shared_type(
    bundle: Any, block_type: str, is_public: bool
) -> None:
    selected: tuple[IntermediateContract, str] | None = None
    for contract in _contracts(bundle):
        blocks = {block.ref: block for block in contract.blocks}
        for placement in contract.shared_placements:
            if blocks[placement.block_ref].type == block_type:
                selected = (contract, placement.subject_ref)
                break
        if selected:
            break
    assert selected is not None, "expected shared type is missing from the bundle"

    contract, subject_ref = selected
    index = build_shared_content_index(contract)
    public = public_projection_for_subject(index, subject_ref)
    entry = next(item for item in public.placements if item.block_type == block_type)
    assert (entry.content is not None) is is_public
    if not is_public:
        assert entry.block_ref
        assert entry.placement_ref


def test_subject_resolution_preserves_identity_and_context_order(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    index = build_shared_content_index(contract)
    subject_ref = _topic_with_multiple_placements(contract)
    projection = index.for_subject(subject_ref)

    assert projection.subject_ref == subject_ref
    assert all(item["subject_ref"] == subject_ref for item in projection.placements)
    assert [item["order"] for item in projection.placements] == sorted(
        item["order"] for item in projection.placements
    )
    assert len(projection.canonical_blocks) == len(
        {item["block_ref"] for item in projection.placements}
    )
    assert all(item["block_ref"] in projection.canonical_blocks for item in projection.placements)
    assert all(
        projection.canonical_blocks[block_ref]["ref"] == block_ref
        for block_ref in projection.canonical_blocks
    )


def test_internal_projection_round_trips_refs_and_provenance_without_duplication(
    bundle: Any,
) -> None:
    for contract in _contracts(bundle):
        index = build_shared_content_index(contract)
        for subject_ref in index.subject_refs:
            projection = index.for_subject(subject_ref)
            payload = internal_projection_payload(projection)
            source_placements = {
                item.ref: item.model_dump(mode="json")
                for item in contract.shared_placements
                if item.subject_ref == subject_ref
            }
            source_blocks = {
                item.ref: item.model_dump(mode="json")
                for item in contract.blocks
                if item.shared
                and any(
                    placement.subject_ref == subject_ref and placement.block_ref == item.ref
                    for placement in contract.shared_placements
                )
            }
            projected_placements = {item["ref"]: item for item in payload["placements"]}
            projected_blocks = {item["ref"]: item for item in payload["canonical_blocks"]}

            if projected_placements != source_placements:
                raise AssertionError("Placement round-trip mismatch")
            if projected_blocks != source_blocks:
                raise AssertionError("Canonical block round-trip mismatch")
            assert len(projected_blocks) == len(payload["canonical_blocks"])
            assert all("provenance" in item for item in payload["placements"])
            assert all("provenance" in item for item in payload["canonical_blocks"])


def test_serialization_is_deterministic_for_reordered_source_collections(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    subject_ref = _topic_with_multiple_placements(contract)
    reversed_contract = contract.model_copy(
        update={
            "nodes": list(reversed(contract.nodes)),
            "blocks": list(reversed(contract.blocks)),
            "shared_placements": list(reversed(contract.shared_placements)),
        }
    )

    first = serialize_internal_projection(
        build_shared_content_index(contract).for_subject(subject_ref)
    )
    second = serialize_internal_projection(
        build_shared_content_index(reversed_contract).for_subject(subject_ref)
    )
    assert first == second

    public_first = serialize_public_projection(
        public_projection_for_subject(build_shared_content_index(contract), subject_ref)
    )
    public_second = serialize_public_projection(
        public_projection_for_subject(build_shared_content_index(reversed_contract), subject_ref)
    )
    assert public_first == public_second


def test_public_projection_fails_closed_and_omits_private_metadata(bundle: Any) -> None:
    for contract in _contracts(bundle):
        index = build_shared_content_index(contract)
        for subject_ref in index.subject_refs:
            payload = public_projection_payload(public_projection_for_subject(index, subject_ref))
            keys = _walk_keys(payload)
            assert not (keys & PRIVATE_FIELD_NAMES), "private field name escaped allowlist"


def test_reference_to_unknown_subject_is_rejected(bundle: Any) -> None:
    index = build_shared_content_index(_find_contract_with_placements(bundle))
    with pytest.raises(SharedContentReferenceError) as error:
        index.for_subject("f10-no-such-topic")
    assert error.value.code == "SHARED_SUBJECT_NOT_FOUND"


def test_non_topic_subject_is_rejected(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    placement = contract.shared_placements[0]
    non_topic_ref = next(
        node.ref for node in contract.nodes if node.ref == contract.nodes[-1].parent_ref
    )
    payload = contract.model_dump(mode="json")
    payload["shared_placements"][0]["subject_ref"] = non_topic_ref
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "SHARED_SUBJECT_NOT_FOUND" in str(error.value)
    assert placement.subject_ref != non_topic_ref


def test_broken_canonical_reference_is_rejected(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    payload = contract.model_dump(mode="json")
    payload["shared_placements"][0]["block_ref"] = "f10-missing-canonical"
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "SHARED_BLOCK_NOT_FOUND" in str(error.value)


def test_duplicate_placement_and_duplicate_block_subject_pair_are_rejected(
    bundle: Any,
) -> None:
    contract = _find_contract_with_placements(bundle)
    payload = contract.model_dump(mode="json")
    duplicate = dict(payload["shared_placements"][0])
    duplicate["ref"] = duplicate["ref"] + "-duplicate"
    payload["shared_placements"].append(duplicate)
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "DUPLICATE_PLACEMENT" in str(error.value)
    assert "DUPLICATE_ORDER" in str(error.value)


def test_non_shared_block_cannot_be_used_as_a_shared_target(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    payload = contract.model_dump(mode="json")
    placement = payload["shared_placements"][0]
    non_shared = next(block for block in payload["blocks"] if not block["shared"])
    placement["block_ref"] = non_shared["ref"]
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "SHARED_BLOCK_NOT_FOUND" in str(error.value)


def test_invalid_placement_provenance_is_rejected(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    payload = contract.model_dump(mode="json")
    payload["shared_placements"][0]["provenance"]["source_sha256"] = "invalid"
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "INVALID_SHA256" in str(error.value)


def test_duplicate_contextual_order_is_rejected(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    subject_ref = _topic_with_multiple_placements(contract)
    payload = contract.model_dump(mode="json")
    subject_items = [
        item for item in payload["shared_placements"] if item["subject_ref"] == subject_ref
    ]
    subject_items[1]["order"] = subject_items[0]["order"]
    altered = IntermediateContract.model_validate(payload)

    with pytest.raises(SharedContentValidationError) as error:
        build_shared_content_index(altered)
    assert "DUPLICATE_ORDER" in str(error.value)


def test_unknown_public_type_is_rejected_without_echoing_content(
    bundle: Any,
) -> None:
    contract = _find_contract_with_placements(bundle)
    index = build_shared_content_index(contract)
    projection = index.for_subject(_topic_with_multiple_placements(contract))
    target_ref = projection.placements[0]["block_ref"]
    altered_blocks = dict(projection.canonical_blocks)
    original = dict(altered_blocks[target_ref])
    original["type"] = "unapproved_type"
    original["sensitive_marker"] = "PRIVATE_TEST_SENTINEL"
    altered_blocks[target_ref] = original
    altered_projection = replace(
        projection,
        canonical_blocks=altered_blocks,
    )

    with pytest.raises(PublicProjectionPolicyError) as error:
        from curriculum_contract.shared_content import public_projection_from_snapshot

        public_projection_from_snapshot(altered_projection)
    assert error.value.code == "PUBLIC_TYPE_POLICY_UNDEFINED"
    assert "PRIVATE_TEST_SENTINEL" not in str(error.value)


def test_input_contract_and_bundle_bytes_are_not_mutated(bundle: Any) -> None:
    original_bytes = BUNDLE_PATH.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    assert original_hash == EXPECTED_BUNDLE_SHA256

    for contract in _contracts(bundle):
        before = contract.model_dump(mode="json")
        index = build_shared_content_index(contract)
        for subject_ref in index.subject_refs:
            projection = index.for_subject(subject_ref)
            serialize_internal_projection(projection)
            serialize_public_projection(public_projection_for_subject(index, subject_ref))
        if contract.model_dump(mode="json") != before:
            raise AssertionError("Contract input was mutated")

    assert hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest() == EXPECTED_BUNDLE_SHA256


def test_all_progress_scopes_are_preserved_exactly_in_internal_projection(
    bundle: Any,
) -> None:
    for contract in _contracts(bundle):
        index = build_shared_content_index(contract)
        for subject_ref in index.subject_refs:
            projection = index.for_subject(subject_ref)
            projected = internal_projection_payload(projection)
            scopes = {item["ref"]: item["progress_scope"] for item in projected["placements"]}
            expected = {
                item.ref: item.progress_scope
                for item in contract.shared_placements
                if item.subject_ref == subject_ref
            }
            assert scopes == expected
            assert all(scope == "undecided" for scope in scopes.values())


def test_immutable_projection_containers_reject_mutation(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    index = build_shared_content_index(contract)
    projection = index.for_subject(_topic_with_multiple_placements(contract))

    with pytest.raises(TypeError):
        projection.subject["title"] = "mutated"  # type: ignore[index]
    with pytest.raises(TypeError):
        projection.placements[0]["order"] = 999  # type: ignore[index]
    with pytest.raises(TypeError):
        projection.canonical_blocks["new-ref"] = {}  # type: ignore[index]


def test_unknown_type_does_not_change_source_validation_policy(bundle: Any) -> None:
    contract = _find_contract_with_placements(bundle)
    payload = contract.model_dump(mode="json")
    payload["blocks"][0]["type"] = "unknown_type"
    with pytest.raises(Exception):
        IntermediateContract.model_validate(payload)
