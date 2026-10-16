from typing import Optional

from fastapi import APIRouter, Depends

from core import current_user, db, require, ser
from integrity import load_snapshot
from schemas.content import (
    BlockIn,
    BlockOut,
    BlockUpdate,
    HistoryOut,
    NodeDetailOut,
    NodeIn,
    NodeOut,
    NodeUpdate,
    OkOut,
    PublishIn,
    RelationIn,
    RelationOut,
    RelationUpdate,
    ReorderIn,
    SearchResultOut,
    StatsOut,
    TrackIn,
    TrackOut,
    TrackTreeOut,
    TrackUpdate,
    VersionOut,
)
from services.blocks import create_block as create_block_service
from services.blocks import delete_block as delete_block_service
from services.blocks import reorder_blocks as reorder_blocks_service
from services.blocks import update_block as update_block_service
from services.common import get_document as _get
from services.history import list_history
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
from services.search import search_nodes
from services.stats import get_stats
from services.tracks import create_track as create_track_service
from services.tracks import delete_track as delete_track_service
from services.tracks import duplicate_track as duplicate_track_service
from services.tracks import get_track as get_track_service
from services.tracks import list_tracks as list_tracks_service
from services.tracks import publish_track as publish_track_service
from services.tracks import reorder_tracks as reorder_tracks_service
from services.tracks import update_track as update_track_service

router = APIRouter(prefix="/api")


# ---------- Tracks ----------
@router.get("/tracks", response_model=list[TrackOut], response_model_exclude_unset=True)
async def list_tracks(status: Optional[str] = None, q: Optional[str] = None, limit: int = 500, skip: int = 0,
                      user: dict = Depends(current_user)):
    return ser(await list_tracks_service(status, q, user, limit, skip))


@router.post("/tracks", response_model=TrackOut, response_model_exclude_unset=True)
async def create_track(body: TrackIn, user: dict = Depends(require("content.write"))):
    return ser(await create_track_service(body.model_dump(), user))


@router.put("/tracks/reorder", response_model=OkOut)
async def reorder_tracks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_tracks_service(body.ordered_ids)


@router.get("/tracks/{track_id}", response_model=TrackOut, response_model_exclude_unset=True)
async def get_track(track_id: str, user: dict = Depends(current_user)):
    return ser(await get_track_service(track_id, user))


@router.put("/tracks/{track_id}", response_model=TrackOut, response_model_exclude_unset=True)
async def update_track(track_id: str, body: TrackUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_track_service(track_id, body.model_dump(exclude_unset=True), user))


@router.delete("/tracks/{track_id}", response_model=OkOut, response_model_exclude_unset=True)
async def delete_track(track_id: str, user: dict = Depends(require("content.delete"))):
    return await delete_track_service(track_id, user)


@router.post("/tracks/{track_id}/duplicate", response_model=TrackOut, response_model_exclude_unset=True)
async def duplicate_track(track_id: str, user: dict = Depends(require("content.write"))):
    return ser(await duplicate_track_service(track_id, user))


@router.post("/tracks/{track_id}/publish", response_model=TrackOut, response_model_exclude_unset=True)
async def publish_track(track_id: str, body: PublishIn, user: dict = Depends(require("content.publish"))):
    return ser(await publish_track_service(track_id, body.note, body.publish_children, user))


@router.get("/tracks/{track_id}/versions", response_model=list[VersionOut], response_model_exclude_unset=True)
async def list_versions(track_id: str, _: dict = Depends(require("content.read"))):
    versions = await db.track_versions.find({"track_id": track_id, "chunks": {"$exists": True}}, {"snapshot": 0}).sort("created_at", -1).to_list(500)
    return [ser(v) for v in versions]


@router.get("/versions/{version_id}", response_model=VersionOut, response_model_exclude_unset=True)
async def get_version(version_id: str, _: dict = Depends(require("content.read"))):
    v = await _get("track_versions", version_id)
    return ser({**v, "snapshot": await load_snapshot(v)})


@router.get("/tracks/{track_id}/tree", response_model=TrackTreeOut, response_model_exclude_unset=True)
async def track_tree(track_id: str, limit: int = 100000, skip: int = 0, user: dict = Depends(current_user)):
    result = await get_track_tree_service(track_id, user, limit, skip)
    return {**result, "track": ser(result["track"]), "nodes": ser(result["nodes"]),
            "relations": ser(result["relations"])}


