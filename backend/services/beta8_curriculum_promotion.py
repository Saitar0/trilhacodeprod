"""Experimental, non-operational promotion into Beta 8 synthetic collections."""

from __future__ import annotations

from typing import Any

from pymongo.errors import DuplicateKeyError

from curriculum_contract.beta8_promotion_contract import (
    ExperimentalApproval,
    ExperimentalCandidateState,
    ExperimentalPromotionCandidate,
    ExperimentalPromotionIntent,
    PromotionContractError,
)
from curriculum_contract.editorial_revision_protocol import RevisionReceipt
from curriculum_contract.experimental_async_editorial_adapter import AsyncEditorialRevisionAdapter
from curriculum_contract.experimental_editorial_iam_authority import (
    EditorialAuthorizationError,
    MongoEditorialIAMAuthority,
)

from .beta8_editorial_enforcement import EditorialMutationDenied


class ExperimentalPromotionConflict(RuntimeError):
    """The expected experimental head no longer matches the candidate."""


class Beta8ExperimentalPromoter:
    """Promote only labelled synthetic candidates to non-operational collections."""

    def __init__(
        self,
        database: Any,
        authority: MongoEditorialIAMAuthority,
        adapter: AsyncEditorialRevisionAdapter,
        writer_credential: Any,
    ) -> None:
        self._database = database
        self._authority = authority
        self._adapter = adapter
        self._writer_credential = writer_credential

    async def promote(
        self,
        candidate: ExperimentalPromotionCandidate,
        intent: ExperimentalPromotionIntent,
        *,
        actor_id: str,
        session_id: str,
        expected_previous_generation: str | None = None,
    ) -> RevisionReceipt:
        if not isinstance(candidate, ExperimentalPromotionCandidate) or not isinstance(
            intent, ExperimentalPromotionIntent
        ):
            raise PromotionContractError("promoção exige contratos Beta 8 validados")
        if (
            candidate.state is not ExperimentalCandidateState.VALIDATED
            or intent.candidate_state is not ExperimentalCandidateState.VALIDATED
            or intent.approval is not ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED
            or intent.target_namespace != "beta8_experimental"
            or candidate.track_id != intent.track_id
            or candidate.batch_id != intent.batch_id
            or candidate.payload_sha256 != intent.payload_sha256
        ):
            raise PromotionContractError("lote não satisfaz a fronteira sintética Beta 8")

        decision = await self._authority.authorize(
            actor_id=actor_id,
            session_id=session_id,
            resolved_track_id=candidate.track_id,
            operation="content.publish",
        )
        if not decision.allowed or decision.capability is None:
            try:
                await self._database["_beta8_authorization_audit"].insert_one(
                    {
                        "_id": intent.operation_id,
                        "actor_id": actor_id,
                        "action": "curriculum.experimental_promotion",
                        "resource_id": candidate.track_id,
                        "operation_id": intent.operation_id,
                        "result": "denied",
                        "reason": decision.code.value,
                        "schema_version": 1,
                    }
                )
            except DuplicateKeyError:
                pass
            except Exception:
                pass
            raise EditorialMutationDenied("promoção experimental não autorizada")

        proposal = {
            "contract_version": 1,
            "operation_kind": "beta8.synthetic.generation_promotion",
            "track_ref": candidate.track_id,
            "batch_id": candidate.batch_id,
            "payload_sha256": candidate.payload_sha256,
            "generation_id": intent.generation_id,
            "source_revision": candidate.source_revision,
            "source_contract_version": candidate.contract_version,
            "target_namespace": intent.target_namespace,
        }
        prepared = await self._adapter.prepare(
            track_id=candidate.track_id,
            credential=self._writer_credential,
            operation_id=intent.operation_id,
            expected_revision=intent.expected_revision,
            fencing_token=intent.fencing_token,
            payload=proposal,
        )

        async def promotion_participant(session: Any, receipt: RevisionReceipt) -> None:
            head = await self._database["_beta8_experimental_heads"].find_one(
                {"_id": candidate.track_id}, session=session
            )
            current_generation = head.get("generation_id") if head else None
            if current_generation != expected_previous_generation:
                raise ExperimentalPromotionConflict("geração experimental mudou")
            await self._database["_beta8_experimental_generations"].insert_one(
                {
                    "_id": intent.generation_id,
                    "track_id": candidate.track_id,
                    "batch_id": candidate.batch_id,
                    "payload_sha256": candidate.payload_sha256,
                    "source_revision": candidate.source_revision,
                    "contract_version": candidate.contract_version,
                    "revision": receipt.revision,
                    "parent_revision": receipt.parent_revision,
                    "records": [dict(record) for record in candidate.records],
                    "fixture_label": candidate.fixture_label,
                    "state": "EXPERIMENTAL_GENERATION",
                    "schema_version": 1,
                },
                session=session,
            )
            if head is None:
                await self._database["_beta8_experimental_heads"].insert_one(
                    {
                        "_id": candidate.track_id,
                        "track_id": candidate.track_id,
                        "generation_id": intent.generation_id,
                        "revision": receipt.revision,
                        "schema_version": 1,
                    },
                    session=session,
                )
            else:
                updated = await self._database["_beta8_experimental_heads"].update_one(
                    {
                        "_id": candidate.track_id,
                        "generation_id": expected_previous_generation,
                        "revision": receipt.parent_revision,
                    },
                    {"$set": {
                        "generation_id": intent.generation_id,
                        "revision": receipt.revision,
                    }},
                    session=session,
                )
                if updated.matched_count != 1:
                    raise ExperimentalPromotionConflict("geração experimental mudou")
            await self._database["_beta8_promotion_audit"].insert_one(
                {
                    "_id": intent.operation_id,
                    "actor_id": actor_id,
                    "track_id": candidate.track_id,
                    "batch_id": candidate.batch_id,
                    "generation_id": intent.generation_id,
                    "operation_id": intent.operation_id,
                    "revision": receipt.revision,
                    "fencing_token": receipt.fencing_token,
                    "result": "experimental_generation_created",
                    "schema_version": 1,
                },
                session=session,
            )

        guarded = self._authority.transaction_participant(
            decision.capability, promotion_participant
        )
        try:
            return await self._adapter.commit(
                prepared,
                self._writer_credential,
                participant=guarded,
            )
        except EditorialAuthorizationError as exc:
            raise EditorialMutationDenied("promoção experimental não autorizada") from exc
