"""Unit contracts for typed activity storage; fake transactions are not Mongo proof."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError, OperationFailure

from curriculum_contract.activity_persistence import (
    ActivityPersistenceAuthorizationError,
    ActivityPersistenceError,
    ActivityTransactionFailedError,
    ActivityTransactionOutcomeUnknownError,
    ActivityTransactionsRequiredError,
    ActivityVersionConflictError,
    ActivityVersionIntegrityError,
    TypedActivityDraftStore,
    _private_content_hash,
    build_activity_version_documents,
)
from curriculum_contract.models import SourceProvenance
from curriculum_contract.typed_activities import (
    ActivityIntegrity,
    ActivityKind,
    ActivityOption,
    ActivityVersionRef,
    EvaluationPolicy,
    EvaluatorCompatibility,
    ObjectiveQuizPolicy,
    PrivateActivity,
    PrivateAnswerMaterial,
    PrivateDiscursiveData,
    PrivateMatchingData,
    PrivateMultipleChoiceData,
    PrivateOrderingData,
    PrivateShortAnswerData,
    PublicActivity,
    PublicationState,
    PublicDiscursiveActivity,
    PublicMatchingActivity,
    PublicMultipleChoiceActivity,
    PublicOrderingActivity,
    PublicReviewActivity,
    PublicShortAnswerActivity,
    TypedActivityRecord,
    UndecidedPolicy,
    UnscoredPolicy,
    ValidationState,
)

PRIVATE_SENTINEL = "PRIVATE_14F_ANSWER_SENTINEL"


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sample_activity(
    kind: ActivityKind,
    number: int,
    correct_option: str = "a",
    prompt_text: str | None = None,
) -> TypedActivityRecord:
    """Sanitized synthetic fixture shaped like the 14E typed records."""
    activity_ref = f"f1-test-activity-{number:02d}"
    prompt = prompt_text or f"Sanitized {kind} prompt {number}."
    question_hash = hashlib.sha256(prompt.encode()).hexdigest()
    key_text = PRIVATE_SENTINEL if kind != "review" else None
    answer_hash = hashlib.sha256((key_text or "no-key").encode()).hexdigest()
    question_source = SourceProvenance(
        source_file="docs/fixtures/typed_activity_sanitized.md",
        source_sha256=question_hash,
        manifest_ref="sanitized-test-fixture",
        source_role="quiz",
        source_id=f"Q{number}",
    )
    answer_source = SourceProvenance(
        source_file="docs/fixtures/typed_activity_answer_sanitized.md",
        source_sha256=answer_hash,
        manifest_ref="sanitized-test-fixture",
        source_role="answer_key",
        source_id=f"A{number}",
    )
    version_ref: ActivityVersionRef = f"question-source-sha256:{question_hash}"
    common: dict[str, Any] = {
        "activity_ref": activity_ref,
        "version_ref": version_ref,
        "title": f"Sanitized activity {number}",
        "order": number,
        "prompt": prompt,
        "instructions": "Use only the supplied information.",
    }
    public: PublicActivity
    if kind == "multiple_choice":
        public = PublicMultipleChoiceActivity(
            **common,
            type="multiple_choice",
            options=[
                ActivityOption(option_id="a", text="Choice A"),
                ActivityOption(option_id="b", text="Choice B"),
            ],
        )
    elif kind == "short_answer":
        public = PublicShortAnswerActivity(**common, type="short_answer")
    elif kind == "discursive":
        public = PublicDiscursiveActivity(**common, type="discursive")
    elif kind == "matching":
        public = PublicMatchingActivity(**common, type="matching", left_items=[], right_items=[])
    elif kind == "ordering":
        public = PublicOrderingActivity(**common, type="ordering", items=[])
    elif kind == "review":
        public = PublicReviewActivity(**common, type="review")
    else:
        raise AssertionError(f"unsupported test kind: {kind}")

    key_id = f"f1-test-activity-{number:02d}-key"
    material = (
        PrivateAnswerMaterial(
            answer_key_ref=key_id,
            question_ref=activity_ref,
            correct_option_ref=correct_option if kind == "multiple_choice" else None,
            expected_answer=key_text,
            accepted_answers=[],
            explanation=f"Private explanation {number}",
            source_markdown=f"Answer source {number}: {PRIVATE_SENTINEL}",
            provenance=answer_source,
        )
        if kind != "review"
        else None
    )
    private: PrivateActivity | None = None
    validation_state: ValidationState
    publication_state: PublicationState
    evaluator: EvaluatorCompatibility
    policy: EvaluationPolicy
    if kind == "multiple_choice":
        private = PrivateMultipleChoiceData(
            type="multiple_choice",
            answer_material=material,
            resolved_correct_option_id=correct_option,
        )
        validation_state = "valid"
        publication_state = "structurally_validated"
        evaluator = "compatible"
        policy = ObjectiveQuizPolicy(type="objective_server_policy")
    elif kind == "short_answer":
        private = PrivateShortAnswerData(type="short_answer", answer_material=material)
        validation_state = "pending_review"
        publication_state = "pending_review"
        evaluator = "unsupported"
        policy = UndecidedPolicy(type="undecided")
    elif kind == "discursive":
        private = PrivateDiscursiveData(type="discursive", answer_material=material)
        validation_state = "pending_review"
        publication_state = "pending_review"
        evaluator = "unsupported"
        policy = UndecidedPolicy(type="undecided")
    elif kind == "matching":
        private = PrivateMatchingData(type="matching", answer_material=material, correct_pairs=[])
        validation_state = "incomplete"
        publication_state = "pending_review"
        evaluator = "unsupported"
        policy = UndecidedPolicy(type="undecided")
    elif kind == "ordering":
        private = PrivateOrderingData(
            type="ordering", answer_material=material, correct_order_refs=[]
        )
        validation_state = "incomplete"
        publication_state = "pending_review"
        evaluator = "unsupported"
        policy = UndecidedPolicy(type="undecided")
    else:
        validation_state = "valid"
        publication_state = "pending_review"
        evaluator = "not_applicable"
        policy = UnscoredPolicy(type="unscored")

    private_dump = private.model_dump(mode="json") if private is not None else None
    record = TypedActivityRecord(
        activity_ref=activity_ref,
        activity_type=kind,
        phase=1,
        source_id=f"Q{number}",
        source_markdown=prompt,
        public=public,
        private=private,
        version_ref=version_ref,
        validation_state=validation_state,
        publication_state=publication_state,
        evaluator_compatibility=evaluator,
        evaluation_policy=policy,
        provenance=question_source,
        integrity=ActivityIntegrity(
            question_source_sha256=question_hash,
            answer_source_sha256=answer_hash if material is not None else None,
            public_payload_sha256=_canonical_hash(public.model_dump(mode="json")),
            private_payload_sha256=_canonical_hash(private_dump)
            if private_dump is not None
            else None,
        ),
    )
    return record


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict]] = []
        self.fail_inserts = False

    async def create_index(self, keys, **options):
        self.indexes.append((list(keys), options))
        return options.get("name", "fake-index")

    async def insert_one(self, document, session=None):
        if self.fail_inserts:
            raise OperationFailure("injected disposable fake failure")
        for existing in self.documents:
            for keys, options in self.indexes:
                if options.get("unique") and all(
                    existing.get(field) == document.get(field) for field, _direction in keys
                ):
                    raise DuplicateKeyError("fake unique-index conflict")
        self.documents.append(copy.deepcopy(document))
        return type("InsertResult", (), {"inserted_id": document.get("_id")})()

    async def find_one(self, query, projection=None, session=None):
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                if projection is None:
                    return copy.deepcopy(document)
                selected = {
                    key: copy.deepcopy(document[key])
                    for key, include in projection.items()
                    if include and key in document
                }
                if "_id" in document:
                    selected["_id"] = document["_id"]
                return selected
        return None

    async def update_one(self, query, update, session=None):
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                for key, value in update.get("$set", {}).items():
                    document[key] = copy.deepcopy(value)
                for key, value in update.get("$inc", {}).items():
                    document[key] = document.get(key, 0) + value
                return type("UpdateResult", (), {"matched_count": 1})()
        return type("UpdateResult", (), {"matched_count": 0})()

    def find(self, query, projection=None):
        documents = []
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                if projection is None:
                    documents.append(copy.deepcopy(document))
                else:
                    selected = {
                        key: copy.deepcopy(document[key])
                        for key, include in projection.items()
                        if include and key in document
                    }
                    if "_id" in document:
                        selected["_id"] = document["_id"]
                    documents.append(selected)
        return FakeCursor(documents)


class FakeCursor:
    def __init__(self, documents: list[dict]) -> None:
        self.documents = documents

    def sort(self, keys):
        for field, direction in reversed(keys):
            self.documents.sort(key=lambda row: row.get(field), reverse=direction < 0)
        return self

    def limit(self, amount: int):
        self.documents = self.documents[:amount]
        return self

    async def to_list(self, amount: int):
        return self.documents[:amount]


class FakeSession:
    def __init__(self, database) -> None:
        self.database = database

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def with_transaction(self, callback):
        async with self.database.lock:
            before = {
                name: copy.deepcopy(collection.documents)
                for name, collection in self.database.collections.items()
            }
            try:
                result = await callback(self)
            except Exception:
                for name, rows in before.items():
                    self.database.collections[name].documents = rows
                raise
            if self.database.unknown_commit_once:
                self.database.unknown_commit_once = False
                error = OperationFailure("injected unknown commit result")
                error._add_error_label("UnknownTransactionCommitResult")
                raise error
            return result


class FakeClient:
    def __init__(self, database) -> None:
        self.database = database

    def start_session(self):
        return FakeSession(self.database)


class FakeDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, FakeCollection] = {}
        self.lock = asyncio.Lock()
        self.unknown_commit_once = False
        self.client = FakeClient(self)

    def __getitem__(self, name: str) -> FakeCollection:
        return self.collections.setdefault(name, FakeCollection())


ADMIN = {"id": "admin-test", "role": "admin"}
STUDENT = {"id": "student-test", "role": "student"}


def test_storage_splits_public_private_and_audit_for_all_six_types():
    kinds = ["multiple_choice", "short_answer", "discursive", "matching", "ordering", "review"]
    for index, kind in enumerate(kinds, start=1):
        record = sample_activity(kind, index)
        public, private, event = build_activity_version_documents(
            record,
            version_id=f"{index:024x}",
            actor_id="admin-test",
            created_at=datetime(2026, 10, 28, tzinfo=UTC),
        )
        public_text = json.dumps(public.model_dump(mode="json"), ensure_ascii=False)
        private_text = json.dumps(private.model_dump(mode="json"), ensure_ascii=False)
        event_text = json.dumps(event.model_dump(mode="json"), ensure_ascii=False)
        assert public.activity_type == kind
        assert PRIVATE_SENTINEL not in public_text
        assert "correct_option_ref" not in public_text
        assert "private_content_sha256" not in public_text
        assert event.activity_type == kind
        assert PRIVATE_SENTINEL not in event_text
        if kind == "review":
            assert private.private_payload is None
        else:
            assert PRIVATE_SENTINEL in private_text


def test_private_answer_change_creates_a_distinct_content_fingerprint():
    first = sample_activity("multiple_choice", 1, correct_option="a")
    second = sample_activity("multiple_choice", 1, correct_option="b")
    assert first.version_ref == second.version_ref
    assert _private_content_hash(first) != _private_content_hash(second)


def test_published_records_cannot_enter_draft_store():
    published = sample_activity("multiple_choice", 1).model_copy(
        update={"publication_state": "published"}
    )
    with pytest.raises(ActivityPersistenceError, match="published activities"):
        build_activity_version_documents(published, version_id="1" * 24, actor_id="admin-test")


def test_publishable_is_only_an_editorial_label_not_operational_publication():
    record = sample_activity("multiple_choice", 1).model_copy(
        update={"publication_state": "publishable"}
    )
    public, _private, event = build_activity_version_documents(
        record, version_id="1" * 24, actor_id="admin-test"
    )
    assert public.publication_state == "publishable"
    assert event.publication_state == "publishable"


def test_public_stored_schema_rejects_private_fields():
    record = sample_activity("multiple_choice", 1)
    public, _private, _event = build_activity_version_documents(
        record, version_id="1" * 24, actor_id="admin-test"
    )
    payload = public.model_dump(mode="json")
    payload["correct_option_ref"] = "a"
    with pytest.raises(ValidationError):
        type(public).model_validate(payload)


def test_store_authentication_reuses_platform_permissions_and_denies_students():
    store = TypedActivityDraftStore(FakeDatabase())
    assert store._require(ADMIN, "content.write") == "admin-test"
    with pytest.raises(ActivityPersistenceAuthorizationError):
        store._require(STUDENT, "content.write")
    with pytest.raises(ActivityPersistenceAuthorizationError):
        store._require(STUDENT, "submissions.grade")


def test_idempotent_write_and_public_private_reads_use_separate_collections():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        record = sample_activity("multiple_choice", 1)
        first = await store.save_version(record, ADMIN)
        retry = await store.save_version(record, ADMIN)
        assert first.outcome == "created"
        assert retry.outcome == "unchanged"
        assert retry.version_id == first.version_id
        public = await store.get_public_version(record.activity_ref, first.version_id, ADMIN)
        assert public is not None
        assert PRIVATE_SENTINEL not in json.dumps(public.model_dump(mode="json"))
        assert len(database["typed_activity_public_versions"].documents) == 1
        assert len(database["typed_activity_private_versions"].documents) == 1
        assert len(database["typed_activity_version_events"].documents) == 1
        with pytest.raises(ActivityPersistenceAuthorizationError):
            await store.get_private_version(record.activity_ref, first.version_id, STUDENT)
        private = await store.get_private_version(record.activity_ref, first.version_id, ADMIN)
        assert private is not None
        assert PRIVATE_SENTINEL in json.dumps(private.model_dump(mode="json"))

    asyncio.run(run())


def test_repository_serializes_all_six_types_in_fake_database():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        kinds = ["multiple_choice", "short_answer", "discursive", "matching", "ordering", "review"]
        for index, kind in enumerate(kinds, start=1):
            result = await store.save_version(sample_activity(kind, index), ADMIN)
            assert result.outcome == "created"
        public_rows = database["typed_activity_public_versions"].documents
        private_rows = database["typed_activity_private_versions"].documents
        event_rows = database["typed_activity_version_events"].documents
        assert {row["activity_type"] for row in public_rows} == set(kinds)
        assert {row["activity_type"] for row in private_rows} == set(kinds)
        assert len(public_rows) == len(private_rows) == len(event_rows) == 6

    asyncio.run(run())


def test_repository_declares_immutable_version_and_head_indexes():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        await store.ensure_indexes()
        indexes = {
            (name, tuple(keys), options.get("unique", False))
            for collection in database.collections.values()
            for keys, options in collection.indexes
            for name in (options.get("name"),)
        }
        assert (
            "one_typed_activity_public_version",
            (("activity_ref", 1), ("version_id", 1)),
            True,
        ) in indexes
        assert (
            "one_typed_activity_content_revision",
            (("activity_ref", 1), ("private_content_sha256", 1)),
            True,
        ) in indexes
        assert (
            "one_typed_activity_current_head",
            (("activity_ref", 1),),
            True,
        ) in indexes

    asyncio.run(run())


def test_new_content_revision_preserves_prior_version_and_history():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        first_record = sample_activity("multiple_choice", 1, correct_option="a")
        revised_record = sample_activity(
            "multiple_choice", 1, prompt_text="Sanitized revised prompt 1."
        )
        first = await store.save_version(first_record, ADMIN)
        revised = await store.save_version(
            revised_record, ADMIN, expected_version_id=first.version_id
        )
        assert revised.outcome == "created"
        assert revised.version_id != first.version_id
        history = await store.list_versions(first_record.activity_ref, ADMIN)
        assert len(history) == 2
        assert {item.version_id for item in history} == {first.version_id, revised.version_id}
        assert len(database["typed_activity_private_versions"].documents) == 2
        current_head = database["typed_activity_heads"].documents[0]
        assert current_head["current_version_id"] == revised.version_id
        assert current_head["revision"] == 2

    asyncio.run(run())


def test_divergent_concurrent_revisions_from_same_base_conflict_in_fake_repository():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        initial = await store.save_version(sample_activity("multiple_choice", 1), ADMIN)
        left = sample_activity(
            "multiple_choice", 1, prompt_text="Sanitized left revision prompt 1."
        )
        right = sample_activity(
            "multiple_choice", 1, prompt_text="Sanitized right revision prompt 1."
        )
        outcomes = await asyncio.gather(
            store.save_version(left, ADMIN, expected_version_id=initial.version_id),
            store.save_version(right, ADMIN, expected_version_id=initial.version_id),
            return_exceptions=True,
        )
        assert sum(isinstance(result, ActivityVersionConflictError) for result in outcomes) == 1
        assert (
            sum(
                not isinstance(result, BaseException) and result.outcome == "created"
                for result in outcomes
            )
            == 1
        )
        assert len(database["typed_activity_public_versions"].documents) == 2
        assert database["typed_activity_heads"].documents[0]["revision"] == 2

    asyncio.run(run())


def test_changed_content_requires_explicit_current_base_version():
    async def run():
        store = TypedActivityDraftStore(FakeDatabase())
        first = await store.save_version(sample_activity("multiple_choice", 1), ADMIN)
        with pytest.raises(ActivityVersionConflictError, match="head changed"):
            await store.save_version(
                sample_activity("multiple_choice", 1, correct_option="b"), ADMIN
            )
        assert first.outcome == "created"

    asyncio.run(run())


def test_existing_history_without_head_fails_closed():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        record = sample_activity("multiple_choice", 1)
        public, private, _event = build_activity_version_documents(
            record, version_id="1" * 24, actor_id="admin-test"
        )
        database["typed_activity_public_versions"].documents.append(
            public.model_dump(mode="python")
        )
        database["typed_activity_private_versions"].documents.append(
            private.model_dump(mode="python")
        )
        with pytest.raises(ActivityVersionIntegrityError, match="without its current head"):
            await store.save_version(
                sample_activity("multiple_choice", 1, prompt_text="Sanitized replacement prompt."),
                ADMIN,
            )

    asyncio.run(run())


def test_revision_fails_closed_when_current_head_pair_is_incomplete():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        initial_record = sample_activity("multiple_choice", 1)
        initial = await store.save_version(initial_record, ADMIN)
        database["typed_activity_private_versions"].documents.clear()
        revised = sample_activity(
            "multiple_choice", 1, prompt_text="Sanitized revision after corrupt head."
        )

        with pytest.raises(ActivityVersionIntegrityError, match="incomplete version pair"):
            await store.save_version(revised, ADMIN, expected_version_id=initial.version_id)

        assert len(database["typed_activity_public_versions"].documents) == 1
        assert not database["typed_activity_private_versions"].documents
        assert len(database["typed_activity_version_events"].documents) == 1
        head = database["typed_activity_heads"].documents[0]
        assert head["current_version_id"] == initial.version_id
        assert head["revision"] == 1

    asyncio.run(run())


def test_idempotent_replay_rejects_corrupt_public_private_identity_pair():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        record = sample_activity("multiple_choice", 1)
        await store.save_version(record, ADMIN)
        database["typed_activity_public_versions"].documents[0]["source_version_ref"] = (
            "question-source-sha256:" + "0" * 64
        )
        with pytest.raises(ActivityVersionIntegrityError, match="integrity"):
            await store.save_version(record, ADMIN)

    asyncio.run(run())


def test_editorial_state_change_is_a_conflict_not_an_overwrite():
    async def run():
        store = TypedActivityDraftStore(FakeDatabase())
        record = sample_activity("multiple_choice", 1)
        await store.save_version(record, ADMIN)
        changed_state = record.model_copy(update={"publication_state": "pending_review"})
        with pytest.raises(ActivityVersionConflictError, match="differs"):
            await store.save_version(changed_state, ADMIN)

    asyncio.run(run())


def test_failed_transaction_rolls_back_all_fake_rows_without_claiming_mongo_proof():
    async def run():
        database = FakeDatabase()
        store = TypedActivityDraftStore(database)
        database["typed_activity_version_events"].fail_inserts = True
        with pytest.raises(ActivityTransactionFailedError):
            await store.save_version(sample_activity("multiple_choice", 1), ADMIN)
        assert not database["typed_activity_public_versions"].documents
        assert not database["typed_activity_private_versions"].documents
        assert not database["typed_activity_version_events"].documents

    asyncio.run(run())


def test_unknown_commit_result_is_reconciled_by_idempotent_replay():
    async def run():
        database = FakeDatabase()
        database.unknown_commit_once = True
        store = TypedActivityDraftStore(database)
        record = sample_activity("multiple_choice", 1)
        with pytest.raises(ActivityTransactionOutcomeUnknownError):
            await store.save_version(record, ADMIN)
        replay = await store.save_version(record, ADMIN)
        assert replay.outcome == "unchanged"
        assert len(database["typed_activity_public_versions"].documents) == 1
        assert len(database["typed_activity_private_versions"].documents) == 1
        assert len(database["typed_activity_version_events"].documents) == 1
        assert len(database["typed_activity_heads"].documents) == 1

    asyncio.run(run())


def test_standalone_transaction_error_is_not_misreported_as_write_failure():
    class StandaloneClient:
        def start_session(self):
            raise OperationFailure(
                "Transaction numbers are only allowed on a replica set member or mongos", code=20
            )

    async def run():
        database = FakeDatabase()
        database.client = StandaloneClient()
        store = TypedActivityDraftStore(database)
        with pytest.raises(ActivityTransactionsRequiredError):
            await store.save_version(sample_activity("multiple_choice", 1), ADMIN)
        assert not database["typed_activity_public_versions"].documents
        assert not database["typed_activity_private_versions"].documents

    asyncio.run(run())


def test_concurrent_identical_writes_are_idempotent_in_fake_repository_only():
    async def run():
        store = TypedActivityDraftStore(FakeDatabase())
        record = sample_activity("multiple_choice", 1)
        results = await asyncio.gather(
            store.save_version(record, ADMIN),
            store.save_version(record, ADMIN),
        )
        assert sorted(result.outcome for result in results) == ["created", "unchanged"]

    asyncio.run(run())
