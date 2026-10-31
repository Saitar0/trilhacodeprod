"""Run backend API tests only inside an owned Beta 6 MongoDB harness.

Usage from ``backend/``::

    python -m test_support.run_beta6_pytest tests/test_beta6_learning_journey.py

The harness provisions and validates the isolated database before pytest starts,
and removes only resources whose Docker and database ownership markers still
match this process.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from test_support.beta5_mongodb_harness import DisposableMongoHarness


def main(arguments: list[str] | None = None) -> int:
    selected = arguments if arguments is not None else sys.argv[1:]
    if not selected or any(arg.startswith("-") for arg in selected):
        raise SystemExit("Informe um ou mais arquivos de teste em backend/tests.")
    test_root = Path(__file__).resolve().parents[1] / "tests"
    paths = []
    for value in selected:
        candidate = (test_root / value).resolve()
        if not candidate.is_relative_to(test_root) or not candidate.is_file():
            raise SystemExit("Cada argumento deve identificar um arquivo existente em backend/tests.")
        paths.append(str(candidate.relative_to(test_root.parent)))

    child_env = os.environ.copy()
    # Do not let inherited application defaults compete with the harness-owned target.
    for name in (
        "MONGO_URL", "DB_NAME", "BETA5_TEST_MONGO_URI", "BETA5_TEST_MONGO_DATABASE",
        "BETA5_TEST_RUN_ID", "BETA5_TEST_OWNER_TOKEN", "BETA5_TEST_CONTAINER_ID",
        "BETA5_TEST_NETWORK_ID",
    ):
        child_env.pop(name, None)

    backend_root = test_root.parent
    with DisposableMongoHarness("beta6") as harness:
        child_env.update(harness.environment())
        command = [sys.executable, "-m", "pytest", "--beta6-isolated-mongo", *paths]
        completed = subprocess.run(command, cwd=backend_root, env=child_env, check=False)
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
