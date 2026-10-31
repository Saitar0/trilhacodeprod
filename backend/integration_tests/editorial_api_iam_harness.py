"""Test-only FastAPI harness for the C10 editorial boundary.

The app is constructed on demand by tests. It does not import the active
server, database, authentication module, or any production route.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bson import ObjectId
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response

from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter
from curriculum_contract.experimental_editorial_api_contract import (
    ExperimentalBlockPatch,
    TestCapabilityAuthority,
    derive_operation_id,
    etag_for_revision,
    map_protocol_error,
    minimal_intent_payload,
    parse_expected_revision,
    stable_receipt,
    validate_idempotency_key,
)


def load_real_role_permission_dependency():
    """Load the real role checker while stubbing only its auth dependency."""

    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    security_stub = types.ModuleType("security")

    async def synthetic_current_user(request: Request) -> dict[str, Any]:
        return request.app.state.principal

    security_stub.current_user = synthetic_current_user
    old_security = sys.modules.get("security")
    sys.modules["security"] = security_stub
    try:
        source = backend_root / "permissions.py"
        spec = importlib.util.spec_from_file_location("_c10_real_permissions", source)
        if spec is None or spec.loader is None:
            raise RuntimeError("unable to load versioned role permission code")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old_security is None:
            sys.modules.pop("security", None)
        else:
            sys.modules["security"] = old_security


def build_editorial_api_test_app(
    *,
    database: Any,
    adapter: AsyncEditorialRevisionAdapter,
    capability_authority: TestCapabilityAuthority,
    operation_hmac_key: bytes,
    content_hmac_key: bytes,
    principal: dict[str, Any],
):
    """Construct a versioned candidate API used only by test clients."""

    permissions = load_real_role_permission_dependency()
    app = FastAPI()
    app.state.principal = principal

    @app.put("/api/v2/tracks/{track_id}/blocks/{block_id}")
    async def update_block_candidate(
        track_id: str,
        block_id: str,
        body: ExperimentalBlockPatch,
        response: Response,
        user: dict = Depends(permissions.require("content.write")),
        if_match: str | None = Header(default=None, alias="If-Match"),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        expected_revision = parse_expected_revision(if_match)
        stable_key = validate_idempotency_key(idempotency_key)
        changes = body.changes()
        try:
            object_id = ObjectId(block_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="ID do bloco inválido") from exc
        actor_id = user.get("id") or user.get("_id")
        if not isinstance(actor_id, str) or not actor_id:
            raise HTTPException(status_code=403, detail="Ator inválido")
        operation_kind = "block.update"
        operation_id = derive_operation_id(
            actor_id=actor_id,
            track_id=track_id,
            operation_kind=operation_kind,
            idempotency_key=stable_key,
            key=operation_hmac_key,
        )
        try:
            capability = capability_authority.issue(
                actor=user,
                track_id=track_id,
                operation_kind=operation_kind,
                operation_id=operation_id,
            )
            capability_authority.validate(
                capability,
                track_id=track_id,
                actor_id=actor_id,
                operation_kind=operation_kind,
                operation_id=operation_id,
            )
            intent = minimal_intent_payload(
                block_id=block_id, changes=changes, fingerprint_key=content_hmac_key
            )
            prepared = await adapter.prepare(
                track_id=track_id,
                credential=capability.credential,
                operation_id=capability.operation_id,
                expected_revision=expected_revision,
                fencing_token=capability.fence_token,
                payload=intent,
            )
            operation_time = datetime.now(timezone.utc)

            async def participant(session: Any, receipt: Any) -> None:
                mutation = dict(changes)
                mutation["updated_at"] = operation_time
                result = await database["content_blocks"].update_one(
                    {"_id": object_id, "track_id": track_id},
                    {"$set": mutation},
                    session=session,
                )
                if result.matched_count != 1:
                    raise HTTPException(status_code=404, detail="Bloco não encontrado")
                actor_name = user.get("name") if isinstance(user.get("name"), str) else ""
                await database["edit_history"].insert_one(
                    {
                        "track_id": track_id,
                        "operation_id": receipt.operation_id,
                        "revision": receipt.revision,
                        "parent_revision": receipt.parent_revision,
                        "entity": "block",
                        "entity_id": block_id,
                        "action": "updated",
                        "summary": "editorial block update",
                        "user_id": actor_id,
                        "user_name": actor_name,
                        "changed_fields": sorted(changes),
                        "at": operation_time,
                    },
                    session=session,
                )

            receipt = await adapter.commit(prepared, capability.credential, participant=participant)
        except HTTPException:
            raise
        except Exception as exc:
            raise map_protocol_error(exc) from None
        response.headers["ETag"] = etag_for_revision(receipt.revision)
        response.headers["Idempotency-Replayed"] = "true" if receipt.replayed else "false"
        return stable_receipt(receipt)

    return app
