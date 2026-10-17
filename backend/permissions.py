"""Role permission policy and FastAPI authorization dependencies."""

from fastapi import Depends, HTTPException

from constants import PERMISSIONS
from security import current_user


def has_permission(user: dict, perm: str) -> bool:
    return perm in PERMISSIONS.get(user["role"], set())


def require(perm: str):
    async def dep(user: dict = Depends(current_user)):
        if not has_permission(user, perm):
            raise HTTPException(status_code=403, detail="Permissão insuficiente")
        return user
    return dep


def is_staff(user: dict) -> bool:
    return "content.read" in PERMISSIONS.get(user["role"], set())


def can_view_track(track: dict, user: dict) -> bool:
    """Return whether a user may read a track's metadata and content tree."""
    return is_staff(user) or (
        track.get("status") == "published" and track.get("visibility") == "public"
    )
