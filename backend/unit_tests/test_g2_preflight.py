import asyncio
import builtins
import json
from pathlib import Path

import pytest
from pymongo.errors import ConnectionFailure, ExecutionTimeout, OperationFailure

import g2_preflight
from g2_protocol import is_rejected, validate_report
from indexes import INDEXES, preflight_index_checks


def env_for(uri="mongodb://g2-reader:p%40ss@mongo:27017/trilhacode_staging?authSource=admin&directConnection=true"):
    return {
        "ENV": "staging",
        "DB_NAME": "trilhacode_staging",
        "MONGO_URL": uri,
        "G2_MONGO_EXPECTED_HOST": "mongo",
        "G2_MONGO_EXPECTED_PORT": "27017",
    }


@pytest.mark.parametrize("key,value", [
    ("G2_MONGO_EXPECTED_HOST", "127.0.0.1"),
    ("G2_MONGO_EXPECTED_HOST", "host.docker.internal"),
    ("G2_MONGO_EXPECTED_PORT", "27018"),
    ("DB_NAME", "another_database"),
    ("ENV", "production"),
])
def test_untrusted_expected_identity_or_environment_is_rejected(key, value):
    env = env_for()
    env[key] = value
    with pytest.raises(ValueError, match="URI_INVALID"):
        g2_preflight.validate_target(env)


@pytest.mark.parametrize("uri", [
    "mongodb://g2-reader:p%40ss@mongo:27017/trilhacode_staging?authSource=admin&directConnection=true",
])
def test_valid_staging_uri(uri):
    assert g2_preflight.validate_target(env_for(uri)) == "mongo"


@pytest.mark.parametrize("uri", [
    "mongodb+srv://g2-reader:pass@mongo/trilhacode_staging",
    "mongodb://g2-reader:pass@mongo:27017,other:27017/trilhacode_staging",
    "mongodb://g2-reader:pass@external.example:27017/trilhacode_staging",
    "mongodb://g2-reader:pass@mongo:27018/trilhacode_staging",
    "mongodb://g2-reader:pass@mongo:27017/other_db",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging?replicaSet=rs0",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging?directConnection=false",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging?loadBalanced=true",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging?authSource=other",
    "mongodb://g2-reader:pass@mongo:27017/trilhacode_staging#fragment",
    "mongodb://mongo:27017/trilhacode_staging",
    "not-a-mongodb-uri",
])
def test_invalid_destination_is_rejected_without_echoing_uri(uri):
    with pytest.raises(ValueError) as error:
        g2_preflight.validate_target(env_for(uri))
    assert "p%40ss" not in str(error.value)
    assert "external.example" not in str(error.value)


def test_invalid_uri_stops_before_database_import(monkeypatch, capsys):
    real_import = builtins.__import__
    attempted_database_import = False

    def guarded_import(name, *args, **kwargs):
        nonlocal attempted_database_import
        if name in {"database", "indexes"}:
            attempted_database_import = True
            raise AssertionError("database modules imported before target validation")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(g2_preflight.os, "environ", {**env_for("mongodb://bad-host/")})
    assert asyncio.run(g2_preflight.run()) == g2_preflight.EXIT_CODES["URI_INVALID"]
    assert not attempted_database_import
    output = capsys.readouterr().out
    assert "p%40ss" not in output and "bad-host" not in output
    assert json.loads(output)["category"] == "URI_INVALID"


def test_database_errors_map_to_safe_categories():
    assert g2_preflight.classify_database_error(OperationFailure("sensitive", code=13)) == "DB_AUTH"
    assert g2_preflight.classify_database_error(OperationFailure("sensitive", code=18)) == "DB_AUTH"
    assert g2_preflight.classify_database_error(ConnectionFailure("sensitive")) == "DB_CONNECTION"
    assert g2_preflight.classify_database_error(ExecutionTimeout("sensitive")) == "DB_TIMEOUT"
    assert g2_preflight.classify_database_error(RuntimeError("secret URI")) == "PREFLIGHT_EXECUTION"


