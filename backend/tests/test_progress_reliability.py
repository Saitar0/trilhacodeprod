"""Integration coverage for idempotent, versioned learning progress."""

import asyncio
import uuid

import pytest
from fastapi import HTTPException

import services.progress as progress_service
from database import db

API = "/api"


def _first_node(student, track):
    response = student.get(f"{API}/tracks/{track['id']}/tree")
    assert response.status_code == 200
    return response.json()["nodes"][0]


def _progress_payload(node_id, status, revision, operation_id, *, block_id=None, data=None, attempt_id=None):
    payload = {
        "node_id": node_id,
        "block_id": block_id,
        "status": status,
        "data": data or {},
        "expected_revision": revision,
        "operation_id": operation_id,
    }
    if attempt_id is not None:
        payload["attempt_id"] = attempt_id
    return payload


def test_completion_retry_is_idempotent_and_reopen_is_a_new_transition(
    fresh_student, seeded_track, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    key = {"user_id": user["id"], "node_id": node["id"], "block_id": None}
    first_id = uuid.uuid4().hex
    first = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "completed", 0, first_id),
    )
    assert first.status_code == 200, first.text
    first_record = first.json()
    assert first_record["status"] == "completed"
    assert first_record["attempts"] == 0  # leitura concluída não é tentativa avaliativa
    assert first_record["revision"] == 1

    repeated = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "completed", 0, first_id),
    )
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["revision"] == 1
    assert repeated.json()["completed_at"] == first_record["completed_at"]
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 1

    # Reopening remains supported, and a later completion is a distinct state transition.
    reopened = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "in_progress", 1, uuid.uuid4().hex),
    )
    assert reopened.status_code == 200, reopened.text
    assert reopened.json()["completed_at"] is None
    completed_again = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "completed", 2, uuid.uuid4().hex),
    )
    assert completed_again.status_code == 200, completed_again.text
    assert completed_again.json()["attempts"] == 0
    assert event_loop.run_until_complete(db.progress.count_documents(key)) == 1
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 2
    event = event_loop.run_until_complete(db.learning_events.find_one({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    }))
    assert event["evidence_kind"] == "self_reported"


def test_concurrent_replay_with_same_operation_creates_one_completion_event(
    fresh_student, seeded_track, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    operation_id = uuid.uuid4().hex
    payload = _progress_payload(node["id"], "completed", 0, operation_id)

    async def send_twice():
        return await asyncio.gather(
            fresh_student._client.post(f"{API}/progress", json=payload),
            fresh_student._client.post(f"{API}/progress", json=payload),
        )

    responses = event_loop.run_until_complete(send_twice())
    assert [response.status_code for response in responses] == [200, 200]
    assert responses[0].json()["id"] == responses[1].json()["id"]
    assert responses[0].json()["revision"] == responses[1].json()["revision"] == 1
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 1


def test_concurrent_visit_replay_creates_one_view_event_and_stable_progress(
    fresh_student, seeded_track, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    payload = {"node_id": node["id"], "operation_id": uuid.uuid4().hex}

    async def visit_twice():
        return await asyncio.gather(
            fresh_student._client.post(f"{API}/progress/visit", json=payload),
            fresh_student._client.post(f"{API}/progress/visit", json=payload),
        )

    responses = event_loop.run_until_complete(visit_twice())
    assert [response.status_code for response in responses] == [200, 200]
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "view",
    })) == 1
    progress_record = event_loop.run_until_complete(db.progress.find_one({
        "user_id": user["id"], "node_id": node["id"], "block_id": None,
    }))
    assert progress_record["status"] == "in_progress"
    assert progress_record["revision"] == 0


def test_distinct_stale_progress_update_returns_current_revision(
    fresh_student, seeded_track,
):
    node = _first_node(fresh_student, seeded_track)
    first = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "in_progress", 0, uuid.uuid4().hex),
    )
    stale = fresh_student.post(
        f"{API}/progress",
        json=_progress_payload(node["id"], "completed", 0, uuid.uuid4().hex),
    )
    assert first.status_code == 200
    assert stale.status_code == 409
    assert stale.json()["error"]["details"]["code"] == "progress_version_conflict"
    assert stale.json()["error"]["details"]["current"]["revision"] == first.json()["revision"]
    assert stale.json()["error"]["details"]["current"]["status"] == "in_progress"


def test_progress_updates_track_state_and_reject_reused_key_with_different_payload(
    fresh_student, seeded_track, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    operation_id = uuid.uuid4().hex
    first = fresh_student.post(f"{API}/progress", json=_progress_payload(
        node["id"], "in_progress", 0, operation_id,
    ))
    assert first.status_code == 200, first.text

    track_progress = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}")
    assert track_progress.status_code == 200
    assert track_progress.json()["state"]["last_node_id"] == node["id"]
    assert track_progress.json()["state"]["last_node_title"] == node["title"]
    assert event_loop.run_until_complete(db.user_track_state.find_one({
        "user_id": user["id"], "track_id": node["track_id"],
    })) is not None

    reused = fresh_student.post(f"{API}/progress", json=_progress_payload(
        node["id"], "completed", 1, operation_id,
    ))
    assert reused.status_code == 409
    assert reused.json()["error"]["details"]["code"] == "progress_idempotency_conflict"
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 0


