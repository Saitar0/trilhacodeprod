from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from curriculum_contract.beta8_promotion_contract import (
    ExperimentalApproval,
    ExperimentalCandidateState,
    ExperimentalPromotionCandidate,
    ExperimentalPromotionIntent,
    make_synthetic_candidate,
)
from services.beta8_editorial_enforcement import _validated_changes

TRACK = "beta8-track-synthetic-unit"


def _intent(candidate, **changes):
    values = {
        "batch_id": candidate.batch_id,
        "payload_sha256": candidate.payload_sha256,
        "track_id": candidate.track_id,
        "generation_id": "beta8-generation-synthetic-1",
        "operation_id": "beta8-op-synthetic-0001",
        "expected_revision": 0,
        "fencing_token": 1,
        "candidate_state": ExperimentalCandidateState.VALIDATED,
        "approval": ExperimentalApproval.SYNTHETIC_FIXTURE_APPROVED,
        "target_namespace": "beta8_experimental",
        "preserve_prior_generations": True,
    }
    return ExperimentalPromotionIntent.model_validate(values | changes)


def test_synthetic_candidate_hash_and_identity_are_deterministic():
    rows = [{"kind": "lesson", "id": "synthetic-1"}]
    first = make_synthetic_candidate(track_id=TRACK, records=rows)
    second = make_synthetic_candidate(track_id=TRACK, records=rows)

    assert first == second
    assert first.payload_sha256 == hashlib.sha256(
        b'[{"id":"synthetic-1","kind":"lesson"}]'
    ).hexdigest()
    assert first.batch_id == f"beta8-fixture-{first.payload_sha256[:32]}"


def test_candidate_rejects_payload_hash_drift_and_real_source_ids():
    candidate = make_synthetic_candidate(
        track_id=TRACK,
        records=[{"kind": "lesson", "id": "synthetic-1"}],
    )
    with pytest.raises(ValidationError):
        ExperimentalPromotionCandidate.model_validate(
            candidate.model_dump() | {"payload_sha256": "0" * 64}
        )
    with pytest.raises(ValidationError):
        make_synthetic_candidate(
            track_id="trilha-real-primeira-fase",
            records=[{"kind": "lesson", "id": "synthetic-1"}],
        )


def test_candidate_rejects_unmodeled_record_metadata():
    with pytest.raises(ValidationError):
        make_synthetic_candidate(
            track_id=TRACK,
            records=[{
                "kind": "node",
                "id": "synthetic-node",
                "private_answer": "must not enter promotion records",
            }],
        )


def test_promotion_intent_is_synthetic_only_and_preserves_prior_generations():
    candidate = make_synthetic_candidate(
        track_id=TRACK,
        records=[{"kind": "node", "id": "synthetic-node"}],
    )
    valid = _intent(candidate)
    assert valid.target_namespace == "beta8_experimental"
    assert valid.preserve_prior_generations is True

    with pytest.raises(ValidationError):
        _intent(candidate, target_namespace="track_publications")
    with pytest.raises(ValidationError):
        _intent(candidate, preserve_prior_generations=False)
    with pytest.raises(ValidationError):
        ExperimentalPromotionIntent(
            **(valid.model_dump() | {"approval": "PEDAGOGICALLY_APPROVED"})
        )


def test_unvalidated_candidate_cannot_be_promoted():
    candidate = make_synthetic_candidate(
        track_id=TRACK,
        records=[{"kind": "node", "id": "synthetic-node"}],
    )
    with pytest.raises(ValidationError):
        ExperimentalPromotionCandidate.model_validate(
            candidate.model_dump() | {"state": "FAILED"}
        )


@pytest.mark.parametrize(
    "patch",
    [
        {},
        {"title": "ok", "track_id": "other"},
        {"title": 17},
        {"body": "x" * 100_001},
        ["title", "ok"],
    ],
)
def test_draft_update_patch_is_closed_and_bounded(patch):
    with pytest.raises(ValueError):
        _validated_changes(patch)


def test_new_beta8_services_remain_disconnected_from_active_bootstrap_and_routes():
    backend = Path(__file__).resolve().parents[1]
    for relative in (
        "services/beta8_editorial_enforcement.py",
        "services/beta8_curriculum_promotion.py",
    ):
        tree = ast.parse((backend / relative).read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert "database" not in imported
        assert not any(value.startswith("routes_") for value in imported)
