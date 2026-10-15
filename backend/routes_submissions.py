from typing import List, Optional

from fastapi import APIRouter, Depends
from core import current_user, require, ser
from schemas.submissions import (
    AnswerIn,
    GradeIn,
    SubmissionDetailOut,
    SubmissionListOut,
    SubmissionOut,
)
from services.submissions import (
    claim_submission,
    get_submission as get_submission_service,
    grade_submission,
    list_submissions as list_submissions_service,
    my_submissions as my_submissions_service,
    save_draft as save_draft_service,
    submit_answer,
)

router = APIRouter(prefix="/api/submissions")


@router.get("/mine", response_model=list[SubmissionOut], response_model_exclude_unset=True)
async def my_submissions(node_id: Optional[str] = None, user: dict = Depends(current_user)):
    return ser(await my_submissions_service(node_id, user))


@router.put("/draft", response_model=SubmissionOut, response_model_exclude_unset=True)
async def save_draft(body: AnswerIn, user: dict = Depends(require("progress.write"))):
    return ser(await save_draft_service(body.block_id, body.answer, user))


@router.post("/submit", response_model=SubmissionOut, response_model_exclude_unset=True)
async def submit(body: AnswerIn, user: dict = Depends(require("progress.write"))):
    return ser(await submit_answer(body.block_id, body.answer, user))


@router.get("", response_model=SubmissionListOut, response_model_exclude_unset=True)
async def list_submissions(track_id: Optional[str] = None, node_id: Optional[str] = None, user_id: Optional[str] = None,
                           block_type: Optional[str] = None, status: Optional[str] = None, q: Optional[str] = None,
                           _: dict = Depends(require("submissions.grade"))):
    result = await list_submissions_service(track_id, node_id, user_id, block_type, status, q)
    return {"items": ser(result["items"]), "counts": result["counts"]}


@router.get("/{sub_id}", response_model=SubmissionDetailOut, response_model_exclude_unset=True)
async def get_submission(sub_id: str, user: dict = Depends(current_user)):
    result = await get_submission_service(sub_id, user)
    return {"submission": ser(result["submission"]), "block": ser(result["block"]) if result["block"] else None,
            "attempts": ser(result["attempts"])}


@router.post("/{sub_id}/claim", response_model=SubmissionOut, response_model_exclude_unset=True)
async def claim(sub_id: str, user: dict = Depends(require("submissions.grade"))):
    return ser(await claim_submission(sub_id, user))


@router.post("/{sub_id}/grade", response_model=SubmissionOut, response_model_exclude_unset=True)
async def grade(sub_id: str, body: GradeIn, user: dict = Depends(require("submissions.grade"))):
    return ser(await grade_submission(sub_id, body.model_dump(), user))
