"""Private, inactive publication snapshots.

This module prepares immutable read models but deliberately does not activate
them. Student readers still use the legacy content collections until a later
phase adds a complete writer revision protocol and switches every reader.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import secrets
from datetime import timedelta
from typing import Any

from bson import ObjectId

from core_utils import now

PUBLICATION_SCHEMA_VERSION = 1
PUBLICATION_LEASE = timedelta(minutes=10)
_TRACK_ID = re.compile(r"[0-9a-fA-F]{24}\Z")
_OPERATION_ID = re.compile(r"[A-Za-z0-9._:-]{8,128}\Z")
_ALLOWED_STATUSES = {"draft", "published", "archived"}
MAX_SNAPSHOT_BYTES = 128 * 1024 * 1024
MAX_SNAPSHOT_DEPTH = 64


class PublicationPreparationError(ValueError):
    """The source snapshot cannot represent a valid publication."""

    status_code = 422


class PublicationConflict(RuntimeError):
    """The idempotency key or preparation lease conflicts with existing work."""

    status_code = 409


class PublicationStorageError(RuntimeError):
    """The private snapshot could not be verified or persisted completely."""

    status_code = 503


def _canonical_value(value: Any, depth: int = 0) -> Any:
    if depth > MAX_SNAPSHOT_DEPTH:
        raise PublicationPreparationError("Snapshot excede a profundidade máxima")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise PublicationPreparationError("Snapshot contém chaves que não são texto")
        return {key: _canonical_value(value[key], depth + 1) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item, depth + 1) for item in value]
    if isinstance(value, ObjectId):
        return str(value)
    if hasattr(value, "isoformat") and callable(value.isoformat):
        return value.isoformat()
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PublicationPreparationError("Snapshot contém número não finito")
        return value
    raise PublicationPreparationError("Snapshot contém valor não serializável")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _canonical_value(value), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        if isinstance(exc, PublicationPreparationError):
            raise
        raise PublicationPreparationError("Snapshot não pode ser canonicalizado") from exc


def _entity_id(item: dict, field: str = "id") -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise PublicationPreparationError(f"Identificador ausente ou inválido: {field}")
    return value


def _order(item: dict) -> float:
    value = item.get("order", 0)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise PublicationPreparationError("Ordem de apresentação inválida")
    return float(value)


def _validate_and_sort_snapshot(snapshot: Any, track_id: str) -> dict:
    if not isinstance(snapshot, dict):
        raise PublicationPreparationError("Snapshot incompleto")
    canonical = _canonical_value(snapshot)
    track = canonical.get("track")
    if not isinstance(track, dict) or track.get("id") != track_id:
        raise PublicationPreparationError("Snapshot sem trilha correspondente")
    for key in ("nodes", "blocks", "relations"):
        if not isinstance(canonical.get(key), list) or any(not isinstance(row, dict) for row in canonical[key]):
            raise PublicationPreparationError(f"Snapshot incompleto: {key}")

    nodes = canonical["nodes"]
    node_ids = [_entity_id(node) for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise PublicationPreparationError("Snapshot contém IDs de nós duplicados")
    by_id = dict(zip(node_ids, nodes))
    for node in nodes:
        if node.get("track_id") != track_id:
            raise PublicationPreparationError("Snapshot contém nó de outra trilha")
        if node.get("status") not in _ALLOWED_STATUSES:
            raise PublicationPreparationError("Snapshot contém status de nó inválido")
        parent_id = node.get("parent_id")
        if parent_id and parent_id not in by_id:
            raise PublicationPreparationError("Snapshot contém referência de hierarquia inexistente")
        _order(node)

    # Detect cycles and derive stable hierarchical ordering without relying on
    # MongoDB cursor order.
    paths: dict[str, tuple] = {}
    visiting: set[str] = set()

    def path_for(node_id: str) -> tuple:
        if node_id in paths:
            return paths[node_id]
        if node_id in visiting:
            raise PublicationPreparationError("Snapshot contém ciclo na hierarquia")
        visiting.add(node_id)
        node = by_id[node_id]
        parent_id = node.get("parent_id")
        part = (_order(node), node_id)
        result = path_for(parent_id) + (part,) if parent_id else (part,)
        visiting.remove(node_id)
        paths[node_id] = result
        return result

    canonical["nodes"] = sorted(nodes, key=lambda node: path_for(node["id"]))

    blocks = canonical["blocks"]
    block_ids = [_entity_id(block) for block in blocks]
    if len(block_ids) != len(set(block_ids)):
        raise PublicationPreparationError("Snapshot contém IDs de blocos duplicados")
    for block in blocks:
        if block.get("track_id") != track_id:
            raise PublicationPreparationError("Snapshot contém bloco de outra trilha")
        if block.get("node_id") not in by_id:
            raise PublicationPreparationError("Snapshot contém bloco sem nó correspondente")
        if block.get("status") not in _ALLOWED_STATUSES:
            raise PublicationPreparationError("Snapshot contém status de bloco inválido")
        _order(block)
    canonical["blocks"] = sorted(
        blocks, key=lambda block: (block["node_id"], _order(block), block["id"]),
    )

    relations = canonical["relations"]
    relation_ids = [row["id"] for row in relations if row.get("id") is not None]
    if len(relation_ids) != len(set(relation_ids)):
        raise PublicationPreparationError("Snapshot contém IDs de relações duplicados")
    relation_keys = []
    for relation in relations:
        if relation.get("track_id") != track_id:
            raise PublicationPreparationError("Snapshot contém relação de outra trilha")
        if relation.get("node_id") not in by_id or relation.get("target_id") not in by_id:
            raise PublicationPreparationError("Snapshot contém relação sem nós correspondentes")
        relation_type = relation.get("type")
        if not isinstance(relation_type, str) or not relation_type:
            raise PublicationPreparationError("Snapshot contém relação sem tipo válido")
        relation_keys.append((relation["node_id"], relation["target_id"], relation_type))
    if len(relation_keys) != len(set(relation_keys)):
        raise PublicationPreparationError("Snapshot contém relações duplicadas")
    canonical["relations"] = sorted(relations, key=lambda row: _canonical_bytes(row))
    return canonical


def canonicalize_publication_snapshot(snapshot: dict, track_id: str, publish_children: bool) -> dict:
    """Validate a complete snapshot and apply publication status only in memory."""
    if not isinstance(publish_children, bool):
        raise PublicationPreparationError("publish_children deve ser booleano")
    result = _validate_and_sort_snapshot(snapshot, track_id)
    if publish_children:
        for node in result["nodes"]:
            if node.get("status") == "draft":
                node["status"] = "published"
        for block in result["blocks"]:
            if block.get("status") == "draft":
                block["status"] = "published"
    return result


def canonical_snapshot_hash(snapshot: dict) -> str:
    return hashlib.sha256(_canonical_bytes(snapshot)).hexdigest()


def _fingerprint(
    *, track_id: str, source_hash: str, snapshot_hash: str, source_revision: Any,
    publish_children: bool, note: str, created_by: str,
) -> str:
    payload = {
        "track_id": track_id,
        "source_hash": source_hash,
        "snapshot_hash": snapshot_hash,
        "source_revision": source_revision,
        "schema_version": PUBLICATION_SCHEMA_VERSION,
        "publish_children": publish_children,
        "note": note,
        "created_by": created_by,
    }
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _safe_result(document: dict) -> dict:
    """Return metadata only; never return snapshots or assessment definitions."""
    return {
        "publication_id": str(document["_id"]),
        "track_id": document["track_id"],
        "operation_id": document["operation_id"],
        "state": document["state"],
        "visibility": document["visibility"],
        "active": document["active"],
        "snapshot_complete": document.get("snapshot_complete", False),
        "schema_version": document["schema_version"],
        "source_revision": document.get("source_revision"),
        "source_consistency": document["source_consistency"],
        "activation_eligible": document["activation_eligible"],
        "activation_block_reason": document.get("activation_block_reason"),
        "source_hash": document["source_hash"],
        "snapshot_hash": document["snapshot_hash"],
        "stats": document["stats"],
        "activity_count": document.get("activity_count", 0),
        "activity_refs_sha256": document.get("activity_refs_sha256"),
        "created_at": document["created_at"],
        "prepared_at": document.get("prepared_at"),
    }


def _validate_request(track_id: str, operation_id: str, note: str, user: dict) -> None:
    if not isinstance(track_id, str) or not _TRACK_ID.fullmatch(track_id):
        raise PublicationPreparationError("Identificador da trilha inválido")
    if not isinstance(operation_id, str) or not _OPERATION_ID.fullmatch(operation_id):
        raise PublicationPreparationError("Idempotency-Key inválida")
    if not isinstance(note, str) or len(note) > 500:
        raise PublicationPreparationError("Nota de publicação inválida")
    if not isinstance(user, dict) or not isinstance(user.get("id"), str) or not user["id"]:
        raise PublicationPreparationError("Identidade do operador inválida")


async def _get_db():
    from database import db
    return db


async def _capture_source_snapshot(track_id: str) -> dict:
    from services.versions import snapshot_track
    return await snapshot_track(track_id)


async def _store_private_snapshot(storage_id: str, snapshot: dict) -> dict:
    from integrity import store_snapshot
    return await store_snapshot(storage_id, snapshot)


async def _load_private_snapshot(manifest: dict) -> dict:
    from integrity import load_snapshot
    storage = manifest["snapshot_storage"]
    version = {
        "_id": storage["version_id"],
        "track_id": manifest["track_id"],
        "chunks": storage["chunks"],
        "sha256": storage["sha256"],
        "stats": manifest["stats"],
    }
    return await load_snapshot(version)


async def _delete_private_snapshot(storage_id: str) -> None:
    database = await _get_db()
    await database.version_chunks.delete_many({"version_id": storage_id})


async def _build_activity_publications(snapshot: dict, publication_id: str, revision: int) -> list[dict]:
    from services.activity_publications import ActivityDefinitionError, normalize_quiz

    eligible_nodes = {node["id"] for node in snapshot["nodes"] if node.get("status") == "published"}
    rows = []
    for block in snapshot["blocks"]:
        if (block.get("type") != "quiz" or block.get("status") != "published"
                or block.get("node_id") not in eligible_nodes):
            continue
        try:
            definition = normalize_quiz(block, publication_id, revision)
        except ActivityDefinitionError as exc:
            raise PublicationPreparationError(str(exc)) from exc
        if definition is None:
            continue
        rows.append({
            "_id": ObjectId(),
            "track_id": snapshot["track"]["id"],
            "node_id": block["node_id"],
            "activity_id": definition["activity_id"],
            "published_version_id": publication_id,
            "visibility": "private",
            "active": False,
            "definition": definition,
            "created_at": now(),
        })
    return sorted(rows, key=lambda row: row["activity_id"])


async def _upsert_private_activities(database, rows: list[dict]) -> dict:
    references = []
    for row in rows:
        key = {
            "track_id": row["track_id"],
            "published_version_id": row["published_version_id"],
            "activity_id": row["activity_id"],
        }
        existing = await database.activity_publications.find_one(key)
        if existing:
            old_definition = existing.get("definition") or {}
            if (old_definition.get("definition_sha256") != row["definition"]["definition_sha256"]
                    or existing.get("visibility") != "private" or existing.get("active") is not False):
                raise PublicationConflict("A definição privada da atividade diverge da preparação")
        else:
            await database.activity_publications.update_one(
                key, {"$setOnInsert": row}, upsert=True,
            )
            existing = await database.activity_publications.find_one(key)
            if (not existing
                    or (existing.get("definition") or {}).get("definition_sha256") != (
                        row["definition"]["definition_sha256"]
                    )
                    or existing.get("visibility") != "private" or existing.get("active") is not False):
                raise PublicationConflict("Conflito ao persistir definição privada de atividade")
        references.append({
            "activity_id": row["activity_id"],
            "node_id": row["node_id"],
            "definition_sha256": row["definition"]["definition_sha256"],
            "evaluator_version": row["definition"]["evaluator_version"],
        })
    digest = hashlib.sha256(_canonical_bytes(references)).hexdigest()
    return {"count": len(references), "sha256": digest}


async def _verify_private_activities(
    database, track_id: str, publication_id: str, expected_count: int, expected_hash: str,
) -> None:
    references = []
    query = {"track_id": track_id, "published_version_id": publication_id}
    async for row in database.activity_publications.find(query):
        definition = row.get("definition")
        if not isinstance(definition, dict):
            raise PublicationStorageError("Definição privada de atividade incompleta")
        if row.get("visibility") != "private" or row.get("active") is not False:
            raise PublicationStorageError("Definição de atividade não está privada e inativa")
        digest = definition.get("definition_sha256")
        unsigned = {key: value for key, value in definition.items() if key != "definition_sha256"}
        actual_digest = hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()
        if not isinstance(digest, str) or digest != actual_digest:
            raise PublicationStorageError("Definição privada de atividade corrompida")
        activity_id = row.get("activity_id")
        node_id = row.get("node_id")
        evaluator_version = definition.get("evaluator_version")
        if not all(isinstance(value, str) and value for value in (activity_id, node_id, evaluator_version)):
            raise PublicationStorageError("Referência de atividade privada inválida")
        if definition.get("activity_id") != activity_id:
            raise PublicationStorageError("Identidade da definição privada diverge da referência")
        references.append({
            "activity_id": activity_id,
            "node_id": node_id,
            "definition_sha256": digest,
            "evaluator_version": evaluator_version,
        })
    references.sort(key=lambda reference: reference["activity_id"])
    actual_hash = hashlib.sha256(_canonical_bytes(references)).hexdigest()
    if len(references) != expected_count or actual_hash != expected_hash:
        raise PublicationStorageError("Referências privadas de atividades incompletas ou divergentes")


async def _claim_operation(
    database, *, track_id: str, operation_id: str, fingerprint: str,
    base_document: dict,
) -> tuple[dict, str | None]:
    from pymongo.errors import DuplicateKeyError

    for _ in range(4):
        existing = await database.track_publications.find_one({
            "track_id": track_id, "operation_id": operation_id,
        })
        if existing is None:
            owner = secrets.token_hex(16)
            storage_id = str(ObjectId())
            document = {
                "_id": ObjectId(), **base_document,
                "track_id": track_id, "operation_id": operation_id,
                "fingerprint": fingerprint, "state": "preparing",
                "visibility": "private", "active": False, "snapshot_complete": False,
                "owner": owner, "lease_until": now() + PUBLICATION_LEASE,
                "storage_id": storage_id, "generation": 1,
                "created_at": now(),
            }
            try:
                await database.track_publications.insert_one(document)
                return document, owner
            except DuplicateKeyError:
                continue

        if existing.get("fingerprint") != fingerprint:
            raise PublicationConflict("Idempotency-Key reutilizada com outro conteúdo")
        if existing.get("state") == "prepared":
            if existing.get("snapshot_complete") is not True:
                raise PublicationStorageError("Manifest preparado sem snapshot completo")
            return existing, None

        current_time = now()
        state = existing.get("state")
        if state == "preparing" and existing.get("lease_until") and existing["lease_until"] > current_time:
            raise PublicationConflict("A preparação idempotente ainda está em andamento")
        if state not in {"preparing", "failed"}:
            raise PublicationConflict("Estado da preparação não pode ser retomado")

        owner = secrets.token_hex(16)
        storage_id = str(ObjectId())
        selector = {"_id": existing["_id"], "fingerprint": fingerprint, "state": state}
        if state == "preparing":
            selector["lease_until"] = {"$lte": current_time}
        update = {
            "$set": {
                "state": "preparing", "owner": owner,
                "lease_until": current_time + PUBLICATION_LEASE,
                "storage_id": storage_id, "snapshot_complete": False,
            },
            "$inc": {"generation": 1},
            "$unset": {
                "failure_code": "", "prepared_at": "", "snapshot_storage": "",
                "activity_count": "", "activity_refs_sha256": "",
            },
        }
        if existing.get("storage_id"):
            update["$addToSet"] = {"orphan_storage_ids": existing["storage_id"]}
        result = await database.track_publications.update_one(selector, update)
        if result.matched_count:
            claimed = await database.track_publications.find_one({"_id": existing["_id"], "owner": owner})
            return claimed, owner
    raise PublicationConflict("A preparação sofreu concorrência; tente novamente com a mesma chave")


async def _mark_failed(database, manifest: dict, owner: str, failure_code: str) -> bool:
    result = await database.track_publications.update_one(
        {"_id": manifest["_id"], "state": "preparing", "owner": owner},
        {"$set": {"state": "failed", "failure_code": failure_code, "failed_at": now()},
         "$unset": {"owner": "", "lease_until": ""}},
    )
    return bool(result.matched_count)


async def prepare_track_publication(
    track_id: str,
    operation_id: str,
    note: str,
    publish_children: bool,
    user: dict,
) -> dict:
    """Persist a validated private snapshot without changing live content or pointers.

    ``prepared`` means the stored snapshot and private assessment definitions are
    complete and hash-verified. It is intentionally not activation-eligible:
    current editorial writers do not maintain a cross-collection revision fence.
    """
    _validate_request(track_id, operation_id, note, user)
    source = await _capture_source_snapshot(track_id)
    if not isinstance(source, dict) or not isinstance(source.get("track"), dict):
        raise PublicationPreparationError("Estado editorial incompleto")
    if source["track"].get("_import_state") is not None:
        raise PublicationConflict("A trilha possui uma importação pendente")

    source_snapshot = _validate_and_sort_snapshot(source, track_id)
    source_hash = canonical_snapshot_hash(source_snapshot)
    snapshot = canonicalize_publication_snapshot(source_snapshot, track_id, publish_children)
    snapshot_hash = canonical_snapshot_hash(snapshot)
    if len(_canonical_bytes(snapshot)) > MAX_SNAPSHOT_BYTES:
        raise PublicationPreparationError("Snapshot excede o limite de tamanho permitido")
    source_revision = source_snapshot["track"].get("editorial_revision")
    source_track_version = source_snapshot["track"].get("version", 0)
    if type(source_track_version) is not int or source_track_version < 0:
        raise PublicationPreparationError("Revisão da trilha inválida")
    fingerprint = _fingerprint(
        track_id=track_id, source_hash=source_hash, snapshot_hash=snapshot_hash,
        source_revision=source_revision, publish_children=publish_children,
        note=note, created_by=user["id"],
    )
    database = await _get_db()
    base_document = {
        "source_revision": source_revision,
        "source_track_version": source_track_version,
        "source_consistency": "unverified",
        "activation_eligible": False,
        "activation_block_reason": "editorial_revision_protocol_required",
        "source_hash": source_hash,
        "snapshot_hash": snapshot_hash,
        "stats": {
            "nodes": len(snapshot["nodes"]),
            "blocks": len(snapshot["blocks"]),
            "relations": len(snapshot["relations"]),
        },
        "schema_version": PUBLICATION_SCHEMA_VERSION,
        "note": note,
        "created_by": user["id"],
        "created_by_name": user.get("name", ""),
    }
    manifest, owner = await _claim_operation(
        database, track_id=track_id, operation_id=operation_id,
        fingerprint=fingerprint, base_document=base_document,
    )
    if owner is None:
        try:
            stored = await _load_private_snapshot(manifest)
        except Exception as exc:
            raise PublicationStorageError("A preparação idempotente não passou na verificação") from exc
        if canonical_snapshot_hash(stored) != manifest["snapshot_hash"]:
            raise PublicationStorageError("Hash do snapshot preparado diverge")
        await _verify_private_activities(
            database, track_id, str(manifest["_id"]),
            manifest.get("activity_count", 0), manifest.get("activity_refs_sha256", ""),
        )
        return _safe_result(manifest)

    publication_id = str(manifest["_id"])
    try:
        activities = await _build_activity_publications(
            snapshot, publication_id, source_track_version + 1,
        )
        activity_manifest = await _upsert_private_activities(database, activities)
        await _verify_private_activities(
            database, track_id, publication_id,
            activity_manifest["count"], activity_manifest["sha256"],
        )
        storage_meta = await _store_private_snapshot(manifest["storage_id"], snapshot)
        stored_manifest = {
            "version_id": manifest["storage_id"],
            **storage_meta,
        }
        candidate_manifest = {
            **manifest,
            "snapshot_storage": stored_manifest,
            "stats": base_document["stats"],
        }
        verified_before_ready = await _load_private_snapshot(candidate_manifest)
        if canonical_snapshot_hash(verified_before_ready) != snapshot_hash:
            raise PublicationStorageError("Snapshot privado não passou na verificação antes da confirmação")
        update = await database.track_publications.update_one(
            {
                "_id": manifest["_id"], "state": "preparing", "owner": owner,
                "fingerprint": fingerprint, "storage_id": manifest["storage_id"],
            },
            {"$set": {
                "state": "prepared", "snapshot_storage": stored_manifest,
                "snapshot_complete": True,
                "activity_count": activity_manifest["count"],
                "activity_refs_sha256": activity_manifest["sha256"],
                "prepared_at": now(),
                "visibility": "private", "active": False,
                "activation_eligible": False,
                "source_consistency": "unverified",
            }, "$unset": {"owner": "", "lease_until": ""}},
        )
        if not update.matched_count:
            current = await database.track_publications.find_one({"_id": manifest["_id"]})
            if (current and current.get("state") == "prepared"
                    and current.get("snapshot_complete") is True
                    and current.get("fingerprint") == fingerprint
                    and current.get("snapshot_storage", {}).get("version_id") == manifest["storage_id"]):
                verified = await _load_private_snapshot(current)
                if canonical_snapshot_hash(verified) == current["snapshot_hash"]:
                    await _verify_private_activities(
                        database, track_id, publication_id,
                        current.get("activity_count", 0), current.get("activity_refs_sha256", ""),
                    )
                    return _safe_result(current)
            await _delete_private_snapshot(manifest["storage_id"])
            raise PublicationConflict("A preparação perdeu sua posse antes da confirmação")
        prepared = await database.track_publications.find_one({
            "_id": manifest["_id"], "state": "prepared", "fingerprint": fingerprint,
        })
        if not prepared:
            raise PublicationStorageError("A confirmação da preparação não pôde ser lida")
        verified = await _load_private_snapshot(prepared)
        if canonical_snapshot_hash(verified) != snapshot_hash:
            raise PublicationStorageError("Snapshot persistido diverge do hash canônico")
        return _safe_result(prepared)
    except Exception as exc:
        current = await database.track_publications.find_one({"_id": manifest["_id"]})
        # Acknowledgement may be lost after MongoDB committed the final state.
        # Never delete the chunks of a manifest that is already prepared.
        if current and current.get("state") == "prepared" and current.get("snapshot_complete") is True:
            try:
                verified = await _load_private_snapshot(current)
                if canonical_snapshot_hash(verified) == current.get("snapshot_hash"):
                    await _verify_private_activities(
                        database, track_id, publication_id,
                        current.get("activity_count", 0), current.get("activity_refs_sha256", ""),
                    )
                    return _safe_result(current)
            except Exception:
                raise PublicationStorageError("Publicação confirmada não pôde ser verificada") from exc
        failed = await _mark_failed(database, manifest, owner, "private_preparation_failed")
        if failed:
            try:
                await _delete_private_snapshot(manifest["storage_id"])
            except Exception:
                pass
        if isinstance(exc, (PublicationPreparationError, PublicationConflict, PublicationStorageError)):
            raise
        raise PublicationStorageError("Falha ao preparar a publicação privada") from exc


async def _get_prepared_publication(track_id: str, publication_id: str) -> tuple[dict, dict]:
    """Internal integrity-checked retrieval; no public API is registered for it."""
    if (not isinstance(track_id, str) or not _TRACK_ID.fullmatch(track_id)
            or not isinstance(publication_id, str) or not _TRACK_ID.fullmatch(publication_id)):
        raise PublicationPreparationError("Identificador de publicação inválido")
    database = await _get_db()
    manifest = await database.track_publications.find_one({
        "_id": ObjectId(publication_id), "track_id": track_id,
        "state": "prepared", "visibility": "private", "active": False,
        "snapshot_complete": True,
    })
    if not manifest:
        raise PublicationConflict("Publicação privada não encontrada ou incompleta")
    snapshot = await _load_private_snapshot(manifest)
    if canonical_snapshot_hash(snapshot) != manifest.get("snapshot_hash"):
        raise PublicationStorageError("Hash da publicação privada inválido")
    await _verify_private_activities(
        database, track_id, publication_id,
        manifest.get("activity_count", 0), manifest.get("activity_refs_sha256", ""),
    )
    return _safe_result(manifest), snapshot
