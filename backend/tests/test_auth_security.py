"""Integration/regression coverage for account verification and recovery flows."""
import uuid
from datetime import timedelta

import pytest

from core_utils import now
from database import db
from security import create_access_token

API = "/api"


def test_registration_requires_long_password_and_email_verification(session_factory, mailbox_token, event_loop):
    session = session_factory()
    email = f"verify_{uuid.uuid4().hex}@example.com"
    short = session.post(f"{API}/auth/register", json={"name": "New user", "email": email, "password": "shortpass1"})
    assert short.status_code == 422

    registration = session.post(f"{API}/auth/register", json={
        "name": "New user", "email": email, "password": "Long-passphrase-12"})
    assert registration.status_code == 202
    assert "access_token" not in session.cookies and "refresh_token" not in session.cookies
    assert session.post(f"{API}/auth/login", json={"email": email, "password": "Long-passphrase-12"}).status_code == 401

    user = event_loop.run_until_complete(db.users.find_one({"email": email}))
    assert user is not None
    tokenized = create_access_token(str(user["_id"]), email, user.get("token_version", 0))
    assert session.get(f"{API}/profile", headers={"Authorization": f"Bearer {tokenized}"}).status_code == 403

    token = mailbox_token(email, "Confirme seu e-mail")
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 200
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 400
    user = event_loop.run_until_complete(db.users.find_one({"email": email}))
    assert user["email_verified"] is True
    assert "email_verification_token_hash" not in user
    assert session.post(f"{API}/auth/login", json={"email": email, "password": "Long-passphrase-12"}).status_code == 200
    assert session.get(f"{API}/profile").status_code == 200


def test_registration_and_recovery_responses_do_not_enumerate_accounts(session_factory, mailbox_token):
    session = session_factory()
    email = f"privacy_{uuid.uuid4().hex}@example.com"
    payload = {"name": "Privacy", "email": email, "password": "Long-passphrase-12"}
    first = session.post(f"{API}/auth/register", json=payload)
    duplicate = session.post(f"{API}/auth/register", json=payload)
    assert first.status_code == duplicate.status_code == 202
    assert first.json() == duplicate.json()

    token = mailbox_token(email, "Confirme seu e-mail")
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 200
    created = session.post(f"{API}/auth/password-reset-request", json={"email": email})
    unknown = session.post(f"{API}/auth/password-reset-request", json={"email": f"absent_{uuid.uuid4().hex}@example.com"})
    assert created.status_code == unknown.status_code == 202
    assert created.json() == unknown.json()
    assert session.post(f"{API}/auth/resend-verification", json={"email": email}).json() == session.post(
        f"{API}/auth/resend-verification", json={"email": f"absent_{uuid.uuid4().hex}@example.com"}
    ).json()

    assert session.post(f"{API}/auth/resend-verification", json={"email": email}).status_code == 202
    assert mailbox_token(email, "Confirme seu e-mail") == token


def test_expired_email_confirmation_token_is_rejected(session_factory, mailbox_token, event_loop):
    session = session_factory()
    email = f"expired_{uuid.uuid4().hex}@example.com"
    assert session.post(f"{API}/auth/register", json={
        "name": "Expired", "email": email, "password": "Long-passphrase-12"}).status_code == 202
    token = mailbox_token(email, "Confirme seu e-mail")

    async def expire():
        await db.users.update_one({"email": email}, {"$set": {
            "email_verification_expires_at": now() - timedelta(seconds=1),
        }})

    event_loop.run_until_complete(expire())
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 400
    assert event_loop.run_until_complete(db.users.find_one({"email": email}))["email_verified"] is False


