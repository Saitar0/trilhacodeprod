from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def _imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_assessment_router_is_not_imported_by_operational_application() -> None:
    operational_entrypoints = (BACKEND / "server.py", BACKEND / "main.py")
    for path in operational_entrypoints:
        if path.exists():
            imports = _imported_names(path)
            assert "test_support.beta7_2_assessment_router" not in imports
            assert "services.beta7_2_assessment" not in imports


def test_gated_test_composition_checks_ownership_before_mounting_assessment_router() -> None:
    source = (BACKEND / "test_support" / "beta7_1_preview_server.py").read_text(encoding="utf-8")
    gate = source.index("connect_internal_verified_target(")
    router_import = source.index("from test_support.beta7_2_assessment_router import router")
    router_mount = source.index("app.include_router(_assessment_router)")
    assert gate < router_import < router_mount


def test_assessment_service_uses_only_disposable_preview_namespace() -> None:
    source = (BACKEND / "services" / "beta7_2_assessment.py").read_text(encoding="utf-8")
    assert 'settings.db_name}_beta7_1_preview' in source
    forbidden = ("db.tracks", "db.nodes", "db.blocks", "track_publications", "student_progress")
    assert all(name not in source for name in forbidden)