def test_manifest_matches_stable_index_and_duplicate_check_ids():
    repo_root = Path(__file__).resolve().parents[2]
    manifest = json.loads((repo_root / "ops/g2/preflight-manifest-v1.json").read_text())
    index_ids = []
    for collection, keys, options, unique_fields in INDEXES:
        name = options.get("name") or "_".join(f"{field}_{direction}" for field, direction in keys)
        index_ids.append(f"index/{collection}/{name}")
        if unique_fields:
            index_ids.append(f"duplicates/{collection}/{name}")
    assert manifest == {"schema_version": 1, "checks": index_ids}
    assert len(index_ids) == len(set(index_ids))


@pytest.mark.parametrize("mutation", ["empty", "missing", "duplicate", "extra", "unknown", "extra-field", "malformed-status"])
def test_protocol_rejects_incomplete_or_untrusted_reports(mutation):
    expected = ["index/a/name", "duplicates/a/name"]
    report = {"schema_version": 1, "result": "COMPLETE", "checks": [
        {"id": expected[0], "status": "OK"}, {"id": expected[1], "status": "OK"},
    ]}
    if mutation == "empty":
        report["checks"] = []
    elif mutation == "missing":
        report["checks"].pop()
    elif mutation == "duplicate":
        report["checks"].append(dict(report["checks"][0]))
    elif mutation == "extra":
        report["checks"].append({"id": "index/a/extra", "status": "OK"})
    elif mutation == "unknown":
        report["checks"][0]["status"] = "UNKNOWN"
    elif mutation == "extra-field":
        report["checks"][0]["document_id"] = "must-not-be-accepted"
    else:
        report["checks"][0]["status"] = {"secret": "value"}
    with pytest.raises(ValueError):
        validate_report(report, expected)


def test_complete_protocol_accepts_expected_absent_state():
    report = {"schema_version": 1, "result": "COMPLETE", "checks": [
        {"id": "index/a/name", "status": "AUSENTE"},
        {"id": "duplicates/a/name", "status": "OK"},
    ]}
    checks = validate_report(report, ["index/a/name", "duplicates/a/name"])
    assert not is_rejected(checks)


@pytest.mark.parametrize("status", ["CONFLITO", "DUPLICATAS"])
def test_conflict_and_duplicate_states_are_semantic_failures(status):
    report = {"schema_version": 1, "result": "COMPLETE", "checks": [
        {"id": "index/a/name", "status": status},
    ]}
    assert is_rejected(validate_report(report, ["index/a/name"]))


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    async def to_list(self, length):
        return self.rows[:length]


class FakeCollection:
    def __init__(self, duplicate=False):
        self.duplicate = duplicate
        self.aggregate_kwargs = []
        self.writes = 0

    async def list_indexes(self):
        return FakeCursor([])

    async def aggregate(self, pipeline, **kwargs):
        self.aggregate_kwargs.append(kwargs)
        return FakeCursor([{"count": 2}] if self.duplicate else [])

    async def create_index(self, *args, **kwargs):
        self.writes += 1
        raise AssertionError("G2 must not create indexes")


class FakeDatabase:
    def __init__(self, duplicate_collection=None):
        self.collections = {}
        self.names = sorted({item[0] for item in INDEXES})
        self.duplicate_collection = duplicate_collection

    async def list_collection_names(self):
        return self.names

    def __getitem__(self, name):
        return self.collections.setdefault(name, FakeCollection(name == self.duplicate_collection))


def test_structured_checks_are_complete_redacted_read_only_and_time_bounded():
    database = FakeDatabase(duplicate_collection="users")
    checks = asyncio.run(preflight_index_checks(database))
    repo_root = Path(__file__).resolve().parents[2]
    manifest = json.loads((repo_root / "ops/g2/preflight-manifest-v1.json").read_text())
    validate_report({"schema_version": 1, "result": "COMPLETE", "checks": checks}, manifest["checks"])
    assert any(check["status"] == "DUPLICATAS" for check in checks)
    assert all(set(check) == {"id", "status"} for check in checks)
    assert all("sample" not in json.dumps(check).lower() for check in checks)
    assert all(collection.writes == 0 for collection in database.collections.values())
    assert all(kwargs == {"maxTimeMS": 10_000}
               for collection in database.collections.values()
               for kwargs in collection.aggregate_kwargs)
