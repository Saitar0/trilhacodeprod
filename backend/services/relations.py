# ruff: noqa: EXE002
from fastapi import HTTPException

from audit import audit
from core_utils import now
from database import db
from learning import prerequisite_cycle
from serialization import oid
from services.common import ancestors, descendants, get_document


async def create_relation(data: dict, user: dict) -> dict:
    if data.get("prerequisite_kind") is not None and data.get("type") != "prerequisite":
        raise HTTPException(status_code=400, detail="O tipo de pré-requisito só se aplica a relações prerequisite")
    if data["node_id"] == data["target_id"]:
        raise HTTPException(status_code=400, detail="Um nó não pode se relacionar consigo mesmo")
    source = await get_document("nodes", data["node_id"])
    target = await get_document("nodes", data["target_id"])
    if source["track_id"] != target["track_id"]:
        raise HTTPException(status_code=400, detail="Relações devem ser dentro da mesma trilha")
    existing = await db.relations.find_one({
        "node_id": data["node_id"], "target_id": data["target_id"], "type": data["type"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Relação já existe")
    if data["type"] == "prerequisite":
        lineage = set(await descendants(source["track_id"], data["node_id"]))
        lineage.update(ancestor["id"] for ancestor in await ancestors(source))
        if data["target_id"] in lineage:
            raise HTTPException(status_code=400, detail="Um item não pode ter como pré-requisito seu próprio pai ou filho")
        relations = await db.relations.find({"track_id": source["track_id"]}).to_list(10000)
        if prerequisite_cycle(relations, data["node_id"], data["target_id"]):
            raise HTTPException(status_code=400, detail="Esta relação criaria um ciclo de pré-requisitos")
    doc = {**data, "track_id": source["track_id"], "created_at": now()}
    result = await db.relations.insert_one(doc)
    await audit(user, "relation", str(result.inserted_id), "created", source["track_id"],
                f"{source['title']} → {data['type']} → {target['title']}")
    return await db.relations.find_one({"_id": result.inserted_id})


async def update_relation(relation_id: str, data: dict, user: dict) -> dict:
    relation = await get_document("relations", relation_id)
    if data.get("prerequisite_kind") is not None and relation.get("type") != "prerequisite":
        raise HTTPException(status_code=400, detail="O tipo de pré-requisito só se aplica a relações prerequisite")
    await db.relations.update_one({"_id": oid(relation_id)}, {"$set": data})
    await audit(user, "relation", relation_id, "updated", relation["track_id"], relation["type"])
    return await db.relations.find_one({"_id": oid(relation_id)})


async def delete_relation(relation_id: str, user: dict) -> dict:
    relation = await get_document("relations", relation_id)
    await db.relations.delete_one({"_id": oid(relation_id)})
    await audit(user, "relation", relation_id, "deleted", relation["track_id"], relation["type"])
    return {"ok": True}
