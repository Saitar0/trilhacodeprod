"""Opt-in MongoDB tests; accept only an explicitly disposable local instance."""

from __future__ import annotations

import asyncio
import ipaddress
import os
import re
import uuid
from collections.abc import Mapping
from typing import Any, Literal
from urllib.parse import parse_qs, parse_qsl, quote, urlencode, urlsplit, urlunsplit

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure

from curriculum_contract.editorial_persistence import (
    EVENTS_COLLECTION,
    HEADS_COLLECTION,
    OPERATIONS_COLLECTION,
    PAYLOADS_COLLECTION,
    REVISIONS_COLLECTION,
    EditorialAuthorizationError,
    EditorialIdempotencyConflictError,
    EditorialPersistenceStore,
    EditorialPrincipal,
    EditorialTransactionFailedError,
    EditorialTransactionsRequiredError,
    EditorialVersionConflictError,
    EditorialWriteResult,
    StoredPlacementPayload,
    StoredProjectPayload,
)
from curriculum_contract.models import (
    AnswerKeyBlock,
    ProjectDelivery,
    ProjectMilestone,
    ProjectSpec,
    SharedPlacement,
    SourceProvenance,
    TheoryBlock,
)

_URI_ENV = "TRILHACODE_EDITORIAL_MONGO_TEST_URI"
_REPLICA_ENV = "TRILHACODE_EDITORIAL_MONGO_TEST_REPLICA_SET"
_DISPOSABLE_ENV = "TRILHACODE_EDITORIAL_MONGO_TEST_DISPOSABLE"
_INSTANCE_ENV = "TRILHACODE_EDITORIAL_MONGO_TEST_INSTANCE_ID"
_STANDALONE_URI_ENV = "TRILHACODE_EDITORIAL_MONGO_STANDALONE_TEST_URI"
_STANDALONE_DISPOSABLE_ENV = "TRILHACODE_EDITORIAL_MONGO_STANDALONE_TEST_DISPOSABLE"
_RUN_REPLICA = all(os.environ.get(name) for name in (_URI_ENV, _REPLICA_ENV, _INSTANCE_ENV)) and (
    os.environ.get(_DISPOSABLE_ENV) == "YES"
)
_RUN_STANDALONE = bool(os.environ.get(_STANDALONE_URI_ENV)) and (
    os.environ.get(_STANDALONE_DISPOSABLE_ENV) == "YES"
)


class _InjectedAbort(RuntimeError):
    pass


class _FaultCollection:
    def __init__(self, collection: Any, name: str, fault: dict[str, str | None]) -> None:
        self._collection = collection
        self._name = name
        self._fault = fault

    def __getattr__(self, name: str) -> Any:
        return getattr(self._collection, name)

    def with_options(self, *args: Any, **kwargs: Any) -> _FaultCollection:
        return _FaultCollection(
            self._collection.with_options(*args, **kwargs), self._name, self._fault
        )

    async def insert_one(self, document: dict[str, Any], **kwargs: Any) -> Any:
        result = await self._collection.insert_one(document, **kwargs)
        point = self._fault.get("point")
        if point == f"after_insert:{self._name}":
            self._fault["point"] = None
            raise _InjectedAbort("injected after transactional insert")
        return result

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], **kwargs: Any) -> Any:
        if self._fault.get("point") == f"before_update:{self._name}":
            self._fault["point"] = None
            raise _InjectedAbort("injected before transactional update")
        return await self._collection.update_one(query, update, **kwargs)


class _FaultDatabase:
    def __init__(self, database: Any, point: str) -> None:
        self._database = database
        self.client = database.client
        self._fault: dict[str, str | None] = {"point": point}

    def get_collection(self, name: str) -> _FaultCollection:
        return _FaultCollection(self._database.get_collection(name), name, self._fault)


class _UnknownCommitSession:
    def __init__(self, session: Any) -> None:
        self._session = session

    async def __aenter__(self) -> _UnknownCommitSession:
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> Any:
        return await self._session.__aexit__(*args)

    async def with_transaction(self, callback: Any, **kwargs: Any) -> Any:
        await self._session.with_transaction(callback, **kwargs)
        error = OperationFailure("injected missing commit acknowledgement", code=91)
        error._add_error_label("UnknownTransactionCommitResult")
        raise error


