import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from integrity import reconcile_orphans, save_version, load_snapshot
from learning import find_cycles
from core import (DEFAULT_HIERARCHY, DEFAULT_LABELS, audit, current_user, db, is_staff, now, oid,
                  require, ser)
from services.history import list_history
from services.search import search_nodes
from services.stats import get_stats
from services.blocks import create_block as create_block_service
from services.blocks import delete_block as delete_block_service
from services.blocks import reorder_blocks as reorder_blocks_service
from services.blocks import update_block as update_block_service
from services.common import check_status as _check_status
from services.common import get_document as _get
from services.common import next_order as _next_order
from services.common import slugify
from services.nodes import clone_nodes as _clone_nodes
from services.nodes import create_node as create_node_service
from services.nodes import delete_node as delete_node_service
from services.nodes import duplicate_node as duplicate_node_service
from services.nodes import get_node as get_node_service
from services.nodes import get_track_tree as get_track_tree_service
from services.nodes import parents_first as _parents_first
from services.nodes import reorder_nodes as reorder_nodes_service
from services.nodes import update_node as update_node_service
from services.relations import create_relation as create_relation_service
from services.relations import delete_relation as delete_relation_service
from services.relations import update_relation as update_relation_service

router = APIRouter(prefix="/api")


# ---------- Models ----------
class TrackIn(BaseModel):
    title: str
    slug: Optional[str] = None
    subtitle: str = ""
    description: str = ""
    cover_url: str = ""
    status: str = "draft"
    visibility: str = "public"
    audience: List[str] = []
    difficulty: str = ""
    tag_ids: List[str] = []
    hierarchy: List[str] = DEFAULT_HIERARCHY
    level_labels: dict = DEFAULT_LABELS
    settings: dict = {}
    meta: dict = {}


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    audience: Optional[List[str]] = None
    difficulty: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    hierarchy: Optional[List[str]] = None
    level_labels: Optional[dict] = None
    settings: Optional[dict] = None
    meta: Optional[dict] = None


NODE_FIELDS = dict(
    summary="", description="", notes="", guidance="", pedagogical_type="", requirement="", depth="",
    status="draft", estimated_minutes=0,
)


class NodeIn(BaseModel):
    track_id: str
    parent_id: Optional[str] = None
    kind: str
    title: str
    summary: str = ""
    description: str = ""
    notes: str = ""
    guidance: str = ""
    pedagogical_type: str = ""
    requirement: str = ""
    depth: str = ""
    status: str = "draft"
    estimated_minutes: int = 0
    tag_ids: List[str] = []
    release: dict = {}
    meta: dict = {}


class NodeUpdate(BaseModel):
    parent_id: Optional[str] = None
    kind: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    guidance: Optional[str] = None
    pedagogical_type: Optional[str] = None
    requirement: Optional[str] = None
    depth: Optional[str] = None
    status: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tag_ids: Optional[List[str]] = None
    release: Optional[dict] = None
    meta: Optional[dict] = None


class BlockIn(BaseModel):
    node_id: str
    type: str
    title: str = ""
    data: dict = {}
    status: str = "published"


class BlockUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[dict] = None
    status: Optional[str] = None


class RelationUpdate(BaseModel):
    enforced: Optional[bool] = None
    note: Optional[str] = None


class RelationIn(BaseModel):
    node_id: str
    target_id: str
    type: str
    enforced: bool = False
    note: str = ""


class ReorderIn(BaseModel):
    ordered_ids: List[str]


class PublishIn(BaseModel):
    note: str = ""
    publish_children: bool = True


# ---------- Tracks ----------
@router.get("/tracks")
async def list_tracks(status: Optional[str] = None, q: Optional[str] = None, user: dict = Depends(current_user)):
    query = {}
    if not is_staff(user):
        query = {"status": "published", "visibility": "public"}
    elif status:
        query["status"] = status
    if q:
        query["title"] = {"$regex": re.escape(q), "$options": "i"}
    tracks = await db.tracks.find(query).sort("order", 1).to_list(500)
    ids = [str(t["_id"]) for t in tracks]
    match = {"track_id": {"$in": ids}}
    if not is_staff(user):
        match["status"] = "published"
    counts = await db.nodes.aggregate([
        {"$match": match}, {"$group": {"_id": {"t": "$track_id", "k": "$kind"}, "n": {"$sum": 1}}}
    ]).to_list(5000)
    by_track = {}
    for c in counts:
        by_track.setdefault(c["_id"]["t"], {})[c["_id"]["k"]] = c["n"]
    out = []
    for t in tracks:
        item = ser(t)
        item["counts"] = by_track.get(item["id"], {})
        out.append(item)
    return out


