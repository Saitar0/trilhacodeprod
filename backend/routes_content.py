import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from integrity import can_view_node, reconcile_orphans, save_version, visible_ids, load_snapshot
from learning import find_cycles, prerequisite_cycle, track_locks, visible_nodes
from core import (DEFAULT_HIERARCHY, DEFAULT_LABELS, STATUSES, audit, current_user, db, is_staff, now, oid,
                  require, ser)

router = APIRouter(prefix="/api")


def slugify(text: str) -> str:
    text = text.lower().strip()
    for a, b in [("áàãâä", "a"), ("éèêë", "e"), ("íìîï", "i"), ("óòõôö", "o"), ("úùûü", "u"), ("ç", "c")]:
        text = re.sub(f"[{a}]", b, text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "item"


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


def _check_status(status):
    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=400, detail="Status inválido")


async def _get(coll, _id):
    found = await db[coll].find_one({"_id": oid(_id)})
    if found is None:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
    return dict(found)


async def _next_order(coll, query):
    last = await db[coll].find(query).sort("order", -1).limit(1).to_list(1)
    return (last[0]["order"] + 1) if last else 0


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


async def _clone_nodes(nodes, track_id, id_map, parent_override=None, root_ids=None):
    """Clone nodes (sorted parents-first) and their blocks, filling id_map old->new."""
    for n in nodes:
        old = str(n["_id"])
        new = {k: v for k, v in n.items() if k != "_id"}
        new["track_id"] = track_id
        if root_ids is not None and old in root_ids:
            new["parent_id"] = parent_override
        else:
            new["parent_id"] = id_map.get(n.get("parent_id"), n.get("parent_id"))
        new["created_at"] = new["updated_at"] = now()
        res = await db.nodes.insert_one(new)
        id_map[old] = str(res.inserted_id)
        blocks = await db.content_blocks.find({"node_id": old}).to_list(1000)
        for b in blocks:
            nb = {k: v for k, v in b.items() if k != "_id"}
            nb.update(node_id=id_map[old], track_id=track_id, created_at=now(), updated_at=now())
            await db.content_blocks.insert_one(nb)


def _parents_first(nodes):
    by_id = {str(n["_id"]): n for n in nodes}
    depth = {}

    def d(n):
        k = str(n["_id"])
        if k not in depth:
            p = by_id.get(n.get("parent_id"))
            depth[k] = 0 if not p else d(p) + 1
        return depth[k]
    return sorted(nodes, key=lambda n: (d(n), n.get("order", 0)))


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


_visible_nodes = visible_nodes


@router.get("/tracks/{track_id}/tree")
async def track_tree(track_id: str, user: dict = Depends(current_user)):
    track = await _get("tracks", track_id)
    staff = is_staff(user)
    if not staff and (track["status"] != "published" or track.get("visibility") == "private"):
        raise HTTPException(status_code=404, detail="Trilha não encontrada")
    nodes = await db.nodes.find({"track_id": track_id}).sort("order", 1).to_list(100000)
    if not staff:
        nodes = _visible_nodes(nodes)
    ids = {str(n["_id"]) for n in nodes}
    rels = [r for r in await db.relations.find({"track_id": track_id}).to_list(10000)
            if r["node_id"] in ids and r["target_id"] in ids]
    bmatch = {"track_id": track_id} if staff else {"track_id": track_id, "status": "published"}
    bcounts = await db.content_blocks.aggregate([
        {"$match": bmatch}, {"$group": {"_id": "$node_id", "n": {"$sum": 1}}}]).to_list(10000)
    return {"track": ser(track), "nodes": ser(nodes), "relations": ser(rels),
            "block_counts": {c["_id"]: c["n"] for c in bcounts}}


# ---------- Nodes ----------
async def _validate_parent(track, kind, parent_id, node_id=None):
    hierarchy = track.get("hierarchy") or DEFAULT_HIERARCHY
    if kind not in hierarchy:
        raise HTTPException(status_code=400, detail="Tipo de nó não pertence à hierarquia da trilha")
    if not parent_id:
        return
    parent = await _get("nodes", parent_id)
    if parent["track_id"] != str(track["_id"]):
        raise HTTPException(status_code=400, detail="Pai pertence a outra trilha")
    if hierarchy.index(kind) <= hierarchy.index(parent["kind"]):
        raise HTTPException(status_code=400, detail="Nível do nó deve ser mais profundo que o do pai")
    cur = parent
    while node_id and cur:
        if str(cur["_id"]) == node_id:
            raise HTTPException(status_code=400, detail="Não é possível mover um nó para dentro de si mesmo")
        cur = await db.nodes.find_one({"_id": oid(cur["parent_id"])}) if cur.get("parent_id") else None


