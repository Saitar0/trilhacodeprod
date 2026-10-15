# ruff: noqa: EXE002
"""Versioned MongoDB data migrations."""

import importlib
import logging
import secrets
from datetime import timedelta

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core import db, now

log = logging.getLogger(__name__)
EXPECTED_MIGRATION_VERSION = 2
MIGRATIONS = ("0001_legacy_snapshots", "0002_block_submission_capabilities")
LOCK_ID = "schema-migrations"


async def current_version() -> int:
    rows = await db.migrations.find({"version": {"$exists": True}}).to_list(100)
    return max((row["version"] for row in rows), default=0)


async def check_schema_version() -> bool:
    version = await current_version()
    return version >= EXPECTED_MIGRATION_VERSION


async def migrate() -> int:
    token = secrets.token_hex(16)
    timestamp = now()
    try:
        lock = await db.migrations.find_one_and_update(
            {
                "_id": LOCK_ID,
                "$or": [{"lease_until": {"$lt": timestamp}}, {"lease_until": {"$exists": False}}],
            },
            {"$set": {"owner": token, "lease_until": timestamp + timedelta(minutes=15)}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError as exc:
        raise RuntimeError("Outra instância está executando migrações") from exc
    if not lock or lock.get("owner") != token:
        raise RuntimeError("Não foi possível obter a trava de migrações")
    try:
        for version, name in enumerate(MIGRATIONS, start=1):
            key = name
            if await db.migrations.find_one({"key": key}):
                continue
            migration = importlib.import_module(f"migrations.{name}")
            await migration.up()
            await db.migrations.insert_one({"key": key, "version": version, "applied_at": now()})
            log.info("Migração aplicada: %s", key)
        return EXPECTED_MIGRATION_VERSION
    finally:
        await db.migrations.delete_one({"_id": LOCK_ID, "owner": token})
