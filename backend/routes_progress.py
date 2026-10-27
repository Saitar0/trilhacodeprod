from typing import Optional

from fastapi import APIRouter, Depends

from permissions import require
from schemas.content import HistoryOut, OkOut
from schemas.progress import (
    ProgressIn,
    ProgressOut,
    ProgressOverviewOut,
    TrackProgressOut,
    VisitIn,
)
from security import current_user
from services.progress import (
    get_progress_overview,
    get_track_progress,
    list_progress_history,
    visit_node,
)
from services.progress import (
    set_progress as set_progress_service,
)

router = APIRouter(prefix="/api/progress")


@router.post("", response_model=ProgressOut, response_model_exclude_unset=True)
async def set_progress(body: ProgressIn, user: dict = Depends(require("progress.write"))):
    return await set_progress_service(body.model_dump(), user)


@router.post("/visit", response_model=OkOut)
async def visit(body: VisitIn, user: dict = Depends(current_user)):
    await visit_node(body.node_id, user, body.operation_id)
    return {"ok": True}


@router.get("/tracks/{track_id}", response_model=TrackProgressOut, response_model_exclude_unset=True)
async def track_progress(track_id: str, limit: int = 20000, skip: int = 0, user: dict = Depends(current_user)):
    return await get_track_progress(track_id, user, limit, skip)


@router.get("/overview", response_model=ProgressOverviewOut, response_model_exclude_unset=True)
async def overview(user: dict = Depends(current_user)):
    return await get_progress_overview(user)


@router.get("/history", response_model=list[HistoryOut], response_model_exclude_unset=True)
async def progress_history(track_id: Optional[str] = None, limit: int = 20, skip: int = 0,
                           user: dict = Depends(current_user)):
    return await list_progress_history(track_id, limit, skip, user)
