"""Fail-closed identity checks for the Beta 5 disposable MongoDB harness.

This module performs no network or database activity at import time. A target
is accepted only after its URI, unique run identity, Docker container, isolated
network, loopback port binding, credentials, and ephemeral storage agree.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, unquote, urlsplit


class MongoTargetError(RuntimeError):
    """Raised when a test database cannot be proven to belong to this run."""


@dataclass(frozen=True)
class MongoTarget:
    uri: str
    database: str
    run_id: str
    owner_token: str
    container_id: str
    network_id: str
    username: str
    password: str
    host_port: int


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise MongoTargetError(f"Configuração obrigatória ausente: {name}")
    return value


def require_explicit_opt_in(enabled: bool) -> None:
    """Require a deliberate test-run switch before selecting persistent tests."""
    if not enabled:
        raise MongoTargetError("Testes persistentes exigem opt-in explícito de isolamento Beta 5")


def _docker_json(command: list[str]) -> Any:
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=10)
        return json.loads(completed.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        # Do not include process output: docker inspect contains credentials.
        raise MongoTargetError("Não foi possível verificar a identidade do recurso Docker Beta 5") from exc


def inspect_container(container_id: str) -> Mapping[str, Any]:
    rows = _docker_json(["docker", "inspect", container_id])
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise MongoTargetError("Identidade do container Mongo Beta 5 inválida")
    return rows[0]


def inspect_network(network_id: str) -> Mapping[str, Any]:
    rows = _docker_json(["docker", "network", "inspect", network_id])
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise MongoTargetError("Identidade da rede Mongo Beta 5 inválida")
    return rows[0]


def validate_target(
    environ: Mapping[str, str],
    *,
    container_inspector: Callable[[str], Mapping[str, Any]] = inspect_container,
    network_inspector: Callable[[str], Mapping[str, Any]] = inspect_network,
) -> MongoTarget:
    """Validate all out-of-band isolation evidence without opening a socket."""
    uri = _required(environ, "BETA5_TEST_MONGO_URI")
    database = _required(environ, "BETA5_TEST_MONGO_DATABASE")
    run_id = _required(environ, "BETA5_TEST_RUN_ID")
    owner_token = _required(environ, "BETA5_TEST_OWNER_TOKEN")
    container_id = _required(environ, "BETA5_TEST_CONTAINER_ID").lower()
    network_id = _required(environ, "BETA5_TEST_NETWORK_ID").lower()

    if not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise MongoTargetError("Identificador exclusivo da execução inválido")
    if not re.fullmatch(rf"beta5_{run_id}", database):
        raise MongoTargetError("Banco não corresponde ao identificador exclusivo da execução")
    if not re.fullmatch(r"[0-9a-f]{64}", container_id):
        raise MongoTargetError("ID do container não é uma identidade Docker completa")
    if not re.fullmatch(r"[0-9a-f]{64}", network_id):
        raise MongoTargetError("ID da rede não é uma identidade Docker completa")
    if len(owner_token) < 32:
        raise MongoTargetError("Marcador de propriedade do harness é insuficiente")

    try:
        parsed = urlsplit(uri)
        host = parsed.hostname
        port = parsed.port
        username = unquote(parsed.username or "")
        password = unquote(parsed.password or "")
        uri_database = unquote(parsed.path.lstrip("/"))
        query = parse_qs(parsed.query, keep_blank_values=True)
    except ValueError as exc:
        raise MongoTargetError("URI MongoDB Beta 5 malformada") from exc
    if parsed.scheme != "mongodb" or parsed.fragment or not host or not port:
        raise MongoTargetError("URI MongoDB Beta 5 inválida ou ambígua")
    if host != "127.0.0.1" or port == 27017 or "," in parsed.netloc:
        raise MongoTargetError("URI não aponta para a porta loopback exclusiva Beta 5")
    if uri_database != database or not username or not password:
        raise MongoTargetError("URI não identifica o banco e as credenciais exclusivos Beta 5")
    if username != f"beta5_{run_id[:10]}" or len(password) < 40:
        raise MongoTargetError("Credenciais não correspondem ao padrão exclusivo desta execução")
    if set(query) != {"authSource", "directConnection"} or any(len(values) != 1 for values in query.values()):
        raise MongoTargetError("URI contém opções não aprovadas ou parâmetros ambíguos")
    if query.get("directConnection", [""])[-1].lower() != "true":
        raise MongoTargetError("URI deve desabilitar descoberta/redirecionamento de topologia")
    if query.get("authSource", [""])[-1] != "admin":
        raise MongoTargetError("URI deve autenticar explicitamente no banco admin do container descartável")

    container = container_inspector(container_id)
    network = network_inspector(network_id)
    labels = (container.get("Config") or {}).get("Labels") or {}
    network_labels = network.get("Labels") or {}
    if container.get("Id", "").lower() != container_id or network.get("Id", "").lower() != network_id:
        raise MongoTargetError("Recurso Docker não corresponde ao ID provisionado")
    expected_labels = {
        "io.trilhacode.phase": "beta5",
        "io.trilhacode.run-id": run_id,
        "io.trilhacode.owner-token": owner_token,
    }
    if any(labels.get(key) != value for key, value in expected_labels.items()):
        raise MongoTargetError("Container sem marcador de propriedade Beta 5 correspondente")
    if any(network_labels.get(key) != value for key, value in expected_labels.items()):
        raise MongoTargetError("Rede sem marcador de propriedade Beta 5 correspondente")
    if container.get("Config", {}).get("Image") != "mongo:7.0.43":
        raise MongoTargetError("Imagem do MongoDB não corresponde à versão descartável aprovada")
    if not (container.get("State") or {}).get("Running"):
        raise MongoTargetError("Container MongoDB Beta 5 não está em execução")
    if network.get("Driver") != "bridge" or network.get("Name") != f"tc-beta5-{run_id[:12]}":
        raise MongoTargetError("Rede do MongoDB Beta 5 não é uma bridge exclusiva da execução")

    configured_env = set((container.get("Config") or {}).get("Env") or [])
    if f"MONGO_INITDB_ROOT_USERNAME={username}" not in configured_env or \
            f"MONGO_INITDB_ROOT_PASSWORD={password}" not in configured_env:
        raise MongoTargetError("Credenciais da URI não correspondem às credenciais provisionadas")

    requested_bindings = ((container.get("HostConfig") or {}).get("PortBindings") or {}).get("27017/tcp") or []
    published_bindings = ((container.get("NetworkSettings") or {}).get("Ports") or {}).get("27017/tcp") or []
    matching_request = any(
        binding.get("HostIp") == "127.0.0.1" and binding.get("HostPort") in {"", str(port)}
        for binding in requested_bindings
    )
    matching_publication = any(
        binding.get("HostIp") == "127.0.0.1" and binding.get("HostPort") == str(port)
        for binding in published_bindings
    )
    if not matching_request or not matching_publication:
        raise MongoTargetError("Porta da URI não corresponde ao binding loopback provisionado")
    mounts = container.get("Mounts") or []
    tmpfs = (container.get("HostConfig") or {}).get("Tmpfs") or {}
    if mounts or set(tmpfs) != {"/data/db", "/data/configdb"}:
        raise MongoTargetError(
            "Armazenamento do MongoDB não é exclusivamente temporário "
            f"(mounts={len(mounts)}, tmpfs={sorted(tmpfs)!r})"
        )
    network_name = network.get("Name")
    attached = set(((container.get("NetworkSettings") or {}).get("Networks") or {}).keys())
    if not network_name or attached != {network_name}:
        raise MongoTargetError("Container não está isolado exclusivamente na rede Beta 5")
    attached_containers = set(((network.get("Containers") or {}).keys()))
    if attached_containers != {container_id}:
        raise MongoTargetError("A rede contém recursos além do container desta execução")

    return MongoTarget(
        uri=uri,
        database=database,
        run_id=run_id,
        owner_token=owner_token,
        container_id=container_id,
        network_id=network_id,
        username=username,
        password=password,
        host_port=port,
    )


def verify_server_and_claim_database(client: Any, target: MongoTarget) -> None:
    """Prove MongoDB 7/WiredTiger and claim only a new or already-owned DB."""
    try:
        hello = client.admin.command("hello")
        build = client.admin.command("buildInfo")
        status = client.admin.command("serverStatus")
        names = set(client.list_database_names())
    except Exception as exc:  # driver errors must fail closed and avoid leaking URI
        raise MongoTargetError("Não foi possível verificar o servidor MongoDB provisionado") from exc
    if str(build.get("version", "")).split(".", 1)[0] != "7":
        raise MongoTargetError("Servidor de teste não é MongoDB 7")
    if (status.get("storageEngine") or {}).get("name") != "wiredTiger":
        raise MongoTargetError("Servidor de teste não utiliza WiredTiger")
    if hello.get("msg") == "isdbgrid" or hello.get("setName"):
        raise MongoTargetError("Topologia do servidor difere do container standalone Beta 5")

    database = client[target.database]
    owner_collection = database["_beta5_test_owner"]
    expected = {
        "_id": "owner",
        "run_id": target.run_id,
        "owner_token": target.owner_token,
        "container_id": target.container_id,
        "network_id": target.network_id,
        "database": target.database,
    }
    existing = owner_collection.find_one({"_id": "owner"})
    if existing is None:
        if target.database in names:
            raise MongoTargetError("Banco já existente sem prova de propriedade desta execução")
        owner_collection.insert_one(expected)
        existing = owner_collection.find_one({"_id": "owner"})
    if not existing or any(existing.get(key) != value for key, value in expected.items()):
        raise MongoTargetError("Marcador de propriedade do banco divergente")


def connect_verified_target(
    environ: Mapping[str, str],
    client_factory: Callable[[str], Any],
    *,
    container_inspector: Callable[[str], Mapping[str, Any]] = inspect_container,
    network_inspector: Callable[[str], Mapping[str, Any]] = inspect_network,
) -> tuple[MongoTarget, Any]:
    """Create a client only after all non-network Docker/URI checks pass."""
    target = validate_target(
        environ,
        container_inspector=container_inspector,
        network_inspector=network_inspector,
    )
    client = client_factory(target.uri)
    try:
        verify_server_and_claim_database(client, target)
    except Exception:
        close = getattr(client, "close", None)
        if close is not None:
            close()
        raise
    return target, client


def assert_database_owned(client: Any, target: MongoTarget) -> None:
    """Recheck the owner marker before cleanup or another destructive action."""
    expected = {
        "run_id": target.run_id,
        "owner_token": target.owner_token,
        "container_id": target.container_id,
        "network_id": target.network_id,
        "database": target.database,
    }
    marker = client[target.database]["_beta5_test_owner"].find_one({"_id": "owner"})
    if not marker or any(marker.get(key) != value for key, value in expected.items()):
        raise MongoTargetError("Recusando operação: propriedade do banco não comprovada")
