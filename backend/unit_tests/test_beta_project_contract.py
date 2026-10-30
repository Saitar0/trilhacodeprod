import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from curriculum_contract.beta_project_contract import (
    ProjectArtifact,
    ProjectArtifactKind,
    ProjectArtifactReference,
    ProjectCompletionRule,
    ProjectPackage,
    ProjectRubric,
    ProjectStep,
)
from curriculum_contract.beta_protected_content import DataClassification


def _artifact(artifact_id: str, kind: ProjectArtifactKind) -> ProjectArtifact:
    return ProjectArtifact(
        artifact_id=artifact_id,
        kind=kind,
        purpose="test",
        source_path=f"{artifact_id}.md",
        content_sha256="a" * 64,
        order=1,
        project_id="3.5",
        phase_id="1",
        student_content="public",
        classification=DataClassification.STUDENT_PUBLIC,
    )


def _package(*artifacts: ProjectArtifact, **kwargs) -> ProjectPackage:
    return ProjectPackage(
        title="Synthetic project",
        source_sha256="b" * 64,
        source_revision="synthetic",
        artifacts=artifacts,
        **kwargs,
    )


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


def test_project_graph_rejects_wrong_reference_kinds_and_duplicates():
    brief = _artifact("brief", ProjectArtifactKind.PROJECT_BRIEF)
    checklist = _artifact("checklist", ProjectArtifactKind.CHECKLIST)
    rubric = _artifact("rubric", ProjectArtifactKind.RUBRIC)
    with pytest.raises(ValueError, match="não é instrução"):
        _package(
            checklist,
            steps=(ProjectStep(step_id="S1", order=1, instruction_artifact_id="checklist"),),
        )
    with pytest.raises(ValueError, match="não é checklist"):
        _package(
            brief,
            rubric,
            steps=(
                ProjectStep(
                    step_id="S1",
                    order=1,
                    instruction_artifact_id="brief",
                    acceptance_artifact_id="rubric",
                ),
            ),
        )
    with pytest.raises(ValueError, match="IDs de etapa"):
        _package(
            brief,
            steps=(
                ProjectStep(step_id="S1", order=1, instruction_artifact_id="brief"),
                ProjectStep(step_id="S1", order=2, instruction_artifact_id="brief"),
            ),
        )


def test_project_graph_rejects_dangling_rubric_and_completion_references():
    brief = _artifact("brief", ProjectArtifactKind.PROJECT_BRIEF)
    with pytest.raises(ValueError, match="Rubrica"):
        _package(
            brief,
            rubrics=(ProjectRubric(artifact_id="missing", raw_content="rubric"),),
        )
    with pytest.raises(ValueError, match="conclusão"):
        _package(
            brief,
            completion_rules=(
                ProjectCompletionRule(source_artifact_id="missing", source_text="rule"),
            ),
        )
