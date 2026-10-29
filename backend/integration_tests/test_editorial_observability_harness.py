"""Behavioral transparency tests around one repository writer and synthetic fakes."""

from __future__ import annotations

import asyncio
import copy
import io
import logging
import socket
import sys
import unittest
import urllib.request
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from curriculum_contract.editorial_observability import (
    OPERATION_CATALOG,
    DurationBucket,
    EditorialObservationEvent,
    EntryPointKind,
    EventKind,
    InMemoryEventCollector,
    NullEditorialInstrumentor,
    OperationKind,
    OperationOutcome,
    PassiveEditorialInstrumentor,
    ProtocolPath,
    WriterCategory,
    get_operation_descriptor,
)
from integration_tests.editorial_observability_harness import (
    SyntheticHTTPException,
    WriterHarness,
    default_context,
    load_real_update_block,
)

PRIVATE_SENTINEL = "synthetic-private-answer-DO-NOT-EMIT"


class ExplodingSink:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls = 0

    def try_emit(self, _event: EditorialObservationEvent) -> bool:
        self.calls += 1
        raise self.error


class FixedClock:
    def __init__(self, *values: int | Exception) -> None:
        self.values = iter(values)

    def __call__(self) -> int:
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        return value


def _run_case(
    mode: str,
    *,
    data: dict[str, Any] | None = None,
    update_error: Exception | None = None,
    find_error: Exception | None = None,
    audit_error: Exception | None = None,
    get_error: Exception | None = None,
    clock: Callable[[], int] | None = None,
    result_classifier: Callable[[object], OperationOutcome] | None = None,
    exception_classifier: Callable[[Exception], OperationOutcome] | None = None,
) -> dict[str, Any]:
    harness = load_real_update_block(
        data=copy.deepcopy(data) if data is not None else None,
        update_error=update_error,
        find_error=find_error,
        audit_error=audit_error,
        get_error=get_error,
    )
    collector = InMemoryEventCollector(capacity=8)
    if mode == "none":
        instrumentor: Any = None
    elif mode == "null":
        instrumentor = NullEditorialInstrumentor()
    elif mode == "passive":
        instrumentor = PassiveEditorialInstrumentor(collector, clock=clock or FixedClock(1, 2))
    elif mode == "broken":
        instrumentor = PassiveEditorialInstrumentor(
            ExplodingSink(RuntimeError("synthetic collector failure")),
            clock=clock or FixedClock(1, 2),
        )
    else:
        raise ValueError(f"unknown test mode: {mode}")

    async def invoke() -> object:
        if instrumentor is None:
            return await harness.invoke()
        return await instrumentor.observe_async(
            default_context(),
            harness.invoke,
            result_classifier=result_classifier,
            exception_classifier=exception_classifier,
        )

    result: object | None = None
    error: BaseException | None = None
    try:
        result = asyncio.run(invoke())
    except BaseException as caught:  # test harness records cancellation as an outcome
        error = caught
    return {
        "harness": harness,
        "collector": collector,
        "instrumentor": instrumentor,
        "result": result,
        "error": error,
    }


def _profile(case: dict[str, Any]) -> tuple[Any, ...]:
    harness: WriterHarness = case["harness"]
    result = case["result"]
    return (
        type(result),
        result,
        tuple(harness.trace),
        copy.deepcopy(harness.collection.document),
        copy.deepcopy(harness.data),
        type(case["error"]) if case["error"] is not None else None,
        str(case["error"]) if case["error"] is not None else None,
    )


def _event_mapping(case: dict[str, Any]) -> dict[str, str | int]:
    events = case["collector"].snapshot()
    if len(events) != 1:
        raise AssertionError(f"expected one event, got {len(events)}")
    return events[0].to_public_mapping()


