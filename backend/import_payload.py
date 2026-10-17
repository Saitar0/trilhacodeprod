NODE_TAX = {"pedagogical_type": "pedagogical_type", "requirement": "requirement", "depth": "depth"}
TRACK_TEXT = ("title", "subtitle", "description", "cover_url", "visibility", "difficulty")
NODE_TEXT = ("title", "summary", "description", "guidance", "notes")
MAX_NODE_DEPTH = 100


def validate_import_shape(payload: dict) -> list[dict]:
    """Reject malformed containers before import planning dereferences or hashes them."""
    errors = []

    def add(path, message):
        errors.append({"path": path, "message": message})

    track = payload.get("track")
    if not isinstance(track, dict):
        add("track", "deve ser um objeto")
    else:
        for field in (*TRACK_TEXT, "slug"):
            if field in track and not isinstance(track[field], str):
                add(f"track.{field}", "deve ser texto")
        if "audience" in track and (
            not isinstance(track["audience"], list)
            or any(not isinstance(item, str) for item in track["audience"])
        ):
            add("track.audience", "deve ser uma lista de textos")
        for field in ("settings", "level_labels"):
            if field in track and not isinstance(track[field], dict):
                add(f"track.{field}", "deve ser um objeto")
        if "hierarchy" in track and track["hierarchy"] is not None and (
            not isinstance(track["hierarchy"], list)
            or any(not isinstance(kind, str) for kind in track["hierarchy"])
        ):
            add("track.hierarchy", "deve ser uma lista de textos")

    options = payload.get("options")
    if options is not None and not isinstance(options, dict):
        add("options", "deve ser um objeto")

    def validate_nodes(items, path, depth=0):
        if depth > MAX_NODE_DEPTH:
            add(path, f"profundidade máxima de {MAX_NODE_DEPTH} níveis excedida")
            return
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
            for field in ("ref", "kind", "status"):
                if field in node and not isinstance(node[field], str):
                    add(f"{node_path}.{field}", "deve ser texto")
            for field in NODE_TEXT:
                if field in node and not isinstance(node[field], str):
                    add(f"{node_path}.{field}", "deve ser texto")
            if "estimated_minutes" in node:
                value = node["estimated_minutes"]
                valid_minutes = isinstance(value, int) and not isinstance(value, bool)
                if isinstance(value, str):
                    try:
                        int(value)
                        valid_minutes = bool(value.strip())
                    except ValueError:
                        valid_minutes = False
                if not valid_minutes:
                    add(f"{node_path}.estimated_minutes", "deve ser um número inteiro")
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
                        for field in ("title", "status"):
                            if field in block and not isinstance(block[field], str):
                                add(f"{block_path}.{field}", "deve ser texto")
                        if block.get("data") is not None and not isinstance(block["data"], dict):
                            add(f"{block_path}.data", "deve ser um objeto")
            children = node.get("children")
            if children is not None:
                validate_nodes(children, f"{node_path}.children", depth + 1)

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
            if "note" in relation and not isinstance(relation["note"], str):
                add(f"{path}.note", "deve ser texto")

    return errors


def has_valid_parent_kind(parent_kind: str | None, hierarchy: list[str]) -> bool:
    return parent_kind is None or parent_kind in hierarchy

