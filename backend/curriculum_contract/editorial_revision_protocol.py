"""Isolated editorial revision/CAS reference protocol.

The in-memory implementation is a deterministic, thread-safe reference model.
Its lock linearizes calls only inside one Python process; it is not a MongoDB
adapter and provides no cross-process durability or transaction guarantee.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import secrets
import threading
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol


JsonValue = Any
ProposalValidator = Callable[[Mapping[str, JsonValue]], bool | None]


class RevisionProtocolError(RuntimeError):
    """Base class for domain-level protocol failures."""

    code = "REVISION_PROTOCOL_ERROR"


class RevisionConflict(RevisionProtocolError):
    """The prepared operation was based on a revision that is no longer current."""

    code = "REVISION_CONFLICT"

    def __init__(self, track_id: str, operation_id: str, expected: int, actual: int):
        self.track_id = track_id
        self.operation_id = operation_id
        self.expected_revision = expected
        self.actual_revision = actual
        super().__init__(
            f"operation {operation_id!r} expected revision {expected}, "
            f"but track {track_id!r} is at revision {actual}"
        )


class FencingRejected(RevisionProtocolError):
    """A writer's fencing epoch is not the current epoch for the track."""

    code = "FENCE_REJECTED"

    def __init__(self, track_id: str, supplied: int, current: int):
        self.track_id = track_id
        self.supplied_fence = supplied
        self.current_fence = current
        super().__init__(
            f"fence {supplied} is stale for track {track_id!r}; current fence is {current}"
        )


class IdempotencyConflict(RevisionProtocolError):
    """An operation identity was reused for a different logical command."""

    code = "IDEMPOTENCY_KEY_REUSED"

    def __init__(self, track_id: str, operation_id: str):
        self.track_id = track_id
        self.operation_id = operation_id
        super().__init__(
            f"operation identity {operation_id!r} was reused with different parameters "
            f"for track {track_id!r}"
        )


class WriterAuthorizationError(RevisionProtocolError):
    """The writer credential is absent, revoked, or outside its track scope."""

    code = "WRITER_NOT_AUTHORIZED"


class FenceAuthorityError(RevisionProtocolError):
    """The supplied credential cannot advance the fencing epoch."""

    code = "FENCE_AUTHORITY_REJECTED"


class InvalidProposal(RevisionProtocolError):
    """A command has invalid identity, revision, token, or JSON payload data."""

    code = "INVALID_PROPOSAL"


class ProposalValidationError(RevisionProtocolError):
    """The configured domain validator rejected a prepared proposal."""

    code = "PROPOSAL_VALIDATION_FAILED"


class InvalidPreparation(RevisionProtocolError):
    """A prepared handle is unknown or does not match its stored operation."""

    code = "INVALID_PREPARATION"


class OperationAborted(RevisionProtocolError):
    """The operation was explicitly abandoned and cannot be committed."""

    code = "OPERATION_ABORTED"


class OperationState(str, Enum):
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    CONFLICTED = "CONFLICTED"
    ABORTED = "ABORTED"


@dataclass(frozen=True, slots=True, repr=False)
class WriterCredential:
    """Opaque in-memory writer capability, scoped to one track and writer."""

    track_id: str
    writer_id: str
    _secret: str = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True, repr=False)
class FenceAuthorityCredential:
    """Opaque capability used by a trusted authority to advance a track fence."""

    track_id: str
    authority_id: str
    _secret: str = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class PreparedRevision:
    """Opaque handle to a validated proposal; it is not a confirmed revision."""

    track_id: str
    writer_id: str
    operation_id: str
    expected_revision: int
    fencing_token: int
    payload_sha256: str
    fingerprint: str
    preparation_id: str


@dataclass(frozen=True, slots=True)
class RevisionReceipt:
    """Stable result of one successful logical revision operation."""

    track_id: str
    operation_id: str
    writer_id: str
    revision: int
    parent_revision: int
    fencing_token: int
    payload_sha256: str
    fingerprint: str
    replayed: bool = False


@dataclass(frozen=True, slots=True)
class RevisionRecord:
    """Immutable historical revision returned by the reference store."""

    track_id: str
    revision: int
    parent_revision: int
    operation_id: str
    writer_id: str
    fencing_token: int
    payload_sha256: str
    payload: Mapping[str, JsonValue]


