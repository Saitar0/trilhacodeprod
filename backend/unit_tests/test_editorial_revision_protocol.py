"""Deterministic unit tests for the isolated revision protocol reference model."""

from __future__ import annotations

import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

from curriculum_contract.editorial_revision_protocol import (
    FenceAuthorityError,
    FencingRejected,
    IdempotencyConflict,
    InMemoryEditorialRevisionProtocol,
    InvalidProposal,
    OperationAborted,
    OperationState,
    ProposalValidationError,
    RevisionConflict,
    WriterAuthorizationError,
    WriterCredential,
)


TRACK = "synthetic-track-a"


class EditorialRevisionProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protocol = InMemoryEditorialRevisionProtocol()
        self.authority = self.protocol.provision_fence_authority(TRACK, "authority-a")
        self.fence = self.protocol.advance_fence(TRACK, self.authority)
        self.credentials = {
            writer: self.protocol.provision_writer_credential(TRACK, writer)
            for writer in ("writer-a", "writer-b")
        }

    def credential(self, writer_id: str = "writer-a") -> WriterCredential:
        if writer_id not in self.credentials:
            self.credentials[writer_id] = self.protocol.provision_writer_credential(
                TRACK, writer_id
            )
        return self.credentials[writer_id]

    def prepare(
        self,
        operation_id: str,
        *,
        writer_id: str = "writer-a",
        expected_revision: int = 0,
        fencing_token: int | None = None,
        payload: dict | None = None,
    ):
        return self.protocol.prepare(
            track_id=TRACK,
            credential=self.credential(writer_id),
            operation_id=operation_id,
            expected_revision=expected_revision,
            fencing_token=self.fence if fencing_token is None else fencing_token,
            payload=payload or {"title": "synthetic"},
        )

    def test_t1_first_valid_change_confirms_server_assigned_revision(self) -> None:
        prepared = self.prepare("first-revision", payload={"title": "A"})
        receipt = self.protocol.commit(prepared, self.credential())

        self.assertEqual(receipt.revision, 1)
        self.assertEqual(receipt.parent_revision, 0)
        self.assertFalse(receipt.replayed)
        self.assertEqual(self.protocol.current_revision(TRACK), 1)
        self.assertEqual(self.protocol.history(TRACK)[0].payload["title"], "A")

    def test_t2_two_writers_on_same_base_have_one_cas_winner(self) -> None:
        prepared = [
            self.prepare("concurrent-a", writer_id="writer-a", payload={"value": "A"}),
            self.prepare("concurrent-b", writer_id="writer-b", payload={"value": "B"}),
        ]
        barrier = threading.Barrier(2)

        def attempt(index: int):
            barrier.wait(timeout=3)
            try:
                return self.protocol.commit(prepared[index], self.credential(
                    "writer-a" if index == 0 else "writer-b"
                ))
            except RevisionConflict as error:
                return error

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, range(2)))

        self.assertEqual(sum(not isinstance(item, RevisionConflict) for item in results), 1)
        self.assertEqual(sum(isinstance(item, RevisionConflict) for item in results), 1)
        self.assertEqual(self.protocol.current_revision(TRACK), 1)
        self.assertEqual([row.revision for row in self.protocol.history(TRACK)], [1])

    def test_t3_stale_revision_is_an_explicit_conflict_and_draft_is_recoverable(self) -> None:
        first = self.prepare("winner", payload={"text": "committed"})
        stale = self.prepare("loser", payload={"text": "keep this draft"})
        self.protocol.commit(first, self.credential())

        with self.assertRaises(RevisionConflict) as caught:
            self.protocol.commit(stale, self.credential())

        self.assertEqual(caught.exception.expected_revision, 0)
        self.assertEqual(caught.exception.actual_revision, 1)
        self.assertEqual(self.protocol.operation_state(TRACK, "loser"), OperationState.CONFLICTED)
        self.assertEqual(
            self.protocol.prepared_payload(TRACK, "loser", self.credential())["text"],
            "keep this draft",
        )
        self.assertEqual(self.protocol.current_revision(TRACK), 1)

    def test_t4_writer_with_old_fence_is_rejected_after_new_epoch_commit(self) -> None:
        old = self.prepare("writer-a-old", payload={"version": "A"})
        new_fence = self.protocol.advance_fence(TRACK, self.authority)
        current = self.prepare(
            "writer-b-new",
            writer_id="writer-b",
            fencing_token=new_fence,
            payload={"version": "B"},
        )
        self.protocol.commit(current, self.credential("writer-b"))

        with self.assertRaises(FencingRejected):
            self.protocol.commit(old, self.credential("writer-a"))
        self.assertEqual(self.protocol.current_revision(TRACK), 1)
        self.assertEqual(self.protocol.history(TRACK)[0].payload["version"], "B")

    def test_t5_old_writer_is_rejected_when_fence_advances_without_content_change(self) -> None:
        old = self.prepare("stale-before-content", payload={"value": "unchanged"})
        self.protocol.advance_fence(TRACK, self.authority)

        with self.assertRaises(FencingRejected):
            self.protocol.commit(old, self.credential())

        self.assertEqual(self.protocol.current_revision(TRACK), 0)
        self.assertEqual(self.protocol.history(TRACK), ())

    def test_t6_exact_repetition_returns_original_receipt_without_new_revision(self) -> None:
        prepared = self.prepare("idempotent-once", payload={"title": "stable"})
        original = self.protocol.commit(prepared, self.credential())
        replay = self.protocol.commit(prepared, self.credential())

        self.assertEqual(replay.revision, original.revision)
        self.assertEqual(replay.fingerprint, original.fingerprint)
        self.assertEqual(replay.payload_sha256, original.payload_sha256)
        self.assertTrue(replay.replayed)
        self.assertEqual(len(self.protocol.history(TRACK)), 1)

    def test_t7_operation_identity_with_different_intent_conflicts(self) -> None:
        original = self.prepare("one-key", payload={"body": "first"})
        with self.assertRaises(IdempotencyConflict):
            self.prepare("one-key", payload={"body": "different"})
        with self.assertRaises(IdempotencyConflict):
            self.prepare("one-key", expected_revision=1, payload={"body": "first"})

        # Concurrent contenders cannot mistake a different payload for a replay.
        barrier = threading.Barrier(2)

        def contender(payload: dict):
            barrier.wait(timeout=3)
            try:
                return self.protocol.prepare(
                    track_id=TRACK,
                    credential=self.credential(),
                    operation_id="concurrent-key-conflict",
                    expected_revision=0,
                    fencing_token=self.fence,
                    payload=payload,
                )
            except IdempotencyConflict as error:
                return error

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(contender, ({"x": 1}, {"x": 2})))
        self.assertEqual(sum(isinstance(item, IdempotencyConflict) for item in results), 1)
        self.assertEqual(sum(not isinstance(item, IdempotencyConflict) for item in results), 1)
        self.assertEqual(self.protocol.operation_state(TRACK, "one-key"), OperationState.PREPARED)
        self.assertEqual(original.expected_revision, 0)

    def test_t8_concurrent_duplicate_commits_make_one_revision_and_replay_receipt(self) -> None:
        prepared = self.prepare("same-operation", payload={"answer": "synthetic"})
        duplicate = self.protocol.prepare(
            track_id=TRACK,
            credential=self.credential(),
            operation_id="same-operation",
            expected_revision=0,
            fencing_token=self.fence,
            payload={"answer": "synthetic"},
        )
        barrier = threading.Barrier(2)

        def attempt(handle):
            barrier.wait(timeout=3)
            return self.protocol.commit(handle, self.credential())

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (prepared, duplicate)))

        self.assertEqual([result.revision for result in results], [1, 1])
        self.assertEqual(sum(result.replayed for result in results), 1)
        self.assertEqual(len(self.protocol.history(TRACK)), 1)

    def test_t9_lost_response_after_commit_recovers_same_result(self) -> None:
        prepared = self.prepare("response-lost", payload={"title": "durable-in-model"})

        def request_that_loses_acknowledgement():
            self.protocol.commit(prepared, self.credential())
            raise TimeoutError("simulated response loss after commit")

        with self.assertRaises(TimeoutError):
            request_that_loses_acknowledgement()
        recovered = self.protocol.commit(prepared, self.credential())

        self.assertEqual(recovered.revision, 1)
        self.assertTrue(recovered.replayed)
        self.assertEqual(len(self.protocol.history(TRACK)), 1)

    def test_t10_failure_before_confirmation_creates_no_revision(self) -> None:
        prepared = self.prepare("not-confirmed", payload={"title": "staged only"})

        self.assertEqual(self.protocol.current_revision(TRACK), 0)
        self.assertEqual(self.protocol.history(TRACK), ())
        self.assertEqual(
            self.protocol.operation_state(TRACK, "not-confirmed"), OperationState.PREPARED
        )
        self.assertEqual(
            self.protocol.prepared_payload(TRACK, "not-confirmed", self.credential())["title"],
            "staged only",
        )
        self.assertEqual(prepared.expected_revision, 0)

    def test_t11_abandoned_preparation_never_becomes_confirmed(self) -> None:
        prepared = self.prepare("abandoned", payload={"title": "abandoned"})

        self.assertTrue(self.protocol.abandon(prepared, self.credential()))
        self.assertFalse(self.protocol.abandon(prepared, self.credential()))
        with self.assertRaises(OperationAborted):
            self.protocol.commit(prepared, self.credential())
        self.assertEqual(self.protocol.current_revision(TRACK), 0)
        self.assertEqual(self.protocol.history(TRACK), ())

    def test_t12_operation_ids_and_revisions_are_isolated_between_tracks(self) -> None:
        other_track = "synthetic-track-b"
        other_writer = self.protocol.provision_writer_credential(other_track, "writer-a")
        other_authority = self.protocol.provision_fence_authority(other_track, "authority-a")
        other_fence = self.protocol.advance_fence(other_track, other_authority)
        first = self.prepare("same-id", payload={"track": "A"})
        second = self.protocol.prepare(
            track_id=other_track,
            credential=other_writer,
            operation_id="same-id",
            expected_revision=0,
            fencing_token=other_fence,
            payload={"track": "B"},
        )

        first_result = self.protocol.commit(first, self.credential())
        second_result = self.protocol.commit(second, other_writer)

        self.assertEqual(first_result.revision, second_result.revision)
        self.assertEqual(self.protocol.current_revision(TRACK), 1)
        self.assertEqual(self.protocol.current_revision(other_track), 1)
        self.assertEqual(self.protocol.history(TRACK)[0].payload["track"], "A")
        self.assertEqual(self.protocol.history(other_track)[0].payload["track"], "B")
        with self.assertRaises(WriterAuthorizationError):
            self.protocol.commit(second, self.credential())

    def test_t13_confirmed_history_is_monotonic_and_immutable(self) -> None:
        for expected in range(12):
            prepared = self.prepare(
                f"sequential-{expected}",
                expected_revision=expected,
                payload={"sequence": expected + 1},
            )
            self.protocol.commit(prepared, self.credential())

        history = self.protocol.history(TRACK)
        self.assertEqual([item.revision for item in history], list(range(1, 13)))
        self.assertEqual([item.parent_revision for item in history], list(range(0, 12)))
        self.assertEqual(self.protocol.current_revision(TRACK), 12)
        with self.assertRaises((TypeError, FrozenInstanceError)):
            history[0].payload["sequence"] = 999

    def test_t14_revoked_or_forged_writer_credentials_cannot_confirm(self) -> None:
        prepared = self.prepare("revoked-writer", payload={"title": "must not commit"})
        self.protocol.revoke_writer_credential(TRACK, "writer-a")

        with self.assertRaises(WriterAuthorizationError):
            self.protocol.commit(prepared, self.credential())

        replacement = self.protocol.provision_writer_credential(TRACK, "writer-a")
        forged = WriterCredential(TRACK, "writer-a", "not-the-provisioned-secret")
        with self.assertRaises(WriterAuthorizationError):
            self.protocol.commit(prepared, forged)
        self.assertNotIn("not-the-provisioned-secret", repr(replacement))
        self.assertEqual(self.protocol.current_revision(TRACK), 0)

    def test_t15_many_concurrent_writers_preserve_one_winner_per_revision(self) -> None:
        writers = [f"writer-{index}" for index in range(6)]
        for writer in writers:
            self.credential(writer)

        rounds = 8
        for expected in range(rounds):
            handles = [
                self.prepare(
                    f"stress-{expected}-{index}",
                    writer_id=writer,
                    expected_revision=expected,
                    payload={"revision-content": [expected + 1, index]},
                )
                for index, writer in enumerate(writers)
            ]
            barrier = threading.Barrier(len(handles))

            def attempt(index: int):
                barrier.wait(timeout=5)
                try:
                    return self.protocol.commit(handles[index], self.credential(writers[index]))
                except RevisionConflict as error:
                    return error

            with ThreadPoolExecutor(max_workers=len(handles)) as pool:
                outcomes = list(pool.map(attempt, range(len(handles))))
            winners = [item for item in outcomes if not isinstance(item, RevisionConflict)]
            losers = [item for item in outcomes if isinstance(item, RevisionConflict)]
            self.assertEqual(len(winners), 1)
            self.assertEqual(len(losers), len(handles) - 1)
            replay = self.protocol.commit(handles[outcomes.index(winners[0])], self.credential(
                writers[outcomes.index(winners[0])]
            ))
            self.assertEqual(replay.revision, expected + 1)
            self.assertTrue(replay.replayed)

        self.assertEqual(self.protocol.current_revision(TRACK), rounds)
        self.assertEqual(
            [record.revision for record in self.protocol.history(TRACK)],
            list(range(1, rounds + 1)),
        )

    def test_stale_handle_cannot_abandon_reprepared_operation_after_fence_takeover(self) -> None:
        old_handle = self.prepare("abandon-fence-race", payload={"value": "keep"})
        new_fence = self.protocol.advance_fence(TRACK, self.authority)
        current_handle = self.prepare(
            "abandon-fence-race",
            fencing_token=new_fence,
            payload={"value": "keep"},
        )

        with self.assertRaises(FencingRejected):
            self.protocol.abandon(old_handle, self.credential())

        self.assertEqual(
            self.protocol.operation_state(TRACK, "abandon-fence-race"),
            OperationState.PREPARED,
        )
        receipt = self.protocol.commit(current_handle, self.credential())
        self.assertEqual(receipt.revision, 1)

    def test_inconsistent_proposal_is_rejected_before_operation_or_revision_creation(self) -> None:
        protocol = InMemoryEditorialRevisionProtocol(
            proposal_validator=lambda proposal: proposal.get("coherent") is True
        )
        authority = protocol.provision_fence_authority(TRACK, "authority")
        fence = protocol.advance_fence(TRACK, authority)
        credential = protocol.provision_writer_credential(TRACK, "writer")

        with self.assertRaises(ProposalValidationError):
            protocol.prepare(
                track_id=TRACK,
                credential=credential,
                operation_id="inconsistent",
                expected_revision=0,
                fencing_token=fence,
                payload={"coherent": False},
            )

        self.assertIsNone(protocol.operation_state(TRACK, "inconsistent"))
        self.assertEqual(protocol.current_revision(TRACK), 0)
        self.assertEqual(protocol.history(TRACK), ())

    def test_invalid_revision_and_untrusted_fence_authority_are_rejected(self) -> None:
        with self.assertRaises(FenceAuthorityError):
            self.protocol.advance_fence(TRACK, self.credential())  # type: ignore[arg-type]
        with self.assertRaises(InvalidProposal):
            self.prepare("bool-is-not-revision", expected_revision=True)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
