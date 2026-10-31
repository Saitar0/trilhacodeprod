from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from pymongo import AsyncMongoClient, monitoring

from curriculum_contract.experimental_editorial_iam_authority import (
    AuthorizationCode,
    EditorialAuthorizationError,
    MongoEditorialIAMAuthority,
)
from integration_tests.editorial_iam_authority_harness import (
    authorize_and_prepare,
    c12_test_uri,
    isolated_database,
    ready_experiment,
    synthetic_block_audit_participant,
)


def _commit(context, capability, prepared, *, title="synthetic-updated", before_audit=None):
    database = context["database"]
    operation_id = prepared.operation_id
    participant = synthetic_block_audit_participant(
        database,
        block_id=context["block_id"],
        track_id=context["track_id"],
        actor_id=context["actor_id"],
        operation_id=operation_id,
        title=title,
        before_audit=before_audit,
    )
    guarded = context["authority"].transaction_participant(capability, participant)
    return context["adapter"].commit(prepared, context["credential"], participant=guarded)


def test_same_mongodb_commit_checks_principal_session_grant_and_editorial_cas():
    async def run():
        async with isolated_database("same_store_commit") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(context, operation_id="c12_same_store_0001")
            assert decision.allowed
            receipt = await _commit(context, decision.capability, prepared)
            assert receipt.revision == 1
            assert await context["adapter"].current_revision(context["track_id"]) == 1
            assert (await database["content_blocks"].find_one({"_id": context["block_id"]}))["title"] == "synthetic-updated"
            assert await database["edit_history"].count_documents({"operation_id": prepared.operation_id}) == 1
            principal = await database["c12_iam_principals"].find_one({"_id": context["actor_id"]})
            session = await database["c12_iam_sessions"].find_one({"actor_id": context["actor_id"]})
            grant = await database["c12_track_grants"].find_one({"actor_id": context["actor_id"]})
            assert principal["use_sequence"] == session["use_sequence"] == grant["use_sequence"] == 1
    asyncio.run(run())


@pytest.mark.parametrize("revocation", ["grant", "role", "permission", "session"])
def test_revocation_before_commit_rejects_stale_capability_without_partial_editorial_state(revocation):
    async def run():
        async with isolated_database(f"revoke_{revocation}") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(
                context, operation_id=f"c12_revoked_{revocation}_0001"
            )
            assert decision.allowed
            authority = context["authority"]
            if revocation == "grant":
                assert await authority.revoke_grant(
                    actor_id=context["actor_id"], track_id=context["track_id"],
                    revoked_by="c12_admin_synthetic",
                )
            elif revocation in {"role", "permission"}:
                assert await authority.change_principal(
                    actor_id=context["actor_id"],
                    role="student" if revocation == "role" else "editor",
                    permissions=("progress.write",) if revocation == "permission" else None,
                    changed_by="c12_admin_synthetic",
                )
            else:
                assert await authority.revoke_session(
                    actor_id=context["actor_id"], session_id=context["session_id"],
                    changed_by="c12_admin_synthetic",
                )
            with pytest.raises(EditorialAuthorizationError) as error:
                await _commit(context, decision.capability, prepared)
            assert error.value.code == AuthorizationCode.AUTHORIZATION_REVOKED
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert (await database["content_blocks"].find_one({"_id": context["block_id"]}))["title"] == "synthetic-original"
            assert await database["edit_history"].count_documents({}) == 0
            for collection_name in (
                "c12_iam_principals", "c12_iam_sessions", "c12_track_grants",
            ):
                record = await database[collection_name].find_one({"actor_id": context["actor_id"]})
                if record is None and collection_name == "c12_iam_principals":
                    record = await database[collection_name].find_one({"_id": context["actor_id"]})
                assert record["use_sequence"] == 0
    asyncio.run(run())


def test_track_mismatch_and_unexplicit_admin_scope_fail_closed():
    async def run():
        async with isolated_database("scope_denied") as (client, database):
            context = await ready_experiment(client, database)
            mismatched = await context["authority"].authorize(
                actor_id=context["actor_id"], session_id=context["session_id"],
                resolved_track_id=context["track_id"], requested_track_id="other_track",
                operation="block.update",
            )
            assert mismatched.code == AuthorizationCode.TRACK_SCOPE_DENIED
            assert mismatched.capability is None

            admin = await ready_experiment(
                client, database, actor_id="c12_admin_no_global", track_id="c12_admin_track",
                role="admin", global_admin_scope=False,
            )
            denied = await admin["authority"].authorize(
                actor_id=admin["actor_id"], session_id=admin["session_id"],
                resolved_track_id="another_track", operation="block.update",
            )
            assert denied.code == AuthorizationCode.TRACK_SCOPE_DENIED
    asyncio.run(run())