class _UnknownCommitClient:
    def __init__(self, client: Any) -> None:
        self._client = client

    def start_session(self) -> _UnknownCommitSession:
        return _UnknownCommitSession(self._client.start_session())


class _UnknownCommitDatabase(_FaultDatabase):
    def __init__(self, database: Any) -> None:
        self._database = database
        self.client = _UnknownCommitClient(database.client)

    def get_collection(self, name: str) -> Any:
        return self._database.get_collection(name)


def _assert_local_replica(uri: str, expected_set: str) -> tuple[str, int]:
    parts = urlsplit(uri)
    if parts.scheme != "mongodb" or not parts.hostname or parts.port is None:
        raise AssertionError("test URI must use mongodb:// with an explicit port")
    if not parts.username or not parts.password:
        raise AssertionError("test URI must authenticate")
    try:
        local = (
            parts.hostname.casefold() == "localhost"
            or ipaddress.ip_address(parts.hostname).is_loopback
        )
    except ValueError:
        local = False
    if not local:
        raise AssertionError("test MongoDB must be addressed through loopback")
    query = {key.casefold(): values for key, values in parse_qs(parts.query).items()}
    if query.get("replicaset") != [expected_set] or query.get("directconnection") == ["true"]:
        raise AssertionError("test URI must discover the explicitly named replica set")
    if os.environ.get(_DISPOSABLE_ENV) != "YES":
        raise AssertionError("disposable-set confirmation marker is required")
    instance = os.environ.get(_INSTANCE_ENV, "")
    if not instance.startswith("14h3b-") or len(instance) < 14:
        raise AssertionError("current-execution instance identifier is required")
    return parts.hostname, parts.port


def _assert_single_local_member(
    hello: Mapping[str, Any], seed_host: str, seed_port: int, expected_set: str
) -> None:
    if hello.get("setName") != expected_set or hello.get("isWritablePrimary") is not True:
        raise AssertionError("configured server is not the expected writable replica-set primary")
    hosts = hello.get("hosts")
    if not isinstance(hosts, list) or len(hosts) != 1:
        raise AssertionError("test environment must advertise exactly one replica-set member")
    match = re.fullmatch(r"([^:]+):(\d+)", hosts[0])
    if match is None:
        raise AssertionError("replica-set member address is malformed")
    host, port = match.group(1), int(match.group(2))
    try:
        member_local = host.casefold() == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        member_local = False
    if not member_local or host.casefold() != seed_host.casefold() or port != seed_port:
        raise AssertionError("replica-set member does not match the isolated seed URI")


def _test_db_name() -> str:
    return f"e14h3b_{uuid.uuid4().hex[:16]}"


def _scoped_uri(base_uri: str, username: str, password: str, auth_source: str) -> str:
    parts = urlsplit(base_uri)
    host = parts.netloc.rsplit("@", 1)[-1]
    query = [
        (key, value) for key, value in parse_qsl(parts.query) if key.casefold() != "authsource"
    ]
    query.append(("authSource", auth_source))
    return urlunsplit(
        (
            parts.scheme,
            f"{quote(username, safe='')}:{quote(password, safe='')}@{host}",
            f"/{auth_source}",
            urlencode(query),
            "",
        )
    )


def _prov(source_id: str = "SYNTHETIC") -> SourceProvenance:
    return SourceProvenance(
        source_file="docs/fixtures/14h3b_synthetic.md",
        source_sha256="a" * 64,
        manifest_ref="14h3b-synthetic-manifest",
        source_role="synthetic-test",
        source_id=source_id,
    )


def _block(
    ref: str = "f1-shared-fixture", *, owner_ref: str | None = "f1-topic-fixture"
) -> TheoryBlock:
    return TheoryBlock(
        ref=ref,
        type="theory",
        owner_ref=owner_ref,
        order=1,
        title="Synthetic editorial block",
        status="draft",
        shared=True,
        provenance=_prov("BLOCK"),
        body="SYNTHETIC_BLOCK_BODY",
        microtopic=None,
    )


def _answer_block() -> AnswerKeyBlock:
    return AnswerKeyBlock(
        ref="f1-answer-fixture",
        type="answer_key",
        owner_ref=None,
        order=2,
        title="Synthetic private answer key",
        status="draft",
        shared=True,
        provenance=_prov("PRIVATE"),
        question_ref="f1-question-fixture",
        correct_option_ref="option-a",
        accepted_answers=["SYNTHETIC_PRIVATE_ANSWER"],
        expected_answer=None,
        explanation="SYNTHETIC_PRIVATE_EXPLANATION",
        source_markdown="SYNTHETIC_PRIVATE_SOURCE",
    )