def test_registration_and_mail_requests_are_rate_limited_per_recipient(session_factory, mailbox_token):
    session = session_factory()
    email = f"limited_{uuid.uuid4().hex}@example.com"
    payload = {"name": "Limited", "email": email, "password": "Long-passphrase-12"}
    responses = [session.post(f"{API}/auth/register", json=payload) for _ in range(3)]
    assert [response.status_code for response in responses] == [202, 202, 202]
    assert session.post(f"{API}/auth/register", json=payload).status_code == 429

    token = mailbox_token(email, "Confirme seu e-mail")
    assert session.post(f"{API}/auth/verify-email", json={"token": token}).status_code == 200
    reset_responses = [session.post(f"{API}/auth/password-reset-request", json={"email": email}) for _ in range(3)]
    assert [response.status_code for response in reset_responses] == [202, 202, 202]
    assert session.post(f"{API}/auth/password-reset-request", json={"email": email}).status_code == 429


def test_password_reset_is_single_use_and_revokes_existing_sessions(session_factory, mailbox_token, create_verified_user):
    session = session_factory()
    email = f"reset_{uuid.uuid4().hex}@example.com"
    password = "Original-passphrase-12"
    create_verified_user(session, email, password=password)
    assert session.post(f"{API}/auth/password-reset-request", json={"email": email}).status_code == 202
    token = mailbox_token(email, "Redefina sua senha")
    too_short = session.post(f"{API}/auth/password-reset", json={"token": token, "password": "shortpass1"})
    assert too_short.status_code == 422
    changed = session.post(f"{API}/auth/password-reset", json={"token": token, "password": "Replacement-passphrase-24"})
    assert changed.status_code == 200
    assert session.post(f"{API}/auth/password-reset", json={"token": token, "password": "Another-passphrase-25"}).status_code == 400
    assert session.get(f"{API}/auth/me").status_code == 401
    assert session.post(f"{API}/auth/login", json={"email": email, "password": password}).status_code == 401
    assert session.post(f"{API}/auth/login", json={"email": email, "password": "Replacement-passphrase-24"}).status_code == 200


def test_password_change_requires_minimum_and_revokes_current_session(session_factory, create_verified_user):
    session = session_factory()
    email = f"change_{uuid.uuid4().hex}@example.com"
    password = "Original-passphrase-12"
    create_verified_user(session, email, password=password)
    assert session.post(f"{API}/auth/password", json={
        "current_password": password, "password": "shortpass1"}).status_code == 422
    changed = session.post(f"{API}/auth/password", json={
        "current_password": password, "password": "New-passphrase-value-34"})
    assert changed.status_code == 200
    assert session.get(f"{API}/auth/me").status_code == 401


def test_account_token_hashes_are_not_exposed_by_user_endpoints(
    session_factory, create_verified_user, admin_session,
):
    session = session_factory()
    email = f"token_fields_{uuid.uuid4().hex}@example.com"
    create_verified_user(session, email)
    assert session.post(f"{API}/auth/password-reset-request", json={"email": email}).status_code == 202

    own_profile = session.get(f"{API}/auth/me").json()
    admin_users = admin_session.get(f"{API}/users?limit=1000").json()
    admin_copy = next(user for user in admin_users if user["email"] == email)
    private_fields = {
        "password_hash",
        "email_verification_token_hash",
        "email_verification_expires_at",
        "password_reset_token_hash",
        "password_reset_expires_at",
    }
    assert private_fields.isdisjoint(own_profile)
    assert private_fields.isdisjoint(admin_copy)


def test_auth_rate_limiter_rejects_over_budget_requests(event_loop):
    from fastapi import HTTPException

    from services.auth import rate_limit

    key = uuid.uuid4().hex

    async def run():
        await rate_limit("test", key, 1, 3600)
        with pytest.raises(HTTPException) as error:
            await rate_limit("test", key, 1, 3600)
        return error.value.status_code

    assert event_loop.run_until_complete(run()) == 429


def test_rate_limit_identifiers_use_a_keyed_hash():
    import hmac

    from routes_auth import _rate_key
    from settings import settings

    email = "example@example.com"
    assert _rate_key(email) == _rate_key(email.upper())
    assert _rate_key(email) == hmac.digest(settings.jwt_secret.encode(), email.encode(), "sha256").hex()
    assert _rate_key(email) != hmac.digest(b"different-secret-key", email.encode(), "sha256").hex()
