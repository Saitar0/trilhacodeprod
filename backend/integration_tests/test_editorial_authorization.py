from __future__ import annotations

import asyncio
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from bson import ObjectId
from pymongo import AsyncMongoClient

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_editorial_authorization import (  # noqa: E402
    AuthorizationCode,
    EditorialAuthorizationError,
    MongoEditorialAuthorizationGate,
)
from curriculum_contract.experimental_editorial_privacy import (  # noqa: E402
    HmacKeyUnavailable,
    HmacPurpose,
    VersionedEditorialHmacKeyring,
)
from curriculum_contract.experimental_editorial_replay_policy import (  # noqa: E402
    InternalReconciliationAuthority,
    ReceiptLookupState,
    lookup_external_receipt,
    lookup_internal_committed_receipt,
)
from curriculum_contract.mongodb_editorial_revision_adapter import CommitOutcomeUnknown  # noqa: E402
from integration_tests.editorial_authorization_harness import (  # noqa: E402
    block_audit_participant,
    c11_test_uri,
    isolated_database,
    prepare_authorized_update,
    ready_track,
    resolve_requested_block_scope,
)


def _keyring(current: str = "k1", *, include_old: bool = True):
    keys = {"k2": b"c11-content-hmac-key-version-two-32bytes"}
    if include_old:
        keys["k1"] = b"c11-content-hmac-key-version-one-32bytes"
    if current not in keys:
        keys[current] = b"c11-content-hmac-key-version-one-32bytes"
    return VersionedEditorialHmacKeyring(keys, current_key_id=current)


def test_c11_uri_accepts_only_explicit_uncredentialed_loopback_replica_set(monkeypatch):
    valid = "mongodb://127.0.0.1:29131/?replicaSet=rsC11"
    monkeypatch.setenv("C11_TEST_MONGODB_URI", valid)
    assert c11_test_uri() == valid
    for unsafe in (
        "mongodb://user:pass@127.0.0.1:29131/?replicaSet=rsC11",
        "mongodb://localhost:29131/?replicaSet=rsC11",
        "mongodb://127.0.0.1:27017/?replicaSet=rsC11",
        "mongodb://127.0.0.1:29131/?replicaSet=rsOther",
        "mongodb+srv://example.invalid/?replicaSet=rsC11",
    ):
        monkeypatch.setenv("C11_TEST_MONGODB_URI", unsafe)
        with pytest.raises(RuntimeError):
            c11_test_uri()


async def _internal_lookup(database, context, operation_id):
    authority = context["reconciliation_authority"]
    return await lookup_internal_committed_receipt(
        database,
        namespace="c8_c11",
        track_id=context["track_id"],
        operation_id=operation_id,
        authority=authority,
        permit=authority.issue(
            database_name=database.name,
            namespace="c8_c11",
            track_id=context["track_id"],
            operation_id=operation_id,
        ),
    )


async def _prepare(database, context, block_id, keyring, *, key="stable-c11-key-000001", key_id=None, title="synthetic-private-title"):
    operation_id = keyring.operation_id_candidates(
        actor_id=context["actor_id"],
        track_id=context["track_id"],
        operation_kind="block.update",
        idempotency_key=key,
    )[0]
    capability, prepared, payload = await prepare_authorized_update(
        database,
        context,
        block_id=block_id,
        requested_track_id=context["track_id"],
        expected_revision=0,
        operation_id=operation_id,
        changes={"title": title},
        keyring=keyring,
        key_id=key_id,
    )
    return capability, prepared, payload, operation_id


