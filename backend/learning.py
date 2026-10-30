from datetime import timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from constants import DEFAULT_HIERARCHY
from core_utils import now
from database import db
from permissions import is_staff, require
from schemas.content import OkOut
from schemas.learning import NoteIn, NoteOut, ReviewDone, ReviewIn, ReviewOut
from schemas.versions import DeletedOut, TrackValidationOut
from security import current_user
from serialization import oid, ser

router = APIRouter(prefix="/api")

REVIEW_BUCKETS = {"today": 0, "soon": 3, "later": 14}
SUGGESTED_DAYS = {"alta": 3, "media": 7, "repertorio": 14}


def visible_nodes(nodes):
    """Published nodes whose ancestors are all published."""
    by_id = {str(n["_id"]): n for n in nodes}
    ok = {}

    def visible(n):
        k = str(n["_id"])
        if k not in ok:
            ok[k] = False
            pid = n.get("parent_id")
            parent = by_id.get(pid) if pid else None
            ok[k] = n["status"] == "published" and (not pid or (parent is not None and visible(parent)))
        return ok[k]
    return [n for n in nodes if visible(n)]


def _quiz_progress_passed(progress: dict | None) -> bool:
    """Require both the server-set pass marker and the persisted best score."""
    if not progress or progress.get("passed") is not True:
        return False
    score = progress.get("best_score_percent")
    try:
        if isinstance(score, Decimal128):
            value = score.to_decimal()
        elif isinstance(score, Decimal):
            value = score
        else:
            return False
        return value.is_finite() and value >= Decimal("70")
    except (InvalidOperation, TypeError, ValueError):
        return False


def compute_prerequisite_states(
    track,
    nodes,
    relations,
    block_counts,
    completed,
    quiz_states=None,
):
    """Return server-evaluated prerequisite states and locks for one learner."""
    if not (track.get("settings") or {}).get("enforce_prerequisites"):
        return {}, {}
    ids = {str(n["_id"]) for n in nodes}
    by_id = {str(n["_id"]): n for n in nodes}
    children = {}
    for n in nodes:
        children.setdefault(n.get("parent_id"), []).append(str(n["_id"]))
    hierarchy = track.get("hierarchy") or DEFAULT_HIERARCHY
    last = hierarchy[-1]
    memo = {}

    def done(nid):
        if nid not in memo:
            memo[nid] = True
            kids = children.get(nid, [])
            if kids:
                memo[nid] = all(done(k) for k in kids)
            else:
                n = by_id[nid]
                learnable = n["kind"] == last or block_counts.get(nid, 0) > 0
                memo[nid] = (nid in completed) if learnable else True
        return memo[nid]

    direct = {}
    states = {}
    quiz_states = quiz_states or {}
    for r in relations:
        if r.get("type") != "prerequisite" or not r.get("enforced") or r.get("node_id") not in ids:
            continue
        target_id = r.get("target_id")
        raw_kind = r.get("prerequisite_kind")
        if raw_kind is None:
            # Relations authored before typed prerequisites retain the existing
            # content-completion behavior, including its missing-target rule.
            if target_id not in ids:
                continue
            kind = "legacy"
            state = "satisfied" if done(target_id) else "pending"
        elif raw_kind == "content_completed":
            kind = raw_kind
            state = (
                "satisfied"
                if target_id in ids and done(target_id)
                else ("pending" if target_id in ids else "unavailable")
            )
        elif raw_kind == "quiz_passed":
            kind = raw_kind
            state = quiz_states.get(target_id, "unavailable")
        else:
            # Corrupt or future unrecognized relation types must fail closed.
            kind = "unavailable"
            state = "unavailable"

        requirement = {
            "target_id": target_id,
            "prerequisite_kind": kind,
            "status": state,
        }
        states.setdefault(r["node_id"], []).append(requirement)
        if state != "satisfied":
            direct.setdefault(r["node_id"], []).append(requirement)

    locks = {}
    for nid in ids:
        if nid in direct:
            locks[nid] = {
                "pending": [item["target_id"] for item in direct[nid]],
                "pending_requirements": direct[nid],
                "via": None,
            }
            continue
        cur, seen = by_id[nid].get("parent_id"), set()
        while cur and cur in by_id and cur not in seen:
            seen.add(cur)
            if cur in direct:
                locks[nid] = {
                    "pending": [item["target_id"] for item in direct[cur]],
                    "pending_requirements": direct[cur],
                    "via": cur,
                }
                break
            cur = by_id[cur].get("parent_id")
    return locks, states


