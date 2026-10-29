from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "backend/integration_tests/editorial_writer_inventory_c13.json"
HARNESS = ROOT / "backend/curriculum_contract/experimental_editorial_writer_containment.py"
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from curriculum_contract.experimental_editorial_writer_containment import (  # noqa: E402
    C16_FAMILY_C13_WRITERS,
)


def test_c16_models_all_c13_editorial_writer_families_without_claiming_runtime_coverage():
    rows = json.loads(INVENTORY.read_text(encoding="utf-8-sig"))["writers"]
    source = HARNESS.read_text(encoding="utf-8")
    assert len(rows) == 17
    assert {row["classification"] for row in rows} == {"A", "B", "C", "D"}
    assert all(row["runtime"] == "NOT_VERIFIED" for row in rows)
    for family in ("block_edit", "publish", "import", "restore", "delete", "duplicate", "reorder"):
        assert f'"{family}"' in source
    assert "AsyncEditorialRevisionAdapter" in source
    assert "Test-only experiment" in source
    assert "never opens a client" in source


def test_c16_participants_never_create_a_second_revision_authority():
    tree = ast.parse(HARNESS.read_text(encoding="utf-8"))
    names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)}
    assert "commit_family_intent" in names
    assert "prepare_family_intent" in names
    assert not any("revision_protocol" in name.lower() or "fence_authority" in name.lower() for name in names)
    assert "writer.adapter.commit" in HARNESS.read_text(encoding="utf-8")


def test_synthetic_family_mapping_is_traceable_to_c13_writer_ids():
    expected = {
        "block_edit": ("W-07",),
        "publish": ("W-04",),
        "import": ("W-10",),
        "restore": ("W-11",),
        "delete": ("W-02", "W-06"),
        "duplicate": ("W-03", "W-06"),
        "reorder": ("W-01", "W-05", "W-07"),
        "seed": ("W-13",),
    }
    assert {family.value: writer_ids for family, writer_ids in C16_FAMILY_C13_WRITERS.items()} == expected
    inventory_ids = {row["id"] for row in json.loads(INVENTORY.read_text(encoding="utf-8-sig"))["writers"]}
    assert {writer_id for ids in expected.values() for writer_id in ids} <= inventory_ids
