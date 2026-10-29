from __future__ import annotations

import pytest
from pydantic import ValidationError

from schemas.submissions import AnswerIn, GradeIn, SubmissionOut
from services.learning_scopes import scope_id
from services.nodes import _student_block
from services.submissions import _reviewer_block, _reviewer_submission, _student_submission


def test_student_assessment_projection_uses_closed_fields_and_removes_metadata():
    block = {
        "_id": "block-id", "node_id": "node-id", "track_id": "track-id", "type": "exercise_open",
        "title": "Prática", "status": "published", "order": 2, "meta": {"import_ref": "secret"},
        "data": {
            "prompt": "Enunciado público", "instructions": "Instruções públicas", "allow_resubmit": True,
            "criteria": ["Rubrica privada"], "rubric": "Rubrica privada", "answer": "Gabarito privado",
            "internal_metadata": {"correct": "segredo"},
        },
    }
    public = _student_block(block)
    assert public["data"] == {
        "prompt": "Enunciado público", "instructions": "Instruções públicas", "allow_resubmit": True,
    }
    assert "meta" not in public and "track_id" not in public


def test_student_submission_projection_hides_private_grading_and_system_fields():
    submission = {
        "_id": "submission-id", "user_id": "student-id", "answer": {"text": "Minha resposta"},
        "grading": {"result": "approved", "feedback": "Bem explicado", "score": 8,
                    "criteria": [{"criterion": "Rubrica privada", "comment": "interno"}],
                    "graded_by_name": "Instrutor", "graded_at": "2026-10-29"},
        "grading_context": {"answer": "solução privada"},
        "grading_history": [{"feedback": "interno"}],
        "answer_history": [{"grading": {"criteria": ["privado"]}}],
        "submission_operations": [{"fingerprint": "interno"}],
        "progress_projection_status": "complete", "status": "graded",
        "future_private_field": "must not cross a projection",
        "history": [{"status": "graded", "by": "private-user-id", "by_name": "Instrutor", "at": "2026-10-29"}],
    }
    public = _student_submission(submission)
    assert public["id"] == "submission-id"
    assert public["grading"] == {
        "result": "approved", "feedback": "Bem explicado", "score": 8,
        "graded_by_name": "Instrutor", "graded_at": "2026-10-29",
    }
    assert not ({"grading_context", "grading_history", "answer_history", "submission_operations",
                 "progress_projection_status"} & set(public))
    assert "future_private_field" not in public
    assert public["history"] == [{"status": "graded", "by_name": "Instrutor", "at": "2026-10-29"}]


def test_student_projection_is_closed_to_future_internal_fields():
    public = _student_submission({
        "_id": "submission-id", "status": "submitted", "answer": {"text": "resposta"},
        "internal_token": "do not serialize", "debug": {"database": "private"},
    })
    assert public == {
        "status": "submitted", "answer": {"text": "resposta"}, "id": "submission-id",
    }


def test_reviewer_submission_projection_excludes_system_only_fields():
    projected = _reviewer_submission({
        "_id": "submission-id", "user_id": "student-id", "answer": {"text": "resposta"},
        "status": "graded", "grading": {
            "result": "approved", "feedback": "bom", "criteria": [], "graded_by": "staff-id",
            "graded_by_name": "Avaliador", "graded_at": "2026-10-29", "internal_secret": "omit",
        },
        "history": [{"status": "graded", "by": "staff-id", "by_name": "Avaliador", "at": "now",
                     "internal": "omit"}],
        "grading_context": {"answer": "restrita"}, "progress_projection_status": "pending",
    })
    assert projected["id"] == "submission-id"
    assert projected["grading"]["criteria"] == []
    assert "graded_by" not in projected["grading"]
    assert projected["history"] == [{"status": "graded", "by_name": "Avaliador", "at": "now"}]
    assert "grading_context" not in projected and "progress_projection_status" not in projected
    SubmissionOut.model_validate(projected)


def test_reviewer_block_projection_is_closed_to_unknown_metadata():
    projected = _reviewer_block({
        "_id": "block-id", "node_id": "node-id", "track_id": "track-id", "type": "exercise_open",
        "title": "Atividade", "status": "published", "debug": "omit",
        "data": {"prompt": "Enunciado", "rubric": "Critérios", "reference_answer": "Solução",
                 "metadata": {"private": "unknown"}},
    })
    assert projected["data"] == {
        "prompt": "Enunciado", "rubric": "Critérios", "reference_answer": "Solução",
    }
    assert "debug" not in projected


def test_submission_requests_reject_unknown_or_oversized_content():
    with pytest.raises(ValidationError):
        AnswerIn(block_id="block", answer={"text": "resposta", "correct": True})
    with pytest.raises(ValidationError):
        AnswerIn(block_id="block", answer={"text": "x" * 25_001})
    with pytest.raises(ValidationError):
        GradeIn(result="approved", feedback="ok", unexpected_solution="secret")


def test_review_scope_identity_is_bound_to_user_and_track():
    assert scope_id("user-a", "track-a") == "user-a:track-a"
    assert scope_id("user-a", "track-a") != scope_id("user-b", "track-a")
    assert scope_id("user-a", "track-a") != scope_id("user-a", "track-b")
