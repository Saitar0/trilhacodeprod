"""HTTP journey across authenticated lesson, quiz, submission, review, and progress flows."""

import uuid

from bson import ObjectId

from database import db
from security import hash_password

API = "/api"
ORIGIN = {"Origin": "http://localhost:3000"}


def test_authenticated_student_journey_requires_track_scoped_review(
    admin, fresh_student, login, seeded_track, session_factory, event_loop,
):
    tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
    node = next(item for item in tree["nodes"] if item["kind"] == "topic")
    quiz = admin.post(f"{API}/blocks", json={
        "node_id": node["id"], "type": "quiz", "title": "Quiz Beta 6", "status": "draft",
        "data": {
            "activity_schema_version": 1,
            "prompt": "Qual alternativa é correta?",
            "options": [{"id": "wrong", "label": "Incorreta"}, {"id": "right", "label": "Correta"}],
            "correct_option_id": "right",
            "feedback": {"correct": "Boa resposta.", "incorrect": "Tente novamente."},
            "completion_policy": "responded", "max_attempts": 2,
        },
    })
    exercise = admin.post(f"{API}/blocks", json={
        "node_id": node["id"], "type": "exercise_open", "title": "Exercício Beta 6", "status": "draft",
        "data": {
            "prompt": "Explique sua solução em texto.", "allow_resubmit": True,
            "criteria": ["Explica o raciocínio", "Apresenta um exemplo"],
            "rubric": "RUBRICA INTERNA: avaliar clareza e exemplo.",
            "answer": "SOLUÇÃO RESERVADA: exemplo de referência.",
        },
    })
    assert quiz.status_code == exercise.status_code == 200
    published = admin.post(f"{API}/tracks/{seeded_track['id']}/publish", json={"publish_children": True})
    assert published.status_code == 200, published.text

    anonymous = session_factory().get(f"{API}/nodes/{node['id']}")
    assert anonymous.status_code == 401

    lesson = fresh_student.get(f"{API}/nodes/{node['id']}")
    assert lesson.status_code == 200, lesson.text
    blocks = {block["id"]: block for block in lesson.json()["blocks"]}
    public_quiz = blocks[quiz.json()["id"]]
    public_exercise = blocks[exercise.json()["id"]]
    assert public_quiz["activity"]["published_version_id"]
    assert "correct_option_id" not in public_quiz["activity"]
    assert "answer" not in public_quiz["data"]
    assert "rubric" not in public_exercise["data"]
    assert "criteria" not in public_exercise["data"]
    assert "answer" not in public_exercise["data"]
    assert "meta" not in public_exercise

    activity = public_quiz["activity"]
    key = uuid.uuid4().hex
    start = fresh_student.post(
        f"{API}/activities/{quiz.json()['id']}/attempts",
        json={"published_version_id": activity["published_version_id"]},
        headers={**ORIGIN, "Idempotency-Key": key},
    )
    assert start.status_code == 201, start.text
    attempt = start.json()
    submitted_quiz = fresh_student.post(
        f"{API}/activities/{quiz.json()['id']}/attempts/{attempt['id']}/submit",
        json={"selected_option_id": "right", "expected_revision": 0},
        headers={**ORIGIN, "Idempotency-Key": uuid.uuid4().hex},
    )
    assert submitted_quiz.status_code == 200, submitted_quiz.text
    assert submitted_quiz.json()["result"]["is_correct"] is True
    assert submitted_quiz.json()["activity"]["published_version_id"] == activity["published_version_id"]

    exercise_id = exercise.json()["id"]
    forged_completion = fresh_student.post(f"{API}/progress", json={
        "node_id": node["id"], "block_id": exercise_id, "status": "completed",
        "data": {"approved": True}, "operation_id": uuid.uuid4().hex,
    })
    assert forged_completion.status_code == 403

    submit_key = uuid.uuid4().hex
    payload = {"block_id": exercise_id, "answer": {"text": "Esta é uma resposta sintética com explicação."}}
    sent = fresh_student.post(f"{API}/submissions/submit", json=payload,
                              headers={"Idempotency-Key": submit_key})
    replay = fresh_student.post(f"{API}/submissions/submit", json=payload,
                                headers={"Idempotency-Key": submit_key})
    assert sent.status_code == replay.status_code == 200
    assert sent.json()["id"] == replay.json()["id"]
    assert sent.json()["status"] == "submitted"
    assert "grading_context" not in sent.json()
    submission_id = sent.json()["id"]

    progress = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
    assert progress["blocks"][exercise_id]["status"] == "in_progress"
    assert progress["blocks"][quiz.json()["id"]]["status"] == "completed"

    unscoped = login("editor@example.com")
    assert unscoped.get(f"{API}/submissions", params={"track_id": seeded_track["id"]}).status_code == 403
    assert unscoped.get(f"{API}/submissions/{submission_id}").status_code == 404
    assert unscoped.post(f"{API}/submissions/{submission_id}/claim").status_code == 404

    reviewer_email = f"beta6-reviewer-{uuid.uuid4().hex}@example.com"
    reviewer_id = ObjectId()
    event_loop.run_until_complete(db.users.insert_one({
        "_id": reviewer_id, "email": reviewer_email, "name": "Avaliadora Beta 6",
        "password_hash": hash_password("Test@1234"),
        "role": "editor", "email_verified": True, "is_active": True,
        "profile": {"bio": "", "goals": "", "preferences": {}},
    }))
    reviewer = login(reviewer_email)
    reviewer_id_text = reviewer.get(f"{API}/auth/me").json()["id"]
    event_loop.run_until_complete(db.learning_review_scopes.insert_one({
        "_id": f"{reviewer_id_text}:{seeded_track['id']}",
        "user_id": reviewer_id_text, "track_id": seeded_track["id"],
        "operations": ["submissions.read", "submissions.grade"], "state": "active",
        "source": "beta6_synthetic_test_setup",
    }))

    queue = reviewer.get(f"{API}/submissions", params={"track_id": seeded_track["id"]})
    assert queue.status_code == 200, queue.text
    assert any(item["id"] == submission_id for item in queue.json()["items"])
    detail = reviewer.get(f"{API}/submissions/{submission_id}")
    assert detail.status_code == 200, detail.text
    assert "RUBRICA INTERNA" in detail.json()["block"]["data"]["rubric"]
    assert "SOLUÇÃO RESERVADA" in detail.json()["block"]["data"]["answer"]

    claimed = reviewer.post(f"{API}/submissions/{submission_id}/claim")
    assert claimed.status_code == 200 and claimed.json()["status"] == "in_review"
    graded = reviewer.post(f"{API}/submissions/{submission_id}/grade", json={
        "result": "approved", "feedback": "Boa justificativa.", "criteria": [],
    })
    assert graded.status_code == 200, graded.text
    assert graded.json()["status"] == "graded"

    student_detail = fresh_student.get(f"{API}/submissions/{submission_id}")
    assert student_detail.status_code == 200
    student_result = student_detail.json()
    assert student_result["submission"]["grading"]["feedback"] == "Boa justificativa."
    assert "criteria" not in student_result["submission"]["grading"]
    assert "grading_context" not in student_result["submission"]
    assert "rubric" not in student_result["block"]["data"]
    assert "answer" not in student_result["block"]["data"]

    other_student = login("student@example.com")
    assert other_student.get(f"{API}/submissions/{submission_id}").status_code == 404
    final_progress = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
    assert final_progress["blocks"][exercise_id]["status"] == "completed"
    assert final_progress["blocks"][exercise_id]["data"]["review_state"] == "approved"

