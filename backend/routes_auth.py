from fastapi import APIRouter, Depends, HTTPException, Request, Response

from permissions import require
from schemas.content import OkOut
from schemas.users import LoginIn, ProfileIn, RegisterIn, RoleIn, UserOut
from security import create_access_token, create_refresh_token, current_user, decode_token
from services.auth import (
    authenticate_user,
    change_user_role,
    get_refresh_user,
    register_user,
    update_user_profile,
)
from services.auth import (
    list_users as list_users_service,
)
from settings import settings

router = APIRouter(prefix="/api")


def _set_cookies(response: Response, user_id: str, email: str):
    options = {"httponly": True, "secure": settings.effective_cookie_secure,
               "samesite": settings.effective_cookie_samesite, "path": "/", "domain": settings.cookie_domain}
    response.set_cookie("access_token", create_access_token(user_id, email), max_age=900, **options)
    response.set_cookie("refresh_token", create_refresh_token(user_id), max_age=604800, **options)


@router.post("/auth/register", response_model=UserOut, response_model_exclude_unset=True)
async def register(body: RegisterIn, response: Response):
    user = await register_user(body.email, body.name, body.password)
    _set_cookies(response, user["id"], user["email"])
    return user


@router.post("/auth/login", response_model=UserOut, response_model_exclude_unset=True)
async def login(body: LoginIn, request: Request, response: Response):
    peer_ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded if settings.trusts_proxy(peer_ip) and forwarded else (peer_ip or "x")
    identifier = f"{client_ip}:{body.email.lower()}"
    user = await authenticate_user(body.email, body.password, identifier)
    _set_cookies(response, user["id"], user["email"])
    return user


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
    user = await get_refresh_user(payload["sub"])
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
    return await update_user_profile(user["id"], data)


@router.get("/users", response_model=list[UserOut], response_model_exclude_unset=True)
async def list_users(limit: int = 1000, skip: int = 0, _: dict = Depends(require("users.manage"))):
    return await list_users_service(limit, skip)


@router.put("/users/{user_id}/role", response_model=UserOut, response_model_exclude_unset=True)
async def set_role(user_id: str, body: RoleIn, actor: dict = Depends(require("users.manage"))):
    return await change_user_role(user_id, body.role, actor)
