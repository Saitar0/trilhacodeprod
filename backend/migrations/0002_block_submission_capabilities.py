# ruff: noqa: EXE002
from core import db, now
from seed import BLOCK_TYPES, SUBMITTABLE


async def up() -> None:
    for key, _label, _category, _icon, fields in BLOCK_TYPES:
        if key not in SUBMITTABLE:
            continue
        existing = await db.block_types.find_one({"key": key})
        if not existing:
            continue
        names = {field["name"] for field in existing.get("fields", [])}
        missing = [field for field in fields if field["name"] not in names]
        update = {"$addToSet": {"capabilities": "submission"}}
        if missing:
            update["$push"] = {"fields": {"$each": missing}}
        await db.block_types.update_one({"_id": existing["_id"]}, update)
    await db.migrations.update_one(
        {"key": "block_types_submission_v1"},
        {"$setOnInsert": {"applied_at": now()}},
        upsert=True,
    )
