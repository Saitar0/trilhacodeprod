"""C12 disposable IAM/grant ledger for editorial ordering experiments only.

This module is intentionally separate from the active IAM. It models the
coordination contract needed if principal, session and track-grant revocations
are to order against an editorial commit in the same MongoDB transaction.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Mapping

from pymongo import AsyncMongoClient

from .editorial_revision_protocol import RevisionReceipt
from .experimental_editorial_grants import (
    EDITORIAL_OPERATIONS,
    EditorialTrackGrant,
    GrantState,
)

_DATABASE = re.compile(r"^editorial_revision_test_c10_c11_c12_[a-zA-Z0-9_-]{8,48}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_ROLES = frozenset({"admin", "editor", "student"})
_KNOWN_PERMISSIONS = frozenset({
    "content.read", "content.write", "content.publish", "content.delete",
    "taxonomy.manage", "users.manage", "progress.write", "submissions.grade",
})
_ROLE_PERMISSIONS = {
    "admin": frozenset({
        "content.read", "content.write", "content.publish", "content.delete",
        "taxonomy.manage", "users.manage", "progress.write", "submissions.grade",
    }),
    "editor": frozenset({
        "content.read", "content.write", "content.publish", "content.delete",
        "progress.write", "submissions.grade",
    }),
    "student": frozenset({"progress.write"}),
}
_OPERATION_PERMISSION = {
    "block.create": "content.write",
    "block.update": "content.write",
    "node.update": "content.write",
    "content.publish": "content.publish",
    "content.delete": "content.delete",
}
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
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True, repr=False)
class EditorialAuthorizationCapability:
    actor_id: str
    session_digest: str = field(repr=False)
    role: str
    track_id: str
    operation: str
    grant_scope_track: str = field(repr=False)
    global_admin_scope: bool = field(repr=False)
    principal_epoch: int = field(repr=False)
    session_epoch: int = field(repr=False)
    grant_id: str = field(repr=False)
    grant_epoch: int = field(repr=False)
    _signature: str = field(repr=False, compare=False)
    _issuer_seal: object = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True, repr=False)
class AuthorizationDecision:
    code: AuthorizationCode
    capability: EditorialAuthorizationCapability | None = field(default=None, repr=False)

    @property
    def allowed(self) -> bool:
        return self.code == AuthorizationCode.ALLOWED and self.capability is not None


class MongoEditorialIAMAuthority:
    """Test-only principal/session/grant authority and transaction guard."""

    def __init__(self, database: Any, *, capability_key: bytes) -> None:
        name = getattr(database, "name", None)
        if not isinstance(name, str) or not _DATABASE.fullmatch(name):
            raise ValueError("C12 authority requires its disposable test database")
        if not isinstance(getattr(database, "client", None), AsyncMongoClient):
            raise TypeError("pass an explicit AsyncMongoClient database")
        if not isinstance(capability_key, bytes) or len(capability_key) < 32:
            raise ValueError("synthetic capability key must contain at least 32 bytes")
        self._database = database
        self._principals = database["c12_iam_principals"]
        self._sessions = database["c12_iam_sessions"]
        self._grants = database["c12_track_grants"]
        self._key = bytes(capability_key)
        self._seal = object()

    async def provision_principal(
        self,
        *,
        actor_id: str,
        role: str,
        permissions: tuple[str, ...] | None = None,
        active: bool = True,
        changed_by: str = "c12_test_admin",
    ) -> None:
        _identifier(actor_id, "actor_id")
        _identifier(changed_by, "changed_by")
        if role not in _ROLES or type(active) is not bool:
            raise ValueError("principal role or active state is invalid")
        granted_permissions = _permissions(permissions if permissions is not None else _ROLE_PERMISSIONS[role])
        await self._principals.insert_one({
            "_id": actor_id,
            "role": role,
            "permissions": list(granted_permissions),
            "active": active,
            "authorization_epoch": 1,
            "use_sequence": 0,
            "changed_by": changed_by,
            "updated_at": _utcnow(),
            "schema_version": 1,
        })

    async def change_principal(
        self,
        *,
        actor_id: str,
        role: str,
        permissions: tuple[str, ...] | None = None,
        active: bool = True,
        changed_by: str,
    ) -> bool:
        _identifier(actor_id, "actor_id")
        _identifier(changed_by, "changed_by")
        if role not in _ROLES or type(active) is not bool:
            raise ValueError("principal role or active state is invalid")
        permission_values = _permissions(permissions if permissions is not None else _ROLE_PERMISSIONS[role])
        result = await self._principals.update_one(
            {"_id": actor_id},
            {"$set": {
                "role": role,
                "permissions": list(permission_values),
                "active": active,
                "changed_by": changed_by,
                "updated_at": _utcnow(),
            }, "$inc": {"authorization_epoch": 1}},
        )
        return result.matched_count == 1

    async def provision_session(
        self,
        *,
        actor_id: str,
        session_id: str,
        expires_at: datetime | None = None,
    ) -> None:
        _identifier(actor_id, "actor_id")
        if not _valid_session_id(session_id):
            raise ValueError("synthetic session identifier has invalid length")
        digest = _session_digest(session_id)
        expiry = expires_at or (_utcnow() + timedelta(hours=1))
        if not isinstance(expiry, datetime) or expiry.tzinfo is None or expiry.utcoffset() != timedelta(0):
            raise ValueError("session expiration must be UTC-aware")
        await self._sessions.insert_one({
            "_id": digest,
            "actor_id": actor_id,
            "active": True,
            "session_epoch": 1,
            "expires_at": expiry,
            "use_sequence": 0,
            "schema_version": 1,
        })

    async def revoke_session(self, *, actor_id: str, session_id: str, changed_by: str) -> bool:
        _identifier(actor_id, "actor_id")
        _identifier(changed_by, "changed_by")
        if not _valid_session_id(session_id):
            return False
        result = await self._sessions.update_one(
            {"_id": _session_digest(session_id), "actor_id": actor_id, "active": True},
            {"$set": {"active": False, "changed_by": changed_by, "updated_at": _utcnow()},
             "$inc": {"session_epoch": 1}},
        )
        return result.matched_count == 1

    async def provision_grant(self, grant: EditorialTrackGrant) -> None:
        if not isinstance(grant, EditorialTrackGrant):
            raise TypeError("grant must be a validated EditorialTrackGrant")
        await self._grants.insert_one(grant.to_document() | {"use_sequence": 0})

    async def revoke_grant(self, *, actor_id: str, track_id: str, revoked_by: str) -> bool:
        _identifier(actor_id, "actor_id")
        _identifier(revoked_by, "revoked_by")
        result = await self._grants.update_one(
            {"_id": _grant_id(actor_id, track_id), "state": GrantState.ACTIVE.value},
            {"$set": {
                "state": GrantState.REVOKED.value,
                "revoked_by": revoked_by,
                "revoked_at": _utcnow(),
            }, "$inc": {"authorization_epoch": 1}},
        )
        return result.matched_count == 1

    async def authorize(
        self,
        *,
        actor_id: str,
        session_id: str,
        resolved_track_id: str,
        operation: str,
        requested_track_id: str | None = None,
    ) -> AuthorizationDecision:
        """Authorize only server-resolved scope; client track mismatch denies."""

        if not all(isinstance(value, str) and _IDENTIFIER.fullmatch(value) for value in
                   (actor_id, resolved_track_id)):
            return AuthorizationDecision(AuthorizationCode.RESOURCE_NOT_FOUND)
        if requested_track_id is not None and requested_track_id != resolved_track_id:
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        if not isinstance(operation, str) or operation not in EDITORIAL_OPERATIONS:
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        if not _valid_session_id(session_id):
            return AuthorizationDecision(AuthorizationCode.SESSION_INVALID)
        try:
            principal = await self._principals.find_one({"_id": actor_id})
            session_digest = _session_digest(session_id)
            session = await self._sessions.find_one({"_id": session_digest, "actor_id": actor_id})
            grant_record = await self._grants.find_one({"_id": _grant_id(actor_id, resolved_track_id)})
            if grant_record is None and principal is not None and principal.get("role") == "admin":
                grant_record = await self._grants.find_one({"_id": _grant_id(actor_id, "*")})
        except Exception:
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if principal is None:
            return AuthorizationDecision(AuthorizationCode.AUTHENTICATION_REQUIRED)
        principal_epoch = principal.get("authorization_epoch")
        if (
            type(principal.get("active")) is not bool
            or principal.get("role") not in _ROLES
            or type(principal_epoch) is not int
            or principal_epoch < 1
        ):
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if not principal["active"]:
            return AuthorizationDecision(AuthorizationCode.AUTHENTICATION_REQUIRED)
        if session is None:
            return AuthorizationDecision(AuthorizationCode.SESSION_INVALID)
        session_epoch = session.get("session_epoch")
        expiry = session.get("expires_at")
        if (
            type(session.get("active")) is not bool
            or type(session_epoch) is not int
            or session_epoch < 1
            or not isinstance(expiry, datetime)
            or expiry.tzinfo is None
        ):
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if not session["active"] or expiry <= _utcnow():
            return AuthorizationDecision(AuthorizationCode.SESSION_INVALID)
        permissions = principal.get("permissions")
        required_permission = _OPERATION_PERMISSION.get(operation)
        if (
            not isinstance(permissions, list)
            or any(not isinstance(item, str) or item not in _KNOWN_PERMISSIONS for item in permissions)
            or required_permission is None
        ):
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if len(permissions) != len(set(permissions)):
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if required_permission not in permissions:
            return AuthorizationDecision(AuthorizationCode.PERMISSION_INSUFFICIENT)
        if grant_record is None:
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        try:
            grant = EditorialTrackGrant.from_document(
                {key: value for key, value in grant_record.items() if key != "use_sequence"}
            )
        except (TypeError, ValueError):
            return AuthorizationDecision(AuthorizationCode.INDETERMINATE)
        if not grant.allows(actor_id, resolved_track_id, operation, role=principal.get("role", "")):
            return AuthorizationDecision(AuthorizationCode.TRACK_SCOPE_DENIED)
        claims = {
            "actor": actor_id,
            "session_digest": session_digest,
            "role": principal["role"],
            "track": resolved_track_id,
            "operation": operation,
            "grant_scope_track": grant.track_id,
            "global_admin_scope": grant.global_admin_scope,
            "principal_epoch": principal_epoch,
            "session_epoch": session_epoch,
            "grant_id": grant.document_id,
            "grant_epoch": grant.authorization_epoch,
        }
        capability = EditorialAuthorizationCapability(
            actor_id=actor_id,
            session_digest=session_digest,
            role=principal["role"],
            track_id=resolved_track_id,
            operation=operation,
            grant_scope_track=grant.track_id,
            global_admin_scope=grant.global_admin_scope,
            principal_epoch=claims["principal_epoch"],
            session_epoch=claims["session_epoch"],
            grant_id=grant.document_id,
            grant_epoch=grant.authorization_epoch,
            _signature=self._sign(claims),
            _issuer_seal=self._seal,
        )
        return AuthorizationDecision(AuthorizationCode.ALLOWED, capability)

    def transaction_participant(
        self,
        capability: EditorialAuthorizationCapability,
        participant: AsyncParticipant,
    ) -> AsyncParticipant:
        """Conditionally touch all auth facts inside the C8 transaction."""

        self._verify_capability(capability)

        async def guarded(session: Any, receipt: RevisionReceipt) -> None:
            now = _utcnow()
            principal = await self._principals.update_one(
                {"_id": capability.actor_id,
                 "role": capability.role,
                 "authorization_epoch": capability.principal_epoch,
                 "active": True,
                 "permissions": _OPERATION_PERMISSION[capability.operation]},
                {"$inc": {"use_sequence": 1}}, session=session,
            )
            auth_session = await self._sessions.update_one(
                {"_id": capability.session_digest,
                 "actor_id": capability.actor_id,
                 "session_epoch": capability.session_epoch,
                 "active": True,
                 "expires_at": {"$gt": now}},
                {"$inc": {"use_sequence": 1}}, session=session,
            )
            grant = await self._grants.update_one(
                {"_id": capability.grant_id,
                 "actor_id": capability.actor_id,
                 "authorization_epoch": capability.grant_epoch,
                 "state": GrantState.ACTIVE.value,
                 "allowed_operations": capability.operation,
                 "track_id": capability.grant_scope_track,
                 "global_admin_scope": capability.global_admin_scope},
                {"$inc": {"use_sequence": 1}}, session=session,
            )
            if principal.matched_count != 1 or auth_session.matched_count != 1 or grant.matched_count != 1:
                raise EditorialAuthorizationError(AuthorizationCode.AUTHORIZATION_REVOKED)
            await participant(session, receipt)

        return guarded

    def _verify_capability(self, capability: object) -> None:
        if not isinstance(capability, EditorialAuthorizationCapability) or capability._issuer_seal is not self._seal:
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)
        expected = self._sign(_capability_claims(capability))
        if not hmac.compare_digest(expected, capability._signature):
            raise EditorialAuthorizationError(AuthorizationCode.CAPABILITY_INVALID)

    def _sign(self, claims: Mapping[str, Any]) -> str:
        payload = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hmac.new(self._key, b"trilhacode:c12:editorial-iam-capability\x00" + payload,
                        hashlib.sha256).hexdigest()


def _capability_claims(capability: EditorialAuthorizationCapability) -> dict[str, Any]:
    return {
        "actor": capability.actor_id,
        "session_digest": capability.session_digest,
        "role": capability.role,
        "track": capability.track_id,
        "operation": capability.operation,
        "grant_scope_track": capability.grant_scope_track,
        "global_admin_scope": capability.global_admin_scope,
        "principal_epoch": capability.principal_epoch,
        "session_epoch": capability.session_epoch,
        "grant_id": capability.grant_id,
        "grant_epoch": capability.grant_epoch,
    }


def _grant_id(actor_id: str, track_id: str) -> str:
    return hashlib.sha256(f"{actor_id}\x00{track_id}".encode("utf-8")).hexdigest()


def _session_digest(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def _valid_session_id(value: object) -> bool:
    return (
        isinstance(value, str)
        and 32 <= len(value) <= 128
        and value.isascii()
        and all(character.isalnum() or character in "-_" for character in value)
    )


def _identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{name} is not a valid synthetic identifier")


def _permissions(values: Any) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list, set, frozenset)):
        raise ValueError("permissions must be a closed collection")
    if any(not isinstance(item, str) or item not in _KNOWN_PERMISSIONS for item in values):
        raise ValueError("permission is outside the reviewed set")
    permissions = tuple(sorted(set(values)))
    return permissions


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
