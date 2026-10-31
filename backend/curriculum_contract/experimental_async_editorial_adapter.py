"""Native-async C8-shape adapter for isolated C10 experiments only.

This is a deliberately small parallel implementation over the same C8
track/operation/history/writer/authority schema. It must not be imported by
the application runtime. Conformance tests are required because it is not the
sync adapter with an async facade.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import replace
from typing import Any, Awaitable, Callable, Mapping

from pymongo import AsyncMongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from .editorial_revision_protocol import (
    FenceAuthorityCredential,
    FenceAuthorityError,
    FencingRejected,
    IdempotencyConflict,
    InvalidPreparation,
    InvalidProposal,
    OperationAborted,
    OperationState,
    PreparedRevision,
    ProposalValidationError,
    RevisionConflict,
    RevisionReceipt,
    WriterAuthorizationError,
    WriterCredential,
    _freeze_json,
)
from .mongodb_editorial_revision_adapter import (
    CommitOutcomeUnknown,
    MongoTopology,
    RevisionSequenceExhausted,
    TrackNotInitialized,
    _canonical_payload,
    _compound_id,
    _fingerprint,
    _validate_identity,
)

_DATABASE = re.compile(r"^editorial_revision_test_c10_[a-zA-Z0-9_-]{8,48}$")
_NAMESPACE = re.compile(r"^c8_[a-z0-9_]{1,28}$")
_MAX_BSON_INT64 = (1 << 63) - 1
AsyncParticipant = Callable[[Any, RevisionReceipt], Awaitable[None]]


class AsyncEditorialAdapterError(RuntimeError):
    """Base class for the C10 async implementation."""


class AsyncMongoTopologyError(AsyncEditorialAdapterError):
    """C10 requires MongoDB 7 on a replica set with logical sessions."""


class AsyncEditorialRevisionAdapter:
    """Experimental AsyncMongoClient implementation of the C8 transaction.

    It shares C8 collection shapes and the single track revision/fence record.
    Its code is separate, so parity is limited to the tested contract surface.
    """

    def __init__(
        self,
        database: Any,
        *,
        namespace: str,
        proposal_validator: Callable[[Mapping[str, Any]], bool | None] | None = None,
        max_payload_bytes: int = 4 * 1024 * 1024,
    ) -> None:
        name = getattr(database, "name", None)
        client = getattr(database, "client", None)
        if not isinstance(name, str) or not _DATABASE.fullmatch(name):
            raise ValueError("async C10 adapter requires its disposable test database")
        if not isinstance(namespace, str) or not _NAMESPACE.fullmatch(namespace):
            raise ValueError("namespace must use the shared C8 namespace format")
        if not isinstance(client, AsyncMongoClient):
            raise TypeError("pass an explicit AsyncMongoClient database")
        if type(max_payload_bytes) is not int or not 1 <= max_payload_bytes <= 8 * 1024 * 1024:
            raise ValueError("max_payload_bytes is outside the supported range")
        self._client = client
        self._database_name = name
        self._database = database.with_options(
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        )
        self._namespace = namespace
        self._max_payload_bytes = max_payload_bytes
        self._proposal_validator = proposal_validator
        self._topology_verified = False
        self._tracks = self._database[f"{namespace}_tracks"]
        self._operations = self._database[f"{namespace}_operations"]
        self._history = self._database[f"{namespace}_history"]
        self._writers = self._database[f"{namespace}_writers"]
        self._authorities = self._database[f"{namespace}_authorities"]

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def namespace(self) -> str:
        return self._namespace

    async def verify_transaction_topology(self) -> MongoTopology:
        hello = await self._client.admin.command({"hello": 1})
        server = await self._client.server_info()
        version = str(server.get("version", ""))
        replica_set = hello.get("setName")
        sessions = hello.get("logicalSessionTimeoutMinutes") is not None
        if not version.startswith("7.") or not isinstance(replica_set, str) or not replica_set or not sessions:
            raise AsyncMongoTopologyError("MongoDB 7 replica-set sessions are required")
        self._topology_verified = True
        return MongoTopology(version, replica_set, sessions)

    def _require_topology(self) -> None:
        if not self._topology_verified:
            raise AsyncMongoTopologyError("verify topology before database operations")

    async def ensure_indexes(self) -> None:
        self._require_topology()
        await self._operations.create_index(
            [("track_id", 1), ("operation_id", 1)],
            unique=True,
            name=f"{self._namespace}_operation_identity",
        )
        await self._history.create_index(
            [("track_id", 1), ("revision", 1)],
            unique=True,
            name=f"{self._namespace}_track_revision",
        )
        await self._writers.create_index(
            [("track_id", 1), ("writer_id", 1)],
            unique=True,
            name=f"{self._namespace}_writer_identity",
        )
        await self._authorities.create_index(
            [("track_id", 1), ("authority_id", 1)],
            unique=True,
            name=f"{self._namespace}_authority_identity",
        )

    async def initialize_track(self, track_id: str) -> dict[str, int | str]:
        self._require_topology()
        _validate_identity(track_id, "track_id")
        await self.ensure_indexes()
        try:
            await self._tracks.insert_one(
                {
                    "_id": track_id,
                    "revision": 0,
                    "fencing_epoch": 0,
                    "control_sequence": 0,
                    "last_fence_sequence": 0,
                    "schema_version": 1,
                }
            )
        except DuplicateKeyError:
            pass
        document = await self._tracks.find_one({"_id": track_id})
        if document is None:
            raise TrackNotInitialized(track_id)
        return self._track_state(document)

    async def provision_writer_credential(self, track_id: str, writer_id: str) -> WriterCredential:
        self._require_topology()
        _validate_identity(track_id, "track_id")
        _validate_identity(writer_id, "writer_id")
        await self._require_track(track_id)
        secret = secrets.token_urlsafe(32)
        await self._writers.replace_one(
            {"_id": _compound_id(track_id, writer_id)},
            {
                "_id": _compound_id(track_id, writer_id),
                "track_id": track_id,
                "writer_id": writer_id,
                "secret_sha256": hashlib.sha256(secret.encode()).hexdigest(),
                "use_sequence": 0,
            },
            upsert=True,
        )
        return WriterCredential(track_id, writer_id, secret)

    async def provision_fence_authority(
        self, track_id: str, authority_id: str
    ) -> FenceAuthorityCredential:
        self._require_topology()
        _validate_identity(track_id, "track_id")
        _validate_identity(authority_id, "authority_id")
        await self._require_track(track_id)
        secret = secrets.token_urlsafe(32)
        key = _compound_id(track_id, authority_id)
        await self._authorities.replace_one(
            {"_id": key},
            {
                "_id": key,
                "track_id": track_id,
                "authority_id": authority_id,
                "secret_sha256": hashlib.sha256(secret.encode()).hexdigest(),
            },
            upsert=True,
        )
        return FenceAuthorityCredential(track_id, authority_id, secret)

    async def advance_fence(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> int:
        self._require_topology()
        _validate_identity(track_id, "track_id")
        await self._authenticate_authority(track_id, authority)
        state = await self._tracks.find_one_and_update(
            {
                "_id": track_id,
                "fencing_epoch": {"$lt": _MAX_BSON_INT64},
                "control_sequence": {"$lt": _MAX_BSON_INT64},
            },
            [
                {
                    "$set": {
                        "fencing_epoch": {"$add": ["$fencing_epoch", 1]},
                        "control_sequence": {"$add": ["$control_sequence", 1]},
                    }
                },
                {"$set": {"last_fence_sequence": "$control_sequence"}},
            ],
            return_document=ReturnDocument.AFTER,
        )
        if state is None:
            current = await self._tracks.find_one({"_id": track_id})
            if current is None:
                raise TrackNotInitialized(track_id)
            raise RevisionSequenceExhausted(f"fencing sequence exhausted for track {track_id!r}")
        return int(state["fencing_epoch"])

    async def prepare(
        self,
        *,
        track_id: str,
        credential: WriterCredential,
        operation_id: str,
        expected_revision: int,
        fencing_token: int,
        payload: Mapping[str, Any],
    ) -> PreparedRevision:
        self._require_topology()
        _validate_identity(track_id, "track_id")
        _validate_identity(operation_id, "operation_id")
        if type(expected_revision) is not int or expected_revision < 0 or expected_revision > _MAX_BSON_INT64:
            raise InvalidProposal("expected_revision must be a non-negative int64")
        if type(fencing_token) is not int or not 1 <= fencing_token <= _MAX_BSON_INT64:
            raise InvalidProposal("fencing_token must be a positive server token")
        if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
            raise WriterAuthorizationError("writer credential is outside track scope")
        canonical, digest, normalized = _canonical_payload(payload, self._max_payload_bytes)
        await self._authenticate_writer(track_id, credential)
        fingerprint = _fingerprint(track_id, credential.writer_id, operation_id, expected_revision, digest)
        query = {"track_id": track_id, "operation_id": operation_id}
        existing = await self._operations.find_one(query)
        if existing is not None:
            return await self._reuse_preparation(
                existing, track_id, credential.writer_id, operation_id,
                expected_revision, fencing_token, digest, fingerprint,
            )
        state = await self._require_track(track_id)
        self._assert_fence(track_id, fencing_token, int(state["fencing_epoch"]))
        if self._proposal_validator is not None:
            try:
                accepted = self._proposal_validator(_freeze_json(normalized))
            except Exception as exc:
                raise ProposalValidationError("proposal validator rejected payload") from exc
            if accepted is False:
                raise ProposalValidationError("proposal validator rejected payload")
        document = {
            "_id": _compound_id(track_id, operation_id),
            "track_id": track_id,
            "operation_id": operation_id,
            "writer_id": credential.writer_id,
            "expected_revision": expected_revision,
            "fencing_token": fencing_token,
            "payload_sha256": digest,
            "payload_json": canonical,
            "fingerprint": fingerprint,
            "preparation_id": secrets.token_hex(16),
            "state": OperationState.PREPARED.value,
            "schema_version": 1,
        }
        try:
            await self._operations.insert_one(document)
            return self._prepared(document)
        except DuplicateKeyError:
            existing = await self._operations.find_one(query)
            if existing is None:
                raise
            return await self._reuse_preparation(
                existing, track_id, credential.writer_id, operation_id,
                expected_revision, fencing_token, digest, fingerprint,
            )

    async def commit(
        self,
        prepared: PreparedRevision,
        credential: WriterCredential,
        *,
        participant: AsyncParticipant | None = None,
    ) -> RevisionReceipt:
        self._require_topology()
        if not isinstance(prepared, PreparedRevision):
            raise InvalidPreparation("prepared operation is invalid")
        await self._authenticate_writer(prepared.track_id, credential)
        if credential.writer_id != prepared.writer_id or credential.track_id != prepared.track_id:
            raise WriterAuthorizationError("credential does not own this preparation")
        key = {"track_id": prepared.track_id, "operation_id": prepared.operation_id}
        existing = await self._operations.find_one(key)
        if existing is None:
            raise InvalidPreparation("prepared operation was not found")
        self._assert_same_preparation(existing, prepared)
        if existing["state"] == OperationState.COMMITTED.value:
            return replace(self._receipt(existing), replayed=True)
        if existing["state"] == OperationState.ABORTED.value:
            raise OperationAborted("operation was abandoned")
        if existing["state"] == OperationState.CONFLICTED.value:
            raise RevisionConflict(
                prepared.track_id, prepared.operation_id, prepared.expected_revision,
                int(existing["conflict_actual_revision"]),
            )

        async def transaction_body(session: Any) -> dict[str, Any]:
            await self._authenticate_writer(prepared.track_id, credential, session=session)
            operation = await self._operations.find_one(key, session=session)
            if operation is None:
                raise InvalidPreparation("prepared operation disappeared")
            self._assert_same_preparation(operation, prepared)
            if operation["state"] == OperationState.COMMITTED.value:
                return {"receipt": self._receipt(operation), "replayed": True}
            if operation["state"] == OperationState.ABORTED.value:
                raise OperationAborted("operation was abandoned")
            if operation["state"] == OperationState.CONFLICTED.value:
                return {"error": RevisionConflict(
                    prepared.track_id, prepared.operation_id, prepared.expected_revision,
                    int(operation["conflict_actual_revision"]),
                )}
            track = await self._tracks.find_one({"_id": prepared.track_id}, session=session)
            if track is None:
                raise TrackNotInitialized(prepared.track_id)
            self._assert_fence(prepared.track_id, prepared.fencing_token, int(track["fencing_epoch"]))
            if int(operation["fencing_token"]) != prepared.fencing_token:
                raise FencingRejected(prepared.track_id, prepared.fencing_token, int(operation["fencing_token"]))
            current = int(track["revision"])
            if current != prepared.expected_revision:
                changed = await self._operations.update_one(
                    {"_id": operation["_id"], "state": OperationState.PREPARED.value,
                     "fingerprint": prepared.fingerprint},
                    {"$set": {"state": OperationState.CONFLICTED.value,
                              "conflict_actual_revision": current}},
                    session=session,
                )
                if changed.matched_count != 1:
                    raise InvalidPreparation("operation changed while recording conflict")
                return {"error": RevisionConflict(
                    prepared.track_id, prepared.operation_id, prepared.expected_revision, current
                )}
            if current >= _MAX_BSON_INT64 or int(track["control_sequence"]) >= _MAX_BSON_INT64:
                raise RevisionSequenceExhausted("track revision sequence exhausted")
            next_revision = current + 1
            cas = await self._tracks.update_one(
                {"_id": prepared.track_id, "revision": current,
                 "fencing_epoch": prepared.fencing_token,
                 "control_sequence": int(track["control_sequence"])},
                {"$set": {"revision": next_revision}, "$inc": {"control_sequence": 1}},
                session=session,
            )
            if cas.matched_count != 1:
                latest = await self._tracks.find_one({"_id": prepared.track_id}, session=session)
                if latest is None:
                    raise TrackNotInitialized(prepared.track_id)
                if int(latest["fencing_epoch"]) != prepared.fencing_token:
                    raise FencingRejected(prepared.track_id, prepared.fencing_token,
                                          int(latest["fencing_epoch"]))
                raise RevisionConflict(prepared.track_id, prepared.operation_id,
                                       prepared.expected_revision, int(latest["revision"]))
            receipt = RevisionReceipt(
                track_id=prepared.track_id, operation_id=prepared.operation_id,
                writer_id=prepared.writer_id, revision=next_revision,
                parent_revision=current, fencing_token=prepared.fencing_token,
                payload_sha256=prepared.payload_sha256, fingerprint=prepared.fingerprint,
            )
            if participant is not None:
                await participant(session, receipt)
            await self._history.insert_one(
                {"_id": _compound_id(prepared.track_id, str(next_revision)),
                 "track_id": prepared.track_id, "revision": next_revision,
                 "parent_revision": current, "operation_id": prepared.operation_id,
                 "writer_id": prepared.writer_id, "fencing_token": prepared.fencing_token,
                 "payload_sha256": prepared.payload_sha256,
                 "payload_json": operation["payload_json"],
                 "fingerprint": prepared.fingerprint,
                 "control_sequence": int(track["control_sequence"]) + 1,
                 "schema_version": 1}, session=session,
            )
            updated = await self._operations.update_one(
                {"_id": operation["_id"], "state": OperationState.PREPARED.value,
                 "preparation_id": prepared.preparation_id,
                 "fencing_token": prepared.fencing_token,
                 "fingerprint": prepared.fingerprint},
                {"$set": {"state": OperationState.COMMITTED.value,
                          "receipt": self._receipt_document(receipt),
                          "committed_revision": next_revision}},
                session=session,
            )
            if updated.matched_count != 1:
                raise InvalidPreparation("operation state changed during commit")
            return {"receipt": receipt, "replayed": False}

        try:
            async with self._client.start_session() as session:
                outcome = await session.with_transaction(
                    transaction_body,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        except Exception as exc:
            if not self._has_label(exc, "UnknownTransactionCommitResult"):
                raise
            try:
                reconciled = await self._operations.find_one(key)
            except Exception as reconcile_error:
                raise CommitOutcomeUnknown(prepared.track_id, prepared.operation_id) from reconcile_error
            if reconciled is not None and not hmac.compare_digest(
                reconciled.get("fingerprint", ""), prepared.fingerprint
            ):
                raise IdempotencyConflict(prepared.track_id, prepared.operation_id) from None
            if reconciled and reconciled.get("state") == OperationState.COMMITTED.value:
                return replace(self._receipt(reconciled), replayed=True)
            if reconciled and reconciled.get("state") == OperationState.CONFLICTED.value:
                raise RevisionConflict(prepared.track_id, prepared.operation_id,
                                      prepared.expected_revision,
                                      int(reconciled["conflict_actual_revision"])) from exc
            raise CommitOutcomeUnknown(prepared.track_id, prepared.operation_id) from exc
        if "error" in outcome:
            raise outcome["error"]
        receipt = outcome["receipt"]
        return replace(receipt, replayed=True) if outcome.get("replayed") else receipt

    async def current_revision(self, track_id: str) -> int:
        self._require_topology()
        state = await self._require_track(track_id)
        return int(state["revision"])

    async def _reuse_preparation(
        self, existing: Mapping[str, Any], track_id: str, writer_id: str,
        operation_id: str, expected_revision: int, fencing_token: int,
        payload_sha256: str, fingerprint: str,
    ) -> PreparedRevision:
        if (existing["writer_id"] != writer_id
            or int(existing["expected_revision"]) != expected_revision
            or not hmac.compare_digest(existing["payload_sha256"], payload_sha256)
            or not hmac.compare_digest(existing["fingerprint"], fingerprint)):
            raise IdempotencyConflict(track_id, operation_id)
        if existing["state"] == OperationState.ABORTED.value:
            raise OperationAborted("operation was abandoned")
        if existing["state"] != OperationState.PREPARED.value:
            return self._prepared(existing)
        state = await self._require_track(track_id)
        self._assert_fence(track_id, fencing_token, int(state["fencing_epoch"]))
        if int(existing["fencing_token"]) != fencing_token:
            await self._operations.update_one(
                {"_id": existing["_id"], "state": OperationState.PREPARED.value,
                 "fencing_token": int(existing["fencing_token"]), "fingerprint": fingerprint},
                {"$set": {"fencing_token": fencing_token}},
            )
            refreshed = await self._operations.find_one({"track_id": track_id,
                                                         "operation_id": operation_id})
            if refreshed is None or int(refreshed["fencing_token"]) != fencing_token:
                raise FencingRejected(track_id, fencing_token,
                                      int(refreshed["fencing_token"]) if refreshed else 0)
            return self._prepared(refreshed)
        return self._prepared(existing)

    async def _authenticate_writer(
        self, track_id: str, credential: WriterCredential, *, session: Any = None
    ) -> None:
        if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
            raise WriterAuthorizationError("writer credential is outside track scope")
        _validate_identity(credential.writer_id, "writer_id")
        if not isinstance(credential._secret, str) or not credential._secret:
            raise WriterAuthorizationError("writer credential is invalid or revoked")
        if len(credential._secret.encode("utf-8")) > 512:
            raise WriterAuthorizationError("writer credential is invalid or revoked")
        key = _compound_id(track_id, credential.writer_id)
        document = await self._writers.find_one({"_id": key}, session=session)
        digest = hashlib.sha256(credential._secret.encode("utf-8")).hexdigest()
        if document is None or not hmac.compare_digest(document["secret_sha256"], digest):
            raise WriterAuthorizationError("writer credential is invalid or revoked")
        if session is not None:
            used = await self._writers.update_one(
                {"_id": key, "secret_sha256": document["secret_sha256"]},
                {"$inc": {"use_sequence": 1}}, session=session,
            )
            if used.matched_count != 1:
                raise WriterAuthorizationError("writer credential was revoked during operation")

    async def _authenticate_authority(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> None:
        if not isinstance(authority, FenceAuthorityCredential) or authority.track_id != track_id:
            raise FenceAuthorityError("fence authority is outside track scope")
        _validate_identity(authority.authority_id, "authority_id")
        if not isinstance(authority._secret, str) or not authority._secret:
            raise FenceAuthorityError("fence authority is invalid")
        if len(authority._secret.encode("utf-8")) > 512:
            raise FenceAuthorityError("fence authority is invalid")
        key = _compound_id(track_id, authority.authority_id)
        document = await self._authorities.find_one({"_id": key})
        digest = hashlib.sha256(authority._secret.encode("utf-8")).hexdigest()
        if document is None or not hmac.compare_digest(document["secret_sha256"], digest):
            raise FenceAuthorityError("fence authority is invalid")

    async def _require_track(self, track_id: str) -> Mapping[str, Any]:
        state = await self._tracks.find_one({"_id": track_id})
        if state is None:
            raise TrackNotInitialized(track_id)
        return state

    @staticmethod
    def _assert_fence(track_id: str, supplied: int, current: int) -> None:
        if supplied != current:
            raise FencingRejected(track_id, supplied, current)

    @staticmethod
    def _prepared(document: Mapping[str, Any]) -> PreparedRevision:
        return PreparedRevision(
            track_id=document["track_id"], writer_id=document["writer_id"],
            operation_id=document["operation_id"],
            expected_revision=int(document["expected_revision"]),
            fencing_token=int(document["fencing_token"]),
            payload_sha256=document["payload_sha256"], fingerprint=document["fingerprint"],
            preparation_id=document["preparation_id"],
        )

    @staticmethod
    def _receipt(document: Mapping[str, Any]) -> RevisionReceipt:
        value = document.get("receipt") or {
            "track_id": document["track_id"], "operation_id": document["operation_id"],
            "writer_id": document["writer_id"],
            "revision": document["committed_revision"],
            "parent_revision": int(document["committed_revision"]) - 1,
            "fencing_token": document["fencing_token"],
            "payload_sha256": document["payload_sha256"],
            "fingerprint": document["fingerprint"],
        }
        return RevisionReceipt(
            track_id=value["track_id"], operation_id=value["operation_id"],
            writer_id=value["writer_id"], revision=int(value["revision"]),
            parent_revision=int(value["parent_revision"]),
            fencing_token=int(value["fencing_token"]),
            payload_sha256=value["payload_sha256"], fingerprint=value["fingerprint"],
            replayed=bool(value.get("replayed", False)),
        )

    @staticmethod
    def _receipt_document(receipt: RevisionReceipt) -> dict[str, Any]:
        return {
            "track_id": receipt.track_id, "operation_id": receipt.operation_id,
            "writer_id": receipt.writer_id, "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "fencing_token": receipt.fencing_token,
            "payload_sha256": receipt.payload_sha256,
            "fingerprint": receipt.fingerprint,
        }

    @staticmethod
    def _track_state(document: Mapping[str, Any]) -> dict[str, int | str]:
        return {"track_id": document["_id"], "revision": int(document["revision"]),
                "fencing_epoch": int(document["fencing_epoch"]),
                "control_sequence": int(document["control_sequence"]),
                "last_fence_sequence": int(document["last_fence_sequence"])}

    @staticmethod
    def _assert_same_preparation(document: Mapping[str, Any], prepared: PreparedRevision) -> None:
        if any((document.get("track_id") != prepared.track_id,
                document.get("writer_id") != prepared.writer_id,
                document.get("operation_id") != prepared.operation_id,
                int(document.get("expected_revision", -1)) != prepared.expected_revision,
                int(document.get("fencing_token", -1)) != prepared.fencing_token,
                document.get("payload_sha256") != prepared.payload_sha256,
                document.get("fingerprint") != prepared.fingerprint,
                document.get("preparation_id") != prepared.preparation_id)):
            raise InvalidPreparation("prepared handle does not match stored operation")

    @staticmethod
    def _has_label(error: Exception, label: str) -> bool:
        predicate = getattr(error, "has_error_label", None)
        return bool(callable(predicate) and predicate(label))
