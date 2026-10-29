"""Provision and safely remove an exclusively owned phase-specific MongoDB 7 container."""

from __future__ import annotations

import json
import secrets
import socket
import subprocess
import time
import uuid
from typing import Any, Literal
from urllib.parse import quote

from test_support.beta5_mongo_target import (
    MongoTarget,
    MongoTargetError,
    assert_database_owned,
    connect_verified_target,
    validate_target,
)


class DisposableMongoHarness:
    """Context manager for a phase-labelled, loopback-only disposable server."""

    def __init__(self, phase: Literal["beta5", "beta6"] = "beta5") -> None:
        self.phase = phase
        self.run_id = uuid.uuid4().hex
        self.owner_token = secrets.token_urlsafe(36)
        self.username = f"{phase}_{self.run_id[:10]}"
        self.password = secrets.token_urlsafe(36)
        self.network_name = f"tc-{phase}-{self.run_id[:12]}"
        self.container_name = f"tc-{phase}-mongo-{self.run_id[:12]}"
        self.network_id: str | None = None
        self.container_id: str | None = None
        self.host_port: int | None = None
        self.target: MongoTarget | None = None
        self.client: Any = None

    @staticmethod
    def _run(arguments: list[str]) -> str:
        try:
            completed = subprocess.run(
                ["docker", *arguments], check=True, capture_output=True, text=True, timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            # Docker output may contain the container environment. Never expose it.
            raise MongoTargetError("Falha ao provisionar o MongoDB descartável") from exc
        return completed.stdout.strip()

    def _labels(self) -> list[str]:
        return [
            "--label", f"io.trilhacode.phase={self.phase}",
            "--label", f"io.trilhacode.run-id={self.run_id}",
            "--label", f"io.trilhacode.owner-token={self.owner_token}",
        ]

    def _inspectors(self, resource_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        container = json.loads(self._run(["inspect", resource_id]))[0]
        network = json.loads(self._run(["network", "inspect", self.network_id or ""]))[0]
        return container, network

    def _environment(self) -> dict[str, str]:
        if not self.container_id or not self.network_id:
            raise MongoTargetError(f"Recursos {self.phase.upper()} ainda não têm identidade verificada")
        deadline = time.monotonic() + 10
        container: dict[str, Any] = {}
        port_binding: dict[str, str] | None = None
        while time.monotonic() < deadline:
            container, _network = self._inspectors(self.container_id)
            bindings = ((container.get("NetworkSettings") or {}).get("Ports") or {}).get("27017/tcp") or []
            if bindings and bindings[0].get("HostPort"):
                port_binding = bindings[0]
                break
            time.sleep(0.1)
        if not port_binding or port_binding.get("HostIp") != "127.0.0.1":
            configured = ((container.get("HostConfig") or {}).get("PortBindings") or {}).get("27017/tcp")
            raise MongoTargetError(
                "Docker não publicou uma porta efêmera exclusivamente no loopback "
                f"(published={port_binding!r}, configured={configured!r}, "
                f"running={(container.get('State') or {}).get('Running')!r})"
            )
        port = int(port_binding["HostPort"])
        if self.host_port is not None and port != self.host_port:
            raise MongoTargetError("Porta publicada diverge da porta efêmera reservada por esta execução")
        database = f"{self.phase}_{self.run_id}"
        uri = (
            f"mongodb://{quote(self.username)}:{quote(self.password)}@127.0.0.1:{port}/{database}"
            "?authSource=admin&directConnection=true"
        )
        return {
            f"{self.phase.upper()}_TEST_MONGO_URI": uri,
            f"{self.phase.upper()}_TEST_MONGO_DATABASE": database,
            f"{self.phase.upper()}_TEST_RUN_ID": self.run_id,
            f"{self.phase.upper()}_TEST_OWNER_TOKEN": self.owner_token,
            f"{self.phase.upper()}_TEST_CONTAINER_ID": self.container_id,
            f"{self.phase.upper()}_TEST_NETWORK_ID": self.network_id,
        }

    def __enter__(self) -> "DisposableMongoHarness":
        # Docker Desktop may leave an empty dynamic binding on an internal
        # network. Reserve an ephemeral loopback port locally, then ask Docker
        # to bind exactly that port. The validator still checks the resulting
        # container and network before any database connection is opened.
        if self.phase == "beta6":
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                listener.bind(("127.0.0.1", 0))
                self.host_port = int(listener.getsockname()[1])
        network_arguments = ["network", "create", "--driver", "bridge"]
        if self.phase == "beta6":
            network_arguments.append("--internal")
        self.network_id = self._run([*network_arguments, *self._labels(), self.network_name])
        try:
            self.container_id = self._run([
                "run", "--detach", "--name", self.container_name,
                "--network", self.network_name,
                "--publish", (
                    f"127.0.0.1:{self.host_port}:27017"
                    if self.host_port is not None else "127.0.0.1::27017"
                ),
                "--tmpfs", "/data/db:rw,noexec,nosuid,size=768m",
                "--tmpfs", "/data/configdb:rw,noexec,nosuid,size=64m",
                *self._labels(),
                "--env", f"MONGO_INITDB_ROOT_USERNAME={self.username}",
                "--env", f"MONGO_INITDB_ROOT_PASSWORD={self.password}",
                "mongo:7.0.43",
            ])
            environment = self._environment()
            # Validate Docker identity once before retrying readiness probes.
            target = validate_target(
                environment,
                phase=self.phase,
                container_inspector=lambda _id: self._inspectors(_id)[0],
                network_inspector=lambda _id: self._inspectors(self.container_id or "")[1],
            )
            deadline = time.monotonic() + 45
            last_error: Exception | None = None
            while time.monotonic() < deadline:
                try:
                    self.target, self.client = connect_verified_target(
                        environment,
                        lambda uri: __import__("pymongo").MongoClient(
                            uri, serverSelectionTimeoutMS=1500, connectTimeoutMS=1000,
                        ),
                        phase=self.phase,
                        container_inspector=lambda _id: self._inspectors(_id)[0],
                        network_inspector=lambda _id: self._inspectors(self.container_id or "")[1],
                    )
                    break
                except MongoTargetError as exc:
                    last_error = exc
                    time.sleep(0.5)
            else:
                raise MongoTargetError("MongoDB descartável não ficou pronto dentro do limite") from last_error
            if self.target != target:
                raise MongoTargetError("Identidade do alvo mudou durante a verificação")
            return self
        except Exception:
            self._cleanup_owned_resources(verify_database=False)
            raise

    def environment(self) -> dict[str, str]:
        if self.target is None:
            raise MongoTargetError(f"Harness {self.phase} não está ativo")
        return self._environment()

    def _cleanup_owned_resources(self, *, verify_database: bool = True) -> None:
        if self.container_id:
            container, network = self._inspectors(self.container_id)
            labels = (container.get("Config") or {}).get("Labels") or {}
            if container.get("Id", "").lower() != self.container_id.lower() or any(
                labels.get(key) != value for key, value in {
                    "io.trilhacode.phase": self.phase,
                    "io.trilhacode.run-id": self.run_id,
                    "io.trilhacode.owner-token": self.owner_token,
                }.items()
            ):
                raise MongoTargetError(f"Container não pertence comprovadamente à execução {self.phase}")
            if verify_database and self.client is not None and self.target is not None:
                assert_database_owned(self.client, self.target)
            if self.client is not None:
                self.client.close()
                self.client = None
            self._run(["rm", "--force", self.container_id])
            self.container_id = None
        if self.network_id:
            rows = json.loads(self._run(["network", "inspect", self.network_id]))
            if len(rows) != 1 or rows[0].get("Id", "").lower() != self.network_id.lower():
                raise MongoTargetError("Rede não pertence comprovadamente à execução Beta 5")
            labels = rows[0].get("Labels") or {}
            if any(labels.get(key) != value for key, value in {
                "io.trilhacode.phase": self.phase,
                "io.trilhacode.run-id": self.run_id,
                "io.trilhacode.owner-token": self.owner_token,
            }.items()):
                raise MongoTargetError(f"Marcador da rede {self.phase} divergiu; preservando o recurso")
            if rows[0].get("Containers"):
                raise MongoTargetError("Rede Beta 5 ainda contém recursos; preservando-a")
            self._run(["network", "rm", self.network_id])
            self.network_id = None

    def __exit__(self, exc_type, exc, traceback) -> Literal[False]:
        self._cleanup_owned_resources()
        return False


# Backward-compatible name for earlier Beta 5 regression tooling.
Beta5MongoHarness = DisposableMongoHarness
