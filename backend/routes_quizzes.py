"""Authenticated quiz delivery, attempts, history, and review endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query

from permissions import require
from schemas.quizzes import (
    QuizAttemptIn,
    QuizAttemptOut,
    QuizHistoryOut,
    QuizPublicOut,
    QuizRecoveryIn,
    QuizRecoveryOut,
    QuizReviewOut,
    QuizVersionPublishedOut,
)
from security import current_user
from services.quizzes import (
    get_public_quiz,
    get_quiz_history,
    get_quiz_recovery,
    get_quiz_review,
    publish_quiz_version,
    submit_quiz_attempt,
)

router = APIRouter(prefix="/api")


@router.get("/quizzes/{quiz_id}", response_model=QuizPublicOut)
async def read_quiz(quiz_id: str, user: dict = Depends(current_user)):
    return await get_public_quiz(quiz_id, user)


@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptOut)
async def submit_attempt(
    quiz_id: str,
    body: QuizAttemptIn,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=16, max_length=128)],
    user: dict = Depends(current_user),
):
    answers = [item.model_dump() for item in body.answers]
    return await submit_quiz_attempt(quiz_id, body.version_id, answers, idempotency_key, user)


@router.get("/quizzes/{quiz_id}/attempts", response_model=QuizHistoryOut)
async def read_quiz_history(
    quiz_id: str,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    skip: Annotated[int, Query(ge=0)] = 0,
    user: dict = Depends(current_user),
):
    return await get_quiz_history(quiz_id, user, limit=limit, skip=skip)


@router.post(
    "/quizzes/{quiz_id}/recovery",
    response_model=QuizRecoveryOut,
)
async def recover_quiz_submission(
    quiz_id: str,
    body: QuizRecoveryIn,
    user: dict = Depends(current_user),
):
    return await get_quiz_recovery(
        quiz_id, body.version_id, user, idempotency_key=body.idempotency_key
    )


@router.get("/quizzes/{quiz_id}/versions/{version_id}/review", response_model=QuizReviewOut)
async def read_quiz_review(quiz_id: str, version_id: str, user: dict = Depends(current_user)):
    return await get_quiz_review(quiz_id, version_id, user)


@router.post(
    "/admin/quizzes/{quiz_id}/versions",
    response_model=QuizVersionPublishedOut,
)
async def publish_quiz(quiz_id: str, user: dict = Depends(require("content.publish"))):
    return await publish_quiz_version(quiz_id, user)
