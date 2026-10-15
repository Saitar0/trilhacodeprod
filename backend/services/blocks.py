# ruff: noqa: EXE002
from fastapi import HTTPException

from core import audit, db, now, oid
from integrity import reconcile_orphans
from services.common import check_status, get_document, next_order


async def create_block(data: dict, user: dict) -> dict:
    check_status(data["status"])
    node = await get_document("nodes", data["node_id"])
    if not await db.block_types.find_one({"key": data["type"]}):
        raise HTTPException(status_code=400, detail="Tipo de bloco desconhecido")
    doc = {
        **data,
        "track_id": node["track_id"],
        "order": await next_order("content_blocks", {"node_id": data["node_id"]}),
        "schema_version": 1,
        "created_by": user["id"],
        "created_at": now(),
        "updated_at": now(),
    }
    result = await db.content_blocks.insert_one(doc)
    await audit(user, "block", str(result.inserted_id), "created", node["track_id"], f"{data['type']} em {node['title']}")
    return await db.content_blocks.find_one({"_id": result.inserted_id})


async def reorder_blocks(ordered_ids: list[str]) -> dict:
    for index, block_id in enumerate(ordered_ids):
        await db.content_blocks.update_one({"_id": oid(block_id)}, {"$set": {"order": index}})
    return {"ok": True}


async def update_block(block_id: str, data: dict, user: dict) -> dict:
    block = await get_document("content_blocks", block_id)
    check_status(data.get("status"))
    data["updated_at"] = now()
    await db.content_blocks.update_one({"_id": oid(block_id)}, {"$set": data})
    await audit(user, "block", block_id, "updated", block["track_id"], block["type"])
    return await db.content_blocks.find_one({"_id": oid(block_id)})


async def delete_block(block_id: str, user: dict) -> dict:
    block = await get_document("content_blocks", block_id)
    await db.content_blocks.delete_one({"_id": oid(block_id)})
    await reconcile_orphans(block["track_id"])
    await audit(user, "block", block_id, "deleted", block["track_id"], block["type"])
    return {"ok": True}
