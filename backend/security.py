"""Password hashing, JWT handling, and authenticated-user resolution."""

from datetime import timedelta

import bcrypt
import jwt
from fastapi import HTTPException, Request

from constants import JWT_ALGORITHM, PERMISSIONS
from core_utils import now
from database import db
from serialization import oid, ser
from settings import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _secret():
    return settings.jwt_secret


def create_access_token(user_id: str, email: str, token_version: int = 0) -> str:
    payload = {"sub": user_id, "email": email, "ver": token_version,
               "type": "access", "exp": now() + timedelta(minutes=15)}
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str, token_version: int = 0) -> str:
    payload = {"sub": user_id, "ver": token_version,
               "type": "refresh", "exp": now() + timedelta(days=7)}
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
    if payload.get("ver", 0) != user.get("token_version", 0):
        raise HTTPException(status_code=401, detail="Sessão revogada")
    if user.get("email_verified") is False:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail para acessar a plataforma")
    user = ser(user)
    request.state.user_id = user["id"]
    user["permissions"] = sorted(PERMISSIONS.get(user["role"], set()))
    return user
