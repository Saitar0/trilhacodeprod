"""C12-only disposable MongoDB harness; no active app configuration imports."""

from __future__ import annotations

import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter
from curriculum_contract.experimental_editorial_grants import EditorialTrackGrant
from curriculum_contract.experimental_editorial_iam_authority import MongoEditorialIAMAuthority

_HOST = "127.0.0.1"
_PORT = 29132
_REPLICA_SET = "rsC12"
_URI_ENV = "C12_TEST_MONGODB_URI"


def c12_test_uri() -> str:
    value = os.environ.get(_URI_ENV)
    if not value:
        raise RuntimeError(f"{_URI_ENV} must explicitly identify the C12 disposable service")
    if not value.startswith("mongodb://"):
        raise RuntimeError("C12 accepts only an explicit loopback mongodb:// URI")
    parsed = parse_uri(value)
    if (
        parsed.get("username") or parsed.get("password")
        or parsed.get("nodelist") != [(_HOST, _PORT)]
        or parsed.get("options", {}).get("replicaSet") != _REPLICA_SET
        or parsed.get("options", {}).get("directConnection")
    ):
        raise RuntimeError("C12 URI does not identify its loopback replica set")
    return value


@asynccontextmanager
async def isolated_database(label: str) -> AsyncIterator[tuple[Any, Any]]:
    client: Any = AsyncMongoClient(
        c12_test_uri(), serverSelectionTimeoutMS=5000,
        appname="trilhacode-c12-isolated-iam-tests", tz_aware=True,
    )
    database: Any | None = None
    marker = f"c12-{uuid.uuid4().hex}"
    try:
        hello = await client.admin.command({"hello": 1})
        server = await client.server_info()
        status = await client.admin.command({"serverStatus": 1})
        if (
            not str(server.get("version", "")).startswith("7.")
            or hello.get("setName") != _REPLICA_SET
            or not hello.get("isWritablePrimary")
            or hello.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"
        ):
            raise RuntimeError("C12 MongoDB version, primary, session, or engine check failed")
        suffix = re.sub(r"[^A-Za-z0-9_-]", "_", label)[:8]
        name = f"editorial_revision_test_c10_c11_c12_{suffix}_{uuid.uuid4().hex[:8]}"
        if name in await client.list_database_names():
            raise RuntimeError("random C12 database name already exists")
        database = client[name]
        await database["_c12_phase_marker"].insert_one({
            "_id": marker, "phase": "2.1a.12c12", "label": suffix,
        })
        yield client, database
    finally:
        if database is not None:
            try:
                proof = await database["_c12_phase_marker"].find_one(
                    {"_id": marker, "phase": "2.1a.12c12"}
                )
            except Exception:
                proof = None
            if proof is not None:
                await client.drop_database(database.name)
        await client.close()


async def ready_experiment(
    client: Any,
    database: Any,
    *,
    actor_id: str = "c12_editor_synthetic",
    track_id: str = "c12_track_synthetic",
    role: str = "editor",
    permissions: tuple[str, ...] | None = None,
    allowed_operations: tuple[str, ...] = ("block.update",),
    global_admin_scope: bool = False,
) -> dict[str, Any]:
    adapter = AsyncEditorialRevisionAdapter(database, namespace="c8_c12")
    await adapter.verify_transaction_topology()
    await adapter.initialize_track(track_id)
    credential = await adapter.provision_writer_credential(track_id, "c12_writer")
    fence_authority = await adapter.provision_fence_authority(track_id, "c12_fence")
    fence = await adapter.advance_fence(track_id, fence_authority)
    authority = MongoEditorialIAMAuthority(
        database, capability_key=b"c12-synthetic-capability-signing-key-32bytes"
    )
    session_id = "c12-session-" + uuid.uuid4().hex
    await authority.provision_principal(
        actor_id=actor_id, role=role, permissions=permissions,
    )
    await authority.provision_session(actor_id=actor_id, session_id=session_id)
    scope_track = "*" if global_admin_scope else track_id
    await authority.provision_grant(EditorialTrackGrant(
        actor_id=actor_id,
        track_id=scope_track,
        allowed_operations=tuple(sorted(allowed_operations)),
        granted_by="c12_admin_synthetic",
        granted_at=datetime.now(timezone.utc),
        global_admin_scope=global_admin_scope,
    ))
    await database["edit_history"].create_index(
        [("track_id", 1), ("operation_id", 1)],
        unique=True,
        name="c12_audit_operation_unique",
    )
    block_id = ObjectId()
    await database["content_blocks"].insert_one({
        "_id": block_id,
        "track_id": track_id,
        "title": "synthetic-original",
    })
    return {
        "adapter": adapter,
        "authority": authority,
        "client": client,
        "database": database,
        "credential": credential,
        "fence": fence,
        "actor_id": actor_id,
        "track_id": track_id,
        "session_id": session_id,
        "block_id": block_id,
    }


async def authorize_and_prepare(
    context: dict[str, Any],
    *,
    operation_id: str,
    expected_revision: int = 0,
    title: str = "synthetic-updated",
    requested_track_id: str | None = None,
) -> tuple[Any, Any]:
    decision = await context["authority"].authorize(
        actor_id=context["actor_id"],
        session_id=context["session_id"],
        resolved_track_id=context["track_id"],
        requested_track_id=requested_track_id,
        operation="block.update",
    )
    if not decision.allowed:
        return decision, None
    payload = {
        "resource_kind": "content_block",
        "resource_id": str(context["block_id"]),
        "change_set": {"title": title},
    }
    prepared = await context["adapter"].prepare(
        track_id=context["track_id"],
        credential=context["credential"],
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=context["fence"],
        payload=payload,
    )
    return decision, prepared


def synthetic_block_audit_participant(
    database: Any,
    *,
    block_id: ObjectId,
    track_id: str,
    actor_id: str,
    operation_id: str,
    title: str,
    before_audit: Any | None = None,
):
    async def participant(session: Any, receipt: Any) -> None:
        result = await database["content_blocks"].update_one(
            {"_id": block_id, "track_id": track_id},
            {"$set": {"title": title, "editorial_revision": receipt.revision}},
            session=session,
        )
        if result.matched_count != 1:
            raise RuntimeError("synthetic block was not found in its resolved track")
        if before_audit is not None:
            await before_audit()
        await database["edit_history"].insert_one({
            "track_id": track_id,
            "block_id": block_id,
            "actor_id": actor_id,
            "operation_id": operation_id,
            "revision": receipt.revision,
            "event": "block_updated",
        }, session=session)

    return participant