def compute_locks(track, nodes, relations, block_counts, completed, quiz_states=None):
    """Compatibility wrapper returning only the existing lock mapping."""
    locks, _states = compute_prerequisite_states(
        track, nodes, relations, block_counts, completed, quiz_states
    )
    return locks


async def _published_quiz_states(track_id: str, user_id: str, quiz_ids: set[str]) -> dict[str, str]:
    """Return pending/passed only for each target's active published quiz version."""
    if not quiz_ids:
        return {}
    catalogs = await db.quiz_catalog.find(
        {"_id": {"$in": list(quiz_ids)}, "track_id": track_id},
        {"_id": 1, "active_version_id": 1},
    ).to_list(len(quiz_ids))
    active_versions = {
        catalog["_id"]: str(catalog["active_version_id"])
        for catalog in catalogs
        if catalog.get("active_version_id") is not None
    }
    if not active_versions:
        return {quiz_id: "unavailable" for quiz_id in quiz_ids}

    active_version_ids = [
        ObjectId(version_id)
        for version_id in active_versions.values()
        if ObjectId.is_valid(version_id)
    ]
    if not active_version_ids:
        return {quiz_id: "unavailable" for quiz_id in quiz_ids}
    versions = await db.quiz_versions.find(
        {
            "_id": {"$in": active_version_ids},
            "quiz_id": {"$in": list(quiz_ids)},
            "node_id": {"$in": list(quiz_ids)},
            "track_id": track_id,
            "status": "published",
        },
        {"_id": 1, "quiz_id": 1},
    ).to_list(len(active_versions))
    valid_versions = {
        version["quiz_id"]: version["_id"]
        for version in versions
        if active_versions.get(version["quiz_id"]) == str(version["_id"])
    }
    valid_versions = {quiz_id: str(version_id) for quiz_id, version_id in valid_versions.items()}
    states = {quiz_id: "unavailable" for quiz_id in quiz_ids}
    if not valid_versions:
        return states

    progress = await db.quiz_progress.find(
        {
            "user_id": user_id,
            "quiz_id": {"$in": list(valid_versions)},
            "version_id": {"$in": list(valid_versions.values())},
        },
        {"quiz_id": 1, "version_id": 1, "passed": 1, "best_score_percent": 1},
    ).to_list(len(valid_versions))
    states.update({quiz_id: "pending" for quiz_id in valid_versions})
    for record in progress:
        quiz_id = record.get("quiz_id")
        if valid_versions.get(quiz_id) == record.get("version_id") and _quiz_progress_passed(
            record
        ):
            states[quiz_id] = "satisfied"
    return states


async def track_prerequisite_evaluation(track_id: str, user: dict):
    track = await db.tracks.find_one({"_id": oid(track_id)})
    if not track:
        return {}, {}
    nodes = await db.nodes.find({"track_id": track_id}).to_list(10000)
    nodes = [n for n in nodes if n["status"] != "archived"] if is_staff(user) else visible_nodes(nodes)
    relations = await db.relations.find({"track_id": track_id}).to_list(10000)
    bq = {"track_id": track_id} if is_staff(user) else {"track_id": track_id, "status": "published"}
    cursor = await db.content_blocks.aggregate([
        {"$match": bq}, {"$group": {"_id": "$node_id", "n": {"$sum": 1}}}
    ])
    counts = await cursor.to_list(10000)
    done = await db.progress.find(
        {"user_id": user["id"], "track_id": track_id, "block_id": None, "status": "completed"},
        {"node_id": 1},
    ).to_list(20000)
    visible_ids = {str(node["_id"]) for node in nodes}
    quiz_ids = {
        relation["target_id"]
        for relation in relations
        if relation.get("type") == "prerequisite"
        and relation.get("enforced")
        and relation.get("prerequisite_kind") == "quiz_passed"
        and relation.get("node_id") in visible_ids
        and relation.get("target_id") in visible_ids
    }
    quiz_states = await _published_quiz_states(track_id, user["id"], quiz_ids)
    return compute_prerequisite_states(
        track,
        nodes,
        relations,
        {c["_id"]: c["n"] for c in counts},
        {d["node_id"] for d in done},
        quiz_states,
    )


async def track_locks(track_id: str, user: dict):
    locks, _states = await track_prerequisite_evaluation(track_id, user)
    return locks


