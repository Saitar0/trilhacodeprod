"""Deterministic fake-store tests for the isolated generation protocol PoC.

The fake serializes each single-document update like MongoDB's atomic document
updates. These tests exercise protocol decisions, not MongoDB wire behavior or
the real server's durability settings.
"""

from __future__ import annotations

import asyncio
import copy
import unittest
from datetime import datetime, timedelta, timezone

from services.editorial_generations_poc import (
    EditorialGenerationsPoC,
    GenerationConflict,
    GenerationInvalid,
    GenerationNotFound,
)

_MISSING = object()


def _path(document, path):
    value = document
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return _MISSING
        value = value[key]
    return value


def _set_path(document, path, value):
    target = document
    parts = path.split(".")
    for key in parts[:-1]:
        target = target.setdefault(key, {})
    target[parts[-1]] = copy.deepcopy(value)


def _matches(document, query):
    for key, expected in query.items():
        actual = _path(document, key)
        if isinstance(expected, dict) and any(str(op).startswith("$") for op in expected):
            for op, operand in expected.items():
                if op == "$exists" and ((actual is not _MISSING) != operand):
                    return False
                if op == "$lte" and (actual is _MISSING or not actual <= operand):
                    return False
                if op == "$gt" and (actual is _MISSING or not actual > operand):
                    return False
        elif actual is _MISSING or actual != expected:
            return False
    return True


class DuplicateKey(Exception):
    code = 11000


class UpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class FakeCollection:
    """Small async Mongo-shaped fake with atomic updates and unique IDs."""

    def __init__(self, name):
        self.name = name
        self.rows = {}
        self.lock = asyncio.Lock()
        self.indexes = []

    async def create_index(self, keys, **options):
        self.indexes.append((copy.deepcopy(keys), copy.deepcopy(options)))
        return options.get("name", "_".join(f"{key}_{direction}" for key, direction in keys))

    async def find_one(self, query):
        async with self.lock:
            row = next((row for row in self.rows.values() if _matches(row, query)), None)
            return copy.deepcopy(row) if row else None

    async def insert_one(self, document):
        async with self.lock:
            key = document["_id"]
            if key in self.rows:
                raise DuplicateKey("duplicate key")
            if (self.name == "poc_editorial_generations" and any(
                    row.get("track_id") == document.get("track_id")
                    and row.get("operation_id") == document.get("operation_id")
                    for row in self.rows.values())):
                raise DuplicateKey("duplicate key")
            self.rows[key] = copy.deepcopy(document)
        return type("InsertResult", (), {"inserted_id": key})()

    async def update_one(self, query, update, upsert=False):
        async with self.lock:
            row = next((row for row in self.rows.values() if _matches(row, query)), None)
            if row is None and not upsert:
                return UpdateResult(0)
            if row is None:
                row = {key: value for key, value in query.items()
                       if not key.startswith("$") and not isinstance(value, dict)}
                for key, value in update.get("$setOnInsert", {}).items():
                    _set_path(row, key, value)
                row.setdefault("_id", query.get("_id"))
                self.rows[row["_id"]] = row
                return UpdateResult(1)
            for key, value in update.get("$set", {}).items():
                _set_path(row, key, value)
            for key, value in update.get("$inc", {}).items():
                old = _path(row, key)
                _set_path(row, key, (0 if old is _MISSING else old) + value)
            for key in update.get("$unset", {}):
                target = row
                parts = key.split(".")
                for part in parts[:-1]:
                    target = target.get(part, {})
                if isinstance(target, dict):
                    target.pop(parts[-1], None)
            return UpdateResult(1)


class FakeDatabase:
    def __init__(self):
        self.poc_editorial_generations = FakeCollection("poc_editorial_generations")
        self.poc_editorial_generation_chunks = FakeCollection("poc_editorial_generation_chunks")
        self.poc_editorial_generation_manifests = FakeCollection("poc_editorial_generation_manifests")
        self.poc_editorial_generation_heads = FakeCollection("poc_editorial_generation_heads")

    def __getitem__(self, name):
        return getattr(self, name)


