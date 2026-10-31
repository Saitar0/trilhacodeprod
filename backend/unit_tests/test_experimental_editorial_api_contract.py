from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_editorial_api_contract import (  # noqa: E402
    ExperimentalBlockPatch,
    derive_operation_id,
    map_protocol_error,
    minimal_intent_payload,
    parse_expected_revision,
    validate_idempotency_key,
)
from curriculum_contract.mongodb_editorial_revision_adapter import CommitOutcomeUnknown  # noqa: E402


def test_revision_headers_are_strict_and_distinguish_missing_from_invalid():
    assert parse_expected_revision('"editorial-rev-0"') == 0
    assert parse_expected_revision('"editorial-rev-18"') == 18
    with pytest.raises(HTTPException) as missing:
        parse_expected_revision(None)
    assert missing.value.status_code == 428
    with pytest.raises(HTTPException) as malformed:
        parse_expected_revision("W/\"editorial-rev-1\"")
    assert malformed.value.status_code == 400


def test_idempotency_key_is_scoped_and_client_value_is_not_stored():
    key = "synthetic-key-000001"
    assert validate_idempotency_key(key) == key
    a = derive_operation_id(actor_id="actor-a", track_id="track-a", operation_kind="block.update",
                            idempotency_key=key, key=b"operation-key-for-tests-0000000000")
    assert a == derive_operation_id(actor_id="actor-a", track_id="track-a", operation_kind="block.update",
                                    idempotency_key=key, key=b"operation-key-for-tests-0000000000")
    assert a != derive_operation_id(actor_id="actor-b", track_id="track-a", operation_kind="block.update",
                                    idempotency_key=key, key=b"operation-key-for-tests-0000000000")
    assert a != derive_operation_id(actor_id="actor-a", track_id="track-b", operation_kind="block.update",
                                    idempotency_key=key, key=b"operation-key-for-tests-0000000000")
    assert key not in a
    with pytest.raises(HTTPException) as invalid:
        validate_idempotency_key("short")
    assert invalid.value.status_code == 400


def test_patch_preserves_missing_null_empty_values_and_rejects_unknown_fields():
    assert ExperimentalBlockPatch().changes() == {}
    assert ExperimentalBlockPatch.model_validate({"title": None}).changes() == {"title": None}
    assert ExperimentalBlockPatch.model_validate({"title": ""}).changes() == {"title": ""}
    assert ExperimentalBlockPatch.model_validate({"data": {}}).changes() == {"data": {}}
    with pytest.raises(ValidationError):
        ExperimentalBlockPatch.model_validate({"data": []})
    with pytest.raises(ValidationError):
        ExperimentalBlockPatch.model_validate({"fencing_token": 3})


def test_minimized_intent_never_contains_private_values_or_plain_digest():
    secret = "private answer text"
    intent = minimal_intent_payload(
        block_id="synthetic-block", changes={"data": {"answer": secret}},
        fingerprint_key=b"private-data-hmac-key-for-tests-32bytes",
    )
    serialized = str(intent)
    assert secret not in serialized
    assert intent["changed_fields"] == ["data"]
    assert len(intent["change_hmac_sha256"]) == 64


def test_commit_unknown_error_maps_to_sanitized_retryable_response():
    error = CommitOutcomeUnknown("synthetic-track", "secret-operation-id")
    mapped = map_protocol_error(error)
    assert mapped.status_code == 503
    assert "secret-operation-id" not in str(mapped.detail)
    assert mapped.headers == {"Retry-After": "1"}
