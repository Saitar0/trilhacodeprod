"""Offline validation of the Beta 6.1 internal-network hand-off."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

import pytest

from test_support.beta5_mongo_target import MongoTargetError
from test_support.beta6_1_docker_harness import (
    Beta61DockerHarness,
    Beta61HarnessError,
    local_readiness_probe,
)
from test_support.beta6_1_internal_target import (
    connect_internal_verified_target,
    validate_internal_target,
)

RUN_ID = "1234567890abcdef1234567890abcdef"
MONGO_ID = "a" * 64
NETWORK_ID = "b" * 64
RUNNER_ID = "c" * 64
OWNER = "owner-token-that-is-long-enough-for-phase-beta-six-point-one"
HOST = f"tc-beta6-1-mongo-{RUN_ID[:12]}"
NETWORK = f"tc-beta6-1-{RUN_ID[:12]}"
RUNNER = f"tc-beta6-1-runner-{RUN_ID[:12]}"
DATABASE = f"beta6_{RUN_ID}"
USERNAME = f"beta6_{RUN_ID[:10]}"
PASSWORD = "synthetic-password-that-is-long-enough-123456"


def test_runner_readiness_probe_is_valid_python() -> None:
    compile(local_readiness_probe(), "<beta6-1-readiness-probe>", "exec")


def valid_environment() -> dict[str, str]:
    uri = (
        f"mongodb://{quote(USERNAME)}:{quote(PASSWORD)}@{HOST}:27017/{DATABASE}"
        "?authSource=admin&directConnection=true"
    )
    return {
        "BETA6_TEST_ISOLATION_GATE": "beta6-1:" + "d" * 64,
        "BETA6_TEST_MONGO_URI": uri,
        "BETA6_TEST_MONGO_DATABASE": DATABASE,
        "BETA6_TEST_RUN_ID": RUN_ID,
        "BETA6_TEST_OWNER_TOKEN": OWNER,
        "BETA6_TEST_CONTAINER_ID": MONGO_ID,
        "BETA6_TEST_NETWORK_ID": NETWORK_ID,
        "BETA6_TEST_RUNNER_ID": RUNNER_ID,
        "BETA6_TEST_MONGO_HOST": HOST,
        "BETA6_TEST_NETWORK_NAME": NETWORK,
        "BETA6_TEST_RUNNER_NAME": RUNNER,
    }


def test_accepts_host_attested_internal_target_without_network_connection() -> None:
    target = validate_internal_target(valid_environment())

    assert target.phase == "beta6"
    assert target.database == DATABASE
    assert target.container_id == MONGO_ID
    assert target.network_id == NETWORK_ID
    assert target.host_port == 27017


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("BETA6_TEST_ISOLATION_GATE", ""),
        ("BETA6_TEST_MONGO_URI", ""),
        ("BETA6_TEST_MONGO_URI", "mongodb://user:pass@127.0.0.1:27017/beta6_test"),
        ("BETA6_TEST_MONGO_DATABASE", "different"),
        ("BETA6_TEST_RUN_ID", "not-a-run-id"),
        ("BETA6_TEST_OWNER_TOKEN", "short"),
        ("BETA6_TEST_CONTAINER_ID", "short"),
        ("BETA6_TEST_NETWORK_ID", "short"),
        ("BETA6_TEST_RUNNER_ID", "short"),
        ("BETA6_TEST_MONGO_HOST", "localhost"),
        ("BETA6_TEST_NETWORK_NAME", "shared-network"),
        ("BETA6_TEST_RUNNER_NAME", "someone-elses-runner"),
    ],
)
def test_rejects_incomplete_or_ambiguous_internal_identity(name: str, value: str) -> None:
    environ = valid_environment()
    environ[name] = value

    with pytest.raises(MongoTargetError):
        validate_internal_target(environ)


def test_connection_factory_is_not_called_until_internal_gate_is_valid() -> None:
    called = False

    def client_factory(_uri: str):
        nonlocal called
        called = True
        raise AssertionError("invalid target must not open a client")

    environ = deepcopy(valid_environment())
    environ.pop("BETA6_TEST_ISOLATION_GATE")

    with pytest.raises(MongoTargetError):
        connect_internal_verified_target(environ, client_factory)
    assert called is False


def _docker_gate_fixture(harness: Beta61DockerHarness):
    harness.network_id = NETWORK_ID
    harness.mongo_id = MONGO_ID
    harness.runner_id = RUNNER_ID
    harness.image_id = "sha256:" + "e" * 64
    network = {
        "Id": NETWORK_ID,
        "Name": harness.network_name,
        "Driver": "bridge",
        "Internal": True,
        "Labels": dict(harness.labels),
        "Containers": {MONGO_ID: {}, RUNNER_ID: {}},
    }
    mongo = {
        "Id": MONGO_ID,
        "Name": f"/{harness.mongo_name}",
        "State": {"Running": True},
        "Config": {
            "Image": "mongo:7.0.43",
            "Labels": dict(harness.labels),
            "Env": [
                f"MONGO_INITDB_ROOT_USERNAME={harness.mongo_user}",
                f"MONGO_INITDB_ROOT_PASSWORD={harness.mongo_password}",
            ],
        },
        "HostConfig": {
            "NetworkMode": harness.network_name,
            "PortBindings": None,
            "Binds": None,
            "VolumesFrom": None,
            "Tmpfs": {"/data/db": "rw,noexec,nosuid", "/data/configdb": "rw,noexec,nosuid"},
        },
        "Mounts": [],
        "NetworkSettings": {"Networks": {harness.network_name: {}}, "Ports": {"27017/tcp": None}},
    }
    runner = {
        "Id": RUNNER_ID,
        "Name": f"/{harness.runner_name}",
        "State": {"Running": True},
        "Config": {
            "Image": harness.image_tag,
            "Labels": dict(harness.labels),
            "Env": [
                f"MONGO_URL={harness.mongo_uri}",
                f"DB_NAME={harness.database}",
                "ENV=development",
                "CI=",
                "EMAIL_TRANSPORT=local",
                "LOCAL_EMAIL_DIR=/tmp/beta6-1-mail",
                "PLAYWRIGHT_BASE_URL=http://127.0.0.1:3000",
                "API_BASE_URL=http://127.0.0.1:18000",
            ],
        },
        "Image": harness.image_id,
        "HostConfig": {
            "NetworkMode": harness.network_name,
            "PortBindings": None,
            "Binds": None,
            "VolumesFrom": None,
            "Tmpfs": {"/tmp": "rw,noexec,nosuid"},
        },
        "Mounts": [],
        "NetworkSettings": {"Networks": {harness.network_name: {}}},
    }
    return network, mongo, runner


def test_host_gate_accepts_only_owned_internal_no_mount_no_publish_topology(monkeypatch) -> None:
    harness = Beta61DockerHarness(Path("."))
    network, mongo, runner = _docker_gate_fixture(harness)
    by_id = {MONGO_ID: mongo, RUNNER_ID: runner}
    monkeypatch.setattr(harness, "_inspect_network", lambda: network)
    monkeypatch.setattr(harness, "_inspect_container", lambda identity: by_id[identity])
    monkeypatch.setattr(harness, "_docker", lambda _args, **_kwargs: "desktop-linux")

    evidence = harness.validate_gate()

    assert evidence["network_internal"] == "true"
    assert evidence["published_ports"] == "none"
    assert evidence["persistent_mounts"] == "none"


@pytest.mark.parametrize("mutation", [
    "external_network",
    "extra_network_member",
    "mongo_published_port",
    "runner_published_port",
    "mongo_persistent_mount",
    "runner_persistent_mount",
    "wrong_mongo_label",
    "runner_outside_network",
])
def test_host_gate_fails_closed_on_isolation_divergence(monkeypatch, mutation: str) -> None:
    harness = Beta61DockerHarness(Path("."))
    network, mongo, runner = _docker_gate_fixture(harness)
    if mutation == "external_network":
        network["Internal"] = False
    elif mutation == "extra_network_member":
        network["Containers"]["f" * 64] = {}
    elif mutation == "mongo_published_port":
        mongo["HostConfig"]["PortBindings"] = {"27017/tcp": [{"HostIp": "127.0.0.1", "HostPort": "27017"}]}
    elif mutation == "runner_published_port":
        runner["HostConfig"]["PortBindings"] = {"3000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "3000"}]}
    elif mutation == "mongo_persistent_mount":
        mongo["Mounts"].append({"Type": "bind", "Source": "shared"})
    elif mutation == "runner_persistent_mount":
        runner["Mounts"].append({"Type": "bind", "Source": "worktree"})
    elif mutation == "wrong_mongo_label":
        mongo["Config"]["Labels"]["io.trilhacode.owner-token"] = "wrong"
    elif mutation == "runner_outside_network":
        runner["NetworkSettings"]["Networks"]["default"] = {}
    by_id = {MONGO_ID: mongo, RUNNER_ID: runner}
    monkeypatch.setattr(harness, "_inspect_network", lambda: network)
    monkeypatch.setattr(harness, "_inspect_container", lambda identity: by_id[identity])
    monkeypatch.setattr(harness, "_docker", lambda _args, **_kwargs: "desktop-linux")

    with pytest.raises(Beta61HarnessError):
        harness.validate_gate()
