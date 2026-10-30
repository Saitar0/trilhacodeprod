"""Beta 8.1 adapter from the real Beta 5 staging service to synthetic authority.

Only explicitly synthetic packages are accepted. This adapter is not imported
by application startup and cannot target operational publication collections.
"""

from __future__ import annotations

from curriculum_contract.beta8_promotion_contract import (
    ExperimentalCandidateState,
    ExperimentalPromotionCandidate,
    ExperimentalPromotionIntent,
    make_synthetic_candidate,
)
from curriculum_contract.beta_staging_contract import StagingPackage
from curriculum_contract.editorial_revision_protocol import RevisionReceipt
from services.beta8_curriculum_promotion import Beta8ExperimentalPromoter
from services.beta_curriculum_staging import CurriculumStagingService


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

    async def prepare_and_promote(
        self,
        package: StagingPackage,
        intent: ExperimentalPromotionIntent,
        *,
        actor_id: str,
        session_id: str,
        expected_previous_generation: str | None = None,
    ) -> RevisionReceipt:
        candidate = self.candidate_for(package)
        outcome = await self._staging.prepare(package)
        staged = await self._staging.inspect_batch(package.manifest.batch_id)
        if (
            outcome.state.value != "PREPARED"
            or outcome.payload_sha256 != package.manifest.payload_sha256
            or staged is None
            or staged.get("status") != "PREPARED"
            or staged.get("payload_sha256") != candidate.source_revision.removeprefix("synthetic:stage:")
            or staged.get("prepared_count") != len(package.records)
        ):
            raise StagingAuthorityError("Lote staging incompleto ou divergente; transição negada")
        if (
            intent.batch_id != candidate.batch_id
            or intent.payload_sha256 != candidate.payload_sha256
            or intent.track_id != candidate.track_id
            or intent.candidate_state is not ExperimentalCandidateState.VALIDATED
        ):
            raise StagingAuthorityError("Intenção não está vinculada ao pacote preparado")
        return await self._promoter.promote(
            candidate,
            intent,
            actor_id=actor_id,
            session_id=session_id,
            expected_previous_generation=expected_previous_generation,
        )
