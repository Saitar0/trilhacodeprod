from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from services.beta8_3_internal_protocol import (
    EDITORIAL_AUTHORITY_AUDIENCE,
    EditorialMutationCommand,
    request_signature,
    verify_request_signature,
)

SECRET = b"ephemeral beta 8.4 protocol test secret 32+ bytes"
ACTOR = {"actor_id": "0123456789abcdef01234567", "session_id": "s" * 43, "token_version": 2}


def test_authority_signature_is_bound_to_exact_body_and_security_context() -> None:
    request = {
        "service_id": "trilhacode-api",
        "audience": EDITORIAL_AUTHORITY_AUDIENCE,
        "method": "POST",
        "path": "/internal/v1/editorial/mutations",
        "timestamp": "1800000000",
        "nonce": "a" * 48,
        "body": b'{"operation":"block.update"}',
    }
    signature = request_signature(SECRET, **request)
    assert verify_request_signature(SECRET, signature, **request)
    for field, value in (
        ("service_id", "other-service"),
        ("audience", "trilhacode-stager"),
        ("method", "PUT"),
        ("path", "/internal/v1/staging/transitions"),
        ("timestamp", "1800000001"),
        ("nonce", "b" * 48),
        ("body", b'{"operation":"node.delete"}'),
    ):
        assert not verify_request_signature(SECRET, signature, **(request | {field: value}))


def test_unknown_database_authority_fields_are_rejected() -> None:
    command = {
        "operation": "block.update",
        "actor": ACTOR,
        "operation_id": "http_" + "a" * 64,
        "expected_revision": 1,
        "block_id": "0123456789abcdef01234567",
        "changes": {"title": "safe draft"},
    }
    assert EditorialMutationCommand.model_validate(command).operation == "block.update"
    for extra in ({"collection": "users"}, {"authorized": True}, {"mongo_query": {"$where": "1"}}):
        with pytest.raises(ValidationError):
            EditorialMutationCommand.model_validate(command | extra)


def test_create_resource_identity_is_bound_to_operation_identity() -> None:
    operation_id = "http_" + "b" * 64
    block_id = hashlib.sha256(operation_id.encode()).digest()[:12].hex()
    payload = {
        "operation": "block.create",
        "actor": ACTOR,
        "operation_id": operation_id,
        "expected_revision": 0,
        "node_id": "abcdef0123456789abcdef01",
        "block_id": block_id,
        "block": {"type": "text", "title": "draft", "data": {"text": "x"}, "status": "draft"},
    }
    assert EditorialMutationCommand.model_validate(payload).block_id == block_id
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate(payload | {"block_id": "0" * 24})
