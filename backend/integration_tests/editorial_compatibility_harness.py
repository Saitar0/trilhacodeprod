"""Positive isolation checks and synthetic fixtures for the C9 experiments."""

from __future__ import annotations

import json
import os
import subprocess
from secrets import token_hex
from typing import Any

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri

PHASE_LABEL = "2.1a.12c9"
CONTAINER_NAME = "trilhacode-12c9-mongo"
NETWORK_NAME = "trilhacode-12c9-editorial-net"
IMAGE = "mongo:7.0.43"
IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
PORT = 29127
REPLICA_SET = "rs12c9"
DATABASE_PREFIX = "editorial_revision_test_c9_"
URI_ENV = "TRILHACODE_C9_MONGODB_URI"
CONTAINER_ID_ENV = "TRILHACODE_C9_CONTAINER_ID"
NETWORK_ID_ENV = "TRILHACODE_C9_NETWORK_ID"


def _docker_json(*args: str) -> Any:
    result = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=10
    )
    return json.loads(result.stdout)


def verify_owned_docker_resources() -> tuple[str, str]:
    """Require the exact C9 container/network envelope before database access."""

    containers = _docker_json("inspect", CONTAINER_NAME)
    if len(containers) != 1:
        raise RuntimeError("exactly one named C9 MongoDB container is required")
    container = containers[0]
    container_id = container["Id"]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != PHASE_LABEL:
        raise RuntimeError("Mongo container is not owned by phase 12C.9")
    if container["Config"]["Image"] != IMAGE or container["Image"] != IMAGE_ID:
        raise RuntimeError("Mongo container image does not match the local verified image")
    if not container["State"]["Running"]:
        raise RuntimeError("phase-owned Mongo container is not running")
    if container["Mounts"]:
        raise RuntimeError("Mongo container has an unexpected volume or bind mount")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("Mongo data directories are not confined to tmpfs")
    bindings = container["HostConfig"]["PortBindings"].get(f"{PORT}/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]:
        raise RuntimeError("Mongo port is not restricted to the C9 loopback binding")
    if os.environ.get(CONTAINER_ID_ENV) != container_id:
        raise RuntimeError("explicit C9 container ID does not match Docker metadata")

    attached_networks = container["NetworkSettings"]["Networks"]
    if set(attached_networks) != {NETWORK_NAME}:
        raise RuntimeError("Mongo container has an unexpected network attachment")
    networks = _docker_json("network", "inspect", NETWORK_NAME)
    if len(networks) != 1:
        raise RuntimeError("exactly one named C9 network is required")
    network = networks[0]
    network_id = network["Id"]
    network_labels = network.get("Labels") or {}
    options = network.get("Options") or {}
    if network_labels.get("io.trilhacode.phase") != PHASE_LABEL:
        raise RuntimeError("Docker network is not owned by phase 12C.9")
    if network["Driver"] != "bridge" or network["Internal"]:
        raise RuntimeError("C9 uses the dedicated bridge needed for loopback forwarding")
    if options.get("com.docker.network.bridge.enable_ip_masquerade") != "false":
        raise RuntimeError("C9 network must disable outbound masquerading")
    if options.get("com.docker.network.bridge.enable_icc") != "false":
        raise RuntimeError("C9 network must disable inter-container communication")
    if set(network["Containers"]) != {container_id}:
        raise RuntimeError("C9 network contains a container not owned by this phase")
    if os.environ.get(NETWORK_ID_ENV) != network_id:
        raise RuntimeError("explicit C9 network ID does not match Docker metadata")
    return container_id, network_id


def verified_uri() -> str:
    uri = os.environ.get(URI_ENV, "")
    if uri != f"mongodb://127.0.0.1:{PORT}/?replicaSet={REPLICA_SET}":
        raise RuntimeError("an explicit credential-free C9 loopback URI is required")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", PORT)]:
        raise RuntimeError("test URI must point only to the C9 loopback port")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("C9 does not accept operational credentials")
    if parsed["options"].get("replicaSet") != REPLICA_SET:
        raise RuntimeError("test URI must select only the C9 replica set")
    if parsed["database"] not in (None, ""):
        raise RuntimeError("test URI cannot select a pre-existing database")
    return uri


def verify_server(client: MongoClient) -> dict[str, str]:
    hello = client.admin.command("hello")
    build = client.admin.command("buildInfo")
    status = client.admin.command("replSetGetStatus")
    storage = client.admin.command("serverStatus")["storageEngine"]["name"]
    if build["version"] != "7.0.43":
        raise RuntimeError("C9 server must be MongoDB 7.0.43")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary"):
        raise RuntimeError("C9 MongoDB must be the writable primary of rs12c9")
    if hello.get("logicalSessionTimeoutMinutes") is None:
        raise RuntimeError("C9 MongoDB does not expose logical sessions")
    if len(status["members"]) != 1 or status["members"][0]["stateStr"] != "PRIMARY":
        raise RuntimeError("C9 topology must be a one-member primary replica set")
    if storage != "wiredTiger":
        raise RuntimeError("C9 requires WiredTiger")
    return {
        "version": build["version"],
        "replica_set": hello["setName"],
        "storage_engine": storage,
        "member_state": status["members"][0]["stateStr"],
    }


def new_database_name() -> str:
    return DATABASE_PREFIX + token_hex(8)


def ensure_versioned_legacy_indexes(database: Any) -> None:
    """Mirror only the relevant source-defined content_blocks/edit_history indexes."""

    database["content_blocks"].create_index(
        [("node_id", 1), ("order", 1)], name="c9_source_node_order"
    )
    database["content_blocks"].create_index(
        [("track_id", 1), ("meta.import_ref", 1)],
        unique=True,
        partialFilterExpression={"meta.import_ref": {"$type": "string"}},
        name="c9_source_block_import_ref",
    )
    database["edit_history"].create_index(
        [("track_id", 1), ("at", -1)], name="c9_source_history_track_time"
    )
    database["edit_history"].create_index(
        [("import_operation_id", 1)],
        unique=True,
        partialFilterExpression={"import_operation_id": {"$type": "string"}},
        name="c9_source_import_audit_operation",
    )


def legacy_audit_row(*, track_id: str, entity_id: str, at: Any) -> dict[str, Any]:
    """Return a synthetic record shaped like the current backend/audit.py insert."""

    return {
        "entity": "block",
        "entity_id": entity_id,
        "action": "updated",
        "track_id": track_id,
        "summary": "theory_text",
        "user_id": "synthetic-editor",
        "user_name": "Synthetic editor",
        "at": at,
    }
