from __future__ import annotations

import asyncio
import sys
from dataclasses import replace
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from curriculum_contract.editorial_revision_protocol import WriterCredential  # noqa: E402
from curriculum_contract.experimental_editorial_authorization import (  # noqa: E402
    AuthorizationCode,
    MongoEditorialAuthorizationGate,
    ServerWriterContext,
    SyntheticPrincipalAuthority,
)
from curriculum_contract.experimental_editorial_privacy import (  # noqa: E402
    EditorialPrivacyError,
    HmacFingerprint,
    HmacKeyUnavailable,
    HmacPurpose,
    VersionedEditorialHmacKeyring,
    build_minimal_intent,
)
from curriculum_contract.experimental_editorial_replay_policy import (  # noqa: E402
    InternalReconciliationAuthority,
    ProtectedResource,
    ReadAccessContext,
    may_read_resource,
)


def _keyring(current: str = "k1") -> VersionedEditorialHmacKeyring:
    return VersionedEditorialHmacKeyring(
        {"k1": b"c11-test-key-one-32-bytes-minimum!!", "k2": b"c11-test-key-two-32-bytes-minimum!!"},
        current_key_id=current,
    )


def test_private_intent_is_reduced_to_closed_structural_metadata():
    secret = "synthetic-private-course-answer"
    block_id = "synthetic-block-reference-11"
    intent = build_minimal_intent(
        track_id="synthetic-track-11",
        block_id=block_id,
        expected_revision=4,
        operation_kind="block.update",
        changes={"data": {"answer": secret}},
        keyring=_keyring(),
    )

    serialized = str(intent)
    assert secret not in serialized
    assert block_id not in serialized
    assert set(intent) == {
        "operation_kind",
        "payload_schema_version",
        "resource_ref_hmac",
        "changed_fields",
        "intent_hmac",
    }
    assert intent["changed_fields"] == ["data"]
    assert intent["intent_hmac"]["key_id"] == "k1"


@pytest.mark.parametrize("changes", [{"unknown": "x"}, {"title": object()}, {}, {1: "x"}])
def test_minimal_intent_rejects_unknown_or_non_json_inputs(changes):
    with pytest.raises(EditorialPrivacyError):
        build_minimal_intent(
            track_id="track",
            block_id="block",
            expected_revision=0,
            operation_kind="block.update",
            changes=changes,
            keyring=_keyring(),
        )


def test_minimal_intent_preserves_null_and_empty_values_as_distinct_intentions():
    ring = _keyring()
    null_intent = build_minimal_intent(
        track_id="track",
        block_id="block",
        expected_revision=0,
        operation_kind="block.update",
        changes={"title": None},
        keyring=ring,
    )
    empty_intent = build_minimal_intent(
        track_id="track",
        block_id="block",
        expected_revision=0,
        operation_kind="block.update",
        changes={"title": ""},
        keyring=ring,
    )
    assert null_intent["intent_hmac"]["digest"] != empty_intent["intent_hmac"]["digest"]
    with pytest.raises(EditorialPrivacyError):
        build_minimal_intent(
            track_id="track",
            block_id="block",
            expected_revision=0,
            operation_kind="block.update",
            changes={"data": {1: "invalid JSON key"}},
            keyring=ring,
        )


def test_hmac_domains_rotation_and_retained_key_verification():
    original = _keyring("k1")
    rotated = _keyring("k2")
    value = {"track": "synthetic-track", "intent": "synthetic-private"}
    first = original.fingerprint(HmacPurpose.INTENT, value)
    assert original.fingerprint(HmacPurpose.INTENT, value) == first
    assert rotated.verify(HmacPurpose.INTENT, value, first)
    assert not rotated.verify(HmacPurpose.OPERATION_ID, value, first)
    assert rotated.fingerprint(HmacPurpose.INTENT, value).digest != first.digest
    assert len(
        rotated.operation_id_candidates(
            actor_id="actor", track_id="track", operation_kind="block.update", idempotency_key="stable-key"
        )
    ) == 2
    assert rotated.operation_id_candidates(
        actor_id="actor", track_id="track", operation_kind="block.update", idempotency_key="stable-key"
    )[-1].startswith("c11_k1_")


def test_missing_hmac_key_fails_closed():
    ring = _keyring("k2")
    with pytest.raises(HmacKeyUnavailable):
        ring.fingerprint(HmacPurpose.INTENT, {"x": 1}, key_id="retired")
    with pytest.raises(HmacKeyUnavailable):
        ring.verify(
            HmacPurpose.INTENT,
            {"x": 1},
            HmacFingerprint("HMAC-SHA-256", "retired", "0" * 64),
        )