def test_progress_writes_are_scoped_to_the_authenticated_user(
    fresh_student, seeded_track, session_factory, create_verified_user, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    owner_id = fresh_student.get(f"{API}/auth/me").json()["id"]
    owner_update = fresh_student.post(f"{API}/progress", json=_progress_payload(
        node["id"], "completed", 0, uuid.uuid4().hex,
    ))
    assert owner_update.status_code == 200

    other = session_factory()
    create_verified_user(other, f"progress_reader_{uuid.uuid4().hex}@example.com")
    other_id = other.get(f"{API}/auth/me").json()["id"]
    other_update = other.post(f"{API}/progress", json=_progress_payload(
        node["id"], "in_progress", 0, uuid.uuid4().hex,
    ))
    assert other_update.status_code == 200
    assert other_update.json()["status"] == "in_progress"

    owner_record = event_loop.run_until_complete(db.progress.find_one({
        "user_id": owner_id, "node_id": node["id"], "block_id": None,
    }))
    other_record = event_loop.run_until_complete(db.progress.find_one({
        "user_id": other_id, "node_id": node["id"], "block_id": None,
    }))
    assert owner_record["status"] == "completed"
    assert other_record["status"] == "in_progress"


def test_mastery_status_is_not_accepted_as_self_reported_progress(
    fresh_student, seeded_track,
):
    node = _first_node(fresh_student, seeded_track)
    response = fresh_student.post(f"{API}/progress", json={
        "node_id": node["id"], "status": "mastered", "data": {},
    })
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"


def test_block_attempts_are_distinct_from_request_idempotency(
    admin, fresh_student, event_loop,
):
    track = admin.post(f"{API}/tracks", json={"title": f"Test attempts {uuid.uuid4().hex}"}).json()
    try:
        node = admin.post(f"{API}/nodes", json={
            "track_id": track["id"], "kind": "topic", "title": "Quiz node",
        }).json()
        block = admin.post(f"{API}/blocks", json={
            "node_id": node["id"], "type": "exercise_objective", "title": "Exercício manual",
            "data": {"prompt": "Envie sua resposta para revisão."},
            "status": "published",
        }).json()
        published = admin.post(f"{API}/tracks/{track['id']}/publish", json={})
        assert published.status_code == 200, published.text
        user = fresh_student.get(f"{API}/auth/me").json()

        first_id = uuid.uuid4().hex
        attempt_id = uuid.uuid4().hex
        first = fresh_student.post(f"{API}/progress", json=_progress_payload(
            node["id"], "completed", 0, first_id, block_id=block["id"], data={"selected": 0},
            attempt_id=attempt_id,
        ))
        # A retried submission may reach the server under a new request ID after a client timeout.
        retry = fresh_student.post(f"{API}/progress", json=_progress_payload(
            node["id"], "completed", 0, uuid.uuid4().hex, block_id=block["id"], data={"selected": 0},
            attempt_id=attempt_id,
        ))
        changed_replay = fresh_student.post(f"{API}/progress", json=_progress_payload(
            node["id"], "completed", 1, uuid.uuid4().hex, block_id=block["id"], data={"selected": 1},
            attempt_id=attempt_id,
        ))
        # The learner's explicit next submission is a new attempt, even with the same selected answer.
        second_attempt = fresh_student.post(f"{API}/progress", json=_progress_payload(
            node["id"], "completed", 1, uuid.uuid4().hex, block_id=block["id"], data={"selected": 0},
            attempt_id=uuid.uuid4().hex,
        ))

        assert first.status_code == retry.status_code == second_attempt.status_code == 200
        assert changed_replay.status_code == 409
        assert first.json()["attempts"] == 1
        assert retry.json()["attempts"] == 1
        assert second_attempt.json()["attempts"] == 2
        assert retry.json()["revision"] == first.json()["revision"] == 1
        assert event_loop.run_until_complete(db.learning_events.count_documents({
            "user_id": user["id"], "node_id": node["id"], "block_id": block["id"],
            "type": "status:completed",
        })) == 2
    finally:
        admin.delete(f"{API}/tracks/{track['id']}")


def test_failed_event_projection_is_reconciled_on_retry(
    fresh_student, seeded_track, event_loop, monkeypatch,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    body = _progress_payload(node["id"], "completed", 0, uuid.uuid4().hex)
    original_flush = progress_service._flush_pending_progress_event
    calls = 0

    async def fail_after_transition(key):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise HTTPException(status_code=503, detail="simulated event store outage")
        return await original_flush(key)

    monkeypatch.setattr(progress_service, "_flush_pending_progress_event", fail_after_transition)
    with pytest.raises(HTTPException) as error:
        event_loop.run_until_complete(progress_service.set_progress(body, user))
    assert error.value.status_code == 503

    key = {"user_id": user["id"], "node_id": node["id"], "block_id": None}
    pending = event_loop.run_until_complete(db.progress.find_one(key))
    assert pending["status"] == "completed"
    assert pending["_pending_event"]["type"] == "status:completed"
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 0

    monkeypatch.setattr(progress_service, "_flush_pending_progress_event", original_flush)
    retry = event_loop.run_until_complete(progress_service.set_progress(body, user))
    assert retry["status"] == "completed"
    assert "_pending_event" not in event_loop.run_until_complete(db.progress.find_one(key))
    assert event_loop.run_until_complete(db.learning_events.count_documents({
        "user_id": user["id"], "node_id": node["id"], "type": "status:completed",
    })) == 1