class EditorialRevisionProtocol(Protocol):
    """Storage-independent domain surface for revisioned editorial commands.

    A persistent adapter must make the final fence check, revision CAS,
    operation receipt, and historical revision write atomically durable.
    This protocol alone does not provide those storage guarantees.
    """

    def prepare(
        self,
        *,
        track_id: str,
        credential: WriterCredential,
        operation_id: str,
        expected_revision: int,
        fencing_token: int,
        payload: Mapping[str, JsonValue],
    ) -> PreparedRevision: ...

    def commit(
        self, prepared: PreparedRevision, credential: WriterCredential
    ) -> RevisionReceipt: ...


@dataclass(slots=True)
class _Operation:
    prepared: PreparedRevision
    canonical_payload: str
    state: OperationState = OperationState.PREPARED
    receipt: RevisionReceipt | None = None


def _require_identity(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidProposal(f"{name} must be a non-empty string")


def _normalize_json(value: JsonValue, path: str = "payload") -> JsonValue:
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise InvalidProposal(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, JsonValue] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise InvalidProposal(f"{path} contains a non-string object key")
            normalized[key] = _normalize_json(child, f"{path}.{key}")
        return normalized
    if isinstance(value, (list, tuple)):
        return [
            _normalize_json(child, f"{path}[{index}]")
            for index, child in enumerate(value)
        ]
    raise InvalidProposal(f"{path} contains a non-JSON value")


def _freeze_json(value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(child) for child in value)
    return value


def _canonical_payload(payload: Mapping[str, JsonValue]) -> tuple[str, str, Mapping[str, JsonValue]]:
    if not isinstance(payload, Mapping):
        raise InvalidProposal("payload must be a JSON object")
    normalized = _normalize_json(payload)
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
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise InvalidProposal("payload cannot be canonically encoded as JSON") from exc
    return canonical, hashlib.sha256(encoded).hexdigest(), _freeze_json(normalized)


class InMemoryEditorialRevisionProtocol:
    """Thread-safe, single-process reference for revision/CAS/fencing semantics.

    The per-instance lock is the linearization mechanism for tests. It must not
    be represented as a distributed lock, a MongoDB transaction, durable
    storage, or a production authorization boundary.
    """

    def __init__(self, proposal_validator: ProposalValidator | None = None) -> None:
        self._lock = threading.RLock()
        self._proposal_validator = proposal_validator
        self._writer_credentials: dict[tuple[str, str], str] = {}
        self._fence_authorities: dict[tuple[str, str], str] = {}
        self._fence_by_track: dict[str, int] = {}
        self._revision_by_track: dict[str, int] = {}
        self._history: dict[str, list[RevisionRecord]] = {}
        self._revisions: dict[tuple[str, int], RevisionRecord] = {}
        self._operations: dict[tuple[str, str], _Operation] = {}

    def provision_writer_credential(self, track_id: str, writer_id: str) -> WriterCredential:
        """Provision a test/reference capability; not a user or IAM service."""

        _require_identity(track_id, "track_id")
        _require_identity(writer_id, "writer_id")
        secret = secrets.token_urlsafe(32)
        with self._lock:
            self._writer_credentials[(track_id, writer_id)] = self._secret_digest(secret)
        return WriterCredential(track_id, writer_id, secret)

    def revoke_writer_credential(self, track_id: str, writer_id: str) -> bool:
        """Revoke the scoped in-memory writer capability."""

        _require_identity(track_id, "track_id")
        _require_identity(writer_id, "writer_id")
        with self._lock:
            return self._writer_credentials.pop((track_id, writer_id), None) is not None

    def provision_fence_authority(
        self, track_id: str, authority_id: str
    ) -> FenceAuthorityCredential:
        """Provision a trusted test/reference authority for one track."""

        _require_identity(track_id, "track_id")
        _require_identity(authority_id, "authority_id")
        secret = secrets.token_urlsafe(32)
        with self._lock:
            self._fence_authorities[(track_id, authority_id)] = self._secret_digest(secret)
        return FenceAuthorityCredential(track_id, authority_id, secret)

    def advance_fence(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> int:
        """Advance a server-owned epoch; all handles from earlier epochs become stale.

        The returned epoch may be distributed by a trusted coordinator to
        authorized writers for the current editing epoch. It is not a lease or
        a claim that a writer is the sole editor.
        """

        _require_identity(track_id, "track_id")
        with self._lock:
            self._authenticate_fence_authority(track_id, authority)
            current = self._fence_by_track.get(track_id, 0)
            next_token = current + 1
            self._fence_by_track[track_id] = next_token
            return next_token

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
        """Validate and stage intent without making a confirmed revision."""

        _require_identity(track_id, "track_id")
        _require_identity(operation_id, "operation_id")
        self._validate_revision_number(expected_revision)
        self._validate_fence_number(fencing_token)
        canonical, payload_sha256, frozen_payload = _canonical_payload(payload)

        with self._lock:
            self._authenticate_writer(track_id, credential)
            fingerprint = self._fingerprint(
                track_id,
                credential.writer_id,
                operation_id,
                expected_revision,
                payload_sha256,
            )
            key = (track_id, operation_id)
            existing = self._operations.get(key)
            if existing is not None:
                if not hmac.compare_digest(existing.prepared.fingerprint, fingerprint):
                    raise IdempotencyConflict(track_id, operation_id)
                if existing.state is OperationState.ABORTED:
                    raise OperationAborted(f"operation {operation_id!r} was abandoned")
                if existing.state in (OperationState.COMMITTED, OperationState.CONFLICTED):
                    return existing.prepared
                self._assert_current_fence(track_id, fencing_token)
                if existing.prepared.fencing_token != fencing_token:
                    existing.prepared = replace(
                        existing.prepared, fencing_token=fencing_token
                    )
                return existing.prepared

            self._assert_current_fence(track_id, fencing_token)
            if self._proposal_validator is not None:
                try:
                    accepted = self._proposal_validator(frozen_payload)
                except Exception as exc:
                    raise ProposalValidationError("proposal validator rejected payload") from exc
                if accepted is False:
                    raise ProposalValidationError("proposal validator rejected payload")

            prepared = PreparedRevision(
                track_id=track_id,
                writer_id=credential.writer_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                fencing_token=fencing_token,
                payload_sha256=payload_sha256,
                fingerprint=fingerprint,
                preparation_id=secrets.token_hex(16),
            )
            self._operations[key] = _Operation(prepared, canonical)
            return prepared

    def commit(
        self, prepared: PreparedRevision, credential: WriterCredential
    ) -> RevisionReceipt:
        """Atomically fence, CAS, append history, and record the operation receipt."""

        with self._lock:
            self._authenticate_writer(prepared.track_id, credential)
            if credential.writer_id != prepared.writer_id:
                raise WriterAuthorizationError("credential does not own the preparation")
            key = (prepared.track_id, prepared.operation_id)
            operation = self._operations.get(key)
            if operation is None or not self._same_preparation(operation.prepared, prepared):
                raise InvalidPreparation("prepared handle is unknown or altered")
            if operation.state is OperationState.COMMITTED:
                assert operation.receipt is not None
                return replace(operation.receipt, replayed=True)
            if operation.state is OperationState.ABORTED:
                raise OperationAborted(f"operation {prepared.operation_id!r} was abandoned")
            if operation.state is OperationState.CONFLICTED:
                raise RevisionConflict(
                    prepared.track_id,
                    prepared.operation_id,
                    prepared.expected_revision,
                    self._revision_by_track.get(prepared.track_id, 0),
                )

            if operation.prepared.fencing_token != prepared.fencing_token:
                raise FencingRejected(
                    prepared.track_id,
                    prepared.fencing_token,
                    operation.prepared.fencing_token,
                )
            self._assert_current_fence(prepared.track_id, prepared.fencing_token)
            current_revision = self._revision_by_track.get(prepared.track_id, 0)
            if current_revision != prepared.expected_revision:
                operation.state = OperationState.CONFLICTED
                raise RevisionConflict(
                    prepared.track_id,
                    prepared.operation_id,
                    prepared.expected_revision,
                    current_revision,
                )

            next_revision = current_revision + 1
            payload_value = json.loads(operation.canonical_payload)
            _, payload_sha256, frozen_payload = _canonical_payload(payload_value)
            if not hmac.compare_digest(payload_sha256, prepared.payload_sha256):
                raise InvalidPreparation("prepared payload integrity check failed")
            record = RevisionRecord(
                track_id=prepared.track_id,
                revision=next_revision,
                parent_revision=current_revision,
                operation_id=prepared.operation_id,
                writer_id=prepared.writer_id,
                fencing_token=prepared.fencing_token,
                payload_sha256=payload_sha256,
                payload=frozen_payload,
            )
            receipt = RevisionReceipt(
                track_id=prepared.track_id,
                operation_id=prepared.operation_id,
                writer_id=prepared.writer_id,
                revision=next_revision,
                parent_revision=current_revision,
                fencing_token=prepared.fencing_token,
                payload_sha256=payload_sha256,
                fingerprint=prepared.fingerprint,
            )
            self._history.setdefault(prepared.track_id, []).append(record)
            self._revisions[(prepared.track_id, next_revision)] = record
            self._revision_by_track[prepared.track_id] = next_revision
            operation.state = OperationState.COMMITTED
            operation.receipt = receipt
            return receipt

    def abandon(self, prepared: PreparedRevision, credential: WriterCredential) -> bool:
        """Mark an uncommitted preparation abandoned while preserving its identity."""

        with self._lock:
            self._authenticate_writer(prepared.track_id, credential)
            if credential.writer_id != prepared.writer_id:
                raise WriterAuthorizationError("credential does not own the preparation")
            operation = self._operations.get((prepared.track_id, prepared.operation_id))
            if operation is None or not self._same_preparation(operation.prepared, prepared):
                raise InvalidPreparation("prepared handle is unknown or altered")
            if operation.state is OperationState.ABORTED:
                return False
            if operation.state is not OperationState.PREPARED:
                return False
            self._assert_current_fence(prepared.track_id, prepared.fencing_token)
            if operation.prepared.fencing_token != prepared.fencing_token:
                raise FencingRejected(
                    prepared.track_id,
                    operation.prepared.fencing_token,
                    self._fence_by_track.get(prepared.track_id, 0),
                )
            operation.state = OperationState.ABORTED
            return True

    def operation_state(self, track_id: str, operation_id: str) -> OperationState | None:
        """Return non-sensitive operation state for local tests and diagnostics."""

        with self._lock:
            operation = self._operations.get((track_id, operation_id))
            return None if operation is None else operation.state

    def prepared_payload(
        self,
        track_id: str,
        operation_id: str,
        credential: WriterCredential,
    ) -> Mapping[str, JsonValue]:
        """Recover the writer's staged payload after conflict, if still authorized."""

        with self._lock:
            self._authenticate_writer(track_id, credential)
            operation = self._operations.get((track_id, operation_id))
            if operation is None or operation.prepared.writer_id != credential.writer_id:
                raise InvalidPreparation("prepared operation was not found")
            if operation.state is OperationState.ABORTED:
                raise OperationAborted(f"operation {operation_id!r} was abandoned")
            return _freeze_json(json.loads(operation.canonical_payload))

    def current_revision(self, track_id: str) -> int:
        with self._lock:
            return self._revision_by_track.get(track_id, 0)

    def read_revision(self, track_id: str, revision: int) -> RevisionRecord | None:
        with self._lock:
            return self._revisions.get((track_id, revision))

    def history(self, track_id: str) -> tuple[RevisionRecord, ...]:
        with self._lock:
            return tuple(self._history.get(track_id, ()))

    @staticmethod
    def _secret_digest(secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @staticmethod
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

    @staticmethod
    def _validate_revision_number(revision: int) -> None:
        if type(revision) is not int or revision < 0:
            raise InvalidProposal("expected_revision must be a non-negative server revision")

    @staticmethod
    def _validate_fence_number(token: int) -> None:
        if type(token) is not int or token < 1:
            raise InvalidProposal("fencing_token must be a positive server-issued epoch")

    def _authenticate_writer(self, track_id: str, credential: WriterCredential) -> None:
        if not isinstance(credential, WriterCredential) or credential.track_id != track_id:
            raise WriterAuthorizationError("writer credential is missing or outside track scope")
        stored = self._writer_credentials.get((track_id, credential.writer_id))
        supplied = self._secret_digest(credential._secret)
        if stored is None or not hmac.compare_digest(stored, supplied):
            raise WriterAuthorizationError("writer credential is invalid or revoked")

    def _authenticate_fence_authority(
        self, track_id: str, authority: FenceAuthorityCredential
    ) -> None:
        if (
            not isinstance(authority, FenceAuthorityCredential)
            or authority.track_id != track_id
        ):
            raise FenceAuthorityError("fence authority credential is missing or out of scope")
        stored = self._fence_authorities.get((track_id, authority.authority_id))
        supplied = self._secret_digest(authority._secret)
        if stored is None or not hmac.compare_digest(stored, supplied):
            raise FenceAuthorityError("fence authority credential is invalid")

    def _assert_current_fence(self, track_id: str, supplied: int) -> None:
        current = self._fence_by_track.get(track_id, 0)
        if supplied != current:
            raise FencingRejected(track_id, supplied, current)

    @staticmethod
    def _same_preparation(stored: PreparedRevision, supplied: PreparedRevision) -> bool:
        return (
            isinstance(supplied, PreparedRevision)
            and stored.track_id == supplied.track_id
            and stored.writer_id == supplied.writer_id
            and stored.operation_id == supplied.operation_id
            and stored.expected_revision == supplied.expected_revision
            and stored.payload_sha256 == supplied.payload_sha256
            and hmac.compare_digest(stored.fingerprint, supplied.fingerprint)
            and hmac.compare_digest(stored.preparation_id, supplied.preparation_id)
        )
