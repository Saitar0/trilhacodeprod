"""MongoDB identifier conversion and API document serialization."""

from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException

_PRIVATE_USER_FIELDS = {
    "password_hash",
    "email_verification_token_hash",
    "email_verification_expires_at",
    "password_reset_token_hash",
    "password_reset_expires_at",
}


def oid(value):
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")


def ser(value):
    if isinstance(value, list):
        return [ser(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k == "_id":
                out["id"] = str(v)
            elif k in _PRIVATE_USER_FIELDS:
                continue
            else:
                out[k] = ser(v)
        return out
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value
