import asyncio
from types import SimpleNamespace

import migrations
from integrity import validate_snapshot
from services import versions


def _snapshot():
    return {"track": {"id": "track-1"}, "nodes": [], "blocks": [], "relations": []}


def test_snapshot_validation_accepts_complete_empty_snapshot():
    validate_snapshot(_snapshot(), {"nodes": 0, "blocks": 0, "relations": 0})


def test_snapshot_validation_rejects_missing_collection():
    snapshot = _snapshot()
    del snapshot["blocks"]

    try:
        validate_snapshot(snapshot)
    except ValueError as exc:
        assert "blocks" in str(exc)
    else:
        raise AssertionError("incomplete snapshot was accepted")


def test_snapshot_validation_rejects_count_mismatch():
    try:
        validate_snapshot(_snapshot(), {"nodes": 1, "blocks": 0, "relations": 0})
    except ValueError as exc:
        assert "nodes" in str(exc)
    else:
        raise AssertionError("snapshot with mismatched counts was accepted")


def test_snapshot_validation_rejects_cross_track_documents():
    snapshot = _snapshot()
    snapshot["nodes"].append({"id": "node-2", "track_id": "another-track", "parent_id": None})
    try:
        validate_snapshot(snapshot, expected_track_id="track-1")
    except ValueError as exc:
        assert "outra trilha" in str(exc)
    else:
        raise AssertionError("snapshot containing a different track was accepted")


class _Cursor:
    def __init__(self, rows):
        self.rows = rows

    async def to_list(self, _length):
        return self.rows


class _Migrations:
    def __init__(self, rows):
        self.rows = rows

    def find(self, _query):
        return _Cursor(self.rows)


def test_migration_ledger_accepts_only_a_contiguous_known_prefix(monkeypatch):
    collection = _Migrations([
        {"key": migrations.MIGRATIONS[1], "version": 2},
        {"key": migrations.MIGRATIONS[0], "version": 1},
        {"key": "block_types_submission_v1"},
    ])
    monkeypatch.setattr(migrations, "db", SimpleNamespace(migrations=collection))
    assert asyncio.run(migrations._migration_ledger()) == [
        {"key": migrations.MIGRATIONS[0], "version": 1},
        {"key": migrations.MIGRATIONS[1], "version": 2},
    ]

    collection.rows = [{"key": migrations.MIGRATIONS[1], "version": 2}]
    assert asyncio.run(migrations._migration_ledger()) is None

    collection.rows = [{"key": "unknown_legacy_marker"}]
    assert asyncio.run(migrations._migration_ledger()) is None


class _AsyncCursor:
    def __init__(self, values):
        self._values = iter(values)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._values)
        except StopIteration:
            raise StopAsyncIteration


class _SnapshotCollection:
    def __init__(self, values):
        self.values = values

    async def count_documents(self, _query):
        return len(self.values)

    def find(self, _query):
        return _AsyncCursor(self.values)


def test_snapshot_capture_reads_past_the_old_limits(monkeypatch):
    counts = {"nodes": 10001, "blocks": 50001, "relations": 10001}
    values = {
        name: _SnapshotCollection([
            {"_id": f"{name}-{index}", "track_id": "track-1"} for index in range(count)
        ])
        for name, count in counts.items()
    }

    async def get_track(_collection, _track_id):
        return {"_id": "track-1", "title": "Test"}

    monkeypatch.setattr(versions, "db", SimpleNamespace(
        nodes=values["nodes"], content_blocks=values["blocks"], relations=values["relations"],
    ))
    monkeypatch.setattr(versions, "get_document", get_track)
    snapshot = asyncio.run(versions.snapshot_track("track-1"))
    assert {key: len(snapshot[key]) for key in counts} == counts
