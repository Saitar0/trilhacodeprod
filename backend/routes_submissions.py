import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core import PERMISSIONS, current_user, db, is_staff, now, oid, require, ser
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from learning import assert_unlocked

router = APIRouter(prefix="/api/submissions")

OPEN_STATUSES = ["draft", "submitted", "returned"]
STAFF_STATUSES = ["submitted", "in_review", "graded", "returned"]


class AnswerIn(BaseModel):
    block_id: str
    answer: dict = {}


class CriterionGrade(BaseModel):
    criterion: str
    met: Optional[bool] = None
    comment: str = ""
    score: Optional[float] = None


class GradeIn(BaseModel):
    result: str
    feedback: str = ""
    criteria: List[CriterionGrade] = []
    score: Optional[float] = None


async def _submittable_block(block_id: str, staff_ok: bool = False):
    block = await db.content_blocks.find_one({"_id": oid(block_id)})
    if not block:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    if block.get("status") != "published" and not staff_ok:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    btype = await db.block_types.find_one({"key": block["type"]})
    if not btype or "submission" not in (btype.get("capabilities") or []):
        raise HTTPException(status_code=400, detail="Este bloco não aceita respostas")
    node = await db.nodes.find_one({"_id": oid(block["node_id"])})
    return block, node


async def _current(user_id: str, block_id: str):
    return await db.submissions.find_one({"user_id": user_id, "block_id": block_id}, sort=[("attempt", -1)])


def _hist(status, user):
    return {"status": status, "at": now(), "by": user["id"], "by_name": user.get("name", "")}


async def _open_attempt(user, block, node):
    cur = await _current(user["id"], str(block["_id"]))
    if cur and cur["status"] in OPEN_STATUSES:
        return cur
    if cur and cur["status"] == "in_review":
        raise HTTPException(status_code=409, detail="Sua resposta está em correção e não pode ser editada")
    if cur and cur["status"] == "graded":
        approved = (cur.get("grading") or {}).get("result") == "approved"
        if approved or not block.get("data", {}).get("allow_resubmit", True):
            raise HTTPException(status_code=409, detail="Este exercício já foi corrigido e não aceita nova tentativa")
    doc = {"user_id": user["id"], "user_name": user.get("name", ""), "track_id": block["track_id"], "node_id": block["node_id"],
           "node_title": node["title"] if node else "", "block_id": str(block["_id"]), "block_type": block["type"],
           "block_title": block.get("title", ""), "attempt": (cur["attempt"] + 1) if cur else 1, "status": "draft",
           "answer": {}, "grading": None, "history": [_hist("draft", user)], "created_at": now(), "updated_at": now(),
           "submitted_at": None}
    try:
        res = await db.submissions.insert_one(doc)
    except DuplicateKeyError:  # concurrent request created this attempt first
        return await _current(user["id"], str(block["_id"]))
    doc["_id"] = res.inserted_id
    return doc


@router.get("/mine")
async def my_submissions(node_id: Optional[str] = None, user: dict = Depends(current_user)):
    q = {"user_id": user["id"], "orphaned": {"$ne": True}}
    if node_id:
        q["node_id"] = node_id
    return ser(await db.submissions.find(q).sort([("block_id", 1), ("attempt", -1)]).to_list(1000))


@router.put("/draft")
async def save_draft(body: AnswerIn, user: dict = Depends(require("progress.write"))):
    block, node = await _submittable_block(body.block_id, is_staff(user))
    await assert_unlocked(node, user)
    sub = await _open_attempt(user, block, node)
    res = await db.submissions.update_one({"_id": sub["_id"], "status": {"$in": OPEN_STATUSES}},
                                          {"$set": {"answer": body.answer, "updated_at": now()}})
    if not res.matched_count:
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    return ser(await db.submissions.find_one({"_id": sub["_id"]}))


@router.post("/submit")
async def submit(body: AnswerIn, user: dict = Depends(require("progress.write"))):
    block, node = await _submittable_block(body.block_id, is_staff(user))
    await assert_unlocked(node, user)
    if not any(str(v).strip() for v in body.answer.values()):
        raise HTTPException(status_code=400, detail="A resposta está vazia")
    sub = await _open_attempt(user, block, node)
    res = await db.submissions.update_one({"_id": sub["_id"], "status": {"$in": OPEN_STATUSES}}, {
        "$set": {"answer": body.answer, "status": "submitted", "submitted_at": now(), "updated_at": now()},
        "$push": {"history": _hist("submitted", user)}})
    if not res.matched_count:
        raise HTTPException(status_code=409, detail="Sua resposta entrou em correção e não pode mais ser editada")
    await db.learning_events.insert_one({"user_id": user["id"], "track_id": block["track_id"], "node_id": block["node_id"],
                                         "block_id": body.block_id, "type": "submission:submitted", "data": {}, "at": now()})
    await db.progress.update_one({"user_id": user["id"], "node_id": block["node_id"], "block_id": body.block_id},
                                 {"$set": {"status": "in_progress", "track_id": block["track_id"], "scope": "block",
                                           "updated_at": now()}, "$setOnInsert": {"started_at": now()}}, upsert=True)
    return ser(await db.submissions.find_one({"_id": sub["_id"]}))