def test_authorization_requires_authenticated_content_write_and_explicit_track_scope():
    async def run():
        async with isolated_database("iam_scope") as (client, database):
            context = await ready_track(client, database)
            gate = context["gate"]
            allowed = await gate.issue_capability(
                context["principal"], context["principal_authority"],
                track_id=context["track_id"], operation_kind="block.update",
                operation_id="c11_scope_allowed_0001", expected_revision=0,
                writer_context=context["writer_context"],
            )
            assert allowed.code is AuthorizationCode.ALLOWED

            student = context["principal_authority"].attest(
                actor_id=context["actor_id"], session_id=context["session_id"],
                role="student", permissions={"progress.write"},
            )
            denied_permission = await gate.issue_capability(
                student, context["principal_authority"], track_id=context["track_id"],
                operation_kind="block.update", operation_id="c11_scope_student_0001",
                expected_revision=0, writer_context=context["writer_context"],
            )
            assert denied_permission.code is AuthorizationCode.PERMISSION_INSUFFICIENT

            other_actor = context["principal_authority"].attest(
                actor_id="actor-without-track-grant", session_id="session-without-grant",
                role="editor", permissions={"content.write"},
            )
            denied_scope = await gate.issue_capability(
                other_actor, context["principal_authority"], track_id=context["track_id"],
                operation_kind="block.update", operation_id="c11_scope_other_actor_01",
                expected_revision=0, writer_context=context["writer_context"],
            )
            assert denied_scope.code is AuthorizationCode.TRACK_SCOPE_DENIED

            invalid_session = context["principal_authority"].attest(
                actor_id=context["actor_id"], session_id=context["session_id"],
                role="editor", permissions={"content.write"}, session_valid=False,
            )
            denied_session = await gate.issue_capability(
                invalid_session, context["principal_authority"], track_id=context["track_id"],
                operation_kind="block.update", operation_id="c11_scope_bad_session_01",
                expected_revision=0, writer_context=context["writer_context"],
            )
            assert denied_session.code is AuthorizationCode.SESSION_INVALID

            forged = await gate.issue_capability(
                {"id": context["actor_id"], "permissions": ["content.write"]},
                context["principal_authority"], track_id=context["track_id"],
                operation_kind="block.update", operation_id="c11_scope_forged_0001",
                expected_revision=0, writer_context=context["writer_context"],
            )
            assert forged.code is AuthorizationCode.AUTHENTICATION_REQUIRED

            no_grant_admin = await ready_track(
                client, database, track_id="track-admin-explicit-only",
                actor_id="synthetic-admin-no-global", session_id="synthetic-admin-session",
                role="admin", grant_track_id="track-admin-explicit-only",
            )
            admin_other_track = await no_grant_admin["gate"].issue_capability(
                no_grant_admin["principal"], no_grant_admin["principal_authority"],
                track_id="another-track", operation_kind="block.update",
                operation_id="c11_admin_implicit_denied1", expected_revision=0,
                writer_context=no_grant_admin["writer_context"],
            )
            assert admin_other_track.code is AuthorizationCode.TRACK_SCOPE_DENIED

            explicit_global = await ready_track(
                client, database, track_id="track-admin-global-target",
                actor_id="synthetic-admin-global", session_id="synthetic-admin-global-session",
                role="admin", global_admin_scope=True,
            )
            admin_allowed = await explicit_global["gate"].issue_capability(
                explicit_global["principal"], explicit_global["principal_authority"],
                track_id=explicit_global["track_id"], operation_kind="block.update",
                operation_id="c11_admin_explicit_allow1", expected_revision=0,
                writer_context=explicit_global["writer_context"],
            )
            assert admin_allowed.code is AuthorizationCode.ALLOWED

    asyncio.run(run())


