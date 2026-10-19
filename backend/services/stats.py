# ruff: noqa: EXE002
from database import db


async def _group(coll: str, field: str) -> dict:
    cursor = await db[coll].aggregate([{"$group": {"_id": f"${field}", "n": {"$sum": 1}}}])
    rows = await cursor.to_list(100)
    return {row["_id"]: row["n"] for row in rows}


async def get_stats() -> dict:
    return {
        "tracks": await _group("tracks", "status"),
        "nodes": await _group("nodes", "kind"),
        "node_status": await _group("nodes", "status"),
        "blocks": await _group("content_blocks", "type"),
        "users": await _group("users", "role"),
        "relations": await db.relations.count_documents({}),
        "versions": await db.track_versions.count_documents({}),
    }
