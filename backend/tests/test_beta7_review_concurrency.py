"""HTTP and real-Mongo proof of CAS review decisions and idempotent retries."""

from __future__ import annotations

import asyncio
import uuid

from bson import ObjectId

from database import db
from security import hash_password

API = "/api"
ORIGIN = {"Origin": "http://localhost:3000"}


def test_two_scoped_reviewers_cannot_overwrite_a_correction_and_same_key_replays(
    admin, fresh_student, login, seeded_track, event_loop, monkeypatch,
):
    tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
    node = next(item for item in tree["nodes"] if item["kind"] == "topic")
    created = admin.post(f"{API}/blocks", json={
        "node_id": node["id"], "type": "exercise_open", "title": "Atividade Beta 7",
        "status": "draft", "data": {"prompt": "Explique o conceito em texto.", "allow_resubmit": True},
    })
    assert created.status_code == 200, created.text
    published = admin.post(f"{API}/tracks/{seeded_track['id']}/publish", json={"publish_children": True})
    assert published.status_code == 200, published.text
    sent = fresh_student.post(f"{API}/submissions/submit", json={
        "block_id": created.json()["id"], "answer": {"text": "Resposta sintética para a corrida."},
    }, headers={"Idempotency-Key": f"beta7-submit-{uuid.uuid4().hex}"})
    assert sent.status_code == 200, sent.text
    submission_id = sent.json()["id"]

    reviewers = []
    for suffix in ("a", "b"):
        email = f"beta7-reviewer-{suffix}-{uuid.uuid4().hex}@example.com"
        user_id = ObjectId()
        event_loop.run_until_complete(db.users.insert_one({
            "_id": user_id, "email": email, "name": f"Avaliador {suffix.upper()}",
            "password_hash": hash_password("Test@12345678"), "role": "editor", "email_verified": True,
            "is_active": True, "profile": {"bio": "", "goals": "", "preferences": {}},
        }))
        session = login(email, "Test@12345678")
        actor_id = session.get(f"{API}/auth/me").json()["id"]
        scope = {
            "_id": f"{actor_id}:{seeded_track['id']}", "user_id": actor_id,
            "track_id": seeded_track["id"], "operations": ["submissions.read", "submissions.grade"],
            "state": "active", "source": "beta7_synthetic_concurrency_fixture",
        }
        event_loop.run_until_complete(db.learning_review_scopes.insert_one(scope))
        reviewers.append(session)

    import services.submissions as submission_service

    original_database = submission_service.db
    collection = original_database.submissions
    barrier = asyncio.Barrier(2)
    reads = 0

    class _BarrierCollection:
        def __getattr__(self, name):
            return getattr(collection, name)

        async def find_one(self, query, *args, **kwargs):
            nonlocal reads
            if query.get("_id") == ObjectId(submission_id) and reads < 2:
                reads += 1
                await barrier.wait()
            return await collection.find_one(query, *args, **kwargs)

    class _DatabaseProxy:
        def __getattr__(self, name):
            return _BarrierCollection() if name == "submissions" else getattr(original_database, name)

    monkeypatch.setattr(submission_service, "db", _DatabaseProxy())
    keys = [f"beta7-grade-{uuid.uuid4().hex}" for _ in reviewers]
    decisions = [
        {"result": "approved", "feedback": "Aprovado pelo primeiro avaliador.", "criteria": []},
        {"result": "returned", "feedback": "Solicitar revisão.", "criteria": []},
    ]

    async def send_both():
        return await asyncio.gather(*[
            reviewer._client.post(
                f"{API}/submissions/{submission_id}/grade", json=decision,
                headers={**ORIGIN, "Idempotency-Key": key},
            )
            for reviewer, decision, key in zip(reviewers, decisions, keys, strict=True)
        ])

    responses = event_loop.run_until_complete(send_both())
    assert sorted(response.status_code for response in responses) == [200, 409]
    winner_index = next(index for index, response in enumerate(responses) if response.status_code == 200)
    winner, winner_key, winner_decision = reviewers[winner_index], keys[winner_index], decisions[winner_index]
    persisted = event_loop.run_until_complete(db.submissions.find_one({"_id": ObjectId(submission_id)}))
    review_history = [item for item in persisted["history"] if item.get("result") in {"approved", "returned"}]
    assert len(review_history) == 1
    assert len(persisted.get("grading_operations", [])) == 1

    async def replay():
        return await winner._client.post(
            f"{API}/submissions/{submission_id}/grade", json=winner_decision,
            headers={**ORIGIN, "Idempotency-Key": winner_key},
        )

    replayed = event_loop.run_until_complete(replay())
    assert replayed.status_code == 200, replayed.text
    assert replayed.json()["grading"]["result"] == winner_decision["result"]
    assert event_loop.run_until_complete(db.submissions.count_documents({
        "_id": ObjectId(submission_id), "history.result": {"$in": ["approved", "returned"]},
    })) == 1

    async def reuse_with_different_payload():
        return await winner._client.post(
            f"{API}/submissions/{submission_id}/grade",
            json={**winner_decision, "feedback": "Payload divergente."},
            headers={**ORIGIN, "Idempotency-Key": winner_key},
        )

    conflicted = event_loop.run_until_complete(reuse_with_different_payload())
    assert conflicted.status_code == 409
    assert event_loop.run_until_complete(db.submissions.count_documents({"_id": ObjectId(submission_id)})) == 1


