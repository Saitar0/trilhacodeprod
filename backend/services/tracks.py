# ruff: noqa: EXE002
import re

from bson import ObjectId
from fastapi import HTTPException

from audit import audit
from core_utils import now
from database import db
from integrity import reconcile_orphans, save_version
from learning import find_cycles
from permissions import can_view_track, is_staff
from serialization import oid
from services.activity_publications import ActivityDefinitionError, normalize_quiz
from services.common import check_status, get_document, next_order, slugify, validate_reorder
from services.nodes import clone_nodes, parents_first
from services.versions import snapshot_track


async def list_tracks(
    status: str | None, query_text: str | None, user: dict, limit: int = 500, skip: int = 0,
) -> list[dict]:
    query = {}
    if not is_staff(user):
        query = {"status": "published", "visibility": "public", "_import_state": {"$exists": False}}
    elif status:
        query["status"] = status
    if query_text:
        query["title"] = {"$regex": re.escape(query_text), "$options": "i"}
    page_size = min(max(limit, 1), 500)
    tracks = await db.tracks.find(query).sort("order", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    track_ids = [str(track["_id"]) for track in tracks]
    match = {"track_id": {"$in": track_ids}}
    if not is_staff(user):
        match["status"] = "published"
    cursor = await db.nodes.aggregate([
        {"$match": match}, {"$group": {"_id": {"t": "$track_id", "k": "$kind"}, "n": {"$sum": 1}}}
    ])
    counts = await cursor.to_list(5000)
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
    ids = await validate_reorder("tracks", ordered_ids)
    for index, track_id in enumerate(ids):
        await db.tracks.update_one({"_id": track_id}, {"$set": {"order": index}})
    return {"ok": True}


async def get_track(track_id: str, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    if not can_view_track(track, user):
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
    for collection in (
        "nodes", "content_blocks", "relations", "progress", "learning_events",
        "activity_publications", "activity_attempts",
    ):
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


async def publish_track(track_id: str, note: str, publish_children: bool, user: dict) -> dict:
    track = await get_document("tracks", track_id)
    if track.get("_import_state") is not None:
        raise HTTPException(status_code=409, detail="A trilha possui uma importação pendente")

    version = track.get("version", 0) + 1
    published_version_id = str(ObjectId())
    publishable_statuses = ["published", "draft"] if publish_children else ["published"]
    snapshot = await snapshot_track(track_id)
    eligible_node_ids = {
        node["id"] for node in snapshot["nodes"] if node.get("status") in publishable_statuses
    }
    blocks = [
        block for block in snapshot["blocks"]
        if block.get("node_id") in eligible_node_ids
        and block.get("type") == "quiz"
        and block.get("status") in publishable_statuses
    ]

    # Validate all new-schema assessments before writing anything. Legacy quiz
    # blocks are included only when they can be safely adapted; invalid legacy
    # blocks remain ordinary static content.
    publications = []
    for block in blocks:
        try:
            definition = normalize_quiz(block, published_version_id, version)
        except ActivityDefinitionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if definition is None:
            continue
        publications.append({
            "_id": ObjectId(),
            "track_id": track_id,
            "node_id": str(block["node_id"]),
            "activity_id": definition["activity_id"],
            "published_version_id": published_version_id,
            "definition": definition,
            "created_at": now(),
        })

    # Prepare the exact snapshot and assessment read model first. The active
    # pointer is swapped only after both are complete, so students keep using
    # the previous immutable definition if preparation fails.
    if publish_children:
        for node in snapshot["nodes"]:
            if node.get("status") == "draft":
                node["status"] = "published"
        for block in snapshot["blocks"]:
            if block.get("status") == "draft":
                block["status"] = "published"
    timestamp = now()
    snapshot["track"].update(
        status="published", version=version, published_at=timestamp.isoformat(), updated_at=timestamp.isoformat(),
    )
    if publications:
        await db.activity_publications.insert_many(publications, ordered=True)
    await save_version(
        track_id, version, "publish", note, user, snapshot,
        extra={"published_activity_version_id": published_version_id,
               "published_activity_count": len(publications)}, version_id=published_version_id,
    )

    if publish_children:
        await db.nodes.update_many({"track_id": track_id, "status": "draft"}, {"$set": {"status": "published"}})
        await db.content_blocks.update_many(
            {"track_id": track_id, "status": "draft"}, {"$set": {"status": "published"}}
        )
    current_version_filter = {"version": track.get("version", 0)} if "version" in track else {"version": {"$exists": False}}
    activated = await db.tracks.update_one({"_id": oid(track_id), **current_version_filter}, {"$set": {
        "status": "published", "version": version, "published_at": timestamp, "updated_at": timestamp,
        "published_activity_version_id": published_version_id,
    }})
    if not activated.matched_count:
        raise HTTPException(status_code=409, detail="A trilha mudou durante a publicação; tente novamente")
    await audit(user, "track", track_id, "published", track_id, f"v{version} {note}".strip())
    return await db.tracks.find_one({"_id": oid(track_id)})
