"""MongoDB integration tests; they only use an explicit loopback test URI.

Set EDITORIAL_REVISION_TEST_URI to a credential-free localhost URI whose path is
an editorial_revision_test_* database. The adapter then creates a fresh,
randomly named database per test and drops it only after checking its ownership
marker. No application or deployment configuration is read.
"""
from __future__ import annotations

import ipaddress
import multiprocessing
import os
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from curriculum_contract.editorial_revision_protocol import (
    FenceAuthorityCredential,
    FencingRejected,
    IdempotencyConflict,
    InvalidProposal,
    OperationAborted,
    OperationState,
    RevisionConflict,
    WriterCredential,
)
from curriculum_contract.mongodb_editorial_revision_adapter import (
    MongoDBEditorialRevisionAdapter,
)

_TEST_URI = os.environ.get("EDITORIAL_REVISION_TEST_URI", "")
_TEST_DB_PATH_PREFIX = "editorial_revision_test_"
_NAMESPACE = "phase12c2"
_TRACK = "synthetic-track"
_WRITER = "writer-a"
_AUTHORITY = "fence-authority"


def _validate_local_test_uri(uri: str) -> str:
    parsed = urlsplit(uri)
    if parsed.scheme != "mongodb" or not parsed.hostname or "," in parsed.netloc:
        raise ValueError("test URI must be a single-host mongodb:// URI")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("test URI must not contain credentials")
    database_name = parsed.path.lstrip("/")
    if not database_name.startswith(_TEST_DB_PATH_PREFIX):
        raise ValueError("test URI database path must use editorial_revision_test_*")
    if not 8 <= len(database_name[len(_TEST_DB_PATH_PREFIX):]) <= 64:
        raise ValueError("test URI database path has an invalid test suffix")
    options = parse_qs(parsed.query, keep_blank_values=True)
    if set(options) - {"replicaSet"}:
        raise ValueError("only the replicaSet query option is accepted")
    host = parsed.hostname.lower()
    if host != "localhost":
        try:
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError("test URI must point to a loopback address")
        except ValueError as exc:
            if "test URI must point" in str(exc):
                raise
            raise ValueError("test URI must point to localhost or a loopback IP") from exc
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError("test URI port is invalid")
    return database_name


def _process_action(
    uri: str,
    database_name: str,
    namespace: str,
    action: str,
    prepared: object | None,
    credential_values: tuple[str, str, str] | None,
    authority_values: tuple[str, str, str] | None,
    barrier: object | None,
    result_queue: object,
) -> None:
    from pymongo import MongoClient

    from curriculum_contract.editorial_revision_protocol import (
        FenceAuthorityCredential,
        FencingRejected,
        RevisionConflict,
        WriterCredential,
    )
    from curriculum_contract.mongodb_editorial_revision_adapter import (
        MongoDBEditorialRevisionAdapter,
    )

    client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    try:
        adapter = MongoDBEditorialRevisionAdapter(
            client[database_name], namespace=namespace
        )
        adapter.verify_transaction_topology()
        if barrier is not None:
            barrier.wait(timeout=20)
        if action == "advance":
            assert authority_values is not None
            authority = FenceAuthorityCredential(*authority_values)
            result_queue.put(("OK", adapter.advance_fence(authority.track_id, authority)))
            return
        assert prepared is not None and credential_values is not None
        credential = WriterCredential(*credential_values)
        try:
            receipt = adapter.commit(prepared, credential)
            result_queue.put(("OK", receipt.revision, receipt.replayed))
        except RevisionConflict as exc:
            result_queue.put(("ERROR", "RevisionConflict", exc.expected_revision, exc.actual_revision))
        except FencingRejected as exc:
            result_queue.put(("ERROR", "FencingRejected", exc.supplied_fence, exc.current_fence))
        except Exception as exc:
            result_queue.put(("ERROR", type(exc).__name__))
    except Exception as exc:
        result_queue.put(("ERROR", type(exc).__name__))
    finally:
        client.close()


