"""Create indexes required by immutable quiz versions and attempt history."""

from indexes import ensure_quiz_indexes


async def up() -> None:
    await ensure_quiz_indexes()
