"""Beta 7.1-owned internal Docker runner with MongoDB replica-set support."""

from __future__ import annotations

import json
import secrets
import subprocess
from pathlib import Path

from test_support.beta6_1_docker_harness import Beta61HarnessError, local_readiness_probe
from test_support.beta7_docker_harness import Beta7DockerHarness


class Beta71DockerHarness(Beta7DockerHarness):
    """Reuses Beta 7's reviewed ownership checks with a distinct phase identity."""

    def __init__(self, repo_root: Path) -> None:
        super().__init__(repo_root)
        self.phase = "beta7-1"
        self.network_name = f"tc-beta7-1-{self.suffix}"
        self.mongo_name = f"tc-beta7-1-mongo-{self.suffix}"
        self.runner_name = f"tc-beta7-1-runner-{self.suffix}"
        self.mongo_user = f"beta7_1_{self.run_id[:10]}"
        self.database = f"beta7_1_{self.run_id}"
        self.mongo_uri = (
            f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_name}:27017/{self.database}"
            "?authSource=admin&replicaSet=rs0"
        )
        self.image_tag = f"tc-beta7-1-e2e:{self.suffix}"
        # MongoDB key files accept a restricted character set. Hex keeps the
        # per-run secret within that format while remaining unguessable.
        self.mongo_replica_key = secrets.token_hex(64)
        self.mongo_environment = {"MONGO_REPLICA_SET_KEY": self.mongo_replica_key}
        self.mongo_command = (
            "sh", "-c",
            "printf '%s' \"$MONGO_REPLICA_SET_KEY\" > /data/configdb/beta7-1-rs-key "
            "&& chown mongodb:mongodb /data/configdb/beta7-1-rs-key "
            "&& chmod 400 /data/configdb/beta7-1-rs-key "
            "&& exec docker-entrypoint.sh mongod --replSet rs0 --bind_ip_all "
            "--keyFile /data/configdb/beta7-1-rs-key",
        )
        self.labels = {
            "io.trilhacode.phase": "beta7-1",
            "io.trilhacode.run-id": self.run_id,
            "io.trilhacode.owner-token": self.owner_token,
        }
        self.student_password = secrets.token_urlsafe(24)
        self.reviewer_password = secrets.token_urlsafe(24)
        self.unscoped_password = secrets.token_urlsafe(24)
        self.admin_password = secrets.token_urlsafe(24)

    def _run_env(self) -> dict[str, str]:
        if (self.mongo_id is None or self.network_id is None or self.runner_id is None
                or self.gate_proof is None or not self.gate_passed):
            raise Beta61HarnessError("Gate Beta 7.1 ainda não aprovado")
        return {
            "BETA7_1_TEST_ISOLATION_GATE": f"beta7-1:{self.gate_proof}",
            "BETA7_1_TEST_MONGO_URI": self.mongo_uri,
            "BETA7_1_TEST_MONGO_DATABASE": self.database,
            "BETA7_1_TEST_RUN_ID": self.run_id,
            "BETA7_1_TEST_OWNER_TOKEN": self.owner_token,
            "BETA7_1_TEST_CONTAINER_ID": self.mongo_id,
            "BETA7_1_TEST_NETWORK_ID": self.network_id,
            "BETA7_1_TEST_RUNNER_ID": self.runner_id,
            "BETA7_1_TEST_MONGO_HOST": self.mongo_name,
            "BETA7_1_TEST_NETWORK_NAME": self.network_name,
            "BETA7_1_TEST_RUNNER_NAME": self.runner_name,
        }

    def __enter__(self) -> "Beta71DockerHarness":
        super().__enter__()
        try:
            import time

            readiness_deadline = time.monotonic() + 120
            while time.monotonic() < readiness_deadline:
                try:
                    self._docker([
                        "exec", self.mongo_id, "mongosh", "--quiet",
                        "--username", self.mongo_user, "--password", self.mongo_password,
                        "--authenticationDatabase", "admin", "--eval",
                        "if (db.adminCommand('ping').ok !== 1) quit(2)",
                    ], timeout=10)
                    break
                except Beta61HarnessError:
                    time.sleep(0.5)
            else:
                diagnostic = ""
                try:
                    logs = self._docker(["logs", "--tail", "60", self.mongo_id], timeout=15)
                    relevant = [
                        line for line in logs.splitlines()
                        if any(word in line.casefold() for word in ("fatal", "error", "keyfile", "failed", "exception"))
                    ]
                    diagnostic = " | ".join(relevant)[-1800:]
                    for secret in (self.mongo_uri, self.mongo_password, self.owner_token, self.mongo_replica_key):
                        diagnostic = diagnostic.replace(secret, "[redacted]")
                except Beta61HarnessError:
                    diagnostic = "logs indisponíveis"
                raise Beta61HarnessError(
                    "MongoDB descartável não aceitou ping após 120 segundos. "
                    f"Diagnóstico sanitizado: {diagnostic or 'sem mensagem fatal disponível'}"
                )

            self._docker([
                "exec", self.mongo_id, "mongosh", "--quiet",
                "--username", self.mongo_user, "--password", self.mongo_password,
                "--authenticationDatabase", "admin", "--eval",
                f"rs.initiate({{_id:'rs0',members:[{{_id:0,host:'{self.mongo_name}:27017'}}]}})",
            ], timeout=90)
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                try:
                    self._docker([
                        "exec", self.mongo_id, "mongosh", "--quiet",
                        "--username", self.mongo_user, "--password", self.mongo_password,
                        "--authenticationDatabase", "admin", "--eval",
                        "if (db.hello().setName !== 'rs0' || !db.hello().isWritablePrimary) quit(2)",
                    ], timeout=10)
                    break
                except Beta61HarnessError:
                    time.sleep(0.5)
            else:
                raise Beta61HarnessError("Replica set MongoDB Beta 7.1 não ficou pronto")
            self.validate_gate()
            return self
        except Exception:
            self.cleanup()
            raise

    def start_local_app(self, fixture: dict[str, object]) -> None:
        if not self.gate_passed:
            raise Beta61HarnessError("Inicialização bloqueada antes do gate Beta 7.1")
        api = self._exec(
            ["sh", "-c", "exec python -m uvicorn test_support.beta7_1_preview_server:app "
             "--host 127.0.0.1 --port 18000 > /tmp/beta7-1-api.log 2>&1"],
            timeout=20, detach=True, environment=self._run_env(), workdir="/workspace/backend",
        )
        if api.returncode != 0:
            raise Beta61HarnessError("Não foi possível iniciar a API de prévia Beta 7.1")
        web = self._exec(
            ["sh", "-c", "exec npm run start -- --mode beta7-1-preview --host 127.0.0.1 "
             "--port 3000 --strictPort > /tmp/beta7-1-web.log 2>&1"],
            timeout=20, detach=True,
            environment={"VITE_BETA7_1_PREVIEW_BATCH_ID": str(fixture["batch_id"])},
            workdir="/workspace/frontend",
        )
        if web.returncode != 0:
            raise Beta61HarnessError("Não foi possível iniciar o frontend de prévia Beta 7.1")
        ready = self._exec(["python", "-c", local_readiness_probe()], timeout=75)
        if ready.returncode != 0:
            logs = self._exec([
                "sh", "-c", "for file in /tmp/beta7-1-api.log /tmp/beta7-1-web.log; do "
                "if [ -f \"$file\" ]; then tail -n 25 \"$file\"; fi; done",
            ], timeout=10)
            diagnostic = logs.stdout[-2500:] if logs.returncode == 0 else ""
            for secret in (self.mongo_uri, self.mongo_password, self.jwt_secret, self.owner_token):
                diagnostic = diagnostic.replace(secret, "[redacted]")
            raise Beta61HarnessError(
                "Serviços de prévia Beta 7.1 não ficaram prontos. "
                f"Diagnóstico sanitizado: {diagnostic or 'logs indisponíveis'}"
            )
        preview_probe = self._exec(
            [
                "python", "-c",
                "import json,re,sys,urllib.request; "
                "source=urllib.request.urlopen('http://127.0.0.1:3000/src/App.tsx',timeout=5).read().decode(); "
                "match=re.search(r'const beta71PreviewEnabled\\s*=\\s*(.*?);',source,re.S); "
                "expression=(match.group(1) if match else 'missing').replace(sys.argv[1],'[batch]'); "
                "mode='import.meta.env.MODE' in expression and 'beta7-1-preview' in expression; "
                "batch=('import.meta.env.VITE_BETA7_1_PREVIEW_BATCH_ID' in expression and sys.argv[1] in source); "
                "route='/beta7-1-preview' in source; "
                "print(json.dumps({'mode_enabled':mode,'batch_enabled':batch,'route_present':route,'expression':expression})); "
                "sys.exit(0 if mode and batch and route else 3)",
                str(fixture["batch_id"]),
            ],
            timeout=10,
        )
        if preview_probe.returncode != 0:
            raise Beta61HarnessError(
                "A rota de prévia não foi habilitada pela configuração Vite restrita: "
                f"{preview_probe.stdout.strip() or 'transformação indisponível'}"
            )

    def run_http_validation(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed:
            raise Beta61HarnessError("Validação HTTP bloqueada antes do gate Beta 7.1")
        environment = {
            **self._run_env(),
            "BETA7_1_E2E_BATCH_ID": str(fixture["batch_id"]),
            "BETA7_1_E2E_PRIVATE_TRACK_ID": str(fixture["private_track_id"]),
            "BETA7_1_STUDENT_PASSWORD": self.student_password,
            "BETA7_1_REVIEWER_PASSWORD": self.reviewer_password,
            "BETA7_1_UNSCOPED_PASSWORD": self.unscoped_password,
        }
        result = self._exec(
            ["python", "test_support/beta7_1_http_validation.py"],
            timeout=180, environment=environment, workdir="/workspace/backend",
        )
        if result.returncode:
            logs = self._exec(
                ["sh", "-c", "tail -n 80 /tmp/beta7-1-api.log"],
                timeout=10, environment=self._run_env(), workdir="/workspace/backend",
            )
            diagnostic = logs.stdout if logs.returncode == 0 else ""
            for secret in (
                self.mongo_uri, self.mongo_password, self.jwt_secret, self.owner_token,
                self.student_password, self.reviewer_password, self.unscoped_password, self.admin_password,
            ):
                if secret:
                    diagnostic = diagnostic.replace(secret, "[redacted]")
            result.stderr = (result.stderr or "") + "\nAPI_LOG_SANITIZED\n" + diagnostic[-6000:]
        return result

    def run_revocation_race(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed:
            raise Beta61HarnessError("Prova de revogação bloqueada antes do gate Beta 7.1")
        return self._exec(
            ["python", "test_support/beta7_1_revocation_race.py"],
            timeout=180,
            environment={**self._run_env(), "BETA7_1_E2E_BATCH_ID": str(fixture["batch_id"])},
            workdir="/workspace/backend",
        )

    def seed_real_curriculum(self, curriculum_root: str) -> dict[str, object]:
        if not self.gate_passed:
            raise Beta61HarnessError("Preparação curricular bloqueada antes do gate Beta 7.1")
        environment = {
            **self._run_env(),
            "TRILHACODE_BETA7_1_SOURCE_ROOT": curriculum_root,
            "BETA7_1_ADMIN_PASSWORD": self.admin_password,
            "BETA7_1_STUDENT_PASSWORD": self.student_password,
            "BETA7_1_REVIEWER_PASSWORD": self.reviewer_password,
            "BETA7_1_UNSCOPED_PASSWORD": self.unscoped_password,
        }
        result = self._exec(
            ["python", "test_support/beta7_1_seed_preview.py"],
            timeout=600, environment=environment, workdir="/workspace/backend",
        )
        if result.returncode != 0:
            raise Beta61HarnessError("Fonte curricular ou lote Beta 7.1 não pôde ser preparado")
        import json

        try:
            fixture = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError) as exc:
            raise Beta61HarnessError("Preparação Beta 7.1 não retornou evidência válida") from exc
        if not isinstance(fixture, dict) or not {"batch_id", "private_track_id", "counts"}.issubset(fixture):
            raise Beta61HarnessError("Contrato de preparação Beta 7.1 incompleto")
        return fixture

    def run_playwright(self, spec: str, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        if not self.gate_passed or Path(spec).is_absolute() or ".." in Path(spec).parts:
            raise Beta61HarnessError("Playwright Beta 7.1 bloqueado ou spec inválido")
        environment = {
            **self._run_env(),
            "BETA7_1_E2E_BATCH_ID": str(fixture["batch_id"]),
            "BETA7_1_E2E_PRIVATE_TRACK_ID": str(fixture["private_track_id"]),
            "E2E_STUDENT_EMAIL": "beta7-1-student@example.com",
            "E2E_STUDENT_PASSWORD": self.student_password,
            "E2E_REVIEWER_EMAIL": "beta7-1-reviewer@example.com",
            "E2E_REVIEWER_PASSWORD": self.reviewer_password,
            "E2E_UNSCOPED_EMAIL": "beta7-1-unscoped@example.com",
            "E2E_UNSCOPED_PASSWORD": self.unscoped_password,
        }
        result = self._exec(
            ["npx", "playwright", "test", spec],
            timeout=1200, environment=environment, workdir="/workspace/frontend",
        )
        if result.returncode:
            diagnostics = self._exec(
                ["sh", "-c", "find test-results -type f -name browser-diagnostics.json "
                 "-exec cat {} \\;"],
                timeout=10, environment=self._run_env(), workdir="/workspace/frontend",
            )
            # The Playwright fixture records only status codes and URL paths,
            # never cookies, request bodies, or form values.
            result.stdout = (result.stdout or "") + "\nBROWSER_DIAGNOSTICS\n" + diagnostics.stdout[-5000:]
            api_paths = self._exec(
                [
                    "python", "-c",
                    "import pathlib,re; text=pathlib.Path('/tmp/beta7-1-api.log').read_text(errors='replace'); "
                    "rows=re.findall(r'\\\"(GET|POST|PUT|DELETE) (/api/[A-Za-z0-9_./{}-]+) HTTP/[0-9.]+\\\" ([0-9]{3})',text); "
                    "print('\\n'.join(f'{method} {path} {status}' for method,path,status in rows[-40:]))",
                ],
                timeout=10, environment=self._run_env(), workdir="/workspace/backend",
            )
            if api_paths.returncode == 0:
                result.stdout += "\nAPI_ACCESS_PATHS\n" + api_paths.stdout[-3000:]
        return result

    def cleanup(self) -> None:
        """Remove only resources whose exact IDs, labels, mounts, and network still match."""
        container_rows: list[tuple[str, str, dict]] = []
        owned_ids = {item for item in (self.mongo_id, self.runner_id) if item}
        network = None
        if self.network_id:
            network = self._inspect_network()
            if (network.get("Id", "").lower() != self.network_id.lower()
                    or network.get("Name") != self.network_name
                    or network.get("Driver") != "bridge" or network.get("Internal") is not True
                    or any((network.get("Labels") or {}).get(key) != value
                           for key, value in self.labels.items())):
                raise Beta61HarnessError("Propriedade da rede Beta 7.1 não comprovada; recurso preservado")
            members = set((network.get("Containers") or {}).keys())
            if not members.issubset(owned_ids):
                raise Beta61HarnessError("Rede Beta 7.1 contém container alheio; recurso preservado")

        for resource_id, name, kind in (
            (self.runner_id, self.runner_name, "runner"),
            (self.mongo_id, self.mongo_name, "mongo"),
        ):
            if not resource_id:
                continue
            row = self._inspect_container(resource_id)
            host = row.get("HostConfig") or {}
            networks = (row.get("NetworkSettings") or {}).get("Networks") or {}
            expected_tmpfs = {"/tmp"} if kind == "runner" else {"/data/db", "/data/configdb"}
            config = row.get("Config") or {}
            if (row.get("Id", "").lower() != resource_id.lower()
                    or row.get("Name") != f"/{name}"
                    or any((config.get("Labels") or {}).get(key) != value
                           for key, value in self.labels.items())
                    or row.get("Mounts") or host.get("PortBindings") or host.get("Binds")
                    or host.get("VolumesFrom")
                    or set(host.get("Tmpfs") or {}) != expected_tmpfs
                    or set(networks) != {self.network_name}):
                raise Beta61HarnessError("Container Beta 7.1 não pertence integralmente à execução; preservado")
            if kind == "mongo":
                configured = set(config.get("Env") or [])
                if (config.get("Image") != "mongo:7.0.43"
                        or list(config.get("Cmd") or []) != list(self.mongo_command)
                        or f"MONGO_INITDB_ROOT_USERNAME={self.mongo_user}" not in configured
                        or f"MONGO_INITDB_ROOT_PASSWORD={self.mongo_password}" not in configured
                        or f"MONGO_REPLICA_SET_KEY={self.mongo_replica_key}" not in configured):
                    raise Beta61HarnessError("Configuração do MongoDB Beta 7.1 divergiu; container preservado")
            elif row.get("Image") != self.image_id:
                raise Beta61HarnessError("Imagem do runner Beta 7.1 divergiu; container preservado")
            container_rows.append((resource_id, name, row))

        if network:
            members = set((network.get("Containers") or {}).keys())
            if any((row.get("State") or {}).get("Running") and resource_id not in members
                   for resource_id, _name, row in container_rows):
                raise Beta61HarnessError("Container ativo fora da rede Beta 7.1; recursos preservados")

        # Ownership and absence of external mounts were rechecked above. Stop
        # and remove only these exact container IDs, even if Mongo exited early.
        for resource_id, _name, _row in container_rows:
            self._docker(["rm", "--force", resource_id])
        if self.network_id:
            self._docker(["network", "rm", self.network_id])
        if self.image_id:
            images = json.loads(self._docker(["image", "inspect", self.image_id]))
            if (len(images) != 1 or images[0].get("Id") != self.image_id
                    or (images[0].get("Config") or {}).get("Labels") != self.labels):
                raise Beta61HarnessError("Imagem Beta 7.1 divergiu; preservada")
            self._docker(["image", "rm", self.image_id])
        self.mongo_id = None
        self.runner_id = None
        self.network_id = None
        self.image_id = None
        self.gate_passed = False
