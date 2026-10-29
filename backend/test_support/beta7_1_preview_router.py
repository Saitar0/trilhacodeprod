"""HTTP routes mounted only by the Beta 7.1 attested test server."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from routes_activities import ensure_cookie_origin
from schemas.beta7_1_preview import (
    ExerciseSubmissionIn,
    ProjectDeliveryIn,
    ProjectReviewIn,
    QuizAttemptIn,
)
from security import current_user
from services import beta7_1_preview as preview

router = APIRouter(prefix="/api/beta7-1/preview", tags=["beta7-1-isolated-preview"])


@router.get("/batches/{batch_id}")
async def get_phase(batch_id: str, user: dict = Depends(current_user)):
    return await preview.phase_tree(batch_id, user)


@router.get("/batches/{batch_id}/units/{unit_id}")
async def get_unit(batch_id: str, unit_id: str, user: dict = Depends(current_user)):
    await preview.require_preview(batch_id, user)
    return preview.public_unit(await preview.unit_for(batch_id, unit_id))


@router.post("/batches/{batch_id}/units/{unit_id}/quizzes/{question_id}/attempts")
async def submit_quiz_attempt(
    request: Request,
    batch_id: str,
    unit_id: str,
    question_id: str,
    body: QuizAttemptIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(current_user),
):
    ensure_cookie_origin(request)
    return await preview.submit_quiz_attempt(
        batch_id, unit_id, question_id, body.selected_option_id, body.source_sha256,
        idempotency_key, user,
    )


@router.post("/batches/{batch_id}/units/{unit_id}/exercises/{exercise_id}/submissions")
async def submit_exercise(
    request: Request,
    batch_id: str,
    unit_id: str,
    exercise_id: str,
    body: ExerciseSubmissionIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(current_user),
):
    ensure_cookie_origin(request)
    return await preview.submit_exercise(
        batch_id, unit_id, exercise_id, body.answer_text, body.source_sha256, body.unit_source_sha256,
        idempotency_key, user,
    )


@router.get("/batches/{batch_id}/submissions/mine")
async def list_my_submissions(
    batch_id: str, unit_id: str | None = None, user: dict = Depends(current_user),
):
    exercises = await preview.my_exercise_submissions(batch_id, unit_id, user)
    projects = await preview.my_project_submissions(batch_id, user)
    return {"exercises": exercises, "projects": projects}


@router.get("/batches/{batch_id}/progress")
async def get_progress(batch_id: str, user: dict = Depends(current_user)):
    return await preview.progress_view(batch_id, user)


@router.get("/batches/{batch_id}/project")
async def get_project(batch_id: str, user: dict = Depends(current_user)):
    return await preview.public_project(batch_id, user)


@router.get("/batches/{batch_id}/project/submissions/mine")
async def list_my_project_submissions(batch_id: str, user: dict = Depends(current_user)):
    return await preview.my_project_submissions(batch_id, user)


@router.post("/batches/{batch_id}/project/submissions")
async def submit_project(
    request: Request,
    batch_id: str,
    body: ProjectDeliveryIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(current_user),
):
    ensure_cookie_origin(request)
    return await preview.submit_project(
        batch_id, body.delivery_text, body.source_sha256, idempotency_key, user,
    )


@router.get("/batches/{batch_id}/project/restricted")
async def get_restricted_project(batch_id: str, user: dict = Depends(current_user)):
    return await preview.restricted_project(batch_id, user)


@router.get("/batches/{batch_id}/project/review-queue")
async def get_project_review_queue(batch_id: str, user: dict = Depends(current_user)):
    return await preview.reviewer_project_queue(batch_id, user)


@router.get("/batches/{batch_id}/project/submissions/{submission_id}")
async def get_project_submission(
    batch_id: str, submission_id: str, user: dict = Depends(current_user),
):
    return await preview.project_submission_detail(batch_id, submission_id, user)


@router.post("/batches/{batch_id}/project/submissions/{submission_id}/review")
async def review_project_submission(
    request: Request,
    batch_id: str,
    submission_id: str,
    body: ProjectReviewIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(current_user),
):
    ensure_cookie_origin(request)
    if idempotency_key is None:
        raise HTTPException(status_code=422, detail="Idempotency-Key obrigatória")
    return await preview.grade_project_submission(
        batch_id, submission_id, user=user, expected_revision=body.expected_revision,
        operation_key=idempotency_key, outcome=body.outcome, feedback=body.feedback,
    )
