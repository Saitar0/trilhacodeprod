import math

from bson import BSON
from bson.errors import InvalidDocument

NODE_TAX = {"pedagogical_type": "pedagogical_type", "requirement": "requirement", "depth": "depth"}
TRACK_TEXT = ("title", "subtitle", "description", "cover_url", "visibility", "difficulty")
NODE_TEXT = ("title", "summary", "description", "guidance", "notes")
MAX_NODE_DEPTH = 100
MAX_ESTIMATED_MINUTES = (1 << 63) - 1
MIN_BSON_INT64 = -(1 << 63)
MAX_IMPORT_DOCUMENT_BYTES = 15 * 1024 * 1024


def _bson_size_within_limit(value, max_bytes=None):
    """Keep each future Mongo document below 16 MiB, leaving room for DB metadata."""
    if max_bytes is None:
        max_bytes = MAX_IMPORT_DOCUMENT_BYTES
    try:
        return len(BSON.encode({"value": value})) <= max_bytes
    except (InvalidDocument, OverflowError, TypeError, ValueError):
        return False


def _validate_json_value(value, path, errors, depth=0):
    if depth > MAX_NODE_DEPTH:
        errors.append({"path": path, "message": f"profundidade máxima de {MAX_NODE_DEPTH} níveis excedida"})
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or "\x00" in key:
                errors.append({"path": path, "message": "chaves devem ser textos sem caractere nulo"})
                continue
            try:
                key.encode("utf-8")
            except UnicodeEncodeError:
                errors.append({"path": path, "message": "chave deve conter texto UTF-8 válido"})
                continue
            _validate_json_value(child, f"{path}.{key}", errors, depth + 1)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_json_value(child, f"{path}[{index}]", errors, depth + 1)
    elif isinstance(value, int) and not isinstance(value, bool):
        if not MIN_BSON_INT64 <= value <= MAX_ESTIMATED_MINUTES:
            errors.append({"path": path, "message": "inteiro fora do intervalo BSON int64"})
    elif isinstance(value, float):
        if not math.isfinite(value):
            errors.append({"path": path, "message": "número deve ser finito"})
    elif isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            errors.append({"path": path, "message": "texto deve conter UTF-8 válido"})
    elif value is not None and not isinstance(value, bool):
        errors.append({"path": path, "message": "valor não é JSON compatível"})


