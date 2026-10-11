from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

import logging  # noqa: E402
import os  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

from core import client, db  # noqa: E402
from routes_auth import router as auth_router  # noqa: E402
from routes_content import router as content_router  # noqa: E402
from routes_progress import router as progress_router  # noqa: E402
from routes_taxonomy import router as taxonomy_router  # noqa: E402
from seed import run_seed  # noqa: E402
from integrity import migrate_legacy_snapshots  # noqa: E402
from routes_versions import resume_restore_jobs  # noqa: E402
from routes_import import router as import_router  # noqa: E402
from learning import router as learning_router  # noqa: E402
from routes_submissions import router as submissions_router  # noqa: E402
from routes_versions import router as versions_router  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(title="Trilha Code API")
for r in (auth_router, taxonomy_router, content_router, progress_router, learning_router, submissions_router,
          versions_router, import_router):
    app.include_router(r)


@app.get("/api/")
async def root():
    return {"app": "Trilha Code", "ok": True}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ["FRONTEND_URL"], "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.login_attempts.create_index("last", expireAfterSeconds=3600)
    await db.nodes.create_index([("track_id", 1), ("parent_id", 1), ("order", 1)])
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
    await db.submissions.create_index([("user_id", 1), ("block_id", 1), ("attempt", -1)], unique=True, name="one_attempt_number")
    await db.submissions.create_index([("status", 1), ("submitted_at", 1)])
    await db.notes.create_index([("user_id", 1), ("node_id", 1), ("block_id", 1)], unique=True)
    await db.reviews.create_index([("user_id", 1), ("status", 1), ("due_at", 1)])
    await db.reviews.create_index([("user_id", 1), ("node_id", 1), ("block_id", 1)], unique=True, name="one_pending_review",
                                  partialFilterExpression={"status": "pending"})
    await db.version_chunks.create_index([("version_id", 1), ("seq", 1)], unique=True)
    await db.restore_jobs.create_index("track_id", unique=True, name="one_running_restore",
                                       partialFilterExpression={"status": "running"})
    await db.migrations.create_index("key", unique=True)
    await migrate_legacy_snapshots()
    await resume_restore_jobs()
    await run_seed()


@app.on_event("shutdown")
async def shutdown():
    client.close()
