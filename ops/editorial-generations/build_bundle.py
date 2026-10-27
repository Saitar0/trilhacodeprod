"""Build the allowlisted bundle from blobs in one exact local Git commit."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent / "executor-template" / "scripts"),
)
from bundle_security import (
    ALLOWED_FILES,
    MAX_FILE_BYTES,
    BundleError,
    build_archive,
    manifest_for,
    sha256_bytes,
)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_commit_files(root: Path, revision: str) -> dict[str, bytes]:
    resolved = git(root, "rev-parse", "--verify", f"{revision}^{{commit}}")
    if resolved != revision:
        raise BundleError("A referência precisa ser um SHA de commit completo")
    remote = git(root, "remote", "get-url", "origin").rstrip("/").removesuffix(".git")
    if remote.casefold() != "https://github.com/saitar0/trilhacodeprod".casefold():
        raise BundleError("O remoto origin não corresponde ao repositório autorizado")

    rows = git(
        root,
        "ls-tree",
        "-r",
        "--full-tree",
        revision,
        "--format=%(objectmode) %(objecttype) %(objectname)%x09%(path)",
    ).splitlines()
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    for row in rows:
        metadata, separator, path = row.partition("\t")
        if not separator:
            raise BundleError("Saída inesperada do inventário Git")
        mode, object_type, blob_sha = metadata.split(" ", 2)
        if path not in ALLOWED_FILES:
            continue
        if path in seen:
            raise BundleError("Caminho duplicado no commit")
        seen.add(path)
        if mode != "100644" or object_type != "blob":
            raise BundleError(f"Somente arquivos regulares versionados são aceitos: {path}")
        data = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", blob_sha],
            check=True,
            capture_output=True,
        ).stdout
        if len(data) > MAX_FILE_BYTES:
            raise BundleError(f"Arquivo excede limite: {path}")
        files[path] = data
    if set(files) != ALLOWED_FILES:
        raise BundleError(
            f"Commit não contém a allowlist exata; ausentes={sorted(ALLOWED_FILES - set(files))}"
        )
    return files


def worktree_paths(root: Path) -> list[Path]:
    listing = git(root, "worktree", "list", "--porcelain")
    paths = []
    for line in listing.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line.removeprefix("worktree ")).resolve())
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.output.resolve()
    try:
        if output.is_relative_to(root):
            raise BundleError("Artefato de pacote deve ficar fora da worktree")
        if any(output.is_relative_to(path) for path in worktree_paths(root)):
            raise BundleError("Artefato não pode ser gravado dentro de qualquer worktree")
        if output.exists():
            raise BundleError("Saída já existe; escolha caminho novo para evitar sobrescrita")
        output.parent.mkdir(parents=True, exist_ok=True)
        files = read_commit_files(root, args.source_sha)
        archive = build_archive(files, args.source_sha)
        manifest = manifest_for(files, args.source_sha)
        with output.open("xb") as handle:
            handle.write(archive)
        print(f"Source SHA: {args.source_sha}")
        print(f"Files: {len(files)} + manifest.json")
        print(f"Package bytes: {len(archive)}")
        print(f"Package SHA-256: {sha256_bytes(archive)}")
        print(f"Package ID: {manifest['package_id']}")
        return 0
    except (BundleError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Bundle rejected: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
