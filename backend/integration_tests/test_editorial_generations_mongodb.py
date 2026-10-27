"""Real MongoDB integration tests for the isolated editorial generation PoC.

Run only through ops/editorial-generations/run_homologation.py. The runner
creates a unique database, identity marker, least-privilege users and indexes.
This module intentionally refuses ordinary local MongoDB URIs and never reads
the application's MONGO_URL or MONGO_URL_TEST settings.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from uuid import uuid4

from pymongo import AsyncMongoClient, errors
from pymongo.errors import DuplicateKeyError

from integration_tests.harness_diagnostics import emit_lifecycle, install_signal_diagnostics
from services.editorial_generations_poc import (
    CHUNK_BYTES,
    EditorialGenerationsPoC,
    GenerationConflict,
    GenerationInvalid,
)

_WAIT_DEADLINE_SECONDS = 10
_ASYNC_OPERATION_DEADLINE_SECONDS = 12


async def _wait_event(event: asyncio.Event, label: str) -> None:
    try:
        await asyncio.wait_for(event.wait(), timeout=_WAIT_DEADLINE_SECONDS)
    except TimeoutError as exc:
        raise TimeoutError(f"timeout aguardando evento de sincronização: {label}") from exc


async def _wait_barrier(barrier: asyncio.Barrier, label: str) -> None:
    try:
        await asyncio.wait_for(barrier.wait(), timeout=_WAIT_DEADLINE_SECONDS)
    except TimeoutError as exc:
        raise TimeoutError(f"timeout aguardando barreira de sincronização: {label}") from exc


async def _bounded_gather(*awaitables, label: str, timeout: float = 20):
    try:
        return await asyncio.wait_for(asyncio.gather(*awaitables), timeout=timeout)
    except TimeoutError as exc:
        raise TimeoutError(f"timeout aguardando operações concorrentes: {label}") from exc

_RUN_ID = os.environ.get("EDITORIAL_POC_RUN_ID", "")
_DB_NAME = os.environ.get("EDITORIAL_POC_DB", "")
_HOST = os.environ.get("EDITORIAL_POC_MONGO_HOST", "")
_PORT = os.environ.get("EDITORIAL_POC_MONGO_PORT", "")
_DISPOSABLE = os.environ.get("EDITORIAL_POC_DISPOSABLE", "")
_MARKER_CHECKED = os.environ.get("EDITORIAL_POC_MARKER_VERIFIED", "")


def _require_harness() -> None:
    if _DISPOSABLE != "1" or _MARKER_CHECKED != "1":
        raise RuntimeError("Use somente o runner descartável de homologação MongoDB")
    if not re.fullmatch(r"[a-f0-9]{32}", _RUN_ID):
        raise RuntimeError("Identidade da execução descartável inválida")
    if _DB_NAME != f"editorial_poc_{_RUN_ID}":
        raise RuntimeError("Banco não corresponde à execução descartável")
    if _HOST != "mongo" or _PORT != "27017":
        raise RuntimeError("O harness aceita somente o serviço MongoDB privado 'mongo'")
    if any(os.environ.get(key) for key in ("MONGO_URL", "MONGO_URL_TEST", "DATABASE_URL")):
        raise RuntimeError("Configuração MongoDB da aplicação não é aceita pelo harness")
    if os.environ.get("EDITORIAL_POC_MONGO_URI"):
        raise RuntimeError("URI externa não é aceita pelo harness Compose")


def _uri(username_env: str, password_env: str) -> str:
    username = os.environ[username_env]
    password = os.environ[password_env]
    return (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{_HOST}:{_PORT}/"
        f"{_DB_NAME}?authSource={_DB_NAME}&directConnection=true&retryWrites=false"
        "&serverSelectionTimeoutMS=5000&connectTimeoutMS=5000"
    )


class _RoutedDatabase:
    """Routes the PoC's four collections through separately authorized users."""

    def __init__(self, collections: dict[str, object]):
        self._collections = collections

    def __getitem__(self, name: str):
        return self._collections[name]

    def __getattr__(self, name: str):
        try:
            return self._collections[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class _PauseAfterFind:
    def __init__(self, collection, found: asyncio.Event, release: asyncio.Event):
        self._collection = collection
        self._found = found
        self._release = release

    async def find_one(self, query):
        value = await self._collection.find_one(query)
        self._found.set()
        await _wait_event(self._release, "reader-release")
        return value


class _Clock:
    def __init__(self):
        self.value = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def advance(self, amount: timedelta):
        self.value += amount


def _snapshot(track_id: str, title: str = "Synthetic track v1", prompt: str = "Select one") -> dict:
    return {
        "track": {
            "id": track_id,
            "title": title,
            "status": "published",
            "visibility": "public",
            "editorial_revision": 1,
        },
        "nodes": [
            {
                "id": f"{track_id}-node",
                "track_id": track_id,
                "parent_id": None,
                "kind": "lesson",
                "title": "Synthetic lesson",
                "status": "published",
                "order": 1,
            }
        ],
        "blocks": [
            {
                "id": f"{track_id}-activity",
                "track_id": track_id,
                "node_id": f"{track_id}-node",
                "type": "quiz",
                "title": "Synthetic activity",
                "status": "published",
                "order": 1,
                "data": {
                    "prompt": prompt,
                    "options": [
                        {"id": "option-a", "label": "First"},
                        {"id": "option-b", "label": "Second", "is_correct": True},
                    ],
                    "correct_option_id": "option-b",
                    "feedback": {"correct": "Private answer explanation"},
                    "hidden_tests": ["synthetic-private-test"],
                },
            }
        ],
        "relations": [],
    }


def _fail_at(target: str):
    def failpoint(stage: str, _context: dict):
        if stage == target:
            raise RuntimeError(f"injected:{target}")

    return failpoint


class EditorialGenerationsMongoDBTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        test_id = f"{cls.__module__}.{cls.__qualname__}.setUpClass"
        started = time.monotonic()
        emit_lifecycle("class_setup", "start", test_id)
        try:
            _require_harness()
        except BaseException:
            emit_lifecycle("class_setup", "failed", test_id, duration=time.monotonic() - started)
            raise
        emit_lifecycle("class_setup", "end", test_id, duration=time.monotonic() - started)

    def _callSetUp(self):
        self._harness_test_id = self.id()
        loop = self._asyncioRunner.get_loop()
        install_signal_diagnostics(loop, self._harness_test_id)
        started = time.monotonic()
        emit_lifecycle("setup", "start", self._harness_test_id)
        try:
            super()._callSetUp()
        except BaseException:
            emit_lifecycle("setup", "failed", self._harness_test_id, duration=time.monotonic() - started)
            raise
        emit_lifecycle("setup", "end", self._harness_test_id, duration=time.monotonic() - started)

    def _callTestMethod(self, method):
        started = time.monotonic()
        emit_lifecycle("test_body", "start", self._harness_test_id)
        try:
            super()._callTestMethod(method)
        except BaseException:
            emit_lifecycle("test_body", "failed", self._harness_test_id, duration=time.monotonic() - started)
            raise
        emit_lifecycle("test_body", "end", self._harness_test_id, duration=time.monotonic() - started)

    def _callTearDown(self):
        started = time.monotonic()
        emit_lifecycle("teardown", "start", self._harness_test_id)
        try:
            super()._callTearDown()
        except BaseException:
            emit_lifecycle("teardown", "failed", self._harness_test_id, duration=time.monotonic() - started)
            raise
        emit_lifecycle("teardown", "end", self._harness_test_id, duration=time.monotonic() - started)

    async def asyncSetUp(self):
        self.clients = []
        self.clock = _Clock()
        self.builder_client = await self._client(
            "EDITORIAL_POC_BUILDER_USER", "EDITORIAL_POC_BUILDER_PASSWORD"
        )
        self.builder_client_two = await self._client(
            "EDITORIAL_POC_BUILDER_USER",
            "EDITORIAL_POC_BUILDER_PASSWORD",
        )
        self.append_client = await self._client(
            "EDITORIAL_POC_APPEND_USER", "EDITORIAL_POC_APPEND_PASSWORD"
        )
        self.append_client_two = await self._client(
            "EDITORIAL_POC_APPEND_USER",
            "EDITORIAL_POC_APPEND_PASSWORD",
        )
        self.reader_client = await self._client(
            "EDITORIAL_POC_READER_USER", "EDITORIAL_POC_READER_PASSWORD"
        )
        self.fixture_client = await self._client(
            "EDITORIAL_POC_FIXTURE_USER", "EDITORIAL_POC_FIXTURE_PASSWORD"
        )
        self.builder_db = self.builder_client[_DB_NAME]
        self.builder_db_two = self.builder_client_two[_DB_NAME]
        self.append_db = self.append_client[_DB_NAME]
        self.append_db_two = self.append_client_two[_DB_NAME]
        self.reader_db = self.reader_client[_DB_NAME]
        self.fixture_db = self.fixture_client[_DB_NAME]
        self.store, (self.reader_store, self.fixture_store) = self._store()

    async def asyncTearDown(self):
        for client in self.clients:
            await asyncio.wait_for(client.close(), timeout=5)

    async def _client(self, user_env: str, password_env: str):
        # Match the canonical backend client: BSON dates are UTC-aware on read.
        client = AsyncMongoClient(_uri(user_env, password_env), tz_aware=True, timeoutMS=10_000)
        self.clients.append(client)
        await asyncio.wait_for(
            client.admin.command("ping"), timeout=_ASYNC_OPERATION_DEADLINE_SECONDS
        )
        return client

    def _store(
        self,
        *,
        builder_db=None,
        append_db=None,
        reader_db=None,
        fixture_db=None,
        pause_head: tuple[asyncio.Event, asyncio.Event] | None = None,
    ):
        builder = builder_db if builder_db is not None else self.builder_db
        append = append_db if append_db is not None else self.append_db
        reader = reader_db if reader_db is not None else self.reader_db
        fixture = fixture_db if fixture_db is not None else self.fixture_db
        writer_routes = {
            "poc_editorial_generations": builder["poc_editorial_generations"],
            "poc_editorial_generation_heads": builder["poc_editorial_generation_heads"],
            "poc_editorial_generation_chunks": append["poc_editorial_generation_chunks"],
            "poc_editorial_generation_manifests": append["poc_editorial_generation_manifests"],
        }
        reader_routes = {name: reader[name] for name in writer_routes}
        if pause_head:
            found, release = pause_head
            reader_routes["poc_editorial_generation_heads"] = _PauseAfterFind(
                reader_routes["poc_editorial_generation_heads"],
                found,
                release,
            )
        return EditorialGenerationsPoC(_RoutedDatabase(writer_routes), self.clock), (
            EditorialGenerationsPoC(_RoutedDatabase(reader_routes), self.clock),
            EditorialGenerationsPoC(
                _RoutedDatabase({name: fixture[name] for name in writer_routes}), self.clock
            ),
        )

    def _store_with_paused_reader(
        self,
        found: asyncio.Event,
        release: asyncio.Event,
        *,
        builder_db=None,
        append_db=None,
        reader_db=None,
        fixture_db=None,
    ):
        writer, (paused_reader, fixture) = self._store(
            builder_db=builder_db,
            append_db=append_db,
            reader_db=reader_db,
            fixture_db=fixture_db,
            pause_head=(found, release),
        )
        return writer, paused_reader, fixture

    async def _begin(
        self, store, track_id: str, operation_id: str, writer_id: str = "writer-a", snap=None
    ):
        content = snap or _snapshot(track_id)
        return await store.begin(
            track_id=track_id,
            operation_id=operation_id,
            writer_id=writer_id,
            snapshot=content,
        )

    async def test_mongodb_lease_dates_use_the_backend_utc_aware_codec(self):
        track_id = f"utc-codec-{uuid4().hex}"
        handle = await self._begin(self.store, track_id, f"utc-op-{uuid4().hex}")
        generation = await self.builder_db["poc_editorial_generations"].find_one(
            {"_id": handle.generation_id}
        )
        self.assertIsNotNone(generation)
        self.assertIsNotNone(generation["lease_until"].tzinfo)
        self.assertEqual(generation["lease_until"].utcoffset(), timedelta(0))
        self.assertEqual((await self.store.prepare(handle, _snapshot(track_id)))["state"], "sealed")

    async def _sealed_selected(self, track_id: str, *, title: str = "Synthetic track v1"):
        snap = _snapshot(track_id, title=title)
        handle = await self._begin(self.store, track_id, f"prepare-{uuid4().hex}", snap=snap)
        await self.store.prepare(handle, snap)
        await self.store.select_active(
            track_id=track_id,
            generation_id=handle.generation_id,
            operation_id=f"select-{uuid4().hex}",
        )
        return handle, snap

    async def test_unique_operation_index_enforces_concurrent_acquisition(self):
        track_id = f"race-{uuid4().hex}"
        snapshot = _snapshot(track_id)
        other_store, _ = self._store(
            builder_db=self.builder_db_two,
            append_db=self.append_db_two,
        )
        barrier = asyncio.Barrier(2)

        async def acquire(store, writer_id):
            await _wait_barrier(barrier, "concurrent-acquisition")
            try:
                return await self._begin(
                    store, track_id, "same-operation-0001", writer_id, snapshot
                )
            except GenerationConflict:
                return None

        first, second = await _bounded_gather(
            acquire(self.store, "writer-one"),
            acquire(other_store, "writer-two"),
            label="concurrent-acquisition",
        )
        self.assertEqual(sum(item is not None for item in (first, second)), 1)
        rows = await self.builder_db["poc_editorial_generations"].count_documents(
            {
                "track_id": track_id,
                "operation_id": "same-operation-0001",
            }
        )
        self.assertEqual(rows, 1)

    async def test_append_identity_can_insert_and_find_but_cannot_update_replace_or_delete(self):
        track_id = f"permissions-{uuid4().hex}"
        handle, _ = await self._sealed_selected(track_id)
        chunk = await self.append_db["poc_editorial_generation_chunks"].find_one(
            {"generation_id": handle.generation_id},
        )
        manifest = await self.append_db["poc_editorial_generation_manifests"].find_one(
            {"_id": handle.generation_id},
        )
        self.assertIsNotNone(chunk)
        self.assertIsNotNone(manifest)

        probe = {
            "_id": f"permission-probe:{uuid4().hex}",
            "generation_id": handle.generation_id,
            "fencing_token": handle.fencing_token,
            "seq": 999,
            "sha256": "synthetic",
            "data": b"permission probe",
        }
        await self.append_db["poc_editorial_generation_chunks"].insert_one(probe)
        self.assertEqual(
            await self.append_db["poc_editorial_generation_chunks"].find_one({"_id": probe["_id"]}),
            probe,
        )
        duplicate = dict(chunk)
        duplicate["_id"] = f"duplicate-sequence:{uuid4().hex}"
        with self.assertRaises(DuplicateKeyError):
            await self.append_db["poc_editorial_generation_chunks"].insert_one(duplicate)
        duplicate_manifest = dict(manifest)
        duplicate_manifest["_id"] = f"duplicate-manifest:{uuid4().hex}"
        with self.assertRaises(DuplicateKeyError):
            await self.append_db["poc_editorial_generation_manifests"].insert_one(
                duplicate_manifest
            )
        for collection_name in (
            "poc_editorial_generation_chunks",
            "poc_editorial_generation_manifests",
        ):
            collection = self.append_db[collection_name]
            existing = probe if collection_name.endswith("_chunks") else manifest
            with self.subTest(operation="update", collection=collection_name):
                with self.assertRaises(errors.OperationFailure) as raised:
                    await collection.update_one(
                        {"_id": existing["_id"]}, {"$set": {"tampered": True}}
                    )
                self.assertEqual(raised.exception.code, 13)
            with self.subTest(operation="replace", collection=collection_name):
                with self.assertRaises(errors.OperationFailure) as raised:
                    await collection.replace_one({"_id": existing["_id"]}, existing)
                self.assertEqual(raised.exception.code, 13)
            with self.subTest(operation="delete", collection=collection_name):
                with self.assertRaises(errors.OperationFailure) as raised:
                    await collection.delete_one({"_id": existing["_id"]})
                self.assertEqual(raised.exception.code, 13)
        with self.assertRaises(errors.OperationFailure) as raised:
            await self.builder_db["poc_editorial_generation_chunks"].insert_one(
                {
                    "_id": f"wrong-writer:{uuid4().hex}",
                    "generation_id": handle.generation_id,
                    "fencing_token": handle.fencing_token,
                    "seq": 1000,
                    "data": b"must be rejected",
                }
            )
        self.assertEqual(raised.exception.code, 13)
        with self.assertRaises(errors.OperationFailure) as raised:
            await self.reader_db["poc_editorial_generation_heads"].update_one(
                {"_id": track_id},
                {"$set": {"active_generation_id": "forged"}},
            )
        self.assertEqual(raised.exception.code, 13)

    async def test_parallel_sealing_has_one_manifest_and_is_replay_safe(self):
        track_id = f"seal-{uuid4().hex}"
        snapshot = _snapshot(track_id)
        handle = await self._begin(self.store, track_id, f"seal-op-{uuid4().hex}", snap=snapshot)
        other_store, _ = self._store(
            builder_db=self.builder_db_two,
            append_db=self.append_db_two,
        )
        barrier = asyncio.Barrier(2)

        async def align(stage, _context):
            if stage == "after_chunk_ownership_check":
                await _wait_barrier(barrier, "parallel-seal")

        results = await _bounded_gather(
            self.store.prepare(handle, snapshot, failpoint=align),
            other_store.prepare(handle, snapshot, failpoint=align),
            label="parallel-seal",
        )
        self.assertTrue(all(result["state"] == "sealed" for result in results))
        count = await self.append_db["poc_editorial_generation_manifests"].count_documents(
            {"_id": handle.generation_id},
        )
        self.assertEqual(count, 1)

    async def test_two_candidates_from_same_head_only_one_can_win_cas_and_replay_is_idempotent(
        self,
    ):
        track_id = f"head-race-{uuid4().hex}"
        snap_a = _snapshot(track_id, title="Candidate A")
        snap_b = _snapshot(track_id, title="Candidate B")
        a = await self._begin(self.store, track_id, f"candidate-a-{uuid4().hex}", snap=snap_a)
        second_store, _ = self._store(
            builder_db=self.builder_db_two,
            append_db=self.append_db_two,
        )
        b = await self._begin(
            second_store, track_id, f"candidate-b-{uuid4().hex}", "writer-b", snap_b
        )
        await self.store.prepare(a, snap_a)
        await second_store.prepare(b, snap_b)
        barrier = asyncio.Barrier(2)

        async def select(handle, op):
            await _wait_barrier(barrier, "head-selection-cas")
            try:
                selected_store = (
                    self.store if handle.generation_id == a.generation_id else second_store
                )
                return await selected_store.select_active(
                    track_id=track_id,
                    generation_id=handle.generation_id,
                    operation_id=op,
                )
            except GenerationConflict:
                return None

        one, two = await _bounded_gather(
            select(a, f"select-a-{uuid4().hex}"),
            select(b, f"select-b-{uuid4().hex}"),
            label="head-selection-cas",
        )
        self.assertEqual(sum(item is not None for item in (one, two)), 1)
        winner_handle = a if one else b
        head = await self.builder_db["poc_editorial_generation_heads"].find_one({"_id": track_id})
        operation = next(iter(head["selection_receipts"]))
        replay_store = (
            self.store if winner_handle.generation_id == a.generation_id else second_store
        )
        replay = await replay_store.select_active(
            track_id=track_id,
            generation_id=winner_handle.generation_id,
            operation_id=operation,
        )
        self.assertTrue(replay["replayed"])

    async def test_lost_selection_response_replays_after_pointer_was_committed(self):
        track_id = f"lost-ack-{uuid4().hex}"
        handle, _ = await self._sealed_selected(track_id)
        next_snapshot = _snapshot(track_id, title="Committed before response loss")
        next_handle = await self._begin(
            self.store,
            track_id,
            f"lost-ack-op-{uuid4().hex}",
            "writer-b",
            next_snapshot,
        )
        await self.store.prepare(next_handle, next_snapshot)
        operation = f"select-loss-{uuid4().hex}"
        with self.assertRaisesRegex(RuntimeError, "injected:after_pointer_cas"):
            await self.store.select_active(
                track_id=track_id,
                generation_id=next_handle.generation_id,
                operation_id=operation,
                failpoint=_fail_at("after_pointer_cas"),
            )
        replay = await self.store.select_active(
            track_id=track_id,
            generation_id=next_handle.generation_id,
            operation_id=operation,
        )
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["generation_id"], next_handle.generation_id)
        self.assertNotEqual(handle.generation_id, replay["generation_id"])

    async def test_reusing_operation_identity_with_different_content_conflicts(self):
        track_id = f"fingerprint-{uuid4().hex}"
        operation_id = f"same-op-{uuid4().hex}"
        original = _snapshot(track_id, title="Original")
        await self._begin(self.store, track_id, operation_id, snap=original)
        changed = _snapshot(track_id, title="Changed")
        with self.assertRaises(GenerationConflict):
            await self._begin(self.store, track_id, operation_id, "writer-b", changed)

    async def test_expired_writer_cannot_seal_after_takeover_even_if_late_chunk_is_inserted(self):
        track_id = f"fencing-{uuid4().hex}"
        snapshot = _snapshot(track_id, prompt="x" * (CHUNK_BYTES + 4096))
        old = await self._begin(
            self.store, track_id, f"fence-op-{uuid4().hex}", "old-writer", snapshot
        )
        entered = asyncio.Event()
        release = asyncio.Event()

        async def pause_after_ownership(stage, _context):
            if stage == "after_chunk_ownership_check":
                entered.set()
                await _wait_event(release, "old-writer-release")

        old_task = asyncio.create_task(
            self.store.prepare(old, snapshot, failpoint=pause_after_ownership)
        )
        await _wait_event(entered, "old-writer-entered")
        self.clock.advance(timedelta(minutes=3))
        new_store, _ = self._store(
            builder_db=self.builder_db_two,
            append_db=self.append_db_two,
        )
        new = await self._begin(new_store, track_id, old.operation_id, "new-writer", snapshot)
        self.assertGreater(new.fencing_token, old.fencing_token)
        release.set()
        with self.assertRaises(GenerationConflict):
            await old_task
        sealed = await new_store.prepare(new, snapshot)
        self.assertEqual(sealed["state"], "sealed")
        active_chunks = await self.append_db["poc_editorial_generation_chunks"].count_documents(
            {
                "generation_id": new.generation_id,
                "fencing_token": new.fencing_token,
            }
        )
        self.assertEqual(active_chunks, 2)
        old_orphans = await self.append_db["poc_editorial_generation_chunks"].count_documents(
            {
                "generation_id": new.generation_id,
                "fencing_token": old.fencing_token,
            }
        )
        self.assertEqual(old_orphans, 1)
        manifest = await self.append_db["poc_editorial_generation_manifests"].find_one(
            {"_id": new.generation_id},
        )
        self.assertTrue(
            all(
                ref["_id"].split(":")[1] == str(new.fencing_token) for ref in manifest["chunk_refs"]
            )
        )

    async def test_failure_points_never_replace_active_generation_before_selection(self):
        stages = (
            "before_first_chunk",
            "after_chunk_write",
            "before_seal",
            "after_seal_intent",
            "after_manifest_insert",
            "after_seal",
        )
        for stage in stages:
            with self.subTest(stage=stage):
                track_id = f"failure-{stage}-{uuid4().hex}"
                old, _ = await self._sealed_selected(track_id, title="Previous")
                old_head = await self.builder_db["poc_editorial_generation_heads"].find_one(
                    {"_id": track_id}
                )
                snapshot = _snapshot(track_id, title=f"Candidate {stage}")
                candidate = await self._begin(
                    self.store,
                    track_id,
                    f"failure-op-{uuid4().hex}",
                    "writer-b",
                    snapshot,
                )
                with self.assertRaisesRegex(RuntimeError, f"injected:{stage}"):
                    await self.store.prepare(candidate, snapshot, failpoint=_fail_at(stage))
                self.clock.advance(timedelta(minutes=3))
                recovery_store, _ = self._store(
                    builder_db=self.builder_db_two,
                    append_db=self.append_db_two,
                )
                resumed = await self._begin(
                    recovery_store,
                    track_id,
                    candidate.operation_id,
                    "recovery-writer",
                    snapshot,
                )
                recovered = await recovery_store.prepare(resumed, snapshot)
                self.assertEqual(recovered["state"], "sealed")
                manifest_count = await self.append_db[
                    "poc_editorial_generation_manifests"
                ].count_documents(
                    {"_id": candidate.generation_id},
                )
                self.assertEqual(manifest_count, 1)
                head = await self.builder_db["poc_editorial_generation_heads"].find_one(
                    {"_id": track_id}
                )
                self.assertEqual(head["active_generation_id"], old.generation_id)
                self.assertEqual(head["revision"], old_head["revision"])
                public = await self.reader_store.read_active_public(track_id)
                self.assertEqual(public["track"]["title"], "Previous")

    async def test_partial_multichunk_write_is_unselectable_then_retry_seals_same_generation(self):
        track_id = f"partial-{uuid4().hex}"
        snapshot = _snapshot(track_id, prompt="p" * (CHUNK_BYTES + 2048))
        handle = await self._begin(self.store, track_id, f"partial-op-{uuid4().hex}", snap=snapshot)
        with self.assertRaisesRegex(RuntimeError, "injected:after_chunk_write"):
            await self.store.prepare(handle, snapshot, failpoint=_fail_at("after_chunk_write"))
        chunks_before = await self.append_db["poc_editorial_generation_chunks"].count_documents(
            {"generation_id": handle.generation_id, "fencing_token": handle.fencing_token},
        )
        self.assertEqual(chunks_before, 1)
        with self.assertRaises(GenerationConflict):
            await self.store.select_active(
                track_id=track_id,
                generation_id=handle.generation_id,
                operation_id=f"premature-{uuid4().hex}",
            )
        manifest = await self.store.prepare(handle, snapshot)
        self.assertEqual(manifest["state"], "sealed")
        chunks_after = await self.append_db["poc_editorial_generation_chunks"].count_documents(
            {"generation_id": handle.generation_id, "fencing_token": handle.fencing_token},
        )
        self.assertEqual(chunks_after, 2)

    async def test_public_reader_pins_generation_when_pointer_changes_mid_read(self):
        track_id = f"reader-pin-{uuid4().hex}"
        first, _ = await self._sealed_selected(track_id, title="Generation one")
        second_snapshot = _snapshot(
            track_id, title="Generation two", prompt="Generation two prompt"
        )
        found = asyncio.Event()
        release = asyncio.Event()
        writer, paused_reader, _fixture = self._store_with_paused_reader(found, release)
        read_task = None
        try:
            read_task = asyncio.create_task(paused_reader.read_active_public(track_id))
            await _wait_event(found, "reader-pinned-head")
            self.assertFalse(read_task.done(), "a leitura deve permanecer pausada após fixar A")

            second = await self._begin(
                writer,
                track_id,
                f"reader-pin-op-{uuid4().hex}",
                "writer-b",
                second_snapshot,
            )
            await writer.prepare(second, second_snapshot)
            selected = await writer.select_active(
                track_id=track_id,
                generation_id=second.generation_id,
                operation_id=f"reader-pin-select-{uuid4().hex}",
            )
            self.assertEqual(selected["generation_id"], second.generation_id)

            release.set()
            before_swap = await asyncio.wait_for(read_task, timeout=_ASYNC_OPERATION_DEADLINE_SECONDS)
            after_swap = await asyncio.wait_for(
                paused_reader.read_active_public(track_id),
                timeout=_ASYNC_OPERATION_DEADLINE_SECONDS,
            )
            self.assertEqual(before_swap["generation_id"], first.generation_id)
            self.assertEqual(before_swap["track"]["title"], "Generation one")
            self.assertEqual(before_swap["blocks"][0]["data"]["prompt"], "Select one")
            self.assertEqual(after_swap["generation_id"], second.generation_id)
            self.assertEqual(after_swap["track"]["title"], "Generation two")
            self.assertEqual(after_swap["blocks"][0]["data"]["prompt"], "Generation two prompt")
            public_json = json.dumps([before_swap, after_swap], sort_keys=True)
            for forbidden in ("correct_option_id", "Private answer explanation", "writer_id"):
                self.assertNotIn(forbidden, public_json)
        finally:
            release.set()
            if read_task is not None:
                if not read_task.done():
                    read_task.cancel()
                await asyncio.wait_for(
                    asyncio.gather(read_task, return_exceptions=True),
                    timeout=_ASYNC_OPERATION_DEADLINE_SECONDS,
                )

    async def test_reader_fails_closed_on_missing_or_corrupt_chunk(self):
        for corruption in ("missing", "modified", "manifest"):
            with self.subTest(corruption=corruption):
                track_id = f"corruption-{corruption}-{uuid4().hex}"
                handle, _ = await self._sealed_selected(track_id)
                manifest = await self.append_db["poc_editorial_generation_manifests"].find_one(
                    {"_id": handle.generation_id},
                )
                chunk_id = manifest["chunk_refs"][0]["_id"]
                # Only the fixture identity can simulate out-of-band damage.
                fixture_chunks = self.fixture_db["poc_editorial_generation_chunks"]
                if corruption == "missing":
                    await fixture_chunks.delete_one({"_id": chunk_id})
                elif corruption == "modified":
                    await fixture_chunks.update_one(
                        {"_id": chunk_id},
                        {"$set": {"data": b"corrupt fixture"}},
                    )
                else:
                    await self.fixture_db["poc_editorial_generation_manifests"].update_one(
                        {"_id": handle.generation_id},
                        {"$set": {"content_hash": "0" * 64}},
                    )
                with self.assertRaises(GenerationInvalid):
                    await self.reader_store.read_active_public(track_id)

    async def test_selection_receipt_limit_fails_closed(self):
        track_id = f"receipt-limit-{uuid4().hex}"
        await self._sealed_selected(track_id)
        candidate_snapshot = _snapshot(track_id, title="Receipt-limit candidate")
        handle = await self._begin(
            self.store,
            track_id,
            f"receipt-limit-op-{uuid4().hex}",
            "writer-b",
            candidate_snapshot,
        )
        await self.store.prepare(handle, candidate_snapshot)
        receipts = {f"receipt-{index:03d}": {"generation_id": "synthetic"} for index in range(256)}
        await self.fixture_db["poc_editorial_generation_heads"].update_one(
            {"_id": track_id},
            {"$set": {"selection_receipts": receipts}},
        )
        with self.assertRaisesRegex(GenerationConflict, "Limite de recibos"):
            await self.store.select_active(
                track_id=track_id,
                generation_id=handle.generation_id,
                operation_id=f"extra-selection-{uuid4().hex}",
            )

    async def test_public_dto_redacts_known_answers_and_internal_control_fields(self):
        track_id = f"dto-{uuid4().hex}"
        await self._sealed_selected(track_id)
        reader_store, _ = self._store()
        public = await reader_store.read_active_public(track_id)
        rendered = json.dumps(public, sort_keys=True)
        for forbidden in (
            "correct_option_id",
            "is_correct",
            "Private answer explanation",
            "synthetic-private-test",
            "content_hash",
            "manifest_hash",
            "fencing_token",
            "operation_id",
            "writer_id",
        ):
            self.assertNotIn(forbidden, rendered)
        self.assertIn("Select one", rendered)

    async def test_selection_rejects_stale_candidate_and_preserves_previous_generation(self):
        track_id = f"stale-{uuid4().hex}"
        first_snapshot = _snapshot(track_id, title="First")
        second_snapshot = _snapshot(track_id, title="Second")
        first = await self._begin(
            self.store, track_id, f"stale-a-{uuid4().hex}", snap=first_snapshot
        )
        second = await self._begin(
            self.store, track_id, f"stale-b-{uuid4().hex}", "writer-b", second_snapshot
        )
        await self.store.prepare(first, first_snapshot)
        await self.store.prepare(second, second_snapshot)
        await self.store.select_active(
            track_id=track_id,
            generation_id=first.generation_id,
            operation_id=f"select-first-{uuid4().hex}",
        )
        with self.assertRaises(GenerationConflict):
            await self.store.select_active(
                track_id=track_id,
                generation_id=second.generation_id,
                operation_id=f"select-stale-{uuid4().hex}",
            )
        reader_store, _ = self._store()
        self.assertEqual(
            (await reader_store.read_active_public(track_id))["generation_id"], first.generation_id
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