def test_capability_is_server_signed_bound_and_fence_is_not_authorization():
    async def run():
        async with isolated_database("capability") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            allowed_scope = await resolve_requested_block_scope(
                database, block_id=block_id, requested_track_id=context["track_id"]
            )
            mismatched_scope = await resolve_requested_block_scope(
                database, block_id=block_id, requested_track_id="different-track"
            )
            missing_scope = await resolve_requested_block_scope(
                database, block_id=ObjectId(), requested_track_id=context["track_id"]
            )
            assert allowed_scope == (AuthorizationCode.ALLOWED, context["track_id"])
            assert mismatched_scope == (AuthorizationCode.TRACK_SCOPE_DENIED, None)
            assert missing_scope == (AuthorizationCode.RESOURCE_NOT_FOUND, None)
            keyring = _keyring()
            capability, prepared, payload, _ = await _prepare(
                database, context, block_id, keyring
            )
            fake_fence_only = await context["gate"].issue_capability(
                context["principal_authority"].attest(
                    actor_id="no-grant", session_id="no-grant-session", role="editor",
                    permissions={"content.write"},
                ),
                context["principal_authority"], track_id=context["track_id"],
                operation_kind="block.update", operation_id="c11_fence_not_iam_001",
                expected_revision=0, writer_context=context["writer_context"],
            )
            assert fake_fence_only.code is AuthorizationCode.TRACK_SCOPE_DENIED
            assert payload["intent_hmac"]["digest"] not in payload.get("title", "")

            tampered = replace(capability, track_id="other-track")
            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "synthetic-private-title"},
                resource_ref_hmac=payload["resource_ref_hmac"],
            )
            with pytest.raises(EditorialAuthorizationError):
                await context["gate"].commit_authorized(
                    context["adapter"], context["principal"], context["principal_authority"],
                    tampered, prepared, participant=participant,
                )
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert (await database.content_blocks.find_one({"_id": block_id}))["title"] == "old"

    asyncio.run(run())


def test_commit_privacy_replay_after_removal_and_revocation_policy():
    async def run():
        async with isolated_database("replay_privacy") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            keyring = _keyring()
            private_value = "synthetic-private-answer-never-in-history"
            capability, prepared, payload, operation_id = await _prepare(
                database, context, block_id, keyring, title=private_value
            )
            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": private_value},
                resource_ref_hmac=payload["resource_ref_hmac"],
            )
            first = await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                capability, prepared, participant=participant,
            )
            assert (first.revision, first.parent_revision, first.replayed) == (1, 0, False)

            from curriculum_contract.editorial_revision_protocol import IdempotencyConflict
            with pytest.raises(IdempotencyConflict):
                await prepare_authorized_update(
                    database, context, block_id=block_id,
                    requested_track_id=context["track_id"], expected_revision=0,
                    operation_id=operation_id,
                    changes={"title": "different-intent-for-same-key"}, keyring=keyring,
                )

            operation = await database["c8_c11_operations"].find_one(
                {"track_id": context["track_id"], "operation_id": operation_id}
            )
            history = await database["c8_c11_history"].find_one({})
            audit = await database.edit_history.find_one({})
            for record in (operation, history, audit):
                assert private_value not in str(record)
                assert str(block_id) not in str(record)
            assert operation["payload_json"].find("intent_hmac") >= 0
            assert "payload" not in (await context["gate"]._authorizations.find_one({"actor_id": context["actor_id"]}))

            lookup = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=capability,
                authorization_gate=context["gate"], principal=context["principal"],
                principal_authority=context["principal_authority"],
            )
            assert lookup.state is ReceiptLookupState.FOUND
            assert lookup.receipt is not None
            assert (lookup.receipt.revision, lookup.receipt.parent_revision) == (1, 0)
            assert not hasattr(lookup.receipt, "operation_id")

            replay_cap, replay_prepared, replay_payload = await prepare_authorized_update(
                database, context, block_id=block_id, requested_track_id=context["track_id"],
                expected_revision=0, operation_id=operation_id,
                changes={"title": private_value}, keyring=keyring,
            )
            assert replay_payload == payload
            replay = await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                replay_cap, replay_prepared, participant=participant,
            )
            assert replay.replayed and replay.revision == first.revision
            assert await database.edit_history.count_documents({}) == 1

            await database.content_blocks.delete_one({"_id": block_id})
            after_removal_cap, after_removal_prepared, _ = await prepare_authorized_update(
                database, context, block_id=block_id,
                requested_track_id=context["track_id"], expected_revision=0,
                operation_id=operation_id, changes={"title": private_value}, keyring=keyring,
            )
            after_removal = await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                after_removal_cap, after_removal_prepared, participant=participant,
            )
            assert after_removal.replayed
            assert await database.content_blocks.find_one({"_id": block_id}) is None
            assert await database.edit_history.count_documents({}) == 1

            await context["gate"].revoke_synthetic_scope(
                actor_id=context["actor_id"], track_id=context["track_id"]
            )
            denied_external = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=after_removal_cap,
                authorization_gate=context["gate"], principal=context["principal"],
                principal_authority=context["principal_authority"],
            )
            assert denied_external.state is ReceiptLookupState.DENIED
            internal = await _internal_lookup(database, context, operation_id)
            assert internal.state is ReceiptLookupState.FOUND
            assert internal.receipt == lookup.receipt
            altered_role = context["principal_authority"].attest(
                actor_id=context["actor_id"], session_id=context["session_id"],
                role="student", permissions={"progress.write"},
            )
            role_revoked_replay = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=after_removal_cap,
                authorization_gate=context["gate"], principal=altered_role,
                principal_authority=context["principal_authority"],
            )
            assert role_revoked_replay.state is ReceiptLookupState.DENIED
            unauthorized_authority = InternalReconciliationAuthority(
                b"different-internal-reconciliation-key-32bytes"
            )
            with pytest.raises(PermissionError):
                await lookup_internal_committed_receipt(
                    database, namespace="c8_c11", track_id=context["track_id"],
                    operation_id=operation_id, authority=unauthorized_authority,
                    permit=context["reconciliation_authority"].issue(
                        database_name=database.name,
                        namespace="c8_c11",
                        track_id=context["track_id"],
                        operation_id=operation_id,
                    ),
                )
            with pytest.raises(PermissionError):
                await lookup_internal_committed_receipt(
                    database, namespace="c8_c11", track_id="other-track",
                    operation_id=operation_id,
                    authority=context["reconciliation_authority"],
                    permit=context["reconciliation_authority"].issue(
                        database_name=database.name,
                        namespace="c8_c11",
                        track_id=context["track_id"],
                        operation_id=operation_id,
                    ),
                )

    asyncio.run(run())


