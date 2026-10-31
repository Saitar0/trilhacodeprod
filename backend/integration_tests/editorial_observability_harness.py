"""Test-only bridge to one real legacy writer with all dependencies replaced.

This module is intentionally imported only by its integration tests. The
writer source is loaded directly while its application dependencies are
temporarily replaced in ``sys.modules``; no application package, database
client, router, or service startup is imported.
"""

from __future__ import annotations

import asyncio
import builtins
import copy
import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Callable


class SyntheticHTTPException(Exception):
    """Small FastAPI-compatible exception shape for the isolated source load."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass
class FakeBlockCollection:
    """Minimal async collection contract used by ``update_block`` only."""

    document: dict[str, Any]
    trace: list[str]
    update_error: Exception | None = None
    find_error: Exception | None = None
    last_result: dict[str, Any] | None = None
    update_started: asyncio.Event | None = None
    update_release: asyncio.Event | None = None

    async def update_one(self, query: dict[str, Any], update: dict[str, Any]) -> object:
        self.trace.append("update_one")
        if self.update_started is not None:
            self.update_started.set()
        if self.update_release is not None:
            await self.update_release.wait()
        if self.update_error is not None:
            raise self.update_error
        if query.get("_id") == self.document.get("_id"):
            self.document.update(copy.deepcopy(update["$set"]))
        return SimpleNamespace(matched_count=1)

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        self.trace.append("find_one")
        if self.find_error is not None:
            raise self.find_error
        if query.get("_id") != self.document.get("_id"):
            return None
        self.last_result = copy.deepcopy(self.document)
        return self.last_result


@dataclass
class WriterHarness:
    """One invocation surface around the repository's real ``update_block``."""

    update_block: Callable[..., Any]
    collection: FakeBlockCollection
    block_id: str
    data: dict[str, Any]
    user: dict[str, Any]
    trace: list[str] = field(default_factory=list)
    source_path: Path | None = None
    synthetic_module_name: str = ""

    async def invoke(self) -> dict[str, Any] | None:
        return await self.update_block(self.block_id, self.data, self.user)


def _module(name: str, **attributes: Any) -> ModuleType:
    result = ModuleType(name)
    for key, value in attributes.items():
        setattr(result, key, value)
    return result


def load_real_update_block(
    *,
    data: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
    update_error: Exception | None = None,
    find_error: Exception | None = None,
    audit_error: Exception | None = None,
    get_error: Exception | None = None,
    repository_root: Path | None = None,
) -> WriterHarness:
    """Load the real source symbol with only the writer's imports substituted."""

    root = (repository_root or Path(__file__).resolve().parents[2]).resolve()
    source = (root / "backend" / "services" / "blocks.py").resolve()
    if not source.is_file() or root not in source.parents:
        raise FileNotFoundError("the expected repository writer source is unavailable")

    trace: list[str] = []
    collection = FakeBlockCollection(
        document={
            "_id": "synthetic-block-001",
            "track_id": "synthetic-track-001",
            "type": "text",
            "status": "draft",
            "title": "synthetic title",
        },
        trace=trace,
        update_error=update_error,
        find_error=find_error,
    )

    async def get_document(collection_name: str, document_id: str) -> dict[str, Any]:
        trace.append("get_document")
        if get_error is not None:
            raise get_error
        if collection_name != "content_blocks" or document_id != collection.document["_id"]:
            raise LookupError("synthetic document not found")
        return copy.deepcopy(collection.document)

    async def audit(*_args: Any, **_kwargs: Any) -> None:
        trace.append("audit")
        if audit_error is not None:
            raise audit_error

    def now() -> str:
        trace.append("now")
        return "synthetic-time"

    def check_status(status: Any) -> None:
        trace.append("check_status")
        if status not in {None, "draft", "published", "archived"}:
            raise SyntheticHTTPException(400, "invalid synthetic status")

    def oid(value: str) -> str:
        trace.append("oid")
        return value

    database = _module("database", db=SimpleNamespace(content_blocks=collection))
    services_package = _module("services")
    services_package.__path__ = []  # type: ignore[attr-defined]
    common = _module(
        "services.common",
        check_status=check_status,
        get_document=get_document,
        next_order=None,
        validate_reorder=None,
    )
    stubs = {
        "fastapi": _module("fastapi", HTTPException=SyntheticHTTPException),
        "audit": _module("audit", audit=audit),
        "core_utils": _module("core_utils", now=now),
        "database": database,
        "integrity": _module("integrity", reconcile_orphans=None),
        "serialization": _module("serialization", oid=oid),
        "services": services_package,
        "services.common": common,
    }

    module_name = "_trilhacode_12c6_real_blocks_writer"

    def isolated_import(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> ModuleType:
        if level == 0 and name in stubs:
            return stubs[name]
        return builtins.__import__(name, globals, locals, fromlist, level)

    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError("could not create an isolated source loader")
    writer_module = importlib.util.module_from_spec(spec)
    safe_builtins = dict(vars(builtins))
    safe_builtins["__import__"] = isolated_import
    writer_module.__dict__["__builtins__"] = safe_builtins
    # The custom import function exists only in this module's execution namespace.
    # No application modules or global import hooks are changed.
    spec.loader.exec_module(writer_module)
    writer = getattr(writer_module, "update_block", None)
    if not callable(writer) or Path(writer.__code__.co_filename).resolve() != source:
        raise ImportError("loaded symbol is not the repository's update_block source")

    if data is not None:
        # The caller owns this dictionary; the writer's own mutation remains observable.
        supplied_data = data
    else:
        supplied_data = {"status": "draft", "title": "synthetic title"}
    if user is not None:
        supplied_user = user
    else:
        supplied_user = {"id": "synthetic-user"}
    harness = WriterHarness(
        update_block=writer,
        collection=collection,
        block_id="synthetic-block-001",
        data=supplied_data,
        user=supplied_user,
        trace=trace,
        source_path=source,
        synthetic_module_name=module_name,
    )
    return harness


def default_context() -> Any:
    """Static context for W-05's service-level block mutation."""

    from curriculum_contract.editorial_observability import (
        EntryPointKind,
        ObservationContext,
        OperationKind,
        ProtocolPath,
        get_operation_descriptor,
    )

    return ObservationContext(
        operation=get_operation_descriptor(OperationKind.BLOCK_MUTATE),
        entrypoint_kind=EntryPointKind.SERVICE,
        protocol_path=ProtocolPath.LEGACY_SERVICE,
    )
