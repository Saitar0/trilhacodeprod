"""Bounded subprocess supervision for disposable editorial-generation tests."""

from __future__ import annotations

import os
import queue
import re
import signal
import subprocess
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

MONGO_URI_RE = re.compile(r"mongodb(?:\+srv)?://[^\s/@:]+:[^\s/@]+@", re.IGNORECASE)
PASSWORD_RE = re.compile(r"(?i)(password|passwd|pwd|token|secret)=([^&\s]+)")
MAX_LOG_LINE = 4000
DIAGNOSTIC_GRACE_SECONDS = 2.0
TERMINATE_GRACE_SECONDS = 2.0
KILL_GRACE_SECONDS = 2.0


@dataclass(frozen=True)
class SupervisedResult:
    returncode: int
    timed_out: bool
    duration_seconds: float
    last_progress_seconds_ago: float


def sanitize_output(value: str, secret_values: Sequence[str] = ()) -> str:
    """Redact known credentials and common credential-bearing URI forms."""
    text = value
    for secret in sorted((item for item in secret_values if item), key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    text = MONGO_URI_RE.sub("mongodb://[REDACTED]@", text)
    text = PASSWORD_RE.sub(r"\1=[REDACTED]", text)
    if len(text) > MAX_LOG_LINE:
        text = text[:MAX_LOG_LINE] + " [TRUNCATED]"
    return text.rstrip("\r\n")


def _emit(output: Callable[[str], None], line: str, secrets: Sequence[str]) -> None:
    cleaned = sanitize_output(line, secrets)
    if cleaned:
        output(cleaned)


def _signal_process(process: subprocess.Popen[str], sig: int) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, sig)
        elif sig == getattr(signal, "SIGTERM", None):
            if process.poll() is None:
                process.terminate()
        else:
            if process.poll() is None:
                process.kill()
    except (ProcessLookupError, OSError):
        pass


def _terminate_process(
    process: subprocess.Popen[str],
    *,
    request_diagnostics: bool,
    output: Callable[[str], None],
    label: str,
    diagnostic_grace: float,
    terminate_grace: float,
    kill_grace: float,
) -> None:
    if process.poll() is None and request_diagnostics and hasattr(signal, "SIGUSR1"):
        output(f"WATCHDOG stack request: {label}")
        try:
            process.send_signal(signal.SIGUSR1)
            process.wait(timeout=diagnostic_grace)
            return
        except (subprocess.TimeoutExpired, OSError):
            pass
    _signal_process(process, signal.SIGTERM)
    if process.poll() is None:
        try:
            process.wait(timeout=terminate_grace)
            return
        except subprocess.TimeoutExpired:
            pass
    _signal_process(process, signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM)
    if process.poll() is None:
        try:
            process.wait(timeout=kill_grace)
        except subprocess.TimeoutExpired:
            output(f"WATCHDOG não conseguiu confirmar encerramento: {label}")


