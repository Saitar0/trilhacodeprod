"""Typed prerequisite behavior backed by the disposable MongoDB fixture."""

import uuid

from bson.decimal128 import Decimal128

from learning import _quiz_progress_passed

API = "/api"


def _create_typed_quiz(admin, *, question_count: int = 10, publish: bool = True) -> dict:
    suffix = uuid.uuid4().hex[:10]
    track = admin.post(
        f"{API}/tracks",
        json={
            "title": f"TEST_typed_prerequisite_{suffix}",
            "settings": {"enforce_prerequisites": True},
        },
    )
    assert track.status_code == 200, track.text
    track_id = track.json()["id"]
    quiz = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": f"Quiz prerequisite {suffix}",
            "status": "published",
        },
    )
    dependent = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": f"Dependent topic {suffix}",
            "status": "published",
        },
    )
    assert quiz.status_code == dependent.status_code == 200
    quiz_id = quiz.json()["id"]
    dependent_id = dependent.json()["id"]
    blocks = []
    for index in range(question_count):
        response = admin.post(
            f"{API}/blocks",
            json={
                "node_id": quiz_id,
                "type": "quiz",
                "title": f"Question {index + 1}",
                "data": {
                    "question": f"Prompt {index + 1}",
                    "options": ["Correct", "Incorrect"],
                    "correct_index": 0,
                },
                "status": "published",
            },
        )
        assert response.status_code == 200, response.text
        blocks.append(response.json())
    relation = admin.post(
        f"{API}/relations",
        json={
            "node_id": dependent_id,
            "target_id": quiz_id,
            "type": "prerequisite",
            "enforced": True,
            "prerequisite_kind": "quiz_passed",
        },
    )
    assert relation.status_code == 200, relation.text
    assert admin.post(f"{API}/tracks/{track_id}/publish", json={}).status_code == 200
    version_id = None
    if publish:
        published = admin.post(f"{API}/admin/quizzes/{quiz_id}/versions")
        assert published.status_code == 200, published.text
        version_id = published.json()["version_id"]
    return {
        "track_id": track_id,
        "quiz_id": quiz_id,
        "dependent_id": dependent_id,
        "version_id": version_id,
        "blocks": blocks,
    }


def _answers(quiz: dict, correct_count: int) -> list[dict]:
    return [
        {
            "question_id": block["id"],
            "option_id": "option-1" if index < correct_count else "option-2",
        }
        for index, block in enumerate(quiz["blocks"])
    ]


def _submit(student, quiz: dict, correct_count: int, key: str | None = None):
    return student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/attempts",
        json={"version_id": quiz["version_id"], "answers": _answers(quiz, correct_count)},
        headers={"Idempotency-Key": key or str(uuid.uuid4())},
    )


def _progress(student, quiz: dict) -> dict:
    response = student.get(f"{API}/progress/tracks/{quiz['track_id']}")
    assert response.status_code == 200, response.text
    return response.json()


def test_quiz_score_threshold_uses_exact_server_persisted_decimal():
    assert not _quiz_progress_passed({"passed": True, "best_score_percent": Decimal128("69.99")})
    assert _quiz_progress_passed({"passed": True, "best_score_percent": Decimal128("70")})
    assert not _quiz_progress_passed({"passed": False, "best_score_percent": Decimal128("100")})
    assert not _quiz_progress_passed({"passed": True, "best_score_percent": 70.0})


