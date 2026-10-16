from fastapi import HTTPException

from constants import PROGRESS_STATUSES
from core_utils import now
from database import db
from learning import assert_unlocked, track_locks
from serialization import oid, ser


async def _node(node_id: str) -> dict:
    found = await db.nodes.find_one({"_id": oid(node_id)})
    if found is None:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    return dict(found)


async def _event(user_id: str, node: dict, kind: str, block_id: str | None = None, data: dict | None = None) -> None:
    await db.learning_events.insert_one({
        "user_id": user_id,
        "track_id": node["track_id"],
        "node_id": str(node["_id"]),
        "block_id": block_id,
        "type": kind,
        "data": data or {},
        "at": now(),
    })


async def set_progress(body: dict, user: dict) -> dict:
    if body["status"] not in PROGRESS_STATUSES:
        raise HTTPException(status_code=400, detail="Status de progresso inválido")
    node = await _node(body["node_id"])
    await assert_unlocked(node, user)
    key = {"user_id": user["id"], "node_id": body["node_id"], "block_id": body.get("block_id")}
    update = {
        "status": body["status"],
        "track_id": node["track_id"],
        "scope": "block" if body.get("block_id") else "node",
        "data": body.get("data", {}),
        "updated_at": now(),
    }
    update["completed_at"] = now() if body["status"] == "completed" else None
    if body["status"] == "not_started":
        update["started_at"] = None
        insert_defaults = {}
    else:
        insert_defaults = {"started_at": now()}
    await db.progress.update_one(
        key, {"$set": update, "$setOnInsert": insert_defaults,
              "$inc": {"attempts": 1 if body["status"] == "completed" else 0}}, upsert=True
    )
    await _event(user["id"], node, f"status:{body['status']}", body.get("block_id"), body.get("data"))
    await db.user_track_state.update_one(
        {"user_id": user["id"], "track_id": node["track_id"]},
        {"$set": {"last_node_id": body["node_id"], "last_at": now()}},
        upsert=True,
    )
    return ser(await db.progress.find_one(key))


async def visit_node(node_id: str, user: dict) -> None:
    node = await _node(node_id)
    await assert_unlocked(node, user)
    await db.user_track_state.update_one(
        {"user_id": user["id"], "track_id": node["track_id"]},
        {
            "$set": {"last_node_id": node_id, "last_node_title": node["title"], "last_at": now()},
            "$setOnInsert": {"started_at": now()},
        },
        upsert=True,
    )
    key = {"user_id": user["id"], "node_id": node_id, "block_id": None}
    timestamp = now()
    await db.progress.update_one(key, {
        "$setOnInsert": {
            "status": "in_progress", "track_id": node["track_id"], "scope": "node",
            "started_at": timestamp, "completed_at": None, "updated_at": timestamp, "attempts": 0,
        }
    }, upsert=True)
    await _event(user["id"], node, "view")


async def get_track_progress(track_id: str, user: dict, limit: int, skip: int) -> dict:
    page_size = min(max(limit, 1), 20000)
    records = await db.progress.find({"user_id": user["id"], "track_id": track_id}).sort("_id", 1).skip(
        max(skip, 0)
    ).limit(page_size).to_list(page_size)
    state = await db.user_track_state.find_one({"user_id": user["id"], "track_id": track_id})
    nodes, blocks = {}, {}
    for record in records:
        item = ser(record)
        if record.get("block_id"):
            blocks[record["block_id"]] = item
        else:
            nodes[record["node_id"]] = item
    return {
        "nodes": nodes,
        "blocks": blocks,
        "state": ser(state) if state else None,
        "locks": await track_locks(track_id, user),
    }


async def get_progress_overview(user: dict) -> dict:
    states = await db.user_track_state.find({"user_id": user["id"]}).sort("last_at", -1).to_list(200)
    cursor = await db.progress.aggregate([
        {"$match": {"user_id": user["id"], "block_id": None, "status": "completed"}},
        {"$group": {"_id": "$track_id", "completed": {"$sum": 1}}},
    ])
    rows = await cursor.to_list(500)
    return {"states": ser(states), "completed": {row["_id"]: row["completed"] for row in rows}}


async def list_progress_history(track_id: str | None, limit: int, skip: int, user: dict) -> list[dict]:
    query = {"user_id": user["id"]}
    if track_id:
        query["track_id"] = track_id
    page_size = min(max(limit, 1), 100)
    events = await db.learning_events.find(query).sort("at", -1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    ids = list({event["node_id"] for event in events})
    titles = {
        str(node["_id"]): node["title"]
        for node in await db.nodes.find({"_id": {"$in": [oid(item_id) for item_id in ids]}}, {"title": 1}).to_list(200)
    }
    return [{**ser(event), "node_title": titles.get(event["node_id"], "")} for event in events]
