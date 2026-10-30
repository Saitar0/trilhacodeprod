"""Isolated, versioned Mongo persistence for typed curriculum activities.

This store is an authoring/draft repository only. It is deliberately not wired
to application routes, quiz publication, student reads, or curricular import.
Public and private snapshots live in separate collections and are inserted in
one MongoDB transaction; a replica set is therefore required for writes.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Annotated, Any, Callable, Literal, TypeGuard

from bson import ObjectId
from pydantic import Field, StringConstraints, ValidationError, model_validator
from pymongo.errors import (
    AutoReconnect,
    DuplicateKeyError,
    InvalidOperation,
    NetworkTimeout,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from permissions import has_permission

from .models import ContractModel, NonEmptyText, SourceProvenance, StableId
from .typed_activities import (
    ActivityDiagnostic,
    ActivityIntegrity,
    ActivityKind,
    ActivityVersionRef,
    EvaluationPolicy,
    EvaluatorCompatibility,
    PrivateActivity,
    PublicActivity,
    PublicationState,
    Sha256,
    TypedActivityRecord,
    ValidationState,
)

STORAGE_SCHEMA_VERSION: Literal["trilhacode.activity_store/1.0"] = "trilhacode.activity_store/1.0"
PUBLIC_COLLECTION = "typed_activity_public_versions"
PRIVATE_COLLECTION = "typed_activity_private_versions"
EVENT_COLLECTION = "typed_activity_version_events"
HEAD_COLLECTION = "typed_activity_heads"
_STORABLE_STATES = {
    "draft",
    "pending_review",
    "structurally_validated",
    "publishable",
}
MongoVersionId = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{24}$")]
_PUBLIC_PROJECTION = {
    "version_id": 1,
    "activity_ref": 1,
    "source_version_ref": 1,
    "activity_type": 1,
    "phase": 1,
    "source_id": 1,
    "source_markdown": 1,
    "public": 1,
    "validation_state": 1,
    "publication_state": 1,
    "evaluator_compatibility": 1,
    "evaluation_policy": 1,
    "provenance": 1,
    "integrity": 1,
    "diagnostics": 1,
    "created_at": 1,
    "created_by": 1,
    "storage_schema_version": 1,
}
_PRIVATE_PROJECTION = {
    "version_id": 1,
    "activity_ref": 1,
    "activity_type": 1,
    "private_payload": 1,
    "private_content_sha256": 1,
    "answer_source_sha256": 1,
    "private_payload_sha256": 1,
    "created_at": 1,
    "created_by": 1,
    "storage_schema_version": 1,
}


class ActivityPersistenceError(RuntimeError):
    """Base error with sanitized messages for the isolated activity store."""


class ActivityPersistenceAuthorizationError(ActivityPersistenceError):
    """The current platform role does not authorize the requested action."""


class ActivityVersionConflictError(ActivityPersistenceError):
    """An immutable version identity already exists with different metadata."""


class ActivityVersionIntegrityError(ActivityPersistenceError):
    """Public/private version rows do not form a complete immutable pair."""


class ActivityTransactionsRequiredError(ActivityPersistenceError):
    """MongoDB did not provide transaction support for the paired write."""


class ActivityTransactionOutcomeUnknownError(ActivityPersistenceError):
    """The caller must replay identical content to reconcile an uncertain commit."""


class ActivityTransactionFailedError(ActivityPersistenceError):
    """A transaction failed; retrying identical content is safe for reconciliation."""


class PublicActivityIntegrity(ContractModel):
    question_source_sha256: Sha256
    public_payload_sha256: Sha256


StoredEditorialState = Literal["draft", "pending_review", "structurally_validated", "publishable"]


class StoredActivityPublicVersion(ContractModel):
    """Answer-key-free snapshot. This is not the student HTTP response model."""

    storage_schema_version: Literal["trilhacode.activity_store/1.0"] = STORAGE_SCHEMA_VERSION
    version_id: MongoVersionId
    activity_ref: StableId
    source_version_ref: ActivityVersionRef
    activity_type: ActivityKind
    phase: int = Field(strict=True, ge=1, le=10)
    source_id: NonEmptyText
    source_markdown: NonEmptyText
    public: PublicActivity
    validation_state: ValidationState
    publication_state: StoredEditorialState
    evaluator_compatibility: EvaluatorCompatibility
    evaluation_policy: EvaluationPolicy
    provenance: SourceProvenance
    integrity: PublicActivityIntegrity
    diagnostics: list[ActivityDiagnostic]
    created_at: datetime
    created_by: NonEmptyText

    @model_validator(mode="after")
    def validate_public_snapshot(self) -> StoredActivityPublicVersion:
        if (
            self.public.activity_ref != self.activity_ref
            or self.public.version_ref != self.source_version_ref
            or self.public.type != self.activity_type
        ):
            raise ValueError("stored public activity identity/version/type are inconsistent")
        payload_hash = hashlib.sha256(
            _canonical_bytes(self.public.model_dump(mode="json"))
        ).hexdigest()
        if payload_hash != self.integrity.public_payload_sha256:
            raise ValueError("stored public activity integrity hash does not match")
        return self

    @classmethod
    def from_record(
        cls, record: TypedActivityRecord, *, version_id: str, created_at: datetime, created_by: str
    ) -> StoredActivityPublicVersion:
        if not _is_storable_state(record.publication_state):
            raise ActivityPersistenceError("published activities cannot enter the draft store")
        return cls(
            version_id=version_id,
            activity_ref=record.activity_ref,
            source_version_ref=record.version_ref,
            activity_type=record.activity_type,
            phase=record.phase,
            source_id=record.source_id,
            source_markdown=record.source_markdown,
            public=record.public,
            validation_state=record.validation_state,
            publication_state=record.publication_state,
            evaluator_compatibility=record.evaluator_compatibility,
            evaluation_policy=record.evaluation_policy,
            provenance=record.provenance,
            integrity=PublicActivityIntegrity(
                question_source_sha256=record.integrity.question_source_sha256,
                public_payload_sha256=record.integrity.public_payload_sha256,
            ),
            diagnostics=record.diagnostics,
            created_at=created_at,
            created_by=created_by,
        )


class StoredActivityPrivateVersion(ContractModel):
    """Private companion snapshot, queried only through an authorized path."""

    storage_schema_version: Literal["trilhacode.activity_store/1.0"] = STORAGE_SCHEMA_VERSION
    version_id: MongoVersionId
    activity_ref: StableId
    activity_type: ActivityKind
    private_payload: PrivateActivity | None = Field(repr=False)
    private_content_sha256: Sha256 = Field(repr=False)
    answer_source_sha256: Sha256 | None = Field(default=None, repr=False)
    private_payload_sha256: Sha256 | None = Field(default=None, repr=False)
    created_at: datetime
    created_by: NonEmptyText

    @model_validator(mode="after")
    def validate_private_snapshot(self) -> StoredActivityPrivateVersion:
        if self.private_payload is not None and self.private_payload.type != self.activity_type:
            raise ValueError("stored private activity type does not match version metadata")
        if (self.private_payload is None) != (self.private_payload_sha256 is None):
            raise ValueError("stored private payload and integrity hash must appear together")
        if self.private_payload is not None:
            payload_hash = hashlib.sha256(
                _canonical_bytes(self.private_payload.model_dump(mode="json"))
            ).hexdigest()
            if payload_hash != self.private_payload_sha256:
                raise ValueError("stored private activity integrity hash does not match")
            answer_material = getattr(self.private_payload, "answer_material", None)
            if answer_material is not None and (
                answer_material.provenance.source_sha256 != self.answer_source_sha256
            ):
                raise ValueError("stored answer-key provenance hash does not match")
        return self


class ActivityVersionCreatedEvent(ContractModel):
    """Append-only creation metadata; never contains answer material or hashes."""

    storage_schema_version: Literal["trilhacode.activity_store/1.0"] = STORAGE_SCHEMA_VERSION
    event_type: Literal["version_created"] = "version_created"
    version_id: MongoVersionId
    activity_ref: StableId
    activity_type: ActivityKind
    publication_state: StoredEditorialState
    created_at: datetime
    created_by: NonEmptyText


class StoredActivityHead(ContractModel):
    """Compare-and-swap pointer used to serialize editorial revisions."""

    storage_schema_version: Literal["trilhacode.activity_store/1.0"] = STORAGE_SCHEMA_VERSION
    activity_ref: StableId
    current_version_id: MongoVersionId
    revision: int = Field(strict=True, ge=1)
    updated_at: datetime
    updated_by: NonEmptyText


class ActivityVersionSummary(ContractModel):
    version_id: MongoVersionId
    activity_ref: StableId
    source_version_ref: str
    activity_type: ActivityKind
    validation_state: ValidationState
    publication_state: StoredEditorialState
    created_at: datetime


class ActivityVersionWriteResult(ContractModel):
    outcome: Literal["created", "unchanged"]
    version_id: str
    activity_ref: StableId


Authorizer = Callable[[dict[str, Any], str], bool]


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _private_content_hash(record: TypedActivityRecord) -> str:
    """Fingerprint the immutable activity content without publicizing its key.

    Editorial publication state is a separate state transition and is excluded;
    a caller cannot use this store to perform that transition. Diagnostics are
    derived output and are excluded so parser message changes do not fork content.
    """
    basis = record.model_dump(mode="json")
    basis.pop("publication_state", None)
    basis.pop("diagnostics", None)
    return hashlib.sha256(_canonical_bytes(basis)).hexdigest()


def _record_from_stored_pair(
    public_document: dict[str, Any], private_document: dict[str, Any]
) -> TypedActivityRecord:
    try:
        public = StoredActivityPublicVersion.model_validate(
            {key: value for key, value in public_document.items() if key != "_id"}
        )
        private = StoredActivityPrivateVersion.model_validate(
            {key: value for key, value in private_document.items() if key != "_id"}
        )
    except ValidationError as exc:
        raise ActivityVersionIntegrityError(
            "stored public/private activity version failed integrity validation"
        ) from exc
    if (
        public.activity_ref != private.activity_ref
        or public.version_id != private.version_id
        or public.activity_type != private.activity_type
    ):
        raise ActivityVersionIntegrityError(
            "public/private activity version identities do not match"
        )
    try:
        return TypedActivityRecord(
            activity_ref=public.activity_ref,
            activity_type=public.activity_type,
            phase=public.phase,
            source_id=public.source_id,
            source_markdown=public.source_markdown,
            public=public.public,
            private=private.private_payload,
            version_ref=public.source_version_ref,
            validation_state=public.validation_state,
            publication_state=public.publication_state,
            evaluator_compatibility=public.evaluator_compatibility,
            evaluation_policy=public.evaluation_policy,
            provenance=public.provenance,
            diagnostics=public.diagnostics,
            integrity=ActivityIntegrity(
                question_source_sha256=public.integrity.question_source_sha256,
                answer_source_sha256=private.answer_source_sha256,
                public_payload_sha256=public.integrity.public_payload_sha256,
                private_payload_sha256=private.private_payload_sha256,
            ),
        )
    except ValidationError as exc:
        raise ActivityVersionIntegrityError(
            "stored public/private activity contents are inconsistent"
        ) from exc


def _authorize_platform_role(user: dict[str, Any], permission: str) -> bool:
    return bool(user.get("id")) and has_permission(user, permission)


def _is_storable_state(
    value: PublicationState,
) -> TypeGuard[StoredEditorialState]:
    return value in _STORABLE_STATES


def _is_transaction_unsupported(error: BaseException) -> bool:
    message = str(error).casefold()
    unsupported_phrases = (
        "transaction numbers are only allowed on a replica set member or mongos",
        "transactions are not supported",
        "transaction support is not available",
    )
    return (isinstance(error, OperationFailure) and error.code == 20) or any(
        phrase in message for phrase in unsupported_phrases
    )


def _mongo_doc(model: ContractModel) -> dict[str, Any]:
    return model.model_dump(mode="python")


def build_activity_version_documents(
    record: TypedActivityRecord,
    *,
    version_id: str,
    actor_id: str,
    created_at: datetime | None = None,
) -> tuple[StoredActivityPublicVersion, StoredActivityPrivateVersion, ActivityVersionCreatedEvent]:
    """Build validated, separate public/private/event rows without database I/O."""
    publication_state = record.publication_state
    if not _is_storable_state(publication_state):
        raise ActivityPersistenceError("published activities cannot enter the draft store")
    timestamp = created_at or datetime.now(UTC)
    public = StoredActivityPublicVersion.from_record(
        record, version_id=version_id, created_at=timestamp, created_by=actor_id
    )
    private = StoredActivityPrivateVersion(
        version_id=version_id,
        activity_ref=record.activity_ref,
        private_payload=record.private,
        activity_type=record.activity_type,
        private_content_sha256=_private_content_hash(record),
        answer_source_sha256=record.integrity.answer_source_sha256,
        private_payload_sha256=record.integrity.private_payload_sha256,
        created_at=timestamp,
        created_by=actor_id,
    )
    event = ActivityVersionCreatedEvent(
        version_id=version_id,
        activity_ref=record.activity_ref,
        activity_type=record.activity_type,
        publication_state=publication_state,
        created_at=timestamp,
        created_by=actor_id,
    )
    return public, private, event


class TypedActivityDraftStore:
    """Mongo repository for immutable editorial versions, not live quiz serving.

    This class is not wired into FastAPI routes or the existing `quiz_versions`
    runtime catalog. The caller must explicitly construct it with a database.
    """

    def __init__(self, database: Any, authorizer: Authorizer | None = None) -> None:
        self._database = database
        self._public = database[PUBLIC_COLLECTION]
        self._private = database[PRIVATE_COLLECTION]
        self._events = database[EVENT_COLLECTION]
        self._heads = database[HEAD_COLLECTION]
        self._authorizer = authorizer or _authorize_platform_role

    def _require(self, user: dict[str, Any], permission: str) -> str:
        actor_id = user.get("id") if isinstance(user, dict) else None
        if not isinstance(actor_id, str) or not actor_id:
            raise ActivityPersistenceAuthorizationError("activity store permission denied")
        try:
            allowed = self._authorizer(user, permission)
        except (KeyError, TypeError):
            allowed = False
        if not allowed:
            raise ActivityPersistenceAuthorizationError("activity store permission denied")
        return actor_id

    async def _validate_current_head(
        self, activity_ref: str, head_document: dict[str, Any], session: Any
    ) -> None:
        try:
            head = StoredActivityHead.model_validate(
                {key: value for key, value in head_document.items() if key != "_id"}
            )
        except ValidationError as exc:
            raise ActivityVersionIntegrityError("activity head is malformed") from exc
        if head.activity_ref != activity_ref:
            raise ActivityVersionIntegrityError("activity head points to another activity")

        pair_query = {"activity_ref": activity_ref, "version_id": head.current_version_id}
        public_document = await self._public.find_one(
            pair_query, projection=_PUBLIC_PROJECTION, session=session
        )
        private_document = await self._private.find_one(
            pair_query, projection=_PRIVATE_PROJECTION, session=session
        )
        if public_document is None or private_document is None:
            raise ActivityVersionIntegrityError(
                "activity head points to an incomplete version pair"
            )
        current_record = _record_from_stored_pair(public_document, private_document)
        if private_document.get("private_content_sha256") != _private_content_hash(current_record):
            raise ActivityVersionIntegrityError("activity head version content hash does not match")
        event = await self._events.find_one(
            {
                "activity_ref": activity_ref,
                "version_id": head.current_version_id,
                "event_type": "version_created",
            },
            projection={"event_type": 1},
            session=session,
        )
        if event is None:
            raise ActivityVersionIntegrityError("activity head version has no creation event")

    async def ensure_indexes(self) -> None:
        """Create indexes only when explicitly invoked by an isolated caller."""
        await self._public.create_index(
            [("activity_ref", 1), ("version_id", 1)],
            unique=True,
            name="one_typed_activity_public_version",
        )
        await self._private.create_index(
            [("activity_ref", 1), ("version_id", 1)],
            unique=True,
            name="one_typed_activity_private_version",
        )
        await self._private.create_index(
            [("activity_ref", 1), ("private_content_sha256", 1)],
            unique=True,
            name="one_typed_activity_content_revision",
        )
        await self._events.create_index(
            [("activity_ref", 1), ("version_id", 1), ("event_type", 1)],
            unique=True,
            name="one_typed_activity_creation_event",
        )
        await self._public.create_index(
            [("activity_ref", 1), ("created_at", -1)],
            name="typed_activity_public_version_history",
        )
        await self._heads.create_index(
            [("activity_ref", 1)], unique=True, name="one_typed_activity_current_head"
        )

    async def save_version(
        self,
        record: TypedActivityRecord,
        user: dict[str, Any],
        *,
        expected_version_id: str | None = None,
    ) -> ActivityVersionWriteResult:
        """Insert an immutable version, atomically pairing public/private rows.

        Replaying identical content returns `unchanged`; changed content creates
        a new ObjectId version. Editorial state transitions are not implemented.
        """
        actor_id = self._require(user, "content.write")
        if expected_version_id is not None and (
            not isinstance(expected_version_id, str)
            or not re.fullmatch(r"[0-9a-f]{24}", expected_version_id)
        ):
            raise ValueError("expected version ID must be a 24-character ObjectId")
        if not _is_storable_state(record.publication_state):
            raise ActivityPersistenceError("published activities cannot enter the draft store")
        await self.ensure_indexes()
        content_hash = _private_content_hash(record)
        existing = await self._private.find_one(
            {"activity_ref": record.activity_ref, "private_content_sha256": content_hash},
            projection={
                "version_id": 1,
                "activity_ref": 1,
                "private_content_sha256": 1,
                "activity_type": 1,
                "private_payload": 1,
                "private_payload_sha256": 1,
                "answer_source_sha256": 1,
                "created_at": 1,
                "created_by": 1,
            },
        )
        if existing is not None:
            return await self._resolve_existing(record, existing, content_hash)

        version_object_id = ObjectId()
        version_id = str(version_object_id)
        created_at = datetime.now(UTC)
        public_model, private_model, event_model = build_activity_version_documents(
            record, version_id=version_id, actor_id=actor_id, created_at=created_at
        )
        public_doc = _mongo_doc(public_model)
        private_doc = _mongo_doc(private_model)
        event_doc = _mongo_doc(event_model)
        public_doc["_id"] = version_object_id
        private_doc["_id"] = version_object_id

        async def insert_all(session: Any) -> None:
            head = await self._heads.find_one(
                {"activity_ref": record.activity_ref},
                projection={
                    "storage_schema_version": 1,
                    "activity_ref": 1,
                    "current_version_id": 1,
                    "revision": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                },
                session=session,
            )
            current_version_id = head.get("current_version_id") if head else None
            if current_version_id != expected_version_id:
                raise ActivityVersionConflictError(
                    "activity head changed; reload before creating a revision"
                )
            if head is None:
                historical_public = await self._public.find_one(
                    {"activity_ref": record.activity_ref},
                    projection={"version_id": 1},
                    session=session,
                )
                historical_private = await self._private.find_one(
                    {"activity_ref": record.activity_ref},
                    projection={"version_id": 1},
                    session=session,
                )
                historical_event = await self._events.find_one(
                    {"activity_ref": record.activity_ref},
                    projection={"version_id": 1},
                    session=session,
                )
                if any(
                    item is not None
                    for item in (historical_public, historical_private, historical_event)
                ):
                    raise ActivityVersionIntegrityError(
                        "activity history exists without its current head"
                    )
            else:
                await self._validate_current_head(record.activity_ref, head, session)
            await self._public.insert_one(public_doc, session=session)
            await self._private.insert_one(private_doc, session=session)
            await self._events.insert_one(event_doc, session=session)
            if head is None:
                head_model = StoredActivityHead(
                    activity_ref=record.activity_ref,
                    current_version_id=version_id,
                    revision=1,
                    updated_at=created_at,
                    updated_by=actor_id,
                )
                head_doc = _mongo_doc(head_model)
                head_doc["_id"] = record.activity_ref
                await self._heads.insert_one(head_doc, session=session)
            else:
                result = await self._heads.update_one(
                    {
                        "activity_ref": record.activity_ref,
                        "current_version_id": expected_version_id,
                    },
                    {
                        "$set": {
                            "current_version_id": version_id,
                            "updated_at": created_at,
                            "updated_by": actor_id,
                        },
                        "$inc": {"revision": 1},
                    },
                    session=session,
                )
                if result.matched_count != 1:
                    raise ActivityVersionConflictError(
                        "activity head changed; reload before creating a revision"
                    )

        try:
            async with self._database.client.start_session() as session:
                await session.with_transaction(insert_all)
        except DuplicateKeyError:
            # A concurrent identical writer may win the unique content index.
            existing = await self._private.find_one(
                {"activity_ref": record.activity_ref, "private_content_sha256": content_hash},
                projection={
                    "version_id": 1,
                    "activity_ref": 1,
                    "activity_type": 1,
                    "private_payload": 1,
                    "private_content_sha256": 1,
                    "private_payload_sha256": 1,
                    "answer_source_sha256": 1,
                    "created_at": 1,
                    "created_by": 1,
                },
            )
            if existing is not None:
                return await self._resolve_existing(record, existing, content_hash)
            raise ActivityVersionConflictError(
                "activity version identity conflicts with stored data"
            )
        except ActivityVersionConflictError:
            # A concurrent identical create can commit after the preflight read
            # but before this transaction observes the current head. Reconcile
            # only when the exact immutable content hash is already persisted.
            existing = await self._private.find_one(
                {"activity_ref": record.activity_ref, "private_content_sha256": content_hash},
                projection={
                    "version_id": 1,
                    "activity_ref": 1,
                    "activity_type": 1,
                    "private_payload": 1,
                    "private_content_sha256": 1,
                    "private_payload_sha256": 1,
                    "answer_source_sha256": 1,
                    "created_at": 1,
                    "created_by": 1,
                },
            )
            if existing is not None:
                return await self._resolve_existing(record, existing, content_hash)
            raise
        except (InvalidOperation, PyMongoError) as exc:
            if isinstance(exc, PyMongoError) and exc.has_error_label(
                "UnknownTransactionCommitResult"
            ):
                raise ActivityTransactionOutcomeUnknownError(
                    "transaction outcome is unknown; replay the identical activity content to reconcile"
                ) from exc
            if _is_transaction_unsupported(exc):
                raise ActivityTransactionsRequiredError(
                    "activity version storage requires MongoDB transaction support"
                ) from exc
            if isinstance(exc, (AutoReconnect, NetworkTimeout, ServerSelectionTimeoutError)):
                raise ActivityTransactionOutcomeUnknownError(
                    "database response was interrupted; replay the identical activity content to reconcile"
                ) from exc
            raise ActivityTransactionFailedError(
                "activity transaction failed; replay identical content to reconcile safely"
            ) from exc

        return ActivityVersionWriteResult(
            outcome="created",
            version_id=version_id,
            activity_ref=record.activity_ref,
        )

    async def _resolve_existing(
        self, record: TypedActivityRecord, private_doc: dict[str, Any], content_hash: str
    ) -> ActivityVersionWriteResult:
        version_id = private_doc.get("version_id")
        public_doc = await self._public.find_one(
            {"activity_ref": record.activity_ref, "version_id": version_id},
            projection=_PUBLIC_PROJECTION,
        )
        if public_doc is None:
            raise ActivityVersionIntegrityError("private activity version has no public companion")
        stored_record = _record_from_stored_pair(public_doc, private_doc)
        if (
            stored_record.publication_state != record.publication_state
            or stored_record.activity_ref != record.activity_ref
            or stored_record.activity_type != record.activity_type
            or stored_record.version_ref != record.version_ref
            or _private_content_hash(stored_record) != content_hash
            or private_doc.get("private_content_sha256") != content_hash
        ):
            raise ActivityVersionConflictError(
                "stored activity version differs; immutable versions cannot be overwritten"
            )
        return ActivityVersionWriteResult(
            outcome="unchanged",
            version_id=str(version_id),
            activity_ref=record.activity_ref,
        )

    async def get_public_version(
        self, activity_ref: str, version_id: str, user: dict[str, Any]
    ) -> StoredActivityPublicVersion | None:
        self._require(user, "content.read")
        raw = await self._public.find_one(
            {"activity_ref": activity_ref, "version_id": version_id},
            projection=_PUBLIC_PROJECTION,
        )
        if raw is None:
            return None
        raw.pop("_id", None)
        return StoredActivityPublicVersion.model_validate(raw)

    async def get_private_version(
        self, activity_ref: str, version_id: str, user: dict[str, Any]
    ) -> StoredActivityPrivateVersion | None:
        self._require(user, "submissions.grade")
        raw = await self._private.find_one(
            {"activity_ref": activity_ref, "version_id": version_id},
            projection=_PRIVATE_PROJECTION,
        )
        if raw is None:
            return None
        companion = await self._public.find_one(
            {"activity_ref": activity_ref, "version_id": version_id},
            projection={"version_id": 1, "activity_ref": 1, "activity_type": 1},
        )
        if companion is None:
            raise ActivityVersionIntegrityError("private activity version has no public companion")
        if companion.get("activity_type") != raw.get("activity_type"):
            raise ActivityVersionIntegrityError("public/private activity types do not match")
        raw.pop("_id", None)
        return StoredActivityPrivateVersion.model_validate(raw)

    async def list_versions(
        self, activity_ref: str, user: dict[str, Any], limit: int = 100
    ) -> list[ActivityVersionSummary]:
        self._require(user, "content.read")
        if type(limit) is not int or not 1 <= limit <= 500:
            raise ValueError("activity version history limit must be from 1 to 500")
        projection = {
            "version_id": 1,
            "activity_ref": 1,
            "source_version_ref": 1,
            "activity_type": 1,
            "validation_state": 1,
            "publication_state": 1,
            "created_at": 1,
        }
        cursor = self._public.find({"activity_ref": activity_ref}, projection=projection)
        documents = (
            await cursor.sort([("created_at", -1), ("version_id", 1)]).limit(limit).to_list(limit)
        )
        for document in documents:
            document.pop("_id", None)
        return [ActivityVersionSummary.model_validate(document) for document in documents]
