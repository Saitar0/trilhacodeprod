"""Isolated tests for process deadlines and ownership-checked cleanup."""

from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

OPS = Path(__file__).resolve().parent
TEMPLATE_SCRIPTS = OPS / "executor-template" / "scripts"
sys.path.insert(0, str(OPS))
sys.path.insert(0, str(TEMPLATE_SCRIPTS))

import cleanup_compose
import cleanup_executor
from runtime_supervision import run_supervised

RUN_ID = "a" * 32
PROJECT = f"editorial-poc-{RUN_ID}"
COMPOSE = OPS / "compose.yaml"


def _python(script: str) -> list[str]:
    return [sys.executable, "-u", "-c", textwrap.dedent(script)]


def _supervise(script: str, *, timeout: float = 0.35, idle: float | None = None, diagnostic=False):
    output: list[str] = []
    result = run_supervised(
        _python(script),
        label="synthetic-test",
        env=dict(os.environ),
        cwd=str(OPS),
        timeout_seconds=timeout,
        inactivity_timeout_seconds=idle,
        request_diagnostics=diagnostic,
        output=output.append,
    )
    return result, output


class ProcessSupervisorTests(unittest.TestCase):
    def test_never_finishing_test_is_terminated_with_failure(self):
        result, output = _supervise("import time\nwhile True: time.sleep(0.02)")
        self.assertTrue(result.timed_out)
        self.assertEqual(result.returncode, 124)
        self.assertTrue(any("hard timeout" in line for line in output))

    def test_indefinite_async_event_wait_is_terminated(self):
        result, output = _supervise(
            "import asyncio\nasyncio.run(asyncio.Event().wait())"
        )
        self.assertTrue(result.timed_out)
        self.assertTrue(any("active_test=synthetic-test" in line for line in output))

    def test_thread_deadlock_is_terminated(self):
        result, _ = _supervise(
            "import threading\n"
            "lock = threading.Lock()\n"
            "lock.acquire()\n"
            "lock.acquire()"
        )
        self.assertTrue(result.timed_out)

    def test_stalled_subprocess_is_terminated(self):
        # The supervised child is itself an OS subprocess; no MongoDB or Docker is used.
        result, _ = _supervise("import time\ntime.sleep(20)")
        self.assertTrue(result.timed_out)

    def test_setup_and_teardown_stall_reports_last_lifecycle_phase(self):
        for phase in ("setup", "teardown"):
            with self.subTest(phase=phase):
                result, output = _supervise(
                    f"print('test_lifecycle phase={phase} start', flush=True)\n"
                    "import time\ntime.sleep(20)"
                )
                self.assertTrue(result.timed_out)
                self.assertTrue(any(f"phase={phase} start" in line for line in output))

    def test_no_progress_watchdog_reports_idle_before_hard_deadline(self):
        result, output = _supervise(
            "import time\nprint('ready', flush=True)\ntime.sleep(20)",
            timeout=0.45,
            idle=0.12,
        )
        self.assertTrue(result.timed_out)
        self.assertTrue(any("no progress" in line for line in output))

    @unittest.skipUnless(hasattr(signal, "SIGUSR1"), "SIGUSR1 disponível apenas em POSIX")
    def test_watchdog_signal_requests_child_diagnostic(self):
        result, output = _supervise(
            "import signal, sys, time\n"
            "def report(_sig, _frame):\n"
            " print('SANITIZED_STACK_FRAME', flush=True)\n"
            " sys.exit(7)\n"
            "signal.signal(signal.SIGUSR1, report)\n"
            "print('ready', flush=True)\n"
            "while True: time.sleep(0.02)",
            timeout=1,
            idle=0.12,
            diagnostic=True,
        )
        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 7)
        self.assertTrue(any("SANITIZED_STACK_FRAME" in line for line in output))

    def test_child_output_redacts_environment_secrets_and_authenticated_uris(self):
        output: list[str] = []
        secret = "temporary-supersecret"
        result = run_supervised(
            _python(
                "print('password=temporary-supersecret', flush=True)\n"
                "print('mongodb://user:anothersecret@mongo/db', flush=True)"
            ),
            label="redaction-test",
            env={**os.environ, "EDITORIAL_POC_TEST_PASSWORD": secret},
            cwd=str(OPS),
            timeout_seconds=2,
            output=output.append,
        )
        joined = "\n".join(output)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(secret, joined)
        self.assertNotIn("anothersecret", joined)
        self.assertIn("[REDACTED]", joined)


