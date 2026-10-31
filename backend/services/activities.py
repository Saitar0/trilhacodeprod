"""Version-pinned student activity attempts with CAS and progress reconciliation."""

import json
import re
import secrets
from hashlib import sha256
from typing import Any

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError

from activity_evaluator import evaluate_multiple_choice
from core_utils import now
from database import db
from integrity import can_view_node
from learning import assert_unlocked
from permissions import is_staff
from serialization import ser
from services.activity_publications import public_activity
from services.progress import set_progress

_IDEMPOTENCY_KEY = re.compile(r"[A-Za-z0-9._:-]{8,128}\Z")


def _http_error(status: int, code: str, message: str, *, current: dict | None = None) -> HTTPException:
    detail: dict[str, Any] = {"code": code, "message": message}
    if current is not None:
        detail["current"] = current
    return HTTPException(status_code=status, detail=detail)


def _validate_idempotency_key(value: str) -> str:
    if not isinstance(value, str) or not _IDEMPOTENCY_KEY.fullmatch(value):
        raise HTTPException(status_code=422, detail="Idempotency-Key inválida")
    return value


def _fingerprint(value: dict) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


async def _active_publication(activity_id: str, user: dict) -> tuple[dict, dict, dict]:
    """Resolve the currently published immutable definition visible to this user."""
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    block = await db.content_blocks.find_one({"_id": ObjectId(activity_id)})
    if not block:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    node = await db.nodes.find_one({"_id": ObjectId(block["node_id"])})
    track = await db.tracks.find_one({"_id": ObjectId(block["track_id"])})
    if not node or not track:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    if not is_staff(user):
        if block.get("status") != "published" or not await can_view_node(node, user):
            raise HTTPException(status_code=404, detail="Atividade não encontrada")
    if track.get("_import_state") is not None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    await assert_unlocked(node, user)
    version_id = track.get("published_activity_version_id")
    if not isinstance(version_id, str):
        raise HTTPException(status_code=404, detail="Atividade ainda não possui avaliação publicada")
    publication = await db.activity_publications.find_one({
        "track_id": str(track["_id"]), "activity_id": activity_id, "published_version_id": version_id,
    })
    if not publication:
        raise HTTPException(status_code=404, detail="Atividade ainda não possui avaliação publicada")
    return dict(track), dict(node), publication


async def _publication_for_attempt(attempt: dict, user: dict) -> dict:
    node = await db.nodes.find_one({"_id": ObjectId(attempt["node_id"])})
    track = await db.tracks.find_one({"_id": ObjectId(attempt["track_id"])})
    if not node or not track or track.get("_import_state") is not None:
        raise HTTPException(status_code=404, detail="Tentativa não encontrada")
    if not is_staff(user) and not await can_view_node(node, user):
        raise HTTPException(status_code=404, detail="Tentativa não encontrada")
    await assert_unlocked(node, user)
    publication = await db.activity_publications.find_one({
        "track_id": attempt["track_id"],
        "activity_id": attempt["activity_id"],
        "published_version_id": attempt["published_version_id"],
    })
    if not publication:
        raise HTTPException(status_code=404, detail="Tentativa não encontrada")
    return publication


def _private_definition(publication: dict) -> dict:
    definition = dict(publication.get("definition") or {})
    digest = definition.pop("definition_sha256", None)
    if not isinstance(digest, str) or _fingerprint(definition) != digest:
        raise HTTPException(status_code=503, detail="A definição publicada não passou na verificação de integridade")
    return definition


def _public_attempt(attempt: dict, publication: dict) -> dict:
    definition = _private_definition(publication)
    result = attempt.get("result")
    return ser({
        "id": attempt["_id"],
        "user_id": attempt["user_id"],
        "track_id": attempt["track_id"],
        "node_id": attempt["node_id"],
        "activity_id": attempt["activity_id"],
        "published_version_id": attempt["published_version_id"],
        "activity_revision": attempt["activity_revision"],
        "attempt_number": attempt["attempt_number"],
        "state": attempt["state"],
        "response": attempt.get("response"),
        "revision": attempt.get("revision", 0),
        "result": ({
            "is_correct": result["is_correct"],
            "score": result["score"],
            "evaluator_version": result["evaluator_version"],
        } if result else None),
        "feedback": attempt.get("public_feedback"),
        "projection_status": attempt.get("projection_status", "complete"),
        "created_at": attempt["created_at"],
        "updated_at": attempt["updated_at"],
        "submitted_at": attempt.get("submitted_at"),
        "evaluated_at": attempt.get("evaluated_at"),
        "activity": public_activity(definition),
    })


