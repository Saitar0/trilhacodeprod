# ruff: noqa: EXE002
from fastapi import HTTPException

from core import DEFAULT_HIERARCHY, audit, db, is_staff, now, oid
from integrity import can_view_node, reconcile_orphans
from learning import track_locks, visible_nodes
from services.common import (
    ancestors,
    check_status,
    descendants,
    get_document,
    next_order,
    slugify,
)


async def validate_parent(track: dict, kind: str, parent_id: str | None, node_id: str | None = None) -> None:
    hierarchy = track.get("hierarchy") or DEFAULT_HIERARCHY
    if kind not in hierarchy:
        raise HTTPException(status_code=400, detail="Tipo de nó não pertence à hierarquia da trilha")
    if not parent_id:
        return
    parent = await get_document("nodes", parent_id)
    if parent["track_id"] != str(track["_id"]):
        raise HTTPException(status_code=400, detail="Pai pertence a outra trilha")
    if hierarchy.index(kind) <= hierarchy.index(parent["kind"]):
        raise HTTPException(status_code=400, detail="Nível do nó deve ser mais profundo que o do pai")
    current = parent
    while node_id and current:
        if str(current["_id"]) == node_id:
            raise HTTPException(status_code=400, detail="Não é possível mover um nó para dentro de si mesmo")
        current = await db.nodes.find_one({"_id": oid(current["parent_id"])}) if current.get("parent_id") else None


