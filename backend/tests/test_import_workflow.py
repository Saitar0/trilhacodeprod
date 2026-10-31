import asyncio
import uuid
from datetime import timedelta

import pytest
from bson import ObjectId
from httpx import ASGITransport, AsyncClient

from core_utils import now
from database import db
from server import app

API = "/api"


async def _import_state():
    names = ("tracks", "nodes", "content_blocks", "relations", "tags", "track_versions",
             "version_chunks", "edit_history", "import_jobs", "import_locks")
    return {name: [document async for document in db[name].find({}).sort("_id", 1)] for name in names}


async def _post_app(session, path, payload):
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
        cookies=session.cookies,
    ) as client:
        return await client.post(path, json=payload)


def _payload(slug):
    return {
        "track": {"slug": slug, "title": "QA Import Persistence"},
        "nodes": [{"ref": "phase-1", "kind": "phase", "title": "Phase 1", "children": [{
            "ref": "topic-1", "kind": "topic", "title": "Topic 1",
            "blocks": [{"ref": "intro", "type": "theory_text", "data": {"body": "synthetic QA body"}}],
        }]}],
    }


def test_import_dry_run_persistence_and_reimport_are_idempotent(admin_session, event_loop):
    slug = f"qa-import-{uuid.uuid4().hex[:12]}"
    payload = _payload(slug)
    track_id = None
    try:
        before = event_loop.run_until_complete(_import_state())
        preview = admin_session.post(f"{API}/import/track?dry_run=true", json=payload)
        assert preview.status_code == 200, preview.text
        assert preview.json()["ok"] is True
        assert preview.json()["dry_run"] is True
        assert preview.json()["summary"]["nodes_create"] == 2
        assert event_loop.run_until_complete(_import_state()) == before, "dry-run must not persist import state"

        imported = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
        assert imported.status_code == 200, imported.text
        assert imported.json()["dry_run"] is False
        assert imported.json()["summary"]["nodes_create"] == 2
        track_id = imported.json()["track"]["id"]

        repeated = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
        assert repeated.status_code == 200, repeated.text
        assert repeated.json()["idempotent_replay"] is True
        tree = admin_session.get(f"/api/tracks/{track_id}/tree")
        assert tree.status_code == 200, tree.text
        assert len(tree.json()["nodes"]) == 2
        assert sum(tree.json()["block_counts"].values()) == 1
        assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 2
        assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 1
        assert event_loop.run_until_complete(
            db.import_jobs.count_documents({"track_id": track_id, "status": "completed"})
        ) == 1
    finally:
        if track_id:
            admin_session.delete(f"/api/tracks/{track_id}")


