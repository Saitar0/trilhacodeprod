"""Separate Beta 8.3 authority process; never mounted by normal startup."""

from __future__ import annotations

import os
import re
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from pymongo.uri_parser import parse_uri


def _preflight() -> tuple[str, bytes, bytes, str, str, str, str]:
    if (
        os.environ.get("BETA8_3_TEST_AUTHORITY") != "1"
        or os.environ.get("BETA8_3_DISPOSABLE") != "1"
    ):
        raise RuntimeError("autoridade Beta 8.3 exige composição experimental explícita")
    if any(name in os.environ for name in (
        "BETA8_3_API_MONGO_URI", "BETA8_3_API_MONGO_PASSWORD", "MONGO_URL_API",
        "BETA8_3_STAGE_WRITE_URI", "BETA8_3_STAGE_WRITE_PASSWORD",
    )):
        raise RuntimeError("autoridade não aceita credencial MongoDB da API")
    uri = os.environ.get("MONGO_URL", "")
    database = os.environ.get("DB_NAME", "")
    parsed = urlsplit(uri)
    if (
        parsed.scheme != "mongodb"
        or parsed.hostname != "mongo"
        or parsed.port != 27017
        or parsed.username != "beta8-3-authority"
        or not parsed.password
        or parsed.path.removeprefix("/") != database
        or not database.startswith("editorial_revision_test_c10_c11_c12_b83_")
    ):
        raise RuntimeError("autoridade sem URI Mongo explícita e restrita ao harness")
    try:
        options = parse_uri(uri).get("options", {})
        secret = bytes.fromhex(os.environ["BETA8_3_SERVICE_SECRET_HEX"])
        stager_secret = bytes.fromhex(os.environ["BETA8_3_STAGER_SECRET_HEX"])
    except (KeyError, ValueError) as exc:
        raise RuntimeError("segredo interno da autoridade Beta 8.3 ausente") from exc
    if (
        options.get("replicaSet") != "rsB83"
        or options.get("authSource") != database
        or min(len(secret), len(stager_secret)) < 32
    ):
        raise RuntimeError("configuração de autoridade Beta 8.3 incompleta")
    stage_uri = os.environ.get("BETA8_3_STAGE_READ_URI", "")
    stage_run_id = os.environ.get("BETA8_3_STAGE_RUN_ID", "")
    stage_owner_token = os.environ.get("BETA8_3_STAGE_OWNER_TOKEN", "")
    stage = urlsplit(stage_uri)
    try:
        stage_options = parse_uri(stage_uri).get("options", {})
    except ValueError as exc:
        raise RuntimeError("URI de staging restrito inválida") from exc
    if (
        stage.scheme != "mongodb" or stage.hostname != "mongo" or stage.port != 27017
        or stage.username != "beta8-3-stage-reader"
        or stage.path.removeprefix("/") != f"beta5_{stage_run_id}"
        or not re.fullmatch(r"[0-9a-f]{32}", stage_run_id)
        or stage_options.get("replicaSet") != "rsB83"
        or stage_options.get("authSource") != f"beta5_{stage_run_id}"
        or len(stage_owner_token) < 32
    ):
        raise RuntimeError("identidade de leitura do staging Beta 8.3 inválida")
    track_id = os.environ.get("BETA8_3_TRACK_ID", "")
    if not re.fullmatch(r"beta8-track-synthetic-[A-Za-z0-9_-]{1,32}", track_id):
        raise RuntimeError("escopo sintético da autoridade não foi definido")
    return database, secret, stager_secret, track_id, stage_uri, stage_run_id, stage_owner_token


(_database_name, _service_secret, _stager_secret, _track_id,
 _stage_read_uri, _stage_run_id, _stage_owner_token) = _preflight()

