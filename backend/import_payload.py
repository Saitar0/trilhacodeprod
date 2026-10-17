NODE_TAX = {"pedagogical_type": "pedagogical_type", "requirement": "requirement", "depth": "depth"}


def validate_import_shape(payload: dict) -> list[dict]:
    """Reject malformed containers before import planning dereferences or hashes them."""
    errors = []

    def add(path, message):
        errors.append({"path": path, "message": message})

    track = payload.get("track")
    if not isinstance(track, dict):
        add("track", "deve ser um objeto")
    else:
        if "slug" in track and not isinstance(track["slug"], str):
            add("track.slug", "deve ser texto")
        if "hierarchy" in track and track["hierarchy"] is not None and (
            not isinstance(track["hierarchy"], list)
            or any(not isinstance(kind, str) for kind in track["hierarchy"])
        ):
            add("track.hierarchy", "deve ser uma lista de textos")

    options = payload.get("options")
    if options is not None and not isinstance(options, dict):
        add("options", "deve ser um objeto")

    def validate_nodes(items, path):
        if items is None:
            return
        if not isinstance(items, list):
            add(path, "deve ser uma lista")
            return
        for i, node in enumerate(items):
            node_path = f"{path}[{i}]"
            if not isinstance(node, dict):
                add(node_path, "deve ser um objeto")
                continue
            for field in ("ref", "kind"):
                if field in node and not isinstance(node[field], str):
                    add(f"{node_path}.{field}", "deve ser texto")
            for field in NODE_TAX:
                if node.get(field) is not None and not isinstance(node[field], str):
                    add(f"{node_path}.{field}", "deve ser texto")
            for field in ("tags", "blocks"):
                values = node.get(field)
                if values is not None and not isinstance(values, list):
                    add(f"{node_path}.{field}", "deve ser uma lista")
                    continue
                if field == "blocks" and isinstance(values, list):
                    for j, block in enumerate(values):
                        block_path = f"{node_path}.blocks[{j}]"
                        if not isinstance(block, dict):
                            add(block_path, "deve ser um objeto")
                            continue
                        if "type" in block and not isinstance(block["type"], str):
                            add(f"{block_path}.type", "deve ser texto")
                        if block.get("data") is not None and not isinstance(block["data"], dict):
                            add(f"{block_path}.data", "deve ser um objeto")
            children = node.get("children")
            if children is not None:
                validate_nodes(children, f"{node_path}.children")

    validate_nodes(payload.get("nodes", []), "nodes")

    relations = payload.get("relations")
    if relations is not None and not isinstance(relations, list):
        add("relations", "deve ser uma lista")
    elif isinstance(relations, list):
        for i, relation in enumerate(relations):
            path = f"relations[{i}]"
            if not isinstance(relation, dict):
                add(path, "deve ser um objeto")
                continue
            for field in ("from", "to", "type"):
                if field in relation and not isinstance(relation[field], str):
                    add(f"{path}.{field}", "deve ser texto")

    return errors

