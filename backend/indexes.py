# ruff: noqa: EXE002
"""Idempotent MongoDB index setup, invoked by the management CLI."""

from core import db


async def ensure_indexes() -> None:
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.login_attempts.create_index("last", expireAfterSeconds=3600)
    await db.nodes.create_index([("track_id", 1), ("parent_id", 1), ("order", 1)])
    await db.nodes.create_index([("title", "text"), ("summary", "text")], name="node_search_text")
    await db.content_blocks.create_index([("node_id", 1), ("order", 1)])
    await db.relations.create_index([("track_id", 1)])
    await db.progress.create_index([("user_id", 1), ("track_id", 1)])
    await db.progress.create_index([("user_id", 1), ("node_id", 1), ("block_id", 1)], unique=True)
    await db.learning_events.create_index([("user_id", 1), ("at", -1)])
    await db.edit_history.create_index([("track_id", 1), ("at", -1)])
    await db.taxonomies.create_index([("group", 1), ("key", 1)], unique=True)
    await db.block_types.create_index("key", unique=True)
    if "user_id_1_block_id_1_attempt_-1" in await db.submissions.index_information():
        await db.submissions.drop_index("user_id_1_block_id_1_attempt_-1")
    await db.submissions.create_index(
        [("user_id", 1), ("block_id", 1), ("attempt", -1)], unique=True, name="one_attempt_number"
    )
    await db.submissions.create_index([("status", 1), ("submitted_at", 1)])
    await db.notes.create_index([("user_id", 1), ("node_id", 1), ("block_id", 1)], unique=True)
    await db.reviews.create_index([("user_id", 1), ("status", 1), ("due_at", 1)])
    await db.reviews.create_index(
        [("user_id", 1), ("node_id", 1), ("block_id", 1)],
        unique=True,
        name="one_pending_review",
        partialFilterExpression={"status": "pending"},
    )
    await db.version_chunks.create_index([("version_id", 1), ("seq", 1)], unique=True)
    await db.restore_jobs.create_index(
        "track_id", unique=True, name="one_running_restore", partialFilterExpression={"status": "running"}
    )
    await db.migrations.create_index("key", unique=True)
