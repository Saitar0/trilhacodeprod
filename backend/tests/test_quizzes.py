import asyncio
import importlib
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import pytest
from pymongo.errors import PyMongoError

from database import client as mongo_client
from database import db
from schemas.quizzes import QuizAttemptOut
from server import app
from settings import settings

API = "/api"


@pytest.fixture(autouse=True)
def allow_repeated_admin_quiz_setup_in_tests(monkeypatch):
    # The integration suite publishes many fixture quizzes under one shared
    # admin identity. Individual rate-limit tests set an explicit low value.
    monkeypatch.setattr(settings, "quiz_publish_limit_per_minute", 1000)


def _create_quiz(admin, question_count: int = 2) -> dict:
    suffix = uuid.uuid4().hex[:10]
    track_response = admin.post(f"{API}/tracks", json={"title": f"TEST_quiz_{suffix}"})
    assert track_response.status_code == 200, track_response.text
    track_id = track_response.json()["id"]
    node_response = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track_id,
            "kind": "topic",
            "title": f"Quiz {suffix}",
            "status": "published",
            "meta": {"import_ref": f"test-{suffix}"},
        },
    )
    assert node_response.status_code == 200, node_response.text
    quiz_id = node_response.json()["id"]
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
                    "options": [f"Correct {index + 1}", f"Wrong {index + 1}"],
                    "correct_index": 0,
                    "explanation": f"Private explanation {index + 1}",
                },
                "status": "published",
            },
        )
        assert response.status_code == 200, response.text
        blocks.append(response.json())
    published_track = admin.post(f"{API}/tracks/{track_id}/publish", json={})
    assert published_track.status_code == 200, published_track.text
    publication = admin.post(f"{API}/admin/quizzes/{quiz_id}/versions")
    assert publication.status_code == 200, publication.text
    return {
        "track_id": track_id,
        "quiz_id": quiz_id,
        "version_id": publication.json()["version_id"],
        "blocks": blocks,
    }


def _answers(quiz: dict, choices: list[int]) -> list[dict]:
    return [
        {
            "question_id": quiz["blocks"][index]["id"],
            "option_id": f"option-{choice + 1}",
        }
        for index, choice in enumerate(choices)
    ]


def _submit(session, quiz: dict, answers: list[dict], key: str | None = None, **extra):
    payload = {"version_id": quiz["version_id"], "answers": answers, **extra}
    return session.post(
        f"{API}/quizzes/{quiz['quiz_id']}/attempts",
        json=payload,
        headers={"Idempotency-Key": key or str(uuid.uuid4())},
    )


def test_public_quiz_and_pre_reveal_responses_never_include_answer_key(admin, fresh_student):
    quiz = _create_quiz(admin)
    public = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert public.status_code == 200, public.text
    payload = public.json()
    assert payload["attempts_remaining"] == 3
    assert payload["curriculum_ref"].startswith("test-")
    assert [item["order"] for item in payload["questions"]] == [0, 1]
    assert "correct_index" not in str(payload)
    assert "correct_option_id" not in str(payload)
    assert "explanation" not in str(payload)
    assert "content_hash" not in str(payload)

    result = _submit(fresh_student, quiz, _answers(quiz, [0, 0]))
    assert result.status_code == 200, result.text
    result_payload = result.json()
    assert result_payload["passed"] is True
    assert result_payload["attempts_remaining"] == 2
    assert result_payload["review_available"] is False
    assert "correct_answers" not in result_payload
    assert "correct_option_id" not in str(result_payload)
    assert "explanation" not in str(result_payload)

    history = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert history.status_code == 200, history.text
    assert len(history.json()["items"]) == 1
    assert all("answers" not in item for item in history.json()["items"])
    assert all("correct_index" not in item for item in history.json()["items"])


