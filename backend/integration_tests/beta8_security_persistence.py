"""Self-contained persistent Beta 8 proof; requires the owned Compose harness."""

from __future__ import annotations

import asyncio
import os
import re
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, cast
from urllib.parse import quote

from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure
from pymongo.uri_parser import parse_uri

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.beta8_promotion_contract import (  # noqa: E402
    ExperimentalApproval,
    ExperimentalCandidateState,
    ExperimentalPromotionIntent,
    make_synthetic_candidate,
)
from curriculum_contract.editorial_revision_protocol import (  # noqa: E402
    FencingRejected,
    IdempotencyConflict,
    RevisionConflict,
)
from curriculum_contract.experimental_async_editorial_adapter import (  # noqa: E402
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.experimental_editorial_grants import (  # noqa: E402
    EditorialTrackGrant,
)
from curriculum_contract.experimental_editorial_iam_authority import (  # noqa: E402
    MongoEditorialIAMAuthority,
)
from services.beta8_curriculum_promotion import (  # noqa: E402
    Beta8ExperimentalPromoter,
)
from services.beta8_editorial_enforcement import (  # noqa: E402
    Beta8EditorialMutationBoundary,
    EditorialMutationDenied,
)

RUN_ID_RE = re.compile(r"^[a-f0-9]{32}$")
DOCKER_ID_RE = re.compile(r"^[a-f0-9]{64}$")
DB_PREFIX = "editorial_revision_test_c10_c11_c12_beta8_"
REPLICA_SET = "rsB8"
_FORBIDDEN_ENV = (
    "MONGO_URL", "MONGO_URL_TEST", "DATABASE_URL", "EDITORIAL_POC_MONGO_URI",
    "C12_TEST_MONGODB_URI", "C16_ROOT_MONGODB_URI",
)


class IsolationGateError(RuntimeError):
    """The supplied target does not prove the Beta 8 disposable execution."""


def _configuration() -> tuple[str, str, str, str]:
    if os.environ.get("BETA8_DISPOSABLE") != "1":
        raise IsolationGateError("modo descartável Beta 8 não foi explicitamente ativado")
    run_id = os.environ.get("BETA8_RUN_ID", "")
    container_id = os.environ.get("BETA8_DOCKER_CONTAINER_ID", "")
    network_id = os.environ.get("BETA8_DOCKER_NETWORK_ID", "")
    if (
        not RUN_ID_RE.fullmatch(run_id)
        or os.environ.get("BETA8_DOCKER_PRECHECKED") != "true"
        or not DOCKER_ID_RE.fullmatch(container_id)
        or not DOCKER_ID_RE.fullmatch(network_id)
    ):
        raise IsolationGateError("preflight de propriedade Beta 8 está ausente ou inválido")
    if os.environ.get("BETA8_MONGO_HOST") != "mongo" or os.environ.get("BETA8_MONGO_PORT") != "27017":
        raise IsolationGateError("o runner aceita somente o MongoDB privado do Compose Beta 8")
    if any(os.environ.get(name) for name in _FORBIDDEN_ENV):
        raise IsolationGateError("configuração de conexão externa foi detectada; execução recusada")
    username = os.environ.get("BETA8_ROOT_USERNAME", "")
    password = os.environ.get("BETA8_ROOT_PASSWORD", "")
    if username != "beta8-root" or not re.fullmatch(r"[a-f0-9]{64}", password):
        raise IsolationGateError("credencial efêmera de provisionamento Beta 8 inválida")
    return run_id, container_id, network_id, password


def _root_uri(password: str, *, replica: bool) -> str:
    suffix = "&replicaSet=rsB8" if replica else "&directConnection=true"
    return (
        "mongodb://beta8-root:" + quote(password, safe="")
        + "@mongo:27017/admin?authSource=admin" + suffix
        + "&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
    )


def _verify_uri(uri: str, *, replica: bool) -> None:
    parsed = parse_uri(uri)
    expected_options = parsed.get("options", {})
    if (
        parsed.get("nodelist") != [("mongo", 27017)]
        or parsed.get("username") != "beta8-root"
        or not parsed.get("password")
        or parsed.get("database") != "admin"
        or expected_options.get("authSource") != "admin"
        or (replica and expected_options.get("replicaSet") != REPLICA_SET)
        or (replica and expected_options.get("directConnection") is True)
        or (not replica and expected_options.get("directConnection") is not True)
    ):
        raise IsolationGateError("URI não corresponde ao serviço Mongo privado Beta 8")


def _privilege(db_name: str, collection: str, actions: list[str]) -> dict:
    return {"resource": {"db": db_name, "collection": collection}, "actions": actions}


async def _create_role(db: Any, name: str, privileges: list[dict]) -> None:
    await db.command({"createRole": name, "privileges": privileges, "roles": []})


async def _create_user(db: Any, name: str, role: str) -> str:
    password = secrets.token_hex(32)
    await db.command(
        "createUser", name, pwd=password, roles=[{"role": role, "db": db.name}]
    )
    return password


def _client_uri(username: str, password: str, db_name: str) -> str:
    return (
        f"mongodb://{quote(username, safe='')}:{quote(password, safe='')}@mongo:27017/"
        f"{db_name}?authSource={db_name}&replicaSet={REPLICA_SET}"
        "&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
    )


async def _wait_for_primary(client: Any) -> None:
    for _ in range(60):
        try:
            hello = await client.admin.command({"hello": 1})
            if hello.get("setName") == REPLICA_SET and hello.get("isWritablePrimary") is True:
                return
        except Exception:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)
    raise IsolationGateError("replica set Beta 8 não elegeu primary dentro do prazo")


