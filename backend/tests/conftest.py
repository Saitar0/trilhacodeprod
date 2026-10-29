"""API fixtures requiring an explicitly provisioned phase-owned MongoDB target."""

import asyncio
import os
import re
import secrets
import shutil
import tempfile
import uuid
from itertools import count
from pathlib import Path

import httpx
import pytest
from pymongo import MongoClient

from test_support.beta5_mongo_target import (
    MongoTarget,
    assert_database_owned,
    connect_verified_target,
    require_explicit_opt_in,
)

_TESTS_DIR = Path(__file__).resolve().parent
_target: MongoTarget | None = None
_ownership_client = None
_db_name = None
_mongo_url = None
_mailbox = None
mongo_client = None
db = None
app = None
ensure_indexes = None
migrate = None
hash_password = None
BLOCK_TYPES = None
SUBMITTABLE = None
TAXONOMIES = None
_client_ids = count(1)
_active_test_ip = None


def pytest_addoption(parser):
    parser.addoption(
        "--beta5-isolated-mongo",
        action="store_true",
        default=False,
        help="explicitly opt into backend/tests using a Docker-proven Beta 5 MongoDB container",
    )
    parser.addoption(
        "--beta6-isolated-mongo",
        action="store_true",
        default=False,
        help="explicitly opt into backend/tests using a Docker-proven Beta 6 MongoDB container",
    )


def _phase(config):
    beta5 = config.getoption("--beta5-isolated-mongo")
    beta6 = config.getoption("--beta6-isolated-mongo")
    if beta5 and beta6:
        raise pytest.UsageError("Selecione somente um ambiente persistente: Beta 5 ou Beta 6.")
    return "beta6" if beta6 else "beta5" if beta5 else None


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "beta5_isolated_mongo: test is running against a verified disposable Beta 5 MongoDB",
    )
    config.addinivalue_line(
        "markers", "beta6_isolated_mongo: test is running against a verified disposable Beta 6 MongoDB",
    )


def pytest_collect_file(file_path, parent):
    """Reject persistent API modules before importing any application code."""
    path = Path(str(file_path)).resolve()
    if path.parent == _TESTS_DIR and path.name.startswith("test_") and path.suffix == ".py":
        try:
            phase = _phase(parent.config)
            require_explicit_opt_in(phase is not None, phase)
        except RuntimeError as exc:
            raise pytest.UsageError(
                "backend/tests collection blocked before module import: provision and verify a "
                "phase-specific disposable MongoDB, then pass exactly one of "
                "--beta5-isolated-mongo or --beta6-isolated-mongo."
            ) from exc


def pytest_collection_modifyitems(config, items):
    persistent_items = [
        item for item in items
        if Path(str(item.path)).resolve().is_relative_to(_TESTS_DIR)
    ]
    phase = _phase(config)
    if persistent_items and phase is None:
        raise pytest.UsageError(
            "backend/tests contains persistent API tests and is disabled by default. "
            "Provision a phase-owned disposable MongoDB and pass exactly one matching opt-in; "
            "no MongoDB URI fallback is available."
        )
    for item in persistent_items:
        item.add_marker(getattr(pytest.mark, f"{phase}_isolated_mongo"))


def pytest_sessionstart(session):
    """Prove Docker ownership and server identity before importing the app."""
    global _target, _ownership_client, _db_name, _mongo_url, _mailbox
    global mongo_client, db, app, ensure_indexes, migrate, hash_password
    global BLOCK_TYPES, SUBMITTABLE, TAXONOMIES
    phase = _phase(session.config)
    if phase is None:
        return

    _target, _ownership_client = connect_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
        phase=phase,
    )
    _db_name = _target.database
    _mongo_url = _target.uri

    # Application settings are changed only after the disposable target has
    # been proven. Importing the application can no longer select a fallback.
    _mailbox = tempfile.mkdtemp(prefix=f"trilhacode-{phase}-{_target.run_id}-mail-")
    os.environ.update({
        "MONGO_URL": _mongo_url,
        "DB_NAME": _db_name,
        "ENV": "development",
        "JWT_SECRET": secrets.token_urlsafe(48),
        "EMAIL_TRANSPORT": "local",
        "LOCAL_EMAIL_DIR": _mailbox,
    })
    from database import client as async_mongo_client
    from database import db as application_db
    from indexes import ensure_indexes as ensure
    from migrations import migrate as run_migrations
    from security import hash_password as hash_pw
    from seed import BLOCK_TYPES as block_types
    from seed import SUBMITTABLE as submittable
    from seed import TAXONOMIES as taxonomies
    from server import app as application

    mongo_client = async_mongo_client
    db = application_db
    app = application
    ensure_indexes = ensure
    migrate = run_migrations
    hash_password = hash_pw
    BLOCK_TYPES = block_types
    SUBMITTABLE = submittable
    TAXONOMIES = taxonomies


