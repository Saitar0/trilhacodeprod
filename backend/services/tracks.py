# ruff: noqa: EXE002
import re

from fastapi import HTTPException

from core import audit, db, is_staff, now, oid, ser
from integrity import reconcile_orphans, save_version
from learning import find_cycles
from services.common import check_status, get_document, next_order, slugify
from services.nodes import clone_nodes, parents_first


async def list_tracks(status: str | None, query_text: str | None, user: dict) -> list[dict]:
    query = {}
    if not is_staff(user):
        query = {"status": "published", "visibility": "public"}
    elif status:
        query["status"] = status
    if query_text:
        query["title"] = {"$regex": re.escape(query_text), "$options": "i"}
    tracks = await db.tracks.find(query).sort("order", 1).to_list(500)
    track_ids = [str(track["_id"]) for track in tracks]
    match = {"track_id": {"$in": track_ids}}
    if not is_staff(user):
        match["status"] = "published"
    counts = await db.nodes.aggregate([
        {"$match": match}, {"$group": {"_id": {"t": "$track_id", "k": "$kind"}, "n": {"$sum": 1}}}
    ]).to_list(5000)
    by_track = {}
    for count in counts:
        by_track.setdefault(count["_id"]["t"], {})[count["_id"]["k"]] = count["n"]
    result = []
    for track in tracks:
        item = dict(track)
        item["counts"] = by_track.get(str(track["_id"]), {})
        result.append(item)
    return result


async def create_track(data: dict, user: dict) -> dict:
    check_status(data["status"])
    document = {
        **data,
        "slug": data["slug"] or slugify(data["title"]),
        "order": await next_order("tracks", {}),
        "version": 0,
        "derived_from": None,
        "created_by": user["id"],
        "created_at": now(),
        "updated_at": now(),
        "published_at": None,
    }
    result = await db.tracks.insert_one(document)
    await audit(user, "track", str(result.inserted_id), "created", str(result.inserted_id), data["title"])
    return await db.tracks.find_one({"_id": result.inserted_id})


async def reorder_tracks(ordered_ids: list[str]) -> dict:
    for index, track_id in enumerate(ordered_ids):
        await db.tracks.update_one({"_id": oid(track_id)}, {"$set": {"order": index}})
    return {"ok": True}


async def get_track(track_id: str, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    if not is_staff(user) and track["status"] != "published":
        raise HTTPException(status_code=404, detail="Trilha não encontrada")
    return track


async def update_track(track_id: str, data: dict, user: dict) -> dict:
    await get_document("tracks", track_id)
    check_status(data.get("status"))
    if data.get("status") == "published":
        raise HTTPException(status_code=400, detail="Use a ação Publicar para publicar a trilha")
    if (data.get("settings") or {}).get("enforce_prerequisites"):
        relations = await db.relations.find({"track_id": track_id}).to_list(10000)
        if find_cycles(relations):
            raise HTTPException(status_code=400, detail="Há ciclos de pré-requisitos. Corrija-os antes de ativar a progressão bloqueante")
    data["updated_at"] = now()
    await db.tracks.update_one({"_id": oid(track_id)}, {"$set": data})
    await audit(user, "track", track_id, "updated", track_id, ", ".join(key for key in data if key != "updated_at"))
    return await db.tracks.find_one({"_id": oid(track_id)})


async def delete_track(track_id: str, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    for collection in ("nodes", "content_blocks", "relations", "progress", "learning_events"):
        await db[collection].delete_many({"track_id": track_id})
    await db.user_track_state.delete_many({"track_id": track_id})
    version_ids = [
        str(version["_id"])
        for version in await db.track_versions.find({"track_id": track_id}, {"_id": 1}).to_list(10000)
    ]
    await db.version_chunks.delete_many({"version_id": {"$in": version_ids}})
    await db.track_versions.delete_many({"track_id": track_id})
    await reconcile_orphans(track_id)
    await db.tracks.delete_one({"_id": oid(track_id)})
    await audit(user, "track", track_id, "deleted", track_id, track["title"])
    return {"ok": True}


async def duplicate_track(track_id: str, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    document = {key: value for key, value in track.items() if key != "_id"}
    document.update(
        title=f"{track['title']} (cópia)",
        slug=f"{track['slug']}-copia",
        status="draft",
        version=0,
        derived_from=track_id,
        order=await next_order("tracks", {}),
        created_by=user["id"],
        created_at=now(),
        updated_at=now(),
        published_at=None,
    )
    result = await db.tracks.insert_one(document)
    new_id = str(result.inserted_id)
    nodes = parents_first(await db.nodes.find({"track_id": track_id}).to_list(10000))
    id_map = {}
    await clone_nodes(nodes, new_id, id_map)
    relations = await db.relations.find({"track_id": track_id}).to_list(10000)
    for relation in relations:
        if relation["node_id"] in id_map and relation["target_id"] in id_map:
            new_relation = {key: value for key, value in relation.items() if key != "_id"}
            new_relation.update(
                track_id=new_id,
                node_id=id_map[relation["node_id"]],
                target_id=id_map[relation["target_id"]],
            )
            await db.relations.insert_one(new_relation)
    await audit(user, "track", new_id, "duplicated", new_id, f"derivada de {track['title']}")
    return await db.tracks.find_one({"_id": result.inserted_id})


async def snapshot_track(track_id: str) -> dict:
    track = await get_document("tracks", track_id)
    nodes = await db.nodes.find({"track_id": track_id}).to_list(10000)
    blocks = await db.content_blocks.find({"track_id": track_id}).to_list(50000)
    relations = await db.relations.find({"track_id": track_id}).to_list(10000)
    return ser({"track": track, "nodes": nodes, "blocks": blocks, "relations": relations})


async def publish_track(track_id: str, note: str, publish_children: bool, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    if publish_children:
        await db.nodes.update_many({"track_id": track_id, "status": "draft"}, {"$set": {"status": "published"}})
        await db.content_blocks.update_many(
            {"track_id": track_id, "status": "draft"}, {"$set": {"status": "published"}}
        )
    version = track.get("version", 0) + 1
    await db.tracks.update_one({"_id": oid(track_id)}, {"$set": {
        "status": "published", "version": version, "published_at": now(), "updated_at": now()
    }})
    await save_version(track_id, version, "publish", note, user, await snapshot_track(track_id))
    await audit(user, "track", track_id, "published", track_id, f"v{version} {note}".strip())
    return await db.tracks.find_one({"_id": oid(track_id)})
