"""Synthetic family mutations composed with the existing C8/C10 authority.

Test-only experiment. This module never opens a client and is not imported by
application routes or services. It deliberately does not implement another
revision/fencing protocol: every cooperative mutation is a participant in the
existing C10 AsyncEditorialRevisionAdapter transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .editorial_revision_protocol import PreparedRevision, RevisionReceipt, WriterCredential
from .experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter


class WriterFamily(str, Enum):
    BLOCK_EDIT = "block_edit"
    PUBLISH = "publish"
    IMPORT = "import"
    RESTORE = "restore"
    DELETE = "delete"
    DUPLICATE = "duplicate"
    REORDER = "reorder"
    SEED = "seed"


# C13 IDs identify source families represented by these deliberately synthetic
# participants. The mapping does not claim that the active implementations ran.
C16_FAMILY_C13_WRITERS = {
    WriterFamily.BLOCK_EDIT: ("W-07",),
    WriterFamily.PUBLISH: ("W-04",),
    WriterFamily.IMPORT: ("W-10",),
    WriterFamily.RESTORE: ("W-11",),
    WriterFamily.DELETE: ("W-02", "W-06"),
    WriterFamily.DUPLICATE: ("W-03", "W-06"),
    WriterFamily.REORDER: ("W-01", "W-05", "W-07"),
    WriterFamily.SEED: ("W-13",),
}


class C16InjectedFailure(RuntimeError):
    """A deterministic failure injected into a synthetic transaction participant."""


class SnapshotRevisionMismatch(ValueError):
    """A synthetic publication snapshot does not represent the prepared revision."""


class MissingSyntheticTarget(RuntimeError):
    """A required synthetic target is missing from the C16 test database."""


class FaultPoint(str, Enum):
    AFTER_FIRST_MUTATION = "after_first_mutation"
    AFTER_SNAPSHOT = "after_snapshot"
    BEFORE_AUDIT = "before_audit"


@dataclass(slots=True)
class FaultPlan:
    point: FaultPoint
    fired: bool = False

    def hit(self, point: FaultPoint) -> None:
        if self.point == point and not self.fired:
            self.fired = True
            raise C16InjectedFailure(f"C16 injected failure at {point.value}")


@dataclass(frozen=True, slots=True)
class FamilyIntent:
    family: WriterFamily
    operation_id: str
    value: str
    snapshot_source_revision: int | None = None


@dataclass(frozen=True, slots=True)
class PreparedFamilyIntent:
    intent: FamilyIntent
    prepared: PreparedRevision


@dataclass(frozen=True, slots=True)
class C16Writer:
    client: Any
    database: Any
    adapter: AsyncEditorialRevisionAdapter
    credentials: dict[WriterFamily, WriterCredential]
    track_id: str
    block_id: str
    node_id: str
    fencing_token: int


async def prepare_family_intent(
    writer: C16Writer,
    intent: FamilyIntent,
    *,
    expected_revision: int,
) -> PreparedFamilyIntent:
    """Prepare a safe metadata-only intent under the shared C8 revision state."""

    if intent.family == WriterFamily.PUBLISH and intent.snapshot_source_revision != expected_revision:
        raise SnapshotRevisionMismatch(
            "publication source snapshot must match the expected track revision"
        )
    payload: dict[str, Any] = {
        "contract_version": 1,
        "family": intent.family.value,
        "operation_kind": f"{intent.family.value}.synthetic",
        "track_ref": writer.track_id,
        "target_ref": writer.block_id,
    }
    if intent.snapshot_source_revision is not None:
        payload["snapshot_source_revision"] = intent.snapshot_source_revision
    prepared = await writer.adapter.prepare(
        track_id=writer.track_id,
        credential=writer.credentials[intent.family],
        operation_id=intent.operation_id,
        expected_revision=expected_revision,
        fencing_token=writer.fencing_token,
        payload=payload,
    )
    return PreparedFamilyIntent(intent=intent, prepared=prepared)


async def commit_family_intent(
    writer: C16Writer,
    prepared: PreparedFamilyIntent,
    *,
    fault: FaultPlan | None = None,
    fail_audit: bool = False,
) -> RevisionReceipt:
    """Apply one family-shaped synthetic mutation inside the C10 transaction."""

    intent = prepared.intent
    database = writer.database

    async def participant(session: Any, receipt: RevisionReceipt) -> None:
        if intent.family == WriterFamily.BLOCK_EDIT:
            result = await database.content_blocks.update_one(
                {"_id": writer.block_id, "track_id": writer.track_id},
                {"$set": {"title": intent.value, "last_operation_id": intent.operation_id}},
                session=session,
            )
            _require_match(result.matched_count, "block edit")
            _hit(fault, FaultPoint.AFTER_FIRST_MUTATION)

        elif intent.family == WriterFamily.PUBLISH:
            if intent.snapshot_source_revision != receipt.parent_revision:
                raise SnapshotRevisionMismatch(
                    "snapshot source revision differs from the committed parent revision"
                )
            blocks = await database.content_blocks.find(
                {"track_id": writer.track_id}, session=session
            ).sort("_id", 1).to_list(length=100)
            snapshot = [
                {"_id": row["_id"], "title": row.get("title", "")}
                for row in blocks
            ]
            await database.track_versions.insert_one(
                {
                    "_id": f"c16-version-{intent.operation_id}",
                    "track_id": writer.track_id,
                    "revision": receipt.revision,
                    "source_revision": receipt.parent_revision,
                    "blocks": snapshot,
                },
                session=session,
            )
            _hit(fault, FaultPoint.AFTER_SNAPSHOT)
            await database.activity_publications.insert_one(
                {
                    "_id": f"c16-publication-{intent.operation_id}",
                    "track_id": writer.track_id,
                    "generation": receipt.revision,
                    "source_revision": receipt.parent_revision,
                },
                session=session,
            )
            result = await database.tracks.update_one(
                {"_id": writer.track_id},
                {"$set": {"published_revision": receipt.revision, "status": "published"}},
                session=session,
            )
            _require_match(result.matched_count, "publish activation")

        elif intent.family == WriterFamily.IMPORT:
            node_id = f"c16-import-node-{intent.operation_id}"
            await database.nodes.insert_one(
                {"_id": node_id, "track_id": writer.track_id, "title": intent.value},
                session=session,
            )
            _hit(fault, FaultPoint.AFTER_FIRST_MUTATION)
            await database.content_blocks.insert_one(
                {
                    "_id": f"c16-import-block-{intent.operation_id}",
                    "track_id": writer.track_id,
                    "node_id": node_id,
                    "title": f"imported-{intent.value}",
                },
                session=session,
            )
            await database.relations.insert_one(
                {
                    "_id": f"c16-import-relation-{intent.operation_id}",
                    "track_id": writer.track_id,
                    "node_id": node_id,
                },
                session=session,
            )

        elif intent.family == WriterFamily.RESTORE:
            await database.content_blocks.delete_many(
                {"track_id": writer.track_id}, session=session
            )
            _hit(fault, FaultPoint.AFTER_FIRST_MUTATION)
            await database.content_blocks.insert_one(
                {
                    "_id": writer.block_id,
                    "track_id": writer.track_id,
                    "node_id": writer.node_id,
                    "title": intent.value,
                    "restored_from_revision": receipt.parent_revision,
                },
                session=session,
            )

        elif intent.family == WriterFamily.DELETE:
            await database.content_blocks.delete_many(
                {"track_id": writer.track_id}, session=session
            )
            await database.relations.delete_many(
                {"track_id": writer.track_id}, session=session
            )
            _hit(fault, FaultPoint.AFTER_FIRST_MUTATION)
            # Mirrors the destructive effect identified for the C13 cascade; it
            # is intentionally included to show that atomicity alone does not
            # approve this learner-data policy.
            await database.progress.delete_many(
                {"track_id": writer.track_id}, session=session
            )
            await database.activity_attempts.delete_many(
                {"track_id": writer.track_id}, session=session
            )

        elif intent.family == WriterFamily.DUPLICATE:
            target_track = f"c16-duplicate-{intent.operation_id}"
            await database.tracks.insert_one(
                {"_id": target_track, "source_track_id": writer.track_id, "status": "draft"},
                session=session,
            )
            await database.nodes.insert_one(
                {
                    "_id": f"{target_track}-node",
                    "track_id": target_track,
                    "title": intent.value,
                },
                session=session,
            )
            await database.content_blocks.insert_one(
                {
                    "_id": f"{target_track}-block",
                    "track_id": target_track,
                    "title": "synthetic-copy",
                },
                session=session,
            )

        elif intent.family == WriterFamily.REORDER:
            result = await database.nodes.update_one(
                {"_id": writer.node_id, "track_id": writer.track_id},
                {"$set": {"order": 7, "order_revision": receipt.revision}},
                session=session,
            )
            _require_match(result.matched_count, "reorder")

        elif intent.family == WriterFamily.SEED:
            await database.content_blocks.update_one(
                {"_id": f"c16-seed-block-{writer.track_id}"},
                {
                    "$set": {
                        "track_id": writer.track_id,
                        "node_id": writer.node_id,
                        "title": intent.value,
                        "seed_operation_id": intent.operation_id,
                    }
                },
                upsert=True,
                session=session,
            )

        else:  # pragma: no cover - Enum makes this defensive branch unreachable.
            raise ValueError(f"unsupported C16 writer family: {intent.family!r}")

        await database.c16_effects.insert_one(
            {
                "_id": intent.operation_id,
                "track_id": writer.track_id,
                "family": intent.family.value,
                "revision": receipt.revision,
            },
            session=session,
        )
        _hit(fault, FaultPoint.BEFORE_AUDIT)
        if fail_audit:
            raise C16InjectedFailure("C16 synthetic mandatory audit failure")
        await database.edit_history.insert_one(
            {
                "track_id": writer.track_id,
                "operation_id": intent.operation_id,
                "revision": receipt.revision,
                "parent_revision": receipt.parent_revision,
                "family": intent.family.value,
                "action": "synthetic_commit",
                "synthetic": True,
            },
            session=session,
        )

    return await writer.adapter.commit(
        prepared.prepared,
        writer.credentials[intent.family],
        participant=participant,
    )


def _require_match(matched_count: int, operation: str) -> None:
    if matched_count != 1:
        raise MissingSyntheticTarget(f"C16 {operation} target was not found")


def _hit(fault: FaultPlan | None, point: FaultPoint) -> None:
    if fault is not None:
        fault.hit(point)