class MongoTestUriSafetyTests(unittest.TestCase):
    def test_rejects_remote_host_and_credentials(self):
        with self.assertRaises(ValueError):
            _validate_local_test_uri(
                "mongodb://example.invalid/editorial_revision_test_abcdefgh"
            )
        with self.assertRaises(ValueError):
            _validate_local_test_uri(
                "mongodb://" + "user" + ":" + "pass"
                + "@localhost/editorial_revision_test_abcdefgh"
            )

    def test_rejects_srv_and_non_test_database(self):
        with self.assertRaises(ValueError):
            _validate_local_test_uri(
                "mongodb+srv://localhost/editorial_revision_test_abcdefgh"
            )
        with self.assertRaises(ValueError):
            _validate_local_test_uri("mongodb://localhost/trilhacode")

    def test_accepts_only_localhost_test_uri(self):
        self.assertEqual(
            _validate_local_test_uri(
                "mongodb://127.0.0.1:27017/editorial_revision_test_abcdefgh?replicaSet=rs0"
            ),
            "editorial_revision_test_abcdefgh",
        )


@unittest.skipUnless(
    _TEST_URI,
    "MongoDB integration disabled: set explicit credential-free loopback test URI",
)
class MongoEditorialRevisionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _validate_local_test_uri(_TEST_URI)

    def setUp(self):
        from pymongo import MongoClient

        self.client = MongoClient(
            _TEST_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000
        )
        self.addCleanup(self.client.close)
        self.database_name = f"editorial_revision_test_{uuid.uuid4().hex}"
        self.database = self.client[self.database_name]
        self.adapter = MongoDBEditorialRevisionAdapter(
            self.database, namespace=_NAMESPACE
        )
        self.topology = self.adapter.verify_transaction_topology()
        if not self.topology.server_version.startswith("7."):
            self.fail("integration tests require MongoDB major version 7")
        if not self.topology.replica_set:
            self.fail("integration tests require a transaction-capable replica set")

        self.owner_token = uuid.uuid4().hex
        self.database["_phase_owner"].insert_one(
            {"_id": "owner", "token": self.owner_token, "purpose": "phase-12c2"}
        )
        self.addCleanup(self._cleanup_owned_database)
        self.adapter.ensure_indexes()
        self.adapter.initialize_track(_TRACK)
        self.authority = self.adapter.provision_fence_authority(_TRACK, _AUTHORITY)
        self.fence = self.adapter.advance_fence(_TRACK, self.authority)
        self.credential = self.adapter.provision_writer_credential(_TRACK, _WRITER)
        self.credential_b = self.adapter.provision_writer_credential(_TRACK, "writer-b")

    def _cleanup_owned_database(self):
        marker = self.database["_phase_owner"].find_one({"_id": "owner"})
        if marker is not None and marker.get("token") == self.owner_token:
            self.client.drop_database(self.database_name)
        elif marker is not None:
            raise AssertionError("test database ownership marker changed; refusing cleanup")

    def _prepare(
        self,
        operation_id: str,
        *,
        writer: WriterCredential | None = None,
        expected_revision: int = 0,
        fence: int | None = None,
        payload: dict | None = None,
        track_id: str = _TRACK,
    ):
        return self.adapter.prepare(
            track_id=track_id,
            credential=writer or self.credential,
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self.fence if fence is None else fence,
            payload={"value": operation_id} if payload is None else payload,
        )

    @staticmethod
    def _credential_values(credential: WriterCredential) -> tuple[str, str, str]:
        return credential.track_id, credential.writer_id, credential._secret

    @staticmethod
    def _authority_values(
        authority: FenceAuthorityCredential,
    ) -> tuple[str, str, str]:
        return authority.track_id, authority.authority_id, authority._secret

    def _run_processes(self, tasks: list[tuple]) -> list[tuple]:
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(len(tasks))
        result_queue = context.Queue()
        processes = [
            context.Process(
                target=_process_action,
                args=(*task, barrier, result_queue),
            )
            for task in tasks
        ]
        for process in processes:
            process.start()
        results = []
        try:
            for _ in processes:
                results.append(result_queue.get(timeout=40))
            for process in processes:
                process.join(timeout=10)
            hanging = [process for process in processes if process.is_alive()]
            for process in hanging:
                process.terminate()
                process.join(timeout=5)
            self.assertFalse(hanging, "phase-owned test child process did not exit")
            self.assertEqual([process.exitcode for process in processes], [0] * len(processes))
            return results
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=5)
            result_queue.close()
            result_queue.join_thread()

    def test_t1_initializes_synthetic_track_at_revision_zero(self):
        state = self.adapter.initialize_track("synthetic-initialized-track")
        self.assertEqual(state.revision, 0)
        self.assertEqual(state.fencing_epoch, 0)
        self.assertEqual(state.control_sequence, 0)

    def test_t2_revisions_are_server_assigned_and_monotonic(self):
        for expected in range(3):
            handle = self._prepare(
                f"sequence-{expected}",
                expected_revision=expected,
                payload={"sequence": expected + 1},
            )
            receipt = self.adapter.commit(handle, self.credential)
            self.assertEqual(receipt.revision, expected + 1)
        self.assertEqual(self.adapter.current_revision(_TRACK), 3)
        self.assertEqual([item.revision for item in self.adapter.history(_TRACK)], [1, 2, 3])

    def test_t3_two_threads_on_same_base_have_one_cas_winner(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor

        handles = [
            self._prepare("thread-a", payload={"value": "a"}),
            self._prepare(
                "thread-b", writer=self.credential_b, payload={"value": "b"}
            ),
        ]
        credentials = [self.credential, self.credential_b]
        barrier = threading.Barrier(2)

        def commit_one(index):
            barrier.wait(timeout=15)
            try:
                return ("OK", self.adapter.commit(handles[index], credentials[index]).revision)
            except RevisionConflict:
                return ("ERROR", "RevisionConflict")

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(commit_one, range(2)))
        self.assertEqual(sum(result[0] == "OK" for result in results), 1)
        self.assertEqual(sum(result[1] == "RevisionConflict" for result in results), 1)
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)
        self.assertEqual(len(self.adapter.history(_TRACK)), 1)

    def test_t4_independent_processes_compete_for_one_revision(self):
        handles = [
            self._prepare("proc-a", payload={"value": "a"}),
            self._prepare(
                "proc-b", writer=self.credential_b, payload={"value": "b"}
            ),
        ]
        tasks = [
            (
                _TEST_URI,
                self.database_name,
                _NAMESPACE,
                "commit",
                handle,
                self._credential_values(credential),
                None,
            )
            for handle, credential in zip(handles, (self.credential, self.credential_b))
        ]
        results = self._run_processes(tasks)
        self.assertEqual(sum(item[0] == "OK" for item in results), 1)
        self.assertEqual(
            sum(item[:2] == ("ERROR", "RevisionConflict") for item in results), 1
        )
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)
        self.assertEqual([row.revision for row in self.adapter.history(_TRACK)], [1])

    def test_t5_stale_revision_is_rejected_and_draft_is_preserved(self):
        stale = self._prepare("stale", payload={"draft": "preserve"})
        winner = self._prepare("winner", payload={"draft": "published"})
        self.adapter.commit(winner, self.credential)
        with self.assertRaises(RevisionConflict):
            self.adapter.commit(stale, self.credential)
        self.assertEqual(self.adapter.prepared_payload(_TRACK, "stale", self.credential)["draft"], "preserve")

    def test_t6_old_writer_process_is_rejected_after_fence_takeover(self):
        stale = self._prepare("old-writer", payload={"value": "stale"})
        advance_task = (
            _TEST_URI,
            self.database_name,
            _NAMESPACE,
            "advance",
            None,
            None,
            self._authority_values(self.authority),
        )
        advanced = self._run_processes([advance_task])[0]
        self.assertEqual(advanced, ("OK", self.fence + 1))

        commit_task = (
            _TEST_URI,
            self.database_name,
            _NAMESPACE,
            "commit",
            stale,
            self._credential_values(self.credential),
            None,
        )
        result = self._run_processes([commit_task])[0]
        self.assertEqual(result[:2], ("ERROR", "FencingRejected"))
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)

    def test_t7_old_fence_is_rejected_without_editorial_revision_change(self):
        stale = self._prepare("fence-only", payload={"value": "unchanged"})
        self.assertEqual(self.adapter.advance_fence(_TRACK, self.authority), self.fence + 1)
        with self.assertRaises(FencingRejected):
            self.adapter.commit(stale, self.credential)
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)
        self.assertEqual(self.adapter.history(_TRACK), ())

    def test_t8_persistent_idempotency_returns_original_receipt(self):
        prepared = self._prepare("persistent-replay", payload={"value": "stable"})
        first = self.adapter.commit(prepared, self.credential)
        second = self.adapter.commit(prepared, self.credential)
        self.assertEqual((second.revision, second.fingerprint), (first.revision, first.fingerprint))
        self.assertTrue(second.replayed)
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)

    def test_t9_new_process_recovers_receipt_after_client_restart(self):
        prepared = self._prepare("process-replay", payload={"value": "stable"})
        first = self._run_processes(
            [
                (
                    _TEST_URI,
                    self.database_name,
                    _NAMESPACE,
                    "commit",
                    prepared,
                    self._credential_values(self.credential),
                    None,
                )
            ]
        )[0]
        replay = self._run_processes(
            [
                (
                    _TEST_URI,
                    self.database_name,
                    _NAMESPACE,
                    "commit",
                    prepared,
                    self._credential_values(self.credential),
                    None,
                )
            ]
        )[0]
        self.assertEqual(first, ("OK", 1, False))
        self.assertEqual(replay, ("OK", 1, True))
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)

    def test_t10_reused_operation_identity_with_different_intent_conflicts(self):
        self._prepare("collision", payload={"value": "first"})
        with self.assertRaises(IdempotencyConflict):
            self._prepare("collision", payload={"value": "changed"})
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)

    def test_t11_concurrent_identical_process_retries_create_one_revision(self):
        prepared = self._prepare("same-process-operation", payload={"value": "once"})
        task = (
            _TEST_URI,
            self.database_name,
            _NAMESPACE,
            "commit",
            prepared,
            self._credential_values(self.credential),
            None,
        )
        results = self._run_processes([task, task])
        self.assertEqual([item[1] for item in results], [1, 1])
        self.assertEqual(sum(item[2] for item in results), 1)
        self.assertEqual(len(self.adapter.history(_TRACK)), 1)

    def test_t12_operation_identity_is_isolated_between_tracks(self):
        other_track = "synthetic-other-track"
        self.adapter.initialize_track(other_track)
        other_authority = self.adapter.provision_fence_authority(other_track, _AUTHORITY)
        other_fence = self.adapter.advance_fence(other_track, other_authority)
        other_writer = self.adapter.provision_writer_credential(other_track, _WRITER)
        first = self._prepare("same-operation-id", payload={"track": "A"})
        second = self._prepare(
            "same-operation-id",
            track_id=other_track,
            writer=other_writer,
            fence=other_fence,
            payload={"track": "B"},
        )
        self.assertEqual(self.adapter.commit(first, self.credential).revision, 1)
        self.assertEqual(self.adapter.commit(second, other_writer).revision, 1)
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)
        self.assertEqual(self.adapter.current_revision(other_track), 1)

    def test_t13_abandoned_preparation_does_not_create_revision(self):
        prepared = self._prepare("abandoned", payload={"value": "not committed"})
        self.assertTrue(self.adapter.abandon(prepared, self.credential))
        self.assertFalse(self.adapter.abandon(prepared, self.credential))
        with self.assertRaises(OperationAborted):
            self.adapter.commit(prepared, self.credential)
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)
        self.assertEqual(self.adapter.history(_TRACK), ())

    def test_t14_failure_before_commit_leaves_no_confirmation(self):
        self._prepare("before-commit", payload={"value": "prepared only"})
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)
        self.assertEqual(self.adapter.history(_TRACK), ())
        self.assertEqual(
            self.adapter.operation_state(_TRACK, "before-commit"),
            OperationState.PREPARED,
        )

    def test_t15_lost_ack_after_commit_is_recovered_by_new_adapter(self):
        prepared = self._prepare("lost-ack", payload={"value": "committed"})
        first = self.adapter.commit(prepared, self.credential)
        self.assertEqual(first.revision, 1)
        # Fault is injected only in the caller after the real commit returned.
        with self.assertRaises(TimeoutError):
            raise TimeoutError("simulated lost acknowledgement after confirmed commit")
        adapter_after_restart = MongoDBEditorialRevisionAdapter(
            self.database, namespace=_NAMESPACE
        )
        adapter_after_restart.verify_transaction_topology()
        replay = adapter_after_restart.commit(prepared, self.credential)
        self.assertTrue(replay.replayed)
        self.assertEqual(replay.revision, 1)
        self.assertEqual(len(adapter_after_restart.history(_TRACK)), 1)

    def test_t16_history_and_receipt_survive_adapter_recreation(self):
        prepared = self._prepare("history-recreated", payload={"value": "durable"})
        self.adapter.commit(prepared, self.credential)
        recreated = MongoDBEditorialRevisionAdapter(
            self.database, namespace=_NAMESPACE
        )
        recreated.verify_transaction_topology()
        self.assertEqual(recreated.current_revision(_TRACK), 1)
        self.assertEqual(recreated.history(_TRACK)[0].operation_id, "history-recreated")
        self.assertEqual(
            recreated.commit(prepared, self.credential).revision,
            1,
        )

    def test_t17_transaction_failure_rolls_back_head_history_and_receipt(self):
        prepared = self._prepare("rollback-transaction", payload={"value": "atomic"})
        original_history = self.adapter._history

        class FailBeforeHistoryInsert:
            def __getattr__(self, name):
                return getattr(original_history, name)

            def insert_one(self, *args, **kwargs):
                raise RuntimeError("controlled client-side failure inside transaction")

        self.adapter._history = FailBeforeHistoryInsert()
        try:
            with self.assertRaisesRegex(RuntimeError, "controlled client-side failure"):
                self.adapter.commit(prepared, self.credential)
        finally:
            self.adapter._history = original_history
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)
        self.assertEqual(self.adapter.history(_TRACK), ())
        self.assertEqual(
            self.adapter.operation_state(_TRACK, "rollback-transaction"),
            OperationState.PREPARED,
        )

    def test_t18_revision_fence_idempotency_and_input_errors_are_distinct(self):
        stale = self._prepare("stale-error", payload={"value": "stale"})
        winner = self._prepare("winner-error", payload={"value": "winner"})
        self.adapter.commit(winner, self.credential)
        with self.assertRaises(RevisionConflict):
            self.adapter.commit(stale, self.credential)
        fenced = self._prepare(
            "fence-error",
            expected_revision=1,
            fence=self.fence,
            payload={"value": "stale fence"},
        )
        self.adapter.advance_fence(_TRACK, self.authority)
        with self.assertRaises(FencingRejected):
            self.adapter.commit(fenced, self.credential)
        with self.assertRaises(IdempotencyConflict):
            self._prepare("winner-error", payload={"value": "different"})
        with self.assertRaises(InvalidProposal):
            self._prepare("bad-revision", expected_revision=True)

    def test_t19_invalid_sizes_are_rejected_before_persistent_operation(self):
        with self.assertRaises(InvalidProposal):
            self._prepare("x" * 257, payload={"value": "small"})
        with self.assertRaises(InvalidProposal):
            self._prepare(
                "int64-overflow",
                expected_revision=(1 << 63),
                payload={"value": "small"},
            )
        with self.assertRaises(InvalidProposal):
            self._prepare("oversized-payload", payload={"value": "x" * (4 * 1024 * 1024 + 1)})
        self.assertIsNone(self.adapter.operation_state(_TRACK, "oversized-payload"))
        self.assertEqual(self.adapter.current_revision(_TRACK), 0)

    def test_t20_old_handle_cannot_abandon_reprepared_operation_after_takeover(self):
        old_handle = self._prepare("abandon-fence-regression", payload={"value": "keep"})
        new_fence = self.adapter.advance_fence(_TRACK, self.authority)
        new_handle = self._prepare(
            "abandon-fence-regression",
            fence=new_fence,
            payload={"value": "keep"},
        )
        with self.assertRaises(FencingRejected):
            self.adapter.abandon(old_handle, self.credential)
        self.assertEqual(
            self.adapter.operation_state(_TRACK, "abandon-fence-regression"),
            OperationState.PREPARED,
        )
        self.assertEqual(self.adapter.commit(new_handle, self.credential).revision, 1)

    def test_t21_delayed_operation_cannot_reorder_after_incompatible_commit(self):
        delayed = self._prepare("delayed", payload={"value": "A"})
        current = self._prepare("current", payload={"value": "B"})
        self.adapter.commit(current, self.credential)
        with self.assertRaises(RevisionConflict):
            self.adapter.commit(delayed, self.credential)
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)
        self.assertEqual(self.adapter.history(_TRACK)[0].payload["value"], "B")

    def test_t22_fence_advance_and_commit_have_one_observable_order(self):
        candidate = self._prepare("fence-commit-race", payload={"value": "race"})
        tasks = [
            (
                _TEST_URI,
                self.database_name,
                _NAMESPACE,
                "commit",
                candidate,
                self._credential_values(self.credential),
                None,
            ),
            (
                _TEST_URI,
                self.database_name,
                _NAMESPACE,
                "advance",
                None,
                None,
                self._authority_values(self.authority),
            ),
        ]
        results = self._run_processes(tasks)
        self.assertEqual(
            sum(item[0] == "OK" and len(item) == 2 for item in results), 1
        )
        commit_results = [item for item in results if item[0] != "OK" or len(item) == 3]
        self.assertEqual(len(commit_results), 1)
        self.assertTrue(
            commit_results[0][0] == "OK"
            or commit_results[0][:2] == ("ERROR", "FencingRejected")
        )
        state = self.database[f"{_NAMESPACE}_tracks"].find_one({"_id": _TRACK})
        self.assertEqual(state["fencing_epoch"], self.fence + 1)
        history = self.database[f"{_NAMESPACE}_history"].find_one(
            {"track_id": _TRACK, "revision": 1}
        )
        if history is None:
            self.assertEqual(self.adapter.current_revision(_TRACK), 0)
        else:
            self.assertLess(history["control_sequence"], state["last_fence_sequence"])
            self.assertEqual(history["fencing_token"], self.fence)

    def test_t23_many_processes_preserve_single_winner_and_dense_history(self):
        writers = [self.credential, self.credential_b]
        for index in range(6):
            writers.append(
                self.adapter.provision_writer_credential(_TRACK, f"writer-{index + 2}")
            )
        tasks = []
        for index, credential in enumerate(writers):
            handle = self._prepare(
                f"stress-{index}",
                writer=credential,
                payload={"winner": index},
            )
            tasks.append(
                (
                    _TEST_URI,
                    self.database_name,
                    _NAMESPACE,
                    "commit",
                    handle,
                    self._credential_values(credential),
                    None,
                )
            )
        results = self._run_processes(tasks)
        self.assertEqual(sum(item[0] == "OK" for item in results), 1)
        self.assertEqual(
            sum(item[:2] == ("ERROR", "RevisionConflict") for item in results), 7
        )
        self.assertEqual([row.revision for row in self.adapter.history(_TRACK)], [1])
        self.assertEqual(self.adapter.current_revision(_TRACK), 1)

    def test_t24_full_suite_can_be_reexecuted_on_fresh_owned_databases(self):
        if os.environ.get("EDITORIAL_REVISION_SUITE_REEXEC_CHILD") == "1":
            self.skipTest("recursive full-suite invocation is suppressed in child run")
        child_environment = {
            "EDITORIAL_REVISION_TEST_URI": _TEST_URI,
            "EDITORIAL_REVISION_SUITE_REEXEC_CHILD": "1",
        }
        python_path = os.environ.get("PYTHONPATH")
        if python_path:
            child_environment["PYTHONPATH"] = python_path
        if os.name == "nt":
            child_environment["SystemRoot"] = os.environ.get("SystemRoot", "")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "integration_tests.test_mongodb_editorial_revision_integration",
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=child_environment,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"clean-namespace suite rerun failed:\n{completed.stdout}\n{completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
