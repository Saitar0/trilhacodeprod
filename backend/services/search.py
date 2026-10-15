# ruff: noqa: EXE002
import re

from core import db, is_staff
from integrity import visible_ids


async def search_nodes(
    query_text: str, track_id: str | None, user: dict, limit: int = 40, skip: int = 0,
    tag_id: str | None = None, taxonomy_group: str | None = None, taxonomy_key: str | None = None,
) -> list[dict]:
    """Find matching nodes that the requesting user is allowed to see."""
    rx = {"$regex": re.escape(query_text), "$options": "i"}
    query = {"$or": [{"title": rx}, {"summary": rx}]}
    if track_id:
        query["track_id"] = track_id
    if tag_id:
        query["tag_ids"] = tag_id
    if taxonomy_group and taxonomy_key:
        if taxonomy_group not in {"pedagogical_type", "requirement", "depth"}:
            return []
        query[taxonomy_group] = taxonomy_key
    if not is_staff(user):
        query["status"] = "published"
    page_size = min(max(limit, 1), 200)
    cursor = db.nodes.find(query)
    nodes = []
    if is_staff(user):
        nodes = await cursor.skip(max(skip, 0)).limit(page_size).to_list(page_size)
    else:
        remaining_skip = max(skip, 0)
        while len(nodes) < page_size:
            batch = await cursor.to_list(200)
            if not batch:
                break
            allowed = await visible_ids(user, [node["track_id"] for node in batch])
            visible = [node for node in batch if str(node["_id"]) in allowed]
            if remaining_skip:
                discarded = min(remaining_skip, len(visible))
                visible = visible[discarded:]
                remaining_skip -= discarded
            nodes.extend(visible[:page_size - len(nodes)])
    tracks = {
        str(track["_id"]): track["title"]
        for track in await db.tracks.find({}, {"title": 1}).to_list(500)
    }
    return [{"node": node, "track_title": tracks.get(node["track_id"], "")} for node in nodes]
