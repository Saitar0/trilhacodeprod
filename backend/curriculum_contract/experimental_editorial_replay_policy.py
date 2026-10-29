"""Minimal, authorization-aware receipt access for isolated C11 experiments."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference

from .experimental_editorial_authorization import (
    EditorialAuthorizationError,
    EditorialCapability,
    MongoEditorialAuthorizationGate,
    SyntheticPrincipalAuthority,
)

_TEST_DATABASE = re.compile(r"^editorial_revision_test_c10_c11_[a-zA-Z0-9_-]{8,64}$")
_NAMESPACE = re.compile(r"^c8_[a-z0-9_]{1,28}$")


class ReceiptLookupState(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    PENDING = "pending"
    INDETERMINATE = "indeterminate"
    DENIED = "denied"
    CONFLICT = "conflict"


class ProtectedResource(str, Enum):
    EDITORIAL_CONTENT = "editorial_content"
    AUDIT = "audit"
    REVISION_HISTORY = "revision_history"
    RECEIPT = "receipt"
    INTENT_FINGERPRINT = "intent_fingerprint"
    OPERATION_PAYLOAD = "operation_payload"


@dataclass(frozen=True, slots=True)
class MinimalEditorialReceipt:
    revision: int
    parent_revision: int
    replayed: bool = True


@dataclass(frozen=True, slots=True)
class ReceiptLookup:
    state: ReceiptLookupState
    receipt: MinimalEditorialReceipt | None = None


@dataclass(frozen=True, slots=True, repr=False)
class InternalReconciliationPermit:
    _database_name: str = field(repr=False)
    _namespace: str = field(repr=False)
    _track_id: str = field(repr=False)
    _operation_id: str = field(repr=False)
    _signature: str = field(repr=False)


class InternalReconciliationAuthority:
    """Trusted recovery service token issuer used only by isolated tests."""

    def __init__(self, secret: bytes) -> None:
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("reconciliation signing key must be at least 32 bytes")
        self._secret = bytes(secret)
        self._seal = object()

    def issue(
        self,
        *,
        database_name: str,
        namespace: str,
        track_id: str,
        operation_id: str,
    ) -> InternalReconciliationPermit:
        _validate_receipt_scope(database_name, namespace, track_id, operation_id)
        claims = (database_name, namespace, track_id, operation_id)
        nonce = secrets.token_hex(16)
        signature = hmac.new(
            self._secret,
            b"trilhacode:c11:internal-reconciliation\x00"
            + _canonical_scope(claims, nonce),
            hashlib.sha256,
        ).hexdigest()
        return InternalReconciliationPermit(*claims, f"{nonce}.{signature}")

    def verify(
        self,
        permit: object,
        *,
        database_name: str,
        namespace: str,
        track_id: str,
        operation_id: str,
    ) -> bool:
        if not isinstance(permit, InternalReconciliationPermit):
            return False
        claims = (database_name, namespace, track_id, operation_id)
        if claims != (
            permit._database_name,
            permit._namespace,
            permit._track_id,
            permit._operation_id,
        ):
            return False
        try:
            nonce, supplied = permit._signature.split(".", 1)
        except (AttributeError, ValueError):
            return False
        expected = hmac.new(
            self._secret,
            b"trilhacode:c11:internal-reconciliation\x00"
            + _canonical_scope(claims, nonce),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, supplied)


@dataclass(frozen=True, slots=True)
class ReadAccessContext:
    """Proposed ACL facts; role labels are not claimed to be runtime roles."""

    authenticated: bool
    session_valid: bool
    track_scope: bool
    actor_matches: bool = False
    explicit_global_admin_scope: bool = False
    reconciliation_service: bool = False
    audit_service: bool = False
    integrity_service: bool = False
    audit_reviewer: bool = False
    public_content: bool = False
    revoked: bool = False


def may_read_resource(resource: ProtectedResource, context: ReadAccessContext) -> bool:
    """Fail-closed proposed ACL matrix for testable data classes."""

    if not context.authenticated or not context.session_valid or context.revoked:
        return resource is ProtectedResource.RECEIPT and context.reconciliation_service
    scoped = context.track_scope or context.explicit_global_admin_scope
    if resource is ProtectedResource.EDITORIAL_CONTENT:
        return scoped or context.public_content
    if resource is ProtectedResource.RECEIPT:
        return context.reconciliation_service or (scoped and context.actor_matches)
    if resource in {ProtectedResource.AUDIT, ProtectedResource.REVISION_HISTORY}:
        return context.audit_service or (scoped and (context.actor_matches or context.audit_reviewer))
    # Digests and stored operation intents are integrity internals, not user data.
    if resource in {ProtectedResource.INTENT_FINGERPRINT, ProtectedResource.OPERATION_PAYLOAD}:
        return context.integrity_service
    return False


async def lookup_internal_committed_receipt(
    database: Any,
    *,
    namespace: str,
    track_id: str,
    operation_id: str,
    authority: InternalReconciliationAuthority,
    permit: InternalReconciliationPermit,
) -> ReceiptLookup:
    """Trusted recovery read; never returns intent, payload or fingerprint fields."""

    database_name = getattr(database, "name", None)
    if (
        not isinstance(database_name, str)
        or not isinstance(authority, InternalReconciliationAuthority)
        or not authority.verify(
            permit,
            database_name=database_name,
            namespace=namespace,
            track_id=track_id,
            operation_id=operation_id,
        )
    ):
        raise PermissionError("internal reconciliation authority is required")
    return await _lookup_minimal_committed_receipt(
        database,
        namespace=namespace,
        track_id=track_id,
        operation_id=operation_id,
    )


async def _lookup_minimal_committed_receipt(
    database: Any,
    *,
    namespace: str,
    track_id: str,
    operation_id: str,
) -> ReceiptLookup:
    """Read only a minimal receipt after the caller's trust check succeeds."""

    name = getattr(database, "name", None)
    if not isinstance(name, str) or not _TEST_DATABASE.fullmatch(name):
        raise ValueError("C11 receipt lookup requires its disposable test database")
    if not isinstance(namespace, str) or not _NAMESPACE.fullmatch(namespace):
        raise ValueError("receipt namespace must use the C8 test format")
    if not _safe_identity(track_id) or not _safe_identity(operation_id):
        return ReceiptLookup(ReceiptLookupState.NOT_FOUND)
    try:
        durable_database = database.with_options(
            read_concern=ReadConcern("majority"),
            read_preference=ReadPreference.PRIMARY,
        )
        document = await durable_database[f"{namespace}_operations"].find_one(
            {"track_id": track_id, "operation_id": operation_id},
            {"_id": 0, "state": 1, "receipt": 1},
        )
    except Exception:
        # Deliberately return a non-diagnostic state; do not expose driver errors.
        return ReceiptLookup(ReceiptLookupState.INDETERMINATE)
    if document is None:
        return ReceiptLookup(ReceiptLookupState.NOT_FOUND)
    if document.get("state") != "COMMITTED":
        return ReceiptLookup(ReceiptLookupState.PENDING)
    receipt = document.get("receipt")
    if not isinstance(receipt, dict):
        return ReceiptLookup(ReceiptLookupState.INDETERMINATE)
    revision = receipt.get("revision")
    parent_revision = receipt.get("parent_revision")
    if (
        type(revision) is not int
        or type(parent_revision) is not int
        or revision <= 0
        or parent_revision < 0
        or parent_revision + 1 != revision
    ):
        return ReceiptLookup(ReceiptLookupState.INDETERMINATE)
    return ReceiptLookup(
        ReceiptLookupState.FOUND,
        MinimalEditorialReceipt(revision, parent_revision, replayed=True),
    )


