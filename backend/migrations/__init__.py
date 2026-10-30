# ruff: noqa: EXE002
"""Versioned MongoDB data migrations."""

import asyncio
import importlib
import logging
import secrets
from datetime import timedelta

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core_utils import now
from database import db

log = logging.getLogger(__name__)
EXPECTED_MIGRATION_VERSION = 3
MIGRATIONS = (
    "0001_legacy_snapshots",
    "0002_block_submission_capabilities",
    "0003_quiz_attempts",
)
LEGACY_MIGRATION_MARKERS = {"block_types_submission_v1"}
LOCK_ID = "schema-migrations"
MIGRATION_LEASE = timedelta(minutes=15)
MIGRATION_HEARTBEAT_SECONDS = 60


async def _migration_ledger() -> list[dict] | None:
    rows = await db.migrations.find({
        "$or": [{"key": {"$exists": True}}, {"version": {"$exists": True}}],
    }).to_list(100)
    markers = [row for row in rows if "version" not in row]
    versioned = [row for row in rows if "version" in row]
    if (len(markers) > len(LEGACY_MIGRATION_MARKERS)
            or any(row.get("key") not in LEGACY_MIGRATION_MARKERS for row in markers)):
        return None
    if (len(versioned) > len(MIGRATIONS)
            or any(type(row.get("version")) is not int for row in versioned)):
        return None
    ordered = sorted(versioned, key=lambda row: row["version"])
    for index, row in enumerate(ordered):
        if row.get("key") != MIGRATIONS[index] or row.get("version") != index + 1:
            return None
    return ordered


async def current_version() -> int:
    rows = await _migration_ledger()
    return len(rows) if rows is not None else 0


async def check_schema_version() -> bool:
    version = await current_version()
    return version == EXPECTED_MIGRATION_VERSION


async def _heartbeat_migration(token: str) -> None:
    while True:
        await asyncio.sleep(MIGRATION_HEARTBEAT_SECONDS)
        result = await db.migrations.update_one(
            {"_id": LOCK_ID, "owner": token},
            {"$set": {"lease_until": now() + MIGRATION_LEASE, "heartbeat_at": now()}},
        )
        if not result.matched_count:
            return


async def migrate() -> int:
    token = secrets.token_hex(16)
    timestamp = now()
    try:
        lock = await db.migrations.find_one_and_update(
            {
                "_id": LOCK_ID,
                "$or": [{"lease_until": {"$lt": timestamp}}, {"lease_until": {"$exists": False}}],
            },
            {"$set": {"owner": token, "lease_until": timestamp + MIGRATION_LEASE}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError as exc:
        raise RuntimeError("Outra instância está executando migrações") from exc
    if not lock or lock.get("owner") != token:
        raise RuntimeError("Não foi possível obter a trava de migrações")
    heartbeat = asyncio.create_task(_heartbeat_migration(token))
    try:
        ledger = await _migration_ledger()
        if ledger is None:
            raise RuntimeError("Ledger de migrações desconhecido ou incompleto; intervenção necessária")
        for version, name in enumerate(MIGRATIONS[len(ledger):], start=len(ledger) + 1):
            migration = importlib.import_module(f"migrations.{name}")
            await migration.up()
            await db.migrations.insert_one({"key": name, "version": version, "applied_at": now()})
            log.info("Migração aplicada: %s", name)
            ledger.append({"key": name, "version": version})
        if heartbeat.done():
            raise RuntimeError("A trava de migrações foi perdida antes da conclusão")
        return EXPECTED_MIGRATION_VERSION
    finally:
        heartbeat.cancel()
        await asyncio.gather(heartbeat, return_exceptions=True)
        await db.migrations.delete_one({"_id": LOCK_ID, "owner": token})
