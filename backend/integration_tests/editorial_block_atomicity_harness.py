"""Test-only execution of the repository's real block writer and audit code.

The source modules are executed with a local Mongo database proxy. The active
``database`` module is never imported, and every injected fault is scoped to a
named operation on the phase's disposable database.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Literal


class SyntheticHTTPException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class InjectedFailure(RuntimeError):
    """Fault raised at a deterministic boundary in the test-only proxy."""


@dataclass
class Fault:
    collection: str
    method: str
    timing: Literal["before", "after"]
    error: BaseException
    remaining: int = 1
    skip_matches: int = 0


@dataclass
class OperationControls:
    faults: list[Fault] = field(default_factory=list)
    before_update_barrier: Any | None = None
    trace: list[str] = field(default_factory=list)

    def raise_if_scheduled(self, collection: str, method: str, timing: str) -> None:
        for fault in self.faults:
            if (
                fault.remaining > 0
                and fault.collection == collection
                and fault.method == method
                and fault.timing == timing
            ):
                if fault.skip_matches > 0:
                    fault.skip_matches -= 1
                    continue
                fault.remaining -= 1
                raise fault.error


class CollectionProxy:
    def __init__(self, name: str, collection: Any, controls: OperationControls) -> None:
        self._name = name
        self._collection = collection
        self._controls = controls

    async def _call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        self._controls.trace.append(f"{self._name}.{method}:before")
        self._controls.raise_if_scheduled(self._name, method, "before")
        if method == "update_one" and self._controls.before_update_barrier is not None:
            await self._controls.before_update_barrier.wait()
        result = await getattr(self._collection, method)(*args, **kwargs)
        self._controls.trace.append(f"{self._name}.{method}:persisted")
        self._controls.raise_if_scheduled(self._name, method, "after")
        return result

    async def find_one(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call("find_one", *args, **kwargs)

    async def update_one(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call("update_one", *args, **kwargs)

    async def insert_one(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call("insert_one", *args, **kwargs)


class DatabaseProxy:
    def __init__(self, database: Any, controls: OperationControls) -> None:
        self.client = database.client
        self.name = database.name
        self._database = database
        self._controls = controls
        self._collections: dict[str, CollectionProxy] = {}

    def __getitem__(self, name: str) -> CollectionProxy:
        if name not in self._collections:
            self._collections[name] = CollectionProxy(name, self._database[name], self._controls)
        return self._collections[name]

    def __getattr__(self, name: str) -> CollectionProxy:
        if name.startswith("_"):
            raise AttributeError(name)
        return self[name]


@dataclass
class RealBlockWriterHarness:
    update_block: Any
    database: DatabaseProxy
    controls: OperationControls
    source_path: Path

    async def invoke(self, block_id: str, data: dict[str, Any], user: dict[str, Any]) -> Any:
        return await self.update_block(block_id, data, user)


def _module(name: str, **attributes: Any) -> ModuleType:
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return module


def _execute_source(name: str, path: Path, substitutions: dict[str, ModuleType]) -> ModuleType:
    module = _module(name)
    module.__file__ = str(path)
    safe_builtins = dict(vars(builtins))

    def isolated_import(
        requested: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> ModuleType:
        if level == 0 and requested in substitutions:
            return substitutions[requested]
        return builtins.__import__(requested, globals, locals, fromlist, level)

    safe_builtins["__import__"] = isolated_import
    module.__dict__["__builtins__"] = safe_builtins
    source = path.read_text(encoding="utf-8")
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def load_real_update_block(
    database: Any,
    *,
    controls: OperationControls | None = None,
    repository_root: Path | None = None,
) -> RealBlockWriterHarness:
    """Load the exact service/audit sources without importing active app modules."""

    root = (repository_root or Path(__file__).resolve().parents[2]).resolve()
    backend = root / "backend"
    writer_path = (backend / "services" / "blocks.py").resolve()
    if not writer_path.is_file() or root not in writer_path.parents:
        raise FileNotFoundError("the versioned block writer is unavailable")

    controls = controls or OperationControls()
    database_proxy = DatabaseProxy(database, controls)
    fastapi = _module("fastapi", HTTPException=SyntheticHTTPException)
    database_stub = _module("database", db=database_proxy)
    integrity_stub = _module("integrity", reconcile_orphans=None)
    substitutions = {
        "fastapi": fastapi,
        "database": database_stub,
        "integrity": integrity_stub,
    }

    constants = _execute_source("_12c7_constants", backend / "constants.py", substitutions)
    core_utils = _execute_source("_12c7_core_utils", backend / "core_utils.py", substitutions)
    serialization = _execute_source(
        "_12c7_serialization", backend / "serialization.py", substitutions
    )
    substitutions.update(
        {
            "constants": constants,
            "core_utils": core_utils,
            "serialization": serialization,
        }
    )
    common = _execute_source(
        "_12c7_services_common", backend / "services" / "common.py", substitutions
    )
    services = _module("services")
    services.__path__ = []  # type: ignore[attr-defined]
    substitutions.update({"services": services, "services.common": common})
    audit = _execute_source("_12c7_audit", backend / "audit.py", substitutions)
    substitutions["audit"] = audit
    writer = _execute_source("_12c7_blocks", writer_path, substitutions)

    symbol = getattr(writer, "update_block", None)
    if not callable(symbol) or Path(symbol.__code__.co_filename).resolve() != writer_path:
        raise ImportError("loaded update_block is not the repository's source symbol")
    if Path(audit.audit.__code__.co_filename).resolve() != (backend / "audit.py").resolve():
        raise ImportError("loaded audit function is not the repository's source symbol")
    return RealBlockWriterHarness(symbol, database_proxy, controls, writer_path)
