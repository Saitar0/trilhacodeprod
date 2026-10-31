"""Explicit, resource-scoped reviewer access for the isolated learning journey.

This is a deny-by-default Beta 6 adapter, not an operational grant-management
system. Scope records are provisioned outside the learner API and require both
the existing role permission and an active per-track record.
"""

from fastapi import HTTPException

from constants import PERMISSIONS
from database import db

READ_SUBMISSIONS = "submissions.read"
GRADE_SUBMISSIONS = "submissions.grade"


def scope_id(user_id: str, track_id: str) -> str:
    return f"{user_id}:{track_id}"


async def authorized_track_ids(user: dict, operation: str) -> list[str]:
    if operation not in {READ_SUBMISSIONS, GRADE_SUBMISSIONS}:
        return []
    if GRADE_SUBMISSIONS not in PERMISSIONS.get(user.get("role", ""), set()):
        return []
    cursor = db.learning_review_scopes.find({
        "user_id": user.get("id"),
        "state": "active",
        "operations": operation,
    }, {"track_id": 1})
    rows = await cursor.to_list(500)
    return sorted({row["track_id"] for row in rows if isinstance(row.get("track_id"), str)})


async def require_track_scope(user: dict, track_id: str, operation: str) -> None:
    allowed = await authorized_track_ids(user, operation)
    if track_id not in allowed:
        # Keep existence and scope indistinguishable to callers.
        raise HTTPException(status_code=404, detail="Submissão não encontrada")

