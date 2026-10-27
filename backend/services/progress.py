import json
from hashlib import sha256
from typing import Any

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError

from constants import PROGRESS_STATUSES
from core_utils import now
from database import db
from learning import assert_unlocked, track_locks
from serialization import oid, ser

RECENT_OPERATION_LIMIT = 128


def _operation_event_id(user_id: str, operation_id: str, kind: str) -> str:
    digest = sha256(f"{kind}:{user_id}:{operation_id}".encode("utf-8")).hexdigest()
    return f"learning-{kind}-{digest}"


def _operation_fingerprint(body: dict) -> str:
    payload = {
        "node_id": body["node_id"],
        "block_id": body.get("block_id"),
        "status": body["status"],
        "data": body.get("data", {}),
    }
    if body.get("attempt_id") is not None:
        payload["attempt_id"] = body["attempt_id"]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _idempotency_conflict(record: dict | None) -> None:
    raise HTTPException(
        status_code=409,
        detail={"code": "progress_idempotency_conflict", "current": _public_progress(record)},
    )


def _public_progress(record: dict | None) -> dict | None:
    if record is None:
        return None
    public = dict(record)
    public.pop("_pending_event", None)
    public.pop("_recent_operation_ids", None)
    public.pop("_recent_operations", None)
    public.pop("_recent_attempts", None)
    return ser(public)


def _progress_conflict(record: dict | None) -> None:
    raise HTTPException(
        status_code=409,
        detail={"code": "progress_version_conflict", "current": _public_progress(record)},
    )


async def _node(node_id: str) -> dict:
    found = await db.nodes.find_one({"_id": oid(node_id)})
    if found is None:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    return dict(found)


async def _event(
    user_id: str,
    node: dict,
    kind: str,
    block_id: str | None = None,
    data: dict | None = None,
    *,
    event_id: str | None = None,
    at=None,
    operation_id: str | None = None,
) -> dict:
    document = {
        "user_id": user_id,
        "track_id": node["track_id"],
        "node_id": str(node["_id"]),
        "block_id": block_id,
        "type": kind,
        "data": data or {},
        "at": at or now(),
    }
    if operation_id:
        document["operation_id"] = operation_id
    if event_id:
        try:
            await db.learning_events.update_one(
                {"_id": event_id}, {"$setOnInsert": {**document, "_id": event_id}}, upsert=True,
            )
        except DuplicateKeyError:
            # Concurrent replay can race on the deterministic event _id.
            pass
        saved = await db.learning_events.find_one({"_id": event_id})
        if (saved.get("user_id"), saved.get("node_id"), saved.get("type")) != (
            user_id, str(node["_id"]), kind,
        ):
            raise HTTPException(status_code=409, detail="Chave de operação reutilizada")
        return saved
    result = await db.learning_events.insert_one(document)
    document["_id"] = result.inserted_id
    return document


async def _flush_pending_progress_event(key: dict) -> None:
    try:
        progress = await db.progress.find_one(key, {"_pending_event": 1})
        pending = (progress or {}).get("_pending_event")
        if not pending:
            return
        event_id = pending["id"]
        track_state = pending.get("track_state")
        event = {name: value for name, value in pending.items() if name not in {"id", "track_state"}}
        event["_id"] = event_id
        await db.learning_events.update_one(
            {"_id": event_id}, {"$setOnInsert": event}, upsert=True,
        )
        if track_state:
            timestamp = track_state["at"]
            await db.user_track_state.update_one(
                {"user_id": track_state["user_id"], "track_id": track_state["track_id"]},
                [{"$set": {
                    "last_node_id": {"$cond": [
                        {"$gte": [timestamp, {"$ifNull": ["$last_at", timestamp]}]},
                        track_state["node_id"], {"$ifNull": ["$last_node_id", track_state["node_id"]]},
                    ]},
                    "last_node_title": {"$cond": [
                        {"$gte": [timestamp, {"$ifNull": ["$last_at", timestamp]}]},
                        track_state["node_title"], {"$ifNull": ["$last_node_title", track_state["node_title"]]},
                    ]},
                    "last_at": {"$max": [{"$ifNull": ["$last_at", timestamp]}, timestamp]},
                    "started_at": {"$ifNull": ["$started_at", timestamp]},
                }}],
                upsert=True,
            )
        await db.progress.update_one(
            {**key, "_pending_event.id": event_id}, {"$unset": {"_pending_event": ""}},
        )
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="O progresso foi salvo, mas o evento ainda aguarda reconciliação.",
        ) from None