@router.post("/nodes")
async def create_node(body: NodeIn, user: dict = Depends(require("content.write"))):
    _check_status(body.status)
    track = await _get("tracks", body.track_id)
    await _validate_parent(track, body.kind, body.parent_id)
    doc = body.model_dump()
    doc.update(slug=slugify(body.title), order=await _next_order("nodes", {"track_id": body.track_id,
                                                                           "parent_id": body.parent_id}),
               created_by=user["id"], created_at=now(), updated_at=now())
    res = await db.nodes.insert_one(doc)
    await audit(user, "node", str(res.inserted_id), "created", body.track_id, body.title)
    return ser(await db.nodes.find_one({"_id": res.inserted_id}))


@router.post("/nodes/reorder")
async def reorder_nodes(body: ReorderIn, _: dict = Depends(require("content.write"))):
    for i, _id in enumerate(body.ordered_ids):
        await db.nodes.update_one({"_id": oid(_id)}, {"$set": {"order": i}})
    return {"ok": True}


async def _ancestors(node):
    chain = []
    cur = node
    while cur.get("parent_id"):
        cur = await db.nodes.find_one({"_id": oid(cur["parent_id"])})
        if not cur:
            break
        chain.insert(0, {"id": str(cur["_id"]), "title": cur["title"], "kind": cur["kind"]})
    return chain


@router.get("/nodes/{node_id}")
async def get_node(node_id: str, user: dict = Depends(current_user)):
    node = await _get("nodes", node_id)
    staff = is_staff(user)
    if not staff and not await can_view_node(node, user):
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    bq = {"node_id": node_id} if staff else {"node_id": node_id, "status": "published"}
    lock = (await track_locks(node["track_id"], user)).get(node_id)
    blocks = [] if lock and not staff else await db.content_blocks.find(bq).sort("order", 1).to_list(1000)
    rels = await db.relations.find({"$or": [{"node_id": node_id}, {"target_id": node_id}]}).to_list(1000)
    other_ids = {r["target_id"] if r["node_id"] == node_id else r["node_id"] for r in rels}
    others = {str(n["_id"]): n for n in await db.nodes.find({"_id": {"$in": [oid(i) for i in other_ids]}}).to_list(1000)}
    out_rels = []
    for r in rels:
        outgoing = r["node_id"] == node_id
        other = others.get(r["target_id"] if outgoing else r["node_id"])
        if not other or (not staff and other["status"] != "published"):
            continue
        item = ser(r)
        item.update(direction="outgoing" if outgoing else "incoming",
                    other={"id": str(other["_id"]), "title": other["title"], "kind": other["kind"]})
        out_rels.append(item)
    if lock and not staff:
        node = {**node, "description": "", "guidance": ""}
    if not staff:
        node = {k: v for k, v in node.items() if k != "notes"}
    return {"node": ser(node), "blocks": ser(blocks), "relations": out_rels, "ancestors": await _ancestors(node),
            "lock": lock}


@router.put("/nodes/{node_id}")
async def update_node(node_id: str, body: NodeUpdate, user: dict = Depends(require("content.write"))):
    node = await _get("nodes", node_id)
    data = body.model_dump(exclude_unset=True)
    _check_status(data.get("status"))
    if "parent_id" in data or "kind" in data:
        track = await _get("tracks", node["track_id"])
        new_parent = data.get("parent_id", node.get("parent_id")) or None
        await _validate_parent(track, data.get("kind", node["kind"]), new_parent, node_id)
        if "parent_id" in data and new_parent != node.get("parent_id"):
            data["parent_id"] = new_parent
            data["order"] = await _next_order("nodes", {"track_id": node["track_id"], "parent_id": new_parent})
    if "title" in data:
        data["slug"] = slugify(data["title"])
    data["updated_at"] = now()
    await db.nodes.update_one({"_id": oid(node_id)}, {"$set": data})
    await audit(user, "node", node_id, "updated", node["track_id"],
                f"{node['title']}: " + ", ".join(k for k in data if k not in ("updated_at", "slug", "order")))
    return ser(await db.nodes.find_one({"_id": oid(node_id)}))


