"""Isolated compatibility composition for the versioned block/audit contracts.

This module is for disposable tests and design experiments only. It does not
import application services, create a MongoDB client, or connect to a backend.
The async entry point runs the synchronous C8 PyMongo contract in a worker
thread; it is not an adapter for the application's AsyncMongoClient.
"""

from __future__ import annotations

import asyncio
import copy
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from .editorial_revision_protocol import (
    IdempotencyConflict,
    PreparedRevision,
    RevisionReceipt,
    WriterCredential,
)
from .mongodb_editorial_revision_adapter import MongoDBEditorialRevisionAdapter

_TEST_DATABASE = re.compile(r"^editorial_revision_test_c9_[a-f0-9]{16,32}$")
_TEST_NAMESPACE = re.compile(r"^c9_[a-z0-9_]{1,28}$")
_OBJECT_ID = re.compile(r"^[a-fA-F0-9]{24}$")
_UPDATE_FIELDS = frozenset({"title", "data", "status"})
_STATUSES = frozenset({"draft", "published", "archived"})
_MAX_IDENTITY_BYTES = 256


class EditorialCompatibilityError(RuntimeError):
    """Base error for the isolated compatibility adapter."""


class InvalidEditorialCompatibilityInput(EditorialCompatibilityError, ValueError):
    """An input does not fit the versioned block or C8 protocol contract."""


class EditorialBlockReferenceNotFound(EditorialCompatibilityError):
    """The ObjectId is absent or does not belong to the supplied track."""


class EditorialBlockSchemaMismatch(EditorialCompatibilityError):
    """A block lacks a field required by the current audit contract."""


class EditorialAuditIdentityConflict(EditorialCompatibilityError):
    """A conflicting legacy audit record already uses the operation identity."""


@dataclass(frozen=True, slots=True)
class PreparedCompatibleBlockUpdate:
    """Prepared track-scoped intent; preparation is not a confirmed update."""

    track_id: str
    block_id: ObjectId
    actor_id: str
    actor_name: str
    changes: Mapping[str, Any]
    revision: PreparedRevision


@dataclass(frozen=True, slots=True)
class CompatibleBlockCommit:
    """A C8 receipt plus the block-shaped result required by the service."""

    receipt: RevisionReceipt
    block: Mapping[str, Any]


def _require_identity(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\x00" in value
        or len(value.encode("utf-8")) > _MAX_IDENTITY_BYTES
    ):
        raise InvalidEditorialCompatibilityInput(f"{name} is invalid")
    return value


def parse_operational_block_id(value: str) -> ObjectId:
    """Convert only the backend's 24-hex string representation to ObjectId."""

    if not isinstance(value, str) or _OBJECT_ID.fullmatch(value) is None:
        raise InvalidEditorialCompatibilityInput("block_id must be a 24-character ObjectId")
    return ObjectId(value)


def _require_scope(
    database: Any, adapter: MongoDBEditorialRevisionAdapter
) -> None:
    database_name = getattr(database, "name", None)
    if not isinstance(database_name, str) or not _TEST_DATABASE.fullmatch(database_name):
        raise ValueError("C9 compatibility experiments require a C9 disposable database")
    if database_name != adapter.database_name:
        raise ValueError("database and revision adapter must use the same database")
    if not isinstance(getattr(database, "client", None), MongoClient):
        raise TypeError("the compatibility bridge requires an explicitly supplied sync PyMongo client")
    if database.client is not adapter._client:
        raise ValueError("database and revision adapter must share one sync MongoClient")
    if not isinstance(adapter.namespace, str) or not _TEST_NAMESPACE.fullmatch(adapter.namespace):
        raise ValueError("C9 compatibility experiments require a c9_ adapter namespace")
    adapter._require_verified_topology()


def _require_adapter_scope(adapter: MongoDBEditorialRevisionAdapter) -> None:
    database_name = getattr(adapter, "database_name", None)
    if not isinstance(database_name, str) or not _TEST_DATABASE.fullmatch(database_name):
        raise ValueError("C9 compatibility preparation requires a C9 disposable database")
    if not isinstance(adapter.namespace, str) or not _TEST_NAMESPACE.fullmatch(adapter.namespace):
        raise ValueError("C9 compatibility preparation requires a c9_ adapter namespace")
    if not isinstance(adapter._client, MongoClient):
        raise TypeError("the compatibility bridge requires a sync PyMongo client")
    adapter._require_verified_topology()


