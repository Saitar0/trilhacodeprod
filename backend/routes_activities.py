from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from permissions import require
from schemas.activities import (
    AttemptCreateIn,
    AttemptListOut,
    AttemptOut,
    AttemptSubmitIn,
    DraftUpdateIn,
)
from security import current_user
from services.activities import (
    create_attempt,
    get_attempt,
    get_attempts,
    save_draft,
    submit_attempt,
)
from settings import settings

router = APIRouter(prefix="/api/activities")


def _origin(value: str | None) -> str | None:
    if not value or value == "null":
        return None
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path not in {"", "/"}:
        return None
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".lower()


async def activity_writer(request: Request, user: dict = Depends(require("progress.write"))) -> dict:
    """Protect cookie-authenticated mutations with an exact configured origin check.

    Bearer clients are not ambient-cookie clients and may omit Origin. Browser
    clients using the access cookie must supply an allowed Origin or Referer.
    """
    if request.cookies.get("access_token"):
        source = request.headers.get("origin")
        if not source:
            source = _origin(request.headers.get("referer"))
        supplied = _origin(source)
        allowed = {origin.rstrip("/").lower() for origin in settings.effective_cors_origins}
        if not supplied or supplied not in allowed:
            raise HTTPException(status_code=403, detail="Origem da requisição não autorizada")
    return user


@router.post("/{activity_id}/attempts", response_model=AttemptOut, status_code=status.HTTP_201_CREATED)
async def start_attempt(
    activity_id: str,
    body: AttemptCreateIn,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
    user: dict = Depends(activity_writer),
):
    return await create_attempt(activity_id, body.published_version_id, idempotency_key, user)


@router.get("/{activity_id}/attempts", response_model=AttemptListOut)
async def list_attempts(
    activity_id: str,
    limit: int = Query(default=20, ge=1, le=50),
    skip: int = Query(default=0, ge=0, le=10_000),
    user: dict = Depends(current_user),
):
    return await get_attempts(activity_id, user, limit, skip)


@router.get("/{activity_id}/attempts/{attempt_id}", response_model=AttemptOut)
async def attempt_detail(activity_id: str, attempt_id: str, user: dict = Depends(current_user)):
    return await get_attempt(activity_id, attempt_id, user)


@router.put("/{activity_id}/attempts/{attempt_id}/draft", response_model=AttemptOut)
async def update_draft(
    activity_id: str,
    attempt_id: str,
    body: DraftUpdateIn,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
    user: dict = Depends(activity_writer),
):
    return await save_draft(
        activity_id, attempt_id, body.selected_option_id, body.expected_revision, idempotency_key, user,
    )


@router.post("/{activity_id}/attempts/{attempt_id}/submit", response_model=AttemptOut)
async def submit(
    activity_id: str,
    attempt_id: str,
    body: AttemptSubmitIn,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=128),
    user: dict = Depends(activity_writer),
):
    return await submit_attempt(
        activity_id, attempt_id, body.selected_option_id, body.expected_revision, idempotency_key, user,
    )
