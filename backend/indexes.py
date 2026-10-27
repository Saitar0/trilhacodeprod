# ruff: noqa: EXE002
"""MongoDB index definitions and read-only release preflight."""

from database import db

# (collection, keys, options, duplicate-check fields)
INDEXES = [
    ("tracks", [("slug", 1)],
     {"unique": True, "name": "one_track_slug", "partialFilterExpression": {"slug": {"$type": "string"}}},
     ("slug",)),
    ("users", [("email", 1)], {"unique": True}, ("email",)),
    (
        "auth_sessions",
        [("expires_at", 1)],
        {"expireAfterSeconds": 0, "name": "auth_session_expiry"},
        None,
    ),
    ("login_attempts", [("identifier", 1)], {}, None),
    ("login_attempts", [("last", 1)], {"expireAfterSeconds": 3600}, None),
    ("nodes", [("track_id", 1), ("parent_id", 1), ("order", 1)], {}, None),
    ("nodes", [("track_id", 1), ("meta.import_ref", 1)],
     {"unique": True, "name": "one_node_import_ref", "partialFilterExpression": {"meta.import_ref": {"$type": "string"}}},
     ("track_id", "meta.import_ref")),
    ("nodes", [("title", "text"), ("summary", "text")], {"name": "node_search_text"}, None),
    ("content_blocks", [("node_id", 1), ("order", 1)], {}, None),
    ("content_blocks", [("track_id", 1), ("meta.import_ref", 1)],
     {"unique": True, "name": "one_block_import_ref", "partialFilterExpression": {"meta.import_ref": {"$type": "string"}}},
     ("track_id", "meta.import_ref")),
    ("relations", [("track_id", 1)], {}, None),
    ("relations", [("track_id", 1), ("node_id", 1), ("target_id", 1), ("type", 1)],
     {"unique": True, "name": "one_track_relation"}, ("track_id", "node_id", "target_id", "type")),
    ("progress", [("user_id", 1), ("track_id", 1)], {}, None),
    ("progress", [("user_id", 1), ("node_id", 1), ("block_id", 1)], {"unique": True},
     ("user_id", "node_id", "block_id")),
    ("user_track_state", [("user_id", 1), ("track_id", 1)],
     {"unique": True, "name": "one_user_track_state"}, ("user_id", "track_id")),
    ("learning_events", [("user_id", 1), ("at", -1)], {}, None),
    ("edit_history", [("track_id", 1), ("at", -1)], {}, None),
    ("edit_history", [("import_operation_id", 1)],
     {"unique": True, "name": "one_import_audit", "partialFilterExpression": {"import_operation_id": {"$type": "string"}}},
     ("import_operation_id",)),
    ("taxonomies", [("group", 1), ("key", 1)], {"unique": True}, ("group", "key")),
    ("block_types", [("key", 1)], {"unique": True}, ("key",)),
    ("tags", [("slug", 1)], {"unique": True, "name": "one_tag_slug"}, ("slug",)),
    ("submissions", [("user_id", 1), ("block_id", 1), ("attempt", -1)], {"unique": True},
     ("user_id", "block_id", "attempt")),
    ("submissions", [("status", 1), ("submitted_at", 1)], {}, None),
    ("notes", [("user_id", 1), ("node_id", 1), ("block_id", 1)], {"unique": True},
     ("user_id", "node_id", "block_id")),
    ("reviews", [("user_id", 1), ("status", 1), ("due_at", 1)], {}, None),
    ("reviews", [("user_id", 1), ("node_id", 1), ("block_id", 1)],
     {"unique": True, "name": "one_pending_review", "partialFilterExpression": {"status": "pending"}},
     ("user_id", "node_id", "block_id")),
    ("version_chunks", [("version_id", 1), ("seq", 1)], {"unique": True}, ("version_id", "seq")),
    ("restore_jobs", [("track_id", 1)],
     {"unique": True, "name": "one_running_restore", "partialFilterExpression": {"status": "running"}},
     ("track_id",)),
    ("migrations", [("key", 1)], {"unique": True}, ("key",)),
]


def _options(index: dict) -> dict:
    options = {key: index[key] for key in (
        "unique", "sparse", "expireAfterSeconds", "partialFilterExpression", "collation", "hidden",
        "wildcardProjection",
    )
            if key in index}
    # MongoDB may return its implicit default collation in listIndexes even when
    # the index was created without an explicit collation.
    if options.get("collation") == {"locale": "simple"}:
        options.pop("collation")
    return options


def _same_keys(index: dict, expected_keys: tuple) -> bool:
    actual_keys = tuple(index["key"].items())
    if actual_keys == expected_keys:
        return True
    # MongoDB stores text index fields as an internal _fts key and a weights map.
    return (expected_keys and all(direction == "text" for _, direction in expected_keys)
            and actual_keys == (("_fts", "text"), ("_ftsx", 1)))


def _keys_match(index: dict, expected_keys: tuple) -> bool:
    if not _same_keys(index, expected_keys):
        return False
    if expected_keys and all(direction == "text" for _, direction in expected_keys):
        return index.get("weights") == {field: 1 for field, _ in expected_keys}
    return True


