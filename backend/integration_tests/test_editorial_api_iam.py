from __future__ import annotations

import asyncio
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter  # noqa: E402
from curriculum_contract.experimental_editorial_api_contract import (  # noqa: E402
    TestCapabilityAuthority as CapabilityAuthority,
)
from integration_tests.editorial_api_iam_harness import build_editorial_api_test_app  # noqa: E402


def _uri() -> str:
    value = os.environ.get("C10_TEST_MONGODB_URI")
    if not value:
        raise RuntimeError("C10_TEST_MONGODB_URI must be explicitly set for the disposable service")
    parsed = parse_uri(value)
    if (parsed.get("username") or parsed.get("password") or parsed.get("nodelist") != [("127.0.0.1", 29130)]
        or parsed.get("options", {}).get("replicaSet") != "rsC10"):
        raise RuntimeError("C10 URI does not identify the expected loopback replica set")
    return value


@asynccontextmanager
async def _isolated_database(test_name: str):
    uri = _uri()
    client = AsyncMongoClient(uri, serverSelectionTimeoutMS=4000, appname="trilhacode-c10-tests")
    database = None
    marker = f"c10-{uuid.uuid4().hex}"
    try:
        hello = await client.admin.command({"hello": 1})
        info = await client.server_info()
        status = await client.admin.command({"serverStatus": 1})
        if (not str(info.get("version", "")).startswith("7.")
            or hello.get("setName") != "rsC10"
            or not hello.get("isWritablePrimary")
            or hello.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"):
            raise RuntimeError("C10 MongoDB identity/topology was not positively verified")
        suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", test_name)[:16]
        name = f"editorial_revision_test_c10_{suffix}_{uuid.uuid4().hex[:12]}"
        if name in await client.list_database_names():
            raise RuntimeError("random C10 database name collided")
        database = client[name]
        await database["_c10_phase_marker"].insert_one(
            {"_id": marker, "phase": "2.1a.12c10", "test": suffix}
        )
        yield client, database
    finally:
        if database is not None:
            stored = await database["_c10_phase_marker"].find_one({"_id": marker})
            if stored and stored.get("phase") == "2.1a.12c10":
                await client.drop_database(database.name)
        await client.close()


async def _ready(client, database, track_id="track-c10"):
    adapter = AsyncEditorialRevisionAdapter(database, namespace="c8_c10")
    topology = await adapter.verify_transaction_topology()
    await adapter.initialize_track(track_id)
    credential = await adapter.provision_writer_credential(track_id, "editorial_api")
    authority = await adapter.provision_fence_authority(track_id, "c10_fence_authority")
    fence = await adapter.advance_fence(track_id, authority)
    await database["edit_history"].create_index(
        [("track_id", 1), ("operation_id", 1)], unique=True, name="c10_audit_operation_identity"
    )
    assert topology.replica_set == "rsC10"
    return adapter, credential, fence


def _app(database, adapter, credential, fence, track_id="track-c10", role="editor"):
    actor_id = "synthetic-actor-17"
    authority = CapabilityAuthority(
        credentials={track_id: credential},
        fences={track_id: fence},
        allowed_scopes={(actor_id, track_id, "block.update")},
    )
    app = build_editorial_api_test_app(
        database=database,
        adapter=adapter,
        capability_authority=authority,
        operation_hmac_key=b"c10-test-operation-hmac-key-32bytes",
        content_hmac_key=b"c10-test-content-hmac-key-32bytes",
        principal={"id": actor_id, "name": "Synthetic editor", "role": role},
    )
    return app, authority


def test_api_iam_headers_replay_private_content_and_delete_replay():
    async def run():
        async with _isolated_database("api_replay") as (client, db):
            adapter, credential, fence = await _ready(client, db)
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-c10", "title": "old"})
            app, _ = _app(db, adapter, credential, fence)
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://c10.test") as http:
                headers = {"If-Match": '"editorial-rev-0"', "Idempotency-Key": "c10-key-000000000001"}
                body = {"data": {"answer": "synthetic-private-value"}, "title": "new"}
                first = await http.put(
                    f"/api/v2/tracks/track-c10/blocks/{block_id}", json=body, headers=headers
                )
                assert first.status_code == 200
                assert first.json() == {"revision": 1, "parent_revision": 0}
                assert first.headers["etag"] == '"editorial-rev-1"'
                assert first.headers["idempotency-replayed"] == "false"
                replay = await http.put(
                    f"/api/v2/tracks/track-c10/blocks/{block_id}", json=body, headers=headers
                )
                assert replay.status_code == 200 and replay.json() == first.json()
                assert replay.headers["idempotency-replayed"] == "true"
                app.state.principal["role"] = "student"
                denied_replay = await http.put(
                    f"/api/v2/tracks/track-c10/blocks/{block_id}", json=body, headers=headers
                )
                assert denied_replay.status_code == 403
                app.state.principal["role"] = "editor"
                assert await db.edit_history.count_documents({}) == 1
                assert await db["c8_c10_history"].count_documents({}) == 1
                operation = await db["c8_c10_operations"].find_one({"state": "COMMITTED"})
                history = await db["c8_c10_history"].find_one({})
                assert "synthetic-private-value" not in operation["payload_json"]
                assert "synthetic-private-value" not in history["payload_json"]
                assert "synthetic-private-value" not in first.text
                stale = await http.put(
                    f"/api/v2/tracks/track-c10/blocks/{block_id}",
                    json={"title": "stale overwrite"},
                    headers={"If-Match": '"editorial-rev-0"',
                             "Idempotency-Key": "c10-key-000000000099"},
                )
                assert stale.status_code == 412
                assert (await db.content_blocks.find_one({"_id": block_id}))["title"] == "new"
                await db.content_blocks.delete_one({"_id": block_id})
                after_delete = await http.put(
                    f"/api/v2/tracks/track-c10/blocks/{block_id}", json=body, headers=headers
                )
                assert after_delete.status_code == 200
                assert after_delete.json() == first.json()
                assert await db.edit_history.count_documents({}) == 1

    asyncio.run(run())


def test_api_uses_real_role_permission_dependency_and_closed_headers_body():
    async def run():
        async with _isolated_database("api_permission") as (client, db):
            adapter, credential, fence = await _ready(client, db)
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-c10"})
            app, _ = _app(db, adapter, credential, fence, role="student")
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://c10.test"
            ) as http:
                good_headers = {"If-Match": '"editorial-rev-0"', "Idempotency-Key": "c10-key-000000000002"}
                path = f"/api/v2/tracks/track-c10/blocks/{block_id}"
                denied = await http.put(path, json={"title": "x"}, headers=good_headers)
                assert denied.status_code == 403
                app.state.principal["role"] = "editor"
                missing_revision = await http.put(
                    path, json={"title": "x"}, headers={"Idempotency-Key": good_headers["Idempotency-Key"]}
                )
                assert missing_revision.status_code == 428
                bad_revision = await http.put(
                    path, json={"title": "x"},
                    headers={"If-Match": "*", "Idempotency-Key": good_headers["Idempotency-Key"]},
                )
                assert bad_revision.status_code == 400
                missing_key = await http.put(path, json={"title": "x"}, headers={"If-Match": good_headers["If-Match"]})
                assert missing_key.status_code == 400
                forged = await http.put(
                    path, json={"title": "x", "fence_token": 999}, headers=good_headers
                )
                assert forged.status_code == 422
                unknown = await http.put(path, json={"title": "x", "admin": True}, headers=good_headers)
                assert unknown.status_code == 422
                assert await db.c8_c10_operations.count_documents({}) == 0

    asyncio.run(run())


