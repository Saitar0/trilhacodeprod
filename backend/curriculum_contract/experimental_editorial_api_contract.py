"""Isolated HTTP/API policy helpers for the experimental C10 boundary.

This module is intentionally not imported by active routes. Capabilities are
server-side test objects; they are neither credentials accepted from a client
nor a replacement for application authentication or authorization.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from .editorial_revision_protocol import (
    FenceAuthorityError,
    FencingRejected,
    IdempotencyConflict,
    InvalidPreparation,
    InvalidProposal,
    OperationAborted,
    ProposalValidationError,
    RevisionConflict,
    RevisionReceipt,
    WriterAuthorizationError,
    WriterCredential,
)
from .mongodb_editorial_revision_adapter import CommitOutcomeUnknown

_ETAG = re.compile(r'^"editorial-rev-(0|[1-9][0-9]{0,18})"$')
_IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9._~-]{16,128}$")
_EDITABLE_FIELDS = frozenset({"title", "data", "status"})
_STATUS_VALUES = frozenset({"draft", "published", "archived"})


class ExperimentalBlockPatch(BaseModel):
    """Strict subset matching the current BlockUpdate fields and null behavior."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    data: dict[str, Any] | None = None
    status: str | None = None

    def changes(self) -> dict[str, Any]:
        changes = self.model_dump(exclude_unset=True)
        status = changes.get("status")
        if status is not None and status not in _STATUS_VALUES:
            raise HTTPException(status_code=400, detail="Status inválido")
        return changes


def parse_expected_revision(if_match: str | None) -> int:
    if if_match is None:
        raise HTTPException(status_code=428, detail="If-Match obrigatório")
    match = _ETAG.fullmatch(if_match.strip())
    if match is None:
        raise HTTPException(status_code=400, detail="If-Match inválido")
    revision = int(match.group(1))
    if revision > (1 << 63) - 1:
        raise HTTPException(status_code=400, detail="If-Match inválido")
    return revision


def validate_idempotency_key(value: str | None) -> str:
    if value is None:
        raise HTTPException(status_code=400, detail="Idempotency-Key obrigatório")
    if not _IDEMPOTENCY_KEY.fullmatch(value):
        raise HTTPException(status_code=400, detail="Idempotency-Key inválido")
    return value


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise HTTPException(status_code=422, detail="Corpo inválido") from exc


def derive_operation_id(
    *,
    actor_id: str,
    track_id: str,
    operation_kind: str,
    idempotency_key: str,
    key: bytes,
) -> str:
    """Return a non-reversible, scoped operation identity; never expose the key."""

    scope = [actor_id, track_id, operation_kind, idempotency_key]
    digest = hmac.new(key, _canonical_json({"scope": scope}), hashlib.sha256).hexdigest()
    return f"http_{digest}"


def minimal_intent_payload(
    *,
    block_id: str,
    changes: Mapping[str, Any],
    fingerprint_key: bytes,
) -> dict[str, Any]:
    """Commit private fields via keyed digest without storing their values."""

    if not changes or any(field_name not in _EDITABLE_FIELDS for field_name in changes):
        raise HTTPException(status_code=422, detail="Alteração inválida")
    digest = hmac.new(fingerprint_key, _canonical_json(changes), hashlib.sha256).hexdigest()
    return {
        "operation_kind": "block.update",
        "payload_schema_version": 1,
        "block_ref": block_id,
        "changed_fields": sorted(changes),
        "change_hmac_sha256": digest,
    }


@dataclass(frozen=True, slots=True, repr=False)
class EditorialCapability:
    """Opaque server-created capability; not accepted from HTTP input."""

    actor_id: str
    track_id: str
    operation_kind: str
    credential: WriterCredential = field(repr=False)
    fence_token: int = field(repr=False)
    operation_id: str = field(repr=False)
    _issuer_seal: object = field(repr=False, compare=False)


class TestCapabilityAuthority:
    """Trusted test boundary. Its track policy is synthetic, not production IAM."""

    def __init__(
        self,
        *,
        credentials: Mapping[str, WriterCredential],
        fences: Mapping[str, int],
        allowed_scopes: set[tuple[str, str, str]],
    ) -> None:
        self._credentials = dict(credentials)
        self._fences = dict(fences)
        self._allowed_scopes = set(allowed_scopes)
        self._seal = object()

    def issue(
        self,
        *,
        actor: Mapping[str, Any],
        track_id: str,
        operation_kind: str,
        operation_id: str,
    ) -> EditorialCapability:
        actor_id = actor.get("id") or actor.get("_id")
        if not isinstance(actor_id, str) or not actor_id:
            raise HTTPException(status_code=403, detail="Escopo editorial negado")
        if (actor_id, track_id, operation_kind) not in self._allowed_scopes:
            raise HTTPException(status_code=403, detail="Escopo editorial negado")
        credential = self._credentials.get(track_id)
        fence = self._fences.get(track_id)
        if credential is None or fence is None:
            raise HTTPException(status_code=403, detail="Escopo editorial negado")
        if credential.track_id != track_id:
            raise HTTPException(status_code=403, detail="Escopo editorial negado")
        return EditorialCapability(
            actor_id=actor_id,
            track_id=track_id,
            operation_kind=operation_kind,
            credential=credential,
            fence_token=fence,
            operation_id=operation_id,
            _issuer_seal=self._seal,
        )

    def validate(
        self,
        capability: EditorialCapability,
        *,
        track_id: str,
        actor_id: str,
        operation_kind: str,
        operation_id: str,
    ) -> None:
        if (
            not isinstance(capability, EditorialCapability)
            or capability._issuer_seal is not self._seal
            or capability.track_id != track_id
            or capability.actor_id != actor_id
            or capability.operation_kind != operation_kind
            or capability.operation_id != operation_id
        ):
            raise HTTPException(status_code=403, detail="Capability inválida")


def map_protocol_error(error: Exception) -> HTTPException:
    """Map protocol failures to sanitized experimental HTTP errors."""

    if isinstance(error, RevisionConflict):
        return HTTPException(status_code=412, detail="Revisão desatualizada")
    if isinstance(error, FencingRejected):
        return HTTPException(status_code=409, detail="Escritor editorial obsoleto")
    if isinstance(error, IdempotencyConflict):
        return HTTPException(status_code=409, detail="Chave de idempotência reutilizada")
    if isinstance(error, (WriterAuthorizationError, FenceAuthorityError)):
        return HTTPException(status_code=403, detail="Operação editorial não autorizada")
    if isinstance(error, InvalidProposal):
        return HTTPException(status_code=422, detail="Proposta editorial inválida")
    if isinstance(error, (InvalidPreparation, OperationAborted, ProposalValidationError)):
        return HTTPException(status_code=409, detail="Operação editorial não disponível")
    if isinstance(error, CommitOutcomeUnknown):
        return HTTPException(
            status_code=503,
            detail="Confirmação indeterminada; repita com a mesma chave de idempotência",
            headers={"Retry-After": "1"},
        )
    return HTTPException(status_code=500, detail="Falha interna")


def stable_receipt(receipt: RevisionReceipt) -> dict[str, int]:
    """Return only a stable, non-content receipt suitable for a future API."""

    return {"revision": receipt.revision, "parent_revision": receipt.parent_revision}


def etag_for_revision(revision: int) -> str:
    return f'"editorial-rev-{revision}"'
