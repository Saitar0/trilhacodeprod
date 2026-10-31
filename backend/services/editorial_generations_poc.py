"""Isolated PoC for append-only editorial generations on MongoDB standalone.

This module is deliberately not wired into application routes or production
publication pointers. A sealed generation is selected only through a separate
PoC head document. Chunks are append-only and a sealed manifest references an
exact, fenced set of chunk IDs, so delayed writes from an old writer can only
create unreachable orphan chunks.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable
from uuid import uuid4

SCHEMA_VERSION = 1
CHUNK_BYTES = 512 * 1024
MAX_SNAPSHOT_BYTES = 128 * 1024 * 1024
MAX_SELECTION_RECEIPTS = 256
LEASE_DURATION = timedelta(minutes=2)
_OPERATION_ID = re.compile(r"[A-Za-z0-9:_-]{8,96}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z0-9._:-]{1,128}\Z")
_PRIVATE_KEYS = {
    "answer", "answers", "answerkey", "correct", "correctindex",
    "correctoptionid", "correctanswer", "iscorrect", "iscorrectanswer",
    "correctness", "gabarito", "solution", "solutions",
    "explanation", "feedback", "feedbackprivate", "privatefeedback",
    "tests", "hiddentests", "evaluator", "token", "writerid",
    "fencingtoken", "contenthash", "manifesthash", "sourcehash",
    "leaseuntil", "operationid", "fingerprint", "activationeligible",
    "sha256", "hash", "generationid", "owner", "writer",
}


class GenerationError(RuntimeError):
    """Base class for expected PoC failures."""


class GenerationConflict(GenerationError):
    """The operation is stale, conflicting, or no longer owns its fence."""


class GenerationInvalid(GenerationError):
    """A candidate snapshot or sealed manifest is invalid."""


class GenerationNotFound(GenerationError):
    """There is no readable selected generation."""


@dataclass(frozen=True)
class GenerationHandle:
    track_id: str
    generation_id: str
    operation_id: str
    writer_id: str
    fencing_token: int
    base_generation_id: str | None
    base_pointer_revision: int
    fingerprint: str


Failpoint = Callable[[str, dict[str, Any]], Any | Awaitable[Any]]


def _canonical_value(value: Any, depth: int = 0) -> Any:
    if depth > 64:
        raise GenerationInvalid("Snapshot excede a profundidade permitida")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise GenerationInvalid("Snapshot contém chave que não é texto")
        return {key: _canonical_value(value[key], depth + 1) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item, depth + 1) for item in value]
    if isinstance(value, datetime):
        normalized = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        return normalized.astimezone(timezone.utc).isoformat()
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise GenerationInvalid("Snapshot contém número não finito")
        return value
    raise GenerationInvalid("Snapshot contém valor fora do contrato JSON da PoC")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _canonical_value(value), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        if isinstance(exc, GenerationInvalid):
            raise
        raise GenerationInvalid("Snapshot não pode ser canonicalizado") from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _row_id(row: dict[str, Any], label: str) -> str:
    value = row.get("id", row.get("_id"))
    if not isinstance(value, str) or not value.strip():
        raise GenerationInvalid(f"Identificador inválido em {label}")
    return value


def canonicalize_snapshot(snapshot: dict[str, Any], track_id: str) -> dict[str, Any]:
    """Validate cross-references and impose stable entity ordering."""
    value = _canonical_value(snapshot)
    if not isinstance(value, dict) or not isinstance(value.get("track"), dict):
        raise GenerationInvalid("Snapshot incompleto: trilha ausente")
    if value["track"].get("id", value["track"].get("_id")) != track_id:
        raise GenerationInvalid("Snapshot incompatível: trilha divergente")
    if value["track"].get("_import_state") is not None:
        raise GenerationConflict("Trilha com importação pendente não pode gerar candidato")
    if value["track"].get("status") not in {None, "draft", "published", "archived"}:
        raise GenerationInvalid("Status da trilha inválido")
    for name in ("nodes", "blocks", "relations"):
        if not isinstance(value.get(name), list) or any(not isinstance(row, dict) for row in value[name]):
            raise GenerationInvalid(f"Snapshot incompleto: {name}")

    nodes = value["nodes"]
    node_ids = [_row_id(row, "nodes") for row in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise GenerationInvalid("Snapshot contém IDs de nós duplicados")
    by_id = dict(zip(node_ids, nodes, strict=True))
    for row in nodes:
        if row.get("track_id") != track_id:
            raise GenerationInvalid("Snapshot contém nó de outra trilha")
        if row.get("status") not in {None, "draft", "published", "archived"}:
            raise GenerationInvalid("Status de nó inválido")
        if row.get("parent_id") and row["parent_id"] not in by_id:
            raise GenerationInvalid("Snapshot contém pai inexistente")
        _sort_order(row)

    paths: dict[str, tuple[Any, ...]] = {}
    visiting: set[str] = set()

    def path_for(identifier: str) -> tuple[Any, ...]:
        if identifier in paths:
            return paths[identifier]
        if identifier in visiting:
            raise GenerationInvalid("Snapshot contém ciclo na hierarquia")
        visiting.add(identifier)
        row = by_id[identifier]
        part = (_sort_order(row), identifier)
        parent = row.get("parent_id")
        result = path_for(parent) + (part,) if parent else (part,)
        visiting.remove(identifier)
        paths[identifier] = result
        return result

    value["nodes"] = sorted(nodes, key=lambda row: path_for(_row_id(row, "nodes")))

    blocks = value["blocks"]
    block_ids = [_row_id(row, "blocks") for row in blocks]
    if len(block_ids) != len(set(block_ids)):
        raise GenerationInvalid("Snapshot contém IDs de blocos duplicados")
    for row in blocks:
        if row.get("track_id") != track_id or row.get("node_id") not in by_id:
            raise GenerationInvalid("Bloco sem trilha ou nó correspondente")
        if row.get("status") not in {None, "draft", "published", "archived"}:
            raise GenerationInvalid("Status de bloco inválido")
        _sort_order(row)
    value["blocks"] = sorted(
        blocks, key=lambda row: (row["node_id"], _sort_order(row), _row_id(row, "blocks")),
    )

    relations = value["relations"]
    relation_keys: set[tuple[str, str, str]] = set()
    relation_ids: set[str] = set()
    for row in relations:
        if row.get("track_id") != track_id:
            raise GenerationInvalid("Relação de outra trilha")
        if row.get("node_id") not in by_id or row.get("target_id") not in by_id:
            raise GenerationInvalid("Relação referencia nó inexistente")
        relation_type = row.get("type")
        if not isinstance(relation_type, str) or not relation_type:
            raise GenerationInvalid("Relação sem tipo")
        if row.get("id") is not None:
            identifier = _row_id(row, "relations")
            if identifier in relation_ids:
                raise GenerationInvalid("Snapshot contém IDs de relações duplicados")
            relation_ids.add(identifier)
        key = (row["node_id"], row["target_id"], relation_type)
        if key in relation_keys:
            raise GenerationInvalid("Snapshot contém relações duplicadas")
        relation_keys.add(key)
    value["relations"] = sorted(relations, key=_canonical_bytes)
    return value


def _sort_order(row: dict[str, Any]) -> float:
    order = row.get("order", 0)
    if isinstance(order, bool) or not isinstance(order, (int, float)) or not math.isfinite(order):
        raise GenerationInvalid("Ordem editorial inválida")
    return float(order)


def _operation_fingerprint(track_id: str, content_hash: str) -> str:
    return _sha256(_canonical_bytes({
        "track_id": track_id,
        "schema_version": SCHEMA_VERSION,
        "content_hash": content_hash,
    }))


def _manifest_payload(document: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "generation_id", "track_id", "base_generation_id", "base_pointer_revision",
        "operation_id", "schema_version", "generation_revision", "content_hash",
        "fencing_token", "chunk_count", "chunk_refs", "activity_refs", "validation",
    )
    return {field: document.get(field) for field in fields}


def _duplicate_key(exc: Exception) -> bool:
    return getattr(exc, "code", None) == 11000 or "duplicate key" in str(exc).lower()


def _dotted_get(document: dict[str, Any], path: str) -> Any:
    value: Any = document
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _safe_generation(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "track_id": document["track_id"],
        "generation_id": document["generation_id"],
        "base_generation_id": document.get("base_generation_id"),
        "state": document["state"],
        "schema_version": document["schema_version"],
        "generation_revision": document.get("generation_revision", 0),
        "validation": dict(document.get("validation", {})),
    }


async def _call_failpoint(failpoint: Failpoint | None, stage: str, **context: Any) -> None:
    if failpoint is None:
        return
    result = failpoint(stage, context)
    if inspect.isawaitable(result):
        await result


class EditorialGenerationsPoC:
    """Database-injected prototype; never obtains the application's global DB."""

    def __init__(self, database: Any, clock: Callable[[], datetime] | None = None):
        self.generations = database.poc_editorial_generations
        self.chunks = database.poc_editorial_generation_chunks
        self.manifests = database.poc_editorial_generation_manifests
        self.heads = database.poc_editorial_generation_heads
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def index_specs() -> tuple[tuple[str, list[tuple[str, int]], dict[str, Any]], ...]:
        """Explicitly PoC-only indexes; not added to production ensure_indexes."""
        return (
            ("poc_editorial_generations", [("track_id", 1), ("operation_id", 1)],
             {"unique": True, "name": "poc_one_generation_per_operation"}),
            ("poc_editorial_generations", [("track_id", 1), ("state", 1), ("created_at", -1)],
             {"name": "poc_generation_state_lookup"}),
            ("poc_editorial_generation_chunks", [("generation_id", 1), ("fencing_token", 1), ("seq", 1)],
             {"unique": True, "name": "poc_one_chunk_per_fence_sequence"}),
            ("poc_editorial_generation_manifests", [("track_id", 1), ("generation_id", 1)],
             {"unique": True, "name": "poc_one_immutable_manifest_per_generation"}),
            ("poc_editorial_generation_heads", [("track_id", 1)],
             {"unique": True, "name": "poc_one_head_per_track"}),
        )

    @classmethod
    async def ensure_poc_indexes(cls, database: Any) -> None:
        for collection, keys, options in cls.index_specs():
            await database[collection].create_index(keys, **options)

    async def _ensure_head(self, track_id: str) -> dict[str, Any]:
        try:
            await self.heads.update_one(
                {"_id": track_id},
                {"$setOnInsert": {
                    "_id": track_id, "track_id": track_id, "active_generation_id": None,
                    "revision": 0, "selection_receipts": {},
                }},
                upsert=True,
            )
        except Exception as exc:
            if not _duplicate_key(exc):
                raise
        head = await self.heads.find_one({"_id": track_id})
        if not head:
            raise GenerationConflict("Ponteiro experimental não pôde ser inicializado")
        return head

    async def begin(
        self,
        *,
        track_id: str,
        operation_id: str,
        writer_id: str,
        snapshot: dict[str, Any],
        lease: timedelta = LEASE_DURATION,
    ) -> GenerationHandle:
        if not isinstance(track_id, str) or not _IDENTIFIER.fullmatch(track_id):
            raise GenerationInvalid("track_id inválido")
        if not isinstance(operation_id, str) or not _OPERATION_ID.fullmatch(operation_id):
            raise GenerationInvalid("operation_id inválido")
        if not isinstance(writer_id, str) or not _IDENTIFIER.fullmatch(writer_id):
            raise GenerationInvalid("writer_id inválido")
        if lease <= timedelta(0) or lease > timedelta(hours=1):
            raise GenerationInvalid("lease fora do limite da PoC")

        canonical = canonicalize_snapshot(snapshot, track_id)
        raw = _canonical_bytes(canonical)
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise GenerationInvalid("Snapshot excede o limite da PoC")
        fingerprint = _operation_fingerprint(track_id, _sha256(raw))
        await self._ensure_head(track_id)

        existing = await self.generations.find_one({"track_id": track_id, "operation_id": operation_id})
        if existing:
            if existing.get("fingerprint") != fingerprint:
                raise GenerationConflict("operation_id reutilizada com conteúdo diferente")
            if existing.get("state") in {"sealing", "sealed"}:
                return self._handle(existing)
            if existing.get("state") != "building":
                raise GenerationConflict("Operação não pode ser retomada")
            if existing.get("lease_until") > self.clock():
                if existing.get("writer_id") != writer_id:
                    raise GenerationConflict("Outro escritor ainda possui a geração")
                return self._handle(existing)
            old_fence = existing["fencing_token"]
            new_lease = self.clock() + lease
            result = await self.generations.update_one(
                {"_id": existing["_id"], "state": "building", "fencing_token": old_fence,
                 "lease_until": {"$lte": self.clock()}},
                {"$set": {"writer_id": writer_id, "lease_until": new_lease}, "$inc": {"fencing_token": 1}},
            )
            if not result.matched_count:
                raise GenerationConflict("Geração foi retomada concorrentemente")
            claimed = await self.generations.find_one({"_id": existing["_id"]})
            return self._handle(claimed)

        head = await self._ensure_head(track_id)
        generation_id = uuid4().hex
        document = {
            "_id": generation_id,
            "track_id": track_id,
            "generation_id": generation_id,
            "base_generation_id": head.get("active_generation_id"),
            "base_pointer_revision": head["revision"],
            "operation_id": operation_id,
            "writer_id": writer_id,
            "fencing_token": 1,
            "fingerprint": fingerprint,
            "schema_version": SCHEMA_VERSION,
            "state": "building",
            "generation_revision": 0,
            "created_at": self.clock(),
            "lease_until": self.clock() + lease,
        }
        try:
            await self.generations.insert_one(document)
        except Exception as exc:
            if not _duplicate_key(exc):
                raise
            raced = await self.generations.find_one({"track_id": track_id, "operation_id": operation_id})
            if not raced or raced.get("fingerprint") != fingerprint:
                raise GenerationConflict("Conflito ao registrar operation_id") from exc
            if raced.get("state") == "building" and raced.get("lease_until") > self.clock():
                if raced.get("writer_id") != writer_id:
                    raise GenerationConflict("Outro escritor ainda possui a geração") from exc
            return self._handle(raced)
        return self._handle(document)

    @staticmethod
    def _handle(document: dict[str, Any]) -> GenerationHandle:
        return GenerationHandle(
            track_id=document["track_id"], generation_id=document["generation_id"],
            operation_id=document["operation_id"], writer_id=document["writer_id"],
            fencing_token=document["fencing_token"],
            base_generation_id=document.get("base_generation_id"),
            base_pointer_revision=document["base_pointer_revision"],
            fingerprint=document["fingerprint"],
        )

    async def _assert_writer(self, handle: GenerationHandle) -> dict[str, Any]:
        document = await self.generations.find_one({"_id": handle.generation_id, "track_id": handle.track_id})
        if (not document or document.get("state") != "building"
                or document.get("writer_id") != handle.writer_id
                or document.get("fencing_token") != handle.fencing_token
                or document.get("lease_until") <= self.clock()):
            raise GenerationConflict("Escritor perdeu a posse/fence da geração")
        return document

    async def _append_chunk(
        self, handle: GenerationHandle, seq: int, data: bytes,
        failpoint: Failpoint | None,
    ) -> dict[str, Any]:
        await self._assert_writer(handle)
        chunk_id = f"{handle.generation_id}:{handle.fencing_token}:{seq}"
        digest = _sha256(data)
        document = {
            "_id": chunk_id, "generation_id": handle.generation_id,
            "fencing_token": handle.fencing_token, "seq": seq,
            "sha256": digest, "data": data,
        }
        # A late old-fence insert is allowed to become an orphan, but the seal
        # can only name chunks from its own fence and exact sequence list.
        await _call_failpoint(
            failpoint, "after_chunk_ownership_check", seq=seq,
            generation_id=handle.generation_id, fencing_token=handle.fencing_token,
        )
        try:
            await self.chunks.insert_one(document)
        except Exception as exc:
            if not _duplicate_key(exc):
                raise
            existing = await self.chunks.find_one({"_id": chunk_id})
            if not existing or existing.get("sha256") != digest or existing.get("data") != data:
                raise GenerationConflict("Chunk idempotente diverge do conteúdo já gravado") from exc
        return {"_id": chunk_id, "seq": seq, "sha256": digest, "size": len(data)}

    async def prepare(
        self,
        handle: GenerationHandle,
        snapshot: dict[str, Any],
        *,
        failpoint: Failpoint | None = None,
    ) -> dict[str, Any]:
        canonical = canonicalize_snapshot(snapshot, handle.track_id)
        raw = _canonical_bytes(canonical)
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise GenerationInvalid("Snapshot excede o limite da PoC")
        content_hash = _sha256(raw)
        if _operation_fingerprint(handle.track_id, content_hash) != handle.fingerprint:
            raise GenerationConflict("Conteúdo diverge do fingerprint da operação")

        current = await self.generations.find_one({"_id": handle.generation_id})
        if current and current.get("state") == "sealed":
            intent = current.get("seal_intent") or {}
            if intent.get("content_hash") != content_hash:
                raise GenerationConflict("Geração selada não pode receber outro conteúdo")
            manifest = await self.manifests.find_one({"_id": handle.generation_id})
            if not manifest:
                raise GenerationInvalid("Geração marcada como selada sem manifesto imutável")
            await self._load_verified(manifest)
            return _safe_generation(manifest)
        if current and current.get("state") == "sealing":
            return await self._complete_sealing(current, failpoint=failpoint)
        await self._assert_writer(handle)
        await _call_failpoint(failpoint, "before_first_chunk", generation_id=handle.generation_id)

        parts = [raw[index:index + CHUNK_BYTES] for index in range(0, len(raw), CHUNK_BYTES)] or [b""]
        chunk_refs = []
        for seq, part in enumerate(parts):
            chunk_refs.append(await self._append_chunk(handle, seq, part, failpoint))
            await _call_failpoint(
                failpoint, "after_chunk_write", seq=seq,
                generation_id=handle.generation_id, fencing_token=handle.fencing_token,
            )

        rebuilt = bytearray()
        for expected in chunk_refs:
            stored = await self.chunks.find_one({
                "_id": expected["_id"], "generation_id": handle.generation_id,
                "fencing_token": handle.fencing_token,
            })
            if (not stored or stored.get("seq") != expected["seq"]
                    or _sha256(stored.get("data", b"")) != expected["sha256"]
                    or stored["sha256"] != expected["sha256"]):
                raise GenerationInvalid("Chunk ausente ou corrompido antes da selagem")
            rebuilt.extend(stored["data"])
        if _sha256(bytes(rebuilt)) != content_hash or bytes(rebuilt) != raw:
            raise GenerationInvalid("Conteúdo reconstruído diverge do snapshot canônico")

        activity_refs = sorted(
            _row_id(block, "blocks") for block in canonical["blocks"] if block.get("type") == "quiz"
        )
        validation = {
            "structural_valid": True,
            "references_valid": True,
            "import_clear": True,
            "activity_count": len(activity_refs),
        }
        sealed_at = self.clock()
        seal_document = {
            "_id": handle.generation_id,
            "generation_id": handle.generation_id,
            "track_id": handle.track_id,
            "base_generation_id": handle.base_generation_id,
            "base_pointer_revision": handle.base_pointer_revision,
            "operation_id": handle.operation_id,
            "schema_version": SCHEMA_VERSION,
            "generation_revision": 1,
            "fencing_token": handle.fencing_token,
            "content_hash": content_hash,
            "chunk_count": len(chunk_refs),
            "chunk_refs": chunk_refs,
            "activity_refs": activity_refs,
            "validation": validation,
            "state": "sealed",
            "created_at": current["created_at"],
            "sealed_at": sealed_at,
        }
        manifest_hash = _sha256(_canonical_bytes(_manifest_payload(seal_document)))
        seal_document["manifest_hash"] = manifest_hash
        await _call_failpoint(failpoint, "before_seal", generation_id=handle.generation_id)
        selector = {
            "_id": handle.generation_id,
            "track_id": handle.track_id,
            "state": "building",
            "writer_id": handle.writer_id,
            "fencing_token": handle.fencing_token,
            "fingerprint": handle.fingerprint,
            "lease_until": {"$gt": sealed_at},
        }
        update = {"$set": {
            "state": "sealing", "seal_intent": seal_document,
            "manifest_hash": manifest_hash,
        }, "$unset": {"lease_until": ""}}
        result = await self.generations.update_one(selector, update)
        if not result.matched_count:
            current = await self.generations.find_one({"_id": handle.generation_id})
            if (current and current.get("state") in {"sealing", "sealed"}
                    and current.get("manifest_hash") == manifest_hash):
                return await self._complete_sealing(current, failpoint=failpoint)
            raise GenerationConflict("Fencing/CAS impediu a selagem desta geração")
        sealing = await self.generations.find_one({"_id": handle.generation_id, "state": "sealing"})
        if not sealing:
            raise GenerationInvalid("Intenção de selagem não foi observada")
        return await self._complete_sealing(sealing, failpoint=failpoint)

    async def _complete_sealing(
        self, build: dict[str, Any], *, failpoint: Failpoint | None = None,
    ) -> dict[str, Any]:
        """Idempotently publish the immutable manifest after a fenced seal intent."""
        if build.get("state") not in {"sealing", "sealed"}:
            raise GenerationConflict("Geração não possui intenção de selagem")
        intent = build.get("seal_intent")
        if not isinstance(intent, dict) or intent.get("generation_id") != build.get("generation_id"):
            raise GenerationInvalid("Intenção de selagem ausente ou incompatível")
        await self._load_verified(intent)
        existing = await self.manifests.find_one({"_id": build["generation_id"]})
        if existing:
            if (existing.get("manifest_hash") != intent.get("manifest_hash")
                    or _canonical_bytes(_manifest_payload(existing))
                    != _canonical_bytes(_manifest_payload(intent))):
                raise GenerationInvalid("Manifesto append-only diverge da intenção selada")
        else:
            await _call_failpoint(failpoint, "after_seal_intent", generation_id=build["generation_id"])
            try:
                await self.manifests.insert_one(intent)
            except Exception as exc:
                if not _duplicate_key(exc):
                    raise
                existing = await self.manifests.find_one({"_id": build["generation_id"]})
                if (not existing or existing.get("manifest_hash") != intent.get("manifest_hash")
                        or _canonical_bytes(_manifest_payload(existing))
                        != _canonical_bytes(_manifest_payload(intent))):
                    raise GenerationConflict("Conflito ao gravar manifesto imutável") from exc
            await _call_failpoint(failpoint, "after_manifest_insert", generation_id=build["generation_id"])

        result = await self.generations.update_one(
            {"_id": build["generation_id"], "state": "sealing",
             "manifest_hash": intent["manifest_hash"],
             "fencing_token": intent["fencing_token"]},
            {"$set": {
                "state": "sealed", "sealed_at": intent["sealed_at"],
                "generation_revision": intent["generation_revision"],
                "content_hash": intent["content_hash"],
                "chunk_count": intent["chunk_count"],
                "validation": intent["validation"],
            }},
        )
        if not result.matched_count:
            latest = await self.generations.find_one({"_id": build["generation_id"]})
            if not latest or latest.get("state") != "sealed" or latest.get("manifest_hash") != intent["manifest_hash"]:
                raise GenerationConflict("Manifesto gravado, mas estado de recuperação divergiu")
        sealed = await self.manifests.find_one({"_id": build["generation_id"]})
        if not sealed:
            raise GenerationInvalid("Manifesto imutável não pôde ser confirmado")
        await self._load_verified(sealed)
        await _call_failpoint(failpoint, "after_seal", generation_id=build["generation_id"])
        return _safe_generation(sealed)

    async def abandon(self, handle: GenerationHandle) -> bool:
        result = await self.generations.update_one(
            {"_id": handle.generation_id, "track_id": handle.track_id, "state": "building",
             "writer_id": handle.writer_id, "fencing_token": handle.fencing_token},
            {"$set": {"state": "abandoned", "abandoned_at": self.clock()},
             "$unset": {"lease_until": ""}},
        )
        return bool(result.matched_count)

    async def _load_verified(self, generation: dict[str, Any]) -> dict[str, Any]:
        if generation.get("state") != "sealed" or generation.get("schema_version") != SCHEMA_VERSION:
            raise GenerationInvalid("Geração não está selada em esquema suportado")
        validation = generation.get("validation", {})
        if (validation.get("structural_valid") is not True
                or validation.get("references_valid") is not True
                or validation.get("import_clear") is not True):
            raise GenerationInvalid("Geração não passou pela validação estrutural")
        expected_manifest_hash = _sha256(_canonical_bytes(_manifest_payload(generation)))
        if generation.get("manifest_hash") != expected_manifest_hash:
            raise GenerationInvalid("Manifesto selado foi alterado")
        refs = generation.get("chunk_refs")
        if not isinstance(refs, list) or len(refs) != generation.get("chunk_count") or not refs:
            raise GenerationInvalid("Manifesto de chunks incompleto")
        raw = bytearray()
        for seq, ref in enumerate(refs):
            if ref.get("seq") != seq:
                raise GenerationInvalid("Sequência de chunks não é contígua")
            stored = await self.chunks.find_one({
                "_id": ref.get("_id"), "generation_id": generation["generation_id"],
                "fencing_token": generation["fencing_token"], "seq": seq,
            })
            if not stored or stored.get("sha256") != ref.get("sha256"):
                raise GenerationInvalid("Chunk selado ausente")
            data = stored.get("data")
            if not isinstance(data, bytes) or _sha256(data) != ref.get("sha256"):
                raise GenerationInvalid("Chunk selado corrompido")
            raw.extend(data)
        content = bytes(raw)
        if _sha256(content) != generation.get("content_hash"):
            raise GenerationInvalid("Hash de conteúdo divergente")
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise GenerationInvalid("Conteúdo selado não é JSON válido") from exc
        canonical = canonicalize_snapshot(parsed, generation["track_id"])
        if _canonical_bytes(canonical) != content:
            raise GenerationInvalid("Snapshot selado não está canonicalizado")
        expected_activities = sorted(
            _row_id(block, "blocks") for block in canonical["blocks"] if block.get("type") == "quiz"
        )
        if expected_activities != generation.get("activity_refs"):
            raise GenerationInvalid("Referências de atividades divergem do snapshot selado")
        return canonical

    async def select_active(
        self,
        *,
        track_id: str,
        generation_id: str,
        operation_id: str,
        failpoint: Failpoint | None = None,
    ) -> dict[str, Any]:
        if not isinstance(operation_id, str) or not _OPERATION_ID.fullmatch(operation_id):
            raise GenerationInvalid("operation_id de seleção inválida")
        generation = await self.manifests.find_one({
            "_id": generation_id, "generation_id": generation_id, "track_id": track_id,
        })
        if not generation or generation.get("state") != "sealed":
            raise GenerationConflict("Somente geração selada pode ser selecionada")
        await self._load_verified(generation)
        head = await self._ensure_head(track_id)
        receipt_path = f"selection_receipts.{operation_id}"
        receipt = _dotted_get(head, receipt_path)
        fingerprint = _sha256(_canonical_bytes({
            "track_id": track_id, "generation_id": generation_id,
            "base_revision": generation["base_pointer_revision"],
        }))
        if receipt is not None:
            if receipt.get("generation_id") != generation_id or receipt.get("fingerprint") != fingerprint:
                raise GenerationConflict("Chave de seleção reutilizada com outro destino")
            return {"track_id": track_id, "generation_id": generation_id,
                    "revision": receipt["revision"], "replayed": True}

        if (generation.get("base_generation_id") != head.get("active_generation_id")
                or generation.get("base_pointer_revision") != head.get("revision")):
            raise GenerationConflict("Geração baseada em ponteiro obsoleto")
        receipts = head.get("selection_receipts") or {}
        if len(receipts) >= MAX_SELECTION_RECEIPTS:
            raise GenerationConflict("Limite de recibos da PoC atingido; seleção bloqueada")
        next_revision = head["revision"] + 1
        receipt_value = {
            "generation_id": generation_id, "fingerprint": fingerprint,
            "revision": next_revision, "selected_at": self.clock(),
        }
        await _call_failpoint(failpoint, "before_pointer_cas", track_id=track_id)
        result = await self.heads.update_one(
            {"_id": track_id, "track_id": track_id,
             "active_generation_id": head.get("active_generation_id"),
             "revision": head["revision"], receipt_path: {"$exists": False}},
            {"$set": {
                "active_generation_id": generation_id,
                "revision": next_revision,
                "last_selection_operation_id": operation_id,
                receipt_path: receipt_value,
            }},
        )
        if not result.matched_count:
            latest = await self.heads.find_one({"_id": track_id})
            raced_receipt = _dotted_get(latest or {}, receipt_path)
            if (raced_receipt and raced_receipt.get("generation_id") == generation_id
                    and raced_receipt.get("fingerprint") == fingerprint):
                return {"track_id": track_id, "generation_id": generation_id,
                        "revision": raced_receipt["revision"], "replayed": True}
            raise GenerationConflict("Ponteiro mudou durante seleção; candidato obsoleto")
        await _call_failpoint(failpoint, "after_pointer_cas", track_id=track_id, revision=next_revision)
        return {"track_id": track_id, "generation_id": generation_id,
                "revision": next_revision, "replayed": False}

    async def read_active_public(self, track_id: str) -> dict[str, Any]:
        # Resolve the head exactly once. Every subsequent read is pinned to this
        # generation ID; there is intentionally no fallback to live collections.
        head = await self.heads.find_one({"_id": track_id, "track_id": track_id})
        if not head or not head.get("active_generation_id"):
            raise GenerationNotFound("Nenhuma geração experimental selecionada")
        generation_id = head["active_generation_id"]
        generation = await self.manifests.find_one({
            "_id": generation_id, "track_id": track_id, "generation_id": generation_id,
        })
        if not generation:
            raise GenerationInvalid("Geração selecionada ausente; fallback proibido")
        snapshot = await self._load_verified(generation)
        return project_public_snapshot(snapshot, generation_id)


