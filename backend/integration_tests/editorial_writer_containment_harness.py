"""Disposable MongoDB 7 fixture for the C16 writer-containment tests.

No work is performed on import. Persistent tests require explicitly supplied,
phase-local root credentials and verify the Docker resource labels, topology,
temporary storage and internal network before writing. MongoDB publishes no port;
the host preflight is relayed to a Python test-runner container on that network.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator
from urllib.parse import quote

from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

from curriculum_contract.editorial_revision_protocol import (
    FenceAuthorityCredential,
)
from curriculum_contract.experimental_async_editorial_adapter import (
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.experimental_editorial_writer_containment import (
    C16Writer,
    WriterFamily,
)

PHASE_LABEL = "2.1a.12c16"
CONTAINER_NAME = "trilhacode-c16-writer-containment-mongo"
NETWORK_NAME = "trilhacode-c16-writer-containment-net"
IMAGE = "mongo:7.0.43"
IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
REPLICA_SET = "rsC16"
DATABASE_PREFIX = "editorial_revision_test_c10_c16_"
NAMESPACE = "c8_c16"
ROOT_URI_ENV = "C16_ROOT_MONGODB_URI"
_ROOT_URI = re.compile(
    rf"^mongodb://c16-root:[A-Za-z0-9_-]{{32,96}}@mongo-c16:27017/"
    rf"\?authSource=admin&replicaSet={REPLICA_SET}$"
)
_VERIFIED_RESOURCES = False


@dataclass(slots=True)
class DisposableDatabase:
    root_client: AsyncMongoClient
    app_client: AsyncMongoClient
    database: Any
    database_name: str
    marker: str
    app_username: str
    app_uri: str
    writer: C16Writer


def _docker_json(*args: str) -> Any:
    result = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout)


def verify_owned_docker_resources() -> None:
    """Fail closed unless host preflight or direct Docker inspection proves ownership."""

    global _VERIFIED_RESOURCES
    if _VERIFIED_RESOURCES:
        return
    if os.environ.get("C16_DOCKER_PRECHECKED") == "true":
        container_id = os.environ.get("C16_DOCKER_RESOURCE_ID", "")
        network_id = os.environ.get("C16_DOCKER_NETWORK_ID", "")
        if not re.fullmatch(r"[a-f0-9]{64}", container_id) or not re.fullmatch(
            r"[a-f0-9]{64}", network_id
        ):
            raise RuntimeError("host Docker preflight identity is missing or malformed")
        _VERIFIED_RESOURCES = True
        return
    container = _docker_json("inspect", CONTAINER_NAME)[0]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != PHASE_LABEL:
        raise RuntimeError("C16 Mongo container ownership label does not match")
    if not container["State"]["Running"] or container["Image"] != IMAGE_ID:
        raise RuntimeError("C16 must use the running, pinned MongoDB 7.0.43 image")
    if container["Mounts"]:
        raise RuntimeError("C16 Mongo must not use persistent Docker volumes")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("C16 database storage must be tmpfs-only")
    bindings = container["HostConfig"].get("PortBindings") or {}
    if any(value for value in bindings.values()):
        raise RuntimeError("C16 Mongo must not publish ports")
    attached = container["NetworkSettings"]["Networks"]
    if set(attached) != {NETWORK_NAME}:
        raise RuntimeError("C16 Mongo must be attached only to the C16 network")

    network = _docker_json("network", "inspect", NETWORK_NAME)[0]
    network_labels = network.get("Labels") or {}
    if (
        network_labels.get("io.trilhacode.phase") != PHASE_LABEL
        or network.get("Driver") != "bridge"
        or network.get("Internal") is not True
        or set(network.get("Containers", {})) != {container["Id"]}
    ):
        raise RuntimeError("C16 Docker network is not private and exclusively owned")
    _VERIFIED_RESOURCES = True


def _root_uri() -> str:
    value = os.environ.get(ROOT_URI_ENV, "")
    if not value or not _ROOT_URI.fullmatch(value):
        raise RuntimeError(f"{ROOT_URI_ENV} must identify only the private C16 replica set")
    parsed = parse_uri(value)
    if (
        parsed.get("nodelist") != [("mongo-c16", 27017)]
        or parsed.get("username") != "c16-root"
        or parsed.get("password") is None
        or parsed.get("options", {}).get("replicaSet") != REPLICA_SET
    ):
        raise RuntimeError("C16 root URI failed private-network allowlist validation")
    if parsed.get("database") not in (None, ""):
        raise RuntimeError("C16 root URI cannot select a database")
    return value


@asynccontextmanager
async def disposable_database(test_name: str) -> AsyncIterator[DisposableDatabase]:
    verify_owned_docker_resources()
    uri = _root_uri()
    root: AsyncMongoClient = AsyncMongoClient(
        uri, serverSelectionTimeoutMS=5000, appname="trilhacode-c16-root"
    )
    app: AsyncMongoClient | None = None
    database_name = f"{DATABASE_PREFIX}{uuid.uuid4().hex[:16]}"
    marker = f"c16-{uuid.uuid4().hex}"
    username = f"c16app{uuid.uuid4().hex[:12]}"
    password = uuid.uuid4().hex + uuid.uuid4().hex
    database = root[database_name]
    created_marker = False
    try:
        server = await root.admin.command({"hello": 1})
        build = await root.server_info()
        status = await root.admin.command({"serverStatus": 1})
        if (
            not str(build.get("version", "")).startswith("7.")
            or server.get("setName") != REPLICA_SET
            or server.get("isWritablePrimary") is not True
            or server.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"
        ):
            raise RuntimeError("C16 server is not the verified MongoDB 7 WiredTiger replica set")
        if database_name in await root.list_database_names():
            raise RuntimeError("random C16 database name unexpectedly already exists")
        await database["_c16_identity"].insert_one(
            {"_id": "owner", "phase": PHASE_LABEL, "marker": marker, "test": test_name}
        )
        created_marker = True
        await database.command(
            "createUser",
            username,
            pwd=password,
            roles=[{"role": "readWrite", "db": database_name}],
        )
        app_uri = (
            f"mongodb://{quote(username)}:{quote(password)}@mongo-c16:27017/"
            f"{database_name}?authSource={database_name}&replicaSet={REPLICA_SET}"
        )
        app = AsyncMongoClient(
            app_uri, serverSelectionTimeoutMS=5000, appname="trilhacode-c16-app"
        )
        app_database = app[database_name]
        await app_database.command("ping")
        adapter = AsyncEditorialRevisionAdapter(app_database, namespace=NAMESPACE)
        await adapter.verify_transaction_topology()
        track_id = "track-c16-synthetic"
        await adapter.initialize_track(track_id)
        credentials = {
            family: await adapter.provision_writer_credential(
                track_id, f"c16-{family.value}"
            )
            for family in WriterFamily
        }
        authority: FenceAuthorityCredential = await adapter.provision_fence_authority(
            track_id, "c16-fence-authority"
        )
        fence = await adapter.advance_fence(track_id, authority)
        await app_database.edit_history.create_index(
            [("track_id", 1), ("operation_id", 1)],
            unique=True,
            name="c16_audit_operation_identity",
        )
        block_id = "block-c16-synthetic"
        node_id = "node-c16-synthetic"
        await app_database.tracks.insert_one(
            {"_id": track_id, "status": "draft", "published_revision": 0}
        )
        await app_database.nodes.insert_one(
            {"_id": node_id, "track_id": track_id, "title": "synthetic-node", "order": 0}
        )
        await app_database.content_blocks.insert_one(
            {
                "_id": block_id,
                "track_id": track_id,
                "node_id": node_id,
                "title": "synthetic-original",
            }
        )
        await app_database.progress.insert_one(
            {
                "_id": "progress-c16-synthetic",
                "track_id": track_id,
                "generation_id": "generation-c16-1",
                "completed": True,
                "attempt_count": 2,
            }
        )
        await app_database.activity_attempts.insert_one(
            {
                "_id": "attempt-c16-synthetic",
                "track_id": track_id,
                "generation_id": "generation-c16-1",
                "attempt": 1,
            }
        )
        writer = C16Writer(
            client=app,
            database=app_database,
            adapter=adapter,
            credentials=credentials,
            track_id=track_id,
            block_id=block_id,
            node_id=node_id,
            fencing_token=fence,
        )
        yield DisposableDatabase(
            root_client=root,
            app_client=app,
            database=app_database,
            database_name=database_name,
            marker=marker,
            app_username=username,
            app_uri=app_uri,
            writer=writer,
        )
    finally:
        if app is not None:
            await app.close()
        if created_marker:
            owner = await database["_c16_identity"].find_one({"_id": "owner"})
            if owner != {
                "_id": "owner",
                "phase": PHASE_LABEL,
                "marker": marker,
                "test": test_name,
            }:
                await root.close()
                raise RuntimeError("C16 database ownership marker changed; refusing cleanup")
            await root.drop_database(database_name)
        await root.close()


def new_operation_id() -> str:
    return f"c16-op-{uuid.uuid4().hex}"
