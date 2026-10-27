"""Remove only containers/network created by the unique PoC Compose project."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_RE = re.compile(r"editorial-poc-([a-f0-9]{32})\Z")
RUN_LABEL = "io.trilhacode.editorial-poc.run"
DOCKER_CONTEXT_CHECK = Path(__file__).with_name("verify_docker_context.py")


def docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args],
        check=check,
        capture_output=True,
        text=True,
    )


def inspect_labels(resource_type: str, identifiers: list[str]) -> None:
    if not identifiers:
        return
    documents = json.loads(docker(resource_type, "inspect", *identifiers).stdout)
    project = os.environ["EDITORIAL_POC_PROJECT"]
    run_id = os.environ["EDITORIAL_POC_RUN_ID"]
    for document in documents:
        if resource_type == "container":
            labels = document.get("Config", {}).get("Labels", {})
        else:
            labels = document.get("Labels", {})
        owned_by_project = labels.get("com.docker.compose.project") == project
        run_matches = labels.get(RUN_LABEL) == run_id
        compose_volume = resource_type == "volume" and bool(
            labels.get("com.docker.compose.volume")
        )
        if not owned_by_project or not (run_matches or compose_volume):
            raise RuntimeError(
                f"Recurso {resource_type} sem identidade desta execução; limpeza recusada"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", required=True)
    args = parser.parse_args()
    project = os.environ.get("EDITORIAL_POC_PROJECT", "")
    run_id = os.environ.get("EDITORIAL_POC_RUN_ID", "")
    match = PROJECT_RE.fullmatch(project)
    if not match or match.group(1) != run_id:
        print(
            "Limpeza recusada: identidade de projeto ausente ou inválida.",
            file=sys.stderr,
        )
        return 2

    try:
        subprocess.run(
            [sys.executable, str(DOCKER_CONTEXT_CHECK)],
            check=True,
            capture_output=True,
            text=True,
        )
        containers = docker(
            "ps",
            "--all",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ).stdout.split()
        networks = docker(
            "network",
            "ls",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ).stdout.split()
        volumes = docker(
            "volume",
            "ls",
            "--quiet",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ).stdout.split()
        inspect_labels("container", containers)
        inspect_labels("network", networks)
        inspect_labels("volume", volumes)
        if not containers and not networks and not volumes:
            print("Limpeza: nenhum recurso do projeto descartável permaneceu.")
            return 0

        compose_file = Path(args.compose_file).resolve()
        result = docker(
            "compose",
            "--project-name",
            project,
            "--file",
            str(compose_file),
            "down",
            "--volumes",
            check=False,
        )
        if result.returncode:
            print(
                "Limpeza Compose falhou; nenhum comando global foi executado.",
                file=sys.stderr,
            )
            print(result.stderr, file=sys.stderr)
            return result.returncode
        print(
            "Limpeza: recursos do projeto exclusivo removidos após validação dos labels."
        )
        return 0
    except (
        OSError,
        subprocess.CalledProcessError,
        RuntimeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"Limpeza recusada/falhou: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