# ---------- Nodes ----------
@router.post("/nodes", response_model=NodeOut, response_model_exclude_unset=True)
async def create_node(body: NodeIn, user: dict = Depends(require("content.write"))):
    return ser(await create_node_service(body.model_dump(), user))


@router.post("/nodes/reorder", response_model=OkOut)
async def reorder_nodes(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_nodes_service(body.ordered_ids)


@router.get("/nodes/{node_id}", response_model=NodeDetailOut, response_model_exclude_unset=True)
async def get_node(node_id: str, blocks_limit: int = 1000, blocks_skip: int = 0,
                   user: dict = Depends(current_user)):
    result = await get_node_service(node_id, user, blocks_limit, blocks_skip)
    return {**result, "node": ser(result["node"]), "blocks": ser(result["blocks"]),
            "relations": ser(result["relations"])}


@router.put("/nodes/{node_id}", response_model=NodeOut, response_model_exclude_unset=True)
async def update_node(node_id: str, body: NodeUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_node_service(node_id, body.model_dump(exclude_unset=True), user))


@router.delete("/nodes/{node_id}", response_model=OkOut, response_model_exclude_unset=True)
async def delete_node(node_id: str, user: dict = Depends(require("content.delete"))):
    return await delete_node_service(node_id, user)


@router.post("/nodes/{node_id}/duplicate", response_model=NodeOut, response_model_exclude_unset=True)
async def duplicate_node(node_id: str, user: dict = Depends(require("content.write"))):
    return ser(await duplicate_node_service(node_id, user))


# ---------- Content blocks ----------
@router.post("/blocks", response_model=BlockOut, response_model_exclude_unset=True)
async def create_block(body: BlockIn, user: dict = Depends(require("content.write"))):
    return ser(await create_block_service(body.model_dump(), user))


@router.post("/blocks/reorder", response_model=OkOut)
async def reorder_blocks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    return await reorder_blocks_service(body.ordered_ids)


@router.put("/blocks/{block_id}", response_model=BlockOut, response_model_exclude_unset=True)
async def update_block(block_id: str, body: BlockUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_block_service(block_id, body.model_dump(exclude_unset=True), user))


@router.delete("/blocks/{block_id}", response_model=OkOut)
async def delete_block(block_id: str, user: dict = Depends(require("content.write"))):
    return await delete_block_service(block_id, user)


# ---------- Relations ----------
@router.post("/relations", response_model=RelationOut, response_model_exclude_unset=True)
async def create_relation(body: RelationIn, user: dict = Depends(require("content.write"))):
    return ser(await create_relation_service(body.model_dump(), user))


@router.put("/relations/{rel_id}", response_model=RelationOut, response_model_exclude_unset=True)
async def update_relation(rel_id: str, body: RelationUpdate, user: dict = Depends(require("content.write"))):
    return ser(await update_relation_service(rel_id, body.model_dump(exclude_unset=True), user))


@router.delete("/relations/{rel_id}", response_model=OkOut)
async def delete_relation(rel_id: str, user: dict = Depends(require("content.write"))):
    return await delete_relation_service(rel_id, user)


# ---------- Search, history, stats ----------
@router.get("/search", response_model=list[SearchResultOut], response_model_exclude_unset=True)
async def search(q: str, track_id: Optional[str] = None, limit: int = 40, skip: int = 0,
                 tag_id: str | None = None, taxonomy_group: str | None = None,
                 taxonomy_key: str | None = None, user: dict = Depends(current_user)):
    results = await search_nodes(q, track_id, user, limit, skip, tag_id, taxonomy_group, taxonomy_key)
    return [{**ser(result["node"]), "track_title": result["track_title"]} for result in results]


@router.get("/history", response_model=list[HistoryOut], response_model_exclude_unset=True)
async def history(track_id: Optional[str] = None, limit: int = 50, skip: int = 0,
                  _: dict = Depends(require("content.read"))):
    return ser(await list_history(track_id, limit, skip))


@router.get("/admin/stats", response_model=StatsOut)
async def stats(_: dict = Depends(require("content.read"))):
    return await get_stats()
