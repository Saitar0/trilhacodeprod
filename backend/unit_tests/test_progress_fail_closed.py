"""Unit coverage for progress writes when MongoDB cannot confirm persistence."""

import asyncio
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import ServerSelectionTimeoutError

import services.progress as progress


def test_progress_write_returns_service_unavailable_when_storage_fails(monkeypatch):
    node_id = str(ObjectId())
    node = {"_id": ObjectId(node_id), "track_id": str(ObjectId()), "title": "Test node"}

    async def get_node(_node_id):
        return node

    async def allowed(_node, _user):
        return None

    async def no_pending_event(_key):
        return None

    class ProgressCollection:
        async def find_one(self, *_args, **_kwargs):
            raise ServerSelectionTimeoutError("test-only unavailable")

    monkeypatch.setattr(progress, "_node", get_node)
    monkeypatch.setattr(progress, "assert_unlocked", allowed)
    monkeypatch.setattr(progress, "_flush_pending_progress_event", no_pending_event)
    monkeypatch.setattr(progress, "db", SimpleNamespace(progress=ProgressCollection()))

    with pytest.raises(HTTPException) as error:
        asyncio.run(progress.set_progress({
            "node_id": node_id, "status": "completed", "data": {},
        }, {"id": "isolated-user"}))
    assert error.value.status_code == 503
