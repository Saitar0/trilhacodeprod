import json
import logging
import re
import sys
import time
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from settings import settings

if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    def _scrub_sentry_event(event, _hint):
        request = event.get("request")
        if request:
            request.pop("cookies", None)
            headers = request.get("headers") or {}
            request["headers"] = {
                key: value for key, value in headers.items()
                if key.lower() not in {"authorization", "cookie", "set-cookie", "proxy-authorization"}
            }
        return event

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or settings.env,
        release=settings.sentry_release,
        send_default_pii=False,
        integrations=[FastApiIntegration()],
        before_send=_scrub_sentry_event,
    )

from core import client, db  # noqa: E402
from learning import router as learning_router  # noqa: E402
from migrations import check_schema_version, current_version  # noqa: E402
from routes_auth import router as auth_router  # noqa: E402
from routes_content import router as content_router  # noqa: E402
from routes_import import router as import_router  # noqa: E402
from routes_progress import router as progress_router  # noqa: E402
from routes_submissions import router as submissions_router  # noqa: E402
from routes_taxonomy import router as taxonomy_router  # noqa: E402
from routes_versions import router as versions_router  # noqa: E402


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status": getattr(record, "status", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "user_id": getattr(record, "user_id", None),
            **({"exception": self.formatException(record.exc_info)} if record.exc_info else {}),
        }, ensure_ascii=False)


_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)
request_log = logging.getLogger("http.request")

app = FastAPI(
    title="Trilha Code API",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)


def _error_code(status_code: int) -> str:
    return {
        400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found",
        409: "conflict", 422: "validation_error",
    }.get(status_code, "request_error" if status_code < 500 else "internal_error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Requisição inválida"
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(status_code=exc.status_code, content={"error": {
        "code": _error_code(exc.status_code), "message": message,
        "request_id": request_id,
    }}, headers={**(exc.headers or {}), "X-Request-ID": request_id})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, _exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(status_code=422, content={"error": {
        "code": "validation_error", "message": "Dados da requisição inválidos",
        "request_id": request_id,
    }}, headers={"X-Request-ID": request_id})


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "")
    logging.getLogger(__name__).exception("Unhandled request exception", exc_info=exc, extra={
        "request_id": request_id,
        "method": request.method, "path": request.url.path,
    })
    if settings.sentry_dsn:
        sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=500, content={"error": {
        "code": "internal_error", "message": "Erro interno do servidor",
        "request_id": request_id,
    }}, headers={"X-Request-ID": request_id})


@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    request_id = supplied if re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", supplied) else str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    request_log.info("HTTP request", extra={
        "request_id": request_id, "method": request.method, "path": request.url.path,
        "status": response.status_code, "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "user_id": getattr(request.state, "user_id", None),
    })
    return response


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/ready")
async def ready():
    try:
        await db.command("ping")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Banco indisponível") from exc
    version = await current_version()
    if version < 2:
        raise HTTPException(status_code=503, detail="Banco sem as migrações esperadas")
    return {"ok": True, "migration_version": version}
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
    expose_headers=["X-Request-ID"],
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
