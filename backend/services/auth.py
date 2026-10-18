import hashlib
import secrets
from datetime import timedelta

from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from audit import audit
from constants import PERMISSIONS, ROLES
from core_utils import now
from database import db
from security import hash_password, verify_password
from serialization import oid, ser

_DUMMY_PASSWORD_HASH = hash_password("a-fixed-dummy-password-used-for-login-timing")


def _public(user: dict) -> dict:
    out = ser(user)
    out["permissions"] = sorted(PERMISSIONS.get(out["role"], set()))
    return out


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def rate_limit(action: str, key: str, maximum: int, window_seconds: int) -> None:
    """Count fixed-window requests using an atomic, privacy-preserving Mongo key."""
    bucket = int(now().timestamp()) // window_seconds
    raw_key = f"{action}:{key}:{bucket}"
    record_id = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    record = await db.login_attempts.find_one_and_update(
        {"_id": record_id},
        {"$inc": {"count": 1}, "$setOnInsert": {
            # Existing login_attempts.last TTL index performs bounded cleanup.
            "last": now(),
        }},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    if record["count"] > maximum:
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente mais tarde.")


async def register_user(email: str, name: str, password: str) -> tuple[dict | None, str | None]:
    email = email.lower()
    password_hash = hash_password(password)
    if await db.users.find_one({"email": email}):
        return None, None
    token = secrets.token_urlsafe(32)
    doc = {
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "role": "student",
        "profile": {"bio": "", "goals": "", "preferences": {}},
        "created_at": now(),
        "email_verified": False,
        "email_verification_token_hash": _token_hash(token),
        "email_verification_expires_at": now() + timedelta(hours=24),
        "token_version": 0,
    }
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError:
        return None, None
    doc["_id"] = result.inserted_id
    return _public(doc), token


async def authenticate_user(email: str, password: str, identifier: str) -> dict:
    email = email.lower()
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    if attempt and attempt.get("count", 0) >= 5 and attempt["last"] > now() - timedelta(minutes=15):
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente em 15 minutos.")
    user = await db.users.find_one({"email": email})
    password_matches = verify_password(password, user["password_hash"] if user else _DUMMY_PASSWORD_HASH)
    if not user or not password_matches:
        await db.login_attempts.update_one(
            {"identifier": identifier}, {"$inc": {"count": 1}, "$set": {"last": now()}}, upsert=True
        )
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    if user.get("email_verified") is False:
        await db.login_attempts.update_one(
            {"identifier": identifier}, {"$inc": {"count": 1}, "$set": {"last": now()}}, upsert=True
        )
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    await db.login_attempts.delete_many({"identifier": identifier})
    return _public(user)


async def get_refresh_user(user_id: str, token_version: int = 0) -> dict:
    user = await db.users.find_one({"_id": oid(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if user.get("email_verified") is False:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail para acessar a plataforma")
    if token_version != user.get("token_version", 0):
        raise HTTPException(status_code=401, detail="Sessão revogada")
    return user


async def consume_email_verification(token: str) -> bool:
    user = await db.users.find_one_and_update(
        {"email_verification_token_hash": _token_hash(token),
         "email_verification_expires_at": {"$gt": now()}, "email_verified": False},
        {"$set": {"email_verified": True, "email_verified_at": now()},
         "$unset": {"email_verification_token_hash": "", "email_verification_expires_at": ""},
         "$inc": {"token_version": 1}},
        return_document=ReturnDocument.AFTER,
    )
    return user is not None


async def issue_email_verification(email: str) -> tuple[str, str] | None:
    token = secrets.token_urlsafe(32)
    result = await db.users.update_one(
        {"email": email.lower(), "email_verified": False},
        {"$set": {"email_verification_token_hash": _token_hash(token),
                  "email_verification_expires_at": now() + timedelta(hours=24)}},
    )
    if not result.modified_count:
        return None
    user = await db.users.find_one({"email": email.lower()}, {"email": 1})
    return user["email"], token


async def issue_password_reset(email: str) -> tuple[str, str] | None:
    token = secrets.token_urlsafe(32)
    result = await db.users.update_one(
        {"email": email.lower(), "email_verified": {"$ne": False}},
        {"$set": {"password_reset_token_hash": _token_hash(token),
                  "password_reset_expires_at": now() + timedelta(hours=1)}},
    )
    if not result.modified_count:
        return None
    user = await db.users.find_one({"email": email.lower()}, {"email": 1})
    if not user:
        return None
    return user["email"], token


async def consume_password_reset(token: str, password: str) -> bool:
    token_hash = _token_hash(token)
    eligible = await db.users.find_one({
        "password_reset_token_hash": token_hash,
        "password_reset_expires_at": {"$gt": now()},
    }, {"_id": 1})
    if not eligible:
        return False
    result = await db.users.update_one(
        {"_id": eligible["_id"], "password_reset_token_hash": token_hash,
         "password_reset_expires_at": {"$gt": now()}},
        {"$set": {"password_hash": hash_password(password), "password_changed_at": now()},
         "$unset": {"password_reset_token_hash": "", "password_reset_expires_at": ""},
         "$inc": {"token_version": 1}},
    )
    return result.modified_count == 1


async def change_password(user_id: str, current_password: str, password: str) -> None:
    key = {"_id": oid(user_id)}
    user = await db.users.find_one(key)
    if not user or not verify_password(current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Senha atual inválida")
    result = await db.users.update_one(
        {**key, "password_hash": user["password_hash"]},
        {"$set": {"password_hash": hash_password(password), "password_changed_at": now()},
         "$inc": {"token_version": 1}},
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=409, detail="A senha foi alterada em outra solicitação. Entre novamente.")


async def update_user_profile(user_id: str, data: dict) -> dict:
    key = {"_id": oid(user_id)}
    await db.users.update_one(key, {"$set": {**data, "updated_at": now()}})
    return _public(await db.users.find_one(key))


async def list_users(limit: int, skip: int) -> list[dict]:
    page_size = min(max(limit, 1), 1000)
    users = await db.users.find({}).sort("created_at", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    return [ser(user) for user in users]


async def change_user_role(user_id: str, role: str, actor: dict) -> dict:
    if role not in ROLES:
        raise HTTPException(status_code=400, detail="Papel inválido")
    if user_id == actor["id"]:
        raise HTTPException(status_code=400, detail="Você não pode alterar o próprio papel")
    key = {"_id": oid(user_id)}
    await db.users.update_one(key, {"$set": {"role": role}})
    await audit(actor, "user", user_id, "role_changed", summary=role)
    return ser(await db.users.find_one(key))
