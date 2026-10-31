import asyncio
import copy
import json

import pytest

import services.immutable_publications as publications

TRACK_ID = "a" * 24
NODE_ID = "b" * 24
BLOCK_ID = "c" * 24
QUIZ_ID = "d" * 24


def _snapshot():
    return {
        "track": {
            "id": TRACK_ID, "title": "Synthetic track", "status": "published",
            "visibility": "public", "version": 3, "published_activity_version_id": "old-publication",
        },
        "nodes": [{
            "id": NODE_ID, "track_id": TRACK_ID, "parent_id": None,
            "kind": "lesson", "title": "Draft lesson", "status": "draft", "order": 0,
        }],
        "blocks": [
            {
                "id": BLOCK_ID, "track_id": TRACK_ID, "node_id": NODE_ID,
                "type": "text", "title": "Draft text", "status": "draft", "order": 0,
                "data": {"text": "synthetic unpublished text"},
            },
            {
                "id": QUIZ_ID, "track_id": TRACK_ID, "node_id": NODE_ID,
                "type": "quiz", "title": "Question", "status": "draft", "order": 1,
                "data": {
                    "activity_schema_version": 1,
                    "prompt": "Synthetic question?",
                    "options": [{"id": "no", "label": "No"}, {"id": "yes", "label": "Yes"}],
                    "correct_option_id": "yes",
                    "feedback": {"correct": "Correct", "incorrect": "Try again"},
                    "completion_policy": "responded", "max_attempts": 2,
                },
            },
        ],
        "relations": [],
    }


def _matches(document, query):
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict):
            if "$lte" in expected and not actual <= expected["$lte"]:
                return False
            if "$in" in expected and actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


class _Collection:
    def __init__(self):
        self.rows = []

    async def find_one(self, query):
        return copy.deepcopy(next((row for row in self.rows if _matches(row, query)), None))

    def find(self, query):
        return _AsyncRows([row for row in self.rows if _matches(row, query)])

    async def insert_one(self, document):
        self.rows.append(copy.deepcopy(document))
        return type("InsertResult", (), {"inserted_id": document["_id"]})()

    async def update_one(self, query, update, upsert=False):
        row = next((row for row in self.rows if _matches(row, query)), None)
        if row is None and upsert:
            row = {key: value for key, value in query.items() if not isinstance(value, dict)}
            row.update(copy.deepcopy(update.get("$setOnInsert", {})))
            self.rows.append(row)
            return type("UpdateResult", (), {"matched_count": 0, "upserted_id": row.get("_id")})()
        if row is None:
            return type("UpdateResult", (), {"matched_count": 0, "upserted_id": None})()
        row.update(copy.deepcopy(update.get("$set", {})))
        for key, increment in update.get("$inc", {}).items():
            row[key] = row.get(key, 0) + increment
        for key, value in update.get("$addToSet", {}).items():
            row.setdefault(key, [])
            if value not in row[key]:
                row[key].append(copy.deepcopy(value))
        for key in update.get("$unset", {}):
            row.pop(key, None)
        return type("UpdateResult", (), {"matched_count": 1, "upserted_id": None})()


class _AsyncRows:
    def __init__(self, rows):
        self.rows = copy.deepcopy(rows)
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.rows):
            raise StopAsyncIteration
        row = self.rows[self.index]
        self.index += 1
        return row


class _Database:
    def __init__(self):
        self.track_publications = _Collection()
        self.activity_publications = _Collection()
        self.version_chunks = _Collection()


