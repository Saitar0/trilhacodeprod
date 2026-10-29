"""Execute the Beta 7.1 real-curriculum proof in owned disposable Docker resources."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from test_support.beta7_1_docker_harness import Beta71DockerHarness


def _show(result, label: str) -> int:
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        print(f"{label}: falhou com código {result.returncode}", file=sys.stderr)
    return result.returncode


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source = os.environ.get("TRILHACODE_BETA7_1_SOURCE_ROOT", "").strip()
    if not source:
        print("TRILHACODE_BETA7_1_SOURCE_ROOT deve apontar à fonte Beta 4 aprovada.", file=sys.stderr)
        return 2

    with Beta71DockerHarness(repo_root) as harness:
        evidence = harness.validate_gate()
        print("ISOLATION_GATE " + json.dumps(evidence, sort_keys=True))
        source_copy = harness.copy_verified_curriculum_source(Path(source))

        offline = harness._exec(
            ["python", "-m", "pytest", "-c", "pytest.ini", "unit_tests/test_beta7_1_preview_contract.py", "-q"],
            timeout=300,
            environment={
                "TRILHACODE_BETA4_SOURCE_ROOT": source_copy,
                "TRILHACODE_BETA7_CURRICULUM_ROOT": source_copy,
            },
            workdir="/workspace/backend",
        )
        if _show(offline, "Contratos offline"):
            return offline.returncode

        composition = harness._exec(
            ["python", "-c", "import test_support.beta7_1_preview_server"],
            timeout=45,
            environment=harness._run_env(),
            workdir="/workspace/backend",
        )
        if _show(composition, "Composição isolada da API"):
            return composition.returncode

        # This script gates its own database connection and refuses any data
        # other than the ownership marker before migrations or seed operations.
        fixture = harness.seed_real_curriculum(source_copy)
        print("REAL_CURRICULUM_FIXTURE " + json.dumps(fixture, sort_keys=True, ensure_ascii=False))
        harness.start_local_app(fixture)

        http_result = harness.run_http_validation(fixture)
        if _show(http_result, "Validação HTTP integrada"):
            return http_result.returncode

        browser = harness.run_playwright("e2e/beta7-1-real-first-phase.spec.ts", fixture)
        if _show(browser, "Jornada Playwright das dez unidades"):
            return browser.returncode

        race = harness.run_revocation_race(fixture)
        if _show(race, "Revogação versus CAS persistente"):
            return race.returncode

        for result in harness.run_frontend_quality():
            if _show(result, "Qualidade frontend"):
                return result.returncode

        return 0


if __name__ == "__main__":
    raise SystemExit(main())