def test_quiz_prerequisite_requires_published_quiz_and_authoritative_pass(admin, fresh_student):
    quiz = _create_typed_quiz(admin)
    try:
        initial = _progress(fresh_student, quiz)
        assert quiz["dependent_id"] in initial["locks"]
        requirement = initial["prerequisite_states"][quiz["dependent_id"]][0]
        assert requirement == {
            "target_id": quiz["quiz_id"],
            "prerequisite_kind": "quiz_passed",
            "status": "pending",
        }

        # Client-supplied completion metadata cannot manufacture an assessment result.
        marked = fresh_student.post(
            f"{API}/progress",
            json={
                "node_id": quiz["quiz_id"],
                "status": "completed",
                "data": {"passed": True, "score": 100},
            },
        )
        assert marked.status_code == 200, marked.text
        assert quiz["dependent_id"] in _progress(fresh_student, quiz)["locks"]

        failed = _submit(fresh_student, quiz, 6)
        assert failed.status_code == 200, failed.text
        assert failed.json()["passed"] is False
        assert quiz["dependent_id"] in _progress(fresh_student, quiz)["locks"]

        exact = _submit(fresh_student, quiz, 7)
        assert exact.status_code == 200, exact.text
        assert exact.json()["score_percent"] == 70
        assert exact.json()["passed"] is True
        assert quiz["dependent_id"] not in _progress(fresh_student, quiz)["locks"]
        assert (
            _progress(fresh_student, quiz)["prerequisite_states"][quiz["dependent_id"]][0]["status"]
            == "satisfied"
        )
    finally:
        admin.delete(f"{API}/tracks/{quiz['track_id']}")


def test_unpublished_quiz_prerequisite_fails_closed(admin, fresh_student):
    quiz = _create_typed_quiz(admin, publish=False)
    try:
        data = _progress(fresh_student, quiz)
        assert quiz["dependent_id"] in data["locks"]
        assert data["prerequisite_states"][quiz["dependent_id"]][0]["status"] == "unavailable"
    finally:
        admin.delete(f"{API}/tracks/{quiz['track_id']}")


def test_quiz_pass_is_scoped_to_authenticated_learner(admin, fresh_student, login):
    quiz = _create_typed_quiz(admin, question_count=1)
    other_student = login("student@example.com")
    try:
        passed = _submit(fresh_student, quiz, 1)
        assert passed.status_code == 200, passed.text
        assert quiz["dependent_id"] not in _progress(fresh_student, quiz)["locks"]
        assert quiz["dependent_id"] in _progress(other_student, quiz)["locks"]
    finally:
        admin.delete(f"{API}/tracks/{quiz['track_id']}")


def test_old_quiz_version_does_not_satisfy_new_active_version(admin, fresh_student):
    quiz = _create_typed_quiz(admin, question_count=1)
    try:
        passed = _submit(fresh_student, quiz, 1)
        assert passed.status_code == 200, passed.text
        assert quiz["dependent_id"] not in _progress(fresh_student, quiz)["locks"]

        updated = admin.put(
            f"{API}/blocks/{quiz['blocks'][0]['id']}",
            json={
                "data": {
                    "question": "Changed prompt creates a new version",
                    "options": ["Correct", "Incorrect"],
                    "correct_index": 0,
                },
            },
        )
        assert updated.status_code == 200, updated.text
        version = admin.post(f"{API}/admin/quizzes/{quiz['quiz_id']}/versions")
        assert version.status_code == 200, version.text
        assert version.json()["version_id"] != quiz["version_id"]
        assert quiz["dependent_id"] in _progress(fresh_student, quiz)["locks"]
        state = _progress(fresh_student, quiz)["prerequisite_states"][quiz["dependent_id"]][0]
        assert state["status"] == "pending"
    finally:
        admin.delete(f"{API}/tracks/{quiz['track_id']}")


