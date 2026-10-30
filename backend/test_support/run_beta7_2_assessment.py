"""Run Beta 7.2 assessment checks inside the owned disposable Beta 7.1 runner."""

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
        print("TRILHACODE_BETA7_1_SOURCE_ROOT deve apontar à fonte Beta 4 verificada.", file=sys.stderr)
        return 2

    with Beta71DockerHarness(repo_root) as harness:
        gate = harness.validate_gate()
        print("ISOLATION_GATE " + json.dumps(gate, sort_keys=True))
        source_copy = harness.copy_verified_curriculum_source(Path(source))

        offline = harness._exec(
            ["python", "-m", "pytest", "-c", "pytest.ini",
             "unit_tests/test_beta7_2_assessment_contract.py",
             "unit_tests/test_beta7_2_runtime_isolation.py", "-q"],
            timeout=300,
            environment={
                "TRILHACODE_BETA4_SOURCE_ROOT": source_copy,
                "TRILHACODE_BETA7_CURRICULUM_ROOT": source_copy,
            },
            workdir="/workspace/backend",
        )
        if _show(offline, "Contratos e conclusão offline"):
            return offline.returncode

        python_quality = (
            (["ruff", "check",
              "curriculum_contract/beta7_2_rubric.py",
              "curriculum_contract/beta7_2_assessment.py",
              "curriculum_contract/beta7_2_completion.py",
              "schemas/beta7_2_assessment.py",
              "services/beta7_2_assessment.py",
              "services/beta7_1_preview.py",
              "test_support/beta7_1_docker_harness.py",
              "test_support/beta7_1_preview_server.py",
              "test_support/beta7_1_seed_preview.py",
              "test_support/beta7_2_assessment_router.py",
              "test_support/beta7_2_persistence_validation.py",
              "test_support/run_beta7_2_assessment.py",
              "unit_tests/test_beta7_2_assessment_contract.py",
              "unit_tests/test_beta7_2_runtime_isolation.py"]),
            (["mypy", "--follow-imports=skip", "--ignore-missing-imports",
              "curriculum_contract/beta7_2_rubric.py",
              "curriculum_contract/beta7_2_assessment.py",
              "curriculum_contract/beta7_2_completion.py",
              "schemas/beta7_2_assessment.py",
              "services/beta7_2_assessment.py"]),
            (["python", "-m", "compileall", "-q",
              "curriculum_contract/beta7_2_rubric.py",
              "curriculum_contract/beta7_2_assessment.py",
              "curriculum_contract/beta7_2_completion.py",
              "schemas/beta7_2_assessment.py",
              "services/beta7_2_assessment.py",
              "test_support/beta7_2_assessment_router.py",
              "test_support/beta7_2_persistence_validation.py"]),
        )
        for command in python_quality:
            result = harness._exec(command, timeout=300, workdir="/workspace/backend")
            if _show(result, command[0]):
                return result.returncode

        composition = harness._exec(
            ["python", "-c", "import test_support.beta7_1_preview_server"],
            timeout=45, environment=harness._run_env(), workdir="/workspace/backend",
        )
        if _show(composition, "Composição test-only com rotas Beta 7.2"):
            return composition.returncode

        fixture = harness.seed_real_curriculum(source_copy)
        print("REAL_CURRICULUM_FIXTURE " + json.dumps(fixture, sort_keys=True, ensure_ascii=False))

        persistent = harness.run_beta7_2_persistence_validation(fixture)
        if _show(persistent, "Avaliação persistente com rubrica sintética"):
            return persistent.returncode

        harness.start_local_app(fixture)
        http = harness.run_http_validation(fixture)
        if _show(http, "Regressão HTTP Beta 7.1"):
            return http.returncode

        browser = harness.run_playwright("e2e/beta7-1-real-first-phase.spec.ts", fixture)
        if _show(browser, "Entrega/revisão/reenvio Playwright"):
            return browser.returncode

        race = harness.run_revocation_race(fixture)
        if _show(race, "Regressão persistente revogação versus CAS"):
            return race.returncode

        for result in harness.run_frontend_quality():
            if _show(result, "Qualidade frontend"):
                return result.returncode
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
