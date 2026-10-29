"""Guarded harness for the Beta 2 disposable MongoDB import proof."""

from __future__ import annotations

import json
import os
import re
import subprocess
from secrets import token_hex
from typing import Any

from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

PHASE = "beta2-curriculum-import-proof"
CONTAINER = "trilhacode-beta2-curriculum-mongo"
NETWORK = "trilhacode-beta2-curriculum-net"
IMAGE = "mongo:7.0.43"
IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
PORT = 27149
DB_PREFIX = "beta2_curriculum_import_"


def _docker_json(*args: str) -> Any:
    completed = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=10,
    )
    return json.loads(completed.stdout)


def verify_owned_disposable() -> None:
    containers = _docker_json("inspect", CONTAINER)
    if len(containers) != 1:
        raise RuntimeError("MongoDB descartável Beta 2 não identificado univocamente")
    container = containers[0]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != PHASE:
        raise RuntimeError("container não pertence à prova Beta 2")
    if not container["State"]["Running"] or container["Config"]["Image"] != IMAGE:
        raise RuntimeError("container não está ativo com a imagem esperada")
    if container["Image"] != IMAGE_ID:
        raise RuntimeError("imagem local não corresponde ao digest verificado")
    if container.get("Mounts"):
        raise RuntimeError("container possui volume ou bind mount inesperado")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("dados MongoDB não estão confinados a tmpfs")
    bindings = container["HostConfig"].get("PortBindings", {}).get("27017/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]:
        raise RuntimeError("porta MongoDB não está restrita à loopback esperada")
    networks = container["NetworkSettings"]["Networks"]
    if set(networks) != {NETWORK}:
        raise RuntimeError("container está conectado a rede não exclusiva")
    network = _docker_json("network", "inspect", NETWORK)[0]
    if (network["Labels"].get("io.trilhacode.phase") != PHASE
            or network["Driver"] != "bridge" or network["Internal"]
            or network["Options"].get("com.docker.network.bridge.enable_ip_masquerade") != "false"
            or set(network["Containers"]) != {container["Id"]}):
        raise RuntimeError("rede não corresponde ao isolamento esperado")


def verified_uri() -> str:
    uri = os.environ.get("TRILHACODE_BETA2_MONGO_URI", "")
    if not uri or "@" in uri or uri.lower().startswith("mongodb+srv://"):
        raise RuntimeError("URI local e sem credenciais é obrigatória")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", PORT)]:
        raise RuntimeError("URI deve apontar somente para a porta loopback da Beta 2")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("credenciais não são aceitas pelo harness")
    if parsed["options"].get("replicaSet") != "rsBeta2":
        raise RuntimeError("replica set Beta 2 esperado")
    if parsed["database"] not in (None, ""):
        raise RuntimeError("URI não pode selecionar banco preexistente")
    if not re.fullmatch(r"mongodb://127\.0\.0\.1:27149/\?replicaSet=rsBeta2&directConnection=true", uri):
        raise RuntimeError("formato da URI não permitido")
    return uri


async def open_owned_database() -> tuple[AsyncMongoClient, Any, str]:
    verify_owned_disposable()
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(
        verified_uri(), timeoutMS=8_000, tz_aware=True,
    )
    database_name = DB_PREFIX + token_hex(8)
    database = client[database_name]
    hello = await client.admin.command("hello")
    build = await client.admin.command("buildInfo")
    status = await client.admin.command("serverStatus")
    replica = await client.admin.command("replSetGetStatus")
    if build.get("version") != "7.0.43":
        await client.close()
        raise RuntimeError("versão de MongoDB diferente da versão aprovada")
    if hello.get("setName") != "rsBeta2" or not hello.get("isWritablePrimary"):
        await client.close()
        raise RuntimeError("replica set não está pronto como primary")
    if hello.get("logicalSessionTimeoutMinutes") is None:
        await client.close()
        raise RuntimeError("sessões MongoDB não disponíveis")
    if status["storageEngine"]["name"] != "wiredTiger":
        await client.close()
        raise RuntimeError("WiredTiger é obrigatório")
    members = replica.get("members", [])
    if len(members) != 1 or members[0].get("stateStr") != "PRIMARY":
        await client.close()
        raise RuntimeError("replica set não é exclusivo de nó único")
    run_id = database_name.removeprefix(DB_PREFIX)
    await database["_beta2_identity"].insert_one({
        "_id": "owner", "phase": PHASE, "run_id": run_id,
    })
    return client, database, run_id


async def drop_owned_database(client: AsyncMongoClient, database: Any, run_id: str) -> None:
    marker = await database["_beta2_identity"].find_one({"_id": "owner"})
    expected = {"_id": "owner", "phase": PHASE, "run_id": run_id}
    if marker != expected:
        await client.close()
        raise RuntimeError("marcador C2 divergiu; banco preservado para inspeção")
    await client.drop_database(database.name)
    await client.close()


def block_type_documents() -> list[dict[str, Any]]:
    """Synthetic copies of the active seed metadata needed by this payload."""
    schemas = {
        "theory_text": ["body"],
        "summary": ["body"],
        "quiz": ["question", "options", "correct_index", "explanation"],
        "exercise_open": [
            "prompt", "rubric", "grading", "criteria", "allow_resubmit", "max_score",
        ],
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
    """Synthetic copies of the active seed taxonomy rows referenced by unit 1.1."""
    return [
        {
            "group": "pedagogical_type", "key": "integrado", "label": "Tema integrado",
            "description": "Conecta vários assuntos em um contexto", "color": "violet", "order": 1,
        },
        {
            "group": "requirement", "key": "obrigatorio", "label": "Obrigatório",
            "description": "Parte essencial da trilha", "color": "emerald", "order": 5,
        },
        {
            "group": "depth", "key": "media", "label": "Profundidade média",
            "description": "Entendimento funcional", "color": "amber", "order": 9,
        },
    ]
