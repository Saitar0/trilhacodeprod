"""Disposable provisioner and HTTP proof for separate Beta 8.3 processes.

Run only through ops/beta8-3-security/run-local.ps1. The script requires the
host-side ownership gate before opening any MongoDB connection or writing.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import secrets
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import jwt
from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure
from pymongo.uri_parser import parse_uri

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

TRACK_ID = "beta8-track-synthetic-runtime"
PASSWORD = "Synthetic-only-password-483!"
JWT_SECRET = os.environ.get("BETA8_3_JWT_SECRET", "")


def _env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"configuração Beta 8.3 ausente: {name}")
    return value


def _gate() -> tuple[str, str, str]:
    if (
        os.environ.get("BETA8_3_DISPOSABLE") != "1"
        or os.environ.get("BETA8_3_DOCKER_PRECHECKED") != "true"
        or not re.fullmatch(r"[0-9a-f]{32}", os.environ.get("BETA8_3_RUN_ID", ""))
        or not re.fullmatch(r"[0-9a-f]{64}", os.environ.get("BETA8_3_DOCKER_CONTAINER_ID", ""))
        or not re.fullmatch(r"[0-9a-f]{64}", os.environ.get("BETA8_3_DOCKER_NETWORK_ID", ""))
    ):
        raise RuntimeError("gate de propriedade Beta 8.3 ausente; operação persistente bloqueada")
    run_id = _env("BETA8_3_RUN_ID")
    database = _env("BETA8_3_DB_NAME")
    if database != f"editorial_revision_test_c10_c11_c12_b83_{run_id[:12]}":
        raise RuntimeError("identidade do banco descartável diverge do gate")
    uri = _env("BETA8_3_ROOT_URI")
    parsed = parse_uri(uri)
    if (
        parsed.get("nodelist") != [("mongo", 27017)]
        or parsed.get("database") != "admin"
        or parsed.get("username") != "beta8-root"
        or parsed.get("options", {}).get("replicaSet") != "rsB83"
    ):
        raise RuntimeError("URI do provisionador não aponta exclusivamente para MongoDB Beta 8.3")
    return run_id, database, uri


def _privilege(db_name: str, collection: str, actions: list[str]) -> dict[str, Any]:
    return {"resource": {"db": db_name, "collection": collection}, "actions": actions}


async def _create_role(database: Any, role: str, privileges: list[dict[str, Any]]) -> None:
    await database.command({
        "createRole": role,
        "privileges": privileges,
        "roles": [],
    })


async def _create_user(database: Any, username: str, password: str, role: str) -> None:
    await database.command({
        "createUser": username,
        "pwd": password,
        "roles": [{"role": role, "db": database.name}],
    })


def _uri(username: str, password: str, database: str) -> str:
    return (
        f"mongodb://{username}:{password}@mongo:27017/{database}"
        f"?authSource={database}&replicaSet=rsB83&serverSelectionTimeoutMS=8000"
        "&connectTimeoutMS=8000"
    )


async def _provision() -> None:
    run_id, db_name, root_uri = _gate()
    stage_run = _env("BETA8_3_STAGE_RUN_ID")
    if not re.fullmatch(r"[0-9a-f]{32}", stage_run):
        raise RuntimeError("identidade do staging Beta 5 inválida")
    stage_name = f"beta5_{stage_run}"
    root = AsyncMongoClient(root_uri, appname="beta8-3-provisioner", tz_aware=True)
    try:
        await _wait_for_primary(root)
        hello = await root.admin.command({"hello": 1})
        server = await root.server_info()
        if not str(server.get("version", "")).startswith("7.") or hello.get("setName") != "rsB83":
            raise RuntimeError("topologia MongoDB Beta 8.3 não corresponde ao contrato")
        existing = set(await root.list_database_names())
        if db_name in existing or stage_name in existing:
            raise RuntimeError("banco descartável já existe; reutilização recusada")

        database = root[db_name]
        await database["_beta8_3_harness_identity"].insert_one({
            "_id": "owner", "phase": "beta8-3", "run_id": run_id,
            "marker": secrets.token_urlsafe(32), "purpose": "process-isolation-proof",
        })
        api_password = _env("BETA8_3_API_PASSWORD")
        authority_password = _env("BETA8_3_AUTHORITY_PASSWORD")
        authority_privileges: list[dict[str, Any]] = []
        for collection, actions in {
            "c8_beta8_1_tracks": ["find", "insert", "update", "createIndex"],
            "c8_beta8_1_operations": ["find", "insert", "update", "createIndex"],
            "c8_beta8_1_history": ["find", "insert", "createIndex"],
            "c8_beta8_1_writers": ["find", "insert", "update", "createIndex"],
            "c8_beta8_1_authorities": ["find", "insert", "update", "createIndex"],
            "c12_iam_principals": ["find", "insert", "update"],
            "c12_iam_sessions": ["find", "insert", "update"],
            "c12_track_grants": ["find", "insert", "update"],
            "nodes": ["find", "update"],
            "content_blocks": ["find", "insert", "update"],
            "_beta8_editorial_audit": ["insert"],
            "_beta8_authorization_audit": ["insert"],
            "_beta8_3_rpc_nonces": ["insert", "createIndex"],
            "_beta8_experimental_heads": ["find", "insert", "update"],
            "_beta8_experimental_generations": ["find", "insert"],
            "_beta8_promotion_audit": ["insert"],
            "users": ["find", "update"],
            "auth_sessions": ["find", "update"],
        }.items():
            authority_privileges.append(_privilege(db_name, collection, actions))
        if os.environ.get("BETA8_4_TEST_BARRIERS") == "1":
            # Test-only persistent interlock; only the authority can poll it.
            authority_privileges.append(_privilege(
                db_name, "_beta8_4_test_barriers", ["find", "update"],
            ))
        await _create_role(database, "beta8_3_authority", authority_privileges)
        await _create_role(database, "beta8_3_api", [
            _privilege(db_name, "users", ["find"]),
            _privilege(db_name, "auth_sessions", ["find", "insert", "update"]),
            _privilege(db_name, "login_attempts", ["find", "insert", "update", "remove"]),
            _privilege(db_name, "content_blocks", ["find"]),
            _privilege(db_name, "nodes", ["find"]),
            _privilege(db_name, "block_types", ["find"]),
            _privilege(db_name, "tracks", ["find"]),
            _privilege(db_name, "migrations", ["find"]),
        ])
        await _create_user(database, "beta8-3-api", api_password, "beta8_3_api")
        await _create_user(database, "beta8-3-authority", authority_password, "beta8_3_authority")

        await database.migrations.insert_many([
            {"key": "0001_legacy_snapshots", "version": 1, "applied_at": datetime.now(UTC)},
            {"key": "0002_block_submission_capabilities", "version": 2, "applied_at": datetime.now(UTC)},
        ])
        await database.block_types.insert_one({"key": "text", "label": "Texto"})
        node_id = ObjectId(_env("BETA8_3_NODE_ID"))
        block_id = ObjectId(_env("BETA8_3_BLOCK_ID"))
        await database.nodes.insert_one({
            "_id": node_id,
            "track_id": TRACK_ID,
            "parent_id": None,
            "kind": "lesson",
            "title": "Unidade sintética Beta 8.3",
            "summary": "",
            "description": "",
            "guidance": "",
            "slug": "unidade-sintetica-beta-8-3",
            "status": "draft",
            "editorial_state": "draft",
            "editorial_revision": 0,
            "order": 0,
        })
        await database.content_blocks.insert_one({
            "_id": block_id,
            "track_id": TRACK_ID,
            "node_id": str(node_id),
            "type": "text",
            "title": "Bloco sintético original",
            "data": {"text": "Conteúdo sintético"},
            "status": "draft",
            "editorial_state": "draft",
            "editorial_revision": 0,
            "schema_version": 1,
            "order": 0,
        })
        await _seed_user(database, _env("BETA8_3_EDITOR_ID"), _env("BETA8_3_EDITOR_EMAIL"), "editor")
        await _seed_user(database, _env("BETA8_3_NO_GRANT_ID"), _env("BETA8_3_NO_GRANT_EMAIL"), "editor")
        await _seed_user(database, _env("BETA8_3_ADMIN_ID"), _env("BETA8_3_ADMIN_EMAIL"), "admin")
        for collection, document in _learning_sentinels(
            run_id, _env("BETA8_3_EDITOR_ID"), str(node_id),
        ).items():
            await database[collection].insert_one(document)

        stage = root[stage_name]
        owner_token = _env("BETA8_3_STAGE_OWNER_TOKEN")
        await stage["_beta5_test_owner"].insert_one({
            "_id": "owner", "run_id": stage_run, "owner_token": owner_token,
            "database": stage_name,
        })
        await _create_role(stage, "beta8_3_stager", [
            _privilege(stage_name, "_beta5_test_owner", ["find"]),
            _privilege(stage_name, "_beta5_staging_batches", ["find", "insert", "update", "createIndex"]),
            _privilege(stage_name, "_beta5_staging_records", ["find", "insert", "createIndex"]),
            _privilege(stage_name, "_beta5_staging_checkpoints", ["find", "insert", "update", "createIndex"]),
            _privilege(stage_name, "_beta5_staging_events", ["find", "insert", "update", "createIndex"]),
        ])
        await _create_role(stage, "beta8_3_stage_reader", [
            _privilege(stage_name, "_beta5_test_owner", ["find"]),
            _privilege(stage_name, "_beta5_staging_batches", ["find"]),
            _privilege(stage_name, "_beta5_staging_records", ["find"]),
            _privilege(stage_name, "_beta5_staging_checkpoints", ["find"]),
            _privilege(stage_name, "_beta5_staging_events", ["find"]),
        ])
        await _create_user(stage, "beta8-3-stager", _env("BETA8_3_STAGE_WRITE_PASSWORD"), "beta8_3_stager")
        await _create_user(stage, "beta8-3-stage-reader", _env("BETA8_3_STAGE_READ_PASSWORD"), "beta8_3_stage_reader")
        print("BETA8_3_PROVISION: PASS; users and roles created only in the gated disposable databases")
    finally:
        await root.close()


async def _seed_user(database: Any, user_id: str, email: str, role: str) -> None:
    from security import hash_password

    await database.users.insert_one({
        "_id": ObjectId(user_id),
        "email": email,
        "name": "Synthetic Beta 8.3 user",
        "password_hash": hash_password(PASSWORD),
        "role": role,
        "profile": {"bio": "", "goals": "", "preferences": {}},
        "email_verified": True,
        "is_active": True,
        "token_version": 0,
    })


async def _wait_for_primary(client: AsyncMongoClient) -> None:
    for _ in range(40):
        try:
            hello = await client.admin.command({"hello": 1})
            if hello.get("isWritablePrimary") or hello.get("ismaster"):
                return
        except Exception:
            await asyncio.sleep(0.5)
    raise RuntimeError("MongoDB descartável não elegeu primary")


async def _provision_c12(root_db: Any, actor_id: str, session_id: str, *, grant_track: str | None) -> None:
    from curriculum_contract.experimental_editorial_grants import EditorialTrackGrant
    from curriculum_contract.experimental_editorial_iam_authority import MongoEditorialIAMAuthority

    iam = MongoEditorialIAMAuthority(root_db, capability_key=secrets.token_bytes(32))
    await iam.provision_principal(actor_id=actor_id, role="editor")
    session_doc = await root_db.auth_sessions.find_one({"_id": _session_digest(session_id)})
    if session_doc is None:
        raise AssertionError("sessão do login real não foi persistida")
    await iam.provision_session(
        actor_id=actor_id,
        session_id=session_id,
        expires_at=session_doc["expires_at"].replace(tzinfo=UTC)
        if session_doc["expires_at"].tzinfo is None else session_doc["expires_at"],
    )
    if grant_track:
        await iam.provision_grant(EditorialTrackGrant(
            actor_id=actor_id,
            track_id=grant_track,
            allowed_operations=("block.create", "block.update", "content.publish", "node.update"),
            granted_by="beta8-3-synthetic-grantor",
            granted_at=datetime.now(UTC),
        ))


def _session_digest(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def _learning_sentinels(run_id: str, actor_id: str, node_id: str) -> dict[str, dict[str, Any]]:
    """Records that editorial operations must leave byte-for-byte unchanged."""

    return {
        "attempts": {
            "_id": f"beta8-3-attempt-{run_id}",
            "user_id": actor_id,
            "activity_id": "synthetic-quiz-v1",
            "answers": [{"question_id": "q1", "answer_id": "a2"}],
            "state": "submitted",
        },
        "submissions": {
            "_id": f"beta8-3-submission-{run_id}",
            "student_id": actor_id,
            "track_id": TRACK_ID,
            "node_id": node_id,
            "exercise_id": "synthetic-exercise-v1",
            "state": "revision_required",
            "feedback": "Registro sintético preservado",
        },
        "progress": {
            "_id": f"beta8-3-progress-{run_id}",
            "user_id": actor_id,
            "track_id": TRACK_ID,
            "node_id": node_id,
            "state": "in_progress",
            "version": 3,
        },
    }


def _stage_package(title: str = "Unidade sintética staged"):
    from curriculum_contract.beta_staging_contract import (
        StagedRecord,
        StagedRecordKind,
        StagingManifest,
        StagingPackage,
        _package_content_hash,
    )

    records = (StagedRecord(
        record_id="synthetic-unit-1",
        kind=StagedRecordKind.UNIT,
        student_public={"unit_id": "synthetic-unit-1", "title": title},
        system_internal={
            "source_revision": "synthetic:beta8-1:revision-1",
            "source_path": "synthetic://beta8-1/unit",
            "source_sha256": "a" * 64,
        },
    ),)
    digest = _package_content_hash(records, (), (), (), (), ())
    manifest = StagingManifest(
        batch_id=f"beta5-{digest[:32]}",
        source_revision="synthetic:beta8-1:revision-1",
        source_manifest_sha256="b" * 64,
        payload_sha256=digest,
        contract_version="synthetic/beta8-1/1",
        converter_version="synthetic/beta8-1/1",
        unit_ids=("synthetic-unit-1",),
        record_count=1,
        project_artifact_count=0,
        warning_count=0,
    )
    return StagingPackage(manifest=manifest, records=records)


async def _wait_for_services(api_client: httpx.AsyncClient, authority_url: str) -> None:
    async with httpx.AsyncClient(timeout=2.0) as authority:
        for _ in range(40):
            try:
                api = await api_client.get("/health")
                internal = await authority.get(f"{authority_url}/internal/health")
                if api.status_code == 200 and internal.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.5)
    raise AssertionError("API/autoridade não ficaram prontas dentro do limite do harness")


async def _login(client: httpx.AsyncClient, email: str) -> tuple[str, str, str]:
    response = await client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, f"login HTTP {response.status_code}: {response.text}"
    token = client.cookies.get("access_token")
    assert token
    claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert claims.get("type") == "access"
    return claims["sub"], claims["sid"], token


async def _verify() -> None:
    run_id, db_name, root_uri = _gate()
    api_uri = _env("BETA8_3_API_MONGO_URI")
    authority_uri = _env("BETA8_3_AUTHORITY_MONGO_URI")
    for uri, username in ((api_uri, "beta8-3-api"), (authority_uri, "beta8-3-authority")):
        parsed = parse_uri(uri)
        if parsed.get("nodelist") != [("mongo", 27017)] or parsed.get("username") != username:
            raise RuntimeError("identidade MongoDB do processo diverge da prova")
        if parsed.get("database") != db_name or parsed.get("options", {}).get("replicaSet") != "rsB83":
            raise RuntimeError("URI de serviço fora do banco Beta 8.3")

    root = AsyncMongoClient(root_uri, appname="beta8-3-verifier", tz_aware=True)
    common = AsyncMongoClient(api_uri, appname="beta8-3-api-privilege-probe", tz_aware=True)
    authority_client = AsyncMongoClient(
        authority_uri, appname="beta8-3-authority-privilege-probe", tz_aware=True,
    )
    stage_writer = AsyncMongoClient(
        _env("BETA8_3_STAGE_WRITE_URI"), appname="beta8-3-stage-writer", tz_aware=True,
    )
    stage_reader = AsyncMongoClient(
        _env("BETA8_3_STAGE_READ_URI"), appname="beta8-3-stage-reader-probe", tz_aware=True,
    )
    root_db = root[db_name]
    db = common[db_name]
    authority_db = authority_client[db_name]
    api_url = _env("BETA8_3_API_URL")
    authority_url = _env("BETA8_3_AUTHORITY_URL")
    editor_id = _env("BETA8_3_EDITOR_ID")
    no_grant_email = _env("BETA8_3_NO_GRANT_EMAIL")
    api_secret = bytes.fromhex(_env("BETA8_3_SERVICE_SECRET_HEX"))
    stager_secret = bytes.fromhex(_env("BETA8_3_STAGER_SECRET_HEX"))
    bytes.fromhex(_env("BETA8_3_OPERATION_KEY_HEX"))  # Validate the synthetic key before use.
    node_id = _env("BETA8_3_NODE_ID")
    block_id = _env("BETA8_3_BLOCK_ID")
    stage_id = _env("BETA8_3_STAGE_RUN_ID")
    try:
        # The normal API role can read the learning/editorial resource but may
        # not create, replace, or delete protected editorial documents.
        await db.content_blocks.find_one({"_id": ObjectId(block_id)})
        denied = 0
        for operation in (
            db.content_blocks.update_one({"_id": ObjectId(block_id)}, {"$set": {"title": "bypass"}}),
            db.content_blocks.insert_one({"_id": ObjectId(), "node_id": node_id, "title": "bypass"}),
            db.content_blocks.delete_one({"_id": ObjectId(block_id)}),
            db.nodes.update_one({"_id": ObjectId(node_id)}, {"$set": {"title": "bypass"}}),
            db["c8_beta8_1_tracks"].insert_one({"_id": "bypass"}),
            db["_beta8_experimental_generations"].insert_one({"_id": "bypass"}),
            db.track_publications.insert_one({"_id": "bypass"}),
        ):
            try:
                await operation
            except OperationFailure:
                denied += 1
        assert denied == 7, f"MongoDB negou somente {denied}/7 tentativas diretas da API"
        authority_denied = 0
        for operation in (
            authority_db.content_blocks.delete_one({"_id": ObjectId(block_id)}),
            authority_db.track_publications.insert_one({"_id": "authority-bypass"}),
            authority_db.attempts.delete_one({"_id": "beta8-3-attempt-deny"}),
        ):
            try:
                await operation
            except OperationFailure:
                authority_denied += 1
        assert authority_denied == 3, "MongoDB permitiu ação fora da autoridade editorial limitada"

        async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as editor_http:
            await _wait_for_services(editor_http, authority_url)
            actor_id, session_id, access_token = await _login(
                editor_http, _env("BETA8_3_EDITOR_EMAIL"),
            )
            assert actor_id == editor_id
            await _provision_c12(root_db, actor_id, session_id, grant_track=TRACK_ID)

            update_headers = {
                "If-Match": '"editorial-rev-0"',
                "Idempotency-Key": "beta83-block-update-0001",
            }
            updated = await editor_http.put(
                f"/api/blocks/{block_id}", json={"title": "Bloco após autoridade separada"},
                headers=update_headers,
            )
            assert updated.status_code == 200, f"W-07 PUT HTTP {updated.status_code}"
            assert updated.headers.get("etag") == '"editorial-rev-1"'
            replay = await editor_http.put(
                f"/api/blocks/{block_id}", json={"title": "Bloco após autoridade separada"},
                headers=update_headers,
            )
            assert replay.status_code == 200 and replay.headers.get("idempotency-replayed") == "true"
            divergent = await editor_http.put(
                f"/api/blocks/{block_id}", json={"title": "payload divergente"},
                headers=update_headers,
            )
            assert divergent.status_code == 409

            created = await editor_http.post(
                "/api/blocks",
                json={"node_id": node_id, "type": "text", "title": "Novo bloco sintético",
                      "data": {"text": "Criado através da autoridade"}, "status": "draft"},
                headers={"If-Match": '"editorial-rev-1"', "Idempotency-Key": "beta83-block-create-0001"},
            )
            assert created.status_code == 200, f"W-07 POST HTTP {created.status_code}"
            node_updated = await editor_http.put(
                f"/api/nodes/{node_id}", json={"summary": "Atualização sintética pela autoridade"},
                headers={"If-Match": '"editorial-rev-2"', "Idempotency-Key": "beta83-node-update-0001"},
            )
            assert node_updated.status_code == 200, f"W-05 PUT HTTP {node_updated.status_code}"

            # Two independent HTTP requests with the same expected revision
            # exercise C8 CAS through both processes and the replica set.
            async def competing(title: str, key: str) -> httpx.Response:
                return await editor_http.put(
                    f"/api/blocks/{block_id}", json={"title": title},
                    headers={"If-Match": '"editorial-rev-3"', "Idempotency-Key": key},
                )

            race = await asyncio.gather(
                competing("concorrente A", "beta83-race-writer-a-0001"),
                competing("concorrente B", "beta83-race-writer-b-0001"),
            )
            assert sorted(response.status_code for response in race) == [200, 412], [
                response.status_code for response in race
            ]

            # A signed internal request is accepted once and its exact nonce
            # replay is rejected, independently of the public HTTP idempotency.
            from services.beta8_3_internal_protocol import (
                API_SERVICE_AUDIENCE,
                EDITORIAL_AUTHORITY_AUDIENCE,
                STAGER_SERVICE_AUDIENCE,
                EditorialMutationCommand,
                request_signature,
                verify_response_signature,
            )

            body = json.dumps({
                "operation": "block.update",
                "actor": {"actor_id": actor_id, "session_id": session_id, "token_version": 0},
                "operation_id": "http_" + "c" * 64,
                "expected_revision": 4,
                "block_id": block_id,
                "node_id": None,
                "changes": {"title": "comando autenticado sintético"},
                "block": None,
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            EditorialMutationCommand.model_validate_json(body)
            timestamp = str(int(datetime.now(UTC).timestamp()))
            nonce = secrets.token_hex(24)
            path = "/internal/v1/editorial/mutations"
            signature = request_signature(
                api_secret, service_id="trilhacode-api", method="POST", path=path,
                audience=EDITORIAL_AUTHORITY_AUDIENCE,
                timestamp=timestamp, nonce=nonce, body=body,
            )
            internal_headers = {
                "Content-Type": "application/json", "X-Beta8-Service": "trilhacode-api",
                "X-Beta8-Timestamp": timestamp, "X-Beta8-Nonce": nonce,
                "X-Beta8-Signature": signature,
            }
            async with httpx.AsyncClient(base_url=authority_url, timeout=10.0) as authority_http:
                unauthenticated = await authority_http.post(
                    path, content=body, headers={"Content-Type": "application/json"},
                )
                assert unauthenticated.status_code == 401, (
                    f"RPC sem autenticação HTTP {unauthenticated.status_code}: {unauthenticated.text}"
                )
                first = await authority_http.post(path, content=body, headers=internal_headers)
                assert first.status_code == 200, f"RPC interno HTTP {first.status_code}"
                assert verify_response_signature(
                    api_secret,
                    first.headers.get("X-Beta8-Response-Signature", ""),
                    audience=API_SERVICE_AUDIENCE,
                    request_nonce=nonce,
                    status_code=first.status_code,
                    body=first.content,
                )
                replayed_nonce = await authority_http.post(path, content=body, headers=internal_headers)
                assert replayed_nonce.status_code == 401

            # The real Beta 5 staging service runs with its own write-restricted
            # account. The separate authority receives a prepared package,
            # independently verifies its persisted records/checkpoints through
            # a read-only account, and commits only a synthetic generation.
            from curriculum_contract.beta_staging_contract import StagingPackage
            from services.beta8_3_internal_protocol import (
                StagingTransitionCommand,
                verify_response_signature,
            )
            from services.beta_curriculum_staging import CurriculumStagingService

            stage_package = _stage_package()
            stage_db = stage_writer[f"beta5_{stage_id}"]
            stage_service = CurriculumStagingService(
                stage_db,
                execution_id=stage_id,
                owner_token=_env("BETA8_3_STAGE_OWNER_TOKEN"),
            )
            staged_outcome = await stage_service.prepare(stage_package)
            assert staged_outcome.state.value == "PREPARED"
            stage_operation_id = f"beta8-op-beta83-stage-{run_id[:16]}"
            stage_command = StagingTransitionCommand(
                actor={"actor_id": actor_id, "session_id": session_id, "token_version": 0},
                operation_id=stage_operation_id,
                expected_revision=5,
                expected_previous_generation=None,
                package=StagingPackage.model_validate(stage_package.model_dump(mode="json")),
            )
            stage_body = json.dumps(
                stage_command.model_dump(mode="json"),
                ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
            ).encode()
            stage_path = "/internal/v1/staging/transitions"

            def signed_stage_headers(body: bytes) -> dict[str, str]:
                issued = str(int(datetime.now(UTC).timestamp()))
                request_nonce = secrets.token_hex(24)
                return {
                    "Content-Type": "application/json",
                    "X-Beta8-Service": "trilhacode-stager",
                    "X-Beta8-Timestamp": issued,
                    "X-Beta8-Nonce": request_nonce,
                    "X-Beta8-Signature": request_signature(
                        stager_secret, service_id="trilhacode-stager", method="POST",
                        audience=EDITORIAL_AUTHORITY_AUDIENCE,
                        path=stage_path, timestamp=issued, nonce=request_nonce, body=body,
                    ),
                }

            async with httpx.AsyncClient(base_url=authority_url, timeout=15.0) as authority_http:
                stage_response = await authority_http.post(
                    stage_path, content=stage_body, headers=signed_stage_headers(stage_body),
                )
                assert stage_response.status_code == 200, (
                    f"Transição de staging HTTP {stage_response.status_code}: {stage_response.text}"
                )
                receipt_payload = stage_response.json()
                assert receipt_payload["revision"] == 6 and receipt_payload["replayed"] is False
                replay_response = await authority_http.post(
                    stage_path, content=stage_body, headers=signed_stage_headers(stage_body),
                )
                assert replay_response.status_code == 200
                assert replay_response.json()["replayed"] is True
                retry_nonce = replay_response.request.headers["X-Beta8-Nonce"]
                assert verify_response_signature(
                    stager_secret,
                    replay_response.headers["X-Beta8-Response-Signature"],
                    audience=STAGER_SERVICE_AUDIENCE,
                    request_nonce=retry_nonce,
                    status_code=replay_response.status_code,
                    body=replay_response.content,
                )

                # Two calls for a second real prepared batch exercise C8
                # idempotency and generation CAS across independent RPCs.
                concurrent_package = _stage_package("Unidade staged concorrente")
                concurrent_outcome = await stage_service.prepare(concurrent_package)
                assert concurrent_outcome.state.value == "PREPARED"
                current_head = await root_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
                concurrent_command = StagingTransitionCommand(
                    actor={"actor_id": actor_id, "session_id": session_id, "token_version": 0},
                    operation_id=f"beta8-op-beta83-stage-race-{run_id[:12]}",
                    expected_revision=6,
                    expected_previous_generation=current_head["generation_id"],
                    package=StagingPackage.model_validate(concurrent_package.model_dump(mode="json")),
                )
                concurrent_body = json.dumps(
                    concurrent_command.model_dump(mode="json"),
                    ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
                ).encode()
                raced = await asyncio.gather(*(
                    authority_http.post(
                        stage_path, content=concurrent_body,
                        headers=signed_stage_headers(concurrent_body),
                    )
                    for _ in range(2)
                ))
                assert [response.status_code for response in raced] == [200, 200], [
                    response.status_code for response in raced
                ]
                assert sorted(response.json()["replayed"] for response in raced) == [False, True]
                for response in raced:
                    nonce_header = response.request.headers["X-Beta8-Nonce"]
                    assert verify_response_signature(
                        stager_secret,
                        response.headers.get("X-Beta8-Response-Signature", ""),
                        audience=STAGER_SERVICE_AUDIENCE,
                        request_nonce=nonce_header,
                        status_code=response.status_code,
                        body=response.content,
                    )

                # A tampered staged document is rejected before the authority
                # creates any additional experimental generation.
                tampered_package = _stage_package("Unidade staged íntegra")
                await stage_service.prepare(tampered_package)
                await root[f"beta5_{stage_id}"]["_beta5_staging_records"].update_one(
                    {"_id": f"{tampered_package.manifest.batch_id}::synthetic-unit-1"},
                    {"$set": {"student_public.title": "Conteúdo adulterado"}},
                )
                tampered_command = StagingTransitionCommand(
                    actor={"actor_id": actor_id, "session_id": session_id, "token_version": 0},
                    operation_id=f"beta8-op-beta83-stage-tamper-{run_id[:12]}",
                    expected_revision=7,
                    expected_previous_generation=(await root_db["_beta8_experimental_heads"].find_one(
                        {"_id": TRACK_ID}, {"generation_id": 1},
                    ))["generation_id"],
                    package=StagingPackage.model_validate(tampered_package.model_dump(mode="json")),
                )
                tampered_body = json.dumps(
                    tampered_command.model_dump(mode="json"),
                    ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
                ).encode()
                tampered_response = await authority_http.post(
                    stage_path, content=tampered_body, headers=signed_stage_headers(tampered_body),
                )
                assert tampered_response.status_code == 409
                assert await root_db["_beta8_experimental_generations"].count_documents(
                    {"track_id": TRACK_ID},
                ) == 2

            assert await root_db["_beta8_experimental_generations"].count_documents({"track_id": TRACK_ID}) == 2
            assert await root_db["_beta8_promotion_audit"].count_documents(
                {"track_id": TRACK_ID},
            ) == 2
            assert await stage_db["_beta5_staging_batches"].count_documents({"status": "PREPARED"}) == 3
            denied_stage = 0
            for operation in (
                common[f"beta5_{stage_id}"]["_beta5_staging_records"].insert_one({"_id": "bypass"}),
                stage_reader[f"beta5_{stage_id}"]["_beta5_staging_batches"].update_one(
                    {"_id": stage_package.manifest.batch_id}, {"$set": {"status": "COMMITTED"}},
                ),
                stage_writer[db_name].content_blocks.insert_one({"_id": ObjectId(), "title": "bypass"}),
            ):
                try:
                    await operation
                except OperationFailure:
                    denied_stage += 1
            assert denied_stage == 3

            expired_claims = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
            expired_claims["exp"] = datetime.now(UTC) - timedelta(seconds=2)
            expired = jwt.encode(expired_claims, JWT_SECRET, algorithm="HS256")
            async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as expired_http:
                expired_result = await expired_http.put(
                    f"/api/blocks/{block_id}", json={"title": "sessão expirada"},
                    headers={"Authorization": f"Bearer {expired}", "If-Match": '"editorial-rev-5"',
                             "Idempotency-Key": "beta83-expired-session-0001"},
                )
            assert expired_result.status_code == 401, (
                f"sessão expirada HTTP {expired_result.status_code}: {expired_result.text}"
            )

            # Unrecognized actor/role fields are not authorization input. Use a
            # stale revision so the HTTP request proves a conflict without
            # creating a second mutation; the authority still uses the session.
            forged = await editor_http.put(
                f"/api/blocks/{block_id}",
                json={"title": "payload", "actor_id": "f" * 24, "role": "admin"},
                headers={"If-Match": '"editorial-rev-4"', "Idempotency-Key": "beta83-forged-actor-0001"},
            )
            assert forged.status_code == 412, (
                f"payload não pode substituir identidade; esperado conflito CAS, obtido HTTP {forged.status_code}"
            )

            from curriculum_contract.experimental_editorial_iam_authority import (
                MongoEditorialIAMAuthority,
            )

            iam = MongoEditorialIAMAuthority(root_db, capability_key=secrets.token_bytes(32))
            assert await iam.revoke_grant(
                actor_id=actor_id, track_id=TRACK_ID, revoked_by="beta8-3-synthetic-revoker",
            )
            revoked_grant = await editor_http.put(
                f"/api/blocks/{block_id}", json={"title": "grant revogado"},
                headers={"If-Match": '"editorial-rev-5"',
                         "Idempotency-Key": "beta83-revoked-grant-0001"},
            )
            assert revoked_grant.status_code == 403

            logout = await editor_http.post("/api/auth/logout")
            assert logout.status_code == 200
            async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as revoked_session_http:
                revoked_session = await revoked_session_http.put(
                    f"/api/blocks/{block_id}", json={"title": "sessão revogada"},
                    headers={"Authorization": f"Bearer {access_token}",
                             "If-Match": '"editorial-rev-5"',
                             "Idempotency-Key": "beta83-revoked-session-0001"},
                )
            assert revoked_session.status_code == 401

        async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as no_grant_http:
            no_grant_actor, no_grant_session, _ = await _login(no_grant_http, no_grant_email)
            await _provision_c12(root_db, no_grant_actor, no_grant_session, grant_track="beta8-track-other-synthetic")
            denied_grant = await no_grant_http.put(
                f"/api/blocks/{block_id}", json={"title": "sem escopo"},
                headers={"If-Match": '"editorial-rev-5"', "Idempotency-Key": "beta83-no-scope-000001"},
            )
            assert denied_grant.status_code == 403

        async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as admin_http:
            _, _, admin_token = await _login(admin_http, _env("BETA8_3_ADMIN_EMAIL"))
            admin_without_grant = await admin_http.put(
                f"/api/blocks/{block_id}", json={"title": "admin sem concessão"},
                headers={"Authorization": f"Bearer {admin_token}", "If-Match": '"editorial-rev-5"',
                         "Idempotency-Key": "beta83-admin-no-grant-0001"},
            )
            assert admin_without_grant.status_code == 403

        # Verify identities remain distinct and protected content remains
        # intact through the API client, while the authority path changed it.
        block = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
        node = await root_db.nodes.find_one({"_id": ObjectId(node_id)})
        assert block and block.get("editorial_revision") == 5
        assert node and node.get("summary") == "Atualização sintética pela autoridade"
        assert await root_db["_beta8_editorial_audit"].count_documents({}) == 5
        assert await root_db["_beta8_3_rpc_nonces"].count_documents({"service_id": "trilhacode-api"}) >= 4
        assert await root_db["c8_beta8_1_history"].count_documents({"track_id": TRACK_ID}) == 7
        for collection, expected in _learning_sentinels(run_id, editor_id, node_id).items():
            persisted = await root_db[collection].find_one({"_id": expected["_id"]})
            assert persisted == expected, f"histórico de aprendizagem alterado em {collection}"

        # Identity of a normal application client is rejected by MongoDB itself.
        assert (await db.content_blocks.find_one({"_id": ObjectId(block_id)}))["title"] == block["title"]
        print("BETA8_3_PROCESS_BOUNDARY: PASS; API and authority are separate Compose services")
        print("BETA8_3_MONGODB_DENIAL: PASS; API credential denied direct node/block writes")
        print("BETA8_3_HTTP_W07_PUT: PASS; auth, grant, CAS, audit, replay and conflict")
        print("BETA8_3_HTTP_W07_POST: PASS; typed creation crossed the authority boundary")
        print("BETA8_3_HTTP_W05_PUT: PASS; node update crossed the authority boundary")
        print("BETA8_3_INTERNAL_AUTH_REPLAY: PASS; unsigned and repeated nonce rejected")
        print("BETA8_3_CAS_CONCURRENCY: PASS; one HTTP writer won and one received 412")
        print("BETA8_3_STAGING_RPC: PASS; Beta 5 preparation crossed a separate authority with verified idempotent retry")
        print("BETA8_3_STAGING_CONCURRENCY: PASS; duplicate concurrent transition produced one generation and one replay")
        print("BETA8_3_STAGING_INTEGRITY: PASS; persisted staging tampering was denied before generation commit")
        print("BETA8_3_AUTH_NEGATIVES: PASS; expired/revoked session, revoked/missing scope, admin without grant, forged body")
    finally:
        await stage_reader.close()
        await stage_writer.close()
        await authority_client.close()
        await common.close()
        await root.close()


async def main() -> None:
    mode = os.environ.get("BETA8_3_MODE", "verify")
    if mode == "provision":
        await _provision()
    elif mode == "verify":
        await _verify()
    else:
        raise RuntimeError("modo de harness desconhecido")


if __name__ == "__main__":
    asyncio.run(main())
