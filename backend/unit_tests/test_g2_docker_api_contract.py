"""Exercise the Docker inspect fields used by the G2 runner on a disposable engine."""

import json
import shutil
import subprocess
import uuid

import pytest


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args], check=check, capture_output=True, text=True, timeout=45
    )


def test_docker_network_and_container_inspect_keep_names_and_aliases_in_expected_objects(capsys):
    if not shutil.which("docker"):
        pytest.skip("Docker CLI unavailable; Linux CI runs this disposable Engine contract test")
    daemon = _docker("info", "--format", "{{.ServerVersion}}", check=False)
    if daemon.returncode != 0:
        pytest.skip("Docker Engine unavailable; Linux CI runs this disposable Engine contract test")
    engine_version = daemon.stdout.strip()
    with capsys.disabled():
        print(f"Checking Docker Engine {engine_version} inspect contract")

    suffix = uuid.uuid4().hex[:12]
    network = f"trilhacode-g2-preflight-internal-{suffix}"
    operational_network = f"g2-api-operational-{suffix}"
    container = f"g2-api-contract-mongo-{suffix}"
    preflight_container = f"g2-api-contract-preflight-{suffix}"
    created_networks: list[str] = []
    try:
        _docker("network", "create", "--internal", network)
        created_networks.append(network)
        _docker("network", "create", operational_network)
        created_networks.append(operational_network)
        _docker(
            "run",
            "--detach",
            "--pull",
            "never",
            "--name",
            container,
            "--network",
            network,
            "--network-alias",
            "mongo-contract",
            "mongo:7",
        )
        _docker("network", "connect", operational_network, container)
        network_inspect = json.loads(_docker("network", "inspect", network).stdout)
        container_id, endpoint = next(iter(network_inspect[0]["Containers"].items()))
        container_inspect = json.loads(_docker("inspect", container).stdout)[0]
        endpoint_config = container_inspect["NetworkSettings"]["Networks"][network]
        mongo_network_names = set(container_inspect["NetworkSettings"]["Networks"])

        assert len(network_inspect) == 1, (
            f"Docker Engine {engine_version} returned unexpected network cardinality"
        )
        assert network_inspect[0]["Internal"] is True
        assert len(network_inspect[0]["Containers"]) == 1
        assert endpoint["Name"] == container
        assert not endpoint["Name"].startswith("/")
        assert "Aliases" not in endpoint
        assert container_inspect["Id"] == container_id
        assert "mongo-contract" in endpoint_config["Aliases"]
        assert mongo_network_names == {network, operational_network}, (
            "MongoDB must retain its operational network while joining the dedicated G2 network"
        )

        # A disposable stand-in for the short-lived preflight container is
        # attached only to G2. It has no published ports or host mounts.
        _docker(
            "create",
            "--pull",
            "never",
            "--name",
            preflight_container,
            "--network",
            network,
            "--entrypoint",
            "sh",
            "mongo:7",
            "-c",
            "true",
        )
        preflight_config = json.loads(_docker("inspect", preflight_container).stdout)[0]
        assert preflight_config["HostConfig"]["NetworkMode"] == network
        assert set(preflight_config["NetworkSettings"]["Networks"]) <= {network}

        # The configured network is verified before start. Once started, the
        # actual endpoint must still be exclusive to G2.
        _docker("start", "--attach", preflight_container)
        preflight_inspect = json.loads(_docker("inspect", preflight_container).stdout)[0]
        preflight_networks = preflight_inspect["NetworkSettings"]["Networks"]
        assert set(preflight_networks) == {network}
        network_after_preflight = json.loads(_docker("network", "inspect", network).stdout)[0]
        assert network_after_preflight["Internal"] is True
        # A stopped container keeps the configured endpoint in `inspect`,
        # while the network's live member list returns to MongoDB alone.
        assert set(network_after_preflight["Containers"]) == {container_id}
    finally:
        _docker("rm", "--force", preflight_container, check=False)
        _docker("rm", "--force", container, check=False)
        for created_network in reversed(created_networks):
            _docker("network", "rm", created_network, check=False)
