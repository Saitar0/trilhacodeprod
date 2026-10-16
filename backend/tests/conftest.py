"""Isolated API fixtures backed by a disposable MongoDB database."""
import asyncio
import os
import uuid
from urllib.parse import urlsplit, urlunsplit

import httpx
import pytest


MONGO_URL = os.environ.get("MONGO_URL_TEST", "mongodb://localhost:27017")
_db_name = f"test_{uuid.uuid4().hex}"
_parts = urlsplit(MONGO_URL)
_query = _parts.query
_mongo_url = urlunsplit((_parts.scheme, _parts.netloc, f"/{_db_name}", _query, _parts.fragment))

# server/core read settings at import time. Point them at this run's disposable DB.
os.environ["MONGO_URL"] = _mongo_url
os.environ["DB_NAME"] = _db_name
os.environ["ENV"] = "development"
os.environ.setdefault("JWT_SECRET", "isolated-tests-only-secret")

if not _db_name.startswith("test_"):
    raise RuntimeError(f"Refusing to run tests against unsafe database: {_db_name!r}")

from core import client as mongo_client, db, hash_password  # noqa: E402
from server import app  # noqa: E402


class TestSession:
    """Small requests-like sync adapter for tests using an AsyncClient transport."""
    def __init__(self, async_client):
        self._client = async_client
        self.cookies = httpx.Cookies()

    def request(self, method, url, **kwargs):
        async def send():
            response = await self._client.request(method, url, cookies=self.cookies, **kwargs)
            self.cookies.update(response.cookies)
            return response
        return asyncio.run(send())

    def get(self, url, **kwargs): return self.request("GET", url, **kwargs)
    def post(self, url, **kwargs): return self.request("POST", url, **kwargs)
    def put(self, url, **kwargs): return self.request("PUT", url, **kwargs)
    def delete(self, url, **kwargs): return self.request("DELETE", url, **kwargs)


@pytest.fixture(scope="session")
def async_client():
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
    yield client
    asyncio.run(client.aclose())


@pytest.fixture(scope="session")
def session_factory():
    clients = []

    def create():
        client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
        clients.append(client)
        return TestSession(client)

    yield create
    for client in clients:
        asyncio.run(client.aclose())


@pytest.fixture(scope="session", autouse=True)
def disposable_database(session_factory):
    async def prepare():
        await db.command("ping")
        for role, email in (("admin", "admin@test.local"), ("editor", "editor@test.local"),
                            ("student", "student@test.local")):
            await db.users.insert_one({
                "email": email, "name": role.title(), "password_hash": hash_password("Test@1234"),
                "role": role, "profile": {"bio": "", "goals": "", "preferences": {}},
            })
    asyncio.run(prepare())
    yield
    async def cleanup():
        if not _db_name.startswith("test_"):
            raise RuntimeError(f"Refusing to drop unsafe database: {_db_name!r}")
        await mongo_client.drop_database(_db_name)
        mongo_client.close()
    asyncio.run(cleanup())


def _login(session_factory, email, password="Test@1234"):
    session = session_factory()
    response = session.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, f"login failed {email}: {response.status_code} {response.text}"
    return session


@pytest.fixture(scope="session")
def admin(session_factory, disposable_database):
    return _login(session_factory, "admin@test.local")


@pytest.fixture(scope="session")
def editor(session_factory, disposable_database):
    return _login(session_factory, "editor@test.local")


@pytest.fixture(scope="session")
def student(session_factory, disposable_database):
    return _login(session_factory, "student@test.local")


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
    return lambda email, password="Test@1234": _login(session_factory, email, password)


@pytest.fixture(scope="session")
def seeded_track(admin):
    response = admin.post("/api/tracks", json={"title": "Test course", "settings": {"enforce_prerequisites": True}})
    assert response.status_code == 200
    track = response.json()
    track_id = track["id"]
    first = admin.post("/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "Prerequisite"}).json()
    second = admin.post("/api/nodes", json={"track_id": track_id, "kind": "topic", "title": "Locked topic"}).json()
    admin.post("/api/relations", json={"node_id": second["id"], "target_id": first["id"], "type": "prerequisite", "enforced": True})
    admin.post(f"/api/tracks/{track_id}/publish", json={})
    return track


@pytest.fixture(scope="session", autouse=True)
def _ensure_seeded_track(seeded_track):
    return seeded_track
