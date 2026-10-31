"""Offline checks for the C13 proposal; this is not an application IAM engine."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "backend/curriculum_contract/editorial_grant_governance_c13.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def _current_permission_matrix() -> dict[str, list[str]]:
    source = ast.parse((ROOT / "backend/constants.py").read_text(encoding="utf-8"))
    for node in source.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PERMISSIONS" for target in node.targets
        ):
            literal = ast.literal_eval(node.value)
            return {role: sorted(permissions) for role, permissions in literal.items()}
    raise AssertionError("PERMISSIONS assignment was not found in backend/constants.py")


def test_contract_role_snapshot_matches_versioned_backend_policy() -> None:
    contract = _contract()
    assert contract["current_backend_roles_and_permissions"] == _current_permission_matrix()


def test_current_model_does_not_claim_track_grants_or_admin_global_scope() -> None:
    contract = _contract()
    facts = contract["current_authorization_facts"]
    proposal = contract["proposed_governance_rules"]
    assert facts["track_write_grants_exist_in_active_backend"] is False
    assert facts["admin_role_implies_universal_track_write"] is False
    assert proposal["admin_global_scope_is_implicit"] is False
    assert proposal["global_admin_scope_requires_explicit_provisioning"] is True
    assert contract["authority_recommendation"]["operational_schema_selected"] is False


def test_proposal_separates_authorization_from_fence_and_idempotency() -> None:
    proposal = _contract()["proposed_governance_rules"]
    assert proposal["fencing_token_is_authorization"] is False
    assert proposal["idempotency_key_is_authorization"] is False
    assert proposal["capability_is_accepted_from_client"] is False
    assert proposal["authorization_lookup_failure_fails_closed"] is True


def test_delegation_is_subset_limited_and_cannot_self_grant() -> None:
    proposal = _contract()["proposed_governance_rules"]
    assert proposal["grantor_can_self_grant"] is False
    assert proposal["grantor_can_delegate_beyond_own_scope"] is False
    assert proposal["delegated_operations_must_be_subset_of_grantor_authority"] is True
    assert proposal["grant_change_increments_authorization_epoch"] is True


def test_revocation_rule_and_audit_contract_are_fail_closed() -> None:
    contract = _contract()
    revocation = contract["revocation_ordering"]
    audit = contract["audit_contract"]
    assert revocation["revocation_before_editorial_commit"] == "reject_editorial_commit"
    assert revocation["editorial_commit_before_revocation"] == "preserve_confirmed_historical_operation"
    assert revocation["external_check_or_eventual_projection_sufficient"] is False
    assert audit["grant_change_audit_is_best_effort"] is False
    assert {"JWT", "session_secret", "fencing_token", "content_payload"}.issubset(
        set(audit["forbidden_fields"])
    )


def test_declarative_contract_is_not_imported_by_runtime_entrypoints() -> None:
    runtime_files = [
        ROOT / "backend/server.py",
        ROOT / "backend/security.py",
        ROOT / "backend/permissions.py",
        ROOT / "backend/routes_content.py",
        ROOT / "backend/routes_auth.py",
    ]
    marker = "editorial_grant_governance_c13"
    for path in runtime_files:
        assert marker not in path.read_text(encoding="utf-8")
