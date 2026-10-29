"""Isolated, privacy-minimal observation contracts for editorial operations.

This module has no application hooks and performs no I/O at import time. The
default instrumentor is a no-op. Passive observation is opt-in and intended
for isolated tests or a separately authorized future integration.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from types import MappingProxyType
from typing import Awaitable, Callable, Mapping, Protocol, TypeVar


class ObservationContractError(ValueError):
    """Observation metadata is not part of the closed contract."""


class OperationKind(str, Enum):
    TRACK_MUTATE = "track.mutate"
    TRACK_REORDER = "track.reorder"
    TRACK_DUPLICATE = "track.duplicate"
    TRACK_DELETE = "track.delete"
    TRACK_PUBLISH = "track.publish"
    NODE_MUTATE = "node.mutate"
    NODE_REORDER = "node.reorder"
    NODE_DUPLICATE = "node.duplicate"
    NODE_DELETE = "node.delete"
    BLOCK_MUTATE = "block.mutate"
    BLOCK_REORDER = "block.reorder"
    RELATION_MUTATE = "relation.mutate"
    TAXONOMY_MUTATE = "taxonomy.mutate"
    IMPORT_APPLY = "import.apply"
    RESTORE_APPLY = "restore.apply"
    SNAPSHOT_CAPTURE = "snapshot.capture"
    INTEGRITY_RECONCILE = "integrity.reconcile"
    ADMIN_ENSURE_INDEXES = "admin.ensure_indexes"
    ADMIN_SEED = "admin.seed"
    ADMIN_LEGACY_SNAPSHOT_MIGRATION = "admin.legacy_snapshot_migration"
    ADMIN_BLOCK_TYPE_MIGRATION = "admin.block_type_migration"
    PRIVATE_PUBLICATION_PREPARE = "publication.private_prepare"
    EXPERIMENTAL_GENERATION_POC = "experimental.generation_poc"


class EntryPointKind(str, Enum):
    HTTP_ROUTE = "http_route"
    SERVICE = "service"
    CLI = "cli"
    JOB = "job"
    INTERNAL = "internal"
    TEST = "test"


class WriterCategory(str, Enum):
    EDITORIAL_CRUD = "editorial_crud"
    REORDER = "reorder"
    DUPLICATION = "duplication"
    DELETION = "deletion"
    PUBLICATION = "publication"
    BLOCK_CHANGE = "block_change"
    RELATION_CHANGE = "relation_change"
    TAXONOMY = "taxonomy"
    IMPORT = "import"
    RESTORE = "restore"
    SNAPSHOT = "snapshot"
    INTEGRITY = "integrity"
    ADMINISTRATION = "administration"
    EXPERIMENTAL = "experimental"


class OperationOutcome(str, Enum):
    SUCCESS = "success"
    CONFLICT = "conflict"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ProtocolPath(str, Enum):
    LEGACY_DIRECT = "legacy_direct"
    LEGACY_SERVICE = "legacy_service"
    REVISION_PROTOCOL = "revision_protocol"
    UNKNOWN = "unknown"


class DurationBucket(str, Enum):
    UNDER_10MS = "under_10ms"
    MS_10_TO_100 = "10_to_100ms"
    MS_100_TO_1000 = "100ms_to_1s"
    S_1_TO_10 = "1s_to_10s"
    OVER_10S = "over_10s"
    UNKNOWN = "unknown"


class EventKind(str, Enum):
    OPERATION_RESULT_OBSERVED = "operation_result_observed"


@dataclass(frozen=True, slots=True)
class OperationDescriptor:
    """Static catalog metadata; descriptions and references never enter events."""

    operation_kind: OperationKind
    writer_category: WriterCategory
    entrypoints: frozenset[EntryPointKind]
    source_reference: str
    description: str


def _descriptor(
    operation_kind: OperationKind,
    writer_category: WriterCategory,
    entrypoints: tuple[EntryPointKind, ...],
    source_reference: str,
    description: str,
) -> OperationDescriptor:
    return OperationDescriptor(
        operation_kind=operation_kind,
        writer_category=writer_category,
        entrypoints=frozenset(entrypoints),
        source_reference=source_reference,
        description=description,
    )


_HTTP_SERVICE = (EntryPointKind.HTTP_ROUTE, EntryPointKind.SERVICE)
_INTERNAL_SERVICE = (EntryPointKind.INTERNAL, EntryPointKind.SERVICE)

_CATALOG_DATA = {
    OperationKind.TRACK_MUTATE: _descriptor(
        OperationKind.TRACK_MUTATE, WriterCategory.EDITORIAL_CRUD, _HTTP_SERVICE,
        "12C.4 W-01", "Create or update a track.",
    ),
    OperationKind.TRACK_REORDER: _descriptor(
        OperationKind.TRACK_REORDER, WriterCategory.REORDER, _HTTP_SERVICE,
        "12C.4 W-01", "Reorder tracks.",
    ),
    OperationKind.TRACK_DUPLICATE: _descriptor(
        OperationKind.TRACK_DUPLICATE, WriterCategory.DUPLICATION, _HTTP_SERVICE,
        "12C.4 W-02", "Duplicate a track.",
    ),
    OperationKind.TRACK_DELETE: _descriptor(
        OperationKind.TRACK_DELETE, WriterCategory.DELETION, _HTTP_SERVICE,
        "12C.4 W-01", "Delete a track and related structures.",
    ),
    OperationKind.TRACK_PUBLISH: _descriptor(
        OperationKind.TRACK_PUBLISH, WriterCategory.PUBLICATION, _HTTP_SERVICE,
        "12C.4 W-03", "Run the current track publication command.",
    ),
    OperationKind.NODE_MUTATE: _descriptor(
        OperationKind.NODE_MUTATE, WriterCategory.EDITORIAL_CRUD, _HTTP_SERVICE,
        "12C.4 W-04", "Create or update a node.",
    ),
    OperationKind.NODE_REORDER: _descriptor(
        OperationKind.NODE_REORDER, WriterCategory.REORDER, _HTTP_SERVICE,
        "12C.4 W-04", "Reorder nodes.",
    ),
    OperationKind.NODE_DUPLICATE: _descriptor(
        OperationKind.NODE_DUPLICATE, WriterCategory.DUPLICATION, _HTTP_SERVICE,
        "12C.4 W-04", "Duplicate a node and its supported children.",
    ),
    OperationKind.NODE_DELETE: _descriptor(
        OperationKind.NODE_DELETE, WriterCategory.DELETION, _HTTP_SERVICE,
        "12C.4 W-04", "Delete a node subtree and related structures.",
    ),
    OperationKind.BLOCK_MUTATE: _descriptor(
        OperationKind.BLOCK_MUTATE, WriterCategory.BLOCK_CHANGE, _HTTP_SERVICE,
        "12C.4 W-05", "Create, update, or delete a block, including quiz blocks.",
    ),
    OperationKind.BLOCK_REORDER: _descriptor(
        OperationKind.BLOCK_REORDER, WriterCategory.REORDER, _HTTP_SERVICE,
        "12C.4 W-05", "Reorder blocks.",
    ),
    OperationKind.RELATION_MUTATE: _descriptor(
        OperationKind.RELATION_MUTATE, WriterCategory.RELATION_CHANGE, _HTTP_SERVICE,
        "12C.4 W-06", "Create, update, or delete editorial relations.",
    ),
    OperationKind.TAXONOMY_MUTATE: _descriptor(
        OperationKind.TAXONOMY_MUTATE, WriterCategory.TAXONOMY, _HTTP_SERVICE,
        "12C.4 W-07", "Change shared taxonomies, tags, or block types.",
    ),
    OperationKind.IMPORT_APPLY: _descriptor(
        OperationKind.IMPORT_APPLY, WriterCategory.IMPORT,
        (EntryPointKind.HTTP_ROUTE, EntryPointKind.SERVICE, EntryPointKind.CLI),
        "12C.4 W-08", "Apply an editorial import.",
    ),
    OperationKind.RESTORE_APPLY: _descriptor(
        OperationKind.RESTORE_APPLY, WriterCategory.RESTORE,
        (EntryPointKind.HTTP_ROUTE, EntryPointKind.SERVICE, EntryPointKind.CLI, EntryPointKind.JOB),
        "12C.4 W-09", "Apply an editorial restoration.",
    ),
    OperationKind.SNAPSHOT_CAPTURE: _descriptor(
        OperationKind.SNAPSHOT_CAPTURE, WriterCategory.SNAPSHOT, _INTERNAL_SERVICE,
        "12C.4 W-10", "Capture a legacy editorial snapshot.",
    ),
    OperationKind.INTEGRITY_RECONCILE: _descriptor(
        OperationKind.INTEGRITY_RECONCILE, WriterCategory.INTEGRITY, _INTERNAL_SERVICE,
        "12C.4 W-10", "Reconcile editorial integrity references.",
    ),
    OperationKind.ADMIN_ENSURE_INDEXES: _descriptor(
        OperationKind.ADMIN_ENSURE_INDEXES, WriterCategory.ADMINISTRATION,
        (EntryPointKind.CLI, EntryPointKind.INTERNAL),
        "12C.4 W-11", "Ensure application indexes.",
    ),
    OperationKind.ADMIN_SEED: _descriptor(
        OperationKind.ADMIN_SEED, WriterCategory.ADMINISTRATION,
        (EntryPointKind.CLI, EntryPointKind.INTERNAL),
        "12C.4 W-11", "Run configured seed operations.",
    ),
    OperationKind.ADMIN_LEGACY_SNAPSHOT_MIGRATION: _descriptor(
        OperationKind.ADMIN_LEGACY_SNAPSHOT_MIGRATION, WriterCategory.ADMINISTRATION,
        (EntryPointKind.CLI, EntryPointKind.INTERNAL),
        "12C.4 W-11", "Migrate legacy snapshots.",
    ),
    OperationKind.ADMIN_BLOCK_TYPE_MIGRATION: _descriptor(
        OperationKind.ADMIN_BLOCK_TYPE_MIGRATION, WriterCategory.ADMINISTRATION,
        (EntryPointKind.CLI, EntryPointKind.INTERNAL),
        "12C.4 W-11", "Migrate block-type submission capabilities.",
    ),
    OperationKind.PRIVATE_PUBLICATION_PREPARE: _descriptor(
        OperationKind.PRIVATE_PUBLICATION_PREPARE, WriterCategory.PUBLICATION, _INTERNAL_SERVICE,
        "12C.4 W-12", "Prepare an ineligible private publication candidate.",
    ),
    OperationKind.EXPERIMENTAL_GENERATION_POC: _descriptor(
        OperationKind.EXPERIMENTAL_GENERATION_POC, WriterCategory.EXPERIMENTAL,
        (EntryPointKind.TEST,), "12C.4 W-13", "Exercise the isolated generation PoC only.",
    ),
}

OPERATION_CATALOG: Mapping[OperationKind, OperationDescriptor] = MappingProxyType(_CATALOG_DATA)
del _CATALOG_DATA


def get_operation_descriptor(operation_kind: OperationKind) -> OperationDescriptor:
    """Return one static descriptor; arbitrary strings and unknown IDs fail closed."""

    if type(operation_kind) is not OperationKind:
        raise ObservationContractError("operation_kind must be a catalog enum value")
    try:
        return OPERATION_CATALOG[operation_kind]
    except KeyError:
        raise ObservationContractError("operation_kind is not in the static catalog") from None


@dataclass(frozen=True, slots=True)
class ObservationContext:
    """Validated, closed metadata for one future integration call site."""

    operation: OperationDescriptor
    entrypoint_kind: EntryPointKind
    protocol_path: ProtocolPath

    def __post_init__(self) -> None:
        if type(self.operation) is not OperationDescriptor:
            raise ObservationContractError("operation must be a static catalog descriptor")
        if OPERATION_CATALOG.get(self.operation.operation_kind) is not self.operation:
            raise ObservationContractError("operation descriptor is not the registered catalog entry")
        if type(self.entrypoint_kind) is not EntryPointKind:
            raise ObservationContractError("entrypoint_kind must be a closed enum value")
        if self.entrypoint_kind not in self.operation.entrypoints:
            raise ObservationContractError("entrypoint_kind is not allowed for this catalog operation")
        if type(self.protocol_path) is not ProtocolPath:
            raise ObservationContractError("protocol_path must be a closed enum value")


@dataclass(frozen=True, slots=True)
class EditorialObservationEvent:
    """Strict event schema. No domain, request, exception, or arbitrary metadata fields."""

    schema_version: int
    operation_kind: OperationKind
    entrypoint_kind: EntryPointKind
    writer_category: WriterCategory
    outcome: OperationOutcome
    duration_bucket: DurationBucket
    protocol_path: ProtocolPath
    event_kind: EventKind

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ObservationContractError("unsupported event schema_version")
        descriptor = get_operation_descriptor(self.operation_kind)
        if type(self.entrypoint_kind) is not EntryPointKind:
            raise ObservationContractError("entrypoint_kind must be a closed enum value")
        if self.entrypoint_kind not in descriptor.entrypoints:
            raise ObservationContractError("entrypoint_kind is not allowed for this operation")
        if type(self.writer_category) is not WriterCategory or self.writer_category is not descriptor.writer_category:
            raise ObservationContractError("writer_category does not match the static operation catalog")
        if type(self.outcome) is not OperationOutcome:
            raise ObservationContractError("outcome must be a closed enum value")
        if type(self.duration_bucket) is not DurationBucket:
            raise ObservationContractError("duration_bucket must be a closed enum value")
        if type(self.protocol_path) is not ProtocolPath:
            raise ObservationContractError("protocol_path must be a closed enum value")
        if type(self.event_kind) is not EventKind:
            raise ObservationContractError("event_kind must be a closed enum value")

    def to_public_mapping(self) -> dict[str, str | int]:
        """Return only the reviewed schema fields, with enum values explicitly encoded."""

        return {
            "schema_version": self.schema_version,
            "operation_kind": self.operation_kind.value,
            "entrypoint_kind": self.entrypoint_kind.value,
            "writer_category": self.writer_category.value,
            "outcome": self.outcome.value,
            "duration_bucket": self.duration_bucket.value,
            "protocol_path": self.protocol_path.value,
            "event_kind": self.event_kind.value,
        }


class EventSink(Protocol):
    """A passive, non-blocking sink. Implementations must not perform external I/O."""

    def try_emit(self, event: EditorialObservationEvent) -> bool:
        """Accept an event without waiting, or return False when it is dropped."""


_T = TypeVar("_T")
ResultClassifier = Callable[[object], OperationOutcome]
ExceptionClassifier = Callable[[Exception], OperationOutcome]
Clock = Callable[[], int]


class EditorialInstrumentor(Protocol):
    """Sync/async operation wrapper interface; no domain dependencies."""

    def observe_sync(
        self,
        context: ObservationContext,
        operation: Callable[[], _T],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        ...

    async def observe_async(
        self,
        context: ObservationContext,
        operation: Callable[[], Awaitable[_T]],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        ...


class NullEditorialInstrumentor:
    """Default instrumentor: invoke the callable once and perform no observation."""

    def observe_sync(
        self,
        context: ObservationContext,
        operation: Callable[[], _T],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        del context
        del result_classifier, exception_classifier
        return operation()

    async def observe_async(
        self,
        context: ObservationContext,
        operation: Callable[[], Awaitable[_T]],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        del context
        del result_classifier, exception_classifier
        return await operation()


NULL_EDITORIAL_INSTRUMENTOR = NullEditorialInstrumentor()


def default_instrumentor() -> EditorialInstrumentor:
    """Return the disabled-by-default no-op instance; reads no configuration."""

    return NULL_EDITORIAL_INSTRUMENTOR


class InMemoryEventCollector:
    """Bounded, non-blocking, in-memory collector intended only for tests."""

    def __init__(self, capacity: int = 256) -> None:
        if type(capacity) is not int or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._capacity = capacity
        self._events: deque[EditorialObservationEvent] = deque()
        self._dropped_count = 0
        self._lock = Lock()

    def try_emit(self, event: EditorialObservationEvent) -> bool:
        if type(event) is not EditorialObservationEvent:
            raise TypeError("collector accepts only validated EditorialObservationEvent instances")
        if not self._lock.acquire(blocking=False):
            return False
        try:
            if len(self._events) >= self._capacity:
                self._dropped_count += 1
                return False
            self._events.append(event)
            return True
        finally:
            self._lock.release()

    def snapshot(self) -> tuple[EditorialObservationEvent, ...]:
        """Copy events for assertions; this read method may wait outside observation."""

        with self._lock:
            return tuple(self._events)

    @property
    def dropped_count(self) -> int:
        with self._lock:
            return self._dropped_count

    def clear(self) -> None:
        """Explicitly clear test state between cases."""

        with self._lock:
            self._events.clear()
            self._dropped_count = 0


class PassiveEditorialInstrumentor:
    """Fail-open wrapper that observes only fixed metadata and never retries work."""

    def __init__(self, sink: EventSink, clock: Clock = time.monotonic_ns) -> None:
        if not callable(getattr(sink, "try_emit", None)):
            raise TypeError("sink must implement non-blocking try_emit(event)")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self._sink = sink
        self._clock = clock

    def observe_sync(
        self,
        context: ObservationContext,
        operation: Callable[[], _T],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        self._validate_call(context, operation, result_classifier, exception_classifier)
        started = self._read_clock()
        try:
            result = operation()
        except Exception as error:
            ended = self._read_clock() if started is not None else None
            outcome = self._classify_exception(error, exception_classifier)
            self._emit(context, outcome, started, ended)
            raise
        ended = self._read_clock() if started is not None else None
        outcome = self._classify_result(result, result_classifier)
        self._emit(context, outcome, started, ended)
        return result

    async def observe_async(
        self,
        context: ObservationContext,
        operation: Callable[[], Awaitable[_T]],
        *,
        result_classifier: ResultClassifier | None = None,
        exception_classifier: ExceptionClassifier | None = None,
    ) -> _T:
        self._validate_call(context, operation, result_classifier, exception_classifier)
        started = self._read_clock()
        try:
            result = await operation()
        except asyncio.CancelledError:
            ended = self._read_clock() if started is not None else None
            self._emit(context, OperationOutcome.CANCELLED, started, ended)
            raise
        except Exception as error:
            ended = self._read_clock() if started is not None else None
            outcome = self._classify_exception(error, exception_classifier)
            self._emit(context, outcome, started, ended)
            raise
        ended = self._read_clock() if started is not None else None
        outcome = self._classify_result(result, result_classifier)
        self._emit(context, outcome, started, ended)
        return result

    @staticmethod
    def _validate_call(
        context: ObservationContext,
        operation: Callable[[], object],
        result_classifier: ResultClassifier | None,
        exception_classifier: ExceptionClassifier | None,
    ) -> None:
        if type(context) is not ObservationContext:
            raise ObservationContractError("context must be validated ObservationContext")
        if not callable(operation):
            raise TypeError("operation must be callable")
        if result_classifier is not None and not callable(result_classifier):
            raise TypeError("result_classifier must be callable")
        if exception_classifier is not None and not callable(exception_classifier):
            raise TypeError("exception_classifier must be callable")

    def _read_clock(self) -> int | None:
        try:
            value = self._clock()
        except Exception:
            return None
        return value if type(value) is int and value >= 0 else None

    @staticmethod
    def _classify_result(result: object, classifier: ResultClassifier | None) -> OperationOutcome:
        if classifier is None:
            return OperationOutcome.UNKNOWN
        try:
            outcome = classifier(result)
        except Exception:
            return OperationOutcome.UNKNOWN
        return outcome if type(outcome) is OperationOutcome else OperationOutcome.UNKNOWN

    @staticmethod
    def _classify_exception(
        error: Exception, classifier: ExceptionClassifier | None
    ) -> OperationOutcome:
        if classifier is None:
            return OperationOutcome.FAILED
        try:
            outcome = classifier(error)
        except Exception:
            return OperationOutcome.FAILED
        if type(outcome) is OperationOutcome and outcome in {
            OperationOutcome.CONFLICT,
            OperationOutcome.REJECTED,
            OperationOutcome.FAILED,
            OperationOutcome.UNKNOWN,
        }:
            return outcome
        return OperationOutcome.FAILED

    def _emit(
        self,
        context: ObservationContext,
        outcome: OperationOutcome,
        started: int | None,
        ended: int | None,
    ) -> None:
        bucket = self._duration_bucket(started, ended)
        try:
            event = EditorialObservationEvent(
                schema_version=1,
                operation_kind=context.operation.operation_kind,
                entrypoint_kind=context.entrypoint_kind,
                writer_category=context.operation.writer_category,
                outcome=outcome,
                duration_bucket=bucket,
                protocol_path=context.protocol_path,
                event_kind=EventKind.OPERATION_RESULT_OBSERVED,
            )
            self._sink.try_emit(event)
        except Exception:
            # Fail open: never expose collector details or alter the operation result.
            return

    @staticmethod
    def _duration_bucket(started: int | None, ended: int | None) -> DurationBucket:
        if started is None or ended is None:
            return DurationBucket.UNKNOWN
        if ended < started:
            return DurationBucket.UNKNOWN
        elapsed = ended - started
        if elapsed < 10_000_000:
            return DurationBucket.UNDER_10MS
        if elapsed < 100_000_000:
            return DurationBucket.MS_10_TO_100
        if elapsed < 1_000_000_000:
            return DurationBucket.MS_100_TO_1000
        if elapsed < 10_000_000_000:
            return DurationBucket.S_1_TO_10
        return DurationBucket.OVER_10S
