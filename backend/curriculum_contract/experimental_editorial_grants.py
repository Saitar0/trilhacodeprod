"""Strict synthetic grant documents for C12 experiments only.

These records are not an operational IAM schema and must not be imported by
application routes or services.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class GrantValidationError(ValueError):
    """A grant document is invalid or contains an unreviewed field."""


class GrantState(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


_ATOM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
EDITORIAL_OPERATIONS = frozenset({
    "block.create", "block.update", "content.publish", "content.delete", "node.update",
})
_GRANT_FIELDS = frozenset({
    "_id", "schema_version", "actor_id", "track_id", "scope_kind",
    "global_admin_scope", "allowed_operations", "state", "authorization_epoch",
    "granted_by", "revoked_by", "granted_at", "revoked_at",
})


@dataclass(frozen=True, slots=True)
class EditorialTrackGrant:
    actor_id: str
    track_id: str
    allowed_operations: tuple[str, ...]
    granted_by: str
    granted_at: datetime
    authorization_epoch: int = 1
    state: GrantState = GrantState.ACTIVE
    revoked_by: str | None = None
    revoked_at: datetime | None = None
    global_admin_scope: bool = False

    def __post_init__(self) -> None:
        _atom(self.actor_id, "actor_id")
        _atom(self.granted_by, "granted_by")
        if self.revoked_by is not None:
            _atom(self.revoked_by, "revoked_by")
        if self.track_id == "*":
            if self.global_admin_scope is not True:
                raise GrantValidationError("wildcard scope requires explicit admin scope")
        else:
            _atom(self.track_id, "track_id")
            if self.global_admin_scope:
                raise GrantValidationError("global admin scope must use the explicit wildcard")
        if type(self.global_admin_scope) is not bool:
            raise GrantValidationError("global_admin_scope must be boolean")
        if not isinstance(self.state, GrantState):
            raise GrantValidationError("grant state must be a known enum value")
        if type(self.authorization_epoch) is not int or self.authorization_epoch < 1:
            raise GrantValidationError("authorization_epoch must be a positive integer")
        if not isinstance(self.allowed_operations, tuple) or not self.allowed_operations:
            raise GrantValidationError("allowed_operations must be a non-empty tuple")
        if any(not isinstance(operation, str) for operation in self.allowed_operations):
            raise GrantValidationError("allowed_operations must contain strings")
        if tuple(sorted(set(self.allowed_operations))) != self.allowed_operations:
            raise GrantValidationError("allowed_operations must be unique and sorted")
        if any(operation not in EDITORIAL_OPERATIONS for operation in self.allowed_operations):
            raise GrantValidationError("operation is outside the reviewed set")
        _aware(self.granted_at, "granted_at")
        if self.state is GrantState.ACTIVE:
            if self.revoked_by is not None or self.revoked_at is not None:
                raise GrantValidationError("active grants cannot contain revocation fields")
        else:
            if self.revoked_by is None or self.revoked_at is None:
                raise GrantValidationError("revoked grants require revoker and timestamp")
            _aware(self.revoked_at, "revoked_at")

    @property
    def scope_kind(self) -> str:
        return "global_admin" if self.track_id == "*" else "track"

    @property
    def document_id(self) -> str:
        return hashlib.sha256(f"{self.actor_id}\x00{self.track_id}".encode()).hexdigest()

    def to_document(self) -> dict[str, Any]:
        return {
            "_id": self.document_id,
            "schema_version": 1,
            "actor_id": self.actor_id,
            "track_id": self.track_id,
            "scope_kind": self.scope_kind,
            "global_admin_scope": self.global_admin_scope,
            "allowed_operations": list(self.allowed_operations),
            "state": self.state.value,
            "authorization_epoch": self.authorization_epoch,
            "granted_by": self.granted_by,
            "revoked_by": self.revoked_by,
            "granted_at": self.granted_at,
            "revoked_at": self.revoked_at,
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> EditorialTrackGrant:
        if not isinstance(document, Mapping) or set(document) != _GRANT_FIELDS:
            raise GrantValidationError("grant document fields do not match the closed schema")
        if type(document["schema_version"]) is not int or document["schema_version"] != 1:
            raise GrantValidationError("unsupported grant schema version")
        try:
            grant = cls(
                actor_id=document["actor_id"],
                track_id=document["track_id"],
                allowed_operations=tuple(document["allowed_operations"]),
                state=GrantState(document["state"]),
                authorization_epoch=document["authorization_epoch"],
                granted_by=document["granted_by"],
                revoked_by=document["revoked_by"],
                granted_at=document["granted_at"],
                revoked_at=document["revoked_at"],
                global_admin_scope=document["global_admin_scope"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GrantValidationError("grant document is invalid") from exc
        if document["_id"] != grant.document_id or document["scope_kind"] != grant.scope_kind:
            raise GrantValidationError("grant identity does not match its scope")
        return grant

    def allows(self, actor_id: str, track_id: str, operation: str, *, role: str) -> bool:
        scope_matches = self.track_id == track_id or (
            self.track_id == "*" and self.global_admin_scope is True and role == "admin"
        )
        return (
            self.state is GrantState.ACTIVE
            and self.actor_id == actor_id
            and scope_matches
            and operation in self.allowed_operations
        )


def _atom(value: object, name: str) -> None:
    if not isinstance(value, str) or not _ATOM.fullmatch(value):
        raise GrantValidationError(f"{name} must use a reviewed identifier format")


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise GrantValidationError(f"{name} must be timezone-aware")
    if value.utcoffset() != timezone.utc.utcoffset(value):
        raise GrantValidationError(f"{name} must be normalized to UTC")
