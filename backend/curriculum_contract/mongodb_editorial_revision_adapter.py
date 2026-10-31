"""Isolated MongoDB 7 adapter for editorial revision/CAS/fencing.

Importing this module performs no I/O and creates no client. This phase's
implementation accepts only a dedicated editorial_revision_test_* database.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
import secrets
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping

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
    RevisionRecord,
    WriterAuthorizationError,
    WriterCredential,
)

JsonValue = Any
ProposalValidator = Callable[[Mapping[str, JsonValue]], bool | None]
TransactionParticipant = Callable[[Any, RevisionReceipt], None]

_TEST_DATABASE_RE = re.compile(r"^editorial_revision_test_[a-zA-Z0-9_-]{8,64}$")
_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_MAX_PAYLOAD_BYTES = 8 * 1024 * 1024
_MAX_IDENTITY_BYTES = 256
_MAX_BSON_INT64 = (1 << 63) - 1
_MAX_JSON_DEPTH = 64
_MAX_JSON_NODES = 100_000


class MongoRevisionAdapterError(RuntimeError):
    """Base class for adapter-specific failures."""


class MongoDependencyUnavailable(MongoRevisionAdapterError):
    """PyMongo is not installed in the isolated execution environment."""


class UnsafeDatabaseName(MongoRevisionAdapterError):
    """This phase's adapter refuses databases outside its disposable namespace."""


class TrackNotInitialized(MongoRevisionAdapterError):
    """No revision state exists for the requested synthetic track."""


class TransactionTopologyError(MongoRevisionAdapterError):
    """The server is not MongoDB 7 on a transaction-capable replica set."""


class RevisionSequenceExhausted(MongoRevisionAdapterError):
    """A persisted int64 revision, epoch, or guard sequence cannot advance."""


class CommitOutcomeUnknown(MongoRevisionAdapterError):
    """The driver could not establish whether a transaction commit succeeded."""

    def __init__(self, track_id: str, operation_id: str):
        self.track_id = track_id
        self.operation_id = operation_id
        super().__init__(
            f"commit outcome is unknown for operation {operation_id!r} "
            f"on track {track_id!r}; reconcile by operation identity"
        )


@dataclass(frozen=True, slots=True)
class MongoTopology:
    server_version: str
    replica_set: str
    sessions_available: bool


@dataclass(frozen=True, slots=True)
class TrackRevisionState:
    track_id: str
    revision: int
    fencing_epoch: int
    control_sequence: int
    last_fence_sequence: int


@dataclass(frozen=True, slots=True)
class _TransactionOutcome:
    receipt: RevisionReceipt | None = None
    error: Exception | None = None


def _driver_types() -> tuple[Any, Any, Any, Any, Any]:
    try:
        from pymongo import ReturnDocument
        from pymongo.errors import DuplicateKeyError
        from pymongo.read_concern import ReadConcern
        from pymongo.read_preferences import ReadPreference
        from pymongo.write_concern import WriteConcern
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise MongoDependencyUnavailable(
            "PyMongo is required to use MongoDBEditorialRevisionAdapter"
        ) from exc
    return ReturnDocument, DuplicateKeyError, ReadConcern, ReadPreference, WriteConcern


def _validate_identity(
    value: str, field_name: str, *, maximum: int = _MAX_IDENTITY_BYTES
) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise InvalidProposal(f"{field_name} must be a non-empty string without NUL")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InvalidProposal(f"{field_name} must be valid UTF-8") from exc
    if len(encoded) > maximum:
        raise InvalidProposal(f"{field_name} exceeds {maximum} UTF-8 bytes")
    return value


