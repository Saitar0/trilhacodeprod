import asyncio
import uuid
from types import SimpleNamespace

from bson import ObjectId

from database import db
from indexes import INDEXES, _keys_match, preflight_indexes
from services.progress import visit_node
from services.taxonomy import create_block_type, create_tag, create_taxonomy


def test_preflight_compound_and_text_index_key_matching():
    assert len(INDEXES) == 24
    assert _keys_match(
        {"key": {"user_id": 1, "at": -1}},
        (("user_id", 1), ("at", -1)),
    )
    assert not _keys_match(
        {"key": {"at": -1, "user_id": 1}},
        (("user_id", 1), ("at", -1)),
    )

    expected_text_keys = (("title", "text"), ("summary", "text"))
    mongo_text_index = {
        "key": {"_fts": "text", "_ftsx": 1},
        "weights": {"title": 1, "summary": 1},
    }
    assert _keys_match(mongo_text_index, expected_text_keys)
    assert not _keys_match(
        {**mongo_text_index, "weights": {"title": 1}},
        expected_text_keys,
    )


def test_concurrent_user_registration_is_private_and_creates_one_account(async_client, event_loop):
    email = f"race_{uuid.uuid4().hex}@example.com"
    payload = {"name": "Race User", "email": email, "password": "Test@12345678"}

    async def register_twice():
        return await asyncio.gather(
            async_client.post("/api/auth/register", json=payload),
            async_client.post("/api/auth/register", json=payload),
        )

    responses = event_loop.run_until_complete(register_twice())
    assert sorted(response.status_code for response in responses) == [202, 202]
    assert responses[0].json() == responses[1].json()
    assert event_loop.run_until_complete(db.users.count_documents({"email": email})) == 1


def test_concurrent_tag_creation_returns_one_conflict(event_loop):
    name = f"race-{uuid.uuid4().hex}"

    async def create_twice():
        async def create():
            try:
                await create_tag(name, None)
                return 200
            except Exception as exc:
                return getattr(exc, "status_code", 500)

        return await asyncio.gather(create(), create())

    responses = event_loop.run_until_complete(create_twice())
    assert sorted(responses) == [200, 400]
    slug = name.lower().replace(" ", "-")
    assert event_loop.run_until_complete(db.tags.count_documents({"slug": slug})) == 1


def test_concurrent_taxonomy_and_block_type_creation_returns_conflicts(event_loop):
    suffix = uuid.uuid4().hex

    async def create_once(service, *args):
        try:
            await service(*args)
            return 200
        except Exception as exc:
            return getattr(exc, "status_code", 500)

    async def run_pair(service, *args):
        return await asyncio.gather(create_once(service, *args), create_once(service, *args))

    taxonomy_data = {"group": "relation_type", "key": f"race-{suffix}", "label": "Race"}
    block_type_data = {
        "key": f"race_{suffix}", "label": "Race", "category": "test", "icon": "test",
        "fields": [], "description": "", "enabled": True, "capabilities": [],
    }
    assert sorted(event_loop.run_until_complete(run_pair(create_taxonomy, taxonomy_data))) == [200, 400]
    assert sorted(event_loop.run_until_complete(run_pair(create_block_type, block_type_data))) == [200, 400]


def test_concurrent_visits_keep_one_node_progress_record(event_loop, seeded_track, fresh_student):
    node = fresh_student.get(f"/api/tracks/{seeded_track['id']}/tree").json()["nodes"][0]
    user = fresh_student.get("/api/auth/me").json()

    async def visit_twice():
        await asyncio.gather(visit_node(node["id"], user), visit_node(node["id"], user))

    event_loop.run_until_complete(visit_twice())
    key = {"user_id": user["id"], "node_id": node["id"], "block_id": None}
    assert event_loop.run_until_complete(db.progress.count_documents(key)) == 1


def test_lifespan_checks_migrations_before_yield_and_closes_client(monkeypatch, event_loop):
    import server

    sequence = []

    async def check_version():
        sequence.append("check")
        return True

    monkeypatch.setattr(server, "check_schema_version", check_version)
    async def close():
        sequence.append("close")

    monkeypatch.setattr(server, "client", SimpleNamespace(close=close))

    async def run_lifespan():
        async with server.lifespan(server.app):
            sequence.append("started")

    event_loop.run_until_complete(run_lifespan())
    assert sequence == ["check", "started", "close"]


