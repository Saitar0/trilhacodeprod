"""Owned, internal-network Docker harness for Beta 6.1 HTTP/browser checks.

No MongoDB port is published. The runner, API, Vite, Playwright, and MongoDB
share one dedicated internal bridge. Host-side Docker inspection is the gate
before any test process, migration, seed, or database connection starts.
"""

from __future__ import annotations

import json
import secrets
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Literal


class Beta61HarnessError(RuntimeError):
    """The disposable Beta 6.1 environment could not be proven safe."""


def local_readiness_probe() -> str:
    """Return valid Python source for runner-local API and frontend probes."""
    return """\
import time
import urllib.request

targets = ["http://127.0.0.1:18000/health", "http://127.0.0.1:3000/login"]
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    try:
        for target in targets:
            urllib.request.urlopen(target, timeout=2).read(2048)
        break
    except Exception:
        time.sleep(0.25)
else:
    raise SystemExit("local application readiness timed out")
"""


class Beta61DockerHarness:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.run_id = uuid.uuid4().hex
        self.owner_token = secrets.token_urlsafe(48)
        self.suffix = self.run_id[:12]
        self.network_name = f"tc-beta6-1-{self.suffix}"
        self.mongo_name = f"tc-beta6-1-mongo-{self.suffix}"
        self.runner_name = f"tc-beta6-1-runner-{self.suffix}"
        self.mongo_user = f"beta6_{self.run_id[:10]}"
        self.mongo_password = secrets.token_urlsafe(48)
        self.database = f"beta6_{self.run_id}"
        self.mongo_uri = (
            f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_name}:27017/{self.database}"
            "?authSource=admin&directConnection=true"
        )
        self.jwt_secret = secrets.token_urlsafe(48)
        self.image_tag = f"tc-beta6-1-e2e:{self.suffix}"
        self.labels = {
            "io.trilhacode.phase": "beta6-1",
            "io.trilhacode.run-id": self.run_id,
            "io.trilhacode.owner-token": self.owner_token,
        }
        self.network_id: str | None = None
        self.mongo_id: str | None = None
        self.runner_id: str | None = None
        self.image_id: str | None = None
        self.gate_proof: str | None = None
        self.gate_passed = False

    def _docker(self, arguments: list[str], *, timeout: int = 30) -> str:
        try:
            completed = subprocess.run(
                ["docker", *arguments], check=True, capture_output=True, text=True, timeout=timeout,
                cwd=self.repo_root,
            )
        except (OSError, subprocess.SubprocessError):
            # Docker inspect/run output can contain credentials; never echo it.
            raise Beta61HarnessError("Falha ao provisionar ou verificar recursos Beta 6.1") from None
        return completed.stdout.strip()

    def _inspect_container(self, resource_id: str) -> dict[str, Any]:
        try:
            rows = json.loads(self._docker(["inspect", resource_id]))
        except (json.JSONDecodeError, Beta61HarnessError) as exc:
            raise Beta61HarnessError("Não foi possível verificar um container Beta 6.1") from exc
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise Beta61HarnessError("Identidade de container Beta 6.1 inválida")
        return rows[0]

    def _inspect_network(self) -> dict[str, Any]:
        if not self.network_id:
            raise Beta61HarnessError("Rede Beta 6.1 ainda não foi provisionada")
        try:
            rows = json.loads(self._docker(["network", "inspect", self.network_id]))
        except (json.JSONDecodeError, Beta61HarnessError) as exc:
            raise Beta61HarnessError("Não foi possível verificar a rede Beta 6.1") from exc
        if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
            raise Beta61HarnessError("Identidade da rede Beta 6.1 inválida")
        return rows[0]

    def _adopt_partial_resources(self) -> None:
        """Recover IDs for exact owned resources if a Docker CLI call timed out."""
        try:
            images = json.loads(self._docker(["image", "inspect", self.image_tag]))
        except (json.JSONDecodeError, Beta61HarnessError):
            images = []
        if len(images) == 1 and (images[0].get("Config") or {}).get("Labels") == self.labels:
            image_id = images[0].get("Id")
            if isinstance(image_id, str) and image_id.startswith("sha256:"):
                self.image_id = image_id

        try:
            networks = json.loads(self._docker(["network", "inspect", self.network_name]))
        except (json.JSONDecodeError, Beta61HarnessError):
            networks = []
        if len(networks) == 1:
            network = networks[0]
            if (network.get("Name") == self.network_name
                    and (network.get("Labels") or {}) == self.labels
                    and isinstance(network.get("Id"), str)):
                self.network_id = network["Id"]

        for name, expected in ((self.mongo_name, "mongo_id"), (self.runner_name, "runner_id")):
            try:
                containers = json.loads(self._docker(["inspect", name]))
            except (json.JSONDecodeError, Beta61HarnessError):
                containers = []
            if len(containers) != 1:
                continue
            container = containers[0]
            if (container.get("Name") == f"/{name}"
                    and ((container.get("Config") or {}).get("Labels") or {}) == self.labels
                    and isinstance(container.get("Id"), str)):
                setattr(self, expected, container["Id"])

    def _label_args(self) -> list[str]:
        return [argument for key, value in self.labels.items() for argument in ("--label", f"{key}={value}")]

    def _run_env(self) -> dict[str, str]:
        if (self.mongo_id is None or self.network_id is None or self.runner_id is None
                or self.gate_proof is None):
            raise Beta61HarnessError("O gate Beta 6.1 ainda não foi aprovado")
        return {
            "BETA6_TEST_ISOLATION_GATE": f"beta6-1:{self.gate_proof}",
            "BETA6_TEST_MONGO_URI": self.mongo_uri,
            "BETA6_TEST_MONGO_DATABASE": self.database,
            "BETA6_TEST_RUN_ID": self.run_id,
            "BETA6_TEST_OWNER_TOKEN": self.owner_token,
            "BETA6_TEST_CONTAINER_ID": self.mongo_id,
            "BETA6_TEST_NETWORK_ID": self.network_id,
            "BETA6_TEST_RUNNER_ID": self.runner_id,
            "BETA6_TEST_MONGO_HOST": self.mongo_name,
            "BETA6_TEST_NETWORK_NAME": self.network_name,
            "BETA6_TEST_RUNNER_NAME": self.runner_name,
        }

    def __enter__(self) -> "Beta61DockerHarness":
        self._docker(["context", "show"])
        build_file = "backend/test_support/Dockerfile.beta6_1_e2e"
        try:
            try:
                self._docker(["image", "inspect", self.image_tag])
            except Beta61HarnessError:
                pass
            else:
                raise Beta61HarnessError("Tag única da imagem Beta 6.1 já existe; preservando o recurso")
            self._docker([
                "build", "--file", build_file, "--tag", self.image_tag,
                *self._label_args(), ".",
            ], timeout=1800)
            images = json.loads(self._docker(["image", "inspect", self.image_tag]))
            if len(images) != 1 or images[0].get("Config", {}).get("Labels") != self.labels:
                raise Beta61HarnessError("Imagem de testes não possui identidade Beta 6.1 esperada")
            self.image_id = images[0].get("Id")
            if not isinstance(self.image_id, str) or not self.image_id.startswith("sha256:"):
                raise Beta61HarnessError("Imagem runner sem identidade imutável")
        except Exception:
            self._adopt_partial_resources()
            self.cleanup()
            raise

        try:
            self.network_id = self._docker([
                "network", "create", "--driver", "bridge", "--internal",
                *self._label_args(), self.network_name,
            ])
            self.mongo_id = self._docker([
                "run", "--detach", "--name", self.mongo_name,
                "--network", self.network_name,
                "--tmpfs", "/data/db:rw,noexec,nosuid,size=768m",
                "--tmpfs", "/data/configdb:rw,noexec,nosuid,size=64m",
                *self._label_args(),
                "--env", f"MONGO_INITDB_ROOT_USERNAME={self.mongo_user}",
                "--env", f"MONGO_INITDB_ROOT_PASSWORD={self.mongo_password}",
                "mongo:7.0.43",
            ], timeout=300)
            runner_env = {
                "MONGO_URL": self.mongo_uri,
                "DB_NAME": self.database,
                "ENV": "development",
                "CI": "",
                "JWT_SECRET": self.jwt_secret,
                "FRONTEND_URL": "http://localhost:3000",
                "CORS_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
                "PLAYWRIGHT_BASE_URL": "http://127.0.0.1:3000",
                "API_BASE_URL": "http://127.0.0.1:18000",
                "EMAIL_TRANSPORT": "local",
                "LOCAL_EMAIL_DIR": "/tmp/beta6-1-mail",
                "E2E_ADMIN_EMAIL": "admin@example.com",
                "E2E_ADMIN_PASSWORD": "beta6-1-synthetic-admin-password",
                "E2E_STUDENT_EMAIL": "student@example.com",
                "E2E_STUDENT_PASSWORD": "beta6-1-synthetic-student-password",
                "E2E_REVIEWER_EMAIL": "reviewer@example.com",
                "E2E_REVIEWER_PASSWORD": "beta6-1-synthetic-reviewer-password",
                "E2E_UNSCOPED_EMAIL": "unscoped@example.com",
                "E2E_UNSCOPED_PASSWORD": "beta6-1-synthetic-unscoped-password",
            }
            runner_arguments = [
                "run", "--detach", "--name", self.runner_name,
                "--network", self.network_name,
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=128m",
                *self._label_args(),
            ]
            for key, value in runner_env.items():
                runner_arguments.extend(("--env", f"{key}={value}"))
            runner_arguments.extend((self.image_tag, "sleep", "infinity"))
            self.runner_id = self._docker(runner_arguments, timeout=300)
            self.validate_gate()
            self.gate_proof = secrets.token_hex(32)
            self.gate_passed = True
            return self
        except Exception:
            self._adopt_partial_resources()
            self.cleanup()
            raise

    def validate_gate(self) -> dict[str, str]:
        """Prove ownership, internal network, storage, and no published ports."""
        if (self.network_id is None or self.mongo_id is None or self.runner_id is None
                or self.image_id is None):
            raise Beta61HarnessError("Recursos necessários ao gate Beta 6.1 estão ausentes")
        network_id, mongo_id = self.network_id, self.mongo_id
        runner_id, image_id = self.runner_id, self.image_id
        network = self._inspect_network()
        mongo = self._inspect_container(mongo_id)
        runner = self._inspect_container(runner_id)
        resources = ((mongo, mongo_id, self.mongo_name), (runner, runner_id, self.runner_name))
        for container, expected_id, expected_name in resources:
            if container.get("Id", "").lower() != expected_id.lower() or container.get("Name") != f"/{expected_name}":
                raise Beta61HarnessError("Container diverge da identidade criada nesta execução")
            labels = (container.get("Config") or {}).get("Labels") or {}
            if any(labels.get(key) != value for key, value in self.labels.items()):
                raise Beta61HarnessError("Container não pertence comprovadamente à execução Beta 6.1")
            if not (container.get("State") or {}).get("Running"):
                raise Beta61HarnessError("Container Beta 6.1 não está em execução")
            host_config = container.get("HostConfig") or {}
            if host_config.get("PortBindings") or host_config.get("Binds") or host_config.get("VolumesFrom"):
                raise Beta61HarnessError("Porta publicada ou armazenamento externo não autorizado")
            if container.get("Mounts"):
                raise Beta61HarnessError("Container Beta 6.1 tem mount persistente inesperado")
            attached = (container.get("NetworkSettings") or {}).get("Networks") or {}
            if set(attached) != {self.network_name}:
                raise Beta61HarnessError("Container não está somente na rede isolada Beta 6.1")

        network_labels = network.get("Labels") or {}
        if network.get("Id", "").lower() != network_id.lower() or network.get("Name") != self.network_name:
            raise Beta61HarnessError("Rede diverge da identidade criada nesta execução")
        if network.get("Driver") != "bridge" or network.get("Internal") is not True:
            raise Beta61HarnessError("A rede Beta 6.1 deve ser uma bridge interna")
        if any(network_labels.get(key) != value for key, value in self.labels.items()):
            raise Beta61HarnessError("Rede sem marcador de propriedade Beta 6.1 correspondente")
        attached_ids = set((network.get("Containers") or {}).keys())
        if attached_ids != {self.mongo_id, self.runner_id}:
            raise Beta61HarnessError("Rede Beta 6.1 contém containers além do Mongo e runner próprios")

        mongo_config = mongo.get("Config") or {}
        if mongo_config.get("Image") != "mongo:7.0.43":
            raise Beta61HarnessError("Imagem do MongoDB diverge da versão descartável aprovada")
        expected_tmpfs = {"/data/db", "/data/configdb"}
        if set((mongo.get("HostConfig") or {}).get("Tmpfs") or {}) != expected_tmpfs:
            raise Beta61HarnessError("Armazenamento do MongoDB não é exclusivamente temporário")
        if ((mongo.get("NetworkSettings") or {}).get("Ports") or {}).get("27017/tcp"):
            raise Beta61HarnessError("MongoDB possui uma porta publicada inesperada")
        configured = set(mongo_config.get("Env") or [])
        if (f"MONGO_INITDB_ROOT_USERNAME={self.mongo_user}" not in configured
                or f"MONGO_INITDB_ROOT_PASSWORD={self.mongo_password}" not in configured):
            raise Beta61HarnessError("Credenciais Mongo não correspondem às exclusivas da execução")

        runner_host = runner.get("HostConfig") or {}
        if set(runner_host.get("Tmpfs") or {}) != {"/tmp"}:
            raise Beta61HarnessError("Runner sem armazenamento temporário exclusivo")
        if runner.get("Image") != image_id:
            raise Beta61HarnessError("Runner não utiliza a imagem imutável verificada")
        expected_runner_env = {
            "MONGO_URL": self.mongo_uri,
            "DB_NAME": self.database,
            "ENV": "development",
            "CI": "",
            "EMAIL_TRANSPORT": "local",
            "LOCAL_EMAIL_DIR": "/tmp/beta6-1-mail",
            "PLAYWRIGHT_BASE_URL": "http://127.0.0.1:3000",
            "API_BASE_URL": "http://127.0.0.1:18000",
        }
        runner_config_env = set((runner.get("Config") or {}).get("Env") or [])
        if any(f"{key}={value}" not in runner_config_env for key, value in expected_runner_env.items()):
            raise Beta61HarnessError("Configuração do runner diverge do banco Beta 6.1 autorizado")

        return {
            "docker_context": self._docker(["context", "show"]),
            "run_id": self.run_id,
            "network_id": network_id,
            "mongo_container_id": mongo_id,
            "runner_container_id": runner_id,
            "database": self.database,
            "network_internal": "true",
            "published_ports": "none",
            "persistent_mounts": "none",
            "image_id": image_id,
        }

    def _exec(
        self,
        arguments: list[str],
        *,
        timeout: int = 300,
        environment: dict[str, str] | None = None,
        detach: bool = False,
        workdir: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed or not self.gate_proof:
            raise Beta61HarnessError("Execução bloqueada: gate Beta 6.1 não aprovado")
        if not self.runner_id:
            raise Beta61HarnessError("Runner Beta 6.1 inexistente")
        command = ["docker", "exec"]
        if detach:
            command.append("--detach")
        if workdir:
            command.extend(("--workdir", workdir))
        for key, value in (environment or {}).items():
            command.extend(("--env", f"{key}={value}"))
        command.extend((self.runner_id, *arguments))
        try:
            return subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError):
            raise Beta61HarnessError("Falha ao executar comando no runner Beta 6.1") from None

    def run_pytest(self, tests: list[str]) -> subprocess.CompletedProcess[str]:
        if not tests or any(".." in Path(value).parts or Path(value).is_absolute() for value in tests):
            raise Beta61HarnessError("Informe testes relativos e contidos no projeto")
        proof_env = self._run_env()
        self.gate_passed = True
        return self._exec(
            ["python", "-m", "pytest", "--beta6-1-isolated-mongo", *tests],
            timeout=900,
            environment=proof_env,
        )

    def start_local_app(self) -> None:
        """Start API and Vite only inside the runner's internal-network namespace."""
        if not self.gate_passed:
            raise Beta61HarnessError("Inicialização bloqueada antes da aprovação do gate")
        api = self._exec(
            ["sh", "-c", "exec python -m uvicorn server:app --host 127.0.0.1 --port 18000 > /tmp/beta6-1-api.log 2>&1"],
            timeout=20,
            detach=True,
        )
        if api.returncode != 0:
            raise Beta61HarnessError("Não foi possível iniciar a API local Beta 6.1")
        web = self._exec([
            "sh", "-c", "exec npm run start -- --host 127.0.0.1 --port 3000 --strictPort > /tmp/beta6-1-web.log 2>&1",
        ], timeout=20, detach=True, workdir="/workspace/frontend")
        if web.returncode != 0:
            raise Beta61HarnessError("Não foi possível iniciar o frontend local Beta 6.1")
        ready = self._exec(["python", "-c", local_readiness_probe()], timeout=75)
        if ready.returncode != 0:
            logs = self._exec([
                "sh", "-c", "for file in /tmp/beta6-1-api.log /tmp/beta6-1-web.log; do "
                "if [ -f \"$file\" ]; then echo ===${file}===; tail -n 30 \"$file\"; fi; done",
            ], timeout=10)
            diagnostic = logs.stdout[-3000:] if logs.returncode == 0 else ""
            for secret in (self.mongo_uri, self.mongo_password, self.jwt_secret, self.owner_token):
                diagnostic = diagnostic.replace(secret, "[redacted]")
            raise Beta61HarnessError(
                "API e frontend não ficaram prontos no runner isolado. "
                f"Diagnóstico sanitizado: {diagnostic or 'logs de startup indisponíveis'}"
            )

    def seed_learning_fixture(self) -> dict[str, str]:
        """Create only the synthetic fixture after the internal-network gate."""
        result = self._exec(
            ["python", "test_support/beta6_1_seed_fixture.py"],
            timeout=120,
            environment=self._run_env(),
            workdir="/workspace/backend",
        )
        if result.returncode != 0:
            raise Beta61HarnessError("Não foi possível preparar a fixture sintética Beta 6.1")
        try:
            fixture = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError) as exc:
            raise Beta61HarnessError("Fixture sintética não retornou identificadores válidos") from exc
        required = {"track_id", "node_id", "quiz_id", "exercise_id"}
        if not isinstance(fixture, dict) or not required.issubset(fixture):
            raise Beta61HarnessError("Fixture sintética retornou um contrato incompleto")
        return fixture

    def run_playwright(self, spec: str, fixture: dict[str, str]) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed:
            raise Beta61HarnessError("Playwright bloqueado antes da aprovação do gate")
        if Path(spec).is_absolute() or ".." in Path(spec).parts or not spec.startswith("e2e/"):
            raise Beta61HarnessError("Informe um spec Playwright relativo a frontend/e2e")
        fixture_env = {
            "BETA6_E2E_TRACK_ID": fixture["track_id"],
            "BETA6_E2E_TRACK_SLUG": fixture["track_slug"],
            "BETA6_E2E_NODE_ID": fixture["node_id"],
            "BETA6_E2E_QUIZ_ID": fixture["quiz_id"],
            "BETA6_E2E_EXERCISE_ID": fixture["exercise_id"],
        }
        return self._exec(
            ["npx", "--prefix", "/workspace/frontend", "playwright", "test", spec],
            timeout=900,
            environment={**self._run_env(), **fixture_env},
            workdir="/workspace/frontend",
        )

    def run_frontend_quality(self) -> list[subprocess.CompletedProcess[str]]:
        """Run declared frontend checks inside the same isolated runner image."""
        if not self.gate_passed:
            raise Beta61HarnessError("QA do frontend bloqueada antes da aprovação do gate")
        results = []
        for arguments in (
            ["npm", "run", "typecheck"],
            ["npm", "run", "lint"],
            ["npm", "test"],
            ["npm", "run", "build"],
        ):
            result = self._exec(arguments, timeout=600, workdir="/workspace/frontend")
            results.append(result)
            if result.returncode != 0:
                break
        return results

    def _verify_owned_container(self, resource_id: str, expected_name: str) -> bool:
        container = self._inspect_container(resource_id)
        labels = (container.get("Config") or {}).get("Labels") or {}
        return (
            container.get("Id", "").lower() == resource_id.lower()
            and container.get("Name") == f"/{expected_name}"
            and all(labels.get(key) == value for key, value in self.labels.items())
        )

    def cleanup(self) -> None:
        """Remove only exact, still-owned Beta 6.1 resources with no external mounts."""
        for resource_id, name in ((self.runner_id, self.runner_name), (self.mongo_id, self.mongo_name)):
            if not resource_id:
                continue
            try:
                if not self._verify_owned_container(resource_id, name):
                    raise Beta61HarnessError("Propriedade do container divergiu; preservando recurso")
                container = self._inspect_container(resource_id)
                if container.get("Mounts") or (container.get("HostConfig") or {}).get("PortBindings"):
                    raise Beta61HarnessError("Container deixou de satisfazer o isolamento; preservando recurso")
                self._docker(["rm", "--force", "--volumes", resource_id])
            except Beta61HarnessError:
                raise
        if self.network_id:
            network = self._inspect_network()
            if (network.get("Id", "").lower() != self.network_id.lower()
                    or network.get("Name") != self.network_name
                    or network.get("Containers")
                    or not all((network.get("Labels") or {}).get(key) == value
                               for key, value in self.labels.items())):
                raise Beta61HarnessError("Rede deixou de pertencer exclusivamente à Beta 6.1; preservando recurso")
            self._docker(["network", "rm", self.network_id])
            self.network_id = None
        if self.image_id:
            image = json.loads(self._docker(["image", "inspect", self.image_id]))[0]
            if image.get("Id") != self.image_id or image.get("Config", {}).get("Labels") != self.labels:
                raise Beta61HarnessError("Imagem deixou de pertencer à Beta 6.1; preservando recurso")
            references = self._docker(["ps", "-aq", "--filter", f"ancestor={self.image_id}"]).splitlines()
            if references:
                raise Beta61HarnessError("Runner image ainda possui containers; preservando imagem")
            try:
                self._docker(["image", "rm", self.image_id])
            except Beta61HarnessError:
                # Docker Desktop can report a removal error after the image has
                # already disappeared. Re-inspect the exact immutable ID before
                # deciding whether cleanup actually failed.
                try:
                    self._docker(["image", "inspect", self.image_id])
                except Beta61HarnessError:
                    self.image_id = None
                else:
                    raise
            self.image_id = None

    def __exit__(self, exc_type, exc, traceback) -> Literal[False]:
        if exc_type is None:
            self.cleanup()
        else:
            try:
                self.cleanup()
            except Exception as cleanup_error:
                # Preserve the original test failure; cleanup diagnostics are
                # deliberately generic so credentials and Docker output cannot leak.
                print(
                    f"Beta 6.1 cleanup warning: {type(cleanup_error).__name__}",
                    file=sys.stderr,
                )
        return False