async def create_node(data: dict, user: dict) -> dict:
    check_status(data["status"])
    track = await get_document("tracks", data["track_id"])
    await validate_parent(track, data["kind"], data["parent_id"])
    doc = {
        **data,
        "slug": slugify(data["title"]),
        "order": await next_order("nodes", {"track_id": data["track_id"], "parent_id": data["parent_id"]}),
        "created_by": user["id"],
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.nodes.insert_one(doc)
    await audit(user, "node", str(result.inserted_id), "created", data["track_id"], data["title"])
    return await db.nodes.find_one({"_id": result.inserted_id})


async def reorder_nodes(ordered_ids: list[str]) -> dict:
    for index, node_id in enumerate(ordered_ids):
        await db.nodes.update_one({"_id": oid(node_id)}, {"$set": {"order": index}})
    return {"ok": True}


async def get_node(node_id: str, user: dict) -> dict:
    node = await get_document("nodes", node_id)
    staff = is_staff(user)
    if not staff and not await can_view_node(node, user):
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    block_query = {"node_id": node_id} if staff else {"node_id": node_id, "status": "published"}
    lock = (await track_locks(node["track_id"], user)).get(node_id)
    blocks = [] if lock and not staff else await db.content_blocks.find(block_query).sort("order", 1).to_list(1000)
    relations = await db.relations.find({"$or": [{"node_id": node_id}, {"target_id": node_id}]}).to_list(1000)
    other_ids = {rel["target_id"] if rel["node_id"] == node_id else rel["node_id"] for rel in relations}
    others = {
        str(other["_id"]): other
        for other in await db.nodes.find({"_id": {"$in": [oid(value) for value in other_ids]}}).to_list(1000)
    }
    result_relations = []
    for relation in relations:
        outgoing = relation["node_id"] == node_id
        other_id = relation["target_id"] if outgoing else relation["node_id"]
        other = others.get(other_id)
        if not other or (not staff and other["status"] != "published"):
            continue
        result_relations.append({
            **relation,
            "direction": "outgoing" if outgoing else "incoming",
            "other": {"id": str(other["_id"]), "title": other["title"], "kind": other["kind"]},
        })
    if lock and not staff:
        node = {**node, "description": "", "guidance": ""}
    if not staff:
        node = {key: value for key, value in node.items() if key != "notes"}
    return {"node": node, "blocks": blocks, "relations": result_relations, "ancestors": await ancestors(node), "lock": lock}


async def update_node(node_id: str, data: dict, user: dict) -> dict:
    node = await get_document("nodes", node_id)
    check_status(data.get("status"))
    if "parent_id" in data or "kind" in data:
        track = await get_document("tracks", node["track_id"])
        new_parent = data.get("parent_id", node.get("parent_id")) or None
        await validate_parent(track, data.get("kind", node["kind"]), new_parent, node_id)
        if "parent_id" in data and new_parent != node.get("parent_id"):
            data["parent_id"] = new_parent
            data["order"] = await next_order("nodes", {"track_id": node["track_id"], "parent_id": new_parent})
    if "title" in data:
        data["slug"] = slugify(data["title"])
    data["updated_at"] = now()
    await db.nodes.update_one({"_id": oid(node_id)}, {"$set": data})
    await audit(user, "node", node_id, "updated", node["track_id"],
                f"{node['title']}: " + ", ".join(key for key in data if key not in ("updated_at", "slug", "order")))
    return await db.nodes.find_one({"_id": oid(node_id)})


async def delete_node(node_id: str, user: dict) -> dict:
    node = await get_document("nodes", node_id)
    node_ids = await descendants(node["track_id"], node_id)
    await db.nodes.delete_many({"_id": {"$in": [oid(value) for value in node_ids]}})
    await db.content_blocks.delete_many({"node_id": {"$in": node_ids}})
    await db.relations.delete_many({"$or": [{"node_id": {"$in": node_ids}}, {"target_id": {"$in": node_ids}}]})
    await db.progress.delete_many({"node_id": {"$in": node_ids}})
    await reconcile_orphans(node["track_id"])
    await audit(user, "node", node_id, "deleted", node["track_id"], f"{node['title']} (+{len(node_ids) - 1} filhos)")
    return {"ok": True, "deleted": len(node_ids)}


async def clone_nodes(nodes: list[dict], track_id: str, id_map: dict, parent_override=None, root_ids=None) -> None:
    for node in nodes:
        old_id = str(node["_id"])
        new_node = {key: value for key, value in node.items() if key != "_id"}
        new_node["track_id"] = track_id
        if root_ids is not None and old_id in root_ids:
            new_node["parent_id"] = parent_override
        else:
            new_node["parent_id"] = id_map.get(node.get("parent_id"), node.get("parent_id"))
        new_node["created_at"] = new_node["updated_at"] = now()
        result = await db.nodes.insert_one(new_node)
        id_map[old_id] = str(result.inserted_id)
        blocks = await db.content_blocks.find({"node_id": old_id}).to_list(1000)
        for block in blocks:
            new_block = {key: value for key, value in block.items() if key != "_id"}
            new_block.update(node_id=id_map[old_id], track_id=track_id, created_at=now(), updated_at=now())
            await db.content_blocks.insert_one(new_block)


def parents_first(nodes: list[dict]) -> list[dict]:
    by_id = {str(node["_id"]): node for node in nodes}
    depth = {}

    def get_depth(node: dict) -> int:
        key = str(node["_id"])
        if key not in depth:
            parent = by_id.get(node.get("parent_id"))
            depth[key] = 0 if not parent else get_depth(parent) + 1
        return depth[key]

    return sorted(nodes, key=lambda node: (get_depth(node), node.get("order", 0)))


async def duplicate_node(node_id: str, user: dict) -> dict:
    node = await get_document("nodes", node_id)
    ids = set(await descendants(node["track_id"], node_id))
    subtree = parents_first(await db.nodes.find({"_id": {"$in": [oid(value) for value in ids]}}).to_list(10000))
    id_map = {}
    await clone_nodes(subtree, node["track_id"], id_map, parent_override=node.get("parent_id"), root_ids={node_id})
    new_id = id_map[node_id]
    siblings = await db.nodes.find({"track_id": node["track_id"], "parent_id": node.get("parent_id")}).sort(
        "order", 1).to_list(10000)
    ordered = [str(sibling["_id"]) for sibling in siblings if str(sibling["_id"]) != new_id]
    ordered.insert(ordered.index(node_id) + 1, new_id)
    for index, sibling_id in enumerate(ordered):
        await db.nodes.update_one({"_id": oid(sibling_id)}, {"$set": {"order": index}})
    await db.nodes.update_one({"_id": oid(new_id)}, {"$set": {"title": f"{node['title']} (cópia)", "status": "draft"}})
    await audit(user, "node", new_id, "duplicated", node["track_id"], node["title"])
    return await db.nodes.find_one({"_id": oid(new_id)})


async def get_track_tree(track_id: str, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    staff = is_staff(user)
    if not staff and (track["status"] != "published" or track.get("visibility") == "private"):
        raise HTTPException(status_code=404, detail="Trilha não encontrada")
    nodes = await db.nodes.find({"track_id": track_id}).sort("order", 1).to_list(100000)
    if not staff:
        nodes = visible_nodes(nodes)
    ids = {str(node["_id"]) for node in nodes}
    relations = [relation for relation in await db.relations.find({"track_id": track_id}).to_list(10000)
                 if relation["node_id"] in ids and relation["target_id"] in ids]
    block_match = {"track_id": track_id} if staff else {"track_id": track_id, "status": "published"}
    block_counts = await db.content_blocks.aggregate([
        {"$match": block_match}, {"$group": {"_id": "$node_id", "n": {"$sum": 1}}}
    ]).to_list(10000)
    return {
        "track": track,
        "nodes": nodes,
        "relations": relations,
        "block_counts": {row["_id"]: row["n"] for row in block_counts},
    }
