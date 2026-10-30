"""Validate then prepare the real first-phase preview after the host gate."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from pymongo import MongoClient

from test_support.beta7_1_internal_target import connect_internal_verified_target

SOURCE_REVISION = "migration@147dc68:tracked-clean-first-phase-files"
EXPECTED_COUNTS = {
    "topics": 30,
    "theory_segments": 42,
    "quiz_files": 30,
    "quiz_questions": 44,
    "manual_exercises": 26,
    "project_materials": 11,
    "references": 39,
    "relations": 30,
    "persisted_blocks": 161,
}


def _validate_source_and_batch(source_root: Path):
    from curriculum_contract.beta_project_contract import project_package_from_converted_unit
    from curriculum_contract.experimental_beta_first_phase_converter import convert_first_phase

    batch = convert_first_phase(source_root, source_revision=SOURCE_REVISION)
    manifest = batch.to_manifest()
    if batch.conversion_status == "CONVERSION_BLOCKED" or manifest["duplicate_generated_ids"]:
        raise RuntimeError("Lote curricular contém bloqueios ou identidades duplicadas")
    if len(batch.units) != 10 or manifest["module_count"] != 3 or manifest["counts"] != EXPECTED_COUNTS:
        raise RuntimeError("Manifesto curricular difere do inventário autorizado")
    project_unit = next(
        item for item in batch.units if item.provenance.source_id == "3.5"
    )
    project = project_package_from_converted_unit(project_unit)
    if len(project.artifacts) != 11 or len(project.rubrics) != 1 or len(project.steps) != 4:
        raise RuntimeError("Projeto 3.5 não corresponde ao contrato de 11 artefatos")
    return batch, manifest, project, project_unit


async def _prepare(source_root: Path, run_id: str, owner_token: str, container_id: str, network_id: str,
                   passwords: dict[str, str]) -> dict[str, Any]:
    # Parsing, source validation, duplicate checks, contract validation and
    # project classification are completed before curriculum persistence.
    batch, manifest, project, project_unit = _validate_source_and_batch(source_root)
    batch_id = f"phase1-{manifest['canonical_manifest_sha256']}"
    from database import db
    from indexes import ensure_indexes
    from migrations import migrate
    from security import hash_password
    from seed import BLOCK_TYPES, SUBMITTABLE, TAXONOMIES
    from services.imports import run_import

    current_collections = set(await db.list_collection_names())
    if current_collections - {"_beta7-1_test_owner"}:
        raise RuntimeError("Banco curricular não está vazio antes da fixture")

    await ensure_indexes()
    await migrate()
    users = {
        "admin": {"email": "beta7-1-admin@example.com", "role": "admin", "name": "Beta 7.1 Synthetic Admin",
                  "password": passwords["admin"]},
        "student": {"email": "beta7-1-student@example.com", "role": "student", "name": "Beta 7.1 Synthetic Student",
                    "password": passwords["student"]},
        "reviewer": {"email": "beta7-1-reviewer@example.com", "role": "editor", "name": "Beta 7.1 Synthetic Reviewer",
                     "password": passwords["reviewer"]},
        "unscoped": {"email": "beta7-1-unscoped@example.com", "role": "editor", "name": "Beta 7.1 Synthetic Unscoped",
                     "password": passwords["unscoped"]},
    }
    inserted: dict[str, dict[str, Any]] = {}
    for key, record in users.items():
        doc = {
            "email": record["email"], "name": record["name"], "role": record["role"],
            "password_hash": hash_password(record["password"]), "email_verified": True,
            "is_active": True, "token_version": 0,
            "profile": {"bio": "", "goals": "", "preferences": {}},
        }
        result = await db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        inserted[key] = doc

    for index, (group, key, label, description, color) in enumerate(TAXONOMIES):
        await db.taxonomies.insert_one({
            "group": group, "key": key, "label": label,
            "description": description, "color": color, "order": index,
        })
    for index, (key, label, category, icon, fields) in enumerate(BLOCK_TYPES):
        await db.block_types.insert_one({
            "key": key, "label": label, "category": category, "icon": icon,
            "fields": fields, "description": "", "enabled": True,
            "capabilities": ["submission"] if key in SUBMITTABLE else [], "order": index,
        })

    payload = batch.to_import_payload()
    payload["track"]["slug"] = f"beta7-1-real-phase-{run_id[:16]}"
    payload["track"]["title"] = "Fase 1 revisada — rascunho Beta 7.1"
    payload["track"]["description"] = "Conteúdo curricular privado, somente para prévia isolada."
    actor = {"id": str(inserted["admin"]["_id"]), "role": "admin", "name": users["admin"]["name"]}
    dry_run = await run_import(payload, dry_run=True, user=actor)
    if not dry_run.get("ok"):
        raise RuntimeError("Dry run do importador real reprovou o lote curricular")
    imported = await run_import(payload, dry_run=False, user=actor)
    if imported.get("dry_run"):
        raise RuntimeError("Importador real não confirmou a persistência no banco Beta 7.1")
    track = await db.tracks.find_one({"slug": payload["track"]["slug"]})
    if track is None or track.get("status") != "draft" or track.get("visibility") != "private":
        raise RuntimeError("Importação do rascunho não preservou draft/private")
    private_track_id = str(track["_id"])
    if await db.activity_publications.count_documents({"track_id": private_track_id}) != 0:
        raise RuntimeError("Importação criou publicação de atividade inesperada")
    if await db.track_publications.count_documents({"track_id": private_track_id}) != 0:
        raise RuntimeError("Importação criou publicação editorial inesperada")

    # A preview is stored in its own database namespace. It is not a visibility
    # flag, track publication, or staging promotion.
    preview_name = f"{db.name}_beta7_1_preview"
    sync_target, owner_client = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    try:
        names = set(owner_client.list_database_names())
        if preview_name in names:
            raise RuntimeError("Namespace da prévia já existe; recurso preexistente preservado")
        preview_owner = owner_client[preview_name]["_beta7-1_test_owner"]
        marker = {
            "_id": "owner", "run_id": run_id, "owner_token": owner_token,
            "container_id": container_id, "network_id": network_id,
            "database": preview_name, "parent_database": db.name,
        }
        preview_owner.insert_one(marker)
        if preview_owner.find_one({"_id": "owner"}) != marker:
            raise RuntimeError("Marcador do namespace Beta 7.1 não foi confirmado")
    finally:
        owner_client.close()

    from curriculum_contract.beta7_2_assessment import proposed_rubric_from_project
    from services.beta7_1_preview import preview_db

    rubric = proposed_rubric_from_project(
        project,
        source_revision=project_unit.provenance.source_revision,
        source_state=project_unit.provenance.source_status,
    )

    await preview_db.preview_units.create_index([("batch_id", 1), ("unit_id", 1)], unique=True)
    await preview_db.preview_grants.create_index([("batch_id", 1), ("user_id", 1)], unique=True)
    await preview_db.preview_project_submissions.create_index([("batch_id", 1), ("user_id", 1), ("created_at", 1)])
    await preview_db.beta7_2_rubrics.create_index(
        [("batch_id", 1), ("rubric_id", 1), ("version", 1)], unique=True,
    )
    await preview_db.beta7_2_assessments.create_index(
        [("batch_id", 1), ("submission_id", 1), ("decided_at", 1)],
    )
    if await preview_db.preview_batches.find_one({"_id": batch_id}):
        raise RuntimeError("Identidade da prévia já existe; não será reutilizada")
    for unit in batch.units:
        await preview_db.preview_units.insert_one({
            "_id": f"{batch_id}:{unit.provenance.source_id}",
            "batch_id": batch_id,
            "unit_id": unit.provenance.source_id,
            "module_order": unit.module_order,
            "unit_order": unit.unit_order,
            **unit.model_dump(mode="json"),
        })
    stored_count = await preview_db.preview_units.count_documents({"batch_id": batch_id})
    if stored_count != len(batch.units):
        raise RuntimeError("Contagem persistida da prévia diverge do lote validado")
    await preview_db.preview_batches.insert_one({
        "_id": batch_id,
        "run_id": run_id,
        "source_revision": batch.source_revision,
        "contract_version": batch.contract_version,
        "converter_version": batch.converter_version,
        "manifest_sha256": manifest["canonical_manifest_sha256"],
        "counts": manifest["counts"],
        "unit_count": len(batch.units),
        "state": "PREPARED",
        "private_payload": True,
        "created_at": __import__("datetime").datetime.now(__import__("datetime").UTC),
    })
    await preview_db.beta7_2_rubrics.insert_one({
        "_id": f"{batch_id}:{rubric.rubric_id}:{rubric.version}",
        "batch_id": batch_id,
        **rubric.model_dump(mode="python"),
    })
    student_id = str(inserted["student"]["_id"])
    reviewer_id = str(inserted["reviewer"]["_id"])
    unscoped_id = str(inserted["unscoped"]["_id"])
    await preview_db.preview_grants.insert_many([
        {
            "_id": f"{batch_id}:{student_id}", "batch_id": batch_id, "user_id": student_id,
            "state": "active", "operations": ["preview.curriculum.read"], "revision": 0,
            "source": "synthetic_beta7_1_harness",
        },
        {
            "_id": f"{batch_id}:{reviewer_id}", "batch_id": batch_id, "user_id": reviewer_id,
            "state": "active", "operations": ["preview.curriculum.read", "preview.project.review"],
            "revision": 0, "source": "synthetic_beta7_1_harness",
        },
        {
            "_id": f"{batch_id}:{unscoped_id}", "batch_id": batch_id, "user_id": unscoped_id,
            "state": "active", "operations": [], "revision": 0,
            "source": "synthetic_beta7_1_harness",
        },
    ])

    return {
        "batch_id": batch_id,
        "private_track_id": private_track_id,
        "counts": manifest["counts"],
        "module_count": manifest["module_count"],
        "unit_count": manifest["unit_count"],
        "manifest_sha256": manifest["canonical_manifest_sha256"],
        "source_revision": batch.source_revision,
        "source_hashes": sorted({unit.provenance.source_sha256 for unit in batch.units}),
        "project_artifact_count": len(project.artifacts),
        "persisted_relation_count": await db.relations.count_documents({"track_id": private_track_id}),
        "publication_records": await db.track_publications.count_documents({"track_id": private_track_id}),
        "activity_publications": await db.activity_publications.count_documents({"track_id": private_track_id}),
        "private_track_status": track["status"],
        "private_track_visibility": track["visibility"],
    }


def main() -> int:
    source_root = Path(os.environ.get("TRILHACODE_BETA7_1_SOURCE_ROOT", "")).resolve(strict=True)
    _, ownership = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    try:
        target = __import__("test_support.beta7_1_internal_target", fromlist=["validate_internal_target"]).validate_internal_target(os.environ)
        collections = set(ownership[target.database].list_collection_names())
        if collections - {"_beta7-1_test_owner"}:
            raise RuntimeError("Banco Beta 7.1 contém dados inesperados antes do seed")
    finally:
        ownership.close()
    passwords = {
        "admin": os.environ["BETA7_1_ADMIN_PASSWORD"],
        "student": os.environ["BETA7_1_STUDENT_PASSWORD"],
        "reviewer": os.environ["BETA7_1_REVIEWER_PASSWORD"],
        "unscoped": os.environ["BETA7_1_UNSCOPED_PASSWORD"],
    }
    result = asyncio.run(_prepare(
        source_root, target.run_id, target.owner_token, target.container_id, target.network_id, passwords,
    ))
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