def test_typed_reading_and_legacy_relations_preserve_completion_behavior(admin, fresh_student):
    suffix = uuid.uuid4().hex[:10]
    track = admin.post(
        f"{API}/tracks",
        json={
            "title": f"TEST_content_prerequisite_{suffix}",
            "settings": {"enforce_prerequisites": True},
        },
    ).json()
    track_id = track["id"]
    target = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": "Reading prerequisite",
            "status": "published",
        },
    ).json()
    typed_dependent = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": "Typed dependent",
            "status": "published",
        },
    ).json()
    legacy_dependent = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": "Legacy dependent",
            "status": "published",
        },
    ).json()
    try:
        typed_relation = admin.post(
            f"{API}/relations",
            json={
                "node_id": typed_dependent["id"],
                "target_id": target["id"],
                "type": "prerequisite",
                "enforced": True,
                "prerequisite_kind": "content_completed",
            },
        )
        legacy_relation = admin.post(
            f"{API}/relations",
            json={
                "node_id": legacy_dependent["id"],
                "target_id": target["id"],
                "type": "prerequisite",
                "enforced": True,
            },
        )
        assert typed_relation.status_code == legacy_relation.status_code == 200
        assert admin.post(f"/api/tracks/{track_id}/publish", json={}).status_code == 200
        before = fresh_student.get(f"/api/progress/tracks/{track_id}").json()
        assert typed_dependent["id"] in before["locks"]
        assert legacy_dependent["id"] in before["locks"]
        assert (
            before["prerequisite_states"][typed_dependent["id"]][0]["prerequisite_kind"]
            == "content_completed"
        )
        assert (
            before["prerequisite_states"][legacy_dependent["id"]][0]["prerequisite_kind"]
            == "legacy"
        )

        completed = fresh_student.post(
            "/api/progress",
            json={
                "node_id": target["id"],
                "status": "completed",
            },
        )
        assert completed.status_code == 200, completed.text
        after = fresh_student.get(f"/api/progress/tracks/{track_id}").json()
        assert typed_dependent["id"] not in after["locks"]
        assert legacy_dependent["id"] not in after["locks"]
    finally:
        admin.delete(f"/api/tracks/{track_id}")


def test_combined_reading_and_quiz_prerequisites_require_both(admin, fresh_student):
    quiz = _create_typed_quiz(admin, question_count=10)
    track_id = quiz["track_id"]
    reading = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": f"Reading prerequisite {uuid.uuid4().hex[:8]}",
            "status": "published",
        },
    )
    assert reading.status_code == 200, reading.text
    reading_id = reading.json()["id"]
    dependent_id = quiz["dependent_id"]

    relations = [
        {
            "node_id": dependent_id,
            "target_id": reading_id,
            "type": "prerequisite",
            "enforced": True,
            "prerequisite_kind": "content_completed",
        },
    ]
    for relation in relations:
        response = admin.post(f"{API}/relations", json=relation)
        assert response.status_code == 200, response.text
    assert admin.post(f"{API}/tracks/{track_id}/publish", json={}).status_code == 200

    marked_read = fresh_student.post(
        f"{API}/progress",
        json={"node_id": reading_id, "status": "completed"},
    )
    assert marked_read.status_code == 200, marked_read.text
    progress = _progress(fresh_student, quiz)
    assert dependent_id in progress["locks"]
    assert {
        state["prerequisite_kind"]: state["status"]
        for state in progress["prerequisite_states"][dependent_id]
    } == {"content_completed": "satisfied", "quiz_passed": "pending"}

    result = _submit(fresh_student, quiz, correct_count=7)
    assert result.status_code == 200, result.text
    assert result.json()["passed"] is True
    assert dependent_id not in _progress(fresh_student, quiz)["locks"]


def test_non_prerequisite_relation_rejects_prerequisite_kind(admin):
    suffix = uuid.uuid4().hex[:10]
    track = admin.post("/api/tracks", json={"title": f"TEST_bad_relation_{suffix}"}).json()
    track_id = track["id"]
    first = admin.post(
        "/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "A"}
    ).json()
    second = admin.post(
        "/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "B"}
    ).json()
    try:
        response = admin.post(
            "/api/relations",
            json={
                "node_id": first["id"],
                "target_id": second["id"],
                "type": "related",
                "prerequisite_kind": "quiz_passed",
            },
        )
        assert response.status_code == 400
    finally:
        admin.delete(f"/api/tracks/{track_id}")
