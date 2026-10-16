from fastapi import APIRouter, Depends

from core import require, ser
from schemas.content import TrackOut
from schemas.versions import RestoreIn, VersionCompareOut
from services.versions import compare_versions, restore_version

router = APIRouter(prefix="/api")


@router.get("/tracks/{track_id}/compare", response_model=VersionCompareOut, response_model_exclude_unset=True)
async def compare(track_id: str, base: str, target: str, _: dict = Depends(require("content.read"))):
    return await compare_versions(track_id, base, target)


@router.post("/tracks/{track_id}/versions/{version_id}/restore", response_model=TrackOut, response_model_exclude_unset=True)
async def restore(track_id: str, version_id: str, body: RestoreIn, user: dict = Depends(require("content.publish"))):
    return ser(await restore_version(track_id, version_id, body.confirm, body.note, user))