async def run_persistent_proof() -> None:
    run_id, _container_id, _network_id, root_password = _configuration()
    initial_uri = _root_uri(root_password, replica=False)
    _verify_uri(initial_uri, replica=False)
    direct: Any = AsyncMongoClient(
        initial_uri, appname="trilhacode-beta8-bootstrap", tz_aware=True
    )
    root: Any = None
    clients: list[Any] = [direct]
    db: Any = None
    db_name = f"{DB_PREFIX}{run_id[:12]}_{uuid.uuid4().hex[:8]}"
    marker = secrets.token_urlsafe(32)
    marker_written = False
    try:
        build = await direct.server_info()
        if not str(build.get("version", "")).startswith("7."):
            raise IsolationGateError("servidor não é MongoDB 7")
        try:
            await direct.admin.command({"replSetGetStatus": 1})
        except OperationFailure as exc:
            if exc.code not in {94, 93}:
                raise
            await direct.admin.command({
                "replSetInitiate": {
                    "_id": REPLICA_SET,
                    "members": [{"_id": 0, "host": "mongo:27017"}],
                }
            })
        await direct.close()

        replica_uri = _root_uri(root_password, replica=True)
        _verify_uri(replica_uri, replica=True)
        root = AsyncMongoClient(replica_uri, appname="trilhacode-beta8-provisioner", tz_aware=True)
        clients.append(root)
        await _wait_for_primary(root)
        hello = await root.admin.command({"hello": 1})
        status = await root.admin.command({"serverStatus": 1})
        if (
            hello.get("setName") != REPLICA_SET
            or hello.get("logicalSessionTimeoutMinutes") is None
            or status.get("storageEngine", {}).get("name") != "wiredTiger"
        ):
            raise IsolationGateError("MongoDB Beta 8 não atende ao contrato transacional verificado")
        if db_name in await root.list_database_names():
            raise IsolationGateError("nome aleatório de banco já existe; reutilização recusada")

        db = root[db_name]
        await db["_beta8_harness_identity"].insert_one({
            "_id": "owner",
            "phase": "beta8",
            "run_id": run_id,
            "marker": marker,
            "purpose": "isolated-editorial-security-proof",
        })
        marker_written = True
        await db["content_blocks"].insert_one({
            "_id": "beta8-block-synthetic-1",
            "track_id": "beta8-track-synthetic-demo",
            "editorial_state": "draft",
            "title": "synthetic original",
            "body": "synthetic body",
        })

        authority_privileges: list[dict] = []
        for collection, actions in {
            "c8_beta8_tracks": ["find", "insert", "update", "createIndex"],
            "c8_beta8_operations": ["find", "insert", "update", "createIndex"],
            "c8_beta8_history": ["find", "insert", "createIndex"],
            "c8_beta8_writers": ["find", "insert", "update", "createIndex"],
            "c8_beta8_authorities": ["find", "insert", "update", "createIndex"],
            "c12_iam_principals": ["find", "insert", "update"],
            "c12_iam_sessions": ["find", "insert", "update"],
            "c12_track_grants": ["find", "insert", "update"],
            "content_blocks": ["find", "update"],
            "_beta8_editorial_audit": ["insert"],
            "_beta8_authorization_audit": ["insert"],
            "_beta8_experimental_generations": ["find", "insert"],
            "_beta8_experimental_heads": ["find", "insert", "update"],
            "_beta8_promotion_audit": ["insert"],
        }.items():
            authority_privileges.append(_privilege(db_name, collection, actions))
        await _create_role(db, "beta8_editorial_authority", authority_privileges)
        await _create_role(db, "beta8_runtime_read", [
            _privilege(db_name, "content_blocks", ["find"]),
            _privilege(db_name, "_beta8_experimental_generations", ["find"]),
            _privilege(db_name, "_beta8_experimental_heads", ["find"]),
        ])
        await _create_role(db, "beta8_preparation", [
            _privilege(db_name, "_beta8_staging_batches", ["find", "insert", "update"]),
            _privilege(db_name, "_beta8_staging_records", ["find", "insert", "update"]),
        ])
        authority_password = await _create_user(db, "beta8-editorial-authority", "beta8_editorial_authority")
        runtime_password = await _create_user(db, "beta8-runtime", "beta8_runtime_read")
        preparation_password = await _create_user(db, "beta8-preparer", "beta8_preparation")

        authority_client: Any = AsyncMongoClient(
            _client_uri("beta8-editorial-authority", authority_password, db_name),
            appname="trilhacode-beta8-editorial-authority",
            tz_aware=True,
        )
        runtime_client: Any = AsyncMongoClient(
            _client_uri("beta8-runtime", runtime_password, db_name),
            appname="trilhacode-beta8-runtime-read",
            tz_aware=True,
        )
        preparation_client: Any = AsyncMongoClient(
            _client_uri("beta8-preparer", preparation_password, db_name),
            appname="trilhacode-beta8-preparer",
            tz_aware=True,
        )
        clients.extend((authority_client, runtime_client, preparation_client))
        authority_db = authority_client[db_name]
        runtime_db = runtime_client[db_name]
        preparation_db = preparation_client[db_name]

        await runtime_db.content_blocks.find_one({"_id": "beta8-block-synthetic-1"})
        await _expect_operation_denied(
            runtime_db.content_blocks.update_one(
                {"_id": "beta8-block-synthetic-1"}, {"$set": {"title": "direct bypass"}}
            )
        )
        await _expect_operation_denied(
            runtime_db.activity_publications.insert_one({"_id": "should-not-exist"})
        )
        await preparation_db["_beta8_staging_records"].insert_one(
            {"_id": "synthetic-prepared-record", "batch_id": "synthetic"}
        )
        await _expect_operation_denied(
            preparation_db.content_blocks.update_one(
                {"_id": "beta8-block-synthetic-1"}, {"$set": {"title": "prep bypass"}}
            )
        )
        await _expect_operation_denied(
            preparation_db["_beta8_experimental_heads"].insert_one({"_id": "no-promotion"})
        )

        adapter = AsyncEditorialRevisionAdapter(authority_db, namespace="c8_beta8")
        await adapter.verify_transaction_topology()
        await adapter.initialize_track("beta8-track-synthetic-demo")
        writer_credential = await adapter.provision_writer_credential(
            "beta8-track-synthetic-demo", "beta8-authority-writer"
        )
        fence_authority = await adapter.provision_fence_authority(
            "beta8-track-synthetic-demo", "beta8-fence-authority"
        )
        fence = await adapter.advance_fence("beta8-track-synthetic-demo", fence_authority)
        iam = MongoEditorialIAMAuthority(
            authority_db,
            capability_key=secrets.token_bytes(32),
        )
        session_id = "beta8-session-" + uuid.uuid4().hex
        actor_id = "beta8-editor-synthetic"
        await iam.provision_principal(actor_id=actor_id, role="editor")
        await iam.provision_session(actor_id=actor_id, session_id=session_id)
        await iam.provision_grant(EditorialTrackGrant(
            actor_id=actor_id,
            track_id="beta8-track-synthetic-demo",
            allowed_operations=("block.update", "content.publish"),
            granted_by="beta8-admin-synthetic",
            granted_at=datetime.now(timezone.utc),
        ))
        boundary = Beta8EditorialMutationBoundary(
            authority_db, iam, adapter, writer_credential, fence
        )

        update = await boundary.prepare_draft_block_update(
            actor_id=actor_id,
            session_id=session_id,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-edit-0001",
            expected_revision=0,
            changes={"title": "synthetic authorized edit"},
        )
        receipt = await boundary.commit_draft_block_update(
            update, actor_id=actor_id, session_id=session_id
        )
        replay = await boundary.commit_draft_block_update(
            update, actor_id=actor_id, session_id=session_id
        )
        assert receipt.revision == 1 and replay.replayed is True
        assert (await authority_db.content_blocks.find_one({"_id": "beta8-block-synthetic-1"}))["title"] == "synthetic authorized edit"
        assert await db["_beta8_editorial_audit"].count_documents({}) == 1
        assert await authority_db["c8_beta8_history"].count_documents({}) == 1

        publisher_id = "beta8-publisher-synthetic"
        publisher_session = "beta8-session-" + uuid.uuid4().hex
        await iam.provision_principal(actor_id=publisher_id, role="editor")
        await iam.provision_session(actor_id=publisher_id, session_id=publisher_session)
        await iam.provision_grant(EditorialTrackGrant(
            actor_id=publisher_id,
            track_id="beta8-track-synthetic-demo",
            allowed_operations=("block.update", "content.publish"),
            granted_by="beta8-admin-synthetic",
            granted_at=datetime.now(timezone.utc),
        ))

        candidate = make_synthetic_candidate(
            track_id="beta8-track-synthetic-demo",
            records=[{"id": "synthetic-node-1", "kind": "node", "title": "Synthetic"}],
        )
        intent = ExperimentalPromotionIntent(
            batch_id=candidate.batch_id,
            payload_sha256=candidate.payload_sha256,
            track_id=candidate.track_id,
            generation_id="beta8-generation-synthetic-1",
            operation_id="beta8-op-synthetic-promotion-0001",
            expected_revision=1,
            fencing_token=fence,
            candidate_state=ExperimentalCandidateState.VALIDATED,
            approval=ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED,
            target_namespace="beta8_experimental",
        )
        promoter = Beta8ExperimentalPromoter(
            authority_db, iam, adapter, writer_credential
        )
        promoted = await promoter.promote(
            candidate, intent, actor_id=publisher_id, session_id=publisher_session
        )
        promotion_replay = await promoter.promote(
            candidate, intent, actor_id=publisher_id, session_id=publisher_session
        )
        assert promoted.revision == 2 and promotion_replay.replayed is True
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 1
        assert await authority_db["_beta8_experimental_heads"].count_documents({}) == 1
        assert await db["_beta8_promotion_audit"].count_documents({}) == 1
        assert await db["activity_publications"].count_documents({}) == 0
        assert await db["track_publications"].count_documents({}) == 0
        assert await db["tracks"].count_documents({}) == 0

        candidate_a = make_synthetic_candidate(
            track_id="beta8-track-synthetic-demo",
            records=[{"id": "synthetic-node-a", "kind": "node", "title": "A"}],
        )
        candidate_b = make_synthetic_candidate(
            track_id="beta8-track-synthetic-demo",
            records=[{"id": "synthetic-node-b", "kind": "node", "title": "B"}],
        )

        def next_intent(candidate, generation_id: str, operation_id: str):
            return ExperimentalPromotionIntent(
                batch_id=candidate.batch_id,
                payload_sha256=candidate.payload_sha256,
                track_id=candidate.track_id,
                generation_id=generation_id,
                operation_id=operation_id,
                expected_revision=2,
                fencing_token=fence,
                candidate_state=ExperimentalCandidateState.VALIDATED,
                approval=ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED,
                target_namespace="beta8_experimental",
            )

        promotion_race = await asyncio.gather(
            promoter.promote(
                candidate_a,
                next_intent(candidate_a, "beta8-generation-synthetic-a", "beta8-op-synthetic-promote-a"),
                actor_id=publisher_id,
                session_id=publisher_session,
                expected_previous_generation="beta8-generation-synthetic-1",
            ),
            promoter.promote(
                candidate_b,
                next_intent(candidate_b, "beta8-generation-synthetic-b", "beta8-op-synthetic-promote-b"),
                actor_id=publisher_id,
                session_id=publisher_session,
                expected_previous_generation="beta8-generation-synthetic-1",
            ),
            return_exceptions=True,
        )
        assert sum(not isinstance(value, BaseException) for value in promotion_race) == 1
        assert sum(isinstance(value, RevisionConflict) for value in promotion_race) == 1
        winner_generation = await authority_db["_beta8_experimental_heads"].find_one(
            {"_id": "beta8-track-synthetic-demo"}
        )
        assert winner_generation["generation_id"] in {
            "beta8-generation-synthetic-a", "beta8-generation-synthetic-b"
        }
        assert await authority_db["_beta8_experimental_generations"].count_documents({}) == 2
        assert await db["_beta8_promotion_audit"].count_documents({}) == 2

        denied_intent = ExperimentalPromotionIntent.model_validate(
            intent.model_dump()
            | {
                "generation_id": "beta8-generation-synthetic-denied",
                "operation_id": "beta8-op-synthetic-promotion-denied",
                "expected_revision": 3,
            }
        )
        with _expect_exception(EditorialMutationDenied):
            await promoter.promote(
                candidate,
                denied_intent,
                actor_id="beta8-ungranted-synthetic",
                session_id="beta8-session-" + uuid.uuid4().hex,
            )
        assert await db["_beta8_authorization_audit"].count_documents({"result": "denied"}) == 1

        second_candidate = make_synthetic_candidate(
            track_id="beta8-track-synthetic-demo",
            records=[{"id": "synthetic-node-2", "kind": "node", "title": "Other"}],
        )
        divergent_intent = ExperimentalPromotionIntent.model_validate(
            intent.model_dump()
            | {
                "batch_id": second_candidate.batch_id,
                "payload_sha256": second_candidate.payload_sha256,
                "generation_id": "beta8-generation-synthetic-2",
                "expected_revision": 1,
            }
        )
        with _expect_exception(RevisionConflict, IdempotencyConflict):
            await promoter.promote(
                second_candidate,
                divergent_intent,
                actor_id=publisher_id,
                session_id=publisher_session,
            )

        # A revoked grant after preparation must fail at the transaction guard.
        revoke_actor = "beta8-revocation-synthetic"
        revoke_session = "beta8-session-" + uuid.uuid4().hex
        await iam.provision_principal(actor_id=revoke_actor, role="editor")
        await iam.provision_session(actor_id=revoke_actor, session_id=revoke_session)
        await iam.provision_grant(EditorialTrackGrant(
            actor_id=revoke_actor,
            track_id="beta8-track-synthetic-demo",
            allowed_operations=("block.update",),
            granted_by="beta8-admin-synthetic",
            granted_at=datetime.now(timezone.utc),
        ))
        pending = await boundary.prepare_draft_block_update(
            actor_id=revoke_actor,
            session_id=revoke_session,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-revoked-edit",
            expected_revision=3,
            changes={"title": "must not commit"},
        )
        assert await iam.revoke_grant(
            actor_id=revoke_actor,
            track_id="beta8-track-synthetic-demo",
            revoked_by="beta8-admin-synthetic",
        )
        with _expect_exception(EditorialMutationDenied):
            await boundary.commit_draft_block_update(
                pending, actor_id=revoke_actor, session_id=revoke_session
            )
        assert (await authority_db.content_blocks.find_one({"_id": "beta8-block-synthetic-1"}))["title"] == "synthetic authorized edit"

        # Pause after the service's final request-level authorization but
        # before C10 opens its transaction; a committed revocation must win.
        class CommitBarrierAdapter:
            def __init__(self, delegate):
                self._delegate = delegate
                self.entered = asyncio.Event()
                self.release = asyncio.Event()

            def __getattr__(self, name):
                return getattr(self._delegate, name)

            async def commit(
                self,
                prepared: Any,
                credential: Any,
                *,
                participant: Any = None,
            ) -> Any:
                self.entered.set()
                await self.release.wait()
                return await self._delegate.commit(
                    prepared, credential, participant=participant
                )

        race_actor = "beta8-revocation-race-synthetic"
        race_session = "beta8-session-" + uuid.uuid4().hex
        await iam.provision_principal(actor_id=race_actor, role="editor")
        await iam.provision_session(actor_id=race_actor, session_id=race_session)
        await iam.provision_grant(EditorialTrackGrant(
            actor_id=race_actor,
            track_id="beta8-track-synthetic-demo",
            allowed_operations=("block.update",),
            granted_by="beta8-admin-synthetic",
            granted_at=datetime.now(timezone.utc),
        ))
        barrier_adapter = CommitBarrierAdapter(adapter)
        barrier_boundary = Beta8EditorialMutationBoundary(
            authority_db,
            iam,
            cast(AsyncEditorialRevisionAdapter, barrier_adapter),
            writer_credential,
            fence,
        )
        revocation_race = await barrier_boundary.prepare_draft_block_update(
            actor_id=race_actor,
            session_id=race_session,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-revocation-race",
            expected_revision=3,
            changes={"title": "revoked before commit must not land"},
        )
        commit_task = asyncio.create_task(
            barrier_boundary.commit_draft_block_update(
                revocation_race, actor_id=race_actor, session_id=race_session
            )
        )
        await asyncio.wait_for(barrier_adapter.entered.wait(), timeout=10)
        assert await iam.revoke_grant(
            actor_id=race_actor,
            track_id="beta8-track-synthetic-demo",
            revoked_by="beta8-admin-synthetic",
        )
        barrier_adapter.release.set()
        with _expect_exception(EditorialMutationDenied):
            await commit_task
        assert await adapter.current_revision("beta8-track-synthetic-demo") == 3
        assert (await authority_db.content_blocks.find_one(
            {"_id": "beta8-block-synthetic-1"}
        ))["title"] == "synthetic authorized edit"

        # Two independent tasks contend on the same C8 track revision.
        p1 = await boundary.prepare_draft_block_update(
            actor_id=publisher_id,
            session_id=publisher_session,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-race-1",
            expected_revision=3,
            changes={"title": "race one"},
        )
        p2 = await boundary.prepare_draft_block_update(
            actor_id=publisher_id,
            session_id=publisher_session,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-race-2",
            expected_revision=3,
            changes={"title": "race two"},
        )
        outcomes = await asyncio.gather(
            boundary.commit_draft_block_update(p1, actor_id=publisher_id, session_id=publisher_session),
            boundary.commit_draft_block_update(p2, actor_id=publisher_id, session_id=publisher_session),
            return_exceptions=True,
        )
        assert sum(not isinstance(value, BaseException) for value in outcomes) == 1, outcomes
        assert sum(isinstance(value, RevisionConflict) for value in outcomes) == 1, outcomes
        assert await adapter.current_revision("beta8-track-synthetic-demo") == 4
        assert await authority_db["c8_beta8_history"].count_documents({}) == 4

        # Fence the already-prepared writer; the stale writer cannot commit.
        stale = await boundary.prepare_draft_block_update(
            actor_id=publisher_id,
            session_id=publisher_session,
            block_id="beta8-block-synthetic-1",
            operation_id="beta8-op-synthetic-stale-fence",
            expected_revision=4,
            changes={"title": "stale fence must not commit"},
        )
        await adapter.advance_fence(
            "beta8-track-synthetic-demo",
            fence_authority,
        )
        with _expect_exception(FencingRejected):
            await boundary.commit_draft_block_update(
                stale, actor_id=publisher_id, session_id=publisher_session
            )
        assert (await authority_db.content_blocks.find_one({"_id": "beta8-block-synthetic-1"}))["title"] in {"race one", "race two"}

        collections = set(await db.list_collection_names())
        forbidden = {
            "tracks", "nodes", "relations", "activity_publications", "track_publications",
            "progress", "activity_attempts", "submissions",
        }
        assert not (collections & forbidden), collections
        print("BETA8_GATE: PASS; MongoDB 7 replica set, owner, network and tmpfs preflight accepted")
        print("BETA8_DB_ROLE: PASS; runtime and preparer writes denied by MongoDB")
        print("BETA8_AUTHORITY: PASS; scoped grant, C8/C10 CAS, fence, audit and replay")
        print("BETA8_PROMOTION: PASS; synthetic generation isolated from operational collections")
        print("BETA8_CONCURRENCY: PASS; post-authorization revocation, stale fence and competing CAS exercised")
    finally:
        for client in reversed(clients):
            if client is root:
                continue
            try:
                await client.close()
            except Exception:
                pass
        if root is not None and db is not None and marker_written:
            proof = await root[db_name]["_beta8_harness_identity"].find_one({"_id": "owner"})
            if proof != {
                "_id": "owner",
                "phase": "beta8",
                "run_id": run_id,
                "marker": marker,
                "purpose": "isolated-editorial-security-proof",
            }:
                raise IsolationGateError("marcador Beta 8 divergiu; limpeza do banco recusada")
            await root.drop_database(db_name)
            if db_name in await root.list_database_names():
                raise IsolationGateError("banco Beta 8 permaneceu após limpeza verificada")
        if root is not None:
            await root.close()


async def _expect_operation_denied(awaitable: Awaitable[Any]) -> None:
    try:
        await awaitable
    except OperationFailure:
        return
    raise AssertionError("MongoDB permitiu uma escrita fora do privilégio previsto")


class _expect_exception:
    def __init__(self, *types: type[BaseException]) -> None:
        self.types = types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, _traceback):
        if exc_type is None or not issubclass(exc_type, self.types):
            raise AssertionError(f"esperava {self.types}, recebi {exc_type}: {exc}")
        return True


if __name__ == "__main__":
    asyncio.run(run_persistent_proof())
