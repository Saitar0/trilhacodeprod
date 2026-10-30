"""Experimental grant-protected draft block mutation boundary.

The service composes C12 authorization with the existing C8/C10 revision
authority. The normal application startup does not construct or inject it;
Beta 8.1 exercises it through an explicitly composed test-only HTTP app.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pymongo.errors import DuplicateKeyError

from curriculum_contract.editorial_revision_protocol import PreparedRevision, RevisionReceipt
from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter
from curriculum_contract.experimental_editorial_iam_authority import (
    EditorialAuthorizationError,
    MongoEditorialIAMAuthority,
)


class EditorialMutationDenied(PermissionError):
    """A safe, non-enumerating denial for the experimental mutation boundary."""


class DraftBlockNotFound(LookupError):
    """The requested block is absent or not an editable draft block."""


@dataclass(frozen=True, slots=True)
class PreparedDraftBlockUpdate:
    actor_id: str
    session_id: str = field(repr=False)
    track_id: str
    block_id: Any
    operation_id: str
    changes: dict[str, Any]
    preparation: PreparedRevision


TransactionGuard = Callable[[Any, RevisionReceipt], Awaitable[None]]
BeforeCommit = Callable[[], Awaitable[None]]


class Beta8EditorialMutationBoundary:
    """Use current C12 grants plus C8/C10 CAS/fence for synthetic draft edits."""

    def __init__(
        self,
        database: Any,
        authority: MongoEditorialIAMAuthority,
        adapter: AsyncEditorialRevisionAdapter,
        writer_credential: Any,
        fencing_token: int,
    ) -> None:
        self._database = database
        self._authority = authority
        self._adapter = adapter
        self._writer_credential = writer_credential
        self._fencing_token = fencing_token

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
    ) -> PreparedDraftBlockUpdate:
        patch = _validated_changes(changes)
        block = await self._database.content_blocks.find_one(
            {"_id": block_id, "editorial_state": "draft"},
            {"track_id": 1},
        )
        if block is None or not isinstance(block.get("track_id"), str):
            raise DraftBlockNotFound("bloco indisponível")
        track_id = block["track_id"]
        decision = await self._authority.authorize(
            actor_id=actor_id,
            session_id=session_id,
            resolved_track_id=track_id,
            operation="block.update",
            requested_track_id=requested_track_id,
        )
        if not decision.allowed:
            await self._audit_denial(
                actor_id=actor_id,
                action="draft_block.update",
                resource_id=str(block_id),
                operation_id=operation_id,
                reason=decision.code.value,
            )
            raise EditorialMutationDenied("operação editorial não autorizada")
        payload = {
            "contract_version": 1,
            "operation_kind": "beta8.synthetic.draft_block_update",
            "track_ref": track_id,
            "target_ref": str(block_id),
            "change_set": patch,
        }
        prepared = await self._adapter.prepare(
            track_id=track_id,
            credential=self._writer_credential,
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self._fencing_token,
            payload=payload,
        )
        assert decision.capability is not None
        return PreparedDraftBlockUpdate(
            actor_id=actor_id,
            session_id=session_id,
            track_id=track_id,
            block_id=block_id,
            operation_id=operation_id,
            changes=patch,
            preparation=prepared,
        )

    async def commit_draft_block_update(
        self,
        prepared: PreparedDraftBlockUpdate,
        *,
        actor_id: str,
        session_id: str,
        transaction_guard: TransactionGuard | None = None,
        before_commit: BeforeCommit | None = None,
    ) -> RevisionReceipt:
        if (
            not isinstance(prepared, PreparedDraftBlockUpdate)
            or prepared.actor_id != actor_id
            or prepared.session_id != session_id
        ):
            raise EditorialMutationDenied("operação editorial não autorizada")

        # Fresh request-level authorization rejects an already revoked grant.
        # The transaction participant below orders a concurrent revocation
        # against the same persisted C12 records as the C10 commit.
        decision = await self._authority.authorize(
            actor_id=actor_id,
            session_id=session_id,
            resolved_track_id=prepared.track_id,
            operation="block.update",
        )
        if not decision.allowed or decision.capability is None:
            await self._audit_denial(
                actor_id=actor_id,
                action="draft_block.update",
                resource_id=str(prepared.block_id),
                operation_id=prepared.operation_id,
                reason=decision.code.value,
            )
            raise EditorialMutationDenied("operação editorial não autorizada")

        async def mutate(session: Any, receipt: RevisionReceipt) -> None:
            result = await self._database.content_blocks.update_one(
                {
                    "_id": prepared.block_id,
                    "track_id": prepared.track_id,
                    "editorial_state": "draft",
                },
                {"$set": prepared.changes | {"editorial_revision": receipt.revision}},
                session=session,
            )
            if result.matched_count != 1:
                raise DraftBlockNotFound("bloco indisponível")
            await self._database["_beta8_editorial_audit"].insert_one(
                {
                    "_id": prepared.operation_id,
                    "actor_id": actor_id,
                    "track_id": prepared.track_id,
                    "resource_id": str(prepared.block_id),
                    "operation_id": prepared.operation_id,
                    "action": "draft_block.update",
                    "revision": receipt.revision,
                    "parent_revision": receipt.parent_revision,
                    "result": "committed",
                    "schema_version": 1,
                },
                session=session,
            )

        authority_guard = self._authority.transaction_participant(decision.capability, mutate)

        async def guarded(session: Any, receipt: Any) -> None:
            if transaction_guard is not None:
                await transaction_guard(session, receipt)
            await authority_guard(session, receipt)

        try:
            if before_commit is not None:
                await before_commit()
            return await self._adapter.commit(
                prepared.preparation,
                self._writer_credential,
                participant=guarded,
            )
        except EditorialAuthorizationError as exc:
            raise EditorialMutationDenied("operação editorial não autorizada") from exc

    async def _audit_denial(
        self,
        *,
        actor_id: str,
        action: str,
        resource_id: str,
        operation_id: str,
        reason: str,
    ) -> None:
        # Denial logging is best effort and contains only identifiers and a
        # closed reason code; failure can never turn a denial into an allow.
        try:
            await self._database["_beta8_authorization_audit"].insert_one(
                {
                    "_id": operation_id,
                    "actor_id": actor_id,
                    "action": action,
                    "resource_id": resource_id,
                    "operation_id": operation_id,
                    "result": "denied",
                    "reason": reason,
                    "schema_version": 1,
                }
            )
        except DuplicateKeyError:
            return
        except Exception:
            return


def _validated_changes(changes: object) -> dict[str, Any]:
    if not isinstance(changes, dict) or not changes or set(changes) - {"title", "body", "data"}:
        raise ValueError("patch de rascunho inválido")
    for field_name, value in changes.items():
        if field_name in {"title", "body"} and (
            not isinstance(value, str) or len(value.encode("utf-8")) > 100_000
        ):
            raise ValueError("patch de rascunho inválido")
        if field_name == "data":
            if not isinstance(value, dict):
                raise ValueError("patch de rascunho inválido")
            try:
                import json

                encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
            except (TypeError, ValueError, UnicodeEncodeError) as exc:
                raise ValueError("patch de rascunho inválido") from exc
            if len(encoded.encode("utf-8")) > 100_000:
                raise ValueError("patch de rascunho inválido")
    return dict(changes)
