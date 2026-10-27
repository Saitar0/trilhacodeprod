"""Integration contracts for immutable, idempotent multiple-choice attempts."""

import asyncio
import uuid

from fastapi import HTTPException

import services.activities as activities_service
from database import db

API = "/api"
ORIGIN = {"Origin": "http://localhost:3000"}


def _activity(admin, student, track, *, correct="option-b", prompt="Versão A", max_attempts=3):
    tree = admin.get(f"{API}/tracks/{track['id']}/tree").json()
    node_id = tree["nodes"][0]["id"]
    data = {
        "activity_schema_version": 1,
        "prompt": prompt,
        "options": [{"id": "option-a", "label": "Alternativa A"}, {"id": "option-b", "label": "Alternativa B"}],
        "correct_option_id": correct,
        "feedback": {"correct": "Resposta correta.", "incorrect": "Revise a explicação."},
        "completion_policy": "responded",
        "max_attempts": max_attempts,
    }
    created = admin.post(f"{API}/blocks", json={
        "node_id": node_id, "type": "quiz", "title": "Atividade sintética", "data": data, "status": "draft",
    })
    assert created.status_code == 200, created.text
    published = admin.post(f"{API}/tracks/{track['id']}/publish", json={"publish_children": True})
    assert published.status_code == 200, published.text
    block_id = created.json()["id"]
    node = student.get(f"{API}/nodes/{node_id}").json()
    activity = next(block["activity"] for block in node["blocks"] if block["id"] == block_id)
    return block_id, node_id, activity


def _start(student, activity_id, published_version_id, key=None):
    response = student.post(
        f"{API}/activities/{activity_id}/attempts",
        json={"published_version_id": published_version_id},
        headers={**ORIGIN, "Idempotency-Key": key or uuid.uuid4().hex},
    )
    return response


def _submit(student, activity_id, attempt, option_id, key=None, *, revision=None):
    return student.post(
        f"{API}/activities/{activity_id}/attempts/{attempt['id']}/submit",
        json={"selected_option_id": option_id, "expected_revision": attempt["revision"] if revision is None else revision},
        headers={**ORIGIN, "Idempotency-Key": key or uuid.uuid4().hex},
    )


def test_attempts_grade_on_server_replay_safely_and_project_only_block_progress(
    admin, fresh_student, seeded_track, event_loop,
):
    activity_id, node_id, activity = _activity(admin, fresh_student, seeded_track)
    detail = fresh_student.get(f"{API}/nodes/{node_id}").json()
    public_block = next(block for block in detail["blocks"] if block["id"] == activity_id)
    assert public_block["activity"]["published_version_id"] == activity["published_version_id"]
    assert "correct_option_id" not in public_block["activity"]
    assert "correct_index" not in public_block["data"]

    key = uuid.uuid4().hex
    started = _start(fresh_student, activity_id, activity["published_version_id"], key)
    replayed = _start(fresh_student, activity_id, activity["published_version_id"], key)
    assert started.status_code == replayed.status_code == 201
    attempt = started.json()
    assert attempt["id"] == replayed.json()["id"]

    draft_key = uuid.uuid4().hex
    saved = fresh_student.put(
        f"{API}/activities/{activity_id}/attempts/{attempt['id']}/draft",
        json={"selected_option_id": "option-a", "expected_revision": 0},
        headers={**ORIGIN, "Idempotency-Key": draft_key},
    )
    assert saved.status_code == 200 and saved.json()["revision"] == 1
    changed_draft_replay = fresh_student.put(
        f"{API}/activities/{activity_id}/attempts/{attempt['id']}/draft",
        json={"selected_option_id": "option-a", "expected_revision": 1},
        headers={**ORIGIN, "Idempotency-Key": draft_key},
    )
    assert changed_draft_replay.status_code == 409
    assert changed_draft_replay.json()["error"]["details"]["code"] == "activity_idempotency_conflict"
    submit_key = uuid.uuid4().hex
    incorrect = _submit(fresh_student, activity_id, saved.json(), "option-a", submit_key)
    replay = _submit(fresh_student, activity_id, saved.json(), "option-a", submit_key)
    assert incorrect.status_code == replay.status_code == 200
    assert incorrect.json()["state"] == "evaluated"
    assert incorrect.json()["result"]["is_correct"] is False
    assert incorrect.json()["feedback"] == "Resposta registrada. Você ainda pode iniciar outra tentativa."
    assert replay.json()["id"] == incorrect.json()["id"]
    assert replay.json()["result"] == incorrect.json()["result"]
    changed_replay = _submit(fresh_student, activity_id, saved.json(), "option-b", submit_key)
    assert changed_replay.status_code == 409
    assert changed_replay.json()["error"]["details"]["code"] == "activity_idempotency_conflict"
    changed_revision_replay = _submit(
        fresh_student, activity_id, saved.json(), "option-a", submit_key,
        revision=saved.json()["revision"] - 1,
    )
    assert changed_revision_replay.status_code == 409
    assert changed_revision_replay.json()["error"]["details"]["code"] == "activity_idempotency_conflict"

    second = _start(fresh_student, activity_id, activity["published_version_id"])
    assert second.status_code == 201
    correct = _submit(fresh_student, activity_id, second.json(), "option-b")
    assert correct.status_code == 200 and correct.json()["result"]["is_correct"] is True
    user_id = fresh_student.get(f"{API}/auth/me").json()["id"]
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user_id, "node_id": node_id, "block_id": activity_id,
        "type": "status:completed", "attempt_id": {"$exists": True},
    })) == 2
    evidence = event_loop.run_until_complete(db.learning_events.find({
        "user_id": user_id, "node_id": node_id, "block_id": activity_id,
    }).to_list(10))
    assert len(evidence) == 2
    assert all(item["evidence_kind"] == "server_assessed" for item in evidence)
    progress = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
    assert progress["blocks"][activity_id]["status"] == "completed"
    assert progress["blocks"][activity_id]["attempts"] == 2
    assert node_id not in progress["nodes"] or progress["nodes"][node_id]["status"] != "completed"


