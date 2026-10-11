from datetime import datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core import audit, db, now, oid, require, ser
from integrity import load_snapshot, reconcile_orphans, save_version
from routes_content import _snapshot

router = APIRouter(prefix="/api")

TRACK_FIELDS = ["title", "subtitle", "description", "cover_url", "status", "visibility", "audience", "difficulty",
                "tag_ids", "hierarchy", "level_labels", "settings", "meta"]
NODE_FIELDS = ["title", "kind", "parent_id", "order", "status", "summary", "description", "guidance", "notes",
               "pedagogical_type", "requirement", "depth", "estimated_minutes", "tag_ids", "release"]
BLOCK_FIELDS = ["node_id", "type", "title", "data", "status", "order"]
RELATION_FIELDS = ["type", "enforced", "note"]


class RestoreIn(BaseModel):
    confirm: str
    note: str = ""


async def _load(track_id: str, ref: str):
    if ref == "current":
        return {"label": "Estado atual (editor)", "snapshot": await _snapshot(track_id)}
    v = await db.track_versions.find_one({"_id": oid(ref), "track_id": track_id})
    if not v:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    return {"label": f"v{v['version']}" + (" (backup)" if v.get("kind") == "backup" else ""), "snapshot": await load_snapshot(v)}


def _diff(a_list, b_list, fields, describe):
    a = {x["id"]: x for x in a_list}
    b = {x["id"]: x for x in b_list}
    added = [describe(b[i]) for i in b if i not in a]
    removed = [describe(a[i]) for i in a if i not in b]
    changed = []
    for i in a.keys() & b.keys():
        changes = [{"field": f, "from": a[i].get(f), "to": b[i].get(f)} for f in fields if a[i].get(f) != b[i].get(f)]
        if changes:
            changed.append({**describe(b[i]), "changes": changes})
    return {"added": added, "removed": removed, "changed": changed}


def compare_snapshots(a, b):
    titles = {n["id"]: n["title"] for n in a["nodes"] + b["nodes"]}
    title = lambda i: titles.get(i, "(raiz)") if i else "(raiz)"  # noqa: E731
    nodes = _diff(a["nodes"], b["nodes"], NODE_FIELDS,
                  lambda n: {"id": n["id"], "title": n["title"], "kind": n["kind"], "parent": title(n.get("parent_id"))})
    for c in nodes["changed"]:
        for ch in c["changes"]:
            if ch["field"] == "parent_id":
                ch.update({"from": title(ch["from"]), "to": title(ch["to"])})
    blocks = _diff(a["blocks"], b["blocks"], BLOCK_FIELDS,
                   lambda x: {"id": x["id"], "title": x.get("title") or x["type"], "type": x["type"], "node": title(x["node_id"])})
    rels = _diff(a["relations"], b["relations"], RELATION_FIELDS,
                 lambda r: {"id": r["id"], "type": r["type"], "title": f"{title(r['node_id'])} → {title(r['target_id'])}"})
    track_changes = [{"field": f, "from": a["track"].get(f), "to": b["track"].get(f)}
                     for f in TRACK_FIELDS if a["track"].get(f) != b["track"].get(f)]
    total = sum(len(d[k]) for d in (nodes, blocks, rels) for k in ("added", "removed", "changed")) + len(track_changes)
    return {"track": track_changes, "nodes": nodes, "blocks": blocks, "relations": rels, "total_changes": total}


@router.get("/tracks/{track_id}/compare")
async def compare(track_id: str, base: str, target: str, _: dict = Depends(require("content.read"))):
    a, b = await _load(track_id, base), await _load(track_id, target)
    return {"base": a["label"], "target": b["label"], **compare_snapshots(a["snapshot"], b["snapshot"])}


def _to_doc(item: dict) -> dict:
    doc = {}
    for k, v in item.items():
        if k == "id":
            doc["_id"] = ObjectId(v)
        elif k.endswith("_at") and isinstance(v, str):
            try:
                doc[k] = datetime.fromisoformat(v)
            except ValueError:
                doc[k] = v
        else:
            doc[k] = v
    return doc


async def _apply_snapshot(track_id: str, snap: dict):
    """Idempotent: replaces the track's structure with the snapshot. Safe to re-run after a crash."""
    for coll in ("nodes", "content_blocks", "relations"):
        await db[coll].delete_many({"track_id": track_id})
    for coll, key in (("nodes", "nodes"), ("content_blocks", "blocks"), ("relations", "relations")):
        docs = [_to_doc(x) for x in snap[key]]
        for i in range(0, len(docs), 1000):
            await db[coll].insert_many(docs[i:i + 1000], ordered=False)
    await reconcile_orphans(track_id)


async def resume_restore_jobs():
    async for job in db.restore_jobs.find({"status": "running"}):
        v = await db.track_versions.find_one({"_id": oid(job["version_id"])})
        await _apply_snapshot(job["track_id"], await load_snapshot(v))
        await db.restore_jobs.update_one({"_id": job["_id"]}, {"$set": {"status": "recovered", "finished_at": now()}})


@router.post("/tracks/{track_id}/versions/{version_id}/restore")
async def restore(track_id: str, version_id: str, body: RestoreIn, user: dict = Depends(require("content.publish"))):
    v = await db.track_versions.find_one({"_id": oid(version_id), "track_id": track_id})
    track = await db.tracks.find_one({"_id": oid(track_id)})
    if not v or not track:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    if body.confirm.strip().lower() != f"v{v['version']}":
        raise HTTPException(status_code=400, detail=f"Confirmação inválida: digite v{v['version']}")
    snap = await load_snapshot(v)
    try:
        job = await db.restore_jobs.insert_one({"track_id": track_id, "version_id": version_id, "status": "running",
                                                "user_id": user["id"], "started_at": now()})
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Já existe uma restauração em andamento nesta trilha")
    await save_version(track_id, track.get("version", 0), "backup", f"Backup automático antes de restaurar v{v['version']}",
                       user, await _snapshot(track_id))
    await _apply_snapshot(track_id, snap)
    version = track.get("version", 0) + 1
    fields = {f: snap["track"].get(f) for f in TRACK_FIELDS if f in snap["track"]}
    fields.update(status="published", version=version, published_at=now(), updated_at=now())
    await db.tracks.update_one({"_id": track["_id"]}, {"$set": fields})
    note = body.note or f"Restaurada a partir da v{v['version']}"
    await save_version(track_id, version, "restore", note, user, await _snapshot(track_id),
                       {"restored_from": version_id, "restored_from_version": v["version"]})
    await db.restore_jobs.update_one({"_id": job.inserted_id}, {"$set": {"status": "done", "finished_at": now()}})
    await audit(user, "track", track_id, "restored", track_id, f"v{v['version']} → nova v{version}")
    return ser(await db.tracks.find_one({"_id": track["_id"]}))
