"""Offline structural checks for the C15 editorial enforcement specification."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "architecture"
    / "editorial-generations-phase-2-1a-12c15-enforcement-contract.json"
)
INVENTORY_PATH = ROOT / "backend" / "integration_tests" / "editorial_writer_inventory_c13.json"


def _read_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_policies_decisions_and_writer_ids_are_unique_and_closed() -> None:
    contract = _read_contract()
    assert [item["id"] for item in contract["policies"]] == [f"P{i}" for i in range(1, 9)]
    assert len({item["id"] for item in contract["decisions"]}) == len(contract["decisions"])
    assert len({item["id"] for item in contract["writers"]}) == 17
    assert {item["id"] for item in contract["writers"]} == {
        f"W-{i:02d}" for i in range(1, 18)
    }
    assert all(item["state"] in contract["decision_states"] for item in contract["decisions"])
    assert all(item["runtime"] == "NOT_VERIFIED" for item in contract["writers"])


def test_writer_contract_matches_historical_inventory_without_reclassification() -> None:
    contract = _read_contract()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    expected = {item["id"]: item for item in inventory["writers"]}
    actual = {item["id"]: item for item in contract["writers"]}

    assert actual.keys() == expected.keys()
    for writer_id, entry in expected.items():
        assert actual[writer_id]["class"] == entry["classification"]
        assert actual[writer_id]["symbols"] == entry["symbols"]
        assert actual[writer_id]["runtime"] == entry["runtime"]
        assert actual[writer_id]["enforcement"].strip()


def test_implementation_dependencies_are_resolved_and_acyclic() -> None:
    stages = _read_contract()["implementation_stages"]
    by_id = {stage["id"]: stage for stage in stages}
    assert len(by_id) == len(stages)
    for stage in stages:
        assert stage["scope"].strip()
        assert set(stage["depends_on"]) <= by_id.keys()

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(stage_id: str) -> None:
        assert stage_id not in visiting, f"dependency cycle includes {stage_id}"
        if stage_id in visited:
            return
        visiting.add(stage_id)
        for dependency in by_id[stage_id]["depends_on"]:
            visit(dependency)
        visiting.remove(stage_id)
        visited.add(stage_id)

    for stage_id in by_id:
        visit(stage_id)


def test_readiness_preserves_operational_blocks_and_historical_gates() -> None:
    contract = _read_contract()
    readiness = {item["id"]: item for item in contract["readiness"]}
    assert len(readiness) == len(contract["readiness"])
    assert all(item["criterion"].strip() for item in readiness.values())
    assert readiness["R-11"]["state"] == "BLOCKED"
    assert readiness["R-12"]["state"] == "BLOCKED"
    assert readiness["R-14"]["state"] == "PENDING_OPERATIONAL_EVIDENCE"
    assert readiness["R-18"]["state"] == "BLOCKED"
    assert contract["integration_authorized"] is False
    assert contract["first_mutation_wave_selected"] is False
    assert contract["runtime_evidence"] == "NOT_VERIFIED"
    assert contract["historical_gates"] == {
        "G1": "PARTIAL",
        "G2": "NOT_VERIFIED",
        "G3": "NOT_VERIFIED",
        "G4": "PARTIAL",
        "G5": "NOT_VERIFIED",
        "G6": "PARTIAL",
        "G7": "PARTIAL",
        "G8": "NOT_VERIFIED",
        "G9": "BLOCKED",
        "G10": "BLOCKED",
        "ADR-008": "BLOCKED",
    }
    assert "OPERATIONALLY_VERIFIED" not in {
        item["state"] for item in contract["readiness"]
    }


def test_document_manifest_exists_and_relative_links_resolve() -> None:
    contract = _read_contract()
    docs_dir = CONTRACT_PATH.parent
    for name in contract["documents"]:
        assert (docs_dir / name).is_file(), name

    for document in [docs_dir / name for name in contract["documents"]]:
        body = document.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", body):
            if "://" in target or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path:
                assert (document.parent / path).resolve().exists(), (document.name, target)
