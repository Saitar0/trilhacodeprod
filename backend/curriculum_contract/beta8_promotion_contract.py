"""Strict contract for the Beta 8 synthetic promotion experiment.

This is not a publication contract and deliberately accepts only fixtures
labelled as synthetic.  It never changes the operational curriculum or readers.
"""

from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

_HASH = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class PromotionContractError(ValueError):
    """A promotion candidate or intent is outside the isolated contract."""


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class ExperimentalCandidateState(StrEnum):
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


class ExperimentalApproval(StrEnum):
    SYNTHETIC_FIXTURE_APPROVED = "SYNTHETIC_FIXTURE_APPROVED"


class ExperimentalPromotionCandidate(_StrictModel):
    """Small synthetic batch representation; no real source content is accepted."""

    batch_id: str = Field(pattern=r"^beta8-fixture-[0-9a-f]{32}$")
    track_id: str = Field(pattern=r"^beta8-track-synthetic-[A-Za-z0-9_-]{1,32}$")
    source_revision: str = Field(pattern=r"^synthetic:[A-Za-z0-9._:-]{1,80}$")
    contract_version: str = Field(pattern=r"^beta8-synthetic/[1-9][0-9]*$", max_length=32)
    state: ExperimentalCandidateState
    records: tuple[dict[str, str], ...] = Field(min_length=1, max_length=100)
    payload_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fixture_label: str = Field(pattern=r"^BETA8_SYNTHETIC_ONLY$")

    @model_validator(mode="after")
    def verify_payload_identity(self) -> ExperimentalPromotionCandidate:
        if self.state is not ExperimentalCandidateState.VALIDATED:
            raise ValueError("somente fixture validada pode entrar na promoção experimental")
        allowed_keys = {"id", "kind", "title"}
        if any(
            not {"id", "kind"}.issubset(record)
            or set(record) - allowed_keys
            or not record["id"].startswith("synthetic-")
            or record["kind"] not in {"lesson", "node"}
            or any(not value for value in record.values())
            for record in self.records
        ):
            raise ValueError("registro Beta 8 fora do esquema sintético permitido")
        canonical = canonical_records(self.records)
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != self.payload_sha256 or self.batch_id != f"beta8-fixture-{digest[:32]}":
            raise ValueError("hash ou identidade do lote sintético divergente")
        return self


class ExperimentalPromotionIntent(_StrictModel):
    """An immutable request to create a generation only in Beta 8 collections."""

    batch_id: str = Field(pattern=r"^beta8-fixture-[0-9a-f]{32}$")
    payload_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    track_id: str = Field(pattern=r"^beta8-track-synthetic-[A-Za-z0-9_-]{1,32}$")
    generation_id: str = Field(pattern=r"^beta8-generation-synthetic-[A-Za-z0-9._:-]{1,64}$")
    operation_id: str = Field(pattern=r"^beta8-op-[A-Za-z0-9._:-]{1,96}$")
    expected_revision: int = Field(ge=0, le=(1 << 63) - 1)
    fencing_token: int = Field(ge=1, le=(1 << 63) - 1)
    candidate_state: ExperimentalCandidateState
    approval: ExperimentalApproval
    target_namespace: str = Field(pattern=r"^beta8_experimental$")
    preserve_prior_generations: bool = True

    @model_validator(mode="after")
    def enforce_experiment_only(self) -> ExperimentalPromotionIntent:
        if not self.preserve_prior_generations:
            raise ValueError("a promoção Beta 8 deve preservar gerações anteriores")
        return self


def canonical_records(records: tuple[dict[str, str], ...] | list[dict[str, str]]) -> bytes:
    """Canonical JSON bytes used by the experimental batch identity."""

    try:
        return json.dumps(
            records,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PromotionContractError("registros não são JSON canônico válido") from exc


def make_synthetic_candidate(
    *,
    track_id: str,
    records: tuple[dict[str, str], ...] | list[dict[str, str]],
    source_revision: str = "synthetic:beta8-fixture-v1",
) -> ExperimentalPromotionCandidate:
    """Build a visibly synthetic candidate for tests; not for curriculum input."""

    canonical = canonical_records(records)
    digest = hashlib.sha256(canonical).hexdigest()
    return ExperimentalPromotionCandidate(
        batch_id=f"beta8-fixture-{digest[:32]}",
        track_id=track_id,
        source_revision=source_revision,
        contract_version="beta8-synthetic/1",
        state=ExperimentalCandidateState.VALIDATED,
        records=tuple(records),
        payload_sha256=digest,
        fixture_label="BETA8_SYNTHETIC_ONLY",
    )
