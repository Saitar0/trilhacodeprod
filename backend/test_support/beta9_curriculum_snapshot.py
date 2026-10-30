"""Copy hash-verified curriculum blobs from the pinned source commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

SOURCE_REVISION = "147dc68b81169f66b0ba3802fa2f26e5130923a3"
PILOT_PATH = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
PILOT_SHA256 = "db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4"


def _git(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        timeout=60,
    ).stdout


def create_snapshot(repository: Path, destination: Path) -> dict[str, object]:
    repository = repository.resolve(strict=True)
    destination = destination.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if not destination.is_relative_to(temp_root) or not destination.name.startswith("trilhacode-beta9-source-"):
        raise RuntimeError("destino da cópia curricular fora do temporário Beta 9")
    if destination.exists():
        raise RuntimeError("destino da cópia curricular já existe")
    resolved = _git(repository, "rev-parse", "--verify", f"{SOURCE_REVISION}^{{commit}}").decode().strip()
    if resolved != SOURCE_REVISION:
        raise RuntimeError("revisão curricular de origem diverge do contrato Beta 9")

    manifest = json.loads((repository / "docs/beta/beta4-first-phase-manifest.json").read_text(encoding="utf-8"))
    expected: dict[str, str] = {}
    for unit in manifest.get("units", []):
        for artifact in unit.get("source_artifacts", []):
            expected[artifact["path"]] = artifact["sha256"]
    if len(expected) != 221:
        raise RuntimeError("manifesto Beta 4 não possui as 221 entradas esperadas")

    tree_rows = _git(repository, "ls-tree", "-r", "-z", "--full-tree", SOURCE_REVISION).split(b"\0")
    tree: dict[str, tuple[str, str]] = {}
    for row in tree_rows:
        if not row:
            continue
        metadata, encoded_path = row.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split(" ", 2)
        tree[encoded_path.decode("utf-8")] = (mode, object_id)

    destination.mkdir(parents=True)
    for relative, expected_hash in expected.items():
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise RuntimeError("caminho de fonte curricular fora do manifesto")
        metadata = tree.get(relative)
        if metadata is None or metadata[0] == "120000":
            raise RuntimeError(f"artefato ausente ou symlink na revisão fixada: {relative}")
        payload = _git(repository, "cat-file", "blob", metadata[1])
        if hashlib.sha256(payload).hexdigest() != expected_hash:
            raise RuntimeError(f"hash curricular divergente no objeto Git: {relative}")
        target = destination.joinpath(*pure.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    fixture_relative = PurePosixPath("backend/integration_tests/fixtures/beta2/unit_1_1_computacao_e_software.source.md")
    fixture = (repository / Path(*fixture_relative.parts)).resolve(strict=True)
    if not fixture.is_relative_to(repository) or fixture.is_symlink():
        raise RuntimeError("fixture legado do conversor fora da worktree Beta 9")
    pilot = fixture.read_bytes()
    if hashlib.sha256(pilot).hexdigest() != PILOT_SHA256:
        raise RuntimeError("fixture legado do conversor não corresponde ao hash aprovado")
    pilot_output = destination.joinpath(*PurePosixPath(PILOT_PATH).parts)
    pilot_output.parent.mkdir(parents=True, exist_ok=True)
    pilot_output.write_bytes(pilot)

    return {
        "source_revision": SOURCE_REVISION,
        "artifact_count": len(expected),
        "pilot_fixture_sha256": PILOT_SHA256,
        "destination": str(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create_snapshot(args.repository, args.destination), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