def ensure_experimental_indexes(
    database: Any, adapter: MongoDBEditorialRevisionAdapter
) -> None:
    """Create namespaced protocol indexes and a legacy-compatible audit index."""

    _require_scope(database, adapter)
    adapter.ensure_indexes()
    # Existing edit_history rows do not carry operation_id. The partial filter
    # avoids treating all such rows as the same (track_id, null) operation.
    database["edit_history"].create_index(
        [("track_id", 1), ("operation_id", 1)],
        unique=True,
        partialFilterExpression={"operation_id": {"$type": "string"}},
        name=f"{adapter.namespace}_audit_operation_identity",
    )


def _snapshot_changes(update_fields: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(update_fields, Mapping):
        raise InvalidEditorialCompatibilityInput("update_fields must be a mapping")
    if any(not isinstance(key, str) or key not in _UPDATE_FIELDS for key in update_fields):
        raise InvalidEditorialCompatibilityInput("update_fields contains a non-editable field")
    changes = copy.deepcopy(dict(update_fields))
    if "title" in changes and changes["title"] is not None and not isinstance(changes["title"], str):
        raise InvalidEditorialCompatibilityInput("title must be a string or null")
    if "data" in changes and changes["data"] is not None and not isinstance(changes["data"], dict):
        raise InvalidEditorialCompatibilityInput("data must be an object or null")
    if "status" in changes:
        status = changes["status"]
        if status is not None and (
            not isinstance(status, str) or status not in _STATUSES
        ):
            raise InvalidEditorialCompatibilityInput("status is invalid")
    return changes


def _intent_payload(
    *,
    track_id: str,
    block_id: ObjectId,
    actor_id: str,
    changes: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "operation_kind": "block.update",
        "schema_version": 1,
        "track_id": track_id,
        "block_id": str(block_id),
        "actor_id": actor_id,
        "changes": dict(changes),
    }


def prepare_compatible_block_update(
    adapter: MongoDBEditorialRevisionAdapter,
    *,
    track_id: str,
    credential: WriterCredential,
    operation_id: str,
    expected_revision: int,
    fencing_token: int,
    block_id: str,
    actor: Mapping[str, Any],
    update_fields: Mapping[str, Any],
) -> PreparedCompatibleBlockUpdate:
    """Translate a validated backend-style edit into the C8 track protocol."""

    _require_adapter_scope(adapter)
    _require_identity(track_id, "track_id")
    _require_identity(operation_id, "operation_id")
    object_id = parse_operational_block_id(block_id)
    if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
        raise InvalidEditorialCompatibilityInput("writer credential is outside the track scope")
    if not isinstance(actor, Mapping):
        raise InvalidEditorialCompatibilityInput("actor must be an explicit mapping")
    actor_id = _require_identity(actor.get("id"), "actor.id")
    actor_name = actor.get("name", "")
    if not isinstance(actor_name, str):
        raise InvalidEditorialCompatibilityInput("actor.name must be a string")
    changes = _snapshot_changes(update_fields)
    payload = _intent_payload(
        track_id=track_id,
        block_id=object_id,
        actor_id=actor_id,
        changes=changes,
    )
    prepared = adapter.prepare(
        track_id=track_id,
        credential=credential,
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=fencing_token,
        payload=payload,
    )
    return PreparedCompatibleBlockUpdate(
        track_id=track_id,
        block_id=object_id,
        actor_id=actor_id,
        actor_name=actor_name,
        changes=changes,
        revision=prepared,
    )


def commit_prepared_compatible_block_update(
    database: Any,
    adapter: MongoDBEditorialRevisionAdapter,
    credential: WriterCredential,
    update: PreparedCompatibleBlockUpdate,
) -> CompatibleBlockCommit:
    """Atomically update operational-shaped block/audit docs with C8 state."""

    _require_scope(database, adapter)
    if not isinstance(update, PreparedCompatibleBlockUpdate):
        raise InvalidEditorialCompatibilityInput("prepared update is invalid")
    if update.track_id != credential.track_id:
        raise InvalidEditorialCompatibilityInput("credential is outside the prepared track")
    payload = _intent_payload(
        track_id=update.track_id,
        block_id=update.block_id,
        actor_id=update.actor_id,
        changes=update.changes,
    )
    persisted_payload = adapter.prepared_payload(
        update.track_id, update.revision.operation_id, credential
    )
    if persisted_payload != payload:
        raise IdempotencyConflict(update.track_id, update.revision.operation_id)

    committed: dict[str, Any] = {}

    def write_block_and_audit(session: Any, receipt: RevisionReceipt) -> None:
        selector = {"_id": update.block_id, "track_id": update.track_id}
        before = database["content_blocks"].find_one(selector, session=session)
        if before is None:
            raise EditorialBlockReferenceNotFound(
                "block was not found in the supplied track"
            )
        block_type = before.get("type")
        if not isinstance(block_type, str):
            raise EditorialBlockSchemaMismatch("block.type is required by the legacy audit")

        written_at = datetime.now(timezone.utc)
        fields = dict(update.changes)
        fields["updated_at"] = written_at
        changed = database["content_blocks"].update_one(
            selector,
            {"$set": fields},
            session=session,
        )
        if changed.matched_count != 1:
            raise EditorialBlockReferenceNotFound(
                "block no longer belongs to the supplied track"
            )
        after = database["content_blocks"].find_one(selector, session=session)
        if after is None:
            raise EditorialBlockReferenceNotFound(
                "updated block could not be read in the transaction"
            )

        audit = {
            # Legacy fields written by backend/audit.py.
            "entity": "block",
            "entity_id": str(update.block_id),
            "action": "updated",
            "track_id": update.track_id,
            "summary": block_type,
            "user_id": update.actor_id,
            "user_name": update.actor_name,
            "at": written_at,
            # Additive C8 correlation fields; operational DB validation is unknown.
            "operation_id": receipt.operation_id,
            "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "writer_id": receipt.writer_id,
            "fencing_token": receipt.fencing_token,
            "changed_fields": sorted(update.changes),
        }
        try:
            database["edit_history"].insert_one(audit, session=session)
        except DuplicateKeyError:
            raise EditorialAuditIdentityConflict(
                "edit_history already contains this track-scoped operation identity"
            ) from None
        committed["block"] = after

    receipt = adapter.commit(
        update.revision,
        credential,
        _transaction_participant=write_block_and_audit,
    )
    block = committed.get("block")
    if block is None:
        # A committed replay does not execute the participant again. The legacy
        # API returns a block document, but C8 stores a receipt, not that snapshot.
        block = database["content_blocks"].find_one(
            {"_id": update.block_id, "track_id": update.track_id}
        )
    if block is None:
        raise EditorialBlockReferenceNotFound(
            "committed operation has no current block result"
        )
    return CompatibleBlockCommit(receipt=receipt, block=dict(block))


def _commit_compatible_block_update(
    database: Any,
    adapter: MongoDBEditorialRevisionAdapter,
    *,
    track_id: str,
    credential: WriterCredential,
    operation_id: str,
    expected_revision: int,
    fencing_token: int,
    block_id: str,
    actor: Mapping[str, Any],
    update_fields: Mapping[str, Any],
) -> CompatibleBlockCommit:
    _require_scope(database, adapter)
    prepared = prepare_compatible_block_update(
        adapter,
        track_id=track_id,
        credential=credential,
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=fencing_token,
        block_id=block_id,
        actor=actor,
        update_fields=update_fields,
    )
    return commit_prepared_compatible_block_update(
        database, adapter, credential, prepared
    )


async def commit_compatible_block_update_async(
    database: Any,
    adapter: MongoDBEditorialRevisionAdapter,
    *,
    track_id: str,
    credential: WriterCredential,
    operation_id: str,
    expected_revision: int,
    fencing_token: int,
    block_id: str,
    actor: Mapping[str, Any],
    update_fields: Mapping[str, Any],
) -> CompatibleBlockCommit:
    """Run the synchronous C8 transaction off-loop with explicit dependencies.

    Cancellation of this coroutine cannot stop a running PyMongo worker thread.
    If cancellation races with commit, reconcile by (track_id, operation_id)
    before deciding whether to retry; this function does not retry automatically.
    """

    actor_snapshot = {
        "id": actor.get("id") if isinstance(actor, Mapping) else None,
        "name": actor.get("name", "") if isinstance(actor, Mapping) else "",
    }
    changes_snapshot = _snapshot_changes(update_fields)
    return await asyncio.to_thread(
        _commit_compatible_block_update,
        database,
        adapter,
        track_id=track_id,
        credential=credential,
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=fencing_token,
        block_id=block_id,
        actor=actor_snapshot,
        update_fields=changes_snapshot,
    )
