import json

from fastapi import APIRouter, Depends, HTTPException, Request

from import_payload import MAX_IMPORT_PAYLOAD_BYTES
from permissions import require
from schemas.versions import ImportReportOut
from services.imports import run_import

router = APIRouter(prefix="/api/import")


@router.post(
    "/track",
    response_model=ImportReportOut,
    response_model_exclude_unset=True,
    openapi_extra={"requestBody": {
        "required": True,
        "content": {"application/json": {"schema": {"type": "object"}}},
    }},
)
async def import_track(request: Request, dry_run: bool = True, user: dict = Depends(require("content.write"))):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_IMPORT_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Payload de importação excede o limite de 32 MiB")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_IMPORT_PAYLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Payload de importação excede o limite de 32 MiB")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise HTTPException(status_code=422, detail="JSON de importação malformado") from exc
    return await run_import(payload, dry_run, user)
