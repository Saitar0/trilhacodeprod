"""Fail-closed MongoDB identity gate for the Beta 7.1 disposable runner."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from urllib.parse import parse_qs, unquote, urlsplit

from test_support.beta5_mongo_target import MongoTarget, MongoTargetError


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise MongoTargetError(f"Configuração obrigatória ausente: {name}")
    return value


def validate_internal_target(environ: Mapping[str, str]) -> MongoTarget:
    gate = _required(environ, "BETA7_1_TEST_ISOLATION_GATE")
    if not re.fullmatch(r"beta7-1:[0-9a-f]{64}", gate):
        raise MongoTargetError("Gate interno Beta 7.1 não foi atestado pelo harness")

    uri = _required(environ, "BETA7_1_TEST_MONGO_URI")
    database = _required(environ, "BETA7_1_TEST_MONGO_DATABASE")
    run_id = _required(environ, "BETA7_1_TEST_RUN_ID")
    owner_token = _required(environ, "BETA7_1_TEST_OWNER_TOKEN")
    container_id = _required(environ, "BETA7_1_TEST_CONTAINER_ID").lower()
    network_id = _required(environ, "BETA7_1_TEST_NETWORK_ID").lower()
    runner_id = _required(environ, "BETA7_1_TEST_RUNNER_ID").lower()
    mongo_host = _required(environ, "BETA7_1_TEST_MONGO_HOST")
    network_name = _required(environ, "BETA7_1_TEST_NETWORK_NAME")
    runner_name = _required(environ, "BETA7_1_TEST_RUNNER_NAME")

    if not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise MongoTargetError("Identificador exclusivo Beta 7.1 inválido")
    if database != f"beta7_1_{run_id}" or len(owner_token) < 48:
        raise MongoTargetError("Banco ou marcador de propriedade Beta 7.1 incompatível")
    if any(not re.fullmatch(r"[0-9a-f]{64}", value)
           for value in (container_id, network_id, runner_id)):
        raise MongoTargetError("IDs Docker completos são obrigatórios no gate Beta 7.1")
    expected_names = (
        (mongo_host, f"tc-beta7-1-mongo-{run_id[:12]}"),
        (network_name, f"tc-beta7-1-{run_id[:12]}"),
        (runner_name, f"tc-beta7-1-runner-{run_id[:12]}"),
    )
    if any(value != expected for value, expected in expected_names):
        raise MongoTargetError("Nomes Docker não correspondem à execução Beta 7.1")

    try:
        parsed = urlsplit(uri)
        host, port = parsed.hostname, parsed.port
        username, password = unquote(parsed.username or ""), unquote(parsed.password or "")
        uri_database = unquote(parsed.path.lstrip("/"))
        query = parse_qs(parsed.query, keep_blank_values=True)
    except ValueError as exc:
        raise MongoTargetError("URI MongoDB Beta 7.1 malformada") from exc
    if (parsed.scheme != "mongodb" or parsed.fragment or host != mongo_host or port != 27017
            or "," in parsed.netloc or uri_database != database):
        raise MongoTargetError("URI não aponta exclusivamente ao MongoDB Beta 7.1")
    if username != f"beta7_1_{run_id[:10]}" or len(password) < 40:
        raise MongoTargetError("Credenciais não pertencem a esta execução Beta 7.1")
    if set(query) != {"authSource", "replicaSet"} or any(len(row) != 1 for row in query.values()):
        raise MongoTargetError("URI contém opções MongoDB não autorizadas")
    if query["authSource"] != ["admin"] or query["replicaSet"] != ["rs0"]:
        raise MongoTargetError("URI requer autenticação explícita no replica set Beta 7.1")

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
        phase="beta7-1",
    )


def verify_beta7_1_server_and_claim(client, target: MongoTarget) -> None:
    """Verify MongoDB 7/WiredTiger/rs0 before claiming the execution database."""
    try:
        hello = client.admin.command("hello")
        build = client.admin.command("buildInfo")
        storage = client.admin.command("serverStatus").get("storageEngine", {}).get("name")
        names = set(client.list_database_names())
    except Exception as exc:
        raise MongoTargetError("Não foi possível verificar o MongoDB Beta 7.1") from exc
    if str(build.get("version", "")).split(".", 1)[0] != "7":
        raise MongoTargetError("O servidor Beta 7.1 não é MongoDB 7")
    if storage != "wiredTiger":
        raise MongoTargetError("O servidor Beta 7.1 não utiliza WiredTiger")
    if hello.get("setName") != "rs0" or hello.get("isWritablePrimary") is not True:
        raise MongoTargetError("O MongoDB Beta 7.1 não está no primário do replica set exclusivo")
    expected_member = f"{urlsplit(target.uri).hostname}:27017"
    if set(hello.get("hosts", [])) != {expected_member} or hello.get("primary") != expected_member:
        raise MongoTargetError("Replica set Beta 7.1 anuncia membros além do container exclusivo")

    database = client[target.database]
    owner = database["_beta7-1_test_owner"]
    expected = {
        "_id": "owner",
        "run_id": target.run_id,
        "owner_token": target.owner_token,
        "container_id": target.container_id,
        "network_id": target.network_id,
        "database": target.database,
    }
    existing = owner.find_one({"_id": "owner"})
    if existing is None:
        if target.database in names:
            raise MongoTargetError("Banco já existe sem prova de propriedade Beta 7.1")
        owner.insert_one(expected)
        existing = owner.find_one({"_id": "owner"})
    if not existing or any(existing.get(key) != value for key, value in expected.items()):
        raise MongoTargetError("Marcador de propriedade Beta 7.1 divergente")


def connect_internal_verified_target(
    environ: Mapping[str, str], client_factory: Callable[[str], object],
) -> tuple[MongoTarget, object]:
    target = validate_internal_target(environ)
    client = client_factory(target.uri)
    try:
        verify_beta7_1_server_and_claim(client, target)
    except Exception:
        close = getattr(client, "close", None)
        if close is not None:
            close()
        raise
    return target, client
