"""Persistent proof against the real importer and read services, isolated in MongoDB."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from curriculum_contract.experimental_beta_curriculum_converter import convert_markdown_unit  # noqa: E402
from integration_tests.beta_curriculum_import_harness import (  # noqa: E402
    block_type_documents,
    drop_owned_database,
    open_owned_database,
    taxonomy_documents,
)

FIXTURE = BACKEND / "integration_tests" / "fixtures" / "beta2" / "unit_1_1_computacao_e_software.source.md"
SOURCE_PATH = "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
SOURCE_REVISION = "migracao@147dc68:tracked-clean-file"


class Beta2PersistentCurriculumImportTests(unittest.IsolatedAsyncioTestCase):
    client: Any
    database: Any
    database_name: str
    run_id: str

    async def asyncSetUp(self) -> None:
        self.client, self.database, self.run_id = await open_owned_database()
        self.database_name = self.database.name
        await self.database["block_types"].insert_many(block_type_documents())
        await self.database["taxonomies"].insert_many(taxonomy_documents())

    async def asyncTearDown(self) -> None:
        if getattr(self, "client", None) is not None:
            await drop_owned_database(self.client, self.database, self.run_id)

    async def test_real_import_service_persists_replays_and_is_readable(self) -> None:
        unit = convert_markdown_unit(
            FIXTURE.read_bytes(), source_path=SOURCE_PATH, source_revision=SOURCE_REVISION,
        )
        payload = unit.to_import_payload()
        actor = {"id": "beta2-synthetic-admin", "name": "Beta 2 synthetic", "role": "admin"}

        from fastapi import HTTPException

        import learning
        import services.common as common_service
        import services.imports as import_service
        import services.nodes as nodes_service

        import_service.db = self.database
        common_service.db = self.database
        nodes_service.db = self.database
        learning.db = self.database

        dry_run = await import_service.run_import(payload, dry_run=True, user=actor)
        self.assertTrue(dry_run["ok"], dry_run.get("errors"))
        self.assertEqual(dry_run["summary"]["blocks_create"], 12)
        self.assertTrue(dry_run["warnings"], "new quiz data should disclose legacy block metadata mismatch")

        first = await import_service.run_import(payload, dry_run=False, user=actor)
        self.assertFalse(first["dry_run"])
        self.assertFalse(first.get("idempotent_replay", False))
        track = await self.database["tracks"].find_one({"slug": payload["track"]["slug"]})
        self.assertIsNotNone(track)
        self.assertEqual(track["status"], "draft")
        self.assertEqual(track["visibility"], "private")
        self.assertNotIn("_import_state", track)
        imported_node = await self.database["nodes"].find_one({"track_id": str(track["_id"])})
        self.assertEqual(imported_node["pedagogical_type"], "integrado")
        self.assertEqual(imported_node["requirement"], "obrigatorio")
        self.assertEqual(imported_node["depth"], "media")
        self.assertNotIn("completion_criteria", imported_node)
        self.assertEqual(await self.database["nodes"].count_documents({"track_id": str(track["_id"])}), 1)
        self.assertEqual(await self.database["content_blocks"].count_documents({"track_id": str(track["_id"])}), 12)
        self.assertEqual(await self.database["edit_history"].count_documents({"track_id": str(track["_id"])}), 1)
        for exercise in unit.exercises:
            if exercise.instructor_reference:
                self.assertEqual(await self.database["content_blocks"].count_documents({
                    "track_id": str(track["_id"]), "data.prompt": exercise.student_prompt,
                    "data.explanation": {"$exists": True},
                }), 0)

        replay = await import_service.run_import(payload, dry_run=False, user=actor)
        self.assertTrue(replay["idempotent_replay"])
        self.assertEqual(await self.database["tracks"].count_documents({"slug": payload["track"]["slug"]}), 1)
        self.assertEqual(await self.database["nodes"].count_documents({"track_id": str(track["_id"])}), 1)
        self.assertEqual(await self.database["content_blocks"].count_documents({"track_id": str(track["_id"])}), 12)
        self.assertEqual(await self.database["edit_history"].count_documents({"track_id": str(track["_id"])}), 1)

        track_tree = await nodes_service.get_track_tree(str(track["_id"]), actor)
        self.assertEqual(len(track_tree["nodes"]), 1)
        self.assertEqual(track_tree["block_counts"], {str((await self.database["nodes"].find_one({"track_id": str(track["_id"])}))["_id"]): 12})
        node = track_tree["nodes"][0]
        read_model = await nodes_service.get_node(str(node["_id"]), actor)
        self.assertEqual(len(read_model["blocks"]), 12)
        self.assertEqual([item["order"] for item in read_model["blocks"]], list(range(12)))

        student = {"id": "beta2-synthetic-student", "role": "student"}
        with self.assertRaises(HTTPException) as denied:
            await nodes_service.get_track_tree(str(track["_id"]), student)
        self.assertEqual(denied.exception.status_code, 404)

        private_quiz = next(block for block in read_model["blocks"] if block["type"] == "quiz")
        self.assertIn("correct_option_id", private_quiz["data"])
        self.assertIn("feedback", private_quiz["data"])
        self.assertFalse(track.get("status") == "published", "the import proof must never publish")


if __name__ == "__main__":
    unittest.main()