def test_revocation_after_prepare_prevents_commit_and_internal_reconciliation_is_read_only():
    async def run():
        async with isolated_database("revoke_precommit") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            keyring = _keyring()
            capability, prepared, payload, operation_id = await _prepare(
                database, context, block_id, keyring
            )
            await context["gate"].revoke_synthetic_scope(
                actor_id=context["actor_id"], track_id=context["track_id"]
            )
            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "never-committed"},
                resource_ref_hmac=payload["resource_ref_hmac"],
            )
            with pytest.raises(EditorialAuthorizationError) as error:
                await context["gate"].commit_authorized(
                    context["adapter"], context["principal"], context["principal_authority"],
                    capability, prepared, participant=participant,
                )
            assert error.value.code is AuthorizationCode.AUTHORIZATION_REVOKED
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert (await database.content_blocks.find_one({"_id": block_id}))["title"] == "old"
            assert await database.edit_history.count_documents({}) == 0
            pending = await _internal_lookup(database, context, operation_id)
            assert pending.state is ReceiptLookupState.PENDING

            before_context = await ready_track(
                client, database, track_id="track-revoked-before-prepare",
                actor_id="actor-revoked-before-prepare", session_id="session-revoked-before-prepare",
            )
            before_block = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": before_block, "track_id": before_context["track_id"], "title": "old"}
            )
            await before_context["gate"].revoke_synthetic_scope(
                actor_id=before_context["actor_id"], track_id=before_context["track_id"]
            )
            before_op = _keyring().operation_id_candidates(
                actor_id=before_context["actor_id"], track_id=before_context["track_id"],
                operation_kind="block.update", idempotency_key="before-revoked-c11-0001",
            )[0]
            with pytest.raises(EditorialAuthorizationError):
                await prepare_authorized_update(
                    database, before_context, block_id=before_block,
                    requested_track_id=before_context["track_id"], expected_revision=0,
                    operation_id=before_op, changes={"title": "blocked"}, keyring=_keyring(),
                )
            assert await database.c8_c11_operations.count_documents(
                {"track_id": before_context["track_id"]}
            ) == 0

    asyncio.run(run())


