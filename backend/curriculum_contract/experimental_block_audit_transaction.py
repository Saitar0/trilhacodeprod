"""Test-only proposal for atomic block mutation plus required audit.

This module is not imported by application code. It assumes that audit is a
mandatory part of the mutation contract and that both records reside in the
same MongoDB deployment. Human approval of that policy is still required.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping

from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

_DISPOSABLE_DATABASE = re.compile(r"^editorial_block_audit_test_[a-f0-9]{16}$")
_ALLOWED_UPDATE_FIELDS = frozenset({"title", "status"})


class BlockTransactionError(RuntimeError):
    """Base error for the isolated transaction proposal."""


class BlockRevisionConflict(BlockTransactionError):
    """The stored block no longer has the expected editorial revision."""


class BlockOperationConflict(BlockTransactionError):
    """An operation identity was already recorded."""


class BlockCommitOutcomeUnknown(BlockTransactionError):
    """MongoDB could not establish whether the transaction commit succeeded."""


class BlockConcurrentWriteConflict(BlockTransactionError):
    """MongoDB rejected a concurrent transaction; no automatic retry was made."""


class BlockTransactionAbortUncertain(BlockTransactionError):
    """A failed transaction could not be conclusively aborted."""


async def update_block_with_audit_transaction(
    database: Any,
    *,
    block_id: Any,
    expected_revision: int,
    operation_id: str,
    update_fields: Mapping[str, Any],
    user: Mapping[str, Any],
) -> dict[str, Any]:
    """Atomically append a synthetic block revision and its audit receipt.

    The caller must create a unique index on ``edit_history.operation_id`` in
    the disposable database. CAS, fencing, application authorization,
    production compatibility, and idempotent receipt replay are out of scope.
    """

    if not isinstance(getattr(database, "name", None), str) or not _DISPOSABLE_DATABASE.fullmatch(
        database.name
    ):
        raise ValueError("transaction proposal accepts only a phase disposable database")
    if type(expected_revision) is not int or expected_revision < 0:
        raise ValueError("expected_revision must be a non-negative integer")
    if not isinstance(operation_id, str) or not operation_id.strip():
        raise ValueError("operation_id must be non-empty")
    if not isinstance(update_fields, Mapping):
        raise TypeError("update_fields must be a mapping")
    if any(key not in _ALLOWED_UPDATE_FIELDS for key in update_fields):
        raise ValueError("update_fields contains a field outside the synthetic allowlist")
    if "id" not in user:
        raise ValueError("user must contain a synthetic id")

    client = database.client
    async with client.start_session() as session:
        await session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        )
        try:
            collection = database["content_blocks"]
            existing = await collection.find_one({"_id": block_id}, session=session)
            if existing is None:
                raise BlockRevisionConflict("block does not exist")
            if existing.get("editorial_revision") != expected_revision:
                raise BlockRevisionConflict("expected revision is stale")

            fields = dict(update_fields)
            fields["updated_at"] = datetime.now(timezone.utc)
            result = await collection.update_one(
                {"_id": block_id, "editorial_revision": expected_revision},
                {"$set": fields, "$inc": {"editorial_revision": 1}},
                session=session,
            )
            if result.matched_count != 1:
                raise BlockRevisionConflict("block revision changed during update")

            await database["edit_history"].insert_one(
                {
                    "operation_id": operation_id,
                    "entity": "block",
                    "entity_id": str(block_id),
                    "action": "updated",
                    "track_id": existing.get("track_id"),
                    "summary": existing.get("type", ""),
                    "user_id": user["id"],
                    "user_name": user.get("name", ""),
                    "at": fields["updated_at"],
                },
                session=session,
            )
            confirmed = await collection.find_one(
                {"_id": block_id, "editorial_revision": expected_revision + 1},
                session=session,
            )
            if confirmed is None:
                raise BlockRevisionConflict("updated block was not visible in transaction snapshot")
            try:
                await session.commit_transaction()
            except PyMongoError as exc:
                if exc.has_error_label("UnknownTransactionCommitResult"):
                    raise BlockCommitOutcomeUnknown(
                        "transaction commit outcome requires reconciliation"
                    ) from None
                raise
            return dict(confirmed)
        except BaseException as original_error:
            if isinstance(original_error, BlockCommitOutcomeUnknown):
                raise
            if session.in_transaction:
                try:
                    await session.abort_transaction()
                except Exception:
                    raise BlockTransactionAbortUncertain(
                        "transaction abort could not be confirmed"
                    ) from None
            if isinstance(original_error, DuplicateKeyError):
                raise BlockOperationConflict("operation identity was already recorded") from None
            if isinstance(original_error, PyMongoError) and original_error.has_error_label(
                "TransientTransactionError"
            ):
                raise BlockConcurrentWriteConflict(
                    "concurrent transaction was rejected; retry requires caller policy"
                ) from None
            raise
