"""Opt-in integration test; refuses implicit, remote, or non-replica-set MongoDB."""

from __future__ import annotations

import asyncio
import ipaddress
import os
import re
import secrets
import uuid
from urllib.parse import parse_qs, parse_qsl, quote, urlencode, urlsplit, urlunsplit

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure

from curriculum_contract.activity_persistence import (
    ActivityTransactionOutcomeUnknownError,
    ActivityVersionConflictError,
    TypedActivityDraftStore,
)
from unit_tests.test_typed_activity_persistence import ADMIN, sample_activity

_URI_ENV = "TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_URI"
_REPLICA_ENV = "TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_REPLICA_SET"
_DISPOSABLE_ENV = "TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_DISPOSABLE"


class _InjectedTransactionFailure(RuntimeError):
    """Client-side fault injected after a staged transactional write."""


class _FaultCollection:
    def __init__(self, collection, name: str, fault_state: dict[str, str | None]) -> None:
        self._collection = collection
        self._name = name
        self._fault_state = fault_state

    def __getattr__(self, name):
        return getattr(self._collection, name)

    async def insert_one(self, document, **kwargs):
        result = await self._collection.insert_one(document, **kwargs)
        if self._fault_state.get("point") == "after_public_insert" and self._name == (
            "typed_activity_public_versions"
        ):
            self._fault_state["point"] = None
            raise _InjectedTransactionFailure("injected failure after first staged write")
        return result

    async def update_one(self, query, update, **kwargs):
        if self._fault_state.get("point") == "before_head_update" and self._name == (
            "typed_activity_heads"
        ):
            self._fault_state["point"] = None
            raise _InjectedTransactionFailure("injected failure before head update")
        return await self._collection.update_one(query, update, **kwargs)


class _FaultDatabase:
    def __init__(self, database, fault_point: str) -> None:
        self._database = database
        self.client = database.client
        self._fault_state: dict[str, str | None] = {"point": fault_point}

    def __getitem__(self, name: str):
        return _FaultCollection(self._database[name], name, self._fault_state)


class _CommitUnknownSession:
    def __init__(self, session) -> None:
        self._session = session

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *args):
        return await self._session.__aexit__(*args)

    async def with_transaction(self, callback):
        await self._session.with_transaction(callback)
        error = OperationFailure("injected lost commit acknowledgement", code=91)
        error._add_error_label("UnknownTransactionCommitResult")
        raise error


class _CommitUnknownClient:
    def __init__(self, client) -> None:
        self._client = client

    def start_session(self):
        return _CommitUnknownSession(self._client.start_session())


class _CommitUnknownDatabase:
    def __init__(self, database) -> None:
        self._database = database
        self.client = _CommitUnknownClient(database.client)

    def __getitem__(self, name: str):
        return self._database[name]


pytestmark = pytest.mark.skipif(
    not os.environ.get(_URI_ENV),
    reason=f"set explicit {_URI_ENV} for a disposable local replica set",
)


def _assert_explicit_local_replica_uri(uri: str, expected_set: str) -> tuple[str, int]:
    parts = urlsplit(uri)
    if parts.scheme != "mongodb" or not parts.hostname or parts.port is None:
        raise AssertionError("test Mongo URI must use mongodb:// and an explicit host port")
    if not parts.username or not parts.password:
        raise AssertionError("Mongo integration tests require an authenticated disposable instance")
    try:
        local = (
            parts.hostname.lower() == "localhost"
            or ipaddress.ip_address(parts.hostname).is_loopback
        )
    except ValueError:
        local = parts.hostname.lower() == "localhost"
    if not local:
        raise AssertionError("typed activity persistence tests only accept loopback Mongo hosts")
    options = {key.casefold(): values for key, values in parse_qs(parts.query).items()}
    replica_values = options.get("replicaset")
    if replica_values != [expected_set] or not expected_set:
        raise AssertionError("Mongo URI and explicit replica-set name must match")
    if options.get("directconnection") == ["true"]:
        raise AssertionError("replica-set discovery must remain enabled for transaction tests")
    if os.environ.get(_DISPOSABLE_ENV) != "YES":
        raise AssertionError(f"set {_DISPOSABLE_ENV}=YES only for a confirmed disposable test set")
    return parts.hostname, parts.port


def _uri_for_test_user(base_uri: str, username: str, password: str) -> str:
    parts = urlsplit(base_uri)
    host = parts.netloc.rsplit("@", 1)[-1]
    query = [
        (key, value) for key, value in parse_qsl(parts.query) if key.casefold() != "authsource"
    ]
    query.append(("authSource", "admin"))
    return urlunsplit(
        (
            parts.scheme,
            f"{quote(username, safe='')}:{quote(password, safe='')}@{host}",
            "/admin",
            urlencode(query),
            "",
        )
    )


