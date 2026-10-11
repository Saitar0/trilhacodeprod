from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core import (DEFAULT_HIERARCHY, DEFAULT_LABELS, PROGRESS_STATUSES, ROLES, STATUSES, current_user, db, now,
                  oid, require, ser)

router = APIRouter(prefix="/api")

TAXONOMY_GROUPS = ["pedagogical_type", "requirement", "depth", "relation_type"]


class TaxonomyIn(BaseModel):
    group: str
    key: str
    label: str
    description: str = ""
    color: str = "slate"
    order: float = 0


class TaxonomyUpdate(BaseModel):
    label: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    order: Optional[float] = None


class TagIn(BaseModel):
    name: str
    color: str = "slate"


class BlockTypeIn(BaseModel):
    key: str
    label: str
    category: str = "recurso"
    icon: str = "Square"
    description: str = ""
    fields: List[dict] = []
    capabilities: List[str] = []
    enabled: bool = True


class BlockTypeUpdate(BaseModel):
    label: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[dict]] = None
    capabilities: Optional[List[str]] = None
    enabled: Optional[bool] = None


@router.get("/meta")
async def meta(_: dict = Depends(current_user)):
    tax = await db.taxonomies.find({}).sort("order", 1).to_list(1000)
    grouped = {g: [] for g in TAXONOMY_GROUPS}
    for t in tax:
        grouped.setdefault(t["group"], []).append(ser(t))
    block_types = await db.block_types.find({}).sort("order", 1).to_list(500)
    tags = await db.tags.find({}).sort("name", 1).to_list(1000)
    return {
        "taxonomies": grouped,
        "block_types": [ser(b) for b in block_types],
        "tags": [ser(t) for t in tags],
        "statuses": STATUSES,
        "progress_statuses": PROGRESS_STATUSES,
        "roles": ROLES,
        "default_hierarchy": DEFAULT_HIERARCHY,
        "default_labels": DEFAULT_LABELS,
    }


@router.post("/taxonomies")
async def create_taxonomy(body: TaxonomyIn, _: dict = Depends(require("taxonomy.manage"))):
    if body.group not in TAXONOMY_GROUPS:
        raise HTTPException(status_code=400, detail="Grupo inválido")
    if await db.taxonomies.find_one({"group": body.group, "key": body.key}):
        raise HTTPException(status_code=400, detail="Chave já existe neste grupo")
    doc = {**body.model_dump(), "created_at": now()}
    res = await db.taxonomies.insert_one(doc)
    return ser(await db.taxonomies.find_one({"_id": res.inserted_id}))


@router.put("/taxonomies/{tax_id}")
async def update_taxonomy(tax_id: str, body: TaxonomyUpdate, _: dict = Depends(require("taxonomy.manage"))):
    await db.taxonomies.update_one({"_id": oid(tax_id)}, {"$set": body.model_dump(exclude_unset=True)})
    return ser(await db.taxonomies.find_one({"_id": oid(tax_id)}))


@router.delete("/taxonomies/{tax_id}")
async def delete_taxonomy(tax_id: str, _: dict = Depends(require("taxonomy.manage"))):
    await db.taxonomies.delete_one({"_id": oid(tax_id)})
    return {"ok": True}


@router.post("/tags")
async def create_tag(body: TagIn, _: dict = Depends(require("content.write"))):
    slug = body.name.strip().lower().replace(" ", "-")
    if await db.tags.find_one({"slug": slug}):
        raise HTTPException(status_code=400, detail="Tag já existe")
    res = await db.tags.insert_one({"name": body.name.strip(), "slug": slug, "color": body.color, "created_at": now()})
    return ser(await db.tags.find_one({"_id": res.inserted_id}))


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str, _: dict = Depends(require("content.write"))):
    await db.tags.delete_one({"_id": oid(tag_id)})
    await db.nodes.update_many({}, {"$pull": {"tag_ids": tag_id}})
    await db.tracks.update_many({}, {"$pull": {"tag_ids": tag_id}})
    return {"ok": True}


@router.post("/block-types")
async def create_block_type(body: BlockTypeIn, _: dict = Depends(require("taxonomy.manage"))):
    if await db.block_types.find_one({"key": body.key}):
        raise HTTPException(status_code=400, detail="Tipo de bloco já existe")
    count = await db.block_types.count_documents({})
    res = await db.block_types.insert_one({**body.model_dump(), "order": count, "created_at": now()})
    return ser(await db.block_types.find_one({"_id": res.inserted_id}))


@router.put("/block-types/{bt_id}")
async def update_block_type(bt_id: str, body: BlockTypeUpdate, _: dict = Depends(require("taxonomy.manage"))):
    await db.block_types.update_one({"_id": oid(bt_id)}, {"$set": body.model_dump(exclude_unset=True)})
    return ser(await db.block_types.find_one({"_id": oid(bt_id)}))
