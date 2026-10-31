from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from constants import PERMISSIONS as ACTIVE_PERMISSIONS  # noqa: E402
from curriculum_contract.experimental_editorial_grants import (  # noqa: E402
    EditorialTrackGrant,
    GrantState,
    GrantValidationError,
)


def _grant(**overrides):
    values = {
        "actor_id": "c12_actor",
        "track_id": "c12_track",
        "allowed_operations": ("block.update",),
        "granted_by": "c12_admin",
        "granted_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return EditorialTrackGrant(**values)


def test_grant_document_is_closed_roundtrippable_and_scoped():
    grant = _grant()
    stored = grant.to_document()
    assert EditorialTrackGrant.from_document(stored) == grant
    assert grant.allows("c12_actor", "c12_track", "block.update", role="editor")
    assert not grant.allows("c12_actor", "other_track", "block.update", role="editor")
    assert not grant.allows("c12_actor", "c12_track", "content.publish", role="editor")
    with pytest.raises(GrantValidationError):
        EditorialTrackGrant.from_document(stored | {"payload": "private"})
    with pytest.raises(GrantValidationError):
        EditorialTrackGrant.from_document(stored | {"schema_version": True})


def test_global_admin_scope_requires_explicit_marker_and_admin_role():
    with pytest.raises(GrantValidationError):
        _grant(track_id="*", global_admin_scope=False)
    global_grant = _grant(track_id="*", global_admin_scope=True)
    assert global_grant.allows("c12_actor", "any_track", "block.update", role="admin")
    assert not global_grant.allows("c12_actor", "any_track", "block.update", role="editor")


def test_revoked_grant_requires_actor_and_timestamp():
    with pytest.raises(GrantValidationError):
        _grant(state=GrantState.REVOKED)
    revoked = _grant(
        state=GrantState.REVOKED,
        authorization_epoch=2,
        revoked_by="c12_revoker",
        revoked_at=datetime.now(timezone.utc),
    )
    assert not revoked.allows("c12_actor", "c12_track", "block.update", role="editor")


def test_grant_rejects_unreviewed_operations_and_naive_timestamps():
    with pytest.raises(GrantValidationError):
        _grant(allowed_operations=("arbitrary.operation",))
    with pytest.raises(GrantValidationError):
        _grant(granted_at=datetime(2026, 1, 1))
    with pytest.raises(GrantValidationError):
        _grant(allowed_operations=("block.update", 1))


class _MemoryCollection:
    def __init__(self, rows):
        self.rows = rows

    async def find_one(self, query, projection=None):
        for row in self.rows:
            if self._matches(row, query):
                return dict(row)
        return None

    async def update_one(self, query, update):
        for row in self.rows:
            if self._matches(row, query):
                for key, value in update.get("$set", {}).items():
                    row[key] = value
                for key, value in update.get("$inc", {}).items():
                    row[key] = row.get(key, 0) + value
                return SimpleNamespace(matched_count=1)
        return SimpleNamespace(matched_count=0)

    @staticmethod
    def _matches(row, query):
        for key, expected in query.items():
            actual = row.get(key)
            if isinstance(expected, dict) and "$gt" in expected:
                if actual is None or actual <= expected["$gt"]:
                    return False
            elif actual != expected:
                return False
        return True


class _Request:
    def __init__(self, token):
        self.cookies = {}
        self.headers = {"Authorization": f"Bearer {token}"}
        self.state = SimpleNamespace()


@pytest.fixture
def isolated_security(monkeypatch):
    """Load the real security/session source with synthetic in-memory collections."""
    user_id = ObjectId()
    session_id = "c12-session-" + "s" * 32
    now = datetime.now(timezone.utc)
    db = SimpleNamespace(
        users=_MemoryCollection([{
            "_id": user_id,
            "email": "synthetic@example.test",
            "role": "editor",
            "email_verified": True,
            "token_version": 0,
            "is_active": True,
        }]),
        auth_sessions=_MemoryCollection([{
            "_id": __import__("hashlib").sha256(session_id.encode()).hexdigest(),
            "user_id": str(user_id),
            "created_at": now,
            "expires_at": now + timedelta(hours=1),
            "revoked_at": None,
        }]),
    )
    database_module = types.ModuleType("database")
    database_module.db = db
    settings_module = types.ModuleType("settings")
    settings_module.settings = SimpleNamespace(jwt_secret="c12-only-synthetic-jwt-signing-key-32-bytes")
    monkeypatch.setitem(sys.modules, "database", database_module)
    monkeypatch.setitem(sys.modules, "settings", settings_module)

    sessions_path = BACKEND / "services" / "sessions.py"
    sessions_spec = importlib.util.spec_from_file_location("services.sessions", sessions_path)
    sessions_module = importlib.util.module_from_spec(sessions_spec)
    monkeypatch.setitem(sys.modules, "services.sessions", sessions_module)
    sessions_spec.loader.exec_module(sessions_module)

    security_path = BACKEND / "security.py"
    security_spec = importlib.util.spec_from_file_location("_c12_security_under_test", security_path)
    security_module = importlib.util.module_from_spec(security_spec)
    security_spec.loader.exec_module(security_module)
    token = security_module.create_access_token(
        str(user_id), "synthetic@example.test", 0, session_id=session_id,
    )
    return SimpleNamespace(
        security=security_module,
        sessions=sessions_module,
        db=db,
        user_id=user_id,
        session_id=session_id,
        token=token,
    )


def test_actual_security_source_accepts_synthetic_jwt_and_reloads_current_role(isolated_security):
    import asyncio

    context = isolated_security
    user = asyncio.run(context.security.current_user(_Request(context.token)))
    assert user["role"] == "editor"
    assert "content.write" in user["permissions"]

    context.db.users.rows[0]["role"] = "student"
    changed = asyncio.run(context.security.current_user(_Request(context.token)))
    assert changed["role"] == "student"
    assert "content.write" not in changed["permissions"]


def test_actual_security_source_rejects_expired_malformed_and_revoked_session(isolated_security):
    import asyncio

    import jwt

    context = isolated_security
    expired = jwt.encode({
        "sub": str(context.user_id), "sid": context.session_id, "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=5),
    }, "c12-only-synthetic-jwt-signing-key-32-bytes", algorithm="HS256")
    with pytest.raises(HTTPException) as expired_error:
        asyncio.run(context.security.current_user(_Request(expired)))
    assert expired_error.value.status_code == 401
    with pytest.raises(HTTPException) as malformed_error:
        asyncio.run(context.security.current_user(_Request("not-a-jwt")))
    assert malformed_error.value.status_code == 401

    assert asyncio.run(context.sessions.revoke_session(context.session_id, str(context.user_id)))
    with pytest.raises(HTTPException) as revoked_error:
        asyncio.run(context.security.current_user(_Request(context.token)))
    assert revoked_error.value.status_code == 401


def test_actual_security_source_rejects_inactive_user_and_changed_token_version(isolated_security):
    import asyncio

    context = isolated_security
    context.db.users.rows[0]["token_version"] = 1
    with pytest.raises(HTTPException) as error:
        asyncio.run(context.security.current_user(_Request(context.token)))
    assert error.value.status_code == 401
    context.db.users.rows[0]["token_version"] = 0
    context.db.users.rows[0]["is_active"] = False
    with pytest.raises(HTTPException) as inactive_error:
        asyncio.run(context.security.current_user(_Request(context.token)))
    assert inactive_error.value.status_code == 401


def test_experimental_role_permission_matrix_matches_versioned_application_constants():
    from curriculum_contract.experimental_editorial_iam_authority import _ROLE_PERMISSIONS

    assert {role: set(values) for role, values in _ROLE_PERMISSIONS.items()} == {
        role: set(values) for role, values in ACTIVE_PERMISSIONS.items()
    }
