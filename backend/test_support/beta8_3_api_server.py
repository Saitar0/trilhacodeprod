"""Explicitly composed API process for the Beta 8.3 disposable harness only."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from types import SimpleNamespace
from urllib.parse import urlsplit

from pymongo.uri_parser import parse_uri


def _preflight() -> tuple[str, bytes, bytes, str]:
    if os.environ.get("BETA8_3_TEST_API") != "1" or os.environ.get("BETA8_3_DISPOSABLE") != "1":
        raise RuntimeError("composição de API Beta 8.3 exige harness descartável explícito")
    if any(name in os.environ for name in (
        "BETA8_3_AUTHORITY_MONGO_URI", "BETA8_3_AUTHORITY_MONGO_PASSWORD",
        "EDITORIAL_MONGO_URI", "EDITORIAL_MONGO_PASSWORD",
        "BETA8_3_ROOT_URI", "BETA8_3_ROOT_PASSWORD",
        "BETA8_3_STAGE_READ_URI", "BETA8_3_STAGE_READ_PASSWORD",
        "BETA8_3_STAGE_WRITE_URI", "BETA8_3_STAGE_WRITE_PASSWORD",
        "BETA8_3_STAGER_SECRET_HEX",
    )):
        raise RuntimeError("processo API não pode receber credencial editorial")
    mongo_uri = os.environ.get("MONGO_URL", "")
    parsed = urlsplit(mongo_uri)
    try:
        options = parse_uri(mongo_uri).get("options", {})
    except Exception as exc:
        raise RuntimeError("API Beta 8.3 recusou URI Mongo inválida") from exc
    database = os.environ.get("DB_NAME", "")
    if (
        parsed.scheme != "mongodb"
        or parsed.hostname != "mongo"
        or parsed.port != 27017
        or parsed.username != "beta8-3-api"
        or not parsed.password
        or parsed.path.removeprefix("/") != database
        or options.get("replicaSet") != "rsB83"
        or options.get("authSource") != database
        or not database.startswith("editorial_revision_test_c10_c11_c12_b83_")
        or not os.environ.get("JWT_SECRET")
    ):
        raise RuntimeError("API Beta 8.3 sem URI explicitamente restrita ao Mongo descartável")
    try:
        service_secret = bytes.fromhex(os.environ["BETA8_3_SERVICE_SECRET_HEX"])
        operation_key = bytes.fromhex(os.environ["BETA8_3_OPERATION_KEY_HEX"])
    except (KeyError, ValueError) as exc:
        raise RuntimeError("segredos efêmeros da API Beta 8.3 ausentes") from exc
    if min(len(service_secret), len(operation_key)) < 32:
        raise RuntimeError("segredo efêmero Beta 8.3 insuficiente")
    authority_url = os.environ.get("BETA8_3_AUTHORITY_URL", "")
    authority = urlsplit(authority_url)
    if (
        authority.scheme != "http" or authority.hostname != "authority" or authority.port != 8101
        or authority.username or authority.password or authority.path or authority.query or authority.fragment
    ):
        raise RuntimeError("destino da autoridade Beta 8.3 fora da rede interna autorizada")
    return authority_url, service_secret, operation_key, database


_authority_url, _service_secret, _operation_key, _database_name = _preflight()

# Importing the real app only after the fail-closed gate prevents the normal
# settings fallback from opening a localhost or caller-configured connection.
import httpx  # noqa: E402

from server import app  # noqa: E402
from services.beta8_3_editorial_rpc import Beta8_3EditorialBoundaryFactory  # noqa: E402

_rpc_client = httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=1.0))
app.state.beta8_1_editorial_runtime = SimpleNamespace(
    boundary=Beta8_3EditorialBoundaryFactory(
        client=_rpc_client,
        base_url=_authority_url,
        service_secret=_service_secret,
    ),
    iam_bridge=None,
    operation_hmac_key=_operation_key,
    content_hmac_key=_operation_key,
    remote_authority=True,
)


_application_lifespan = app.router.lifespan_context


@asynccontextmanager
async def _api_lifespan(application):
    async with _application_lifespan(application):
        try:
            yield
        finally:
            await _rpc_client.aclose()


app.router.lifespan_context = _api_lifespan
