# ruff: noqa: EXE002
from core import db


async def list_history(track_id: str | None = None, limit: int = 50) -> list[dict]:
    query = {"track_id": track_id} if track_id else {}
    return await db.edit_history.find(query).sort("at", -1).limit(min(limit, 200)).to_list(200)