def test_delete_tag_failure_can_be_retried(monkeypatch, event_loop):
    import services.taxonomy as taxonomy

    state = {"tag_exists": True, "node_has_tag": True, "track_has_tag": True}
    calls = {"tracks": 0}

    class Tags:
        async def delete_one(self, _query):
            state["tag_exists"] = False

    class Nodes:
        async def update_many(self, _query, _update):
            state["node_has_tag"] = False

    class Tracks:
        async def update_many(self, _query, _update):
            calls["tracks"] += 1
            if calls["tracks"] == 1:
                raise RuntimeError("simulated intermediate database failure")
            state["track_has_tag"] = False

    monkeypatch.setattr(taxonomy, "db", SimpleNamespace(tags=Tags(), nodes=Nodes(), tracks=Tracks()))
    tag_id = str(ObjectId())

    async def run():
        try:
            await taxonomy.delete_tag(tag_id)
        except RuntimeError:
            pass
        assert state == {"tag_exists": True, "node_has_tag": False, "track_has_tag": True}
        await taxonomy.delete_tag(tag_id)

    event_loop.run_until_complete(run())
    assert state == {"tag_exists": False, "node_has_tag": False, "track_has_tag": False}


def test_unique_index_preflight_reports_duplicates_and_respects_partial_indexes(monkeypatch, event_loop):
    class AggregationCursor:
        def __init__(self, rows):
            self.rows = rows

        async def to_list(self, length):
            assert length == 20
            return self.rows

    class IndexCursor:
        async def to_list(self, length):
            assert length == 1000
            return []

    class Collection:
        def __init__(self, name):
            self.name = name
            self.pipelines = []

        async def list_indexes(self):
            return IndexCursor()

        async def aggregate(self, pipeline):
            self.pipelines.append(pipeline)
            rows = ([{"_id": {"slug": "same"}, "count": 2, "sample_id": "id-1"}]
                    if self.name == "tags" else [])
            return AggregationCursor(rows)

    class Database:
        def __init__(self):
            self.collections = {}

        async def list_collection_names(self):
            return list({collection for collection, _, _, fields in INDEXES if fields})

        def __getitem__(self, name):
            return self.collections.setdefault(name, Collection(name))

    fake_db = Database()
    monkeypatch.setattr("indexes.db", fake_db)

    findings = event_loop.run_until_complete(preflight_indexes())
    assert any(finding.startswith("DUPLICATAS tags.one_tag_slug:") for finding in findings)
    assert "id-1" in next(finding for finding in findings if finding.startswith("DUPLICATAS tags."))

    unique_indexes = [(collection, fields, options.get("partialFilterExpression"))
                      for collection, _, options, fields in INDEXES if fields]
    observed = []
    for collection, fields, partial_filter in unique_indexes:
        pipeline = fake_db.collections[collection].pipelines.pop(0)
        expected_group = {field: {"$ifNull": [f"${field}", None]} for field in fields}
        expected = ([{"$match": partial_filter}] if partial_filter else []) + [
            {"$group": {"_id": expected_group, "count": {"$sum": 1},
                         "sample_id": {"$first": "$_id"}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$limit": 20},
        ]
        assert pipeline == expected
        observed.append((collection, partial_filter))

    assert len(unique_indexes) == sum(len(collection.pipelines) for collection in fake_db.collections.values()) + len(observed)
    assert ("reviews", {"status": "pending"}) in observed
    assert ("restore_jobs", {"status": "running"}) in observed

    import manage

    closed = []

    async def report_findings():
        return findings

    async def close_client():
        closed.append(True)

    monkeypatch.setattr(manage, "preflight_indexes", report_findings)
    monkeypatch.setattr(manage, "client", SimpleNamespace(close=close_client))
    try:
        event_loop.run_until_complete(manage.run("preflight-indexes"))
    except RuntimeError as exc:
        assert "Preflight encontrou conflitos ou duplicatas" in str(exc)
    else:
        raise AssertionError("duplicate findings must fail the public preflight command")
    assert closed == [True]