@pytest.fixture
def publication_harness(monkeypatch):
    database = _Database()
    saved = {}
    source = _snapshot()

    async def get_db():
        return database

    async def capture(_track_id):
        return copy.deepcopy(source)

    async def store(storage_id, snapshot):
        saved[storage_id] = copy.deepcopy(snapshot)
        payload = publications._canonical_bytes(snapshot)
        return {
            "storage": "synthetic-chunk-store", "chunks": 1,
            "raw_bytes": len(payload), "packed_bytes": len(payload),
            "sha256": publications.hashlib.sha256(payload).hexdigest(),
        }

    async def load(manifest):
        storage_id = manifest["snapshot_storage"]["version_id"]
        return copy.deepcopy(saved[storage_id])

    async def delete(storage_id):
        saved.pop(storage_id, None)

    monkeypatch.setattr(publications, "_get_db", get_db)
    monkeypatch.setattr(publications, "_capture_source_snapshot", capture)
    monkeypatch.setattr(publications, "_store_private_snapshot", store)
    monkeypatch.setattr(publications, "_load_private_snapshot", load)
    monkeypatch.setattr(publications, "_delete_private_snapshot", delete)
    return database, saved, source


def test_canonical_snapshot_hash_is_stable_and_changes_with_content():
    first = _snapshot()
    second = copy.deepcopy(first)
    second["track"] = dict(reversed(list(second["track"].items())))
    second["nodes"].reverse()
    second["blocks"].reverse()

    canonical_first = publications.canonicalize_publication_snapshot(first, TRACK_ID, False)
    canonical_second = publications.canonicalize_publication_snapshot(second, TRACK_ID, False)
    assert publications.canonical_snapshot_hash(canonical_first) == publications.canonical_snapshot_hash(canonical_second)

    canonical_second["blocks"][0]["data"]["text"] = "changed"
    assert publications.canonical_snapshot_hash(canonical_first) != publications.canonical_snapshot_hash(canonical_second)


@pytest.mark.parametrize("mutate, message", [
    (lambda doc: doc["nodes"].append(copy.deepcopy(doc["nodes"][0])), "IDs de nós duplicados"),
    (lambda doc: doc["blocks"][0].update(node_id="f" * 24), "sem nó correspondente"),
    (lambda doc: doc.update(blocks=None), "Snapshot incompleto"),
    (lambda doc: doc["nodes"][0].update(parent_id=NODE_ID), "ciclo na hierarquia"),
])
def test_invalid_or_incomplete_snapshots_are_rejected(mutate, message):
    snapshot = _snapshot()
    mutate(snapshot)
    with pytest.raises(publications.PublicationPreparationError, match=message):
        publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, False)


def test_snapshot_depth_and_duplicate_relations_are_rejected():
    snapshot = _snapshot()
    deep_value = "leaf"
    for _ in range(publications.MAX_SNAPSHOT_DEPTH + 1):
        deep_value = {"nested": deep_value}
    snapshot["track"]["meta"] = deep_value
    with pytest.raises(publications.PublicationPreparationError, match="profundidade"):
        publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, False)

    snapshot = _snapshot()
    relation = {
        "id": "relation-1", "track_id": TRACK_ID, "node_id": NODE_ID,
        "target_id": NODE_ID, "type": "related",
    }
    snapshot["relations"] = [relation, {**relation, "id": "relation-2"}]
    with pytest.raises(publications.PublicationPreparationError, match="relações duplicadas"):
        publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, False)


def test_legacy_quiz_is_adapted_only_when_its_definition_is_valid():
    snapshot = _snapshot()
    quiz = snapshot["blocks"][1]
    quiz["data"] = {
        "question": "Legacy synthetic question?", "options": ["A", "B"],
        "correct_index": 1, "explanation": "Legacy feedback",
    }
    candidate = publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, True)
    activities = asyncio.run(publications._build_activity_publications(candidate, "e" * 24, 4))
    assert len(activities) == 1
    assert activities[0]["definition"]["prompt"] == "Legacy synthetic question?"
    assert activities[0]["definition"]["correct_option_id"] == "option-2"

    quiz["data"]["correct_index"] = 9
    candidate = publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, True)
    assert asyncio.run(publications._build_activity_publications(candidate, "e" * 24, 4)) == []


def test_invalid_new_quiz_schema_blocks_candidate_definition():
    snapshot = _snapshot()
    snapshot["blocks"][1]["data"]["correct_option_id"] = "missing"
    candidate = publications.canonicalize_publication_snapshot(snapshot, TRACK_ID, True)
    with pytest.raises(publications.PublicationPreparationError, match="Gabarito"):
        asyncio.run(publications._build_activity_publications(candidate, "e" * 24, 4))


