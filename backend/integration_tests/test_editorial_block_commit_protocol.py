"""Persistent MongoDB 7 tests for the isolated 12C.8 block commit contract."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
import unittest
from dataclasses import replace
from secrets import token_hex
from typing import Any
from queue import Queue, Empty

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.uri_parser import parse_uri

from curriculum_contract.editorial_revision_protocol import (
    FencingRejected,
    IdempotencyConflict,
    RevisionConflict,
    WriterAuthorizationError,
    WriterCredential,
)
from curriculum_contract.experimental_editorial_block_commit import (
    EditorialBlockAuditIdentityConflict,
    EditorialBlockNotFound,
    PreparedEditorialBlockUpdate,
    commit_editorial_block_update,
    commit_prepared_editorial_block_update,
    ensure_experimental_indexes,
    prepare_editorial_block_update,
)
from curriculum_contract.mongodb_editorial_revision_adapter import (
    MongoDBEditorialRevisionAdapter,
)
from integration_tests.editorial_block_commit_harness import (
    ClientProxy,
    DatabaseProxy,
    FaultPlan,
    FaultStage,
    InjectedFailure,
)

_PHASE_LABEL = "2.1a.12c8"
_CONTAINER = "trilhacode-12c8-editorial-mongo"
_NETWORK = "trilhacode-12c8-editorial-net"
_IMAGE = "mongo:7.0.43"
_IMAGE_ID = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
_PORT = 27138
_REPLICA_SET = "rs12c8"
_NAMESPACE = "c8_editorial"
_DATABASE_PREFIX = "editorial_revision_test_"
_URI_ENV = "TRILHACODE_12C8_MONGODB_URI"
_INITIAL_TITLE = "synthetic-original-title"


def _docker_json(*args: str) -> Any:
    result = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=10
    )
    return json.loads(result.stdout)


def _verify_owned_docker_resources() -> None:
    container = _docker_json("inspect", _CONTAINER)[0]
    labels = container["Config"].get("Labels") or {}
    if labels.get("io.trilhacode.phase") != _PHASE_LABEL:
        raise RuntimeError("Mongo container is not labeled as owned by this phase")
    if not container["State"]["Running"]:
        raise RuntimeError("phase-owned Mongo container is not running")
    if container["Config"]["Image"] != _IMAGE or container["Image"] != _IMAGE_ID:
        raise RuntimeError("Mongo container does not use the verified MongoDB 7 image")
    if container["Mounts"]:
        raise RuntimeError("Mongo container unexpectedly has a persistent mount")
    tmpfs = container["HostConfig"].get("Tmpfs", {})
    if not {"/data/db", "/data/configdb"}.issubset(tmpfs):
        raise RuntimeError("Mongo data directories are not confined to disposable tmpfs")
    bindings = container["HostConfig"]["PortBindings"].get(f"{_PORT}/tcp", [])
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(_PORT)}]:
        raise RuntimeError("Mongo port is not restricted to its loopback binding")
    networks = container["NetworkSettings"]["Networks"]
    if set(networks) != {_NETWORK}:
        raise RuntimeError("Mongo container has an unexpected network attachment")

    network = _docker_json("network", "inspect", _NETWORK)[0]
    network_labels = network.get("Labels") or {}
    if network_labels.get("io.trilhacode.phase") != _PHASE_LABEL:
        raise RuntimeError("Mongo network is not labeled as owned by this phase")
    if network["Driver"] != "bridge" or network["Internal"]:
        raise RuntimeError("Mongo must use the phase-specific bridge network")
    if network["Options"].get("com.docker.network.bridge.enable_ip_masquerade") != "false":
        raise RuntimeError("phase test network must not provide outbound masquerading")
    if set(network["Containers"]) != {container["Id"]}:
        raise RuntimeError("phase test network contains an unexpected container")


def _verified_uri() -> str:
    uri = os.environ.get(_URI_ENV, "")
    if not uri or "@" in uri or uri.lower().startswith("mongodb+srv://"):
        raise RuntimeError("an explicit credential-free phase-local URI is required")
    parsed = parse_uri(uri)
    if parsed["nodelist"] != [("127.0.0.1", _PORT)]:
        raise RuntimeError("test URI must target only the dedicated loopback port")
    if parsed["username"] is not None or parsed["password"] is not None:
        raise RuntimeError("test credentials are not accepted")
    if parsed["options"].get("replicaSet") != _REPLICA_SET:
        raise RuntimeError("test URI must select the phase replica set")
    if parsed["database"] not in (None, ""):
        raise RuntimeError("test URI must not select an existing database")
    if not re.fullmatch(r"mongodb://127\.0\.0\.1:27138/\?replicaSet=rs12c8", uri):
        raise RuntimeError("test URI has an unexpected form")
    return uri


def _start_worker(config: dict[str, Any]) -> subprocess.Popen[str]:
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    worker_path = os.path.join(os.path.dirname(__file__), "editorial_block_commit_harness.py")
    process = subprocess.Popen(
        [sys.executable, worker_path],
        cwd=backend_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdin is not None
    process.stdin.write(json.dumps(config) + "\n")
    process.stdin.flush()
    return process


def _readline_with_timeout(process: subprocess.Popen[str], timeout: float = 20) -> str:
    if process.stdout is None:
        raise AssertionError("worker stdout is unavailable")
    result: Queue[str] = Queue(maxsize=1)
    reader = threading.Thread(target=lambda: result.put(process.stdout.readline()), daemon=True)
    reader.start()
    try:
        return result.get(timeout=timeout)
    except Empty:
        process.terminate()
        process.wait(timeout=5)
        raise TimeoutError("test-owned worker did not produce its synchronization result")


def _worker_config(
    *,
    mode: str,
    uri: str,
    database_name: str,
    track_id: str,
    writer_id: str,
    secret: str,
    operation_id: str,
    fencing_token: int,
    actor_id: str,
    title: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "uri": uri,
        "database_name": database_name,
        "namespace": _NAMESPACE,
        "track_id": track_id,
        "writer_id": writer_id,
        "secret": secret,
        "operation_id": operation_id,
        "expected_revision": 0,
        "fencing_token": fencing_token,
        "block_id": "synthetic-block-12c8",
        "actor_id": actor_id,
        "title": title,
    }


class EditorialBlockCommitProtocolTests(unittest.TestCase):
    mongo_uri: str

    @classmethod
    def setUpClass(cls) -> None:
        _verify_owned_docker_resources()
        cls.mongo_uri = _verified_uri()

    def setUp(self) -> None:
        self.client = MongoClient(
            self.mongo_uri,
            appname="trilhacode-12c8-tests",
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
            retryWrites=True,
        )
        self.database_name = _DATABASE_PREFIX + token_hex(12)
        self.database = self.client[self.database_name]
        self.run_id = self.database_name.removeprefix(_DATABASE_PREFIX)
        self.track_id = "synthetic-track-12c8"
        self.block_id = "synthetic-block-12c8"
        self.database["_phase_identity"].insert_one(
            {"_id": "owner", "phase": _PHASE_LABEL, "run_id": self.run_id}
        )
        self.adapter = self._new_adapter(self.database)
        self.adapter.initialize_track(self.track_id)
        self.credential = self.adapter.provision_writer_credential(
            self.track_id, "synthetic-writer-a"
        )
        self.authority = self.adapter.provision_fence_authority(
            self.track_id, "synthetic-fence-authority"
        )
        self.fence = self.adapter.advance_fence(self.track_id, self.authority)
        ensure_experimental_indexes(self.database, self.adapter)
        self.database["content_blocks"].insert_one(
            {"_id": self.block_id, "track_id": self.track_id, "title": _INITIAL_TITLE}
        )

    def tearDown(self) -> None:
        marker = self.database["_phase_identity"].find_one({"_id": "owner"})
        expected = {"_id": "owner", "phase": _PHASE_LABEL, "run_id": self.run_id}
        if marker != expected:
            self.client.close()
            self.fail("database identity marker changed; database was not dropped")
        self.client.drop_database(self.database_name)
        self.client.close()

    def _new_adapter(self, database: Any) -> MongoDBEditorialRevisionAdapter:
        adapter = MongoDBEditorialRevisionAdapter(database, namespace=_NAMESPACE)
        topology = adapter.verify_transaction_topology()
        self.assertTrue(topology.sessions_available)
        self.assertEqual(topology.replica_set, _REPLICA_SET)
        self.assertTrue(topology.server_version.startswith("7."))
        return adapter

    def _prepare(
        self,
        *,
        track_id: str | None = None,
        operation_id: str = "synthetic-operation-a",
        expected_revision: int = 0,
        fencing_token: int | None = None,
        credential: WriterCredential | None = None,
        block_id: str | None = None,
        actor_id: str = "synthetic-actor-a",
        title: str = "synthetic-updated-title",
        adapter: MongoDBEditorialRevisionAdapter | None = None,
    ) -> PreparedEditorialBlockUpdate:
        return prepare_editorial_block_update(
            adapter or self.adapter,
            track_id=track_id or self.track_id,
            credential=credential or self.credential,
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self.fence if fencing_token is None else fencing_token,
            block_id=block_id or self.block_id,
            actor_id=actor_id,
            title=title,
        )

    def _commit(
        self,
        *,
        track_id: str | None = None,
        operation_id: str = "synthetic-operation-a",
        expected_revision: int = 0,
        fencing_token: int | None = None,
        credential: WriterCredential | None = None,
        block_id: str | None = None,
        actor_id: str = "synthetic-actor-a",
        title: str = "synthetic-updated-title",
        adapter: MongoDBEditorialRevisionAdapter | None = None,
        database: Any | None = None,
    ) -> Any:
        actual_adapter = adapter or self.adapter
        actual_database = database or self.database
        return commit_editorial_block_update(
            actual_database,
            actual_adapter,
            track_id=track_id or self.track_id,
            credential=credential or self.credential,
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self.fence if fencing_token is None else fencing_token,
            block_id=block_id or self.block_id,
            actor_id=actor_id,
            title=title,
        )

    def _block(self, block_id: str | None = None) -> dict[str, Any]:
        result = self.database["content_blocks"].find_one(
            {"_id": block_id or self.block_id}
        )
        self.assertIsNotNone(result)
        return result

    def _audit_rows(self) -> list[dict[str, Any]]:
        return list(self.database["edit_history"].find({}))

    def _assert_no_confirmed_effects(self, operation_id: str) -> None:
        track = self.database[f"{_NAMESPACE}_tracks"].find_one({"_id": self.track_id})
        self.assertEqual(track["revision"], 0)
        self.assertEqual(self._block()["title"], _INITIAL_TITLE)
        self.assertEqual(self.database[f"{_NAMESPACE}_history"].count_documents({}), 0)
        self.assertEqual(self._audit_rows(), [])
        operation = self.database[f"{_NAMESPACE}_operations"].find_one(
            {"track_id": self.track_id, "operation_id": operation_id}
        )
        if operation is not None:
            self.assertEqual(operation["state"], "PREPARED")
            self.assertNotIn("receipt", operation)

    def _fault_adapter(self, stage: FaultStage) -> tuple[Any, Any, FaultPlan]:
        plan = FaultPlan(stage)
        database = DatabaseProxy(self.database, plan)
        adapter = self._new_adapter(database)
        return database, adapter, plan

    # T1
    def test_t01_success_confirms_block_audit_history_and_receipt(self) -> None:
        receipt = self._commit()
        self.assertEqual(receipt.revision, 1)
        self.assertEqual(self._block()["title"], "synthetic-updated-title")
        self.assertEqual(len(self._audit_rows()), 1)
        self.assertEqual(self.adapter.history(self.track_id)[0].revision, 1)
        self.assertEqual(self.adapter.operation_state(self.track_id, receipt.operation_id).value, "COMMITTED")

    # T2
    def test_t02_revisions_are_monotonic(self) -> None:
        first = self._commit(operation_id="synthetic-operation-1", title="synthetic-title-1")
        second = self._commit(
            operation_id="synthetic-operation-2",
            expected_revision=1,
            title="synthetic-title-2",
        )
        self.assertEqual((first.revision, second.revision), (1, 2))
        self.assertEqual(self.adapter.current_revision(self.track_id), 2)

    # T3
    def test_t03_receipt_is_recoverable_from_adapter_state(self) -> None:
        receipt = self._commit()
        recovered = self.adapter.history(self.track_id)[0]
        operation = self.database[f"{_NAMESPACE}_operations"].find_one(
            {"track_id": self.track_id, "operation_id": receipt.operation_id}
        )
        self.assertEqual(operation["receipt"]["revision"], recovered.revision)

    # T4
    def test_t04_history_is_persisted_and_matches_operation(self) -> None:
        receipt = self._commit()
        history = self.database[f"{_NAMESPACE}_history"].find_one(
            {"track_id": self.track_id, "revision": receipt.revision}
        )
        self.assertEqual(history["operation_id"], receipt.operation_id)
        self.assertEqual(history["fencing_token"], self.fence)

    # T5
    def test_t05_audit_is_required_for_confirmed_mutation(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.BEFORE_AUDIT_INSERT)
        operation_id = "synthetic-no-audit"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T6
    def test_t06_block_audit_history_and_receipt_share_references(self) -> None:
        receipt = self._commit()
        audit = self._audit_rows()[0]
        operation = self.database[f"{_NAMESPACE}_operations"].find_one(
            {"track_id": self.track_id, "operation_id": receipt.operation_id}
        )
        history = self.adapter.read_revision(self.track_id, receipt.revision)
        self.assertEqual(audit["operation_id"], receipt.operation_id)
        self.assertEqual(audit["revision"], receipt.revision)
        self.assertEqual(operation["receipt"]["revision"], receipt.revision)
        self.assertEqual(history.operation_id, receipt.operation_id)

    # T7
    def test_t07_failure_before_block_update_has_no_confirmed_effects(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.BEFORE_BLOCK_UPDATE)
        operation_id = "synthetic-fail-before-block"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T8
    def test_t08_failure_after_block_update_rolls_back_every_component(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.AFTER_BLOCK_UPDATE)
        operation_id = "synthetic-fail-after-block"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T9
    def test_t09_failure_after_audit_insert_rolls_back_audit_and_block(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.AFTER_AUDIT_INSERT)
        operation_id = "synthetic-fail-after-audit"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T10
    def test_t10_failure_before_receipt_rolls_back_history_audit_and_block(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.BEFORE_RECEIPT_WRITE)
        operation_id = "synthetic-fail-before-receipt"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T11
    def test_t11_failure_after_receipt_write_ack_rolls_back_transaction(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.AFTER_RECEIPT_WRITE)
        operation_id = "synthetic-fail-after-receipt-write"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T12
    def test_t12_failure_after_transaction_body_before_commit_rolls_back(self) -> None:
        plan = FaultPlan(FaultStage.BEFORE_COMMIT)
        client_proxy = ClientProxy(self.client, plan)
        database = DatabaseProxy(self.database, plan, client_proxy)
        adapter = self._new_adapter(database)
        operation_id = "synthetic-fail-before-commit"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T13
    def test_t13_lost_response_after_confirmed_commit_replays_receipt(self) -> None:
        operation_id = "synthetic-lost-response"
        with self.assertRaises(InjectedFailure):
            receipt = self._commit(operation_id=operation_id)
            self.assertEqual(receipt.revision, 1)
            raise InjectedFailure("synthetic caller response loss after return")
        replay = self._commit(operation_id=operation_id)
        self.assertTrue(replay.replayed)
        self.assertEqual(replay.revision, 1)
        self.assertEqual(len(self._audit_rows()), 1)

    # T14
    def test_t14_receipt_survives_a_post_commit_read_failure(self) -> None:
        receipt = self._commit(operation_id="synthetic-read-loss")
        plan = FaultPlan(FaultStage.RECEIPT_READ)
        proxy = DatabaseProxy(self.database, plan)
        adapter = self._new_adapter(proxy)
        with self.assertRaises(InjectedFailure):
            adapter.operation_state(self.track_id, receipt.operation_id)
        recovered = self.adapter.operation_state(self.track_id, receipt.operation_id)
        self.assertEqual(recovered.value, "COMMITTED")
        self.assertEqual(len(self._audit_rows()), 1)

    # T15
    def test_t15_storage_failure_after_track_cas_is_atomic(self) -> None:
        database, adapter, _ = self._fault_adapter(FaultStage.AFTER_TRACK_UPDATE)
        operation_id = "synthetic-track-storage-failure"
        with self.assertRaises(InjectedFailure):
            self._commit(operation_id=operation_id, adapter=adapter, database=database)
        self._assert_no_confirmed_effects(operation_id)

    # T16
    def test_t16_process_exit_inside_transaction_aborts_uncommitted_work(self) -> None:
        process = _start_worker(
            _worker_config(
                mode="crash",
                uri=self.mongo_uri,
                database_name=self.database_name,
                track_id=self.track_id,
                writer_id=self.credential.writer_id,
                secret=self.credential._secret,
                operation_id="synthetic-process-crash",
                fencing_token=self.fence,
                actor_id="synthetic-crash-actor",
                title="synthetic-crash-title",
            )
        )
        try:
            self.assertEqual(_readline_with_timeout(process), "PREPARED\n")
            self.assertEqual(process.wait(timeout=20), 73)

            deadline = time.monotonic() + 12
            while time.monotonic() < deadline:
                operation = self.database[f"{_NAMESPACE}_operations"].find_one(
                    {"track_id": self.track_id, "operation_id": "synthetic-process-crash"}
                )
                if (
                    operation is not None
                    and operation["state"] == "prepared"
                    and self.database[f"{_NAMESPACE}_tracks"].find_one(
                        {"_id": self.track_id}
                    )["revision"]
                    == 0
                    and self.database["edit_history"].count_documents({}) == 0
                ):
                    break
                time.sleep(0.1)
            self._assert_no_confirmed_effects("synthetic-process-crash")
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()

    # T17
    def test_t17_expected_revision_is_accepted(self) -> None:
        receipt = self._commit(expected_revision=0)
        self.assertEqual(receipt.parent_revision, 0)
        self.assertEqual(receipt.revision, 1)

    # T18
    def test_t18_stale_revision_is_rejected(self) -> None:
        self._commit(operation_id="synthetic-first", expected_revision=0)
        with self.assertRaises(RevisionConflict):
            self._commit(
                operation_id="synthetic-stale",
                expected_revision=0,
                title="synthetic-stale-title",
            )
        self.assertEqual(self._block()["title"], "synthetic-updated-title")
        self.assertEqual(len(self._audit_rows()), 1)

    # T19
    def test_t19_two_independent_processes_contend_on_same_revision(self) -> None:
        writer_a = self.adapter.provision_writer_credential(self.track_id, "synthetic-writer-a2")
        writer_b = self.adapter.provision_writer_credential(self.track_id, "synthetic-writer-b2")
        workers = [
            _start_worker(
                _worker_config(
                    mode="race",
                    uri=self.mongo_uri,
                    database_name=self.database_name,
                    track_id=self.track_id,
                    writer_id=credential.writer_id,
                    secret=credential._secret,
                    operation_id=f"synthetic-race-{suffix}",
                    fencing_token=self.fence,
                    actor_id=f"synthetic-actor-{suffix}",
                    title=f"synthetic-title-{suffix}",
                )
            )
            for credential, suffix in ((writer_a, "a"), (writer_b, "b"))
        ]
        try:
            ready = [_readline_with_timeout(worker) for worker in workers]
            self.assertEqual(ready, ["READY\n", "READY\n"])
            for worker in workers:
                assert worker.stdin is not None
                worker.stdin.write("GO\n")
                worker.stdin.flush()
            outcomes = [json.loads(_readline_with_timeout(worker)) for worker in workers]
            self.assertEqual([worker.wait(timeout=20) for worker in workers], [0, 0])
        finally:
            for worker in workers:
                if worker.poll() is None:
                    worker.terminate()
                    worker.wait(timeout=5)
                if worker.stdin:
                    worker.stdin.close()
                if worker.stdout:
                    worker.stdout.close()
                if worker.stderr:
                    worker.stderr.close()
        self.assertEqual(sum(item.get("result") == "committed" for item in outcomes), 1)
        self.assertEqual(sum(item.get("result") == "revision_conflict" for item in outcomes), 1)
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        self.assertEqual(len(self._audit_rows()), 1)
        self.assertEqual(self.database[f"{_NAMESPACE}_history"].count_documents({}), 1)

    # T20
    def test_t20_concurrent_updates_do_not_lose_the_winner(self) -> None:
        self._commit(operation_id="synthetic-t20-winner", title="synthetic-preserved-winner")
        with self.assertRaises(RevisionConflict):
            self._commit(
                operation_id="synthetic-t20-stale",
                expected_revision=0,
                title="synthetic-overwrite-attempt",
            )
        self.assertEqual(self._block()["title"], "synthetic-preserved-winner")
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)

    # T21
    def test_t21_revision_conflict_has_no_partial_audit_or_block_effect(self) -> None:
        self._commit(operation_id="synthetic-winner", expected_revision=0)
        with self.assertRaises(RevisionConflict):
            self._commit(
                operation_id="synthetic-loser",
                expected_revision=0,
                title="synthetic-loser-title",
            )
        self.assertEqual(self.database[f"{_NAMESPACE}_history"].count_documents({}), 1)
        self.assertEqual(len(self._audit_rows()), 1)
        self.assertEqual(self._block()["title"], "synthetic-updated-title")

    # T22
    def test_t22_confirmed_revision_has_matching_history_and_receipt(self) -> None:
        receipt = self._commit()
        track = self.database[f"{_NAMESPACE}_tracks"].find_one({"_id": self.track_id})
        history = self.database[f"{_NAMESPACE}_history"].find_one(
            {"track_id": self.track_id, "revision": 1}
        )
        operation = self.database[f"{_NAMESPACE}_operations"].find_one(
            {"track_id": self.track_id, "operation_id": receipt.operation_id}
        )
        self.assertEqual(track["revision"], history["revision"])
        self.assertEqual(history["revision"], operation["receipt"]["revision"])

    # T23
    def test_t23_current_fence_allows_commit(self) -> None:
        receipt = self._commit(fencing_token=self.fence)
        self.assertEqual(receipt.fencing_token, self.fence)

    # T24
    def test_t24_old_fence_is_rejected(self) -> None:
        new_fence = self.adapter.advance_fence(self.track_id, self.authority)
        with self.assertRaises(FencingRejected):
            self._commit(fencing_token=self.fence)
        self.assertEqual(new_fence, self.fence + 1)
        self._assert_no_confirmed_effects("synthetic-operation-a")

    # T25
    def test_t25_fence_advance_invalidates_prepared_writer(self) -> None:
        prepared = self._prepare(operation_id="synthetic-prepared-old-fence")
        new_fence = self.adapter.advance_fence(self.track_id, self.authority)
        with self.assertRaises(FencingRejected):
            commit_prepared_editorial_block_update(
                self.database, self.adapter, self.credential, prepared
            )
        self.assertEqual(new_fence, 2)
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self._block()["title"], _INITIAL_TITLE)
        self.assertEqual(self._audit_rows(), [])

    # T26
    def test_t26_fence_can_advance_without_editorial_revision(self) -> None:
        revision_before = self.adapter.current_revision(self.track_id)
        next_fence = self.adapter.advance_fence(self.track_id, self.authority)
        self.assertEqual(next_fence, self.fence + 1)
        self.assertEqual(self.adapter.current_revision(self.track_id), revision_before)
        self.assertEqual(self._block()["title"], _INITIAL_TITLE)

    # T27
    def test_t27_fence_and_commit_race_has_a_serializable_outcome(self) -> None:
        prepared = self._prepare(operation_id="synthetic-fence-race")
        barrier = threading.Barrier(2)
        client_a = MongoClient(self.mongo_uri, appname="trilhacode-12c8-fence-race-a")
        client_b = MongoClient(self.mongo_uri, appname="trilhacode-12c8-fence-race-b")
        self.addCleanup(client_a.close)
        self.addCleanup(client_b.close)
        adapter_a = self._new_adapter(client_a[self.database_name])
        adapter_b = self._new_adapter(client_b[self.database_name])
        outcomes: list[tuple[str, Any]] = []
        outcome_lock = threading.Lock()

        def commit_old() -> None:
            barrier.wait(timeout=10)
            try:
                result = commit_prepared_editorial_block_update(
                    client_a[self.database_name], adapter_a, self.credential, prepared
                )
                value: tuple[str, Any] = ("committed", result)
            except FencingRejected:
                value = ("rejected", None)
            with outcome_lock:
                outcomes.append(value)

        def advance() -> None:
            barrier.wait(timeout=10)
            result = adapter_b.advance_fence(self.track_id, self.authority)
            with outcome_lock:
                outcomes.append(("advanced", result))

        threads = [threading.Thread(target=commit_old), threading.Thread(target=advance)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=20)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(len(outcomes), 2)
        commit_result = next(item for item in outcomes if item[0] in {"committed", "rejected"})
        fence_result = next(item for item in outcomes if item[0] == "advanced")
        self.assertEqual(fence_result[1], 2)
        if commit_result[0] == "committed":
            self.assertEqual(commit_result[1].fencing_token, 1)
            self.assertEqual(self.adapter.current_revision(self.track_id), 1)
            self.assertEqual(len(self._audit_rows()), 1)
        else:
            self.assertEqual(self.adapter.current_revision(self.track_id), 0)
            self.assertEqual(self._block()["title"], _INITIAL_TITLE)
            self.assertEqual(self._audit_rows(), [])

    # T28
    def test_t28_stale_fence_conflict_creates_no_audit_or_receipt(self) -> None:
        prepared = self._prepare(operation_id="synthetic-fence-conflict")
        self.adapter.advance_fence(self.track_id, self.authority)
        with self.assertRaises(FencingRejected):
            commit_prepared_editorial_block_update(
                self.database, self.adapter, self.credential, prepared
            )
        operation = self.database[f"{_NAMESPACE}_operations"].find_one(
            {"track_id": self.track_id, "operation_id": "synthetic-fence-conflict"}
        )
        self.assertEqual(operation["state"], "PREPARED")
        self.assertNotIn("receipt", operation)
        self.assertEqual(self._audit_rows(), [])

    # T29
    def test_t29_identical_replay_returns_original_receipt(self) -> None:
        original = self._commit()
        replay = self._commit()
        self.assertTrue(replay.replayed)
        self.assertEqual(replay, replace(original, replayed=True))

    # T30
    def test_t30_replay_does_not_duplicate_audit(self) -> None:
        self._commit()
        self._commit()
        self.assertEqual(len(self._audit_rows()), 1)

    # T31
    def test_t31_replay_does_not_advance_revision(self) -> None:
        self._commit()
        self._commit()
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)

    # T32
    def test_t32_replay_does_not_repeat_block_mutation(self) -> None:
        plan = FaultPlan()
        database = DatabaseProxy(self.database, plan)
        adapter = self._new_adapter(database)
        first = self._commit(adapter=adapter, database=database)
        initial_updates = plan.calls.count(FaultStage.BEFORE_BLOCK_UPDATE.value)
        replay = self._commit(adapter=adapter, database=database)
        self.assertTrue(replay.replayed)
        self.assertEqual(plan.calls.count(FaultStage.BEFORE_BLOCK_UPDATE.value), initial_updates)
        self.assertEqual(first.revision, 1)

    # T33
    def test_t33_same_key_with_different_intent_is_rejected(self) -> None:
        self._commit(operation_id="synthetic-key-conflict")
        with self.assertRaises(IdempotencyConflict):
            self._prepare(
                operation_id="synthetic-key-conflict",
                title="synthetic-different-intent",
            )
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        self.assertEqual(len(self._audit_rows()), 1)

    # T34
    def test_t34_concurrent_same_operation_has_one_effect(self) -> None:
        credential = self.credential
        barrier = threading.Barrier(2)
        receipts: list[Any] = []
        errors: list[type[BaseException]] = []
        guard = threading.Lock()

        def duplicate_commit() -> None:
            client = MongoClient(self.mongo_uri, appname="trilhacode-12c8-idempotency-race")
            try:
                database = client[self.database_name]
                adapter = self._new_adapter(database)
                prepared = self._prepare(
                    operation_id="synthetic-duplicate-concurrent",
                    adapter=adapter,
                    credential=credential,
                )
                barrier.wait(timeout=10)
                receipt = commit_prepared_editorial_block_update(
                    database, adapter, credential, prepared
                )
                with guard:
                    receipts.append(receipt)
            except Exception as exc:
                with guard:
                    errors.append(type(exc))
            finally:
                client.close()

        threads = [threading.Thread(target=duplicate_commit) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=20)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(len(receipts), 2)
        self.assertEqual({receipt.revision for receipt in receipts}, {1})
        self.assertEqual(sum(receipt.replayed for receipt in receipts), 1)
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        self.assertEqual(len(self._audit_rows()), 1)

    # T35
    def test_t35_receipt_survives_client_and_adapter_recreation(self) -> None:
        original = self._commit(operation_id="synthetic-client-restart")
        self.client.close()
        self.client = MongoClient(
            self.mongo_uri,
            appname="trilhacode-12c8-restarted-client",
            serverSelectionTimeoutMS=8000,
        )
        self.database = self.client[self.database_name]
        self.adapter = self._new_adapter(self.database)
        replay = self._commit(operation_id="synthetic-client-restart")
        self.assertTrue(replay.replayed)
        self.assertEqual(replay.revision, original.revision)

    # T36
    def test_t36_response_loss_after_commit_recovers_without_duplication(self) -> None:
        operation_id = "synthetic-response-lost"
        first = self._commit(operation_id=operation_id)
        with self.assertRaises(InjectedFailure):
            raise InjectedFailure("synthetic response channel lost after durable return")
        second = self._commit(operation_id=operation_id)
        self.assertTrue(second.replayed)
        self.assertEqual(second.revision, first.revision)
        self.assertEqual(len(self._audit_rows()), 1)

    # T37
    def test_t37_receipt_and_audit_reference_same_commit(self) -> None:
        receipt = self._commit()
        audit = self._audit_rows()[0]
        record = self.adapter.read_revision(self.track_id, receipt.revision)
        self.assertEqual((audit["track_id"], audit["operation_id"], audit["revision"]),
                         (record.track_id, record.operation_id, record.revision))
        self.assertEqual(audit["writer_id"], receipt.writer_id)
        self.assertEqual(audit["fencing_token"], receipt.fencing_token)

    # T38
    def test_t38_operation_scope_prevents_cross_writer_confusion(self) -> None:
        self._commit(operation_id="synthetic-scoped-key")
        other_writer = self.adapter.provision_writer_credential(
            self.track_id, "synthetic-writer-other"
        )
        with self.assertRaises(IdempotencyConflict):
            self._prepare(
                operation_id="synthetic-scoped-key",
                credential=other_writer,
            )
        other_track = "synthetic-track-other"
        self.adapter.initialize_track(other_track)
        other_credential = self.adapter.provision_writer_credential(
            other_track, "synthetic-writer-other-track"
        )
        other_fence = self.adapter.advance_fence(
            other_track,
            self.adapter.provision_fence_authority(other_track, "synthetic-authority-other"),
        )
        other_block = "synthetic-block-other-track"
        self.database["content_blocks"].insert_one(
            {"_id": other_block, "track_id": other_track, "title": _INITIAL_TITLE}
        )
        prepared = self._prepare(
            track_id=other_track,
            operation_id="synthetic-scoped-key",
            expected_revision=0,
            fencing_token=other_fence,
            credential=other_credential,
            block_id=other_block,
            actor_id="synthetic-other-actor",
            title="synthetic-other-title",
        )
        receipt = commit_prepared_editorial_block_update(
            self.database, self.adapter, other_credential, prepared
        )
        self.assertEqual(receipt.track_id, other_track)
        self.assertEqual(self.adapter.current_revision(self.track_id), 1)
        self.assertEqual(self.adapter.current_revision(other_track), 1)

    def test_t39_writer_credential_revocation_blocks_confirmation(self) -> None:
        prepared = self._prepare(operation_id="synthetic-revoked-writer")
        self.adapter.revoke_writer_credential(self.track_id, self.credential.writer_id)
        with self.assertRaises(WriterAuthorizationError):
            commit_prepared_editorial_block_update(
                self.database, self.adapter, self.credential, prepared
            )
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self._audit_rows(), [])

    def test_t40_missing_block_aborts_revision_audit_and_history(self) -> None:
        operation_id = "synthetic-missing-block"
        with self.assertRaises(EditorialBlockNotFound):
            self._commit(operation_id=operation_id, block_id="synthetic-absent-block")
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self.database[f"{_NAMESPACE}_history"].count_documents({}), 0)
        self.assertEqual(self._audit_rows(), [])

    def test_t41_duplicate_audit_identity_aborts_new_commit(self) -> None:
        self.database["edit_history"].insert_one(
            {
                "track_id": self.track_id,
                "operation_id": "synthetic-preexisting-audit",
                "revision": 1,
            }
        )
        with self.assertRaises(EditorialBlockAuditIdentityConflict):
            self._commit(operation_id="synthetic-preexisting-audit")
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self._block()["title"], _INITIAL_TITLE)
        self.assertEqual(self.database[f"{_NAMESPACE}_history"].count_documents({}), 0)
        self.assertEqual(self.database["edit_history"].count_documents({}), 1)

    def test_t42_prepared_operation_is_not_a_confirmed_revision(self) -> None:
        prepared = self._prepare(operation_id="synthetic-only-prepared")
        self.assertEqual(prepared.revision.operation_id, "synthetic-only-prepared")
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self.adapter.history(self.track_id), ())
        self.assertEqual(self._block()["title"], _INITIAL_TITLE)
        self.assertEqual(self._audit_rows(), [])

    def test_t43_invalid_synthetic_input_is_rejected_before_persistence(self) -> None:
        with self.assertRaises(ValueError):
            self._prepare(title="x" * 300)
        with self.assertRaises(ValueError):
            self._prepare(operation_id="", title="synthetic-valid")
        self.assertEqual(self.adapter.current_revision(self.track_id), 0)
        self.assertEqual(self.database[f"{_NAMESPACE}_operations"].count_documents({}), 0)


if __name__ == "__main__":
    unittest.main()