class EditorialObservabilityHarnessTests(unittest.TestCase):
    def test_01_loads_the_real_repository_symbol(self) -> None:
        database_before = sys.modules.get("database")
        case = _run_case("none")
        harness: WriterHarness = case["harness"]
        self.assertEqual(harness.source_path, Path(__file__).resolve().parents[1] / "services" / "blocks.py")
        self.assertEqual(harness.update_block.__name__, "update_block")
        self.assertEqual(Path(harness.update_block.__code__.co_filename).resolve(), harness.source_path)
        self.assertNotIn(harness.synthetic_module_name, sys.modules)
        self.assertIs(sys.modules.get("database"), database_before)
        self.assertIs(harness.update_block.__globals__["db"].content_blocks, harness.collection)

    def test_02_uninstrumented_execution_is_reference(self) -> None:
        case = _run_case("none")
        self.assertIsNone(case["error"])
        self.assertEqual(case["harness"].trace.count("update_one"), 1)
        self.assertEqual(case["collector"].snapshot(), ())

    def test_03_null_instrumentor_matches_reference(self) -> None:
        self.assertEqual(_profile(_run_case("null")), _profile(_run_case("none")))

    def test_04_passive_instrumentor_matches_reference(self) -> None:
        baseline = _run_case("none")
        observed = _run_case("passive")
        self.assertEqual(_profile(observed), _profile(baseline))
        self.assertEqual(_event_mapping(observed)["outcome"], OperationOutcome.UNKNOWN.value)

    def test_05_writer_executes_once_in_each_mode(self) -> None:
        for mode in ("none", "null", "passive", "broken"):
            with self.subTest(mode=mode):
                case = _run_case(mode)
                self.assertEqual(case["harness"].trace.count("update_one"), 1)
                self.assertEqual(case["harness"].trace.count("audit"), 1)

    def test_06_wrapped_return_is_the_writer_return_object(self) -> None:
        for mode in ("none", "null", "passive", "broken"):
            with self.subTest(mode=mode):
                case = _run_case(mode)
                self.assertIs(case["result"], case["harness"].collection.last_result)

    def test_07_update_exception_identity_is_preserved(self) -> None:
        for mode in ("none", "null", "passive", "broken"):
            with self.subTest(mode=mode):
                expected = RuntimeError("synthetic update failure")
                case = _run_case(mode, update_error=expected)
                self.assertIs(case["error"], expected)
                self.assertEqual(case["harness"].trace.count("update_one"), 1)
                self.assertEqual(case["harness"].trace.count("audit"), 0)

    def test_08_broken_collector_does_not_change_successful_writer(self) -> None:
        baseline = _run_case("none")
        observed = _run_case("broken")
        self.assertEqual(_profile(observed), _profile(baseline))
        self.assertEqual(observed["instrumentor"]._sink.calls, 1)

    def test_09_broken_collector_does_not_replace_writer_error(self) -> None:
        expected = RuntimeError("synthetic writer error")
        case = _run_case("broken", update_error=expected)
        self.assertIs(case["error"], expected)
        self.assertEqual(case["instrumentor"]._sink.calls, 1)

    def test_10_private_input_never_enters_event(self) -> None:
        case = _run_case(
            "passive",
            data={"status": "draft", "answer_key": PRIVATE_SENTINEL, "title": "synthetic"},
        )
        self.assertIn(PRIVATE_SENTINEL, repr(case["harness"].data))
        self.assertNotIn(PRIVATE_SENTINEL, repr(_event_mapping(case)))

    def test_11_private_return_never_enters_event(self) -> None:
        case = _run_case(
            "passive",
            data={"status": "draft", "private_definition": PRIVATE_SENTINEL},
        )
        self.assertIn(PRIVATE_SENTINEL, repr(case["result"]))
        self.assertNotIn(PRIVATE_SENTINEL, repr(_event_mapping(case)))

    def test_12_private_exception_never_enters_event_or_logs(self) -> None:
        expected = RuntimeError(PRIVATE_SENTINEL)
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        logger = logging.getLogger()
        previous_level = logger.level
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        try:
            case = _run_case("passive", update_error=expected)
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous_level)
        self.assertIs(case["error"], expected)
        event = case["collector"].snapshot()[0]
        self.assertNotIn(PRIVATE_SENTINEL, repr(event.to_public_mapping()))
        self.assertNotIn(PRIVATE_SENTINEL, output.getvalue())

    def test_13_event_schema_rejects_extra_fields(self) -> None:
        descriptor = get_operation_descriptor(OperationKind.BLOCK_MUTATE)
        with self.assertRaises(TypeError):
            EditorialObservationEvent(
                schema_version=1,
                operation_kind=OperationKind.BLOCK_MUTATE,
                entrypoint_kind=EntryPointKind.SERVICE,
                writer_category=descriptor.writer_category,
                outcome=OperationOutcome.UNKNOWN,
                duration_bucket=DurationBucket.UNKNOWN,
                protocol_path=ProtocolPath.LEGACY_SERVICE,
                event_kind=EventKind.OPERATION_RESULT_OBSERVED,
                private_payload=PRIVATE_SENTINEL,  # type: ignore[call-arg]
            )

    def test_14_operation_is_in_static_w05_catalog(self) -> None:
        descriptor = get_operation_descriptor(OperationKind.BLOCK_MUTATE)
        self.assertIs(OPERATION_CATALOG[OperationKind.BLOCK_MUTATE], descriptor)
        self.assertEqual(descriptor.source_reference, "12C.4 W-05")
        self.assertIn(EntryPointKind.SERVICE, descriptor.entrypoints)
        self.assertIs(descriptor.writer_category, WriterCategory.BLOCK_CHANGE)

    def test_15_missing_result_classifier_stays_unknown(self) -> None:
        case = _run_case("passive")
        self.assertEqual(_event_mapping(case)["outcome"], OperationOutcome.UNKNOWN.value)

    def test_16_duration_uses_only_a_closed_bucket(self) -> None:
        case = _run_case("passive", clock=FixedClock(0, 100_000_000))
        event = case["collector"].snapshot()[0]
        self.assertIs(event.duration_bucket, DurationBucket.MS_100_TO_1000)

    def test_17_operation_order_matches_uninstrumented_execution(self) -> None:
        baseline = _run_case("none")
        for mode in ("null", "passive", "broken"):
            self.assertEqual(_run_case(mode)["harness"].trace, baseline["harness"].trace)
        self.assertEqual(
            baseline["harness"].trace,
            ["get_document", "check_status", "now", "oid", "update_one", "audit", "oid", "find_one"],
        )

    def test_18_no_mode_retries_writer_after_return(self) -> None:
        for mode in ("none", "null", "passive", "broken"):
            case = _run_case(mode)
            self.assertEqual(case["harness"].trace.count("update_one"), 1)
            self.assertEqual(case["harness"].trace.count("find_one"), 1)

    def test_19_no_network_entrypoint_is_used(self) -> None:
        with patch.object(socket, "create_connection", side_effect=AssertionError("network attempted")), patch.object(
            urllib.request, "urlopen", side_effect=AssertionError("network attempted")
        ):
            case = _run_case("passive")
        self.assertIsNone(case["error"])

    def test_20_application_entrypoints_do_not_import_harness_or_observer(self) -> None:
        root = Path(__file__).resolve().parents[2]
        entrypoints = [
            root / "backend" / "server.py",
            root / "backend" / "routes_content.py",
            root / "backend" / "services" / "blocks.py",
        ]
        for path in entrypoints:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("editorial_observability_harness", text)
            self.assertNotIn("curriculum_contract.editorial_observability", text)

    def test_21_writer_source_is_not_modified_by_harness_execution(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "services" / "blocks.py").read_bytes()
        _run_case("passive")
        self.assertEqual(
            (Path(__file__).resolve().parents[1] / "services" / "blocks.py").read_bytes(), source
        )

    def test_22_async_cancellation_is_propagated_and_observed(self) -> None:
        harness = load_real_update_block()
        harness.collection.update_started = asyncio.Event()
        harness.collection.update_release = asyncio.Event()
        collector = InMemoryEventCollector(capacity=4)
        instrumentor = PassiveEditorialInstrumentor(collector, clock=FixedClock(1, 2))

        async def scenario() -> None:
            started = harness.collection.update_started
            assert started is not None
            task = asyncio.create_task(instrumentor.observe_async(default_context(), harness.invoke))
            await started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task

        asyncio.run(scenario())
        self.assertEqual(harness.trace.count("update_one"), 1)
        self.assertEqual(len(collector.snapshot()), 1)
        self.assertIs(collector.snapshot()[0].outcome, OperationOutcome.CANCELLED)

    def test_23_fake_storage_failure_propagates_without_mutation(self) -> None:
        expected = OSError("synthetic storage failure")
        case = _run_case("passive", update_error=expected)
        self.assertIs(case["error"], expected)
        self.assertEqual(case["harness"].collection.document["title"], "synthetic title")
        self.assertIs(case["collector"].snapshot()[0].outcome, OperationOutcome.FAILED)

    def test_24_repeated_clean_runs_are_reproducible(self) -> None:
        first = _run_case("passive")
        second = _run_case("passive")
        self.assertEqual(_profile(first), _profile(second))
        self.assertEqual(_event_mapping(first), _event_mapping(second))

    def test_25_audit_failure_after_write_remains_partial_and_transparent(self) -> None:
        expected = RuntimeError("synthetic audit failure")
        baseline = _run_case("none", audit_error=expected)
        observed_error = RuntimeError("synthetic audit failure")
        observed = _run_case("passive", audit_error=observed_error)
        self.assertIs(baseline["error"], expected)
        self.assertIs(observed["error"], observed_error)
        self.assertEqual(_profile(observed), _profile(baseline))
        self.assertEqual(observed["harness"].trace.count("update_one"), 1)
        self.assertEqual(observed["harness"].collection.document["title"], "synthetic title")
        self.assertEqual(_event_mapping(observed)["outcome"], OperationOutcome.FAILED.value)

    def test_26_explicit_classifier_is_used_without_serializing_result(self) -> None:
        case = _run_case(
            "passive",
            result_classifier=lambda result: (
                OperationOutcome.SUCCESS
                if isinstance(result, dict) and result.get("_id") == "synthetic-block-001"
                else OperationOutcome.UNKNOWN
            ),
        )
        self.assertEqual(_event_mapping(case)["outcome"], OperationOutcome.SUCCESS.value)

    def test_27_explicit_validation_classifier_can_mark_rejection(self) -> None:
        case = _run_case(
            "passive",
            data={"status": "invalid-synthetic-status"},
            exception_classifier=lambda error: (
                OperationOutcome.REJECTED
                if isinstance(error, SyntheticHTTPException)
                else OperationOutcome.FAILED
            ),
        )
        self.assertIsInstance(case["error"], SyntheticHTTPException)
        self.assertEqual(_event_mapping(case)["outcome"], OperationOutcome.REJECTED.value)

    def test_28_failure_of_audit_does_not_trigger_rollback_or_retry(self) -> None:
        case = _run_case("passive", audit_error=RuntimeError("synthetic audit failure"))
        self.assertIsNotNone(case["error"])
        self.assertEqual(case["harness"].trace.count("update_one"), 1)
        self.assertEqual(case["harness"].trace.count("audit"), 1)
        self.assertEqual(case["harness"].trace.count("find_one"), 0)
        self.assertIn("updated_at", case["harness"].collection.document)

    def test_29_clock_failure_does_not_change_writer_result(self) -> None:
        baseline = _run_case("none")
        observed = _run_case(
            "passive",
            clock=FixedClock(RuntimeError("synthetic clock failure"), RuntimeError("again")),
        )
        self.assertEqual(_profile(observed), _profile(baseline))
        self.assertEqual(_event_mapping(observed)["duration_bucket"], DurationBucket.UNKNOWN.value)

    def test_30_writer_owned_input_mutation_is_equal_across_modes(self) -> None:
        original = {"status": "draft", "private_definition": PRIVATE_SENTINEL}
        cases = [_run_case(mode, data=original) for mode in ("none", "null", "passive", "broken")]
        for case in cases[1:]:
            self.assertEqual(case["harness"].data, cases[0]["harness"].data)
        self.assertEqual(original, {"status": "draft", "private_definition": PRIVATE_SENTINEL})


if __name__ == "__main__":
    unittest.main()
