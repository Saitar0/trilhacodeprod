import hashlib
import json
import logging
import zlib

from bson import Binary, ObjectId

from core_utils import now
from database import db
from learning import visible_nodes
from permissions import is_staff
from serialization import oid

CHUNK = 4 * 1024 * 1024
log = logging.getLogger("integrity")


def validate_snapshot(
    snapshot: dict, expected_stats: dict | None = None, expected_track_id: str | None = None,
) -> None:
    """Reject malformed or count-mismatched snapshots before they are restored."""
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("track"), dict):
        raise ValueError("Snapshot incompleto: trilha ausente")
    if expected_stats is not None and not isinstance(expected_stats, dict):
        raise ValueError("Snapshot incompleto: contagens inválidas")
    if expected_track_id is not None and snapshot["track"].get("id") != expected_track_id:
        raise ValueError("Snapshot incompatível: identificador da trilha divergente")
    for key in ("nodes", "blocks", "relations"):
        values = snapshot.get(key)
        if not isinstance(values, list):
            raise ValueError(f"Snapshot incompleto: {key} ausente")
        if any(not isinstance(item, dict) for item in values):
            raise ValueError(f"Snapshot incompleto: registros inválidos em {key}")
        if expected_stats is not None and expected_stats.get(key) != len(values):
            raise ValueError(f"Snapshot incompleto: contagem de {key} divergente")
        if expected_track_id is not None and any(item.get("track_id") != expected_track_id for item in values):
            raise ValueError(f"Snapshot incompatível: {key} de outra trilha")

    node_ids = {node.get("id") for node in snapshot["nodes"]}
    if (None in node_ids or len(node_ids) != len(snapshot["nodes"])
            or any(node.get("parent_id") not in node_ids and node.get("parent_id")
                   for node in snapshot["nodes"])):
        raise ValueError("Snapshot inconsistente: hierarquia de nós inválida")
    if any(block.get("node_id") not in node_ids for block in snapshot["blocks"]):
        raise ValueError("Snapshot inconsistente: bloco sem nó correspondente")
    if any(relation.get("node_id") not in node_ids or relation.get("target_id") not in node_ids
           for relation in snapshot["relations"]):
        raise ValueError("Snapshot inconsistente: relação sem nós correspondentes")


# ---------- Chunked, compressed snapshots ----------
async def store_snapshot(version_id, snapshot: dict) -> dict:
    validate_snapshot(snapshot)
    raw = json.dumps(snapshot, ensure_ascii=False, default=str).encode()
    packed = zlib.compress(raw, 6)
    parts = [packed[i:i + CHUNK] for i in range(0, len(packed), CHUNK)] or [b""]
    await db.version_chunks.delete_many({"version_id": str(version_id)})
    await db.version_chunks.insert_many([{"version_id": str(version_id), "seq": i, "data": Binary(p)} for i, p in enumerate(parts)])
    return {"storage": "chunked-zlib", "chunks": len(parts), "raw_bytes": len(raw), "packed_bytes": len(packed),
            "sha256": hashlib.sha256(raw).hexdigest()}


async def load_snapshot(version: dict) -> dict:
    if "snapshot" in version:
        validate_snapshot(version["snapshot"], version.get("stats"), version.get("track_id"))
        return version["snapshot"]
    decompressor = zlib.decompressobj()
    raw_parts, digest, count = [], hashlib.sha256(), 0
    async for chunk in db.version_chunks.find({"version_id": str(version["_id"])}).sort("seq", 1):
        data = decompressor.decompress(bytes(chunk["data"]))
        raw_parts.append(data)
        digest.update(data)
        count += 1
    tail = decompressor.flush()
    raw_parts.append(tail)
    digest.update(tail)
    if count != version.get("chunks"):
        raise ValueError("Snapshot incompleto")
    if digest.hexdigest() != version.get("sha256"):
        raise ValueError("Snapshot corrompido (checksum)")
    snapshot = json.loads(b"".join(raw_parts))
    validate_snapshot(snapshot, version.get("stats"), version.get("track_id"))
    return snapshot


async def save_version(track_id, version, kind, note, user, snapshot, extra=None, version_id=None):
    """Chunks first, metadata last: a version is only listed once fully written."""
    validate_snapshot(snapshot, expected_track_id=track_id)
    vid = ObjectId(version_id) if version_id else ObjectId()
    meta = await store_snapshot(vid, snapshot)
    await db.track_versions.replace_one({"_id": vid}, {
        "_id": vid, "track_id": track_id, "version": version, "kind": kind, "note": note, **meta,
        "stats": {"nodes": len(snapshot["nodes"]), "blocks": len(snapshot["blocks"]), "relations": len(snapshot["relations"])},
        "snapshot_complete": True, "created_by": user["id"], "created_by_name": user.get("name", ""),
        "created_at": now(), **(extra or {})}, upsert=True)
    return str(vid)


async def migrate_legacy_snapshots():
    async for v in db.track_versions.find({"snapshot": {"$exists": True}}):
        meta = await store_snapshot(v["_id"], v["snapshot"])
        await db.track_versions.update_one(
            {"_id": v["_id"]},
            {"$set": {**meta, "snapshot_complete": False}, "$unset": {"snapshot": ""}},
        )


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
    alive = {str(n["_id"]) async for n in db.nodes.find({"track_id": track_id}, {"_id": 1})}
    alive_blocks = {str(b["_id"]) async for b in db.content_blocks.find({"track_id": track_id}, {"_id": 1})}
    for coll in ("submissions", "notes", "reviews"):
        async for d in db[coll].find({"track_id": track_id}, {"node_id": 1, "block_id": 1, "orphaned": 1}):
            dead = d["node_id"] not in alive or bool(d.get("block_id") and d["block_id"] not in alive_blocks)
            if dead != bool(d.get("orphaned")):
                await db[coll].update_one({"_id": d["_id"]}, {"$set": {"orphaned": dead, "orphaned_at": now() if dead else None}})
