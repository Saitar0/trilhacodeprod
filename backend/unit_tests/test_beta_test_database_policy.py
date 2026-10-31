from __future__ import annotations

from copy import deepcopy
from urllib.parse import quote

import pytest

from test_support.beta5_mongo_target import (
    MongoTargetError,
    assert_database_owned,
    connect_verified_target,
    require_explicit_opt_in,
    validate_target,
    verify_server_and_claim_database,
)

RUN_ID = "a" * 32
OWNER_TOKEN = "owner-token-" + "t" * 40
CONTAINER_ID = "c" * 64
NETWORK_ID = "d" * 64
DATABASE = f"beta5_{RUN_ID}"
USERNAME = f"beta5_{RUN_ID[:10]}"
PASSWORD = "synthetic-password-" + "p" * 30
PORT = 29165


def _environment() -> dict[str, str]:
    return {
        "BETA5_TEST_MONGO_URI": (
            f"mongodb://{quote(USERNAME)}:{quote(PASSWORD)}@127.0.0.1:{PORT}/{DATABASE}"
            "?authSource=admin&directConnection=true"
        ),
        "BETA5_TEST_MONGO_DATABASE": DATABASE,
        "BETA5_TEST_RUN_ID": RUN_ID,
        "BETA5_TEST_OWNER_TOKEN": OWNER_TOKEN,
        "BETA5_TEST_CONTAINER_ID": CONTAINER_ID,
        "BETA5_TEST_NETWORK_ID": NETWORK_ID,
    }


def _docker_resources() -> tuple[dict, dict]:
    labels = {
        "io.trilhacode.phase": "beta5",
        "io.trilhacode.run-id": RUN_ID,
        "io.trilhacode.owner-token": OWNER_TOKEN,
    }
    container = {
        "Id": CONTAINER_ID,
        "Config": {
            "Image": "mongo:7.0.43",
            "Labels": labels,
            "Env": [
                f"MONGO_INITDB_ROOT_USERNAME={USERNAME}",
                f"MONGO_INITDB_ROOT_PASSWORD={PASSWORD}",
            ],
        },
        "State": {"Running": True},
        "HostConfig": {
            "PortBindings": {"27017/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]},
            "Tmpfs": {"/data/db": "rw", "/data/configdb": "rw"},
        },
        "NetworkSettings": {
            "Ports": {"27017/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORT)}]},
            "Networks": {f"tc-beta5-{RUN_ID[:12]}": {}},
        },
        "Mounts": [],
    }
    network = {
        "Id": NETWORK_ID,
        "Name": f"tc-beta5-{RUN_ID[:12]}",
        "Driver": "bridge",
        "Labels": labels,
        "Containers": {CONTAINER_ID: {"Name": "beta5-mongo"}},
    }
    return container, network


def _inspectors(container: dict | None = None, network: dict | None = None):
    actual_container, actual_network = _docker_resources()
    actual_container = container or actual_container
    actual_network = network or actual_network
    return (
        lambda resource_id: actual_container if resource_id == CONTAINER_ID else {},
        lambda resource_id: actual_network if resource_id == NETWORK_ID else {},
    )


def _validate(environ: dict[str, str] | None = None, *, container=None, network=None):
    inspect_container, inspect_network = _inspectors(container, network)
    return validate_target(
        _environment() if environ is None else environ,
        container_inspector=inspect_container,
        network_inspector=inspect_network,
    )


def test_persistent_tests_require_explicit_isolation_opt_in():
    with pytest.raises(MongoTargetError, match="opt-in explícito"):
        require_explicit_opt_in(False)
    require_explicit_opt_in(True)


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {**_environment(), "BETA5_TEST_MONGO_URI": ""},
        {**_environment(), "BETA5_TEST_MONGO_URI": "not-a-mongodb-uri"},
        {
            **_environment(),
            "BETA5_TEST_MONGO_URI": _environment()["BETA5_TEST_MONGO_URI"] + "&replicaSet=operational",
        },
        {
            **_environment(),
            "BETA5_TEST_MONGO_URI": f"mongodb://{USERNAME}:{PASSWORD}@localhost:27017/{DATABASE}?authSource=admin&directConnection=true",
        },
        {
            **_environment(),
            "BETA5_TEST_MONGO_URI": f"mongodb://{USERNAME}:{PASSWORD}@127.0.0.1:27017/{DATABASE}?authSource=admin&directConnection=true",
        },
        {**_environment(), "BETA5_TEST_MONGO_DATABASE": "test_shared"},
        {**_environment(), "BETA5_TEST_OWNER_TOKEN": "short"},
        {**_environment(), "BETA5_TEST_CONTAINER_ID": "unverified"},
        {**_environment(), "BETA5_TEST_NETWORK_ID": "unverified"},
    ],
)
def test_invalid_or_ambiguous_target_is_rejected_before_client_creation(environ):
    inspect_container, inspect_network = _inspectors()
    client_created = False

    def client_factory(_uri):
        nonlocal client_created
        client_created = True
        raise AssertionError("a conexão não pode ser criada antes de validar o alvo")

    with pytest.raises(MongoTargetError):
        connect_verified_target(
            environ,
            client_factory,
            container_inspector=inspect_container,
            network_inspector=inspect_network,
        )
    assert not client_created