def _test_database_name(suffix: str) -> str:
    """Return a unique Mongo database name safely below MongoDB's 63-char limit."""
    return f"ta14f2_{suffix}_{uuid.uuid4().hex[:16]}"


def _assert_single_local_member(
    hello: dict, seed_host: str, seed_port: int, expected_set: str
) -> None:
    if hello.get("setName") != expected_set or hello.get("isWritablePrimary") is not True:
        raise AssertionError("configured MongoDB is not the expected writable test replica set")
    hosts = hello.get("hosts")
    if not isinstance(hosts, list) or len(hosts) != 1:
        raise AssertionError("integration test requires a one-member disposable replica set")
    match = re.fullmatch(r"([^:]+):(\d+)", hosts[0])
    if match is None:
        raise AssertionError("replica-set member address is malformed")
    member_host, member_port = match.group(1), int(match.group(2))
    try:
        member_local = (
            member_host.casefold() == "localhost" or ipaddress.ip_address(member_host).is_loopback
        )
    except ValueError:
        member_local = member_host.casefold() == "localhost"
    if not member_local or member_port != seed_port:
        raise AssertionError("replica set advertises a nonlocal or unexpected member")
    seed_is_local = (
        seed_host.casefold() == "localhost" or ipaddress.ip_address(seed_host).is_loopback
    )
    if not seed_is_local:
        raise AssertionError("Mongo seed host is not loopback")


