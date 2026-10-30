"""Database-free contract and security tests for 14H.3B editorial persistence."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from curriculum_contract.editorial_persistence import (
    EDITORIAL_SCHEMA_VERSION,
    EditorialAuthorizationError,
    EditorialHead,
    EditorialIdentity,
    EditorialOperationStatus,
    EditorialPersistenceStore,
    EditorialPrincipal,
    EditorialRevisionMetadata,
    EditorialValidationError,
    PinnedBlockReference,
    StoredBlockPayload,
    StoredPlacementPayload,
    StoredProjectPayload,
    _mongo_doc,
    _require_expected_head_pair,
    _validate_block_provenance,
    _validate_placement_provenance,
    _validate_project_provenance,
    canonical_editorial_sha256,
    hash_identity,
)
from curriculum_contract.models import (
    AnswerKeyBlock,
    ProjectDelivery,
    ProjectMilestone,
    ProjectSpec,
    ProjectVariant,
    SharedPlacement,
    SourceProvenance,
    TheoryBlock,
)


def provenance(source_id: str = "SOURCE-1") -> SourceProvenance:
    return SourceProvenance(
        source_file="docs/fixtures/editorial_synthetic.md",
        source_sha256="a" * 64,
        manifest_ref="fixture-manifest",
        source_role="synthetic-test",
        source_id=source_id,
    )


def block(ref: str = "f1-shared-fixture") -> TheoryBlock:
    return TheoryBlock(
        ref=ref,
        type="theory",
        owner_ref="f1-topic-fixture",
        order=2,
        title="Synthetic shared block",
        status="draft",
        shared=True,
        provenance=provenance(),
        body="SYNTHETIC_EDITORIAL_BODY",
        microtopic=None,
    )


def placement(ref: str = "f1-placement-fixture") -> SharedPlacement:
    return SharedPlacement(
        ref=ref,
        block_ref="f1-shared-fixture",
        subject_ref="f1-topic-fixture",
        order=1,
        progress_scope="undecided",
        provenance=provenance(),
    )


def project() -> ProjectSpec:
    return ProjectSpec(
        ref="f1-project-fixture",
        unit_ref="f1-submodule-fixture",
        title="Synthetic project",
        scope="SYNTHETIC_PROJECT_SCOPE",
        has_formal_deliveries=True,
        deliveries=[
            ProjectDelivery(
                ref="f1-delivery-fixture",
                title="Synthetic delivery",
                body="SYNTHETIC_DELIVERY_BODY",
                order=1,
                acceptance_refs=[],
                checklist_refs=[],
                rubric_refs=[],
                content_refs=["f1-shared-fixture"],
                provenance=provenance("DELIVERY-1"),
            )
        ],
        has_formal_milestones=True,
        milestones=[
            ProjectMilestone(
                ref="f1-milestone-fixture",
                title="Synthetic milestone",
                body="SYNTHETIC_MILESTONE_BODY",
                order=2,
                acceptance_refs=[],
                checklist_refs=[],
                rubric_refs=[],
                content_refs=[],
                provenance=provenance("MILESTONE-1"),
            )
        ],
        variants=[],
        checklist_refs=[],
        rubric_refs=[],
        stack_options=["synthetic-stack-a", "synthetic-stack-b"],
        stack_selected=None,
        source_metadata={"fixture": "synthetic"},
        provenance=provenance("PROJECT-1"),
    )


def test_identity_keeps_canonical_block_and_placement_separate() -> None:
    block_identity = EditorialIdentity(
        entity_kind="block",
        entity_ref="f1-shared-fixture",
        block_type="theory",
        owner_ref="f1-topic-fixture",
    )
    placement_identity = EditorialIdentity(
        entity_kind="placement",
        entity_ref="f1-placement-fixture",
        block_ref="f1-shared-fixture",
        subject_ref="f1-topic-fixture",
    )

    assert block_identity.entity_ref != placement_identity.entity_ref
    assert placement_identity.block_ref == block_identity.entity_ref
    assert hash_identity(block_identity) != hash_identity(placement_identity)


def test_identity_rejects_fields_from_other_entity_kinds() -> None:
    with pytest.raises(ValidationError):
        EditorialIdentity(
            entity_kind="placement",
            entity_ref="f1-placement-fixture",
            block_ref="f1-shared-fixture",
            subject_ref="f1-topic-fixture",
            unit_ref="f1-submodule-fixture",
        )


def test_canonical_payload_hash_is_stable_and_preserves_array_order() -> None:
    first = {"b": ["second", "first"], "a": {"z": 1, "x": 2}}
    reordered_keys = {"a": {"x": 2, "z": 1}, "b": ["second", "first"]}
    reordered_array = {"a": {"x": 2, "z": 1}, "b": ["first", "second"]}

    assert canonical_editorial_sha256(first) == canonical_editorial_sha256(reordered_keys)
    assert canonical_editorial_sha256(first) != canonical_editorial_sha256(reordered_array)


def test_revision_ids_are_validated_as_sha256() -> None:
    identity = EditorialIdentity(
        entity_kind="block",
        entity_ref="f1-shared-fixture",
        block_type="theory",
        owner_ref="f1-topic-fixture",
    )
    metadata = EditorialRevisionMetadata(
        entity_kind="block",
        entity_ref=identity.entity_ref,
        identity=identity,
        identity_sha256=hash_identity(identity),
        revision_id="b" * 64,
        revision_no=1,
        content_sha256="c" * 64,
        created_at=datetime.now(UTC),
        created_by="editor-synthetic",
    )
    assert metadata.storage_schema_version == EDITORIAL_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        EditorialRevisionMetadata.model_validate(
            {**metadata.model_dump(mode="python"), "revision_id": "not-a-hash"}
        )


def test_head_uses_external_reference_and_compare_and_swap_revision() -> None:
    identity = EditorialIdentity(
        entity_kind="block",
        entity_ref="f1-shared-fixture",
        block_type="theory",
        owner_ref="f1-topic-fixture",
    )
    head = EditorialHead(
        entity_kind="block",
        entity_ref=identity.entity_ref,
        identity=identity,
        identity_sha256=hash_identity(identity),
        current_revision_id="d" * 64,
        revision_no=2,
        updated_at=datetime.now(UTC),
        updated_by="editor-synthetic",
    )
    assert head.entity_ref == "f1-shared-fixture"
    assert head.current_revision_id == "d" * 64
    with pytest.raises(ValidationError):
        EditorialHead.model_validate(
            {
                **head.model_dump(mode="python"),
                "unexpected": "field",
            }
        )


def test_payload_schemas_preserve_source_types_without_copying_placement_content() -> None:
    source_block = block()
    source_placement = placement()
    project_source = project()
    block_payload = StoredBlockPayload(
        entity_kind="block",
        entity_ref=source_block.ref,
        revision_id="e" * 64,
        revision_no=1,
        content_sha256="f" * 64,
        block=source_block,
    )
    placement_payload = StoredPlacementPayload(
        entity_kind="placement",
        entity_ref=source_placement.ref,
        revision_id="1" * 64,
        revision_no=1,
        content_sha256="2" * 64,
        placement=source_placement,
    )
    project_payload = StoredProjectPayload(
        entity_kind="project",
        entity_ref=project_source.ref,
        revision_id="3" * 64,
        revision_no=1,
        content_sha256="4" * 64,
        project=project_source,
        pinned_blocks=[
            PinnedBlockReference(
                block_ref="f1-shared-fixture",
                resolution="unresolved",
                roles=["step_content"],
            )
        ],
    )

    assert "block" in block_payload.model_dump(mode="json")
    assert "block" not in placement_payload.model_dump(mode="json")
    assert placement_payload.placement.progress_scope == "undecided"
    assert [step.ref for step in project_payload.project.deliveries] == ["f1-delivery-fixture"]
    assert [step.ref for step in project_payload.project.milestones] == ["f1-milestone-fixture"]
    assert project_payload.project.stack_selected is None
    assert project_payload.project.variants == []


def test_project_pins_allow_explicit_unresolved_reference_without_fake_version() -> None:
    pending = PinnedBlockReference(
        block_ref="f1-shared-fixture",
        resolution="unresolved",
        roles=["step_content"],
    )
    assert pending.revision_id is None
    with pytest.raises(ValidationError):
        PinnedBlockReference(
            block_ref="f1-shared-fixture",
            resolution="unresolved",
            revision_id="5" * 64,
            revision_no=1,
            content_sha256="6" * 64,
            block_type="theory",
            roles=["step_content"],
        )


def test_project_pin_requires_exact_revision_metadata_when_resolved() -> None:
    pinned = PinnedBlockReference(
        block_ref="f1-shared-fixture",
        resolution="pinned",
        revision_id="6" * 64,
        revision_no=3,
        content_sha256="7" * 64,
        block_type="theory",
        roles=["step_content"],
    )
    assert pinned.revision_no == 3
    with pytest.raises(ValidationError):
        PinnedBlockReference(
            block_ref="f1-shared-fixture",
            resolution="pinned",
            revision_id="6" * 64,
            roles=["step_content"],
        )


def test_public_payload_serialization_is_not_provided_by_editorial_store() -> None:
    assert not hasattr(EditorialPersistenceStore, "public_projection")
    assert not hasattr(EditorialPersistenceStore, "student_payload")


def test_repository_has_no_student_progress_publication_or_import_operations() -> None:
    forbidden = {
        "publish",
        "publish_project",
        "record_progress",
        "save_attempt",
        "submit_project",
        "grade_project",
        "import_bundle",
    }
    assert forbidden.isdisjoint(dir(EditorialPersistenceStore))


def test_payload_fields_are_hidden_from_model_repr() -> None:
    payload = StoredBlockPayload(
        entity_kind="block",
        entity_ref=block().ref,
        revision_id="8" * 64,
        revision_no=1,
        content_sha256="9" * 64,
        block=block(),
    )
    assert "SYNTHETIC_EDITORIAL_BODY" not in repr(payload)


def test_persisted_payload_preserves_absent_optional_source_fields() -> None:
    private_block = AnswerKeyBlock(
        ref="f1-optional-field-fixture",
        type="answer_key",
        owner_ref=None,
        order=1,
        title="Synthetic private fixture",
        status="draft",
        shared=True,
        provenance=provenance("OPTIONAL-FIELD"),
        question_ref="f1-question-fixture",
        correct_option_ref=None,
        accepted_answers=["SYNTHETIC_PRIVATE_VALUE"],
        expected_answer=None,
        explanation=None,
    )
    assert "source_markdown" not in private_block.model_fields_set
    stored = StoredBlockPayload(
        entity_kind="block",
        entity_ref=private_block.ref,
        revision_id="a" * 64,
        revision_no=1,
        content_sha256="b" * 64,
        block=private_block,
    )

    document = _mongo_doc(stored)
    assert "source_markdown" not in document["block"]
    restored = StoredBlockPayload.model_validate(document)
    assert isinstance(restored.block, AnswerKeyBlock)
    assert restored.block.source_markdown is None
    assert "source_markdown" not in restored.block.model_dump(mode="json", exclude_unset=True)


def test_provenance_hashes_are_validated_without_rewriting_source() -> None:
    source_block = block()
    original_hash = source_block.provenance.source_sha256
    _validate_block_provenance(source_block)
    assert source_block.provenance.source_sha256 == original_hash

    with pytest.raises(Exception, match="lowercase SHA-256"):
        _validate_block_provenance(
            source_block.model_copy(
                update={
                    "provenance": source_block.provenance.model_copy(
                        update={"source_sha256": "A" * 64}
                    )
                }
            )
        )


def test_placement_scope_must_remain_explicitly_undecided() -> None:
    source = placement()
    _validate_placement_provenance(source)
    assert source.progress_scope == "undecided"
    store = object.__new__(EditorialPersistenceStore)
    store._authorizer = lambda _principal, _capability: True
    store._node_kind_resolver = lambda _ref: "topic"
    with pytest.raises(EditorialValidationError, match="remain undecided"):
        asyncio.run(
            store.save_placement(
                SharedPlacement.model_validate(
                    {**source.model_dump(mode="python"), "progress_scope": "per_context"}
                ),
                EditorialPrincipal(actor_ref="synthetic-editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="synthetic-placement-operation",
            )
        )


def test_project_provenance_covers_aggregate_and_each_formal_step() -> None:
    source = project()
    _validate_project_provenance(source)
    assert [item.order for item in source.deliveries] == [1]
    assert [item.order for item in source.milestones] == [2]
    assert source.stack_options == ["synthetic-stack-a", "synthetic-stack-b"]


def test_missing_authorizer_denies_by_default_before_database_access() -> None:
    store = object.__new__(EditorialPersistenceStore)
    store._authorizer = None
    principal = EditorialPrincipal(actor_ref="synthetic-editor")

    with pytest.raises(EditorialAuthorizationError):
        store._require(principal, "curriculum.editorial.read")


def test_authorizer_exception_fails_closed() -> None:
    store = object.__new__(EditorialPersistenceStore)
    store._authorizer = lambda _principal, _capability: (_ for _ in ()).throw(RuntimeError())
    principal = EditorialPrincipal(actor_ref="synthetic-editor")

    with pytest.raises(EditorialAuthorizationError):
        store._require(principal, "curriculum.editorial.revision.create")


def test_operation_not_found_is_not_conclusive() -> None:
    status = EditorialOperationStatus(
        state="not_found",
        operation_ref="a" * 64,
        outcome_conclusive=False,
    )
    assert status.outcome_conclusive is False


def test_only_complete_expected_head_pairs_are_accepted() -> None:
    _require_expected_head_pair(None, None)
    _require_expected_head_pair("b" * 64, 2)
    with pytest.raises(Exception, match="must be supplied together"):
        _require_expected_head_pair("b" * 64, None)
    with pytest.raises(Exception, match="malformed"):
        _require_expected_head_pair("wrong", 2)


def test_projects_reject_stack_selection_and_variants_at_repository_boundary() -> None:
    source = project()
    store = object.__new__(EditorialPersistenceStore)
    store._authorizer = lambda _principal, _capability: True
    store._node_kind_resolver = lambda _ref: "submodule"
    principal = EditorialPrincipal(actor_ref="synthetic-editor")
    with pytest.raises(EditorialValidationError, match="remain out of scope"):
        asyncio.run(
            store.save_project(
                ProjectSpec.model_validate(
                    {**source.model_dump(mode="python"), "stack_selected": "synthetic-stack-a"}
                ),
                principal,
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="synthetic-stack-operation",
            )
        )
    with pytest.raises(EditorialValidationError, match="remain out of scope"):
        asyncio.run(
            store.save_project(
                ProjectSpec.model_validate(
                    {
                        **source.model_dump(mode="python"),
                        "variants": [
                            ProjectVariant(
                                ref="f1-variant-fixture",
                                title="Synthetic variant",
                                order=1,
                                description="Synthetic",
                                delivery_refs=["f1-delivery-fixture"],
                                stack_option="synthetic-stack-a",
                                provenance=provenance("VARIANT-1"),
                            ).model_dump(mode="python")
                        ],
                    }
                ),
                principal,
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="synthetic-variant-operation",
            )
        )
    assert json.loads(source.model_dump_json())["variants"] == []


def test_editorial_repository_rejects_non_draft_block_states() -> None:
    store = object.__new__(EditorialPersistenceStore)
    store._authorizer = lambda _principal, _capability: True
    principal = EditorialPrincipal(actor_ref="synthetic-editor")
    for status in ("published", "archived"):
        source = block().model_copy(update={"status": status})
        with pytest.raises(EditorialValidationError, match="draft blocks only"):
            asyncio.run(
                store.save_block(
                    source,
                    principal,
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key=f"synthetic-{status}-operation",
                )
            )
