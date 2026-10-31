"""Verify a local bundle using an independently supplied expected SHA-256."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "executor-template" / "scripts"),
)
from bundle_security import (
    MAX_ARCHIVE_BYTES,
    BundleError,
    extract_verified,
    verify_archive,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--extract-to", type=Path)
    args = parser.parse_args()
    try:
        archive_path = args.archive.resolve(strict=True)
        if args.archive.is_symlink() or not archive_path.is_file():
            raise BundleError("Pacote precisa ser arquivo regular sem symlink")
        if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise BundleError("Pacote excede o limite")
        archive_bytes = archive_path.read_bytes()
        if args.extract_to:
            manifest = extract_verified(
                archive_bytes,
                args.extract_to,
                expected_archive_sha256=args.expected_sha256,
                expected_source_sha=args.expected_source_sha,
            )
        else:
            manifest, _files = verify_archive(
                archive_bytes,
                expected_archive_sha256=args.expected_sha256,
                expected_source_sha=args.expected_source_sha,
            )
        print(f"Pacote íntegro: {manifest['package_id']}")
        print(f"SHA de origem: {manifest['source']['git_sha']}")
        print(f"Arquivos verificados: {len(manifest['files'])}")
        return 0
    except (BundleError, OSError) as exc:
        print(f"Verificação recusada: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
