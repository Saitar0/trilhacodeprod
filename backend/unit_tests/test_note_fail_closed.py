"""Unit coverage for note writes when MongoDB cannot confirm persistence."""

import asyncio
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import ServerSelectionTimeoutError

import learning
from schemas.learning import NoteIn


def test_note_write_returns_service_unavailable_when_storage_fails(monkeypatch):
    node_id = str(ObjectId())

    class Nodes:
        async def find_one(self, _query):
            return {"_id": ObjectId(node_id), "track_id": str(ObjectId())}

    class ContentBlocks:
        async def find_one(self, _query):
            return None

    class Notes:
        async def find_one(self, _query):
            raise ServerSelectionTimeoutError("test-only unavailable")

    async def visible(_node, _user):
        return None

    monkeypatch.setattr(
        learning,
        "db",
        SimpleNamespace(nodes=Nodes(), content_blocks=ContentBlocks(), notes=Notes()),
    )
    monkeypatch.setattr(learning, "assert_visible", visible)

    with pytest.raises(HTTPException) as error:
        asyncio.run(learning.upsert_note(
            NoteIn(node_id=node_id, body="nota", expected_version=0),
            {"id": "isolated-user"},
        ))
    assert error.value.status_code == 503