# Import application/database modules only after all fail-closed checks above.
from constants import PERMISSIONS  # noqa: E402
from database import client, db  # noqa: E402
from pymongo import AsyncMongoClient  # noqa: E402
from serialization import ser  # noqa: E402
from services.beta8_1_runtime_iam import (  # noqa: E402
    AuthenticatedEditorialIdentity,
    Beta8_1RuntimeIAMBridge,
)
from services.beta8_editorial_enforcement import (  # noqa: E402
    Beta8EditorialMutationBoundary,
    DraftBlockNotFound,
    EditorialMutationDenied,
)
from services.beta8_1_staging_authority import (  # noqa: E402
    Beta8_1StagingAuthorityBridge,
    StagingAuthorityError,
)
from services.beta8_curriculum_promotion import (  # noqa: E402
    Beta8ExperimentalPromoter,
    ExperimentalPromotionConflict,
)
from services.beta_curriculum_staging import (  # noqa: E402
    CurriculumStagingService,
)
from services.beta8_3_internal_protocol import (  # noqa: E402
    EditorialMutationCommand,
    StagingTransitionCommand,
    response_signature,
    verify_request_signature,
)
from curriculum_contract.editorial_revision_protocol import (  # noqa: E402
    FencingRejected,
    IdempotencyConflict,
    RevisionConflict,
)
from curriculum_contract.experimental_async_editorial_adapter import (  # noqa: E402
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.mongodb_editorial_revision_adapter import CommitOutcomeUnknown  # noqa: E402
from curriculum_contract.experimental_editorial_iam_authority import (  # noqa: E402
    MongoEditorialIAMAuthority,
)
from security import account_is_active  # noqa: E402
from services.sessions import session_id_digest  # noqa: E402
from curriculum_contract.beta8_promotion_contract import (  # noqa: E402
    ExperimentalApproval,
    ExperimentalCandidateState,
    ExperimentalPromotionIntent,
    PromotionContractError,
)

_MAX_CLOCK_SKEW_SECONDS = 60
_MAX_BODY_BYTES = 120_000
_NONCE = re.compile(r"^[0-9a-f]{48}$")
_stage_client = AsyncMongoClient(_stage_read_uri, appname="beta8-3-authority-stage-reader", tz_aware=True)


class AuthorityRuntime:
    def __init__(self, boundary, iam_bridge, staging_bridge, fencing_token: int) -> None:
        self.boundary = boundary
        self.iam_bridge = iam_bridge
        self.staging_bridge = staging_bridge
        self.fencing_token = fencing_token


async def _build_runtime() -> AuthorityRuntime:
    adapter = AsyncEditorialRevisionAdapter(db, namespace="c8_beta8_1")
    await adapter.verify_transaction_topology()
    await adapter.initialize_track(_track_id)
    writer_credential = await adapter.provision_writer_credential(
        _track_id, "beta8-3-separated-authority",
    )
    fence_authority = await adapter.provision_fence_authority(
        _track_id, "beta8-3-separated-fence",
    )
    fencing_token = await adapter.advance_fence(_track_id, fence_authority)
    iam = MongoEditorialIAMAuthority(db, capability_key=os.urandom(32))
    boundary = Beta8EditorialMutationBoundary(
        db, iam, adapter, writer_credential, fencing_token,
    )
    promoter = Beta8ExperimentalPromoter(db, iam, adapter, writer_credential)
    staging = CurriculumStagingService(
        _stage_client[f"beta5_{_stage_run_id}"],
        execution_id=_stage_run_id,
        owner_token=_stage_owner_token,
    )
    staging_bridge = Beta8_1StagingAuthorityBridge(
        staging, promoter, track_id=_track_id,
    )
    await db["_beta8_3_rpc_nonces"].create_index(
        "expires_at", expireAfterSeconds=0, name="beta8_3_rpc_nonce_expiry",
    )
    return AuthorityRuntime(
        boundary, Beta8_1RuntimeIAMBridge(db), staging_bridge, fencing_token,
    )


@asynccontextmanager
async def _lifespan(app: FastAPI):
    await db.command("ping")
    app.state.authority_runtime = await _build_runtime()
    try:
        yield
    finally:
        await _stage_client.close()
        await client.close()


app = FastAPI(title="Beta 8.3 isolated editorial authority", lifespan=_lifespan,
              docs_url=None, redoc_url=None, openapi_url=None)


@app.exception_handler(RequestValidationError)
async def _validation_error(_request: Request, _exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": "invalid_command"})


async def _verify_service_request(
    request: Request,
    *,
    expected_service: str,
    secret: bytes,
) -> str:
    service_id = request.headers.get("X-Beta8-Service", "")
    timestamp = request.headers.get("X-Beta8-Timestamp", "")
    nonce = request.headers.get("X-Beta8-Nonce", "")
    signature = request.headers.get("X-Beta8-Signature", "")
    if service_id != expected_service or not timestamp.isdecimal() or not _NONCE.fullmatch(nonce):
        raise HTTPException(status_code=401, detail="Autenticação interna inválida")
    issued_at = int(timestamp)
    if abs(int(time.time()) - issued_at) > _MAX_CLOCK_SKEW_SECONDS:
        raise HTTPException(status_code=401, detail="Autenticação interna inválida")
    body = await request.body()
    if len(body) > _MAX_BODY_BYTES or not verify_request_signature(
        secret,
        signature,
        service_id=service_id,
        method=request.method,
        path=request.url.path,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
    ):
        raise HTTPException(status_code=401, detail="Autenticação interna inválida")
    try:
        await db["_beta8_3_rpc_nonces"].insert_one({
            "_id": nonce,
            "service_id": service_id,
            "issued_at": datetime.fromtimestamp(issued_at, tz=UTC),
            "expires_at": datetime.now(UTC) + timedelta(minutes=2),
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=401, detail="Autenticação interna inválida") from None
    except Exception:
        # A replay ledger outage is a hard denial, never an allow.
        raise HTTPException(status_code=503, detail="Autoridade temporariamente indisponível") from None
    return nonce


async def _resolve_actor(
    assertion, *, required_permission: str = "content.write",
) -> tuple[dict, AuthenticatedEditorialIdentity]:
    if not ObjectId.is_valid(assertion.actor_id):
        raise HTTPException(status_code=403, detail="Ação editorial negada")
    user_document = await db.users.find_one({"_id": ObjectId(assertion.actor_id)})
    digest = session_id_digest(assertion.session_id)
    active_session = await db.auth_sessions.find_one({
        "_id": digest,
        "user_id": assertion.actor_id,
        "revoked_at": None,
        "expires_at": {"$gt": datetime.now(UTC)},
    }, {"_id": 1})
    if (
        user_document is None
        or not account_is_active(user_document)
        or user_document.get("email_verified") is False
        or type(user_document.get("token_version", 0)) is not int
        or user_document.get("token_version", 0) != assertion.token_version
        or active_session is None
    ):
        raise HTTPException(status_code=401, detail="Sessão inválida")
    user = ser(user_document)
    user["permissions"] = sorted(PERMISSIONS.get(user.get("role"), set()))
    identity = AuthenticatedEditorialIdentity(
        actor_id=assertion.actor_id,
        role=user["role"],
        token_version=assertion.token_version,
        session_id=assertion.session_id,
    )
    try:
        await app.state.authority_runtime.iam_bridge.require_matching_projection(
            identity, user, required_permission=required_permission,
        )
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail="Ação editorial negada") from None
    return user, identity


def _error_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        status = exc.status_code if exc.status_code in {401, 403, 404, 409, 503} else 500
        code = {
            401: "session_invalid",
            403: "authorization_denied",
            404: "resource_unavailable",
            409: "state_conflict",
            503: "authority_unavailable",
        }.get(status, "internal_error")
        return JSONResponse(status_code=status, content={"code": code})
    if isinstance(exc, EditorialMutationDenied):
        return JSONResponse(status_code=403, content={"code": "authorization_denied"})
    if isinstance(exc, DraftBlockNotFound):
        return JSONResponse(status_code=404, content={"code": "resource_unavailable"})
    if isinstance(exc, RevisionConflict):
        return JSONResponse(status_code=412, content={"code": "revision_conflict"})
    if isinstance(exc, IdempotencyConflict):
        return JSONResponse(status_code=409, content={"code": "idempotency_conflict"})
    if isinstance(exc, FencingRejected):
        return JSONResponse(status_code=409, content={"code": "fencing_conflict"})
    if isinstance(exc, (ExperimentalPromotionConflict,)):
        return JSONResponse(status_code=409, content={"code": "generation_conflict"})
    if isinstance(exc, StagingAuthorityError):
        return JSONResponse(status_code=409, content={"code": "staging_integrity_conflict"})
    if isinstance(exc, PromotionContractError):
        return JSONResponse(status_code=422, content={"code": "invalid_promotion"})
    if isinstance(exc, CommitOutcomeUnknown):
        return JSONResponse(status_code=503, content={"code": "commit_outcome_unknown"})
    if isinstance(exc, ValueError):
        return JSONResponse(status_code=422, content={"code": "invalid_command"})
    return JSONResponse(status_code=500, content={"code": "internal_error"})


@app.get("/internal/health")
async def _health():
    if not getattr(app.state, "authority_runtime", None):
        raise HTTPException(status_code=503, detail="Autoridade indisponível")
    return {"ok": True}


@app.post("/internal/v1/editorial/mutations", dependencies=[])
async def mutate_editorial(command: EditorialMutationCommand, request: Request):
    nonce = await _verify_service_request(
        request, expected_service="trilhacode-api", secret=_service_secret,
    )
    try:
        _, identity = await _resolve_actor(command.actor)
        boundary = app.state.authority_runtime.boundary
        guard = app.state.authority_runtime.iam_bridge.transaction_guard(identity)
        if command.operation == "block.update":
            prepared = await boundary.prepare_draft_block_update(
                actor_id=identity.actor_id,
                session_id=identity.session_id,
                block_id=ObjectId(command.block_id),
                operation_id=command.operation_id,
                expected_revision=command.expected_revision,
                changes=command.changes,
            )
            receipt = await boundary.commit_draft_block_update(
                prepared, actor_id=identity.actor_id, session_id=identity.session_id,
                transaction_guard=guard,
            )
        elif command.operation == "block.create":
            now = datetime.now(UTC)
            document = {
                "_id": ObjectId(command.block_id),
                "node_id": command.node_id,
                **command.block,
                "schema_version": 1,
                "created_by": identity.actor_id,
                "created_at": now,
                "updated_at": now,
            }
            node = await db.nodes.find_one({"_id": ObjectId(command.node_id)}, {"track_id": 1})
            if node is None:
                raise DraftBlockNotFound("unidade indisponível")
            document["track_id"] = node.get("track_id")
            prepared = await boundary.prepare_draft_block_create(
                actor_id=identity.actor_id,
                session_id=identity.session_id,
                node_id=command.node_id,
                block_id=ObjectId(command.block_id),
                operation_id=command.operation_id,
                expected_revision=command.expected_revision,
                document=document,
            )
            receipt = await boundary.commit_draft_block_create(
                prepared, actor_id=identity.actor_id, session_id=identity.session_id,
                transaction_guard=guard,
            )
        else:
            prepared = await boundary.prepare_draft_node_update(
                actor_id=identity.actor_id,
                session_id=identity.session_id,
                node_id=command.node_id,
                operation_id=command.operation_id,
                expected_revision=command.expected_revision,
                changes=command.changes,
            )
            receipt = await boundary.commit_draft_node_update(
                prepared, actor_id=identity.actor_id, session_id=identity.session_id,
                transaction_guard=guard,
            )
        result = {
            "track_id": receipt.track_id,
            "operation_id": receipt.operation_id,
            "writer_id": receipt.writer_id,
            "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "fencing_token": receipt.fencing_token,
            "payload_sha256": receipt.payload_sha256,
            "fingerprint": receipt.fingerprint,
            "replayed": receipt.replayed,
        }
        response = JSONResponse(status_code=200, content=result)
    except Exception as exc:
        response = _error_response(exc)
    response.headers["X-Beta8-Response-Signature"] = response_signature(
        _service_secret,
        request_nonce=nonce,
        status_code=response.status_code,
        body=response.body,
    )
    return response


@app.post("/internal/v1/staging/transitions", dependencies=[])
async def promote_staged_package(command: StagingTransitionCommand, request: Request):
    nonce = await _verify_service_request(
        request, expected_service="trilhacode-stager", secret=_stager_secret,
    )
    try:
        _, identity = await _resolve_actor(command.actor, required_permission="content.publish")
        bridge = app.state.authority_runtime.staging_bridge
        candidate = bridge.candidate_for(command.package)
        intent = ExperimentalPromotionIntent(
            batch_id=candidate.batch_id,
            payload_sha256=candidate.payload_sha256,
            track_id=candidate.track_id,
            generation_id=f"beta8-generation-synthetic-{candidate.payload_sha256[:32]}",
            operation_id=command.operation_id,
            expected_revision=command.expected_revision,
            fencing_token=app.state.authority_runtime.fencing_token,
            candidate_state=ExperimentalCandidateState.VALIDATED,
            approval=ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED,
            target_namespace="beta8_experimental",
        )
        receipt = await bridge.promote_prepared(
            command.package,
            intent,
            actor_id=identity.actor_id,
            session_id=identity.session_id,
            expected_previous_generation=command.expected_previous_generation,
            transaction_guard=app.state.authority_runtime.iam_bridge.transaction_guard(identity),
        )
        response = JSONResponse(status_code=200, content={
            "track_id": receipt.track_id,
            "operation_id": receipt.operation_id,
            "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "fencing_token": receipt.fencing_token,
            "replayed": receipt.replayed,
        })
    except Exception as exc:
        response = _error_response(exc)
    response.headers["X-Beta8-Response-Signature"] = response_signature(
        _stager_secret,
        request_nonce=nonce,
        status_code=response.status_code,
        body=response.body,
    )
    return response
