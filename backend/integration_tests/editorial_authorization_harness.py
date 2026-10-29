"""Disposable C11 harness; imports no active FastAPI app or database module."""

from __future__ import annotations

import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Mapping

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

from curriculum_contract.editorial_revision_protocol import RevisionReceipt
from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter
from curriculum_contract.experimental_editorial_authorization import (
    AuthorizationCode,
    EditorialAuthorizationError,
    EditorialCapability,
    MongoEditorialAuthorizationGate,
    ServerWriterContext,
    SyntheticPrincipalAuthority,
)
from curriculum_contract.experimental_editorial_privacy import (
    VersionedEditorialHmacKeyring,
    build_minimal_intent,
)
from curriculum_contract.experimental_editorial_replay_policy import InternalReconciliationAuthority

_EXPECTED_HOST = "127.0.0.1"
_EXPECTED_PORT = 29131
_EXPECTED_REPLICA_SET = "rsC11"


class SyntheticBlockNotFound(RuntimeError):
    pass


def c11_test_uri() -> str:
    value = os.environ.get("C11_TEST_MONGODB_URI")
    if not value:
        raise RuntimeError("C11_TEST_MONGODB_URI must explicitly identify the disposable service")
    # Reject SRV before PyMongo parses it: URI parsing performs DNS discovery.
    if not value.startswith("mongodb://"):
        raise RuntimeError("C11 tests accept only the explicit loopback MongoDB URI scheme")
    parsed = parse_uri(value)
    if (
        parsed.get("username")
        or parsed.get("password")
        or parsed.get("nodelist") != [(_EXPECTED_HOST, _EXPECTED_PORT)]
        or parsed.get("options", {}).get("replicaSet") != _EXPECTED_REPLICA_SET
        or parsed.get("options", {}).get("directConnection")
    ):
        raise RuntimeError("C11 URI does not identify the expected loopback replica set")
    return value


@asynccontextmanager
async def isolated_database(test_name: str) -> AsyncIterator[tuple[Any, Any]]:
    """Use a unique DB and drop it only after verifying its phase marker."""

    uri = c11_test_uri()
    client: Any = AsyncMongoClient(
        uri, serverSelectionTimeoutMS=4000, appname="trilhacode-c11-isolated-tests"
    )
    database = None
    marker = f"c11-{uuid.uuid4().hex}"
    try:
        hello = await client.admin.command({"hello": 1})
        server = await client.server_info()
        status = await client.admin.command({"serverStatus": 1})
        if (
            not str(server.get("version", "")).startswith("7.")
            or hello.get("setName") != _EXPECTED_REPLICA_SET
            or not hello.get("isWritablePrimary")
            or hello.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"
        ):
            raise RuntimeError("C11 MongoDB identity/topology was not positively verified")
        suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", test_name)[:16]
        name = f"editorial_revision_test_c10_c11_{suffix}_{uuid.uuid4().hex[:12]}"
        if name in await client.list_database_names():
            raise RuntimeError("random C11 database name already exists")
        database = client[name]
        await database["_c11_phase_marker"].insert_one(
            {"_id": marker, "phase": "2.1a.12c11", "test": suffix}
        )
        yield client, database
    finally:
        if database is not None:
            proof = await database["_c11_phase_marker"].find_one(
                {"_id": marker, "phase": "2.1a.12c11"}
            )
            if proof is not None:
                await client.drop_database(database.name)
        await client.close()


async def ready_track(
    client: Any,
    database: Any,
    *,
    track_id: str = "track-c11-synthetic",
    actor_id: str = "actor-c11-synthetic",
    session_id: str = "session-c11-synthetic",
    role: str = "editor",
    permissions: tuple[str, ...] = ("content.write",),
    grant_track_id: str | None = None,
    global_admin_scope: bool = False,
) -> dict[str, Any]:
    adapter = AsyncEditorialRevisionAdapter(database, namespace="c8_c11")
    topology = await adapter.verify_transaction_topology()
    await adapter.initialize_track(track_id)
    credential = await adapter.provision_writer_credential(track_id, "c11_writer")
    authority = await adapter.provision_fence_authority(track_id, "c11_fence_authority")
    fence = await adapter.advance_fence(track_id, authority)
    gate = MongoEditorialAuthorizationGate(
        database,
        namespace="c8_c11",
        capability_key=b"c11-synthetic-capability-signing-key-32-bytes",
    )
    principal_authority = SyntheticPrincipalAuthority(
        b"c11-synthetic-principal-attestation-key-32-bytes"
    )
    reconciliation_authority = InternalReconciliationAuthority(
        b"c11-synthetic-internal-reconciliation-key-32bytes"
    )
    principal = principal_authority.attest(
        actor_id=actor_id,
        session_id=session_id,
        role=role,
        permissions=permissions,
    )
    scope = grant_track_id or track_id
    if global_admin_scope:
        scope = "*"
    await gate.provision_synthetic_scope(
        actor_id=actor_id,
        session_id=session_id,
        track_id=scope,
        permissions=permissions,
        allowed_operations=("block.update",),
        role=role,
        global_admin_scope=global_admin_scope,
    )
    await database["edit_history"].create_index(
        [("track_id", 1), ("operation_id", 1)],
        unique=True,
        name="c11_audit_operation_identity",
    )
    return {
        "adapter": adapter,
        "gate": gate,
        "principal_authority": principal_authority,
        "reconciliation_authority": reconciliation_authority,
        "principal": principal,
        "credential": credential,
        "writer_context": ServerWriterContext(credential, fence),
        "authority": authority,
        "fence": fence,
        "track_id": track_id,
        "actor_id": actor_id,
        "session_id": session_id,
        "topology": topology,
    }


