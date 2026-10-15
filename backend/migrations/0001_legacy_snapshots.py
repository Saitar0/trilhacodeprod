# ruff: noqa: EXE002
from integrity import migrate_legacy_snapshots


async def up() -> None:
    await migrate_legacy_snapshots()
