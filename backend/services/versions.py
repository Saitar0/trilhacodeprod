# ruff: noqa: EXE002
import asyncio
import secrets
from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from audit import audit
from core_utils import now
from database import db
from integrity import load_snapshot, reconcile_orphans, save_version
from serialization import oid, ser
from services.common import get_document

TRACK_FIELDS = ["title", "subtitle", "description", "cover_url", "status", "visibility", "audience", "difficulty",
                "tag_ids", "hierarchy", "level_labels", "settings", "meta"]
NODE_FIELDS = ["title", "kind", "parent_id", "order", "status", "summary", "description", "guidance", "notes",
               "pedagogical_type", "requirement", "depth", "estimated_minutes", "tag_ids", "release"]
BLOCK_FIELDS = ["node_id", "type", "title", "data", "status", "order"]
RELATION_FIELDS = ["type", "enforced", "note"]
RESTORE_LEASE = timedelta(minutes=2)
RESTORE_HEARTBEAT_SECONDS = 20


async def _heartbeat_restore(job_id, owner: str) -> None:
    while True:
        await asyncio.sleep(RESTORE_HEARTBEAT_SECONDS)
        result = await db.restore_jobs.update_one(
            {"_id": job_id, "status": "running", "lease_owner": owner},
            {"$set": {"lease_until": now() + RESTORE_LEASE, "heartbeat_at": now()}},
        )
        if not result.matched_count:
            return


async def _claim_restore(job: dict) -> dict | None:
    owner = secrets.token_hex(16)
    timestamp = now()
    return await db.restore_jobs.find_one_and_update(
        {
            "_id": job["_id"],
            "status": "running",
            "$or": [{"lease_until": {"$lt": timestamp}}, {"lease_until": {"$exists": False}}],
        },
        {"$set": {"lease_owner": owner, "lease_until": timestamp + RESTORE_LEASE, "heartbeat_at": timestamp}},
        return_document=ReturnDocument.AFTER,
    )