def _private_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return (
        normalized in _PRIVATE_KEYS
        or normalized.startswith(("hidden", "answer", "correct"))
        or any(part in normalized for part in ("private", "secret", "token", "hash", "digest", "fingerprint"))
    )


def _public_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _public_value(item) for key, item in value.items()
                if not key.startswith("_") and not _private_key(key)}
    if isinstance(value, list):
        return [_public_value(item) for item in value]
    return value


def project_public_snapshot(snapshot: dict[str, Any], generation_id: str) -> dict[str, Any]:
    """Project only the sealed snapshot; apply visibility to its captured state."""
    track = snapshot["track"]
    if track.get("status") != "published" or track.get("visibility") != "public":
        raise GenerationNotFound("Geração sem trilha publicável")
    source_nodes = {_row_id(node, "nodes"): node for node in snapshot["nodes"]}
    visible: set[str] = set()

    def node_is_visible(identifier: str, visiting: set[str] | None = None) -> bool:
        if identifier in visible:
            return True
        node = source_nodes.get(identifier)
        if not node or node.get("status") != "published":
            return False
        parent = node.get("parent_id")
        if parent:
            active = visiting or set()
            if identifier in active:
                return False
            active.add(identifier)
            if not node_is_visible(parent, active):
                return False
            active.remove(identifier)
        visible.add(identifier)
        return True

    for identifier in source_nodes:
        node_is_visible(identifier)
    public_track_fields = {
        "id", "title", "slug", "subtitle", "description", "cover_url",
        "difficulty", "hierarchy", "level_labels",
    }
    public_node_fields = {
        "id", "track_id", "parent_id", "kind", "title", "summary", "description",
        "guidance", "notes", "pedagogical_type", "requirement", "depth",
        "estimated_minutes", "tag_ids", "release", "order",
    }
    public_block_fields = {"id", "track_id", "node_id", "type", "title", "order", "data"}
    public_relation_fields = {"id", "track_id", "node_id", "target_id", "type", "enforced", "note"}

    def select_fields(row: dict[str, Any], fields: set[str]) -> dict[str, Any]:
        return {key: _public_value(value) for key, value in row.items() if key in fields}

    nodes = [select_fields(node, public_node_fields) for node in snapshot["nodes"]
             if _row_id(node, "nodes") in visible]
    blocks = [select_fields(block, public_block_fields) for block in snapshot["blocks"]
              if block.get("node_id") in visible and block.get("status") == "published"]
    relations = [select_fields(relation, public_relation_fields) for relation in snapshot["relations"]
                 if relation.get("node_id") in visible and relation.get("target_id") in visible]
    public_track = {key: _public_value(value) for key, value in track.items()
                    if key in public_track_fields}
    return {
        "generation_id": generation_id,
        "track": public_track,
        "nodes": nodes,
        "blocks": blocks,
        "relations": relations,
    }