def test_api_scope_denied_status_null_and_payload_conflict_are_explicit():
    async def run():
        async with _isolated_database("api_scope_null") as (client, db):
            adapter, credential, fence = await _ready(client, db)
            block_id = ObjectId()
            await db.content_blocks.insert_one({"_id": block_id, "track_id": "track-c10", "status": "draft"})
            app, authority = _app(db, adapter, credential, fence)
            authority._allowed_scopes.clear()
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://c10.test"
            ) as http:
                headers = {"If-Match": '"editorial-rev-0"', "Idempotency-Key": "c10-key-000000000003"}
                path = f"/api/v2/tracks/track-c10/blocks/{block_id}"
                denied = await http.put(path, json={"status": "published"}, headers=headers)
                assert denied.status_code == 403
                authority._allowed_scopes.add(("synthetic-actor-17", "track-c10", "block.update"))
                app.state.principal["id"] = "other-synthetic-actor"
                actor_mismatch = await http.put(path, json={"status": "published"}, headers=headers)
                assert actor_mismatch.status_code == 403
                app.state.principal["id"] = "synthetic-actor-17"
                changed = await http.put(path, json={"status": None}, headers=headers)
                assert changed.status_code == 200
                stored = await db.content_blocks.find_one({"_id": block_id})
                assert stored["status"] is None
                conflicting = await http.put(path, json={"status": "draft"}, headers=headers)
                assert conflicting.status_code == 409
                bad_status = await http.put(
                    path,
                    json={"status": "unknown"},
                    headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "c10-key-000000000004"},
                )
                assert bad_status.status_code == 400

    asyncio.run(run())
