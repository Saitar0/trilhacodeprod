"""Run Beta 7 proofs only inside phase-owned internal Docker resources."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from test_support.beta7_docker_harness import Beta7DockerHarness


def _report(result, label: str) -> int:
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        print(f"{label} failed with exit code {result.returncode}", file=sys.stderr)
    return result.returncode


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    repo_root = backend_root.parent
    source = os.environ.get("TRILHACODE_BETA7_SOURCE_ROOT", "").strip()
    if not source:
        print("TRILHACODE_BETA7_SOURCE_ROOT deve apontar para a fonte Beta 4 verificada.", file=sys.stderr)
        return 2

    with Beta7DockerHarness(repo_root) as harness:
        evidence = harness.validate_gate()
        print("ISOLATION_GATE " + json.dumps(evidence, sort_keys=True))
        curriculum_root = harness.copy_verified_curriculum_source(Path(source))

        offline = harness._exec(
            ["python", "-m", "pytest", "-c", "pytest.ini", "unit_tests"],
            timeout=600,
            environment={
                "TRILHACODE_BETA4_SOURCE_ROOT": curriculum_root,
                "TRILHACODE_BETA7_CURRICULUM_ROOT": curriculum_root,
            },
            workdir="/workspace/backend",
        )
        if _report(offline, "Offline and source-backed tests"):
            return offline.returncode

        persistent_tests = [
            "tests/test_auth_sessions.py",
            "tests/test_auth_role_refresh.py",
            "tests/test_beta6_learning_journey.py",
            "tests/test_beta7_review_concurrency.py",
            "tests/test_beta7_first_phase_http.py",
            "tests/test_progress_reliability.py",
            "tests/test_activity_attempts.py",
        ]
        persistent = harness.run_pytest(persistent_tests, curriculum_root=curriculum_root)
        if _report(persistent, "HTTP and persistent integration tests"):
            return persistent.returncode

        harness.start_local_app()
        fixture = harness.seed_multiunit_fixture()
        print("SYNTHETIC_MULTIUNIT_FIXTURE " + json.dumps(fixture, sort_keys=True))
        browser = harness.run_playwright("e2e/beta7-multiunit-learning.spec.ts", fixture)
        if _report(browser, "Browser multiunit journey"):
            return browser.returncode

        for result in harness.run_frontend_quality():
            if _report(result, "Frontend quality"):
                return result.returncode
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
