"""Run offline gates first, then the staging proof in an owned MongoDB 7 container."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

OFFLINE_TESTS = (
    "unit_tests/test_beta_test_database_policy.py",
    "unit_tests/test_beta_protected_content.py",
    "unit_tests/test_beta_project_contract.py",
    "unit_tests/test_beta_staging_contract.py",
    "unit_tests/test_beta_first_phase_converter.py",
)


def _run(command: list[str], *, env: dict[str, str], cwd: Path) -> int:
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    return completed.returncode


def main() -> int:
    from test_support.beta5_mongodb_harness import Beta5MongoHarness

    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    source_root = args.source_root.resolve(strict=True)
    env = os.environ.copy()
    env["BETA5_CURRICULUM_SOURCE"] = str(source_root)
    env["TRILHACODE_BETA4_SOURCE_ROOT"] = str(source_root)
    env.pop("BETA5_TEST_MONGO_URI", None)
    env.pop("BETA5_TEST_MONGO_DATABASE", None)
    env.pop("BETA5_TEST_RUN_ID", None)
    env.pop("BETA5_TEST_OWNER_TOKEN", None)
    env.pop("BETA5_TEST_CONTAINER_ID", None)
    env.pop("BETA5_TEST_NETWORK_ID", None)

    print("Etapa offline: contratos, proveniência e isolamento fail-closed")
    result = _run(
        [sys.executable, "-m", "pytest", *OFFLINE_TESTS, "-q"],
        env=env,
        cwd=BACKEND,
    )
    if result:
        print("Etapa persistente bloqueada: a suíte offline não foi aprovada")
        return result

    print("Provisionando MongoDB 7 descartável Beta 5; URI e credenciais não serão exibidas")
    with Beta5MongoHarness() as harness:
        persistent_env = env | harness.environment()
        result = _run(
            [sys.executable, "-m", "pytest", "integration_tests/test_beta_staging_recovery.py", "-q"],
            env=persistent_env,
            cwd=BACKEND,
        )
        if result:
            return result
        print("Executando verificação histórica de índices somente no mesmo banco descartável")
        result = _run(
            [
                sys.executable, "-m", "pytest", "--beta5-isolated-mongo",
                "tests/test_integrity_concurrency.py::test_preflight_compound_and_text_index_key_matching",
                "tests/test_integrity_concurrency.py::test_live_index_preflight_accepts_existing_indexes",
                "-q",
            ],
            env=persistent_env,
            cwd=BACKEND,
        )
        if result:
            return result
    print("Prova persistente concluída; propriedade do contêiner e do banco verificada antes da remoção")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
