"""Provision, execute and safely tear down the MongoDB 7 PoC homologation."""

from __future__ import annotations

import os
import re
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.errors import PyMongoError

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
COLLECTIONS = (
    "poc_editorial_generations",
    "poc_editorial_generation_chunks",
    "poc_editorial_generation_manifests",
    "poc_editorial_generation_heads",
)
FORBIDDEN_CONNECTION_ENV = (
    "MONGO_URL",
    "MONGO_URL_TEST",
    "DATABASE_URL",
    "EDITORIAL_POC_MONGO_URI",
)
RUN_ID_RE = re.compile(r"[a-f0-9]{32}\Z")
PROJECT_RE = re.compile(r"editorial-poc-[a-f0-9]{32}\Z")


class HarnessSafetyError(RuntimeError):
    """The target cannot be proven to be this execution's disposable server."""


def required_environment() -> tuple[str, str, str, str, str]:
    run_id = os.environ.get("EDITORIAL_POC_RUN_ID", "")
    project = os.environ.get("EDITORIAL_POC_PROJECT", "")
    host = os.environ.get("EDITORIAL_POC_MONGO_HOST", "")
    port = os.environ.get("EDITORIAL_POC_MONGO_PORT", "")
    username = os.environ.get("EDITORIAL_POC_ROOT_USERNAME", "")
    if os.environ.get("EDITORIAL_POC_DISPOSABLE") != "1":
        raise HarnessSafetyError("Ative o modo descartável somente pelo runner Compose")
    if not RUN_ID_RE.fullmatch(run_id) or project != f"editorial-poc-{run_id}":
        raise HarnessSafetyError("Identidade exclusiva de execução inválida")
    if not PROJECT_RE.fullmatch(project):
        raise HarnessSafetyError("Nome de projeto Compose não é exclusivo")
    if host != "mongo" or port != "27017":
        raise HarnessSafetyError(
            "Alvo recusado: o harness aceita apenas o serviço privado Mongo 'mongo'"
        )
    if not username or not os.environ.get("EDITORIAL_POC_ROOT_PASSWORD"):
        raise HarnessSafetyError("Credenciais efêmeras de provisionamento ausentes")
    if any(os.environ.get(key) for key in FORBIDDEN_CONNECTION_ENV):
        raise HarnessSafetyError(
            "Variável de conexão da aplicação encontrada; nenhuma será usada"
        )
    return run_id, project, host, port, username


def root_uri(host: str, port: str, username: str, password: str) -> str:
    return (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/admin"
        "?authSource=admin&directConnection=true&retryWrites=false"
        "&serverSelectionTimeoutMS=7000&connectTimeoutMS=7000"
    )


def _privilege(database_name: str, collection: str, actions: list[str]) -> dict:
    return {
        "resource": {"db": database_name, "collection": collection},
        "actions": actions,
    }


def _create_role(
    database, database_name: str, name: str, privileges: list[dict]
) -> None:
    database.command({"createRole": name, "privileges": privileges, "roles": []})


def _create_user(database, name: str, role: str) -> str:
    password = secrets.token_urlsafe(36)
    database.command(
        "createUser", name, pwd=password, roles=[{"role": role, "db": database.name}]
    )
    return password


def cleanup_database(
    client, database_name: str, run_id: str, project: str, marker: str
) -> None:
    """Drop only a database whose run, project and random marker all match."""
    database = client[database_name]
    identity = database["poc_harness_control"].find_one({"_id": "execution-identity"})
    if not identity:
        raise HarnessSafetyError("Marcador de propriedade ausente; limpeza recusada")
    if (
        identity.get("run_id") != run_id
        or identity.get("project") != project
        or not secrets.compare_digest(str(identity.get("marker", "")), marker)
        or identity.get("purpose") != "ephemeral-editorial-generation-homologation"
    ):
        raise HarnessSafetyError("Marcador de propriedade divergente; limpeza recusada")
    client.drop_database(database_name)
    if database_name in client.list_database_names():
        raise HarnessSafetyError("Banco efêmero permaneceu após a limpeza direcionada")