async def set_progress(body: dict, user: dict) -> dict:
    status = body["status"]
    if status not in PROGRESS_STATUSES:
        raise HTTPException(status_code=400, detail="Status de progresso inválido")
    node = await _node(body["node_id"])
    await assert_unlocked(node, user)
    block_id = body.get("block_id")
    if block_id is not None:
        block = await db.content_blocks.find_one({"_id": oid(block_id), "node_id": body["node_id"]})
        if block is None:
            raise HTTPException(status_code=404, detail="Bloco não encontrado")

    key = {"user_id": user["id"], "node_id": body["node_id"], "block_id": block_id}
    data = body.get("data", {})
    operation_id = body.get("operation_id")
    attempt_id = body.get("attempt_id")
    if attempt_id and (block_id is None or status != "completed"):
        raise HTTPException(status_code=400, detail="Uma tentativa avaliativa exige a conclusão de um bloco")
    expected_revision = body.get("expected_revision")
    event_id = (
        _operation_event_id(user["id"], attempt_id, "attempt") if attempt_id
        else _operation_event_id(user["id"], operation_id, "progress") if operation_id
        else None
    )
    operation_fingerprint = _operation_fingerprint(body) if operation_id else None

    for _ in range(8):
        try:
            await _flush_pending_progress_event(key)
            current = await db.progress.find_one(key)
            if current is None and expected_revision not in (None, 0):
                _progress_conflict(None)
            if current is not None:
                if attempt_id:
                    prior_attempt = next((
                        item for item in current.get("_recent_attempts", [])
                        if isinstance(item, dict) and item.get("id") == attempt_id
                    ), None)
                    if prior_attempt:
                        if prior_attempt.get("fingerprint") != operation_fingerprint:
                            _idempotency_conflict(current)
                        return _public_progress(current)
                if operation_id:
                    prior_operation = next((
                        item for item in current.get("_recent_operations", [])
                        if isinstance(item, dict) and item.get("id") == operation_id
                    ), None)
                    if prior_operation:
                        if prior_operation.get("fingerprint") != operation_fingerprint:
                            _idempotency_conflict(current)
                        return _public_progress(current)
                current_revision = current.get("revision", 0)
                if expected_revision is not None and expected_revision != current_revision:
                    _progress_conflict(current)
            else:
                current_revision = 0

            if event_id:
                prior_event = await db.learning_events.find_one({"_id": event_id})
                if prior_event is not None:
                    expected_event = (user["id"], str(node["_id"]), block_id, f"status:{status}", data)
                    actual_event = (
                        prior_event.get("user_id"), prior_event.get("node_id"),
                        prior_event.get("block_id"), prior_event.get("type"),
                        prior_event.get("data", {}),
                    )
                    if current is None or actual_event != expected_event:
                        _idempotency_conflict(current)
                    return _public_progress(current)

            old_status = current.get("status") if current else None
            old_data = current.get("data", {}) if current else {}
            status_changed = current is None or old_status != status
            data_changed = current is None or old_data != data
            new_block_attempt = bool(
                block_id
                and status == "completed"
                and (
                    status_changed
                    or (old_status == "completed" and data_changed)
                    or attempt_id is not None
                )
            )
            event_needed = status_changed or data_changed or new_block_attempt

            if not event_needed:
                if not operation_id or current is None:
                    return _public_progress(current)
                cas_filter = {**key, "_pending_event": None, "_recent_operations.id": {"$ne": operation_id}}
                if "revision" in current:
                    cas_filter["revision"] = current_revision
                else:
                    cas_filter["revision"] = {"$exists": False}
                result = await db.progress.update_one(
                    cas_filter,
                    {
                        "$inc": {"revision": 1},
                        "$push": {"_recent_operations": {
                            "$each": [{"id": operation_id, "fingerprint": operation_fingerprint}],
                            "$slice": -RECENT_OPERATION_LIMIT,
                        }},
                    },
                )
                if result.matched_count:
                    return _public_progress(await db.progress.find_one(key))
                continue

            timestamp = now()
            attempts = current.get("attempts", 0) if current else 0
            event = None
            if event_needed:
                event = {
                    "id": event_id or f"learning-progress-{ObjectId()}",
                    "user_id": user["id"],
                    "track_id": node["track_id"],
                    "node_id": str(node["_id"]),
                    "block_id": block_id,
                    "type": f"status:{status}",
                    "data": data,
                    "at": timestamp,
                }
                if status == "completed":
                    event["evidence_kind"] = "self_reported"
                if operation_id:
                    event["operation_id"] = operation_id
                if attempt_id:
                    event["attempt_id"] = attempt_id
                event["track_state"] = {
                    "user_id": user["id"],
                    "track_id": node["track_id"],
                    "node_id": str(node["_id"]),
                    "node_title": node["title"],
                    "at": timestamp,
                }
                if new_block_attempt:
                    event["attempt"] = attempts + 1

            fields: dict[str, Any] = {
                "status": status,
                "track_id": node["track_id"],
                "scope": "block" if block_id else "node",
                "data": data,
                "updated_at": timestamp,
            }
            if status == "completed" and status_changed:
                fields["completed_at"] = timestamp
            elif status != "completed":
                fields["completed_at"] = None
            if status == "not_started":
                fields["started_at"] = None
            elif current is None or old_status == "not_started" or current.get("started_at") is None:
                fields["started_at"] = timestamp
            if event:
                fields["_pending_event"] = event

            cas_filter = {**key, "_pending_event": None}
            if current is not None and "revision" in current:
                cas_filter["revision"] = current_revision
            else:
                cas_filter["revision"] = {"$exists": False}
            if operation_id:
                cas_filter["_recent_operations.id"] = {"$ne": operation_id}

            update: dict[str, Any] = {
                "$set": fields,
                "$setOnInsert": {"created_at": timestamp},
                "$inc": {"revision": 1},
            }
            if not new_block_attempt:
                update["$setOnInsert"]["attempts"] = 0
            if new_block_attempt:
                update["$inc"]["attempts"] = 1
            if operation_id:
                update["$push"] = {
                    "_recent_operations": {
                        "$each": [{"id": operation_id, "fingerprint": operation_fingerprint}],
                        "$slice": -RECENT_OPERATION_LIMIT,
                    }
                }
            if attempt_id and new_block_attempt:
                update.setdefault("$push", {})["_recent_attempts"] = {
                    "$each": [{"id": attempt_id, "fingerprint": operation_fingerprint}],
                    "$slice": -RECENT_OPERATION_LIMIT,
                }

            result = await db.progress.update_one(cas_filter, update, upsert=True)
            if result.matched_count or result.upserted_id is not None:
                await _flush_pending_progress_event(key)
                saved = await db.progress.find_one(key)
                return _public_progress(saved)
        except DuplicateKeyError:
            # A concurrent upsert won the unique (user, node, block) key; reread and retry by revision.
            continue
        except PyMongoError:
            raise HTTPException(status_code=503, detail="Não foi possível salvar o progresso temporariamente.") from None

    current = await db.progress.find_one(key)
    if expected_revision is not None:
        _progress_conflict(current)
    raise HTTPException(status_code=503, detail="O progresso está sendo atualizado em paralelo. Tente novamente.")