def test_synthetic_principal_cannot_be_changed_after_attestation():
    issuer = SyntheticPrincipalAuthority(b"synthetic-principal-key-for-c11-tests!!")
    principal = issuer.attest(
        actor_id="synthetic-actor",
        session_id="synthetic-session",
        role="editor",
        permissions={"content.write"},
    )
    assert issuer.verifies(principal)
    tampered = replace(principal, actor_id="another-actor")
    assert not issuer.verifies(tampered)
    no_session = issuer.attest(
        actor_id="synthetic-actor",
        session_id="synthetic-session",
        role="editor",
        permissions={"content.write"},
        session_valid=False,
    )
    assert issuer.verifies(no_session)
    assert no_session.session_valid is False
    assert AuthorizationCode.AUTHENTICATION_REQUIRED.value == "authentication_required"


def test_proposed_acl_is_fail_closed_for_receipts_history_and_fingerprints():
    editor = ReadAccessContext(
        authenticated=True,
        session_valid=True,
        track_scope=True,
        actor_matches=True,
        audit_reviewer=True,
    )
    assert may_read_resource(ProtectedResource.RECEIPT, editor)
    assert may_read_resource(ProtectedResource.AUDIT, editor)
    assert not may_read_resource(ProtectedResource.INTENT_FINGERPRINT, editor)
    assert not may_read_resource(ProtectedResource.OPERATION_PAYLOAD, editor)
    assert not may_read_resource(
        ProtectedResource.RECEIPT,
        replace(editor, revoked=True),
    )
    assert not may_read_resource(
        ProtectedResource.AUDIT,
        replace(editor, track_scope=False, explicit_global_admin_scope=False),
    )
    assert may_read_resource(
        ProtectedResource.INTENT_FINGERPRINT,
        ReadAccessContext(True, True, False, integrity_service=True),
    )
    assert may_read_resource(
        ProtectedResource.RECEIPT,
        ReadAccessContext(False, False, False, reconciliation_service=True, revoked=True),
    )
    assert may_read_resource(
        ProtectedResource.EDITORIAL_CONTENT,
        ReadAccessContext(True, True, False, public_content=True),
    )


def test_internal_reconciliation_permit_is_signed_and_non_forgeable():
    issuer = InternalReconciliationAuthority(b"c11-test-reconciliation-key-with-32-bytes!")
    scope = {
        "database_name": "editorial_revision_test_c10_c11_unit_case_12345678",
        "namespace": "c8_c11",
        "track_id": "synthetic-track",
        "operation_id": "synthetic-operation",
    }
    permit = issuer.issue(**scope)
    assert issuer.verify(permit, **scope)
    assert not issuer.verify(permit, **{**scope, "track_id": "other-track"})
    assert not issuer.verify(replace(permit, _signature="forged"), **scope)


def test_versioned_role_permission_does_not_establish_track_scope():
    from constants import PERMISSIONS

    assert "content.write" in PERMISSIONS["admin"]
    assert "content.write" in PERMISSIONS["editor"]
    assert "content.write" not in PERMISSIONS["student"]
    assert "track.write" not in PERMISSIONS.get("admin", set())


def test_authorization_store_failure_is_indeterminate_and_fail_closed():
    class FailingCollection:
        async def find_one(self, *_args, **_kwargs):
            raise OSError("synthetic authorization-store outage")

    class FakeDatabase:
        name = "editorial_revision_test_c10_c11_unit_case_12345678"

        def __getitem__(self, _name):
            return FailingCollection()

    issuer = SyntheticPrincipalAuthority(b"c11-test-principal-signing-key-32-bytes!!")
    principal = issuer.attest(
        actor_id="actor", session_id="session", role="editor",
        permissions={"content.write"},
    )
    gate = MongoEditorialAuthorizationGate(
        FakeDatabase(), namespace="c8_c11",
        capability_key=b"c11-test-capability-signing-key-32-bytes!!",
    )
    decision = asyncio.run(gate.issue_capability(
        principal, issuer,
        track_id="track", operation_kind="block.update",
        operation_id="c11_store_error_test_0001", expected_revision=0,
        writer_context=ServerWriterContext(WriterCredential("track", "writer", "secret"), 1),
    ))
    assert decision.code is AuthorizationCode.INDETERMINATE
    assert decision.capability is None
