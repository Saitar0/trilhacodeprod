import hashlib
import json
import logging
import zlib

from bson import Binary, ObjectId

from core import db, is_staff, now, oid
from learning import visible_nodes

CHUNK = 4 * 1024 * 1024
log = logging.getLogger("integrity")


# ---------- Chunked, compressed snapshots ----------
async def store_snapshot(version_id, snapshot: dict) -> dict:
    raw = json.dumps(snapshot, ensure_ascii=False, default=str).encode()
    packed = zlib.compress(raw, 6)
    parts = [packed[i:i + CHUNK] for i in range(0, len(packed), CHUNK)] or [b""]
    await db.version_chunks.insert_many([{"version_id": str(version_id), "seq": i, "data": Binary(p)} for i, p in enumerate(parts)])
    return {"storage": "chunked-zlib", "chunks": len(parts), "raw_bytes": len(raw), "packed_bytes": len(packed),
            "sha256": hashlib.sha256(raw).hexdigest()}


async def load_snapshot(version: dict) -> dict:
    if "snapshot" in version:
        return version["snapshot"]
    chunks = await db.version_chunks.find({"version_id": str(version["_id"])}).sort("seq", 1).to_list(10000)
    if len(chunks) != version.get("chunks"):
        raise ValueError("Snapshot incompleto")
    raw = zlib.decompress(b"".join(bytes(c["data"]) for c in chunks))
    if hashlib.sha256(raw).hexdigest() != version.get("sha256"):
        raise ValueError("Snapshot corrompido (checksum)")
    return json.loads(raw)


async def save_version(track_id, version, kind, note, user, snapshot, extra=None):
    """Chunks first, metadata last: a version is only listed once fully written."""
    vid = ObjectId()
    meta = await store_snapshot(vid, snapshot)
    await db.track_versions.insert_one({
        "_id": vid, "track_id": track_id, "version": version, "kind": kind, "note": note, **meta,
        "stats": {"nodes": len(snapshot["nodes"]), "blocks": len(snapshot["blocks"]), "relations": len(snapshot["relations"])},
        "created_by": user["id"], "created_by_name": user.get("name", ""), "created_at": now(), **(extra or {})})
    return str(vid)


async def migrate_legacy_snapshots():
    async for v in db.track_versions.find({"snapshot": {"$exists": True}}):
        meta = await store_snapshot(v["_id"], v["snapshot"])
        await db.track_versions.update_one({"_id": v["_id"]}, {"$set": meta, "$unset": {"snapshot": ""}})


# ---------- Student visibility ----------
async def visible_ids(user: dict, track_ids) -> set:
    """Node ids the user may see: published+public track, node and all ancestors published."""
    track_ids = [t for t in set(track_ids) if t]
    q = {"_id": {"$in": [oid(t) for t in track_ids]}}
    if not is_staff(user):
        q.update(status="published", visibility="public")
    tracks = [str(t["_id"]) for t in await db.tracks.find(q, {"_id": 1}).to_list(1000)]
    nodes = await db.nodes.find({"track_id": {"$in": tracks}}, {"parent_id": 1, "status": 1, "track_id": 1}).to_list(100000)
    keep = nodes if is_staff(user) else visible_nodes(nodes)
    return {str(n["_id"]) for n in keep}


async def can_view_node(node: dict, user: dict) -> bool:
    return str(node["_id"]) in await visible_ids(user, [node["track_id"]])


# ---------- Orphans ----------
async def reconcile_orphans(track_id: str):
    """Flag submissions/notes/reviews whose node no longer exists; unflag if it came back (restore)."""
    alive = {str(n["_id"]) for n in await db.nodes.find({"track_id": track_id}, {"_id": 1}).to_list(100000)}
    alive_blocks = {str(b["_id"]) for b in await db.content_blocks.find({"track_id": track_id}, {"_id": 1}).to_list(200000)}
    for coll in ("submissions", "notes", "reviews"):
        async for d in db[coll].find({"track_id": track_id}, {"node_id": 1, "block_id": 1, "orphaned": 1}):
            dead = d["node_id"] not in alive or bool(d.get("block_id") and d["block_id"] not in alive_blocks)
            if dead != bool(d.get("orphaned")):
                await db[coll].update_one({"_id": d["_id"]}, {"$set": {"orphaned": dead, "orphaned_at": now() if dead else None}})
