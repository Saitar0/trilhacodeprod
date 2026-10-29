"""Failure injection helpers for isolated editorial block commit tests only."""

from __future__ import annotations

import os
import json
import sys
import threading
from enum import Enum
from typing import Any


class FaultStage(str, Enum):
    BEFORE_TRACK_UPDATE = "before_track_update"
    AFTER_TRACK_UPDATE = "after_track_update"
    BEFORE_BLOCK_UPDATE = "before_block_update"
    AFTER_BLOCK_UPDATE = "after_block_update"
    BEFORE_AUDIT_INSERT = "before_audit_insert"
    AFTER_AUDIT_INSERT = "after_audit_insert"
    BEFORE_HISTORY_INSERT = "before_history_insert"
    AFTER_HISTORY_INSERT = "after_history_insert"
    BEFORE_RECEIPT_WRITE = "before_receipt_write"
    AFTER_RECEIPT_WRITE = "after_receipt_write"
    RECEIPT_READ = "receipt_read"
    BEFORE_COMMIT = "before_commit"


class InjectedFailure(RuntimeError):
    """Synthetic failure at a named MongoDB transaction boundary."""


class FaultPlan:
    def __init__(
        self,
        stage: FaultStage | None = None,
        *,
        action: str = "raise",
        exit_code: int = 73,
    ) -> None:
        if action not in {"raise", "exit"}:
            raise ValueError("fault action must be raise or exit")
        self.stage = stage
        self.action = action
        self.exit_code = exit_code
        self._lock = threading.Lock()
        self._consumed = False
        self.calls: list[str] = []

    def trigger(self, stage: FaultStage) -> None:
        with self._lock:
            self.calls.append(stage.value)
            if stage != self.stage or self._consumed:
                return
            self._consumed = True
        if self.action == "exit":
            os._exit(self.exit_code)
        raise InjectedFailure(f"injected failure at {stage.value}")


class CollectionProxy:
    def __init__(self, name: str, collection: Any, fault_plan: FaultPlan) -> None:
        self._name = name
        self._collection = collection
        self._fault_plan = fault_plan

    def update_one(self, filter: Any, update: Any, **kwargs: Any) -> Any:
        if (
            self._name.endswith("_tracks")
            and "revision" in update.get("$set", {})
        ):
            self._fault_plan.trigger(FaultStage.BEFORE_TRACK_UPDATE)
            result = self._collection.update_one(filter, update, **kwargs)
            self._fault_plan.trigger(FaultStage.AFTER_TRACK_UPDATE)
            return result
        if self._name == "content_blocks":
            self._fault_plan.trigger(FaultStage.BEFORE_BLOCK_UPDATE)
            result = self._collection.update_one(filter, update, **kwargs)
            self._fault_plan.trigger(FaultStage.AFTER_BLOCK_UPDATE)
            return result
        if (
            self._name.endswith("_operations")
            and update.get("$set", {}).get("state") == "COMMITTED"
        ):
            self._fault_plan.trigger(FaultStage.BEFORE_RECEIPT_WRITE)
            result = self._collection.update_one(filter, update, **kwargs)
            self._fault_plan.trigger(FaultStage.AFTER_RECEIPT_WRITE)
            return result
        return self._collection.update_one(filter, update, **kwargs)

    def insert_one(self, document: Any, **kwargs: Any) -> Any:
        if self._name == "edit_history":
            self._fault_plan.trigger(FaultStage.BEFORE_AUDIT_INSERT)
            result = self._collection.insert_one(document, **kwargs)
            self._fault_plan.trigger(FaultStage.AFTER_AUDIT_INSERT)
            return result
        if self._name.endswith("_history"):
            self._fault_plan.trigger(FaultStage.BEFORE_HISTORY_INSERT)
            result = self._collection.insert_one(document, **kwargs)
            self._fault_plan.trigger(FaultStage.AFTER_HISTORY_INSERT)
            return result
        return self._collection.insert_one(document, **kwargs)

    def find_one(self, *args: Any, **kwargs: Any) -> Any:
        if self._name.endswith("_operations"):
            self._fault_plan.trigger(FaultStage.RECEIPT_READ)
        return self._collection.find_one(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._collection, name)


