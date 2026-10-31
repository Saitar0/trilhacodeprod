"""Run selected Beta 6 API tests inside the owned Beta 6.1 internal network."""

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
        result = harness.run_pytest(["tests/test_beta6_learning_journey.py"])
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
