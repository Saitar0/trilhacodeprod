"""Remove only containers/network created by the unique PoC Compose project."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path

from runtime_supervision import run_bounded_capture, sanitize_output
from verify_docker_context import DockerContextError
from verify_docker_context import verify as verify_docker_context

PROJECT_RE = re.compile(r"editorial-poc-([a-f0-9]{32})\Z")
RUN_LABEL = "io.trilhacode.editorial-poc.run"
MAX_CLEANUP_SECONDS = 180


class CleanupFailure(RuntimeError):
    def __init__(self, message: str, exit_code: int = 3):
        super().__init__(message)
        self.exit_code = exit_code


class CleanupInterrupted(Exception):
    def __init__(self, signum: int):
        self.signum = signum


def _sanitized(value: object, environment: Mapping[str, str]) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    secrets = [
        item
        for key, item in environment.items()
        if any(part in key.upper() for part in ("PASSWORD", "TOKEN", "SECRET", "URI"))
    ]
    return sanitize_output(str(value or ""), secrets)


def _run(
    command: list[str],
    *,
    runner: Callable = run_bounded_capture,
    deadline: float,
    monotonic: Callable[[], float],
    environment: Mapping[str, str],
    label: str,
) -> subprocess.CompletedProcess[str]:
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise CleanupFailure(f"prazo de limpeza excedido antes de {label}", 124)
    try:
        result = runner(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=remaining,
        )
    except subprocess.TimeoutExpired as exc:
        detail = _sanitized(exc.stderr or exc.output, environment)
        suffix = f"; detalhe={detail}" if detail else ""
        raise CleanupFailure(f"timeout em {label}{suffix}", 124) from None
    except OSError as exc:
        raise CleanupFailure(f"falha ao iniciar {label}: {type(exc).__name__}", 3) from None
    if result.returncode:
        detail = _sanitized(result.stderr or result.stdout, environment)
        suffix = f"; detalhe={detail}" if detail else ""
        raise CleanupFailure(
            f"{label} retornou código {result.returncode}{suffix}", 3
        )
    return result


def _docker(
    args: list[str],
    *,
    runner: Callable,
    deadline: float,
    monotonic: Callable[[], float],
    environment: Mapping[str, str],
    label: str,
) -> subprocess.CompletedProcess[str]:
    return _run(
        ["docker", *args],
        runner=runner,
        deadline=deadline,
        monotonic=monotonic,
        environment=environment,
        label=label,
    )


def _resource_ids(
    kind: str,
    project: str,
    *,
    runner: Callable,
    deadline: float,
    monotonic: Callable[[], float],
    environment: Mapping[str, str],
) -> list[str]:
    if kind == "container":
        args = ["ps", "--all", "--quiet"]
    else:
        args = [kind, "ls", "--quiet"]
    result = _docker(
        [*args, "--filter", f"label=com.docker.compose.project={project}"],
        runner=runner,
        deadline=deadline,
        monotonic=monotonic,
        environment=environment,
        label=f"listar {kind}",
    )
    return result.stdout.split()


def _inspect_labels(
    resource_type: str,
    identifiers: list[str],
    project: str,
    run_id: str,
    *,
    runner: Callable,
    deadline: float,
    monotonic: Callable[[], float],
    environment: Mapping[str, str],
) -> None:
    if not identifiers:
        return
    documents = json.loads(
        _docker(
            [resource_type, "inspect", *identifiers],
            runner=runner,
            deadline=deadline,
            monotonic=monotonic,
            environment=environment,
            label=f"inspecionar {resource_type}",
        ).stdout
    )
    if not isinstance(documents, list) or len(documents) != len(identifiers):
        raise CleanupFailure(f"resposta de inspeção inválida para {resource_type}")
    for document in documents:
        if not isinstance(document, dict):
            raise CleanupFailure(f"documento de inspeção inválido para {resource_type}")
        if resource_type == "container":
            config = document.get("Config", {})
            if not isinstance(config, dict):
                raise CleanupFailure("configuração de container inspecionada é inválida")
            labels = config.get("Labels", {})
        else:
            labels = document.get("Labels", {})
        if not isinstance(labels, dict):
            raise CleanupFailure(f"labels de inspeção inválidas para {resource_type}")
        owned_by_project = labels.get("com.docker.compose.project") == project
        run_matches = labels.get(RUN_LABEL) == run_id
        compose_volume = resource_type == "volume" and bool(
            labels.get("com.docker.compose.volume")
        )
        if not owned_by_project or not (run_matches or compose_volume):
            raise CleanupFailure(
                f"recurso {resource_type} sem identidade desta execução; limpeza recusada",
                2,
            )


def cleanup_project(
    project: str,
    run_id: str,
    compose_file: str | Path,
    *,
    runner: Callable = run_bounded_capture,
    verify_context: Callable[[], object] = verify_docker_context,
    monotonic: Callable[[], float] = time.monotonic,
    budget_seconds: float = MAX_CLEANUP_SECONDS,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Fail closed unless identity, Compose file, Docker context and labels agree."""
    match = PROJECT_RE.fullmatch(project)
    if not match or match.group(1) != run_id:
        raise CleanupFailure("identidade de projeto ausente ou inválida", 2)
    compose_path = Path(compose_file)
    expected_compose = Path(__file__).with_name("compose.yaml")
    if compose_path.is_symlink() or expected_compose.is_symlink():
        raise CleanupFailure("arquivo Compose é link simbólico; limpeza recusada", 2)
    try:
        resolved_compose = compose_path.resolve(strict=True)
        expected_resolved = expected_compose.resolve(strict=True)
    except OSError:
        raise CleanupFailure("arquivo Compose da execução está ausente", 2) from None
    if resolved_compose != expected_resolved or not resolved_compose.is_file():
        raise CleanupFailure("arquivo Compose não corresponde ao harness fixo", 2)

    env = environment if environment is not None else os.environ
    deadline = monotonic() + budget_seconds
    try:
        verify_context()
    except KeyboardInterrupt:
        raise
    except (DockerContextError, OSError, json.JSONDecodeError) as exc:
        raise CleanupFailure(
            f"contexto Docker recusado: {type(exc).__name__}", 3
        ) from None

    resources = {
        kind: _resource_ids(
            kind,
            project,
            runner=runner,
            deadline=deadline,
            monotonic=monotonic,
            environment=env,
        )
        for kind in ("container", "network", "volume")
    }
    for kind, identifiers in resources.items():
        _inspect_labels(
            kind,
            identifiers,
            project,
            run_id,
            runner=runner,
            deadline=deadline,
            monotonic=monotonic,
            environment=env,
        )
    if not any(resources.values()):
        print("Limpeza: nenhum recurso do projeto descartável permaneceu.", flush=True)
        return

    _docker(
        [
            "compose",
            "--project-name",
            project,
            "--file",
            str(resolved_compose),
            "down",
            "--volumes",
        ],
        runner=runner,
        deadline=deadline,
        monotonic=monotonic,
        environment=env,
        label="docker compose down direcionado",
    )
    remaining = {
        kind: _resource_ids(
            kind,
            project,
            runner=runner,
            deadline=deadline,
            monotonic=monotonic,
            environment=env,
        )
        for kind in ("container", "network", "volume")
    }
    if any(remaining.values()):
        raise CleanupFailure(
            "recursos identificados permaneceram após docker compose down"
        )
    print(
        "Limpeza: recursos do projeto exclusivo removidos e ausência confirmada.",
        flush=True,
    )


