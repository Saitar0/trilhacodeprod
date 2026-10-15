import logging  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from settings import settings  # noqa: E402

from core import client, db  # noqa: E402
from routes_auth import router as auth_router  # noqa: E402
from routes_content import router as content_router  # noqa: E402
from routes_progress import router as progress_router  # noqa: E402
from routes_taxonomy import router as taxonomy_router  # noqa: E402
from migrations import check_schema_version  # noqa: E402
from routes_import import router as import_router  # noqa: E402
from learning import router as learning_router  # noqa: E402
from routes_submissions import router as submissions_router  # noqa: E402
from routes_versions import router as versions_router  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Trilha Code API",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)
for r in (auth_router, taxonomy_router, content_router, progress_router, learning_router, submissions_router,
          versions_router, import_router):
    app.include_router(r)


@app.get("/api/")
async def root():
    return {"app": "Trilha Code", "ok": True}


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.effective_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
async def startup():
    if not await check_schema_version():
        message = "Banco sem todas as migrações; execute python -m backend.manage migrate"
        if settings.is_production:
            raise RuntimeError(message)
        logging.getLogger(__name__).warning(message)


@app.on_event("shutdown")
async def shutdown():
    client.close()
