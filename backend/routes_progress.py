from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from core import PROGRESS_STATUSES, current_user, db, now, oid, require, ser
from learning import assert_unlocked, assert_visible, track_locks
from schemas.content import HistoryOut, OkOut
from schemas.progress import ProgressIn, ProgressOut, ProgressOverviewOut, TrackProgressOut, VisitIn

router = APIRouter(prefix="/api/progress")


async def _node(node_id):
    found = await db.nodes.find_one({"_id": oid(node_id)})
    if found is None:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    return dict(found)


async def _event(user_id, node, kind, block_id=None, data=None):
    await db.learning_events.insert_one({
        "user_id": user_id, "track_id": node["track_id"], "node_id": str(node["_id"]), "block_id": block_id,
        "type": kind, "data": data or {}, "at": now()})


@router.post("", response_model=ProgressOut, response_model_exclude_unset=True)
async def set_progress(body: ProgressIn, user: dict = Depends(require("progress.write"))):
    if body.status not in PROGRESS_STATUSES:
        raise HTTPException(status_code=400, detail="Status de progresso inválido")
    node = await _node(body.node_id)
    await assert_unlocked(node, user)
    key = {"user_id": user["id"], "node_id": body.node_id, "block_id": body.block_id}
    existing = await db.progress.find_one(key)
    update = {"status": body.status, "track_id": node["track_id"], "scope": "block" if body.block_id else "node",
              "data": body.data, "updated_at": now()}
    if body.status != "not_started" and not (existing and existing.get("started_at")):
        update["started_at"] = now()
    update["completed_at"] = now() if body.status == "completed" else None
    if body.status == "not_started":
        update["started_at"] = None
    await db.progress.update_one(key, {"$set": update, "$inc": {"attempts": 1 if body.status == "completed" else 0}},
                                 upsert=True)
    await _event(user["id"], node, f"status:{body.status}", body.block_id, body.data)
    await db.user_track_state.update_one(
        {"user_id": user["id"], "track_id": node["track_id"]},
        {"$set": {"last_node_id": body.node_id, "last_at": now()}}, upsert=True)
    return ser(await db.progress.find_one(key))


@router.post("/visit", response_model=OkOut)
async def visit(body: VisitIn, user: dict = Depends(current_user)):
    node = await _node(body.node_id)
    await assert_unlocked(node, user)
    await db.user_track_state.update_one(
        {"user_id": user["id"], "track_id": node["track_id"]},
        {"$set": {"last_node_id": body.node_id, "last_node_title": node["title"], "last_at": now()},
         "$setOnInsert": {"started_at": now()}}, upsert=True)
    key = {"user_id": user["id"], "node_id": body.node_id, "block_id": None}
    if not await db.progress.find_one(key):
        await db.progress.insert_one({**key, "status": "in_progress", "track_id": node["track_id"], "scope": "node",
                                      "started_at": now(), "completed_at": None, "updated_at": now(), "attempts": 0})
    await _event(user["id"], node, "view")
    return {"ok": True}


@router.get("/tracks/{track_id}", response_model=TrackProgressOut, response_model_exclude_unset=True)
async def track_progress(track_id: str, limit: int = 20000, skip: int = 0, user: dict = Depends(current_user)):
    page_size = min(max(limit, 1), 20000)
    records = await db.progress.find({"user_id": user["id"], "track_id": track_id}).sort("_id", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    state = await db.user_track_state.find_one({"user_id": user["id"], "track_id": track_id})
    nodes, blocks = {}, {}
    for r in records:
        item = ser(r)
        if r.get("block_id"):
            blocks[r["block_id"]] = item
        else:
            nodes[r["node_id"]] = item
    return {"nodes": nodes, "blocks": blocks, "state": ser(state) if state else None,
            "locks": await track_locks(track_id, user)}


@router.get("/overview", response_model=ProgressOverviewOut, response_model_exclude_unset=True)
async def overview(user: dict = Depends(current_user)):
    states = await db.user_track_state.find({"user_id": user["id"]}).sort("last_at", -1).to_list(200)
    rows = await db.progress.aggregate([
        {"$match": {"user_id": user["id"], "block_id": None, "status": "completed"}},
        {"$group": {"_id": "$track_id", "completed": {"$sum": 1}}}]).to_list(500)
    completed = {r["_id"]: r["completed"] for r in rows}
    return {"states": ser(states), "completed": completed}


@router.get("/history", response_model=list[HistoryOut], response_model_exclude_unset=True)
async def progress_history(track_id: Optional[str] = None, limit: int = 20, skip: int = 0,
                           user: dict = Depends(current_user)):
    query = {"user_id": user["id"]}
    if track_id:
        query["track_id"] = track_id
    page_size = min(max(limit, 1), 100)
    events = await db.learning_events.find(query).sort("at", -1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    ids = list({e["node_id"] for e in events})
    titles = {str(n["_id"]): n["title"] for n in await db.nodes.find(
        {"_id": {"$in": [oid(i) for i in ids]}}, {"title": 1}).to_list(200)}
    return [{**ser(e), "node_title": titles.get(e["node_id"], "")} for e in events]
