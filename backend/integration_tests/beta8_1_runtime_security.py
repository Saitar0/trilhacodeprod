"""Persistent Beta 8.1 integration proof; run only in the owned Beta 8 harness."""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import jwt
from bson import ObjectId
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.beta8_promotion_contract import (  # noqa: E402
    ExperimentalApproval,
    ExperimentalCandidateState,
    ExperimentalPromotionIntent,
)
from curriculum_contract.beta_staging_contract import StagingPackage  # noqa: E402
from curriculum_contract.experimental_async_editorial_adapter import (  # noqa: E402
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.experimental_editorial_grants import (  # noqa: E402
    EditorialTrackGrant,
)
from curriculum_contract.experimental_editorial_iam_authority import (  # noqa: E402
    MongoEditorialIAMAuthority,
)
from integration_tests.beta8_security_persistence import (  # noqa: E402
    _client_uri,
    _configuration,
    _create_role,
    _create_user,
    _expect_operation_denied,
    _privilege,
    _root_uri,
    _wait_for_primary,
)

REPLICA_SET = "rsB8"
TRACK_ID = "beta8-track-synthetic-runtime"
PASSWORD = "Synthetic-only-password-483!"
JWT_SECRET = "beta8-1 synthetic signing secret only; never for runtime"


def _uri(username: str, password: str, database: str) -> str:
    return (
        f"mongodb://{username}:{password}@mongo:27017/{database}"
        f"?authSource={database}&replicaSet={REPLICA_SET}"
        "&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
    )


def _stage_package(*, unit_title: str = "Synthetic staged unit") -> StagingPackage:
    from curriculum_contract.beta_staging_contract import (
        StagedRecord,
        StagedRecordKind,
        StagingManifest,
        _package_content_hash,
    )

    records = (StagedRecord(
        record_id="synthetic-unit-1",
        kind=StagedRecordKind.UNIT,
        student_public={"unit_id": "synthetic-unit-1", "title": unit_title},
        system_internal={
            "source_revision": "synthetic:beta8-1:revision-1",
            "source_path": "synthetic://beta8-1/unit",
            "source_sha256": "a" * 64,
        },
    ),)
    content_hash = _package_content_hash(records, (), (), (), (), ())
    manifest = StagingManifest(
        batch_id=f"beta5-{content_hash[:32]}",
        source_revision="synthetic:beta8-1:revision-1",
        source_manifest_sha256="b" * 64,
        payload_sha256=content_hash,
        contract_version="synthetic/beta8-1/1",
        converter_version="synthetic/beta8-1/1",
        unit_ids=("synthetic-unit-1",),
        record_count=len(records),
        project_artifact_count=0,
        warning_count=0,
    )
    return StagingPackage(manifest=manifest, records=records)


async def _login(client: httpx.AsyncClient, email: str) -> tuple[str, str]:
    response = await client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    token = client.cookies.get("access_token")
    assert token
    claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert claims["type"] == "access" and claims["sub"]
    return claims["sub"], claims["sid"]


async def _provision_user(root_db: Any, *, role: str, email: str) -> str:
    from security import hash_password

    actor_id = ObjectId()
    await root_db.users.insert_one({
        "_id": actor_id,
        "email": email,
        "name": "Synthetic Beta 8.1 editor",
        "password_hash": hash_password(PASSWORD),
        "role": role,
        "profile": {"bio": "", "goals": "", "preferences": {}},
        "email_verified": True,
        "is_active": True,
        "token_version": 0,
    })
    return str(actor_id)


async def run_beta8_1_runtime_proof() -> None:
    # This gate must run before importing any active application module. Those
    # modules construct the shared AsyncMongoClient at import time.
    run_id, _container_id, _network_id, root_password = _configuration()
    preloaded = {
        "settings", "database", "security", "routes_auth", "routes_content",
    }.intersection(sys.modules)
    if preloaded:
        raise RuntimeError("Módulos ativos carregados antes do gate; integração persistente recusada")
    root_uri = _root_uri(root_password, replica=True)
    parsed = parse_uri(root_uri)
    if parsed.get("nodelist") != [("mongo", 27017)] or parsed.get("options", {}).get("replicaSet") != REPLICA_SET:
        raise RuntimeError("Beta 8.1 recusou URI fora do Mongo descartável aprovado")

    root_client = AsyncMongoClient(root_uri, appname="trilhacode-beta8-1-provisioner", tz_aware=True)
    clients: list[Any] = [root_client]
    authority_db = None
    stage_db = None
    marker = secrets.token_urlsafe(32)
    stage_owner = secrets.token_urlsafe(32)
    db_name = f"editorial_revision_test_c10_c11_c12_b81_{run_id[:12]}_{uuid.uuid4().hex[:5]}"
    stage_run = uuid.uuid4().hex
    stage_name = f"beta5_{stage_run}"
    stage_marker_written = False
    authority_marker_written = False
    active_modules: dict[str, Any] = {}
    settings = None
    app_client = None
    old_env = {
        name: os.environ.get(name)
        for name in ("MONGO_URL", "DB_NAME", "JWT_SECRET", "ENV")
    }
    old_settings = None
    try:
        await _wait_for_primary(root_client)
        hello = await root_client.admin.command({"hello": 1})
        info = await root_client.server_info()
        if not str(info.get("version", "")).startswith("7.") or hello.get("setName") != REPLICA_SET:
            raise RuntimeError("MongoDB Beta 8.1 não corresponde à topologia descartável")
        names = await root_client.list_database_names()
        if db_name in names or stage_name in names:
            raise RuntimeError("Banco aleatório já existe; reutilização Beta 8.1 recusada")

        root_db = root_client[db_name]
        await root_db["_beta8_1_harness_identity"].insert_one({
            "_id": "owner", "phase": "beta8-1", "run_id": run_id,
            "marker": marker, "purpose": "runtime-iam-and-staging-proof",
        })
        authority_marker_written = True
        node_id = ObjectId()
        await root_db.nodes.insert_one({
            "_id": node_id,
            "track_id": TRACK_ID,
            "kind": "lesson",
            "title": "Synthetic draft unit",
            "status": "draft",
            "editorial_state": "draft",
        })
        await root_db.block_types.insert_one({"key": "text", "label": "Texto"})
        await root_db.content_blocks.insert_one({
            "_id": ObjectId(),
            "track_id": TRACK_ID,
            "node_id": str(node_id),
            "editorial_state": "draft",
            "title": "Synthetic original title",
            "data": {"text": "Synthetic original body"},
            "status": "draft",
        })
        block = await root_db.content_blocks.find_one({"track_id": TRACK_ID})
        if block is None:
            raise RuntimeError("Fixture sintética de bloco não foi persistida")

        authority_privileges: list[dict] = []
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
            "edit_history": ["insert"],
            "_beta8_editorial_audit": ["insert"],
            "_beta8_authorization_audit": ["insert"],
            "_beta8_experimental_generations": ["find", "insert"],
            "_beta8_experimental_heads": ["find", "insert", "update"],
            "_beta8_promotion_audit": ["insert"],
            "users": ["find", "update"],
            "auth_sessions": ["find", "update"],
        }.items():
            authority_privileges.append(_privilege(db_name, collection, actions))
        await _create_role(root_db, "beta8_1_authority", authority_privileges)
        await _create_role(root_db, "beta8_1_runtime", [
            _privilege(db_name, "users", ["find"]),
            _privilege(db_name, "auth_sessions", ["find", "insert", "update"]),
            _privilege(db_name, "login_attempts", ["find", "insert", "update", "remove"]),
            _privilege(db_name, "content_blocks", ["find"]),
            _privilege(db_name, "nodes", ["find"]),
            _privilege(db_name, "block_types", ["find"]),
        ])
        authority_password = await _create_user(root_db, "beta8-1-authority", "beta8_1_authority")
        runtime_password = await _create_user(root_db, "beta8-1-runtime", "beta8_1_runtime")
        # Import the real FastAPI/auth modules only after a permitted Mongo user
        # and the disposable target exist. The global client must never inherit
        # settings.py's localhost fallback or a caller's unrelated .env value.
        runtime_uri = _client_uri("beta8-1-runtime", runtime_password, db_name)
        runtime_parsed = parse_uri(runtime_uri)
        if (
            runtime_parsed.get("nodelist") != [("mongo", 27017)]
            or runtime_parsed.get("username") != "beta8-1-runtime"
            or runtime_parsed.get("database") != db_name
            or runtime_parsed.get("options", {}).get("authSource") != db_name
            or runtime_parsed.get("options", {}).get("replicaSet") != REPLICA_SET
        ):
            raise RuntimeError("Cliente do runtime não corresponde à identidade descartável restrita")
        os.environ["MONGO_URL"] = runtime_uri
        os.environ["DB_NAME"] = db_name
        os.environ["JWT_SECRET"] = JWT_SECRET
        os.environ["ENV"] = "development"

        import database as application_database
        from settings import settings as app_settings
        app_client = application_database.client
        import security as application_security
        import services.auth as auth_service
        import services.blocks as blocks_service
        import services.common as common_service
        import services.sessions as sessions_service
        from routes_auth import login as real_login_route
        from routes_auth import logout as real_logout_route
        from routes_content import create_block as real_create_block_route
        from routes_content import update_node as real_update_node_route
        from routes_content import update_block as real_update_block_route
        from schemas.content import BlockOut, NodeOut
        from services.beta8_1_runtime_iam import (
            Beta8_1EditorialRuntime,
            Beta8_1RuntimeIAMBridge,
        )
        from services.beta8_1_staging_authority import Beta8_1StagingAuthorityBridge
        from services.beta8_curriculum_promotion import Beta8ExperimentalPromoter
        from services.beta8_editorial_enforcement import (
            Beta8EditorialMutationBoundary,
            EditorialMutationDenied,
        )
        from services.beta_curriculum_staging import CurriculumStagingService

        settings = app_settings
        active_modules = {
            "database": application_database,
            "security": application_security,
            "auth": auth_service,
            "blocks": blocks_service,
            "common": common_service,
            "sessions": sessions_service,
        }
        clients.append(app_client)
        old_settings = (settings.mongo_url, settings.db_name, settings.jwt_secret, settings.env)
        old_db_refs = (
            application_database.db,
            application_security.db,
            auth_service.db,
            blocks_service.db,
            common_service.db,
            sessions_service.db,
        )
        authority_client = AsyncMongoClient(
            _client_uri("beta8-1-authority", authority_password, db_name),
            appname="trilhacode-beta8-1-authority", tz_aware=True,
        )
        runtime_client = AsyncMongoClient(
            _client_uri("beta8-1-runtime", runtime_password, db_name),
            appname="trilhacode-beta8-1-runtime", tz_aware=True,
        )
        clients.extend((authority_client, runtime_client))
        authority_db = authority_client[db_name]
        runtime_db = runtime_client[db_name]
        await runtime_db.content_blocks.find_one({"_id": block["_id"]})
        await _expect_operation_denied(runtime_db.content_blocks.update_one(
            {"_id": block["_id"]}, {"$set": {"title": "direct runtime bypass"}},
        ))
        await _expect_operation_denied(runtime_db.content_blocks.insert_one({
            "_id": ObjectId(), "track_id": TRACK_ID, "node_id": str(node_id),
            "status": "draft", "title": "direct create bypass",
        }))
        await _expect_operation_denied(runtime_db.content_blocks.delete_one({"_id": block["_id"]}))
        await _expect_operation_denied(runtime_db.track_publications.insert_one({"_id": "denied"}))
        await _expect_operation_denied(runtime_db.nodes.update_one(
            {"_id": node_id}, {"$set": {"title": "direct runtime node bypass"}},
        ))
        await _expect_operation_denied(runtime_db.nodes.insert_one({
            "track_id": TRACK_ID, "title": "direct runtime node create bypass", "status": "draft",
        }))
        await _expect_operation_denied(runtime_db.nodes.delete_one({"_id": node_id}))

        await root_db.content_blocks.create_index("track_id")
        adapter = AsyncEditorialRevisionAdapter(authority_db, namespace="c8_beta8_1")
        await adapter.verify_transaction_topology()
        await adapter.initialize_track(TRACK_ID)
        writer_credential = await adapter.provision_writer_credential(TRACK_ID, "beta8-1-block-update")
        fence_authority = await adapter.provision_fence_authority(TRACK_ID, "beta8-1-fence-authority")
        fence = await adapter.advance_fence(TRACK_ID, fence_authority)
        iam = MongoEditorialIAMAuthority(authority_db, capability_key=secrets.token_bytes(32))

        actor_id = await _provision_user(root_db, role="editor", email=f"editor-{run_id[:8]}@example.com")
        await iam.provision_principal(actor_id=actor_id, role="editor")
        settings.jwt_secret = JWT_SECRET
        application_security.db = runtime_db
        auth_service.db = runtime_db
        sessions_service.db = runtime_db
        blocks_service.db = runtime_db
        common_service.db = runtime_db

        # The unadapted service call still exists for legacy callers, but the
        # runtime Mongo identity itself cannot bypass the database boundary.
        await _expect_operation_denied(blocks_service.update_block(
            str(block["_id"]),
            {"title": "must not bypass through legacy service", "status": "draft"},
            {"id": actor_id},
        ))
        assert (await root_db.content_blocks.find_one({"_id": block["_id"]}))["title"] == "Synthetic original title"

        app = FastAPI()
        # The active login route and current_user dependencies are reused.
        app.add_api_route("/api/auth/login", real_login_route, methods=["POST"])
        app.add_api_route("/api/auth/logout", real_logout_route, methods=["POST"])
        app.add_api_route(
            "/api/blocks", real_create_block_route, methods=["POST"],
            response_model=BlockOut, response_model_exclude_unset=True,
        )
        app.add_api_route(
            "/api/blocks/{block_id}",
            real_update_block_route,
            methods=["PUT"],
            response_model=BlockOut,
            response_model_exclude_unset=True,
        )
        app.add_api_route(
            "/api/nodes/{node_id}", real_update_node_route, methods=["PUT"],
            response_model=NodeOut, response_model_exclude_unset=True,
        )

        def make_boundary() -> Beta8EditorialMutationBoundary:
            return Beta8EditorialMutationBoundary(
                authority_db, iam, adapter, writer_credential, fence,
            )

        entered = asyncio.Event()
        release = asyncio.Event()
        pause_enabled = False

        async def before_commit() -> None:
            if pause_enabled:
                entered.set()
                await release.wait()

        app.state.beta8_1_editorial_runtime = Beta8_1EditorialRuntime(
            boundary=make_boundary(),
            iam_bridge=Beta8_1RuntimeIAMBridge(authority_db),
            operation_hmac_key=secrets.token_bytes(32),
            content_hmac_key=secrets.token_bytes(32),
            before_commit=before_commit,
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test"
        ) as student_http:
            anonymous = await student_http.put(
                f"/api/blocks/{block['_id']}",
                json={"title": "anonymous attempt"},
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-anon-0001"},
            )
            assert anonymous.status_code == 401
            login_response = await student_http.post(
                "/api/auth/login",
                json={"email": f"editor-{run_id[:8]}@example.com", "password": PASSWORD},
            )
            assert login_response.status_code == 200, login_response.text
            access_token = student_http.cookies.get("access_token")
            student_cookies = dict(student_http.cookies)
            claims = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
            actor_id = claims["sub"]
            session_id = claims["sid"]
            expired_claims = claims | {"exp": datetime.now(UTC) - timedelta(seconds=1)}
            expired_token = jwt.encode(expired_claims, JWT_SECRET, algorithm="HS256")
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="https://beta8-1.test",
                cookies={"access_token": expired_token},
            ) as expired_http:
                expired = await expired_http.put(
                    f"/api/blocks/{block['_id']}",
                    json={"title": "expired attempt"},
                    headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-expired-0001"},
                )
                assert expired.status_code == 401
            inactive_app = FastAPI()
            inactive_app.add_api_route("/api/blocks", real_create_block_route, methods=["POST"])
            inactive_app.add_api_route("/api/blocks/{block_id}", real_update_block_route, methods=["PUT"])
            inactive_app.add_api_route("/api/nodes/{node_id}", real_update_node_route, methods=["PUT"])
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=inactive_app),
                base_url="https://beta8-1.test",
                cookies={"access_token": access_token},
            ) as inactive_http:
                unavailable = await inactive_http.put(
                    f"/api/blocks/{block['_id']}",
                    json={"title": "must remain disabled without explicit composition"},
                    headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-no-capability-0001"},
                )
                assert unavailable.status_code == 503
                assert (await root_db.content_blocks.find_one({"_id": block["_id"]}))["title"] == "Synthetic original title"
                create_unavailable = await inactive_http.post(
                    "/api/blocks",
                    json={
                        "node_id": str(node_id), "type": "text", "title": "disabled create",
                        "data": {"body": "must not persist"}, "status": "draft",
                    },
                )
                assert create_unavailable.status_code == 503
                node_unavailable = await inactive_http.put(
                    f"/api/nodes/{node_id}", json={"title": "disabled node update"},
                )
                assert node_unavailable.status_code == 503
                assert await root_db.content_blocks.count_documents({"track_id": TRACK_ID}) == 1
                assert (await root_db.nodes.find_one({"_id": node_id}))["title"] == "Synthetic draft unit"
            active_session = await runtime_db.auth_sessions.find_one({
                "_id": hashlib.sha256(session_id.encode()).hexdigest(), "user_id": actor_id,
            })
            assert active_session is not None
            await iam.provision_session(
                actor_id=actor_id,
                session_id=session_id,
                expires_at=active_session["expires_at"].replace(tzinfo=UTC)
                if active_session["expires_at"].tzinfo is None else active_session["expires_at"],
            )

            path = f"/api/blocks/{block['_id']}"
            headers = {"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-runtime-write-0001"}
            no_grant = await student_http.put(
                path,
                json={"title": "must be denied"},
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-runtime-denied-0001"},
            )
            assert no_grant.status_code == 403
            assert "track" not in no_grant.text.lower()
            no_create_grant = await student_http.post(
                "/api/blocks",
                json={
                    "node_id": str(node_id), "type": "text", "title": "Denied draft",
                    "data": {"body": "must not persist"}, "status": "draft",
                },
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b82-create-denied-0001"},
            )
            assert no_create_grant.status_code == 403
            no_node_grant = await student_http.put(
                f"/api/nodes/{node_id}", json={"title": "must be denied without node grant"},
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b82-node-denied-0001"},
            )
            assert no_node_grant.status_code == 403
            await iam.provision_grant(EditorialTrackGrant(
                actor_id=actor_id,
                track_id="beta8-track-synthetic-other",
                allowed_operations=("block.update", "node.update"),
                granted_by="beta8-1-synthetic-authorizer",
                granted_at=datetime.now(UTC),
            ))
            wrong_scope = await student_http.put(
                path,
                json={"title": "wrong track scope must be denied"},
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b81-runtime-wrong-scope-0001"},
            )
            assert wrong_scope.status_code == 403
            wrong_node_scope = await student_http.put(
                f"/api/nodes/{node_id}", json={"title": "wrong node scope must be denied"},
                headers={"If-Match": '"editorial-rev-0"', "Idempotency-Key": "b82-node-wrong-scope-0001"},
            )
            assert wrong_node_scope.status_code == 403
            assert (await root_db.content_blocks.find_one({"_id": block["_id"]}))["title"] == "Synthetic original title"

            await iam.provision_grant(EditorialTrackGrant(
                actor_id=actor_id,
                track_id=TRACK_ID,
                allowed_operations=("block.create", "block.update", "content.publish", "node.update"),
                granted_by="beta8-1-synthetic-authorizer",
                granted_at=datetime.now(UTC),
            ))
            accepted = await student_http.put(path, json={"title": "Authorized HTTP update"}, headers=headers)
            assert accepted.status_code == 200, accepted.text
            assert accepted.headers["etag"] == '"editorial-rev-1"'
            assert accepted.headers["idempotency-replayed"] == "false"
            replay = await student_http.put(path, json={"title": "Authorized HTTP update"}, headers=headers)
            assert replay.status_code == 200
            assert replay.headers["idempotency-replayed"] == "true"
            stored = await root_db.content_blocks.find_one({"_id": block["_id"]})
            assert stored["title"] == "Authorized HTTP update"
            # Verify write-only audit/history collections through the isolated
            # provisioner, not by widening the authority writer's privileges.
            assert await root_db["_beta8_editorial_audit"].count_documents({}) == 1
            assert await root_db["c8_beta8_1_history"].count_documents({}) == 1

            race_actor_id = await _provision_user(
                root_db, role="editor", email=f"race-{run_id[:8]}@example.com",
            )
            await iam.provision_principal(actor_id=race_actor_id, role="editor")
            race_http = httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test",
            )
            race_login = await race_http.post(
                "/api/auth/login",
                json={"email": f"race-{run_id[:8]}@example.com", "password": PASSWORD},
            )
            assert race_login.status_code == 200
            race_claims = jwt.decode(
                race_http.cookies.get("access_token"), JWT_SECRET, algorithms=["HS256"],
            )
            race_session_id = race_claims["sid"]
            race_session = await runtime_db.auth_sessions.find_one({
                "_id": hashlib.sha256(race_session_id.encode()).hexdigest(),
                "user_id": race_actor_id,
            })
            assert race_session is not None
            await iam.provision_session(
                actor_id=race_actor_id,
                session_id=race_session_id,
                expires_at=race_session["expires_at"].replace(tzinfo=UTC)
                if race_session["expires_at"].tzinfo is None else race_session["expires_at"],
            )
            await iam.provision_grant(EditorialTrackGrant(
                actor_id=race_actor_id,
                track_id=TRACK_ID,
                allowed_operations=("block.update",),
                granted_by="beta8-1-synthetic-authorizer",
                granted_at=datetime.now(UTC),
            ))
            pause_enabled = True
            race_task = asyncio.create_task(race_http.put(
                path,
                json={"title": "must not commit after grant revocation"},
                headers={"If-Match": '"editorial-rev-1"', "Idempotency-Key": "b81-revocation-race-0001"},
            ))
            await asyncio.wait_for(entered.wait(), timeout=10)
            assert await iam.revoke_grant(
                actor_id=race_actor_id, track_id=TRACK_ID, revoked_by="beta8-1-synthetic-revoker",
            )
            release.set()
            denied_race = await race_task
            pause_enabled = False
            assert denied_race.status_code in {403, 409}, denied_race.text
            after_race = await root_db.content_blocks.find_one({"_id": block["_id"]})
            assert after_race["title"] == "Authorized HTTP update"
            state = await authority_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
            assert state["revision"] == 1
            await race_http.aclose()

            create_headers = {
                "If-Match": '"editorial-rev-1"',
                "Idempotency-Key": "b82-create-draft-block-0001",
            }
            create_body = {
                "node_id": str(node_id), "type": "text", "title": "Authorized draft block",
                "data": {"body": "created through C12 and C8"}, "status": "draft",
            }
            created = await student_http.post("/api/blocks", json=create_body, headers=create_headers)
            assert created.status_code == 200, created.text
            assert created.headers["etag"] == '"editorial-rev-2"'
            assert created.headers["idempotency-replayed"] == "false"
            created_replay = await student_http.post("/api/blocks", json=create_body, headers=create_headers)
            assert created_replay.status_code == 200, created_replay.text
            assert created_replay.headers["idempotency-replayed"] == "true"
            assert created_replay.json()["id"] == created.json()["id"]
            assert await root_db.content_blocks.count_documents({"track_id": TRACK_ID}) == 2
            node_headers = {
                "If-Match": '"editorial-rev-2"',
                "Idempotency-Key": "b82-update-draft-node-0001",
            }
            node_update = await student_http.put(
                f"/api/nodes/{node_id}", json={"title": "Updated synthetic draft unit"}, headers=node_headers,
            )
            assert node_update.status_code == 200, node_update.text
            assert node_update.headers["etag"] == '"editorial-rev-3"'
            assert node_update.headers["idempotency-replayed"] == "false"
            assert node_update.json()["title"] == "Updated synthetic draft unit"
            node_replay = await student_http.put(
                f"/api/nodes/{node_id}", json={"title": "Updated synthetic draft unit"}, headers=node_headers,
            )
            assert node_replay.status_code == 200
            assert node_replay.headers["idempotency-replayed"] == "true"
            assert await root_db.nodes.count_documents({
                "_id": node_id, "title": "Updated synthetic draft unit",
            }) == 1
            assert await root_db["_beta8_editorial_audit"].count_documents({}) == 3
            assert await root_db["c8_beta8_1_history"].count_documents({}) == 3

        # A separately authenticated admin still needs the explicit resource grant.
        admin_id = await _provision_user(
            root_db, role="admin", email=f"admin-{run_id[:8]}@example.com",
        )
        await iam.provision_principal(actor_id=admin_id, role="admin")
        admin_http = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test",
        )
        admin_login = await admin_http.post(
            "/api/auth/login",
            json={"email": f"admin-{run_id[:8]}@example.com", "password": PASSWORD},
        )
        assert admin_login.status_code == 200
        admin_claims = jwt.decode(admin_http.cookies.get("access_token"), JWT_SECRET, algorithms=["HS256"])
        admin_session_id = admin_claims["sid"]
        admin_session = await runtime_db.auth_sessions.find_one({
            "_id": hashlib.sha256(admin_session_id.encode()).hexdigest(), "user_id": admin_id,
        })
        assert admin_session is not None
        await iam.provision_session(
            actor_id=admin_id,
            session_id=admin_session_id,
            expires_at=admin_session["expires_at"].replace(tzinfo=UTC)
            if admin_session["expires_at"].tzinfo is None else admin_session["expires_at"],
        )
        admin_denied = await admin_http.put(
            f"/api/blocks/{block['_id']}",
            json={"title": "admin without scope"},
            headers={"If-Match": '"editorial-rev-1"', "Idempotency-Key": "b81-admin-no-scope-0001"},
        )
        assert admin_denied.status_code == 403
        await admin_http.aclose()

        disabled_id = await _provision_user(
            root_db, role="editor", email=f"disabled-{run_id[:8]}@example.com",
        )
        await iam.provision_principal(actor_id=disabled_id, role="editor")
        disabled_http = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test",
        )
        disabled_login = await disabled_http.post(
            "/api/auth/login",
            json={"email": f"disabled-{run_id[:8]}@example.com", "password": PASSWORD},
        )
        assert disabled_login.status_code == 200
        await root_db.users.update_one({"_id": ObjectId(disabled_id)}, {"$set": {"is_active": False}})
        disabled_attempt = await disabled_http.put(
            f"/api/blocks/{block['_id']}",
            json={"title": "disabled account must be denied"},
            headers={"If-Match": '"editorial-rev-1"', "Idempotency-Key": "b81-disabled-user-0001"},
        )
        assert disabled_attempt.status_code == 401
        await disabled_http.aclose()

        # The real Beta 5 staging service runs with a distinct, preparation-only DB user.
        stage_root = root_client[stage_name]
        await stage_root["_beta5_test_owner"].insert_one({
            "_id": "owner", "run_id": stage_run, "owner_token": stage_owner,
            "database": stage_name,
        })
        stage_marker_written = True
        stage_collections = (
            "_beta5_staging_batches", "_beta5_staging_records",
            "_beta5_staging_checkpoints", "_beta5_staging_events",
        )
        stage_privileges = [_privilege(stage_name, "_beta5_test_owner", ["find"])]
        for collection in stage_collections:
            stage_privileges.append(_privilege(stage_name, collection, ["find", "insert", "update", "createIndex"]))
        await _create_role(stage_root, "beta8_1_preparation", stage_privileges)
        stage_password = await _create_user(stage_root, "beta8-1-preparer", "beta8_1_preparation")
        stage_client = AsyncMongoClient(
            _uri("beta8-1-preparer", stage_password, stage_name),
            appname="trilhacode-beta8-1-preparation", tz_aware=True,
        )
        clients.append(stage_client)
        stage_db = stage_client[stage_name]
        staging = CurriculumStagingService(
            stage_db, execution_id=stage_run, owner_token=stage_owner,
        )
        promoter = Beta8ExperimentalPromoter(authority_db, iam, adapter, writer_credential)
        stage_bridge = Beta8_1StagingAuthorityBridge(staging, promoter, track_id=TRACK_ID)
        package = _stage_package()
        candidate = stage_bridge.candidate_for(package)
        intent = ExperimentalPromotionIntent(
            batch_id=candidate.batch_id,
            payload_sha256=candidate.payload_sha256,
            track_id=TRACK_ID,
            generation_id="beta8-generation-synthetic-stage-1",
            operation_id="beta8-op-stage-promote-0001",
            expected_revision=3,
            fencing_token=fence,
            candidate_state=ExperimentalCandidateState.VALIDATED,
            approval=ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED,
            target_namespace="beta8_experimental",
        )
        promoted = await stage_bridge.prepare_and_promote(
            package, intent, actor_id=actor_id, session_id=session_id,
        )
        assert promoted.revision == 4
        staged = await stage_db["_beta5_staging_batches"].find_one({"_id": package.manifest.batch_id})
        generation = await authority_db["_beta8_experimental_generations"].find_one(
            {"_id": intent.generation_id},
        )
        assert staged["status"] == "PREPARED"
        assert generation["source_revision"] == f"synthetic:stage:{package.manifest.payload_sha256}"
        assert await root_db["_beta8_promotion_audit"].count_documents({}) == 1
        # The preparation principal has no access to the promotion namespace.
        await _expect_operation_denied(stage_db["_beta8_experimental_heads"].insert_one({"_id": "bypass"}))

        replayed = await stage_bridge.prepare_and_promote(
            package, intent, actor_id=actor_id, session_id=session_id,
        )
        assert replayed.revision == promoted.revision and replayed.replayed is True
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 1
        assert await root_db["_beta8_promotion_audit"].count_documents({}) == 1

        recovery_package = _stage_package(unit_title="Synthetic stage recovery unit")
        recovery_candidate = stage_bridge.candidate_for(recovery_package)
        recovery_intent = intent.model_copy(update={
            "batch_id": recovery_candidate.batch_id,
            "payload_sha256": recovery_candidate.payload_sha256,
            "generation_id": "beta8-generation-synthetic-stage-recovered",
            "operation_id": "beta8-op-stage-recovery-retry",
            "expected_revision": 4,
        })

        async def fail_after_first_staged_record(point: str, index: int, _record_id: str | None) -> None:
            if point == "after_document_before_checkpoint" and index == 1:
                raise RuntimeError("injected staging interruption after document")

        try:
            await stage_bridge.prepare_and_promote(
                recovery_package,
                recovery_intent,
                actor_id=actor_id,
                session_id=session_id,
                expected_previous_generation=intent.generation_id,
                staging_fault_hook=fail_after_first_staged_record,
            )
        except RuntimeError as exc:
            assert "injected staging interruption" in str(exc)
        else:
            raise AssertionError("interrupção durante staging não foi exercitada")
        partial_stage = await stage_db["_beta5_staging_batches"].find_one(
            {"_id": recovery_package.manifest.batch_id},
        )
        assert partial_stage and partial_stage["status"] == "RECOVERABLE"
        assert await stage_db["_beta5_staging_records"].count_documents(
            {"batch_id": recovery_package.manifest.batch_id},
        ) == 1
        assert await stage_db["_beta5_staging_checkpoints"].count_documents(
            {"batch_id": recovery_package.manifest.batch_id},
        ) == 0
        recovered_stage_receipt = await stage_bridge.prepare_and_promote(
            recovery_package,
            recovery_intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=intent.generation_id,
        )
        assert recovered_stage_receipt.revision == 5
        assert (await stage_db["_beta5_staging_batches"].find_one(
            {"_id": recovery_package.manifest.batch_id},
        ))["status"] == "PREPARED"

        lost_response_intent = recovery_intent.model_copy(update={
            "generation_id": "beta8-generation-synthetic-stage-lost-response",
            "operation_id": "beta8-op-stage-lost-response",
            "expected_revision": 5,
        })

        async def lose_response_after_commit() -> None:
            raise RuntimeError("injected response loss after durable commit")

        try:
            await stage_bridge.prepare_and_promote(
                recovery_package,
                lost_response_intent,
                actor_id=actor_id,
                session_id=session_id,
                expected_previous_generation=recovery_intent.generation_id,
                after_commit=lose_response_after_commit,
            )
        except RuntimeError as exc:
            assert "injected response loss" in str(exc)
        else:
            raise AssertionError("perda sintética da resposta após commit não foi exercitada")
        recovered_receipt = await stage_bridge.prepare_and_promote(
            recovery_package,
            lost_response_intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=recovery_intent.generation_id,
        )
        assert recovered_receipt.revision == 6 and recovered_receipt.replayed is True
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 3
        assert await root_db["_beta8_promotion_audit"].count_documents({}) == 3
        assert await authority_db["_beta8_experimental_generations"].find_one(
            {"_id": intent.generation_id},
        ) is not None

        entered_transitions = 0
        both_entered = asyncio.Event()
        release_transitions = asyncio.Event()

        async def transition_barrier() -> None:
            nonlocal entered_transitions
            entered_transitions += 1
            if entered_transitions == 2:
                both_entered.set()
            await release_transitions.wait()

        concurrent_intents = [
            recovery_intent.model_copy(update={
                "generation_id": f"beta8-generation-synthetic-race-{suffix}",
                "operation_id": f"beta8-op-stage-race-{suffix}",
                "expected_revision": 6,
            })
            for suffix in ("a", "b")
        ]
        concurrent_tasks = [
            asyncio.create_task(stage_bridge.prepare_and_promote(
                recovery_package,
                concurrent_intent,
                actor_id=actor_id,
                session_id=session_id,
                expected_previous_generation=lost_response_intent.generation_id,
                before_commit=transition_barrier,
            ))
            for concurrent_intent in concurrent_intents
        ]
        await asyncio.wait_for(both_entered.wait(), timeout=10)
        release_transitions.set()
        concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        winners = [result for result in concurrent_results if not isinstance(result, Exception)]
        losers = [result for result in concurrent_results if isinstance(result, Exception)]
        assert len(winners) == 1 and len(losers) == 1, concurrent_results
        current_head = await authority_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
        assert current_head and current_head["revision"] == 7
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 4
        assert await root_db["_beta8_promotion_audit"].count_documents({}) == 4

        revocation_entered = asyncio.Event()
        release_revocation = asyncio.Event()

        async def pause_before_revocable_commit() -> None:
            revocation_entered.set()
            await release_revocation.wait()

        revocation_intent = recovery_intent.model_copy(update={
            "generation_id": "beta8-generation-synthetic-revoked",
            "operation_id": "beta8-op-stage-revoked",
            "expected_revision": 7,
        })
        revocation_task = asyncio.create_task(stage_bridge.prepare_and_promote(
            recovery_package,
            revocation_intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=current_head["generation_id"],
            before_commit=pause_before_revocable_commit,
        ))
        await asyncio.wait_for(revocation_entered.wait(), timeout=10)
        assert await iam.revoke_grant(
            actor_id=actor_id, track_id=TRACK_ID, revoked_by="beta8-2-synthetic-revoker",
        )
        release_revocation.set()
        revoked_transition = await asyncio.gather(revocation_task, return_exceptions=True)
        assert isinstance(revoked_transition[0], EditorialMutationDenied), revoked_transition
        assert await authority_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID}) == current_head
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 4

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test",
            cookies=student_cookies,
        ) as logout_http:
            logout_response = await logout_http.post("/api/auth/logout")
            assert logout_response.status_code == 200
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://beta8-1.test",
            cookies={"access_token": student_cookies["access_token"]},
        ) as revoked_http:
            revoked = await revoked_http.put(
                f"/api/blocks/{block['_id']}",
                json={"title": "revoked session attempt"},
                headers={"If-Match": '"editorial-rev-2"', "Idempotency-Key": "b81-revoked-session-0001"},
            )
            assert revoked.status_code == 401

        print("BETA8_1_ACTIVE_AUTH_HTTP: PASS")
        print("BETA8_1_RESOURCE_GRANT: PASS")
        print("BETA8_1_RUNTIME_SESSION_COMMIT_GUARD: PASS")
        print("BETA8_1_MONGODB_RUNTIME_DENIAL: PASS")
        print("BETA8_1_LEGACY_SERVICE_MONGODB_DENIAL: PASS")
        print("BETA8_1_AUTH_NEGATIVES: PASS (anonymous, expired, revoked session, disabled user, missing/wrong scope, admin without grant)")
        print("BETA8_1_REVOKED_GRANT_RACE: PASS")
        print("BETA8_1_SELECTED_WRITER: PASS (existing PUT /api/blocks/{id} service path)")
        print("BETA8_2_W07_CREATE: PASS (authenticated POST, grant, C8 CAS, replay and audit)")
        print("BETA8_2_W05_UPDATE: PASS (authenticated PUT, track grant, node CAS, replay and audit)")
        print("BETA8_2_DEFAULT_STARTUP_DENY: PASS (selected create/update paths disabled without explicit authority composition)")
        print("BETA8_2_W07_DIRECT_CREATE_DELETE_DENIAL: PASS (runtime MongoDB role)")
        print("BETA8_1_DEFAULT_STARTUP_FAIL_CLOSED: PASS")
        print("BETA8_1_REAL_STAGING_TO_EXPERIMENTAL_AUTHORITY: PASS")
        print("BETA8_2_STAGING_PARTIAL_RECOVERY: PASS (Beta 5 checkpoint resumed through bridge)")
        print("BETA8_2_STAGING_COMMIT_REPLAY: PASS (lost response reconciled by same operation ID)")
        print("BETA8_2_STAGING_CONCURRENT_TRANSITIONS: PASS (one CAS winner, one conflict)")
        print("BETA8_2_STAGING_REVOCATION_RACE: PASS (revocation before commit prevents transition)")
        print("BETA8_1_PREPARER_PROMOTION_DENIAL: PASS")
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        if old_settings is not None:
            settings.mongo_url, settings.db_name, settings.jwt_secret, settings.env = old_settings
        if active_modules:
            (
                active_modules["database"].db,
                active_modules["security"].db,
                active_modules["auth"].db,
                active_modules["blocks"].db,
                active_modules["common"].db,
                active_modules["sessions"].db,
            ) = old_db_refs
        for client in reversed(clients):
            await client.close()
        if app_client is not None and app_client not in clients:
            await app_client.close()
        cleanup_client = None
        try:
            # The caller's disposable-root handle is reopened only to verify the
            # markers before dropping these two random databases. No prefix
            # cleanup is used.
            cleanup_client = AsyncMongoClient(
                root_uri, appname="trilhacode-beta8-1-cleanup", tz_aware=True,
            )
            if authority_marker_written:
                stored = await cleanup_client[db_name]["_beta8_1_harness_identity"].find_one({"_id": "owner"})
                if (
                    stored and stored.get("phase") == "beta8-1"
                    and stored.get("run_id") == run_id and stored.get("marker") == marker
                ):
                    await cleanup_client.drop_database(db_name)
                else:
                    raise RuntimeError("Propriedade do banco editorial Beta 8.1 não comprovada; preservado")
            if stage_marker_written:
                stored = await cleanup_client[stage_name]["_beta5_test_owner"].find_one({"_id": "owner"})
                if (
                    stored and stored.get("run_id") == stage_run
                    and stored.get("owner_token") == stage_owner
                    and stored.get("database") == stage_name
                ):
                    await cleanup_client.drop_database(stage_name)
                else:
                    raise RuntimeError("Propriedade do banco staging Beta 8.1 não comprovada; preservado")
        finally:
            if cleanup_client is not None:
                await cleanup_client.close()


async def main() -> None:
    # The original Beta 8 proof is retained as a regression in the same owned run.
    from integration_tests.beta8_security_persistence import run_persistent_proof

    await run_persistent_proof()
    await run_beta8_1_runtime_proof()


if __name__ == "__main__":
    asyncio.run(main())
