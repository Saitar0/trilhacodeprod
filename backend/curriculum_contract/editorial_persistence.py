"""Isolated editorial persistence for canonical blocks, placements, and projects.

This module is deliberately not wired to application routes, student reads,
publication, import, quizzes, submissions, or progress. Every payload is stored
in a restricted collection; database-free contract models are reused from
``models.py``. Writes require explicit authorization and MongoDB transactions.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from collections import OrderedDict
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, TypeAlias

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
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from .models import (
    AcceptanceCriteriaBlock,
    ChecklistBlock,
    ContentBlock,
    ContractModel,
    ProjectSpec,
    RubricBlock,
    SharedPlacement,
    SourceProvenance,
    StableId,
)

EDITORIAL_SCHEMA_VERSION: Literal["trilhacode.editorial_store/1.0"] = (
    "trilhacode.editorial_store/1.0"
)

HEADS_COLLECTION = "curriculum_editorial_heads"
REVISIONS_COLLECTION = "curriculum_editorial_revisions"
PAYLOADS_COLLECTION = "curriculum_editorial_private_payloads"
EVENTS_COLLECTION = "curriculum_editorial_events"
OPERATIONS_COLLECTION = "curriculum_editorial_operations"

EntityKind = Literal["block", "placement", "project"]
EditorialCapability = Literal[
    "curriculum.editorial.read",
    "curriculum.editorial.content.read",
    "curriculum.editorial.private.read",
    "curriculum.editorial.revision.create",
    "curriculum.editorial.history.read",
    "curriculum.editorial.admin",
]
NodeKind = Literal["phase", "module", "submodule", "topic"]
HexSha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
RevisionId = HexSha256
IdempotencyKey = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=200, pattern=r"^[^\x00-\x1f]+$"),
]

_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_IDEMPOTENCY_KEY = re.compile(r"^[^\x00-\x1f]{1,200}$")
_REVISION_NAMESPACE = b"trilhacode.editorial.revision.v1\0"
_OPERATION_NAMESPACE = b"trilhacode.editorial.operation.v1\0"
_PRIVATE_BLOCK_TYPES = frozenset(
    {
        "quiz",
        "answer_key",
        "practice",
        "solution",
        "feedback",
        "instructor_note",
        "flashcard",
        "checklist",
        "acceptance_criteria",
        "completion_criteria",
        "project_decision",
        "project_scenario",
        "project_review",
        "rubric",
    }
)


class EditorialPersistenceError(RuntimeError):
    """Base error with messages that never include editorial payloads."""


class EditorialAuthorizationError(EditorialPersistenceError):
    """The isolated editorial authorization check denied the operation."""


class EditorialValidationError(EditorialPersistenceError):
    """A source-backed editorial command failed strict validation."""


class EditorialReferenceError(EditorialPersistenceError):
    """A curricular identity or typed reference is absent or inconsistent."""


class EditorialVersionConflictError(EditorialPersistenceError):
    """Compare-and-swap rejected a stale or competing editorial revision."""


class EditorialIntegrityError(EditorialPersistenceError):
    """Stored head, revision, payload, or event records are inconsistent."""


class EditorialIdempotencyConflictError(EditorialPersistenceError):
    """An idempotency key was already bound to a different command."""


class EditorialTransactionsRequiredError(EditorialPersistenceError):
    """MongoDB does not support the transaction required by this repository."""


class EditorialTransactionOutcomeUnknownError(EditorialPersistenceError):
    """The commit result is uncertain; inspect the operation before retrying."""


class EditorialTransactionFailedError(EditorialPersistenceError):
    """A known-aborted transaction failed; replay only the same command key."""


class EditorialOperationStateError(EditorialPersistenceError):
    """An operation is reserved but cannot safely be replayed automatically."""


class EditorialPrincipal(ContractModel):
    """Authenticated identity passed by a future integration boundary."""

    actor_ref: str = Field(min_length=1, max_length=200, repr=False)


Authorizer: TypeAlias = Callable[[EditorialPrincipal, EditorialCapability], bool]
NodeKindResolver: TypeAlias = Callable[[str], NodeKind | None]


class EditorialIdentity(ContractModel):
    """Immutable curricular identity stored separately from Mongo ObjectIds."""

    entity_kind: EntityKind
    entity_ref: StableId
    block_type: str | None = None
    owner_ref: StableId | None = None
    block_ref: StableId | None = None
    subject_ref: StableId | None = None
    unit_ref: StableId | None = None

    @model_validator(mode="after")
    def validate_identity_shape(self) -> EditorialIdentity:
        if self.entity_kind == "block":
            valid = (
                self.block_type is not None
                and self.block_ref is None
                and self.subject_ref is None
                and self.unit_ref is None
            )
        elif self.entity_kind == "placement":
            valid = (
                self.block_ref is not None
                and self.subject_ref is not None
                and self.block_type is None
                and self.owner_ref is None
                and self.unit_ref is None
            )
        else:
            valid = (
                self.unit_ref is not None
                and self.block_type is None
                and self.owner_ref is None
                and self.block_ref is None
                and self.subject_ref is None
            )
        if not valid:
            raise ValueError("editorial identity fields do not match entity kind")
        return self


class EditorialHead(ContractModel):
    storage_schema_version: Literal["trilhacode.editorial_store/1.0"] = EDITORIAL_SCHEMA_VERSION
    entity_kind: EntityKind
    entity_ref: StableId
    identity: EditorialIdentity
    identity_sha256: HexSha256
    current_revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    updated_at: datetime
    updated_by: str = Field(min_length=1, max_length=200, repr=False)

    @model_validator(mode="after")
    def head_identity_matches(self) -> EditorialHead:
        if (
            self.identity.entity_kind != self.entity_kind
            or self.identity.entity_ref != self.entity_ref
        ):
            raise ValueError("head identity does not match its entity")
        if hash_identity(self.identity) != self.identity_sha256:
            raise ValueError("head identity integrity hash does not match")
        return self


class EditorialRevisionMetadata(ContractModel):
    storage_schema_version: Literal["trilhacode.editorial_store/1.0"] = EDITORIAL_SCHEMA_VERSION
    entity_kind: EntityKind
    entity_ref: StableId
    identity: EditorialIdentity
    identity_sha256: HexSha256
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    created_at: datetime
    created_by: str = Field(min_length=1, max_length=200, repr=False)

    @model_validator(mode="after")
    def revision_identity_matches(self) -> EditorialRevisionMetadata:
        if (
            self.identity.entity_kind != self.entity_kind
            or self.identity.entity_ref != self.entity_ref
        ):
            raise ValueError("revision identity does not match its entity")
        if hash_identity(self.identity) != self.identity_sha256:
            raise ValueError("revision identity integrity hash does not match")
        return self


class PinnedBlockReference(ContractModel):
    block_ref: StableId
    resolution: Literal["pinned", "unresolved"]
    revision_id: RevisionId | None = None
    revision_no: int | None = Field(default=None, strict=True, ge=1)
    content_sha256: HexSha256 | None = None
    block_type: str | None = None
    roles: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_pin(self) -> PinnedBlockReference:
        populated = all(
            value is not None
            for value in (self.revision_id, self.revision_no, self.content_sha256, self.block_type)
        )
        if (self.resolution == "pinned") != populated:
            raise ValueError("pinned reference must have a complete immutable revision identity")
        if len(self.roles) != len(set(self.roles)):
            raise ValueError("pinned reference roles must be unique")
        return self


class StoredBlockPayload(ContractModel):
    entity_kind: Literal["block"]
    entity_ref: StableId
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    block: ContentBlock = Field(repr=False)

    @model_validator(mode="after")
    def block_matches_identity(self) -> StoredBlockPayload:
        if self.block.ref != self.entity_ref or not self.block.shared:
            raise ValueError("stored block must match its canonical shared identity")
        return self


class StoredPlacementPayload(ContractModel):
    entity_kind: Literal["placement"]
    entity_ref: StableId
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    placement: SharedPlacement = Field(repr=False)

    @model_validator(mode="after")
    def placement_matches_identity(self) -> StoredPlacementPayload:
        if self.placement.ref != self.entity_ref:
            raise ValueError("stored placement does not match its curricular identity")
        return self


class StoredProjectPayload(ContractModel):
    entity_kind: Literal["project"]
    entity_ref: StableId
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    project: ProjectSpec = Field(repr=False)
    pinned_blocks: list[PinnedBlockReference]

    @model_validator(mode="after")
    def project_matches_identity(self) -> StoredProjectPayload:
        if self.project.ref != self.entity_ref:
            raise ValueError("stored project does not match its curricular identity")
        if len({item.block_ref for item in self.pinned_blocks}) != len(self.pinned_blocks):
            raise ValueError("project block references must be coalesced by canonical block")
        return self


EditorialPayload: TypeAlias = StoredBlockPayload | StoredPlacementPayload | StoredProjectPayload


class EditorialEvent(ContractModel):
    storage_schema_version: Literal["trilhacode.editorial_store/1.0"] = EDITORIAL_SCHEMA_VERSION
    event_type: Literal["revision_created"] = "revision_created"
    operation_ref: HexSha256
    entity_kind: EntityKind
    entity_ref: StableId
    base_revision_id: RevisionId | None
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    created_at: datetime
    actor_ref: str = Field(min_length=1, max_length=200, repr=False)


class EditorialOperation(ContractModel):
    storage_schema_version: Literal["trilhacode.editorial_store/1.0"] = EDITORIAL_SCHEMA_VERSION
    operation_ref: HexSha256
    actor_ref: str = Field(min_length=1, max_length=200, repr=False)
    entity_kind: EntityKind
    entity_ref: StableId
    command_sha256: HexSha256
    state: Literal["pending", "retryable", "confirmed"]
    created_at: datetime
    updated_at: datetime
    result_revision_id: RevisionId | None = None
    result_revision_no: int | None = Field(default=None, strict=True, ge=1)
    result_content_sha256: HexSha256 | None = None

    @model_validator(mode="after")
    def result_matches_state(self) -> EditorialOperation:
        complete = all(
            item is not None
            for item in (
                self.result_revision_id,
                self.result_revision_no,
                self.result_content_sha256,
            )
        )
        if (self.state == "confirmed") != complete:
            raise ValueError("confirmed operation requires a complete result")
        return self


class EditorialWriteResult(ContractModel):
    outcome: Literal["created", "unchanged"]
    entity_kind: EntityKind
    entity_ref: StableId
    revision_id: RevisionId
    revision_no: int = Field(strict=True, ge=1)
    content_sha256: HexSha256
    operation_ref: HexSha256


class EditorialOperationStatus(ContractModel):
    state: Literal["confirmed", "not_committed", "unknown", "not_found"]
    operation_ref: HexSha256
    entity_kind: EntityKind | None = None
    entity_ref: StableId | None = None
    revision_id: RevisionId | None = None
    revision_no: int | None = None
    # not_found is intentionally not evidence that an interrupted write failed.
    outcome_conclusive: bool


class EditorialRevisionRead(ContractModel):
    metadata: EditorialRevisionMetadata
    payload: EditorialPayload = Field(repr=False)


class EditorialHistory(ContractModel):
    items: list[EditorialRevisionMetadata]


def canonical_editorial_bytes(value: Any) -> bytes:
    """Canonical JSON for already-validated Pydantic data; arrays retain source order."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_editorial_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_editorial_bytes(value)).hexdigest()