async def lookup_external_receipt(
    database: Any,
    *,
    namespace: str,
    track_id: str,
    operation_id: str,
    capability: EditorialCapability | None,
    authorization_gate: MongoEditorialAuthorizationGate,
    principal: object,
    principal_authority: SyntheticPrincipalAuthority,
) -> ReceiptLookup:
    """External receipt read requires a fresh, scoped server capability."""

    if not isinstance(capability, EditorialCapability):
        return ReceiptLookup(ReceiptLookupState.DENIED)
    try:
        await authorization_gate.validate_external_receipt_access(
            capability,
            principal,
            principal_authority,
            track_id=track_id,
            operation_id=operation_id,
        )
    except EditorialAuthorizationError as exc:
        if exc.code.value == "indeterminate":
            return ReceiptLookup(ReceiptLookupState.INDETERMINATE)
        return ReceiptLookup(ReceiptLookupState.DENIED)
    return await _lookup_minimal_committed_receipt(
        database,
        namespace=namespace,
        track_id=track_id,
        operation_id=operation_id,
    )


def _safe_identity(value: str) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and "\x00" not in value
        and len(value.encode("utf-8")) <= 256
    )


def _validate_receipt_scope(
    database_name: str, namespace: str, track_id: str, operation_id: str
) -> None:
    if not isinstance(database_name, str) or not _TEST_DATABASE.fullmatch(database_name):
        raise ValueError("reconciliation permit requires a disposable C11 database")
    if not isinstance(namespace, str) or not _NAMESPACE.fullmatch(namespace):
        raise ValueError("reconciliation permit requires a C8 test namespace")
    if not _safe_identity(track_id) or not _safe_identity(operation_id):
        raise ValueError("reconciliation permit scope is invalid")


def _canonical_scope(scope: tuple[str, str, str, str], nonce: str) -> bytes:
    return "\x00".join((*scope, nonce)).encode("utf-8")