class FakeDocker:
    def __init__(self, *, resources=True, down_code=0, inspect_labels=None):
        self.active = resources
        self.down_code = down_code
        self.inspect_labels_override = inspect_labels
        self.calls: list[list[str]] = []

    def __call__(self, command, **kwargs):
        self.calls.append(list(command))
        args = command[1:]
        output = ""
        code = 0
        if args[:2] == ["ps", "--all"]:
            output = "container-1\n" if self.active else ""
        elif args[:2] == ["network", "ls"]:
            output = "network-1\n" if self.active else ""
        elif args[:2] == ["volume", "ls"]:
            output = "volume-1\n" if self.active else ""
        elif len(args) >= 3 and args[1] == "inspect":
            kind = args[0]
            labels = self.inspect_labels_override or {
                "com.docker.compose.project": PROJECT,
                cleanup_compose.RUN_LABEL: RUN_ID,
            }
            if kind == "container":
                document = {"Config": {"Labels": labels}}
            else:
                document = {"Labels": labels}
            output = json.dumps([document])
        elif args and args[0] == "compose":
            code = self.down_code
            if code == 0:
                self.active = False
        return subprocess.CompletedProcess(command, code, stdout=output, stderr="")


class CleanupTests(unittest.TestCase):
    def run_cleanup(self, runner, *, project=PROJECT, run_id=RUN_ID, **kwargs):
        return cleanup_compose.cleanup_project(
            project,
            run_id,
            COMPOSE,
            runner=runner,
            verify_context=lambda: ("local", "test-engine"),
            **kwargs,
        )

    def test_daemon_unavailable_fails_closed(self):
        def unavailable(*_args, **_kwargs):
            raise FileNotFoundError("docker not available")

        with self.assertRaises(cleanup_compose.CleanupFailure):
            self.run_cleanup(unavailable)

    def test_divergent_labels_fail_closed_before_compose_down(self):
        fake = FakeDocker(inspect_labels={"com.docker.compose.project": PROJECT})
        with self.assertRaisesRegex(cleanup_compose.CleanupFailure, "limpeza recusada"):
            self.run_cleanup(fake)
        self.assertFalse(any(call[1] == "compose" for call in fake.calls))

    def test_malformed_inspect_response_fails_closed_before_compose_down(self):
        class MalformedDocker(FakeDocker):
            def __call__(self, command, **kwargs):
                result = super().__call__(command, **kwargs)
                if len(command) >= 3 and command[2] == "inspect":
                    return subprocess.CompletedProcess(
                        command, 0, stdout="[null]", stderr=""
                    )
                return result

        fake = MalformedDocker()
        with self.assertRaises(cleanup_compose.CleanupFailure):
            self.run_cleanup(fake)
        self.assertFalse(any(call[1] == "compose" for call in fake.calls))

    def test_wrong_project_is_rejected_without_docker_commands(self):
        calls = []
        with self.assertRaises(cleanup_compose.CleanupFailure):
            self.run_cleanup(
                lambda *args, **kwargs: calls.append(args),
                project=f"editorial-poc-{'b' * 32}",
            )
        self.assertEqual(calls, [])

    def test_cleanup_command_error_is_sanitized_and_nonzero(self):
        class FailingDocker(FakeDocker):
            def __call__(self, command, **kwargs):
                if command[1:2] == ["compose"]:
                    self.calls.append(list(command))
                    return subprocess.CompletedProcess(
                        command, 1, stdout="", stderr="password=ephemeral-secret"
                    )
                return super().__call__(command, **kwargs)

        fake = FailingDocker()
        with self.assertRaises(cleanup_compose.CleanupFailure) as raised:
            self.run_cleanup(fake, environment={"EDITORIAL_POC_ROOT_PASSWORD": "ephemeral-secret"})
        self.assertEqual(raised.exception.exit_code, 3)
        self.assertNotIn("ephemeral-secret", str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))

    def test_command_timeout_returns_timeout_failure(self):
        def timed_out(command, **_kwargs):
            raise subprocess.TimeoutExpired(command, 10, stderr="token=temporary")

        with self.assertRaises(cleanup_compose.CleanupFailure) as raised:
            self.run_cleanup(timed_out)
        self.assertEqual(raised.exception.exit_code, 124)
        self.assertNotIn("temporary", str(raised.exception))

    def test_signal_interrupt_is_reported_without_claiming_cleanup_success(self):
        def interrupted(*_args, **_kwargs):
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            self.run_cleanup(interrupted)
        with patch.dict(
            os.environ,
            {
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
            },
            clear=True,
        ), contextlib.redirect_stderr(io.StringIO()) as captured:
            code = cleanup_compose.main(
                ["--compose-file", str(COMPOSE)],
                runner=interrupted,
                verify_context=lambda: ("local", "test-engine"),
            )
        self.assertEqual(code, 130)
        self.assertIn("interrompida", captured.getvalue())

    def test_repeated_cleanup_is_idempotent_after_resources_are_absent(self):
        fake = FakeDocker(resources=False)
        self.run_cleanup(fake)
        self.run_cleanup(fake)
        self.assertFalse(any(call[1] == "compose" for call in fake.calls))

    def test_absent_resources_are_success_only_after_runtime_identity_check(self):
        fake = FakeDocker(resources=False)
        self.run_cleanup(fake)
        self.assertGreater(len(fake.calls), 0)

    def test_executor_preserves_directories_and_redacts_captured_failure(self):
        with tempfile.TemporaryDirectory(prefix="editorial-cleanup-") as temp:
            root = Path(temp)
            bundle = root / "editorial-generations-bundle"
            compose = bundle / "ops" / "editorial-generations" / "compose.yaml"
            cleanup = compose.with_name("cleanup_compose.py")
            compose.parent.mkdir(parents=True)
            compose.write_text("synthetic", encoding="utf-8")
            cleanup.write_text(
                "import sys\n"
                "sys.stderr.write('cleanup failed password=temporary-secret')\n"
                "sys.exit(3)\n",
                encoding="utf-8",
            )
            env = {
                "RUNNER_TEMP": str(root),
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "EDITORIAL_POC_CLEANUP_NEEDED": "true",
                "EDITORIAL_POC_ROOT_PASSWORD": "temporary-secret",
            }
            with patch.dict(os.environ, env, clear=True), contextlib.redirect_stderr(
                io.StringIO()
            ) as captured:
                code = cleanup_executor.main()
            self.assertEqual(code, 3)
            self.assertTrue(bundle.exists())
            self.assertNotIn("temporary-secret", captured.getvalue())
            self.assertIn("[REDACTED]", captured.getvalue())

    def test_executor_timeout_preserves_evidence_and_returns_124(self):
        with tempfile.TemporaryDirectory(prefix="editorial-cleanup-timeout-") as temp:
            root = Path(temp)
            bundle = root / "editorial-generations-bundle"
            compose = bundle / "ops" / "editorial-generations" / "compose.yaml"
            cleanup = compose.with_name("cleanup_compose.py")
            compose.parent.mkdir(parents=True)
            compose.write_text("synthetic", encoding="utf-8")
            cleanup.write_text("import time\ntime.sleep(20)\n", encoding="utf-8")
            env = {
                "RUNNER_TEMP": str(root),
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "EDITORIAL_POC_CLEANUP_NEEDED": "true",
            }
            with patch.dict(os.environ, env, clear=True), patch.object(
                cleanup_executor, "COMPOSE_CLEANUP_TIMEOUT_SECONDS", 0.2
            ), contextlib.redirect_stderr(io.StringIO()) as captured:
                code = cleanup_executor.main()
            self.assertEqual(code, 124)
            self.assertTrue(bundle.exists())
            self.assertNotIn("hush", captured.getvalue())

    def test_executor_repeated_after_success_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="editorial-cleanup-repeat-") as temp:
            root = Path(temp)
            bundle = root / "editorial-generations-bundle"
            download = root / "editorial-generations-download"
            compose = bundle / "ops" / "editorial-generations" / "compose.yaml"
            cleanup = compose.with_name("cleanup_compose.py")
            compose.parent.mkdir(parents=True)
            compose.write_text("synthetic", encoding="utf-8")
            cleanup.write_text("pass\n", encoding="utf-8")
            env = {
                "RUNNER_TEMP": str(root),
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "EDITORIAL_POC_CLEANUP_NEEDED": "true",
            }
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(cleanup_executor.main(), 0)
                self.assertFalse(bundle.exists())
                self.assertFalse(download.exists())
                os.environ["EDITORIAL_POC_CLEANUP_NEEDED"] = "false"
                self.assertEqual(cleanup_executor.main(), 0)

    def test_executor_signal_interruption_preserves_evidence(self):
        with tempfile.TemporaryDirectory(prefix="editorial-cleanup-signal-") as temp:
            root = Path(temp)
            bundle = root / "editorial-generations-bundle"
            compose = bundle / "ops" / "editorial-generations" / "compose.yaml"
            cleanup = compose.with_name("cleanup_compose.py")
            compose.parent.mkdir(parents=True)
            compose.write_text("synthetic", encoding="utf-8")
            cleanup.write_text("pass\n", encoding="utf-8")
            env = {
                "RUNNER_TEMP": str(root),
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "EDITORIAL_POC_CLEANUP_NEEDED": "true",
            }

            def interrupted(*_args, **_kwargs):
                raise KeyboardInterrupt

            with patch.dict(os.environ, env, clear=True), contextlib.redirect_stderr(io.StringIO()):
                code = cleanup_executor.main(popen_factory=interrupted)
            self.assertEqual(code, 130)
            self.assertTrue(bundle.exists())

    @unittest.skipUnless(os.name == "posix", "SIGTERM de processo é coberto no runner POSIX")
    def test_executor_sigterm_stops_child_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory(prefix="editorial-cleanup-sigterm-") as temp:
            root = Path(temp)
            bundle = root / "editorial-generations-bundle"
            compose = bundle / "ops" / "editorial-generations" / "compose.yaml"
            cleanup = compose.with_name("cleanup_compose.py")
            compose.parent.mkdir(parents=True)
            compose.write_text("synthetic", encoding="utf-8")
            cleanup.write_text("pass\\n", encoding="utf-8")
            env = {
                "RUNNER_TEMP": str(root),
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "EDITORIAL_POC_CLEANUP_NEEDED": "true",
                "PYTHONPATH": str(TEMPLATE_SCRIPTS),
            }
            launcher = textwrap.dedent(
                """
                import subprocess, sys, time
                import cleanup_executor

                def start_blocked_child(*_args, **kwargs):
                    process = subprocess.Popen(
                        [sys.executable, "-c", "import time; time.sleep(30)"],
                        **kwargs,
                    )
                    print("CHILD_STARTED", flush=True)
                    return process

                raise SystemExit(cleanup_executor.main(popen_factory=start_blocked_child))
                """
            )
            process = subprocess.Popen(
                [sys.executable, "-u", "-c", launcher],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            assert process.stdout is not None
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            try:
                self.assertTrue(selector.select(timeout=5), "cleanup child did not start")
                self.assertEqual(process.stdout.readline().strip(), "CHILD_STARTED")
                process.send_signal(signal.SIGTERM)
                _stdout, stderr = process.communicate(timeout=5)
            finally:
                selector.close()
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=3)
            self.assertEqual(process.returncode, 128 + signal.SIGTERM, stderr)
            self.assertIn("interrompido", stderr)
            self.assertTrue(bundle.exists())

    @unittest.skipUnless(os.name == "posix", "SIGTERM de processo é coberto no runner POSIX")
    def test_compose_cleanup_sigterm_returns_failure_not_success(self):
        launcher = textwrap.dedent(
            f"""
            import signal, subprocess, sys, time
            from pathlib import Path
            import cleanup_compose

            def blocked(*_args, **_kwargs):
                print("DOCKER_CALL_STARTED", flush=True)
                time.sleep(30)

            raise SystemExit(cleanup_compose.main(
                ["--compose-file", {str(COMPOSE)!r}],
                runner=blocked,
                verify_context=lambda: ("local", "synthetic"),
            ))
            """
        )
        env = dict(os.environ)
        env.update(
            {
                "EDITORIAL_POC_PROJECT": PROJECT,
                "EDITORIAL_POC_RUN_ID": RUN_ID,
                "PYTHONPATH": str(OPS),
            }
        )
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", launcher],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        try:
            self.assertTrue(selector.select(timeout=5), "cleanup command did not start")
            self.assertEqual(process.stdout.readline().strip(), "DOCKER_CALL_STARTED")
            process.send_signal(signal.SIGTERM)
            _stdout, stderr = process.communicate(timeout=5)
        finally:
            selector.close()
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
        self.assertEqual(process.returncode, 128 + signal.SIGTERM, stderr)
        self.assertIn("interrompida", stderr)