def test_invalid_versioned_activity_does_not_activate_or_publish_partial_content(
    admin, fresh_student, seeded_track,
):
    activity_id, _node_id, activity = _activity(admin, fresh_student, seeded_track)
    before = admin.get(f"{API}/tracks/{seeded_track['id']}").json()
    tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
    node_id = tree["nodes"][0]["id"]
    invalid = admin.post(f"{API}/blocks", json={
        "node_id": node_id,
        "type": "quiz",
        "title": "Invalid synthetic activity",
        "status": "draft",
        "data": {
            "activity_schema_version": 1,
            "prompt": "Invalid because its key is absent.",
            "options": [{"id": "one", "label": "One"}, {"id": "two", "label": "Two"}],
            "correct_option_id": "missing",
        },
    })
    assert invalid.status_code == 200
    result = admin.post(f"{API}/tracks/{seeded_track['id']}/publish", json={"publish_children": True})
    assert result.status_code == 422
    after = admin.get(f"{API}/tracks/{seeded_track['id']}").json()
    assert after["version"] == before["version"]
    assert after["published_activity_version_id"] == before["published_activity_version_id"]
    student_node = fresh_student.get(f"{API}/nodes/{node_id}").json()
    assert any(item["id"] == activity_id for item in student_node["blocks"])
    assert all(item["id"] != invalid.json()["id"] for item in student_node["blocks"])
    deleted = admin.delete(f"{API}/blocks/{invalid.json()['id']}")
    assert deleted.status_code == 200


