"""Experimental atomic block-edit contract for disposable MongoDB tests only.

This module is deliberately not imported by application code. It composes the
existing track-scoped revision adapter and its MongoDB transaction rather than
creating a separate block revision or fencing authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from pymongo.errors import DuplicateKeyError

from .editorial_revision_protocol import (
    IdempotencyConflict,
    PreparedRevision,
    RevisionReceipt,
    WriterCredential,
)
from .mongodb_editorial_revision_adapter import MongoDBEditorialRevisionAdapter

_TEST_DATABASE = re.compile(r"^editorial_revision_test_[a-zA-Z0-9_-]{8,64}$")
_TEST_NAMESPACE = re.compile(r"^c8_[a-z0-9_]{1,28}$")
_MAX_IDENTITY_LENGTH = 256
_MAX_TITLE_LENGTH = 256


class EditorialBlockCommitError(RuntimeError):
    """Base class for isolated block-commit errors."""


class EditorialBlockNotFound(EditorialBlockCommitError):
    """The synthetic block is missing or belongs to another track."""


class EditorialBlockAuditIdentityConflict(EditorialBlockCommitError):
    """An audit operation identity already exists without a matching replay."""


class InvalidEditorialBlockUpdate(EditorialBlockCommitError, ValueError):
    """A synthetic block update violates this experiment's narrow contract."""


@dataclass(frozen=True, slots=True)
class PreparedEditorialBlockUpdate:
    """Prepared intent; it is not a committed block change."""

    track_id: str
    block_id: str
    actor_id: str
    title: str
    revision: PreparedRevision


def _require_identity(value: str, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\x00" in value
        or len(value.encode("utf-8")) > _MAX_IDENTITY_LENGTH
    ):
        raise InvalidEditorialBlockUpdate(f"{name} is invalid")


def _require_scope(
    database: Any, adapter: MongoDBEditorialRevisionAdapter
) -> None:
    database_name = getattr(database, "name", None)
    if not isinstance(database_name, str) or not _TEST_DATABASE.fullmatch(database_name):
        raise ValueError("experimental block commits require a disposable test database")
    if database_name != adapter.database_name:
        raise ValueError("database and revision adapter must use the same database")
    if not _TEST_NAMESPACE.fullmatch(adapter.namespace):
        raise ValueError("experimental block commits require a c8_ adapter namespace")
    if getattr(database, "client", None) is not adapter._client:
        raise ValueError("database and revision adapter must share one MongoDB client")
    adapter._require_verified_topology()


def ensure_experimental_indexes(
    database: Any, adapter: MongoDBEditorialRevisionAdapter
) -> None:
    """Create only the protocol and audit indexes in the guarded test database."""

    _require_scope(database, adapter)
    adapter.ensure_indexes()
    database["edit_history"].create_index(
        [("track_id", 1), ("operation_id", 1)],
        unique=True,
        name=f"{adapter.namespace}_audit_operation_identity",
    )


def _intent_payload(
    *, track_id: str, block_id: str, actor_id: str, title: str
) -> dict[str, Any]:
    return {
        "operation_kind": "block.update.title",
        "block_id": block_id,
        "actor_id": actor_id,
        "changes": {"title": title},
        "schema_version": 1,
        "track_id": track_id,
    }


