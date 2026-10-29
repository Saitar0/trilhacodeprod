"""Disconnected, recoverable preparation service for Beta 5 curriculum packages.

The service takes an explicitly supplied database handle and writes only to
``_beta5_staging_*`` collections. It does not import the application database,
routes, active writers, startup, or publication services. It has no promotion or
published state.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from pymongo.errors import DuplicateKeyError

from curriculum_contract.beta_staging_contract import (
    StagedRecord,
    StageState,
    StagingPackage,
)


class StagingError(RuntimeError):
    """Base error for isolated staging operations."""


class StagingIdentityConflict(StagingError):
    """A batch identity was reused for a different validated payload."""


class StagingIntegrityError(StagingError):
    """Persisted staging documents do not match the validated manifest."""


class InjectedStagingFailure(StagingError):
    """Test-only failure raised at a deterministic staging checkpoint."""


class StagingOutcome:
    __slots__ = ("batch_id", "state", "payload_sha256", "record_count", "resumed")

    def __init__(self, batch_id: str, payload_sha256: str, record_count: int, resumed: bool) -> None:
        self.batch_id = batch_id
        self.state = StageState.PREPARED
        self.payload_sha256 = payload_sha256
        self.record_count = record_count
        self.resumed = resumed


FaultHook = Callable[[str, int, str | None], None | Awaitable[None]]


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


class CurriculumStagingService:
    """Write a validated package into an isolated namespace and resume safely."""

    BATCHES = "_beta5_staging_batches"
    RECORDS = "_beta5_staging_records"
    CHECKPOINTS = "_beta5_staging_checkpoints"
    EVENTS = "_beta5_staging_events"

    def __init__(self, database: Any, *, execution_id: str, owner_token: str) -> None:
        if not re.fullmatch(r"[0-9a-f]{32}", execution_id):
            raise ValueError("Identidade UUID exclusiva da execução Beta 5 obrigatória")
        if len(owner_token) < 32:
            raise ValueError("Marcador de propriedade Beta 5 insuficiente")
        if getattr(database, "name", None) != f"beta5_{execution_id}":
            raise ValueError("Serviço staging aceita somente o banco exclusivo da execução")
        self._database = database
        self._execution_id = execution_id
        self._owner_token = owner_token

    async def _verify_database_owner(self) -> None:
        marker = await self._database["_beta5_test_owner"].find_one({"_id": "owner"})
        if not marker or any(marker.get(key) != value for key, value in {
            "run_id": self._execution_id,
            "owner_token": self._owner_token,
            "database": f"beta5_{self._execution_id}",
        }.items()):
            raise StagingError("Banco staging sem marcador de propriedade da execução Beta 5")

    async def _ensure_indexes(self) -> None:
        await self._database[self.BATCHES].create_index("payload_sha256")
        await self._database[self.RECORDS].create_index(
            [("batch_id", 1), ("record_id", 1)], unique=True, name="beta5_stage_record_identity",
        )
        await self._database[self.CHECKPOINTS].create_index(
            [("batch_id", 1), ("record_id", 1)], unique=True, name="beta5_stage_checkpoint_identity",
        )
        await self._database[self.EVENTS].create_index(
            [("batch_id", 1), ("event_id", 1)], unique=True, name="beta5_stage_event_identity",
        )

    async def _emit_event(
        self,
        *,
        batch_id: str,
        event_id: str,
        event_type: str,
        payload_sha256: str,
        record_id: str | None = None,
        error_code: str | None = None,
    ) -> None:
        query = {"batch_id": batch_id, "event_id": event_id}
        event = {
            "batch_id": batch_id,
            "event_id": event_id,
            "event_type": event_type,
            "record_id": record_id,
            "error_code": error_code,
            "payload_sha256": payload_sha256,
            "execution_id": self._execution_id,
            "at": _now(),
        }
        try:
            await self._database[self.EVENTS].update_one(query, {"$setOnInsert": event}, upsert=True)
        except DuplicateKeyError:
            existing = await self._database[self.EVENTS].find_one(query)
            if not existing or existing.get("payload_sha256") != payload_sha256:
                raise StagingIdentityConflict("Evento concorrente diverge da identidade do lote")

    async def _fault(self, hook: FaultHook | None, point: str, index: int, record_id: str | None) -> None:
        if hook is None:
            return
        outcome = hook(point, index, record_id)
        if inspect.isawaitable(outcome):
            await outcome

    async def _persist_record(
        self,
        batch_id: str,
        record: StagedRecord,
        *,
        fault_hook: FaultHook | None,
        index: int,
    ) -> None:
        record_id = record.record_id
        document_id = f"{batch_id}::{record_id}"
        document = record.model_dump(mode="json")
        record_hash = _canonical_hash(document)
        stored = await self._database[self.RECORDS].find_one({"_id": document_id})
        if stored is None:
            try:
                await self._database[self.RECORDS].insert_one({
                    "_id": document_id,
                    "batch_id": batch_id,
                    "record_id": record_id,
                    "record_sha256": record_hash,
                    "state": "PREPARED",
                    **document,
                })
            except DuplicateKeyError:
                stored = await self._database[self.RECORDS].find_one({"_id": document_id})
        else:
            if stored.get("record_sha256") != record_hash:
                raise StagingIdentityConflict("Registro existente diverge do hash validado")

        stored = stored or await self._database[self.RECORDS].find_one({"_id": document_id})
        if not stored or stored.get("record_sha256") != record_hash:
            raise StagingIdentityConflict("Registro concorrente possui conteúdo divergente")

        await self._fault(fault_hook, "after_document_before_checkpoint", index, record_id)

        checkpoint_id = document_id
        checkpoint = await self._database[self.CHECKPOINTS].find_one({"_id": checkpoint_id})
        if checkpoint and checkpoint.get("record_sha256") != record_hash:
            raise StagingIdentityConflict("Checkpoint existente diverge do conteúdo validado")
        if checkpoint is None:
            try:
                await self._database[self.CHECKPOINTS].update_one(
                    {"_id": checkpoint_id},
                    {"$setOnInsert": {
                        "_id": checkpoint_id,
                        "batch_id": batch_id,
                        "record_id": record_id,
                        "record_sha256": record_hash,
                        "execution_id": self._execution_id,
                        "confirmed_at": _now(),
                    }},
                    upsert=True,
                )
            except DuplicateKeyError:
                pass
            checkpoint = await self._database[self.CHECKPOINTS].find_one({"_id": checkpoint_id})
            if not checkpoint or checkpoint.get("record_sha256") != record_hash:
                raise StagingIdentityConflict("Checkpoint concorrente diverge do conteúdo validado")

    async def prepare(self, package: StagingPackage | dict[str, Any], *, fault_hook: FaultHook | None = None) -> StagingOutcome:
        """Validate all input in memory before the first database write."""
        validated = StagingPackage.model_validate(package.model_dump(mode="python") if isinstance(package, StagingPackage) else package)
        await self._verify_database_owner()
        await self._ensure_indexes()
        batch_id = validated.manifest.batch_id
        payload_sha256 = validated.manifest.payload_sha256
        batches = self._database[self.BATCHES]
        job = await batches.find_one({"_id": batch_id})
        resumed = job is not None
        if job and job.get("payload_sha256") != payload_sha256:
            raise StagingIdentityConflict("Identidade de lote reutilizada com payload diferente")
        if job and job.get("status") == StageState.QUARANTINED.value:
            raise StagingError("Lote em quarentena exige reconciliação explícita")

        if job is None:
            job_document = {
                "_id": batch_id,
                "batch_id": batch_id,
                "payload_sha256": payload_sha256,
                "manifest": validated.manifest.model_dump(mode="json"),
                "status": StageState.VALIDATED.value,
                "execution_id": self._execution_id,
                "created_at": _now(),
                "updated_at": _now(),
            }
            try:
                await batches.insert_one(job_document)
            except DuplicateKeyError:
                job = await batches.find_one({"_id": batch_id})
                if not job or job.get("payload_sha256") != payload_sha256:
                    raise StagingIdentityConflict("Lote concorrente possui outro payload")
                resumed = True
            await self._emit_event(
                batch_id=batch_id, event_id="validated", event_type="VALIDATED", payload_sha256=payload_sha256,
            )
        elif job.get("status") == StageState.PREPARED.value:
            await self._assert_complete(validated)
            return StagingOutcome(batch_id, payload_sha256, len(validated.records), resumed=True)

        await batches.update_one(
            {"_id": batch_id, "payload_sha256": payload_sha256, "status": {"$ne": StageState.QUARANTINED.value}},
            {"$set": {"status": StageState.PREPARING.value, "updated_at": _now()}},
        )
        await self._emit_event(
            batch_id=batch_id, event_id="preparing", event_type="PREPARING", payload_sha256=payload_sha256,
        )

        try:
            for index, record in enumerate(validated.records, start=1):
                await self._fault(fault_hook, "before_record", index, record.record_id)
                await self._persist_record(
                    batch_id, record, fault_hook=fault_hook, index=index,
                )
                await self._emit_event(
                    batch_id=batch_id,
                    event_id=f"record:{record.record_id}",
                    event_type="RECORD_CONFIRMED",
                    payload_sha256=payload_sha256,
                    record_id=record.record_id,
                )
                await self._fault(fault_hook, "after_record", index, record.record_id)
            await self._fault(fault_hook, "before_finalize", len(validated.records), None)
            await self._assert_complete(validated)
            await batches.update_one(
                {"_id": batch_id, "payload_sha256": payload_sha256},
                {"$set": {
                    "status": StageState.PREPARED.value,
                    "prepared_count": len(validated.records),
                    "updated_at": _now(),
                }},
            )
            await self._emit_event(
                batch_id=batch_id, event_id="prepared", event_type="PREPARED", payload_sha256=payload_sha256,
            )
        except Exception as exc:
            current = await batches.find_one({"_id": batch_id})
            if current and current.get("status") != StageState.PREPARED.value:
                record_count = await self._database[self.RECORDS].count_documents({"batch_id": batch_id})
                state = StageState.RECOVERABLE if record_count else StageState.FAILED
                await batches.update_one(
                    {"_id": batch_id, "payload_sha256": payload_sha256},
                    {"$set": {
                        "status": state.value,
                        "last_error_code": type(exc).__name__,
                        "updated_at": _now(),
                    }},
                )
                error_identity = getattr(exc, "record_id", None) or getattr(exc, "point", None) or type(exc).__name__
                await self._emit_event(
                    batch_id=batch_id,
                    event_id=f"recoverable:{error_identity}",
                    event_type=state.value,
                    payload_sha256=payload_sha256,
                    record_id=getattr(exc, "record_id", None),
                    error_code=type(exc).__name__,
                )
            raise

        return StagingOutcome(batch_id, payload_sha256, len(validated.records), resumed=resumed)

    async def _assert_complete(self, package: StagingPackage) -> None:
        batch_id = package.manifest.batch_id
        record_count = await self._database[self.RECORDS].count_documents({"batch_id": batch_id})
        checkpoint_count = await self._database[self.CHECKPOINTS].count_documents({"batch_id": batch_id})
        if record_count != len(package.records) or checkpoint_count != len(package.records):
            raise StagingIntegrityError("Lote staging possui registros ou checkpoints incompletos")
        for record in package.records:
            document_id = f"{batch_id}::{record.record_id}"
            expected_hash = _canonical_hash(record.model_dump(mode="json"))
            stored = await self._database[self.RECORDS].find_one({"_id": document_id})
            checkpoint = await self._database[self.CHECKPOINTS].find_one({"_id": document_id})
            if (
                not stored or stored.get("record_sha256") != expected_hash
                or not checkpoint or checkpoint.get("record_sha256") != expected_hash
            ):
                raise StagingIntegrityError("Hash de registro ou checkpoint não corresponde ao pacote")

    async def inspect_batch(self, batch_id: str) -> dict[str, Any] | None:
        """Return a metadata-only job summary; no staged content is returned."""
        job = await self._database[self.BATCHES].find_one({"_id": batch_id})
        if not job:
            return None
        return {
            "batch_id": job["batch_id"],
            "status": job["status"],
            "payload_sha256": job["payload_sha256"],
            "prepared_count": job.get("prepared_count", 0),
            "last_error_code": job.get("last_error_code"),
        }