def _placement(ref: str = "f1-placement-fixture") -> SharedPlacement:
    return SharedPlacement(
        ref=ref,
        block_ref="f1-shared-fixture",
        subject_ref="f1-topic-fixture",
        order=1,
        progress_scope="undecided",
        provenance=_prov("PLACEMENT"),
    )


def _project(
    *,
    project_ref: str = "f1-project-fixture",
    content_ref: str = "f1-project-content-fixture",
) -> ProjectSpec:
    return ProjectSpec(
        ref=project_ref,
        unit_ref="f1-submodule-fixture",
        title="Synthetic aggregate project",
        scope="SYNTHETIC_PROJECT_SCOPE",
        has_formal_deliveries=True,
        deliveries=[
            ProjectDelivery(
                ref="f1-delivery-fixture",
                title="Synthetic delivery",
                body="SYNTHETIC_DELIVERY_BODY",
                order=1,
                acceptance_refs=[],
                checklist_refs=[],
                rubric_refs=[],
                content_refs=[content_ref],
                provenance=_prov("DELIVERY"),
            )
        ],
        has_formal_milestones=True,
        milestones=[
            ProjectMilestone(
                ref="f1-milestone-fixture",
                title="Synthetic milestone",
                body="SYNTHETIC_MILESTONE_BODY",
                order=2,
                acceptance_refs=[],
                checklist_refs=[],
                rubric_refs=[],
                content_refs=[],
                provenance=_prov("MILESTONE"),
            )
        ],
        variants=[],
        checklist_refs=[],
        rubric_refs=[],
        stack_options=["synthetic-stack-a", "synthetic-stack-b"],
        stack_selected=None,
        source_metadata={"fixture": "synthetic"},
        provenance=_prov("PROJECT"),
    )


def _principal(actor: str) -> EditorialPrincipal:
    return EditorialPrincipal(actor_ref=actor)


def _authorizer(principal: EditorialPrincipal, capability: str) -> bool:
    grants = {
        "editor": {
            "curriculum.editorial.admin",
            "curriculum.editorial.read",
            "curriculum.editorial.content.read",
            "curriculum.editorial.private.read",
            "curriculum.editorial.revision.create",
            "curriculum.editorial.history.read",
        },
        "metadata-reader": {"curriculum.editorial.read", "curriculum.editorial.history.read"},
        "content-reader": {
            "curriculum.editorial.read",
            "curriculum.editorial.content.read",
            "curriculum.editorial.private.read",
            "curriculum.editorial.history.read",
        },
    }
    return capability in grants.get(principal.actor_ref, set())


def _node_kind(ref: str) -> Literal["topic", "submodule"] | None:
    if ref == "f1-topic-fixture":
        return "topic"
    if ref == "f1-submodule-fixture":
        return "submodule"
    return None


def _make_store(database: Any) -> EditorialPersistenceStore:
    return EditorialPersistenceStore(
        database, authorizer=_authorizer, node_kind_resolver=_node_kind
    )


async def _create_scoped_role(db: Any, role: str, collection_actions: dict[str, list[str]]) -> None:
    privileges = [
        {"resource": {"db": db.name, "collection": collection}, "actions": actions}
        for collection, actions in collection_actions.items()
    ]
    await db.command({"createRole": role, "privileges": privileges, "roles": []})


async def _create_user(db: Any, username: str, password: str, role: str) -> None:
    await db.command(
        {"createUser": username, "pwd": password, "roles": [{"role": role, "db": db.name}]}
    )


