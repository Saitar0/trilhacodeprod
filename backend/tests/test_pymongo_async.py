"""Integration coverage for the native PyMongo Async driver."""

import asyncio
import uuid

from bson import ObjectId
from pymongo import AsyncMongoClient

from core import client as facade_client
from database import client, db


def test_database_and_core_share_one_async_client():
    assert isinstance(client, AsyncMongoClient)
    assert facade_client is client
    assert db.client is client


def test_async_crud_cursors_aggregation_and_object_id_round_trip(event_loop):
    marker = f"pymongo-async-{uuid.uuid4().hex}"
    inserted_ids = []

    async def exercise_driver():
        loop = asyncio.get_running_loop()
        assert loop is event_loop

        collection = db.pymongo_async_migration_checks
        try:
            inserted = await collection.insert_many([
                {"marker": marker, "order": 2},
                {"marker": marker, "order": 1},
            ])
            inserted_ids.extend(inserted.inserted_ids)
            assert all(isinstance(value, ObjectId) for value in inserted.inserted_ids)

            cursor = collection.find({"marker": marker}).sort("order", 1)
            documents = await cursor.to_list(length=10)
            assert [document["order"] for document in documents] == [1, 2]
            assert all(isinstance(document["_id"], ObjectId) for document in documents)

            iterated = [document async for document in collection.find({"marker": marker})]
            assert len(iterated) == 2

            aggregate_cursor = await collection.aggregate([
                {"$match": {"marker": marker}},
                {"$group": {"_id": "$marker", "count": {"$sum": 1}}},
            ])
            grouped = await aggregate_cursor.to_list(length=10)
            assert grouped == [{"_id": marker, "count": 2}]

            fetched = await collection.find_one({"_id": inserted_ids[0]})
            assert fetched is not None and fetched["_id"] == inserted_ids[0]
            result = await collection.delete_many({"marker": marker})
            assert result.deleted_count == 2
        finally:
            if inserted_ids:
                await collection.delete_many({"_id": {"$in": inserted_ids}})

    event_loop.run_until_complete(exercise_driver())
