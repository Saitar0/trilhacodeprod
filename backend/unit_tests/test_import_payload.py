from import_payload import MAX_IMPORT_PAYLOAD_BYTES, validate_import_shape


def _valid_payload():
    return {
        "track": {"slug": "synthetic-track", "title": "Synthetic Track"},
        "nodes": [{"ref": "phase-1", "kind": "phase", "title": "Phase 1", "children": [{
            "ref": "topic-1", "kind": "topic", "title": "Topic 1",
            "blocks": [{"ref": "theory", "type": "theory_text", "data": {"body": "synthetic"}}],
        }]}],
        "relations": [],
    }


def test_import_payload_accepts_supported_legacy_additional_content_fields():
    payload = _valid_payload()
    payload["nodes"][0]["legacy_editor_field"] = {"color": "blue"}
    payload["nodes"][0]["children"][0]["blocks"][0]["data"]["legacy_field"] = "kept by current contract"
    assert validate_import_shape(payload) == []


def test_import_payload_rejects_invalid_types_and_nonfinite_numbers():
    payload = _valid_payload()
    payload["nodes"][0]["children"][0]["estimated_minutes"] = True
    payload["nodes"][0]["children"][0]["blocks"][0]["data"]["score"] = float("inf")
    errors = validate_import_shape(payload)
    assert any(error["path"].endswith("estimated_minutes") for error in errors)
    assert any("finito" in error["message"] for error in errors)


def test_import_payload_rejects_oversized_payload_before_planning():
    payload = {"track": {"slug": "synthetic-track", "title": "x" * (MAX_IMPORT_PAYLOAD_BYTES + 1)}}
    errors = validate_import_shape(payload)
    assert errors == [{"path": "payload", "message": "payload excede o limite de 32 MiB"}]
