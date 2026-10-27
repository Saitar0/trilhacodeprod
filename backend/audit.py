"""Write user actions to the shared edit history collection."""

from core_utils import now
from database import db


async def audit(user: dict, entity: str, entity_id: str, action: str, track_id: str = None, summary: str = ""):
    await db.edit_history.insert_one({
        "entity": entity, "entity_id": entity_id, "action": action, "track_id": track_id,
        "summary": summary, "user_id": user["id"], "user_name": user.get("name", ""), "at": now(),
    })