def provision(client, run_id: str, project: str) -> tuple[str, str, dict[str, str]]:
    database_name = f"editorial_poc_{run_id}"
    listed = client.admin.command("listDatabases", nameOnly=True)["databases"]
    if database_name in {row["name"] for row in listed}:
        raise HarnessSafetyError(
            "O banco exclusivo já existe; o harness recusou reutilizá-lo"
        )

    os.environ["EDITORIAL_POC_DB"] = database_name
    marker = secrets.token_urlsafe(48)
    database = client[database_name]
    database["poc_harness_control"].insert_one(
        {
            "_id": "execution-identity",
            "run_id": run_id,
            "project": project,
            "marker": marker,
            "purpose": "ephemeral-editorial-generation-homologation",
        }
    )
    try:
        # This harness provisions only the four PoC collections and its private
        # marker. It does not inspect or initialize application collections.
        sys.path.insert(0, str(BACKEND))
        from services.editorial_generations_poc import EditorialGenerationsPoC

        for collection_name, keys, options in EditorialGenerationsPoC.index_specs():
            database[collection_name].create_index(keys, **options)
        actual_indexes = {
            (collection_name, row["name"])
            for collection_name in COLLECTIONS
            for row in database[collection_name].list_indexes()
        }
        expected_indexes = {
            (collection_name, options["name"])
            for collection_name, _keys, options in EditorialGenerationsPoC.index_specs()
        }
        if actual_indexes & expected_indexes != expected_indexes:
            raise HarnessSafetyError("Índices PoC obrigatórios não foram criados")
        print(
            "Índices MongoDB verificados: "
            + ", ".join(
                sorted(name for _collection, name in expected_indexes),
            )
        )
        for collection_name, keys, options in EditorialGenerationsPoC.index_specs():
            if options.get("unique"):
                actual = next(
                    row
                    for row in database[collection_name].list_indexes()
                    if row["name"] == options["name"]
                )
                if actual.get("unique") is not True or tuple(
                    actual["key"].items()
                ) != tuple(keys):
                    raise HarnessSafetyError(
                        f"Índice único divergente: {options['name']}"
                    )

        _create_role(
            database,
            database_name,
            "poc_append_only",
            [
                _privilege(
                    database_name, "poc_editorial_generation_chunks", ["find", "insert"]
                ),
                _privilege(
                    database_name,
                    "poc_editorial_generation_manifests",
                    ["find", "insert"],
                ),
            ],
        )
        _create_role(
            database,
            database_name,
            "poc_builder",
            [
                _privilege(
                    database_name,
                    "poc_editorial_generations",
                    ["find", "insert", "update"],
                ),
                _privilege(
                    database_name,
                    "poc_editorial_generation_heads",
                    ["find", "insert", "update"],
                ),
            ],
        )
        _create_role(
            database,
            database_name,
            "poc_reader",
            [
                _privilege(database_name, collection, ["find"])
                for collection in COLLECTIONS
            ],
        )
        # Fixture privileges are confined to the unique scratch database and
        # are used only to simulate administrator-side corruption.
        _create_role(
            database,
            database_name,
            "poc_fixture_admin",
            [
                _privilege(
                    database_name, collection, ["find", "insert", "update", "remove"]
                )
                for collection in COLLECTIONS
            ],
        )
        credentials = {
            "EDITORIAL_POC_BUILDER_PASSWORD": _create_user(
                database, "poc_builder", "poc_builder"
            ),
            "EDITORIAL_POC_APPEND_PASSWORD": _create_user(
                database, "poc_append", "poc_append_only"
            ),
            "EDITORIAL_POC_READER_PASSWORD": _create_user(
                database, "poc_reader", "poc_reader"
            ),
            "EDITORIAL_POC_FIXTURE_PASSWORD": _create_user(
                database, "poc_fixture", "poc_fixture_admin"
            ),
        }
        credentials.update(
            {
                "EDITORIAL_POC_BUILDER_USER": "poc_builder",
                "EDITORIAL_POC_APPEND_USER": "poc_append",
                "EDITORIAL_POC_READER_USER": "poc_reader",
                "EDITORIAL_POC_FIXTURE_USER": "poc_fixture",
            }
        )
        return database_name, marker, credentials
    except Exception:
        cleanup_database(client, database_name, run_id, project, marker)
        raise


def run_suite(environment: dict[str, str]) -> int:
    commands = (
        [
            sys.executable,
            "-m",
            "unittest",
            "unit_tests.test_editorial_generations_poc",
            "-v",
        ],
        [
            sys.executable,
            "-m",
            "unittest",
            "integration_tests.test_editorial_generations_mongodb",
            "-v",
        ],
    )
    for command in commands:
        result = subprocess.run(command, cwd=BACKEND, env=environment, check=False)
        if result.returncode:
            return result.returncode
    return 0


def main() -> int:
    client = None
    database_name = ""
    marker = ""
    run_id = project = host = port = ""
    exit_code = 1
    try:
        run_id, project, host, port, username = required_environment()
        password = os.environ["EDITORIAL_POC_ROOT_PASSWORD"]
        client = MongoClient(root_uri(host, port, username, password))
        build_info = client.admin.command("buildInfo")
        version = build_info.get("version", "")
        hello = client.admin.command("hello")
        if not version.startswith("7."):
            raise HarnessSafetyError(
                f"Era esperado MongoDB 7; servidor reportou major {version.split('.')[0]}",
            )
        if "setName" in hello or hello.get("msg") == "isdbgrid":
            raise HarnessSafetyError(
                "Era esperado MongoDB standalone, sem replica set ou mongos"
            )
        print(
            f"Runtime: Python {sys.version.split()[0]}; "
            f"PyMongo {__import__('pymongo').version}; MongoDB {version}",
        )
        print(
            f"Topologia: standalone; projeto descartável {project}; banco exclusivo em memória."
        )
        database_name, marker, credentials = provision(client, run_id, project)

        child_environment = {
            key: os.environ[key]
            for key in ("PATH", "HOME", "TMPDIR", "TEMP", "TMP")
            if os.environ.get(key)
        }
        child_environment.update(
            {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            }
        )
        child_environment.update(credentials)
        child_environment.update(
            {
                "EDITORIAL_POC_RUN_ID": run_id,
                "EDITORIAL_POC_PROJECT": project,
                "EDITORIAL_POC_DB": database_name,
                "EDITORIAL_POC_MONGO_HOST": host,
                "EDITORIAL_POC_MONGO_PORT": port,
                "EDITORIAL_POC_DISPOSABLE": "1",
                "EDITORIAL_POC_MARKER_VERIFIED": "1",
            }
        )
        exit_code = run_suite(child_environment)
    except (HarnessSafetyError, PyMongoError) as exc:
        print(f"Harness bloqueado: {type(exc).__name__}: {exc}", file=sys.stderr)
        exit_code = 2
    finally:
        if client is not None:
            if database_name and marker:
                try:
                    cleanup_database(client, database_name, run_id, project, marker)
                    print(
                        "Limpeza: banco efêmero removido após validar o marcador desta execução."
                    )
                except (HarnessSafetyError, PyMongoError) as exc:
                    print(
                        f"Limpeza recusada/falhou: {type(exc).__name__}: {exc}",
                        file=sys.stderr,
                    )
                    if exit_code == 0:
                        exit_code = 3
            client.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
