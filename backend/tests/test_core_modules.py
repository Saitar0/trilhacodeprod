"""Focused coverage for helpers extracted from the legacy core facade."""

from datetime import datetime, timezone

import pytest
from bson import ObjectId
from fastapi import HTTPException

import core
from constants import PERMISSIONS
from database import client, db
from permissions import has_permission, is_staff
from security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from serialization import oid, ser


def test_compatibility_facade_preserves_shared_mongo_objects():
    assert core.client is client
    assert core.db is db


def test_access_and_refresh_tokens_keep_their_contract():
    session_id = "s" * 43
    access = decode_token(
        create_access_token("user-id", "user@example.com", session_id=session_id), "access"
    )
    refresh = decode_token(create_refresh_token("user-id", session_id=session_id), "refresh")

    assert access["sub"] == "user-id"
    assert access["email"] == "user@example.com"
    assert access["type"] == "access"
    assert access["sid"] == session_id
    assert refresh["sub"] == "user-id"
    assert refresh["type"] == "refresh"
    assert refresh["sid"] == session_id
    with pytest.raises(HTTPException) as error:
        decode_token(create_refresh_token("user-id", session_id=session_id), "access")
    assert error.value.status_code == 401
    with pytest.raises(HTTPException) as error:
        decode_token("invalid-token", "access")
    assert error.value.status_code == 401


def test_password_helpers_and_role_permissions_keep_their_contract():
    hashed = hash_password("Test@1234")
    assert verify_password("Test@1234", hashed)
    assert not verify_password("incorrect", hashed)

    assert is_staff({"role": "admin"})
    assert is_staff({"role": "editor"})
    assert not is_staff({"role": "student"})
    assert "users.manage" in PERMISSIONS["admin"]
    assert "users.manage" not in PERMISSIONS["editor"]
    assert "content.write" not in PERMISSIONS["student"]


def test_role_authorization_keeps_admin_editor_and_student_boundaries():
    assert has_permission({"role": "admin"}, "users.manage")
    assert has_permission({"role": "editor"}, "content.write")
    assert not has_permission({"role": "editor"}, "users.manage")
    assert not has_permission({"role": "student"}, "users.manage")
    assert not has_permission({"role": "student"}, "content.write")


def test_object_id_and_nested_serialization_keep_their_contract():
    object_id = ObjectId()
    timestamp = datetime(2026, 1, 2, tzinfo=timezone.utc)
    document = {"_id": object_id, "password_hash": "hidden", "nested": [object_id, timestamp]}

    assert oid(str(object_id)) == object_id
    assert ser(document) == {
        "id": str(object_id),
        "nested": [str(object_id), timestamp.isoformat()],
    }
    with pytest.raises(HTTPException) as error:
        oid("not-an-object-id")
    assert error.value.status_code == 404
