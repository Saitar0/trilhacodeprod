"""Deterministic full-curriculum import package assembled from phase contracts.

This module is deliberately offline: it reads contract artifacts and an existing
legacy payload, but never calls the database or the import endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .models import IntermediateContract, canonical_json
from .validation import validate_contract

BULK_IMPORT_SCHEMA: Literal["trilhacode.import_bundle/1.0"] = "trilhacode.import_bundle/1.0"
EXPECTED_BASE_COMMIT = "147dc68b81169f66b0ba3802fa2f26e5130923a3"
EXPECTED_INTEGRITY_MANIFEST_SHA256 = (
    "c3f5aa792641408eb66fc80cf801206de4e1deef2130a5a5c436c8d9ade58055"
)
EXPECTED_LEGACY_JSON_SHA256 = "43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7"


class ImportBundlePhase(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    phase: int = Field(ge=1, le=10)
    contract: IntermediateContract


class StructuralArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    path: str
    sha256: str
    content: str

    @model_validator(mode="after")
    def validate_path_and_content_hash(self) -> StructuralArtifact:
        if (
            not self.path
            or self.path.startswith(("/", "\\"))
            or "\\" in self.path
            or (len(self.path) > 1 and self.path[1] == ":")
            or any(part in {"", ".", ".."} for part in self.path.split("/"))
        ):
            raise ValueError("structural artifact path must be repository-relative POSIX")
        if _sha256(self.content.encode("utf-8")) != self.sha256:
            raise ValueError("structural artifact content hash does not match")
        return self


class CurriculumImportBundle(BaseModel):
    """Versioned, lossless envelope for the ten validated phase contracts."""

    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal["trilhacode.import_bundle/1.0"]
    track: dict[str, Any]
    options: dict[str, Any]
    source: dict[str, Any]
    phases: list[ImportBundlePhase]
    source_mappings: dict[str, Any]
    diagnostics: dict[str, Any]
    structural_artifacts: list[StructuralArtifact]
    integrity: dict[str, Any]

    @model_validator(mode="after")
    def validate_phase_order_and_global_ids(self) -> CurriculumImportBundle:
        phase_numbers = [item.phase for item in self.phases]
        if phase_numbers != list(range(1, 11)):
            raise ValueError("bundle must contain phases 1 through 10 exactly once, in order")
        entity_refs: list[str] = []
        for item in self.phases:
            report = validate_contract(item.contract)
            if not report.ok:
                raise ValueError(f"phase {item.phase} contract has blocking diagnostics")
            entity_refs.extend(_contract_entity_refs(item.contract))
        if len(entity_refs) != len(set(entity_refs)):
            raise ValueError("bundle entity refs must be globally unique")
        return self


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _metadata_sha256(track: dict[str, Any], options: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"track": track, "options": options},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256(canonical)


def _contract_entity_refs(contract: IntermediateContract) -> list[str]:
    refs: list[str] = []
    for collection_name in (
        "nodes",
        "blocks",
        "relations",
        "shared_placements",
        "projects",
        "editorial_pendings",
    ):
        refs.extend(getattr(item, "ref") for item in getattr(contract, collection_name))
    for project in contract.projects:
        refs.extend(item.ref for item in project.deliveries)
        refs.extend(item.ref for item in project.milestones)
        refs.extend(item.ref for item in project.variants)
    return refs


def _verify_artifacts(contract_root: Path, integrity_path: Path) -> tuple[dict[str, Any], str]:
    raw = integrity_path.read_bytes()
    manifest_sha = _sha256(raw)
    if manifest_sha != EXPECTED_INTEGRITY_MANIFEST_SHA256:
        raise ValueError("intermediate integrity manifest does not match the approved artifact")
    manifest = json.loads(raw.decode("utf-8"))
    for artifact in manifest.get("artifacts", []):
        path = contract_root / artifact["path"]
        if not path.is_file():
            raise ValueError(f"required contract artifact is missing: {artifact['path']}")
        if _sha256(path.read_bytes()) != artifact["sha256"]:
            raise ValueError(f"contract artifact hash mismatch: {artifact['path']}")
    return manifest, manifest_sha


def build_import_bundle(
    repo_root: Path,
    *,
    contract_root: Path | None = None,
    legacy_json_path: Path | None = None,
    phase_order: list[int] | None = None,
) -> CurriculumImportBundle:
    """Load, validate and bundle the approved phase contracts deterministically."""
    repo_root = repo_root.resolve()
    contract_root = contract_root or repo_root / "docs/migracao/contrato_intermediario"
    legacy_json_path = (
        legacy_json_path or repo_root / "docs/courses/trilhacode/trilha-code-bulk-import.json"
    )
    integrity_path = contract_root / "integrity_manifest.json"
    manifest, manifest_sha = _verify_artifacts(contract_root, integrity_path)
    if manifest.get("base_commit") != EXPECTED_BASE_COMMIT:
        raise ValueError("intermediate contract base commit differs from the approved revision")

    legacy_bytes = legacy_json_path.read_bytes()
    legacy_sha = _sha256(legacy_bytes)
    legacy = json.loads(legacy_bytes.decode("utf-8"))
    if legacy.get("schema_version") == BULK_IMPORT_SCHEMA:
        source_legacy_sha = legacy.get("source", {}).get("legacy_json_sha256_before_conversion")
        if source_legacy_sha != EXPECTED_LEGACY_JSON_SHA256:
            raise ValueError("existing bundle does not identify the verified legacy JSON source")
        expected_metadata_sha = legacy.get("source", {}).get("legacy_metadata_sha256")
        if expected_metadata_sha != _metadata_sha256(
            legacy.get("track", {}), legacy.get("options", {})
        ):
            raise ValueError(
                "versioned bundle track/options differ from the verified legacy metadata"
            )
    elif legacy_sha != EXPECTED_LEGACY_JSON_SHA256:
        raise ValueError("legacy import JSON differs from its verified pre-conversion version")
    if not isinstance(legacy.get("track"), dict) or not isinstance(legacy.get("options"), dict):
        raise ValueError("import JSON has no valid track/options metadata to preserve")

    numbers = phase_order or list(range(1, 11))
    if sorted(numbers) != list(range(1, 11)):
        raise ValueError("phase_order must contain each phase 1 through 10 exactly once")
    phases: list[ImportBundlePhase] = []
    for number in sorted(numbers):
        path = contract_root / f"fase_{number:02d}.contract.json"
        contract = IntermediateContract.model_validate_json(path.read_text(encoding="utf-8"))
        report = validate_contract(contract)
        if not report.ok:
            errors = [
                item.model_dump(mode="json")
                for item in report.diagnostics
                if item.severity.value == "error"
            ]
            raise ValueError(
                f"phase {number} contract is invalid: {json.dumps(errors, ensure_ascii=False)}"
            )
        phases.append(ImportBundlePhase(phase=number, contract=contract))

    structural_artifacts: list[StructuralArtifact] = []
    for relative_path in manifest.get("unrepresented_structural_files", []):
        path = Path(relative_path)
        if path.is_absolute() or ".." in path.parts or "\\" in relative_path:
            raise ValueError(f"unsafe structural artifact path: {relative_path}")
        artifact_path = (repo_root / path).resolve()
        try:
            artifact_path.relative_to(repo_root)
        except ValueError as error:
            raise ValueError(
                f"structural artifact escapes repository root: {relative_path}"
            ) from error
        artifact_bytes = artifact_path.read_bytes()
        structural_artifacts.append(
            StructuralArtifact(
                path=relative_path,
                sha256=_sha256(artifact_bytes),
                content=artifact_bytes.decode("utf-8"),
            )
        )

    bundle = CurriculumImportBundle(
        schema_version=BULK_IMPORT_SCHEMA,
        track=legacy["track"],
        options=legacy["options"],
        source={
            "base_commit": EXPECTED_BASE_COMMIT,
            "branch": manifest["branch"],
            "contract_schema_version": manifest["contract_schema_version"],
            "integrity_manifest": "docs/migracao/contrato_intermediario/integrity_manifest.json",
            "integrity_manifest_sha256": manifest_sha,
            "legacy_json_sha256_before_conversion": (
                legacy["source"]["legacy_json_sha256_before_conversion"]
                if legacy.get("schema_version") == BULK_IMPORT_SCHEMA
                else legacy_sha
            ),
            "legacy_metadata_sha256": (
                legacy["source"]["legacy_metadata_sha256"]
                if legacy.get("schema_version") == BULK_IMPORT_SCHEMA
                else _metadata_sha256(legacy["track"], legacy["options"])
            ),
        },
        phases=phases,
        source_mappings=json.loads(
            (contract_root / "source_mappings.json").read_text(encoding="utf-8")
        ),
        diagnostics=json.loads((contract_root / "diagnostics.json").read_text(encoding="utf-8")),
        structural_artifacts=structural_artifacts,
        integrity={
            "global_counts": manifest["global_counts"],
            "phase_summaries": manifest["phase_summaries"],
            "represented_source_files": manifest["represented_source_files"],
            "unrepresented_structural_files": manifest["unrepresented_structural_files"],
            "validation": manifest["validation"],
            "artifact_sha256": {
                artifact["path"]: artifact["sha256"] for artifact in manifest["artifacts"]
            },
            "legacy_importer_projection": "not_embedded; full semantic package retained",
            "legacy_import_endpoint": "fail_closed_for_versioned_bundle",
        },
    )
    return bundle


def canonical_import_bundle_json(bundle: CurriculumImportBundle) -> str:
    """Serialize with stable phase/entity order and no volatile generation time."""
    payload = bundle.model_dump(mode="json")
    for phase in payload["phases"]:
        contract = phase["contract"]
        # Reuse the canonical phase serialization order while retaining the bundle envelope.
        parsed = IntermediateContract.model_validate(contract)
        canonical = json.loads(canonical_json(parsed))
        phase["contract"] = canonical
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def validate_import_bundle_json(text: str) -> CurriculumImportBundle:
    """Parse and validate a persisted import bundle without I/O or database access."""
    try:
        return CurriculumImportBundle.model_validate_json(text)
    except ValidationError:
        raise


def write_import_bundle(
    bundle: CurriculumImportBundle, output_path: Path, *, overwrite: bool = False
) -> None:
    """Write a validated package atomically; never overwrite without explicit opt-in."""
    output_path = output_path.resolve()
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"refusing to overwrite existing file without explicit opt-in: {output_path}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = canonical_import_bundle_json(bundle).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, output_path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the full Trilha Code v2 import bundle offline."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/courses/trilhacode/trilha-code-bulk-import.json"),
    )
    parser.add_argument("--write", action="store_true", help="write the output file")
    parser.add_argument(
        "--overwrite", action="store_true", help="explicitly replace the output path"
    )
    args = parser.parse_args()
    bundle = build_import_bundle(args.repo_root)
    content = canonical_import_bundle_json(bundle)
    parsed = validate_import_bundle_json(content)
    if parsed != bundle:
        raise ValueError("serialized import bundle did not round-trip exactly")
    target = args.output if args.output.is_absolute() else args.repo_root / args.output
    if args.write:
        write_import_bundle(bundle, target, overwrite=args.overwrite)
        print(f"wrote {target.resolve()} ({len(content.encode('utf-8'))} bytes)")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
