# ruff: noqa: EXE002
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from core import audit, db, now, oid, ser
from integrity import load_snapshot, reconcile_orphans, save_version
from services.common import get_document

TRACK_FIELDS = ["title", "subtitle", "description", "cover_url", "status", "visibility", "audience", "difficulty",
                "tag_ids", "hierarchy", "level_labels", "settings", "meta"]
NODE_FIELDS = ["title", "kind", "parent_id", "order", "status", "summary", "description", "guidance", "notes",
               "pedagogical_type", "requirement", "depth", "estimated_minutes", "tag_ids", "release"]
BLOCK_FIELDS = ["node_id", "type", "title", "data", "status", "order"]
RELATION_FIELDS = ["type", "enforced", "note"]


async def snapshot_track(track_id: str) -> dict:
    track = await get_document("tracks", track_id)
    nodes = await db.nodes.find({"track_id": track_id}).to_list(10000)
    blocks = await db.content_blocks.find({"track_id": track_id}).to_list(50000)
    relations = await db.relations.find({"track_id": track_id}).to_list(10000)
    return ser({"track": track, "nodes": nodes, "blocks": blocks, "relations": relations})


async def load_reference(track_id: str, reference: str) -> dict:
    if reference == "current":
        return {"label": "Estado atual (editor)", "snapshot": await snapshot_track(track_id)}
    version = await db.track_versions.find_one({"_id": oid(reference), "track_id": track_id})
    if not version:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    label = f"v{version['version']}" + (" (backup)" if version.get("kind") == "backup" else "")
    return {"label": label, "snapshot": await load_snapshot(version)}


def _diff(a_list: list[dict], b_list: list[dict], fields: list[str], describe) -> dict:
    a = {item["id"]: item for item in a_list}
    b = {item["id"]: item for item in b_list}
    added = [describe(b[item_id]) for item_id in b if item_id not in a]
    removed = [describe(a[item_id]) for item_id in a if item_id not in b]
    changed = []
    for item_id in a.keys() & b.keys():
        changes = [
            {"field": field, "from": a[item_id].get(field), "to": b[item_id].get(field)}
            for field in fields if a[item_id].get(field) != b[item_id].get(field)
        ]
        if changes:
            changed.append({**describe(b[item_id]), "changes": changes})
    return {"added": added, "removed": removed, "changed": changed}


def compare_snapshots(a: dict, b: dict) -> dict:
    titles = {node["id"]: node["title"] for node in a["nodes"] + b["nodes"]}
    title = lambda item_id: titles.get(item_id, "(raiz)") if item_id else "(raiz)"  # noqa: E731
    nodes = _diff(a["nodes"], b["nodes"], NODE_FIELDS,
                  lambda node: {"id": node["id"], "title": node["title"], "kind": node["kind"],
                                "parent": title(node.get("parent_id"))})
    for change in nodes["changed"]:
        for field_change in change["changes"]:
            if field_change["field"] == "parent_id":
                field_change.update({"from": title(field_change["from"]), "to": title(field_change["to"])})
    blocks = _diff(a["blocks"], b["blocks"], BLOCK_FIELDS,
                   lambda block: {"id": block["id"], "title": block.get("title") or block["type"],
                                  "type": block["type"], "node": title(block["node_id"])})
    relations = _diff(a["relations"], b["relations"], RELATION_FIELDS,
                      lambda relation: {"id": relation["id"], "type": relation["type"],
                                        "title": f"{title(relation['node_id'])} → {title(relation['target_id'])}"})
    track_changes = [
        {"field": field, "from": a["track"].get(field), "to": b["track"].get(field)}
        for field in TRACK_FIELDS if a["track"].get(field) != b["track"].get(field)
    ]
    total = sum(len(section[key]) for section in (nodes, blocks, relations)
                for key in ("added", "removed", "changed")) + len(track_changes)
    return {"track": track_changes, "nodes": nodes, "blocks": blocks, "relations": relations,
            "total_changes": total}


async def compare_versions(track_id: str, base: str, target: str) -> dict:
    a, b = await load_reference(track_id, base), await load_reference(track_id, target)
    return {"base": a["label"], "target": b["label"], **compare_snapshots(a["snapshot"], b["snapshot"])}


def _to_doc(item: dict) -> dict:
    document = {}
    for key, value in item.items():
        if key == "id":
            document["_id"] = ObjectId(value)
        elif key.endswith("_at") and isinstance(value, str):
            try:
                document[key] = datetime.fromisoformat(value)
            except ValueError:
                document[key] = value
        else:
            document[key] = value
    return document


async def apply_snapshot(track_id: str, snapshot: dict) -> None:
    """Idempotently replace a track's structure with the supplied snapshot."""
    for collection in ("nodes", "content_blocks", "relations"):
        await db[collection].delete_many({"track_id": track_id})
    for collection, key in (("nodes", "nodes"), ("content_blocks", "blocks"), ("relations", "relations")):
        documents = [_to_doc(item) for item in snapshot[key]]
        for offset in range(0, len(documents), 1000):
            await db[collection].insert_many(documents[offset:offset + 1000], ordered=False)
    await reconcile_orphans(track_id)


async def resume_restore_jobs() -> None:
    async for job in db.restore_jobs.find({"status": "running"}):
        version = await db.track_versions.find_one({"_id": oid(job["version_id"])})
        await apply_snapshot(job["track_id"], await load_snapshot(version))
        await db.restore_jobs.update_one({"_id": job["_id"]}, {"$set": {"status": "recovered", "finished_at": now()}})


async def restore_version(track_id: str, version_id: str, confirm: str, note: str, user: dict) -> dict:
    version = await db.track_versions.find_one({"_id": oid(version_id), "track_id": track_id})
    track = await db.tracks.find_one({"_id": oid(track_id)})
    if not version or not track:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    if confirm.strip().lower() != f"v{version['version']}":
        raise HTTPException(status_code=400, detail=f"Confirmação inválida: digite v{version['version']}")
    snapshot = await load_snapshot(version)
    try:
        job = await db.restore_jobs.insert_one({
            "track_id": track_id, "version_id": version_id, "status": "running",
            "user_id": user["id"], "started_at": now(),
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Já existe uma restauração em andamento nesta trilha")
    await save_version(track_id, track.get("version", 0), "backup",
                       f"Backup automático antes de restaurar v{version['version']}", user,
                       await snapshot_track(track_id))
    await apply_snapshot(track_id, snapshot)
    new_version = track.get("version", 0) + 1
    fields = {field: snapshot["track"].get(field) for field in TRACK_FIELDS if field in snapshot["track"]}
    fields.update(status="published", version=new_version, published_at=now(), updated_at=now())
    await db.tracks.update_one({"_id": track["_id"]}, {"$set": fields})
    version_note = note or f"Restaurada a partir da v{version['version']}"
    await save_version(track_id, new_version, "restore", version_note, user, await snapshot_track(track_id),
                       {"restored_from": version_id, "restored_from_version": version["version"]})
    await db.restore_jobs.update_one({"_id": job.inserted_id}, {"$set": {"status": "done", "finished_at": now()}})
    await audit(user, "track", track_id, "restored", track_id, f"v{version['version']} → nova v{new_version}")
    return await db.tracks.find_one({"_id": track["_id"]})
