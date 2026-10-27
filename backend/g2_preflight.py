"""Fail-closed G2 entry point: validate the target before creating a Mongo client."""

from __future__ import annotations

import asyncio
import ipaddress
import json
import os
import re
import sys
from urllib.parse import urlsplit

from pymongo.errors import (  # type: ignore[attr-defined]
    ConfigurationError,
    ConnectionFailure,
    ExecutionTimeout,
    OperationFailure,
    ServerSelectionTimeoutError,
)
from pymongo.uri_parser import parse_uri

SCHEMA_VERSION = 1
EXIT_CODES = {
    "URI_INVALID": 40,
    "DB_AUTH": 41,
    "DB_CONNECTION": 42,
    "PREFLIGHT_REJECTED": 43,
    "PREFLIGHT_EXECUTION": 44,
    "PROTOCOL_INVALID": 45,
    "DB_TIMEOUT": 46,
}


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n")
    sys.stdout.flush()


def validate_target(environ: dict[str, str]) -> str:
    """Validate URI and trusted endpoint identity without logging URI material."""
    uri = environ.get("MONGO_URL", "")
    expected_host = environ.get("G2_MONGO_EXPECTED_HOST", "").lower()
    expected_port = environ.get("G2_MONGO_EXPECTED_PORT", "")
    if environ.get("ENV") != "staging" or environ.get("DB_NAME") != "trilhacode_staging":
        raise ValueError("URI_INVALID")
    host_labels = expected_host.split(".")
    if (not expected_host or expected_host in {"localhost", "host.docker.internal"} or len(expected_host) > 253
            or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                   for label in host_labels)
            or expected_port != "27017" or not uri):
        raise ValueError("URI_INVALID")
    try:
        ipaddress.ip_address(expected_host)
    except ValueError:
        pass
    else:
        raise ValueError("URI_INVALID")
    try:
        parts = urlsplit(uri)
        if parts.scheme != "mongodb" or parts.fragment or parts.port != int(expected_port):
            raise ValueError("URI_INVALID")
        parsed = parse_uri(uri, validate=True)
    except (ConfigurationError, ValueError, TypeError):
        raise ValueError("URI_INVALID") from None

    nodes = parsed.get("nodelist") or []
    if len(nodes) != 1:
        raise ValueError("URI_INVALID")
    actual_host, actual_port = nodes[0]
    if actual_host.lower() != expected_host or actual_port != int(expected_port):
        raise ValueError("URI_INVALID")
    if parsed.get("database") != "trilhacode_staging":
        raise ValueError("URI_INVALID")
    if not parsed.get("username") or not parsed.get("password"):
        raise ValueError("URI_INVALID")

    options = {key.lower(): value for key, value in (parsed.get("options") or {}).items()}
    # The endpoint is a single Docker service. Permit only authentication
    # source and explicit direct connection; reject topology discovery options.
    if set(options) - {"authsource", "directconnection"}:
        raise ValueError("URI_INVALID")
    # A replica-set URI without directConnection=true can discover members
    # advertised by MongoDB and leave the verified Docker endpoint.
    if options.get("directconnection") is not True:
        raise ValueError("URI_INVALID")
    if options.get("authsource") not in (None, "trilhacode_staging", "admin"):
        raise ValueError("URI_INVALID")
    return expected_host


def classify_database_error(exc: Exception) -> str:
    """Map driver failures to fixed categories without exposing exception text."""
    if isinstance(exc, (ExecutionTimeout, ServerSelectionTimeoutError)):
        return "DB_TIMEOUT"
    if isinstance(exc, ConnectionFailure):
        return "DB_CONNECTION"
    if isinstance(exc, OperationFailure) and getattr(exc, "code", None) in {13, 18}:
        return "DB_AUTH"
    return "PREFLIGHT_EXECUTION"


async def run() -> int:
    try:
        validate_target(dict(os.environ))
    except ValueError:
        _emit({"schema_version": SCHEMA_VERSION, "result": "ERROR", "category": "URI_INVALID"})
        return EXIT_CODES["URI_INVALID"]

    # Import only after target validation: these modules construct Mongo clients.
    from database import client, db
    from indexes import preflight_index_checks

    checks = None
    category = None
    try:
        checks = await preflight_index_checks(db)
    except Exception as exc:
        # Do not expose the driver message, which can contain URI or query data.
        category = classify_database_error(exc)
    finally:
        try:
            await client.close()
        except Exception:
            category = category or "PREFLIGHT_EXECUTION"

    if category:
        _emit({"schema_version": SCHEMA_VERSION, "result": "ERROR", "category": category})
        return EXIT_CODES[category]

    if any(check["status"] in {"CONFLITO", "DUPLICATAS"} for check in checks):
        _emit({"schema_version": SCHEMA_VERSION, "result": "COMPLETE", "checks": checks})
        return EXIT_CODES["PREFLIGHT_REJECTED"]
    _emit({"schema_version": SCHEMA_VERSION, "result": "COMPLETE", "checks": checks})
    return 0


def main() -> None:
    try:
        code = asyncio.run(run())
    except Exception:
        # Last-resort sanitized boundary for import/runtime failures.
        _emit({"schema_version": SCHEMA_VERSION, "result": "ERROR", "category": "PREFLIGHT_EXECUTION"})
        code = EXIT_CODES["PREFLIGHT_EXECUTION"]
    raise SystemExit(code)


if __name__ == "__main__":
    main()