async def prepare_authorized_update(
    database: Any,
    context: Mapping[str, Any],
    *,
    block_id: ObjectId,
    expected_revision: int,
    operation_id: str,
    changes: Mapping[str, Any],
    keyring: VersionedEditorialHmacKeyring,
    key_id: str | None = None,
    requested_track_id: str | None = None,
) -> tuple[EditorialCapability, Any, dict[str, Any]]:
    """Resolve track from stored block, authorize, prepare and bind capability."""

    preflight = context["gate"].preflight_principal(
        context["principal"], context["principal_authority"]
    )
    if preflight is not AuthorizationCode.ALLOWED:
        raise EditorialAuthorizationError(preflight)
    block = await database["content_blocks"].find_one(
        {"_id": block_id}, {"track_id": 1}
    )
    if block is None:
        # A removed resource is eligible only for reconciliation of an already
        # committed operation under the explicit route scope; this branch never
        # recreates a block and is later fingerprint-checked by C8 prepare.
        resolved_track_id = requested_track_id or ""
        committed = await database["c8_c11_operations"].find_one(
            {
                "track_id": resolved_track_id,
                "operation_id": operation_id,
                "state": "COMMITTED",
            },
            {"_id": 1},
        ) if resolved_track_id else None
        if committed is None:
            raise EditorialAuthorizationError(AuthorizationCode.RESOURCE_NOT_FOUND)
    elif not isinstance(block.get("track_id"), str):
        raise EditorialAuthorizationError(AuthorizationCode.RESOURCE_NOT_FOUND)
    else:
        resolved_track_id = block["track_id"]
    if requested_track_id is not None and requested_track_id != resolved_track_id:
        raise EditorialAuthorizationError(AuthorizationCode.TRACK_SCOPE_DENIED)
    if resolved_track_id != context["track_id"]:
        raise EditorialAuthorizationError(AuthorizationCode.TRACK_SCOPE_DENIED)
    payload = build_minimal_intent(
        track_id=resolved_track_id,
        block_id=str(block_id),
        expected_revision=expected_revision,
        operation_kind="block.update",
        changes=changes,
        keyring=keyring,
        key_id=key_id,
    )
    decision = await context["gate"].issue_capability(
        context["principal"],
        context["principal_authority"],
        track_id=resolved_track_id,
        operation_kind="block.update",
        operation_id=operation_id,
        expected_revision=expected_revision,
        writer_context=context["writer_context"],
    )
    if not decision.allowed or decision.capability is None:
        raise EditorialAuthorizationError(decision.code)
    prepared = await context["adapter"].prepare(
        track_id=resolved_track_id,
        credential=context["credential"],
        operation_id=operation_id,
        expected_revision=expected_revision,
        fencing_token=context["writer_context"].fencing_token,
        payload=payload,
    )
    capability = context["gate"].bind_preparation(decision.capability, prepared)
    return capability, prepared, payload


def block_audit_participant(
    database: Any,
    *,
    block_id: ObjectId,
    track_id: str,
    actor_id: str,
    changes: Mapping[str, Any],
    resource_ref_hmac: str,
    before_audit: Any = None,
):
    """Create a synthetic block + mandatory audit participant for a transaction."""

    async def participant(session: Any, receipt: RevisionReceipt) -> None:
        updated = await database["content_blocks"].update_one(
            {"_id": block_id, "track_id": track_id},
            {"$set": dict(changes)},
            session=session,
        )
        if updated.matched_count != 1:
            raise SyntheticBlockNotFound("synthetic block is missing or out of scope")
        if before_audit is not None:
            result = before_audit()
            if hasattr(result, "__await__"):
                await result
        await database["edit_history"].insert_one(
            {
                "track_id": track_id,
                "operation_id": receipt.operation_id,
                "revision": receipt.revision,
                "parent_revision": receipt.parent_revision,
                "entity": "block",
                "resource_ref_hmac": resource_ref_hmac,
                "action": "updated",
                "actor_id": actor_id,
                "changed_fields": sorted(changes),
                "synthetic_event_at": datetime.now(timezone.utc),
            },
            session=session,
        )

    return participant


async def resolve_requested_block_scope(
    database: Any, *, block_id: ObjectId, requested_track_id: str
) -> tuple[AuthorizationCode, str | None]:
    """Server lookup; client track must equal the block's persisted track."""

    document = await database["content_blocks"].find_one(
        {"_id": block_id}, {"track_id": 1}
    )
    if document is None:
        return AuthorizationCode.RESOURCE_NOT_FOUND, None
    track_id = document.get("track_id")
    if not isinstance(track_id, str) or not track_id:
        return AuthorizationCode.INDETERMINATE, None
    if track_id != requested_track_id:
        return AuthorizationCode.TRACK_SCOPE_DENIED, None
    return AuthorizationCode.ALLOWED, track_id
