"""Adversarial RPC revocation and real-process-restart proof for Beta 8.4.

Run only from the isolated Beta 8.4 Docker controller. The existing Beta 8.3
HTTP/Mongo proof is rerun first; this file then adds cross-process barriers,
revocation races, and restart/reconciliation cases against the same synthetic
replica set and real Beta 5 staging service.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from bson import ObjectId
from pymongo import AsyncMongoClient

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from beta8_3_process_security import (  # noqa: E402
    TRACK_ID,
    _env,
    _gate,
    _login,
    _provision_c12,
    _seed_user,
    _session_digest,
    _stage_package,
    _verify,
)


def _operation_id(actor_id: str, scope: str, kind: str, key: str) -> str:
    from curriculum_contract.experimental_editorial_api_contract import derive_operation_id

    return derive_operation_id(
        actor_id=actor_id,
        track_id=scope,
        operation_kind=kind,
        idempotency_key=key,
        key=bytes.fromhex(_env("BETA8_3_OPERATION_KEY_HEX")),
    )


async def _new_editor(root_db: Any, api_url: str, suffix: str):
    user_id = str(ObjectId())
    email = f"beta84-{suffix}-{user_id[:8]}@example.com"
    await _seed_user(root_db, user_id, email, "editor")
    client = httpx.AsyncClient(base_url=api_url, timeout=12.0)
    actor_id, session_id, _ = await _login(client, email)
    await _provision_c12(root_db, actor_id, session_id, grant_track=TRACK_ID)
    return client, actor_id, session_id


async def _wait_barrier(root_db: Any, barrier_id: str, task: asyncio.Task | None = None) -> dict[str, Any]:
    for _ in range(600):
        barrier = await root_db["_beta8_4_test_barriers"].find_one({"_id": barrier_id})
        if barrier and barrier.get("state") == "PAUSED":
            return barrier
        if task is not None and task.done():
            try:
                result = task.result()
                raise AssertionError(
                    f"authority returned before barrier: HTTP {result.status_code} {result.text}"
                )
            except httpx.HTTPError as exc:
                raise AssertionError(f"authority connection failed before barrier: {type(exc).__name__}") from exc
        await asyncio.sleep(0.025)
    raise AssertionError(f"autoridade não alcançou a barreira persistente {barrier_id}")


async def _arm(root_db: Any, operation_id: str, phase: str) -> str:
    barrier_id = f"{operation_id}:{phase}"
    await root_db["_beta8_4_test_barriers"].insert_one({
        "_id": barrier_id,
        "operation_id": operation_id,
        "phase": phase,
        "state": "ARMED",
        "created_at": datetime.now(UTC),
    })
    return barrier_id


def _request_for_operation(
    client: httpx.AsyncClient,
    operation: str,
    *,
    block_id: str,
    node_id: str,
    revision: int,
    key: str,
):
    headers = {"If-Match": f'"editorial-rev-{revision}"', "Idempotency-Key": key}
    if operation == "block.update":
        return client.put(f"/api/blocks/{block_id}", json={"title": "must-not-commit"}, headers=headers)
    if operation == "block.create":
        return client.post(
            "/api/blocks",
            json={"node_id": node_id, "type": "text", "title": "must-not-create",
                  "data": {"text": "synthetic"}, "status": "draft"},
            headers=headers,
        )
    return client.put(
        f"/api/nodes/{node_id}", json={"summary": "must-not-commit"}, headers=headers,
    )


async def _verify_revocation_races(root_db: Any, api_url: str, run_id: str) -> None:
    from curriculum_contract.experimental_editorial_iam_authority import MongoEditorialIAMAuthority

    iam = MongoEditorialIAMAuthority(root_db, capability_key=secrets.token_bytes(32))
    node_id = _env("BETA8_3_NODE_ID")
    block_id = _env("BETA8_3_BLOCK_ID")
    race_cases = (
        ("block.update", "block.update", f"block:{block_id}"),
        ("block.create", "block.create", f"node:{node_id}"),
        ("node.update", "node.update", f"node:{node_id}"),
    )
    for index, (operation, kind, scope) in enumerate(race_cases):
        client, actor_id, _session_id = await _new_editor(root_db, api_url, f"revoke-{index}")
        try:
            key = f"beta84-revoke-{index}-0001"
            operation_id = _operation_id(actor_id, scope, kind, key)
            barrier_id = await _arm(root_db, operation_id, "before_commit")
            head = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
            assert head is not None
            revision = int(head["revision"])
            block_before = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
            node_before = await root_db.nodes.find_one({"_id": ObjectId(node_id)})
            task = asyncio.create_task(_request_for_operation(
                client, operation, block_id=block_id, node_id=node_id,
                revision=revision, key=key,
            ))
            await _wait_barrier(root_db, barrier_id, task)
            if operation == "block.create":
                logout = await client.post("/api/auth/logout")
                assert logout.status_code == 200, "sessão sintética não foi revogada"
                session_record = await root_db.auth_sessions.find_one({
                    "_id": _session_digest(_session_id), "user_id": actor_id,
                })
                assert session_record and session_record.get("revoked_at") is not None
            else:
                assert await iam.revoke_grant(
                    actor_id=actor_id, track_id=TRACK_ID, revoked_by="beta8-4-verifier",
                ), "grant sintético não foi efetivamente revogado"
            await root_db["_beta8_4_test_barriers"].update_one(
                {"_id": barrier_id, "state": "PAUSED"},
                {"$set": {"state": "RELEASED", "revocation_confirmed_at": datetime.now(UTC)}},
            )
            response = await asyncio.wait_for(task, timeout=15)
            assert response.status_code == 403, (
                f"{operation} após revogação confirmou HTTP {response.status_code}"
            )
            current_head = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
            assert current_head["revision"] == revision, "revisão avançou após revogação confirmada"
            block_after = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
            node_after = await root_db.nodes.find_one({"_id": ObjectId(node_id)})
            assert block_after == block_before, f"{operation} alterou bloco após revogação"
            assert node_after == node_before, f"{operation} alterou unidade após revogação"
            assert await root_db["_beta8_editorial_audit"].count_documents({"_id": operation_id}) == 0
            assert await root_db["c8_beta8_1_history"].count_documents({"operation_id": operation_id}) == 0
            retry_response = await _request_for_operation(
                client, operation, block_id=block_id, node_id=node_id,
                revision=revision, key=key,
            )
            expected_retry = 401 if operation == "block.create" else 403
            assert retry_response.status_code == expected_retry, "retry reutilizou contexto revogado"
            assert (await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID}))["revision"] == revision
        finally:
            await client.aclose()
    print("BETA8_4_CROSS_PROCESS_REVOCATION: PASS; W-07 PUT/POST and W-05 PUT aborted after confirmed grant revocation", flush=True)


async def _verify_revocation_serializes_with_open_transaction(
    root_db: Any, api_url: str, root_uri: str, db_name: str,
) -> None:
    """Show an overlapping revocation and mutation serialize at the grant document."""
    from curriculum_contract.experimental_editorial_iam_authority import MongoEditorialIAMAuthority

    client, actor_id, _session_id = await _new_editor(root_db, api_url, "revoke-in-txn")
    grant_id = hashlib.sha256(f"{actor_id}\x00{TRACK_ID}".encode()).hexdigest()

    observer = AsyncMongoClient(
        root_uri, appname="beta8-4-revoke-order-observer", tz_aware=True,
    )
    barrier_id: str | None = None
    mutation_task: asyncio.Task | None = None
    revoke_task: asyncio.Task | None = None
    try:
        operation_id = _operation_id(actor_id, f"block:{_env('BETA8_3_BLOCK_ID')}", "block.update",
                                     "beta84-revoke-transaction-0001")
        barrier_id = await _arm(root_db, operation_id, "before_transaction_commit")
        track = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        assert track is not None
        revision = int(track["revision"])
        block_id = _env("BETA8_3_BLOCK_ID")
        before = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
        print("BETA8_4_TRANSACTION_REVOCATION_ORDER: request-start", flush=True)
        mutation_task = asyncio.create_task(_request_for_operation(
            client, "block.update", block_id=block_id,
            node_id=_env("BETA8_3_NODE_ID"), revision=revision,
            key="beta84-revoke-transaction-0001",
        ))
        await _wait_barrier(root_db, barrier_id, mutation_task)
        print("BETA8_4_TRANSACTION_REVOCATION_ORDER: mutation-paused-inside-transaction", flush=True)
        revoker = MongoEditorialIAMAuthority(observer[db_name], capability_key=secrets.token_bytes(32))
        revocation_call_started = asyncio.Event()

        async def revoke_while_transaction_is_open() -> bool:
            # This coroutine sets the event and immediately enters the real
            # Mongo update await. The verifier resumes only after that await
            # yields, while the API's transaction is still paused in Mongo.
            revocation_call_started.set()
            return await revoker.revoke_grant(
                actor_id=actor_id, track_id=TRACK_ID,
                revoked_by="beta8-4-transaction-order",
            )

        revoke_task = asyncio.create_task(revoke_while_transaction_is_open())
        await asyncio.wait_for(revocation_call_started.wait(), timeout=5)
        revoke_done_before_release = revoke_task.done()
        if revoke_done_before_release:
            try:
                assert revoke_task.result() is True, "revogação concorrente não foi confirmada"
            except Exception as exc:
                raise AssertionError(
                    f"revogação concorrente falhou antes do commit: {type(exc).__name__}"
                ) from exc
        await root_db["_beta8_4_test_barriers"].update_one(
            {"_id": barrier_id, "state": "PAUSED"},
            {"$set": {"state": "RELEASED", "revocation_command_started": True}},
        )
        mutation_response = await asyncio.wait_for(mutation_task, timeout=15)
        if revoke_done_before_release:
            committed = False
            assert mutation_response.status_code == 403, (
                "a mutação confirmou após a revogação persistida; "
                f"HTTP={mutation_response.status_code}"
            )
            order = "revocation-confirmed-before-transaction-commit"
        else:
            committed = True
            assert mutation_response.status_code == 200, (
                "a mutação que serializou primeiro deveria confirmar antes da revogação; "
                f"HTTP={mutation_response.status_code}"
            )
            assert await asyncio.wait_for(revoke_task, timeout=15) is True
            order = "transaction-commit-before-revocation-confirmation"
        current = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        block = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
        assert current and current["revision"] == revision + int(committed)
        assert block is not None and before is not None
        assert (block.get("title") == "must-not-commit") is committed
        assert await root_db["_beta8_editorial_audit"].count_documents({"_id": operation_id}) == int(committed)
        assert await root_db["c8_beta8_1_history"].count_documents({"operation_id": operation_id}) == int(committed)
        grant = await root_db["c12_track_grants"].find_one({"_id": grant_id})
        assert grant and grant["state"] == "revoked"
        print(f"BETA8_4_TRANSACTION_REVOCATION_ORDER: PASS; overlapping revocation call; {order}; persisted state and audit matched commit order", flush=True)
    finally:
        # Always release a transaction paused by the test hook, including on
        # assertion/monitor failures, so the ephemeral harness cannot hang.
        if barrier_id is not None:
            await root_db["_beta8_4_test_barriers"].update_one(
                {"_id": barrier_id, "state": "PAUSED"},
                {"$set": {"state": "RELEASED", "cleanup_release": True}},
            )
        for pending in (mutation_task, revoke_task):
            if pending is not None and not pending.done():
                try:
                    await asyncio.wait_for(pending, timeout=8)
                except Exception:
                    pending.cancel()
        await observer.close()
        await client.aclose()


async def _await_real_restart(
    root_db: Any,
    authority_url: str,
    barrier_id: str,
    label: str,
) -> None:
    print(f"BETA8_4_RESTART_AUTHORITY:{label}:pause", flush=True)
    observed_down = False
    async with httpx.AsyncClient(base_url=authority_url, timeout=0.75) as client:
        for _ in range(600):
            try:
                response = await client.get("/internal/health")
                if response.status_code == 200 and observed_down:
                    result = await root_db["_beta8_4_test_barriers"].update_one(
                        {"_id": barrier_id, "state": "PAUSED"},
                        {"$set": {"state": "RESTARTED", "health_restored_at": datetime.now(UTC)}},
                    )
                    assert result.matched_count == 1, "barreira não sobreviveu ao restart"
                    return
            except httpx.HTTPError:
                if not observed_down:
                    observed_down = True
                    print(f"BETA8_4_RESTART_AUTHORITY:{label}:down", flush=True)
            await asyncio.sleep(0.05)
    raise AssertionError("autoridade não foi observada indisponível e restaurada")


async def _restart_editorial_operation(
    root_db: Any, api_url: str, authority_url: str, run_id: str, phase: str,
) -> None:
    client, actor_id, _session_id = await _new_editor(root_db, api_url, f"restart-{phase}")
    block_id = _env("BETA8_3_BLOCK_ID")
    node_id = _env("BETA8_3_NODE_ID")
    key = f"beta84-restart-{phase}-0001"
    scope, kind = f"block:{block_id}", "block.update"
    operation_id = _operation_id(actor_id, scope, kind, key)
    barrier_id = await _arm(root_db, operation_id, phase)
    head = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
    revision = int(head["revision"])
    before = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
    task = asyncio.create_task(_request_for_operation(
        client, "block.update", block_id=block_id, node_id=node_id,
        revision=revision, key=key,
    ))
    try:
        await _wait_barrier(root_db, barrier_id)
        await _await_real_restart(root_db, authority_url, barrier_id, phase)
        try:
            first = await asyncio.wait_for(task, timeout=15)
            assert first.status_code == 503, f"resultado inicial após restart HTTP {first.status_code}"
        except httpx.HTTPError:
            pass  # The API connection itself may close as the RPC peer is killed.
        retried = await _request_for_operation(
            client, "block.update", block_id=block_id, node_id=node_id,
            revision=revision, key=key,
        )
        assert retried.status_code == 200, f"retry após restart HTTP {retried.status_code}: {retried.text}"
        if phase == "after_commit":
            assert retried.headers.get("idempotency-replayed") == "true"
            assert retried.headers.get("etag") == f'"editorial-rev-{revision + 1}"'
        else:
            assert retried.headers.get("idempotency-replayed") == "false"
            assert retried.headers.get("etag") == f'"editorial-rev-{revision + 1}"'
        operation_id = _operation_id(actor_id, scope, kind, key)
        assert await root_db["c8_beta8_1_history"].count_documents({"operation_id": operation_id}) == 1
        assert await root_db["_beta8_editorial_audit"].count_documents({"_id": operation_id}) == 1
        block = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
        assert block["editorial_revision"] == revision + 1
        assert block["title"] == "must-not-commit"
        assert int(before["editorial_revision"]) <= revision
    finally:
        await client.aclose()


async def _restart_staging_after_commit(
    root_db: Any, api_url: str, authority_url: str, run_id: str,
    stage_client: AsyncMongoClient,
) -> None:
    from curriculum_contract.beta_staging_contract import StagingPackage
    from services.beta8_3_internal_protocol import (
        EDITORIAL_AUTHORITY_AUDIENCE,
        StagingTransitionCommand,
        request_signature,
    )
    from services.beta_curriculum_staging import CurriculumStagingService

    client, actor_id, session_id = await _new_editor(root_db, api_url, "restart-stage")
    try:
        package = _stage_package(f"Beta 8.4 persistent restart {run_id[:10]}")
        stage_id = _env("BETA8_3_STAGE_RUN_ID")
        stage_service = CurriculumStagingService(
            stage_client[f"beta5_{stage_id}"], execution_id=stage_id,
            owner_token=_env("BETA8_3_STAGE_OWNER_TOKEN"),
        )
        staged = await stage_service.prepare(package)
        assert staged.state.value == "PREPARED"
        track = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        head = await root_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
        operation_id = f"beta8-op-beta84-stage-restart-{run_id[:12]}"
        command = StagingTransitionCommand(
            actor={"actor_id": actor_id, "session_id": session_id, "token_version": 0},
            operation_id=operation_id,
            expected_revision=int(track["revision"]),
            expected_previous_generation=head.get("generation_id") if head else None,
            package=StagingPackage.model_validate(package.model_dump(mode="json")),
        )
        body = json.dumps(
            command.model_dump(mode="json"), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode()
        path = "/internal/v1/staging/transitions"
        stager_secret = bytes.fromhex(_env("BETA8_3_STAGER_SECRET_HEX"))

        def signed_headers() -> dict[str, str]:
            timestamp = str(int(datetime.now(UTC).timestamp()))
            nonce = secrets.token_hex(24)
            return {
                "Content-Type": "application/json", "X-Beta8-Service": "trilhacode-stager",
                "X-Beta8-Timestamp": timestamp, "X-Beta8-Nonce": nonce,
                "X-Beta8-Signature": request_signature(
                    stager_secret, service_id="trilhacode-stager", method="POST",
                    audience=EDITORIAL_AUTHORITY_AUDIENCE,
                    path=path, timestamp=timestamp, nonce=nonce, body=body,
                ),
            }

        barrier_id = await _arm(root_db, operation_id, "after_commit")
        generation_id = f"beta8-generation-synthetic-{package.manifest.payload_sha256[:32]}"
        old_generation = command.expected_previous_generation
        async with httpx.AsyncClient(base_url=authority_url, timeout=8.0) as authority:
            first_task = asyncio.create_task(authority.post(path, content=body, headers=signed_headers()))
            await _wait_barrier(root_db, barrier_id, first_task)
            await _await_real_restart(root_db, authority_url, barrier_id, "staging_after_commit")
            try:
                first = await asyncio.wait_for(first_task, timeout=12)
                assert first.status_code >= 500
            except httpx.HTTPError:
                pass
            retry = await authority.post(path, content=body, headers=signed_headers())
            assert retry.status_code == 200, f"retry staging HTTP {retry.status_code}: {retry.text}"
            assert retry.json()["replayed"] is True
        # The bridge maps a staged package into a separate synthetic candidate
        # identity. Its source_revision preserves the full Beta 5 staging hash,
        # so use that provenance to locate the single recovered generation.
        generations = await root_db["_beta8_experimental_generations"].find(
            {"source_revision": f"synthetic:stage:{package.manifest.payload_sha256}"}
        ).to_list(length=2)
        assert len(generations) == 1, "restart duplicou ou perdeu a geração do lote"
        generation = generations[0]
        generation_id = generation["_id"]
        assert generation["batch_id"].startswith("beta8-fixture-")
        assert await root_db["_beta8_promotion_audit"].count_documents({"_id": operation_id}) == 1
        head_after = await root_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
        assert head_after["generation_id"] == generation_id
        if old_generation:
            assert await root_db["_beta8_experimental_generations"].find_one({"_id": old_generation})
        assert generation["fixture_label"] == "BETA8_SYNTHETIC_ONLY"

        # An ordinary draft edit advances the editorial revision without
        # changing the independent generation-pointer CAS sequence. Prepare a
        # second batch afterward to prove the two revision domains stay apart.
        edited_track = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        assert edited_track is not None
        edit_key = f"beta84-edit-between-generations-{run_id[:10]}"
        edit = await client.put(
            f"/api/blocks/{_env('BETA8_3_BLOCK_ID')}",
            json={"title": "draft edit between synthetic generations"},
            headers={
                "If-Match": f'"editorial-rev-{edited_track["revision"]}"',
                "Idempotency-Key": edit_key,
            },
        )
        assert edit.status_code == 200, f"edição entre gerações HTTP {edit.status_code}: {edit.text}"
        edited_track = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        assert edited_track is not None
        second_package = _stage_package(f"Beta 8.4 post-edit generation {run_id[:10]}")
        second_staged = await stage_service.prepare(second_package)
        assert second_staged.state.value == "PREPARED"
        head_before_second = await root_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
        assert head_before_second is not None and head_before_second["generation_id"] == generation_id
        second_operation_id = f"beta8-op-beta84-stage-second-{run_id[:12]}"
        second_command = StagingTransitionCommand(
            actor={"actor_id": actor_id, "session_id": session_id, "token_version": 0},
            operation_id=second_operation_id,
            expected_revision=int(edited_track["revision"]),
            expected_previous_generation=generation_id,
            package=StagingPackage.model_validate(second_package.model_dump(mode="json")),
        )
        body = json.dumps(
            second_command.model_dump(mode="json"), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode()
        async with httpx.AsyncClient(base_url=authority_url, timeout=8.0) as authority:
            second_transition = await authority.post(path, content=body, headers=signed_headers())
        assert second_transition.status_code == 200, (
            f"segunda geração após edição HTTP {second_transition.status_code}: {second_transition.text}"
        )
        assert second_transition.json()["replayed"] is False
        second_generations = await root_db["_beta8_experimental_generations"].find(
            {"source_revision": f"synthetic:stage:{second_package.manifest.payload_sha256}"}
        ).to_list(length=2)
        assert len(second_generations) == 1, "edição entre gerações perdeu ou duplicou a segunda geração"
        second_generation = second_generations[0]
        second_head = await root_db["_beta8_experimental_heads"].find_one({"_id": TRACK_ID})
        assert second_head is not None and second_head["generation_id"] == second_generation["_id"]
        assert second_head["revision"] == head_before_second["revision"] + 1
        assert second_generation["parent_revision"] == edited_track["revision"]
        assert second_generation["revision"] == edited_track["revision"] + 1
        assert await root_db["_beta8_promotion_audit"].count_documents(
            {"_id": second_operation_id}
        ) == 1
        print("BETA8_4_STAGING_REAL_RESTART: PASS; durable generation reconciled and retry was idempotent", flush=True)
    finally:
        await client.aclose()


async def _verify_internal_channel_attacks(root_db: Any, api_url: str, authority_url: str) -> None:
    """Exercise signed/unsigned protocol attacks over the real service boundary."""
    from services.beta8_3_internal_protocol import (
        EDITORIAL_AUTHORITY_AUDIENCE,
        EditorialMutationCommand,
        request_signature,
    )

    client, actor_id, session_id = await _new_editor(root_db, api_url, "rpc-attacks")
    try:
        block_id = _env("BETA8_3_BLOCK_ID")
        current = await root_db["c8_beta8_1_tracks"].find_one({"_id": TRACK_ID})
        assert current is not None
        revision = int(current["revision"])
        operation_id = "http_" + secrets.token_hex(32)
        base_command = {
            "operation": "block.update",
            "actor": {"actor_id": actor_id, "session_id": session_id, "token_version": 0},
            "operation_id": operation_id,
            "expected_revision": revision,
            "block_id": block_id,
            "node_id": None,
            "changes": {"title": "must-not-commit"},
            "block": None,
        }
        EditorialMutationCommand.model_validate(base_command)
        body = json.dumps(base_command, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode()
        tampered_command = base_command | {"changes": {"title": "tampered"}}
        tampered_body = json.dumps(tampered_command, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False).encode()
        arbitrary = base_command | {"collection": "users"}
        arbitrary_body = json.dumps(arbitrary, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()
        path = "/internal/v1/editorial/mutations"
        secret = bytes.fromhex(_env("BETA8_3_SERVICE_SECRET_HEX"))

        def headers_for(
            signed_body: bytes, *, service: str = "trilhacode-api",
            audience: str = EDITORIAL_AUTHORITY_AUDIENCE,
            sent_body_nonce: str | None = None, timestamp: str | None = None,
        ) -> dict[str, str]:
            issued = timestamp or str(int(datetime.now(UTC).timestamp()))
            nonce = sent_body_nonce or secrets.token_hex(24)
            return {
                "Content-Type": "application/json",
                "X-Beta8-Service": service,
                "X-Beta8-Timestamp": issued,
                "X-Beta8-Nonce": nonce,
                "X-Beta8-Signature": request_signature(
                    secret, service_id=service, method="POST", path=path,
                    audience=audience,
                    timestamp=issued, nonce=nonce, body=signed_body,
                ),
            }

        async with httpx.AsyncClient(base_url=authority_url, timeout=10.0) as authority:
            unsigned = await authority.post(path, content=body, headers={"Content-Type": "application/json"})
            assert unsigned.status_code == 401
            altered = await authority.post(
                path, content=tampered_body, headers=headers_for(body),
            )
            assert altered.status_code == 401, "corpo adulterado foi aceito pelo RPC"
            wrong_service = await authority.post(
                path, content=body, headers=headers_for(body, service="trilhacode-stager"),
            )
            assert wrong_service.status_code == 401, "identidade de serviço divergente foi aceita"
            wrong_audience = await authority.post(
                path, content=body,
                headers=headers_for(body, audience="trilhacode-stager"),
            )
            assert wrong_audience.status_code == 401, "audiência interna divergente foi aceita"
            expired_timestamp = str(int(datetime.now(UTC).timestamp()) - 180)
            expired = await authority.post(
                path, content=body, headers=headers_for(body, timestamp=expired_timestamp),
            )
            assert expired.status_code == 401, "mensagem interna expirada foi aceita"
            arbitrary_result = await authority.post(
                path, content=arbitrary_body, headers=headers_for(arbitrary_body),
            )
            assert arbitrary_result.status_code == 422, "comando com coleção arbitrária não foi rejeitado"

        after = await root_db.content_blocks.find_one({"_id": ObjectId(block_id)})
        assert after is not None and after.get("title") != "must-not-commit"
        assert await root_db["_beta8_editorial_audit"].count_documents({"_id": operation_id}) == 0
        assert await root_db["c8_beta8_1_history"].count_documents({"operation_id": operation_id}) == 0
        print("BETA8_4_RPC_ATTACKS: PASS; unsigned, altered, expired, wrong-service and arbitrary-collection commands denied", flush=True)
    finally:
        await client.aclose()


async def _verify_beta8_4() -> None:
    run_id, db_name, root_uri = _gate()
    root = AsyncMongoClient(root_uri, appname="beta8-4-verifier", tz_aware=True)
    stage_client = AsyncMongoClient(
        _env("BETA8_3_STAGE_WRITE_URI"), appname="beta8-4-stage-writer", tz_aware=True,
    )
    try:
        api_url = _env("BETA8_3_API_URL")
        authority_url = _env("BETA8_3_AUTHORITY_URL")
        root_db = root[db_name]
        await _verify_internal_channel_attacks(root_db, api_url, authority_url)
        await _verify_revocation_races(root_db, api_url, run_id)
        await _verify_revocation_serializes_with_open_transaction(
            root_db, api_url, root_uri, db_name,
        )
        await _restart_editorial_operation(root_db, api_url, authority_url, run_id, "before_commit")
        await _restart_editorial_operation(root_db, api_url, authority_url, run_id, "after_commit")
        await _restart_staging_after_commit(root_db, api_url, authority_url, run_id, stage_client)
        print("BETA8_4_PERSISTED_RECOVERY: PASS; authority container restarts reconciled from MongoDB", flush=True)
    finally:
        await stage_client.close()
        await root.close()


async def main() -> None:
    if os.environ.get("BETA8_4_TEST_BARRIERS") != "1":
        raise RuntimeError("Beta 8.4 exige barreiras explícitas no harness descartável")
    await _verify()
    await _verify_beta8_4()


if __name__ == "__main__":
    asyncio.run(main())