@router.post("/tracks")
async def create_track(body: TrackIn, user: dict = Depends(require("content.write"))):
    _check_status(body.status)
    doc = body.model_dump()
    doc["slug"] = body.slug or slugify(body.title)
    doc.update(order=await _next_order("tracks", {}), version=0, derived_from=None, created_by=user["id"],
               created_at=now(), updated_at=now(), published_at=None)
    res = await db.tracks.insert_one(doc)
    await audit(user, "track", str(res.inserted_id), "created", str(res.inserted_id), body.title)
    return ser(await db.tracks.find_one({"_id": res.inserted_id}))


@router.put("/tracks/reorder")
async def reorder_tracks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    for i, _id in enumerate(body.ordered_ids):
        await db.tracks.update_one({"_id": oid(_id)}, {"$set": {"order": i}})
    return {"ok": True}


@router.get("/tracks/{track_id}")
async def get_track(track_id: str, user: dict = Depends(current_user)):
    track = await _get("tracks", track_id)
    if not is_staff(user) and track["status"] != "published":
        raise HTTPException(status_code=404, detail="Trilha não encontrada")
    return ser(track)


@router.put("/tracks/{track_id}")
async def update_track(track_id: str, body: TrackUpdate, user: dict = Depends(require("content.write"))):
    await _get("tracks", track_id)
    data = body.model_dump(exclude_unset=True)
    _check_status(data.get("status"))
    if data.get("status") == "published":
        raise HTTPException(status_code=400, detail="Use a ação Publicar para publicar a trilha")
    if (data.get("settings") or {}).get("enforce_prerequisites"):
        if find_cycles(await db.relations.find({"track_id": track_id}).to_list(10000)):
            raise HTTPException(status_code=400, detail="Há ciclos de pré-requisitos. Corrija-os antes de ativar a progressão bloqueante")
    data["updated_at"] = now()
    await db.tracks.update_one({"_id": oid(track_id)}, {"$set": data})
    await audit(user, "track", track_id, "updated", track_id, ", ".join(k for k in data if k != "updated_at"))
    return ser(await db.tracks.find_one({"_id": oid(track_id)}))


@router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, user: dict = Depends(require("content.delete"))):
    track = await _get("tracks", track_id)
    for coll in ["nodes", "content_blocks", "relations", "progress", "learning_events"]:
        await db[coll].delete_many({"track_id": track_id})
    await db.user_track_state.delete_many({"track_id": track_id})
    vids = [str(v["_id"]) for v in await db.track_versions.find({"track_id": track_id}, {"_id": 1}).to_list(10000)]
    await db.version_chunks.delete_many({"version_id": {"$in": vids}})
    await db.track_versions.delete_many({"track_id": track_id})
    await reconcile_orphans(track_id)
    await db.tracks.delete_one({"_id": oid(track_id)})
    await audit(user, "track", track_id, "deleted", track_id, track["title"])
    return {"ok": True}


@router.post("/tracks/{track_id}/duplicate")
async def duplicate_track(track_id: str, user: dict = Depends(require("content.write"))):
    track = await _get("tracks", track_id)
    new = {k: v for k, v in track.items() if k != "_id"}
    new.update(title=f"{track['title']} (cópia)", slug=f"{track['slug']}-copia", status="draft", version=0,
               derived_from=track_id, order=await _next_order("tracks", {}), created_by=user["id"],
               created_at=now(), updated_at=now(), published_at=None)
    res = await db.tracks.insert_one(new)
    new_id = str(res.inserted_id)
    nodes = _parents_first(await db.nodes.find({"track_id": track_id}).to_list(10000))
    id_map = {}
    await _clone_nodes(nodes, new_id, id_map)
    rels = await db.relations.find({"track_id": track_id}).to_list(10000)
    for r in rels:
        if r["node_id"] in id_map and r["target_id"] in id_map:
            nr = {k: v for k, v in r.items() if k != "_id"}
            nr.update(track_id=new_id, node_id=id_map[r["node_id"]], target_id=id_map[r["target_id"]])
            await db.relations.insert_one(nr)
    await audit(user, "track", new_id, "duplicated", new_id, f"derivada de {track['title']}")
    return ser(await db.tracks.find_one({"_id": res.inserted_id}))


async def _snapshot(track_id):
    track = await _get("tracks", track_id)
    nodes = await db.nodes.find({"track_id": track_id}).to_list(10000)
    blocks = await db.content_blocks.find({"track_id": track_id}).to_list(50000)
    rels = await db.relations.find({"track_id": track_id}).to_list(10000)
    return ser({"track": track, "nodes": nodes, "blocks": blocks, "relations": rels})