@pytest.mark.parametrize("field", ["container_label", "network_label", "credential", "binding", "mount", "network-sharing"])
def test_resource_ownership_or_isolation_mismatch_is_rejected(field):
    container, network = _docker_resources()
    container = deepcopy(container)
    network = deepcopy(network)
    if field == "container_label":
        container["Config"]["Labels"]["io.trilhacode.owner-token"] = "other"
    elif field == "network_label":
        network["Labels"]["io.trilhacode.run-id"] = "b" * 32
    elif field == "credential":
        container["Config"]["Env"][1] = "MONGO_INITDB_ROOT_PASSWORD=wrong"
    elif field == "binding":
        container["NetworkSettings"]["Ports"]["27017/tcp"][0]["HostIp"] = "0.0.0.0"
    elif field == "mount":
        container["HostConfig"]["Tmpfs"].pop("/data/db")
        container["Mounts"] = [{"Type": "volume", "Destination": "/data/db"}]
    else:
        network["Containers"]["e" * 64] = {"Name": "unrelated"}
    with pytest.raises(MongoTargetError):
        _validate(container=container, network=network)


def test_explicitly_provisioned_target_is_accepted_without_connecting():
    target = _validate()
    assert target.database == DATABASE
    assert target.run_id == RUN_ID
    assert target.host_port != 27017


class _FakeCollection:
    def __init__(self, database):
        self.database = database
        self.documents = {}

    def find_one(self, query):
        return self.documents.get(query["_id"])

    def insert_one(self, document):
        self.documents[document["_id"]] = deepcopy(document)
        self.database.client.names.add(self.database.name)


class _FakeDatabase:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.collections = {}

    def __getitem__(self, name):
        return self.collections.setdefault(name, _FakeCollection(self))


class _FakeAdmin:
    @staticmethod
    def command(name):
        return {
            "hello": {},
            "buildInfo": {"version": "7.0.43"},
            "serverStatus": {"storageEngine": {"name": "wiredTiger"}},
        }[name]


class _FakeClient:
    def __init__(self):
        self.admin = _FakeAdmin()
        self.names = set()
        self.databases = {}

    def list_database_names(self):
        return list(self.names)

    def __getitem__(self, name):
        return self.databases.setdefault(name, _FakeDatabase(self, name))


def test_server_is_checked_then_database_is_claimed_and_cleanup_requires_same_owner():
    target = _validate()
    client = _FakeClient()
    verify_server_and_claim_database(client, target)
    verify_server_and_claim_database(client, target)
    assert client[target.database]["_beta5_test_owner"].find_one({"_id": "owner"})["run_id"] == RUN_ID
    assert_database_owned(client, target)


def test_existing_database_without_owner_marker_is_rejected():
    target = _validate()
    client = _FakeClient()
    client.names.add(target.database)
    with pytest.raises(MongoTargetError, match="sem prova de propriedade"):
        verify_server_and_claim_database(client, target)


def test_cleanup_refuses_missing_or_divergent_ownership_marker():
    target = _validate()
    client = _FakeClient()
    with pytest.raises(MongoTargetError, match="propriedade do banco não comprovada"):
        assert_database_owned(client, target)
