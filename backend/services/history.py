# ruff: noqa: EXE002
from database import db


async def list_history(track_id: str | None = None, limit: int = 50, skip: int = 0) -> list[dict]:
    query = {"track_id": track_id} if track_id else {}
    page_size = min(max(limit, 1), 200)
    return await db.edit_history.find(query).sort("at", -1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
