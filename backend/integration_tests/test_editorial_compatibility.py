"""MongoDB 7 disposable compatibility tests for C9; no app routes are imported."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from bson import ObjectId
from pymongo import AsyncMongoClient, MongoClient
from pymongo.errors import PyMongoError

from curriculum_contract.editorial_revision_protocol import (
    IdempotencyConflict,
    OperationState,
    RevisionConflict,
)
from curriculum_contract.experimental_editorial_compatibility import (
    EditorialBlockReferenceNotFound,
    InvalidEditorialCompatibilityInput,
    commit_compatible_block_update_async,
    commit_prepared_compatible_block_update,
    ensure_experimental_indexes,
    parse_operational_block_id,
    prepare_compatible_block_update,
)
from curriculum_contract.mongodb_editorial_revision_adapter import (
    MongoDBEditorialRevisionAdapter,
)
from integration_tests.editorial_block_atomicity_harness import (
    Fault,
    InjectedFailure,
    OperationControls,
    load_real_update_block,
)
from integration_tests.editorial_compatibility_harness import (
    DATABASE_PREFIX,
    PHASE_LABEL,
    ensure_versioned_legacy_indexes,
    legacy_audit_row,
    new_database_name,
    verified_uri,
    verify_owned_docker_resources,
    verify_server,
)
from schemas.content import BlockUpdate

_NAMESPACE = "c9_editorial"
_TRACK_ID = "synthetic-track-c9"
_ACTOR = {"id": "synthetic-editor-c9", "name": "Synthetic editor"}
_INITIAL_TITLE = "synthetic-original-title"


class _FailingAuditCollection:
    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        raise PyMongoError("synthetic audit insert failure")

    def __getattr__(self, name: str) -> Any:
        return getattr(self._collection, name)


class _FailingAuditDatabase:
    def __init__(self, database: Any) -> None:
        self._database = database
        self.client = database.client
        self.name = database.name

    def __getitem__(self, name: str) -> Any:
        collection = self._database[name]
        if name == "edit_history":
            return _FailingAuditCollection(collection)
        return collection


class EditorialCompatibilityTests(IsolatedAsyncioTestCase):
    mongo_uri: str
    server: dict[str, str]
    sync_client: MongoClient
    async_client: AsyncMongoClient

    @classmethod
    def setUpClass(cls) -> None:
        verify_owned_docker_resources()
        cls.mongo_uri = verified_uri()
        client: MongoClient = MongoClient(
            cls.mongo_uri,
            appname="trilhacode-12c9-preflight",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        cls.server = verify_server(client)
        client.close()

    async def asyncSetUp(self) -> None:
        verify_owned_docker_resources()
        self.mongo_uri = verified_uri()
        self.sync_client = MongoClient(
            self.mongo_uri,
            appname="trilhacode-12c9-sync-adapter",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            retryWrites=True,
        )
        self.async_client = AsyncMongoClient(
            self.mongo_uri,
            appname="trilhacode-12c9-real-writer",
            timeoutMS=5000,
            retryWrites=True,
        )
        self.database_name = new_database_name()
        self.run_id = self.database_name.removeprefix(DATABASE_PREFIX)
        self.database = self.sync_client[self.database_name]
        self.async_database = self.async_client[self.database_name]
        self.track_id = f"{_TRACK_ID}-{self.run_id}"
        self.database["_phase_identity"].insert_one(
            {"_id": "owner", "phase": PHASE_LABEL, "run_id": self.run_id}
        )

        ensure_versioned_legacy_indexes(self.database)
        legacy_time = datetime.now(timezone.utc)
        # Current audit rows have no operation_id. Both must coexist under the
        # new partial unique index used by the experiment.
        self.database["edit_history"].insert_many(
            [
                legacy_audit_row(
                    track_id=self.track_id,
                    entity_id=str(ObjectId()),
                    at=legacy_time,
                ),
                legacy_audit_row(
                    track_id=self.track_id,
                    entity_id=str(ObjectId()),
                    at=legacy_time,
                ),
            ]
        )

        self.adapter = MongoDBEditorialRevisionAdapter(
            self.database, namespace=_NAMESPACE
        )
        topology = self.adapter.verify_transaction_topology()
        self.assertEqual(topology.server_version, "7.0.43")
        self.assertEqual(topology.replica_set, "rs12c9")
        self.assertTrue(topology.sessions_available)
        self.adapter.initialize_track(self.track_id)
        self.credential = self.adapter.provision_writer_credential(
            self.track_id, "synthetic-writer-c9"
        )
        self.authority = self.adapter.provision_fence_authority(
            self.track_id, "synthetic-fence-authority-c9"
        )
        self.fence = self.adapter.advance_fence(self.track_id, self.authority)
        ensure_experimental_indexes(self.database, self.adapter)

    async def asyncTearDown(self) -> None:
        marker = await self.async_database["_phase_identity"].find_one(
            {"_id": "owner"}
        )
        expected = {
            "_id": "owner",
            "phase": PHASE_LABEL,
            "run_id": self.run_id,
        }
        if marker != expected:
            await self.async_client.close()
            self.sync_client.close()
            self.fail("C9 database marker changed; refusing to drop the database")
        self.sync_client.drop_database(self.database_name)
        await self.async_client.close()
        self.sync_client.close()

    async def seed_block(self, *, track_id: str | None = None) -> ObjectId:
        block_id = ObjectId()
        now = datetime.now(timezone.utc)
        await self.async_database["content_blocks"].insert_one(
            {
                "_id": block_id,
                "node_id": str(ObjectId()),
                "track_id": track_id or self.track_id,
                "type": "theory_text",
                "title": _INITIAL_TITLE,
                "data": {"body": "Synthetic block body"},
                "status": "draft",
                "order": 0,
                "schema_version": 1,
                "created_by": _ACTOR["id"],
                "created_at": now,
                "updated_at": now,
            }
        )
        return block_id

    async def _invoke_compatibility(
        self,
        block_id: ObjectId,
        *,
        operation_id: str = "synthetic-operation-c9",
        expected_revision: int = 0,
        update_fields: dict[str, Any] | None = None,
        database: Any | None = None,
    ):
        return await commit_compatible_block_update_async(
            database or self.database,
            self.adapter,
            track_id=self.track_id,
            credential=self.credential,
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self.fence,
            block_id=str(block_id),
            actor=_ACTOR,
            update_fields=update_fields
            if update_fields is not None
            else {"title": "synthetic-updated-title", "status": "published"},
        )

    async def test_01_versioned_block_update_contract_and_real_async_writer(self) -> None:
        block_id = await self.seed_block()
        body = BlockUpdate.model_validate(
            {
                "title": "synthetic-real-writer-title",
                "data": {"body": "Synthetic revised body"},
                "status": "published",
            }
        )
        fields = body.model_dump(exclude_unset=True)
        writer = load_real_update_block(self.async_database)
        source_path = writer.source_path
        self.assertEqual(writer.update_block.__code__.co_filename, str(source_path))
        self.assertEqual(source_path.name, "blocks.py")

        result = await writer.invoke(str(block_id), fields, dict(_ACTOR))
        assert result is not None
        stored = await self.async_database["content_blocks"].find_one(
            {"_id": block_id}
        )
        audit = await self.async_database["edit_history"].find_one(
            {"entity_id": str(block_id), "action": "updated"}
        )
        assert stored is not None
        assert audit is not None
        self.assertEqual(result["_id"], block_id)
        self.assertEqual(result["title"], "synthetic-real-writer-title")
        self.assertEqual(stored["data"], {"body": "Synthetic revised body"})
        self.assertEqual(stored["status"], "published")
        self.assertEqual(stored["track_id"], self.track_id)
        self.assertIsInstance(stored["_id"], ObjectId)
        self.assertEqual(audit["entity"], "block")
        self.assertEqual(audit["summary"], "theory_text")
        self.assertEqual(audit["user_id"], _ACTOR["id"])
        self.assertEqual(audit["user_name"], _ACTOR["name"])
        self.assertNotIn("operation_id", audit)
        self.assertNotIn("revision", audit)

    async def test_02_compatibility_transaction_updates_real_document_shape(self) -> None:
        block_id = await self.seed_block()
        result = await self._invoke_compatibility(
            block_id,
            update_fields={
                "title": "synthetic-transaction-title",
                "data": {"body": "Synthetic transactional data"},
                "status": "published",
            },
        )
        self.assertEqual(result.receipt.revision, 1)
        self.assertEqual(result.receipt.parent_revision, 0)
        self.assertEqual(result.block["_id"], block_id)
        self.assertEqual(result.block["title"], "synthetic-transaction-title")
        self.assertEqual(result.block["data"], {"body": "Synthetic transactional data"})
        self.assertEqual(result.block["status"], "published")
        self.assertEqual(result.block["track_id"], self.track_id)
        self.assertEqual(result.block["node_id"], str(ObjectId(result.block["node_id"])))
        self.assertEqual(result.block["schema_version"], 1)
        self.assertIsInstance(result.block["updated_at"], datetime)

        audit = self.database["edit_history"].find_one(
            {"track_id": self.track_id, "operation_id": result.receipt.operation_id}
        )
        assert audit is not None
        self.assertEqual(
            {
                key: audit[key]
                for key in (
                    "entity",
                    "entity_id",
                    "action",
                    "track_id",
                    "summary",
                    "user_id",
                    "user_name",
                )
            },
            {
                "entity": "block",
                "entity_id": str(block_id),
                "action": "updated",
                "track_id": self.track_id,
                "summary": "theory_text",
                "user_id": _ACTOR["id"],
                "user_name": _ACTOR["name"],
            },
        )
        self.assertEqual(audit["revision"], 1)
        self.assertEqual(audit["parent_revision"], 0)
        self.assertEqual(audit["writer_id"], self.credential.writer_id)
        self.assertEqual(audit["fencing_token"], self.fence)
        self.assertEqual(audit["changed_fields"], ["data", "status", "title"])
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)

    async def test_03_partial_operation_index_preserves_legacy_audits(self) -> None:
        legacy = list(
            self.database["edit_history"].find({"track_id": self.track_id})
        )
        self.assertEqual(len(legacy), 2)
        self.assertTrue(all("operation_id" not in row for row in legacy))
        indexes = list(self.database["edit_history"].list_indexes())
        operation_index = next(
            index
            for index in indexes
            if index["name"] == f"{_NAMESPACE}_audit_operation_identity"
        )
        self.assertEqual(
            operation_index["partialFilterExpression"],
            {"operation_id": {"$type": "string"}},
        )
        self.assertTrue(operation_index["unique"])

    async def test_04_real_writer_can_leave_persisted_partial_state(self) -> None:
        block_id = await self.seed_block()
        injected = InjectedFailure("synthetic audit outage")
        controls = OperationControls(
            faults=[Fault("edit_history", "insert_one", "before", injected)]
        )
        writer = load_real_update_block(self.async_database, controls=controls)
        with self.assertRaises(InjectedFailure) as caught:
            await writer.invoke(
                str(block_id),
                {"title": "synthetic-before-audit-failure"},
                dict(_ACTOR),
            )
        self.assertIs(caught.exception, injected)
        stored = await self.async_database["content_blocks"].find_one(
            {"_id": block_id}
        )
        assert stored is not None
        audit_count = await self.async_database["edit_history"].count_documents(
            {"entity_id": str(block_id), "action": "updated"}
        )
        self.assertEqual(stored["title"], "synthetic-before-audit-failure")
        self.assertEqual(audit_count, 0)
        self.assertEqual(controls.trace.count("content_blocks.update_one:persisted"), 1)

    async def test_05_transaction_rolls_back_block_when_audit_insert_fails(self) -> None:
        block_id = await self.seed_block()
        before = await self.async_database["content_blocks"].find_one(
            {"_id": block_id}
        )
        failing_db = _FailingAuditDatabase(self.database)
        with self.assertRaisesRegex(PyMongoError, "synthetic audit insert failure"):
            await self._invoke_compatibility(
                block_id,
                operation_id="synthetic-audit-failure",
                database=failing_db,
                update_fields={"title": "synthetic-must-roll-back"},
            )
        after = await self.async_database["content_blocks"].find_one(
            {"_id": block_id}
        )
        self.assertEqual(after, before)
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self.adapter.history(self.track_id), ())
        self.assertEqual(
            self.adapter.operation_state(
                self.track_id, "synthetic-audit-failure"
            ),
            OperationState.PREPARED,
        )
        self.assertEqual(
            self.database["edit_history"].count_documents(
                {"operation_id": "synthetic-audit-failure"}
            ),
            0,
        )

    async def test_06_retry_replays_receipt_without_duplicate_audit(self) -> None:
        block_id = await self.seed_block()
        first = await self._invoke_compatibility(
            block_id, operation_id="synthetic-idempotent-replay"
        )
        second = await self._invoke_compatibility(
            block_id, operation_id="synthetic-idempotent-replay"
        )
        self.assertFalse(first.receipt.replayed)
        self.assertTrue(second.receipt.replayed)
        self.assertEqual(
            (
                first.receipt.track_id,
                first.receipt.operation_id,
                first.receipt.revision,
                first.receipt.parent_revision,
                first.receipt.fingerprint,
            ),
            (
                second.receipt.track_id,
                second.receipt.operation_id,
                second.receipt.revision,
                second.receipt.parent_revision,
                second.receipt.fingerprint,
            ),
        )
        self.assertEqual(first.block, second.block)
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        self.assertEqual(
            self.database["edit_history"].count_documents(
                {
                    "track_id": self.track_id,
                    "operation_id": "synthetic-idempotent-replay",
                }
            ),
            1,
        )

    async def test_07_same_operation_with_different_payload_conflicts(self) -> None:
        block_id = await self.seed_block()
        await self._invoke_compatibility(
            block_id,
            operation_id="synthetic-payload-conflict",
            update_fields={"title": "synthetic-first-title"},
        )
        with self.assertRaises(IdempotencyConflict):
            await self._invoke_compatibility(
                block_id,
                operation_id="synthetic-payload-conflict",
                update_fields={"title": "synthetic-second-title"},
            )
        self.assertEqual(
            self.database["edit_history"].count_documents(
                {"operation_id": "synthetic-payload-conflict"}
            ),
            1,
        )

    async def test_08_object_id_and_request_schema_contract(self) -> None:
        block_id = ObjectId()
        self.assertEqual(parse_operational_block_id(str(block_id)), block_id)
        self.assertEqual(
            parse_operational_block_id(str(block_id).upper()), block_id
        )
        self.assertEqual(
            str(parse_operational_block_id(str(block_id).upper())),
            str(block_id),
        )
        for invalid in ("", "not-an-object-id", "123", "z" * 24, block_id):
            with self.subTest(invalid=type(invalid).__name__):
                with self.assertRaises(InvalidEditorialCompatibilityInput):
                    parse_operational_block_id(invalid)  # type: ignore[arg-type]

        model = BlockUpdate.model_validate(
            {"title": "synthetic", "ignored_extra": "not an API field"}
        )
        self.assertEqual(model.model_dump(exclude_unset=True), {"title": "synthetic"})
        with self.assertRaises(InvalidEditorialCompatibilityInput):
            await self._invoke_compatibility(
                block_id,
                update_fields={"unexpected": "field"},
            )
        with self.assertRaises(InvalidEditorialCompatibilityInput):
            await self._invoke_compatibility(
                block_id,
                update_fields={"status": "unsupported"},
            )

    async def test_09_block_must_match_unambiguous_track_reference(self) -> None:
        block_id = await self.seed_block(track_id="synthetic-other-track")
        with self.assertRaises(EditorialBlockReferenceNotFound):
            await self._invoke_compatibility(
                block_id, operation_id="synthetic-cross-track"
            )
        stored = await self.async_database["content_blocks"].find_one(
            {"_id": block_id}
        )
        assert stored is not None
        self.assertEqual(stored["title"], _INITIAL_TITLE)
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self.adapter.history(self.track_id), ())

    async def test_10_worker_thread_does_not_block_event_loop(self) -> None:
        block_id = await self.seed_block()
        entered = threading.Event()
        release = threading.Event()
        original = __import__(
            "curriculum_contract.experimental_editorial_compatibility",
            fromlist=["_commit_compatible_block_update"],
        )._commit_compatible_block_update

        def delayed(*args: Any, **kwargs: Any):
            entered.set()
            if not release.wait(5):
                raise TimeoutError("test did not release the worker")
            return original(*args, **kwargs)

        module = __import__(
            "curriculum_contract.experimental_editorial_compatibility",
            fromlist=["_commit_compatible_block_update"],
        )
        with patch.object(module, "_commit_compatible_block_update", delayed):
            task = asyncio.create_task(
                self._invoke_compatibility(
                    block_id, operation_id="synthetic-event-loop-responsiveness"
                )
            )
            self.assertTrue(await asyncio.to_thread(entered.wait, 5))
            heartbeat = asyncio.Event()
            asyncio.get_running_loop().call_soon(heartbeat.set)
            await asyncio.wait_for(heartbeat.wait(), timeout=0.2)
            release.set()
            result = await task
        self.assertEqual(result.receipt.revision, 1)

    async def test_11_cancellation_can_leave_commit_outcome_for_reconciliation(self) -> None:
        block_id = await self.seed_block()
        entered = threading.Event()
        release = threading.Event()
        finished = threading.Event()
        module = __import__(
            "curriculum_contract.experimental_editorial_compatibility",
            fromlist=["_commit_compatible_block_update"],
        )
        original = module._commit_compatible_block_update

        def delayed(*args: Any, **kwargs: Any):
            entered.set()
            if not release.wait(5):
                raise TimeoutError("test did not release the worker")
            try:
                return original(*args, **kwargs)
            finally:
                finished.set()

        with patch.object(module, "_commit_compatible_block_update", delayed):
            task = asyncio.create_task(
                self._invoke_compatibility(
                    block_id, operation_id="synthetic-cancelled-client"
                )
            )
            self.assertTrue(await asyncio.to_thread(entered.wait, 5))
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            release.set()
            self.assertTrue(await asyncio.to_thread(finished.wait, 5))

        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        replay = await self._invoke_compatibility(
            block_id, operation_id="synthetic-cancelled-client"
        )
        self.assertTrue(replay.receipt.replayed)
        self.assertEqual(
            self.database["edit_history"].count_documents(
                {
                    "track_id": self.track_id,
                    "operation_id": "synthetic-cancelled-client",
                }
            ),
            1,
        )

    async def test_12_independent_clients_cannot_confirm_same_track_revision(self) -> None:
        block_id = await self.seed_block()
        barrier = threading.Barrier(2)

        def contend(operation_id: str, title: str) -> tuple[str, int | None]:
            client: MongoClient = MongoClient(
                self.mongo_uri,
                appname=f"trilhacode-12c9-{operation_id}",
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True,
            )
            try:
                database = client[self.database_name]
                adapter = MongoDBEditorialRevisionAdapter(
                    database, namespace=_NAMESPACE
                )
                adapter.verify_transaction_topology()
                prepared = prepare_compatible_block_update(
                    adapter,
                    track_id=self.track_id,
                    credential=self.credential,
                    operation_id=operation_id,
                    expected_revision=0,
                    fencing_token=self.fence,
                    block_id=str(block_id),
                    actor=_ACTOR,
                    update_fields={"title": title},
                )
                barrier.wait(timeout=10)
                try:
                    result = commit_prepared_compatible_block_update(
                        database, adapter, self.credential, prepared
                    )
                    return "committed", result.receipt.revision
                except RevisionConflict:
                    return "conflict", None
            finally:
                client.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(contend, "synthetic-race-a", "synthetic-title-a"),
                executor.submit(contend, "synthetic-race-b", "synthetic-title-b"),
            ]
            outcomes = [future.result(timeout=30) for future in futures]

        self.assertEqual(sum(outcome[0] == "committed" for outcome in outcomes), 1)
        self.assertEqual(sum(outcome[0] == "conflict" for outcome in outcomes), 1)
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        history = self.adapter.history(self.track_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(
            self.database["edit_history"].count_documents(
                {
                    "track_id": self.track_id,
                    "operation_id": {
                        "$in": ["synthetic-race-a", "synthetic-race-b"]
                    },
                }
            ),
            1,
        )


if __name__ == "__main__":
    raise SystemExit(0)
