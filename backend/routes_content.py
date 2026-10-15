from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from integrity import load_snapshot
from core import DEFAULT_HIERARCHY, DEFAULT_LABELS, current_user, db, require, ser
from services.history import list_history
from services.search import search_nodes
from services.stats import get_stats
from services.blocks import create_block as create_block_service
from services.blocks import delete_block as delete_block_service
from services.blocks import reorder_blocks as reorder_blocks_service
from services.blocks import update_block as update_block_service
from services.common import get_document as _get
from services.nodes import create_node as create_node_service
from services.nodes import delete_node as delete_node_service
from services.nodes import duplicate_node as duplicate_node_service
from services.nodes import get_node as get_node_service
from services.nodes import get_track_tree as get_track_tree_service
from services.nodes import reorder_nodes as reorder_nodes_service
from services.nodes import update_node as update_node_service
from services.relations import create_relation as create_relation_service
from services.relations import delete_relation as delete_relation_service
from services.relations import update_relation as update_relation_service
from services.tracks import create_track as create_track_service
from services.tracks import delete_track as delete_track_service
from services.tracks import duplicate_track as duplicate_track_service
from services.tracks import get_track as get_track_service
from services.tracks import list_tracks as list_tracks_service
from services.tracks import publish_track as publish_track_service
from services.tracks import reorder_tracks as reorder_tracks_service
from services.tracks import update_track as update_track_service

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
    return ser(await list_tracks_service(status, q, user))


@router.post("/tracks")
async def create_track(body: TrackIn, user: dict = Depends(require("content.write"))):
    return ser(await create_track_service(body.model_dump(), user))


@router.put("/tracks/reorder")
async def reorder_tracks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_tracks_service(body.ordered_ids)


@router.get("/tracks/{track_id}")
async def get_track(track_id: str, user: dict = Depends(current_user)):
    return ser(await get_track_service(track_id, user))


@router.put("/tracks/{track_id}")
async def update_track(track_id: str, body: TrackUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_track_service(track_id, body.model_dump(exclude_unset=True), user))


@router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, user: dict = Depends(require("content.delete"))):
    return await delete_track_service(track_id, user)


@router.post("/tracks/{track_id}/duplicate")
async def duplicate_track(track_id: str, user: dict = Depends(require("content.write"))):
    return ser(await duplicate_track_service(track_id, user))


@router.post("/tracks/{track_id}/publish")
async def publish_track(track_id: str, body: PublishIn, user: dict = Depends(require("content.publish"))):
    return ser(await publish_track_service(track_id, body.note, body.publish_children, user))


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