def run_bounded_capture(
    command: Sequence[str],
    *,
    check: bool = False,
    capture_output: bool = True,
    text: bool = True,
    timeout: float,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run one bounded helper command and terminate its process group on signal."""
    if not capture_output or timeout <= 0:
        raise ValueError("captura e timeout positivo são obrigatórios")
    kwargs: dict[str, object] = {
        "cwd": cwd,
        "env": dict(env) if env is not None else None,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": text,
    }
    if os.name == "posix":
        kwargs["start_new_session"] = True
    elif os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    process = subprocess.Popen(list(command), **kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _signal_process(process, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=TERMINATE_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            _signal_process(
                process,
                signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM,
            )
            try:
                stdout, stderr = process.communicate(timeout=KILL_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
        raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr) from None
    except KeyboardInterrupt:
        _signal_process(process, signal.SIGTERM)
        try:
            process.communicate(timeout=TERMINATE_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            _signal_process(
                process,
                signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM,
            )
            try:
                process.communicate(timeout=KILL_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                pass
        raise
    except BaseException:
        _signal_process(process, signal.SIGTERM)
        try:
            process.communicate(timeout=TERMINATE_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            _signal_process(
                process,
                signal.SIGKILL if hasattr(signal, "SIGKILL") else signal.SIGTERM,
            )
            try:
                process.communicate(timeout=KILL_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                pass
        raise
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check and result.returncode:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def run_supervised(
    command: Sequence[str],
    *,
    label: str,
    env: Mapping[str, str],
    cwd: str,
    timeout_seconds: float,
    inactivity_timeout_seconds: float | None = None,
    request_diagnostics: bool = False,
    output: Callable[[str], None] = print,
    monotonic: Callable[[], float] = time.monotonic,
) -> SupervisedResult:
    """Stream sanitized child output and enforce both idle and hard deadlines.

    On POSIX the child receives its own process group so a timed-out test and
    any subprocesses it created can be terminated without touching neighbors.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds deve ser positivo")
    if inactivity_timeout_seconds is not None and inactivity_timeout_seconds <= 0:
        raise ValueError("inactivity_timeout_seconds deve ser positivo")

    secret_values = tuple(
        value
        for key, value in env.items()
        if any(part in key.upper() for part in ("PASSWORD", "TOKEN", "SECRET", "URI"))
        and value
    )
    started = monotonic()
    deadline = started + timeout_seconds
    last_output = started
    idle_reported = False
    events: queue.Queue[str | None] = queue.Queue()
    kwargs: dict[str, object] = {
        "cwd": cwd,
        "env": dict(env),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "bufsize": 1,
    }
    if os.name == "posix":
        kwargs["start_new_session"] = True
    elif os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    process = subprocess.Popen(list(command), **kwargs)
    process_group = process.pid if os.name == "posix" else "unavailable"
    output(
        f"SUPERVISOR start: {label}; pid={process.pid}; group={process_group}; "
        f"deadline={timeout_seconds:.1f}s"
    )
    assert process.stdout is not None

    def pump_output() -> None:
        try:
            for line in process.stdout:
                events.put(line)
        finally:
            events.put(None)

    reader = threading.Thread(target=pump_output, name="harness-output-reader", daemon=True)
    reader.start()
    timed_out = False
    eof = False
    try:
        while process.poll() is None or not eof:
            now = monotonic()
            remaining = deadline - now
            if remaining <= 0:
                timed_out = True
                output(f"SUPERVISOR hard timeout: {label}; active_test={label}; pipe_open={not eof}")
                _terminate_process(
                    process,
                    request_diagnostics=request_diagnostics,
                    output=output,
                    label=label,
                    diagnostic_grace=DIAGNOSTIC_GRACE_SECONDS,
                    terminate_grace=TERMINATE_GRACE_SECONDS,
                    kill_grace=KILL_GRACE_SECONDS,
                )
                break

            if (
                process.poll() is None
                and inactivity_timeout_seconds is not None
                and not idle_reported
                and now - last_output >= inactivity_timeout_seconds
            ):
                idle_reported = True
                output(
                    f"SUPERVISOR no progress: {label}; "
                    f"idle={now - last_output:.1f}s; hard_deadline_in={max(0, remaining):.1f}s"
                )
                if request_diagnostics and hasattr(signal, "SIGUSR1"):
                    try:
                        process.send_signal(signal.SIGUSR1)
                    except OSError:
                        pass

            wait_for = min(0.2, max(0.01, remaining)) if process.poll() is None else 0.05
            try:
                item = events.get(timeout=wait_for)
            except queue.Empty:
                continue
            if item is None:
                eof = True
            else:
                last_output = monotonic()
                _emit(output, item, secret_values)
    except KeyboardInterrupt:
        output(f"SUPERVISOR interrupted; terminating only {label}")
        _terminate_process(
            process,
            request_diagnostics=request_diagnostics,
            output=output,
            label=label,
            diagnostic_grace=0,
            terminate_grace=TERMINATE_GRACE_SECONDS,
            kill_grace=KILL_GRACE_SECONDS,
        )
        raise
    finally:
        if process.poll() is None:
            _terminate_process(
                process,
                request_diagnostics=False,
                output=output,
                label=label,
                diagnostic_grace=0,
                terminate_grace=TERMINATE_GRACE_SECONDS,
                kill_grace=KILL_GRACE_SECONDS,
            )
        reader.join(timeout=1)
        if process.stdout is not None:
            process.stdout.close()

    duration = max(0.0, monotonic() - started)
    return SupervisedResult(
        returncode=124 if timed_out else int(process.returncode or 0),
        timed_out=timed_out,
        duration_seconds=duration,
        last_progress_seconds_ago=max(0.0, monotonic() - last_output),
    )