@pytest.mark.parametrize("failure_phase", ["nodes", "relations", "snapshot", "finalizing"])
def test_interrupted_published_import_is_hidden_and_same_payload_recovers(
    admin_session, student_session, event_loop, monkeypatch,
    failure_phase,
):
    import services.imports as imports

    slug = f"qa-recovery-{uuid.uuid4().hex[:12]}"
    payload = _payload(slug)
    first = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
    assert first.status_code == 200, first.text
    track_id = first.json()["track"]["id"]
    phase_node = event_loop.run_until_complete(db.nodes.find_one({"track_id": track_id, "meta.import_ref": "phase-1"}))
    pending_node_id = ObjectId()
    event_loop.run_until_complete(db.nodes.insert_one({
        "_id": pending_node_id, "track_id": track_id, "parent_id": str(phase_node["_id"]),
        "meta": {"import_ref": "synthetic-prerequisite"}, "kind": "topic", "title": "Prerequisite",
        "status": "published", "order": 1,
    }))
    event_loop.run_until_complete(db.relations.insert_one({
        "track_id": track_id, "node_id": str(phase_node["_id"]), "target_id": str(pending_node_id),
        "type": "prerequisite", "enforced": True,
    }))
    event_loop.run_until_complete(db.tracks.update_one(
        {"_id": ObjectId(track_id)}, {"$set": {"settings.enforce_prerequisites": True}},
    ))
    old_nodes = event_loop.run_until_complete(db.nodes.find({"track_id": track_id}).to_list(10))
    stable_node_ids = {node["meta"]["import_ref"]: str(node["_id"]) for node in old_nodes}
    old_block = event_loop.run_until_complete(db.content_blocks.find_one({"track_id": track_id}))
    student = student_session.get("/api/auth/me").json()
    topic_id = stable_node_ids["topic-1"]
    event_loop.run_until_complete(db.progress.insert_one({
        "user_id": student["id"], "track_id": track_id, "node_id": topic_id,
        "block_id": None, "status": "completed", "revision": 1,
    }))
    event_loop.run_until_complete(db.notes.insert_one({
        "user_id": student["id"], "track_id": track_id, "node_id": topic_id,
        "block_id": str(old_block["_id"]), "body": "synthetic student note", "version": 1,
        "deleted": False,
    }))
    event_loop.run_until_complete(db.learning_events.insert_one({
        "user_id": student["id"], "track_id": track_id, "node_id": topic_id,
        "block_id": None, "type": "complete", "data": {}, "at": now(),
    }))
    submission_id = ObjectId()
    event_loop.run_until_complete(db.submissions.insert_one({
        "_id": submission_id, "user_id": student["id"], "track_id": track_id,
        "node_id": topic_id, "node_title": "Topic 1", "block_id": str(old_block["_id"]),
        "block_type": old_block["type"], "block_title": "Intro", "attempt": 1,
        "status": "submitted", "answer": {"text": "synthetic answer"},
    }))
    published = admin_session.post(f"/api/tracks/{track_id}/publish", json={})
    assert published.status_code == 200, published.text
    previous_version = published.json()["version"]
    visible_progress = student_session.get(f"/api/progress/tracks/{track_id}")
    assert visible_progress.status_code == 200, visible_progress.text
    assert str(phase_node["_id"]) in visible_progress.json()["locks"]

    changed_payload = _payload(slug)
    changed_payload["nodes"][0]["children"][0]["title"] = "Topic revised"
    changed_payload["nodes"][0]["children"][0]["blocks"][0]["data"]["body"] = "synthetic revised"
    original = imports._set_import_phase
    failed_once = False

    async def inject_failure(slug_arg, job_id, owner, phase):
        nonlocal failed_once
        if phase == failure_phase and not failed_once:
            failed_once = True
            raise RuntimeError("synthetic failure after node and block writes")
        await original(slug_arg, job_id, owner, phase)

    monkeypatch.setattr(imports, "_set_import_phase", inject_failure)
    failed = event_loop.run_until_complete(
        _post_app(admin_session, f"{API}/import/track?dry_run=false", changed_payload)
    )
    assert failed.status_code == 500
    track = event_loop.run_until_complete(db.tracks.find_one({"_id": ObjectId(track_id)}))
    assert track["_import_state"]["status"] == "interrupted"
    assert event_loop.run_until_complete(
        db.import_jobs.count_documents({"slug": slug, "status": "interrupted"})
    ) == 1
    assert student_session.get(f"/api/tracks/{track_id}/tree").status_code == 404
    assert student_session.get(f"/api/tracks/{track_id}").status_code == 404
    assert student_session.get(f"/api/nodes/{topic_id}").status_code == 404
    hidden_progress = student_session.get(f"/api/progress/tracks/{track_id}")
    assert hidden_progress.status_code == 200, hidden_progress.text
    assert hidden_progress.json()["locks"] == {}
    assert all(track["id"] != track_id for track in student_session.get("/api/tracks").json())
    assert all(node["id"] != topic_id for node in student_session.get(
        "/api/search", params={"q": "Topic revised"},
    ).json())
    history = student_session.get("/api/progress/history", params={"track_id": track_id})
    assert history.status_code == 200, history.text
    topic_event = next(item for item in history.json() if item["node_id"] == topic_id)
    assert topic_event["node_title"] != "Topic revised"
    submission_detail = student_session.get(f"/api/submissions/{submission_id}")
    assert submission_detail.status_code == 200, submission_detail.text
    assert submission_detail.json()["block"] is None
    assert submission_detail.json()["submission"]["answer"] == {"text": "synthetic answer"}
    different_payload = _payload(slug)
    different_payload["track"]["title"] = "Different operation while recovery is pending"
    conflict = admin_session.post(f"{API}/import/track?dry_run=false", json=different_payload)
    assert conflict.status_code == 409

    monkeypatch.setattr(imports, "_set_import_phase", original)
    recovered = admin_session.post(f"{API}/import/track?dry_run=false", json=changed_payload)
    assert recovered.status_code == 200, recovered.text
    track = event_loop.run_until_complete(db.tracks.find_one({"_id": ObjectId(track_id)}))
    assert "_import_state" not in track
    assert track["version"] == previous_version + 1
    assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 3
    assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 1
    new_nodes = event_loop.run_until_complete(db.nodes.find({"track_id": track_id}).to_list(10))
    assert {node["meta"]["import_ref"]: str(node["_id"]) for node in new_nodes} == stable_node_ids
    new_block = event_loop.run_until_complete(db.content_blocks.find_one({"track_id": track_id}))
    assert new_block["_id"] == old_block["_id"]
    assert event_loop.run_until_complete(
        db.progress.count_documents({"user_id": student["id"], "node_id": topic_id})
    ) == 1
    assert event_loop.run_until_complete(
        db.notes.count_documents({"user_id": student["id"], "node_id": topic_id})
    ) == 1
    assert event_loop.run_until_complete(db.track_versions.count_documents({"track_id": track_id})) == 3
    assert event_loop.run_until_complete(
        db.edit_history.count_documents({"import_operation_id": {"$exists": True}, "track_id": track_id})
    ) == 2  # One audit for the initial import and one for the resumed update.
    assert student_session.get(f"/api/tracks/{track_id}/tree").status_code == 200


