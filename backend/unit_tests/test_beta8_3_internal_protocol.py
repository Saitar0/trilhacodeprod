from __future__ import annotations

import hashlib
import asyncio
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError
from bson import ObjectId

from services.beta8_3_internal_protocol import (
    EditorialMutationCommand,
    response_signature,
    request_signature,
    verify_response_signature,
    verify_request_signature,
)
from curriculum_contract.mongodb_editorial_revision_adapter import CommitOutcomeUnknown
from services.beta8_1_runtime_iam import AuthenticatedEditorialIdentity
from services.beta8_3_editorial_rpc import Beta8_3EditorialBoundaryFactory

_SECRET = b"beta8.3 unit test key with enough entropy!!"
_ACTOR = {"actor_id": "0123456789abcdef01234567", "session_id": "s" * 43,
          "token_version": 3}


def _update_command(**overrides):
    command = {
        "operation": "block.update",
        "actor": _ACTOR,
        "operation_id": "http_" + "a" * 64,
        "expected_revision": 4,
        "block_id": "0123456789abcdef01234567",
        "changes": {"title": "Título de teste"},
    }
    command.update(overrides)
    return command


def test_internal_command_accepts_only_typed_supported_operation() -> None:
    command = EditorialMutationCommand.model_validate(_update_command())
    assert command.operation == "block.update"
    assert command.expected_revision == 4


@pytest.mark.parametrize("changes", [
    {"$set": {"status": "published"}},
    {"track_id": "other-track"},
    {"editorial_revision": 99},
    {},
])
def test_block_update_rejects_unreviewed_fields_and_empty_changes(changes) -> None:
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate(_update_command(changes=changes))


def test_command_rejects_arbitrary_collection_and_extra_authority_fields() -> None:
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate(_update_command(collection="users"))
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate(_update_command(authorized=True))


def test_create_id_is_bound_to_operation_identity_and_draft_state() -> None:
    operation_id = "http_" + "b" * 64
    block_id = hashlib.sha256(operation_id.encode()).digest()[:12].hex()
    valid = EditorialMutationCommand.model_validate({
        "operation": "block.create",
        "actor": _ACTOR,
        "operation_id": operation_id,
        "expected_revision": 0,
        "node_id": "abcdef0123456789abcdef01",
        "block_id": block_id,
        "block": {"type": "text", "title": "Rascunho", "data": {"text": "x"}, "status": "draft"},
    })
    assert valid.block_id == block_id
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate({
            **valid.model_dump(), "block_id": "000000000000000000000000",
        })
    with pytest.raises(ValidationError):
        EditorialMutationCommand.model_validate({
            **valid.model_dump(), "block": {**valid.block, "status": "published"},
        })


def test_signature_binds_service_method_path_timestamp_nonce_and_body() -> None:
    kwargs = {
        "service_id": "trilhacode-api", "method": "POST",
        "path": "/internal/v1/editorial/mutations", "timestamp": "1800000000",
        "nonce": "a" * 48, "body": b'{"operation":"block.update"}',
    }
    signature = request_signature(_SECRET, **kwargs)
    assert verify_request_signature(_SECRET, signature, **kwargs)
    for changed in (
        {**kwargs, "service_id": "other-service"},
        {**kwargs, "method": "PUT"},
        {**kwargs, "path": "/internal/v1/other"},
        {**kwargs, "timestamp": "1800000001"},
        {**kwargs, "nonce": "b" * 48},
        {**kwargs, "body": b'{"operation":"block.delete"}'},
    ):
        assert not verify_request_signature(_SECRET, signature, **changed)


def test_signature_requires_high_entropy_key_length() -> None:
    with pytest.raises(ValueError):
        request_signature(b"too short", service_id="s", method="POST", path="/p",
                          timestamp="1", nonce="n", body=b"")


def test_authority_response_signature_is_bound_to_request_nonce_and_result() -> None:
    kwargs = {
        "request_nonce": "c" * 48,
        "status_code": 200,
        "body": b'{"revision":5}',
    }
    signature = response_signature(_SECRET, **kwargs)
    assert verify_response_signature(_SECRET, signature, **kwargs)
    assert not verify_response_signature(
        _SECRET, signature, **{**kwargs, "request_nonce": "d" * 48},
    )
    assert not verify_response_signature(
        _SECRET, signature, **{**kwargs, "body": b'{"revision":6}'},
    )
    assert not verify_response_signature(
        _SECRET, signature, **{**kwargs, "status_code": 403},
    )


@pytest.mark.parametrize(
    ("module_path", "activation_names", "expected_message"),
    [
        (
            "beta8_3_api_server.py",
            ("BETA8_3_TEST_API", "BETA8_3_DISPOSABLE"),
            "composição de API Beta 8.3 exige harness descartável explícito",
        ),
        (
            "beta8_3_authority_server.py",
            ("BETA8_3_TEST_AUTHORITY", "BETA8_3_DISPOSABLE"),
            "autoridade Beta 8.3 exige composição experimental explícita",
        ),
    ],
)
def test_experimental_processes_fail_closed_without_explicit_composition(
    module_path: str,
    activation_names: tuple[str, ...],
    expected_message: str,
) -> None:
    env = os.environ.copy()
    for name in activation_names:
        env.pop(name, None)
    target = Path(__file__).parents[1] / "test_support" / module_path
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import runpy, sys; runpy.run_path(sys.argv[1])",
            str(target),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode != 0
    assert expected_message in result.stderr
    assert "/repo/backend/server.py" not in result.stderr
    assert "/repo/backend/database.py" not in result.stderr


def test_authority_unavailable_fails_closed_without_direct_writer_fallback() -> None:
    async def unavailable(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("synthetic authority outage")

    async def exercise() -> None:
        client = httpx.AsyncClient(transport=httpx.MockTransport(unavailable))
        identity = AuthenticatedEditorialIdentity(
            actor_id="0123456789abcdef01234567",
            role="editor",
            token_version=1,
            session_id="s" * 43,
        )
        boundary = Beta8_3EditorialBoundaryFactory(
            client=client,
            base_url="http://authority:8101",
            service_secret=_SECRET,
        ).for_identity(identity)
        prepared = await boundary.prepare_draft_block_update(
            actor_id=identity.actor_id,
            session_id=identity.session_id,
            block_id=ObjectId("0123456789abcdef01234567"),
            operation_id="http_" + "d" * 64,
            expected_revision=0,
            changes={"title": "no fallback"},
        )
        try:
            with pytest.raises(CommitOutcomeUnknown):
                await boundary.commit_draft_block_update(
                    prepared,
                    actor_id=identity.actor_id,
                    session_id=identity.session_id,
                )
        finally:
            await client.aclose()

    asyncio.run(exercise())
