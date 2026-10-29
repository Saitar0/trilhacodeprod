"""Persist the full reviewed phase as private drafts and read it through API services."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

from database import db

SOURCE_ROOT = os.environ.get("TRILHACODE_BETA7_CURRICULUM_ROOT", "")
pytestmark = pytest.mark.skipif(not SOURCE_ROOT, reason="fonte curricular Beta 7 não foi copiada pelo harness próprio")


def test_full_first_phase_imports_as_private_draft_and_http_readers_preserve_structure(
    admin, student, event_loop,
):
    import services.imports as import_service
    from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase

    batch = convert_first_phase(
        Path(SOURCE_ROOT), source_revision="migration@147dc68:tracked-clean-first-phase-files",
    )
    manifest = batch.to_manifest()
    assert manifest["unit_count"] == 10
    assert manifest["counts"] == {
        "topics": 30,
        "theory_segments": 42,
        "quiz_files": 30,
        "quiz_questions": 44,
        "manual_exercises": 26,
        "project_materials": 11,
        "references": 39,
        "relations": 30,
        "persisted_blocks": 161,
    }
    payload = batch.to_import_payload()
    payload["track"]["slug"] = f"beta7-first-phase-{uuid.uuid4().hex[:16]}"
    payload["track"]["title"] = "Fase 1 — fixture privada Beta 7"
    actor = admin.get("/api/auth/me").json()

    dry_run = event_loop.run_until_complete(import_service.run_import(payload, dry_run=True, user=actor))
    assert dry_run["ok"], dry_run.get("errors")
    assert awaitable_count(event_loop, db.tracks, {"slug": payload["track"]["slug"]}) == 0
    result = event_loop.run_until_complete(import_service.run_import(payload, dry_run=False, user=actor))
    assert not result["dry_run"]

    track = event_loop.run_until_complete(db.tracks.find_one({"slug": payload["track"]["slug"]}))
    assert track is not None
    assert track["status"] == "draft" and track["visibility"] == "private"
    track_id = str(track["_id"])
    assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 44
    assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 161
    assert event_loop.run_until_complete(db.relations.count_documents({"track_id": track_id})) == 21
    assert event_loop.run_until_complete(db.content_blocks.count_documents({
        "track_id": track_id, "type": "quiz",
    })) == 44
    assert event_loop.run_until_complete(db.content_blocks.count_documents({
        "track_id": track_id, "type": "exercise_open",
    })) == 26

    tree_response = admin.get(f"/api/tracks/{track_id}/tree")
    assert tree_response.status_code == 200, tree_response.text
    tree = tree_response.json()
    assert len(tree["nodes"]) == 44
    unit_nodes = event_loop.run_until_complete(db.nodes.find({
        "track_id": track_id, "kind": "submodule",
    }).sort("order", 1).to_list(20))
    assert len(unit_nodes) == 10

    topic_nodes = event_loop.run_until_complete(db.nodes.find({
        "track_id": track_id, "kind": "topic",
    }).sort("order", 1).to_list(50))
    assert len(topic_nodes) == 30
    all_nodes = event_loop.run_until_complete(db.nodes.find({
        "track_id": track_id,
    }).sort("order", 1).to_list(100))
    theory_count = quiz_count = exercise_count = 0
    for node in all_nodes:
        response = admin.get(f"/api/nodes/{node['_id']}")
        assert response.status_code == 200, response.text
        blocks = response.json()["blocks"]
        theory_count += sum(block["type"] == "theory_text" for block in blocks)
        quiz_count += sum(block["type"] == "quiz" for block in blocks)
        exercise_count += sum(block["type"] == "exercise_open" for block in blocks)
    assert (theory_count, quiz_count, exercise_count) == (42, 44, 26)

    # The exact same importer identity/payload is replay-safe; the source stays private.
    replay = event_loop.run_until_complete(import_service.run_import(payload, dry_run=False, user=actor))
    assert replay.get("idempotent_replay") is True
    assert event_loop.run_until_complete(db.tracks.count_documents({"slug": payload["track"]["slug"]})) == 1
    assert event_loop.run_until_complete(db.nodes.count_documents({"track_id": track_id})) == 44
    assert event_loop.run_until_complete(db.content_blocks.count_documents({"track_id": track_id})) == 161
    assert event_loop.run_until_complete(db.edit_history.count_documents({"track_id": track_id})) == 1
    assert event_loop.run_until_complete(db.activity_publications.count_documents({"track_id": track_id})) == 0

    student_tree = student.get(f"/api/tracks/{track_id}/tree")
    assert student_tree.status_code == 404
    student_node = student.get(f"/api/nodes/{unit_nodes[0]['_id']}")
    assert student_node.status_code == 404


def awaitable_count(event_loop, collection, query):
    return event_loop.run_until_complete(collection.count_documents(query))
