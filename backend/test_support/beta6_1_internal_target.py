"""Validate a host-attested MongoDB target on a phase-owned internal Docker network.

The Docker-owning host harness must inspect the network, Mongo container, and
test-runner container before it starts pytest. This in-container check then
validates the explicit hand-off and server identity before application imports
or writes. It deliberately accepts only the per-run Mongo DNS name, never a
host address or a localhost fallback.
"""

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
    """Validate the host harness hand-off without opening a socket."""
    gate = _required(environ, "BETA6_TEST_ISOLATION_GATE")
    if not re.fullmatch(r"beta6-1:[0-9a-f]{64}", gate):
        raise MongoTargetError("Gate do ambiente interno não foi atestado pelo harness Beta 6.1")

    uri = _required(environ, "BETA6_TEST_MONGO_URI")
    database = _required(environ, "BETA6_TEST_MONGO_DATABASE")
    run_id = _required(environ, "BETA6_TEST_RUN_ID")
    owner_token = _required(environ, "BETA6_TEST_OWNER_TOKEN")
    container_id = _required(environ, "BETA6_TEST_CONTAINER_ID").lower()
    network_id = _required(environ, "BETA6_TEST_NETWORK_ID").lower()
    runner_id = _required(environ, "BETA6_TEST_RUNNER_ID").lower()
    mongo_host = _required(environ, "BETA6_TEST_MONGO_HOST")
    network_name = _required(environ, "BETA6_TEST_NETWORK_NAME")

    if not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise MongoTargetError("Identificador exclusivo da execução inválido")
    if database != f"beta6_{run_id}":
        raise MongoTargetError("Banco não corresponde à execução Beta 6.1")
    for value, label in ((container_id, "Mongo"), (network_id, "rede"), (runner_id, "runner")):
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise MongoTargetError(f"Identidade Docker do {label} não é completa")
    if len(owner_token) < 32:
        raise MongoTargetError("Marcador de propriedade do harness é insuficiente")

    expected_suffix = run_id[:12]
    if mongo_host != f"tc-beta6-1-mongo-{expected_suffix}":
        raise MongoTargetError("Host Mongo não corresponde ao recurso exclusivo da execução")
    if network_name != f"tc-beta6-1-{expected_suffix}":
        raise MongoTargetError("Rede não corresponde ao recurso exclusivo da execução")
    if _required(environ, "BETA6_TEST_RUNNER_NAME") != f"tc-beta6-1-runner-{expected_suffix}":
        raise MongoTargetError("Runner não corresponde ao recurso exclusivo da execução")

    try:
        parsed = urlsplit(uri)
        host, port = parsed.hostname, parsed.port
        username, password = unquote(parsed.username or ""), unquote(parsed.password or "")
        uri_database = unquote(parsed.path.lstrip("/"))
        query = parse_qs(parsed.query, keep_blank_values=True)
    except ValueError as exc:
        raise MongoTargetError("URI MongoDB interna Beta 6.1 malformada") from exc
    if parsed.scheme != "mongodb" or parsed.fragment or host != mongo_host or port != 27017:
        raise MongoTargetError("URI MongoDB não aponta para o serviço interno provisionado")
    if "," in parsed.netloc or uri_database != database or not username or len(password) < 40:
        raise MongoTargetError("URI MongoDB contém identidade ou credenciais incompatíveis")
    if username != f"beta6_{run_id[:10]}":
        raise MongoTargetError("Credencial Mongo não corresponde à execução Beta 6.1")
    if set(query) != {"authSource", "directConnection"} or any(len(values) != 1 for values in query.values()):
        raise MongoTargetError("URI contém opções não aprovadas ou parâmetros ambíguos")
    if query.get("authSource") != ["admin"] or query.get("directConnection", [""])[0].lower() != "true":
        raise MongoTargetError("URI exige autenticação e conexão direta explicitamente")

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
        phase="beta6",
    )


def connect_internal_verified_target(
    environ: Mapping[str, str], client_factory: Callable[[str], object],
) -> tuple[MongoTarget, object]:
    """Connect only after validating the explicit internal-network hand-off."""
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