async def _finish_restore(job: dict, owner: str, version: dict, snapshot: dict, user: dict, recovered: bool) -> dict:
    track_id = job["track_id"]
    track = await db.tracks.find_one({"_id": oid(track_id)})
    if not track:
        raise ValueError(f"Trilha de restore {track_id} não encontrada")

    new_version = job.get("recovery_version")
    restore_version_id = job.get("restore_version_id")
    backup_version_id = job.get("backup_version_id")
    if new_version is None or not restore_version_id or not backup_version_id:
        new_version = track.get("version", 0) + 1
        restore_version_id = restore_version_id or str(ObjectId())
        if not backup_version_id:
            legacy_backup = await db.track_versions.find_one(
                {
                    "track_id": track_id,
                    "kind": "backup",
                    "note": f"Backup automático antes de restaurar v{version['version']}",
                    "created_at": {"$gte": job["started_at"]},
                },
                sort=[("created_at", 1)],
            )
            backup_version_id = str(legacy_backup["_id"]) if legacy_backup else str(ObjectId())
        saved_plan = await db.restore_jobs.update_one(
            {"_id": job["_id"], "lease_owner": owner},
            {"$set": {
                "recovery_version": new_version,
                "restore_version_id": restore_version_id,
                "backup_version_id": backup_version_id,
            }},
        )
        if not saved_plan.matched_count:
            raise RuntimeError("A trava de restauração foi perdida antes da recuperação")

    backup_note = f"Backup automático antes de restaurar v{version['version']}"
    backup = await db.track_versions.find_one({"_id": oid(backup_version_id)})
    if not backup:
        await save_version(
            track_id, track.get("version", 0), "backup", backup_note, user, await snapshot_track(track_id),
            extra={
                "published_activity_version_id": track.get("published_activity_version_id"),
                "published_activity_count": await db.activity_publications.count_documents({
                    "track_id": track_id, "published_version_id": track.get("published_activity_version_id"),
                }) if track.get("published_activity_version_id") else 0,
            },
            version_id=backup_version_id,
        )

    await apply_snapshot(track_id, snapshot)
    fields = {field: snapshot["track"].get(field) for field in TRACK_FIELDS if field in snapshot["track"]}
    fields.update(status="published", version=new_version, published_at=now(), updated_at=now())
    restored_activity_version_id = version.get("published_activity_version_id")
    if restored_activity_version_id:
        expected_activity_count = version.get("published_activity_count", 0)
        actual_activity_count = await db.activity_publications.count_documents({
            "track_id": track_id, "published_version_id": restored_activity_version_id,
        })
        if actual_activity_count != expected_activity_count:
            raise HTTPException(status_code=409, detail="A publicação de atividades desta versão está incompleta")
        fields["published_activity_version_id"] = restored_activity_version_id
    else:
        fields.pop("published_activity_version_id", None)
    track_update = {"$set": fields}
    if not restored_activity_version_id:
        track_update["$unset"] = {"published_activity_version_id": ""}
    await db.tracks.update_one({"_id": track["_id"]}, track_update)

    version_note = job.get("note") or f"Restaurada a partir da v{version['version']}"
    await save_version(
        track_id, new_version, "restore", version_note, user, await snapshot_track(track_id),
        {"restored_from": str(version["_id"]), "restored_from_version": version["version"],
         "published_activity_version_id": restored_activity_version_id,
         "published_activity_count": await db.activity_publications.count_documents({
             "track_id": track_id, "published_version_id": restored_activity_version_id,
         }) if restored_activity_version_id else 0},
        version_id=restore_version_id,
    )
    status = "recovered" if recovered else "done"
    completed = await db.restore_jobs.update_one(
        {"_id": job["_id"], "lease_owner": owner},
        {"$set": {"status": status, "finished_at": now()},
         "$unset": {"lease_owner": "", "lease_until": "", "failure_code": ""}},
    )
    if not completed.matched_count:
        raise RuntimeError("A trava de restauração foi perdida antes do registro da conclusão")
    await audit(user, "track", track_id, "restored", track_id, f"v{version['version']} → nova v{new_version}")
    return await db.tracks.find_one({"_id": track["_id"]})


async def snapshot_track(track_id: str) -> dict:
    track = await get_document("tracks", track_id)
    collections = {
        "nodes": db.nodes,
        "blocks": db.content_blocks,
        "relations": db.relations,
    }
    filters = {name: {"track_id": track_id} for name in collections}
    before = {name: await collection.count_documents(filters[name]) for name, collection in collections.items()}
    values = {
        name: [item async for item in collection.find(filters[name])]
        for name, collection in collections.items()
    }
    after = {name: await collection.count_documents(filters[name]) for name, collection in collections.items()}
    if before != after or any(len(values[name]) != after[name] for name in collections):
        raise HTTPException(status_code=409, detail="A trilha mudou durante a captura; tente novamente")
    nodes, blocks, relations = values["nodes"], values["blocks"], values["relations"]
    return ser({"track": track, "nodes": nodes, "blocks": blocks, "relations": relations})


async def load_reference(track_id: str, reference: str) -> dict:
    if reference == "current":
        return {"label": "Estado atual (editor)", "snapshot": await snapshot_track(track_id)}
    version = await db.track_versions.find_one({"_id": oid(reference), "track_id": track_id})
    if not version:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    label = f"v{version['version']}" + (" (backup)" if version.get("kind") == "backup" else "")
    return {"label": label, "snapshot": await load_snapshot(version)}


async def list_track_versions(track_id: str) -> list[dict]:
    return await db.track_versions.find(
        {"track_id": track_id, "chunks": {"$exists": True}}, {"snapshot": 0}
    ).sort("created_at", -1).to_list(500)


