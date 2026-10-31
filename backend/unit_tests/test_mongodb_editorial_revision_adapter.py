"""Offline tests for Mongo adapter contracts; these never open a database connection."""
from __future__ import annotations

import unittest

from curriculum_contract.editorial_revision_protocol import InvalidProposal
from curriculum_contract.mongodb_editorial_revision_adapter import (
    MongoDBEditorialRevisionAdapter,
    TransactionTopologyError,
    UnsafeDatabaseName,
    _canonical_payload,
    _fingerprint,
    _validate_identity,
)


class _NoIOClient:
    def start_session(self):
        raise AssertionError("constructor must not open a session")


class _NoIOCollection:
    def create_index(self, *args, **kwargs):
        raise AssertionError("indexes must not be created before topology verification")


class _NoIODatabase:
    def __init__(self, name: str):
        self.name = name
        self.client = _NoIOClient()
        self.collections = {}

    def with_options(self, **kwargs):
        return self

    def __getitem__(self, name):
        return self.collections.setdefault(name, _NoIOCollection())


class MongoAdapterOfflineContractTests(unittest.TestCase):
    def test_import_and_construction_do_not_connect_or_create_collections(self):
        database = _NoIODatabase("editorial_revision_test_0123456789")
        adapter = MongoDBEditorialRevisionAdapter(database, namespace="phase12c2")

        self.assertEqual(adapter.database_name, database.name)
        self.assertFalse(adapter._topology_verified)
        with self.assertRaises(TransactionTopologyError):
            adapter.ensure_indexes()

    def test_non_disposable_database_is_rejected_before_any_io(self):
        database = _NoIODatabase("trilhacode_production")
        with self.assertRaises(UnsafeDatabaseName):
            MongoDBEditorialRevisionAdapter(database, namespace="phase12c2")

    def test_namespace_and_payload_limit_are_validated_without_io(self):
        database = _NoIODatabase("editorial_revision_test_0123456789")
        with self.assertRaises(ValueError):
            MongoDBEditorialRevisionAdapter(database, namespace="../unsafe")
        with self.assertRaises(ValueError):
            MongoDBEditorialRevisionAdapter(
                database, namespace="safe", max_payload_bytes=9 * 1024 * 1024
            )

    def test_identity_byte_limit_and_nul_are_rejected(self):
        with self.assertRaises(InvalidProposal):
            _validate_identity("x" * 257, "operation_id")
        with self.assertRaises(InvalidProposal):
            _validate_identity("track\x00unsafe", "track_id")
        self.assertEqual(_validate_identity("trilha-sintetica", "track_id"), "trilha-sintetica")

    def test_canonical_payload_is_order_independent_and_bounded(self):
        first = _canonical_payload({"b": 2, "a": [True, "sintético"]}, 1024)
        second = _canonical_payload({"a": [True, "sintético"], "b": 2}, 1024)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        with self.assertRaises(InvalidProposal):
            _canonical_payload({"too_large": "x" * 100}, 32)

    def test_payload_rejects_non_json_values_and_non_finite_numbers(self):
        with self.assertRaises(InvalidProposal):
            _canonical_payload({"object": object()}, 1024)
        with self.assertRaises(InvalidProposal):
            _canonical_payload({"number": float("nan")}, 1024)

    def test_payload_depth_and_node_budgets_are_enforced(self):
        deep = {"value": None}
        for _ in range(66):
            deep = {"nested": deep}
        with self.assertRaises(InvalidProposal):
            _canonical_payload(deep, 1024)
        wide = list(range(100_001))
        with self.assertRaises(InvalidProposal):
            _canonical_payload({"values": wide}, 2 * 1024 * 1024)

    def test_operation_fingerprint_scopes_track_writer_operation_and_base(self):
        payload_hash = "a" * 64
        original = _fingerprint("track-a", "writer", "op", 4, payload_hash)
        self.assertNotEqual(original, _fingerprint("track-b", "writer", "op", 4, payload_hash))
        self.assertNotEqual(original, _fingerprint("track-a", "writer", "op", 5, payload_hash))
        self.assertNotEqual(original, _fingerprint("track-a", "writer-b", "op", 4, payload_hash))
        self.assertNotEqual(original, _fingerprint("track-a", "writer", "op-b", 4, payload_hash))


if __name__ == "__main__":
    unittest.main()