def test_explicit_global_admin_grant_is_scoped_to_admin_role():
    async def run():
        async with isolated_database("global_admin_scope") as (client, database):
            context = await ready_experiment(
                client, database, actor_id="c12_admin_global", track_id="c12_admin_track",
                role="admin", global_admin_scope=True,
            )
            allowed = await context["authority"].authorize(
                actor_id=context["actor_id"], session_id=context["session_id"],
                resolved_track_id="another_track", operation="block.update",
            )
            assert allowed.allowed
            assert allowed.capability.global_admin_scope is True
            assert allowed.capability.grant_scope_track == "*"
            await context["authority"].change_principal(
                actor_id=context["actor_id"], role="editor", changed_by="c12_admin_synthetic"
            )
            denied = await context["authority"].authorize(
                actor_id=context["actor_id"], session_id=context["session_id"],
                resolved_track_id="another_track", operation="block.update",
            )
            assert denied.code == AuthorizationCode.TRACK_SCOPE_DENIED
    asyncio.run(run())


def test_capability_is_server_issued_and_bound_to_actor_track_operation_and_fence_is_separate():
    async def run():
        async with isolated_database("capability_scope") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(context, operation_id="c12_capability_0001")
            assert decision.allowed
            forged = type(decision.capability)(
                actor_id="other_actor", session_digest=decision.capability.session_digest,
                role=decision.capability.role, track_id=decision.capability.track_id,
                operation=decision.capability.operation,
                grant_scope_track=decision.capability.grant_scope_track,
                global_admin_scope=decision.capability.global_admin_scope,
                principal_epoch=decision.capability.principal_epoch,
                session_epoch=decision.capability.session_epoch,
                grant_id=decision.capability.grant_id,
                grant_epoch=decision.capability.grant_epoch,
                _signature=decision.capability._signature,
                _issuer_seal=decision.capability._issuer_seal,
            )
            with pytest.raises(EditorialAuthorizationError) as error:
                context["authority"].transaction_participant(forged, _noop)
            assert error.value.code == AuthorizationCode.CAPABILITY_INVALID
            assert prepared.fencing_token == context["fence"]
            assert not hasattr(decision.capability, "fencing_token")
    async def _noop(_session, _receipt):
        return None
    asyncio.run(run())


def test_authorization_storage_failure_denies_instead_of_granting_access():
    async def run():
        async with isolated_database("auth_read_failure") as (client, database):
            context = await ready_experiment(client, database)

            class Unavailable:
                async def find_one(self, *_args, **_kwargs):
                    raise RuntimeError("synthetic authorization store unavailable")

            original = context["authority"]._principals
            context["authority"]._principals = Unavailable()
            try:
                decision = await context["authority"].authorize(
                    actor_id=context["actor_id"], session_id=context["session_id"],
                    resolved_track_id=context["track_id"], operation="block.update",
                )
            finally:
                context["authority"]._principals = original
            assert decision.code == AuthorizationCode.INDETERMINATE
            assert decision.capability is None
    asyncio.run(run())


def test_operation_specific_permission_and_expired_session_are_checked_fail_closed():
    async def run():
        async with isolated_database("operation_session") as (client, database):
            context = await ready_experiment(
                client, database,
                actor_id="c12_publish_only_write",
                track_id="c12_publish_track",
                permissions=("content.write",),
                allowed_operations=("content.publish",),
            )
            denied_publish = await context["authority"].authorize(
                actor_id=context["actor_id"], session_id=context["session_id"],
                resolved_track_id=context["track_id"], operation="content.publish",
            )
            assert denied_publish.code == AuthorizationCode.PERMISSION_INSUFFICIENT
            assert denied_publish.capability is None

            session_digest = __import__("hashlib").sha256(
                context["session_id"].encode("utf-8")
            ).hexdigest()
            await database["c12_iam_sessions"].update_one(
                {"_id": session_digest}, {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)}}
            )
            denied_session = await context["authority"].authorize(
                actor_id=context["actor_id"], session_id=context["session_id"],
                resolved_track_id=context["track_id"], operation="content.publish",
            )
            assert denied_session.code == AuthorizationCode.SESSION_INVALID
            assert denied_session.capability is None
    asyncio.run(run())