def hash_identity(identity: EditorialIdentity) -> str:
    return canonical_editorial_sha256(identity)


def _content_hash(kind: EntityKind, ref: str, payload: Any) -> str:
    return canonical_editorial_sha256(
        {
            "storage_schema_version": EDITORIAL_SCHEMA_VERSION,
            "entity_kind": kind,
            "entity_ref": ref,
            "payload": payload,
        }
    )


def _operation_hash(actor_ref: str, idempotency_key: str) -> str:
    return hashlib.sha256(
        _OPERATION_NAMESPACE + actor_ref.encode("utf-8") + b"\0" + idempotency_key.encode("utf-8")
    ).hexdigest()


def _validated_idempotency_key(value: str) -> str:
    if not isinstance(value, str) or not _IDEMPOTENCY_KEY.fullmatch(value):
        raise EditorialValidationError("idempotency key is invalid")
    return value


def _revision_id(operation_ref: str) -> str:
    return hashlib.sha256(_REVISION_NAMESPACE + operation_ref.encode("ascii")).hexdigest()


def _mongo_doc(model: ContractModel) -> dict[str, Any]:
    # Keep optional source fields absent when they were absent in the input model.
    return model.model_dump(mode="python", exclude_unset=True)


def _without_mongo_id(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "_id"}


def _validate_provenance(provenance: SourceProvenance) -> None:
    if not _HEX_SHA256.fullmatch(provenance.source_sha256):
        raise EditorialValidationError("source provenance hash must be lowercase SHA-256")


def _validate_block_provenance(block: ContentBlock) -> None:
    _validate_provenance(block.provenance)


def _validate_placement_provenance(placement: SharedPlacement) -> None:
    _validate_provenance(placement.provenance)