def test_typed_activity_versions_are_transactional_on_explicit_disposable_replica_set():
    uri = os.environ[_URI_ENV]
    expected_set = os.environ.get(_REPLICA_ENV, "")
    seed_host, seed_port = _assert_explicit_local_replica_uri(uri, expected_set)

    async def run():
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        database_name = _test_database_name("versions")
        database_created = False
        created_users: list[str] = []
        created_roles: list[str] = []
        scoped_clients = []
        try:
            # This is a read-only topology check; no database is selected or modified yet.
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, expected_set)
            database = client[database_name]
            database_created = True
            store = TypedActivityDraftStore(database)
            await store.ensure_indexes()
            for index, kind in enumerate(
                ("multiple_choice", "short_answer", "discursive", "matching", "ordering", "review"),
                start=1,
            ):
                saved = await store.save_version(sample_activity(kind, index), ADMIN)
                assert saved.outcome == "created"
                repeated = await store.save_version(sample_activity(kind, index), ADMIN)
                assert repeated.outcome == "unchanged"
                assert repeated.version_id == saved.version_id
                public = await store.get_public_version(saved.activity_ref, saved.version_id, ADMIN)
                private = await store.get_private_version(
                    saved.activity_ref, saved.version_id, ADMIN
                )
                assert public is not None and private is not None
                if kind == "review":
                    assert private.private_payload is None
                else:
                    assert private.private_payload is not None
            base_record = sample_activity("multiple_choice", 20)
            base = await store.save_version(base_record, ADMIN)
            revised_record = sample_activity(
                "multiple_choice", 20, prompt_text="Sanitized revised prompt 20."
            )
            revised = await store.save_version(
                revised_record, ADMIN, expected_version_id=base.version_id
            )
            assert revised.outcome == "created"
            assert revised.version_id != base.version_id
            with pytest.raises(ActivityVersionConflictError):
                await store.save_version(
                    sample_activity(
                        "multiple_choice", 20, prompt_text="Sanitized stale prompt 20."
                    ),
                    ADMIN,
                    expected_version_id=base.version_id,
                )
            index_specs = {}
            for collection_name in (
                "typed_activity_public_versions",
                "typed_activity_private_versions",
                "typed_activity_version_events",
                "typed_activity_heads",
            ):
                cursor = await database[collection_name].list_indexes()
                index_specs.update(
                    {
                        spec["name"]: (list(spec["key"].items()), spec.get("unique", False))
                        for spec in await cursor.to_list(100)
                        if spec.get("name")
                    }
                )
            expected_unique_indexes = {
                "one_typed_activity_public_version": [
                    ("activity_ref", 1),
                    ("version_id", 1),
                ],
                "one_typed_activity_private_version": [
                    ("activity_ref", 1),
                    ("version_id", 1),
                ],
                "one_typed_activity_content_revision": [
                    ("activity_ref", 1),
                    ("private_content_sha256", 1),
                ],
                "one_typed_activity_creation_event": [
                    ("activity_ref", 1),
                    ("version_id", 1),
                    ("event_type", 1),
                ],
                "one_typed_activity_current_head": [("activity_ref", 1)],
            }
            for name, keys in expected_unique_indexes.items():
                assert index_specs[name] == (keys, True)
            assert index_specs["typed_activity_public_version_history"] == (
                [("activity_ref", 1), ("created_at", -1)],
                False,
            )

            duplicate_head = {
                "activity_ref": "index-duplicate-head",
                "current_version_id": "1" * 24,
            }
            await database["typed_activity_heads"].insert_one(duplicate_head)
            with pytest.raises(DuplicateKeyError):
                await database["typed_activity_heads"].insert_one(
                    {**duplicate_head, "_id": "different-id"}
                )

            public_role = f"typed_public_read_{uuid.uuid4().hex}"
            editor_role = f"typed_editor_write_{uuid.uuid4().hex}"
            internal_role = f"typed_private_read_{uuid.uuid4().hex}"
            public_user = f"typed_public_{uuid.uuid4().hex}"
            editor_user = f"typed_editor_{uuid.uuid4().hex}"
            internal_user = f"typed_internal_{uuid.uuid4().hex}"
            public_resource = {
                "resource": {
                    "db": database_name,
                    "collection": "typed_activity_public_versions",
                },
                "actions": ["find"],
            }
            private_read_resource = {
                "resource": {
                    "db": database_name,
                    "collection": "typed_activity_private_versions",
                },
                "actions": ["find"],
            }
            editable_resources = [
                {
                    "resource": {"db": database_name, "collection": collection_name},
                    # Editors must read private drafts to validate/replay revisions;
                    # this role is still scoped to this one disposable test database.
                    "actions": ["find", "insert", "update", "createIndex"],
                }
                for collection_name in (
                    "typed_activity_public_versions",
                    "typed_activity_private_versions",
                    "typed_activity_version_events",
                    "typed_activity_heads",
                )
            ]
            for role_name, privileges in (
                (public_role, [public_resource]),
                (editor_role, editable_resources),
                (internal_role, [public_resource, private_read_resource]),
            ):
                await client.admin.command("createRole", role_name, privileges=privileges, roles=[])
                created_roles.append(role_name)

            scoped_users = (
                (public_user, public_role),
                (editor_user, editor_role),
                (internal_user, internal_role),
            )
            scoped_passwords: dict[str, str] = {}
            for username, role_name in scoped_users:
                password = secrets.token_urlsafe(32)
                scoped_passwords[username] = password
                await client.admin.command(
                    "createUser",
                    username,
                    pwd=password,
                    roles=[{"role": role_name, "db": "admin"}],
                )
                created_users.append(username)

            public_client = AsyncMongoClient(
                _uri_for_test_user(uri, public_user, scoped_passwords[public_user]),
                serverSelectionTimeoutMS=3000,
            )
            editor_client = AsyncMongoClient(
                _uri_for_test_user(uri, editor_user, scoped_passwords[editor_user]),
                serverSelectionTimeoutMS=3000,
            )
            internal_client = AsyncMongoClient(
                _uri_for_test_user(uri, internal_user, scoped_passwords[internal_user]),
                serverSelectionTimeoutMS=3000,
            )
            scoped_clients.extend((public_client, editor_client, internal_client))

            public_row = await public_client[database_name][
                "typed_activity_public_versions"
            ].find_one({"activity_ref": base.activity_ref})
            assert public_row is not None
            with pytest.raises(OperationFailure) as private_denied:
                await public_client[database_name]["typed_activity_private_versions"].find_one(
                    {"activity_ref": base.activity_ref}
                )
            assert private_denied.value.code == 13
            with pytest.raises(OperationFailure) as write_denied:
                await public_client[database_name]["typed_activity_public_versions"].insert_one(
                    {"activity_ref": "unauthorized-write"}
                )
            assert write_denied.value.code == 13

            editor_store = TypedActivityDraftStore(editor_client[database_name])
            editorial = await editor_store.save_version(sample_activity("review", 44), ADMIN)
            assert editorial.outcome == "created"

            internal_store = TypedActivityDraftStore(internal_client[database_name])
            internal_private = await internal_store.get_private_version(
                base.activity_ref, revised.version_id, ADMIN
            )
            assert internal_private is not None
        finally:
            for scoped_client in scoped_clients:
                await scoped_client.close()
            for username in created_users:
                await client.admin.command("dropUser", username)
            for role_name in created_roles:
                await client.admin.command("dropRole", role_name)
            if database_created and database_name.startswith("ta14f2_"):
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


def test_mongo_transaction_rolls_back_after_first_staged_write():
    uri = os.environ[_URI_ENV]
    expected_set = os.environ.get(_REPLICA_ENV, "")
    seed_host, seed_port = _assert_explicit_local_replica_uri(uri, expected_set)

    async def run():
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        database_name = _test_database_name("rollback")
        database_created = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, expected_set)
            database = client[database_name]
            database_created = True
            store = TypedActivityDraftStore(_FaultDatabase(database, "after_public_insert"))
            with pytest.raises(_InjectedTransactionFailure):
                await store.save_version(sample_activity("multiple_choice", 40), ADMIN)
            for name in (
                "typed_activity_public_versions",
                "typed_activity_private_versions",
                "typed_activity_version_events",
                "typed_activity_heads",
            ):
                assert await database[name].count_documents({}) == 0
        finally:
            if database_created and database_name.startswith("ta14f2_"):
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


