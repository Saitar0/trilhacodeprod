# ruff: noqa: EXE002
from fastapi import HTTPException

from audit import audit
from core_utils import now
from database import db
from integrity import reconcile_orphans
from serialization import oid
from services.common import check_status, get_document, next_order, validate_reorder


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
    ids = await validate_reorder("content_blocks", ordered_ids, ("node_id",))
    for index, block_id in enumerate(ids):
        await db.content_blocks.update_one({"_id": block_id}, {"$set": {"order": index}})
    return {"ok": True}


async def update_block(
    block_id: str,
    data: dict,
    user: dict,
    *,
    editorial_boundary=None,
    session_id: str | None = None,
    expected_revision: int | None = None,
    operation_id: str | None = None,
    requested_track_id: str | None = None,
    transaction_guard=None,
    before_commit=None,
) -> dict:
    if editorial_boundary is not None:
        if (
            not isinstance(session_id, str)
            or expected_revision is None
            or not isinstance(operation_id, str)
            or set(data) - {"title", "data"}
            or not data
        ):
            raise HTTPException(status_code=422, detail="Alteração editorial inválida")
        block_object_id = oid(block_id)
        block = await get_document("content_blocks", block_id)
        if requested_track_id is not None and block.get("track_id") != requested_track_id:
            raise HTTPException(status_code=404, detail="Bloco não encontrado")
        try:
            prepared = await editorial_boundary.prepare_draft_block_update(
                actor_id=user["id"],
                session_id=session_id,
                block_id=block_object_id,
                operation_id=operation_id,
                expected_revision=expected_revision,
                changes=data,
                requested_track_id=requested_track_id,
            )
            receipt = await editorial_boundary.commit_draft_block_update(
                prepared,
                actor_id=user["id"],
                session_id=session_id,
                transaction_guard=transaction_guard,
                before_commit=before_commit,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Alteração editorial inválida") from exc
        updated = await db.content_blocks.find_one({"_id": block_object_id})
        if updated is None:
            raise HTTPException(status_code=409, detail="Bloco alterado; recarregue antes de continuar")
        return {"document": updated, "receipt": receipt}

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
