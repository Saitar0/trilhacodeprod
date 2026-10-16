from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from core import (
    PERMISSIONS,
    ROLES,
    audit,
    create_access_token,
    create_refresh_token,
    current_user,
    db,
    decode_token,
    hash_password,
    now,
    oid,
    require,
    ser,
    verify_password,
)
from schemas.content import OkOut
from schemas.users import LoginIn, ProfileIn, RegisterIn, RoleIn, UserOut
from settings import settings

router = APIRouter(prefix="/api")


def _set_cookies(response: Response, user_id: str, email: str):
    options = {"httponly": True, "secure": settings.effective_cookie_secure,
               "samesite": settings.effective_cookie_samesite, "path": "/", "domain": settings.cookie_domain}
    response.set_cookie("access_token", create_access_token(user_id, email), max_age=900, **options)
    response.set_cookie("refresh_token", create_refresh_token(user_id), max_age=604800, **options)


def _public(user: dict) -> dict:
    out = ser(user)
    out["permissions"] = sorted(PERMISSIONS.get(out["role"], set()))
    return out


@router.post("/auth/register", response_model=UserOut, response_model_exclude_unset=True)
async def register(body: RegisterIn, response: Response):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Este email já está cadastrado")
    doc = {"email": email, "name": body.name, "password_hash": hash_password(body.password), "role": "student",
           "profile": {"bio": "", "goals": "", "preferences": {}}, "created_at": now()}
    res = await db.users.insert_one(doc)
    doc["_id"] = res.inserted_id
    _set_cookies(response, str(res.inserted_id), email)
    return _public(doc)


@router.post("/auth/login", response_model=UserOut, response_model_exclude_unset=True)
async def login(body: LoginIn, request: Request, response: Response):
    email = body.email.lower()
    peer_ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded if settings.trusts_proxy(peer_ip) and forwarded else (peer_ip or "x")
    identifier = f"{client_ip}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    if attempt and attempt.get("count", 0) >= 5 and attempt["last"] > now() - timedelta(minutes=15):
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente em 15 minutos.")
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        await db.login_attempts.update_one({"identifier": identifier},
                                           {"$inc": {"count": 1}, "$set": {"last": now()}}, upsert=True)
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    await db.login_attempts.delete_many({"identifier": identifier})
    _set_cookies(response, str(user["_id"]), email)
    return _public(user)


@router.post("/auth/logout", response_model=OkOut)
async def logout(response: Response):
    options = {"path": "/", "secure": settings.effective_cookie_secure,
               "samesite": settings.effective_cookie_samesite, "domain": settings.cookie_domain}
    response.delete_cookie("access_token", **options)
    response.delete_cookie("refresh_token", **options)
    return {"ok": True}


@router.get("/auth/me", response_model=UserOut, response_model_exclude_unset=True)
async def me(user: dict = Depends(current_user)):
    return user


@router.post("/auth/refresh", response_model=OkOut)
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Sem sessão")
    payload = decode_token(token, "refresh")
    user = await db.users.find_one({"_id": oid(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    response.set_cookie("access_token", create_access_token(str(user["_id"]), user["email"]), httponly=True,
                        secure=settings.effective_cookie_secure, samesite=settings.effective_cookie_samesite,
                        max_age=900, path="/", domain=settings.cookie_domain)
    return {"ok": True}


@router.get("/profile", response_model=UserOut, response_model_exclude_unset=True)
async def get_profile(user: dict = Depends(current_user)):
    return user


@router.put("/profile", response_model=UserOut, response_model_exclude_unset=True)
async def update_profile(body: ProfileIn, user: dict = Depends(current_user)):
    data = body.model_dump(exclude_unset=True)
    await db.users.update_one({"_id": oid(user["id"])}, {"$set": {**data, "updated_at": now()}})
    return _public(await db.users.find_one({"_id": oid(user["id"])}))


@router.get("/users", response_model=list[UserOut], response_model_exclude_unset=True)
async def list_users(limit: int = 1000, skip: int = 0, _: dict = Depends(require("users.manage"))):
    page_size = min(max(limit, 1), 1000)
    users = await db.users.find({}).sort("created_at", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    return [ser(u) for u in users]


@router.put("/users/{user_id}/role", response_model=UserOut, response_model_exclude_unset=True)
async def set_role(user_id: str, body: RoleIn, actor: dict = Depends(require("users.manage"))):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail="Papel inválido")
    if user_id == actor["id"]:
        raise HTTPException(status_code=400, detail="Você não pode alterar o próprio papel")
    await db.users.update_one({"_id": oid(user_id)}, {"$set": {"role": body.role}})
    await audit(actor, "user", user_id, "role_changed", summary=body.role)
    return ser(await db.users.find_one({"_id": oid(user_id)}))