def _normalize_json(
    value: JsonValue,
    *,
    path: str,
    depth: int,
    budget: list[int],
    max_payload_bytes: int,
) -> JsonValue:
    budget[0] += 1
    if budget[0] > _MAX_JSON_NODES:
        raise InvalidProposal("payload contains too many JSON values")
    if depth > _MAX_JSON_DEPTH:
        raise InvalidProposal(f"{path} exceeds maximum JSON depth {_MAX_JSON_DEPTH}")
    if value is None or type(value) in (str, bool, int):
        if isinstance(value, str):
            try:
                if len(value.encode("utf-8")) > max_payload_bytes:
                    raise InvalidProposal(f"{path} contains an oversized string")
            except UnicodeEncodeError as exc:
                raise InvalidProposal(f"{path} contains invalid UTF-8 text") from exc
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise InvalidProposal(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        result: dict[str, JsonValue] = {}
        for key, child in value.items():
            if not isinstance(key, str) or "\x00" in key:
                raise InvalidProposal(f"{path} contains an invalid object key")
            try:
                if len(key.encode("utf-8")) > 1024:
                    raise InvalidProposal(f"{path} contains an oversized object key")
            except UnicodeEncodeError as exc:
                raise InvalidProposal(f"{path} contains an invalid UTF-8 object key") from exc
            result[key] = _normalize_json(
                child,
                path=f"{path}.{key}",
                depth=depth + 1,
                budget=budget,
                max_payload_bytes=max_payload_bytes,
            )
        return result
    if isinstance(value, (list, tuple)):
        return [
            _normalize_json(
                child,
                path=f"{path}[{index}]",
                depth=depth + 1,
                budget=budget,
                max_payload_bytes=max_payload_bytes,
            )
            for index, child in enumerate(value)
        ]
    raise InvalidProposal(f"{path} contains a value that is not JSON-compatible")


def _canonical_payload(
    payload: Mapping[str, JsonValue], max_payload_bytes: int
) -> tuple[str, str, Mapping[str, JsonValue]]:
    if not isinstance(payload, Mapping):
        raise InvalidProposal("payload must be a JSON object")
    normalized = _normalize_json(
        payload,
        path="payload",
        depth=0,
        budget=[0],
        max_payload_bytes=max_payload_bytes,
    )
    if not isinstance(normalized, dict):
        raise InvalidProposal("payload must be a JSON object")
    try:
        canonical = json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        encoded = canonical.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as exc:
        raise InvalidProposal("payload cannot be canonically encoded as JSON") from exc
    if len(encoded) > max_payload_bytes:
        raise InvalidProposal(
            f"payload is {len(encoded)} bytes; maximum is {max_payload_bytes}"
        )
    return canonical, hashlib.sha256(encoded).hexdigest(), normalized


def _freeze_json(value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        from types import MappingProxyType

        return MappingProxyType({key: _freeze_json(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(child) for child in value)
    return value


def _fingerprint(
    track_id: str,
    writer_id: str,
    operation_id: str,
    expected_revision: int,
    payload_sha256: str,
) -> str:
    intent = json.dumps(
        [track_id, writer_id, operation_id, expected_revision, payload_sha256],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(intent.encode("utf-8")).hexdigest()


def _compound_id(*parts: str) -> str:
    raw = json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class MongoDBEditorialRevisionAdapter:
    """Persistent reference adapter restricted to disposable MongoDB databases.

    The final fence check, revision CAS, history append and durable operation
    receipt share one MongoDB transaction. Its successful commit is the
    linearization point. control_sequence serializes fence advancement,
    revision commits and abandonment on the same track-state document.
    """

    def __init__(
        self,
        database: Any,
        *,
        namespace: str,
        proposal_validator: ProposalValidator | None = None,
        max_payload_bytes: int = 4 * 1024 * 1024,
    ) -> None:
        database_name = getattr(database, "name", None)
        if not isinstance(database_name, str) or not _TEST_DATABASE_RE.fullmatch(database_name):
            raise UnsafeDatabaseName(
                "only editorial_revision_test_<8-64 safe characters> databases are allowed"
            )
        if not isinstance(namespace, str) or not _NAMESPACE_RE.fullmatch(namespace):
            raise ValueError("namespace must match [a-z][a-z0-9_]{0,31}")
        if (
            type(max_payload_bytes) is not int
            or not 1 <= max_payload_bytes <= _MAX_PAYLOAD_BYTES
        ):
            raise ValueError(f"max_payload_bytes must be between 1 and {_MAX_PAYLOAD_BYTES}")
        if not callable(getattr(database, "with_options", None)):
            raise TypeError("database must be an explicitly supplied PyMongo Database")
        client = getattr(database, "client", None)
        if client is None or not callable(getattr(client, "start_session", None)):
            raise TypeError("database must expose a PyMongo client; no client is created here")

        _, _, ReadConcern, ReadPreference, WriteConcern = _driver_types()
        self._client = client
        self._topology_verified = False
        self._database = database.with_options(
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        )
        self._namespace = namespace
        self._max_payload_bytes = max_payload_bytes
        self._proposal_validator = proposal_validator
        self._tracks = self._database[f"{namespace}_tracks"]
        self._operations = self._database[f"{namespace}_operations"]
        self._history = self._database[f"{namespace}_history"]
        self._writers = self._database[f"{namespace}_writers"]
        self._authorities = self._database[f"{namespace}_authorities"]

    @property
    def database_name(self) -> str:
        return self._database.name

    @property
    def namespace(self) -> str:
        return self._namespace

    def verify_transaction_topology(self) -> MongoTopology:
        """Explicitly connect and require MongoDB 7 replica-set transaction support."""

        hello = self._client.admin.command("hello")
        server = self._client.server_info()
        version = str(server.get("version", ""))
        replica_set = hello.get("setName")
        sessions_available = hello.get("logicalSessionTimeoutMinutes") is not None
        if not version.startswith("7."):
            raise TransactionTopologyError(
                f"MongoDB major version 7 required; server reported {version or 'unknown'}"
            )
        if not isinstance(replica_set, str) or not replica_set:
            raise TransactionTopologyError(
                "transactions require a replica-set or compatible cluster; standalone refused"
            )
        if not sessions_available:
            raise TransactionTopologyError("server does not report logical session support")
        self._topology_verified = True
        return MongoTopology(version, replica_set, sessions_available)

    def _require_verified_topology(self) -> None:
        if not self._topology_verified:
            raise TransactionTopologyError(
                "call verify_transaction_topology successfully before database operations"
            )

    def ensure_indexes(self) -> None:
        """Create only namespaced indexes in the guarded disposable database."""

        self._require_verified_topology()

        self._operations.create_index(
            [("track_id", 1), ("operation_id", 1)],
            unique=True,
            name=f"{self._namespace}_operation_identity",
        )
        self._history.create_index(
            [("track_id", 1), ("revision", 1)],
            unique=True,
            name=f"{self._namespace}_track_revision",
        )
        self._writers.create_index(
            [("track_id", 1), ("writer_id", 1)],
            unique=True,
            name=f"{self._namespace}_writer_identity",
        )
        self._authorities.create_index(
            [("track_id", 1), ("authority_id", 1)],
            unique=True,
            name=f"{self._namespace}_authority_identity",
        )

    def initialize_track(self, track_id: str) -> TrackRevisionState:
        _validate_identity(track_id, "track_id")
        self.ensure_indexes()
        _, DuplicateKeyError, _, _, _ = _driver_types()
        document = {
            "_id": track_id,
            "revision": 0,
            "fencing_epoch": 0,
            "control_sequence": 0,
            "last_fence_sequence": 0,
            "schema_version": 1,
        }
        try:
            self._tracks.insert_one(document)
        except DuplicateKeyError:
            pass
        state = self._tracks.find_one({"_id": track_id})
        if state is None:
            raise TrackNotInitialized(track_id)
        return self._track_state(state)

    def provision_writer_credential(
        self, track_id: str, writer_id: str
    ) -> WriterCredential:
        """Provision a synthetic capability; this is not production IAM."""

        _validate_identity(track_id, "track_id")
        _validate_identity(writer_id, "writer_id")
        self._require_track(track_id)
        secret = secrets.token_urlsafe(32)
        document_id = _compound_id(track_id, writer_id)
        self._writers.replace_one(
            {"_id": document_id},
            {
                "_id": document_id,
                "track_id": track_id,
                "writer_id": writer_id,
                "secret_sha256": self._secret_digest(secret),
                "use_sequence": 0,
            },
            upsert=True,
        )
        return WriterCredential(track_id, writer_id, secret)

    def revoke_writer_credential(self, track_id: str, writer_id: str) -> bool:
        self._require_verified_topology()
        _validate_identity(track_id, "track_id")
        _validate_identity(writer_id, "writer_id")
        result = self._writers.delete_one({"_id": _compound_id(track_id, writer_id)})
        return result.deleted_count == 1

    def provision_fence_authority(
        self, track_id: str, authority_id: str
    ) -> FenceAuthorityCredential:
        """Provision a synthetic capability; authority provisioning is test-only."""

        _validate_identity(track_id, "track_id")
        _validate_identity(authority_id, "authority_id")
        self._require_track(track_id)
        secret = secrets.token_urlsafe(32)
        document_id = _compound_id(track_id, authority_id)
        self._authorities.replace_one(
            {"_id": document_id},
            {
                "_id": document_id,
                "track_id": track_id,
                "authority_id": authority_id,
                "secret_sha256": self._secret_digest(secret),
            },
            upsert=True,
        )
        return FenceAuthorityCredential(track_id, authority_id, secret)

    def advance_fence(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> int:
        _validate_identity(track_id, "track_id")
        self._authenticate_authority(track_id, authority)
        ReturnDocument, _, _, _, _ = _driver_types()
        state = self._tracks.find_one_and_update(
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
            current = self._tracks.find_one({"_id": track_id})
            if current is None:
                raise TrackNotInitialized(track_id)
            raise RevisionSequenceExhausted(
                f"fencing sequence exhausted for track {track_id!r}"
            )
        return int(state["fencing_epoch"])

    def prepare(
        self,
        *,
        track_id: str,
        credential: WriterCredential,
        operation_id: str,
        expected_revision: int,
        fencing_token: int,
        payload: Mapping[str, JsonValue],
    ) -> PreparedRevision:
        _validate_identity(track_id, "track_id")
        _validate_identity(operation_id, "operation_id")
        if type(expected_revision) is not int or not 0 <= expected_revision <= _MAX_BSON_INT64:
            raise InvalidProposal("expected_revision must be a non-negative integer")
        if type(fencing_token) is not int or not 1 <= fencing_token <= _MAX_BSON_INT64:
            raise InvalidProposal("fencing_token must be a positive server-issued epoch")
        if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
            raise WriterAuthorizationError(
                "writer credential is missing or outside track scope"
            )
        _validate_identity(credential.writer_id, "writer_id")
        canonical, payload_sha256, normalized = _canonical_payload(
            payload, self._max_payload_bytes
        )
        self._authenticate_writer(track_id, credential)
        fingerprint = _fingerprint(
            track_id, credential.writer_id, operation_id, expected_revision, payload_sha256
        )
        key = {"track_id": track_id, "operation_id": operation_id}
        existing = self._operations.find_one(key)
        if existing is not None:
            return self._reuse_or_refresh_preparation(
                existing=existing,
                track_id=track_id,
                writer_id=credential.writer_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                fencing_token=fencing_token,
                payload_sha256=payload_sha256,
                fingerprint=fingerprint,
            )

        state = self._require_track(track_id)
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
            "payload_sha256": payload_sha256,
            "payload_json": canonical,
            "fingerprint": fingerprint,
            "preparation_id": secrets.token_hex(16),
            "state": OperationState.PREPARED.value,
            "schema_version": 1,
        }
        _, DuplicateKeyError, _, _, _ = _driver_types()
        try:
            self._operations.insert_one(document)
            return self._prepared_from_document(document)
        except DuplicateKeyError:
            concurrent = self._operations.find_one(key)
            if concurrent is None:
                raise
            return self._reuse_or_refresh_preparation(
                existing=concurrent,
                track_id=track_id,
                writer_id=credential.writer_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                fencing_token=fencing_token,
                payload_sha256=payload_sha256,
                fingerprint=fingerprint,
            )

    def commit(
        self,
        prepared: PreparedRevision,
        credential: WriterCredential,
        *,
        _transaction_participant: TransactionParticipant | None = None,
    ) -> RevisionReceipt:
        """Commit a prepared revision, optionally joining an isolated participant.

        The private participant hook exists only for experimental composition.
        It runs inside the same MongoDB transaction as revision CAS, immutable
        history and the operation receipt. Because ``with_transaction`` may
        rerun its callback, participants must only perform deterministic,
        session-bound MongoDB work and must not cause external side effects.
        Existing callers that omit the hook retain the original contract.
        """

        if _transaction_participant is not None and not callable(_transaction_participant):
            raise TypeError("transaction participant must be callable")
        self._validate_prepared_identity(prepared)
        self._authenticate_writer(prepared.track_id, credential)
        if credential.writer_id != prepared.writer_id:
            raise WriterAuthorizationError("credential does not own the preparation")

        key = {"track_id": prepared.track_id, "operation_id": prepared.operation_id}
        existing = self._operations.find_one(key)
        if existing is None:
            raise InvalidPreparation("prepared operation was not found")
        self._assert_same_preparation(existing, prepared)
        if existing["state"] == OperationState.COMMITTED.value:
            return replace(self._receipt_from_document(existing), replayed=True)
        if existing["state"] == OperationState.ABORTED.value:
            raise OperationAborted(f"operation {prepared.operation_id!r} was abandoned")
        if existing["state"] == OperationState.CONFLICTED.value:
            raise RevisionConflict(
                prepared.track_id,
                prepared.operation_id,
                prepared.expected_revision,
                int(existing["conflict_actual_revision"]),
            )

        _, _, ReadConcern, ReadPreference, WriteConcern = _driver_types()

        def transaction_body(session: Any) -> _TransactionOutcome:
            self._authenticate_writer(prepared.track_id, credential, session=session)
            operation = self._operations.find_one(key, session=session)
            if operation is None:
                raise InvalidPreparation("prepared operation disappeared")
            self._assert_same_preparation(operation, prepared)
            if operation["state"] == OperationState.COMMITTED.value:
                return _TransactionOutcome(
                    receipt=replace(self._receipt_from_document(operation), replayed=True)
                )
            if operation["state"] == OperationState.ABORTED.value:
                raise OperationAborted(f"operation {prepared.operation_id!r} was abandoned")
            if operation["state"] == OperationState.CONFLICTED.value:
                return _TransactionOutcome(
                    error=RevisionConflict(
                        prepared.track_id,
                        prepared.operation_id,
                        prepared.expected_revision,
                        int(operation["conflict_actual_revision"]),
                    )
                )

            track = self._tracks.find_one({"_id": prepared.track_id}, session=session)
            if track is None:
                raise TrackNotInitialized(prepared.track_id)
            self._assert_fence(
                prepared.track_id, prepared.fencing_token, int(track["fencing_epoch"])
            )
            if int(operation["fencing_token"]) != prepared.fencing_token:
                raise FencingRejected(
                    prepared.track_id,
                    prepared.fencing_token,
                    int(operation["fencing_token"]),
                )

            current_revision = int(track["revision"])
            if current_revision != prepared.expected_revision:
                conflict = self._operations.update_one(
                    {
                        "_id": operation["_id"],
                        "state": OperationState.PREPARED.value,
                        "fingerprint": prepared.fingerprint,
                    },
                    {
                        "$set": {
                            "state": OperationState.CONFLICTED.value,
                            "conflict_actual_revision": current_revision,
                        }
                    },
                    session=session,
                )
                if conflict.matched_count != 1:
                    latest = self._operations.find_one(key, session=session)
                    if latest and latest["state"] == OperationState.COMMITTED.value:
                        return _TransactionOutcome(
                            receipt=replace(self._receipt_from_document(latest), replayed=True)
                        )
                    raise InvalidPreparation("operation changed during conflict recording")
                return _TransactionOutcome(
                    error=RevisionConflict(
                        prepared.track_id,
                        prepared.operation_id,
                        prepared.expected_revision,
                        current_revision,
                    )
                )

            if (
                current_revision >= _MAX_BSON_INT64
                or int(track["control_sequence"]) >= _MAX_BSON_INT64
            ):
                raise RevisionSequenceExhausted(
                    f"revision sequence exhausted for track {prepared.track_id!r}"
                )

            next_revision = current_revision + 1
            changed = self._tracks.update_one(
                {
                    "_id": prepared.track_id,
                    "revision": current_revision,
                    "fencing_epoch": prepared.fencing_token,
                    "control_sequence": int(track["control_sequence"]),
                },
                {
                    "$set": {"revision": next_revision},
                    "$inc": {"control_sequence": 1},
                },
                session=session,
            )
            if changed.matched_count != 1:
                latest = self._tracks.find_one({"_id": prepared.track_id}, session=session)
                if latest is None:
                    raise TrackNotInitialized(prepared.track_id)
                if int(latest["fencing_epoch"]) != prepared.fencing_token:
                    raise FencingRejected(
                        prepared.track_id,
                        prepared.fencing_token,
                        int(latest["fencing_epoch"]),
                    )
                raise RevisionConflict(
                    prepared.track_id,
                    prepared.operation_id,
                    prepared.expected_revision,
                    int(latest["revision"]),
                )

            receipt = RevisionReceipt(
                track_id=prepared.track_id,
                operation_id=prepared.operation_id,
                writer_id=prepared.writer_id,
                revision=next_revision,
                parent_revision=current_revision,
                fencing_token=prepared.fencing_token,
                payload_sha256=prepared.payload_sha256,
                fingerprint=prepared.fingerprint,
            )
            if _transaction_participant is not None:
                _transaction_participant(session, receipt)
            self._history.insert_one(
                {
                    "_id": _compound_id(prepared.track_id, str(next_revision)),
                    "track_id": prepared.track_id,
                    "revision": next_revision,
                    "parent_revision": current_revision,
                    "operation_id": prepared.operation_id,
                    "writer_id": prepared.writer_id,
                    "fencing_token": prepared.fencing_token,
                    "payload_sha256": prepared.payload_sha256,
                    "payload_json": operation["payload_json"],
                    "fingerprint": prepared.fingerprint,
                    "control_sequence": int(track["control_sequence"]) + 1,
                    "schema_version": 1,
                },
                session=session,
            )
            operation_update = self._operations.update_one(
                {
                    "_id": operation["_id"],
                    "state": OperationState.PREPARED.value,
                    "preparation_id": prepared.preparation_id,
                    "fencing_token": prepared.fencing_token,
                    "fingerprint": prepared.fingerprint,
                },
                {
                    "$set": {
                        "state": OperationState.COMMITTED.value,
                        "receipt": self._receipt_document(receipt),
                        "committed_revision": next_revision,
                    }
                },
                session=session,
            )
            if operation_update.matched_count != 1:
                raise InvalidPreparation("operation state changed during commit")
            return _TransactionOutcome(receipt=receipt)

        try:
            with self._client.start_session() as session:
                outcome = session.with_transaction(
                    transaction_body,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        except Exception as exc:
            if not self._has_error_label(exc, "UnknownTransactionCommitResult"):
                raise
            try:
                reconciled = self._operations.find_one(
                    {
                        "track_id": prepared.track_id,
                        "operation_id": prepared.operation_id,
                    }
                )
            except Exception:
                raise CommitOutcomeUnknown(
                    prepared.track_id, prepared.operation_id
                ) from exc
            if reconciled is not None and not hmac.compare_digest(
                reconciled.get("fingerprint", ""), prepared.fingerprint
            ):
                raise IdempotencyConflict(prepared.track_id, prepared.operation_id)
            if reconciled and reconciled.get("state") == OperationState.COMMITTED.value:
                return replace(self._receipt_from_document(reconciled), replayed=True)
            if reconciled and reconciled.get("state") == OperationState.CONFLICTED.value:
                raise RevisionConflict(
                    prepared.track_id,
                    prepared.operation_id,
                    prepared.expected_revision,
                    int(reconciled["conflict_actual_revision"]),
                ) from exc
            if reconciled and reconciled.get("state") == OperationState.ABORTED.value:
                raise OperationAborted(
                    f"operation {prepared.operation_id!r} was abandoned"
                ) from exc
            raise CommitOutcomeUnknown(prepared.track_id, prepared.operation_id) from exc

        if outcome.error is not None:
            raise outcome.error
        if outcome.receipt is None:
            raise MongoRevisionAdapterError("transaction completed without a receipt")
        return outcome.receipt

    def abandon(self, prepared: PreparedRevision, credential: WriterCredential) -> bool:
        self._validate_prepared_identity(prepared)
        self._authenticate_writer(prepared.track_id, credential)
        if credential.writer_id != prepared.writer_id:
            raise WriterAuthorizationError("credential does not own the preparation")
        key = {"track_id": prepared.track_id, "operation_id": prepared.operation_id}
        _, _, ReadConcern, ReadPreference, WriteConcern = _driver_types()

        def transaction_body(session: Any) -> bool:
            self._authenticate_writer(prepared.track_id, credential, session=session)
            operation = self._operations.find_one(key, session=session)
            if operation is None:
                raise InvalidPreparation("prepared operation was not found")
            self._assert_same_preparation(operation, prepared)
            if operation["state"] == OperationState.ABORTED.value:
                return False
            if operation["state"] != OperationState.PREPARED.value:
                return False
            state = self._tracks.find_one({"_id": prepared.track_id}, session=session)
            if state is None:
                raise TrackNotInitialized(prepared.track_id)
            self._assert_fence(
                prepared.track_id, prepared.fencing_token, int(state["fencing_epoch"])
            )
            if int(state["control_sequence"]) >= _MAX_BSON_INT64:
                raise RevisionSequenceExhausted(
                    f"control sequence exhausted for track {prepared.track_id!r}"
                )
            if int(operation["fencing_token"]) != prepared.fencing_token:
                raise FencingRejected(
                    prepared.track_id,
                    prepared.fencing_token,
                    int(operation["fencing_token"]),
                )
            guard = self._tracks.update_one(
                {
                    "_id": prepared.track_id,
                    "fencing_epoch": prepared.fencing_token,
                    "revision": int(state["revision"]),
                    "control_sequence": int(state["control_sequence"]),
                },
                {"$inc": {"control_sequence": 1}},
                session=session,
            )
            if guard.matched_count != 1:
                latest = self._tracks.find_one({"_id": prepared.track_id}, session=session)
                if latest is None:
                    raise TrackNotInitialized(prepared.track_id)
                self._assert_fence(
                    prepared.track_id, prepared.fencing_token, int(latest["fencing_epoch"])
                )
                raise RevisionConflict(
                    prepared.track_id,
                    prepared.operation_id,
                    prepared.expected_revision,
                    int(latest["revision"]),
                )
            changed = self._operations.update_one(
                {
                    "_id": operation["_id"],
                    "state": OperationState.PREPARED.value,
                    "preparation_id": prepared.preparation_id,
                    "fencing_token": prepared.fencing_token,
                    "fingerprint": prepared.fingerprint,
                },
                {"$set": {"state": OperationState.ABORTED.value}},
                session=session,
            )
            if changed.matched_count != 1:
                raise InvalidPreparation("operation state changed during abandonment")
            return True

        with self._client.start_session() as session:
            return bool(
                session.with_transaction(
                    transaction_body,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
            )

    def current_revision(self, track_id: str) -> int:
        _validate_identity(track_id, "track_id")
        return int(self._require_track(track_id)["revision"])

    def read_revision(self, track_id: str, revision: int) -> RevisionRecord | None:
        self._require_verified_topology()
        _validate_identity(track_id, "track_id")
        if type(revision) is not int or revision < 1:
            raise InvalidProposal("revision must be a positive integer")
        document = self._history.find_one({"track_id": track_id, "revision": revision})
        return None if document is None else self._revision_from_document(document)

    def history(self, track_id: str) -> tuple[RevisionRecord, ...]:
        self._require_verified_topology()
        _validate_identity(track_id, "track_id")
        documents = self._history.find({"track_id": track_id}).sort("revision", 1)
        return tuple(self._revision_from_document(document) for document in documents)

    def operation_state(
        self, track_id: str, operation_id: str
    ) -> OperationState | None:
        self._require_verified_topology()
        _validate_identity(track_id, "track_id")
        _validate_identity(operation_id, "operation_id")
        document = self._operations.find_one(
            {"track_id": track_id, "operation_id": operation_id}
        )
        return None if document is None else OperationState(document["state"])

    def prepared_payload(
        self,
        track_id: str,
        operation_id: str,
        credential: WriterCredential,
    ) -> Mapping[str, JsonValue]:
        _validate_identity(track_id, "track_id")
        _validate_identity(operation_id, "operation_id")
        self._authenticate_writer(track_id, credential)
        document = self._operations.find_one(
            {"track_id": track_id, "operation_id": operation_id}
        )
        if document is None or document["writer_id"] != credential.writer_id:
            raise InvalidPreparation("prepared operation was not found")
        if document["state"] == OperationState.ABORTED.value:
            raise OperationAborted(f"operation {operation_id!r} was abandoned")
        return _freeze_json(json.loads(document["payload_json"]))

    def _reuse_or_refresh_preparation(
        self,
        *,
        existing: Mapping[str, Any],
        track_id: str,
        writer_id: str,
        operation_id: str,
        expected_revision: int,
        fencing_token: int,
        payload_sha256: str,
        fingerprint: str,
    ) -> PreparedRevision:
        if (
            existing["writer_id"] != writer_id
            or int(existing["expected_revision"]) != expected_revision
            or not hmac.compare_digest(existing["payload_sha256"], payload_sha256)
            or not hmac.compare_digest(existing["fingerprint"], fingerprint)
        ):
            raise IdempotencyConflict(track_id, operation_id)
        if existing["state"] == OperationState.ABORTED.value:
            raise OperationAborted(f"operation {operation_id!r} was abandoned")
        if existing["state"] != OperationState.PREPARED.value:
            return self._prepared_from_document(existing)

        state = self._require_track(track_id)
        self._assert_fence(track_id, fencing_token, int(state["fencing_epoch"]))
        if int(existing["fencing_token"]) != fencing_token:
            self._operations.update_one(
                {
                    "_id": existing["_id"],
                    "state": OperationState.PREPARED.value,
                    "fencing_token": int(existing["fencing_token"]),
                    "fingerprint": fingerprint,
                },
                {"$set": {"fencing_token": fencing_token}},
            )
            refreshed = self._operations.find_one(
                {"track_id": track_id, "operation_id": operation_id}
            )
            if refreshed is None:
                raise InvalidPreparation("prepared operation disappeared")
            if int(refreshed["fencing_token"]) != fencing_token:
                self._assert_fence(track_id, fencing_token, int(refreshed["fencing_token"]))
            return self._prepared_from_document(refreshed)
        return self._prepared_from_document(existing)

    def _authenticate_writer(
        self, track_id: str, credential: WriterCredential, *, session: Any = None
    ) -> None:
        self._require_verified_topology()
        if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
            raise WriterAuthorizationError(
                "writer credential is missing or outside track scope"
            )
        _validate_identity(credential.writer_id, "writer_id")
        if not isinstance(credential._secret, str) or not credential._secret:
            raise WriterAuthorizationError("writer credential is invalid or revoked")
        try:
            if len(credential._secret.encode("utf-8")) > 512:
                raise WriterAuthorizationError("writer credential is invalid or revoked")
        except UnicodeEncodeError as exc:
            raise WriterAuthorizationError("writer credential is invalid or revoked") from exc
        document = self._writers.find_one(
            {"_id": _compound_id(track_id, credential.writer_id)}
        )
        if document is None or not hmac.compare_digest(
            document["secret_sha256"], self._secret_digest(credential._secret)
        ):
            raise WriterAuthorizationError("writer credential is invalid or revoked")
        if session is not None:
            # Serialize authorization checks with revocation/reprovisioning.
            used = self._writers.update_one(
                {
                    "_id": document["_id"],
                    "secret_sha256": document["secret_sha256"],
                },
                {"$inc": {"use_sequence": 1}},
                session=session,
            )
            if used.matched_count != 1:
                raise WriterAuthorizationError(
                    "writer credential was revoked during operation"
                )

    def _authenticate_authority(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> None:
        self._require_verified_topology()
        if not isinstance(authority, FenceAuthorityCredential) or authority.track_id != track_id:
            raise FenceAuthorityError("fence authority is missing or outside track scope")
        _validate_identity(authority.authority_id, "authority_id")
        if not isinstance(authority._secret, str) or not authority._secret:
            raise FenceAuthorityError("fence authority is invalid")
        try:
            if len(authority._secret.encode("utf-8")) > 512:
                raise FenceAuthorityError("fence authority is invalid")
        except UnicodeEncodeError as exc:
            raise FenceAuthorityError("fence authority is invalid") from exc
        document = self._authorities.find_one(
            {"_id": _compound_id(track_id, authority.authority_id)}
        )
        if document is None or not hmac.compare_digest(
            document["secret_sha256"], self._secret_digest(authority._secret)
        ):
            raise FenceAuthorityError("fence authority is invalid")

    def _require_track(self, track_id: str) -> Mapping[str, Any]:
        self._require_verified_topology()
        state = self._tracks.find_one({"_id": track_id})
        if state is None:
            raise TrackNotInitialized(track_id)
        return state

    @staticmethod
    def _assert_fence(track_id: str, supplied: int, current: int) -> None:
        if supplied != current:
            raise FencingRejected(track_id, supplied, current)

    @staticmethod
    def _validate_prepared_identity(prepared: PreparedRevision) -> None:
        if not isinstance(prepared, PreparedRevision):
            raise InvalidPreparation("prepared handle has an invalid type")
        _validate_identity(prepared.track_id, "track_id")
        _validate_identity(prepared.writer_id, "writer_id")
        _validate_identity(prepared.operation_id, "operation_id")
        if (
            type(prepared.expected_revision) is not int
            or not 0 <= prepared.expected_revision <= _MAX_BSON_INT64
        ):
            raise InvalidPreparation("prepared handle has an invalid expected revision")
        if (
            type(prepared.fencing_token) is not int
            or not 1 <= prepared.fencing_token <= _MAX_BSON_INT64
        ):
            raise InvalidPreparation("prepared handle has an invalid fencing token")
        for field_name in ("payload_sha256", "fingerprint"):
            value = getattr(prepared, field_name)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise InvalidPreparation(f"prepared handle has an invalid {field_name}")
        if not isinstance(prepared.preparation_id, str) or not re.fullmatch(
            r"[0-9a-f]{32}", prepared.preparation_id
        ):
            raise InvalidPreparation("prepared handle has an invalid preparation_id")

    @staticmethod
    def _assert_same_preparation(
        document: Mapping[str, Any], prepared: PreparedRevision
    ) -> None:
        if (
            document["track_id"] != prepared.track_id
            or document["writer_id"] != prepared.writer_id
            or document["operation_id"] != prepared.operation_id
            or int(document["expected_revision"]) != prepared.expected_revision
            or not hmac.compare_digest(document["payload_sha256"], prepared.payload_sha256)
            or not hmac.compare_digest(document["fingerprint"], prepared.fingerprint)
            or not hmac.compare_digest(document["preparation_id"], prepared.preparation_id)
        ):
            raise InvalidPreparation("prepared handle is unknown or altered")

    @staticmethod
    def _prepared_from_document(document: Mapping[str, Any]) -> PreparedRevision:
        return PreparedRevision(
            track_id=document["track_id"],
            writer_id=document["writer_id"],
            operation_id=document["operation_id"],
            expected_revision=int(document["expected_revision"]),
            fencing_token=int(document["fencing_token"]),
            payload_sha256=document["payload_sha256"],
            fingerprint=document["fingerprint"],
            preparation_id=document["preparation_id"],
        )

    @staticmethod
    def _receipt_document(receipt: RevisionReceipt) -> dict[str, Any]:
        return {
            "track_id": receipt.track_id,
            "operation_id": receipt.operation_id,
            "writer_id": receipt.writer_id,
            "revision": receipt.revision,
            "parent_revision": receipt.parent_revision,
            "fencing_token": receipt.fencing_token,
            "payload_sha256": receipt.payload_sha256,
            "fingerprint": receipt.fingerprint,
        }

    @staticmethod
    def _receipt_from_document(document: Mapping[str, Any]) -> RevisionReceipt:
        saved = document.get("receipt")
        if not isinstance(saved, Mapping):
            raise MongoRevisionAdapterError("committed operation has no durable receipt")
        return RevisionReceipt(
            track_id=saved["track_id"],
            operation_id=saved["operation_id"],
            writer_id=saved["writer_id"],
            revision=int(saved["revision"]),
            parent_revision=int(saved["parent_revision"]),
            fencing_token=int(saved["fencing_token"]),
            payload_sha256=saved["payload_sha256"],
            fingerprint=saved["fingerprint"],
        )

    @staticmethod
    def _revision_from_document(document: Mapping[str, Any]) -> RevisionRecord:
        payload = json.loads(document["payload_json"])
        return RevisionRecord(
            track_id=document["track_id"],
            revision=int(document["revision"]),
            parent_revision=int(document["parent_revision"]),
            operation_id=document["operation_id"],
            writer_id=document["writer_id"],
            fencing_token=int(document["fencing_token"]),
            payload_sha256=document["payload_sha256"],
            payload=_freeze_json(payload),
        )

    @staticmethod
    def _track_state(document: Mapping[str, Any]) -> TrackRevisionState:
        return TrackRevisionState(
            track_id=document["_id"],
            revision=int(document["revision"]),
            fencing_epoch=int(document["fencing_epoch"]),
            control_sequence=int(document["control_sequence"]),
            last_fence_sequence=int(document["last_fence_sequence"]),
        )

    @staticmethod
    def _secret_digest(secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @staticmethod
    def _has_error_label(error: Exception, label: str) -> bool:
        predicate = getattr(error, "has_error_label", None)
        return bool(callable(predicate) and predicate(label))
