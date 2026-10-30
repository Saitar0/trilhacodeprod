"""Explicit test-composition bridge from active FastAPI identity to C12 grants.

This module is not imported by application startup. The active user/session
remain authoritative; C12 records are a grant projection that must match them.
The runtime session and user are conditionally touched in the same transaction
as the editorial CAS, so revocation/update races conflict at commit.
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, Request

from constants import PERMISSIONS
from curriculum_contract.experimental_editorial_iam_authority import (
    AuthorizationCode,
    EditorialAuthorizationError,
)

_ACTOR_ID = re.compile(r"^[0-9a-fA-F]{24}$")


@dataclass(frozen=True, slots=True, repr=False)
class AuthenticatedEditorialIdentity:
    actor_id: str
    role: str
    token_version: int
    session_id: str = field(repr=False)


RuntimeTransactionGuard = Callable[[Any, Any], Awaitable[None]]


def identity_from_authenticated_request(request: Request, user: dict) -> AuthenticatedEditorialIdentity:
    """Extract the already-authenticated access session without trusting body fields."""

    # Lazy imports keep this experimental bridge inert until explicitly used by
    # the isolated composition. Both active modules construct a shared DB client.
    from security import decode_token
    from services.sessions import is_valid_session_id

    token = request.cookies.get("access_token")
    if not token:
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    claims = decode_token(token, "access")
    actor_id = user.get("id")
    token_version = user.get("token_version", 0)
    session_id = claims.get("sid")
    if (
        not isinstance(actor_id, str)
        or claims.get("sub") != actor_id
        or claims.get("ver", 0) != token_version
        or not isinstance(user.get("role"), str)
        or type(token_version) is not int
        or not is_valid_session_id(session_id)
    ):
        raise HTTPException(status_code=401, detail="Sessão inválida")
    return AuthenticatedEditorialIdentity(actor_id, user["role"], token_version, session_id)


class Beta8_1RuntimeIAMBridge:
    """Bind current_user output to the isolated C12 grant projection."""

    def __init__(self, database: Any) -> None:
        self._database = database

    async def require_matching_projection(
        self,
        identity: AuthenticatedEditorialIdentity,
        user: dict,
        *,
        required_permission: str,
    ) -> None:
        from services.sessions import session_id_digest

        if required_permission not in PERMISSIONS.get(user.get("role"), set()):
            raise HTTPException(status_code=403, detail="Permissão insuficiente")
        if not _ACTOR_ID.fullmatch(identity.actor_id):
            raise HTTPException(status_code=403, detail="Ação editorial negada")

        expected_permissions = sorted(user.get("permissions", []))
        principal = await self._database["c12_iam_principals"].find_one(
            {"_id": identity.actor_id},
            {"role": 1, "permissions": 1, "active": 1},
        )
        session_digest = session_id_digest(identity.session_id)
        active_session = await self._database.auth_sessions.find_one({
            "_id": session_digest,
            "user_id": identity.actor_id,
            "revoked_at": None,
            "expires_at": {"$gt": datetime.now(UTC)},
        })
        grant_session = await self._database["c12_iam_sessions"].find_one({
            "_id": session_digest,
            "actor_id": identity.actor_id,
            "active": True,
            "expires_at": {"$gt": datetime.now(UTC)},
        })
        if (
            principal is None
            or principal.get("active") is not True
            or principal.get("role") != identity.role
            or principal.get("permissions") != expected_permissions
            or active_session is None
            or grant_session is None
            or grant_session.get("expires_at") != active_session.get("expires_at")
        ):
            raise HTTPException(status_code=403, detail="Ação editorial negada")

    def transaction_guard(self, identity: AuthenticatedEditorialIdentity) -> RuntimeTransactionGuard:
        """Order active IAM/session validity against the editorial commit."""

        from services.sessions import session_id_digest

        if not _ACTOR_ID.fullmatch(identity.actor_id):
            raise HTTPException(status_code=403, detail="Ação editorial negada")
        object_id = ObjectId(identity.actor_id)
        digest = session_id_digest(identity.session_id)

        async def guard(session: Any, _receipt: Any) -> None:
            now = datetime.now(UTC)
            user_result = await self._database.users.update_one(
                {
                    "_id": object_id,
                    "role": identity.role,
                    "token_version": identity.token_version,
                    "is_active": {"$ne": False},
                    "disabled": {"$ne": True},
                    "email_verified": {"$ne": False},
                },
                {"$inc": {"beta8_1_editorial_use_sequence": 1}},
                session=session,
            )
            session_result = await self._database.auth_sessions.update_one(
                {
                    "_id": digest,
                    "user_id": identity.actor_id,
                    "revoked_at": None,
                    "expires_at": {"$gt": now},
                },
                {"$inc": {"beta8_1_editorial_use_sequence": 1}},
                session=session,
            )
            if user_result.matched_count != 1 or session_result.matched_count != 1:
                raise EditorialAuthorizationError(AuthorizationCode.AUTHORIZATION_REVOKED)

        return guard


@dataclass(frozen=True, slots=True)
class Beta8_1EditorialRuntime:
    """Capabilities explicitly injected by the isolated FastAPI test composition."""

    boundary: Any
    iam_bridge: Beta8_1RuntimeIAMBridge
    operation_hmac_key: bytes = field(repr=False)
    content_hmac_key: bytes = field(repr=False)
    before_commit: Callable[[], Awaitable[None]] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if len(self.operation_hmac_key) < 32 or len(self.content_hmac_key) < 32:
            raise ValueError("Chaves experimentais devem ter ao menos 32 bytes")
