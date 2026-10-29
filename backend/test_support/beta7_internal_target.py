"""Validate a host-attested Beta 7 Mongo target on an internal Docker network."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from urllib.parse import parse_qs, unquote, urlsplit

from test_support.beta5_mongo_target import (
    MongoTarget,
    MongoTargetError,
    verify_server_and_claim_database,
)


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise MongoTargetError(f"Configuração obrigatória ausente: {name}")
    return value


def validate_internal_target(environ: Mapping[str, str]) -> MongoTarget:
    gate = _required(environ, "BETA7_TEST_ISOLATION_GATE")
    if not re.fullmatch(r"beta7:[0-9a-f]{64}", gate):
        raise MongoTargetError("Gate interno não foi atestado pelo harness Beta 7")

    uri = _required(environ, "BETA7_TEST_MONGO_URI")
    database = _required(environ, "BETA7_TEST_MONGO_DATABASE")
    run_id = _required(environ, "BETA7_TEST_RUN_ID")
    owner_token = _required(environ, "BETA7_TEST_OWNER_TOKEN")
    container_id = _required(environ, "BETA7_TEST_CONTAINER_ID").lower()
    network_id = _required(environ, "BETA7_TEST_NETWORK_ID").lower()
    runner_id = _required(environ, "BETA7_TEST_RUNNER_ID").lower()
    mongo_host = _required(environ, "BETA7_TEST_MONGO_HOST")
    network_name = _required(environ, "BETA7_TEST_NETWORK_NAME")
    runner_name = _required(environ, "BETA7_TEST_RUNNER_NAME")

    if not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise MongoTargetError("Identificador exclusivo Beta 7 inválido")
    if database != f"beta7_{run_id}" or owner_token == run_id or len(owner_token) < 48:
        raise MongoTargetError("Identidade do banco ou propriedade Beta 7 incompatível")
    if any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in (container_id, network_id, runner_id)):
        raise MongoTargetError("IDs Docker completos são obrigatórios no gate Beta 7")
    suffix = run_id[:12]
    expected_names = (
        (mongo_host, f"tc-beta7-mongo-{suffix}"),
        (network_name, f"tc-beta7-{suffix}"),
        (runner_name, f"tc-beta7-runner-{suffix}"),
    )
    if any(value != expected for value, expected in expected_names):
        raise MongoTargetError("Nomes Docker não correspondem à execução Beta 7")

    try:
        parsed = urlsplit(uri)
        host, port = parsed.hostname, parsed.port
        username, password = unquote(parsed.username or ""), unquote(parsed.password or "")
        uri_database = unquote(parsed.path.lstrip("/"))
        query = parse_qs(parsed.query, keep_blank_values=True)
    except ValueError as exc:
        raise MongoTargetError("URI MongoDB Beta 7 malformada") from exc
    if parsed.scheme != "mongodb" or parsed.fragment or host != mongo_host or port != 27017:
        raise MongoTargetError("URI não aponta exclusivamente ao container Mongo Beta 7")
    if "," in parsed.netloc or uri_database != database or not username or len(password) < 40:
        raise MongoTargetError("Banco ou credenciais da URI incompatíveis")
    if username != f"beta7_{run_id[:10]}":
        raise MongoTargetError("Credencial não pertence à execução Beta 7")
    if set(query) != {"authSource", "directConnection"} or any(len(v) != 1 for v in query.values()):
        raise MongoTargetError("URI contém opções MongoDB não autorizadas")
    if query["authSource"] != ["admin"] or query["directConnection"][0].lower() != "true":
        raise MongoTargetError("URI precisa exigir authSource admin e conexão direta")

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
        phase="beta7",
    )


def connect_internal_verified_target(
    environ: Mapping[str, str], client_factory: Callable[[str], object],
) -> tuple[MongoTarget, object]:
    target = validate_internal_target(environ)
    client = client_factory(target.uri)
    try:
        verify_server_and_claim_database(client, target)
    except Exception:
        close = getattr(client, "close", None)
        if close is not None:
            close()
        raise
    return target, client
