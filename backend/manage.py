# ruff: noqa: EXE002
"""Run database management tasks: python -m backend.manage <command>."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import client
from indexes import ensure_indexes, preflight_indexes
from migrations import migrate
from seed import run_seed
from services.versions import resume_restore_jobs


async def run(command: str) -> None:
    try:
        if command == "ensure-indexes":
            await ensure_indexes()
        elif command == "preflight-indexes":
            findings = await preflight_indexes()
            for finding in findings:
                print(finding)
            if any(finding.startswith(("CONFLITO ", "DUPLICATAS ")) for finding in findings):
                raise RuntimeError("Preflight encontrou conflitos ou duplicatas; índices não foram alterados")
        elif command == "migrate":
            await migrate()
        elif command == "seed":
            await run_seed()
        elif command == "resume-restores":
            await resume_restore_jobs()
    finally:
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m backend.manage")
    parser.add_argument("command", choices=("migrate", "seed", "ensure-indexes", "preflight-indexes", "resume-restores"))
    args = parser.parse_args()
    asyncio.run(run(args.command))


if __name__ == "__main__":
    main()
