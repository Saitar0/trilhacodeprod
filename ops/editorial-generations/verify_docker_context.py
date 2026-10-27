"""Refuse Docker contexts that could target a remote or non-Linux engine."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from runtime_supervision import run_bounded_capture

DOCKER_OVERRIDES = (
    "DOCKER_HOST",
    "DOCKER_CONTEXT",
    "DOCKER_TLS_VERIFY",
    "DOCKER_CERT_PATH",
)
LOCAL_UNIX_ENDPOINTS = {"unix:///var/run/docker.sock", "unix:///run/docker.sock"}
WINDOWS_DOCKER_DESKTOP_LINUX_ENDPOINT = (
    "npipe:////./pipe/dockerDesktopLinuxEngine"
)


class DockerContextError(RuntimeError):
    pass


def _run(*args: str) -> str:
    try:
        result = run_bounded_capture(
            ["docker", *args],
            check=False,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        raise DockerContextError(f"Docker {' '.join(args[:2])} excedeu 10 segundos") from None
    if result.returncode:
        raise DockerContextError(f"Docker {' '.join(args[:2])} indisponível")
    return result.stdout.strip()


def verify() -> tuple[str, str]:
    if any(os.environ.get(name) for name in DOCKER_OVERRIDES):
        raise DockerContextError("Overrides DOCKER_* são recusados pelo harness")
    context = _run("context", "show")
    endpoint_document = json.loads(
        _run(
            "context",
            "inspect",
            context,
            "--format",
            "{{json .Endpoints.docker}}",
        )
    )
    if not isinstance(endpoint_document, dict):
        raise DockerContextError("Docker retornou metadados de endpoint inválidos")
    host = endpoint_document.get("Host", "")
    if sys.platform == "win32":
        if host.casefold() != WINDOWS_DOCKER_DESKTOP_LINUX_ENDPOINT.casefold():
            raise DockerContextError(
                "No Windows, somente o pipe local exato do Engine Linux do Docker Desktop é aceito"
            )
    elif sys.platform.startswith("linux"):
        if host not in LOCAL_UNIX_ENDPOINTS:
            raise DockerContextError(
                "No Linux, somente o socket local padrão do Docker é aceito"
            )
    else:
        raise DockerContextError("Plataforma Docker não homologada por este harness")

    info = _run("info", "--format", "{{.ServerVersion}}|{{.OSType}}")
    version, separator, operating_system = info.partition("|")
    if not separator or operating_system != "linux" or not version:
        raise DockerContextError(
            "O Engine selecionado não é um Engine Linux operacional"
        )
    return context, version


if __name__ == "__main__":
    try:
        context_name, server_version = verify()
    except (DockerContextError, OSError, json.JSONDecodeError) as exc:
        print(f"Docker recusado: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(
        f"Docker local verificado: contexto {context_name}; "
        f"Engine Linux {server_version}."
    )