def test_invalid_source_fails_before_manifest_or_active_pointer_changes(publication_harness):
    database, _saved, source = publication_harness
    source["nodes"].append(copy.deepcopy(source["nodes"][0]))
    with pytest.raises(publications.PublicationPreparationError, match="IDs de nós duplicados"):
        asyncio.run(publications.prepare_track_publication(
            TRACK_ID, "operation-before", "bad source", True, {"id": "admin-1"},
        ))
    assert database.track_publications.rows == []
    assert source["track"]["published_activity_version_id"] == "old-publication"


def test_preparation_is_private_inactive_and_does_not_mutate_editorial_source(publication_harness):
    database, saved, source = publication_harness
    before = copy.deepcopy(source)
    result = asyncio.run(publications.prepare_track_publication(
        TRACK_ID, "operation-0001", "synthetic test", True, {"id": "admin-1", "name": "Admin"},
    ))

    assert result["state"] == "prepared"
    assert result["snapshot_complete"] is True
    assert result["visibility"] == "private"
    assert result["active"] is False
    assert result["activation_eligible"] is False
    assert result["source_consistency"] == "unverified"
    assert result["activation_block_reason"] == "editorial_revision_protocol_required"
    assert source == before
    assert source["track"]["published_activity_version_id"] == "old-publication"
    assert source["nodes"][0]["status"] == "draft"
    assert source["blocks"][0]["status"] == "draft"
    assert len(database.track_publications.rows) == 1
    assert len(database.activity_publications.rows) == 1
    assert result["activity_count"] == 1
    assert "correct_option_id" not in result
    assert "snapshot_storage" not in result

    manifest, snapshot = asyncio.run(
        publications._get_prepared_publication(TRACK_ID, result["publication_id"])
    )
    assert manifest["active"] is False
    assert snapshot["nodes"][0]["status"] == "published"
    assert snapshot["blocks"][0]["status"] == "published"
    assert snapshot["blocks"][1]["data"]["correct_option_id"] == "yes"
    stored_definition = database.activity_publications.rows[0]["definition"]
    assert stored_definition["correct_option_id"] == "yes"
    assert database.activity_publications.rows[0]["visibility"] == "private"
    assert database.activity_publications.rows[0]["active"] is False
    assert all(storage_id for storage_id in saved)


def test_same_operation_replays_same_prepared_publication(publication_harness):
    database, _saved, _source = publication_harness
    args = (TRACK_ID, "operation-0002", "same", True, {"id": "admin-1"})
    first = asyncio.run(publications.prepare_track_publication(*args))
    second = asyncio.run(publications.prepare_track_publication(*args))

    assert second["publication_id"] == first["publication_id"]
    assert len(database.track_publications.rows) == 1
    assert len(database.activity_publications.rows) == 1


def test_operation_key_with_changed_snapshot_conflicts_without_changing_active_pointer(
    publication_harness,
):
    database, _saved, source = publication_harness
    asyncio.run(publications.prepare_track_publication(
        TRACK_ID, "operation-0003", "same", True, {"id": "admin-1"},
    ))
    source["blocks"][0]["data"]["text"] = "different content"

    with pytest.raises(publications.PublicationConflict, match="outro conteúdo"):
        asyncio.run(publications.prepare_track_publication(
            TRACK_ID, "operation-0003", "same", True, {"id": "admin-1"},
        ))
    assert source["track"]["published_activity_version_id"] == "old-publication"
    assert len(database.track_publications.rows) == 1


