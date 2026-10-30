"""Assessment routes mounted only by an explicitly gated test application."""

from fastapi import APIRouter, Depends, Header, Query, Request

from curriculum_contract.beta7_2_assessment import AssessmentCommand
from routes_activities import ensure_cookie_origin
from schemas.beta7_2_assessment import ProjectAssessmentIn
from security import current_user
from services import beta7_2_assessment as assessment

router = APIRouter(prefix="/api/beta7-2/assessment/batches/{batch_id}", tags=["beta7-2-isolated-assessment"])


@router.get("/project/rubric")
async def get_project_rubric(
    batch_id: str,
    version: str | None = Query(default=None, min_length=1, max_length=128),
    user: dict = Depends(current_user),
):
    return await assessment.instructor_rubric(batch_id, user, version)


@router.post("/project/submissions/{submission_id}/assess")
async def assess_project_submission(
    request: Request,
    batch_id: str,
    submission_id: str,
    body: ProjectAssessmentIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(current_user),
):
    ensure_cookie_origin(request)
    if idempotency_key is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="Idempotency-Key obrigatória")
    command = AssessmentCommand(
        submission_id=submission_id,
        project_id="3.5",
        project_version=body.project_version,
        rubric_id=body.rubric_id,
        rubric_version=body.rubric_version,
        expected_revision=body.expected_revision,
        outcome=body.outcome,
        feedback=body.feedback,
        criteria=body.criteria,
    )
    return await assessment.assess_project(
        batch_id, submission_id, user=user, command=command, operation_key=idempotency_key,
    )


@router.get("/project/assessment-history/mine")
async def get_my_project_assessment_history(batch_id: str, user: dict = Depends(current_user)):
    return await assessment.learner_assessment_history(batch_id, user)