async def _descendants(track_id, node_id):
    nodes = await db.nodes.find({"track_id": track_id}, {"parent_id": 1}).to_list(10000)
    children = {}
    for n in nodes:
        children.setdefault(n.get("parent_id"), []).append(str(n["_id"]))
    out, stack = [], [node_id]
    while stack:
        cur = stack.pop()
        out.append(cur)
        stack.extend(children.get(cur, []))
    return out


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, user: dict = Depends(require("content.delete"))):
    node = await _get("nodes", node_id)
    ids = await _descendants(node["track_id"], node_id)
    await db.nodes.delete_many({"_id": {"$in": [oid(i) for i in ids]}})
    await db.content_blocks.delete_many({"node_id": {"$in": ids}})
    await db.relations.delete_many({"$or": [{"node_id": {"$in": ids}}, {"target_id": {"$in": ids}}]})
    await db.progress.delete_many({"node_id": {"$in": ids}})
    await reconcile_orphans(node["track_id"])
    await audit(user, "node", node_id, "deleted", node["track_id"], f"{node['title']} (+{len(ids) - 1} filhos)")
    return {"ok": True, "deleted": len(ids)}


@router.post("/nodes/{node_id}/duplicate")
async def duplicate_node(node_id: str, user: dict = Depends(require("content.write"))):
    node = await _get("nodes", node_id)
    ids = set(await _descendants(node["track_id"], node_id))
    subtree = _parents_first(await db.nodes.find({"_id": {"$in": [oid(i) for i in ids]}}).to_list(10000))
    id_map = {}
    await _clone_nodes(subtree, node["track_id"], id_map, parent_override=node.get("parent_id"), root_ids={node_id})
    new_id = id_map[node_id]
    siblings = await db.nodes.find({"track_id": node["track_id"], "parent_id": node.get("parent_id")}).sort(
        "order", 1).to_list(10000)
    ordered = [str(s["_id"]) for s in siblings if str(s["_id"]) != new_id]
    ordered.insert(ordered.index(node_id) + 1, new_id)
    for i, _id in enumerate(ordered):
        await db.nodes.update_one({"_id": oid(_id)}, {"$set": {"order": i}})
    await db.nodes.update_one({"_id": oid(new_id)}, {"$set": {"title": f"{node['title']} (cópia)", "status": "draft"}})
    await audit(user, "node", new_id, "duplicated", node["track_id"], node["title"])
    return ser(await db.nodes.find_one({"_id": oid(new_id)}))


# ---------- Content blocks ----------
@router.post("/blocks")
async def create_block(body: BlockIn, user: dict = Depends(require("content.write"))):
    _check_status(body.status)
    node = await _get("nodes", body.node_id)
    if not await db.block_types.find_one({"key": body.type}):
        raise HTTPException(status_code=400, detail="Tipo de bloco desconhecido")
    doc = body.model_dump()
    doc.update(track_id=node["track_id"], order=await _next_order("content_blocks", {"node_id": body.node_id}),
               schema_version=1, created_by=user["id"], created_at=now(), updated_at=now())
    res = await db.content_blocks.insert_one(doc)
    await audit(user, "block", str(res.inserted_id), "created", node["track_id"], f"{body.type} em {node['title']}")
    return ser(await db.content_blocks.find_one({"_id": res.inserted_id}))


@router.post("/blocks/reorder")
async def reorder_blocks(body: ReorderIn, _: dict = Depends(require("content.write"))):
    for i, _id in enumerate(body.ordered_ids):
        await db.content_blocks.update_one({"_id": oid(_id)}, {"$set": {"order": i}})
    return {"ok": True}


@router.put("/blocks/{block_id}")
async def update_block(block_id: str, body: BlockUpdate, user: dict = Depends(require("content.write"))):
    block = await _get("content_blocks", block_id)
    data = body.model_dump(exclude_unset=True)
    _check_status(data.get("status"))
    data["updated_at"] = now()
    await db.content_blocks.update_one({"_id": oid(block_id)}, {"$set": data})
    await audit(user, "block", block_id, "updated", block["track_id"], block["type"])
    return ser(await db.content_blocks.find_one({"_id": oid(block_id)}))


@router.delete("/blocks/{block_id}")
async def delete_block(block_id: str, user: dict = Depends(require("content.write"))):
    block = await _get("content_blocks", block_id)
    await db.content_blocks.delete_one({"_id": oid(block_id)})
    await reconcile_orphans(block["track_id"])
    await audit(user, "block", block_id, "deleted", block["track_id"], block["type"])
    return {"ok": True}


