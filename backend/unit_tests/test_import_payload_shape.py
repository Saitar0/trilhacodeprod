import pytest

from import_payload import has_valid_parent_kind, validate_import_shape


@pytest.mark.parametrize(
    ("payload", "path"),
    [
        ({"track": {"slug": []}, "nodes": []}, "track.slug"),
        ({"track": {"title": 4}, "nodes": []}, "track.title"),
        ({"track": {}, "nodes": [{"ref": [], "kind": "module"}]}, "nodes[0].ref"),
        ({"track": {}, "nodes": [{"title": 4}]}, "nodes[0].title"),
        ({"track": {}, "nodes": [{"estimated_minutes": "many"}]}, "nodes[0].estimated_minutes"),
        ({"track": {}, "nodes": [{"estimated_minutes": {}}]}, "nodes[0].estimated_minutes"),
        ({"track": {}, "nodes": [{"blocks": "not-a-list"}]}, "nodes[0].blocks"),
        ({"track": {}, "nodes": [{"blocks": [{"type": [], "data": []}]}]}, "nodes[0].blocks[0].type"),
        ({"track": {}, "relations": ["not-an-object"]}, "relations[0]"),
    ],
)
def test_import_shape_reports_malformed_values_with_a_path(payload, path):
    errors = validate_import_shape(payload)

    assert path in {error["path"] for error in errors}


def test_import_shape_limits_nested_nodes_before_python_recursion_limit():
    root = node = {"ref": "node-0", "kind": "phase"}
    for index in range(1, 105):
        child = {"ref": f"node-{index}", "kind": "phase"}
        node["children"] = [child]
        node = child

    errors = validate_import_shape({"track": {}, "nodes": [root]})

    assert any("profundidade máxima" in error["message"] for error in errors)


def test_invalid_parent_kind_is_reported_without_hierarchy_index_lookup():
    hierarchy = ["phase", "module", "topic"]

    assert not has_valid_parent_kind("unknown", hierarchy)
    assert has_valid_parent_kind("module", hierarchy)

