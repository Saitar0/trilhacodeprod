import os
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.environ["MONGO_URL"], tz_aware=True)
db = client[os.environ["DB_NAME"]]

JWT_ALGORITHM = "HS256"
STATUSES = ["draft", "published", "archived"]
PROGRESS_STATUSES = ["not_started", "in_progress", "completed"]
ROLES = ["admin", "editor", "student"]
DEFAULT_HIERARCHY = ["phase", "module", "submodule", "topic"]
DEFAULT_LABELS = {"phase": "Fase", "module": "Módulo", "submodule": "Submódulo", "topic": "Tópico"}

PERMISSIONS = {
    "admin": {"content.read", "content.write", "content.publish", "content.delete",
              "taxonomy.manage", "users.manage", "progress.write", "submissions.grade"},
    "editor": {"content.read", "content.write", "content.publish", "content.delete", "progress.write",
               "submissions.grade"},
    "student": {"progress.write"},
}


def now():
    return datetime.now(timezone.utc)


def oid(value):
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")


def ser(value):
    if isinstance(value, list):
        return [ser(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k == "_id":
                out["id"] = str(v)
            elif k == "password_hash":
                continue
            else:
                out[k] = ser(v)
        return out
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _secret():
    return os.environ["JWT_SECRET"]


def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "type": "access", "exp": now() + timedelta(minutes=15)}
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "type": "refresh", "exp": now() + timedelta(days=7)}
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str, expected: str) -> dict:
    try:
        payload = jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("type") != expected:
        raise HTTPException(status_code=401, detail="Tipo de token inválido")
    return payload


async def current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = decode_token(token, "access")
    user = await db.users.find_one({"_id": oid(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    user = ser(user)
    user["permissions"] = sorted(PERMISSIONS.get(user["role"], set()))
    return user


def require(perm: str):
    async def dep(user: dict = Depends(current_user)):
        if perm not in PERMISSIONS.get(user["role"], set()):
            raise HTTPException(status_code=403, detail="Permissão insuficiente")
        return user
    return dep


def is_staff(user: dict) -> bool:
    return "content.read" in PERMISSIONS.get(user["role"], set())


async def audit(user: dict, entity: str, entity_id: str, action: str, track_id: str = None, summary: str = ""):
    await db.edit_history.insert_one({
        "entity": entity, "entity_id": entity_id, "action": action, "track_id": track_id,
        "summary": summary, "user_id": user["id"], "user_name": user.get("name", ""), "at": now(),
    })