# ---------- Relations ----------
@router.post("/relations")
async def create_relation(body: RelationIn, user: dict = Depends(require("content.write"))):
    if body.node_id == body.target_id:
        raise HTTPException(status_code=400, detail="Um nó não pode se relacionar consigo mesmo")
    src = await _get("nodes", body.node_id)
    tgt = await _get("nodes", body.target_id)
    if src["track_id"] != tgt["track_id"]:
        raise HTTPException(status_code=400, detail="Relações devem ser dentro da mesma trilha")
    if await db.relations.find_one({"node_id": body.node_id, "target_id": body.target_id, "type": body.type}):
        raise HTTPException(status_code=400, detail="Relação já existe")
    if body.type == "prerequisite":
        lineage = set(await _descendants(src["track_id"], body.node_id)) | {a["id"] for a in await _ancestors(src)}
        if body.target_id in lineage:
            raise HTTPException(status_code=400, detail="Um item não pode ter como pré-requisito seu próprio pai ou filho")
        rels = await db.relations.find({"track_id": src["track_id"]}).to_list(10000)
        if prerequisite_cycle(rels, body.node_id, body.target_id):
            raise HTTPException(status_code=400, detail="Esta relação criaria um ciclo de pré-requisitos")
    doc = {**body.model_dump(), "track_id": src["track_id"], "created_at": now()}
    res = await db.relations.insert_one(doc)
    await audit(user, "relation", str(res.inserted_id), "created", src["track_id"],
                f"{src['title']} → {body.type} → {tgt['title']}")
    return ser(await db.relations.find_one({"_id": res.inserted_id}))


@router.put("/relations/{rel_id}")
async def update_relation(rel_id: str, body: RelationUpdate, user: dict = Depends(require("content.write"))):
    rel = await _get("relations", rel_id)
    await db.relations.update_one({"_id": oid(rel_id)}, {"$set": body.model_dump(exclude_unset=True)})
    await audit(user, "relation", rel_id, "updated", rel["track_id"], rel["type"])
    return ser(await db.relations.find_one({"_id": oid(rel_id)}))


@router.delete("/relations/{rel_id}")
async def delete_relation(rel_id: str, user: dict = Depends(require("content.write"))):
    rel = await _get("relations", rel_id)
    await db.relations.delete_one({"_id": oid(rel_id)})
    await audit(user, "relation", rel_id, "deleted", rel["track_id"], rel["type"])
    return {"ok": True}


# ---------- Search, history, stats ----------
@router.get("/search")
async def search(q: str, track_id: Optional[str] = None, user: dict = Depends(current_user)):
    rx = {"$regex": re.escape(q), "$options": "i"}
    query = {"$or": [{"title": rx}, {"summary": rx}]}
    if track_id:
        query["track_id"] = track_id
    if not is_staff(user):
        query["status"] = "published"
    nodes = await db.nodes.find(query).limit(200).to_list(200)
    if not is_staff(user):
        allowed = await visible_ids(user, [n["track_id"] for n in nodes])
        nodes = [n for n in nodes if str(n["_id"]) in allowed]
    nodes = nodes[:40]
    tracks = {str(t["_id"]): t["title"] for t in await db.tracks.find({}, {"title": 1}).to_list(500)}
    return [{**ser(n), "track_title": tracks.get(n["track_id"], "")} for n in nodes]


@router.get("/history")
async def history(track_id: Optional[str] = None, limit: int = 50, _: dict = Depends(require("content.read"))):
    query = {"track_id": track_id} if track_id else {}
    items = await db.edit_history.find(query).sort("at", -1).limit(min(limit, 200)).to_list(200)
    return ser(items)


@router.get("/admin/stats")
async def stats(_: dict = Depends(require("content.read"))):
    async def group(coll, field):
        rows = await db[coll].aggregate([{"$group": {"_id": f"${field}", "n": {"$sum": 1}}}]).to_list(100)
        return {r["_id"]: r["n"] for r in rows}
    return {
        "tracks": await group("tracks", "status"),
        "nodes": await group("nodes", "kind"),
        "node_status": await group("nodes", "status"),
        "blocks": await group("content_blocks", "type"),
        "users": await group("users", "role"),
        "relations": await db.relations.count_documents({}),
        "versions": await db.track_versions.count_documents({}),
    }