class StaticRuntimeContractTests(unittest.TestCase):
    @staticmethod
    def workflow_job_and_steps(source: str):
        """Read the job/step fields from this intentionally simple YAML layout."""
        lines = source.splitlines()
        job_timeout = None
        in_target_job = False
        for line in lines:
            if line == "  homologation:":
                in_target_job = True
                continue
            if in_target_job and line.startswith("  ") and not line.startswith("    "):
                break
            if in_target_job and line.startswith("    timeout-minutes:"):
                job_timeout = int(line.split(":", 1)[1].strip())
                break

        steps = []
        current = None
        in_steps = False
        for line in lines:
            if line == "    steps:":
                in_steps = True
                continue
            if not in_steps:
                continue
            if line.startswith("    ") and not line.startswith("      "):
                break
            if line.startswith("      - name:"):
                current = {"name": line.split(":", 1)[1].strip()}
                steps.append(current)
                continue
            if current is not None and line.startswith("        ") and not line.startswith("          "):
                key, separator, value = line.strip().partition(":")
                if separator:
                    current[key] = value.strip()
        if job_timeout is None or not steps:
            raise AssertionError("job/steps do workflow não puderam ser lidos")
        return job_timeout, {step["name"]: step for step in steps}

    def test_all_integrated_cases_are_discovered_and_run_with_individual_deadlines(self):
        repository = OPS.parents[1]
        test_path = repository / "backend" / "integration_tests" / "test_editorial_generations_mongodb.py"
        source = test_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(test_path))
        test_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "EditorialGenerationsMongoDBTests"
        )
        test_names = sorted(
            node.name
            for node in test_class.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
        self.assertEqual(len(test_names), 15)

        runner = (OPS / "run_homologation.py").read_text(encoding="utf-8")
        self.assertIn("INTEGRATION_TEST_TIMEOUT_SECONDS = 60", runner)
        self.assertIn("INTEGRATION_SUITE_TIMEOUT_SECONDS = 20 * 60", runner)
        self.assertIn("for index, test_name in enumerate(names, start=1)", runner)
        self.assertIn("run_supervised(", runner)
        self.assertIn("TEST_CASE start:", runner)
        self.assertIn("TEST_CASE end:", runner)

        run_ci = (OPS / "run-ci.sh").read_text(encoding="utf-8")
        workflow = (
            OPS / "executor-template" / ".github" / "workflows" / "mongodb-homologation.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('COMPOSE_TIMEOUT_SECONDS="32m"', run_ci)
        self.assertIn("timeout-minutes: 37", workflow)
        self.assertIn("timeout-minutes: 5", workflow)

    def test_workflow_reserves_cleanup_and_finalization_with_bounded_preparation(self):
        workflow = (
            OPS / "executor-template" / ".github" / "workflows" / "mongodb-homologation.yml"
        ).read_text(encoding="utf-8")
        job_timeout, steps = self.workflow_job_and_steps(workflow)

        checkout = steps["Check out executor configuration without persisted credentials"]
        setup = steps["Set up Python for package verification"]
        verify = steps["Verify fixed release package and extract"]
        execution = steps["Run verified package against disposable MongoDB 7"]
        cleanup = steps["Clean only this run's resources and temporary package"]
        preparation_budget = sum(
            int(step["timeout-minutes"]) for step in (checkout, setup, verify)
        )
        execution_budget = int(execution["timeout-minutes"])
        cleanup_budget = int(cleanup["timeout-minutes"])
        finalization_reserve = 2

        self.assertEqual(preparation_budget, 5)
        self.assertEqual(execution_budget, 37)
        self.assertEqual(cleanup_budget, 5)
        self.assertEqual(job_timeout, 50)
        self.assertEqual(cleanup.get("if"), "always()")
        self.assertLess(
            preparation_budget + execution_budget + cleanup_budget + finalization_reserve,
            job_timeout,
        )

        compose = (OPS / "run-ci.sh").read_text(encoding="utf-8")
        self.assertIn('COMPOSE_TIMEOUT_SECONDS="32m"', compose)
        compose_hard_limit = 32 * 60 + 20 + 180
        self.assertLess(compose_hard_limit, execution_budget * 60)
        self.assertEqual(execution_budget * 60 - compose_hard_limit, 100)

        external_cleanup = (
            OPS / "executor-template" / "scripts" / "cleanup_executor.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(external_cleanup)
        timeout_assignment = next(
            node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "COMPOSE_CLEANUP_TIMEOUT_SECONDS"
                for target in node.targets
            )
        )
        external_cleanup_seconds = ast.literal_eval(timeout_assignment)
        self.assertEqual(external_cleanup_seconds, 240)
        self.assertLess(external_cleanup_seconds, cleanup_budget * 60)

    def test_runtime_diagnostics_are_shipped_in_the_disposable_image(self):
        repository = OPS.parents[1]
        dockerfile = (OPS / "Dockerfile").read_text(encoding="utf-8")
        dockerignore = (OPS / "Dockerfile.dockerignore").read_text(encoding="utf-8")
        for relative in (
            "backend/integration_tests/harness_diagnostics.py",
            "ops/editorial-generations/runtime_supervision.py",
        ):
            self.assertIn(relative, dockerfile)
            self.assertIn(f"!{relative}", dockerignore)
            self.assertTrue((repository / relative).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