async def create_attempt(activity_id: str, version_id: str, operation_key: str, user: dict) -> dict:
    operation_key = _validate_idempotency_key(operation_key)
    fingerprint = _fingerprint({"activity_id": activity_id, "published_version_id": version_id})
    try:
        existing = await db.activity_attempts.find_one({
            "user_id": user["id"], "create_operation_key": operation_key,
        })
        if existing:
            if existing.get("create_fingerprint") != fingerprint:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados")
            publication = await _publication_for_attempt(existing, user)
            return _public_attempt(existing, publication)

        _track, _node, publication = await _active_publication(activity_id, user)
        if version_id != publication["published_version_id"]:
            raise _http_error(409, "activity_version_conflict", "A atividade publicada mudou. Recarregue o conteúdo.")
        definition = _private_definition(publication)
        active = await db.activity_attempts.find_one({
            "user_id": user["id"], "activity_id": activity_id,
            "published_version_id": version_id, "state": {"$in": ["draft", "submitted"]},
        })
        if active:
            raise _http_error(409, "activity_active_attempt", "Já existe uma tentativa que pode ser retomada.")
        submitted_count = await db.activity_attempts.count_documents({
            "user_id": user["id"], "activity_id": activity_id,
            "published_version_id": version_id, "state": {"$in": ["submitted", "evaluated"]},
        })
        max_attempts = definition["max_attempts"]
        if submitted_count >= max_attempts:
            raise _http_error(409, "activity_attempt_limit", "O limite de tentativas desta versão foi atingido.")

        attempt_id = secrets.token_urlsafe(24)
        timestamp = now()
        attempt = {
            "_id": attempt_id,
            "user_id": user["id"],
            "track_id": publication["track_id"],
            "node_id": publication["node_id"],
            "activity_id": activity_id,
            "published_version_id": version_id,
            "activity_revision": definition["activity_revision"],
            "attempt_number": submitted_count + 1,
            "state": "draft",
            "response": None,
            "revision": 0,
            "create_operation_key": operation_key,
            "create_fingerprint": fingerprint,
            "projection_status": "complete",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        await db.activity_attempts.insert_one(attempt)
        return _public_attempt(attempt, publication)
    except DuplicateKeyError:
        existing = await db.activity_attempts.find_one({"user_id": user["id"], "create_operation_key": operation_key})
        if existing:
            if existing.get("create_fingerprint") != fingerprint:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados")
            publication = await _publication_for_attempt(existing, user)
            return _public_attempt(existing, publication)
        active = await db.activity_attempts.find_one({
            "user_id": user["id"], "activity_id": activity_id,
            "published_version_id": version_id, "state": {"$in": ["draft", "submitted"]},
        })
        if active:
            raise _http_error(409, "activity_active_attempt", "Já existe uma tentativa que pode ser retomada.")
        raise _http_error(409, "activity_attempt_conflict", "A tentativa foi iniciada em paralelo; recarregue e tente novamente.")
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Não foi possível iniciar a tentativa temporariamente.") from None


async def _owned_attempt(activity_id: str, attempt_id: str, user: dict) -> dict:
    attempt = await db.activity_attempts.find_one({
        "_id": attempt_id, "user_id": user["id"], "activity_id": activity_id,
    })
    if not attempt:
        raise HTTPException(status_code=404, detail="Tentativa não encontrada")
    return dict(attempt)


async def save_draft(
    activity_id: str, attempt_id: str, selected_option_id: str | None, expected_revision: int,
    operation_key: str, user: dict,
) -> dict:
    operation_key = _validate_idempotency_key(operation_key)
    operation_fingerprint = _fingerprint({
        "selected_option_id": selected_option_id,
        "expected_revision": expected_revision,
    })
    try:
        attempt = await _owned_attempt(activity_id, attempt_id, user)
        publication = await _publication_for_attempt(attempt, user)
        definition = _private_definition(publication)
        if selected_option_id is not None and selected_option_id not in {item["id"] for item in definition["options"]}:
            raise HTTPException(status_code=422, detail="Alternativa inexistente")
        prior = await db.activity_attempts.find_one({
            "user_id": user["id"], "draft_operations.id": operation_key,
        })
        if prior:
            saved = next((item for item in prior.get("draft_operations", []) if item.get("id") == operation_key), {})
            if prior["_id"] != attempt_id or saved.get("fingerprint") != operation_fingerprint:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados")
            return _public_attempt(attempt, publication)
        if attempt["state"] != "draft":
            raise _http_error(409, "activity_state_conflict", "A tentativa não aceita mais alterações de rascunho.",
                              current=_public_attempt(attempt, publication))
        if attempt.get("revision", 0) != expected_revision:
            raise _http_error(409, "activity_revision_conflict", "O rascunho mudou em outro dispositivo.",
                              current=_public_attempt(attempt, publication))
        timestamp = now()
        update = await db.activity_attempts.update_one({
            "_id": attempt_id, "user_id": user["id"], "state": "draft", "revision": expected_revision,
        }, {
            "$set": {
                "response": {"selected_option_id": selected_option_id} if selected_option_id else None,
                "updated_at": timestamp,
            },
            "$inc": {"revision": 1},
            "$push": {"draft_operations": {
                "$each": [{"id": operation_key, "fingerprint": operation_fingerprint}], "$slice": -64,
            }},
        })
        if not update.matched_count:
            current = await _owned_attempt(activity_id, attempt_id, user)
            concurrent = next((
                item for item in current.get("draft_operations", [])
                if isinstance(item, dict) and item.get("id") == operation_key
            ), None)
            if concurrent and concurrent.get("fingerprint") == operation_fingerprint:
                return _public_attempt(current, publication)
            if concurrent:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados")
            raise _http_error(409, "activity_revision_conflict", "O rascunho mudou em outro dispositivo.",
                              current=_public_attempt(current, publication))
        current = await _owned_attempt(activity_id, attempt_id, user)
        return _public_attempt(current, publication)
    except DuplicateKeyError:
        raise _http_error(409, "activity_idempotency_conflict", "Chave de operação já utilizada.")
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Não foi possível salvar o rascunho temporariamente.") from None


async def _project_progress(attempt: dict) -> None:
    if attempt.get("projection_status") == "complete":
        return
    result = attempt.get("result") or {}
    body = {
        "node_id": attempt["node_id"],
        "block_id": attempt["activity_id"],
        "status": "completed",
        "data": {
            "activity_id": attempt["activity_id"],
            "published_version_id": attempt["published_version_id"],
            "activity_attempt_id": attempt["_id"],
            "is_correct": result.get("is_correct", False),
        },
        "attempt_id": attempt["_id"],
        "operation_id": f"activity:{attempt['_id']}",
    }
    try:
        owner = await db.users.find_one({"_id": ObjectId(attempt["user_id"])}, {"role": 1})
        if not owner:
            raise HTTPException(status_code=503, detail="O progresso aguarda a recuperação da conta do aluno.")
        await set_progress(body, {"id": attempt["user_id"], "role": owner.get("role", "student")})
        await db.activity_attempts.update_one(
            {"_id": attempt["_id"], "user_id": attempt["user_id"], "projection_status": "pending"},
            {"$set": {"projection_status": "complete", "projected_at": now()}},
        )
    except HTTPException as exc:
        if exc.status_code >= 500:
            raise
        # The durable attempt remains evaluated and pending; a later retry may
        # reconcile it if content visibility temporarily prevented projection.
        raise HTTPException(status_code=503, detail="Resposta salva; progresso aguarda reconciliação.") from None
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Resposta salva; progresso aguarda reconciliação.") from None


async def _finish_submitted_attempt(attempt: dict, publication: dict) -> dict:
    """Recover the durable submitted state after a process restart or lost response."""
    if attempt.get("state") != "submitted":
        return attempt
    definition = _private_definition(publication)
    option_id = (attempt.get("response") or {}).get("selected_option_id")
    if _fingerprint({
        "selected_option_id": option_id,
        "expected_revision": attempt.get("revision", 1) - 1,
    }) != attempt.get("submit_fingerprint"):
        raise HTTPException(status_code=503, detail="A tentativa enviada não passou na verificação de integridade")
    try:
        evaluation = evaluate_multiple_choice(definition, option_id)
    except ValueError:
        raise HTTPException(status_code=503, detail="A resposta enviada não corresponde à publicação salva") from None
    remaining = max(0, definition["max_attempts"] - attempt["attempt_number"])
    public_feedback = (
        evaluation["feedback"] if evaluation["is_correct"] or remaining == 0
        else "Resposta registrada. Você ainda pode iniciar outra tentativa."
    )
    await db.activity_attempts.update_one({
        "_id": attempt["_id"], "user_id": attempt["user_id"], "state": "submitted",
        "submit_operation_key": attempt["submit_operation_key"],
        "submit_fingerprint": attempt["submit_fingerprint"],
    }, {
        "$set": {
            "state": "evaluated",
            "result": {
                "is_correct": evaluation["is_correct"], "score": evaluation["score"],
                "evaluator_version": evaluation["evaluator_version"],
            },
            "public_feedback": public_feedback,
            "projection_status": "pending",
            "evaluated_at": now(),
            "updated_at": now(),
        },
        "$inc": {"revision": 1},
    })
    return dict(await db.activity_attempts.find_one({"_id": attempt["_id"], "user_id": attempt["user_id"]}))


async def submit_attempt(
    activity_id: str, attempt_id: str, selected_option_id: str, expected_revision: int,
    operation_key: str, user: dict,
) -> dict:
    operation_key = _validate_idempotency_key(operation_key)
    request_fingerprint = _fingerprint({
        "selected_option_id": selected_option_id,
        "expected_revision": expected_revision,
    })
    try:
        attempt = await _owned_attempt(activity_id, attempt_id, user)
        publication = await _publication_for_attempt(attempt, user)
        definition = _private_definition(publication)
        try:
            evaluation = evaluate_multiple_choice(definition, selected_option_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        prior_operation = await db.activity_attempts.find_one({
            "user_id": user["id"], "submit_operation_key": operation_key,
        })
        if prior_operation and prior_operation["_id"] != attempt_id:
            raise _http_error(409, "activity_idempotency_conflict", "Chave de operação já utilizada em outra tentativa")
        if attempt.get("submit_operation_key"):
            if attempt["submit_operation_key"] != operation_key:
                raise _http_error(409, "activity_state_conflict", "A tentativa já foi enviada com outra operação.",
                                  current=_public_attempt(attempt, publication))
            if attempt.get("submit_fingerprint") != request_fingerprint:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados.",
                                  current=_public_attempt(attempt, publication))
        elif attempt["state"] == "draft":
            if attempt.get("revision", 0) != expected_revision:
                raise _http_error(409, "activity_revision_conflict", "O rascunho mudou em outro dispositivo.",
                                  current=_public_attempt(attempt, publication))
            timestamp = now()
            try:
                update = await db.activity_attempts.update_one({
                    "_id": attempt_id, "user_id": user["id"], "state": "draft", "revision": expected_revision,
                }, {
                    "$set": {
                        "state": "submitted",
                        "response": {"selected_option_id": selected_option_id},
                        "submit_operation_key": operation_key,
                        "submit_fingerprint": request_fingerprint,
                        "submitted_at": timestamp,
                        "updated_at": timestamp,
                    },
                    "$inc": {"revision": 1},
                })
            except DuplicateKeyError:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação já utilizada")
            if update.matched_count:
                attempt = await _owned_attempt(activity_id, attempt_id, user)
            else:
                attempt = await _owned_attempt(activity_id, attempt_id, user)
                if (attempt.get("submit_operation_key") != operation_key
                        or attempt.get("submit_fingerprint") != request_fingerprint):
                    raise _http_error(409, "activity_revision_conflict", "A tentativa mudou em outro dispositivo.",
                                      current=_public_attempt(attempt, publication))
        elif attempt["state"] != "submitted":
            raise _http_error(409, "activity_state_conflict", "Estado da tentativa incompatível.",
                              current=_public_attempt(attempt, publication))

        if attempt["state"] == "submitted":
            if attempt.get("submit_operation_key") != operation_key:
                raise _http_error(409, "activity_state_conflict", "A tentativa foi enviada por outra operação.",
                                  current=_public_attempt(attempt, publication))
            if attempt.get("submit_fingerprint") != request_fingerprint:
                raise _http_error(409, "activity_idempotency_conflict", "Chave de operação reutilizada com outros dados.",
                                  current=_public_attempt(attempt, publication))
            # Re-evaluation is safe only from the exact immutable publication
            # pinned on the attempt. The operation fingerprint makes retries
            # return the same assessment input.
            remaining = max(0, definition["max_attempts"] - attempt["attempt_number"])
            if evaluation["is_correct"] or remaining == 0:
                public_feedback = evaluation["feedback"]
            else:
                public_feedback = "Resposta registrada. Você ainda pode iniciar outra tentativa."
            timestamp = now()
            await db.activity_attempts.update_one({
                "_id": attempt_id, "user_id": user["id"], "state": "submitted",
                "submit_operation_key": operation_key, "submit_fingerprint": request_fingerprint,
            }, {
                "$set": {
                    "state": "evaluated",
                    "result": {
                        "is_correct": evaluation["is_correct"],
                        "score": evaluation["score"],
                        "evaluator_version": evaluation["evaluator_version"],
                    },
                    "public_feedback": public_feedback,
                    "projection_status": "pending",
                    "evaluated_at": timestamp,
                    "updated_at": timestamp,
                },
                "$inc": {"revision": 1},
            })
            attempt = await _owned_attempt(activity_id, attempt_id, user)
        if attempt["state"] != "evaluated":
            raise HTTPException(status_code=503, detail="A avaliação ainda aguarda processamento.")
        await _project_progress(attempt)
        attempt = await _owned_attempt(activity_id, attempt_id, user)
        return _public_attempt(attempt, publication)
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Não foi possível avaliar a resposta temporariamente.") from None


async def get_attempts(activity_id: str, user: dict, limit: int, skip: int) -> dict:
    _track, _node, _publication = await _active_publication(activity_id, user)
    page_size = min(max(limit, 1), 50)
    offset = min(max(skip, 0), 10_000)
    attempts = await db.activity_attempts.find({
        "user_id": user["id"], "activity_id": activity_id,
    }).sort("created_at", -1).skip(offset).limit(page_size).to_list(page_size)
    total = await db.activity_attempts.count_documents({"user_id": user["id"], "activity_id": activity_id})
    results = []
    for attempt in attempts:
        publication = await _publication_for_attempt(attempt, user)
        if attempt.get("state") == "submitted":
            attempt = await _finish_submitted_attempt(attempt, publication)
        if attempt.get("projection_status") == "pending" and attempt.get("state") == "evaluated":
            await _project_progress(attempt)
            attempt = await _owned_attempt(activity_id, attempt["_id"], user)
        results.append(_public_attempt(attempt, publication))
    return {"items": results, "limit": page_size, "skip": offset, "total": total}


async def get_attempt(activity_id: str, attempt_id: str, user: dict) -> dict:
    attempt = await _owned_attempt(activity_id, attempt_id, user)
    publication = await _publication_for_attempt(attempt, user)
    if attempt.get("state") == "submitted":
        attempt = await _finish_submitted_attempt(attempt, publication)
    if attempt.get("projection_status") == "pending" and attempt.get("state") == "evaluated":
        await _project_progress(attempt)
        attempt = await _owned_attempt(activity_id, attempt_id, user)
    return _public_attempt(attempt, publication)
