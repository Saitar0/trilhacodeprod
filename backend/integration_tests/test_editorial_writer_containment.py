from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.editorial_revision_protocol import (  # noqa: E402
    FencingRejected,
    RevisionConflict,
)
from curriculum_contract.experimental_async_editorial_adapter import (  # noqa: E402
    AsyncEditorialRevisionAdapter,
)
from curriculum_contract.experimental_editorial_writer_containment import (  # noqa: E402
    C16InjectedFailure,
    FamilyIntent,
    FaultPlan,
    FaultPoint,
    SnapshotRevisionMismatch,
    WriterFamily,
    commit_family_intent,
    prepare_family_intent,
)
from integration_tests.editorial_writer_containment_harness import (  # noqa: E402
    disposable_database,
    new_operation_id,
)


async def _two_party_barrier() -> None:
    ready = 0
    lock = asyncio.Lock()
    release = asyncio.Event()

    async def arrive() -> None:
        nonlocal ready
        async with lock:
            ready += 1
            if ready == 2:
                release.set()
        await release.wait()

    await asyncio.gather(arrive(), arrive())


@pytest.mark.parametrize(
    ("family_a", "family_b"),
    [
        (WriterFamily.BLOCK_EDIT, WriterFamily.BLOCK_EDIT),
        (WriterFamily.BLOCK_EDIT, WriterFamily.PUBLISH),
        (WriterFamily.BLOCK_EDIT, WriterFamily.IMPORT),
        (WriterFamily.BLOCK_EDIT, WriterFamily.RESTORE),
        (WriterFamily.PUBLISH, WriterFamily.RESTORE),
        (WriterFamily.IMPORT, WriterFamily.PUBLISH),
        (WriterFamily.DELETE, WriterFamily.BLOCK_EDIT),
        (WriterFamily.DUPLICATE, WriterFamily.REORDER),
        (WriterFamily.SEED, WriterFamily.BLOCK_EDIT),
    ],
)
def test_cooperative_writer_families_share_one_revision_authority(family_a, family_b):
    async def run() -> None:
        async with disposable_database(f"race_{family_a.value}_{family_b.value}") as fixture:
            base = fixture.writer
            op_a = new_operation_id()
            op_b = new_operation_id()
            intent_a = FamilyIntent(
                family_a, op_a, "synthetic-a", snapshot_source_revision=0
                if family_a == WriterFamily.PUBLISH else None,
            )
            intent_b = FamilyIntent(
                family_b, op_b, "synthetic-b", snapshot_source_revision=0
                if family_b == WriterFamily.PUBLISH else None,
            )
            prepared_a = await prepare_family_intent(base, intent_a, expected_revision=0)
            prepared_b = await prepare_family_intent(base, intent_b, expected_revision=0)

            second_client = AsyncMongoClient(
                fixture.app_uri, serverSelectionTimeoutMS=5000, appname="trilhacode-c16-second-client"
            )
            try:
                second_db = second_client[fixture.database_name]
                second_adapter = AsyncEditorialRevisionAdapter(second_db, namespace="c8_c16")
                await second_adapter.verify_transaction_topology()
                second_writer = type(base)(
                    client=second_client,
                    database=second_db,
                    adapter=second_adapter,
                    credentials=base.credentials,
                    track_id=base.track_id,
                    block_id=base.block_id,
                    node_id=base.node_id,
                    fencing_token=base.fencing_token,
                )

                async def begin_first():
                    await _two_party_barrier()
                    return await commit_family_intent(base, prepared_a)

                async def begin_second():
                    await _two_party_barrier()
                    return await commit_family_intent(second_writer, prepared_b)

                outcomes = await asyncio.gather(begin_first(), begin_second(), return_exceptions=True)
            finally:
                await second_client.close()

            assert sum(not isinstance(value, BaseException) for value in outcomes) == 1, outcomes
            assert sum(isinstance(value, RevisionConflict) for value in outcomes) == 1, outcomes
            winner = next(value for value in outcomes if not isinstance(value, BaseException))
            assert winner.operation_id in {op_a, op_b}
            assert await base.adapter.current_revision(base.track_id) == 1
            assert await fixture.database["c8_c16_history"].count_documents(
                {"track_id": base.track_id}
            ) == 1
            assert await fixture.database.edit_history.count_documents(
                {"track_id": base.track_id}
            ) == 1
            assert await fixture.database.c16_effects.count_documents(
                {"track_id": base.track_id}
            ) == 1
            operations = await fixture.database["c8_c16_operations"].find(
                {"track_id": base.track_id}
            ).to_list(length=10)
            assert sorted(item["state"] for item in operations) == ["COMMITTED", "CONFLICTED"]
            loser_id = next(item["operation_id"] for item in operations if item["state"] == "CONFLICTED")
            assert await fixture.database.c16_effects.count_documents({"_id": loser_id}) == 0
            assert await fixture.database.nodes.count_documents(
                {"_id": f"c16-import-node-{loser_id}"}
            ) == 0
            assert await fixture.database.track_versions.count_documents(
                {"_id": f"c16-version-{loser_id}"}
            ) == 0
            assert await fixture.database.activity_publications.count_documents(
                {"_id": f"c16-publication-{loser_id}"}
            ) == 0
            assert await fixture.database.track_versions.count_documents({"track_id": base.track_id}) <= 1
            assert await fixture.database.activity_publications.count_documents(
                {"track_id": base.track_id}
            ) <= 1

    asyncio.run(run())


