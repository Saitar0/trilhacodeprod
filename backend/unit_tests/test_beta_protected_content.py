import json

import pytest
from pydantic import ValidationError

from curriculum_contract.beta_completion_criteria import (
    CompletionCriteriaContract,
    CompletionRule,
    CriterionKind,
    EvaluationMode,
)
from curriculum_contract.beta_curricular_metadata import (
    CurricularReference,
    CurricularRelation,
    RelationScope,
)
from curriculum_contract.beta_protected_content import (
    DisclosurePolicy,
    ProjectionGrantEvidence,
    ProtectedManualExercise,
    ProtectedQuizQuestion,
    RestrictedExerciseGuidance,
    RestrictedQuizAnswer,
    StudentExercise,
    StudentQuizQuestion,
)


def _question():
    return ProtectedQuizQuestion(
        track_id="synthetic-track",
        unit_id="1.synthetic",
        version="synthetic-v1",
        student=StudentQuizQuestion(
            question_id="q-synthetic",
            order=1,
            prompt="SYNTHETIC TEST PROMPT; not curriculum content",
            options=(
                {"id": "a", "label": "Option A"},
                {"id": "b", "label": "Option B"},
            ),
            schema_version=1,
        ),
        instructor=RestrictedQuizAnswer(
            question_id="q-synthetic",
            correct_option_id="b",
            explanation="SYNTHETIC TEST EXPLANATION",
            disclosure=DisclosurePolicy.PENDING_DECISION,
        ),
    )


def test_student_quiz_projection_omits_answer_and_explanation():
    projected = _question().student_projection()
    encoded = json.dumps(projected)
    assert projected["question_id"] == "q-synthetic"
    assert "correct_option_id" not in encoded
    assert "SYNTHETIC TEST EXPLANATION" not in encoded


def test_restricted_quiz_projection_requires_track_scoped_grant_operation():
    question = _question()
    with pytest.raises(PermissionError):
        question.instructor_projection(ProjectionGrantEvidence(
            subject_id="synthetic-admin",
            grant_id="grant-other-track",
            grant_track_id="other-track",
            operations=("curriculum.read_restricted",),
        ))
    with pytest.raises(PermissionError):
        question.instructor_projection(ProjectionGrantEvidence(
            subject_id="synthetic-admin",
            grant_id="grant-no-operation",
            grant_track_id="synthetic-track",
            operations=("content.write",),
        ))
    restricted = question.instructor_projection(ProjectionGrantEvidence(
        subject_id="synthetic-instructor",
        grant_id="grant-synthetic-read",
        grant_track_id="synthetic-track",
        operations=("curriculum.read_restricted",),
    ))
    assert restricted["correct_option_id"] == "b"
    assert restricted["explanation"] == "SYNTHETIC TEST EXPLANATION"


def test_manual_exercise_separates_student_prompt_from_rubric():
    exercise = ProtectedManualExercise(
        track_id="synthetic-track",
        unit_id="1.synthetic",
        version="synthetic-v1",
        student=StudentExercise(
            exercise_id="exercise-synthetic",
            order=1,
            title="Synthetic exercise",
            prompt="SYNTHETIC TEST PROMPT",
            instructions=("SYNTHETIC INSTRUCTION",),
        ),
        instructor=RestrictedExerciseGuidance(
            exercise_id="exercise-synthetic",
            reference_answer="SYNTHETIC PRIVATE ANSWER",
            rubric=("SYNTHETIC PRIVATE RUBRIC",),
        ),
    )
    student = json.dumps(exercise.student_projection())
    assert "SYNTHETIC TEST PROMPT" in student
    assert "SYNTHETIC PRIVATE ANSWER" not in student
    assert "SYNTHETIC PRIVATE RUBRIC" not in student


def test_completion_keeps_ambiguous_source_text_human_gated():
    rule = CompletionRule(
        criterion_id="criterion-synthetic",
        unit_id="1.synthetic",
        source_text="SYNTHETIC CRITERION TEXT",
        kind=CriterionKind.UNSTRUCTURED,
        evaluation=EvaluationMode.DECISION_REQUIRED,
        requires_human_review=True,
    )
    contract = CompletionCriteriaContract(unit_id="1.synthetic", rules=(rule,))
    assert contract.rules[0].source_text == "SYNTHETIC CRITERION TEXT"
    assert contract.rules[0].automated_threshold is None
    with pytest.raises(ValidationError):
        CompletionRule(
            criterion_id="criterion-bad",
            unit_id="1.synthetic",
            source_text="SYNTHETIC TEXT",
            kind=CriterionKind.UNSTRUCTURED,
            evaluation=EvaluationMode.DECISION_REQUIRED,
            requires_human_review=False,
        )


def test_relations_keep_external_targets_unenforced_and_references_keep_descriptions():
    relation = CurricularRelation(
        relation_id="relation-synthetic",
        source_unit_id="1.synthetic",
        source_kind="Relacionado",
        target_source_path="Fase_2/2.1_external",
        target_unit_id="2.1",
        scope=RelationScope.EXTERNAL_NOT_LOADED,
        enforced=False,
    )
    assert relation.target_unit_id == "2.1"
    assert relation.enforced is False
    with pytest.raises(ValidationError):
        CurricularRelation(
            relation_id="relation-bad",
            source_unit_id="1.synthetic",
            source_kind="Pré-requisito",
            target_source_path="Fase_2/2.1_external",
            target_unit_id="2.1",
            scope=RelationScope.EXTERNAL_NOT_LOADED,
            enforced=True,
        )
    reference = CurricularReference(
        reference_id="reference-synthetic",
        unit_id="1.synthetic",
        order=1,
        title="Synthetic reference",
        description="SYNTHETIC DESCRIPTION",
        url="https://example.invalid/synthetic",
        origin="synthetic-fixture.md",
        provenance_sha256="a" * 64,
    )
    assert reference.description == "SYNTHETIC DESCRIPTION"


def test_unknown_fields_and_private_data_in_public_quiz_are_rejected():
    with pytest.raises(ValidationError):
        StudentQuizQuestion.model_validate({
            "question_id": "q",
            "order": 1,
            "prompt": "SYNTHETIC",
            "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
            "schema_version": 1,
            "correct_option_id": "a",
        })
