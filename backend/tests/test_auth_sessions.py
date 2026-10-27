"""Integration coverage for server-side session revocation."""

import asyncio
import uuid
from datetime import timedelta

import jwt

from constants import JWT_ALGORITHM
from core_utils import now
from database import db
from security import create_access_token, create_refresh_token, decode_token
from services.sessions import session_id_digest
from settings import settings

API = "/api"


def _new_verified_login(session_factory, create_verified_user, password="Long-passphrase-12"):
    email = f"session_{uuid.uuid4().hex}@example.com"
    session = session_factory()
    create_verified_user(session, email, password=password)
    return email, password, session


def _copy_auth_cookies(target, access_token, refresh_token):
    target.cookies.set("access_token", access_token)
    target.cookies.set("refresh_token", refresh_token)


def test_login_creates_hashed_server_session_and_tokens_validate(
    session_factory, create_verified_user, event_loop,
):
    email, _, session = _new_verified_login(session_factory, create_verified_user)
    access_token = session.cookies.get("access_token")
    refresh_token = session.cookies.get("refresh_token")
    access = decode_token(access_token, "access")
    refresh = decode_token(refresh_token, "refresh")

    assert access["sid"] == refresh["sid"]
    assert session.get(f"{API}/auth/me").status_code == 200
    assert session.post(f"{API}/auth/refresh").status_code == 200

    user = event_loop.run_until_complete(db.users.find_one({"email": email}))
    record = event_loop.run_until_complete(
        db.auth_sessions.find_one({"_id": session_id_digest(access["sid"])})
    )
    assert record["user_id"] == str(user["_id"])
    assert record["expires_at"] > now()
    assert record["revoked_at"] is None
    assert record["_id"] != access["sid"]
    assert access_token not in repr(record)
    assert refresh_token not in repr(record)


def test_logout_revokes_only_its_session_and_is_idempotent(
    session_factory, create_verified_user, event_loop,
):
    email, password, session_a = _new_verified_login(session_factory, create_verified_user)
    session_b = session_factory()
    assert session_b.post(
        f"{API}/auth/login", json={"email": email, "password": password},
    ).status_code == 200

    access_a = session_a.cookies.get("access_token")
    refresh_a = session_a.cookies.get("refresh_token")
    refresh_b = session_b.cookies.get("refresh_token")
    sid_a = decode_token(refresh_a, "refresh")["sid"]
    sid_b = decode_token(refresh_b, "refresh")["sid"]
    assert sid_a != sid_b
    assert session_a.get(f"{API}/auth/me").status_code == 200
    assert session_a.post(f"{API}/auth/refresh").status_code == 200

    assert session_a.post(f"{API}/auth/logout").status_code == 200
    assert session_a.cookies.get("access_token") is None
    assert session_a.cookies.get("refresh_token") is None
    replay_a = session_factory()
    _copy_auth_cookies(replay_a, access_a, refresh_a)
    assert replay_a.get(f"{API}/auth/me").status_code == 401
    assert replay_a.post(f"{API}/auth/refresh").status_code == 401
    bearer_replay = session_factory()
    assert bearer_replay.get(
        f"{API}/auth/me", headers={"Authorization": f"Bearer {access_a}"},
    ).status_code == 401
    assert replay_a.post(f"{API}/auth/logout").status_code == 200
    assert session_b.get(f"{API}/auth/me").status_code == 200
    assert session_b.post(f"{API}/auth/refresh").status_code == 200

    record_a = event_loop.run_until_complete(
        db.auth_sessions.find_one({"_id": session_id_digest(sid_a)})
    )
    record_b = event_loop.run_until_complete(
        db.auth_sessions.find_one({"_id": session_id_digest(sid_b)})
    )
    assert record_a["revoked_at"] is not None
    assert record_b["revoked_at"] is None


def test_refresh_racing_with_logout_cannot_restore_a_revoked_session(
    session_factory, create_verified_user, event_loop,
):
    _, _, session = _new_verified_login(session_factory, create_verified_user)
    access_token = session.cookies.get("access_token")
    refresh_token = session.cookies.get("refresh_token")
    logout_client = session_factory()
    refresh_client = session_factory()
    for client in (logout_client, refresh_client):
        client.cookies.set("access_token", access_token)
        client.cookies.set("refresh_token", refresh_token)

    async def race():
        return await asyncio.gather(
            logout_client._client.post(f"{API}/auth/logout"),
            refresh_client._client.post(f"{API}/auth/refresh"),
        )

    logout_response, refresh_response = event_loop.run_until_complete(race())
    raced_access_token = refresh_client.cookies.get("access_token")
    assert logout_response.status_code == 200
    assert refresh_response.status_code in {200, 401}

    replay = session_factory()
    _copy_auth_cookies(replay, raced_access_token, refresh_token)
    assert replay.get(f"{API}/auth/me").status_code == 401
    assert replay.post(f"{API}/auth/refresh").status_code == 401