def _validate_project_provenance(project: ProjectSpec) -> None:
    _validate_provenance(project.provenance)
    for delivery in project.deliveries:
        _validate_provenance(delivery.provenance)
    for milestone in project.milestones:
        _validate_provenance(milestone.provenance)
    for variant in project.variants:
        _validate_provenance(variant.provenance)


def _require_expected_head_pair(revision_id: str | None, revision_no: int | None) -> None:
    if (revision_id is None) != (revision_no is None):
        raise EditorialValidationError("expected revision ID and number must be supplied together")
    if revision_id is not None and not _HEX_SHA256.fullmatch(revision_id):
        raise EditorialValidationError("expected revision ID is malformed")
    if revision_no is not None and (type(revision_no) is not int or revision_no < 1):
        raise EditorialValidationError("expected revision number is malformed")


def _is_transactions_unsupported(error: BaseException) -> bool:
    text = str(error).casefold()
    return (isinstance(error, OperationFailure) and error.code == 20) or any(
        marker in text
        for marker in (
            "transaction numbers are only allowed on a replica set member or mongos",
            "transactions are not supported",
            "transaction support is not available",
        )
    )


def _has_label(error: BaseException, label: str) -> bool:
    return isinstance(error, PyMongoError) and error.has_error_label(label)


def _project_block_references(project: ProjectSpec) -> list[tuple[str, str, type[Any] | None, str]]:
    """Return first-seen refs with each typed role and owning project element."""
    found: OrderedDict[str, list[tuple[str, type[Any] | None, str]]] = OrderedDict()

    def add(ref: str, role: str, expected: type[Any] | None, owner_ref: str) -> None:
        found.setdefault(ref, []).append((role, expected, owner_ref))

    for ref in project.checklist_refs:
        add(ref, "project_checklist", ChecklistBlock, project.ref)
    for ref in project.rubric_refs:
        add(ref, "project_rubric", RubricBlock, project.ref)
    for delivery in project.deliveries:
        for ref in delivery.acceptance_refs:
            add(ref, "delivery_acceptance", AcceptanceCriteriaBlock, delivery.ref)
        for ref in delivery.checklist_refs:
            add(ref, "step_checklist", ChecklistBlock, delivery.ref)
        for ref in delivery.rubric_refs:
            add(ref, "step_rubric", RubricBlock, delivery.ref)
        for ref in delivery.content_refs:
            add(ref, "step_content", None, delivery.ref)
    for milestone in project.milestones:
        for ref in milestone.acceptance_refs:
            add(ref, "milestone_acceptance", AcceptanceCriteriaBlock, milestone.ref)
        for ref in milestone.checklist_refs:
            add(ref, "step_checklist", ChecklistBlock, milestone.ref)
        for ref in milestone.rubric_refs:
            add(ref, "step_rubric", RubricBlock, milestone.ref)
        for ref in milestone.content_refs:
            add(ref, "step_content", None, milestone.ref)
    return [
        (ref, role, expected, owner)
        for ref, roles in found.items()
        for role, expected, owner in roles
    ]


def _project_roles_by_ref(
    project: ProjectSpec,
) -> list[tuple[str, tuple[tuple[str, type[Any] | None, str], ...]]]:
    grouped: OrderedDict[str, list[tuple[str, type[Any] | None, str]]] = OrderedDict()
    for ref, role, expected, owner in _project_block_references(project):
        grouped.setdefault(ref, []).append((role, expected, owner))
    return [(ref, tuple(roles)) for ref, roles in grouped.items()]


def _validate_project_identities(project: ProjectSpec) -> None:
    refs: list[str] = [project.ref]
    for values in (project.checklist_refs, project.rubric_refs):
        if len(values) != len(set(values)):
            raise EditorialValidationError("project contains duplicate block references")
    for delivery in project.deliveries:
        refs.append(delivery.ref)
        for values in (
            delivery.acceptance_refs,
            delivery.checklist_refs,
            delivery.rubric_refs,
            delivery.content_refs,
        ):
            if len(values) != len(set(values)):
                raise EditorialValidationError("project step contains duplicate block references")
    for milestone in project.milestones:
        refs.append(milestone.ref)
        for values in (
            milestone.acceptance_refs,
            milestone.checklist_refs,
            milestone.rubric_refs,
            milestone.content_refs,
        ):
            if len(values) != len(set(values)):
                raise EditorialValidationError("project step contains duplicate block references")
    refs.extend(item.ref for item in project.variants)
    if len(refs) != len(set(refs)):
        raise EditorialValidationError(
            "project, delivery, milestone, and variant identities must be unique"
        )


def _validate_project_target(block: ContentBlock, role: str, owner_ref: str) -> None:
    if role in {"project_checklist", "step_checklist", "step_content"}:
        if block.owner_ref != owner_ref:
            raise EditorialReferenceError("project block owner does not match its source reference")
    elif role == "project_rubric":
        if not isinstance(block, RubricBlock):
            raise EditorialReferenceError("project rubric reference has an incompatible block type")
        if owner_ref not in (block.target_refs or [block.target_ref]):
            raise EditorialReferenceError(
                "project rubric target does not match its source reference"
            )
    elif role in {"delivery_acceptance", "milestone_acceptance"}:
        if not isinstance(block, AcceptanceCriteriaBlock):
            raise EditorialReferenceError(
                "project acceptance reference has an incompatible block type"
            )
        target_matches = (
            block.delivery_ref == owner_ref
            if role == "delivery_acceptance"
            else block.milestone_ref == owner_ref
        )
        if block.owner_ref != owner_ref or not target_matches:
            raise EditorialReferenceError(
                "project acceptance target does not match its source reference"
            )
    elif role == "step_rubric":
        if not isinstance(block, RubricBlock):
            raise EditorialReferenceError("project rubric reference has an incompatible block type")
        if owner_ref not in (block.target_refs or [block.target_ref]):
            raise EditorialReferenceError(
                "project rubric target does not match its source reference"
            )