async def visit_node(node_id: str, user: dict, operation_id: str | None = None) -> None:
    node = await _node(node_id)
    await assert_unlocked(node, user)
    timestamp = now()
    event_id = _operation_event_id(user["id"], operation_id, "visit") if operation_id else None
    key = {"user_id": user["id"], "node_id": node_id, "block_id": None}
    state_key = {"user_id": user["id"], "track_id": node["track_id"]}
    state_update = [{"$set": {
        "last_node_id": {"$cond": [{"$gte": [timestamp, {"$ifNull": ["$last_at", timestamp]}]}, node_id, "$last_node_id"]},
        "last_node_title": {"$cond": [{"$gte": [timestamp, {"$ifNull": ["$last_at", timestamp]}]}, node["title"], "$last_node_title"]},
        "last_at": {"$max": [{"$ifNull": ["$last_at", timestamp]}, timestamp]},
        "started_at": {"$ifNull": ["$started_at", timestamp]},
    }}]
    try:
        event = await _event(
            user["id"], node, "view", event_id=event_id, at=timestamp, operation_id=operation_id,
        )
        timestamp = event["at"]
        try:
            await db.user_track_state.update_one(state_key, state_update, upsert=True)
        except DuplicateKeyError:
            # A simultaneous first visit created the unique summary; apply this visit to it.
            await db.user_track_state.update_one(state_key, state_update, upsert=False)
        try:
            await db.progress.update_one(key, {
                "$setOnInsert": {
                    "status": "in_progress", "track_id": node["track_id"], "scope": "node",
                    "started_at": timestamp, "completed_at": None, "updated_at": timestamp, "attempts": 0,
                    "revision": 0,
                }
            }, upsert=True)
        except DuplicateKeyError:
            # Another visit inserted the same unique progress key concurrently.
            pass
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Não foi possível registrar a visita temporariamente.") from None