async def _duplicates(collection, fields: tuple[str, ...], partial_filter: dict | None = None) -> list[dict]:
    # Unique indexes treat missing and null as the same key value.
    # Keep the key as an array: MongoDB field names in a $group _id object cannot
    # contain dots, while indexed paths such as "meta.import_ref" are valid inputs.
    group_id = [{"$ifNull": [f"${field}", None]} for field in fields]
    pipeline = ([{"$match": partial_filter}] if partial_filter else []) + [
        {"$group": {"_id": group_id, "count": {"$sum": 1}, "sample_id": {"$first": "$_id"}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$limit": 20},
    ]
    cursor = await collection.aggregate(pipeline)
    rows = await cursor.to_list(20)
    return [{"values": dict(zip(fields, row["_id"], strict=True)),
             "count": row["count"], "sample_id": str(row["sample_id"])} for row in rows]


async def preflight_indexes() -> list[str]:
    """Inspect current index definitions and unique-key duplicates without writing."""
    findings = []
    existing_collections = set(await db.list_collection_names())
    for collection_name, keys, options, unique_fields in INDEXES:
        collection = db[collection_name]
        collection_exists = collection_name in existing_collections
        existing = await (await collection.list_indexes()).to_list(1000) if collection_exists else []
        expected_keys = tuple(keys)
        same_keys = [index for index in existing if _same_keys(index, expected_keys)]
        expected_options = {key: value for key, value in options.items()
                            if key in ("unique", "sparse", "expireAfterSeconds", "partialFilterExpression",
                                       "collation", "hidden", "wildcardProjection")}
        expected_name = options.get("name") or "_".join(f"{field}_{direction}" for field, direction in keys)
        matches = [index for index in same_keys
                   if _keys_match(index, expected_keys) and _options(index) == expected_options
                   and index["name"] == expected_name]
        label = expected_name
        if matches:
            findings.append(f"OK {collection_name}.{label}: índice compatível presente")
        elif same_keys:
            findings.append(f"CONFLITO {collection_name}.{label}: mesmas chaves com opções diferentes; "
                             f"existente={[_options(index) for index in same_keys]}")
        else:
            findings.append(f"AUSENTE {collection_name}.{label}: será criado por ensure-indexes")
        if unique_fields:
            duplicates = (await _duplicates(collection, unique_fields, options.get("partialFilterExpression"))
                          if collection_exists else [])
            if duplicates:
                findings.append(f"DUPLICATAS {collection_name}.{label}: {duplicates}")
    return findings


async def preflight_index_checks(database) -> list[dict[str, str]]:
    """Return the versioned G2 check set without document-derived values."""
    checks: list[dict[str, str]] = []
    existing_collections = set(await database.list_collection_names())
    for collection_name, keys, options, unique_fields in INDEXES:
        collection = database[collection_name]
        collection_exists = collection_name in existing_collections
        existing = await (await collection.list_indexes()).to_list(1000) if collection_exists else []
        expected_keys = tuple(keys)
        same_keys = [index for index in existing if _same_keys(index, expected_keys)]
        expected_options = {key: value for key, value in options.items()
                            if key in ("unique", "sparse", "expireAfterSeconds", "partialFilterExpression",
                                       "collation", "hidden", "wildcardProjection")}
        expected_name = options.get("name") or "_".join(f"{field}_{direction}" for field, direction in keys)
        matches = [index for index in same_keys
                   if _keys_match(index, expected_keys) and _options(index) == expected_options
                   and index["name"] == expected_name]
        if matches:
            index_status = "OK"
        elif same_keys:
            index_status = "CONFLITO"
        else:
            index_status = "AUSENTE"
        checks.append({"id": f"index/{collection_name}/{expected_name}", "status": index_status})

        if unique_fields:
            duplicate_status = "AUSENTE" if not collection_exists else "OK"
            if collection_exists:
                group_id = {field: {"$ifNull": [f"${field}", None]} for field in unique_fields}
                pipeline = ([{"$match": options["partialFilterExpression"]}]
                            if options.get("partialFilterExpression") else []) + [
                    {"$group": {"_id": group_id, "count": {"$sum": 1}}},
                    {"$match": {"count": {"$gt": 1}}},
                    {"$limit": 1},
                ]
                cursor = await collection.aggregate(pipeline, maxTimeMS=10_000)
                if await cursor.to_list(1):
                    duplicate_status = "DUPLICATAS"
            checks.append({
                "id": f"duplicates/{collection_name}/{expected_name}",
                "status": duplicate_status,
            })
    return checks


async def ensure_indexes() -> None:
    findings = await preflight_indexes()
    blockers = [finding for finding in findings if finding.startswith(("CONFLITO ", "DUPLICATAS "))]
    if blockers:
        raise RuntimeError("Preflight bloqueou criação de índices; reconciliação manual necessária: " + "; ".join(blockers))
    for collection_name, keys, options, _unique_fields in INDEXES:
        await db[collection_name].create_index(keys, **options)