def test_recovery_confirms_exact_submission_without_consuming_an_attempt(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    key = str(uuid.uuid4())
    submitted = _submit(fresh_student, quiz, _answers(quiz, [0]), key=key)
    assert submitted.status_code == 200, submitted.text
    original = submitted.json()

    recovery_payload = {"version_id": quiz["version_id"], "idempotency_key": key}
    first = fresh_student.post(f"{API}/quizzes/{quiz['quiz_id']}/recovery", json=recovery_payload)
    repeated = fresh_student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/recovery", json=recovery_payload
    )

    assert first.status_code == repeated.status_code == 200
    assert first.json() == repeated.json()
    assert first.json()["state"] == "confirmed"
    assert first.json()["attempt"]["attempt_id"] == original["attempt_id"]
    assert first.json()["attempts_used"] == 1
    assert first.json()["attempts_remaining"] == 2
    assert first.json()["attempt"]["review_available"] is False
    assert "answers" not in str(first.json())
    assert "correct_option_id" not in str(first.json())
    assert "explanation" not in str(first.json())
    assert fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}").json()["attempts_used"] == 1


def test_recovery_without_local_key_returns_only_latest_authoritative_result(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    first = _submit(fresh_student, quiz, _answers(quiz, [0]), key=str(uuid.uuid4())).json()
    latest = _submit(fresh_student, quiz, _answers(quiz, [1]), key=str(uuid.uuid4())).json()

    recovered = fresh_student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/recovery", json={"version_id": quiz["version_id"]}
    )

    assert recovered.status_code == 200
    assert recovered.json()["state"] == "latest_confirmed"
    assert recovered.json()["attempt"]["attempt_id"] == latest["attempt_id"]
    assert recovered.json()["attempt"]["attempt_id"] != first["attempt_id"]
    assert recovered.json()["attempts_used"] == 2
    assert recovered.json()["may_still_be_processing"] is False
    assert "answers" not in str(recovered.json())


def test_recovery_reports_unknown_for_unmatched_or_uncommitted_intent(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    key = str(uuid.uuid4())
    payload = {"version_id": quiz["version_id"], "idempotency_key": key}

    before = fresh_student.post(f"{API}/quizzes/{quiz['quiz_id']}/recovery", json=payload)
    assert before.status_code == 200
    assert before.json() == {
        "state": "unknown",
        "quiz_id": quiz["quiz_id"],
        "version_id": quiz["version_id"],
        "attempts_used": 0,
        "attempts_remaining": 3,
        "review_available": False,
        "attempt": None,
        "may_still_be_processing": True,
    }
    assert _submit(fresh_student, quiz, _answers(quiz, [0]), key=key).status_code == 200
    after = fresh_student.post(f"{API}/quizzes/{quiz['quiz_id']}/recovery", json=payload)
    assert after.status_code == 200
    assert after.json()["state"] == "confirmed"
    assert after.json()["attempts_used"] == 1


def test_recovery_is_scoped_to_authenticated_user_and_quiz_version(admin, fresh_student, login):
    quiz = _create_quiz(admin, question_count=1)
    submitted = _submit(fresh_student, quiz, _answers(quiz, [0]), key=str(uuid.uuid4()))
    assert submitted.status_code == 200
    other_student = login("student@example.com")

    hidden = other_student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/recovery",
        json={"version_id": quiz["version_id"]},
    )
    unknown_version = fresh_student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/recovery",
        json={"version_id": "000000000000000000000000"},
    )
    malformed = fresh_student.post(
        f"{API}/quizzes/{quiz['quiz_id']}/recovery", json={"version_id": "not-a-version"}
    )

    assert hidden.status_code == 200
    assert hidden.json()["state"] == "unknown"
    assert hidden.json()["attempt"] is None
    assert hidden.json()["attempts_used"] == 0
    assert unknown_version.status_code == 404
    assert malformed.status_code == 422


