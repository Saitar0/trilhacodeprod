from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core import require, ser
from services.versions import compare_versions, restore_version

router = APIRouter(prefix="/api")


class RestoreIn(BaseModel):
    confirm: str
    note: str = ""


@router.get("/tracks/{track_id}/compare")
async def compare(track_id: str, base: str, target: str, _: dict = Depends(require("content.read"))):
    return await compare_versions(track_id, base, target)


@router.post("/tracks/{track_id}/versions/{version_id}/restore")
async def restore(track_id: str, version_id: str, body: RestoreIn, user: dict = Depends(require("content.publish"))):
    return ser(await restore_version(track_id, version_id, body.confirm, body.note, user))