class SessionProxy:
    def __init__(self, session: Any, fault_plan: FaultPlan) -> None:
        self._session = session
        self._fault_plan = fault_plan

    def __enter__(self) -> SessionProxy:
        self._session.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Any:
        return self._session.__exit__(exc_type, exc_value, traceback)

    @property
    def in_transaction(self) -> bool:
        return self._session.in_transaction

    def with_transaction(self, callback: Any, **kwargs: Any) -> Any:
        def guarded(real_session: Any) -> Any:
            result = callback(real_session)
            self._fault_plan.trigger(FaultStage.BEFORE_COMMIT)
            return result

        return self._session.with_transaction(guarded, **kwargs)

    def abort_transaction(self) -> Any:
        return self._session.abort_transaction()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._session, name)


class ClientProxy:
    def __init__(self, client: Any, fault_plan: FaultPlan) -> None:
        self._client = client
        self._fault_plan = fault_plan

    def start_session(self, *args: Any, **kwargs: Any) -> SessionProxy:
        return SessionProxy(self._client.start_session(*args, **kwargs), self._fault_plan)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


class DatabaseProxy:
    def __init__(
        self,
        database: Any,
        fault_plan: FaultPlan,
        client_proxy: ClientProxy | None = None,
    ) -> None:
        self._database = database
        self._fault_plan = fault_plan
        self._client_proxy = client_proxy or ClientProxy(database.client, fault_plan)

    @property
    def name(self) -> str:
        return self._database.name

    @property
    def client(self) -> ClientProxy:
        return self._client_proxy

    def with_options(self, **kwargs: Any) -> DatabaseProxy:
        return DatabaseProxy(
            self._database.with_options(**kwargs), self._fault_plan, self._client_proxy
        )

    def __getitem__(self, name: str) -> CollectionProxy:
        return CollectionProxy(name, self._database[name], self._fault_plan)


def _worker_main() -> None:
    """Run one test-owned OS process; inputs and outputs use private stdio pipes."""

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pymongo import MongoClient

    from curriculum_contract.editorial_revision_protocol import (
        FencingRejected,
        RevisionConflict,
        WriterCredential,
    )
    from curriculum_contract.experimental_editorial_block_commit import (
        commit_prepared_editorial_block_update,
        prepare_editorial_block_update,
    )
    from curriculum_contract.mongodb_editorial_revision_adapter import (
        MongoDBEditorialRevisionAdapter,
    )

    config = json.loads(sys.stdin.readline())
    client = MongoClient(
        config["uri"], appname="trilhacode-12c8-test-worker", serverSelectionTimeoutMS=8000
    )
    database = client[config["database_name"]]
    mode = config["mode"]
    plan = FaultPlan(FaultStage.AFTER_AUDIT_INSERT, action="exit", exit_code=73) if mode == "crash" else FaultPlan()
    database_arg: Any = DatabaseProxy(database, plan) if mode == "crash" else database
    adapter = MongoDBEditorialRevisionAdapter(database_arg, namespace=config["namespace"])
    adapter.verify_transaction_topology()
    credential = WriterCredential(
        config["track_id"], config["writer_id"], config["secret"]
    )

    try:
        prepared = prepare_editorial_block_update(
            adapter,
            track_id=config["track_id"],
            credential=credential,
            operation_id=config["operation_id"],
            expected_revision=config["expected_revision"],
            fencing_token=config["fencing_token"],
            block_id=config["block_id"],
            actor_id=config["actor_id"],
            title=config["title"],
        )
        if mode == "crash":
            print("PREPARED", flush=True)
            commit_prepared_editorial_block_update(
                database_arg, adapter, credential, prepared
            )
            os._exit(74)

        print("READY", flush=True)
        if sys.stdin.readline().strip() != "GO":
            print(json.dumps({"error": "start_signal_missing"}), flush=True)
            return
        receipt = commit_prepared_editorial_block_update(
            database, adapter, credential, prepared
        )
        print(
            json.dumps(
                {
                    "result": "committed",
                    "revision": receipt.revision,
                    "fencing_token": receipt.fencing_token,
                    "replayed": receipt.replayed,
                }
            ),
            flush=True,
        )
    except RevisionConflict:
        print(json.dumps({"result": "revision_conflict"}), flush=True)
    except FencingRejected:
        print(json.dumps({"result": "fencing_rejected"}), flush=True)
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__}), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    _worker_main()