def test_request_logs_and_openapi_do_not_publish_answer_material(admin, fresh_student, caplog):
    quiz = _create_quiz(admin, question_count=1)
    response = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert response.status_code == 200
    assert "Private explanation 1" not in caplog.text
    assert "correct_index" not in caplog.text

    properties = app.openapi()["components"]["schemas"]["QuizPublicOut"]["properties"]
    assert not {"correct_index", "correct_option_id", "explanation", "content_hash"} & set(
        properties
    )


def test_three_attempts_preserve_history_best_score_and_gate_review(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=2)
    results = [
        _submit(fresh_student, quiz, _answers(quiz, [0, 1])),
        _submit(fresh_student, quiz, _answers(quiz, [0, 0])),
        _submit(fresh_student, quiz, []),
    ]
    assert [response.status_code for response in results] == [200, 200, 200]
    first, second, third = [response.json() for response in results]
    assert [first["attempt_number"], second["attempt_number"], third["attempt_number"]] == [1, 2, 3]
    assert [
        first["attempts_remaining"],
        second["attempts_remaining"],
        third["attempts_remaining"],
    ] == [2, 1, 0]
    assert first["passed"] is False
    assert second["passed"] is True
    assert third["passed"] is False
    assert third["best_score_percent"] == 100
    assert third["review_available"] is True

    rejected = _submit(fresh_student, quiz, _answers(quiz, [0, 0]))
    assert rejected.status_code == 409

    history = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert history.status_code == 200
    assert history.json()["total"] == 3
    assert {item["attempt_number"] for item in history.json()["items"]} == {1, 2, 3}
    history_page = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts?limit=2&skip=1")
    assert history_page.status_code == 200
    assert history_page.json()["total"] == 3
    assert len(history_page.json()["items"]) == 2
    assert "correct_option_id" not in str(history.json())
    assert "explanation" not in str(history.json())

    review = fresh_student.get(
        f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    )
    assert review.status_code == 200, review.text
    questions = review.json()["questions"]
    assert [question["order"] for question in questions] == [0, 1]
    assert all(question["options"][0]["correct"] for question in questions)
    assert [question["explanation"] for question in questions] == [
        "Private explanation 1",
        "Private explanation 2",
    ]


def test_review_is_unavailable_until_the_third_valid_attempt(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    for _ in range(2):
        response = _submit(fresh_student, quiz, _answers(quiz, [0]))
        assert response.status_code == 200
        assert response.json()["passed"] is True
        assert response.json()["review_available"] is False
    review = fresh_student.get(
        f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    )
    assert review.status_code == 403
    public = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}").json()
    assert public["attempts_remaining"] == 1
    assert public["passed"] is True
    assert public["review_available"] is False


def test_invalid_and_client_supplied_grading_data_do_not_consume_attempts(admin, fresh_student):
    quiz = _create_quiz(admin)
    unknown = _submit(
        fresh_student,
        quiz,
        [{"question_id": "000000000000000000000000", "option_id": "option-1"}],
    )
    duplicate = _submit(
        fresh_student,
        quiz,
        [
            {"question_id": quiz["blocks"][0]["id"], "option_id": "option-1"},
            {"question_id": quiz["blocks"][0]["id"], "option_id": "option-2"},
        ],
    )
    invalid_option = _submit(
        fresh_student,
        quiz,
        [{"question_id": quiz["blocks"][0]["id"], "option_id": "not-an-option"}],
    )
    client_grade = _submit(
        fresh_student, quiz, _answers(quiz, [0, 0]), score_percent=100, passed=True
    )
    forged_identity = _submit(fresh_student, quiz, _answers(quiz, [0, 0]), user_id="another-user")
    assert [unknown.status_code, duplicate.status_code, invalid_option.status_code] == [
        422,
        422,
        422,
    ]
    assert client_grade.status_code == 422
    assert forged_identity.status_code == 422
    public = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert public.json()["attempts_used"] == 0