def test_failure_after_track_creation_can_resume_without_duplicate_entities(admin_session, event_loop, monkeypatch):
    import services.imports as imports

    slug = f"qa-create-recovery-{uuid.uuid4().hex[:12]}"
    payload = _payload(slug)
    original = imports._set_import_phase
    failed_once = False

    async def fail_after_track(slug_arg, job_id, owner, phase):
        nonlocal failed_once
        if phase == "nodes" and not failed_once:
            failed_once = True
            raise RuntimeError("synthetic failure after track creation")
        await original(slug_arg, job_id, owner, phase)

    monkeypatch.setattr(imports, "_set_import_phase", fail_after_track)
    failed = event_loop.run_until_complete(
        _post_app(admin_session, f"{API}/import/track?dry_run=false", payload)
    )
    assert failed.status_code == 500
    partial_track = event_loop.run_until_complete(db.tracks.find_one({"slug": slug}))
    assert partial_track and partial_track.get("_import_state")
    assert event_loop.run_until_complete(
        db.nodes.count_documents({"track_id": str(partial_track["_id"])})
    ) == 0
    monkeypatch.setattr(imports, "_set_import_phase", original)
    event_loop.run_until_complete(db.import_locks.update_one(
        {"_id": slug}, {"$set": {"status": "running", "lease_until": now() - timedelta(seconds=1)}},
    ))

    recovered = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
    assert recovered.status_code == 200, recovered.text
    track_id = recovered.json()["track"]["id"]
    assert event_loop.run_until_complete(db.tracks.count_documents({"slug": slug})) == 1
    assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 2
    assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 1
    lock = event_loop.run_until_complete(db.import_locks.find_one({"_id": slug}))
    assert lock["status"] == "completed"
    assert "lease_until" not in lock


def test_concurrent_equivalent_imports_do_not_duplicate_tracks_or_content(admin_session, event_loop):
    from services.imports import run_import

    slug = f"qa-concurrent-{uuid.uuid4().hex[:12]}"
    payload = _payload(slug)
    user_response = admin_session.get("/api/auth/me")
    assert user_response.status_code == 200, user_response.text
    user = user_response.json()

    async def import_twice():
        async def attempt():
            try:
                return await run_import(payload, False, user)
            except Exception as exc:
                return exc
        return await asyncio.gather(attempt(), attempt())

    results = event_loop.run_until_complete(import_twice())
    success = next((result for result in results if isinstance(result, dict)), None)
    assert success is not None, results
    track_id = success["track"]["id"]
    assert event_loop.run_until_complete(db.tracks.count_documents({"slug": slug})) == 1
    assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 2
    assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 1


def test_student_cannot_use_import_endpoint_even_in_dry_run(student_session):
    payload = _payload(f"qa-forbidden-{uuid.uuid4().hex[:12]}")
    response = student_session.post(f"{API}/import/track?dry_run=true", json=payload)
    assert response.status_code == 403
