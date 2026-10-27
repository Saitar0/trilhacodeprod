import hmac
import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from email_delivery import send_email
from permissions import require
from schemas.content import OkOut
from schemas.users import (
    EmailIn,
    LoginIn,
    PasswordChangeIn,
    PasswordResetIn,
    ProfileIn,
    RegisterIn,
    RoleIn,
    TokenIn,
    UserOut,
)
from security import (
    create_access_token,
    create_refresh_token,
    current_user,
    decode_token,
    require_active_session,
)
from services.auth import (
    authenticate_user,
    change_password,
    change_user_role,
    consume_email_verification,
    consume_password_reset,
    get_refresh_user,
    issue_email_verification,
    issue_password_reset,
    rate_limit,
    register_user,
    update_user_profile,
)
from services.auth import (
    list_users as list_users_service,
)
from services.sessions import (
    SESSION_TTL_SECONDS,
    create_session,
    is_valid_session_id,
    revoke_session,
)
from settings import settings

router = APIRouter(prefix="/api")
log = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded if settings.trusts_proxy(peer_ip) and forwarded else (peer_ip or "unknown")


def _rate_key(value: str) -> str:
    return hmac.digest(settings.jwt_secret.encode("utf-8"), value.strip().lower().encode("utf-8"), "sha256").hex()


async def _deliver_account_email(kind: str, recipient: str, token: str) -> None:
    path = "auth/confirm-email" if kind == "Confirme seu e-mail" else "auth/reset-password"
    link = f"{settings.frontend_url.rstrip('/')}/{path}?token={token}"
    try:
        await send_email(kind, recipient,
                         f"Acesse o link abaixo para continuar. Ele expira e só pode ser usado uma vez.\n\n{link}\n")
    except Exception:
        # Never write a token, recipient, provider credentials, or full message to logs.
        log.warning("Account email delivery failed (%s)", kind)


def _cookie_options() -> dict:
    return {
        "httponly": True,
        "secure": settings.effective_cookie_secure,
        "samesite": settings.effective_cookie_samesite,
        "path": "/",
        "domain": settings.cookie_domain,
    }


def _clear_auth_cookies(response: Response) -> None:
    options = {key: value for key, value in _cookie_options().items() if key != "httponly"}
    response.delete_cookie("access_token", **options)
    response.delete_cookie("refresh_token", **options)


def _set_cookies(
    response: Response,
    user_id: str,
    email: str,
    token_version: int,
    session_id: str,
    refresh_expires_at: datetime,
) -> None:
    options = _cookie_options()
    response.set_cookie(
        "access_token",
        create_access_token(user_id, email, token_version, session_id=session_id),
        max_age=900,
        **options,
    )
    response.set_cookie(
        "refresh_token",
        create_refresh_token(
            user_id,
            token_version,
            session_id=session_id,
            expires_at=refresh_expires_at,
        ),
        max_age=SESSION_TTL_SECONDS,
        **options,
    )


def _session_claim(token: str | None, expected_type: str) -> tuple[str, str] | None:
    if not token:
        return None
    try:
        payload = decode_token(token, expected_type)
    except HTTPException:
        return None
    session_id = payload.get("sid")
    user_id = payload.get("sub")
    if not is_valid_session_id(session_id) or not isinstance(user_id, str) or not user_id:
        return None
    return session_id, user_id


@router.post("/auth/register", status_code=202)
async def register(body: RegisterIn, request: Request, background_tasks: BackgroundTasks):
    ip_key = _rate_key(_client_ip(request))
    email_key = _rate_key(body.email)
    await rate_limit("register-ip", ip_key, 20, 3600)
    await rate_limit("register-email", email_key, 3, 3600)
    user, token = await register_user(body.email, body.name, body.password)
    if user and token:
        background_tasks.add_task(_deliver_account_email, "Confirme seu e-mail", user["email"], token)
    return {"message": "Se o cadastro puder ser concluído, enviaremos instruções para o endereço informado."}