def test_idempotency_returns_prior_result_and_rejects_changed_payload(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    key = str(uuid.uuid4())
    answers = _answers(quiz, [0])
    first = _submit(fresh_student, quiz, answers, key)
    retry = _submit(fresh_student, quiz, answers, key)
    changed = _submit(fresh_student, quiz, _answers(quiz, [1]), key)
    assert first.status_code == retry.status_code == 200
    assert first.json() == retry.json()
    assert changed.status_code == 409
    assert fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}").json()["attempts_used"] == 1


def test_attempts_are_isolated_per_user_and_history_cannot_be_read_by_another(
    admin, fresh_student, login
):
    quiz = _create_quiz(admin, question_count=1)
    first = _submit(fresh_student, quiz, _answers(quiz, [0]))
    assert first.status_code == 200
    other = login("student@example.com")
    public = other.get(f"{API}/quizzes/{quiz['quiz_id']}")
    history = other.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert public.status_code == history.status_code == 200
    assert public.json()["attempts_used"] == 0
    assert history.json()["total"] == 0


def test_quiz_endpoints_require_authentication_and_staff_publication_permission(
    admin, async_client, fresh_student, event_loop
):
    quiz = _create_quiz(admin, question_count=1)
    response = event_loop.run_until_complete(async_client.get(f"{API}/quizzes/{quiz['quiz_id']}"))
    assert response.status_code == 401
    denied = fresh_student.post(f"{API}/admin/quizzes/{quiz['quiz_id']}/versions")
    assert denied.status_code == 403


def test_private_quiz_cannot_be_accessed_by_student(admin, fresh_student):
    suffix = uuid.uuid4().hex[:10]
    track = admin.post(
        f"{API}/tracks",
        json={"title": f"TEST_private_quiz_{suffix}", "visibility": "private"},
    ).json()
    node = admin.post(
        f"{API}/nodes",
        json={
            "track_id": track["id"],
            "kind": "topic",
            "title": "Private quiz",
            "status": "published",
        },
    ).json()
    block = admin.post(
        f"{API}/blocks",
        json={
            "node_id": node["id"],
            "type": "quiz",
            "data": {"question": "Q", "options": ["A", "B"], "correct_index": 0},
            "status": "published",
        },
    )
    assert block.status_code == 200
    admin.post(f"{API}/tracks/{track['id']}/publish", json={})
    publication = admin.post(f"{API}/admin/quizzes/{node['id']}/versions")
    assert publication.status_code == 200, publication.text
    response = fresh_student.get(f"{API}/quizzes/{node['id']}")
    assert response.status_code == 404


def test_empty_quiz_cannot_be_published(admin):
    suffix = uuid.uuid4().hex[:10]
    track = admin.post(f"{API}/tracks", json={"title": f"TEST_empty_quiz_{suffix}"}).json()
    node = admin.post(
        f"{API}/nodes",
        json={"track_id": track["id"], "kind": "topic", "title": "Empty quiz"},
    ).json()
    admin.post(f"{API}/tracks/{track['id']}/publish", json={})
    response = admin.post(f"{API}/admin/quizzes/{node['id']}/versions")
    assert response.status_code == 422


def test_review_unlock_is_scoped_to_the_authenticated_user(admin, student, login):
    quiz = _create_quiz(admin, question_count=1)
    for _ in range(3):
        response = _submit(student, quiz, _answers(quiz, [0]))
        assert response.status_code == 200
    another_user = login("editor@example.com")
    history = another_user.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    review = another_user.get(
        f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    )
    assert history.status_code == 200
    assert history.json()["total"] == 0
    assert review.status_code == 403


def test_history_is_persisted_across_independent_authenticated_clients(admin, student, login):
    quiz = _create_quiz(admin, question_count=1)
    submitted = _submit(student, quiz, _answers(quiz, [0]))
    assert submitted.status_code == 200

    new_client = login("student@example.com")
    history = new_client.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["attempt_id"] == submitted.json()["attempt_id"]


