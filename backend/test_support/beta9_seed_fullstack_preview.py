"""Prepare the real reviewed curriculum in a disposable, granted preview."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.uri_parser import parse_uri

from test_support.beta7_1_seed_preview import _validate_source_and_batch


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"configuração descartável ausente: {name}")
    return value


def _gate() -> tuple[str, str, str]:
    run_id = _required("BETA9_RUN_ID")
    database_name = _required("BETA8_3_DB_NAME")
    root_uri = _required("BETA8_3_ROOT_URI")
    if (
        os.environ.get("BETA9_DISPOSABLE") != "1"
        or os.environ.get("BETA8_3_DOCKER_PRECHECKED") != "true"
        or not re.fullmatch(r"[0-9a-f]{32}", run_id)
        or not re.fullmatch(r"[0-9a-f]{64}", os.environ.get("BETA8_3_DOCKER_CONTAINER_ID", ""))
        or not re.fullmatch(r"[0-9a-f]{64}", os.environ.get("BETA8_3_DOCKER_NETWORK_ID", ""))
        or database_name != f"editorial_revision_test_c10_c11_c12_b83_{run_id[:12]}"
    ):
        raise RuntimeError("gate de propriedade Beta 9 ausente ou divergente")
    parsed = parse_uri(root_uri)
    if (
        parsed.get("nodelist") != [("mongo", 27017)]
        or parsed.get("database") != "admin"
        or parsed.get("username") != "beta8-root"
        or parsed.get("options", {}).get("replicaSet") != "rsB83"
    ):
        raise RuntimeError("URI do preparador não aponta exclusivamente ao Mongo descartável")
    return run_id, database_name, root_uri


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


async def _seed(source_root: Path) -> dict[str, Any]:
    run_id, database_name, root_uri = _gate()
    batch, manifest, project, project_unit = _validate_source_and_batch(source_root)
    batch_id = f"phase1-{manifest['canonical_manifest_sha256']}"

    from database import db
    from indexes import ensure_indexes
    from migrations import migrate
    from security import hash_password
    from seed import BLOCK_TYPES, SUBMITTABLE, TAXONOMIES
    from services.imports import run_import
    from services.beta7_1_preview import preview_db
    from curriculum_contract.beta7_2_assessment import proposed_rubric_from_project

    root = AsyncMongoClient(root_uri, tz_aware=True, appname="beta9-fullstack-seeder")
    try:
        await root.admin.command({"ping": 1})
        if database_name not in set(await root.list_database_names()):
            raise RuntimeError("banco principal Beta 9 não foi provisionado pelo harness")
        if (
            await preview_db["_beta9_preview_owner"].find_one({"_id": "owner"})
            or await preview_db.preview_batches.count_documents({})
            or await preview_db.preview_units.count_documents({})
        ):
            raise RuntimeError("namespace de prévia contém dados; reutilização recusada")
        owner = await root[database_name]["_beta8_3_harness_identity"].find_one({"_id": "owner"})
        if not owner or owner.get("run_id") != run_id or owner.get("phase") != "beta8-3":
            raise RuntimeError("marcador de propriedade do banco diverge do harness")

        await ensure_indexes()
        if await migrate() != 2:
            raise RuntimeError("versão de esquema descartável incompatível")
        for index, (group, key, label, description, color) in enumerate(TAXONOMIES):
            await db.taxonomies.update_one(
                {"group": group, "key": key},
                {"$setOnInsert": {
                    "group": group, "key": key, "label": label,
                    "description": description, "color": color, "order": index,
                }}, upsert=True,
            )
        for index, (key, label, category, icon, fields) in enumerate(BLOCK_TYPES):
            await db.block_types.update_one(
                {"key": key},
                {"$setOnInsert": {
                    "key": key, "label": label, "category": category, "icon": icon,
                    "fields": fields, "description": "", "enabled": True,
                    "capabilities": ["submission"] if key in SUBMITTABLE else [], "order": index,
                }}, upsert=True,
            )

        passwords = {
            "admin": _required("BETA9_ADMIN_PASSWORD"),
            "student": _required("BETA9_STUDENT_PASSWORD"),
            "reviewer": _required("BETA9_REVIEWER_PASSWORD"),
            "unscoped": _required("BETA9_UNSCOPED_PASSWORD"),
        }
        users: dict[str, dict[str, Any]] = {}
        now = datetime.now(UTC)
        for role_key, role, display in (
            ("admin", "admin", "Beta 9 synthetic importer"),
            ("student", "student", "Beta 9 synthetic student"),
            ("reviewer", "editor", "Beta 9 synthetic reviewer"),
            ("unscoped", "editor", "Beta 9 synthetic unscoped user"),
        ):
            email = _required(f"BETA9_{role_key.upper()}_EMAIL").lower()
            if await db.users.find_one({"email": email}, {"_id": 1}):
                raise RuntimeError("identidade sintética já existe; reutilização recusada")
            document = {
                "_id": ObjectId(), "email": email, "name": display,
                "password_hash": hash_password(passwords[role_key]), "role": role,
                "profile": {"bio": "", "goals": "", "preferences": {}},
                "email_verified": True, "is_active": True, "token_version": 0,
                "created_at": now,
            }
            await db.users.insert_one(document)
            users[role_key] = document

        payload = batch.to_import_payload()
        payload["track"]["slug"] = f"beta9-real-phase-{run_id[:16]}"
        payload["track"]["title"] = "Fase 1 revisada — prévia isolada Beta 9"
        payload["track"]["description"] = "Cópia descartável da fonte revisada; sem publicação."
        payload["track"]["status"] = "draft"
        payload["track"]["visibility"] = "private"
        actor = {
            "id": str(users["admin"]["_id"]), "role": "admin",
            "name": users["admin"]["name"],
        }
        dry_run = await run_import(payload, dry_run=True, user=actor)
        if not dry_run.get("ok"):
            raise RuntimeError("validação do importador real recusou o lote Beta 9")
        imported = await run_import(payload, dry_run=False, user=actor)
        if imported.get("dry_run"):
            raise RuntimeError("importador real não confirmou a cópia curricular descartável")
        track = await db.tracks.find_one({"slug": payload["track"]["slug"]})
        if track is None or track.get("status") != "draft" or track.get("visibility") != "private":
            raise RuntimeError("importação real não preservou draft/private")
        private_track_id = str(track["_id"])
        if await db.activity_publications.count_documents({"track_id": private_track_id}) or await db.track_publications.count_documents({"track_id": private_track_id}):
            raise RuntimeError("importação da prévia criou publicação inesperada")

        owner_token = secrets.token_urlsafe(32)
        await preview_db["_beta9_preview_owner"].insert_one({
            "_id": "owner", "run_id": run_id, "database": preview_db.name,
            "parent_database": database_name, "owner_token": owner_token,
            "phase": "beta9", "manifest_sha256": manifest["canonical_manifest_sha256"],
        })
        await preview_db.preview_units.create_index([("batch_id", 1), ("unit_id", 1)], unique=True)
        await preview_db.preview_grants.create_index([("batch_id", 1), ("user_id", 1)], unique=True)
        await preview_db.preview_project_submissions.create_index(
            [("batch_id", 1), ("user_id", 1), ("created_at", 1)],
        )
        await preview_db.beta7_2_rubrics.create_index(
            [("batch_id", 1), ("rubric_id", 1), ("version", 1)], unique=True,
        )
        await preview_db.beta7_2_assessments.create_index(
            [("batch_id", 1), ("submission_id", 1), ("decided_at", 1)],
        )
        for unit in batch.units:
            await preview_db.preview_units.insert_one({
                "_id": f"{batch_id}:{unit.provenance.source_id}",
                "batch_id": batch_id, "unit_id": unit.provenance.source_id,
                "module_order": unit.module_order, "unit_order": unit.unit_order,
                **unit.model_dump(mode="json"),
            })
        stored_count = await preview_db.preview_units.count_documents({"batch_id": batch_id})
        if stored_count != 10:
            raise RuntimeError("número de unidades persistidas diverge do lote validado")
        await preview_db.preview_batches.insert_one({
            "_id": batch_id, "run_id": run_id,
            "source_revision": batch.source_revision,
            "contract_version": batch.contract_version,
            "converter_version": batch.converter_version,
            "manifest_sha256": manifest["canonical_manifest_sha256"],
            "counts": manifest["counts"], "unit_count": len(batch.units),
            "state": "PREPARED", "private_payload": True, "created_at": now,
        })
        rubric = proposed_rubric_from_project(
            project, source_revision=project_unit.provenance.source_revision,
            source_state=project_unit.provenance.source_status,
        )
        await preview_db.beta7_2_rubrics.insert_one({
            "_id": f"{batch_id}:{rubric.rubric_id}:{rubric.version}",
            "batch_id": batch_id, **rubric.model_dump(mode="python"),
        })
        for role_key, operations in (
            ("student", ["preview.curriculum.read"]),
            ("reviewer", ["preview.curriculum.read", "preview.project.review"]),
        ):
            user_id = str(users[role_key]["_id"])
            await preview_db.preview_grants.insert_one({
                "_id": f"{batch_id}:{user_id}", "batch_id": batch_id,
                "user_id": user_id, "state": "active", "operations": operations,
                "revision": 0, "source": "synthetic_beta9_fullstack_harness",
            })

        return {
            "batch_id": batch_id,
            "private_track_id": private_track_id,
            "source_revision": batch.source_revision,
            "manifest_sha256": manifest["canonical_manifest_sha256"],
            "unit_count": stored_count,
            "module_count": manifest["module_count"],
            "counts": manifest["counts"],
            "rubric_state": rubric.state.value if hasattr(rubric.state, "value") else rubric.state,
        }
    finally:
        await root.close()


def main() -> int:
    if os.environ.get("BETA9_DISPOSABLE") != "1":
        raise RuntimeError("preparação Beta 9 sem composição descartável")
    source_root = Path(_required("BETA9_SOURCE_ROOT")).resolve(strict=True)
    result = asyncio.run(_seed(source_root))
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
