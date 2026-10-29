"""Offline integrity checks for the C14 readiness package, not runtime security."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READINESS_PATH = ROOT / "docs/architecture/editorial-generations-phase-2-1a-12c14-readiness.json"
WRITER_PATH = ROOT / "backend/integration_tests/editorial_writer_inventory_c13.json"
ALLOWED_STATES = {
    "SATISFIED_IN_ISOLATION",
    "OPERATIONALLY_VERIFIED",
    "PENDING_DECISION",
    "PENDING_TEST",
    "BLOCKED",
    "NOT_APPLICABLE_WITH_RATIONALE",
}
EXPECTED_GATES = {
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


def _readiness() -> dict:
    return json.loads(READINESS_PATH.read_text(encoding="utf-8"))


def test_readiness_rows_are_complete_unique_and_use_closed_states() -> None:
    contract = _readiness()
    rows = contract["requirements"]
    ids = [row["id"] for row in rows]
    assert ids and len(ids) == len(set(ids))

    required = {
        "id",
        "description",
        "domain",
        "evidence",
        "decision_owner",
        "state",
        "blocker",
        "dependencies",
        "acceptance_criterion",
        "next_action",
    }
    for row in rows:
        assert required <= row.keys()
        assert row["state"] in ALLOWED_STATES
        assert row["evidence"]
        assert row["decision_owner"].strip()
        assert row["acceptance_criterion"].strip()
        assert row["next_action"].strip()
        if row["state"] in {"PENDING_DECISION", "PENDING_TEST", "BLOCKED"}:
            assert row["blocker"].strip()


def test_readiness_dependencies_resolve_and_are_acyclic() -> None:
    rows = {row["id"]: row for row in _readiness()["requirements"]}
    graph = {key: set(row["dependencies"]) for key, row in rows.items()}
    assert all(dependencies <= rows.keys() for dependencies in graph.values())

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item: str) -> None:
        assert item not in visiting, f"dependency cycle at {item}"
        if item in visited:
            return
        visiting.add(item)
        for dependency in graph[item]:
            visit(dependency)
        visiting.remove(item)
        visited.add(item)

    for item in graph:
        visit(item)


def test_evidence_sources_exist_and_line_references_are_valid() -> None:
    for row in _readiness()["requirements"]:
        for reference in row["evidence"]:
            path_text, separator, line_text = reference.partition("#L")
            path = ROOT / path_text
            assert path.is_file(), (row["id"], path_text)
            if separator:
                line = int(line_text)
                assert 1 <= line <= len(path.read_text(encoding="utf-8").splitlines())


def test_writer_coverage_matches_revalidated_c13_inventory() -> None:
    contract = _readiness()["writer_coverage"]
    inventory = json.loads(WRITER_PATH.read_text(encoding="utf-8-sig"))
    writers = inventory["writers"]
    ids = [row["id"] for row in writers]
    assert contract["expected_count"] == len(writers) == 17
    assert contract["expected_ids"] == ids
    assert dict(Counter(row["classification"] for row in writers)) == contract[
        "classification_counts"
    ]
    assert contract["runtime"] == "NOT_VERIFIED"
    assert all(row["runtime"] == "NOT_VERIFIED" for row in writers)


def test_first_wave_and_historical_gates_remain_blocked_as_required() -> None:
    contract = _readiness()
    assert contract["first_wave"]["selected"] is False
    assert contract["first_wave"]["blockers"]
    assert contract["gates"] == EXPECTED_GATES
    assert all(row["state"] != "OPERATIONALLY_VERIFIED" for row in contract["requirements"])
