"""Shared MongoDB client and database for the backend process."""

from pymongo import AsyncMongoClient

from settings import settings

client = AsyncMongoClient(settings.mongo_url, tz_aware=True)
db = client[settings.db_name]