async def get_track_progress(track_id: str, user: dict, limit: int, skip: int) -> dict:
    page_size = min(max(limit, 1), 20000)
    records = await db.progress.find({"user_id": user["id"], "track_id": track_id}).sort("_id", 1).skip(
        max(skip, 0)
    ).limit(page_size).to_list(page_size)
    state = await db.user_track_state.find_one({"user_id": user["id"], "track_id": track_id})
    nodes, blocks = {}, {}
    for record in records:
        item = _public_progress(record)
        if record.get("block_id"):
            blocks[record["block_id"]] = item
        else:
            nodes[record["node_id"]] = item
    return {
        "nodes": nodes,
        "blocks": blocks,
        "state": ser(state) if state else None,
        "locks": await track_locks(track_id, user),
    }


async def get_progress_overview(user: dict) -> dict:
    states = await db.user_track_state.find({"user_id": user["id"]}).sort("last_at", -1).to_list(200)
    cursor = await db.progress.aggregate([
        {"$match": {"user_id": user["id"], "block_id": None, "status": "completed"}},
        {"$group": {"_id": "$track_id", "completed": {"$sum": 1}}},
    ])
    rows = await cursor.to_list(500)
    return {"states": ser(states), "completed": {row["_id"]: row["completed"] for row in rows}}


async def list_progress_history(track_id: str | None, limit: int, skip: int, user: dict) -> list[dict]:
    pending = await db.progress.find(
        {"user_id": user["id"], "_pending_event": {"$exists": True}},
        {"user_id": 1, "node_id": 1, "block_id": 1},
    ).to_list(20000)
    for record in pending:
        key = {
            "user_id": record["user_id"],
            "node_id": record["node_id"],
            "block_id": record.get("block_id"),
        }
        await _flush_pending_progress_event(key)

    query = {"user_id": user["id"]}
    if track_id:
        query["track_id"] = track_id
    page_size = min(max(limit, 1), 100)
    events = await db.learning_events.find(query).sort("at", -1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    ids = list({event["node_id"] for event in events})
    titles = {
        str(node["_id"]): node["title"]
        for node in await db.nodes.find({"_id": {"$in": [oid(item_id) for item_id in ids]}}, {"title": 1}).to_list(200)
    }
    return [{**ser(event), "node_title": titles.get(event["node_id"], "")} for event in events]