async def get_version(version_id: str) -> dict:
    version = await get_document("track_versions", version_id)
    return {**version, "snapshot": await load_snapshot(version)}


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
    from integrity import validate_snapshot

    validate_snapshot(snapshot, expected_track_id=track_id)
    for collection in ("nodes", "content_blocks", "relations"):
        await db[collection].delete_many({"track_id": track_id})
    for collection, key in (("nodes", "nodes"), ("content_blocks", "blocks"), ("relations", "relations")):
        documents = [_to_doc(item) for item in snapshot[key]]
        for offset in range(0, len(documents), 1000):
            await db[collection].insert_many(documents[offset:offset + 1000], ordered=False)
    await reconcile_orphans(track_id)


async def resume_restore_jobs() -> None:
    query = {
        "status": "running",
        "$or": [{"lease_until": {"$lt": now()}}, {"lease_until": {"$exists": False}}],
    }
    async for candidate in db.restore_jobs.find(query):
        job = await _claim_restore(candidate)
        if not job:
            continue
        owner = job["lease_owner"]
        heartbeat = asyncio.create_task(_heartbeat_restore(job["_id"], owner))
        try:
            version = await db.track_versions.find_one({"_id": oid(job["version_id"])})
            if not version:
                raise ValueError(f"Versão de restore {job['version_id']} não encontrada")
            if version.get("snapshot_complete") is not True:
                await db.restore_jobs.update_one(
                    {"_id": job["_id"], "lease_owner": owner},
                    {"$set": {"status": "failed", "failure_code": "snapshot_unverified", "finished_at": now()},
                     "$unset": {"lease_owner": "", "lease_until": ""}},
                )
                continue
            try:
                snapshot = await load_snapshot(version)
            except ValueError:
                await db.restore_jobs.update_one(
                    {"_id": job["_id"], "lease_owner": owner},
                    {"$set": {"status": "failed", "failure_code": "snapshot_invalid", "finished_at": now()},
                     "$unset": {"lease_owner": "", "lease_until": ""}},
                )
                continue
            user = {"id": job["user_id"], "name": job.get("user_name", "")}
            await _finish_restore(job, owner, version, snapshot, user, recovered=True)
        finally:
            heartbeat.cancel()
            await asyncio.gather(heartbeat, return_exceptions=True)


async def restore_version(track_id: str, version_id: str, confirm: str, note: str, user: dict) -> dict:
    version = await db.track_versions.find_one({"_id": oid(version_id), "track_id": track_id})
    track = await db.tracks.find_one({"_id": oid(track_id)})
    if not version or not track:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    if confirm.strip().lower() != f"v{version['version']}":
        raise HTTPException(status_code=400, detail=f"Confirmação inválida: digite v{version['version']}")
    if version.get("snapshot_complete") is not True:
        raise HTTPException(
            status_code=409,
            detail="Esta versão não comprova captura completa e não pode ser restaurada automaticamente",
        )
    snapshot = await load_snapshot(version)
    owner = secrets.token_hex(16)
    started = now()
    recovery_version = track.get("version", 0) + 1
    restore_version_id = str(ObjectId())
    backup_version_id = str(ObjectId())
    version_note = note or f"Restaurada a partir da v{version['version']}"
    try:
        job = await db.restore_jobs.insert_one({
            "track_id": track_id, "version_id": version_id, "status": "running",
            "user_id": user["id"], "user_name": user.get("name", ""), "started_at": started,
            "heartbeat_at": started, "note": version_note, "recovery_version": recovery_version,
            "restore_version_id": restore_version_id, "backup_version_id": backup_version_id,
            "lease_owner": owner, "lease_until": started + RESTORE_LEASE,
        })
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Já existe uma restauração em andamento nesta trilha")
    heartbeat = asyncio.create_task(_heartbeat_restore(job.inserted_id, owner))
    try:
        job_data = await db.restore_jobs.find_one({"_id": job.inserted_id})
        return await _finish_restore(job_data, owner, version, snapshot, user, recovered=False)
    finally:
        heartbeat.cancel()
        await asyncio.gather(heartbeat, return_exceptions=True)