@pytest.mark.parametrize(
    ("family", "fault_point"),
    [
        (WriterFamily.IMPORT, FaultPoint.AFTER_FIRST_MUTATION),
        (WriterFamily.PUBLISH, FaultPoint.AFTER_SNAPSHOT),
        (WriterFamily.RESTORE, FaultPoint.AFTER_FIRST_MUTATION),
        (WriterFamily.DELETE, FaultPoint.AFTER_FIRST_MUTATION),
        (WriterFamily.BLOCK_EDIT, FaultPoint.BEFORE_AUDIT),
    ],
)
def test_multicollection_participant_failure_rolls_back_and_replay_is_single(family, fault_point):
    async def run() -> None:
        async with disposable_database(f"rollback_{family.value}") as fixture:
            writer = fixture.writer
            intent = FamilyIntent(
                family,
                new_operation_id(),
                "synthetic-value",
                snapshot_source_revision=0 if family == WriterFamily.PUBLISH else None,
            )
            prepared = await prepare_family_intent(writer, intent, expected_revision=0)
            with pytest.raises(C16InjectedFailure):
                await commit_family_intent(
                    writer, prepared, fault=FaultPlan(fault_point)
                )

            assert await writer.adapter.current_revision(writer.track_id) == 0
            assert await fixture.database["c8_c16_history"].count_documents({}) == 0
            assert await fixture.database.edit_history.count_documents({}) == 0
            assert await fixture.database.c16_effects.count_documents({}) == 0
            assert await fixture.database.track_versions.count_documents({}) == 0
            assert await fixture.database.activity_publications.count_documents({}) == 0
            assert (await fixture.database.content_blocks.find_one({"_id": writer.block_id}))[
                "title"
            ] == "synthetic-original"
            assert await fixture.database.nodes.count_documents(
                {"_id": {"$regex": "^c16-import-node-"}}
            ) == 0
            assert await fixture.database.c16_effects.count_documents({}) == 0

            committed = await commit_family_intent(writer, prepared)
            replay = await commit_family_intent(writer, prepared)
            assert committed.revision == 1
            assert replay.replayed is True
            assert await writer.adapter.current_revision(writer.track_id) == 1
            assert await fixture.database["c8_c16_history"].count_documents({}) == 1
            assert await fixture.database.edit_history.count_documents({}) == 1
            assert await fixture.database.c16_effects.count_documents({}) == 1

    asyncio.run(run())


def test_publication_rejects_stale_snapshot_before_preparation():
    async def run() -> None:
        async with disposable_database("stale_snapshot") as fixture:
            with pytest.raises(SnapshotRevisionMismatch):
                await prepare_family_intent(
                    fixture.writer,
                    FamilyIntent(
                        WriterFamily.PUBLISH,
                        new_operation_id(),
                        "synthetic",
                        snapshot_source_revision=4,
                    ),
                    expected_revision=3,
                )
            assert await fixture.writer.adapter.current_revision(fixture.writer.track_id) == 0

    asyncio.run(run())


def test_stale_fence_is_rejected_and_does_not_commit_family_mutation():
    async def run() -> None:
        async with disposable_database("stale_fence") as fixture:
            writer = fixture.writer
            prepared = await prepare_family_intent(
                writer,
                FamilyIntent(WriterFamily.BLOCK_EDIT, new_operation_id(), "stale"),
                expected_revision=0,
            )
            authority = await writer.adapter.provision_fence_authority(
                writer.track_id, "c16-fence-advance"
            )
            await writer.adapter.advance_fence(writer.track_id, authority)
            with pytest.raises(FencingRejected):
                await commit_family_intent(writer, prepared)
            assert await writer.adapter.current_revision(writer.track_id) == 0
            assert (await fixture.database.content_blocks.find_one({"_id": writer.block_id}))[
                "title"
            ] == "synthetic-original"
            assert await fixture.database.edit_history.count_documents({}) == 0

    asyncio.run(run())