def test_two_editorial_operations_cannot_both_commit_the_same_revision():
    async def run():
        async with isolated_database("two_editors_cas") as (client, database):
            context = await ready_experiment(client, database)
            first, first_prepared = await authorize_and_prepare(
                context, operation_id="c12_parallel_edit_0001", title="first"
            )
            second, second_prepared = await authorize_and_prepare(
                context, operation_id="c12_parallel_edit_0002", title="second"
            )
            results = await asyncio.gather(
                _commit(context, first.capability, first_prepared, title="first"),
                _commit(context, second.capability, second_prepared, title="second"),
                return_exceptions=True,
            )
            successes = [item for item in results if not isinstance(item, BaseException)]
            failures = [item for item in results if isinstance(item, BaseException)]
            assert len(successes) == 1
            assert len(failures) == 1
            assert await context["adapter"].current_revision(context["track_id"]) == 1
            assert await database["edit_history"].count_documents({}) == 1
            block = await database["content_blocks"].find_one({"_id": context["block_id"]})
            assert block["title"] in {"first", "second"}
    asyncio.run(run())


def test_fence_is_separate_from_authorization_and_stale_writer_is_rejected():
    async def run():
        async with isolated_database("stale_fence") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(context, operation_id="c12_old_fence_0001")
            assert decision.allowed
            fence_authority = await context["adapter"].provision_fence_authority(
                context["track_id"], "c12_new_fence_authority"
            )
            await context["adapter"].advance_fence(context["track_id"], fence_authority)
            from curriculum_contract.editorial_revision_protocol import FencingRejected

            with pytest.raises(FencingRejected):
                await _commit(context, decision.capability, prepared)
            assert await context["adapter"].current_revision(context["track_id"]) == 0
            assert await database["edit_history"].count_documents({}) == 0
    asyncio.run(run())


@pytest.mark.parametrize("target_collection", [
    "c12_track_grants", "c12_iam_principals", "c12_iam_sessions",
])
def test_authorization_record_update_racing_with_commit_is_serialized(target_collection):
    class GrantUpdateStarted(monitoring.CommandListener):
        def __init__(self, loop, observed, collection_name):
            self.loop = loop
            self.observed = observed
            self.collection_name = collection_name

        def started(self, event):
            if event.command_name == "update" and event.command.get("update") == self.collection_name:
                self.loop.call_soon_threadsafe(self.observed.set)

        def succeeded(self, _event):
            pass

        def failed(self, _event):
            pass

    async def run():
        async with isolated_database("grant_commit_race") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(
                context, operation_id=f"c12_race_{target_collection[-6:]}_0001"
            )
            entered = asyncio.Event()
            release = asyncio.Event()

            async def pause_before_audit():
                entered.set()
                await release.wait()

            commit_task = asyncio.create_task(_commit(
                context, decision.capability, prepared, before_audit=pause_before_audit,
            ))
            await asyncio.wait_for(entered.wait(), timeout=5)
            observed = asyncio.Event()
            listener = GrantUpdateStarted(asyncio.get_running_loop(), observed, target_collection)
            revoker_client = AsyncMongoClient(
                c12_test_uri(),
                serverSelectionTimeoutMS=5000,
                appname="trilhacode-c12-independent-revoker",
                event_listeners=[listener],
            )
            try:
                revoker = MongoEditorialIAMAuthority(
                    revoker_client[database.name],
                    capability_key=b"c12-synthetic-capability-signing-key-32bytes",
                )
                if target_collection == "c12_track_grants":
                    revoke_call = revoker.revoke_grant(
                        actor_id=context["actor_id"], track_id=context["track_id"],
                        revoked_by="c12_admin_synthetic",
                    )
                elif target_collection == "c12_iam_principals":
                    revoke_call = revoker.change_principal(
                        actor_id=context["actor_id"], role="student",
                        changed_by="c12_admin_synthetic",
                    )
                else:
                    revoke_call = revoker.revoke_session(
                        actor_id=context["actor_id"], session_id=context["session_id"],
                        changed_by="c12_admin_synthetic",
                    )
                revoke_task = asyncio.create_task(revoke_call)
                await asyncio.wait_for(observed.wait(), timeout=5)
                release.set()
                receipt, revoked = await asyncio.gather(commit_task, revoke_task)
                assert receipt.revision == 1
                assert revoked is True
                assert await context["adapter"].current_revision(context["track_id"]) == 1
                assert await database["edit_history"].count_documents({}) == 1
                if target_collection == "c12_track_grants":
                    record = await database[target_collection].find_one({"actor_id": context["actor_id"]})
                    assert record["state"] == "revoked"
                elif target_collection == "c12_iam_principals":
                    record = await database[target_collection].find_one({"_id": context["actor_id"]})
                    assert record["role"] == "student"
                else:
                    record = await database[target_collection].find_one({"actor_id": context["actor_id"]})
                    assert record["active"] is False
            finally:
                release.set()
                if not commit_task.done():
                    await asyncio.gather(commit_task, return_exceptions=True)
                await revoker_client.close()
    asyncio.run(run())


