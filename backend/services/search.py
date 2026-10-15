# ruff: noqa: EXE002
import re

from core import db, is_staff
from integrity import visible_ids


async def search_nodes(query_text: str, track_id: str | None, user: dict) -> list[dict]:
    """Find matching nodes that the requesting user is allowed to see."""
    rx = {"$regex": re.escape(query_text), "$options": "i"}
    query = {"$or": [{"title": rx}, {"summary": rx}]}
    if track_id:
        query["track_id"] = track_id
    if not is_staff(user):
        query["status"] = "published"
    nodes = await db.nodes.find(query).limit(200).to_list(200)
    if not is_staff(user):
        allowed = await visible_ids(user, [node["track_id"] for node in nodes])
        nodes = [node for node in nodes if str(node["_id"]) in allowed]
    nodes = nodes[:40]
    tracks = {
        str(track["_id"]): track["title"]
        for track in await db.tracks.find({}, {"title": 1}).to_list(500)
    }
    return [{"node": node, "track_title": tracks.get(node["track_id"], "")} for node in nodes]