def test_audit_failure_and_cancellation_abort_authz_revision_and_editorial_writes():
    async def run():
        async with isolated_database("rollback_cancel") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            keyring = _keyring()
            capability, prepared, payload, _ = await _prepare(
                database, context, block_id, keyring, key="failure-key-c11-000001"
            )
            async def fail_audit():
                raise RuntimeError("synthetic audit failure")

            failing_participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "uncommitted"},
                resource_ref_hmac=payload["resource_ref_hmac"], before_audit=fail_audit,
            )
            with pytest.raises(RuntimeError, match="synthetic audit failure"):
                await context["gate"].commit_authorized(
                    context["adapter"], context["principal"], context["principal_authority"],
                    capability, prepared, participant=failing_participant,
                )
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert (await database.content_blocks.find_one({"_id": block_id}))["title"] == "old"
            assert await database.edit_history.count_documents({}) == 0
            grant = await context["gate"]._authorizations.find_one({"actor_id": context["actor_id"]})
            assert grant["use_sequence"] == 0

            entered = asyncio.Event()
            hold = asyncio.Event()
            cap2, prepared2, payload2, _ = await _prepare(
                database, context, block_id, keyring, key="cancel-key-c11-000001"
            )
            async def pause_after_block_update():
                entered.set()
                await hold.wait()
            participant2 = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "cancelled-before-commit"},
                resource_ref_hmac=payload2["resource_ref_hmac"],
                before_audit=pause_after_block_update,
            )
            pending = asyncio.create_task(context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                cap2, prepared2, participant=participant2,
            ))
            await asyncio.wait_for(entered.wait(), timeout=4)
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert (await database.content_blocks.find_one({"_id": block_id}))["title"] == "old"
            assert await database.edit_history.count_documents({}) == 0
            grant = await context["gate"]._authorizations.find_one({"actor_id": context["actor_id"]})
            assert grant["use_sequence"] == 0

    asyncio.run(run())


def test_revocation_and_commit_are_serialized_by_the_same_authorization_document():
    async def run():
        async with isolated_database("revoke_commit_race") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            capability, prepared, payload, _ = await _prepare(
                database, context, block_id, _keyring(), key="race-key-c11-000001"
            )
            entered = asyncio.Event()
            release = asyncio.Event()

            async def pause_inside_transaction():
                entered.set()
                await release.wait()

            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "race-update"},
                resource_ref_hmac=payload["resource_ref_hmac"],
                before_audit=pause_inside_transaction,
            )
            commit_task = asyncio.create_task(context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                capability, prepared, participant=participant,
            ))
            await asyncio.wait_for(entered.wait(), timeout=4)

            second_client = AsyncMongoClient(
                __import__("integration_tests.editorial_authorization_harness", fromlist=["c11_test_uri"]).c11_test_uri(),
                serverSelectionTimeoutMS=4000,
                appname="trilhacode-c11-revoker-client",
            )
            try:
                revoker = MongoEditorialAuthorizationGate(
                    second_client[database.name], namespace="c8_c11",
                    capability_key=b"c11-synthetic-capability-signing-key-32-bytes",
                )
                revoke_task = asyncio.create_task(revoker.revoke_synthetic_scope(
                    actor_id=context["actor_id"], track_id=context["track_id"]
                ))
                await asyncio.sleep(0.05)
                release.set()
                commit_result, revoke_result = await asyncio.gather(
                    commit_task, revoke_task, return_exceptions=True
                )
                assert revoke_result is True
                revision = await context["adapter"].current_revision(context["track_id"])
                block = await database.content_blocks.find_one({"_id": block_id})
                audits = await database.edit_history.count_documents({})
                if not isinstance(commit_result, Exception):
                    assert commit_result.revision == 1
                    assert revision == 1 and block["title"] == "race-update" and audits == 1
                else:
                    assert isinstance(commit_result, EditorialAuthorizationError)
                    assert commit_result.code is AuthorizationCode.AUTHORIZATION_REVOKED
                    assert revision == 0 and block["title"] == "old" and audits == 0
            finally:
                release.set()
                await second_client.close()

    asyncio.run(run())


