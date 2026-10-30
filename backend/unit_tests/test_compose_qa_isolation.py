import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

COMPOSE_FILE = Path(__file__).resolve().parents[2] / "compose.qa.yaml"


def _render(project: str, api_port: str, frontend_port: str) -> dict:
    docker = shutil.which("docker")
    if not docker:
        pytest.skip("Docker Compose CLI is required for offline Compose rendering")

    environment = os.environ.copy()
    environment.update({
        "QA_MONGO_ROOT_USERNAME": "synthetic-compose-user",
        "QA_MONGO_ROOT_PASSWORD": "synthetic-compose-password",
        "QA_JWT_SECRET": "synthetic-compose-only-jwt-secret",
        "QA_API_PORT": api_port,
        "QA_FRONTEND_PORT": frontend_port,
    })
    result = subprocess.run(
        [docker, "compose", "--project-name", project, "-f", str(COMPOSE_FILE),
         "config", "--format", "json"],
        capture_output=True,
        text=True,
        env=environment,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, "Compose QA configuration should render with synthetic variables"
    return json.loads(result.stdout)


def test_qa_compose_resources_are_project_scoped_and_keep_isolation_contract():
    first = _render("trilhacode-qa-probe-a", "18181", "13181")
    second = _render("trilhacode-qa-probe-b", "18182", "13182")

    assert first["name"] == "trilhacode-qa-probe-a"
    assert second["name"] == "trilhacode-qa-probe-b"

    for project, config, api_port, frontend_port in (
        ("trilhacode-qa-probe-a", first, "18181", "13181"),
        ("trilhacode-qa-probe-b", second, "18182", "13182"),
    ):
        networks = config["networks"]
        volumes = config["volumes"]
        services = config["services"]

        assert networks["qa_internal"]["name"].startswith(project)
        assert networks["qa_internal"]["internal"] is True
        assert networks["qa_access"]["name"].startswith(project)
        assert volumes["qa_mongo_data"]["name"].startswith(project)
        assert volumes["qa_frontend_node_modules"]["name"].startswith(project)
        assert all("container_name" not in service for service in services.values())

        assert set(services["mongo"]["networks"]) == {"qa_internal"}
        assert set(services["api"]["networks"]) == {"qa_internal", "qa_access"}
        assert set(services["frontend"]["networks"]) == {"qa_access"}
        assert "mongo" not in services["frontend"]["networks"]
        assert services["mongo"]["healthcheck"]
        assert services["api"]["healthcheck"]
        assert services["api"]["depends_on"]["mongo"]["condition"] == "service_healthy"
        assert services["frontend"]["depends_on"]["api"]["condition"] == "service_healthy"

        assert services["mongo"].get("ports", []) == []
        assert services["api"]["environment"]["FRONTEND_URL"] == f"http://localhost:{frontend_port}"
        assert services["api"]["environment"]["CORS_ORIGINS"] == f"http://localhost:{frontend_port}"
        assert services["frontend"]["environment"]["VITE_BACKEND_URL"] == f"http://localhost:{api_port}"
        api_binding = services["api"]["ports"][0]
        frontend_binding = services["frontend"]["ports"][0]
        assert (api_binding["host_ip"], api_binding["published"], api_binding["target"]) == (
            "127.0.0.1", api_port, 8000,
        )
        assert (frontend_binding["host_ip"], frontend_binding["published"], frontend_binding["target"]) == (
            "127.0.0.1", frontend_port, 3000,
        )

    for network_name in ("qa_internal", "qa_access"):
        assert first["networks"][network_name]["name"] != second["networks"][network_name]["name"]
    for volume_name in ("qa_mongo_data", "qa_frontend_node_modules"):
        assert first["volumes"][volume_name]["name"] != second["volumes"][volume_name]["name"]