def prepare_editorial_block_update(
    adapter: MongoDBEditorialRevisionAdapter,
    *,
    track_id: str,
    credential: WriterCredential,
    operation_id: str,
    expected_revision: int,
    fencing_token: int,
    block_id: str,
    actor_id: str,
    title: str,
) -> PreparedEditorialBlockUpdate:
    """Prepare a title change under the existing track revision and fence."""

    if not isinstance(adapter.database_name, str) or not _TEST_DATABASE.fullmatch(
        adapter.database_name
    ):
        raise ValueError("experimental block commits require a disposable test database")
    if not _TEST_NAMESPACE.fullmatch(adapter.namespace):
        raise ValueError("experimental block commits require a c8_ adapter namespace")
    adapter._require_verified_topology()
    for value, name in (
        (track_id, "track_id"),
        (operation_id, "operation_id"),
        (block_id, "block_id"),
        (actor_id, "actor_id"),
    ):
        _require_identity(value, name)
    if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
        raise InvalidEditorialBlockUpdate("writer credential is outside the track scope")
    if not isinstance(title, str) or not title.strip() or len(title.encode("utf-8")) > _MAX_TITLE_LENGTH:
        raise InvalidEditorialBlockUpdate("title is invalid")
    if type(expected_revision) is not int or expected_revision < 0:
        raise InvalidEditorialBlockUpdate("expected revision must be a non-negative integer")
    if type(fencing_token) is not int or fencing_token < 1:
        raise InvalidEditorialBlockUpdate("fencing token must be a positive integer")

    payload = _intent_payload(
        track_id=track_id, block_id=block_id, actor_id=actor_id, title=title
    )
    prepared = adapter.prepare(
        track_id=track_id,
        credential=credential,
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=fencing_token,
        payload=payload,
    )
    return PreparedEditorialBlockUpdate(track_id, block_id, actor_id, title, prepared)


def commit_prepared_editorial_block_update(
    database: Any,
    adapter: MongoDBEditorialRevisionAdapter,
    credential: WriterCredential,
    update: PreparedEditorialBlockUpdate,
) -> RevisionReceipt:
    """Atomically update a block and append its required audit record.

    The adapter's track document is the sole revision and fencing authority.
    A transaction participant writes the block and audit using the exact
    session supplied by the adapter. The participant has no external effects.
    """

    _require_scope(database, adapter)
    if not isinstance(update, PreparedEditorialBlockUpdate):
        raise InvalidEditorialBlockUpdate("prepared block update is invalid")
    prepared = update.revision
    expected_payload = _intent_payload(
        track_id=update.track_id,
        block_id=update.block_id,
        actor_id=update.actor_id,
        title=update.title,
    )
    persisted_payload = adapter.prepared_payload(
        update.track_id, prepared.operation_id, credential
    )
    if persisted_payload != expected_payload:
        raise IdempotencyConflict(update.track_id, prepared.operation_id)

    def write_block_and_audit(session: Any, receipt: RevisionReceipt) -> None:
        block_result = database["content_blocks"].update_one(
            {"_id": update.block_id, "track_id": update.track_id},
            {"$set": {"title": update.title}},
            session=session,
        )
        if block_result.matched_count != 1:
            raise EditorialBlockNotFound("synthetic block was not found in the requested track")

        audit = {
            "track_id": receipt.track_id,
            "operation_id": receipt.operation_id,
            "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "writer_id": receipt.writer_id,
            "fencing_token": receipt.fencing_token,
            "entity": "block",
            "entity_id": update.block_id,
            "action": "updated",
            "actor_id": update.actor_id,
            "changed_fields": ["title"],
            "at": datetime.now(timezone.utc),
        }
        try:
            database["edit_history"].insert_one(audit, session=session)
        except DuplicateKeyError:
            raise EditorialBlockAuditIdentityConflict(
                "an audit record already uses this operation identity"
            ) from None

    return adapter.commit(
        prepared,
        credential,
        _transaction_participant=write_block_and_audit,
    )


def commit_editorial_block_update(
    database: Any,
    adapter: MongoDBEditorialRevisionAdapter,
    *,
    track_id: str,
    credential: WriterCredential,
    operation_id: str,
    expected_revision: int,
    fencing_token: int,
    block_id: str,
    actor_id: str,
    title: str,
) -> RevisionReceipt:
    """Convenience wrapper for an isolated prepare-then-commit sequence."""

    prepared = prepare_editorial_block_update(
        adapter,
        track_id=track_id,
        credential=credential,
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=fencing_token,
        block_id=block_id,
        actor_id=actor_id,
        title=title,
    )
    return commit_prepared_editorial_block_update(database, adapter, credential, prepared)
