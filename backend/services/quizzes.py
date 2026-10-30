"""Versioned quiz publication, server grading, and private attempt history."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core_utils import now
from database import db
from learning import assert_unlocked, assert_visible
from services.auth import rate_limit
from services.common import get_document
from settings import settings

MAX_ATTEMPTS = 3
MAX_QUESTIONS = 250
PASSING_PERCENT = 70
CAS_RETRIES = 12
DISPLAY_QUANTUM = Decimal("0.01")
RATE_LIMIT_WINDOW_SECONDS = 60


class QuizSourceError(ValueError):
    """The published source cannot be graded without guessing or data loss."""


async def _limit_quiz_request(action: str, user_id: str, maximum: int) -> None:
    # Use the authenticated identity, not the client IP, so changing networks
    # cannot reset a user's quiz budget. The token-bucket service hashes again
    # before persisting its key.
    key = hmac.new(
        settings.jwt_secret.encode("utf-8"), user_id.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    try:
        await rate_limit(f"quiz:{action}", key, maximum, RATE_LIMIT_WINDOW_SECONDS)
    except HTTPException as exc:
        if exc.status_code != 429:
            raise
        retry_after = max(1, (RATE_LIMIT_WINDOW_SECONDS + maximum - 1) // maximum)
        raise HTTPException(
            status_code=429,
            detail=exc.detail,
            headers={**(exc.headers or {}), "Retry-After": str(retry_after)},
        ) from exc


def _display_percent(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value.quantize(DISPLAY_QUANTUM, rounding=ROUND_HALF_UP))


def _percent(correct: int, total: int) -> Decimal:
    if total <= 0:
        raise QuizSourceError("Quiz sem questões avaliáveis")
    return Decimal(correct) * Decimal(100) / Decimal(total)


def grade_quiz_questions(questions: list[dict], answers: list[dict]) -> dict[str, Any]:
    """Grade one response against a private immutable snapshot.

    Missing question responses count as incorrect. Duplicate or foreign
    question/option references are rejected rather than silently ignored.
    """
    if not questions:
        raise QuizSourceError("Quiz sem questões avaliáveis")

    question_map: dict[str, dict] = {}
    for question in questions:
        question_id = question.get("question_id")
        if not isinstance(question_id, str) or question_id in question_map:
            raise QuizSourceError("Identidade de questão ausente ou duplicada")
        raw_options = question.get("options")
        if not isinstance(raw_options, list):
            raise QuizSourceError("Alternativas ausentes ou inválidas")
        option_ids: list[str] = []
        for option in raw_options:
            if not isinstance(option, dict) or not isinstance(option.get("option_id"), str):
                raise QuizSourceError("Identidade de alternativa ausente ou inválida")
            option_ids.append(option["option_id"])
        if not option_ids or len(option_ids) != len(set(option_ids)):
            raise QuizSourceError("Alternativas ausentes ou duplicadas")
        correct_option_id = question.get("correct_option_id")
        if not isinstance(correct_option_id, str) or correct_option_id not in option_ids:
            raise QuizSourceError("Gabarito não corresponde a uma alternativa")
        question_map[question_id] = question

    submitted: dict[str, str] = {}
    for answer in answers:
        question_id = answer.get("question_id")
        option_id = answer.get("option_id")
        if not isinstance(question_id, str) or not isinstance(option_id, str):
            raise QuizSourceError("Resposta com identidade inválida")
        if question_id not in question_map:
            raise QuizSourceError("Questão não pertence a esta versão do quiz")
        if question_id in submitted:
            raise QuizSourceError("Há mais de uma resposta para a mesma questão")
        if option_id not in {item["option_id"] for item in question_map[question_id]["options"]}:
            raise QuizSourceError("Alternativa não pertence à questão")
        submitted[question_id] = option_id

    correct_count = sum(
        submitted.get(question_id) == question["correct_option_id"]
        for question_id, question in question_map.items()
    )
    total = len(question_map)
    score = _percent(correct_count, total)
    # Integer arithmetic avoids rounding the displayed percentage before the threshold check.
    passed = correct_count * 100 >= PASSING_PERCENT * total
    return {
        "correct_answers": correct_count,
        "total_questions": total,
        "score_percent": score,
        "passed": passed,
    }


def _question_snapshot(block: dict, order: int) -> dict:
    data = block.get("data")
    if not isinstance(data, dict):
        raise QuizSourceError("Bloco de quiz sem dados válidos")
    prompt = data.get("question", data.get("prompt"))
    options = data.get("options")
    correct_index = data.get("correct_index")
    explanation = data.get("explanation")
    answer_key_ref = data.get("answer_key_ref")
    answer_key = data.get("answer_key")
    answer_key_provenance = None
    if "weight" in data:
        raise QuizSourceError("Pesos por questão não são suportados pelo modelo atual")
    if data.get("format", "multiple_choice") != "multiple_choice":
        raise QuizSourceError("Formato de questão não suportado pelo avaliador atual")
    if not isinstance(prompt, str) or not prompt.strip():
        raise QuizSourceError("Questão sem enunciado")
    if not isinstance(options, list) or len(options) < 2:
        raise QuizSourceError("Questão precisa de pelo menos duas alternativas")
    option_items = []
    for index, option in enumerate(options):
        option_id: object
        option_text: object
        if isinstance(option, str):
            option_id, option_text = f"option-{index + 1}", option
        elif isinstance(option, dict):
            option_id = option.get("ref", option.get("option_id"))
            option_text = option.get("text")
        else:
            raise QuizSourceError("Alternativa com formato inválido")
        if not isinstance(option_id, str) or not option_id.strip():
            raise QuizSourceError("Identidade de alternativa ausente ou inválida")
        if not isinstance(option_text, str) or not option_text.strip():
            raise QuizSourceError("Alternativa com texto inválido")
        option_items.append({"option_id": option_id, "text": option_text})
    option_ids = [item["option_id"] for item in option_items]
    if len(option_ids) != len(set(option_ids)):
        raise QuizSourceError("Alternativas duplicadas")

    correct_option_ref = data.get("correct_option_ref")
    if answer_key is not None:
        if not isinstance(answer_key, dict):
            raise QuizSourceError("Gabarito tipado com formato inválido")
        if not isinstance(answer_key_ref, str) or answer_key.get("ref") != answer_key_ref:
            raise QuizSourceError("Referência do gabarito não corresponde ao gabarito associado")
        question_ref = data.get("import_ref")
        if answer_key.get("question_ref") != question_ref:
            raise QuizSourceError("Gabarito associado a outra questão")
        correct_option_ref = answer_key.get("correct_option_ref")
        if not isinstance(correct_option_ref, str):
            raise QuizSourceError("Gabarito tipado sem alternativa correta avaliável")
        explanation = answer_key.get("explanation")
        answer_key_provenance = answer_key.get("provenance")
    elif answer_key_ref is not None or data.get("answer_key_required") is True:
        raise QuizSourceError("A questão exige gabarito tipado associado")

    if correct_option_ref is not None:
        if not isinstance(correct_option_ref, str) or correct_option_ref not in option_ids:
            raise QuizSourceError("Gabarito não corresponde a uma alternativa")
        if correct_index is not None and (
            type(correct_index) is not int
            or not 0 <= correct_index < len(option_items)
            or option_items[correct_index]["option_id"] != correct_option_ref
        ):
            raise QuizSourceError("Índice e referência de resposta correta divergem")
    elif type(correct_index) is not int or not 0 <= correct_index < len(option_items):
        raise QuizSourceError("Índice de resposta correta inválido")
    else:
        correct_option_ref = option_items[correct_index]["option_id"]
    if explanation is not None and not isinstance(explanation, str):
        raise QuizSourceError("Explicação com formato inválido")
    source_block_id = str(block.get("_id", ""))
    if not ObjectId.is_valid(source_block_id):
        raise QuizSourceError("Bloco de questão sem identidade persistente válida")
    question_id = data.get("import_ref", source_block_id)
    if not isinstance(question_id, str) or not question_id.strip() or len(question_id) > 100:
        raise QuizSourceError("Identidade curricular da questão inválida")
    source_provenance = data.get("provenance")
    if source_provenance is not None and not isinstance(source_provenance, dict):
        raise QuizSourceError("Proveniência da questão inválida")
    if answer_key_provenance is not None and not isinstance(answer_key_provenance, dict):
        raise QuizSourceError("Proveniência do gabarito inválida")
    return {
        "question_id": question_id,
        "order": order,
        "prompt": prompt,
        "options": option_items,
        "correct_option_id": correct_option_ref,
        "explanation": explanation,
        "answer_key_ref": answer_key_ref,
        "source_block_id": source_block_id,
        "source_provenance": source_provenance,
        "answer_key_provenance": answer_key_provenance,
    }


def _snapshot_hash(
    quiz_id: str, title: str, curriculum_ref: str | None, questions: list[dict]
) -> str:
    canonical = json.dumps(
        {
            "quiz_id": quiz_id,
            "title": title,
            "curriculum_ref": curriculum_ref,
            "questions": questions,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


async def publish_quiz_version(quiz_id: str, user: dict) -> dict:
    await _limit_quiz_request("publish", user["id"], settings.quiz_publish_limit_per_minute)
    node = await get_document("nodes", quiz_id)
    blocks = (
        await db.content_blocks.find({"node_id": quiz_id, "type": "quiz", "status": "published"})
        .sort([("order", 1), ("_id", 1)])
        .to_list(MAX_QUESTIONS + 1)
    )
    if not blocks:
        raise HTTPException(status_code=422, detail="O tópico não contém questões publicadas")
    if len(blocks) > MAX_QUESTIONS:
        raise HTTPException(status_code=422, detail="O quiz excede o limite de questões suportado")
    try:
        questions = [_question_snapshot(block, order) for order, block in enumerate(blocks)]
        grade_quiz_questions(questions, [])
    except QuizSourceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    raw_meta = node.get("meta")
    meta = raw_meta if isinstance(raw_meta, dict) else {}
    curriculum_ref = meta.get("import_ref") if isinstance(meta.get("import_ref"), str) else None
    title = str(node.get("title") or "Quiz")
    content_hash = _snapshot_hash(quiz_id, title, curriculum_ref, questions)
    version = await db.quiz_versions.find_one({"quiz_id": quiz_id, "content_hash": content_hash})
    if version is None:
        version_id = ObjectId()
        document = {
            "_id": version_id,
            "quiz_id": quiz_id,
            "node_id": quiz_id,
            "track_id": node["track_id"],
            "status": "published",
            "curriculum_ref": curriculum_ref,
            "title": title,
            "questions": questions,
            "question_count": len(questions),
            "content_hash": content_hash,
            "created_at": now(),
            "created_by": user["id"],
            "source_block_ids": [question["source_block_id"] for question in questions],
        }
        try:
            await db.quiz_versions.insert_one(document)
            version = document
        except DuplicateKeyError:
            version = await db.quiz_versions.find_one(
                {"quiz_id": quiz_id, "content_hash": content_hash}
            )
            if version is None:
                raise HTTPException(status_code=409, detail="Conflito ao publicar versão do quiz")

    await db.quiz_catalog.replace_one(
        {"_id": quiz_id},
        {
            "_id": quiz_id,
            "quiz_id": quiz_id,
            "node_id": quiz_id,
            "track_id": node["track_id"],
            "active_version_id": version["_id"],
            "updated_at": now(),
            "updated_by": user["id"],
        },
        upsert=True,
    )
    return {
        "quiz_id": quiz_id,
        "version_id": str(version["_id"]),
        "title": version["title"],
        "question_count": version["question_count"],
        "created_at": version["created_at"],
    }


async def _accessible_node(quiz_id: str, user: dict, *, enforce_unlock: bool = True) -> dict:
    node = await get_document("nodes", quiz_id)
    if enforce_unlock:
        await assert_unlocked(node, user)
    else:
        await assert_visible(node, user)
    return node


async def _current_version(quiz_id: str) -> tuple[dict, dict]:
    catalog = await db.quiz_catalog.find_one({"_id": quiz_id})
    if not catalog:
        raise HTTPException(status_code=404, detail="Quiz não encontrado")
    version = await db.quiz_versions.find_one(
        {"_id": catalog["active_version_id"], "quiz_id": quiz_id}
    )
    if not version:
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")
    return catalog, version


def _public_question(question: dict) -> dict:
    return {
        "question_id": question["question_id"],
        "order": question["order"],
        "prompt": question["prompt"],
        "options": [
            {"option_id": option["option_id"], "text": option["text"]}
            for option in question["options"]
        ],
    }


def _progress_key(user_id: str, quiz_id: str, version_id: str) -> dict:
    return {"user_id": user_id, "quiz_id": quiz_id, "version_id": version_id}


async def _get_or_create_progress(user_id: str, quiz_id: str, version_id: str) -> dict:
    key = _progress_key(user_id, quiz_id, version_id)
    try:
        progress = await db.quiz_progress.find_one_and_update(
            key,
            {
                "$setOnInsert": {
                    **key,
                    "attempt_count": 0,
                    "best_correct_answers": 0,
                    "best_score_percent": Decimal128("0"),
                    "passed": False,
                    "attempts": [],
                    "created_at": now(),
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
    except DuplicateKeyError:
        progress = await db.quiz_progress.find_one(key)
    if progress is None:
        raise HTTPException(status_code=503, detail="Não foi possível carregar o histórico do quiz")
    return progress


def _result_payload(attempt: dict) -> dict:
    result = attempt["result"]
    return {
        "quiz_id": result["quiz_id"],
        "version_id": result["version_id"],
        "attempt_number": result["attempt_number"],
        "total_questions": result["total_questions"],
        "score_percent": result["score_percent"],
        "passed": result["passed"],
        "attempts_used": result["attempts_used"],
        "attempts_remaining": result["attempts_remaining"],
        "best_score_percent": result["best_score_percent"],
        "review_available": result["review_available"],
        "attempt_id": str(attempt["attempt_id"]),
        "submitted_at": attempt["submitted_at"],
    }


async def get_public_quiz(quiz_id: str, user: dict) -> dict:
    await _accessible_node(quiz_id, user)
    await _limit_quiz_request("read", user["id"], settings.quiz_read_limit_per_minute)
    _catalog, version = await _current_version(quiz_id)
    version_id = str(version["_id"])
    progress = await db.quiz_progress.find_one(_progress_key(user["id"], quiz_id, version_id))
    attempts_used = progress.get("attempt_count", 0) if progress else 0
    best = progress.get("best_score_percent") if progress else None
    return {
        "quiz_id": quiz_id,
        "version_id": version_id,
        "curriculum_ref": version.get("curriculum_ref"),
        "title": version["title"],
        "questions": [_public_question(item) for item in version["questions"]],
        "attempts_used": attempts_used,
        "attempts_remaining": max(0, MAX_ATTEMPTS - attempts_used),
        "passed": bool(progress and progress.get("passed")),
        "best_score_percent": _display_percent(best.to_decimal() if best else None),
        "review_available": attempts_used >= MAX_ATTEMPTS,
    }


def _request_hash(version_id: str, answers: list[dict]) -> str:
    body = json.dumps(
        {"version_id": version_id, "answers": answers},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


async def submit_quiz_attempt(
    quiz_id: str,
    version_id: str,
    answers: list[dict],
    idempotency_key: str,
    user: dict,
) -> dict:
    await _accessible_node(quiz_id, user)
    if not ObjectId.is_valid(version_id):
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")
    current = await db.quiz_versions.find_one({"_id": ObjectId(version_id), "quiz_id": quiz_id})
    if current is None:
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")

    user_id = user["id"]
    idem_hash = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
    request_hash = _request_hash(version_id, answers)
    key = _progress_key(user_id, quiz_id, version_id)

    # A retry of a completed request remains idempotent after a newer version
    # becomes active. New submissions against the stale version are rejected.
    existing_progress = await db.quiz_progress.find_one(key)
    if existing_progress is not None:
        previous = next(
            (
                item
                for item in existing_progress.get("attempts", [])
                if item.get("idempotency_key_hash") == idem_hash
            ),
            None,
        )
        if previous is not None:
            if previous.get("request_hash") != request_hash:
                raise HTTPException(
                    status_code=409, detail="Chave idempotente reutilizada com outro conteúdo"
                )
            return _result_payload(previous)

    # A completed idempotent retry above is free. Only a new request consumes
    # a token, and no attempt is reserved until the atomic progress update.
    await _limit_quiz_request("attempt", user_id, settings.quiz_attempt_limit_per_minute)

    catalog = await db.quiz_catalog.find_one({"_id": quiz_id})
    if catalog is None or str(catalog["active_version_id"]) != version_id:
        raise HTTPException(status_code=409, detail="Esta versão do quiz não está mais ativa")
    try:
        grade = grade_quiz_questions(current["questions"], answers)
    except QuizSourceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for _attempt in range(CAS_RETRIES):
        progress = await _get_or_create_progress(user_id, quiz_id, version_id)
        previous = next(
            (
                item
                for item in progress.get("attempts", [])
                if item.get("idempotency_key_hash") == idem_hash
            ),
            None,
        )
        if previous is not None:
            if previous.get("request_hash") != request_hash:
                raise HTTPException(
                    status_code=409, detail="Chave idempotente reutilizada com outro conteúdo"
                )
            return _result_payload(previous)

        count = progress.get("attempt_count", 0)
        if count >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=409, detail="As três tentativas desta versão já foram utilizadas"
            )

        attempt_number = count + 1
        next_best_correct = max(progress.get("best_correct_answers", 0), grade["correct_answers"])
        score = grade["score_percent"]
        best_score = _percent(next_best_correct, grade["total_questions"])
        remaining = MAX_ATTEMPTS - attempt_number
        submitted_at = now()
        attempt_result = {
            "quiz_id": quiz_id,
            "version_id": version_id,
            "attempt_number": attempt_number,
            "total_questions": grade["total_questions"],
            "score_percent": _display_percent(score),
            "passed": grade["passed"],
            "attempts_used": attempt_number,
            "attempts_remaining": remaining,
            "best_score_percent": _display_percent(best_score),
            "review_available": attempt_number == MAX_ATTEMPTS,
        }
        attempt_doc = {
            "attempt_id": ObjectId(),
            "attempt_number": attempt_number,
            "answers": answers,
            "correct_answers": grade["correct_answers"],
            "total_questions": grade["total_questions"],
            "score_percent_exact": Decimal128(str(score)),
            "passed": grade["passed"],
            "idempotency_key_hash": idem_hash,
            "request_hash": request_hash,
            "submitted_at": submitted_at,
            "result": attempt_result,
        }
        update: dict[str, Any] = {
            "$inc": {"attempt_count": 1},
            "$push": {"attempts": attempt_doc},
            "$max": {
                "best_correct_answers": next_best_correct,
                "best_score_percent": Decimal128(str(best_score)),
            },
            "$set": {"updated_at": submitted_at},
        }
        if grade["passed"]:
            update["$set"]["passed"] = True
        saved = await db.quiz_progress.find_one_and_update(
            {
                "_id": progress["_id"],
                "attempt_count": count,
                "attempts.idempotency_key_hash": {"$ne": idem_hash},
            },
            update,
            return_document=ReturnDocument.AFTER,
        )
        if saved is not None:
            persisted_attempt = next(
                item for item in saved["attempts"] if item.get("idempotency_key_hash") == idem_hash
            )
            return _result_payload(persisted_attempt)
        await asyncio.sleep(0)

    raise HTTPException(
        status_code=409,
        detail="Há outra submissão concorrente; repita com a mesma chave de idempotência",
    )


async def get_quiz_history(quiz_id: str, user: dict, *, limit: int = 100, skip: int = 0) -> dict:
    await _accessible_node(quiz_id, user, enforce_unlock=False)
    await _limit_quiz_request("history", user["id"], settings.quiz_history_limit_per_minute)
    pipeline: list[dict[str, Any]] = [
        {"$match": {"user_id": user["id"], "quiz_id": quiz_id}},
        {"$unwind": "$attempts"},
        {"$replaceRoot": {"newRoot": "$attempts"}},
        {"$sort": {"submitted_at": -1, "attempt_id": 1}},
        {
            "$facet": {
                "items": [
                    {"$skip": skip},
                    {"$limit": limit},
                    {
                        "$project": {
                            "_id": 0,
                            "attempt_id": 1,
                            "result": 1,
                            "submitted_at": 1,
                        }
                    },
                ],
                "total": [{"$count": "count"}],
            }
        },
    ]
    cursor = await db.quiz_progress.aggregate(pipeline)
    rows = await cursor.to_list(1)
    if not rows:
        return {"items": [], "total": 0, "limit": limit, "skip": skip}
    row = rows[0]
    return {
        "items": [_result_payload(attempt) for attempt in row["items"]],
        "total": row["total"][0]["count"] if row["total"] else 0,
        "limit": limit,
        "skip": skip,
    }


async def get_quiz_recovery(
    quiz_id: str, version_id: str, user: dict, idempotency_key: str | None = None
) -> dict:
    """Read only the authenticated learner's durable state for one quiz version.

    Attempt insertion and result persistence happen in one atomic update today,
    so there is no durable pending reservation to report. A missing exact
    idempotency match stays unknown because a request may still be in flight.
    Without a key, the most recent complete attempt is returned as history,
    never as proof that it corresponds to a lost browser intent.
    """
    await _accessible_node(quiz_id, user, enforce_unlock=False)
    await _limit_quiz_request("history", user["id"], settings.quiz_history_limit_per_minute)
    if not ObjectId.is_valid(version_id):
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")
    version = await db.quiz_versions.find_one(
        {"_id": ObjectId(version_id), "quiz_id": quiz_id}, {"_id": 1}
    )
    if version is None:
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")

    progress = await db.quiz_progress.find_one(_progress_key(user["id"], quiz_id, version_id))
    attempts = progress.get("attempts", []) if progress else []
    attempt_count = progress.get("attempt_count", 0) if progress else 0
    if not isinstance(attempts, list) or attempt_count != len(attempts):
        raise HTTPException(status_code=503, detail="Histórico do quiz inconsistente")

    matched = None
    if idempotency_key is not None:
        key_hash = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
        matched = next(
            (item for item in attempts if item.get("idempotency_key_hash") == key_hash),
            None,
        )
        if matched is not None:
            state = "confirmed"
        else:
            state = "unknown"
    elif attempts:
        matched = max(attempts, key=lambda item: item.get("attempt_number", 0))
        state = "latest_confirmed"
    else:
        state = "unknown"

    return {
        "state": state,
        "quiz_id": quiz_id,
        "version_id": version_id,
        "attempts_used": attempt_count,
        "attempts_remaining": max(0, MAX_ATTEMPTS - attempt_count),
        "review_available": attempt_count >= MAX_ATTEMPTS,
        "attempt": _result_payload(matched) if matched is not None else None,
        "may_still_be_processing": state == "unknown",
    }


async def get_quiz_review(quiz_id: str, version_id: str, user: dict) -> dict:
    await _accessible_node(quiz_id, user, enforce_unlock=False)
    await _limit_quiz_request("review", user["id"], settings.quiz_review_limit_per_minute)
    if not ObjectId.is_valid(version_id):
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")
    version = await db.quiz_versions.find_one({"_id": ObjectId(version_id), "quiz_id": quiz_id})
    if version is None:
        raise HTTPException(status_code=404, detail="Versão do quiz não encontrada")
    progress = await db.quiz_progress.find_one(
        _progress_key(user["id"], quiz_id, version_id), {"attempt_count": 1}
    )
    if not progress or progress.get("attempt_count", 0) < MAX_ATTEMPTS:
        raise HTTPException(
            status_code=403, detail="A revisão fica disponível após três tentativas"
        )
    return {
        "quiz_id": quiz_id,
        "version_id": version_id,
        "title": version["title"],
        "questions": [
            {
                "question_id": question["question_id"],
                "order": question["order"],
                "prompt": question["prompt"],
                "options": [
                    {
                        "option_id": option["option_id"],
                        "text": option["text"],
                        "correct": option["option_id"] == question["correct_option_id"],
                    }
                    for option in question["options"]
                ],
                "explanation": question.get("explanation"),
            }
            for question in version["questions"]
        ],
    }