@router.post("/tracks/{track_id}/publish")
async def publish_track(track_id: str, body: PublishIn, user: dict = Depends(require("content.publish"))):
    track = await _get("tracks", track_id)
    if body.publish_children:
        await db.nodes.update_many({"track_id": track_id, "status": "draft"}, {"$set": {"status": "published"}})
        await db.content_blocks.update_many({"track_id": track_id, "status": "draft"},
                                            {"$set": {"status": "published"}})
    version = track.get("version", 0) + 1
    await db.tracks.update_one({"_id": oid(track_id)}, {"$set": {
        "status": "published", "version": version, "published_at": now(), "updated_at": now()}})
    await save_version(track_id, version, "publish", body.note, user, await _snapshot(track_id))
    await audit(user, "track", track_id, "published", track_id, f"v{version} {body.note}".strip())
    return ser(await db.tracks.find_one({"_id": oid(track_id)}))


@router.get("/tracks/{track_id}/versions")
async def list_versions(track_id: str, _: dict = Depends(require("content.read"))):
    versions = await db.track_versions.find({"track_id": track_id, "chunks": {"$exists": True}}, {"snapshot": 0}).sort("created_at", -1).to_list(500)
    return [ser(v) for v in versions]


@router.get("/versions/{version_id}")
async def get_version(version_id: str, _: dict = Depends(require("content.read"))):
    v = await _get("track_versions", version_id)
    return ser({**v, "snapshot": await load_snapshot(v)})


@router.get("/tracks/{track_id}/tree")
async def track_tree(track_id: str, user: dict = Depends(current_user)):
    result = await get_track_tree_service(track_id, user)
    return {**result, "track": ser(result["track"]), "nodes": ser(result["nodes"]),
            "relations": ser(result["relations"])}


# ---------- Nodes ----------
@router.post("/nodes")
async def create_node(body: NodeIn, user: dict = Depends(require("content.write"))):
    return ser(await create_node_service(body.model_dump(), user))


@router.post("/nodes/reorder")
async def reorder_nodes(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_nodes_service(body.ordered_ids)


@router.get("/nodes/{node_id}")
async def get_node(node_id: str, user: dict = Depends(current_user)):
    result = await get_node_service(node_id, user)
    return {**result, "node": ser(result["node"]), "blocks": ser(result["blocks"]),
            "relations": ser(result["relations"])}


@router.put("/nodes/{node_id}")
async def update_node(node_id: str, body: NodeUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_node_service(node_id, body.model_dump(exclude_unset=True), user))


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, user: dict = Depends(require("content.delete"))):
    return await delete_node_service(node_id, user)


@router.post("/nodes/{node_id}/duplicate")
async def duplicate_node(node_id: str, user: dict = Depends(require("content.write"))):
    return ser(await duplicate_node_service(node_id, user))


# ---------- Content blocks ----------
@router.post("/blocks")
async def create_block(body: BlockIn, user: dict = Depends(require("content.write"))):
    return ser(await create_block_service(body.model_dump(), user))


@router.post("/blocks/reorder")
async def reorder_blocks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_blocks_service(body.ordered_ids)


@router.put("/blocks/{block_id}")
async def update_block(block_id: str, body: BlockUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_block_service(block_id, body.model_dump(exclude_unset=True), user))


@router.delete("/blocks/{block_id}")
async def delete_block(block_id: str, user: dict = Depends(require("content.write"))):
    return await delete_block_service(block_id, user)


# ---------- Relations ----------
@router.post("/relations")
async def create_relation(body: RelationIn, user: dict = Depends(require("content.write"))):
    return ser(await create_relation_service(body.model_dump(), user))


@router.put("/relations/{rel_id}")
async def update_relation(rel_id: str, body: RelationUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_relation_service(rel_id, body.model_dump(exclude_unset=True), user))


@router.delete("/relations/{rel_id}")
async def delete_relation(rel_id: str, user: dict = Depends(require("content.write"))):
    return await delete_relation_service(rel_id, user)


# ---------- Search, history, stats ----------
@router.get("/search")
async def search(q: str, track_id: Optional[str] = None, user: dict = Depends(current_user)):
    results = await search_nodes(q, track_id, user)
    return [{**ser(result["node"]), "track_title": result["track_title"]} for result in results]


@router.get("/history")
async def history(track_id: Optional[str] = None, limit: int = 50, _: dict = Depends(require("content.read"))):
    return ser(await list_history(track_id, limit))


@router.get("/admin/stats")
async def stats(_: dict = Depends(require("content.read"))):
    return await get_stats()
