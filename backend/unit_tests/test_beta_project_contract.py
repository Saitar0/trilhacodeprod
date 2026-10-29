import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from curriculum_contract.beta_project_contract import ProjectArtifactKind, ProjectArtifactReference


def test_real_project_35_manifest_inventories_eleven_artifacts_without_bodies():
    manifest_path = Path(__file__).parents[2] / "docs" / "beta" / "beta5-project-3-5-artifacts.json"
    inventory = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert inventory["project_id"] == "3.5"
    assert inventory["artifact_count"] == 11
    artifacts = tuple(ProjectArtifactReference.model_validate(item) for item in inventory["artifacts"])
    assert len({item.artifact_id for item in artifacts}) == 11
    assert {item.kind for item in artifacts} == {
        ProjectArtifactKind.PROJECT_BRIEF,
        ProjectArtifactKind.MILESTONE,
        ProjectArtifactKind.RUBRIC,
        ProjectArtifactKind.CHECKLIST,
    }
    assert all("content" not in item.model_dump() for item in artifacts)


def test_project_inventory_rejects_invalid_hash_and_unknown_content():
    with pytest.raises(ValidationError):
        ProjectArtifactReference.model_validate({
            "artifact_id": "synthetic-artifact",
            "kind": "milestone",
            "source_path": "synthetic.md",
            "content_sha256": "bad",
            "order": 1,
            "source_item_ids": ["M01"],
            "body": "must not be copied into a provenance-only inventory",
        })
