"""Isolated C11 authorization and server-issued editorial capabilities.

This module is experimental and must not be imported by application routes or
services. Its Mongo authorization documents are synthetic test state, separate
from (and never a replacement for) the C8 per-track revision/fencing record.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Awaitable, Callable, Mapping

from .editorial_revision_protocol import PreparedRevision, RevisionReceipt, WriterCredential

_TEST_DATABASE = re.compile(r"^editorial_revision_test_c10_c11_[a-zA-Z0-9_-]{8,64}$")
_NAMESPACE = re.compile(r"^c8_[a-z0-9_]{1,28}$")
_IDENTITY = re.compile(r"^[^\x00]{1,256}$")
_OPERATION_KINDS = frozenset({"block.update"})
AsyncParticipant = Callable[[Any, RevisionReceipt], Awaitable[None]]


class AuthorizationCode(str, Enum):
    ALLOWED = "allowed"
    AUTHENTICATION_REQUIRED = "authentication_required"
    SESSION_INVALID = "session_invalid"
    PERMISSION_INSUFFICIENT = "permission_insufficient"
    TRACK_SCOPE_DENIED = "track_scope_denied"
    RESOURCE_NOT_FOUND = "resource_not_found"
    AUTHORIZATION_REVOKED = "authorization_revoked"
    CAPABILITY_INVALID = "capability_invalid"
    INDETERMINATE = "indeterminate"


class EditorialAuthorizationError(PermissionError):
    def __init__(self, code: AuthorizationCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class AuthenticatedPrincipal:
    """Signed server-side authentication result; never accepted from a request body."""

    actor_id: str
    session_id: str = field(repr=False)
    role: str
    permissions: tuple[str, ...]
    session_valid: bool
    _signature: str = field(repr=False)


class SyntheticPrincipalAuthority:
    """Test-only attestor standing in for a trusted auth/session boundary."""

    def __init__(self, secret: bytes) -> None:
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("principal attestation key must be at least 32 bytes")
        self._secret = bytes(secret)

    def attest(
        self,
        *,
        actor_id: str,
        session_id: str,
        role: str,
        permissions: tuple[str, ...] | list[str] | set[str],
        session_valid: bool = True,
    ) -> AuthenticatedPrincipal:
        actor = _identity(actor_id, "actor_id")
        session = _identity(session_id, "session_id")
        if not isinstance(role, str) or role not in {"admin", "editor", "student", "synthetic"}:
            raise ValueError("role is outside the experimental role set")
        if type(session_valid) is not bool:
            raise ValueError("session_valid must be boolean")
        if not isinstance(permissions, (tuple, list, set, frozenset)):
            raise ValueError("permissions must be a closed collection of strings")
        permission_values = tuple(sorted({_identity(value, "permission") for value in permissions}))
        claims = _principal_claims(actor, session, role, permission_values, session_valid)
        signature = self._sign(claims)
        return AuthenticatedPrincipal(actor, session, role, permission_values, session_valid, signature)

    def verifies(self, principal: object) -> bool:
        if not isinstance(principal, AuthenticatedPrincipal):
            return False
        try:
            claims = _principal_claims(
                principal.actor_id,
                principal.session_id,
                principal.role,
                principal.permissions,
                principal.session_valid,
            )
            return hmac.compare_digest(self._sign(claims), principal._signature)
        except (TypeError, ValueError):
            return False

    def _sign(self, claims: Mapping[str, Any]) -> str:
        payload = _canonical(claims)
        return hmac.new(self._secret, b"trilhacode:c11:principal\x00" + payload, hashlib.sha256).hexdigest()


@dataclass(frozen=True, slots=True, repr=False)
class ServerWriterContext:
    """Writer credential and fence supplied by trusted server-side wiring."""

    credential: WriterCredential = field(repr=False)
    fencing_token: int = field(repr=False)


@dataclass(frozen=True, slots=True, repr=False)
class EditorialCapability:
    """Unserializable-to-HTTP capability scoped to actor, track and one intent."""

    actor_id: str
    role: str
    session_digest: str = field(repr=False)
    track_id: str
    authorization_scope_track: str = field(repr=False)
    operation_kind: str
    operation_id: str = field(repr=False)
    authorization_epoch: int = field(repr=False)
    writer_id: str = field(repr=False)
    fencing_token: int = field(repr=False)
    expected_revision: int = field(repr=False)
    prepared_sha256: str = field(repr=False)
    prepared_fingerprint: str = field(repr=False)
    preparation_id: str = field(repr=False)
    credential: WriterCredential = field(repr=False, compare=False)
    _signature: str = field(repr=False, compare=False)
    _issuer_seal: object = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True, repr=False)
class AuthorizationDecision:
    code: AuthorizationCode
    capability: EditorialCapability | None = field(default=None, repr=False)

    @property
    def allowed(self) -> bool:
        return self.code is AuthorizationCode.ALLOWED and self.capability is not None


class MongoEditorialAuthorizationGate:
    """C11 test-only authorization ledger and transaction participant guard."""

    def __init__(self, database: Any, *, namespace: str, capability_key: bytes) -> None:
        name = getattr(database, "name", None)
        if not isinstance(name, str) or not _TEST_DATABASE.fullmatch(name):
            raise ValueError("C11 authorization requires its disposable test database")
        if not isinstance(namespace, str) or not _NAMESPACE.fullmatch(namespace):
            raise ValueError("authorization namespace must use the C8 test format")
        if not isinstance(capability_key, bytes) or len(capability_key) < 32:
            raise ValueError("capability signing key must be at least 32 bytes")
        self._database = database
        self._namespace = namespace
        self._authorizations = database[f"{namespace}_c11_authorizations"]
        self._capability_key = bytes(capability_key)
        self._issuer_seal = object()

    @staticmethod
    def preflight_principal(
        principal: object, principal_authority: SyntheticPrincipalAuthority
    ) -> AuthorizationCode:
        """Reject unauthenticated or globally unauthorized callers before lookup."""

        if (
            not isinstance(principal_authority, SyntheticPrincipalAuthority)
            or not principal_authority.verifies(principal)
        ):
            return AuthorizationCode.AUTHENTICATION_REQUIRED
        assert isinstance(principal, AuthenticatedPrincipal)
        if not principal.session_valid:
            return AuthorizationCode.SESSION_INVALID
        if "content.write" not in principal.permissions:
            return AuthorizationCode.PERMISSION_INSUFFICIENT
        return AuthorizationCode.ALLOWED

    async def provision_synthetic_scope(
        self,
        *,
        actor_id: str,
        session_id: str,
        track_id: str,
        permissions: tuple[str, ...] | list[str] | set[str],
        allowed_operations: tuple[str, ...] | list[str] | set[str],
        role: str = "editor",
        global_admin_scope: bool = False,
    ) -> None:
        """Create synthetic IAM state for tests; not an operational grant API."""

        actor = _identity(actor_id, "actor_id")
        session = _identity(session_id, "session_id")
        track = _identity(track_id, "track_id")
        if type(global_admin_scope) is not bool:
            raise ValueError("global_admin_scope must be boolean")
        if role not in {"admin", "editor", "student", "synthetic"}:
            raise ValueError("role is outside the experimental role set")
        permission_values = sorted({_identity(value, "permission") for value in permissions})
        operations = sorted({_identity(value, "operation") for value in allowed_operations})
        if any(value not in _OPERATION_KINDS for value in operations):
            raise ValueError("operation is outside the experimental operation set")
        if track == "*" and not (global_admin_scope and role == "admin"):
            raise ValueError("wildcard scope requires an explicit admin grant")
        _id = _scope_id(actor, track)
        await self._authorizations.insert_one(
            {
                "_id": _id,
                "actor_id": actor,
                "track_id": track,
                "role": role,
                "permissions": permission_values,
                "allowed_operations": operations,
                "global_admin_scope": global_admin_scope,
                "active": True,
                "session_active": True,
                "session_sha256": hashlib.sha256(session.encode("utf-8")).hexdigest(),
                "authorization_epoch": 1,
                "use_sequence": 0,
                "schema_version": 1,
            }
        )

    async def revoke_synthetic_scope(
        self,
        *,
        actor_id: str,
        track_id: str,
        revoke_session: bool = False,
        remove_content_write: bool = False,
    ) -> bool:
        """Advance the synthetic authorization epoch and revoke selected facts."""

        actor = _identity(actor_id, "actor_id")
        track = _identity(track_id, "track_id")
        if type(revoke_session) is not bool or type(remove_content_write) is not bool:
            raise ValueError("revocation switches must be boolean")
        update: dict[str, Any] = {"$inc": {"authorization_epoch": 1}}
        set_values: dict[str, Any] = {"active": False}
        if revoke_session:
            set_values["session_active"] = False
        if remove_content_write:
            set_values["permissions"] = []
        if set_values:
            update["$set"] = set_values
        result = await self._authorizations.update_one(
            {"_id": _scope_id(actor, track)}, update
        )
        return result.matched_count == 1

    async def issue_capability(
        self,
        principal: object,
        principal_authority: SyntheticPrincipalAuthority,
        *,
        track_id: str,
        operation_kind: str,
        operation_id: str,
        expected_revision: int,
        writer_context: ServerWriterContext,
    ) -> AuthorizationDecision:
        """Authorize current actor/scope and issue a server-signed capability."""

        if not isinstance(principal_authority, SyntheticPrincipalAuthority) or not principal_authority.verifies(principal):
            return AuthorizationDecision(AuthorizationCode.AUTHENTICATION_REQUIRED)
        assert isinstance(principal, AuthenticatedPrincipal)
        if not principal.session_valid:
            return AuthorizationDecision(AuthorizationCode.SESSION_INVALID)
        if "content.write" not in principal.permissions:
            return AuthorizationDecision(AuthorizationCode.PERMISSION_INSUFFICIENT)
        if operation_kind not in _OPERATION_KINDS or type(expected_revision) is not int or expected_revision < 0:
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        try:
            record = await self._find_scope(principal, track_id)
        except Exception:
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        code = _scope_decision(principal, record, track_id, operation_kind)
        if code is not AuthorizationCode.ALLOWED or record is None:
            return AuthorizationDecision(code)
        if (
            not isinstance(writer_context, ServerWriterContext)
            or not isinstance(writer_context.credential, WriterCredential)
            or writer_context.credential.track_id != track_id
            or type(writer_context.fencing_token) is not int
            or writer_context.fencing_token <= 0
        ):
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        if not isinstance(operation_id, str) or not _IDENTITY.fullmatch(operation_id):
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        claims = {
            "actor": principal.actor_id,
            "role": principal.role,
            "session_digest": hashlib.sha256(principal.session_id.encode("utf-8")).hexdigest(),
            "track": track_id,
            "authorization_scope_track": record["track_id"],
            "operation": operation_kind,
            "operation_id": operation_id,
            "authorization_epoch": int(record["authorization_epoch"]),
            "writer_id": writer_context.credential.writer_id,
            "credential_digest": hashlib.sha256(
                writer_context.credential._secret.encode("utf-8")
            ).hexdigest(),
            "fence": writer_context.fencing_token,
            "expected_revision": expected_revision,
        }
        capability = EditorialCapability(
            actor_id=claims["actor"],
            role=claims["role"],
            session_digest=claims["session_digest"],
            track_id=claims["track"],
            authorization_scope_track=claims["authorization_scope_track"],
            operation_kind=claims["operation"],
            operation_id=claims["operation_id"],
            authorization_epoch=claims["authorization_epoch"],
            writer_id=claims["writer_id"],
            fencing_token=claims["fence"],
            expected_revision=claims["expected_revision"],
            prepared_sha256="",
            prepared_fingerprint="",
            preparation_id="",
            credential=writer_context.credential,
            _signature="",
            _issuer_seal=self._issuer_seal,
        )
        capability = replace(
            capability, _signature=self._sign(_capability_claims(capability))
        )
        return AuthorizationDecision(AuthorizationCode.ALLOWED, capability)

    def bind_preparation(
        self, capability: EditorialCapability, prepared: PreparedRevision
    ) -> EditorialCapability:
        """Bind the authorized capability to the immutable C8 preparation handle."""

        self._verify_capability_signature(capability)
        if (
            prepared.track_id != capability.track_id
            or prepared.writer_id != capability.writer_id
            or prepared.operation_id != capability.operation_id
            or prepared.expected_revision != capability.expected_revision
            or prepared.fencing_token != capability.fencing_token
        ):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        claims = _capability_claims(capability)
        claims.update(
            {
                "prepared_sha256": prepared.payload_sha256,
                "prepared_fingerprint": prepared.fingerprint,
                "preparation_id": prepared.preparation_id,
            }
        )
        return EditorialCapability(
            actor_id=capability.actor_id,
            role=capability.role,
            session_digest=capability.session_digest,
            track_id=capability.track_id,
            authorization_scope_track=capability.authorization_scope_track,
            operation_kind=capability.operation_kind,
            operation_id=capability.operation_id,
            authorization_epoch=capability.authorization_epoch,
            writer_id=capability.writer_id,
            fencing_token=capability.fencing_token,
            expected_revision=capability.expected_revision,
            prepared_sha256=prepared.payload_sha256,
            prepared_fingerprint=prepared.fingerprint,
            preparation_id=prepared.preparation_id,
            credential=capability.credential,
            _signature=self._sign(claims),
            _issuer_seal=self._issuer_seal,
        )

    async def commit_authorized(
        self,
        adapter: Any,
        principal: object,
        principal_authority: SyntheticPrincipalAuthority,
        capability: EditorialCapability,
        prepared: PreparedRevision,
        *,
        participant: AsyncParticipant,
    ) -> RevisionReceipt:
        """Revalidate current authorization then guard it inside the C8 transaction."""

        self._verify_capability_signature(capability)
        if (
            not isinstance(principal_authority, SyntheticPrincipalAuthority)
            or not principal_authority.verifies(principal)
            or not isinstance(principal, AuthenticatedPrincipal)
            or principal.actor_id != capability.actor_id
            or principal.role != capability.role
            or hashlib.sha256(principal.session_id.encode("utf-8")).hexdigest()
            != capability.session_digest
            or not principal.session_valid
            or "content.write" not in principal.permissions
            or prepared.track_id != capability.track_id
            or prepared.writer_id != capability.writer_id
            or prepared.operation_id != capability.operation_id
            or prepared.expected_revision != capability.expected_revision
            or prepared.fencing_token != capability.fencing_token
            or prepared.payload_sha256 != capability.prepared_sha256
            or prepared.fingerprint != capability.prepared_fingerprint
            or prepared.preparation_id != capability.preparation_id
        ):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        await self._assert_current(capability)

        async def guarded_participant(session: Any, receipt: RevisionReceipt) -> None:
            query = {
                "_id": _scope_id(capability.actor_id, capability.authorization_scope_track),
                "actor_id": capability.actor_id,
                "authorization_epoch": capability.authorization_epoch,
                "session_sha256": capability.session_digest,
                "active": True,
                "session_active": True,
                "permissions": "content.write",
                "allowed_operations": capability.operation_kind,
            }
            guarded = await self._authorizations.update_one(
                query, {"$inc": {"use_sequence": 1}}, session=session
            )
            if guarded.matched_count != 1:
                # A conflicting write from the revoker causes MongoDB to abort
                # or retry this transaction; on retry, this predicate fails.
                raise EditorialAuthorizationError(AuthorizationCode.AUTHORIZATION_REVOKED)
            await participant(session, receipt)

        return await adapter.commit(
            prepared, capability.credential, participant=guarded_participant
        )

    async def validate_external_receipt_access(
        self,
        capability: EditorialCapability,
        principal: object,
        principal_authority: SyntheticPrincipalAuthority,
        *,
        track_id: str,
        operation_id: str,
    ) -> None:
        """Revalidate authorization before exposing a minimal external receipt."""

        self._verify_capability_signature(capability)
        if (
            not isinstance(principal_authority, SyntheticPrincipalAuthority)
            or not principal_authority.verifies(principal)
            or not isinstance(principal, AuthenticatedPrincipal)
            or principal.actor_id != capability.actor_id
            or principal.role != capability.role
            or not principal.session_valid
            or "content.write" not in principal.permissions
            or capability.track_id != track_id
            or capability.operation_id != operation_id
            or hashlib.sha256(principal.session_id.encode("utf-8")).hexdigest()
            != capability.session_digest
        ):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        await self._assert_current(capability)

    async def _find_scope(
        self, principal: AuthenticatedPrincipal, track_id: str
    ) -> Mapping[str, Any] | None:
        if not isinstance(track_id, str) or not _IDENTITY.fullmatch(track_id):
            return None
        exact = await self._authorizations.find_one(
            {"_id": _scope_id(principal.actor_id, track_id)}
        )
        if exact is not None:
            return exact
        if principal.role == "admin":
            global_record = await self._authorizations.find_one(
                {"_id": _scope_id(principal.actor_id, "*")}
            )
            if global_record is not None and global_record.get("global_admin_scope") is True:
                return global_record
        return None

    async def _assert_current(self, capability: EditorialCapability) -> None:
        scope_track = capability.authorization_scope_track
        try:
            record = await self._authorizations.find_one(
                {"_id": _scope_id(capability.actor_id, scope_track)}
            )
        except Exception as exc:
            raise EditorialAuthorizationError(AuthorizationCode.INDETERMINATE) from exc
        if record is None:
            raise EditorialAuthorizationError(AuthorizationCode.AUTHORIZATION_REVOKED)
        current_code = _scope_decision_fields(
            record,
            actor_id=capability.actor_id,
            track_id=capability.track_id,
            operation_kind=capability.operation_kind,
            session_digest=capability.session_digest,
            role=record.get("role"),
        )
        if (
            current_code is not AuthorizationCode.ALLOWED
            or record.get("role") != capability.role
            or int(record.get("authorization_epoch", -1)) != capability.authorization_epoch
        ):
            raise EditorialAuthorizationError(
                AuthorizationCode.SESSION_INVALID
                if current_code is AuthorizationCode.SESSION_INVALID
                else AuthorizationCode.AUTHORIZATION_REVOKED
            )

    def _verify_capability_signature(self, capability: object) -> None:
        if not isinstance(capability, EditorialCapability) or capability._issuer_seal is not self._issuer_seal:
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        claims = _capability_claims(capability)
        expected = self._sign(claims)
        if not hmac.compare_digest(expected, capability._signature):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        credential = capability.credential
        if not isinstance(credential._secret, str) or not credential._secret:
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        credential_digest = hashlib.sha256(credential._secret.encode("utf-8")).hexdigest()
        if (
            credential.track_id != capability.track_id
            or credential.writer_id != capability.writer_id
            or not hmac.compare_digest(credential_digest, claims.get("credential_digest", ""))
        ):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)

    def _sign(self, claims: Mapping[str, Any]) -> str:
        return hmac.new(
            self._capability_key,
            b"trilhacode:c11:editorial-capability\x00" + _canonical(claims),
            hashlib.sha256,
        ).hexdigest()


def _scope_decision(
    principal: AuthenticatedPrincipal,
    record: Mapping[str, Any] | None,
    track_id: str,
    operation_kind: str,
) -> AuthorizationCode:
    if record is None:
        return AuthorizationCode.TRACK_SCOPE_DENIED
    return _scope_decision_fields(
        record,
        actor_id=principal.actor_id,
        track_id=track_id,
        operation_kind=operation_kind,
        session_digest=hashlib.sha256(principal.session_id.encode("utf-8")).hexdigest(),
        role=principal.role,
    )


def _scope_decision_fields(
    record: Mapping[str, Any],
    *,
    actor_id: str,
    track_id: str,
    operation_kind: str,
    session_digest: str,
    role: Any,
) -> AuthorizationCode:
    scope_track = record.get("track_id")
    is_exact = scope_track == track_id
    is_explicit_admin_global = (
        scope_track == "*" and role == "admin" and record.get("global_admin_scope") is True
    )
    if (
        record.get("actor_id") != actor_id
        or not (is_exact or is_explicit_admin_global)
        or record.get("role") != role
        or not isinstance(record.get("allowed_operations"), list)
        or operation_kind not in record.get("allowed_operations", [])
    ):
        return AuthorizationCode.TRACK_SCOPE_DENIED
    if not record.get("session_active", False) or not hmac.compare_digest(
        str(record.get("session_sha256", "")), session_digest
    ):
        return AuthorizationCode.SESSION_INVALID
    if not record.get("active", False):
        return AuthorizationCode.TRACK_SCOPE_DENIED
    if not isinstance(record.get("permissions"), list):
        return AuthorizationCode.INDETERMINATE
    if "content.write" not in record.get("permissions", []):
        return AuthorizationCode.PERMISSION_INSUFFICIENT
    return AuthorizationCode.ALLOWED


def _capability_claims(capability: EditorialCapability) -> dict[str, Any]:
    return {
        "actor": capability.actor_id,
        "role": capability.role,
        "session_digest": capability.session_digest,
        "track": capability.track_id,
        "authorization_scope_track": capability.authorization_scope_track,
        "operation": capability.operation_kind,
        "operation_id": capability.operation_id,
        "authorization_epoch": capability.authorization_epoch,
        "writer_id": capability.writer_id,
        "credential_digest": hashlib.sha256(
            capability.credential._secret.encode("utf-8")
        ).hexdigest(),
        "fence": capability.fencing_token,
        "expected_revision": capability.expected_revision,
        "prepared_sha256": capability.prepared_sha256,
        "prepared_fingerprint": capability.prepared_fingerprint,
        "preparation_id": capability.preparation_id,
    }


def _scope_id(actor_id: str, track_id: str) -> str:
    value = json.dumps([actor_id, track_id], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _principal_claims(
    actor_id: str, session_id: str, role: str, permissions: tuple[str, ...], session_valid: bool
) -> dict[str, Any]:
    return {
        "actor": _identity(actor_id, "actor_id"),
        "session_digest": hashlib.sha256(_identity(session_id, "session_id").encode("utf-8")).hexdigest(),
        "role": role,
        "permissions": list(permissions),
        "session_valid": session_valid,
    }


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _identity(value: str, name: str) -> str:
    if not isinstance(value, str) or not _IDENTITY.fullmatch(value) or not value.strip():
        raise ValueError(f"{name} is invalid")
    return value