def test_new_version_resets_allowance_and_preserves_old_history_and_retries(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    key = str(uuid.uuid4())
    answers = _answers(quiz, [0])
    first = _submit(fresh_student, quiz, answers, key)
    assert first.status_code == 200

    block_id = quiz["blocks"][0]["id"]
    updated = admin.put(
        f"{API}/blocks/{block_id}",
        json={
            "data": {
                "question": "Changed prompt",
                "options": ["Correct", "Wrong"],
                "correct_index": 1,
                "explanation": "Changed explanation",
            }
        },
    )
    assert updated.status_code == 200, updated.text
    published = admin.post(f"{API}/admin/quizzes/{quiz['quiz_id']}/versions")
    assert published.status_code == 200, published.text
    new_version_id = published.json()["version_id"]
    assert new_version_id != quiz["version_id"]

    retry = _submit(fresh_student, quiz, answers, key)
    assert retry.status_code == 200
    assert retry.json() == first.json()
    stale_new = _submit(fresh_student, quiz, answers)
    assert stale_new.status_code == 409

    current = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert current.status_code == 200
    assert current.json()["version_id"] == new_version_id
    assert current.json()["attempts_used"] == 0
    history = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert history.json()["total"] == 1
    old_review = fresh_student.get(
        f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    )
    assert old_review.status_code == 403


def test_simultaneous_submissions_cannot_exceed_three_attempts(
    admin, fresh_student, async_client, event_loop
):
    quiz = _create_quiz(admin, question_count=1)
    async_client.cookies.update(fresh_student.cookies)
    answers = _answers(quiz, [0])

    async def send(index: int):
        return await async_client.post(
            f"{API}/quizzes/{quiz['quiz_id']}/attempts",
            json={"version_id": quiz["version_id"], "answers": answers},
            headers={"Idempotency-Key": f"parallel-{index}-{uuid.uuid4()}"},
        )

    responses = event_loop.run_until_complete(asyncio.gather(*(send(i) for i in range(4))))
    assert sorted(response.status_code for response in responses) == [200, 200, 200, 409]
    rows = event_loop.run_until_complete(
        db.quiz_progress.find(
            {"quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]}
        ).to_list(10)
    )
    assert len(rows) == 1
    progress = rows[0]
    assert progress["attempt_count"] == 3
    assert sorted(item["attempt_number"] for item in progress["attempts"]) == [1, 2, 3]


def test_simultaneous_retry_with_same_idempotency_key_creates_one_attempt(
    admin, fresh_student, async_client, event_loop
):
    quiz = _create_quiz(admin, question_count=1)
    async_client.cookies.update(fresh_student.cookies)
    body = {"version_id": quiz["version_id"], "answers": _answers(quiz, [0])}
    headers = {"Idempotency-Key": f"same-request-{uuid.uuid4()}"}

    async def send():
        return await async_client.post(
            f"{API}/quizzes/{quiz['quiz_id']}/attempts", json=body, headers=headers
        )

    first, second = event_loop.run_until_complete(asyncio.gather(send(), send()))
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    progress_rows = event_loop.run_until_complete(
        db.quiz_progress.find(
            {"quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]}
        ).to_list(10)
    )
    assert len(progress_rows) == 1
    assert progress_rows[0]["attempt_count"] == 1
    assert len(progress_rows[0]["attempts"]) == 1


@pytest.mark.parametrize("submission_count", [2, 3])
def test_two_and_three_concurrent_attempts_receive_distinct_numbers(
    submission_count, admin, fresh_student, async_client, event_loop
):
    quiz = _create_quiz(admin, question_count=1)
    async_client.cookies.update(fresh_student.cookies)
    answers = _answers(quiz, [0])

    async def send(index: int):
        return await async_client.post(
            f"{API}/quizzes/{quiz['quiz_id']}/attempts",
            json={"version_id": quiz["version_id"], "answers": answers},
            headers={"Idempotency-Key": f"parallel-count-{index}-{uuid.uuid4()}"},
        )

    responses = event_loop.run_until_complete(
        asyncio.gather(*(send(index) for index in range(submission_count)))
    )
    assert all(response.status_code == 200 for response in responses)
    assert {response.json()["attempt_number"] for response in responses} == set(
        range(1, submission_count + 1)
    )
    progress = event_loop.run_until_complete(
        db.quiz_progress.find_one({"quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]})
    )
    assert progress["attempt_count"] == submission_count
    assert sorted(item["attempt_number"] for item in progress["attempts"]) == list(
        range(1, submission_count + 1)
    )


def test_unique_persistence_indexes_exist(event_loop):
    async def inspect():
        versions = await (await db.quiz_versions.list_indexes()).to_list(100)
        progress = await (await db.quiz_progress.list_indexes()).to_list(100)
        return versions, progress

    versions, progress = event_loop.run_until_complete(inspect())
    assert any(
        index.get("unique") and index["key"] == {"quiz_id": 1, "content_hash": 1}
        for index in versions
    )
    assert any(
        index.get("unique") and index["key"] == {"user_id": 1, "quiz_id": 1, "version_id": 1}
        for index in progress
    )


def test_quiz_rate_limits_are_user_scoped_and_idempotent_replays_are_free(
    admin, fresh_student, event_loop, monkeypatch
):
    monkeypatch.setattr(settings, "quiz_attempt_limit_per_minute", 1)
    first_quiz = _create_quiz(admin, question_count=1)
    second_quiz = _create_quiz(admin, question_count=1)
    key = f"rate-limit-retry-{uuid.uuid4()}"
    answers = _answers(first_quiz, [0])

    first = _submit(fresh_student, first_quiz, answers, key)
    replay = _submit(fresh_student, first_quiz, answers, key)
    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()

    # A second client with a different network address cannot reset the user's
    # authenticated attempt budget.
    transport = httpx.ASGITransport(app=app, client=("203.0.113.70", 54321))
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    client.cookies.update(fresh_student.cookies)
    second_answers = _answers(second_quiz, [0])
    response = event_loop.run_until_complete(
        client.post(
            f"{API}/quizzes/{second_quiz['quiz_id']}/attempts",
            json={"version_id": second_quiz["version_id"], "answers": second_answers},
            headers={"Idempotency-Key": f"rate-limit-new-{uuid.uuid4()}"},
        )
    )
    event_loop.run_until_complete(client.aclose())
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert response.json()["error"]["code"] == "rate_limited"


def test_quiz_read_history_review_and_publish_limits_return_consistent_429(
    admin, fresh_student, monkeypatch
):
    quiz = _create_quiz(admin, question_count=1)
    monkeypatch.setattr(settings, "quiz_read_limit_per_minute", 1)
    monkeypatch.setattr(settings, "quiz_history_limit_per_minute", 1)
    monkeypatch.setattr(settings, "quiz_review_limit_per_minute", 1)
    monkeypatch.setattr(settings, "quiz_publish_limit_per_minute", 1)

    assert fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}").status_code == 200
    read_limited = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert read_limited.status_code == 429
    assert read_limited.json()["error"]["code"] == "rate_limited"

    assert fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts").status_code == 200
    history_limited = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}/attempts")
    assert history_limited.status_code == 429
    assert history_limited.headers["Retry-After"] == "60"

    review_path = f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    assert fresh_student.get(review_path).status_code == 403
    review_limited = fresh_student.get(review_path)
    assert review_limited.status_code == 429

    assert admin.post(f"{API}/admin/quizzes/{quiz['quiz_id']}/versions").status_code == 200
    publish_limited = admin.post(f"{API}/admin/quizzes/{quiz['quiz_id']}/versions")
    assert publish_limited.status_code == 429


def test_generic_progress_cannot_forge_authoritative_quiz_result(admin, fresh_student):
    quiz = _create_quiz(admin, question_count=1)
    response = fresh_student.post(
        f"{API}/progress",
        json={
            "node_id": quiz["quiz_id"],
            "status": "completed",
            "data": {"passed": True, "score_percent": 100, "correct_answers": 1},
        },
    )
    assert response.status_code == 200, response.text

    public = fresh_student.get(f"{API}/quizzes/{quiz['quiz_id']}")
    assert public.status_code == 200, public.text
    assert public.json()["passed"] is False
    assert public.json()["attempts_used"] == 0
    review = fresh_student.get(
        f"{API}/quizzes/{quiz['quiz_id']}/versions/{quiz['version_id']}/review"
    )
    assert review.status_code == 403


def test_quiz_migration_is_idempotent_and_preserves_index_definitions(event_loop):
    migration = importlib.import_module("migrations.0003_quiz_attempts")

    async def run():
        await migration.up()
        before_versions = await (await db.quiz_versions.list_indexes()).to_list(100)
        before_progress = await (await db.quiz_progress.list_indexes()).to_list(100)
        await migration.up()
        after_versions = await (await db.quiz_versions.list_indexes()).to_list(100)
        after_progress = await (await db.quiz_progress.list_indexes()).to_list(100)
        return before_versions, before_progress, after_versions, after_progress

    before_versions, before_progress, after_versions, after_progress = (
        event_loop.run_until_complete(run())
    )
    assert before_versions == after_versions
    assert before_progress == after_progress
    assert any(
        item.get("unique") and item["name"] == "one_quiz_content_version" for item in after_versions
    )
    assert any(
        item.get("unique") and item["name"] == "one_user_quiz_version_progress"
        for item in after_progress
    )


def test_quiz_migration_fails_safely_when_disposable_db_has_duplicate_keys(event_loop, monkeypatch):
    import indexes

    migration = importlib.import_module("migrations.0003_quiz_attempts")
    disposable_name = f"test_{uuid.uuid4().hex}"
    disposable_db = mongo_client.get_database(disposable_name)

    async def run():
        try:
            await disposable_db.quiz_versions.insert_many(
                [
                    {"quiz_id": "quiz-duplicate", "content_hash": "same"},
                    {"quiz_id": "quiz-duplicate", "content_hash": "same"},
                ]
            )
            monkeypatch.setattr(indexes, "db", disposable_db)
            with pytest.raises(PyMongoError):
                await migration.up()
            indexes_after = await (await disposable_db.quiz_versions.list_indexes()).to_list(100)
            assert not any(item["name"] == "one_quiz_content_version" for item in indexes_after)
        finally:
            await mongo_client.drop_database(disposable_name)

    event_loop.run_until_complete(run())


def test_mongo_test_server_version_and_topology_are_recorded(event_loop):
    async def inspect():
        build_info = await mongo_client.admin.command("buildInfo")
        hello = await mongo_client.admin.command("hello")
        return build_info["version"], hello

    version, hello = event_loop.run_until_complete(inspect())
    major = int(version.split(".", maxsplit=1)[0])
    topology = "replica set" if hello.get("setName") else "standalone"
    print(f"Disposable MongoDB: version={version}; topology={topology}")
    assert major >= 4


def test_failed_attempt_before_atomic_write_does_not_consume_attempt(
    admin, fresh_student, event_loop, monkeypatch
):
    import services.quizzes as quiz_service

    quiz = _create_quiz(admin, question_count=1)
    user = fresh_student.get(f"{API}/auth/me").json()
    key = f"prewrite-failure-{uuid.uuid4()}"
    answers = _answers(quiz, [0])
    real_db = quiz_service.db
    real_collection = real_db.quiz_progress

    class ProgressCollection:
        def __getattr__(self, name):
            return getattr(real_collection, name)

        async def find_one_and_update(self, query, update, **kwargs):
            if "$push" in update:
                raise TimeoutError("simulated failure before atomic write")
            return await real_collection.find_one_and_update(query, update, **kwargs)

    class DatabaseProxy:
        def __getattr__(self, name):
            return ProgressCollection() if name == "quiz_progress" else getattr(real_db, name)

    async def run_failure():
        with monkeypatch.context() as patch:
            patch.setattr(quiz_service, "db", DatabaseProxy())
            with pytest.raises(TimeoutError):
                await quiz_service.submit_quiz_attempt(
                    quiz["quiz_id"], quiz["version_id"], answers, key, user
                )
        row = await real_collection.find_one(
            {"user_id": user["id"], "quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]}
        )
        assert row is not None and row["attempt_count"] == 0
        return await quiz_service.submit_quiz_attempt(
            quiz["quiz_id"], quiz["version_id"], answers, key, user
        )

    recovered = event_loop.run_until_complete(run_failure())
    assert recovered["attempt_number"] == 1
    progress = event_loop.run_until_complete(
        db.quiz_progress.find_one(
            {"user_id": user["id"], "quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]}
        )
    )
    assert progress["attempt_count"] == 1


def test_persisted_attempt_retry_survives_service_process_restart(
    admin, fresh_student, event_loop, monkeypatch
):
    import services.quizzes as quiz_service

    quiz = _create_quiz(admin, question_count=1)
    user = fresh_student.get(f"{API}/auth/me").json()
    key = f"restart-retry-{uuid.uuid4()}"
    answers = _answers(quiz, [0])
    real_db = quiz_service.db
    real_collection = real_db.quiz_progress

    class ProgressCollection:
        failed = False

        def __getattr__(self, name):
            return getattr(real_collection, name)

        async def find_one_and_update(self, query, update, **kwargs):
            saved = await real_collection.find_one_and_update(query, update, **kwargs)
            if "$push" in update and not self.failed:
                self.failed = True
                raise TimeoutError("simulated response loss after committed write")
            return saved

    class DatabaseProxy:
        def __getattr__(self, name):
            return ProgressCollection() if name == "quiz_progress" else getattr(real_db, name)

    async def persist_then_lose_response():
        with monkeypatch.context() as patch:
            patch.setattr(quiz_service, "db", DatabaseProxy())
            with pytest.raises(TimeoutError):
                await quiz_service.submit_quiz_attempt(
                    quiz["quiz_id"], quiz["version_id"], answers, key, user
                )

    event_loop.run_until_complete(persist_then_lose_response())
    stored = event_loop.run_until_complete(
        real_collection.find_one(
            {"user_id": user["id"], "quiz_id": quiz["quiz_id"], "version_id": quiz["version_id"]}
        )
    )
    assert stored is not None and stored["attempt_count"] == 1
    expected = QuizAttemptOut.model_validate(
        quiz_service._result_payload(stored["attempts"][0])
    ).model_dump(mode="json")

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    backend_dir = Path(__file__).resolve().parents[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=backend_dir,
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        base_url = f"http://127.0.0.1:{port}"
        ready = False
        for _ in range(100):
            if process.poll() is not None:
                raise AssertionError(
                    f"Temporary API process exited with status {process.returncode}"
                )
            try:
                if httpx.get(f"{base_url}/health", timeout=0.2, trust_env=False).status_code == 200:
                    ready = True
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        assert ready, "Temporary API process did not become ready"
        response = httpx.post(
            f"{base_url}{API}/quizzes/{quiz['quiz_id']}/attempts",
            json={"version_id": quiz["version_id"], "answers": answers},
            headers={
                "Authorization": f"Bearer {fresh_student.cookies.get('access_token')}",
                "Idempotency-Key": key,
            },
            timeout=10,
            trust_env=False,
        )
        assert response.status_code == 200, response.text
        assert response.json() == expected
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
