"""Validate the resolved Compose model without printing interpolated secrets."""

from __future__ import annotations

import json
import os
import sys


def main() -> int:
    try:
        config = json.load(sys.stdin)
        services = config["services"]
        networks = config["networks"]
        if set(services) != {"mongo", "harness"}:
            raise ValueError("conjunto de serviços inesperado")
        mongo = services["mongo"]
        harness = services["harness"]
        if mongo.get("image") != "mongo:7":
            raise ValueError("serviço Mongo não usa mongo:7")
        if mongo.get("tmpfs") != ["/data/db"]:
            raise ValueError("dados Mongo não estão somente em tmpfs")
        forbidden_service_keys = {
            "ports",
            "volumes",
            "container_name",
            "privileged",
            "devices",
            "cap_add",
            "network_mode",
        }
        for name, service in services.items():
            unexpected = forbidden_service_keys.intersection(service)
            if unexpected:
                raise ValueError(f"serviço {name} contém recursos não isolados")
        if (
            "editorial_poc" not in networks
            or networks["editorial_poc"].get("internal") is not True
        ):
            raise ValueError("rede de teste não é interna")
        for name, service in services.items():
            service_networks = service.get("networks", {})
            if set(service_networks) != {"editorial_poc"}:
                raise ValueError(f"serviço {name} está fora da única rede privada")
            labels = service.get("labels", {})
            if labels.get("io.trilhacode.editorial-poc.run") != os.environ.get(
                "EDITORIAL_POC_RUN_ID"
            ):
                raise ValueError(f"serviço {name} não está marcado para a execução")
        if harness.get("environment", {}).get("EDITORIAL_POC_MONGO_HOST") != "mongo":
            raise ValueError("runner não está limitado ao serviço Compose mongo")
        if harness.get("environment", {}).get("EDITORIAL_POC_DISPOSABLE") != "1":
            raise ValueError("runner não está marcado como descartável")
        print(
            "Compose isolation contract: OK (MongoDB 7, network internal, sem portas ou volumes)."
        )
        return 0
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Compose isolation contract rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
