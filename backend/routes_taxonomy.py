from fastapi import APIRouter, Depends

from permissions import require
from schemas.content import OkOut
from schemas.taxonomy import (
    BlockTypeIn,
    BlockTypeUpdate,
    MetaOut,
    TagIn,
    TaxonomyIn,
    TaxonomyOut,
    TaxonomyUpdate,
)
from security import current_user
from services.taxonomy import (
    create_block_type as create_block_type_service,
)
from services.taxonomy import (
    create_tag as create_tag_service,
)
from services.taxonomy import (
    create_taxonomy as create_taxonomy_service,
)
from services.taxonomy import (
    delete_tag as delete_tag_service,
)
from services.taxonomy import (
    delete_taxonomy as delete_taxonomy_service,
)
from services.taxonomy import (
    get_metadata,
)
from services.taxonomy import (
    update_block_type as update_block_type_service,
)
from services.taxonomy import (
    update_taxonomy as update_taxonomy_service,
)

router = APIRouter(prefix="/api")

@router.get("/meta", response_model=MetaOut, response_model_exclude_unset=True)
async def meta(_: dict = Depends(current_user)):
    return await get_metadata()


@router.post("/taxonomies", response_model=TaxonomyOut, response_model_exclude_unset=True)
async def create_taxonomy(body: TaxonomyIn, _: dict = Depends(require("taxonomy.manage"))):
    return await create_taxonomy_service(body.model_dump())


@router.put("/taxonomies/{tax_id}", response_model=TaxonomyOut, response_model_exclude_unset=True)
async def update_taxonomy(tax_id: str, body: TaxonomyUpdate, _: dict = Depends(require("taxonomy.manage"))):
    return await update_taxonomy_service(tax_id, body.model_dump(exclude_unset=True))


@router.delete("/taxonomies/{tax_id}", response_model=OkOut)
async def delete_taxonomy(tax_id: str, _: dict = Depends(require("taxonomy.manage"))):
    await delete_taxonomy_service(tax_id)
    return {"ok": True}


@router.post("/tags", response_model=TaxonomyOut, response_model_exclude_unset=True)
async def create_tag(body: TagIn, _: dict = Depends(require("content.write"))):
    return await create_tag_service(body.name, body.color)


@router.delete("/tags/{tag_id}", response_model=OkOut)
async def delete_tag(tag_id: str, _: dict = Depends(require("content.write"))):
    await delete_tag_service(tag_id)
    return {"ok": True}


@router.post("/block-types", response_model=TaxonomyOut, response_model_exclude_unset=True)
async def create_block_type(body: BlockTypeIn, _: dict = Depends(require("taxonomy.manage"))):
    return await create_block_type_service(body.model_dump())


@router.put("/block-types/{bt_id}", response_model=TaxonomyOut, response_model_exclude_unset=True)
async def update_block_type(bt_id: str, body: BlockTypeUpdate, _: dict = Depends(require("taxonomy.manage"))):
    return await update_block_type_service(bt_id, body.model_dump(exclude_unset=True))
