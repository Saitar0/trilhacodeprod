from __future__ import annotations

from datetime import UTC, datetime

import pytest

from curriculum_contract.experimental_editorial_grants import (
    EDITORIAL_OPERATIONS,
    EditorialTrackGrant,
    GrantValidationError,
)


def test_block_create_is_an_explicit_resource_scoped_grant_operation() -> None:
    grant = EditorialTrackGrant(
        actor_id="synthetic-editor-1",
        track_id="synthetic-track-1",
        allowed_operations=("block.create",),
        granted_by="synthetic-authorizer",
        granted_at=datetime.now(UTC),
    )

    assert "block.create" in EDITORIAL_OPERATIONS
    assert grant.allows("synthetic-editor-1", "synthetic-track-1", "block.create", role="editor")
    assert not grant.allows("synthetic-editor-1", "other-track", "block.create", role="editor")
    assert not grant.allows("synthetic-editor-1", "synthetic-track-1", "block.update", role="editor")


def test_node_update_is_explicit_and_separate_from_block_permissions() -> None:
    grant = EditorialTrackGrant(
        actor_id="synthetic-editor-1",
        track_id="synthetic-track-1",
        allowed_operations=("node.update",),
        granted_by="synthetic-authorizer",
        granted_at=datetime.now(UTC),
    )

    assert "node.update" in EDITORIAL_OPERATIONS
    assert grant.allows("synthetic-editor-1", "synthetic-track-1", "node.update", role="editor")
    assert not grant.allows("synthetic-editor-1", "other-track", "node.update", role="editor")
    assert not grant.allows("synthetic-editor-1", "synthetic-track-1", "block.update", role="editor")


def test_unreviewed_mutation_operations_remain_denied_by_the_grant_contract() -> None:
    with pytest.raises(GrantValidationError):
        EditorialTrackGrant(
            actor_id="synthetic-editor-1",
            track_id="synthetic-track-1",
            allowed_operations=("block.delete",),
            granted_by="synthetic-authorizer",
            granted_at=datetime.now(UTC),
        )
