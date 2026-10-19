"""Validation helpers for the versioned, non-sensitive G2 result protocol."""

from __future__ import annotations

from typing import Any

ALLOWED_STATES = {"OK", "AUSENTE", "CONFLITO", "DUPLICATAS"}


def validate_report(report: Any, expected_ids: list[str]) -> list[dict[str, str]]:
    """Reject incomplete, malformed, duplicated, or unrecognized check reports."""
    if not isinstance(report, dict) or set(report) != {"schema_version", "result", "checks"}:
        raise ValueError("invalid G2 report")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1 or report["result"] != "COMPLETE":
        raise ValueError("invalid G2 report")
    checks = report["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("invalid G2 report")
    ids: list[str] = []
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "status"}:
            raise ValueError("invalid G2 check")
        if not isinstance(check["id"], str) or not isinstance(check["status"], str) or check["status"] not in ALLOWED_STATES:
            raise ValueError("invalid G2 check")
        ids.append(check["id"])
    if len(ids) != len(set(ids)) or sorted(ids) != sorted(expected_ids):
        raise ValueError("G2 check set does not match manifest")
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("invalid G2 manifest")
    return checks


def is_rejected(checks: list[dict[str, str]]) -> bool:
    return any(check["status"] in {"CONFLITO", "DUPLICATAS"} for check in checks)
