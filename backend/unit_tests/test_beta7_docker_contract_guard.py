"""Offline checks for the ownership gate around the legacy Docker contract."""

from __future__ import annotations

import pytest
import test_g2_docker_api_contract as legacy_contract


def test_legacy_docker_contract_requires_explicit_opt_in_by_default(monkeypatch):
    monkeypatch.delenv("TRILHACODE_RUN_G2_DOCKER_CONTRACT", raising=False)
    monkeypatch.setattr(legacy_contract.shutil, "which", lambda _: "docker")
    with pytest.raises(pytest.skip.Exception):
        legacy_contract.test_docker_network_and_container_inspect_keep_names_and_aliases_in_expected_objects(
            capsys=None,
        )


def test_cleanup_proof_requires_exact_id_name_and_all_owner_labels(monkeypatch):
    run_id = "a" * 32
    owner = "b" * 64
    labels = legacy_contract.expected_labels(run_id, owner)
    resource_id = "c" * 64
    resource = {
        "Id": resource_id,
        "Name": "/tc-beta7-g2-mongo-test",
        "Config": {"Labels": labels},
        "HostConfig": {},
        "Mounts": [],
    }
    monkeypatch.setattr(legacy_contract, "_inspect_one", lambda *_: resource)
    monkeypatch.setattr(legacy_contract, "_docker", lambda *_args, **_kwargs: pytest.fail("must not remove"))

    altered = dict(resource)
    altered["Config"] = {"Labels": {**labels, legacy_contract.LABEL_OWNER: "wrong"}}
    monkeypatch.setattr(legacy_contract, "_inspect_one", lambda *_: altered)
    with pytest.raises(RuntimeError, match="Propriedade do container"):
        legacy_contract._cleanup_container(resource_id, "tc-beta7-g2-mongo-test", labels)


def test_container_cleanup_rejects_published_ports(monkeypatch):
    run_id = "d" * 32
    owner = "e" * 64
    labels = legacy_contract.expected_labels(run_id, owner)
    resource_id = "f" * 64
    resource = {
        "Id": resource_id,
        "Name": "/tc-beta7-g2-mongo-test",
        "Config": {"Labels": labels},
        "HostConfig": {"PortBindings": {"27017/tcp": []}},
        "Mounts": [],
    }
    monkeypatch.setattr(legacy_contract, "_inspect_one", lambda *_: resource)
    monkeypatch.setattr(legacy_contract, "_docker", lambda *_args, **_kwargs: pytest.fail("must not remove"))
    with pytest.raises(RuntimeError, match="fora do isolamento"):
        legacy_contract._cleanup_container(resource_id, "tc-beta7-g2-mongo-test", labels)


def test_container_cleanup_allows_only_the_declared_tmpfs(monkeypatch):
    run_id = "a" * 32
    owner = "b" * 64
    labels = legacy_contract.expected_labels(run_id, owner)
    resource_id = "c" * 64
    resource = {
        "Id": resource_id,
        "Name": "/tc-beta7-g2-mongo-test",
        "Config": {"Labels": labels},
        "HostConfig": {"Tmpfs": {
            "/data/db": "rw,noexec,nosuid,size=256m",
            "/data/configdb": "rw,noexec,nosuid,size=64m",
        }},
        # Docker Desktop can omit tmpfs entries from .Mounts; HostConfig.Tmpfs
        # is the effective configuration to verify in that response shape.
        "Mounts": [],
    }
    removed = []
    monkeypatch.setattr(legacy_contract, "_inspect_one", lambda *_: resource)
    monkeypatch.setattr(legacy_contract, "_docker", lambda *args, **_kwargs: removed.append(args))
    legacy_contract._cleanup_container(resource_id, "tc-beta7-g2-mongo-test", labels)
    assert removed == [("rm", "--force", resource_id)]


def test_container_cleanup_rejects_bind_mounts_even_with_matching_ownership(monkeypatch):
    run_id = "a" * 32
    owner = "b" * 64
    labels = legacy_contract.expected_labels(run_id, owner)
    resource_id = "c" * 64
    resource = {
        "Id": resource_id,
        "Name": "/tc-beta7-g2-mongo-test",
        "Config": {"Labels": labels},
        "HostConfig": {"Binds": ["C:/shared:/data/db"]},
        "Mounts": [{"Type": "bind", "Destination": "/data/db"}],
    }
    monkeypatch.setattr(legacy_contract, "_inspect_one", lambda *_: resource)
    monkeypatch.setattr(legacy_contract, "_docker", lambda *_args, **_kwargs: pytest.fail("must not remove"))
    with pytest.raises(RuntimeError, match="fora do isolamento"):
        legacy_contract._cleanup_container(resource_id, "tc-beta7-g2-mongo-test", labels)
