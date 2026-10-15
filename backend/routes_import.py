from fastapi import APIRouter, Depends

from core import require
from schemas.versions import ImportReportOut
from services.imports import run_import

router = APIRouter(prefix="/api/import")


@router.post("/track", response_model=ImportReportOut, response_model_exclude_unset=True)
async def import_track(payload: dict, dry_run: bool = True, user: dict = Depends(require("content.write"))):
    return await run_import(payload, dry_run, user)