class EditorialPersistenceStore:
    """Restricted repository; no routes, publishing, student state, or import hooks."""

    def __init__(
        self,
        database: Any,
        *,
        authorizer: Authorizer | None = None,
        node_kind_resolver: NodeKindResolver | None = None,
        operation_wait_seconds: float = 1.0,
    ) -> None:
        self._database = database
        self._heads = database.get_collection(HEADS_COLLECTION).with_options(
            read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority")
        )
        self._revisions = database.get_collection(REVISIONS_COLLECTION).with_options(
            read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority")
        )
        self._payloads = database.get_collection(PAYLOADS_COLLECTION).with_options(
            read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority")
        )
        self._events = database.get_collection(EVENTS_COLLECTION).with_options(
            read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority")
        )
        self._operations = database.get_collection(OPERATIONS_COLLECTION).with_options(
            read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority")
        )
        # Missing authorization is deliberately deny-all; no platform permission is reused.
        self._authorizer = authorizer
        self._node_kind_resolver = node_kind_resolver
        self._operation_wait_seconds = max(0.0, min(operation_wait_seconds, 3.0))
        self._indexes_ready = False

    def _require(self, principal: EditorialPrincipal, capability: EditorialCapability) -> None:
        if not isinstance(principal, EditorialPrincipal) or self._authorizer is None:
            raise EditorialAuthorizationError("editorial authorization denied")
        try:
            allowed = self._authorizer(principal, capability)
        except Exception:
            allowed = False
        if not allowed:
            raise EditorialAuthorizationError("editorial authorization denied")

    def _resolve_node_kind(self, ref: str) -> NodeKind:
        if self._node_kind_resolver is None:
            raise EditorialReferenceError("curricular node resolver is required for this write")
        try:
            kind = self._node_kind_resolver(ref)
        except Exception:
            kind = None
        if kind is None:
            raise EditorialReferenceError("curricular node reference could not be resolved")
        return kind

    async def ensure_indexes(self, principal: EditorialPrincipal) -> None:
        """Explicit administrative setup; never called implicitly by a write."""
        self._require(principal, "curriculum.editorial.admin")
        try:
            await self._heads.create_index(
                [("entity_kind", 1), ("entity_ref", 1)],
                unique=True,
                name="one_curriculum_editorial_head",
            )
            await self._heads.create_index(
                [("identity.block_ref", 1), ("identity.subject_ref", 1)],
                unique=True,
                partialFilterExpression={"entity_kind": "placement"},
                name="one_curriculum_editorial_block_subject_placement",
            )
            await self._revisions.create_index(
                [("entity_kind", 1), ("entity_ref", 1), ("revision_no", 1)],
                unique=True,
                name="one_curriculum_editorial_revision_number",
            )
            await self._revisions.create_index(
                [("revision_id", 1)], unique=True, name="one_curriculum_editorial_revision_id"
            )
            await self._revisions.create_index(
                [("entity_kind", 1), ("entity_ref", 1), ("created_at", -1)],
                name="curriculum_editorial_revision_history",
            )
            await self._payloads.create_index(
                [("revision_id", 1)], unique=True, name="one_curriculum_editorial_private_payload"
            )
            await self._events.create_index(
                [("operation_ref", 1)],
                unique=True,
                name="one_curriculum_editorial_event_per_operation",
            )
            await self._events.create_index(
                [("entity_kind", 1), ("entity_ref", 1), ("created_at", -1)],
                name="curriculum_editorial_event_history",
            )
            await self._operations.create_index(
                [("operation_ref", 1)], unique=True, name="one_curriculum_editorial_operation"
            )
            await self._operations.create_index(
                [("entity_kind", 1), ("entity_ref", 1), ("created_at", -1)],
                name="curriculum_editorial_operation_history",
            )
        except PyMongoError:
            raise EditorialIntegrityError(
                "editorial index verification or creation failed"
            ) from None
        self._indexes_ready = True

    async def save_block(
        self,
        block: ContentBlock,
        principal: EditorialPrincipal,
        *,
        expected_revision_id: str | None,
        expected_revision_no: int | None,
        idempotency_key: str,
    ) -> EditorialWriteResult:
        self._require(principal, "curriculum.editorial.revision.create")
        if not block.shared:
            raise EditorialValidationError("only canonical shared blocks are accepted")
        if block.status != "draft":
            raise EditorialValidationError(
                "editorial persistence accepts draft blocks only; publication is out of scope"
            )
        _validate_block_provenance(block)
        identity = EditorialIdentity(
            entity_kind="block",
            entity_ref=block.ref,
            block_type=block.type,
            owner_ref=block.owner_ref,
        )
        payload = block.model_dump(mode="json", exclude_unset=True)
        return await self._save(
            "block",
            block.ref,
            identity,
            block,
            payload,
            principal,
            expected_revision_id,
            expected_revision_no,
            idempotency_key,
        )

    async def save_placement(
        self,
        placement: SharedPlacement,
        principal: EditorialPrincipal,
        *,
        expected_revision_id: str | None,
        expected_revision_no: int | None,
        idempotency_key: str,
    ) -> EditorialWriteResult:
        self._require(principal, "curriculum.editorial.revision.create")
        _validate_placement_provenance(placement)
        if placement.progress_scope != "undecided":
            raise EditorialValidationError("progress scope must remain undecided in this stage")
        if self._resolve_node_kind(placement.subject_ref) != "topic":
            raise EditorialReferenceError("placement subject must resolve to a topic node")
        identity = EditorialIdentity(
            entity_kind="placement",
            entity_ref=placement.ref,
            block_ref=placement.block_ref,
            subject_ref=placement.subject_ref,
        )
        payload = placement.model_dump(mode="json", exclude_unset=True)
        return await self._save(
            "placement",
            placement.ref,
            identity,
            placement,
            payload,
            principal,
            expected_revision_id,
            expected_revision_no,
            idempotency_key,
        )

    async def save_project(
        self,
        project: ProjectSpec,
        principal: EditorialPrincipal,
        *,
        expected_revision_id: str | None,
        expected_revision_no: int | None,
        idempotency_key: str,
    ) -> EditorialWriteResult:
        self._require(principal, "curriculum.editorial.revision.create")
        _validate_project_provenance(project)
        if self._resolve_node_kind(project.unit_ref) != "submodule":
            raise EditorialReferenceError("project owner must resolve to a submodule node")
        if project.stack_selected is not None or project.variants:
            raise EditorialValidationError(
                "stack selection and project variants remain out of scope"
            )
        _validate_project_identities(project)
        identity = EditorialIdentity(
            entity_kind="project", entity_ref=project.ref, unit_ref=project.unit_ref
        )
        command_payload = project.model_dump(mode="json", exclude_unset=True)
        return await self._save(
            "project",
            project.ref,
            identity,
            project,
            command_payload,
            principal,
            expected_revision_id,
            expected_revision_no,
            idempotency_key,
        )

    async def _save(
        self,
        kind: EntityKind,
        ref: str,
        identity: EditorialIdentity,
        source_payload: ContentBlock | SharedPlacement | ProjectSpec,
        command_payload: dict[str, Any],
        principal: EditorialPrincipal,
        expected_revision_id: str | None,
        expected_revision_no: int | None,
        idempotency_key: str,
    ) -> EditorialWriteResult:
        if not self._indexes_ready:
            raise EditorialOperationStateError(
                "editorial indexes must be explicitly verified first"
            )
        _require_expected_head_pair(expected_revision_id, expected_revision_no)
        normalized_key = _validated_idempotency_key(idempotency_key)
        identity_hash = hash_identity(identity)
        command_hash = _content_hash(
            kind,
            ref,
            {
                "expected_revision_id": expected_revision_id,
                "expected_revision_no": expected_revision_no,
                "identity": identity.model_dump(mode="json"),
                "source_payload": command_payload,
            },
        )
        operation_ref = _operation_hash(principal.actor_ref, normalized_key)
        operation = await self._operations.find_one({"operation_ref": operation_ref})
        if operation is not None:
            if operation.get("command_sha256") != command_hash:
                raise EditorialIdempotencyConflictError(
                    "idempotency key conflicts with another command"
                )
            if operation.get("state") != "retryable":
                return await self._replay_or_reject(
                    operation, command_hash, operation_ref, kind, ref
                )
        else:
            now = datetime.now(UTC)
            reservation = EditorialOperation(
                storage_schema_version=EDITORIAL_SCHEMA_VERSION,
                operation_ref=operation_ref,
                actor_ref=principal.actor_ref,
                entity_kind=kind,
                entity_ref=ref,
                command_sha256=command_hash,
                state="pending",
                created_at=now,
                updated_at=now,
            )
            try:
                await self._operations.insert_one(_mongo_doc(reservation))
            except DuplicateKeyError:
                operation = await self._wait_for_operation(operation_ref)
                if operation is None:
                    raise EditorialTransactionOutcomeUnknownError(
                        "operation reservation could not be reconciled"
                    ) from None
                if operation.get("command_sha256") != command_hash:
                    raise EditorialIdempotencyConflictError(
                        "idempotency key conflicts with another command"
                    ) from None
                if operation.get("state") != "retryable":
                    return await self._replay_or_reject(
                        operation, command_hash, operation_ref, kind, ref
                    )
            except PyMongoError:
                operation = await self._safe_find_operation(operation_ref)
                if operation is not None and operation.get("command_sha256") != command_hash:
                    raise EditorialIdempotencyConflictError(
                        "idempotency key conflicts with another command"
                    ) from None
                raise EditorialTransactionOutcomeUnknownError(
                    "operation reservation result is unknown; inspect the same operation key"
                ) from None

        try:
            async with self._database.client.start_session() as session:
                result = await session.with_transaction(
                    lambda active_session: self._commit_revision(
                        active_session,
                        kind,
                        ref,
                        identity,
                        identity_hash,
                        source_payload,
                        command_payload,
                        principal,
                        expected_revision_id,
                        expected_revision_no,
                        command_hash,
                        operation_ref,
                    ),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                    read_preference=ReadPreference.PRIMARY,
                )
            return EditorialWriteResult.model_validate(result)
        except (
            EditorialValidationError,
            EditorialReferenceError,
            EditorialVersionConflictError,
        ) as exc:
            await self._mark_retryable(operation_ref)
            raise exc
        except DuplicateKeyError:
            await self._mark_retryable(operation_ref)
            raise EditorialVersionConflictError(
                "a competing editorial identity or revision already exists"
            ) from None
        except (InvalidOperation, PyMongoError) as exc:
            if _has_label(exc, "UnknownTransactionCommitResult") or isinstance(
                exc, (AutoReconnect, NetworkTimeout, ServerSelectionTimeoutError)
            ):
                operation = await self._safe_find_operation(operation_ref)
                if operation is not None and operation.get("state") == "confirmed":
                    return await self._result_from_operation(operation, "unchanged")
                raise EditorialTransactionOutcomeUnknownError(
                    "transaction outcome is unknown; inspect this operation without replaying under a new key"
                ) from None
            if _is_transactions_unsupported(exc):
                await self._mark_retryable(operation_ref)
                raise EditorialTransactionsRequiredError(
                    "editorial writes require MongoDB transaction support"
                ) from None
            await self._mark_retryable(operation_ref)
            raise EditorialTransactionFailedError(
                "editorial transaction failed; replay only after operation status is retryable"
            ) from None
        except EditorialPersistenceError:
            await self._mark_retryable(operation_ref)
            raise
        except Exception:
            await self._mark_retryable(operation_ref)
            raise EditorialTransactionFailedError(
                "editorial transaction aborted; retry only with the same operation key"
            ) from None

    async def _commit_revision(
        self,
        session: Any,
        kind: EntityKind,
        ref: str,
        identity: EditorialIdentity,
        identity_hash: str,
        source_payload: ContentBlock | SharedPlacement | ProjectSpec,
        command_payload: dict[str, Any],
        principal: EditorialPrincipal,
        expected_revision_id: str | None,
        expected_revision_no: int | None,
        command_hash: str,
        operation_ref: str,
    ) -> dict[str, Any]:
        operation = await self._operations.find_one(
            {"operation_ref": operation_ref}, session=session
        )
        if operation is None or operation.get("state") not in {"pending", "retryable"}:
            raise EditorialOperationStateError("operation reservation is unavailable")
        if operation.get("command_sha256") != command_hash:
            raise EditorialIdempotencyConflictError(
                "idempotency key conflicts with another command"
            )

        payload_content: dict[str, Any]
        if kind == "project":
            assert isinstance(source_payload, ProjectSpec)
            pinned_blocks = await self._pin_project_blocks(source_payload, session)
            payload_content = {
                "project": command_payload,
                "pinned_blocks": [
                    item.model_dump(mode="json", exclude_unset=True) for item in pinned_blocks
                ],
            }
        elif kind == "block":
            payload_content = {"block": command_payload}
        else:
            assert isinstance(source_payload, SharedPlacement)
            block_head_raw = await self._heads.find_one(
                {"entity_kind": "block", "entity_ref": source_payload.block_ref},
                session=session,
            )
            if block_head_raw is None:
                raise EditorialReferenceError(
                    "placement canonical block is not in the editorial store"
                )
            block_head = self._validate_head(block_head_raw, None)
            block_meta = await self._validate_current_revision(block_head, session)
            block_payload_raw = await self._payloads.find_one(
                {
                    "entity_kind": "block",
                    "entity_ref": source_payload.block_ref,
                    "revision_id": block_head.current_revision_id,
                },
                session=session,
            )
            if block_payload_raw is None:
                raise EditorialIntegrityError("placement canonical block payload is missing")
            stored_block = self._validate_payload(block_meta, block_payload_raw)
            if not isinstance(stored_block, StoredBlockPayload) or not stored_block.block.shared:
                raise EditorialReferenceError("placement target is not a shared canonical block")
            payload_content = {"placement": command_payload}
        content_hash = _content_hash(kind, ref, payload_content)

        head_raw = await self._heads.find_one(
            {"entity_kind": kind, "entity_ref": ref}, session=session
        )
        head: EditorialHead | None = None
        if head_raw is not None:
            head = self._validate_head(head_raw, identity)
            await self._validate_current_revision(head, session)
            if (
                expected_revision_id != head.current_revision_id
                or expected_revision_no != head.revision_no
            ):
                raise EditorialVersionConflictError(
                    "editorial head changed; reload before revising"
                )
            if head.identity_sha256 != identity_hash:
                raise EditorialReferenceError("curricular identity references are immutable")
            current_meta = await self._revisions.find_one(
                {"revision_id": head.current_revision_id}, session=session
            )
            if current_meta is None:
                raise EditorialIntegrityError("editorial head revision is missing")
            if current_meta.get("content_sha256") == content_hash:
                return await self._confirm_no_change(
                    session, operation_ref, current_meta, principal.actor_ref, kind, ref
                )
        else:
            if expected_revision_id is not None:
                raise EditorialVersionConflictError(
                    "editorial head no longer matches expected revision"
                )
            revision_no = 1

        revision_no = head.revision_no + 1 if head else 1
        revision_id = _revision_id(operation_ref)
        now = datetime.now(UTC)
        metadata = EditorialRevisionMetadata(
            storage_schema_version=EDITORIAL_SCHEMA_VERSION,
            entity_kind=kind,
            entity_ref=ref,
            identity=identity,
            identity_sha256=identity_hash,
            revision_id=revision_id,
            revision_no=revision_no,
            content_sha256=content_hash,
            created_at=now,
            created_by=principal.actor_ref,
        )
        payload_doc = self._build_payload_document(
            kind, ref, revision_id, revision_no, content_hash, command_payload, payload_content
        )
        event = EditorialEvent(
            storage_schema_version=EDITORIAL_SCHEMA_VERSION,
            operation_ref=operation_ref,
            entity_kind=kind,
            entity_ref=ref,
            base_revision_id=head.current_revision_id if head else None,
            revision_id=revision_id,
            revision_no=revision_no,
            content_sha256=content_hash,
            created_at=now,
            actor_ref=principal.actor_ref,
        )
        await self._revisions.insert_one(_mongo_doc(metadata), session=session)
        await self._payloads.insert_one(_mongo_doc(payload_doc), session=session)
        await self._events.insert_one(_mongo_doc(event), session=session)
        if head is None:
            new_head = EditorialHead(
                storage_schema_version=EDITORIAL_SCHEMA_VERSION,
                entity_kind=kind,
                entity_ref=ref,
                identity=identity,
                identity_sha256=identity_hash,
                current_revision_id=revision_id,
                revision_no=revision_no,
                updated_at=now,
                updated_by=principal.actor_ref,
            )
            await self._heads.insert_one(_mongo_doc(new_head), session=session)
        else:
            updated = await self._heads.update_one(
                {
                    "entity_kind": kind,
                    "entity_ref": ref,
                    "current_revision_id": expected_revision_id,
                    "revision_no": expected_revision_no,
                    "identity_sha256": identity_hash,
                },
                {
                    "$set": {
                        "current_revision_id": revision_id,
                        "revision_no": revision_no,
                        "updated_at": now,
                        "updated_by": principal.actor_ref,
                    }
                },
                session=session,
            )
            if updated.matched_count != 1:
                raise EditorialVersionConflictError("editorial compare-and-swap lost a race")
        operation_update = await self._operations.update_one(
            {
                "operation_ref": operation_ref,
                "command_sha256": command_hash,
                "state": {"$in": ["pending", "retryable"]},
            },
            {
                "$set": {
                    "state": "confirmed",
                    "updated_at": now,
                    "result_revision_id": revision_id,
                    "result_revision_no": revision_no,
                    "result_content_sha256": content_hash,
                }
            },
            session=session,
        )
        if operation_update.matched_count != 1:
            raise EditorialOperationStateError("editorial operation could not be confirmed")
        return EditorialWriteResult(
            outcome="created",
            entity_kind=kind,
            entity_ref=ref,
            revision_id=revision_id,
            revision_no=revision_no,
            content_sha256=content_hash,
            operation_ref=operation_ref,
        ).model_dump(mode="json")

    def _build_payload_document(
        self,
        kind: EntityKind,
        ref: str,
        revision_id: str,
        revision_no: int,
        content_hash: str,
        command_payload: dict[str, Any],
        payload_content: dict[str, Any],
    ) -> ContractModel:
        common = {
            "entity_kind": kind,
            "entity_ref": ref,
            "revision_id": revision_id,
            "revision_no": revision_no,
            "content_sha256": content_hash,
        }
        try:
            if kind == "block":
                return StoredBlockPayload.model_validate({**common, "block": command_payload})
            if kind == "placement":
                return StoredPlacementPayload.model_validate(
                    {**common, "placement": command_payload}
                )
            return StoredProjectPayload.model_validate(
                {
                    **common,
                    "project": payload_content["project"],
                    "pinned_blocks": payload_content["pinned_blocks"],
                }
            )
        except ValidationError:
            raise EditorialValidationError(
                "editorial payload does not match its strict schema"
            ) from None

    async def _pin_project_blocks(
        self, project: ProjectSpec, session: Any
    ) -> list[PinnedBlockReference]:
        results: list[PinnedBlockReference] = []
        for ref, roles in _project_roles_by_ref(project):
            head_raw = await self._heads.find_one(
                {"entity_kind": "block", "entity_ref": ref}, session=session
            )
            role_names = [f"{role}:{owner}" for role, _expected, owner in roles]
            if head_raw is None:
                results.append(
                    PinnedBlockReference(block_ref=ref, resolution="unresolved", roles=role_names)
                )
                continue
            head = self._validate_head(head_raw, None, allow_identity_check=False)
            meta_raw = await self._validate_current_revision(head, session)
            payload_raw = await self._payloads.find_one(
                {
                    "entity_kind": "block",
                    "entity_ref": ref,
                    "revision_id": head.current_revision_id,
                },
                session=session,
            )
            if payload_raw is None:
                raise EditorialIntegrityError("referenced canonical block payload is missing")
            block = self._validate_payload(meta_raw, payload_raw)
            assert isinstance(block, StoredBlockPayload)
            for role, expected_type, owner_ref in roles:
                if expected_type is not None and not isinstance(block.block, expected_type):
                    raise EditorialReferenceError(
                        "project reference points to an incompatible block type"
                    )
                _validate_project_target(block.block, role, owner_ref)
            results.append(
                PinnedBlockReference(
                    block_ref=ref,
                    resolution="pinned",
                    revision_id=head.current_revision_id,
                    revision_no=head.revision_no,
                    content_sha256=meta_raw["content_sha256"],
                    block_type=block.block.type,
                    roles=role_names,
                )
            )
        return results

    async def _confirm_no_change(
        self,
        session: Any,
        operation_ref: str,
        current_meta: Mapping[str, Any],
        actor_ref: str,
        kind: EntityKind,
        ref: str,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        result = EditorialWriteResult(
            outcome="unchanged",
            entity_kind=kind,
            entity_ref=ref,
            revision_id=current_meta["revision_id"],
            revision_no=current_meta["revision_no"],
            content_sha256=current_meta["content_sha256"],
            operation_ref=operation_ref,
        )
        updated = await self._operations.update_one(
            {"operation_ref": operation_ref, "state": {"$in": ["pending", "retryable"]}},
            {
                "$set": {
                    "state": "confirmed",
                    "updated_at": now,
                    "result_revision_id": result.revision_id,
                    "result_revision_no": result.revision_no,
                    "result_content_sha256": result.content_sha256,
                }
            },
            session=session,
        )
        if updated.matched_count != 1:
            raise EditorialOperationStateError("editorial operation could not be confirmed")
        return result.model_dump(mode="json")

    def _validate_head(
        self,
        raw: Mapping[str, Any],
        identity: EditorialIdentity | None,
        *,
        allow_identity_check: bool = True,
    ) -> EditorialHead:
        try:
            head = EditorialHead.model_validate(_without_mongo_id(dict(raw)))
        except ValidationError:
            raise EditorialIntegrityError("stored editorial head is malformed") from None
        if (
            allow_identity_check
            and identity is not None
            and head.identity_sha256 != hash_identity(identity)
        ):
            raise EditorialReferenceError("curricular identity references are immutable")
        return head

    async def _validate_current_revision(self, head: EditorialHead, session: Any) -> dict[str, Any]:
        metadata = await self._revisions.find_one(
            {
                "entity_kind": head.entity_kind,
                "entity_ref": head.entity_ref,
                "revision_id": head.current_revision_id,
                "revision_no": head.revision_no,
            },
            session=session,
        )
        payload = await self._payloads.find_one(
            {
                "entity_kind": head.entity_kind,
                "entity_ref": head.entity_ref,
                "revision_id": head.current_revision_id,
            },
            session=session,
        )
        if metadata is None or payload is None:
            raise EditorialIntegrityError(
                "editorial head points to an incomplete immutable revision"
            )
        if metadata.get("identity_sha256") != head.identity_sha256:
            raise EditorialIntegrityError("editorial head and revision identity do not match")
        self._validate_payload(metadata, payload)
        return metadata

    def _validate_payload(
        self, metadata_raw: Mapping[str, Any], payload_raw: Mapping[str, Any]
    ) -> EditorialPayload:
        try:
            metadata = EditorialRevisionMetadata.model_validate(
                _without_mongo_id(dict(metadata_raw))
            )
            if metadata.entity_kind == "block":
                block_payload = StoredBlockPayload.model_validate(
                    _without_mongo_id(dict(payload_raw))
                )
                payload: EditorialPayload = block_payload
                material: Any = {
                    "block": block_payload.block.model_dump(mode="json", exclude_unset=True)
                }
                actual_identity = EditorialIdentity(
                    entity_kind="block",
                    entity_ref=block_payload.block.ref,
                    block_type=block_payload.block.type,
                    owner_ref=block_payload.block.owner_ref,
                )
            elif metadata.entity_kind == "placement":
                placement_payload = StoredPlacementPayload.model_validate(
                    _without_mongo_id(dict(payload_raw))
                )
                payload = placement_payload
                material = {
                    "placement": placement_payload.placement.model_dump(
                        mode="json", exclude_unset=True
                    )
                }
                actual_identity = EditorialIdentity(
                    entity_kind="placement",
                    entity_ref=placement_payload.placement.ref,
                    block_ref=placement_payload.placement.block_ref,
                    subject_ref=placement_payload.placement.subject_ref,
                )
            else:
                project_payload = StoredProjectPayload.model_validate(
                    _without_mongo_id(dict(payload_raw))
                )
                payload = project_payload
                material = {
                    "project": project_payload.project.model_dump(mode="json", exclude_unset=True),
                    "pinned_blocks": [
                        item.model_dump(mode="json", exclude_unset=True)
                        for item in project_payload.pinned_blocks
                    ],
                }
                actual_identity = EditorialIdentity(
                    entity_kind="project",
                    entity_ref=project_payload.project.ref,
                    unit_ref=project_payload.project.unit_ref,
                )
            if (
                payload.entity_kind != metadata.entity_kind
                or payload.entity_ref != metadata.entity_ref
                or payload.revision_id != metadata.revision_id
                or payload.revision_no != metadata.revision_no
                or payload.content_sha256 != metadata.content_sha256
                or actual_identity != metadata.identity
                or _content_hash(metadata.entity_kind, metadata.entity_ref, material)
                != metadata.content_sha256
            ):
                raise ValueError("revision and payload integrity mismatch")
        except (ValidationError, KeyError, TypeError, ValueError):
            raise EditorialIntegrityError(
                "stored editorial revision failed integrity validation"
            ) from None
        return payload

    async def _mark_retryable(self, operation_ref: str) -> None:
        try:
            await self._operations.update_one(
                {"operation_ref": operation_ref, "state": "pending"},
                {"$set": {"state": "retryable", "updated_at": datetime.now(UTC)}},
            )
        except PyMongoError:
            # Leaving a durable pending reservation is safer than guessing.
            return

    async def _safe_find_operation(self, operation_ref: str) -> dict[str, Any] | None:
        try:
            return await self._operations.find_one({"operation_ref": operation_ref})
        except PyMongoError:
            return None

    async def _wait_for_operation(self, operation_ref: str) -> dict[str, Any] | None:
        deadline = time.monotonic() + self._operation_wait_seconds
        while True:
            operation = await self._safe_find_operation(operation_ref)
            if operation is None or operation.get("state") != "pending":
                return operation
            if time.monotonic() >= deadline:
                return operation
            await asyncio.sleep(0.025)

    async def _replay_or_reject(
        self,
        operation: Mapping[str, Any],
        command_hash: str,
        operation_ref: str,
        kind: EntityKind,
        ref: str,
    ) -> EditorialWriteResult:
        if operation.get("command_sha256") != command_hash:
            raise EditorialIdempotencyConflictError(
                "idempotency key conflicts with another command"
            )
        state = operation.get("state")
        if state == "confirmed":
            return await self._result_from_operation(operation, "unchanged")
        if state == "retryable":
            # The caller has explicitly replayed the same key after a known abort.
            raise EditorialOperationStateError(
                "operation is known not committed; invoke the same command again to resume"
            )
        if state == "pending":
            await self._wait_for_operation(operation_ref)
            latest = await self._safe_find_operation(operation_ref)
            if latest is not None and latest.get("state") == "confirmed":
                if latest.get("command_sha256") != command_hash:
                    raise EditorialIdempotencyConflictError(
                        "idempotency key conflicts with another command"
                    )
                return await self._result_from_operation(latest, "unchanged")
            raise EditorialTransactionOutcomeUnknownError(
                "operation is pending or its outcome is unknown; no new write was started"
            )
        raise EditorialIntegrityError("stored editorial operation has an invalid state")

    async def _result_from_operation(
        self, operation: Mapping[str, Any], outcome: Literal["created", "unchanged"]
    ) -> EditorialWriteResult:
        try:
            return EditorialWriteResult(
                outcome=outcome,
                entity_kind=operation["entity_kind"],
                entity_ref=operation["entity_ref"],
                revision_id=operation["result_revision_id"],
                revision_no=operation["result_revision_no"],
                content_sha256=operation["result_content_sha256"],
                operation_ref=operation["operation_ref"],
            )
        except (ValidationError, KeyError, TypeError):
            raise EditorialIntegrityError(
                "confirmed editorial operation has an invalid result"
            ) from None

    async def get_head(
        self, kind: EntityKind, ref: str, principal: EditorialPrincipal
    ) -> EditorialHead | None:
        self._require(principal, "curriculum.editorial.read")
        raw = await self._heads.find_one({"entity_kind": kind, "entity_ref": ref})
        if raw is None:
            return None
        return self._validate_head(raw, None)

    async def get_revision(
        self,
        kind: EntityKind,
        ref: str,
        revision_id: str,
        principal: EditorialPrincipal,
    ) -> EditorialRevisionRead | None:
        self._require(principal, "curriculum.editorial.read")
        self._require(principal, "curriculum.editorial.content.read")
        if kind in {"block", "project"}:
            self._require(principal, "curriculum.editorial.private.read")
        metadata = await self._revisions.find_one(
            {"entity_kind": kind, "entity_ref": ref, "revision_id": revision_id}
        )
        if metadata is None:
            return None
        raw_payload = await self._payloads.find_one(
            {"entity_kind": kind, "entity_ref": ref, "revision_id": revision_id}
        )
        if raw_payload is None:
            raise EditorialIntegrityError("editorial revision payload is missing")
        payload = self._validate_payload(metadata, raw_payload)
        try:
            return EditorialRevisionRead(
                metadata=EditorialRevisionMetadata.model_validate(_without_mongo_id(metadata)),
                payload=payload,
            )
        except ValidationError:
            raise EditorialIntegrityError("editorial revision response failed validation") from None

    async def list_history(
        self,
        kind: EntityKind,
        ref: str,
        principal: EditorialPrincipal,
        *,
        limit: int = 100,
    ) -> EditorialHistory:
        self._require(principal, "curriculum.editorial.history.read")
        if type(limit) is not int or not 1 <= limit <= 500:
            raise EditorialValidationError("history limit must be between 1 and 500")
        cursor = (
            self._revisions.find({"entity_kind": kind, "entity_ref": ref})
            .sort([("revision_no", -1), ("revision_id", 1)])
            .limit(limit)
        )
        raw_items = await cursor.to_list(length=limit)
        try:
            return EditorialHistory(
                items=[
                    EditorialRevisionMetadata.model_validate(_without_mongo_id(item))
                    for item in raw_items
                ]
            )
        except ValidationError:
            raise EditorialIntegrityError("editorial history contains malformed metadata") from None

    async def get_operation_status(
        self, idempotency_key: str, principal: EditorialPrincipal
    ) -> EditorialOperationStatus:
        self._require(principal, "curriculum.editorial.history.read")
        normalized_key = _validated_idempotency_key(idempotency_key)
        operation_ref = _operation_hash(principal.actor_ref, normalized_key)
        operation = await self._operations.find_one({"operation_ref": operation_ref})
        if operation is None:
            return EditorialOperationStatus(
                state="not_found", operation_ref=operation_ref, outcome_conclusive=False
            )
        state = operation.get("state")
        if state == "confirmed":
            return EditorialOperationStatus(
                state="confirmed",
                operation_ref=operation_ref,
                entity_kind=operation.get("entity_kind"),
                entity_ref=operation.get("entity_ref"),
                revision_id=operation.get("result_revision_id"),
                revision_no=operation.get("result_revision_no"),
                outcome_conclusive=True,
            )
        if state == "retryable":
            return EditorialOperationStatus(
                state="not_committed",
                operation_ref=operation_ref,
                entity_kind=operation.get("entity_kind"),
                entity_ref=operation.get("entity_ref"),
                outcome_conclusive=True,
            )
        if state == "pending":
            return EditorialOperationStatus(
                state="unknown",
                operation_ref=operation_ref,
                entity_kind=operation.get("entity_kind"),
                entity_ref=operation.get("entity_ref"),
                outcome_conclusive=False,
            )
        raise EditorialIntegrityError("stored editorial operation has an invalid state")

    async def _safe_find_head(self, kind: EntityKind, ref: str) -> EditorialHead | None:
        raw = await self._heads.find_one({"entity_kind": kind, "entity_ref": ref})
        return self._validate_head(raw, None) if raw is not None else None


__all__ = [
    "EDITORIAL_SCHEMA_VERSION",
    "EditorialAuthorizationError",
    "EditorialCapability",
    "EditorialEvent",
    "EditorialHead",
    "EditorialHistory",
    "EditorialIdentity",
    "EditorialIntegrityError",
    "EditorialOperationStatus",
    "EditorialPersistenceError",
    "EditorialPersistenceStore",
    "EditorialPrincipal",
    "EditorialReferenceError",
    "EditorialRevisionMetadata",
    "EditorialRevisionRead",
    "EditorialTransactionFailedError",
    "EditorialTransactionOutcomeUnknownError",
    "EditorialTransactionsRequiredError",
    "EditorialValidationError",
    "EditorialVersionConflictError",
    "EditorialWriteResult",
    "IdempotencyKey",
    "PinnedBlockReference",
    "canonical_editorial_bytes",
    "canonical_editorial_sha256",
]
