"""Ownership-checked access to the Beta 3 disposable MongoDB only."""

from __future__ import annotations

import json
import os
import subprocess
from secrets import token_hex
from typing import Any

from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

PHASE = "beta3-curriculum-fidelity"
CONTAINER = "trilhacode-beta3-curriculum-mongo"
NETWORK = "trilhacode-beta3-curriculum-net"
IMAGE = "mongo:7.0.43"
IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
PORT = 27150
DB_PREFIX = "beta3_curriculum_fidelity_"


def _docker_json(*args: str) -> Any:
    completed = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=10,
    )
    return json.loads(completed.stdout)


def verify_owned_disposable() -> None:
    rows = _docker_json("inspect", CONTAINER)
    if len(rows) != 1:
        raise RuntimeError("MongoDB descartável Beta 3 não identificado univocamente")
    container = rows[0]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != PHASE:
        raise RuntimeError("container não pertence à Beta 3")
    if not container["State"]["Running"] or container["Config"]["Image"] != IMAGE:
        raise RuntimeError("container Beta 3 não está ativo com a imagem esperada")
    if container["Image"] != IMAGE_ID:
        raise RuntimeError("digest local MongoDB não corresponde ao verificado")
    if container.get("Mounts"):
        raise RuntimeError("container Beta 3 possui volume/bind mount inesperado")
    if not {"/data/db", "/data/configdb"}.issubset(container["HostConfig"].get("Tmpfs", {})):
        raise RuntimeError("armazenamento MongoDB não está confinado a tmpfs")
    bindings = container["HostConfig"].get("PortBindings", {}).get("27017/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]:
        raise RuntimeError("MongoDB não está publicado exclusivamente na loopback Beta 3")
    if container["HostConfig"].get("NetworkMode") != NETWORK:
        raise RuntimeError("container está conectado fora da rede dedicada Beta 3")
    if set(container["NetworkSettings"]["Networks"]) != {NETWORK}:
        raise RuntimeError("container possui rede adicional")

    networks = _docker_json("network", "inspect", NETWORK)
    if len(networks) != 1:
        raise RuntimeError("rede Beta 3 não identificada univocamente")
    network = networks[0]
    if (network["Labels"].get("io.trilhacode.phase") != PHASE
            or network["Driver"] != "bridge" or network["Internal"] is not False
            or network["Options"].get("com.docker.network.bridge.enable_ip_masquerade") != "false"
            or set(network["Containers"]) != {container["Id"]}):
        raise RuntimeError("rede não corresponde ao bridge sem egress exclusivo Beta 3")


def verified_uri() -> str:
    uri = os.environ.get("TRILHACODE_BETA3_MONGO_URI", "")
    if uri != f"mongodb://127.0.0.1:{PORT}":
        raise RuntimeError("URI deve apontar exatamente para o MongoDB loopback Beta 3")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", PORT)]:
        raise RuntimeError("host/porta MongoDB divergente da Beta 3")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("credenciais não são aceitas pelo harness Beta 3")
    if parsed["database"] not in (None, "") or parsed["options"]:
        raise RuntimeError("URI Beta 3 não pode selecionar banco ou opções extras")
    return uri


async def open_owned_database() -> tuple[AsyncMongoClient[dict[str, Any]], Any, str]:
    verify_owned_disposable()
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(
        verified_uri(), timeoutMS=8_000, tz_aware=True,
    )
    database_name = DB_PREFIX + token_hex(8)
    database = client[database_name]
    try:
        hello = await client.admin.command("hello")
        build = await client.admin.command("buildInfo")
        status = await client.admin.command("serverStatus")
        if build.get("version") != "7.0.43":
            raise RuntimeError("versão MongoDB diferente de 7.0.43")
        if hello.get("setName") is not None or not hello.get("isWritablePrimary"):
            raise RuntimeError("esperado MongoDB standalone gravável, sem replica set")
        if status["storageEngine"]["name"] != "wiredTiger":
            raise RuntimeError("WiredTiger é obrigatório")
        run_id = database_name.removeprefix(DB_PREFIX)
        await database["_beta3_identity"].insert_one({
            "_id": "owner", "phase": PHASE, "run_id": run_id,
        })
        return client, database, run_id
    except BaseException:
        await client.close()
        raise


async def drop_owned_database(
    client: AsyncMongoClient[dict[str, Any]], database: Any, run_id: str,
) -> None:
    verify_owned_disposable()
    marker = await database["_beta3_identity"].find_one({"_id": "owner"})
    if marker != {"_id": "owner", "phase": PHASE, "run_id": run_id}:
        await client.close()
        raise RuntimeError("marcador de propriedade Beta 3 divergiu; banco preservado")
    if not database.name.startswith(DB_PREFIX):
        await client.close()
        raise RuntimeError("nome do banco fora do prefixo exclusivo Beta 3")
    await client.drop_database(database.name)
    await client.close()


def block_type_documents() -> list[dict[str, Any]]:
    schemas = {
        "theory_text": ["body"],
        "summary": ["body"],
        "quiz": ["question", "options", "correct_index", "explanation"],
        "exercise_open": ["prompt", "rubric", "grading", "criteria", "allow_resubmit", "max_score"],
        "reference": ["citation", "url"],
    }
    return [
        {
            "key": key,
            "label": key,
            "enabled": True,
            "fields": [{"name": name, "label": name, "type": "text"} for name in fields],
        }
        for key, fields in schemas.items()
    ]


def taxonomy_documents() -> list[dict[str, Any]]:
    return [
        {"group": "pedagogical_type", "key": "integrado", "label": "Tema integrado",
         "description": "Taxonomia sintética", "color": "violet", "order": 1},
        {"group": "requirement", "key": "obrigatorio", "label": "Obrigatório",
         "description": "Taxonomia sintética", "color": "emerald", "order": 1},
        {"group": "depth", "key": "media", "label": "Profundidade média",
         "description": "Taxonomia sintética", "color": "amber", "order": 1},
    ]
