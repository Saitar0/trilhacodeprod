"""Run the real Beta 6 HTTP suite and browser journey in one owned database."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from test_support.beta6_1_docker_harness import Beta61DockerHarness


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    repo_root = backend_root.parent
    with Beta61DockerHarness(repo_root) as harness:
        evidence = harness.validate_gate()
        print("ISOLATION_GATE " + json.dumps(evidence, sort_keys=True))

        http_result = harness.run_pytest(["tests/test_beta6_learning_journey.py"])
        if http_result.stdout:
            print(http_result.stdout, end="")
        if http_result.stderr:
            print(http_result.stderr, file=sys.stderr, end="")
        if http_result.returncode != 0:
            return http_result.returncode

        harness.start_local_app()
        fixture = harness.seed_learning_fixture()
        print("SYNTHETIC_FIXTURE " + json.dumps(fixture, sort_keys=True))
        browser_result = harness.run_playwright("e2e/beta6-1-learning-journey.spec.ts", fixture)
        if browser_result.stdout:
            print(browser_result.stdout, end="")
        if browser_result.stderr:
            print(browser_result.stderr, file=sys.stderr, end="")
        if browser_result.returncode != 0:
            return browser_result.returncode

        for result in harness.run_frontend_quality():
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="")
            if result.returncode != 0:
                return result.returncode
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