def main(
    argv: list[str] | None = None,
    *,
    runner: Callable = run_bounded_capture,
    verify_context: Callable[[], object] = verify_docker_context,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", required=True)
    args = parser.parse_args(argv)
    project = os.environ.get("EDITORIAL_POC_PROJECT", "")
    run_id = os.environ.get("EDITORIAL_POC_RUN_ID", "")
    watched_signals = [signal.SIGINT]
    if hasattr(signal, "SIGTERM"):
        watched_signals.append(signal.SIGTERM)
    previous_handlers = {signum: signal.getsignal(signum) for signum in watched_signals}

    def interrupt(signum, _frame):
        raise CleanupInterrupted(signum)

    try:
        for signum in watched_signals:
            signal.signal(signum, interrupt)
        cleanup_project(
            project,
            run_id,
            args.compose_file,
            runner=runner,
            verify_context=verify_context,
        )
        return 0
    except CleanupInterrupted as exc:
        print(
            f"Limpeza interrompida por sinal {exc.signum}; estado não confirmado.",
            file=sys.stderr,
            flush=True,
        )
        return 128 + exc.signum
    except KeyboardInterrupt:
        print("Limpeza interrompida; estado não confirmado.", file=sys.stderr, flush=True)
        return 130
    except CleanupFailure as exc:
        detail = sanitize_output(
            f"{type(exc).__name__}: {exc}",
            [value for key, value in os.environ.items() if any(
                part in key.upper() for part in ("PASSWORD", "TOKEN", "SECRET", "URI")
            )],
        )
        print(f"Limpeza falhou: {detail}", file=sys.stderr, flush=True)
        return exc.exit_code
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Limpeza falhou: {type(exc).__name__}", file=sys.stderr, flush=True)
        return 3
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(main())
