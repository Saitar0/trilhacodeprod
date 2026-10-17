"""Isolated API fixtures backed by a disposable MongoDB database."""
import asyncio
import os
import uuid

import httpx
import pytest
from pymongo import MongoClient

from test_support.mongo_target import make_disposable_mongo_url

MONGO_URL = os.environ.get("MONGO_URL_TEST", "mongodb://localhost:27017")
_db_name = f"test_{uuid.uuid4().hex}"
_mongo_url = make_disposable_mongo_url(MONGO_URL, _db_name)

# server/core read settings at import time. Point them at this run's disposable DB.
os.environ["MONGO_URL"] = _mongo_url
os.environ["DB_NAME"] = _db_name
os.environ["ENV"] = "development"
os.environ["JWT_SECRET"] = "isolated-tests-only-secret-key-32-bytes"

from database import client as mongo_client
from database import db
from indexes import ensure_indexes
from migrations import migrate
from security import hash_password
from seed import BLOCK_TYPES, SUBMITTABLE, TAXONOMIES
from server import app


class TestSession:
    """Small requests-like sync adapter for tests using an AsyncClient transport."""
    def __init__(self, async_client, event_loop):
        self._client = async_client
        self._event_loop = event_loop
        self.cookies = async_client.cookies

    def request(self, method, url, **kwargs):
        async def send():
            return await self._client.request(method, url, **kwargs)
        return self._event_loop.run_until_complete(send())

    def get(self, url, **kwargs): return self.request("GET", url, **kwargs)
    def post(self, url, **kwargs): return self.request("POST", url, **kwargs)
    def put(self, url, **kwargs): return self.request("PUT", url, **kwargs)
    def delete(self, url, **kwargs): return self.request("DELETE", url, **kwargs)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)


@pytest.fixture(scope="session")
def async_client(event_loop):
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
    yield client
    event_loop.run_until_complete(client.aclose())


@pytest.fixture(scope="session")
def session_factory(event_loop):
    clients = []

    def create():
        client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        clients.append(client)
        return TestSession(client, event_loop)

    create.close_all = lambda: [event_loop.run_until_complete(client.aclose()) for client in clients]
    yield create


@pytest.fixture(scope="session", autouse=True)
def disposable_database(session_factory, event_loop):
    async def prepare():
        await db.command("ping")
        await ensure_indexes()
        for role, email in (("admin", "admin@example.com"), ("editor", "editor@example.com"),
                            ("student", "student@example.com")):
            await db.users.insert_one({
                "email": email, "name": role.title(), "password_hash": hash_password("Test@1234"),
                "role": role, "profile": {"bio": "", "goals": "", "preferences": {}},
            })
        for index, (group, key, label, description, color) in enumerate(TAXONOMIES):
            await db.taxonomies.insert_one({"group": group, "key": key, "label": label,
                                            "description": description, "color": color, "order": index})
        for index, (key, label, category, icon, fields) in enumerate(BLOCK_TYPES):
            await db.block_types.insert_one({
                "key": key, "label": label, "category": category, "icon": icon,
                "fields": fields, "description": "", "enabled": True,
                "capabilities": ["submission"] if key in SUBMITTABLE else [], "order": index,
            })
        await migrate()
    try:
        event_loop.run_until_complete(prepare())
        yield
    finally:
        try:
            session_factory.close_all()
        finally:
            event_loop.run_until_complete(mongo_client.close())
            if not _db_name.startswith("test_"):
                raise RuntimeError(f"Refusing to drop unsafe database: {_db_name!r}")
            with MongoClient(_mongo_url) as cleanup_client:
                cleanup_client.drop_database(_db_name)


def _login(session_factory, email, password="Test@1234"):
    session = session_factory()
    response = session.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, f"login failed {email}: {response.status_code} {response.text}"
    return session


@pytest.fixture(scope="session")
def admin(session_factory, disposable_database):
    return _login(session_factory, "admin@example.com")


@pytest.fixture(scope="session")
def editor(session_factory, disposable_database):
    return _login(session_factory, "editor@example.com")


@pytest.fixture(scope="session")
def student(session_factory, disposable_database):
    return _login(session_factory, "student@example.com")


@pytest.fixture(scope="session")
def admin_session(admin):
    return admin


@pytest.fixture(scope="session")
def editor_session(editor):
    return editor


@pytest.fixture(scope="session")
def student_session(student):
    return student


@pytest.fixture(scope="session")
def login(session_factory, disposable_database):
    def log_in(role_or_email, password="Test@1234"):
        aliases = {"admin": "admin@example.com", "editor": "editor@example.com", "student": "student@example.com"}
        email = aliases.get(role_or_email, role_or_email)
        return _login(session_factory, email, password)
    return log_in


@pytest.fixture
def fresh_student(login, event_loop):
    email = f"student_{uuid.uuid4().hex}@example.com"
    event_loop.run_until_complete(db.users.insert_one({
        "email": email, "name": "Isolated student", "password_hash": hash_password("Test@1234"),
        "role": "student", "profile": {"bio": "", "goals": "", "preferences": {}},
    }))
    return login(email)


@pytest.fixture(scope="session")
def seeded_track(admin):
    response = admin.post("/api/tracks", json={"title": "Test course", "settings": {"enforce_prerequisites": True}})
    assert response.status_code == 200
    track = response.json()
    track_id = track["id"]
    first = admin.post("/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "Prerequisite",
                                           "status": "published"}).json()
    second = admin.post("/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "Locked topic",
                                            "status": "published"}).json()
    relation = admin.post("/api/relations", json={"node_id": second["id"], "target_id": first["id"],
                                                   "type": "prerequisite", "enforced": True})
    assert relation.status_code == 200, relation.text
    published = admin.post(f"/api/tracks/{track_id}/publish", json={})
    assert published.status_code == 200, published.text
    return published.json()


@pytest.fixture(scope="session", autouse=True)
def _ensure_seeded_track(seeded_track):
    return seeded_track
