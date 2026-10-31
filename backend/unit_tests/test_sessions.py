"""Unit coverage for fail-closed session storage behavior."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pymongo.errors import ServerSelectionTimeoutError

import services.sessions as sessions


def test_session_validation_fails_closed_when_mongo_is_unavailable(monkeypatch):
    async def unavailable(*_args, **_kwargs):
        raise ServerSelectionTimeoutError("test-only unavailable")

    monkeypatch.setattr(
        sessions,
        "db",
        SimpleNamespace(auth_sessions=SimpleNamespace(find_one=unavailable)),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(sessions.require_active_session("s" * 43, "user-id"))
    assert error.value.status_code == 503


def test_login_session_creation_fails_closed_when_mongo_is_unavailable(monkeypatch):
    async def unavailable(*_args, **_kwargs):
        raise ServerSelectionTimeoutError("test-only unavailable")

    monkeypatch.setattr(
        sessions,
        "db",
        SimpleNamespace(auth_sessions=SimpleNamespace(insert_one=unavailable)),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(sessions.create_session("user-id"))
    assert error.value.status_code == 503