def validate_import_shape(payload: dict) -> list[dict]:
    """Reject malformed containers before import planning dereferences or hashes them."""
    errors = []
    _validate_json_value(payload, "payload", errors)

    def add(path, message):
        errors.append({"path": path, "message": message})

    # The lossless curriculum bundle is intentionally not interpreted as a legacy
    # {track, nodes, relations} payload. Refuse it here so the old importer cannot
    # silently create an empty/partial track by ignoring its phase contracts.
    if "schema_version" in payload:
        add(
            "schema_version",
            "pacote curricular versionado requer adaptador explícito; o importador legado recusou a carga para evitar importação parcial",
        )

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
                        value = int(value)
                        valid_minutes = bool(node["estimated_minutes"].strip())
                    except ValueError:
                        valid_minutes = False
                valid_minutes = valid_minutes and 0 <= value <= MAX_ESTIMATED_MINUTES
                if not valid_minutes:
                    add(f"{node_path}.estimated_minutes", "deve ser um número inteiro entre 0 e 9223372036854775807")
            for field in NODE_TAX:
                if node.get(field) is not None and not isinstance(node[field], str):
                    add(f"{node_path}.{field}", "deve ser texto")
            for field in ("tags", "blocks"):
                values = node.get(field)
                if values is not None and not isinstance(values, list):
                    add(f"{node_path}.{field}", "deve ser uma lista")
                    continue
                if field == "tags" and isinstance(values, list):
                    for tag_index, tag in enumerate(values):
                        tag_path = f"{node_path}.tags[{tag_index}]"
                        if not isinstance(tag, str):
                            add(tag_path, "deve ser texto")
                            continue
                        tag_doc = {"name": tag, "slug": tag.lower().replace(" ", "-"), "color": "slate", "created_at": None}
                        if not _bson_size_within_limit(tag_doc):
                            add(tag_path, "documento excede o limite seguro de tamanho para importação")
                if field == "blocks" and isinstance(values, list):
                    for j, block in enumerate(values):
                        block_path = f"{node_path}.blocks[{j}]"
                        if not isinstance(block, dict):
                            add(block_path, "deve ser um objeto")
                            continue
                        if "type" in block and not isinstance(block["type"], str):
                            add(f"{block_path}.type", "deve ser texto")
                        if "ref" in block and block["ref"] is not None and not isinstance(block["ref"], str):
                            add(f"{block_path}.ref", "deve ser texto")
                        for field in ("title", "status"):
                            if field in block and not isinstance(block[field], str):
                                add(f"{block_path}.{field}", "deve ser texto")
                        if block.get("data") is not None and not isinstance(block["data"], dict):
                            add(f"{block_path}.data", "deve ser um objeto")
            children = node.get("children")
            if children is not None:
                validate_nodes(children, f"{node_path}.children", depth + 1)

    validate_nodes(payload.get("nodes", []), "nodes")

    # MongoDB limits each stored document to 16 MiB. Imports write the track and
    # nodes before their blocks, so reject oversized source records up front to
    # avoid a late block failure leaving a partially applied import. The 15 MiB
    # cap reserves space for the IDs and metadata added by _execute.
    track = payload.get("track")
    if isinstance(track, dict):
        stored_track_fields = {key: track[key] for key in (*TRACK_TEXT, "slug", "audience", "level_labels", "settings", "hierarchy") if key in track}
        if not _bson_size_within_limit(stored_track_fields):
            add("track", "documento excede o limite seguro de tamanho para importação")

    def validate_document_sizes(items, path, depth=0):
        if depth > MAX_NODE_DEPTH or not isinstance(items, list):
            return
        for index, node in enumerate(items):
            node_path = f"{path}[{index}]"
            if not isinstance(node, dict):
                continue
            stored_node_fields = {
                "track_id": "0" * 24,
                "parent_id": "0" * 24,
                "kind": node.get("kind", ""),
                "title": node.get("title", "").strip() if isinstance(node.get("title", ""), str) else "",
                "slug": node.get("title", "").strip().lower() if isinstance(node.get("title", ""), str) else "",
                "order": 0,
                "status": node.get("status", "draft"),
                "estimated_minutes": 0,
                "tag_ids": ["0" * 24 for _ in node.get("tags", [])] if isinstance(node.get("tags"), list) else [],
                "updated_at": None,
                "summary": node.get("summary", ""),
                "description": node.get("description", ""),
                "guidance": node.get("guidance", ""),
                "notes": node.get("notes", ""),
                "pedagogical_type": node.get("pedagogical_type", ""),
                "requirement": node.get("requirement", ""),
                "depth": node.get("depth", ""),
                "release": {},
                "meta": {"import_ref": node.get("ref", "")},
                "created_by": "0" * 24,
                "created_at": None,
            }
            if not _bson_size_within_limit(stored_node_fields):
                add(node_path, "documento excede o limite seguro de tamanho para importação")
            blocks = node.get("blocks")
            if isinstance(blocks, list):
                for block_index, block in enumerate(blocks):
                    if not isinstance(block, dict):
                        continue
                    block_ref = block.get("ref")
                    block_doc = {
                        "node_id": "0" * 24,
                        "track_id": "0" * 24,
                        "type": block.get("type", ""),
                        "title": block.get("title", ""),
                        "data": block.get("data") or {},
                        "status": block.get("status", "published"),
                        "order": block_index,
                        "updated_at": None,
                        "meta": {"import_ref": f"{node.get('ref', '')}/{block_ref}"} if block_ref else {},
                        "schema_version": 1,
                        "created_at": None,
                    }
                    if not _bson_size_within_limit(block_doc):
                        add(f"{node_path}.blocks[{block_index}]", "documento excede o limite seguro de tamanho para importação")
            validate_document_sizes(node.get("children"), f"{node_path}.children", depth + 1)

    validate_document_sizes(payload.get("nodes"), "nodes")

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
            if not _bson_size_within_limit(relation):
                add(path, "documento excede o limite seguro de tamanho para importação")

    return errors


def has_valid_parent_kind(parent_kind: str | None, hierarchy: list[str]) -> bool:
    return parent_kind is None or parent_kind in hierarchy

