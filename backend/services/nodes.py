# ruff: noqa: EXE002
from fastapi import HTTPException

from audit import audit
from constants import DEFAULT_HIERARCHY
from core_utils import now
from database import db
from integrity import can_view_node, reconcile_orphans
from learning import track_locks, visible_nodes
from permissions import can_view_track, is_staff
from serialization import oid
from services.activity_publications import is_assessment_candidate, public_activity
from services.common import (
    ancestors,
    check_status,
    descendants,
    get_document,
    next_order,
    slugify,
    validate_reorder,
)

_ASSESSMENT_BLOCK_TYPES = {"exercise_objective", "exercise_open", "practical_challenge", "quiz"}
_STUDENT_ASSESSMENT_FIELDS = {
    "prompt", "question", "options", "instructions", "starter_code", "language",
    "acceptance", "grading", "allow_resubmit", "activity_schema_version",
}


def _student_block(block: dict) -> dict:
    """Project assessment blocks through a closed public-field allowlist."""
    if block.get("type") not in _ASSESSMENT_BLOCK_TYPES:
        return block
    data = block.get("data")
    if not isinstance(data, dict):
        return {key: block[key] for key in ("_id", "node_id", "type", "title", "order", "status")
                if key in block}
    if block.get("type") == "quiz":
        # Keep only rendering inputs for an unpublished/legacy static quiz.
        safe_data = {key: value for key, value in data.items()
                     if key in {"question", "prompt", "options", "activity_schema_version"}}
    else:
        safe_data = {key: value for key, value in data.items() if key in _STUDENT_ASSESSMENT_FIELDS}
    public = {key: block[key] for key in (
        "_id", "node_id", "type", "title", "order", "status", "schema_version",
    ) if key in block}
    public["data"] = safe_data
    return public


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
    ids = await validate_reorder("nodes", ordered_ids, ("track_id", "parent_id"))
    for index, node_id in enumerate(ids):
        await db.nodes.update_one({"_id": node_id}, {"$set": {"order": index}})
    return {"ok": True}


async def get_node(node_id: str, user: dict, blocks_limit: int = 1000, blocks_skip: int = 0) -> dict:
    node = await get_document("nodes", node_id)
    staff = is_staff(user)
    if not staff and not await can_view_node(node, user):
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    block_query = {"node_id": node_id} if staff else {"node_id": node_id, "status": "published"}
    lock = (await track_locks(node["track_id"], user)).get(node_id)
    block_page_size = min(max(blocks_limit, 1), 1000)
    blocks = [] if lock and not staff else await db.content_blocks.find(block_query).sort("order", 1).skip(
        max(blocks_skip, 0)).limit(block_page_size).to_list(block_page_size)
    if not staff:
        track = await db.tracks.find_one({"_id": oid(node["track_id"])})
        published_version_id = (track or {}).get("published_activity_version_id")
        activity_publications = {}
        if published_version_id:
            activity_publications = {
                item["activity_id"]: item
                async for item in db.activity_publications.find({
                    "track_id": node["track_id"], "node_id": node_id,
                    "published_version_id": published_version_id,
                })
            }
        student_blocks = []
        for block in blocks:
            if block.get("type") == "quiz":
                publication = activity_publications.get(str(block["_id"]))
                if publication:
                    definition = publication.get("definition") or {}
                    safe_block = _student_block(block)
                    safe_block["activity"] = public_activity(definition)
                    safe_block["data"] = {
                        "question": definition["prompt"],
                        "options": [option["label"] for option in definition["options"]],
                    }
                    student_blocks.append(safe_block)
                    continue
                # During a republish, a valid assessment absent from the old
                # active read model must not become an active student exercise.
                if published_version_id and is_assessment_candidate(block):
                    continue
            student_blocks.append(_student_block(block))
        blocks = student_blocks
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


async def update_node(
    node_id: str,
    data: dict,
    user: dict,
    *,
    editorial_boundary=None,
    session_id: str | None = None,
    expected_revision: int | None = None,
    operation_id: str | None = None,
    transaction_guard=None,
    before_commit=None,
) -> dict:
    if editorial_boundary is not None:
        if (
            not isinstance(session_id, str)
            or expected_revision is None
            or not isinstance(operation_id, str)
            or not data
            or set(data) - {"title", "summary", "description", "guidance"}
            or any(not isinstance(value, str) for value in data.values())
        ):
            raise HTTPException(status_code=422, detail="Alteração editorial inválida")
        changes = dict(data)
        try:
            prepared = await editorial_boundary.prepare_draft_node_update(
                actor_id=user["id"],
                session_id=session_id,
                node_id=node_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                changes=changes,
            )
            receipt = await editorial_boundary.commit_draft_node_update(
                prepared,
                actor_id=user["id"],
                session_id=session_id,
                transaction_guard=transaction_guard,
                before_commit=before_commit,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Alteração editorial inválida") from exc
        stored = await db.nodes.find_one({"_id": oid(node_id)})
        if stored is None:
            raise HTTPException(status_code=409, detail="Unidade não disponível após a operação")
        return {"document": stored, "receipt": receipt}
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


async def get_track_tree(track_id: str, user: dict, limit: int = 100000, skip: int = 0) -> dict:
    track = await get_document("tracks", track_id)
    staff = is_staff(user)
    if not can_view_track(track, user):
        raise HTTPException(status_code=404, detail="Trilha não encontrada")
    nodes = await db.nodes.find({"track_id": track_id}).sort("order", 1).to_list(100000)
    if not staff:
        nodes = visible_nodes(nodes)
    nodes = nodes[max(skip, 0):max(skip, 0) + min(max(limit, 1), 100000)]
    ids = {str(node["_id"]) for node in nodes}
    relations = [relation for relation in await db.relations.find({"track_id": track_id}).to_list(10000)
                 if relation["node_id"] in ids and relation["target_id"] in ids]
    block_match = {"track_id": track_id} if staff else {"track_id": track_id, "status": "published"}
    cursor = await db.content_blocks.aggregate([
        {"$match": block_match}, {"$group": {"_id": "$node_id", "n": {"$sum": 1}}}
    ])
    block_counts = await cursor.to_list(10000)
    return {
        "track": track,
        "nodes": nodes,
        "relations": relations,
        "block_counts": {row["_id"]: row["n"] for row in block_counts},
    }
