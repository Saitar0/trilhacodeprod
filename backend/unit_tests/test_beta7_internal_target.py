"""Offline validation of the Beta 7 internal Mongo hand-off."""

from __future__ import annotations

from urllib.parse import quote

import pytest

from test_support.beta5_mongo_target import MongoTargetError
from test_support.beta7_internal_target import validate_internal_target


def _valid_target() -> dict[str, str]:
    run_id = "1" * 32
    password = "p" * 48
    host = f"tc-beta7-mongo-{run_id[:12]}"
    database = f"beta7_{run_id}"
    return {
        "BETA7_TEST_ISOLATION_GATE": "beta7:" + "e" * 64,
        "BETA7_TEST_MONGO_URI": (
            f"mongodb://beta7_{run_id[:10]}:{quote(password)}@{host}:27017/{database}"
            "?authSource=admin&directConnection=true"
        ),
        "BETA7_TEST_MONGO_DATABASE": database,
        "BETA7_TEST_RUN_ID": run_id,
        "BETA7_TEST_OWNER_TOKEN": "o" * 64,
        "BETA7_TEST_CONTAINER_ID": "a" * 64,
        "BETA7_TEST_NETWORK_ID": "b" * 64,
        "BETA7_TEST_RUNNER_ID": "c" * 64,
        "BETA7_TEST_MONGO_HOST": host,
        "BETA7_TEST_NETWORK_NAME": f"tc-beta7-{run_id[:12]}",
        "BETA7_TEST_RUNNER_NAME": f"tc-beta7-runner-{run_id[:12]}",
    }


def test_valid_internal_handoff_is_parsed_without_connecting():
    target = validate_internal_target(_valid_target())
    assert target.phase == "beta7"
    assert target.database == "beta7_" + "1" * 32
    assert target.host_port == 27017
    assert target.container_id == "a" * 64


@pytest.mark.parametrize("name", [
    "BETA7_TEST_ISOLATION_GATE", "BETA7_TEST_MONGO_URI", "BETA7_TEST_MONGO_DATABASE",
    "BETA7_TEST_RUN_ID", "BETA7_TEST_OWNER_TOKEN", "BETA7_TEST_CONTAINER_ID",
    "BETA7_TEST_NETWORK_ID", "BETA7_TEST_RUNNER_ID", "BETA7_TEST_MONGO_HOST",
    "BETA7_TEST_NETWORK_NAME", "BETA7_TEST_RUNNER_NAME",
])
def test_missing_provisioning_evidence_fails_closed(name):
    environ = _valid_target()
    environ.pop(name)
    with pytest.raises(MongoTargetError):
        validate_internal_target(environ)


@pytest.mark.parametrize("mutate", [
    lambda env: env.update(BETA7_TEST_MONGO_URI="mongodb://localhost:27017/test"),
    lambda env: env.update(BETA7_TEST_MONGO_DATABASE="beta7_other"),
    lambda env: env.update(BETA7_TEST_MONGO_HOST="tc-beta7-mongo-ffffffffffff"),
    lambda env: env.update(BETA7_TEST_NETWORK_ID="short"),
    lambda env: env.update(BETA7_TEST_ISOLATION_GATE="beta6-1:" + "e" * 64),
    lambda env: env.update(BETA7_TEST_OWNER_TOKEN="too-short"),
    lambda env: env.update(BETA7_TEST_MONGO_URI=env["BETA7_TEST_MONGO_URI"] + "&replicaSet=unexpected"),
])
def test_ambiguous_or_foreign_target_fails_closed(mutate):
    environ = _valid_target()
    mutate(environ)
    with pytest.raises(MongoTargetError):
        validate_internal_target(environ)
