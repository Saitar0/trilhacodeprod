"""Strict privacy helpers for isolated C11 editorial authorization tests.

This module is not imported by the active application. It minimizes the intent
stored by the C8-shaped protocol; it does not encrypt block contents in the
content collection and does not define production key retention or rotation.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class EditorialPrivacyError(ValueError):
    """Raised when an intent cannot be safely minimized."""


class HmacKeyUnavailable(EditorialPrivacyError):
    """The key version needed to verify a retained fingerprint is unavailable."""


class HmacPurpose(str, Enum):
    OPERATION_ID = "editorial-operation-id"
    INTENT = "editorial-intent"
    RESOURCE_REFERENCE = "editorial-resource-reference"


_KEY_ID = re.compile(r"^[A-Za-z0-9_-]{1,24}$")
_EDITABLE_FIELDS = frozenset({"title", "data", "status"})
_STATUS_VALUES = frozenset({"draft", "published", "archived"})
_MAX_CANONICAL_BYTES = 1024 * 1024
_MAX_JSON_NODES = 20_000
_MAX_JSON_DEPTH = 64


@dataclass(frozen=True, slots=True)
class HmacFingerprint:
    algorithm: str
    key_id: str
    digest: str


class VersionedEditorialHmacKeyring:
    """In-memory versioned keyring; keys are supplied by the trusted caller."""

    def __init__(self, keys: Mapping[str, bytes], *, current_key_id: str) -> None:
        if not isinstance(keys, Mapping) or not keys:
            raise EditorialPrivacyError("at least one HMAC key is required")
        copied: dict[str, bytes] = {}
        for key_id, key in keys.items():
            if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
                raise EditorialPrivacyError("invalid HMAC key identifier")
            if not isinstance(key, bytes) or len(key) < 32:
                raise EditorialPrivacyError("HMAC keys must contain at least 32 bytes")
            copied[key_id] = bytes(key)
        if current_key_id not in copied:
            raise HmacKeyUnavailable("current HMAC key is not available")
        self._keys = copied
        self._current_key_id = current_key_id

    @property
    def current_key_id(self) -> str:
        return self._current_key_id

    @property
    def available_key_ids(self) -> tuple[str, ...]:
        return tuple(self._keys)

    def fingerprint(
        self,
        purpose: HmacPurpose,
        value: Any,
        *,
        key_id: str | None = None,
    ) -> HmacFingerprint:
        if not isinstance(purpose, HmacPurpose):
            raise EditorialPrivacyError("HMAC purpose is not recognized")
        selected = key_id or self._current_key_id
        key = self._keys.get(selected)
        if key is None:
            raise HmacKeyUnavailable("required HMAC key is unavailable")
        payload = _canonical_json(value)
        message = b"trilhacode:c11:" + purpose.value.encode("ascii") + b"\x00" + payload
        digest = hmac.new(key, message, hashlib.sha256).hexdigest()
        return HmacFingerprint("HMAC-SHA-256", selected, digest)

    def verify(
        self,
        purpose: HmacPurpose,
        value: Any,
        expected: HmacFingerprint,
    ) -> bool:
        if expected.algorithm != "HMAC-SHA-256":
            return False
        actual = self.fingerprint(purpose, value, key_id=expected.key_id)
        return hmac.compare_digest(actual.digest, expected.digest)

    def operation_id_candidates(
        self,
        *,
        actor_id: str,
        track_id: str,
        operation_kind: str,
        idempotency_key: str,
    ) -> tuple[str, ...]:
        """Derive opaque IDs under retained keys to support controlled rotation."""

        scope = {
            "actor": _required_text(actor_id, "actor_id"),
            "track": _required_text(track_id, "track_id"),
            "operation": _required_text(operation_kind, "operation_kind"),
            "key": _required_text(idempotency_key, "idempotency_key"),
        }
        candidates: list[str] = []
        ordered_ids = [self._current_key_id] + [
            key_id for key_id in self._keys if key_id != self._current_key_id
        ]
        for key_id in ordered_ids:
            fingerprint = self.fingerprint(
                HmacPurpose.OPERATION_ID, scope, key_id=key_id
            )
            candidates.append(f"c11_{key_id}_{fingerprint.digest}")
        return tuple(candidates)


def build_minimal_intent(
    *,
    track_id: str,
    block_id: str,
    expected_revision: int,
    operation_kind: str,
    changes: Mapping[str, Any],
    keyring: VersionedEditorialHmacKeyring,
    key_id: str | None = None,
) -> dict[str, Any]:
    """Return only structural metadata and keyed digests, never raw changes."""

    track = _required_text(track_id, "track_id")
    block = _required_text(block_id, "block_id")
    operation = _required_text(operation_kind, "operation_kind")
    if type(expected_revision) is not int or expected_revision < 0:
        raise EditorialPrivacyError("expected revision must be non-negative")
    if not isinstance(changes, Mapping) or not changes:
        raise EditorialPrivacyError("changes must be a non-empty mapping")
    if any(not isinstance(field, str) or field not in _EDITABLE_FIELDS for field in changes):
        raise EditorialPrivacyError("unknown or non-editable field")
    if "title" in changes and changes["title"] is not None and not isinstance(changes["title"], str):
        raise EditorialPrivacyError("title must be a string or null")
    if "data" in changes and changes["data"] is not None and not isinstance(changes["data"], dict):
        raise EditorialPrivacyError("data must be an object or null")
    if "status" in changes and changes["status"] is not None:
        status = changes["status"]
        if not isinstance(status, str) or status not in _STATUS_VALUES:
            raise EditorialPrivacyError("status is outside the supported values")

    canonical_changes = dict(changes)
    # The canonicalizer is a validation boundary; it rejects arbitrary objects,
    # NaN and unsupported values without serializing them to the record.
    _canonical_json(canonical_changes)
    intent = {
        "track": track,
        "block": block,
        "expected_revision": expected_revision,
        "operation": operation,
        "changes": canonical_changes,
    }
    fingerprint = keyring.fingerprint(
        HmacPurpose.INTENT, intent, key_id=key_id
    )
    resource_ref = keyring.fingerprint(
        HmacPurpose.RESOURCE_REFERENCE,
        {"track": track, "block": block},
        key_id=fingerprint.key_id,
    )
    return {
        "operation_kind": operation,
        "payload_schema_version": 2,
        "resource_ref_hmac": resource_ref.digest,
        "changed_fields": sorted(canonical_changes),
        "intent_hmac": {
            "algorithm": fingerprint.algorithm,
            "key_id": fingerprint.key_id,
            "digest": fingerprint.digest,
        },
    }


def _canonical_json(value: Any) -> bytes:
    _validate_json(value, depth=0, budget=[0])
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise EditorialPrivacyError("intent contains unsupported values") from exc
    if len(encoded) > _MAX_CANONICAL_BYTES:
        raise EditorialPrivacyError("intent exceeds the isolated size limit")
    return encoded


def _required_text(value: str, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\x00" in value
        or len(value.encode("utf-8")) > 256
    ):
        raise EditorialPrivacyError(f"{name} is invalid")
    return value


def _validate_json(value: Any, *, depth: int, budget: list[int]) -> None:
    budget[0] += 1
    if budget[0] > _MAX_JSON_NODES or depth > _MAX_JSON_DEPTH:
        raise EditorialPrivacyError("intent exceeds structural limits")
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise EditorialPrivacyError("non-finite numbers are not supported")
        return
    if isinstance(value, list):
        for child in value:
            _validate_json(child, depth=depth + 1, budget=budget)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise EditorialPrivacyError("object keys must be strings")
            _validate_json(child, depth=depth + 1, budget=budget)
        return
    raise EditorialPrivacyError("intent contains unsupported values")