def test_mongo_transaction_rolls_back_revision_when_head_update_fails():
    uri = os.environ[_URI_ENV]
    expected_set = os.environ.get(_REPLICA_ENV, "")
    seed_host, seed_port = _assert_explicit_local_replica_uri(uri, expected_set)

    async def run():
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        database_name = _test_database_name("revision_rollback")
        database_created = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, expected_set)
            database = client[database_name]
            database_created = True
            store = TypedActivityDraftStore(database)
            initial = await store.save_version(sample_activity("multiple_choice", 41), ADMIN)
            revised = sample_activity(
                "multiple_choice", 41, prompt_text="Sanitized revision rollback 41."
            )
            failing_store = TypedActivityDraftStore(_FaultDatabase(database, "before_head_update"))
            with pytest.raises(_InjectedTransactionFailure):
                await failing_store.save_version(
                    revised, ADMIN, expected_version_id=initial.version_id
                )
            assert await database["typed_activity_public_versions"].count_documents({}) == 1
            assert await database["typed_activity_private_versions"].count_documents({}) == 1
            assert await database["typed_activity_version_events"].count_documents({}) == 1
            head = await database["typed_activity_heads"].find_one(
                {"activity_ref": initial.activity_ref}
            )
            assert head is not None and head["current_version_id"] == initial.version_id
            assert head["revision"] == 1
        finally:
            if database_created and database_name.startswith("ta14f2_"):
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


def test_mongo_unknown_commit_ack_reconciles_by_replaying_identical_content():
    uri = os.environ[_URI_ENV]
    expected_set = os.environ.get(_REPLICA_ENV, "")
    seed_host, seed_port = _assert_explicit_local_replica_uri(uri, expected_set)

    async def run():
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        database_name = _test_database_name("unknown_commit")
        database_created = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, expected_set)
            database = client[database_name]
            database_created = True
            record = sample_activity("multiple_choice", 45)
            uncertain_store = TypedActivityDraftStore(_CommitUnknownDatabase(database))
            with pytest.raises(ActivityTransactionOutcomeUnknownError):
                await uncertain_store.save_version(record, ADMIN)

            replay = await TypedActivityDraftStore(database).save_version(record, ADMIN)
            assert replay.outcome == "unchanged"
            for name in (
                "typed_activity_public_versions",
                "typed_activity_private_versions",
                "typed_activity_version_events",
                "typed_activity_heads",
            ):
                assert await database[name].count_documents({}) == 1
            head = await database["typed_activity_heads"].find_one(
                {"activity_ref": record.activity_ref}
            )
            assert head is not None and head["revision"] == 1
        finally:
            if database_created and database_name.startswith("ta14f2_"):
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


def test_mongo_concurrent_identical_and_divergent_revisions():
    uri = os.environ[_URI_ENV]
    expected_set = os.environ.get(_REPLICA_ENV, "")
    seed_host, seed_port = _assert_explicit_local_replica_uri(uri, expected_set)

    async def run():
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        database_name = _test_database_name("concurrency")
        database_created = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, expected_set)
            database = client[database_name]
            database_created = True
            store = TypedActivityDraftStore(database)

            identical = sample_activity("multiple_choice", 42)
            identical_results = await asyncio.gather(
                store.save_version(identical, ADMIN),
                store.save_version(identical, ADMIN),
            )
            assert sorted(result.outcome for result in identical_results) == [
                "created",
                "unchanged",
            ]
            assert (
                await database["typed_activity_public_versions"].count_documents(
                    {"activity_ref": identical.activity_ref}
                )
                == 1
            )

            base_record = sample_activity("multiple_choice", 43)
            base = await store.save_version(base_record, ADMIN)
            left = sample_activity(
                "multiple_choice", 43, prompt_text="Concurrent left revision 43."
            )
            right = sample_activity(
                "multiple_choice", 43, prompt_text="Concurrent right revision 43."
            )
            outcomes = await asyncio.gather(
                store.save_version(left, ADMIN, expected_version_id=base.version_id),
                store.save_version(right, ADMIN, expected_version_id=base.version_id),
                return_exceptions=True,
            )
            assert (
                sum(
                    not isinstance(result, BaseException) and result.outcome == "created"
                    for result in outcomes
                )
                == 1
            )
            assert sum(isinstance(result, ActivityVersionConflictError) for result in outcomes) == 1
            assert (
                await database["typed_activity_public_versions"].count_documents(
                    {"activity_ref": base.activity_ref}
                )
                == 2
            )
        finally:
            if database_created and database_name.startswith("ta14f2_"):
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())