@router.post("/auth/verify-email")
async def verify_email(body: TokenIn, request: Request):
    await rate_limit("verify-email-ip", _rate_key(_client_ip(request)), 60, 60)
    if not await consume_email_verification(body.token):
        raise HTTPException(status_code=400, detail="Link inválido ou expirado")
    return {"ok": True, "message": "E-mail confirmado. Você já pode entrar."}


@router.post("/auth/resend-verification", status_code=202)
async def resend_verification(body: EmailIn, request: Request, background_tasks: BackgroundTasks):
    ip_key = _rate_key(_client_ip(request))
    email_key = _rate_key(body.email)
    await rate_limit("resend-verification-ip", ip_key, 10, 3600)
    await rate_limit("resend-verification-email", email_key, 3, 3600)
    issued = await issue_email_verification(body.email)
    if issued:
        background_tasks.add_task(_deliver_account_email, "Confirme seu e-mail", *issued)
    return {"message": "Se houver uma conta pendente para esse endereço, enviaremos um novo link."}


@router.post("/auth/password-reset-request", status_code=202)
async def request_password_reset(body: EmailIn, request: Request, background_tasks: BackgroundTasks):
    ip_key = _rate_key(_client_ip(request))
    email_key = _rate_key(body.email)
    await rate_limit("password-reset-ip", ip_key, 10, 3600)
    await rate_limit("password-reset-email", email_key, 3, 3600)
    issued = await issue_password_reset(body.email)
    if issued:
        background_tasks.add_task(_deliver_account_email, "Redefina sua senha", *issued)
    return {"message": "Se houver uma conta confirmada para esse endereço, enviaremos instruções."}


@router.post("/auth/password-reset")
async def reset_password(body: PasswordResetIn, request: Request):
    await rate_limit("password-reset-consume-ip", _rate_key(_client_ip(request)), 60, 60)
    if not await consume_password_reset(body.token, body.password):
        raise HTTPException(status_code=400, detail="Link inválido ou expirado")
    return {"ok": True, "message": "Senha alterada. Entre novamente."}


@router.post("/auth/password")
async def update_password(body: PasswordChangeIn, request: Request, user: dict = Depends(current_user)):
    await rate_limit("password-change-ip", _rate_key(_client_ip(request)), 30, 3600)
    await change_password(user["id"], body.current_password, body.password)
    return {"ok": True, "message": "Senha alterada. Entre novamente."}


@router.post("/auth/login", response_model=UserOut, response_model_exclude_unset=True)
async def login(body: LoginIn, request: Request, response: Response):
    client_ip = _client_ip(request)
    await rate_limit("login-ip", _rate_key(client_ip), 120, 60)
    identifier = _rate_key(f"{client_ip}:{body.email}")
    user = await authenticate_user(body.email, body.password, identifier)
    session_id, refresh_expires_at = await create_session(user["id"])
    _set_cookies(
        response,
        user["id"],
        user["email"],
        user.get("token_version", 0),
        session_id,
        refresh_expires_at,
    )
    return user


@router.post("/auth/logout", response_model=OkOut)
async def logout(request: Request, response: Response):
    _clear_auth_cookies(response)
    session = _session_claim(request.cookies.get("refresh_token"), "refresh")
    if session is None:
        session = _session_claim(request.cookies.get("access_token"), "access")
    if session is not None:
        try:
            await revoke_session(*session)
        except PyMongoError:
            failure = JSONResponse(
                status_code=503,
                content={"detail": "Não foi possível confirmar o encerramento da sessão."},
            )
            _clear_auth_cookies(failure)
            return failure
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
    session_id = payload.get("sid")
    await require_active_session(session_id, payload.get("sub"))
    user = await get_refresh_user(payload["sub"], payload.get("ver", 0))
    response.set_cookie(
        "access_token",
        create_access_token(
            str(user["_id"]),
            user["email"],
            user.get("token_version", 0),
            session_id=session_id,
        ),
        httponly=True,
        secure=settings.effective_cookie_secure,
        samesite=settings.effective_cookie_samesite,
        max_age=900,
        path="/",
        domain=settings.cookie_domain,
    )
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
