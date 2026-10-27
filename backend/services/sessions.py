"""Server-side authentication session lifecycle."""

import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException
from pymongo.errors import PyMongoError

from core_utils import now
from database import db

SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
SESSION_TTL = timedelta(seconds=SESSION_TTL_SECONDS)


def is_valid_session_id(session_id: object) -> bool:
    return (
        isinstance(session_id, str)
        and 32 <= len(session_id) <= 128
        and session_id.isascii()
        and all(character.isalnum() or character in "-_" for character in session_id)
    )


def session_id_digest(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


async def create_session(user_id: str) -> tuple[str, datetime]:
    session_id = secrets.token_urlsafe(32)
    created_at = now()
    expires_at = created_at + SESSION_TTL
    try:
        await db.auth_sessions.insert_one({
            "_id": session_id_digest(session_id),
            "user_id": str(user_id),
            "created_at": created_at,
            "expires_at": expires_at,
            "revoked_at": None,
        })
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível iniciar uma sessão. Tente novamente.",
        ) from None
    return session_id, expires_at


async def require_active_session(session_id: object, user_id: str) -> None:
    if not is_valid_session_id(session_id) or not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida ou revogada")
    try:
        session = await db.auth_sessions.find_one(
            {
                "_id": session_id_digest(session_id),
                "user_id": user_id,
                "expires_at": {"$gt": now()},
                "revoked_at": None,
            },
            {"_id": 1},
        )
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível validar a sessão temporariamente.",
        ) from None
    if session is None:
        raise HTTPException(status_code=401, detail="Sessão inválida ou revogada")


async def revoke_session(session_id: str, user_id: str) -> bool:
    if not is_valid_session_id(session_id) or not user_id:
        return False
    result = await db.auth_sessions.update_one(
        {
            "_id": session_id_digest(session_id),
            "user_id": user_id,
            "revoked_at": None,
        },
        {"$set": {"revoked_at": now()}},
    )
    return result.matched_count > 0