def test_expired_missing_and_unknown_session_tokens_are_rejected(
    session_factory, create_verified_user,
):
    email, _, session = _new_verified_login(session_factory, create_verified_user)
    user = session.get(f"{API}/auth/me").json()
    unknown_sid = "x" * 43

    unknown = session_factory()
    unknown.cookies.set(
        "access_token",
        create_access_token(user["id"], email, session_id=unknown_sid),
    )
    unknown.cookies.set(
        "refresh_token",
        create_refresh_token(user["id"], session_id=unknown_sid),
    )
    assert unknown.get(f"{API}/auth/me").status_code == 401
    assert unknown.post(f"{API}/auth/refresh").status_code == 401

    legacy_claims = {
        "sub": user["id"],
        "email": email,
        "ver": 0,
        "type": "access",
        "exp": now() + timedelta(minutes=5),
    }
    legacy = session_factory()
    legacy.cookies.set(
        "access_token",
        jwt.encode(legacy_claims, settings.jwt_secret, algorithm=JWT_ALGORITHM),
    )
    legacy_claims["type"] = "refresh"
    legacy.cookies.set(
        "refresh_token",
        jwt.encode(legacy_claims, settings.jwt_secret, algorithm=JWT_ALGORITHM),
    )
    assert legacy.get(f"{API}/auth/me").status_code == 401
    assert legacy.post(f"{API}/auth/refresh").status_code == 401

    expired_claims = decode_token(session.cookies.get("access_token"), "access")
    expired_claims["exp"] = now() - timedelta(seconds=1)
    expired = session_factory()
    expired.cookies.set(
        "access_token",
        jwt.encode(expired_claims, settings.jwt_secret, algorithm=JWT_ALGORITHM),
    )
    assert expired.get(f"{API}/auth/me").status_code == 401


def test_logout_database_failure_is_reported_and_clears_client_cookies(
    session_factory, create_verified_user, monkeypatch,
):
    from pymongo.errors import ServerSelectionTimeoutError

    import routes_auth

    _, _, session = _new_verified_login(session_factory, create_verified_user)

    async def unavailable(*_args, **_kwargs):
        raise ServerSelectionTimeoutError("test-only unavailable")

    monkeypatch.setattr(routes_auth, "revoke_session", unavailable)
    response = session.post(f"{API}/auth/logout")

    assert response.status_code == 503
    assert session.cookies.get("access_token") is None
    assert session.cookies.get("refresh_token") is None


def test_login_does_not_issue_cookies_when_session_storage_fails(
    session_factory, mailbox_token, monkeypatch,
):
    import routes_auth

    email = f"session_store_{uuid.uuid4().hex}@example.com"
    password = "Long-passphrase-12"
    session = session_factory()
    assert session.post(
        f"{API}/auth/register",
        json={"name": "Session Store", "email": email, "password": password},
    ).status_code == 202
    token = mailbox_token(email, "Confirme seu e-mail")
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 200

    async def unavailable(_user_id):
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Session storage unavailable")

    monkeypatch.setattr(routes_auth, "create_session", unavailable)
    response = session.post(
        f"{API}/auth/login", json={"email": email, "password": password},
    )

    assert response.status_code == 503
    assert session.cookies.get("access_token") is None
    assert session.cookies.get("refresh_token") is None


def test_deactivated_user_cannot_use_existing_or_new_sessions(
    session_factory, create_verified_user, event_loop,
):
    email, password, session = _new_verified_login(session_factory, create_verified_user)
    event_loop.run_until_complete(
        db.users.update_one({"email": email}, {"$set": {"is_active": False}})
    )

    assert session.get(f"{API}/auth/me").status_code == 401
    assert session.post(f"{API}/auth/refresh").status_code == 401
    new_session = session_factory()
    assert new_session.post(
        f"{API}/auth/login", json={"email": email, "password": password},
    ).status_code == 401


def test_password_change_revokes_all_existing_sessions(
    session_factory, create_verified_user,
):
    email, password, session_a = _new_verified_login(session_factory, create_verified_user)
    session_b = session_factory()
    assert session_b.post(
        f"{API}/auth/login", json={"email": email, "password": password},
    ).status_code == 200

    changed = session_a.post(
        f"{API}/auth/password",
        json={"current_password": password, "password": "New-password-value-34"},
    )
    assert changed.status_code == 200
    assert session_a.get(f"{API}/auth/me").status_code == 401
    assert session_a.post(f"{API}/auth/refresh").status_code == 401
    assert session_b.get(f"{API}/auth/me").status_code == 401
    assert session_b.post(f"{API}/auth/refresh").status_code == 401


def test_auth_session_ttl_index_is_declared(event_loop):
    indexes = event_loop.run_until_complete(db.auth_sessions.index_information())
    assert any(
        index.get("key") == [("expires_at", 1)]
        and index.get("expireAfterSeconds") == 0
        for index in indexes.values()
    )
