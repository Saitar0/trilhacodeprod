"""Narrow, authenticated Beta 8.3 API-to-authority command protocol.

The protocol is test-harness-only. It carries no MongoDB command, collection
name, or self-asserted authorization decision. The API gateway signs an actor
assertion only after the regular access-token dependency has authenticated it;
the authority then rechecks the persisted user, session, C12 grant, and state.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from curriculum_contract.beta_staging_contract import StagingPackage

_ACTOR_ID = re.compile(r"^[0-9a-fA-F]{24}$")
_OBJECT_ID = re.compile(r"^[0-9a-fA-F]{24}$")
_OPERATION_ID = re.compile(r"^http_[0-9a-f]{64}$")
_SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
_ALLOWED_BLOCK_FIELDS = {"title", "data"}
_ALLOWED_NODE_FIELDS = {"title", "summary", "description", "guidance"}


class ActorAssertion(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    actor_id: str
    session_id: str = Field(repr=False)
    token_version: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_identity(self) -> ActorAssertion:
        if not _ACTOR_ID.fullmatch(self.actor_id) or not _SESSION_ID.fullmatch(self.session_id):
            raise ValueError("contexto de identidade inválido")
        return self


class EditorialMutationCommand(BaseModel):
    """Only the three reviewed Beta 8.2 mutations are expressible."""

    model_config = ConfigDict(extra="forbid", strict=True)

    operation: Literal["block.update", "block.create", "node.update"]
    actor: ActorAssertion
    operation_id: str
    expected_revision: int = Field(ge=0)
    block_id: str | None = None
    node_id: str | None = None
    changes: dict[str, Any] | None = None
    block: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_operation_shape(self) -> EditorialMutationCommand:
        if not _OPERATION_ID.fullmatch(self.operation_id):
            raise ValueError("identidade da operação inválida")

        if self.operation == "block.update":
            if (
                not isinstance(self.block_id, str)
                or not _OBJECT_ID.fullmatch(self.block_id)
                or self.node_id is not None
                or self.block is not None
                or not isinstance(self.changes, dict)
                or not self.changes
                or set(self.changes) - _ALLOWED_BLOCK_FIELDS
            ):
                raise ValueError("comando de atualização de bloco inválido")
            _validate_json_payload(self.changes)
        elif self.operation == "block.create":
            if (
                not isinstance(self.node_id, str)
                or not _OBJECT_ID.fullmatch(self.node_id)
                or self.block_id is None
                or self.changes is not None
                or not isinstance(self.block, dict)
                or set(self.block) != {"type", "title", "data", "status"}
                or self.block.get("status") != "draft"
                or not isinstance(self.block.get("type"), str)
                or not isinstance(self.block.get("title"), str)
                or not isinstance(self.block.get("data"), dict)
            ):
                raise ValueError("comando de criação de bloco inválido")
            if not _OBJECT_ID.fullmatch(self.block_id):
                raise ValueError("identidade de bloco inválida")
            expected_block_id = hashlib.sha256(self.operation_id.encode("utf-8")).digest()[:12].hex()
            if self.block_id.lower() != expected_block_id:
                raise ValueError("identidade do bloco não corresponde à operação")
            _validate_json_payload(self.block)
        else:
            if (
                not isinstance(self.node_id, str)
                or not _OBJECT_ID.fullmatch(self.node_id)
                or self.block_id is not None
                or self.block is not None
                or not isinstance(self.changes, dict)
                or not self.changes
                or set(self.changes) - _ALLOWED_NODE_FIELDS
                or any(not isinstance(value, str) for value in self.changes.values())
            ):
                raise ValueError("comando de atualização de unidade inválido")
            _validate_json_payload(self.changes)
        return self


class EditorialMutationReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    revision: int = Field(ge=0)
    parent_revision: int = Field(ge=0)
    fencing_token: int = Field(ge=0)
    replayed: bool


class StagingTransitionCommand(BaseModel):
    """A prepared, synthetic Beta 5 package; no promotion decision is client supplied."""

    model_config = ConfigDict(extra="forbid", strict=True)

    actor: ActorAssertion
    operation_id: str = Field(pattern=r"^beta8-op-[A-Za-z0-9._:-]{1,96}$")
    expected_revision: int = Field(ge=0)
    expected_previous_generation: str | None = Field(default=None, max_length=96)
    package: StagingPackage

    @model_validator(mode="after")
    def validate_staging_transition(self) -> StagingTransitionCommand:
        if (
            self.expected_previous_generation is not None
            and not self.expected_previous_generation.startswith("beta8-generation-synthetic-")
        ):
            raise ValueError("geração anterior fora do namespace experimental")
        _validate_json_payload(self.package.model_dump(mode="json"))
        return self


def _validate_json_payload(value: dict[str, Any]) -> None:
    try:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ValueError("dados do comando inválidos") from exc
    if len(encoded.encode("utf-8")) > 100_000:
        raise ValueError("dados do comando excedem o limite")


def request_signature(
    secret: bytes,
    *,
    service_id: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    """Sign exact request bytes and fixed routing metadata."""

    if len(secret) < 32:
        raise ValueError("segredo interno deve conter ao menos 32 bytes")
    canonical = "\n".join((
        "beta8-3-rpc-v1",
        service_id,
        method.upper(),
        path,
        timestamp,
        nonce,
        hashlib.sha256(body).hexdigest(),
    )).encode("utf-8")
    return hmac.new(secret, canonical, hashlib.sha256).hexdigest()


def verify_request_signature(
    secret: bytes,
    supplied: str,
    *,
    service_id: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> bool:
    if not re.fullmatch(r"[0-9a-f]{64}", supplied):
        return False
    expected = request_signature(
        secret,
        service_id=service_id,
        method=method,
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
    )
    return hmac.compare_digest(expected, supplied)


def response_signature(
    secret: bytes,
    *,
    request_nonce: str,
    status_code: int,
    body: bytes,
) -> str:
    """Authenticate the response and bind it to the request that caused it."""

    if len(secret) < 32 or not re.fullmatch(r"[0-9a-f]{48}", request_nonce):
        raise ValueError("contexto de resposta interna inválido")
    if type(status_code) is not int or not 100 <= status_code <= 599:
        raise ValueError("status da resposta interna inválido")
    canonical = "\n".join((
        "beta8-3-response-v1",
        "trilhacode-editorial-authority",
        request_nonce,
        str(status_code),
        hashlib.sha256(body).hexdigest(),
    )).encode("utf-8")
    return hmac.new(secret, canonical, hashlib.sha256).hexdigest()


def verify_response_signature(
    secret: bytes,
    supplied: str,
    *,
    request_nonce: str,
    status_code: int,
    body: bytes,
) -> bool:
    if not re.fullmatch(r"[0-9a-f]{64}", supplied):
        return False
    try:
        expected = response_signature(
            secret,
            request_nonce=request_nonce,
            status_code=status_code,
            body=body,
        )
    except ValueError:
        return False
    return hmac.compare_digest(expected, supplied)