async def assert_visible(node: dict, user: dict):
    from integrity import can_view_node
    if not is_staff(user) and not await can_view_node(node, user):
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")


async def assert_unlocked(node: dict, user: dict):
    if is_staff(user):
        return
    await assert_visible(node, user)
    locks = await track_locks(node["track_id"], user)
    if str(node["_id"]) in locks:
        raise HTTPException(status_code=403, detail="Conteúdo bloqueado: conclua os pré-requisitos primeiro")


def prerequisite_cycle(relations, source, target):
    """True if adding source->target (source requires target) creates a cycle."""
    edges = {}
    for r in relations:
        if r["type"] == "prerequisite":
            edges.setdefault(r["node_id"], []).append(r["target_id"])
    stack, seen = [target], set()
    while stack:
        cur = stack.pop()
        if cur == source:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(edges.get(cur, []))
    return False


def find_cycles(relations):
    edges = {}
    for r in relations:
        if r["type"] == "prerequisite":
            edges.setdefault(r["node_id"], []).append(r["target_id"])
    color, cycles = {}, []

    def dfs(n, path):
        color[n] = 1
        for m in edges.get(n, []):
            if color.get(m) == 1:
                cycles.append(path[path.index(m):] + [m] if m in path else [n, m])
            elif not color.get(m):
                dfs(m, path + [m])
        color[n] = 2
    for n in list(edges):
        if not color.get(n):
            dfs(n, [n])
    return cycles


@router.get("/tracks/{track_id}/validate", response_model=TrackValidationOut, response_model_exclude_unset=True)
async def validate_track(track_id: str, _: dict = Depends(require("content.read"))):
    nodes = await db.nodes.find({"track_id": track_id}).to_list(10000)
    by_id = {str(n["_id"]): n for n in nodes}
    published = {str(n["_id"]) for n in visible_nodes(nodes)}
    relations = await db.relations.find({"track_id": track_id}).to_list(10000)
    issues = [{"level": "error", "code": "cycle", "node_ids": c,
               "message": "Ciclo de pré-requisitos: " + " → ".join(by_id[i]["title"] for i in c if i in by_id)}
              for c in find_cycles(relations)]
    for r in relations:
        if r["type"] == "prerequisite" and r.get("enforced"):
            tgt = by_id.get(r["target_id"])
            src = by_id.get(r["node_id"])
            if tgt and src and r["target_id"] not in published and r["node_id"] in published:
                issues.append({"level": "warning", "code": "unpublished_prerequisite", "node_ids": [r["node_id"], r["target_id"]],
                               "message": f"\"{src['title']}\" exige \"{tgt['title']}\", que não está publicado — o bloqueio é ignorado para alunos."})
    return {"ok": not any(i["level"] == "error" for i in issues), "issues": issues}