@pytest.mark.skipif(
    not _RUN_REPLICA,
    reason=f"requires this execution's disposable local replica set via {_URI_ENV}",
)
def test_editorial_repositories_are_transactional_and_private_on_explicit_disposable_replica_set():
    uri = os.environ[_URI_ENV]
    replica_set = os.environ[_REPLICA_ENV]
    seed_host, seed_port = _assert_local_replica(uri, replica_set)

    async def run() -> None:
        admin_client: Any = AsyncMongoClient(uri, serverSelectionTimeoutMS=4000)
        database_name = _test_db_name()
        created_db = False
        scoped_clients: list[Any] = []
        try:
            hello = await admin_client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, replica_set)
            build_info = await admin_client.admin.command("buildInfo")
            assert str(build_info.get("version", "")).startswith("9.")

            db = admin_client[database_name]
            created_db = True
            writer_actions = {
                HEADS_COLLECTION: ["find", "insert", "update", "createIndex"],
                REVISIONS_COLLECTION: ["find", "insert", "createIndex"],
                PAYLOADS_COLLECTION: ["find", "insert", "createIndex"],
                EVENTS_COLLECTION: ["find", "insert", "createIndex"],
                OPERATIONS_COLLECTION: ["find", "insert", "update", "createIndex"],
            }
            await _create_scoped_role(db, "editorial_repository_writer", writer_actions)
            await _create_scoped_role(
                db,
                "editorial_metadata_reader",
                {
                    HEADS_COLLECTION: ["find"],
                    REVISIONS_COLLECTION: ["find"],
                    EVENTS_COLLECTION: ["find"],
                    OPERATIONS_COLLECTION: ["find"],
                },
            )
            await _create_scoped_role(
                db,
                "editorial_private_reader",
                {PAYLOADS_COLLECTION: ["find"]},
            )
            suffix = uuid.uuid4().hex[:12]
            writer_user, metadata_user, private_user = (
                f"editor_{suffix}",
                f"meta_{suffix}",
                f"private_{suffix}",
            )
            passwords = [uuid.uuid4().hex + "Aa1!" for _ in range(3)]
            await _create_user(db, writer_user, passwords[0], "editorial_repository_writer")
            await _create_user(db, metadata_user, passwords[1], "editorial_metadata_reader")
            await _create_user(db, private_user, passwords[2], "editorial_private_reader")

            writer_client: Any = AsyncMongoClient(
                _scoped_uri(uri, writer_user, passwords[0], database_name),
                serverSelectionTimeoutMS=4000,
            )
            metadata_client: Any = AsyncMongoClient(
                _scoped_uri(uri, metadata_user, passwords[1], database_name),
                serverSelectionTimeoutMS=4000,
            )
            private_client: Any = AsyncMongoClient(
                _scoped_uri(uri, private_user, passwords[2], database_name),
                serverSelectionTimeoutMS=4000,
            )
            scoped_clients.extend([writer_client, metadata_client, private_client])

            store = _make_store(writer_client[database_name])
            await store.ensure_indexes(_principal("editor"))
            block_result = await store.save_block(
                _block(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="block-create-001",
            )
            assert block_result.outcome == "created"
            assert block_result.revision_no == 1

            # Same key/payload is replayed; the same key with changed content conflicts.
            replay = await store.save_block(
                _block(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="block-create-001",
            )
            assert replay.outcome == "unchanged"
            assert replay.revision_id == block_result.revision_id
            with pytest.raises(EditorialIdempotencyConflictError):
                await store.save_block(
                    _block().model_copy(update={"body": "SYNTHETIC_CHANGED_BODY"}),
                    _principal("editor"),
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key="block-create-001",
                )

            answer_result = await store.save_block(
                _answer_block(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="answer-create-001",
            )
            answer_meta = await writer_client[database_name][REVISIONS_COLLECTION].find_one(
                {"revision_id": answer_result.revision_id}
            )
            event = await writer_client[database_name][EVENTS_COLLECTION].find_one(
                {"operation_ref": answer_result.operation_ref}
            )
            operation_doc = await writer_client[database_name][OPERATIONS_COLLECTION].find_one(
                {"operation_ref": answer_result.operation_ref}
            )
            for value in (answer_meta, event, operation_doc):
                assert value is not None
                assert "SYNTHETIC_PRIVATE_ANSWER" not in str(value)
                assert "SYNTHETIC_PRIVATE_EXPLANATION" not in str(value)

            metadata_db = metadata_client[database_name]
            assert (
                await metadata_db[HEADS_COLLECTION].find_one({"entity_ref": _block().ref})
                is not None
            )
            assert (
                await metadata_db[REVISIONS_COLLECTION].find_one(
                    {"revision_id": block_result.revision_id}
                )
                is not None
            )
            with pytest.raises(OperationFailure) as denied_private:
                await metadata_db[PAYLOADS_COLLECTION].find_one(
                    {"revision_id": answer_result.revision_id}
                )
            assert denied_private.value.code == 13
            with pytest.raises(OperationFailure) as denied_write:
                await metadata_db[HEADS_COLLECTION].insert_one({"entity_ref": "forbidden"})
            assert denied_write.value.code == 13

            private_db = private_client[database_name]
            private_document = await private_db[PAYLOADS_COLLECTION].find_one(
                {"revision_id": answer_result.revision_id}
            )
            assert private_document is not None
            assert "SYNTHETIC_PRIVATE_ANSWER" in str(private_document)

            # A normal editor cannot read full payloads without both explicit read capabilities.
            metadata_principal = _principal("metadata-reader")
            with pytest.raises(EditorialAuthorizationError):
                await store.get_revision(
                    "block", _block().ref, block_result.revision_id, metadata_principal
                )

            # Persist a placement only after its canonical block exists; scope remains undecided.
            placement_result = await store.save_placement(
                _placement(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="placement-create-001",
            )
            placement_read = await store.get_revision(
                "placement", _placement().ref, placement_result.revision_id, _principal("editor")
            )
            assert placement_read is not None
            assert isinstance(placement_read.payload, StoredPlacementPayload)
            assert placement_read.payload.placement.progress_scope == "undecided"
            with pytest.raises(EditorialVersionConflictError):
                await store.save_placement(
                    _placement("f1-placement-duplicate-fixture"),
                    _principal("editor"),
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key="placement-duplicate-pair-001",
                )
            assert (
                await writer_client[database_name][HEADS_COLLECTION].count_documents(
                    {"entity_kind": "placement"}
                )
                == 1
            )

            # Project snapshot pins the exact block revision; unresolved refs remain explicit.
            project_block = _block("f1-project-content-fixture", owner_ref="f1-delivery-fixture")
            project_block_result = await store.save_block(
                project_block,
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="project-block-create-001",
            )
            project_result = await store.save_project(
                _project(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="project-create-001",
            )
            project_read = await store.get_revision(
                "project", "f1-project-fixture", project_result.revision_id, _principal("editor")
            )
            assert project_read is not None
            assert isinstance(project_read.payload, StoredProjectPayload)
            pinned = project_read.payload.pinned_blocks[0]
            assert pinned.block_ref == project_block.ref
            assert pinned.revision_id == project_block_result.revision_id
            assert pinned.resolution == "pinned"

            unresolved_result = await store.save_project(
                _project(
                    project_ref="f1-project-unresolved-fixture",
                    content_ref="f1-unresolved-project-block",
                ),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="project-unresolved-create-001",
            )
            unresolved_read = await store.get_revision(
                "project",
                "f1-project-unresolved-fixture",
                unresolved_result.revision_id,
                _principal("editor"),
            )
            assert unresolved_read is not None
            assert isinstance(unresolved_read.payload, StoredProjectPayload)
            assert unresolved_read.payload.pinned_blocks[0].resolution == "unresolved"
            assert unresolved_read.payload.pinned_blocks[0].revision_id is None

            # A later canonical block revision cannot mutate a project's pinned snapshot.
            updated_project_block = project_block.model_copy(
                update={"body": "SYNTHETIC_PROJECT_BLOCK_REVISION_2"}
            )
            project_block_v2 = await store.save_block(
                updated_project_block,
                _principal("editor"),
                expected_revision_id=project_block_result.revision_id,
                expected_revision_no=1,
                idempotency_key="project-block-revision-002",
            )
            old_project_read = await store.get_revision(
                "project", "f1-project-fixture", project_result.revision_id, _principal("editor")
            )
            assert old_project_read is not None
            assert isinstance(old_project_read.payload, StoredProjectPayload)
            assert (
                old_project_read.payload.pinned_blocks[0].revision_id
                == project_block_result.revision_id
            )
            assert project_block_v2.revision_no == 2

            # CAS: exactly one concurrent divergent revision based on the same head can win.
            async def race(number: int) -> Any:
                candidate = _block().model_copy(update={"body": f"SYNTHETIC_RACE_{number}"})
                try:
                    return await store.save_block(
                        candidate,
                        _principal("editor"),
                        expected_revision_id=block_result.revision_id,
                        expected_revision_no=1,
                        idempotency_key=f"block-race-{number}",
                    )
                except EditorialVersionConflictError as exc:
                    return exc

            concurrent = await asyncio.gather(race(1), race(2))
            assert sum(isinstance(item, EditorialWriteResult) for item in concurrent) == 1
            assert sum(isinstance(item, EditorialVersionConflictError) for item in concurrent) == 1
            head_after_race = await store.get_head("block", _block().ref, _principal("editor"))
            assert head_after_race is not None and head_after_race.revision_no == 2

            async def create_race(number: int) -> Any:
                candidate = _block("f1-concurrent-create-fixture").model_copy(
                    update={"body": f"SYNTHETIC_CREATE_RACE_{number}"}
                )
                try:
                    return await store.save_block(
                        candidate,
                        _principal("editor"),
                        expected_revision_id=None,
                        expected_revision_no=None,
                        idempotency_key=f"block-create-race-{number}",
                    )
                except EditorialVersionConflictError as exc:
                    return exc

            creation_race = await asyncio.gather(create_race(1), create_race(2))
            assert sum(isinstance(item, EditorialWriteResult) for item in creation_race) == 1
            assert (
                sum(isinstance(item, EditorialVersionConflictError) for item in creation_race) == 1
            )
            assert (
                await writer_client[database_name][REVISIONS_COLLECTION].count_documents(
                    {"entity_ref": "f1-concurrent-create-fixture"}
                )
                == 1
            )

            async def same_key_replay() -> EditorialWriteResult:
                return await store.save_block(
                    _block("f1-concurrent-idempotency-fixture"),
                    _principal("editor"),
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key="block-concurrent-idempotency-001",
                )

            idempotent_race = await asyncio.gather(same_key_replay(), same_key_replay())
            assert {item.outcome for item in idempotent_race} == {"created", "unchanged"}
            assert len({item.revision_id for item in idempotent_race}) == 1
            assert (
                await writer_client[database_name][REVISIONS_COLLECTION].count_documents(
                    {"entity_ref": "f1-concurrent-idempotency-fixture"}
                )
                == 1
            )

            # Stale identity references cannot be moved to another subject or block.
            altered_placement = SharedPlacement.model_validate(
                {**_placement().model_dump(mode="python"), "subject_ref": "f1-other-topic"}
            )
            with pytest.raises(Exception):
                await store.save_placement(
                    altered_placement,
                    _principal("editor"),
                    expected_revision_id=placement_result.revision_id,
                    expected_revision_no=1,
                    idempotency_key="placement-identity-change-001",
                )

            history = await store.list_history("block", _block().ref, _principal("editor"))
            assert {item.revision_no for item in history.items} == {1, 2}
            operation_status = await store.get_operation_status(
                "block-create-001", _principal("editor")
            )
            assert operation_status.state == "confirmed"
            assert operation_status.outcome_conclusive is True

            # Indexes are inspected on the disposable MongoDB server itself.
            indexes = await db[HEADS_COLLECTION].index_information()
            assert indexes["one_curriculum_editorial_head"]["unique"] is True
            assert "expireAfterSeconds" not in str(indexes)
            revision_indexes = await db[REVISIONS_COLLECTION].index_information()
            assert revision_indexes["one_curriculum_editorial_revision_id"]["unique"] is True

        finally:
            for scoped in scoped_clients:
                await scoped.close()
            if created_db:
                await admin_client.drop_database(database_name)
            await admin_client.close()

    asyncio.run(run())


@pytest.mark.skipif(
    not _RUN_REPLICA,
    reason=f"requires this execution's disposable local replica set via {_URI_ENV}",
)
def test_transaction_rolls_back_payload_revision_event_and_head_after_injected_failure():
    uri = os.environ[_URI_ENV]
    replica_set = os.environ[_REPLICA_ENV]
    seed_host, seed_port = _assert_local_replica(uri, replica_set)

    async def run() -> None:
        client: Any = AsyncMongoClient(uri, serverSelectionTimeoutMS=4000)
        database_name = _test_db_name()
        created_db = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, replica_set)
            raw_db = client[database_name]
            created_db = True
            base_store = _make_store(raw_db)
            await base_store.ensure_indexes(_principal("editor"))
            fault_store = EditorialPersistenceStore(
                _FaultDatabase(raw_db, f"after_insert:{PAYLOADS_COLLECTION}"),
                authorizer=_authorizer,
                node_kind_resolver=_node_kind,
            )
            await fault_store.ensure_indexes(_principal("editor"))
            with pytest.raises(EditorialTransactionFailedError):
                await fault_store.save_block(
                    _block(),
                    _principal("editor"),
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key="rollback-block-001",
                )
            for collection in (
                HEADS_COLLECTION,
                REVISIONS_COLLECTION,
                PAYLOADS_COLLECTION,
                EVENTS_COLLECTION,
            ):
                assert await raw_db[collection].count_documents({}) == 0
            status = await base_store.get_operation_status(
                "rollback-block-001", _principal("editor")
            )
            assert status.state == "not_committed"
            # Explicit retry with the same command key is safe after a proven abort.
            replay = await base_store.save_block(
                _block(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="rollback-block-001",
            )
            assert replay.outcome == "created"
        finally:
            if created_db:
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


@pytest.mark.skipif(
    not _RUN_REPLICA,
    reason=f"requires this execution's disposable local replica set via {_URI_ENV}",
)
def test_unknown_commit_is_reconciled_without_new_revision():
    uri = os.environ[_URI_ENV]
    replica_set = os.environ[_REPLICA_ENV]
    seed_host, seed_port = _assert_local_replica(uri, replica_set)

    async def run() -> None:
        client: Any = AsyncMongoClient(uri, serverSelectionTimeoutMS=4000)
        database_name = _test_db_name()
        created_db = False
        try:
            hello = await client.admin.command("hello")
            _assert_single_local_member(hello, seed_host, seed_port, replica_set)
            raw_db = client[database_name]
            created_db = True
            base = _make_store(raw_db)
            await base.ensure_indexes(_principal("editor"))
            uncertain = EditorialPersistenceStore(
                _UnknownCommitDatabase(raw_db),
                authorizer=_authorizer,
                node_kind_resolver=_node_kind,
            )
            await uncertain.ensure_indexes(_principal("editor"))
            result = await uncertain.save_block(
                _block(),
                _principal("editor"),
                expected_revision_id=None,
                expected_revision_no=None,
                idempotency_key="unknown-commit-001",
            )
            assert result.outcome == "unchanged"
            assert await raw_db[REVISIONS_COLLECTION].count_documents({}) == 1
            assert await raw_db[PAYLOADS_COLLECTION].count_documents({}) == 1
            assert await raw_db[EVENTS_COLLECTION].count_documents({}) == 1
            assert await raw_db[HEADS_COLLECTION].count_documents({}) == 1
            status = await base.get_operation_status("unknown-commit-001", _principal("editor"))
            assert status.state == "confirmed"
            assert status.outcome_conclusive is True
        finally:
            if created_db:
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())


def test_transaction_support_is_required_on_explicit_disposable_standalone():
    if not _RUN_STANDALONE:
        pytest.skip("standalone isolation marker and explicit URI are not configured")
    uri = os.environ[_STANDALONE_URI_ENV]
    parts = urlsplit(uri)
    if parts.scheme != "mongodb" or not parts.hostname or parts.port is None:
        raise AssertionError("standalone URI must use an explicit host and port")
    if not parts.username or not parts.password:
        raise AssertionError("standalone test URI must authenticate")
    try:
        if not ipaddress.ip_address(parts.hostname).is_loopback:
            raise AssertionError("standalone test host must be loopback")
    except ValueError:
        if parts.hostname.casefold() != "localhost":
            raise AssertionError("standalone test host must be loopback")
    query = {key.casefold() for key, _value in parse_qsl(parts.query)}
    if "replicaset" in query or "directconnection" in query:
        raise AssertionError("standalone URI must not masquerade as a replica set")

    async def run() -> None:
        client: Any = AsyncMongoClient(uri, serverSelectionTimeoutMS=4000)
        database_name = _test_db_name()
        created_db = False
        try:
            hello = await client.admin.command("hello")
            if hello.get("setName") is not None or hello.get("msg") == "isdbgrid":
                raise AssertionError("configured server is not a standalone test process")
            raw_db = client[database_name]
            created_db = True
            store = _make_store(raw_db)
            await store.ensure_indexes(_principal("editor"))
            with pytest.raises(EditorialTransactionsRequiredError):
                await store.save_block(
                    _block(),
                    _principal("editor"),
                    expected_revision_id=None,
                    expected_revision_no=None,
                    idempotency_key="standalone-rejected-001",
                )
            status = await store.get_operation_status(
                "standalone-rejected-001", _principal("editor")
            )
            assert status.state == "not_committed"
        finally:
            if created_db:
                await client.drop_database(database_name)
            await client.close()

    asyncio.run(run())