@router.get("")
async def list_submissions(track_id: Optional[str] = None, node_id: Optional[str] = None, user_id: Optional[str] = None,
                           block_type: Optional[str] = None, status: Optional[str] = None, q: Optional[str] = None,
                           _: dict = Depends(require("submissions.grade"))):
    query = {"status": {"$in": STAFF_STATUSES}}
    for k, v in (("track_id", track_id), ("node_id", node_id), ("user_id", user_id), ("block_type", block_type)):
        if v:
            query[k] = v
    base = {k: v for k, v in query.items() if k != "status"}
    if status:
        query["status"] = status
    if q:
        query["$or"] = [{"user_name": {"$regex": re.escape(q), "$options": "i"}}, {"node_title": {"$regex": re.escape(q), "$options": "i"}}]
    items = await db.submissions.find(query, {"history": 0}).sort("submitted_at", 1).to_list(500)
    counts = await db.submissions.aggregate([{"$match": base}, {"$group": {"_id": "$status", "n": {"$sum": 1}}}]).to_list(20)
    return {"items": ser(items), "counts": {c["_id"]: c["n"] for c in counts}}


@router.get("/{sub_id}")
async def get_submission(sub_id: str, user: dict = Depends(current_user)):
    sub = await db.submissions.find_one({"_id": oid(sub_id)})
    staff = "submissions.grade" in PERMISSIONS.get(user["role"], set())
    if not sub or (sub["user_id"] != user["id"] and not staff):
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    block = await db.content_blocks.find_one({"_id": oid(sub["block_id"])})
    attempts = await db.submissions.find({"user_id": sub["user_id"], "block_id": sub["block_id"]},
                                         {"history": 0}).sort("attempt", -1).to_list(50)
    return {"submission": ser(sub), "block": ser(block) if block else None, "attempts": ser(attempts)}


@router.post("/{sub_id}/claim")
async def claim(sub_id: str, user: dict = Depends(require("submissions.grade"))):
    sub = await db.submissions.find_one_and_update({"_id": oid(sub_id), "status": "submitted"}, {
        "$set": {"status": "in_review", "reviewer_id": user["id"], "reviewer_name": user.get("name", ""), "updated_at": now()},
        "$push": {"history": _hist("in_review", user)}}, return_document=ReturnDocument.AFTER)
    if not sub:
        raise HTTPException(status_code=409, detail="Esta submissão já está em correção ou não está mais aguardando")
    return ser(sub)


@router.post("/{sub_id}/grade")
async def grade(sub_id: str, body: GradeIn, user: dict = Depends(require("submissions.grade"))):
    if body.result not in ("approved", "rejected", "returned"):
        raise HTTPException(status_code=400, detail="Resultado inválido")
    sub = await db.submissions.find_one({"_id": oid(sub_id)})
    if not sub or sub["status"] not in ("submitted", "in_review"):
        raise HTTPException(status_code=409, detail="Esta submissão não está aguardando correção")
    if body.result != "approved" and not body.feedback.strip():
        raise HTTPException(status_code=400, detail="Escreva um feedback ao reprovar ou devolver")
    status = "returned" if body.result == "returned" else "graded"
    grading = {**body.model_dump(), "graded_by": user["id"], "graded_by_name": user.get("name", ""), "graded_at": now()}
    res = await db.submissions.update_one({"_id": sub["_id"], "status": {"$in": ["submitted", "in_review"]}}, {
        "$set": {"status": status, "grading": grading, "updated_at": now()},
        "$push": {"history": {**_hist(status, user), "result": body.result}}})
    if not res.modified_count:
        raise HTTPException(status_code=409, detail="Outra pessoa corrigiu esta submissão ao mesmo tempo")
    if body.result == "approved":
        await db.progress.update_one({"user_id": sub["user_id"], "node_id": sub["node_id"], "block_id": sub["block_id"]},
                                     {"$set": {"status": "completed", "completed_at": now(), "updated_at": now(),
                                               "track_id": sub["track_id"], "scope": "block"}}, upsert=True)
    await db.learning_events.insert_one({"user_id": sub["user_id"], "track_id": sub["track_id"], "node_id": sub["node_id"],
                                         "block_id": sub["block_id"], "type": f"submission:{body.result}", "data": {},
                                         "at": now()})
    return ser(await db.submissions.find_one({"_id": sub["_id"]}))
