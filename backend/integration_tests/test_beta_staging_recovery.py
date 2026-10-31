"""Persistent recovery proof; only the explicitly verified Beta 5 target is used."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest
from pydantic import ValidationError
from pymongo import AsyncMongoClient, MongoClient

from curriculum_contract.beta_staging_contract import (
    StagedRecordKind,
    StageState,
    StagingPackage,
    staging_package_from_first_phase,
)
from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase
from services.beta_curriculum_staging import (
    CurriculumStagingService,
    InjectedStagingFailure,
    StagingIdentityConflict,
)
from test_support.beta5_mongo_target import connect_verified_target


def _verified_uri() -> tuple[str, str]:
    """Verify Docker/server identity and claim the database before AsyncMongoClient."""
    target, verifier = connect_verified_target(os.environ, MongoClient)
    try:
        return target.uri, target.run_id
    finally:
        verifier.close()


def test_full_first_phase_staging_recovers_and_repeats_without_duplicates():
    source_root = os.environ.get("BETA5_CURRICULUM_SOURCE")
    assert source_root, "o harness deve fornecer a fonte autorizada em modo leitura"
    root = Path(source_root).resolve(strict=True)
    batch = convert_first_phase(root)
    package = staging_package_from_first_phase(batch)
    uri, run_id = _verified_uri()

    async def exercise() -> None:
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000)
        try:
            await client.admin.command("ping")
            database_name = os.environ["BETA5_TEST_MONGO_DATABASE"]
            database = client[database_name]
            owner_token = os.environ["BETA5_TEST_OWNER_TOKEN"]
            service = CurriculumStagingService(
                database, execution_id=run_id, owner_token=owner_token,
            )
            operational = {
                "tracks", "nodes", "content_blocks", "track_publications",
                "progress", "attempts", "submissions",
            }
            before = set(await database.list_collection_names())
            assert not (before & operational)

            async def fail_after_first_document(point: str, index: int, _record_id: str | None) -> None:
                if point == "after_document_before_checkpoint" and index == 1:
                    raise InjectedStagingFailure("synthetic-after-document-before-checkpoint")

            with pytest.raises(InjectedStagingFailure):
                await service.prepare(package, fault_hook=fail_after_first_document)

            partial = await service.inspect_batch(package.manifest.batch_id)
            assert partial and partial["status"] == StageState.RECOVERABLE.value
            assert await database[service.RECORDS].count_documents({"batch_id": package.manifest.batch_id}) == 1
            assert await database[service.CHECKPOINTS].count_documents({"batch_id": package.manifest.batch_id}) == 0

            recovered = await service.prepare(package)
            assert recovered.state == StageState.PREPARED
            assert recovered.resumed
            record_count = await database[service.RECORDS].count_documents({"batch_id": package.manifest.batch_id})
            checkpoint_count = await database[service.CHECKPOINTS].count_documents({"batch_id": package.manifest.batch_id})
            event_count = await database[service.EVENTS].count_documents({"batch_id": package.manifest.batch_id})
            assert record_count == len(package.records)
            assert checkpoint_count == len(package.records)

            repeated = await service.prepare(package)
            assert repeated.state == StageState.PREPARED
            assert await database[service.RECORDS].count_documents({"batch_id": package.manifest.batch_id}) == record_count
            assert await database[service.CHECKPOINTS].count_documents({"batch_id": package.manifest.batch_id}) == checkpoint_count
            assert await database[service.EVENTS].count_documents({"batch_id": package.manifest.batch_id}) == event_count

            # Simulate a corrupted/reused persisted identity; the service must
            # refuse it without touching staged records.
            await database[service.BATCHES].update_one(
                {"_id": package.manifest.batch_id},
                {"$set": {"payload_sha256": "f" * 64}},
            )
            with pytest.raises(StagingIdentityConflict):
                await service.prepare(package)
            await database[service.BATCHES].update_one(
                {"_id": package.manifest.batch_id},
                {"$set": {"payload_sha256": package.manifest.payload_sha256}},
            )

            # A same-ID payload mutation is rejected by the typed contract before DB access.
            altered = package.model_dump(mode="python")
            altered["manifest"]["payload_sha256"] = "f" * 64
            with pytest.raises(ValidationError):
                StagingPackage.model_validate(altered)

            project_package_record = await database[service.RECORDS].find_one({
                "batch_id": package.manifest.batch_id,
                "record_id": "project-package:3.5",
            })
            assert project_package_record
            assert project_package_record["student_public"] == {}
            stored_project = project_package_record["system_internal"]["project_contract"]
            assert len(stored_project["artifacts"]) == 11
            assert len(stored_project["steps"]) == 4
            project_artifacts = [
                record async for record in database[service.RECORDS].find({
                    "batch_id": package.manifest.batch_id,
                    "kind": StagedRecordKind.PROJECT_ARTIFACT.value,
                })
            ]
            assert len(project_artifacts) == 11
            assert all(record["student_public"] == {} for record in project_artifacts)

            public_quiz = await database[service.RECORDS].find_one({
                "batch_id": package.manifest.batch_id,
                "kind": StagedRecordKind.QUIZ_QUESTION.value,
            })
            assert public_quiz
            assert "correct_option_id" not in json.dumps(public_quiz["student_public"])
            assert "correct_option_id" in public_quiz["instructor_restricted"]

            after = set(await database.list_collection_names())
            assert not (after & operational)
            assert {service.BATCHES, service.RECORDS, service.CHECKPOINTS, service.EVENTS}.issubset(after)

            # A distinct, real-source package exercises concurrent retries of one batch.
            one_unit_batch = batch.model_copy(update={"units": (batch.units[0],)})
            one_unit_package = staging_package_from_first_phase(one_unit_batch)
            service_a = CurriculumStagingService(
                database, execution_id=run_id, owner_token=owner_token,
            )
            concurrent_client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000)
            try:
                service_b = CurriculumStagingService(
                    concurrent_client[database_name], execution_id=run_id, owner_token=owner_token,
                )
                outcomes = await asyncio.gather(
                    service_a.prepare(one_unit_package),
                    service_b.prepare(one_unit_package),
                )
                assert all(item.state == StageState.PREPARED for item in outcomes)
                assert await database[service_a.RECORDS].count_documents({
                    "batch_id": one_unit_package.manifest.batch_id,
                }) == len(one_unit_package.records)
                assert await database[service_a.CHECKPOINTS].count_documents({
                    "batch_id": one_unit_package.manifest.batch_id,
                }) == len(one_unit_package.records)
                assert await database[service_a.EVENTS].count_documents({
                    "batch_id": one_unit_package.manifest.batch_id,
                    "event_id": "prepared",
                }) == 1
            finally:
                await concurrent_client.close()
        finally:
            await client.close()

    asyncio.run(exercise())