def test_direct_legacy_write_bypasses_revision_audit_and_fence():
    async def run() -> None:
        async with disposable_database("direct_bypass") as fixture:
            writer = fixture.writer
            prepared = await prepare_family_intent(
                writer,
                FamilyIntent(WriterFamily.BLOCK_EDIT, new_operation_id(), "cooperative"),
                expected_revision=0,
            )
            direct = AsyncMongoClient(
                fixture.app_uri, serverSelectionTimeoutMS=5000, appname="trilhacode-c16-legacy"
            )
            try:
                legacy_db = direct[fixture.database_name]
                first = await legacy_db.content_blocks.update_one(
                    {"_id": writer.block_id}, {"$set": {"title": "direct-before-commit"}}
                )
                assert first.matched_count == 1
                assert await writer.adapter.current_revision(writer.track_id) == 0
                assert await legacy_db.edit_history.count_documents({}) == 0
                await commit_family_intent(writer, prepared)

                second = await legacy_db.content_blocks.update_one(
                    {"_id": writer.block_id}, {"$set": {"title": "direct-after-commit"}}
                )
                assert second.matched_count == 1
                block = await legacy_db.content_blocks.find_one({"_id": writer.block_id})
                assert block["title"] == "direct-after-commit"
                assert await writer.adapter.current_revision(writer.track_id) == 1
                assert await legacy_db.edit_history.count_documents({}) == 1
                assert await legacy_db["c8_c16_history"].count_documents({}) == 1
            finally:
                await direct.close()

    asyncio.run(run())


def test_scoped_database_role_does_not_contain_a_legacy_writer():
    async def run() -> None:
        async with disposable_database("scoped_role") as fixture:
            root = fixture.root_client
            db = root[fixture.database_name]
            role = "c16ContentOnly"
            user = f"c16legacy{fixture.database_name[-8:]}"
            password = "c16synthetic" + fixture.database_name[-16:]
            await db.command(
                "createRole",
                role,
                privileges=[
                    {
                        "resource": {"db": fixture.database_name, "collection": "content_blocks"},
                        "actions": ["find", "insert", "update", "remove"],
                    }
                ],
                roles=[],
            )
            await db.command(
                "createUser", user, pwd=password, roles=[{"role": role, "db": fixture.database_name}]
            )
            uri = (
                f"mongodb://{user}:{password}@mongo-c16:27017/{fixture.database_name}"
                f"?authSource={fixture.database_name}&replicaSet=rsC16"
            )
            scoped = AsyncMongoClient(uri, serverSelectionTimeoutMS=5000)
            try:
                scoped_db = scoped[fixture.database_name]
                changed = await scoped_db.content_blocks.update_one(
                    {"_id": fixture.writer.block_id}, {"$set": {"title": "scoped-direct-bypass"}}
                )
                assert changed.matched_count == 1
                with pytest.raises(OperationFailure):
                    await scoped_db["c8_c16_tracks"].update_one(
                        {"_id": fixture.writer.track_id}, {"$inc": {"revision": 1}}
                    )
            finally:
                await scoped.close()

            reader = f"c16reader{fixture.database_name[-8:]}"
            reader_password = "c16reader" + fixture.database_name[-16:]
            await db.command(
                "createUser",
                reader,
                pwd=reader_password,
                roles=[{"role": "read", "db": fixture.database_name}],
            )
            reader_uri = (
                f"mongodb://{reader}:{reader_password}@mongo-c16:27017/{fixture.database_name}"
                f"?authSource={fixture.database_name}&replicaSet=rsC16"
            )
            readonly = AsyncMongoClient(reader_uri, serverSelectionTimeoutMS=5000)
            try:
                with pytest.raises(OperationFailure):
                    await readonly[fixture.database_name].content_blocks.update_one(
                        {"_id": fixture.writer.block_id}, {"$set": {"title": "must-be-denied"}}
                    )
            finally:
                await readonly.close()

    asyncio.run(run())


def test_delete_atomicity_does_not_decide_student_data_retention_policy():
    async def run() -> None:
        async with disposable_database("learner_data_policy") as fixture:
            writer = fixture.writer
            intent = FamilyIntent(WriterFamily.DELETE, new_operation_id(), "delete")
            prepared = await prepare_family_intent(writer, intent, expected_revision=0)
            await commit_family_intent(writer, prepared)
            assert await fixture.database.content_blocks.count_documents(
                {"track_id": writer.track_id}
            ) == 0
            assert await fixture.database.progress.count_documents(
                {"track_id": writer.track_id}
            ) == 0
            assert await fixture.database.activity_attempts.count_documents(
                {"track_id": writer.track_id}
            ) == 0
            assert await fixture.database["c8_c16_history"].count_documents({}) == 1

    asyncio.run(run())
