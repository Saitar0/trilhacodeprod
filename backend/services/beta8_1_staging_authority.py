"""Beta 8.1 adapter from the real Beta 5 staging service to synthetic authority.

Only explicitly synthetic packages are accepted. This adapter is not imported
by application startup and cannot target operational publication collections.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from curriculum_contract.beta8_promotion_contract import (
    ExperimentalCandidateState,
    ExperimentalPromotionCandidate,
    ExperimentalPromotionIntent,
    make_synthetic_candidate,
)
from curriculum_contract.beta_staging_contract import StagingPackage
from curriculum_contract.editorial_revision_protocol import RevisionReceipt
from services.beta8_curriculum_promotion import Beta8ExperimentalPromoter
from services.beta_curriculum_staging import CurriculumStagingService, StagingError


class StagingAuthorityError(RuntimeError):
    """A prepared batch cannot cross the isolated authority boundary."""


class Beta8_1StagingAuthorityBridge:
    """Prepare through Beta 5 code, then pass a hash-bound synthetic candidate to C12/C8."""

    def __init__(
        self,
        staging: CurriculumStagingService,
        promoter: Beta8ExperimentalPromoter,
        *,
        track_id: str,
    ) -> None:
        if not track_id.startswith("beta8-track-synthetic-"):
            raise ValueError("A transição aceita somente a trilha sintética Beta 8")
        self._staging = staging
        self._promoter = promoter
        self._track_id = track_id

    def candidate_for(self, package: StagingPackage) -> ExperimentalPromotionCandidate:
        validated = StagingPackage.model_validate(package.model_dump(mode="python"))
        if not validated.manifest.source_revision.startswith("synthetic:beta8-1:"):
            raise StagingAuthorityError("A fronteira Beta 8.1 aceita somente pacote sintético identificado")
        if validated.manifest.source_manifest_sha256 != "b" * 64:
            raise StagingAuthorityError("Proveniência sintética Beta 8.1 divergente")
        records = tuple(
            {
                "id": f"synthetic-{record.record_id.replace(':', '-')}",
                "kind": "node",
                "title": str(record.student_public.get("title", record.record_id)),
            }
            for record in validated.records
            if record.record_id.startswith("synthetic-")
        )
        if len(records) != len(validated.records):
            raise StagingAuthorityError("Pacote de teste contém identidade de registro não sintética")
        return make_synthetic_candidate(
            track_id=self._track_id,
            records=records,
            # Keep the complete staging hash while staying inside the C8
            # candidate's bounded source_revision field.
            source_revision=f"synthetic:stage:{validated.manifest.payload_sha256}",
        )

    async def verify_prepared_package(
        self, package: StagingPackage,
    ) -> ExperimentalPromotionCandidate:
        """Re-read and validate a prepared Beta 5 batch through a read-only handle.

        The caller may live in the staging writer process. The authority process
        supplies a Mongo identity limited to reads on the staging collections;
        this method never prepares or mutates staging data.
        """

        validated = StagingPackage.model_validate(package.model_dump(mode="python"))
        candidate = self.candidate_for(validated)
        await self._staging._verify_database_owner()
        staged = await self._staging.inspect_batch(validated.manifest.batch_id)
        try:
            await self._staging._assert_complete(validated)
        except StagingError as exc:
            raise StagingAuthorityError("Lote staging não passou na verificação de integridade") from exc
        if (
            staged is None
            or staged.get("status") != "PREPARED"
            or staged.get("payload_sha256") != validated.manifest.payload_sha256
            or staged.get("prepared_count") != len(validated.records)
        ):
            raise StagingAuthorityError("Lote staging incompleto ou divergente; transição negada")
        return candidate

    async def promote_prepared(
        self,
        package: StagingPackage,
        intent: ExperimentalPromotionIntent,
        *,
        actor_id: str,
        session_id: str,
        expected_previous_generation: str | None = None,
        transaction_guard=None,
        before_commit: Callable[[], Awaitable[None]] | None = None,
        after_commit: Callable[[], Awaitable[None]] | None = None,
    ) -> RevisionReceipt:
        """Promote only a batch already prepared by a separate staging writer."""

        candidate = await self.verify_prepared_package(package)
        if (
            intent.batch_id != candidate.batch_id
            or intent.payload_sha256 != candidate.payload_sha256
            or intent.track_id != candidate.track_id
            or intent.candidate_state is not ExperimentalCandidateState.VALIDATED
        ):
            raise StagingAuthorityError("Intenção não está vinculada ao pacote preparado")
        receipt = await self._promoter.promote(
            candidate,
            intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=expected_previous_generation,
            transaction_guard=transaction_guard,
            before_commit=before_commit,
        )
        if after_commit is not None:
            await after_commit()
        return receipt

    async def prepare_and_promote(
        self,
        package: StagingPackage,
        intent: ExperimentalPromotionIntent,
        *,
        actor_id: str,
        session_id: str,
        expected_previous_generation: str | None = None,
        transaction_guard=None,
        staging_fault_hook=None,
        before_commit: Callable[[], Awaitable[None]] | None = None,
        after_commit: Callable[[], Awaitable[None]] | None = None,
    ) -> RevisionReceipt:
        outcome = await self._staging.prepare(package, fault_hook=staging_fault_hook)
        if outcome.state.value != "PREPARED" or outcome.payload_sha256 != package.manifest.payload_sha256:
            raise StagingAuthorityError("Lote staging incompleto ou divergente; transição negada")
        receipt = await self.promote_prepared(
            package,
            intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=expected_previous_generation,
            transaction_guard=transaction_guard,
            before_commit=before_commit,
            after_commit=after_commit,
        )
        return receipt