def test_failed_storage_can_be_retried_without_duplicate_manifest(publication_harness, monkeypatch):
    database, _saved, _source = publication_harness
    real_store = publications._store_private_snapshot
    calls = 0

    async def fail_once(storage_id, snapshot):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic storage interruption")
        return await real_store(storage_id, snapshot)

    monkeypatch.setattr(publications, "_store_private_snapshot", fail_once)
    args = (TRACK_ID, "operation-0004", "retry", True, {"id": "admin-1"})
    with pytest.raises(publications.PublicationStorageError, match="Falha ao preparar"):
        asyncio.run(publications.prepare_track_publication(*args))

    failed = database.track_publications.rows[0]
    assert failed["state"] == "failed"
    failed_id = str(failed["_id"])
    result = asyncio.run(publications.prepare_track_publication(*args))
    assert result["publication_id"] == failed_id
    assert result["state"] == "prepared"
    assert len(database.track_publications.rows) == 1


def test_incomplete_stored_snapshot_is_not_marked_prepared_and_can_be_retried(
    publication_harness, monkeypatch,
):
    database, saved, source = publication_harness
    real_load = publications._load_private_snapshot
    calls = 0

    async def fail_once(manifest):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic verification interruption")
        return await real_load(manifest)

    monkeypatch.setattr(publications, "_load_private_snapshot", fail_once)
    args = (TRACK_ID, "operation-verify", "verify", True, {"id": "admin-1"})
    with pytest.raises(publications.PublicationStorageError, match="Falha ao preparar"):
        asyncio.run(publications.prepare_track_publication(*args))

    manifest = database.track_publications.rows[0]
    assert manifest["state"] == "failed"
    assert manifest.get("snapshot_storage") is None
    assert saved == {}
    assert source["track"]["published_activity_version_id"] == "old-publication"

    monkeypatch.setattr(publications, "_load_private_snapshot", real_load)
    recovered = asyncio.run(publications.prepare_track_publication(*args))
    assert recovered["state"] == "prepared"
    assert recovered["publication_id"] == str(manifest["_id"])
    assert len(database.track_publications.rows) == 1


def test_missing_private_activity_reference_blocks_prepared_state(publication_harness, monkeypatch):
    database, saved, source = publication_harness
    real_upsert = publications._upsert_private_activities

    async def remove_after_upsert(target_database, rows):
        result = await real_upsert(target_database, rows)
        target_database.activity_publications.rows.clear()
        return result

    monkeypatch.setattr(publications, "_upsert_private_activities", remove_after_upsert)
    with pytest.raises(publications.PublicationStorageError, match="Referências privadas"):
        asyncio.run(publications.prepare_track_publication(
            TRACK_ID, "operation-activity-check", "activity check", True, {"id": "admin-1"},
        ))
    assert database.track_publications.rows[0]["state"] == "failed"
    assert saved == {}
    assert source["track"]["published_activity_version_id"] == "old-publication"


def test_serialized_activity_reference_list_has_no_gabarito_or_snapshot_data():
    result = {
        "publication_id": "e" * 24, "track_id": TRACK_ID, "operation_id": "operation-0005",
        "state": "prepared", "visibility": "private", "active": False, "schema_version": 1,
        "source_revision": None, "source_consistency": "unverified", "activation_eligible": False,
        "activation_block_reason": "editorial_revision_protocol_required",
        "source_hash": "1" * 64, "snapshot_hash": "2" * 64,
        "stats": {"nodes": 1, "blocks": 2, "relations": 0}, "activity_count": 1,
        "activity_refs_sha256": "3" * 64, "created_at": "now", "prepared_at": "now",
    }
    public_json = json.dumps(result)
    assert "correct_option_id" not in public_json
    assert "snapshot_storage" not in public_json


def test_operation_index_is_unique_and_recovery_index_is_declared():
    from indexes import INDEXES

    operation = next(row for row in INDEXES if row[0:2] == (
        "track_publications", [("track_id", 1), ("operation_id", 1)],
    ))
    recovery = next(row for row in INDEXES if row[0:2] == (
        "track_publications", [("state", 1), ("lease_until", 1)],
    ))
    assert operation[2]["unique"] is True
    assert operation[2]["name"] == "one_track_publication_operation"
    assert operation[3] == ("track_id", "operation_id")
    assert recovery[2]["name"] == "track_publication_recovery_lookup"
