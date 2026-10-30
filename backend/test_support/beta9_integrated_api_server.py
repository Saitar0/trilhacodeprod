"""Full-stack Beta 9 preview composition over the isolated Beta 8.3 API."""

from __future__ import annotations

import os
import re

if os.environ.get("BETA9_FULLSTACK_TEST") != "1" or os.environ.get("BETA9_DISPOSABLE") != "1":
    raise RuntimeError("composição Beta 9 disponível somente no harness descartável explícito")

_preview_run_id = os.environ.get("BETA7_1_PREVIEW_RUN_ID", "")
if not re.fullmatch(r"[0-9a-f]{32}", _preview_run_id):
    raise RuntimeError("identidade da prévia Beta 9 ausente ou inválida")

# Importing the existing test-only API applies its Mongo credential and service
# boundary checks before the normal application is imported.
from test_support.beta8_3_api_server import app  # noqa: E402
from test_support.beta7_1_preview_router import router as preview_router  # noqa: E402
from test_support.beta7_2_assessment_router import router as assessment_router  # noqa: E402

app.state.beta7_1_preview_run_id = _preview_run_id
app.include_router(preview_router)
app.include_router(assessment_router)

_expected = {
    "/api/beta7-1/preview/batches/{batch_id}",
    "/api/beta7-2/assessment/batches/{batch_id}/project/rubric",
}
# FastAPI may keep included routers as lazy route containers until lifespan.
# Validate the concrete source routers here; the HTTP harness exercises the
# mounted paths after startup.
_declared = {
    route.path
    for source_router in (preview_router, assessment_router)
    for route in source_router.routes
    if isinstance(getattr(route, "path", None), str)
}
if not _expected.issubset(_declared):
    raise RuntimeError("contratos de rota da prévia Beta 9 estão incompletos")
