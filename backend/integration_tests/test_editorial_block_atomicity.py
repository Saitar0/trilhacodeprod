"""MongoDB 7 disposable tests for the real W-05 writer and an isolated proposal."""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import unittest
from secrets import token_hex
from types import SimpleNamespace
from typing import Any

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure
from pymongo.uri_parser import parse_uri

from curriculum_contract.experimental_block_audit_transaction import (
    BlockConcurrentWriteConflict,
    BlockOperationConflict,
    BlockRevisionConflict,
    update_block_with_audit_transaction,
)
from integration_tests.editorial_block_atomicity_harness import (
    DatabaseProxy,
    Fault,
    InjectedFailure,
    OperationControls,
    load_real_update_block,
)

_PHASE_LABEL = "2.1a.12c7"
_CONTAINER = "trilhacode-12c7-update-block-mongo"
_NETWORK = "trilhacode-12c7-update-block-net"
_IMAGE = "mongo:7.0.43"
_IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
_PORT = 52926
_RUN_PREFIX = "editorial_block_audit_test_"


def _verify_owned_docker_resources() -> None:
    container_raw = subprocess.run(
        ["docker", "inspect", _CONTAINER], check=True, capture_output=True, text=True
    ).stdout
    container = json.loads(container_raw)[0]
    if container["Config"]["Labels"].get("io.trilhacode.phase") != _PHASE_LABEL:
        raise RuntimeError("Mongo container does not carry this phase's ownership label")
    if not container["State"]["Running"]:
        raise RuntimeError("phase-owned Mongo container is not running")
    if container["Config"]["Image"] != _IMAGE or container["Image"] != _IMAGE_ID:
        raise RuntimeError("Mongo container image is not the verified local MongoDB 7 image")
    if container["Mounts"]:
        raise RuntimeError("Mongo container unexpectedly has persistent or bind mounts")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("Mongo data paths are not confined to disposable tmpfs")
    bindings = container["HostConfig"]["PortBindings"].get(f"{_PORT}/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(_PORT)}]:
        raise RuntimeError("Mongo port is not restricted to the expected loopback binding")
    networks = container["NetworkSettings"]["Networks"]
    if set(networks) != {_NETWORK}:
        raise RuntimeError("Mongo container is attached to an unexpected Docker network")

    network_raw = subprocess.run(
        ["docker", "network", "inspect", _NETWORK], check=True, capture_output=True, text=True
    ).stdout
    network = json.loads(network_raw)[0]
    if network["Labels"].get("io.trilhacode.phase") != _PHASE_LABEL:
        raise RuntimeError("Docker network does not carry this phase's ownership label")
    if network["Driver"] != "bridge" or network["Internal"]:
        raise RuntimeError("Mongo must use only the dedicated phase bridge network")
    if network["Options"].get("com.docker.network.bridge.enable_ip_masquerade") != "false":
        raise RuntimeError("dedicated bridge must disable outbound masquerading")
    if set(network["Containers"]) != {container["Id"]}:
        raise RuntimeError("dedicated test network contains an unexpected container")


def _verified_uri() -> str:
    uri = os.environ.get("TRILHACODE_12C7_MONGODB_URI", "")
    if not uri or "@" in uri or uri.lower().startswith("mongodb+srv://"):
        raise RuntimeError("an explicit credential-free phase-local MongoDB URI is required")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", _PORT)]:
        raise RuntimeError("test URI must point only to the phase's loopback Mongo container")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("credentials are not accepted by this test harness")
    if parsed["options"].get("replicaSet") != "rs12c7":
        raise RuntimeError("test URI must select the dedicated rs12c7 replica set")
    if parsed["database"] not in (None, ""):
        raise RuntimeError("the URI must not select a pre-existing database")
    if not re.match(r"^mongodb://127\.0\.0\.1:52926/\?", uri):
        raise RuntimeError("unexpected test URI form")
    return uri


class EditorialBlockAtomicityTests(unittest.IsolatedAsyncioTestCase):
    mongo_uri: str

    @classmethod
    def setUpClass(cls) -> None:
        _verify_owned_docker_resources()
        cls.mongo_uri = _verified_uri()

    async def asyncSetUp(self) -> None:
        self.client = AsyncMongoClient(self.mongo_uri, timeoutMS=8_000)
        self.db_name = _RUN_PREFIX + token_hex(8)
        self.run_id = self.db_name.removeprefix(_RUN_PREFIX)
        self.database = self.client[self.db_name]

        hello = await self.client.admin.command("hello")
        build = await self.client.admin.command("buildInfo")
        server_status = await self.client.admin.command("serverStatus")
        replica_status = await self.client.admin.command("replSetGetStatus")
        self.assertEqual(build["version"], "7.0.43")
        self.assertEqual(hello.get("setName"), "rs12c7")
        self.assertTrue(hello.get("isWritablePrimary"))
        self.assertIsNotNone(hello.get("logicalSessionTimeoutMinutes"))
        self.assertEqual(server_status["storageEngine"]["name"], "wiredTiger")
        members = replica_status["members"]
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["stateStr"], "PRIMARY")

        await self.database["_phase_identity"].insert_one(
            {"_id": "owner", "phase": _PHASE_LABEL, "run_id": self.run_id}
        )
        await self.database["edit_history"].create_index(
            "operation_id",
            unique=True,
            partialFilterExpression={"operation_id": {"$type": "string"}},
        )

    async def asyncTearDown(self) -> None:
        marker = await self.database["_phase_identity"].find_one({"_id": "owner"})
        if marker != {"_id": "owner", "phase": _PHASE_LABEL, "run_id": self.run_id}:
            await self.client.close()
            self.fail("disposable database identity marker changed; database not dropped")
        await self.client.drop_database(self.db_name)
        await self.client.close()

    async def seed_block(self, *, revision: int | None = None) -> ObjectId:
        block_id = ObjectId()
        document: dict[str, Any] = {
            "_id": block_id,
            "track_id": "synthetic-track-12c7",
            "type": "text",
            "status": "draft",
            "title": "synthetic-original-title",
        }
        if revision is not None:
            document["editorial_revision"] = revision
        await self.database["content_blocks"].insert_one(document)
        return block_id

    async def block(self, block_id: ObjectId) -> dict[str, Any] | None:
        return await self.database["content_blocks"].find_one({"_id": block_id})

    async def required_block(self, block_id: ObjectId) -> dict[str, Any]:
        document = await self.block(block_id)
        if document is None:
            raise AssertionError("synthetic block disappeared")
        return document

    async def audit_rows(self) -> list[dict[str, Any]]:
        return await self.database["edit_history"].find({}).to_list(100)

    def writer(self, controls: OperationControls | None = None):
        return load_real_update_block(self.database, controls=controls)

    async def invoke_real_writer(
        self,
        block_id: ObjectId,
        *,
        title: str = "synthetic-updated-title",
        controls: OperationControls | None = None,
    ) -> Any:
        harness = self.writer(controls)
        return await harness.invoke(
            str(block_id),
            {"title": title, "status": "draft"},
            {"id": "synthetic-editor", "name": "Synthetic"},
        )

    async def invoke_transaction(
        self,
        block_id: ObjectId,
        *,
        expected_revision: int = 0,
        operation_id: str = "synthetic-operation-12c7",
        title: str = "synthetic-transaction-title",
        controls: OperationControls | None = None,
    ) -> dict[str, Any]:
        database = DatabaseProxy(self.database, controls or OperationControls())
        return await update_block_with_audit_transaction(
            database,
            block_id=block_id,
            expected_revision=expected_revision,
            operation_id=operation_id,
            update_fields={"title": title, "status": "draft"},
            user={"id": "synthetic-editor", "name": "Synthetic"},
        )

    async def test_01_real_writer_and_audit_sources_are_invoked(self) -> None:
        block_id = await self.seed_block()
        writer = self.writer()
        source = writer.source_path.read_text(encoding="utf-8")
        self.assertIn("async def update_block(", source)
        self.assertIn('await audit(user, "block", block_id, "updated"', source)
        self.assertEqual(writer.update_block.__code__.co_filename, str(writer.source_path))
        result = await writer.invoke(
            str(block_id),
            {"title": "synthetic-real-writer", "status": "draft"},
            {"id": "synthetic-editor"},
        )
        self.assertEqual(result["title"], "synthetic-real-writer")
        self.assertEqual(len(await self.audit_rows()), 1)
        self.assertEqual(writer.controls.trace[0], "content_blocks.find_one:before")
        self.assertEqual(writer.controls.trace[1], "content_blocks.find_one:persisted")
        self.assertIn("edit_history.insert_one:persisted", writer.controls.trace)

    async def test_02_database_starts_without_editorial_documents(self) -> None:
        self.assertEqual(await self.database["content_blocks"].count_documents({}), 0)
        self.assertEqual(await self.database["edit_history"].count_documents({}), 0)

    async def test_03_successful_update_and_audit_persist_separately(self) -> None:
        block_id = await self.seed_block()
        await self.invoke_real_writer(block_id)
        persisted = await self.required_block(block_id)
        self.assertEqual(persisted["title"], "synthetic-updated-title")
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_04_failure_before_update_leaves_both_unchanged(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic failure before update")
        controls = OperationControls(
            faults=[Fault("content_blocks", "update_one", "before", failure)]
        )
        with self.assertRaises(InjectedFailure) as caught:
            await self.invoke_real_writer(block_id, controls=controls)
        self.assertIs(caught.exception, failure)
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-original-title")
        self.assertEqual(await self.audit_rows(), [])

    async def test_05_mongodb_validation_failure_rejects_update(self) -> None:
        await self.database.create_collection(
            "content_blocks",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["_id", "track_id", "type", "status", "title"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "track_id": {"bsonType": "string"},
                        "type": {"bsonType": "string"},
                        "status": {"bsonType": "string"},
                        "title": {"bsonType": "string"},
                        "updated_at": {"bsonType": "date"},
                    },
                    "additionalProperties": False,
                }
            },
            validationLevel="strict",
        )
        block_id = await self.seed_block()
        with self.assertRaises(OperationFailure):
            await self.writer().invoke(
                str(block_id),
                {"status": "draft", "not_in_schema": "synthetic"},
                {"id": "synthetic-editor"},
            )
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-original-title")
        self.assertEqual(await self.audit_rows(), [])

    async def test_06_failure_after_update_ack_leaves_partial_state(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic response lost after Mongo update acknowledgement")
        controls = OperationControls(
            faults=[Fault("content_blocks", "update_one", "after", failure)]
        )
        with self.assertRaises(InjectedFailure) as caught:
            await self.invoke_real_writer(block_id, controls=controls)
        self.assertIs(caught.exception, failure)
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-updated-title")
        self.assertEqual(await self.audit_rows(), [])

    async def test_07_audit_insert_failure_leaves_real_writer_partial(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic audit insert failure")
        controls = OperationControls(
            faults=[Fault("edit_history", "insert_one", "before", failure)]
        )
        with self.assertRaises(InjectedFailure) as caught:
            await self.invoke_real_writer(block_id, controls=controls)
        self.assertIs(caught.exception, failure)
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-updated-title")
        self.assertEqual(await self.audit_rows(), [])
        self.assertLess(
            controls.trace.index("content_blocks.update_one:persisted"),
            controls.trace.index("edit_history.insert_one:before"),
        )

    async def test_08_audit_ack_loss_can_leave_audit_and_block_persisted_with_error(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic audit response lost after insert acknowledgement")
        controls = OperationControls(faults=[Fault("edit_history", "insert_one", "after", failure)])
        with self.assertRaises(InjectedFailure) as caught:
            await self.invoke_real_writer(block_id, controls=controls)
        self.assertIs(caught.exception, failure)
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-updated-title")
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_09_failure_of_final_read_occurs_after_both_writes(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic failure before response read")
        controls = OperationControls(
            faults=[Fault("content_blocks", "find_one", "before", failure, skip_matches=1)]
        )
        with self.assertRaises(InjectedFailure):
            await self.invoke_real_writer(block_id, controls=controls)
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-updated-title")
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_10_retry_after_audit_failure_applies_writer_again(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic audit failure")
        controls = OperationControls(
            faults=[Fault("edit_history", "insert_one", "before", failure)]
        )
        writer = self.writer(controls)
        with self.assertRaises(InjectedFailure):
            await writer.invoke(
                str(block_id),
                {"title": "synthetic-retry", "status": "draft"},
                {"id": "synthetic-editor"},
            )
        await writer.invoke(
            str(block_id),
            {"title": "synthetic-retry", "status": "draft"},
            {"id": "synthetic-editor"},
        )
        self.assertEqual(writer.controls.trace.count("content_blocks.update_one:persisted"), 2)
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_11_retry_after_lost_audit_response_creates_duplicate_audit(self) -> None:
        block_id = await self.seed_block()
        failure = InjectedFailure("synthetic audit response lost")
        controls = OperationControls(faults=[Fault("edit_history", "insert_one", "after", failure)])
        writer = self.writer(controls)
        with self.assertRaises(InjectedFailure):
            await writer.invoke(
                str(block_id),
                {"title": "synthetic-retry", "status": "draft"},
                {"id": "synthetic-editor"},
            )
        await writer.invoke(
            str(block_id),
            {"title": "synthetic-retry", "status": "draft"},
            {"id": "synthetic-editor"},
        )
        self.assertEqual(writer.controls.trace.count("content_blocks.update_one:persisted"), 2)
        self.assertEqual(len(await self.audit_rows()), 2)

    async def test_12_two_real_writer_calls_can_overwrite_without_cas(self) -> None:
        block_id = await self.seed_block()
        barrier = asyncio.Barrier(2)
        first_controls = OperationControls(before_update_barrier=barrier)
        second_controls = OperationControls(before_update_barrier=barrier)
        first = self.writer(first_controls)
        second = self.writer(second_controls)
        outcomes = await asyncio.gather(
            first.invoke(
                str(block_id),
                {"title": "synthetic-writer-a", "status": "draft"},
                {"id": "synthetic-a"},
            ),
            second.invoke(
                str(block_id),
                {"title": "synthetic-writer-b", "status": "draft"},
                {"id": "synthetic-b"},
            ),
        )
        self.assertEqual(len(outcomes), 2)
        self.assertIn(
            (await self.required_block(block_id))["title"],
            {"synthetic-writer-a", "synthetic-writer-b"},
        )
        self.assertEqual(len(await self.audit_rows()), 2)
        self.assertEqual(first_controls.trace.count("content_blocks.update_one:persisted"), 1)
        self.assertEqual(second_controls.trace.count("content_blocks.update_one:persisted"), 1)

    async def test_13_outer_response_loss_is_not_a_database_rollback(self) -> None:
        block_id = await self.seed_block()
        with self.assertRaises(InjectedFailure):
            await self.invoke_real_writer(block_id)
            raise InjectedFailure("synthetic caller response lost after writer returned")
        self.assertEqual((await self.required_block(block_id))["title"], "synthetic-updated-title")
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_14_transaction_commits_update_and_audit_together(self) -> None:
        block_id = await self.seed_block(revision=0)
        result = await self.invoke_transaction(block_id)
        persisted = await self.required_block(block_id)
        audit = await self.audit_rows()
        self.assertEqual(result["editorial_revision"], 1)
        self.assertEqual(persisted["title"], "synthetic-transaction-title")
        self.assertEqual(persisted["editorial_revision"], 1)
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["operation_id"], "synthetic-operation-12c7")

    async def test_15_transaction_rolls_back_when_audit_fails_before_insert(self) -> None:
        block_id = await self.seed_block(revision=0)
        failure = InjectedFailure("synthetic audit failure before insert")
        controls = OperationControls(
            faults=[Fault("edit_history", "insert_one", "before", failure)]
        )
        with self.assertRaises(InjectedFailure) as caught:
            await self.invoke_transaction(block_id, controls=controls)
        self.assertIs(caught.exception, failure)
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 0)
        self.assertEqual(await self.audit_rows(), [])

    async def test_16_transaction_rolls_back_if_audit_insert_succeeded_but_ack_failed(self) -> None:
        block_id = await self.seed_block(revision=0)
        failure = InjectedFailure("synthetic audit acknowledgement lost inside transaction")
        controls = OperationControls(faults=[Fault("edit_history", "insert_one", "after", failure)])
        with self.assertRaises(InjectedFailure):
            await self.invoke_transaction(block_id, controls=controls)
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 0)
        self.assertEqual(await self.audit_rows(), [])

    async def test_17_transaction_conflict_does_not_change_block_or_audit(self) -> None:
        block_id = await self.seed_block(revision=2)
        with self.assertRaises(BlockRevisionConflict):
            await self.invoke_transaction(block_id, expected_revision=1)
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 2)
        self.assertEqual(await self.audit_rows(), [])

    async def test_18_transaction_retry_does_not_duplicate_operation(self) -> None:
        block_id = await self.seed_block(revision=0)
        await self.invoke_transaction(block_id)
        with self.assertRaises(BlockRevisionConflict):
            await self.invoke_transaction(block_id)
        with self.assertRaises(BlockOperationConflict):
            await self.invoke_transaction(block_id, expected_revision=1)
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 1)
        self.assertEqual(len(await self.audit_rows()), 1)

    async def test_19_two_transactional_writers_have_one_winner(self) -> None:
        block_id = await self.seed_block(revision=0)
        barrier = asyncio.Barrier(2)
        first_controls = OperationControls(before_update_barrier=barrier)
        second_controls = OperationControls(before_update_barrier=barrier)
        outcomes = await asyncio.gather(
            self.invoke_transaction(
                block_id, operation_id="synthetic-a", title="synthetic-a", controls=first_controls
            ),
            self.invoke_transaction(
                block_id, operation_id="synthetic-b", title="synthetic-b", controls=second_controls
            ),
            return_exceptions=True,
        )
        successes = [item for item in outcomes if isinstance(item, dict)]
        failures = [item for item in outcomes if isinstance(item, BaseException)]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], (BlockRevisionConflict, BlockConcurrentWriteConflict))
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 1)
        self.assertEqual(len(await self.audit_rows()), 1)
        self.assertEqual(
            first_controls.trace.count("content_blocks.update_one:before")
            + second_controls.trace.count("content_blocks.update_one:before"),
            2,
        )

    async def test_20_experimental_writer_rejects_revision_override(self) -> None:
        block_id = await self.seed_block(revision=0)
        with self.assertRaises(ValueError):
            await update_block_with_audit_transaction(
                self.database,
                block_id=block_id,
                expected_revision=0,
                operation_id="synthetic-invalid",
                update_fields={"editorial_revision": 500},
                user={"id": "synthetic-editor"},
            )
        self.assertEqual((await self.required_block(block_id))["editorial_revision"], 0)
        self.assertEqual(await self.audit_rows(), [])

    async def test_21_rejects_a_non_disposable_database_name(self) -> None:
        with self.assertRaises(ValueError):
            await update_block_with_audit_transaction(
                SimpleNamespace(name="application_database"),
                block_id=ObjectId(),
                expected_revision=0,
                operation_id="synthetic-operation",
                update_fields={"title": "synthetic"},
                user={"id": "synthetic-editor"},
            )

    async def test_22_every_database_is_bound_to_disposable_identity(self) -> None:
        marker = await self.database["_phase_identity"].find_one({"_id": "owner"})
        self.assertEqual(marker["phase"], _PHASE_LABEL)
        self.assertRegex(self.db_name, r"^editorial_block_audit_test_[a-f0-9]{16}$")


if __name__ == "__main__":
    unittest.main()