# ---------- Notes ----------
@router.get("/notes", response_model=list[NoteOut], response_model_exclude_unset=True)
async def list_notes(track_id: Optional[str] = None, node_id: Optional[str] = None, limit: int = 2000,
                     skip: int = 0, user: dict = Depends(current_user)):
    q = {"user_id": user["id"], "orphaned": {"$ne": True}}
    if track_id:
        q["track_id"] = track_id
    if node_id:
        q["node_id"] = node_id
    page_size = min(max(limit, 1), 2000)
    notes = await db.notes.find(q).sort("updated_at", -1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    return await _with_titles(notes, user)


@router.put("/notes", response_model=NoteOut | DeletedOut, response_model_exclude_unset=True)
async def upsert_note(body: NoteIn, user: dict = Depends(current_user)):
    node = await db.nodes.find_one({"_id": oid(body.node_id)})
    if not node:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    await assert_visible(node, user)
    key = {"user_id": user["id"], "node_id": body.node_id, "block_id": body.block_id}
    if not body.body.strip():
        await db.notes.delete_one(key)
        return {"deleted": True}
    await db.notes.update_one(key, {"$set": {"body": body.body, "track_id": node["track_id"], "updated_at": now()},
                                    "$setOnInsert": {"created_at": now()}}, upsert=True)
    return ser(await db.notes.find_one(key))


async def _with_titles(items, user):
    from integrity import visible_ids
    allowed = await visible_ids(user, [i["track_id"] for i in items])
    items = [i for i in items if i["node_id"] in allowed]
    node_ids = list({i["node_id"] for i in items})
    nodes = {str(n["_id"]): n for n in await db.nodes.find({"_id": {"$in": [oid(x) for x in node_ids]}},
                                                         {"title": 1, "kind": 1}).to_list(5000)}
    track_ids = list({i["track_id"] for i in items})
    tracks = {str(t["_id"]): t["title"] for t in await db.tracks.find({"_id": {"$in": [oid(x) for x in track_ids]}},
                                                                     {"title": 1}).to_list(500)}
    return [{**ser(i), "node_title": nodes.get(i["node_id"], {}).get("title", "(removido)"),
             "track_title": tracks.get(i["track_id"], "")} for i in items]


# ---------- Reviews ----------
def _due(when: str, node: dict, due_at: Optional[str]):
    if when == "custom":
        if not due_at:
            raise HTTPException(status_code=400, detail="Informe a data da revisão")
        from datetime import datetime, timezone
        d = datetime.fromisoformat(due_at)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    if when == "suggested":
        return now() + timedelta(days=SUGGESTED_DAYS.get(node.get("depth"), 7))
    if when not in REVIEW_BUCKETS:
        raise HTTPException(status_code=400, detail="Opção de revisão inválida")
    return now() + timedelta(days=REVIEW_BUCKETS[when])


@router.post("/reviews", response_model=ReviewOut, response_model_exclude_unset=True)
async def schedule_review(body: ReviewIn, user: dict = Depends(current_user)):
    node = await db.nodes.find_one({"_id": oid(body.node_id)})
    if not node:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    await assert_visible(node, user)
    due = _due(body.when, node, body.due_at)
    key = {"user_id": user["id"], "node_id": body.node_id, "block_id": body.block_id, "status": "pending"}
    for _ in range(2):  # unique partial index: concurrent upserts retry as update
        try:
            await _upsert_review(key, body, node, due)
            break
        except DuplicateKeyError:
            continue
    return ser(await db.reviews.find_one(key))


async def _upsert_review(key, body, node, due):
    await db.reviews.update_one(key, {
        "$set": {"due_at": due, "bucket": body.when, "note": body.note, "track_id": node["track_id"], "updated_at": now()},
        "$setOnInsert": {"created_at": now(), "history": [], "review_count": 0, "last_reviewed_at": None,
                         "ease": None, "interval_days": None}}, upsert=True)


@router.get("/reviews", response_model=list[ReviewOut], response_model_exclude_unset=True)
async def list_reviews(status: str = "pending", track_id: Optional[str] = None, limit: int = 2000,
                       skip: int = 0, user: dict = Depends(current_user)):
    q = {"user_id": user["id"], "status": status, "orphaned": {"$ne": True}}
    if track_id:
        q["track_id"] = track_id
    page_size = min(max(limit, 1), 2000)
    items = await db.reviews.find(q).sort("due_at", 1).skip(max(skip, 0)).limit(page_size).to_list(page_size)
    return await _with_titles(items, user)


@router.post("/reviews/{review_id}/complete", response_model=ReviewOut, response_model_exclude_unset=True)
async def complete_review(review_id: str, body: ReviewDone, user: dict = Depends(current_user)):
    rev = await db.reviews.find_one({"_id": oid(review_id), "user_id": user["id"]})
    if not rev:
        raise HTTPException(status_code=404, detail="Revisão não encontrada")
    entry = {"at": now(), "outcome": body.outcome}
    update = {"$push": {"history": entry}, "$inc": {"review_count": 1},
              "$set": {"last_reviewed_at": now(), "updated_at": now()}}
    if body.reschedule:
        node = await db.nodes.find_one({"_id": oid(rev["node_id"])}) or {}
        update["$set"].update(due_at=_due(body.reschedule, node, None), bucket=body.reschedule)
    else:
        update["$set"]["status"] = "done"
    await db.reviews.update_one({"_id": rev["_id"]}, update)
    await db.learning_events.insert_one({"user_id": user["id"], "track_id": rev["track_id"], "node_id": rev["node_id"],
                                         "block_id": rev.get("block_id"), "type": "review", "data": {"outcome": body.outcome},
                                         "at": now()})
    return ser(await db.reviews.find_one({"_id": rev["_id"]}))


@router.delete("/reviews/{review_id}", response_model=OkOut)
async def delete_review(review_id: str, user: dict = Depends(current_user)):
    await db.reviews.update_one({"_id": oid(review_id), "user_id": user["id"]},
                                {"$set": {"status": "dismissed", "updated_at": now()}})
    return {"ok": True}
