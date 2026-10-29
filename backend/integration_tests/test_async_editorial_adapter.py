from __future__ import annotations

import asyncio
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

import pytest
from bson import ObjectId
from pymongo import AsyncMongoClient, MongoClient
from pymongo.uri_parser import parse_uri

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.editorial_revision_protocol import (  # noqa: E402
    FencingRejected,
    RevisionConflict,
)
from curriculum_contract.experimental_async_editorial_adapter import (  # noqa: E402
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.experimental_editorial_api_contract import (  # noqa: E402
    minimal_intent_payload,
)
from curriculum_contract.mongodb_editorial_revision_adapter import (  # noqa: E402
    MongoDBEditorialRevisionAdapter,
)


def _uri() -> str:
    value = os.environ.get("C10_TEST_MONGODB_URI")
    if not value:
        raise RuntimeError("C10_TEST_MONGODB_URI must be explicitly set")
    parsed = parse_uri(value)
    if (parsed.get("username") or parsed.get("password") or parsed.get("nodelist") != [("127.0.0.1", 29130)]
        or parsed.get("options", {}).get("replicaSet") != "rsC10"):
        raise RuntimeError("C10 URI does not identify the C10 loopback replica set")
    return value


@asynccontextmanager
async def _database(test_name: str):
    client = AsyncMongoClient(_uri(), serverSelectionTimeoutMS=4000, appname="trilhacode-c10-tests")
    database = None
    marker = f"c10-{uuid.uuid4().hex}"
    try:
        hello = await client.admin.command({"hello": 1})
        server = await client.server_info()
        status = await client.admin.command({"serverStatus": 1})
        if (not str(server.get("version", "")).startswith("7.") or hello.get("setName") != "rsC10"
            or not hello.get("isWritablePrimary") or hello.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"):
            raise RuntimeError("C10 MongoDB topology was not verified")
        suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", test_name)[:16]
        name = f"editorial_revision_test_c10_{suffix}_{uuid.uuid4().hex[:12]}"
        if name in await client.list_database_names():
            raise RuntimeError("random C10 database name already exists")
        database = client[name]
        await database["_c10_phase_marker"].insert_one({"_id": marker, "phase": "2.1a.12c10"})
        yield client, database
    finally:
        if database is not None:
            found = await database["_c10_phase_marker"].find_one({"_id": marker})
            if found and found.get("phase") == "2.1a.12c10":
                await client.drop_database(database.name)
        await client.close()


async def _ready(client, db, track_id="track-c10"):
    adapter = AsyncEditorialRevisionAdapter(db, namespace="c8_c10")
    await adapter.verify_transaction_topology()
    await adapter.initialize_track(track_id)
    credential = await adapter.provision_writer_credential(track_id, "c10_writer")
    authority = await adapter.provision_fence_authority(track_id, "c10_authority")
    fence = await adapter.advance_fence(track_id, authority)
    await db.edit_history.create_index(
        [("track_id", 1), ("operation_id", 1)], unique=True, name="c10_audit_operation_identity"
    )
    return adapter, credential, authority, fence


def _payload(block_id, data):
    return minimal_intent_payload(
        block_id=str(block_id), changes={"data": data},
        fingerprint_key=b"c10-test-content-hmac-key-32bytes",
    )


def test_async_adapter_audit_failure_rolls_back_and_same_intent_retries():
    async def run():
        async with _database("audit_rollback") as (client, db):
            adapter, credential, _, fence = await _ready(client, db)
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-c10", "data": {"v": 0}})
            prepared = await adapter.prepare(
                track_id="track-c10", credential=credential, operation_id="http_retry_0001",
                expected_revision=0, fencing_token=fence, payload=_payload(block_id, {"secret": "synthetic"}),
            )

            async def fail_audit(session, receipt):
                await db.content_blocks.update_one(
                    {"_id": block_id}, {"$set": {"data": {"v": 1}}}, session=session
                )
                raise RuntimeError("synthetic audit storage failure")

            with pytest.raises(RuntimeError, match="synthetic audit storage failure"):
                await adapter.commit(prepared, credential, participant=fail_audit)
            block = await db.content_blocks.find_one({"_id": block_id})
            assert block["data"] == {"v": 0}
            assert await adapter.current_revision("track-c10") == 0
            assert await db.edit_history.count_documents({}) == 0
            assert await db["c8_c10_history"].count_documents({}) == 0
            assert (await db.c8_c10_operations.find_one({"operation_id": "http_retry_0001"}))["state"] == "PREPARED"

            async def write_both(session, receipt):
                await db.content_blocks.update_one(
                    {"_id": block_id}, {"$set": {"data": {"v": 2}}}, session=session
                )
                await db.edit_history.insert_one({
                    "track_id": receipt.track_id, "operation_id": receipt.operation_id,
                    "revision": receipt.revision, "action": "updated", "entity_id": str(block_id),
                }, session=session)

            receipt = await adapter.commit(prepared, credential, participant=write_both)
            assert (receipt.parent_revision, receipt.revision) == (0, 1)
            assert (await db.content_blocks.find_one({"_id": block_id}))["data"] == {"v": 2}
            assert await db.edit_history.count_documents({}) == 1
            assert await db.c8_c10_history.count_documents({}) == 1
            assert (await adapter.commit(prepared, credential, participant=fail_audit)).replayed

    asyncio.run(run())


def test_async_adapter_cas_concurrency_and_fencing_share_track_authority():
    async def run():
        async with _database("cas_fence") as (client, db):
            adapter, credential, authority, fence = await _ready(client, db)
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-c10", "title": "old"})
            p1 = await adapter.prepare(track_id="track-c10", credential=credential,
                operation_id="http_cas_00000001", expected_revision=0, fencing_token=fence,
                payload=minimal_intent_payload(block_id=str(block_id), changes={"title": "a"},
                                               fingerprint_key=b"c10-test-content-hmac-key-32bytes"))
            p2 = await adapter.prepare(track_id="track-c10", credential=credential,
                operation_id="http_cas_00000002", expected_revision=0, fencing_token=fence,
                payload=minimal_intent_payload(block_id=str(block_id), changes={"title": "b"},
                                               fingerprint_key=b"c10-test-content-hmac-key-32bytes"))

            async def participant(target_db, title):
                async def write(session, receipt):
                    await target_db.content_blocks.update_one(
                        {"_id": block_id}, {"$set": {"title": title}}, session=session
                    )
                    await target_db.edit_history.insert_one({"track_id": receipt.track_id,
                        "operation_id": receipt.operation_id, "revision": receipt.revision}, session=session)
                return write

            second_client = AsyncMongoClient(_uri(), serverSelectionTimeoutMS=4000,
                                             appname="trilhacode-c10-second-client")
            try:
                second_adapter = AsyncEditorialRevisionAdapter(second_client[db.name], namespace="c8_c10")
                await second_adapter.verify_transaction_topology()
                results = await asyncio.gather(
                    adapter.commit(p1, credential, participant=await participant(db, "a")),
                    second_adapter.commit(p2, credential,
                                         participant=await participant(second_client[db.name], "b")),
                    return_exceptions=True,
                )
            finally:
                await second_client.close()
            assert sum(not isinstance(value, Exception) for value in results) == 1
            assert sum(isinstance(value, RevisionConflict) for value in results) == 1, [
                (type(value).__name__, str(value)) for value in results
            ]
            assert await adapter.current_revision("track-c10") == 1
            assert await db.edit_history.count_documents({}) == 1

            stale = await adapter.prepare(track_id="track-c10", credential=credential,
                operation_id="http_fence_old_0001", expected_revision=1, fencing_token=fence,
                payload={"operation_kind": "block.update", "payload_schema_version": 1})
            new_fence = await adapter.advance_fence("track-c10", authority)
            with pytest.raises(FencingRejected):
                await adapter.commit(stale, credential)
            assert new_fence == fence + 1
            assert await adapter.current_revision("track-c10") == 1

    asyncio.run(run())


def test_async_adapter_cancellation_before_commit_and_thread_bridge_conformance():
    async def run():
        async with _database("cancel_compare") as (client, db):
            adapter, credential, _, fence = await _ready(client, db, "track-native")
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-native", "title": "old"})
            prepared = await adapter.prepare(track_id="track-native", credential=credential,
                operation_id="http_cancel_0000001", expected_revision=0, fencing_token=fence,
                payload={"operation_kind": "block.update", "payload_schema_version": 1,
                         "block_ref": str(block_id), "changed_fields": ["title"]})
            entered = asyncio.Event()
            release = asyncio.Event()
            async def blocked_participant(session, receipt):
                await db.content_blocks.update_one({"_id": block_id}, {"$set": {"title": "uncommitted"}}, session=session)
                entered.set()
                await release.wait()

            pending = asyncio.create_task(adapter.commit(prepared, credential, participant=blocked_participant))
            await asyncio.wait_for(entered.wait(), timeout=4)
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
            assert await adapter.current_revision("track-native") == 0
            assert (await db.content_blocks.find_one({"_id": block_id}))["title"] == "old"

            # Compare the same C8-shaped transaction through the synchronous adapter
            # on a worker thread and the native async adapter; this is contract parity,
            # not a production benchmark.
            def sync_commit():
                sync_client = MongoClient(_uri(), serverSelectionTimeoutMS=4000, appname="trilhacode-c10-thread")
                try:
                    sync_db = sync_client[db.name]
                    sync = MongoDBEditorialRevisionAdapter(sync_db, namespace="c8_thread")
                    sync.verify_transaction_topology()
                    sync.initialize_track("track-thread")
                    writer = sync.provision_writer_credential("track-thread", "c10_writer")
                    fence_authority = sync.provision_fence_authority("track-thread", "c10_authority")
                    thread_fence = sync.advance_fence("track-thread", fence_authority)
                    obj_id = ObjectId()
                    sync_db.content_blocks.insert_one({"_id": obj_id, "track_id": "track-thread", "title": "old"})
                    intent = {"operation_kind": "block.update", "payload_schema_version": 1,
                              "block_ref": str(obj_id), "changed_fields": ["title"]}
                    proposal = sync.prepare(track_id="track-thread", credential=writer,
                        operation_id="http_thread_000001", expected_revision=0,
                        fencing_token=thread_fence, payload=intent)
                    def write(session, receipt):
                        sync_db.content_blocks.update_one({"_id": obj_id}, {"$set": {"title": "new"}}, session=session)
                        sync_db.edit_history.insert_one({"track_id": receipt.track_id,
                            "operation_id": receipt.operation_id, "revision": receipt.revision}, session=session)
                    result = sync.commit(proposal, writer, _transaction_participant=write)
                    return result.revision, sync_db.edit_history.count_documents({"track_id": "track-thread"})
                finally:
                    sync_client.close()

            ticks = 0
            async def heartbeat():
                nonlocal ticks
                for _ in range(20):
                    ticks += 1
                    await asyncio.sleep(0.001)
            started = perf_counter()
            thread_result, _ = await asyncio.gather(asyncio.to_thread(sync_commit), heartbeat())
            thread_duration = perf_counter() - started
            assert thread_result == (1, 1) and ticks == 20 and thread_duration > 0

            native_prepared = await adapter.prepare(track_id="track-native", credential=credential,
                operation_id="http_native_000001", expected_revision=0, fencing_token=fence,
                payload={"operation_kind": "block.update", "payload_schema_version": 1,
                         "block_ref": str(block_id), "changed_fields": ["title"]})
            async def native_write(session, receipt):
                await db.content_blocks.update_one({"_id": block_id}, {"$set": {"title": "native"}}, session=session)
                await db.edit_history.insert_one({"track_id": receipt.track_id,
                    "operation_id": receipt.operation_id, "revision": receipt.revision}, session=session)
            native_receipt = await adapter.commit(native_prepared, credential, participant=native_write)
            assert (native_receipt.revision, await db.edit_history.count_documents({"track_id": "track-native"})) == (1, 1)

    asyncio.run(run())