def test_reviewer_queue_requires_track_scope_even_for_role_permission(login, seeded_track):
    admin_without_scope = login("admin")
    assert admin_without_scope.get(f"{API}/submissions", params={"track_id": seeded_track["id"]}).status_code == 403

    unscoped_editor = login("editor")
    assert unscoped_editor.get(f"{API}/submissions", params={"track_id": seeded_track["id"]}).status_code == 403
    assert unscoped_editor.get(f"{API}/submissions", params={"track_id": "f" * 24, "skip": -1}).status_code == 403


def test_revoked_track_scope_after_initial_read_blocks_grade_before_cas(
    admin, fresh_student, login, seeded_track, event_loop, monkeypatch,
):
    tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
    node = next(item for item in tree["nodes"] if item["kind"] == "topic")
    exercise = admin.post(f"{API}/blocks", json={
        "node_id": node["id"], "type": "exercise_open", "title": "Atividade de revogação",
        "status": "draft", "data": {"prompt": "Explique em texto.", "allow_resubmit": True},
    })
    assert exercise.status_code == 200, exercise.text
    assert admin.post(f"{API}/tracks/{seeded_track['id']}/publish", json={
        "publish_children": True,
    }).status_code == 200
    sent = fresh_student.post(f"{API}/submissions/submit", json={
        "block_id": exercise.json()["id"], "answer": {"text": "Resposta sintética."},
    }, headers={"Idempotency-Key": f"beta7-revoke-{uuid.uuid4().hex}"})
    assert sent.status_code == 200, sent.text
    submission_id = sent.json()["id"]

    reviewer = login("editor")
    reviewer_id = reviewer.get(f"{API}/auth/me").json()["id"]
    scope_id = f"{reviewer_id}:{seeded_track['id']}"
    event_loop.run_until_complete(db.learning_review_scopes.insert_one({
        "_id": scope_id, "user_id": reviewer_id, "track_id": seeded_track["id"],
        "operations": ["submissions.read", "submissions.grade"],
        "state": "active", "source": "beta7_revocation_race_fixture",
    }))

    import services.submissions as submission_service

    original = submission_service.require_track_scope
    checks = 0

    async def revoke_after_first_check(user, track_id, operation):
        nonlocal checks
        checks += 1
        await original(user, track_id, operation)
        if checks == 1:
            await db.learning_review_scopes.delete_one({"_id": scope_id})

    monkeypatch.setattr(submission_service, "require_track_scope", revoke_after_first_check)
    denied = reviewer.post(
        f"{API}/submissions/{submission_id}/grade",
        json={"result": "approved", "feedback": "Decisão não deve ser persistida."},
        headers={**ORIGIN, "Idempotency-Key": f"beta7-grade-revoke-{uuid.uuid4().hex}"},
    )
    assert denied.status_code == 404
    assert checks == 2
    persisted = event_loop.run_until_complete(db.submissions.find_one({"_id": ObjectId(submission_id)}))
    assert persisted["status"] == "submitted"
    assert persisted.get("grading") is None
    assert not any(item.get("result") for item in persisted.get("history", []))
