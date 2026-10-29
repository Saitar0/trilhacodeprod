"""Offline security, privacy, and transparency tests for editorial observation."""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import socket
import sys
import threading
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from curriculum_contract import editorial_observability as observability
from curriculum_contract.editorial_observability import (
    OPERATION_CATALOG,
    DurationBucket,
    EditorialObservationEvent,
    EntryPointKind,
    EventKind,
    InMemoryEventCollector,
    NullEditorialInstrumentor,
    ObservationContext,
    ObservationContractError,
    OperationKind,
    OperationOutcome,
    PassiveEditorialInstrumentor,
    ProtocolPath,
    WriterCategory,
    default_instrumentor,
    get_operation_descriptor,
)


def context(
    operation_kind: OperationKind = OperationKind.TRACK_MUTATE,
    entrypoint: EntryPointKind = EntryPointKind.HTTP_ROUTE,
    protocol_path: ProtocolPath = ProtocolPath.LEGACY_SERVICE,
) -> ObservationContext:
    return ObservationContext(
        operation=get_operation_descriptor(operation_kind),
        entrypoint_kind=entrypoint,
        protocol_path=protocol_path,
    )


def make_event(**overrides: object) -> EditorialObservationEvent:
    values: dict[str, object] = {
        "schema_version": 1,
        "operation_kind": OperationKind.TRACK_MUTATE,
        "entrypoint_kind": EntryPointKind.HTTP_ROUTE,
        "writer_category": WriterCategory.EDITORIAL_CRUD,
        "outcome": OperationOutcome.UNKNOWN,
        "duration_bucket": DurationBucket.UNKNOWN,
        "protocol_path": ProtocolPath.LEGACY_SERVICE,
        "event_kind": EventKind.OPERATION_RESULT_OBSERVED,
    }
    values.update(overrides)
    return EditorialObservationEvent(**values)  # type: ignore[arg-type]


class FakeClock:
    def __init__(self, *values: int | Exception) -> None:
        self._values = iter(values)

    def __call__(self) -> int:
        value = next(self._values)
        if isinstance(value, Exception):
            raise value
        return value


class ExplodingSink:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls = 0

    def try_emit(self, event: EditorialObservationEvent) -> bool:
        self.calls += 1
        raise self.error


class EditorialObservabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.collector = InMemoryEventCollector(capacity=64)
        self.instrumentor = PassiveEditorialInstrumentor(
            self.collector, clock=FakeClock(100, 101)
        )
        self.context = context()

    def test_01_import_has_no_network_thread_or_logging_setup(self) -> None:
        module_path = Path(observability.__file__)
        spec = importlib.util.spec_from_file_location(
            "_editorial_observability_import_probe", module_path
        )
        assert spec is not None
        assert spec.loader is not None
        probe = importlib.util.module_from_spec(spec)
        probe_name = spec.name
        with (
            patch.object(socket, "create_connection", side_effect=AssertionError("network")),
            patch.object(threading.Thread, "start", side_effect=AssertionError("thread")),
            patch.object(logging, "basicConfig", side_effect=AssertionError("logging setup")),
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("network")),
        ):
            sys.modules[probe_name] = probe
            try:
                spec.loader.exec_module(probe)
            finally:
                sys.modules.pop(probe_name, None)
        self.assertFalse(hasattr(probe, "client"))

    def test_02_default_is_null_and_emits_nothing(self) -> None:
        default = default_instrumentor()
        self.assertIs(default, default_instrumentor())
        self.assertIsInstance(default, NullEditorialInstrumentor)
        calls: list[str] = []
        value = object()

        def operation() -> object:
            calls.append("run")
            return value

        returned = default.observe_sync(self.context, operation)
        self.assertIs(returned, value)
        self.assertEqual(calls, ["run"])
        self.assertEqual(self.collector.snapshot(), ())

    def test_03_observed_operation_executes_exactly_once(self) -> None:
        calls = 0

        def operation() -> str:
            nonlocal calls
            calls += 1
            return "done"

        self.instrumentor.observe_sync(self.context, operation)
        self.assertEqual(calls, 1)

    def test_04_return_object_identity_is_preserved(self) -> None:
        value = {"synthetic": object()}
        returned = self.instrumentor.observe_sync(self.context, lambda: value)
        self.assertIs(returned, value)

    def test_05_exception_identity_is_preserved(self) -> None:
        error = RuntimeError("synthetic failure")

        def operation() -> None:
            raise error

        with self.assertRaises(RuntimeError) as raised:
            self.instrumentor.observe_sync(self.context, operation)
        self.assertIs(raised.exception, error)
        self.assertEqual(self.collector.snapshot()[0].outcome, OperationOutcome.FAILED)

    def test_06_sink_failure_does_not_change_successful_result(self) -> None:
        value = object()
        sink = ExplodingSink(RuntimeError("collector failure"))
        observer = PassiveEditorialInstrumentor(sink, clock=FakeClock(1, 2))
        self.assertIs(observer.observe_sync(self.context, lambda: value), value)
        self.assertEqual(sink.calls, 1)

    def test_07_sink_failure_does_not_replace_operation_exception(self) -> None:
        operation_error = ValueError("operation failure")
        sink_error = RuntimeError("collector failure")
        sink = ExplodingSink(sink_error)
        observer = PassiveEditorialInstrumentor(sink, clock=FakeClock(1, 2))

        def operation() -> None:
            raise operation_error

        with self.assertRaises(ValueError) as raised:
            observer.observe_sync(self.context, operation)
        self.assertIs(raised.exception, operation_error)
        self.assertEqual(sink.calls, 1)

    def test_08_event_rejects_unknown_fields(self) -> None:
        with self.assertRaises(TypeError):
            make_event(payload={"answer": "secret"})

    def test_09_context_rejects_arbitrary_metadata(self) -> None:
        with self.assertRaises(ObservationContractError):
            ObservationContext(
                operation={"operation": "track.update"},  # type: ignore[arg-type]
                entrypoint_kind=EntryPointKind.HTTP_ROUTE,
                protocol_path=ProtocolPath.LEGACY_SERVICE,
            )

    def test_10_payload_cannot_be_added_to_event(self) -> None:
        with self.assertRaises(TypeError):
            make_event(payload={"private": True})

    def test_11_personal_or_content_identifiers_are_not_event_fields(self) -> None:
        for name in ("track_id", "node_id", "student_id", "user_id", "email", "ip"):
            with self.subTest(name=name), self.assertRaises(TypeError):
                make_event(**{name: "synthetic-sensitive-value"})

    def test_12_event_rejects_string_for_enum_value(self) -> None:
        with self.assertRaises(ObservationContractError):
            make_event(operation_kind="track.mutate")

    def test_13_catalog_has_fixed_ids_and_is_read_only(self) -> None:
        self.assertIn(OperationKind.TRACK_PUBLISH, OPERATION_CATALOG)
        self.assertIn(OperationKind.RESTORE_APPLY, OPERATION_CATALOG)
        self.assertFalse(hasattr(observability, "_CATALOG_DATA"))
        with self.assertRaises(TypeError):
            OPERATION_CATALOG[OperationKind.TRACK_MUTATE] = OPERATION_CATALOG[
                OperationKind.TRACK_MUTATE
            ]

    def test_14_unknown_operation_id_is_rejected(self) -> None:
        with self.assertRaises(ObservationContractError):
            get_operation_descriptor("unknown.operation")  # type: ignore[arg-type]

    def test_15_duration_buckets_use_only_fixed_categories(self) -> None:
        cases = (
            (9_999_999, DurationBucket.UNDER_10MS),
            (10_000_000, DurationBucket.MS_10_TO_100),
            (99_999_999, DurationBucket.MS_10_TO_100),
            (100_000_000, DurationBucket.MS_100_TO_1000),
            (1_000_000_000, DurationBucket.S_1_TO_10),
            (10_000_000_000, DurationBucket.OVER_10S),
        )
        for elapsed, expected in cases:
            with self.subTest(elapsed=elapsed):
                collector = InMemoryEventCollector()
                observer = PassiveEditorialInstrumentor(
                    collector, clock=FakeClock(1, 1 + elapsed)
                )
                observer.observe_sync(self.context, lambda: None)
                self.assertEqual(collector.snapshot()[0].duration_bucket, expected)

    def test_16_concurrent_calls_leave_only_valid_events(self) -> None:
        count = 24
        barrier = threading.Barrier(count)
        observer = PassiveEditorialInstrumentor(
            self.collector, clock=lambda: 1
        )

        def run(index: int) -> int:
            barrier.wait(timeout=5)
            return observer.observe_sync(self.context, lambda: index)

        with ThreadPoolExecutor(max_workers=count) as pool:
            results = list(pool.map(run, range(count)))
        self.assertEqual(sorted(results), list(range(count)))
        events = self.collector.snapshot()
        self.assertLessEqual(len(events), count)
        self.assertTrue(all(type(event) is EditorialObservationEvent for event in events))

    def test_17_collector_capacity_is_bounded_and_drops_new_events(self) -> None:
        collector = InMemoryEventCollector(capacity=2)
        observer = PassiveEditorialInstrumentor(collector, clock=lambda: 1)
        for _ in range(5):
            observer.observe_sync(self.context, lambda: None)
        self.assertEqual(len(collector.snapshot()), 2)
        self.assertEqual(collector.dropped_count, 3)

    def test_18_sync_observer_preserves_order_and_single_call(self) -> None:
        order: list[str] = []

        def operation() -> str:
            order.append("operation")
            return "value"

        result = self.instrumentor.observe_sync(self.context, operation)
        self.assertEqual(result, "value")
        self.assertEqual(order, ["operation"])
        self.assertEqual(len(self.collector.snapshot()), 1)

    def test_19_async_observer_preserves_return_and_single_call(self) -> None:
        async def run() -> None:
            calls = 0
            value = object()

            async def operation() -> object:
                nonlocal calls
                calls += 1
                return value

            returned = await self.instrumentor.observe_async(self.context, operation)
            self.assertIs(returned, value)
            self.assertEqual(calls, 1)

        asyncio.run(run())

    def test_20_async_cancellation_propagates_same_instance(self) -> None:
        async def run() -> None:
            cancellation = asyncio.CancelledError("synthetic cancellation")
            calls = 0

            async def operation() -> object:
                nonlocal calls
                calls += 1
                raise cancellation

            with self.assertRaises(asyncio.CancelledError) as raised:
                await self.instrumentor.observe_async(self.context, operation)
            self.assertIs(raised.exception, cancellation)
            self.assertEqual(calls, 1)
            self.assertEqual(self.collector.snapshot()[0].outcome, OperationOutcome.CANCELLED)

        asyncio.run(run())

    def test_21_event_serialization_never_walks_domain_objects(self) -> None:
        class DomainObject:
            track_id = "student-track-sensitive"
            answer = "private-answer"

        domain = DomainObject()
        self.instrumentor.observe_sync(self.context, lambda: domain)
        mapping = self.collector.snapshot()[0].to_public_mapping()
        self.assertEqual(
            set(mapping),
            {
                "schema_version", "operation_kind", "entrypoint_kind", "writer_category",
                "outcome", "duration_bucket", "protocol_path", "event_kind",
            },
        )
        self.assertNotIn("student-track-sensitive", repr(mapping))
        self.assertNotIn("private-answer", repr(mapping))

    def test_22_collector_failure_logs_no_exception_details(self) -> None:
        sensitive_text = "synthetic-private-payload-must-not-appear"
        observer = PassiveEditorialInstrumentor(
            ExplodingSink(RuntimeError(sensitive_text)), clock=FakeClock(1, 2)
        )
        with self.assertNoLogs(level="DEBUG"):
            observer.observe_sync(self.context, lambda: "safe-result")

    def test_23_observation_does_not_access_network(self) -> None:
        with (
            patch.object(socket, "create_connection", side_effect=AssertionError("network")),
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("network")),
        ):
            result = self.instrumentor.observe_sync(self.context, lambda: "offline")
        self.assertEqual(result, "offline")

    def test_24_clock_failure_yields_unknown_duration_without_changing_result(self) -> None:
        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(
            collector, clock=FakeClock(RuntimeError("clock failure"))
        )
        value = object()
        self.assertIs(observer.observe_sync(self.context, lambda: value), value)
        self.assertEqual(collector.snapshot()[0].duration_bucket, DurationBucket.UNKNOWN)

    def test_25_outcome_is_unknown_unless_explicitly_classified(self) -> None:
        self.instrumentor.observe_sync(self.context, lambda: {"http_status": 200})
        self.assertEqual(self.collector.snapshot()[0].outcome, OperationOutcome.UNKNOWN)

        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(collector, clock=FakeClock(1, 2))
        observer.observe_sync(
            self.context,
            lambda: "explicit-domain-conflict",
            result_classifier=lambda _result: OperationOutcome.CONFLICT,
        )
        self.assertEqual(collector.snapshot()[0].outcome, OperationOutcome.CONFLICT)

    def test_26_operation_is_not_retried_or_given_additional_mutations(self) -> None:
        calls = [0]
        returned = ["original"]

        def operation() -> list[str]:
            calls[0] += 1
            return returned

        result = self.instrumentor.observe_sync(self.context, operation)
        self.assertIs(result, returned)
        self.assertEqual(calls, [1])
        self.assertEqual(returned, ["original"])

    def test_27_mismatched_category_is_rejected(self) -> None:
        with self.assertRaises(ObservationContractError):
            make_event(writer_category=WriterCategory.PUBLICATION)

    def test_28_unsupported_entrypoint_is_rejected(self) -> None:
        with self.assertRaises(ObservationContractError):
            context(OperationKind.ADMIN_SEED, EntryPointKind.HTTP_ROUTE)

    def test_29_schema_has_no_identity_or_payload_extension_fields(self) -> None:
        for name in (
            "track_id", "node_id", "student_id", "user_id", "document_id", "payload",
            "answer", "email", "ip", "exception", "stack_trace", "request",
        ):
            with self.subTest(name=name), self.assertRaises(TypeError):
                make_event(**{name: "forbidden"})

    def test_30_async_sink_failure_preserves_success_result(self) -> None:
        async def run() -> None:
            value = object()
            observer = PassiveEditorialInstrumentor(
                ExplodingSink(RuntimeError("collector")), clock=FakeClock(1, 2)
            )
            returned = await observer.observe_async(self.context, lambda: _immediate(value))
            self.assertIs(returned, value)

        asyncio.run(run())

    def test_31_invalid_result_classifier_fails_open_to_unknown(self) -> None:
        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(collector, clock=FakeClock(1, 2))
        value = object()
        returned = observer.observe_sync(
            self.context, lambda: value,
            result_classifier=lambda _result: "success",  # type: ignore[arg-type,return-value]
        )
        self.assertIs(returned, value)
        self.assertEqual(collector.snapshot()[0].outcome, OperationOutcome.UNKNOWN)

    def test_32_exception_classifier_uses_only_closed_outcomes(self) -> None:
        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(collector, clock=FakeClock(1, 2))
        error = RuntimeError("private message")

        def operation() -> None:
            raise error

        with self.assertRaises(RuntimeError) as raised:
            observer.observe_sync(
                self.context,
                operation,
                exception_classifier=lambda _error: OperationOutcome.REJECTED,
            )
        self.assertIs(raised.exception, error)
        self.assertEqual(collector.snapshot()[0].outcome, OperationOutcome.REJECTED)

    def test_33_contended_collector_drops_without_blocking_operation(self) -> None:
        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(collector, clock=lambda: 1)
        operation_called = False
        self.assertTrue(collector._lock.acquire(blocking=False))
        try:
            value = object()

            def operation() -> object:
                nonlocal operation_called
                operation_called = True
                return value

            self.assertIs(observer.observe_sync(self.context, operation), value)
        finally:
            collector._lock.release()
        self.assertTrue(operation_called)
        self.assertEqual(collector.snapshot(), ())

    def test_34_clear_resets_bounded_test_state(self) -> None:
        self.instrumentor.observe_sync(self.context, lambda: None)
        self.collector.clear()
        self.assertEqual(self.collector.snapshot(), ())
        self.assertEqual(self.collector.dropped_count, 0)

    def test_35_clock_regression_yields_unknown_duration(self) -> None:
        collector = InMemoryEventCollector()
        observer = PassiveEditorialInstrumentor(collector, clock=FakeClock(10, 9))
        observer.observe_sync(self.context, lambda: None)
        self.assertEqual(collector.snapshot()[0].duration_bucket, DurationBucket.UNKNOWN)

    def test_36_duration_stops_before_result_classification(self) -> None:
        order: list[str] = []
        ticks = iter((10, 15))

        def clock() -> int:
            order.append("clock")
            return next(ticks)

        observer = PassiveEditorialInstrumentor(self.collector, clock=clock)

        def operation() -> str:
            order.append("operation")
            return "synthetic-result"

        def classify(_result: object) -> OperationOutcome:
            order.append("classifier")
            return OperationOutcome.SUCCESS

        observer.observe_sync(self.context, operation, result_classifier=classify)
        self.assertEqual(order, ["clock", "operation", "clock", "classifier"])
        self.assertEqual(self.collector.snapshot()[0].duration_bucket, DurationBucket.UNDER_10MS)


async def _immediate(value: object) -> object:
    return value


if __name__ == "__main__":
    unittest.main()
