"""Sanitized lifecycle and async-task diagnostics for isolated Mongo tests."""

from __future__ import annotations

import asyncio
import faulthandler
import json
import os
import signal
import sys
import time
from types import FrameType

_ACTIVE_LOOP: asyncio.AbstractEventLoop | None = None
_ACTIVE_TEST = "unknown"


def _run_id() -> str:
    value = os.environ.get("EDITORIAL_POC_RUN_ID", "")
    return value[:8] if len(value) == 32 and all(ch in "0123456789abcdef" for ch in value) else "unknown"


def _deadline_remaining() -> float | None:
    raw = os.environ.get("EDITORIAL_POC_TEST_DEADLINE_EPOCH", "")
    try:
        return max(0.0, float(raw) - time.time()) if raw else None
    except ValueError:
        return None


def emit_lifecycle(phase: str, state: str, test_id: str, *, duration: float | None = None) -> None:
    payload: dict[str, object] = {
        "event": "test_lifecycle",
        "run": _run_id(),
        "test": test_id,
        "phase": phase,
        "state": state,
        "deadline_remaining_seconds": _deadline_remaining(),
    }
    if duration is not None:
        payload["duration_seconds"] = round(duration, 3)
    print(json.dumps(payload, separators=(",", ":")), file=sys.stderr, flush=True)


def _dump_pending_tasks(loop: asyncio.AbstractEventLoop, test_id: str) -> None:
    print(
        json.dumps(
            {"event": "watchdog_async_tasks", "run": _run_id(), "test": test_id},
            separators=(",", ":"),
        ),
        file=sys.stderr,
        flush=True,
    )
    try:
        tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    except RuntimeError:
        return
    for index, task in enumerate(tasks, start=1):
        coroutine = task.get_coro()
        code = getattr(coroutine, "cr_code", None)
        name = getattr(code, "co_name", type(coroutine).__name__)
        print(f"WATCHDOG task[{index}] coroutine={name}", file=sys.stderr, flush=True)
        for frame in task.get_stack(limit=8):
            print(
                f"WATCHDOG frame {os.path.basename(frame.f_code.co_filename)}:"
                f"{frame.f_lineno} in {frame.f_code.co_name}",
                file=sys.stderr,
                flush=True,
            )


def install_signal_diagnostics(
    loop: asyncio.AbstractEventLoop | None,
    test_id: str,
) -> None:
    """On POSIX SIGUSR1, dump thread stacks and coroutine frame names only."""
    global _ACTIVE_LOOP, _ACTIVE_TEST
    _ACTIVE_LOOP = loop
    _ACTIVE_TEST = test_id
    if not hasattr(signal, "SIGUSR1") or threading_is_not_main():
        return

    def dump(_signum: int, _frame: FrameType | None) -> None:
        print(
            f"WATCHDOG diagnostic signal; run={_run_id()}; test={_ACTIVE_TEST}",
            file=sys.stderr,
            flush=True,
        )
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        active_loop = _ACTIVE_LOOP
        if active_loop is not None and active_loop.is_running():
            active_loop.call_soon_threadsafe(_dump_pending_tasks, active_loop, _ACTIVE_TEST)

    signal.signal(signal.SIGUSR1, dump)


def threading_is_not_main() -> bool:
    # Keep signal registration safe without importing or exposing thread state.
    import threading

    return threading.current_thread() is not threading.main_thread()