def test_attempts_enforce_cas_conflicts_and_owner_scoping(admin, fresh_student, login, seeded_track):
    activity_id, _node_id, activity = _activity(admin, fresh_student, seeded_track)
    started = _start(fresh_student, activity_id, activity["published_version_id"]).json()
    draft_key = uuid.uuid4().hex
    saved = fresh_student.put(
        f"{API}/activities/{activity_id}/attempts/{started['id']}/draft",
        json={"selected_option_id": "option-a", "expected_revision": 0},
        headers={**ORIGIN, "Idempotency-Key": draft_key},
    )
    assert saved.status_code == 200
    reused = fresh_student.put(
        f"{API}/activities/{activity_id}/attempts/{started['id']}/draft",
        json={"selected_option_id": "option-a", "expected_revision": 1},
        headers={**ORIGIN, "Idempotency-Key": draft_key},
    )
    assert reused.status_code == 409
    assert reused.json()["error"]["details"]["code"] == "activity_idempotency_conflict"
    stale = fresh_student.put(
        f"{API}/activities/{activity_id}/attempts/{started['id']}/draft",
        json={"selected_option_id": "option-b", "expected_revision": 0},
        headers={**ORIGIN, "Idempotency-Key": uuid.uuid4().hex},
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["details"]["code"] == "activity_revision_conflict"

    other_student = login("student")
    hidden = other_student.get(f"{API}/activities/{activity_id}/attempts/{started['id']}")
    assert hidden.status_code == 404


def test_legacy_attempt_remains_pinned_when_a_new_publication_changes_the_answer(
    admin, fresh_student, seeded_track,
):
    activity_id, node_id, old_activity = _activity(admin, fresh_student, seeded_track, correct="option-a", prompt="Versão antiga")
    old_attempt = _start(fresh_student, activity_id, old_activity["published_version_id"]).json()

    live_block = admin.get(f"{API}/nodes/{node_id}").json()
    block = next(item for item in live_block["blocks"] if item["id"] == activity_id)
    new_data = dict(block["data"])
    new_data.update(prompt="Versão nova", correct_option_id="option-b")
    updated = admin.put(f"{API}/blocks/{activity_id}", json={"data": new_data})
    assert updated.status_code == 200, updated.text
    published = admin.post(f"{API}/tracks/{seeded_track['id']}/publish", json={})
    assert published.status_code == 200, published.text

    # The old attempt uses its old immutable key even after the live block changes.
    result = _submit(fresh_student, activity_id, old_attempt, "option-a")
    assert result.status_code == 200
    assert result.json()["result"]["is_correct"] is True
    assert result.json()["activity"]["prompt"] == "Versão antiga"
    current = fresh_student.get(f"{API}/nodes/{node_id}").json()
    current_activity = next(item["activity"] for item in current["blocks"] if item["id"] == activity_id)
    assert current_activity["prompt"] == "Versão nova"


def test_projection_failure_keeps_evaluated_attempt_pending_and_retry_reconciles(
    admin, fresh_student, seeded_track, monkeypatch, event_loop,
):
    activity_id, _node_id, activity = _activity(admin, fresh_student, seeded_track)
    attempt = _start(fresh_student, activity_id, activity["published_version_id"]).json()
    original = activities_service.set_progress

    async def fail_once(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="synthetic projection failure")

    monkeypatch.setattr(activities_service, "set_progress", fail_once)
    key = uuid.uuid4().hex
    first = _submit(fresh_student, activity_id, attempt, "option-b", key)
    assert first.status_code == 503
    saved = event_loop.run_until_complete(activities_service.db.activity_attempts.find_one({"_id": attempt["id"]}))
    assert saved["state"] == "evaluated"
    assert saved["projection_status"] == "pending"

    monkeypatch.setattr(activities_service, "set_progress", original)
    retry = _submit(fresh_student, activity_id, attempt, "option-b", key)
    assert retry.status_code == 200
    assert retry.json()["projection_status"] == "complete"


def test_cookie_mutation_rejects_untrusted_origin(admin, fresh_student, seeded_track):
    activity_id, _node_id, activity = _activity(admin, fresh_student, seeded_track)
    response = fresh_student.post(
        f"{API}/activities/{activity_id}/attempts",
        json={"published_version_id": activity["published_version_id"]},
        headers={"Idempotency-Key": uuid.uuid4().hex, "Origin": "https://attacker.example"},
    )
    assert response.status_code == 403


def test_published_activity_cannot_be_completed_through_generic_progress_endpoint(
    admin, fresh_student, seeded_track,
):
    activity_id, node_id, activity = _activity(admin, fresh_student, seeded_track)
    response = fresh_student.post(f"{API}/progress", json={
        "node_id": node_id,
        "block_id": activity_id,
        "status": "completed",
        "data": {"correct": True, "score": 100},
        "operation_id": uuid.uuid4().hex,
    })
    assert response.status_code == 403
    record = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
    assert activity_id not in record["blocks"]


def test_client_cannot_forge_server_assessed_evidence_on_other_blocks(
    admin, fresh_student, seeded_track, event_loop,
):
    _activity_id, node_id, _activity_view = _activity(admin, fresh_student, seeded_track)
    created = admin.post(f"{API}/blocks", json={
        "node_id": node_id,
        "type": "exercise_objective",
        "title": "Synthetic self-report block",
        "status": "published",
        "data": {"prompt": "Marque como concluído."},
    })
    assert created.status_code == 200
    block_id = created.json()["id"]
    response = fresh_student.post(f"{API}/progress", json={
        "node_id": node_id,
        "block_id": block_id,
        "status": "completed",
        "data": {"activity_attempt_id": "forged", "is_correct": True},
        "operation_id": uuid.uuid4().hex,
    })
    assert response.status_code == 200
    user_id = fresh_student.get(f"{API}/auth/me").json()["id"]
    event = event_loop.run_until_complete(db.learning_events.find_one({
        "user_id": user_id, "node_id": node_id, "block_id": block_id,
    }))
    assert event["evidence_kind"] == "self_reported"


def test_concurrent_submit_replay_creates_one_attempt_event(admin, fresh_student, seeded_track, event_loop):
    activity_id, node_id, activity = _activity(admin, fresh_student, seeded_track)
    attempt = _start(fresh_student, activity_id, activity["published_version_id"]).json()
    operation_key = uuid.uuid4().hex
    payload = {
        "selected_option_id": "option-b",
        "expected_revision": attempt["revision"],
    }
    headers = {**ORIGIN, "Idempotency-Key": operation_key}

    async def send_twice():
        return await asyncio.gather(*(
            fresh_student._client.post(
                f"{API}/activities/{activity_id}/attempts/{attempt['id']}/submit",
                json=payload, headers=headers,
            )
            for _ in range(2)
        ))

    responses = event_loop.run_until_complete(send_twice())
    assert [response.status_code for response in responses] == [200, 200]
    assert responses[0].json()["id"] == responses[1].json()["id"]
    user_id = fresh_student.get(f"{API}/auth/me").json()["id"]
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user_id, "node_id": node_id, "block_id": activity_id,
        "type": "status:completed", "attempt_id": attempt["id"],
    })) == 1
