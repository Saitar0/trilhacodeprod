from __future__ import annotations

from copy import deepcopy
from urllib.parse import quote

import pytest

from test_support.beta5_mongo_target import (
    MongoTargetError,
    connect_verified_target,
    validate_target,
)
from test_support.beta5_mongodb_harness import DisposableMongoHarness

RUN_ID = "6" * 32
OWNER = "beta6-owner-" + "x" * 40
CONTAINER = "a" * 64
NETWORK = "b" * 64
PORT = 29166
DATABASE = f"beta6_{RUN_ID}"
USERNAME = f"beta6_{RUN_ID[:10]}"
PASSWORD = "synthetic-password-" + "p" * 30


def environment() -> dict[str, str]:
    return {
        "BETA6_TEST_MONGO_URI": (
            f"mongodb://{quote(USERNAME)}:{quote(PASSWORD)}@127.0.0.1:{PORT}/{DATABASE}"
            "?authSource=admin&directConnection=true"
        ),
        "BETA6_TEST_MONGO_DATABASE": DATABASE,
        "BETA6_TEST_RUN_ID": RUN_ID,
        "BETA6_TEST_OWNER_TOKEN": OWNER,
        "BETA6_TEST_CONTAINER_ID": CONTAINER,
        "BETA6_TEST_NETWORK_ID": NETWORK,
    }


def docker_resources() -> tuple[dict, dict]:
    labels = {
        "io.trilhacode.phase": "beta6",
        "io.trilhacode.run-id": RUN_ID,
        "io.trilhacode.owner-token": OWNER,
    }
    container = {
        "Id": CONTAINER,
        "Config": {
            "Image": "mongo:7.0.43", "Labels": labels,
            "Env": [f"MONGO_INITDB_ROOT_USERNAME={USERNAME}", f"MONGO_INITDB_ROOT_PASSWORD={PASSWORD}"],
        },
        "State": {"Running": True},
        "HostConfig": {
            "PortBindings": {"27017/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]},
            "Tmpfs": {"/data/db": "rw", "/data/configdb": "rw"},
        },
        "NetworkSettings": {
            "Ports": {"27017/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]},
            "Networks": {f"tc-beta6-{RUN_ID[:12]}": {}},
        },
        "Mounts": [],
    }
    network = {
        "Id": NETWORK, "Name": f"tc-beta6-{RUN_ID[:12]}", "Driver": "bridge", "Labels": labels,
        "Internal": True, "Containers": {CONTAINER: {"Name": "beta6-mongo"}},
    }
    return container, network


def inspectors(container=None, network=None):
    expected_container, expected_network = docker_resources()
    selected_container = container or expected_container
    selected_network = network or expected_network
    return (
        lambda resource_id: selected_container if resource_id == CONTAINER else {},
        lambda resource_id: selected_network if resource_id == NETWORK else {},
    )


def target(env=None, container=None, network=None):
    inspect_container, inspect_network = inspectors(container, network)
    return validate_target(env if env is not None else environment(), phase="beta6",
                           container_inspector=inspect_container, network_inspector=inspect_network)


@pytest.mark.parametrize("env", [
    {},
    {**environment(), "BETA6_TEST_MONGO_URI": ""},
    {**environment(), "BETA6_TEST_MONGO_URI": "mongodb://localhost:27017/test"},
    {**environment(), "BETA6_TEST_MONGO_URI": environment()["BETA6_TEST_MONGO_URI"].replace(
        f"127.0.0.1:{PORT}", "127.0.0.1:27017")},
    {**environment(), "BETA6_TEST_MONGO_DATABASE": "beta6_shared"},
    {key: value for key, value in environment().items() if key != "BETA6_TEST_OWNER_TOKEN"},
    {**environment(), "BETA6_TEST_RUN_ID": "not-a-run"},
])
def test_beta6_target_rejects_missing_or_ambiguous_identity_before_connect(env):
    inspect_container, inspect_network = inspectors()
    client_created = False

    def client_factory(_uri):
        nonlocal client_created
        client_created = True
        raise AssertionError("Conexão persistente antes da validação")

    with pytest.raises(MongoTargetError):
        connect_verified_target(env, client_factory, phase="beta6",
                                container_inspector=inspect_container, network_inspector=inspect_network)
    assert not client_created


@pytest.mark.parametrize("field", ["phase", "owner", "network", "external", "mount", "binding", "credential"])
def test_beta6_target_rejects_resource_ownership_mismatch(field):
    container, network = docker_resources()
    container, network = deepcopy(container), deepcopy(network)
    if field == "phase":
        container["Config"]["Labels"]["io.trilhacode.phase"] = "beta5"
    elif field == "owner":
        network["Labels"]["io.trilhacode.owner-token"] = "different"
    elif field == "network":
        network["Containers"]["c" * 64] = {"Name": "unrelated"}
    elif field == "external":
        network["Internal"] = False
    elif field == "mount":
        container["Mounts"] = [{"Type": "volume", "Destination": "/data/db"}]
    elif field == "binding":
        container["NetworkSettings"]["Ports"]["27017/tcp"][0]["HostIp"] = "0.0.0.0"
    else:
        container["Config"]["Env"][1] = "MONGO_INITDB_ROOT_PASSWORD=other"
    with pytest.raises(MongoTargetError):
        target(container=container, network=network)


def test_beta6_explicit_provisioned_shape_is_accepted_without_opening_socket():
    result = target()
    assert result.phase == "beta6"
    assert result.database == DATABASE
    assert result.host_port != 27017


def test_beta6_harness_uses_a_distinct_phase_identity_without_provisioning():
    harness = DisposableMongoHarness("beta6")
    assert harness.phase == "beta6"
    assert harness.username.startswith("beta6_")
    assert harness.network_name.startswith("tc-beta6-")
    assert harness.container_name.startswith("tc-beta6-mongo-")
