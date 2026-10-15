# ruff: noqa: EXE002
"""Run database management tasks: python -m backend.manage <command>."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import client
from indexes import ensure_indexes
from migrations import migrate
from seed import run_seed
from services.versions import resume_restore_jobs


async def run(command: str) -> None:
    try:
        if command == "ensure-indexes":
            await ensure_indexes()
        elif command == "migrate":
            await migrate()
        elif command == "seed":
            await run_seed()
        elif command == "resume-restores":
            await resume_restore_jobs()
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m backend.manage")
    parser.add_argument("command", choices=("migrate", "seed", "ensure-indexes", "resume-restores"))
    args = parser.parse_args()
    asyncio.run(run(args.command))


if __name__ == "__main__":
    main()
