"""Opt-in Docker Engine contract test with owned, isolated resources only.

This historical contract test used to create unlabelled resources and attach
MongoDB to a non-internal companion network.  It now skips by default and will
remove only resources whose immutable IDs and complete ownership labels still
match this invocation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid

import pytest

PHASE = "beta7"
TEST = "legacy-g2-docker-api-contract"
EXPECTED_TMPFS_PATHS = {"/data/db", "/data/configdb"}
LABEL_PHASE = "io.trilhacode.phase"
LABEL_TEST = "io.trilhacode.test"
LABEL_RUN = "io.trilhacode.run-id"
LABEL_OWNER = "io.trilhacode.owner-token"


def expected_labels(run_id: str, owner_token: str) -> dict[str, str]:
    return {
        LABEL_PHASE: PHASE,
        LABEL_TEST: TEST,
        LABEL_RUN: run_id,
        LABEL_OWNER: owner_token,
    }


def owned_resource(resource: dict, labels: dict[str, str], *, resource_id: str, name: str) -> bool:
    actual = resource.get("Config", {}).get("Labels") or resource.get("Labels") or {}
    return resource.get("Id", "").lower() == resource_id.lower() and resource.get("Name") in {
        name, f"/{name}",
    } and all(actual.get(key) == value for key, value in labels.items())


def _docker(*args: str, timeout: int = 45) -> str:
    completed = subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=timeout,
    )
    return completed.stdout.strip()


def _inspect_one(*args: str) -> dict:
    rows = json.loads(_docker(*args))
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise RuntimeError("Docker não identificou univocamente um recurso próprio")
    return rows[0]


def _verify_container(resource_id: str, name: str, labels: dict[str, str]) -> dict:
    item = _inspect_one("inspect", resource_id)
    if not owned_resource(item, labels, resource_id=resource_id, name=name):
        raise RuntimeError("Propriedade do container não comprovada; recurso preservado")
    host = item.get("HostConfig") or {}
    mounts = item.get("Mounts") or []
    tmpfs_paths = set((host.get("Tmpfs") or {}).keys())
    observed_tmpfs = {
        mount.get("Destination") for mount in mounts if mount.get("Type") == "tmpfs"
    }
    if (host.get("Binds") or host.get("VolumesFrom") or host.get("Volumes")
            or host.get("PortBindings") or any(mount.get("Type") != "tmpfs" for mount in mounts)
            or tmpfs_paths != EXPECTED_TMPFS_PATHS or not observed_tmpfs.issubset(tmpfs_paths)):
        raise RuntimeError("Container fora do isolamento permitido; recurso preservado")
    return item


def _verify_network(resource_id: str, name: str, labels: dict[str, str]) -> dict:
    item = _inspect_one("network", "inspect", resource_id)
    if not owned_resource(item, labels, resource_id=resource_id, name=name):
        raise RuntimeError("Propriedade da rede não comprovada; recurso preservado")
    if item.get("Internal") is not True or item.get("Driver") != "bridge":
        raise RuntimeError("Rede não é uma bridge interna; recurso preservado")
    return item


def _cleanup_container(resource_id: str | None, name: str, labels: dict[str, str]) -> None:
    if not resource_id:
        return
    _verify_container(resource_id, name, labels)
    _docker("rm", "--force", resource_id)


def _cleanup_network(resource_id: str | None, name: str, labels: dict[str, str]) -> None:
    if not resource_id:
        return
    item = _verify_network(resource_id, name, labels)
    if item.get("Containers"):
        raise RuntimeError("Rede ainda possui membros; recurso preservado")
    _docker("network", "rm", resource_id)


def test_docker_network_and_container_inspect_keep_names_and_aliases_in_expected_objects(capsys):
    if os.environ.get("TRILHACODE_RUN_G2_DOCKER_CONTRACT") != "1":
        pytest.skip("Requer opt-in explícito: TRILHACODE_RUN_G2_DOCKER_CONTRACT=1")
    if not shutil.which("docker"):
        pytest.skip("Docker CLI indisponível")
    try:
        version = _docker("info", "--format", "{{.ServerVersion}}")
        _docker("image", "inspect", "mongo:7.0.43")
    except (OSError, subprocess.SubprocessError, RuntimeError, json.JSONDecodeError):
        pytest.skip("Docker Engine ou imagem MongoDB 7.0.43 pré-carregada indisponível; sem pull automático")

    run_id = uuid.uuid4().hex
    suffix = run_id[:12]
    owner_token = uuid.uuid4().hex + uuid.uuid4().hex
    labels = expected_labels(run_id, owner_token)
    network = f"tc-beta7-g2-{suffix}"
    companion_network = f"tc-beta7-g2-companion-{suffix}"
    container = f"tc-beta7-g2-mongo-{suffix}"
    preflight_container = f"tc-beta7-g2-preflight-{suffix}"
    network_ids: dict[str, str] = {}
    container_ids: dict[str, str] = {}
    label_args = [item for key, value in labels.items() for item in ("--label", f"{key}={value}")]

    def make_network(name: str) -> str:
        return _docker("network", "create", "--driver", "bridge", "--internal", *label_args, name)

    def create_container(name: str, net: str, *, run: bool) -> str:
        args = ["run" if run else "create"]
        if run:
            args.append("--detach")
        args.extend(("--pull", "never", "--name", name, "--network", net, *label_args))
        args.extend((
            "--tmpfs", "/data/db:rw,noexec,nosuid,size=256m",
            "--tmpfs", "/data/configdb:rw,noexec,nosuid,size=64m",
        ))
        if run:
            args.extend(("--network-alias", "mongo-contract"))
            args.extend(("mongo:7.0.43", "mongod", "--bind_ip_all"))
        else:
            args.extend(("--entrypoint", "sh", "mongo:7.0.43", "-c", "true"))
        return _docker(*args)

    try:
        network_ids[network] = make_network(network)
        network_ids[companion_network] = make_network(companion_network)
        container_ids[container] = create_container(container, network, run=True)
        _docker("network", "connect", companion_network, container_ids[container])

        network_inspect = _verify_network(network_ids[network], network, labels)
        container_inspect = _verify_container(container_ids[container], container, labels)
        companion_inspect = _verify_network(network_ids[companion_network], companion_network, labels)
        endpoint = network_inspect["Containers"][container_ids[container]]
        endpoint_config = container_inspect["NetworkSettings"]["Networks"][network]
        attached_names = set(container_inspect["NetworkSettings"]["Networks"])
        assert version
        assert endpoint["Name"] == container
        assert "mongo-contract" in endpoint_config["Aliases"]
        assert attached_names == {network, companion_network}
        assert len(network_inspect["Containers"]) == 1
        assert companion_inspect["Internal"] is True

        container_ids[preflight_container] = create_container(preflight_container, network, run=False)
        preflight = _verify_container(container_ids[preflight_container], preflight_container, labels)
        assert preflight["HostConfig"]["NetworkMode"] == network
        _docker("start", "--attach", container_ids[preflight_container])
        stopped_preflight = _verify_container(container_ids[preflight_container], preflight_container, labels)
        assert set(stopped_preflight["NetworkSettings"]["Networks"]) == {network}
        network_after = _verify_network(network_ids[network], network, labels)
        assert set(network_after["Containers"]) == {container_ids[container]}
        with capsys.disabled():
            print(f"Checking owned Docker Engine {version} resources")
    finally:
        # Do not guess at ownership if a create command returned ambiguously.
        # Recover only exact random names whose labels match this invocation.
        for name in (preflight_container, container):
            if name not in container_ids:
                try:
                    candidate = _inspect_one("inspect", name)
                    candidate_id = candidate.get("Id")
                    if isinstance(candidate_id, str) and owned_resource(
                        candidate, labels, resource_id=candidate_id, name=name,
                    ):
                        container_ids[name] = candidate_id
                except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError):
                    pass
        for name in (preflight_container, container):
            _cleanup_container(container_ids.get(name), name, labels)
        for name in (companion_network, network):
            if name not in network_ids:
                try:
                    candidate = _inspect_one("network", "inspect", name)
                    candidate_id = candidate.get("Id")
                    if isinstance(candidate_id, str) and owned_resource(
                        candidate, labels, resource_id=candidate_id, name=name,
                    ):
                        network_ids[name] = candidate_id
                except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError):
                    pass
        for name in (companion_network, network):
            _cleanup_network(network_ids.get(name), name, labels)
