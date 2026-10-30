"""Beta 8.2 persistent regressions run only inside its owned Docker harness."""

from __future__ import annotations

import asyncio

from integration_tests.beta8_1_runtime_security import run_beta8_1_runtime_proof
from integration_tests.beta8_security_persistence import run_persistent_proof


async def main() -> None:
    await run_persistent_proof()
    await run_beta8_1_runtime_proof()


if __name__ == "__main__":
    asyncio.run(main())
