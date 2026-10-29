"""Failure/replay proof through the versioned import service in disposable MongoDB."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_beta_curriculum_fidelity import (  # noqa: E402
    convert_fidelity_unit,
)
from integration_tests.beta_import_recovery_harness import (  # noqa: E402
    block_type_documents,
    drop_owned_database,
    open_owned_database,
    taxonomy_documents,
)

FIXTURE = BACKEND / "integration_tests" / "fixtures" / "beta2" / "unit_1_1_computacao_e_software.source.md"
SOURCE_PATH = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
SOURCE_REVISION = "migracao@147dc68:tracked-clean-file"
SOURCE_SHA256 = "db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4"
ENABLED = bool(os.environ.get("TRILHACODE_BETA3_MONGO_URI"))


@unittest.skipUnless(ENABLED, "MongoDB Beta 3 descartável não configurado")
class Beta3ImportRecoveryTests(unittest.IsolatedAsyncioTestCase):
    client: Any
    database: Any
    database_name: str
    run_id: str

    async def asyncSetUp(self) -> None:
        self.client, self.database, self.run_id = await open_owned_database()
        self.database_name = self.database.name
        await self.database["block_types"].insert_many(block_type_documents())
        await self.database["taxonomies"].insert_many(taxonomy_documents())

        import learning
        import services.common as common_service
        import services.imports as import_service
        import services.nodes as nodes_service

        import_service.db = self.database
        common_service.db = self.database
        nodes_service.db = self.database
        learning.db = self.database
        self.import_service = import_service
        self.nodes_service = nodes_service
        self.actor = {"id": "beta3-synthetic-admin", "name": "Beta 3 synthetic", "role": "admin"}
        self.unit = convert_fidelity_unit(
            FIXTURE.read_bytes(), source_path=SOURCE_PATH, source_revision=SOURCE_REVISION,
            expected_source_sha256=SOURCE_SHA256,
        )
        self.payload = self.unit.to_import_payload()

    async def asyncTearDown(self) -> None:
        if getattr(self, "client", None) is not None:
            await drop_owned_database(self.client, self.database, self.run_id)

    async def _run_and_track(self) -> tuple[dict[str, Any], dict[str, Any]]:
        result = await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        self.assertIsNotNone(track)
        return result, track

    async def test_real_import_and_read_services_preserve_order_and_no_student_leak(self) -> None:
        dry_run = await self.import_service.run_import(self.payload, dry_run=True, user=self.actor)
        self.assertTrue(dry_run["ok"], dry_run.get("errors"))
        result, track = await self._run_and_track()
        self.assertFalse(result["dry_run"])
        self.assertEqual(track["status"], "draft")
        self.assertEqual(track["visibility"], "private")
        self.assertNotIn("_import_state", track)

        node = await self.database["nodes"].find_one({"track_id": str(track["_id"])})
        self.assertIsNotNone(node)
        blocks = await self.database["content_blocks"].find(
            {"track_id": str(track["_id"])}
        ).sort("order", 1).to_list(100)
        self.assertEqual(len(blocks), 19)
        self.assertEqual([block["order"] for block in blocks], list(range(19)))
        self.assertTrue(all(block["status"] == "draft" for block in blocks))
        self.assertEqual(sum(block["type"] == "theory_text" for block in blocks), 8)
        self.assertEqual(sum(block["type"] == "quiz" for block in blocks), 5)
        self.assertEqual(sum(block["type"] == "exercise_open" for block in blocks), 3)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": str(track["_id"])}), 1)

        tree = await self.nodes_service.get_track_tree(str(track["_id"]), self.actor)
        self.assertEqual(len(tree["nodes"]), 1)
        read = await self.nodes_service.get_node(str(node["_id"]), self.actor)
        self.assertEqual([block["order"] for block in read["blocks"]], list(range(19)))
        self.assertEqual(len([block for block in read["blocks"] if block["type"] == "theory_text"]), 8)

        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as denied:
            await self.nodes_service.get_track_tree(
                str(track["_id"]), {"id": "synthetic-student", "role": "student"},
            )
        self.assertEqual(denied.exception.status_code, 404)

        quiz = next(block for block in read["blocks"] if block["type"] == "quiz")
        self.assertIn("correct_option_id", quiz["data"])
        replay = await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertTrue(replay["idempotent_replay"])
        self.assertEqual(await self.database["tracks"].count_documents({"slug": self.payload["track"]["slug"]}), 1)
        self.assertEqual(await self.database["nodes"].count_documents({"track_id": str(track["_id"])}), 1)
        self.assertEqual(await self.database["content_blocks"].count_documents({"track_id": str(track["_id"])}), 19)
        self.assertEqual(await self.database["edit_history"].count_documents({"track_id": str(track["_id"])}), 1)

    async def test_partial_block_failure_is_reconciled_by_same_import_identity(self) -> None:
        original = self.import_service._block_values
        calls = 0

        def fail_after_four_calls(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            if calls == 5:
                raise RuntimeError("synthetic failure after four persisted blocks")
            return original(*args, **kwargs)

        with patch.object(self.import_service, "_block_values", side_effect=fail_after_four_calls):
            with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
                await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)

        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        self.assertIsNotNone(track)
        self.assertEqual(track["_import_state"]["status"], "interrupted")
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": str(track["_id"])}), 4)
        job = await self.database["import_jobs"].find_one({"slug": self.payload["track"]["slug"]})
        self.assertEqual(job["status"], "interrupted")

        resumed = await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertFalse(resumed.get("idempotent_replay", False))
        final = await self.database["tracks"].find_one({"_id": track["_id"]})
        self.assertNotIn("_import_state", final)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": str(track["_id"])}), 19)
        self.assertEqual(await self.database["nodes"].count_documents(
            {"track_id": str(track["_id"])}), 1)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": str(track["_id"])}), 1)

    async def test_failure_after_versioned_quiz_persistence_resumes_without_duplicates(self) -> None:
        original = self.import_service._block_values
        calls = 0

        def fail_before_first_exercise(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            if calls == 15:  # 8 theory + summary + 5 quiz blocks have returned.
                raise RuntimeError("synthetic failure after persisted quiz stage")
            return original(*args, **kwargs)

        with patch.object(self.import_service, "_block_values", side_effect=fail_before_first_exercise):
            with self.assertRaisesRegex(RuntimeError, "persisted quiz stage"):
                await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)

        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        track_id = str(track["_id"])
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id, "type": "quiz"}), 5)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id}), 14)

        await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id}), 19)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id, "type": "quiz"}), 5)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": track_id}), 1)

    async def test_failure_after_all_exercises_before_references_is_recoverable(self) -> None:
        original = self.import_service._block_values
        calls = 0

        def fail_before_first_reference(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            if calls == 18:  # 8 theory + summary + 5 quiz + 3 exercises.
                raise RuntimeError("synthetic failure after persisted exercise stage")
            return original(*args, **kwargs)

        with patch.object(self.import_service, "_block_values", side_effect=fail_before_first_reference):
            with self.assertRaisesRegex(RuntimeError, "persisted exercise stage"):
                await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)

        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        track_id = str(track["_id"])
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id, "type": "exercise_open"}), 3)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id}), 17)

        await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id}), 19)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": track_id}), 1)

    async def test_audit_failure_before_persistence_is_recoverable(self) -> None:
        async def fail_before_audit(*_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("synthetic audit persistence failure")

        with patch.object(self.import_service, "_record_import_audit", side_effect=fail_before_audit):
            with self.assertRaisesRegex(RuntimeError, "audit persistence failure"):
                await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)

        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        track_id = str(track["_id"])
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": track_id}), 19)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": track_id}), 0)

        await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": track_id}), 1)

    async def test_audit_persisted_then_lost_ack_retries_without_duplicate_audit(self) -> None:
        original = self.import_service._record_import_audit

        async def persist_then_lose_ack(*args: Any, **kwargs: Any) -> None:
            await original(*args, **kwargs)
            raise RuntimeError("synthetic acknowledgment loss after audit write")

        with patch.object(self.import_service, "_record_import_audit", side_effect=persist_then_lose_ack):
            with self.assertRaisesRegex(RuntimeError, "acknowledgment loss"):
                await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)

        track = await self.database["tracks"].find_one({"slug": self.payload["track"]["slug"]})
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": str(track["_id"])}), 1)
        interrupted_job = await self.database["import_jobs"].find_one(
            {"slug": self.payload["track"]["slug"]}
        )
        self.assertEqual(interrupted_job["status"], "interrupted")

        resumed = await self.import_service.run_import(self.payload, dry_run=False, user=self.actor)
        self.assertFalse(resumed.get("idempotent_replay", False))
        self.assertEqual(await self.database["edit_history"].count_documents(
            {"track_id": str(track["_id"])}), 1)
        self.assertEqual(await self.database["content_blocks"].count_documents(
            {"track_id": str(track["_id"])}), 19)