def test_key_rotation_replay_and_unknown_commit_response_reconcile_without_mutation():
    async def run():
        async with isolated_database("rotation_reconcile") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            old_ring = _keyring("k1", include_old=False)
            cap, prepared, payload, old_operation_id = await _prepare(
                database, context, block_id, old_ring, key="rotation-key-c11-000001",
                key_id="k1", title="rotated-private-title",
            )
            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "rotated-private-title"},
                resource_ref_hmac=payload["resource_ref_hmac"],
            )
            receipt = await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                cap, prepared, participant=participant,
            )
            assert receipt.revision == 1

            rotated_ring = _keyring("k2", include_old=True)
            candidates = rotated_ring.operation_id_candidates(
                actor_id=context["actor_id"], track_id=context["track_id"],
                operation_kind="block.update", idempotency_key="rotation-key-c11-000001",
            )
            assert old_operation_id in candidates
            assert rotated_ring.available_key_ids
            rotated_cap, rotated_prepared, _ = await prepare_authorized_update(
                database, context, block_id=block_id, requested_track_id=context["track_id"],
                expected_revision=0, operation_id=old_operation_id,
                changes={"title": "rotated-private-title"}, keyring=rotated_ring,
                key_id="k1",
            )
            replay = await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                rotated_cap, rotated_prepared, participant=participant,
            )
            assert replay.replayed and replay.revision == 1
            with pytest.raises(HmacKeyUnavailable):
                rotated_ring.fingerprint(
                    HmacPurpose.INTENT,
                    {"x": 1}, key_id="retired-key",
                )

            # A synthetic lost response after a real commit models response loss;
            # it is not a MongoDB-labeled UnknownTransactionCommitResult.
            try:
                raise CommitOutcomeUnknown(context["track_id"], old_operation_id)
            except CommitOutcomeUnknown:
                recovered = await _internal_lookup(database, context, old_operation_id)
            assert recovered.state is ReceiptLookupState.FOUND
            assert recovered.receipt is not None and recovered.receipt.revision == 1
            assert await context["adapter"].current_revision(context["track_id"]) == 1
            assert await database.edit_history.count_documents({}) == 1

    asyncio.run(run())


def test_external_receipt_rejects_forged_capability_even_when_operation_exists():
    async def run():
        async with isolated_database("forged_receipt") as (client, database):
            context = await ready_track(client, database)
            block_id = ObjectId()
            await database.content_blocks.insert_one(
                {"_id": block_id, "track_id": context["track_id"], "title": "old"}
            )
            keyring = _keyring()
            capability, prepared, payload, operation_id = await _prepare(
                database, context, block_id, keyring
            )
            participant = block_audit_participant(
                database, block_id=block_id, track_id=context["track_id"],
                actor_id=context["actor_id"], changes={"title": "new"},
                resource_ref_hmac=payload["resource_ref_hmac"],
            )
            await context["gate"].commit_authorized(
                context["adapter"], context["principal"], context["principal_authority"],
                capability, prepared, participant=participant,
            )
            forged = replace(capability, operation_id="another-operation")
            role_changed = context["principal_authority"].attest(
                actor_id=context["actor_id"], session_id=context["session_id"],
                role="admin", permissions={"content.write"},
            )
            changed_role_result = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=capability,
                authorization_gate=context["gate"], principal=role_changed,
                principal_authority=context["principal_authority"],
            )
            result = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=forged,
                authorization_gate=context["gate"], principal=context["principal"],
                principal_authority=context["principal_authority"],
            )
            wrong_track_result = await lookup_external_receipt(
                database, namespace="c8_c11", track_id="another-track",
                operation_id=operation_id, capability=capability,
                authorization_gate=context["gate"], principal=context["principal"],
                principal_authority=context["principal_authority"],
            )
            no_capability = await lookup_external_receipt(
                database, namespace="c8_c11", track_id=context["track_id"],
                operation_id=operation_id, capability=None,
                authorization_gate=context["gate"], principal=context["principal"],
                principal_authority=context["principal_authority"],
            )
            assert result.state is ReceiptLookupState.DENIED
            assert wrong_track_result.state is ReceiptLookupState.DENIED
            assert changed_role_result.state is ReceiptLookupState.DENIED
            assert no_capability.state is ReceiptLookupState.DENIED

    asyncio.run(run())