class FakeClock:
    def __init__(self):
        self.value = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def advance(self, duration):
        self.value += duration


TRACK_ID = "synthetic-track"


def snapshot(*, title="Track v1", prompt="Choose safely", import_state=None):
    track = {
        "id": TRACK_ID, "title": title, "status": "published", "visibility": "public",
        "editorial_revision": 1,
    }
    if import_state is not None:
        track["_import_state"] = import_state
    return {
        "track": track,
        "nodes": [{
            "id": "node-1", "track_id": TRACK_ID, "parent_id": None,
            "kind": "lesson", "title": "Unit", "status": "published", "order": 1,
        }],
        "blocks": [{
            "id": "activity-1", "track_id": TRACK_ID, "node_id": "node-1",
            "type": "quiz", "title": "Activity", "status": "published", "order": 1,
            "data": {
                "prompt": prompt,
                "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B", "is_correct": True}],
                "correct_option_id": "b", "feedback": {"correct": "Private feedback"},
                "hidden_tests": ["synthetic-private-test"],
            },
        }],
        "relations": [],
    }


def fail_at(target):
    def failpoint(stage, _context):
        if stage == target:
            raise RuntimeError(f"injected:{target}")
    return failpoint


class EditorialGenerationPoCTests(unittest.TestCase):
    def setUp(self):
        self.database = FakeDatabase()
        self.clock = FakeClock()
        self.store = EditorialGenerationsPoC(self.database, self.clock)
        self.run_async(self.store.ensure_poc_indexes(self.database))

    def run_async(self, awaitable):
        return asyncio.run(awaitable)

    def begin(self, op="operation-0001", writer="writer-1", content=None):
        return self.run_async(self.store.begin(
            track_id=TRACK_ID, operation_id=op, writer_id=writer,
            snapshot=content or snapshot(),
        ))

    def prepare(self, handle, content=None, **kwargs):
        return self.run_async(self.store.prepare(handle, content or snapshot(), **kwargs))

    def select(self, handle, op="select-op-0001", **kwargs):
        return self.run_async(self.store.select_active(
            track_id=TRACK_ID, generation_id=handle.generation_id,
            operation_id=op, **kwargs,
        ))

    def read(self):
        return self.run_async(self.store.read_active_public(TRACK_ID))

    def test_canonicalization_is_stable_and_relevant_content_changes_hash(self):
        first = snapshot()
        reordered = snapshot()
        reordered["nodes"].reverse()
        reordered["blocks"].reverse()
        self.assertEqual(
            self.run_async(self.store.begin(track_id=TRACK_ID, operation_id="canonical-001",
                                             writer_id="writer-1", snapshot=first)).fingerprint,
            self.run_async(self.store.begin(track_id=TRACK_ID, operation_id="canonical-002",
                                             writer_id="writer-1", snapshot=reordered)).fingerprint,
        )
        changed = snapshot(prompt="Changed prompt")
        with self.assertRaises(GenerationConflict):
            self.run_async(self.store.begin(track_id=TRACK_ID, operation_id="canonical-001",
                                             writer_id="writer-1", snapshot=changed))

    def test_duplicate_ids_and_invalid_references_are_rejected(self):
        broken = snapshot()
        broken["nodes"].append(copy.deepcopy(broken["nodes"][0]))
        with self.assertRaises(GenerationInvalid):
            self.begin("duplicate-ids-01", content=broken)
        broken = snapshot()
        broken["blocks"][0]["node_id"] = "missing"
        with self.assertRaises(GenerationInvalid):
            self.begin("bad-reference-01", content=broken)

    def test_import_pending_snapshot_is_rejected_before_generation_creation(self):
        with self.assertRaises(GenerationConflict):
            self.begin("import-pending-01", content=snapshot(import_state={"status": "applying"}))
        self.assertEqual(self.database.poc_editorial_generations.rows, {})

    def test_operation_replay_is_idempotent_and_payload_reuse_conflicts(self):
        first = self.begin("operation-idem-01")
        replay = self.begin("operation-idem-01")
        self.assertEqual(first.generation_id, replay.generation_id)
        with self.assertRaises(GenerationConflict):
            self.begin("operation-idem-01", content=snapshot(prompt="other"))
        self.assertEqual(len(self.database.poc_editorial_generations.rows), 1)

    def test_second_writer_cannot_claim_operation_while_first_lease_is_live(self):
        self.begin("writer-claim-0001", writer="writer-first")
        with self.assertRaises(GenerationConflict):
            self.begin("writer-claim-0001", writer="writer-second")

    def test_failure_before_first_chunk_leaves_private_building_generation(self):
        handle = self.begin("fail-before-001")
        with self.assertRaisesRegex(RuntimeError, "before_first_chunk"):
            self.prepare(handle, failpoint=fail_at("before_first_chunk"))
        manifest = self.database.poc_editorial_generations.rows[handle.generation_id]
        self.assertEqual(manifest["state"], "building")
        with self.assertRaises(GenerationNotFound):
            self.read()
        self.assertEqual(self.prepare(handle)["state"], "sealed")

    def test_failure_after_chunk_write_cannot_be_selected_and_retry_seals_same_generation(self):
        handle = self.begin("fail-after-chunk")
        with self.assertRaisesRegex(RuntimeError, "after_chunk_write"):
            self.prepare(handle, failpoint=fail_at("after_chunk_write"))
        self.assertEqual(self.database.poc_editorial_generations.rows[handle.generation_id]["state"], "building")
        with self.assertRaises(GenerationConflict):
            self.select(handle)
        sealed = self.prepare(handle)
        self.assertEqual(sealed["state"], "sealed")
        self.assertEqual(len(self.database.poc_editorial_generations.rows), 1)

    def test_failed_writer_is_fenced_after_lease_takeover_even_if_late_chunk_arrives(self):
        async def scenario():
            handle = await self.store.begin(track_id=TRACK_ID, operation_id="fence-race-0001",
                                           writer_id="writer-old", snapshot=snapshot())
            checked = asyncio.Event()
            release = asyncio.Event()

            async def pause_after_check(stage, _context):
                if stage == "after_chunk_ownership_check":
                    checked.set()
                    await release.wait()

            old_task = asyncio.create_task(self.store.prepare(handle, snapshot(), failpoint=pause_after_check))
            await checked.wait()
            self.clock.advance(timedelta(minutes=3))
            new_handle = await self.store.begin(track_id=TRACK_ID, operation_id="fence-race-0001",
                                                writer_id="writer-new", snapshot=snapshot())
            self.assertEqual(new_handle.fencing_token, handle.fencing_token + 1)
            release.set()
            with self.assertRaises(GenerationConflict):
                await old_task
            new_manifest = await self.store.prepare(new_handle, snapshot())
            self.assertEqual(new_manifest["state"], "sealed")
            chunks = list(self.database.poc_editorial_generation_chunks.rows.values())
            self.assertTrue(any(row["fencing_token"] == handle.fencing_token for row in chunks))
            self.assertTrue(any(row["fencing_token"] == new_handle.fencing_token for row in chunks))
            return new_handle

        handle = self.run_async(scenario())
        self.select(handle)
        self.assertEqual(self.read()["track"]["id"], TRACK_ID)

    def test_two_concurrent_writers_cannot_select_candidates_based_on_same_stale_head(self):
        async def scenario():
            one = await self.store.begin(track_id=TRACK_ID, operation_id="parallel-op-001",
                                         writer_id="writer-a", snapshot=snapshot(title="A"))
            two = await self.store.begin(track_id=TRACK_ID, operation_id="parallel-op-002",
                                         writer_id="writer-b", snapshot=snapshot(title="B"))
            await asyncio.gather(self.store.prepare(one, snapshot(title="A")),
                                 self.store.prepare(two, snapshot(title="B")))
            results = await asyncio.gather(
                self.store.select_active(track_id=TRACK_ID, generation_id=one.generation_id,
                                         operation_id="select-parallel-a"),
                self.store.select_active(track_id=TRACK_ID, generation_id=two.generation_id,
                                         operation_id="select-parallel-b"),
                return_exceptions=True,
            )
            self.assertEqual(sum(not isinstance(item, Exception) for item in results), 1)
            self.assertEqual(sum(isinstance(item, GenerationConflict) for item in results), 1)
            head = await self.database.poc_editorial_generation_heads.find_one({"_id": TRACK_ID})
            return head

        head = self.run_async(scenario())
        self.assertEqual(head["revision"], 1)
        self.assertIn(head["active_generation_id"], self.database.poc_editorial_generations.rows)

    def test_concurrent_seal_requests_are_idempotent_and_sealed_manifest_is_stable(self):
        async def scenario():
            handle = await self.store.begin(track_id=TRACK_ID, operation_id="seal-race-0001",
                                            writer_id="writer-1", snapshot=snapshot())
            results = await asyncio.gather(self.store.prepare(handle, snapshot()),
                                           self.store.prepare(handle, snapshot()))
            return handle, results

        handle, results = self.run_async(scenario())
        self.assertEqual(results[0], results[1])
        sealed = copy.deepcopy(self.database.poc_editorial_generations.rows[handle.generation_id])
        with self.assertRaises(GenerationConflict):
            self.run_async(self.store.prepare(handle, snapshot(prompt="mutated")))
        self.assertEqual(self.database.poc_editorial_generations.rows[handle.generation_id], sealed)

    def test_retry_after_seal_response_loss_returns_the_same_sealed_generation(self):
        handle = self.begin("seal-response-loss")
        with self.assertRaisesRegex(RuntimeError, "after_seal"):
            self.prepare(handle, failpoint=fail_at("after_seal"))
        replay = self.prepare(handle)
        self.assertEqual(replay["generation_id"], handle.generation_id)
        self.assertEqual(replay["state"], "sealed")

    def test_restart_recovers_seal_intent_and_append_only_manifest(self):
        for stage, expected_manifest_count in (("after_seal_intent", 0), ("after_manifest_insert", 1)):
            with self.subTest(stage=stage):
                database = FakeDatabase()
                clock = FakeClock()
                first_process = EditorialGenerationsPoC(database, clock)
                handle = self.run_async(first_process.begin(
                    track_id=TRACK_ID, operation_id=f"restart-recovery-{stage}",
                    writer_id="writer-before-restart", snapshot=snapshot(),
                ))
                with self.assertRaisesRegex(RuntimeError, stage):
                    self.run_async(first_process.prepare(handle, snapshot(), failpoint=fail_at(stage)))
                self.assertEqual(len(database.poc_editorial_generation_manifests.rows), expected_manifest_count)
                restarted_process = EditorialGenerationsPoC(database, clock)
                recovered_handle = self.run_async(restarted_process.begin(
                    track_id=TRACK_ID, operation_id=f"restart-recovery-{stage}",
                    writer_id="writer-after-restart", snapshot=snapshot(),
                ))
                recovered = self.run_async(restarted_process.prepare(recovered_handle, snapshot()))
                self.assertEqual(recovered["state"], "sealed")
                self.assertEqual(len(database.poc_editorial_generation_manifests.rows), 1)

    def test_independent_store_instances_use_database_cas_not_process_local_locks(self):
        async def scenario():
            writer_a = EditorialGenerationsPoC(self.database, self.clock)
            writer_b = EditorialGenerationsPoC(self.database, self.clock)
            a = await writer_a.begin(track_id=TRACK_ID, operation_id="multi-instance-a",
                                     writer_id="instance-a", snapshot=snapshot(title="A"))
            b = await writer_b.begin(track_id=TRACK_ID, operation_id="multi-instance-b",
                                     writer_id="instance-b", snapshot=snapshot(title="B"))
            await asyncio.gather(writer_a.prepare(a, snapshot(title="A")),
                                 writer_b.prepare(b, snapshot(title="B")))
            results = await asyncio.gather(
                writer_a.select_active(track_id=TRACK_ID, generation_id=a.generation_id,
                                       operation_id="multi-select-a"),
                writer_b.select_active(track_id=TRACK_ID, generation_id=b.generation_id,
                                       operation_id="multi-select-b"),
                return_exceptions=True,
            )
            return results

        outcomes = self.run_async(scenario())
        self.assertEqual(sum(not isinstance(item, Exception) for item in outcomes), 1)
        self.assertEqual(sum(isinstance(item, GenerationConflict) for item in outcomes), 1)

    def test_sealed_manifest_is_never_updated_by_replay(self):
        handle = self.begin("manifest-immutable-01")
        self.prepare(handle)
        before = copy.deepcopy(self.database.poc_editorial_generation_manifests.rows[handle.generation_id])
        replay = self.begin("manifest-immutable-01", writer="restarted-writer")
        self.prepare(replay)
        after = self.database.poc_editorial_generation_manifests.rows[handle.generation_id]
        self.assertEqual(after, before)

    def test_selection_is_cas_idempotent_and_preserves_previous_generation(self):
        first = self.begin("select-generation-1")
        self.prepare(first)
        selected_first = self.select(first, "selection-op-0001")
        original_head = self.database.poc_editorial_generation_heads.rows[TRACK_ID]["active_generation_id"]
        second_snapshot = snapshot(title="Track v2")
        second = self.begin("select-generation-2", content=second_snapshot)
        self.prepare(second, second_snapshot)
        selected_second = self.select(second, "selection-op-0002")
        self.assertEqual(selected_second["revision"], selected_first["revision"] + 1)
        self.assertEqual(self.database.poc_editorial_generation_heads.rows[TRACK_ID]["active_generation_id"],
                         second.generation_id)
        self.assertIn(original_head, self.database.poc_editorial_generations.rows)
        replay = self.select(first, "selection-op-0001")
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["generation_id"], first.generation_id)
        self.assertEqual(self.database.poc_editorial_generation_heads.rows[TRACK_ID]["active_generation_id"],
                         second.generation_id)

    def test_same_selection_key_with_another_generation_conflicts(self):
        one = self.begin("selection-key-gen-1")
        self.prepare(one)
        self.select(one, "selection-same-key")
        two = self.begin("selection-key-gen-2", content=snapshot(title="v2"))
        self.prepare(two, snapshot(title="v2"))
        with self.assertRaises(GenerationConflict):
            self.select(two, "selection-same-key")

    def test_failure_before_pointer_swap_keeps_old_selection_and_retry_after_swap_is_idempotent(self):
        first = self.begin("pointer-fault-gen1")
        self.prepare(first)
        self.select(first, "pointer-select-gen1")
        second_snapshot = snapshot(title="v2")
        second = self.begin("pointer-fault-gen2", content=second_snapshot)
        self.prepare(second, second_snapshot)
        with self.assertRaisesRegex(RuntimeError, "before_pointer_cas"):
            self.select(second, "pointer-select-gen2", failpoint=fail_at("before_pointer_cas"))
        self.assertEqual(self.read()["track"]["title"], "Track v1")
        with self.assertRaisesRegex(RuntimeError, "after_pointer_cas"):
            self.select(second, "pointer-select-gen2", failpoint=fail_at("after_pointer_cas"))
        self.assertEqual(self.read()["track"]["title"], "v2")
        self.assertTrue(self.select(second, "pointer-select-gen2")["replayed"])

    def test_read_pins_one_generation_during_concurrent_pointer_swap(self):
        async def scenario():
            first = await self.store.begin(track_id=TRACK_ID, operation_id="read-pin-gen1",
                                           writer_id="writer-1", snapshot=snapshot())
            await self.store.prepare(first, snapshot())
            await self.store.select_active(track_id=TRACK_ID, generation_id=first.generation_id,
                                           operation_id="read-pin-select1")
            next_snapshot = snapshot(title="new generation")
            second = await self.store.begin(track_id=TRACK_ID, operation_id="read-pin-gen2",
                                            writer_id="writer-2", snapshot=next_snapshot)
            await self.store.prepare(second, next_snapshot)
            at_swap = asyncio.Event()
            release = asyncio.Event()

            async def barrier(stage, _context):
                if stage == "before_pointer_cas":
                    at_swap.set()
                    await release.wait()

            selector = asyncio.create_task(self.store.select_active(
                track_id=TRACK_ID, generation_id=second.generation_id,
                operation_id="read-pin-select2", failpoint=barrier,
            ))
            await at_swap.wait()
            read_before = await self.store.read_active_public(TRACK_ID)
            release.set()
            await selector
            read_after = await self.store.read_active_public(TRACK_ID)
            return read_before, read_after

        before, after = self.run_async(scenario())
        self.assertEqual(before["track"]["title"], "Track v1")
        self.assertEqual(after["track"]["title"], "new generation")
        self.assertNotEqual(before["generation_id"], after["generation_id"])

    def test_public_projection_filters_drafts_and_private_quiz_fields(self):
        handle = self.begin("public-projection-01")
        self.prepare(handle)
        self.select(handle)
        result = self.read()
        rendered = str(result)
        self.assertIn("Choose safely", rendered)
        self.assertNotIn("correct_option_id", rendered)
        self.assertNotIn("is_correct", rendered)
        self.assertNotIn("Private feedback", rendered)
        self.assertNotIn("synthetic-private-test", rendered)
        self.assertNotIn("content_hash", rendered)
        self.assertNotIn("writer_id", rendered)

        draft_snapshot = snapshot(title="draft")
        draft_snapshot["nodes"][0]["status"] = "draft"
        handle2 = self.begin("public-projection-draft", content=draft_snapshot)
        self.prepare(handle2, draft_snapshot)
        # It is a new candidate based on revision 1, so select succeeds but
        # the public read contains no student-visible node or block.
        self.select(handle2, "select-draft-0001")
        draft_read = self.read()
        self.assertEqual(draft_read["nodes"], [])
        self.assertEqual(draft_read["blocks"], [])

    def test_unpublished_or_corrupt_selected_generation_fails_closed(self):
        handle = self.begin("corrupt-read-0001")
        self.prepare(handle)
        self.select(handle)
        generation = self.database.poc_editorial_generation_manifests.rows[handle.generation_id]
        ref = generation["chunk_refs"][0]
        self.database.poc_editorial_generation_chunks.rows[ref["_id"]]["data"] = b"tampered"
        with self.assertRaises(GenerationInvalid):
            self.read()

    def test_missing_chunk_fails_closed_without_falling_back(self):
        handle = self.begin("missing-chunk-001")
        self.prepare(handle)
        self.select(handle)
        manifest = self.database.poc_editorial_generation_manifests.rows[handle.generation_id]
        del self.database.poc_editorial_generation_chunks.rows[manifest["chunk_refs"][0]["_id"]]
        with self.assertRaises(GenerationInvalid):
            self.read()
        del self.database.poc_editorial_generation_manifests.rows[handle.generation_id]
        with self.assertRaises(GenerationInvalid):
            self.read()

    def test_legacy_snapshot_without_editorial_revision_can_be_sealed_but_is_not_live_migrated(self):
        legacy = snapshot()
        legacy["track"].pop("editorial_revision")
        handle = self.begin("legacy-source-001", content=legacy)
        result = self.prepare(handle, legacy)
        self.assertEqual(result["state"], "sealed")
        self.assertNotIn("editorial_revision", self.database.poc_editorial_generations.rows[
            handle.generation_id
        ])

    def test_published_track_flag_is_taken_from_the_captured_generation_only(self):
        private_snapshot = snapshot()
        private_snapshot["track"]["status"] = "draft"
        handle = self.begin("private-track-001", content=private_snapshot)
        self.prepare(handle, private_snapshot)
        self.select(handle)
        with self.assertRaises(GenerationNotFound):
            self.read()

    def test_indexes_are_namespaced_to_poc_collections(self):
        specs = EditorialGenerationsPoC.index_specs()
        self.assertEqual({item[0] for item in specs}, {
            "poc_editorial_generations", "poc_editorial_generation_chunks",
            "poc_editorial_generation_manifests", "poc_editorial_generation_heads",
        })
        self.run_async(EditorialGenerationsPoC.ensure_poc_indexes(self.database))
        self.assertTrue(self.database.poc_editorial_generation_heads.indexes)


if __name__ == "__main__":
    unittest.main()
