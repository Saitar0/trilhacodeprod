"""Explicitly composed ASGI app for the attested Beta 7.1 test runner.

This module checks the disposable MongoDB identity before importing route
modules. It does not import ``server:app`` or mount the operational router set.
Only selected handlers are re-registered directly, avoiding broad router
exposure and FastAPI's version-dependent lazy ``include_router`` container.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware

from test_support.beta7_1_internal_target import connect_internal_verified_target

_target, _ownership_client = connect_internal_verified_target(
    os.environ,
    lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
)
_ownership_client.close()

# Route modules and database-backed dependencies are imported only after the
# container, network, credentials and ownership-marker gate has passed.
from routes_auth import router as _auth_router  # noqa: E402
from routes_content import router as _content_router  # noqa: E402
from test_support.beta7_1_preview_router import router as _preview_router  # noqa: E402

app = FastAPI(title="Trilha Code Beta 7.1 isolated preview", docs_url=None, openapi_url=None)
app.state.beta7_1_preview_run_id = _target.run_id
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Idempotency-Key"],
)


def _copy_selected_route(source: APIRouter, path: str, method: str) -> None:
    method = method.upper()
    matches = [
        route for route in source.routes
        if isinstance(route, APIRoute) and route.path == path and method in route.methods
    ]
    if len(matches) != 1:
        candidates = sorted(
            getattr(route, "path", "<sem-path>")
            for route in source.routes
            if "node" in getattr(route, "path", "") or "track" in getattr(route, "path", "")
        )
        raise RuntimeError(
            f"Rota permitida ausente ou ambígua na composição Beta 7.1: {path}; "
            f"matches={len(matches)}; candidatos={candidates!r}"
        )
    route = matches[0]
    app.add_api_route(
        path,
        route.endpoint,
        methods=[method],
        response_model=route.response_model,
        status_code=route.status_code,
        response_model_include=route.response_model_include,
        response_model_exclude=route.response_model_exclude,
        response_model_by_alias=route.response_model_by_alias,
        response_model_exclude_unset=route.response_model_exclude_unset,
        response_model_exclude_defaults=route.response_model_exclude_defaults,
        response_model_exclude_none=route.response_model_exclude_none,
        response_class=route.response_class,
        name=route.name,
        dependencies=route.dependencies,
        deprecated=route.deprecated,
        include_in_schema=False,
        response_description=route.response_description,
        openapi_extra=route.openapi_extra,
    )


# Authentication/session endpoints and two protected readers are the only
# operational handlers reachable in this test app. No import, publish, editor,
# content-write, or account-provisioning routes are mounted.
for _path, _method in (
    ("/api/auth/login", "POST"),
    ("/api/auth/logout", "POST"),
    ("/api/auth/refresh", "POST"),
    ("/api/auth/me", "GET"),
):
    _copy_selected_route(_auth_router, _path, _method)

for _path in ("/api/tracks/{track_id}/tree", "/api/nodes/{node_id}"):
    _copy_selected_route(_content_router, _path, "GET")

app.include_router(_preview_router)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/api/", include_in_schema=False)
async def root() -> dict[str, object]:
    return {"app": "Trilha Code Beta 7.1 isolated preview", "ok": True}


_expected_paths = {
    "/api/auth/login", "/api/auth/logout", "/api/auth/refresh", "/api/auth/me",
    "/api/tracks/{track_id}/tree", "/api/nodes/{node_id}", "/health", "/api/",
}
_registered_paths = {
    route.path for route in app.router.routes if isinstance(route, APIRoute)
}
if not _expected_paths.issubset(_registered_paths):
    raise RuntimeError(
        "Composição Beta 7.1 incompleta; "
        f"faltando={sorted(_expected_paths - _registered_paths)!r}"
    )