def _test_transport():
    client_ip = _active_test_ip
    if client_ip is None:
        client_id = next(_client_ids)
        client_ip = f"127.0.{(client_id >> 8) & 255}.{client_id & 255}"
    return httpx.ASGITransport(app=app, client=(client_ip, 12345))


def pytest_runtest_setup(item):
    global _active_test_ip
    client_id = next(_client_ids)
    _active_test_ip = f"127.0.{(client_id >> 8) & 255}.{client_id & 255}"


class TestSession:
    """Small requests-like sync adapter for tests using an AsyncClient transport."""
    def __init__(self, async_client, event_loop):
        self._client = async_client
        self._event_loop = event_loop
        self.cookies = async_client.cookies

    def request(self, method, url, **kwargs):
        if method.upper() not in {"GET", "HEAD", "OPTIONS"}:
            headers = dict(kwargs.get("headers") or {})
            if not any(key.lower() == "origin" for key in headers):
                headers["Origin"] = "http://localhost:3000"
            kwargs["headers"] = headers
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


@pytest.fixture
def async_client(event_loop):
    client = httpx.AsyncClient(transport=_test_transport(), base_url="http://testserver")
    yield client
    event_loop.run_until_complete(client.aclose())


@pytest.fixture(scope="session")
def session_factory(event_loop):
    clients = []

    def create():
        client = httpx.AsyncClient(transport=_test_transport(), base_url="http://testserver")
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
            try:
                assert_database_owned(_ownership_client, _target)
                for collection_name in _ownership_client[_db_name].list_collection_names():
                    if collection_name != f"_{_target.phase}_test_owner":
                        _ownership_client[_db_name].drop_collection(collection_name)
            finally:
                _ownership_client.close()
                if _mailbox and os.path.commonpath([tempfile.gettempdir(), _mailbox]) == tempfile.gettempdir():
                    shutil.rmtree(_mailbox, ignore_errors=True)


@pytest.fixture(scope="session")
def mailbox_token():
    from email import policy
    from email.parser import BytesParser
    from pathlib import Path

    def find(recipient: str, subject: str | None = None) -> str:
        candidates = sorted(Path(_mailbox).glob("*.eml"), key=lambda path: path.stat().st_mtime, reverse=True)
        for path in candidates:
            message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
            if message["To"] != recipient or (subject and message["Subject"] != subject):
                continue
            body = message.get_body(preferencelist=("plain",)).get_content()
            match = re.search(r"[?&]token=([A-Za-z0-9_-]{32,})", body)
            if match:
                return match.group(1)
        raise AssertionError(f"No local test email found for {recipient}")
    return find


@pytest.fixture(scope="session")
def create_verified_user(mailbox_token):
    def create(session, email: str, password: str = "Test@12345678", name: str = "Test user"):
        registered = session.post("/api/auth/register", json={"name": name, "email": email, "password": password})
        assert registered.status_code == 202, registered.text
        token = mailbox_token(email, "Confirme seu e-mail")
        verified = session.post("/api/auth/verify-email", json={"token": token})
        assert verified.status_code == 200, verified.text
        logged_in = session.post("/api/auth/login", json={"email": email, "password": password})
        assert logged_in.status_code == 200, logged_in.text
        return registered
    return create


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


@pytest.fixture(scope="session")
def grant_track_review(event_loop):
    """Provision an explicit synthetic per-track reviewer scope in the test DB."""
    def grant(session, track_id: str, operations=None):
        actor = session.get("/api/auth/me")
        assert actor.status_code == 200, actor.text
        user_id = actor.json()["id"]
        scope = {
            "_id": f"{user_id}:{track_id}",
            "user_id": user_id,
            "track_id": track_id,
            "operations": operations or ["submissions.read", "submissions.grade"],
            "state": "active",
            "source": "synthetic_test_fixture",
        }
        event_loop.run_until_complete(db.learning_review_scopes.replace_one(
            {"_id": scope["_id"]}, scope, upsert=True,
        ))
        return scope
    return grant


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
