"""Static consistency checks for C13's versioned-code writer inventory."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "backend/integration_tests/editorial_writer_inventory_c13.json"
ALLOWED_CLASSES = {"A", "B", "C", "D"}
ALLOWED_RISKS = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "NOT_VERIFIED"}


def _inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))


def _defined_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def test_writer_ids_are_unique_and_every_row_is_classified() -> None:
    rows = _inventory()["writers"]
    ids = [row["id"] for row in rows]
    assert len(rows) >= 12
    assert len(ids) == len(set(ids))
    for row in rows:
        assert row["classification"] in ALLOWED_CLASSES
        assert row["risk"] in ALLOWED_RISKS
        assert row["runtime"] == "NOT_VERIFIED"
        assert row["strategy"].strip()
        assert row["acceptance"].strip()
        assert row["test_evidence"]["located"]
        assert row["test_evidence"]["execution_in_c13"].startswith("not_run")


def test_sources_symbols_and_evidence_ranges_exist() -> None:
    for row in _inventory()["writers"]:
        source = ROOT / row["file"]
        assert source.is_file(), row["file"]
        defined = _defined_symbols(source)
        for symbol in row["symbols"]:
            assert symbol in defined, f"{row['id']} missing symbol {symbol} in {row['file']}"

        evidence = row["evidence"]
        evidence_file = ROOT / evidence["file"]
        lines = evidence_file.read_text(encoding="utf-8").splitlines()
        start, end = evidence["lines"]
        assert 1 <= start <= end <= len(lines), (row["id"], evidence)
        for key in ("additional_file",):
            if key in evidence:
                assert (ROOT / evidence[key]).is_file(), (row["id"], evidence[key])
                extra_lines = (ROOT / evidence[key]).read_text(encoding="utf-8").splitlines()
                extra_start, extra_end = evidence["additional_lines"]
                assert 1 <= extra_start <= extra_end <= len(extra_lines)


def test_known_editorial_mutation_modules_are_represented() -> None:
    rows = _inventory()["writers"]
    inventoried = {row["file"] for row in rows}
    known_editorial_modules = {
        "backend/audit.py",
        "backend/integrity.py",
        "backend/seed.py",
        "backend/services/blocks.py",
        "backend/services/editorial_generations_poc.py",
        "backend/services/immutable_publications.py",
        "backend/services/imports.py",
        "backend/services/nodes.py",
        "backend/services/relations.py",
        "backend/services/taxonomy.py",
        "backend/services/tracks.py",
        "backend/services/versions.py",
    }
    assert known_editorial_modules <= inventoried


def test_test_evidence_paths_are_existing_repository_files_or_explicit_gaps() -> None:
    for row in _inventory()["writers"]:
        for item in row["test_evidence"]["located"]:
            if item.startswith("No focused"):
                continue
            path_text = item.split("::", 1)[0] if "::" in item else item.split(maxsplit=1)[0]
            path = ROOT / path_text
            assert path.is_file(), (row["id"], item)
            if "::" in item:
                test_name = item.split("::", 1)[1]
                assert test_name in _defined_symbols(path), (row["id"], item)


def test_special_risks_and_cutover_blocks_are_not_hidden() -> None:
    rows = {row["id"]: row for row in _inventory()["writers"]}
    assert rows["W-02"]["classification"] == "B"
    assert rows["W-04"]["classification"] == "B"
    assert rows["W-07"]["classification"] == "A"
    assert rows["W-10"]["classification"] == "B"
    assert rows["W-11"]["classification"] == "B"
    assert rows["W-17"]["classification"] == "C"
    assert "progress" in rows["W-02"]["collections"]
    assert rows["W-07"]["permission"] == "content.write, including the current DELETE block route"