@pytest.mark.parametrize("number_of_checks", [1, 2])
def test_external_iam_check_has_toctou_window_even_after_second_check(number_of_checks):
    async def run():
        async with isolated_database(f"external_iam_{number_of_checks}") as (client, database):
            context = await ready_experiment(client, database)
            decision, prepared = await authorize_and_prepare(
                context, operation_id=f"c12_external_{number_of_checks}_0001"
            )
            assert decision.allowed
            external_iam = {"active": True}
            last_check = asyncio.Event()
            continue_commit = asyncio.Event()

            async def writer():
                assert external_iam["active"]  # initial check
                if number_of_checks == 2:
                    assert external_iam["active"]  # revalidation still ends before commit
                last_check.set()
                await continue_commit.wait()
                return await context["adapter"].commit(
                    prepared,
                    context["credential"],
                    participant=synthetic_block_audit_participant(
                        database, block_id=context["block_id"], track_id=context["track_id"],
                        actor_id=context["actor_id"], operation_id=prepared.operation_id,
                        title="external-check-was-stale",
                    ),
                )

            task = asyncio.create_task(writer())
            await asyncio.wait_for(last_check.wait(), timeout=5)
            external_iam["active"] = False  # authoritative revocation commits first
            continue_commit.set()
            receipt = await task
            assert receipt.revision == 1
            assert await context["adapter"].current_revision(context["track_id"]) == 1
            assert (await database["content_blocks"].find_one({"_id": context["block_id"]}))["title"] == "external-check-was-stale"
    asyncio.run(run())


def test_eventually_consistent_projection_can_allow_commit_after_authority_revocation():
    async def run():
        async with isolated_database("stale_projection") as (client, database):
            context = await ready_experiment(client, database)
            _, prepared = await authorize_and_prepare(context, operation_id="c12_projection_0001")
            authority_collection = database["c12_authz_authoritative_source"]
            projection_collection = database["c12_authz_projection"]
            await authority_collection.insert_one({"_id": "grant-1", "active": True, "epoch": 1})
            await projection_collection.insert_one({
                "_id": "grant-1", "active": True, "epoch": 1, "use_sequence": 0,
            })
            await authority_collection.update_one(
                {"_id": "grant-1", "active": True},
                {"$set": {"active": False}, "$inc": {"epoch": 1}},
            )  # projector is intentionally lagging

            async def projected_guard(session, receipt):
                matched = await projection_collection.update_one(
                    {"_id": "grant-1", "active": True, "epoch": 1},
                    {"$inc": {"use_sequence": 1}}, session=session,
                )
                assert matched.matched_count == 1
                await synthetic_block_audit_participant(
                    database, block_id=context["block_id"], track_id=context["track_id"],
                    actor_id=context["actor_id"], operation_id=prepared.operation_id,
                    title="stale-projection-allowed",
                )(session, receipt)

            receipt = await context["adapter"].commit(
                prepared, context["credential"], participant=projected_guard,
            )
            assert receipt.revision == 1
            assert (await authority_collection.find_one({"_id": "grant-1"})) == {
                "_id": "grant-1", "active": False, "epoch": 2,
            }
            assert await context["adapter"].current_revision(context["track_id"]) == 1
    asyncio.run(run())


async def _noop(_session, _receipt):
    return None
