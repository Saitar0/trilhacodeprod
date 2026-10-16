from datetime import timedelta

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from audit import audit
from constants import PERMISSIONS, ROLES
from core_utils import now
from database import db
from security import hash_password, verify_password
from serialization import oid, ser


def _public(user: dict) -> dict:
    out = ser(user)
    out["permissions"] = sorted(PERMISSIONS.get(out["role"], set()))
    return out


async def register_user(email: str, name: str, password: str) -> dict:
    email = email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Este email já está cadastrado")
    doc = {
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
        "role": "student",
        "profile": {"bio": "", "goals": "", "preferences": {}},
        "created_at": now(),
    }
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Este email já está cadastrado") from exc
    doc["_id"] = result.inserted_id
    return _public(doc)


async def authenticate_user(email: str, password: str, identifier: str) -> dict:
    email = email.lower()
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    if attempt and attempt.get("count", 0) >= 5 and attempt["last"] > now() - timedelta(minutes=15):
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente em 15 minutos.")
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": identifier}, {"$inc": {"count": 1}, "$set": {"last": now()}}, upsert=True
        )
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    await db.login_attempts.delete_many({"identifier": identifier})
    return _public(user)


async def get_refresh_user(user_id: str) -> dict:
    user = await db.users.find_one({"_id": oid(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


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
