from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from constants import DEFAULT_HIERARCHY, DEFAULT_LABELS, PROGRESS_STATUSES, ROLES, STATUSES
from core_utils import now
from database import db
from serialization import oid, ser

TAXONOMY_GROUPS = ["pedagogical_type", "requirement", "depth", "relation_type"]


async def get_metadata() -> dict:
    taxonomies = await db.taxonomies.find({}).sort("order", 1).to_list(1000)
    grouped = {group: [] for group in TAXONOMY_GROUPS}
    for taxonomy in taxonomies:
        grouped.setdefault(taxonomy["group"], []).append(ser(taxonomy))
    block_types = await db.block_types.find({}).sort("order", 1).to_list(500)
    tags = await db.tags.find({}).sort("name", 1).to_list(1000)
    return {
        "taxonomies": grouped,
        "block_types": [ser(item) for item in block_types],
        "tags": [ser(item) for item in tags],
        "statuses": STATUSES,
        "progress_statuses": PROGRESS_STATUSES,
        "roles": ROLES,
        "default_hierarchy": DEFAULT_HIERARCHY,
        "default_labels": DEFAULT_LABELS,
    }


async def create_taxonomy(data: dict) -> dict:
    if data["group"] not in TAXONOMY_GROUPS:
        raise HTTPException(status_code=400, detail="Grupo inválido")
    if await db.taxonomies.find_one({"group": data["group"], "key": data["key"]}):
        raise HTTPException(status_code=400, detail="Chave já existe neste grupo")
    try:
        result = await db.taxonomies.insert_one({**data, "created_at": now()})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Chave já existe neste grupo") from exc
    return ser(await db.taxonomies.find_one({"_id": result.inserted_id}))


async def update_taxonomy(tax_id: str, data: dict) -> dict:
    key = {"_id": oid(tax_id)}
    try:
        await db.taxonomies.update_one(key, {"$set": data})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Chave já existe neste grupo") from exc
    return ser(await db.taxonomies.find_one(key))


async def delete_taxonomy(tax_id: str) -> None:
    await db.taxonomies.delete_one({"_id": oid(tax_id)})


async def create_tag(name: str, color: str | None) -> dict:
    normalized_name = name.strip()
    slug = normalized_name.lower().replace(" ", "-")
    if await db.tags.find_one({"slug": slug}):
        raise HTTPException(status_code=400, detail="Tag já existe")
    try:
        result = await db.tags.insert_one({"name": normalized_name, "slug": slug, "color": color, "created_at": now()})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Tag já existe") from exc
    return ser(await db.tags.find_one({"_id": result.inserted_id}))


async def delete_tag(tag_id: str) -> None:
    await db.nodes.update_many({}, {"$pull": {"tag_ids": tag_id}})
    await db.tracks.update_many({}, {"$pull": {"tag_ids": tag_id}})
    await db.tags.delete_one({"_id": oid(tag_id)})


async def create_block_type(data: dict) -> dict:
    count = await db.block_types.count_documents({})
    if await db.block_types.find_one({"key": data["key"]}):
        raise HTTPException(status_code=400, detail="Tipo de bloco já existe")
    try:
        result = await db.block_types.insert_one({**data, "order": count, "created_at": now()})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Tipo de bloco já existe") from exc
    return ser(await db.block_types.find_one({"_id": result.inserted_id}))


async def update_block_type(block_type_id: str, data: dict) -> dict:
    key = {"_id": oid(block_type_id)}
    try:
        await db.block_types.update_one(key, {"$set": data})
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Tipo de bloco já existe") from exc
    return ser(await db.block_types.find_one(key))
