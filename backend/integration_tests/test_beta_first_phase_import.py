"""Persistent proof through the real C16 import and read services in MongoDB 7."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase  # noqa: E402
from integration_tests.beta_first_phase_import_harness import (  # noqa: E402
    bind_application_services,
    drop_owned_database,
    open_owned_database,
    seed_import_contract,
)

SOURCE_ROOT = os.environ.get("TRILHACODE_BETA4_SOURCE_ROOT", "")
ENABLED = bool(os.environ.get("TRILHACODE_BETA4_MONGO_URI")) and bool(SOURCE_ROOT)
pytestmark = pytest.mark.skipif(not ENABLED, reason="fontes ou MongoDB descartável Beta 4 não configurados")


@pytest_asyncio.fixture
async def isolated_import_db():
    client, database, run_id = await open_owned_database()
    await seed_import_contract(database)
    import_service, nodes_service = bind_application_services(database)
    try:
        yield client, database, run_id, import_service, nodes_service
    finally:
        await drop_owned_database(client, database, run_id)
        import database as database_module
        await database_module.client.close()


def _batch_payload() -> dict[str, Any]:
    batch = convert_first_phase(Path(SOURCE_ROOT))
    assert batch.conversion_status == "CONVERSION_SUCCESS_WITH_WARNINGS"
    return batch.to_import_payload()


@pytest.mark.asyncio
async def test_full_batch_uses_real_import_and_read_services_without_publication(isolated_import_db) -> None:
    _client, database, _run_id, importer, readers = isolated_import_db
    payload = _batch_payload()
    actor = {"id": "beta4-synthetic-admin", "name": "Beta 4 synthetic", "role": "admin"}

    preflight = await importer.run_import(payload, dry_run=True, user=actor)
    assert preflight["ok"], preflight.get("errors")
    assert await database["tracks"].count_documents({}) == 0
    assert await database["nodes"].count_documents({}) == 0
    assert await database["content_blocks"].count_documents({}) == 0
    result = await importer.run_import(payload, dry_run=False, user=actor)
    assert not result["dry_run"]

    track = await database["tracks"].find_one({"slug": payload["track"]["slug"]})
    assert track is not None
    assert track["status"] == "draft"
    assert track["visibility"] == "private"
    assert "_import_state" not in track
    track_id = str(track["_id"])
    assert await database["nodes"].count_documents({"track_id": track_id}) == 44
    assert await database["content_blocks"].count_documents({"track_id": track_id}) == 161
    assert await database["relations"].count_documents({"track_id": track_id}) == 21
    assert await database["edit_history"].count_documents({"track_id": track_id}) == 1
    assert await database["content_blocks"].count_documents({
        "track_id": track_id, "type": "quiz",
    }) == 44
    assert await database["content_blocks"].count_documents({
        "track_id": track_id, "type": "exercise_open",
    }) == 26

    tree = await readers.get_track_tree(track_id, actor)
    assert len(tree["nodes"]) == 44
    assert sum(tree["block_counts"].values()) == 161
    unit_11 = await database["nodes"].find_one({
        "track_id": track_id, "meta.import_ref": "unit-1-1",
    })
    assert unit_11 is not None
    unit_tree = await readers.get_node(str(unit_11["_id"]), actor)
    assert unit_tree["node"]["status"] == "draft"
    topic_nodes = await database["nodes"].find({
        "track_id": track_id, "parent_id": str(unit_11["_id"]), "kind": "topic",
    }).sort("order", 1).to_list(20)
    assert len(topic_nodes) == 5
    topic_reads = [await readers.get_node(str(node["_id"]), actor) for node in topic_nodes]
    theory_blocks = [
        block for topic in topic_reads for block in topic["blocks"]
        if block["type"] == "theory_text"
    ]
    quiz_blocks = [
        block for topic in topic_reads for block in topic["blocks"]
        if block["type"] == "quiz"
    ]
    assert len(theory_blocks) == 8
    assert len(quiz_blocks) == 5
    assert [block["order"] for block in topic_reads[1]["blocks"]] == list(
        range(len(topic_reads[1]["blocks"]))
    )

    # The actual service denies access to a private draft; its existing helper
    # also strips solution fields from a student projection.
    with pytest.raises(Exception) as denied:
        await readers.get_track_tree(track_id, {"id": "synthetic-student", "role": "student"})
    assert getattr(denied.value, "status_code", None) == 404
    import services.nodes as nodes_service
    for block in quiz_blocks:
        projected = nodes_service._student_block(block)
        assert "correct_option_id" not in projected["data"]
        assert "feedback" not in projected["data"]
        assert "explanation" not in projected["data"]

    replay = await importer.run_import(payload, dry_run=False, user=actor)
    assert replay["idempotent_replay"] is True
    assert await database["nodes"].count_documents({"track_id": track_id}) == 44
    assert await database["content_blocks"].count_documents({"track_id": track_id}) == 161
    assert await database["relations"].count_documents({"track_id": track_id}) == 21
    assert await database["edit_history"].count_documents({"track_id": track_id}) == 1


@pytest.mark.asyncio
async def test_partial_batch_failure_resumes_same_import_without_duplicates(isolated_import_db) -> None:
    _client, database, _run_id, importer, _readers = isolated_import_db
    payload = _batch_payload()
    actor = {"id": "beta4-synthetic-admin", "name": "Beta 4 synthetic", "role": "admin"}
    original = importer._block_values
    calls = 0

    def fail_after_partial_stage(*args: Any, **kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        if calls == 61:
            raise RuntimeError("synthetic Beta 4 interruption after 60 block writes")
        return original(*args, **kwargs)

    with patch.object(importer, "_block_values", side_effect=fail_after_partial_stage):
        with pytest.raises(RuntimeError, match="synthetic Beta 4 interruption"):
            await importer.run_import(payload, dry_run=False, user=actor)

    track = await database["tracks"].find_one({"slug": payload["track"]["slug"]})
    assert track is not None
    track_id = str(track["_id"])
    assert track.get("_import_state", {}).get("status") == "interrupted"
    partial_count = await database["content_blocks"].count_documents({"track_id": track_id})
    assert partial_count == 60
    job = await database["import_jobs"].find_one({"slug": payload["track"]["slug"]})
    assert job is not None and job["status"] == "interrupted"

    resumed = await importer.run_import(payload, dry_run=False, user=actor)
    assert resumed.get("idempotent_replay") is not True
    final_track = await database["tracks"].find_one({"_id": track["_id"]})
    assert final_track is not None and "_import_state" not in final_track
    assert await database["nodes"].count_documents({"track_id": track_id}) == 44
    assert await database["content_blocks"].count_documents({"track_id": track_id}) == 161
    assert await database["relations"].count_documents({"track_id": track_id}) == 21
    assert await database["edit_history"].count_documents({"track_id": track_id}) == 1
