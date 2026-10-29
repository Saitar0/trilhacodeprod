"""Beta 7 runner reusing the proven no-published-port Docker harness pattern."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path, PurePosixPath

from test_support.beta6_1_docker_harness import Beta61DockerHarness, Beta61HarnessError


class Beta7DockerHarness(Beta61DockerHarness):
    """Phase-owned resources; no host Mongo/API/browser ports or persistent mounts."""

    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root)
        self.run_id = uuid.uuid4().hex
        self.suffix = self.run_id[:12]
        self.network_name = f"tc-beta7-{self.suffix}"
        self.mongo_name = f"tc-beta7-mongo-{self.suffix}"
        self.runner_name = f"tc-beta7-runner-{self.suffix}"
        self.mongo_user = f"beta7_{self.run_id[:10]}"
        self.mongo_password = secrets.token_urlsafe(48)
        self.database = f"beta7_{self.run_id}"
        self.mongo_uri = (
            f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_name}:27017/{self.database}"
            "?authSource=admin&directConnection=true"
        )
        self.image_tag = f"tc-beta7-e2e:{self.suffix}"
        self.labels = {
            "io.trilhacode.phase": "beta7",
            "io.trilhacode.run-id": self.run_id,
            "io.trilhacode.owner-token": self.owner_token,
        }

    def _docker(self, arguments: list[str], *, timeout: int = 30) -> str:
        """Decode Docker Desktop output consistently on Windows without exposing it."""
        try:
            completed = subprocess.run(
                ["docker", *arguments], check=True, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout, cwd=self.repo_root,
            )
        except (OSError, subprocess.SubprocessError):
            # Docker inspect and build output can contain credentials or labels.
            raise Beta61HarnessError("Falha ao provisionar ou verificar recursos Beta 7") from None
        return completed.stdout.strip()

    def _run_env(self) -> dict[str, str]:
        if (self.mongo_id is None or self.network_id is None or self.runner_id is None
                or self.gate_proof is None):
            raise RuntimeError("Gate de isolamento Beta 7 ainda não aprovado")
        return {
            "BETA7_TEST_ISOLATION_GATE": f"beta7:{self.gate_proof}",
            "BETA7_TEST_MONGO_URI": self.mongo_uri,
            "BETA7_TEST_MONGO_DATABASE": self.database,
            "BETA7_TEST_RUN_ID": self.run_id,
            "BETA7_TEST_OWNER_TOKEN": self.owner_token,
            "BETA7_TEST_CONTAINER_ID": self.mongo_id,
            "BETA7_TEST_NETWORK_ID": self.network_id,
            "BETA7_TEST_RUNNER_ID": self.runner_id,
            "BETA7_TEST_MONGO_HOST": self.mongo_name,
            "BETA7_TEST_NETWORK_NAME": self.network_name,
            "BETA7_TEST_RUNNER_NAME": self.runner_name,
        }

    def run_pytest(self, tests: list[str], *, curriculum_root: str | None = None) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed:
            raise RuntimeError("Testes Beta 7 bloqueados antes da aprovação do gate")
        if not tests or any(".." in Path(value).parts or Path(value).is_absolute() for value in tests):
            raise RuntimeError("Informe apenas caminhos de teste relativos ao repositório")
        environment = self._run_env()
        if curriculum_root:
            environment["TRILHACODE_BETA7_CURRICULUM_ROOT"] = curriculum_root
            environment["TRILHACODE_BETA4_SOURCE_ROOT"] = curriculum_root
        return self._exec(
            ["python", "-m", "pytest", "--beta7-isolated-mongo", *tests],
            timeout=1200,
            environment=environment,
            workdir="/workspace/backend",
        )

    def copy_verified_curriculum_source(self, source_root: Path) -> str:
        """Copy only manifest-listed read-only inputs into the owned runner."""
        if not self.gate_passed or not self.runner_id:
            raise RuntimeError("Cópia da fonte bloqueada antes do gate Beta 7")
        source_root = source_root.resolve(strict=True)
        try:
            revision = subprocess.run(
                ["git", "-C", str(source_root), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(source_root), "status", "--porcelain", "--",
                 "docs/courses/trilhacode/Conteudos_migrado/Fase_1",
                 "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"],
                check=True, capture_output=True, text=True, timeout=10,
            ).stdout
        except (OSError, subprocess.SubprocessError):
            raise RuntimeError("Não foi possível comprovar revisão e estado da fonte curricular") from None
        if revision != "147dc68b81169f66b0ba3802fa2f26e5130923a3" or status.strip():
            raise RuntimeError("Fonte curricular difere da revisão limpa Beta 4 aprovada para experimento")
        manifest_path = self.repo_root / "docs/beta/beta4-first-phase-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files: dict[str, str] = {}
        for unit in manifest.get("units", []):
            for artifact in unit.get("source_artifacts", []):
                files[artifact["path"]] = artifact["sha256"]
        if len(files) != 221:
            raise RuntimeError("Manifesto Beta 4 não contém exatamente as entradas esperadas")
        pilot_path = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
        files[pilot_path] = "db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4"

        with tempfile.TemporaryDirectory(prefix=f"trilhacode-beta7-source-{self.run_id}-") as temp:
            destination_root = Path(temp)
            for relative, expected_hash in files.items():
                pure = PurePosixPath(relative)
                source_file = source_root.joinpath(*pure.parts)
                resolved = source_file.resolve(strict=True)
                if not resolved.is_relative_to(source_root) or source_file.is_symlink():
                    raise RuntimeError("Fonte contém caminho fora da origem aprovada")
                source_hash = hashlib.sha256(resolved.read_bytes()).hexdigest()
                if source_hash != expected_hash:
                    raise RuntimeError(f"Hash curricular divergente: {relative}")
                output = destination_root.joinpath(*pure.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(resolved, output)
                if hashlib.sha256(output.read_bytes()).hexdigest() != expected_hash:
                    raise RuntimeError(f"Cópia curricular divergiu: {relative}")
            try:
                subprocess.run(
                    ["docker", "exec", self.runner_id, "mkdir", "-p", "/workspace/beta7-source"],
                    check=True, capture_output=True, text=True, timeout=30,
                )
                subprocess.run(
                    ["docker", "cp", f"{destination_root}{os.sep}.",
                     f"{self.runner_id}:/workspace/beta7-source"],
                    check=True, capture_output=True, text=True, timeout=180,
                )
            except (OSError, subprocess.SubprocessError):
                raise RuntimeError("Não foi possível copiar a fonte Beta 7 para o runner próprio") from None
        return "/workspace/beta7-source"

    def seed_multiunit_fixture(self) -> dict[str, str]:
        if not self.gate_passed:
            raise RuntimeError("Fixture Beta 7 bloqueada antes do gate")
        result = self._exec(
            ["python", "test_support/beta7_seed_multiunit_fixture.py"],
            timeout=180,
            environment=self._run_env(),
            workdir="/workspace/backend",
        )
        if result.returncode != 0:
            raise RuntimeError("Fixture sintética multiunidade Beta 7 não foi criada")
        try:
            fixture = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            raise RuntimeError("Fixture Beta 7 não retornou identificadores válidos") from None
        required = {
            "track_id", "track_slug", "first_node_id", "second_node_id",
            "first_quiz_id", "second_quiz_id", "exercise_id",
        }
        if not isinstance(fixture, dict) or not required.issubset(fixture):
            raise RuntimeError("Fixture Beta 7 retornou contrato incompleto")
        return fixture

    def run_playwright(self, spec: str, fixture: dict[str, str]) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed:
            raise RuntimeError("Playwright Beta 7 bloqueado antes da aprovação do gate")
        if Path(spec).is_absolute() or ".." in Path(spec).parts or not spec.startswith("e2e/"):
            raise RuntimeError("Informe um spec Playwright relativo a frontend/e2e")
        fixture_env = {f"BETA7_E2E_{key.upper()}": value for key, value in fixture.items()}
        return self._exec(
            ["npx", "--prefix", "/workspace/frontend", "playwright", "test", spec],
            timeout=1200,
            environment={**self._run_env(), **fixture_env},
            workdir="/workspace/frontend",
        )

    def cleanup(self) -> None:
        """Recheck the complete owned boundary before removing any phase resource."""
        complete = all((self.network_id, self.mongo_id, self.runner_id, self.image_id))
        if complete and self.gate_passed:
            self.validate_gate()
        else:
            owned_container_ids = {item for item in (self.mongo_id, self.runner_id) if item}
            for resource_id, expected_name in (
                (self.mongo_id, self.mongo_name), (self.runner_id, self.runner_name),
            ):
                if not resource_id:
                    continue
                container = self._inspect_container(resource_id)
                labels = (container.get("Config") or {}).get("Labels") or {}
                if (container.get("Id", "").lower() != resource_id.lower()
                        or container.get("Name") != f"/{expected_name}"
                        or any(labels.get(key) != value for key, value in self.labels.items())):
                    raise Beta61HarnessError("Propriedade parcial Beta 7 não comprovada; recursos preservados")
                host = container.get("HostConfig") or {}
                if (container.get("Mounts") or host.get("PortBindings") or host.get("Binds")
                        or host.get("VolumesFrom")):
                    raise Beta61HarnessError("Container parcial fora do isolamento; recurso preservado")
                networks = (container.get("NetworkSettings") or {}).get("Networks") or {}
                if networks and (not self.network_id or set(networks) != {self.network_name}):
                    raise Beta61HarnessError("Container parcial conectado a rede não autorizada; preservado")
            if self.network_id:
                network = self._inspect_network()
                labels = network.get("Labels") or {}
                if (network.get("Id", "").lower() != self.network_id.lower()
                        or network.get("Name") != self.network_name
                        or network.get("Driver") != "bridge" or network.get("Internal") is not True
                        or any(labels.get(key) != value for key, value in self.labels.items())):
                    raise Beta61HarnessError("Propriedade parcial da rede Beta 7 não comprovada; preservada")
                members = set((network.get("Containers") or {}).keys())
                if not members.issubset(owned_container_ids):
                    raise Beta61HarnessError("Rede Beta 7 contém container não pertencente à execução; preservada")
        super().cleanup()
