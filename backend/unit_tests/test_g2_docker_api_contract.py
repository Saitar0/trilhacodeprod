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
    network = f"g2-api-contract-{suffix}"
    container = f"g2-api-contract-mongo-{suffix}"
    network_created = False
    try:
        _docker("network", "create", "--internal", network)
        network_created = True
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
        network_inspect = json.loads(_docker("network", "inspect", network).stdout)
        container_id, endpoint = next(iter(network_inspect[0]["Containers"].items()))
        container_inspect = json.loads(_docker("inspect", container).stdout)[0]
        endpoint_config = container_inspect["NetworkSettings"]["Networks"][network]

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
    finally:
        if network_created:
            _docker("rm", "--force", container, check=False)
            _docker("network", "rm", network, check=False)
