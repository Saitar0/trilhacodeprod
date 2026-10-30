"""Client-side adapter from existing Beta 8.2 writers to a separate authority.

This object has no Mongo client and never receives an editorial database URI.
The existing service functions still validate their inputs and call the same
prepare/commit-shaped boundary; commit sends one narrow operation to authority.
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx
from bson import ObjectId

from curriculum_contract.editorial_revision_protocol import (
    FencingRejected,
    IdempotencyConflict,
    InvalidProposal,
    RevisionConflict,
)
from curriculum_contract.mongodb_editorial_revision_adapter import CommitOutcomeUnknown
from services.beta8_editorial_enforcement import DraftBlockNotFound, EditorialMutationDenied
from services.beta8_1_runtime_iam import AuthenticatedEditorialIdentity
from services.beta8_3_internal_protocol import (
    EditorialMutationCommand,
    request_signature,
    verify_response_signature,
)

_MUTATION_PATH = "/internal/v1/editorial/mutations"


@dataclass(frozen=True, slots=True, repr=False)
class RemotePreparedMutation:
    operation: str
    actor_id: str
    session_id: str = field(repr=False)
    operation_id: str
    expected_revision: int
    resource: dict[str, Any]


@dataclass(frozen=True, slots=True, repr=False)
class Beta8_3EditorialBoundaryFactory:
    """A test-composition factory containing only RPC capability, never Mongo."""

    client: httpx.AsyncClient = field(repr=False, compare=False)
    base_url: str
    service_secret: bytes = field(repr=False)

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname != "authority"
            or parsed.port != 8101
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or len(self.service_secret) < 32
        ):
            raise ValueError("composição RPC Beta 8.3 inválida")

    def for_identity(self, identity: AuthenticatedEditorialIdentity) -> Beta8_3RemoteEditorialBoundary:
        return Beta8_3RemoteEditorialBoundary(self, identity)


class Beta8_3RemoteEditorialBoundary:
    """RPC facade implementing the existing mutation-boundary method shape."""

    def __init__(
        self,
        factory: Beta8_3EditorialBoundaryFactory,
        identity: AuthenticatedEditorialIdentity,
    ) -> None:
        self._factory = factory
        self._identity = identity

    async def prepare_draft_block_update(
        self,
        *,
        actor_id: str,
        session_id: str,
        block_id: Any,
        operation_id: str,
        expected_revision: int,
        changes: dict[str, Any],
        requested_track_id: str | None = None,
    ) -> RemotePreparedMutation:
        self._assert_identity(actor_id, session_id)
        resource = {"block_id": str(block_id), "changes": dict(changes)}
        if requested_track_id is not None:
            raise ValueError("escopo não pode ser escolhido pelo cliente")
        return self._prepared("block.update", operation_id, expected_revision, resource)

    async def commit_draft_block_update(
        self,
        prepared: RemotePreparedMutation,
        *,
        actor_id: str,
        session_id: str,
        transaction_guard=None,
        before_commit=None,
    ):
        return await self._commit(prepared, "block.update", actor_id, session_id,
                                  transaction_guard, before_commit)

    async def prepare_draft_block_create(
        self,
        *,
        actor_id: str,
        session_id: str,
        node_id: str,
        block_id: ObjectId,
        operation_id: str,
        expected_revision: int,
        document: dict[str, Any],
        requested_track_id: str | None = None,
    ) -> RemotePreparedMutation:
        self._assert_identity(actor_id, session_id)
        if requested_track_id is not None:
            raise ValueError("escopo não pode ser escolhido pelo cliente")
        resource = {
            "node_id": node_id,
            "block_id": str(block_id),
            "block": {
                "type": document.get("type"),
                "title": document.get("title"),
                "data": document.get("data", {}),
                "status": document.get("status"),
            },
        }
        return self._prepared("block.create", operation_id, expected_revision, resource)

    async def commit_draft_block_create(
        self,
        prepared: RemotePreparedMutation,
        *,
        actor_id: str,
        session_id: str,
        transaction_guard=None,
        before_commit=None,
    ):
        return await self._commit(prepared, "block.create", actor_id, session_id,
                                  transaction_guard, before_commit)

    async def prepare_draft_node_update(
        self,
        *,
        actor_id: str,
        session_id: str,
        node_id: str,
        operation_id: str,
        expected_revision: int,
        changes: dict[str, Any],
        requested_track_id: str | None = None,
    ) -> RemotePreparedMutation:
        self._assert_identity(actor_id, session_id)
        if requested_track_id is not None:
            raise ValueError("escopo não pode ser escolhido pelo cliente")
        return self._prepared(
            "node.update", operation_id, expected_revision,
            {"node_id": node_id, "changes": dict(changes)},
        )

    async def commit_draft_node_update(
        self,
        prepared: RemotePreparedMutation,
        *,
        actor_id: str,
        session_id: str,
        transaction_guard=None,
        before_commit=None,
    ):
        return await self._commit(prepared, "node.update", actor_id, session_id,
                                  transaction_guard, before_commit)

    def _prepared(
        self, operation: str, operation_id: str, expected_revision: int, resource: dict[str, Any],
    ) -> RemotePreparedMutation:
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("revisão esperada inválida")
        return RemotePreparedMutation(
            operation=operation,
            actor_id=self._identity.actor_id,
            session_id=self._identity.session_id,
            operation_id=operation_id,
            expected_revision=expected_revision,
            resource=resource,
        )

    async def _commit(
        self,
        prepared: RemotePreparedMutation,
        operation: str,
        actor_id: str,
        session_id: str,
        transaction_guard: Any,
        before_commit: Any,
    ):
        from curriculum_contract.editorial_revision_protocol import RevisionReceipt

        self._assert_identity(actor_id, session_id)
        if (
            not isinstance(prepared, RemotePreparedMutation)
            or prepared.operation != operation
            or prepared.actor_id != actor_id
            or prepared.session_id != session_id
        ):
            raise EditorialMutationDenied("operação editorial não autorizada")
        # Transaction guards and callbacks must execute beside the privileged
        # transaction. Serializing a Python callback would create a false guarantee.
        if transaction_guard is not None or before_commit is not None:
            raise ValueError("callbacks locais não atravessam a autoridade separada")

        command_data: dict[str, Any] = {
            "operation": operation,
            "actor": {
                "actor_id": self._identity.actor_id,
                "session_id": self._identity.session_id,
                "token_version": self._identity.token_version,
            },
            "operation_id": prepared.operation_id,
            "expected_revision": prepared.expected_revision,
            **prepared.resource,
        }
        command = EditorialMutationCommand.model_validate(command_data)
        body = json.dumps(
            command.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(24)
        service_id = "trilhacode-api"
        signature = request_signature(
            self._factory.service_secret,
            service_id=service_id,
            method="POST",
            path=_MUTATION_PATH,
            timestamp=timestamp,
            nonce=nonce,
            body=body,
        )
        try:
            response = await self._factory.client.post(
                f"{self._factory.base_url}{_MUTATION_PATH}",
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Beta8-Service": service_id,
                    "X-Beta8-Timestamp": timestamp,
                    "X-Beta8-Nonce": nonce,
                    "X-Beta8-Signature": signature,
                },
            )
        except httpx.TimeoutException as exc:
            raise CommitOutcomeUnknown("remote", prepared.operation_id) from exc
        except httpx.HTTPError as exc:
            raise CommitOutcomeUnknown("remote", prepared.operation_id) from exc

        if not verify_response_signature(
            self._factory.service_secret,
            response.headers.get("X-Beta8-Response-Signature", ""),
            request_nonce=nonce,
            status_code=response.status_code,
            body=response.content,
        ):
            raise CommitOutcomeUnknown("remote", prepared.operation_id)

        if response.status_code == 403:
            raise EditorialMutationDenied("operação editorial não autorizada")
        if response.status_code == 404:
            raise DraftBlockNotFound("recurso indisponível")
        if response.status_code == 412:
            raise RevisionConflict("remote", prepared.operation_id, prepared.expected_revision,
                                   prepared.expected_revision + 1)
        if response.status_code == 409:
            payload = _safe_json(response)
            if payload.get("code") == "idempotency_conflict":
                raise IdempotencyConflict("remote", prepared.operation_id)
            raise FencingRejected("remote", 0, 1)
        if response.status_code >= 500:
            raise CommitOutcomeUnknown("remote", prepared.operation_id)
        if response.status_code != 200:
            raise InvalidProposal()
        payload = _safe_json(response)
        try:
            return RevisionReceipt(
                track_id=str(payload["track_id"]),
                operation_id=str(payload["operation_id"]),
                writer_id=str(payload["writer_id"]),
                revision=int(payload["revision"]),
                parent_revision=int(payload["parent_revision"]),
                fencing_token=int(payload["fencing_token"]),
                payload_sha256=str(payload["payload_sha256"]),
                fingerprint=str(payload["fingerprint"]),
                replayed=payload["replayed"] is True,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CommitOutcomeUnknown("remote", prepared.operation_id) from exc

    def _assert_identity(self, actor_id: str, session_id: str) -> None:
        if actor_id != self._identity.actor_id or session_id != self._identity.session_id:
            raise EditorialMutationDenied("operação editorial não autorizada")


def _safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}
