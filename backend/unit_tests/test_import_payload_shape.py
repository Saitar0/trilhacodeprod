import pytest

from import_payload import validate_import_shape


@pytest.mark.parametrize(
    ("payload", "path"),
    [
        ({"track": {"slug": []}, "nodes": []}, "track.slug"),
        ({"track": {}, "nodes": [{"ref": [], "kind": "module"}]}, "nodes[0].ref"),
        ({"track": {}, "nodes": [{"blocks": "not-a-list"}]}, "nodes[0].blocks"),
        ({"track": {}, "nodes": [{"blocks": [{"type": [], "data": []}]}]}, "nodes[0].blocks[0].type"),
        ({"track": {}, "relations": ["not-an-object"]}, "relations[0]"),
    ],
)
def test_import_shape_reports_malformed_values_with_a_path(payload, path):
    errors = validate_import_shape(payload)

    assert path in {error["path"] for error in errors}

