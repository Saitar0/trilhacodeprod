"""Ownership-checked disposable MongoDB access for the Beta 4 experiment."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from secrets import token_hex
from typing import Any

from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

PHASE = "beta4-first-phase-import"
CONTAINER = "trilhacode-beta4-first-phase-mongo"
NETWORK = "trilhacode-beta4-first-phase-net"
IMAGE = "mongo:7.0.43"
IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
PORT = 29164
DB_PREFIX = "beta4_first_phase_"


def _docker_json(*args: str) -> Any:
    completed = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=15,
    )
    return json.loads(completed.stdout)


def verify_owned_disposable() -> None:
    containers = _docker_json("inspect", CONTAINER)
    if len(containers) != 1:
        raise RuntimeError("MongoDB descartável Beta 4 não identificado univocamente")
    container = containers[0]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != PHASE:
        raise RuntimeError("container MongoDB não pertence à Beta 4")
    if not container["State"]["Running"] or container["Config"]["Image"] != IMAGE:
        raise RuntimeError("container Beta 4 não está ativo na imagem esperada")
    if container["Image"] != IMAGE_ID or container.get("Mounts"):
        raise RuntimeError("imagem ou mounts do container Beta 4 divergentes")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("armazenamento MongoDB Beta 4 não está em tmpfs")
    bindings = container["HostConfig"].get("PortBindings", {}).get("27017/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]:
        raise RuntimeError("MongoDB Beta 4 não está restrito à porta loopback esperada")
    if container["HostConfig"].get("NetworkMode") != NETWORK:
        raise RuntimeError("container MongoDB Beta 4 usa rede divergente")
    if set(container["NetworkSettings"]["Networks"]) != {NETWORK}:
        raise RuntimeError("container MongoDB Beta 4 possui rede adicional")
    networks = _docker_json("network", "inspect", NETWORK)
    if len(networks) != 1:
        raise RuntimeError("rede Beta 4 não identificada univocamente")
    network = networks[0]
    if (
        network["Labels"].get("io.trilhacode.phase") != PHASE
        or network["Driver"] != "bridge"
        or network["Internal"] is not False
        or network["Options"].get("com.docker.network.bridge.enable_ip_masquerade") != "false"
        or set(network["Containers"]) != {container["Id"]}
    ):
        raise RuntimeError("rede Beta 4 não é exclusiva ou usa modo interno incompatível com host-loopback")


def verified_uri() -> str:
    uri = os.environ.get("TRILHACODE_BETA4_MONGO_URI", "")
    if uri != f"mongodb://127.0.0.1:{PORT}":
        raise RuntimeError("URI deve apontar somente ao MongoDB descartável Beta 4")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", PORT)]:
        raise RuntimeError("host/porta MongoDB Beta 4 divergente")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("URI Beta 4 não aceita credenciais externas")
    if parsed["database"] not in (None, "") or parsed["options"]:
        raise RuntimeError("URI Beta 4 não pode selecionar banco/opções adicionais")
    return uri


async def open_owned_database() -> tuple[AsyncMongoClient[dict[str, Any]], Any, str]:
    verify_owned_disposable()
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(
        verified_uri(), timeoutMS=8_000, tz_aware=True,
    )
    database_name = DB_PREFIX + token_hex(8)
    database = client[database_name]
    try:
        for attempt in range(20):
            try:
                await client.admin.command("ping")
                break
            except Exception:
                if attempt == 19:
                    raise
                await asyncio.sleep(0.5)
        hello = await client.admin.command("hello")
        build = await client.admin.command("buildInfo")
        status = await client.admin.command("serverStatus")
        if build.get("version") != "7.0.43":
            raise RuntimeError("MongoDB deve ser exatamente 7.0.43")
        if hello.get("setName") is not None or not hello.get("isWritablePrimary"):
            raise RuntimeError("importador não exige replica set; espera-se standalone isolado")
        if status["storageEngine"]["name"] != "wiredTiger":
            raise RuntimeError("WiredTiger é obrigatório")
        run_id = database_name.removeprefix(DB_PREFIX)
        await database["_beta4_identity"].insert_one({
            "_id": "owner", "phase": PHASE, "run_id": run_id,
        })
        return client, database, run_id
    except BaseException:
        await client.close()
        raise


async def drop_owned_database(client: AsyncMongoClient[dict[str, Any]], database: Any, run_id: str) -> None:
    verify_owned_disposable()
    marker = await database["_beta4_identity"].find_one({"_id": "owner"})
    if marker != {"_id": "owner", "phase": PHASE, "run_id": run_id}:
        await client.close()
        raise RuntimeError("marcador de propriedade Beta 4 divergiu; banco preservado")
    if not database.name.startswith(DB_PREFIX):
        await client.close()
        raise RuntimeError("banco fora do prefixo exclusivo Beta 4")
    await client.drop_database(database.name)
    await client.close()


async def seed_import_contract(database: Any) -> None:
    block_types = {
        "theory_text": ["body"],
        "summary": ["body"],
        "quiz": ["prompt", "options", "correct_option_id", "feedback"],
        "exercise_open": ["prompt", "grading"],
        "reference": ["citation", "url"],
    }
    await database["block_types"].insert_many([
        {
            "key": key,
            "label": key,
            "enabled": True,
            "fields": [{"name": field, "label": field, "type": "text"} for field in fields],
        }
        for key, fields in block_types.items()
    ])
    taxonomies = [
        ("pedagogical_type", "solo"), ("pedagogical_type", "integrado"),
        ("pedagogical_type", "pratica"), ("pedagogical_type", "revisita"),
        ("pedagogical_type", "projeto"), ("requirement", "obrigatorio"),
        ("requirement", "repertorio"), ("requirement", "opcional"),
        ("depth", "alta"), ("depth", "media"), ("depth", "repertorio"),
        ("relation_type", "prerequisite"), ("relation_type", "complement"),
        ("relation_type", "related"), ("relation_type", "revisit"),
    ]
    await database["taxonomies"].insert_many([
        {"group": group, "key": key, "label": key, "description": "taxonomy fixture Beta 4"}
        for group, key in taxonomies
    ])


def bind_application_services(database: Any) -> tuple[Any, Any]:
    """Bind only versioned Python service modules to the verified test DB."""
    os.environ["MONGO_URL"] = verified_uri()
    os.environ["DB_NAME"] = database.name
    os.environ["ENV"] = "development"
    import database as database_module
    import learning
    import services.common as common_service
    import services.imports as import_service
    import services.nodes as nodes_service

    database_module.db = database
    import_service.db = database
    common_service.db = database
    nodes_service.db = database
    learning.db = database
    return import_service, nodes_service
