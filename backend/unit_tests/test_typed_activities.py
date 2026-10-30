"""Executable contracts for typed activities; no persistence or publication."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from curriculum_contract.bulk_import import CurriculumImportBundle
from curriculum_contract.experimental_quiz_converter import analyze_bundle_quizzes
from curriculum_contract.models import AnswerKeyBlock, SourceProvenance
from curriculum_contract.quiz_structure_audit import (
    audit_quiz_items,
    previous_statuses_from_csv,
)
from curriculum_contract.typed_activities import (
    ActivityIntegrity,
    ActivityItem,
    ActivityKind,
    ActivityOption,
    ActivityReference,
    EvaluationPolicy,
    EvaluatorCompatibility,
    ObjectiveQuizPolicy,
    PrivateActivity,
    PrivateAnswerMaterial,
    PrivateDiscursiveData,
    PrivateMatchingData,
    PrivateMatchPair,
    PrivateMultipleChoiceData,
    PrivateOrderingData,
    PrivateShortAnswerData,
    PublicActivity,
    PublicationState,
    PublicDiscursiveActivity,
    PublicMatchingActivity,
    PublicMultipleChoiceActivity,
    PublicOrderingActivity,
    PublicReviewActivity,
    PublicShortAnswerActivity,
    TypedActivityOutcome,
    TypedActivityRecord,
    UndecidedPolicy,
    UnscoredPolicy,
    ValidationState,
    canonical_activity_json,
    convert_bundle_activities,
    typed_activity_csv,
    validate_activity_records,
)
from services.quizzes import grade_quiz_questions

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "docs/courses/trilhacode/trilha-code-bulk-import.json"
BASELINE_14C = REPO_ROOT / "docs/migracao/COBERTURA_CONVERSAO_QUIZZES_14C.csv"
CLASSIFICATION_14D = REPO_ROOT / "docs/migracao/CLASSIFICACAO_QUIZZES_14D.csv"
EXPECTED_BUNDLE_SHA256 = "43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2"
EXPECTED_14C_SHA256 = "bd8487357aab3e6aa6b4831362ee52b88fa230d1f78c1bc136ae95be60fab89b"
EXPECTED_14D_SHA256 = "ed6e48e675965bb6936a4451372641da212e2589f9696d1bba26acbe18cc10b2"
SOURCE_SHA = "a" * 64
KEY_SHA = "b" * 64
PRIVATE_SENTINEL = "PRIVATE_TYPED_ANSWER_SENTINEL"


def _provenance(source_id: str, role: str = "quiz") -> SourceProvenance:
    return SourceProvenance(
        source_file=f"docs/fixtures/{source_id}.md",
        source_sha256=SOURCE_SHA if role == "quiz" else KEY_SHA,
        manifest_ref="1.2",
        source_role=role,
        source_id=source_id,
    )


def _material(
    activity_ref: str, *, expected: str | None = PRIVATE_SENTINEL
) -> PrivateAnswerMaterial:
    return PrivateAnswerMaterial(
        answer_key_ref=f"{activity_ref}-key",
        question_ref=activity_ref,
        correct_option_ref=None,
        expected_answer=expected,
        accepted_answers=[],
        explanation="PRIVATE_TYPED_EXPLANATION_SENTINEL",
        source_markdown="**Resposta privada**",
        provenance=_provenance("Q1-key", "quiz-answer-key"),
    )


def _record(
    public: PublicActivity,
    private: PrivateActivity | None,
    *,
    activity_type: ActivityKind,
    validation_state: ValidationState,
    publication_state: PublicationState,
    evaluator_compatibility: EvaluatorCompatibility,
    policy: EvaluationPolicy,
    source_markdown: str = "Original source question",
) -> TypedActivityRecord:
    public_dump = public.model_dump(mode="json")
    private_dump = private.model_dump(mode="json") if private is not None else None
    private_sha = (
        hashlib.sha256(
            json.dumps(
                private_dump, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ).hexdigest()
        if private_dump is not None
        else None
    )
    public_sha = hashlib.sha256(
        json.dumps(public_dump, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    ref = public.activity_ref
    version = public.version_ref
    return TypedActivityRecord(
        activity_ref=ref,
        activity_type=activity_type,
        phase=1,
        source_id="Q1",
        source_markdown=source_markdown,
        public=public,
        private=private,
        version_ref=version,
        validation_state=validation_state,
        publication_state=publication_state,
        evaluator_compatibility=evaluator_compatibility,
        evaluation_policy=policy,
        provenance=_provenance("Q1"),
        integrity=ActivityIntegrity(
            question_source_sha256=SOURCE_SHA,
            answer_source_sha256=KEY_SHA if private is not None else None,
            public_payload_sha256=public_sha,
            private_payload_sha256=private_sha,
        ),
    )


def _multiple_choice_record(
    *,
    activity_ref: str = "f1-test-topic-q01",
    expected: str | None = PRIVATE_SENTINEL,
    version_ref: str = f"question-source-sha256:{SOURCE_SHA}",
) -> TypedActivityRecord:
    public = PublicMultipleChoiceActivity(
        activity_ref=activity_ref,
        version_ref=version_ref,
        title="Question 1",
        order=1,
        prompt="Choose one option.",
        type="multiple_choice",
        options=[
            ActivityOption(option_id="a", text="First", source_label="A"),
            ActivityOption(option_id="b", text="Second", source_label="B"),
        ],
    )
    private = PrivateMultipleChoiceData(
        type="multiple_choice",
        answer_material=_material(activity_ref, expected=expected),
        resolved_correct_option_id="b",
    )
    return _record(
        public,
        private,
        activity_type="multiple_choice",
        validation_state="valid",
        publication_state="structurally_validated",
        evaluator_compatibility="compatible",
        policy=ObjectiveQuizPolicy(type="objective_server_policy"),
    )


def _real_inventory() -> tuple[CurriculumImportBundle, list[TypedActivityOutcome]]:
    bundle_bytes = BUNDLE_PATH.read_bytes()
    assert hashlib.sha256(bundle_bytes).hexdigest() == EXPECTED_BUNDLE_SHA256
    assert hashlib.sha256(BASELINE_14C.read_bytes()).hexdigest() == EXPECTED_14C_SHA256
    assert hashlib.sha256(CLASSIFICATION_14D.read_bytes()).hexdigest() == EXPECTED_14D_SHA256
    bundle = CurriculumImportBundle.model_validate_json(bundle_bytes)
    conversion_outcomes = analyze_bundle_quizzes(bundle)
    previous = previous_statuses_from_csv(BASELINE_14C.read_text(encoding="utf-8"))
    audit_records = audit_quiz_items(bundle, conversion_outcomes, previous, REPO_ROOT)
    return bundle, convert_bundle_activities(bundle, audit_records)


def test_contracts_distinguish_all_six_activity_kinds():
    version = f"question-source-sha256:{SOURCE_SHA}"
    common = {
        "activity_ref": "f1-test-topic-q01",
        "version_ref": version,
        "title": "A prompt",
        "order": 1,
        "prompt": "Original prompt",
    }
    public = [
        PublicMultipleChoiceActivity(**common, type="multiple_choice"),
        PublicShortAnswerActivity(**common, type="short_answer"),
        PublicDiscursiveActivity(**common, type="discursive"),
        PublicMatchingActivity(**common, type="matching"),
        PublicOrderingActivity(**common, type="ordering"),
        PublicReviewActivity(**common, type="review"),
    ]
    assert [item.type for item in public] == [
        "multiple_choice",
        "short_answer",
        "discursive",
        "matching",
        "ordering",
        "review",
    ]


def test_public_and_private_serializers_are_separate_and_gabarito_does_not_leak():
    record = _multiple_choice_record()
    public_text = json.dumps(record.public_payload(), ensure_ascii=False)
    private_text = json.dumps(record.private_payload(), ensure_ascii=False)

    assert record.contract_version == "trilhacode.typed_activities/1.0"
    assert record.model_dump(mode="json")["contract_version"] == record.contract_version
    assert PRIVATE_SENTINEL not in public_text
    assert "PRIVATE_TYPED_EXPLANATION_SENTINEL" not in public_text
    assert "correct_option_ref" not in public_text
    assert "resolved_correct_option_id" not in public_text
    assert PRIVATE_SENTINEL in private_text
    assert "PRIVATE_TYPED_EXPLANATION_SENTINEL" in private_text


def test_objective_contract_matches_current_backend_and_approved_policy():
    record = _multiple_choice_record(expected="B.")
    question = record.backend_question()
    graded = grade_quiz_questions(
        [record.backend_grader_record()],
        [{"question_id": record.activity_ref, "option_id": "b"}],
    )
    assert question.question_id == record.activity_ref
    assert record.evaluation_policy == ObjectiveQuizPolicy(type="objective_server_policy")
    assert graded["passed"] is True
    assert graded["score_percent"] == 100


def test_short_answer_and_discursive_contracts_are_not_auto_graded():
    version = f"question-source-sha256:{SOURCE_SHA}"
    common = {
        "activity_ref": "f1-test-topic-q01",
        "version_ref": version,
        "title": "Open prompt",
        "order": 1,
        "prompt": "Explain the difference.",
    }
    short = _record(
        PublicShortAnswerActivity(**common, type="short_answer"),
        PrivateShortAnswerData(
            type="short_answer", answer_material=_material(common["activity_ref"])
        ),
        activity_type="short_answer",
        validation_state="pending_review",
        publication_state="pending_review",
        evaluator_compatibility="unsupported",
        policy=UndecidedPolicy(type="undecided"),
    )
    discursive = _record(
        PublicDiscursiveActivity(**common, type="discursive"),
        PrivateDiscursiveData(type="discursive", answer_material=_material(common["activity_ref"])),
        activity_type="discursive",
        validation_state="pending_review",
        publication_state="pending_review",
        evaluator_compatibility="unsupported",
        policy=UndecidedPolicy(type="undecided"),
    )
    for record in (short, discursive):
        assert isinstance(record.evaluation_policy, UndecidedPolicy)
        with pytest.raises(ValueError, match="not compatible"):
            record.backend_question()


def test_matching_and_ordering_can_represent_keys_without_activating_evaluation():
    version = f"question-source-sha256:{SOURCE_SHA}"
    common = {
        "activity_ref": "f1-test-topic-q01",
        "version_ref": version,
        "title": "Arrange these items",
        "order": 1,
        "prompt": "Use the supplied instructions.",
    }
    matching_public = PublicMatchingActivity(
        **common,
        type="matching",
        left_items=[ActivityItem(ref="left-a", text="Left A")],
        right_items=[ActivityItem(ref="right-a", text="Right A")],
    )
    matching_private = PrivateMatchingData(
        type="matching",
        answer_material=_material(common["activity_ref"]),
        correct_pairs=[PrivateMatchPair(left_ref="left-a", right_ref="right-a")],
    )
    matching = _record(
        matching_public,
        matching_private,
        activity_type="matching",
        validation_state="valid",
        publication_state="structurally_validated",
        evaluator_compatibility="unsupported",
        policy=UndecidedPolicy(type="undecided"),
    )
    ordering_public = PublicOrderingActivity(
        **common,
        type="ordering",
        items=[
            ActivityItem(ref="step-1", text="First step"),
            ActivityItem(ref="step-2", text="Second step"),
        ],
    )
    ordering_private = PrivateOrderingData(
        type="ordering",
        answer_material=_material(common["activity_ref"]),
        correct_order_refs=["step-1", "step-2"],
    )
    ordering = _record(
        ordering_public,
        ordering_private,
        activity_type="ordering",
        validation_state="valid",
        publication_state="structurally_validated",
        evaluator_compatibility="unsupported",
        policy=UndecidedPolicy(type="undecided"),
    )
    assert matching.activity_type == "matching"
    assert ordering.activity_type == "ordering"
    with pytest.raises(ValueError, match="not compatible"):
        matching.backend_question()
    with pytest.raises(ValueError, match="not compatible"):
        ordering.backend_question()


def test_review_contract_is_explicitly_unscored_with_or_without_private_key():
    common = {
        "activity_ref": "f1-test-topic-r01",
        "version_ref": f"question-source-sha256:{SOURCE_SHA}",
        "title": "Review question",
        "order": 1,
        "prompt": "Discuss this topic.",
    }
    public = PublicReviewActivity(**common, type="review")
    private = None
    record = _record(
        public,
        private,
        activity_type="review",
        validation_state="valid",
        publication_state="pending_review",
        evaluator_compatibility="not_applicable",
        policy=UnscoredPolicy(type="unscored"),
    )
    assert isinstance(record.evaluation_policy, UnscoredPolicy)
    with pytest.raises(ValidationError):
        _record(
            public,
            private,
            activity_type="review",
            validation_state="valid",
            publication_state="pending_review",
            evaluator_compatibility="not_applicable",
            policy=UndecidedPolicy(type="undecided"),
        )


def test_incomplete_multiple_choice_is_representable_but_not_evaluable():
    public = PublicMultipleChoiceActivity(
        activity_ref="f1-test-topic-q01",
        version_ref=f"question-source-sha256:{SOURCE_SHA}",
        title="Incomplete MC",
        order=1,
        prompt="Choose an answer.",
        type="multiple_choice",
        options=[],
    )
    private = PrivateMultipleChoiceData(
        type="multiple_choice", answer_material=_material(public.activity_ref)
    )
    record = _record(
        public,
        private,
        activity_type="multiple_choice",
        validation_state="incomplete",
        publication_state="draft",
        evaluator_compatibility="unsupported",
        policy=UndecidedPolicy(type="undecided"),
    )
    assert record.public.options == []
    with pytest.raises(ValueError, match="not compatible"):
        record.backend_question()


def test_ambiguous_answer_key_cannot_be_marked_valid_or_objective():
    public = PublicMultipleChoiceActivity(
        activity_ref="f1-test-topic-q01",
        version_ref=f"question-source-sha256:{SOURCE_SHA}",
        title="Ambiguous key",
        order=1,
        prompt="Choose one.",
        type="multiple_choice",
        options=[ActivityOption(option_id="a", text="A"), ActivityOption(option_id="b", text="B")],
    )
    private = PrivateMultipleChoiceData(
        type="multiple_choice",
        answer_material=_material(public.activity_ref),
        resolved_correct_option_id=None,
    )
    with pytest.raises(ValidationError):
        _record(
            public,
            private,
            activity_type="multiple_choice",
            validation_state="valid",
            publication_state="structurally_validated",
            evaluator_compatibility="blocked",
            policy=UndecidedPolicy(type="undecided"),
        )


def test_unknown_activity_type_is_rejected_instead_of_falling_back_to_theory():
    raw = {
        "type": "unrecognized_activity",
        "activity_ref": "f1-test-topic-q01",
        "version_ref": f"question-source-sha256:{SOURCE_SHA}",
        "title": "Unsupported",
        "order": 1,
        "prompt": "Do not coerce me.",
    }
    with pytest.raises(ValidationError):
        TypeAdapter(
            PublicMultipleChoiceActivity
            | PublicShortAnswerActivity
            | PublicDiscursiveActivity
            | PublicMatchingActivity
            | PublicOrderingActivity
            | PublicReviewActivity
        ).validate_python(raw)


def test_invalid_version_id_option_ids_and_references_are_rejected():
    with pytest.raises(ValidationError):
        PublicReviewActivity(
            activity_ref="f1-test-topic-r01",
            version_ref="latest",
            title="Review",
            order=0,
            prompt="Review this.",
            type="review",
        )
    with pytest.raises(ValidationError, match="unique"):
        PublicMultipleChoiceActivity(
            activity_ref="f1-test-topic-q01",
            version_ref=f"question-source-sha256:{SOURCE_SHA}",
            title="Duplicate choices",
            order=0,
            prompt="Choose.",
            type="multiple_choice",
            options=[
                ActivityOption(option_id="a", text="One"),
                ActivityOption(option_id="a", text="Two"),
            ],
        )
    with pytest.raises(ValidationError, match="target_ref"):
        ActivityReference(kind="internal", label="Missing target")
    with pytest.raises(ValidationError, match="absolute HTTP"):
        ActivityReference(kind="external", label="Bad URL", url="not-a-url")


def test_activity_collection_validator_reports_duplicate_ids_and_broken_references():
    record = _multiple_choice_record(expected="B.")
    outcome = TypedActivityOutcome(
        phase=1,
        activity_ref=record.activity_ref,
        source_id="Q1",
        source_file="docs/fixtures/Q1.md",
        source_sha256=SOURCE_SHA,
        activity_type="multiple_choice",
        classification="multiple_choice_recoverable",
        conversion_status="converted_candidate",
        validation_state="valid",
        publication_state="structurally_validated",
        evaluator_compatibility="compatible",
        diagnostic_code="OK",
        activity=record,
    )
    duplicate = validate_activity_records([outcome, outcome])
    assert [item.code for item in duplicate] == ["ACTIVITY_ID_DUPLICATED"]

    broken_ref = ActivityReference(
        kind="internal", label="missing", target_ref="f1-not-in-inventory"
    )
    changed_public = record.public.model_copy(update={"references": [broken_ref]})
    changed_public_hash = hashlib.sha256(
        json.dumps(
            changed_public.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()
    changed_record = record.model_copy(
        update={
            "public": changed_public,
            "integrity": record.integrity.model_copy(
                update={"public_payload_sha256": changed_public_hash}
            ),
        }
    )
    changed_outcome = replace(outcome, activity=changed_record)
    diagnostics = validate_activity_records([changed_outcome])
    assert any(item.code == "ACTIVITY_REFERENCE_UNRESOLVED" for item in diagnostics)


def test_collection_rejects_publishable_state_for_incomplete_content():
    public = PublicMultipleChoiceActivity(
        activity_ref="f1-test-topic-q01",
        version_ref=f"question-source-sha256:{SOURCE_SHA}",
        title="Incomplete",
        order=0,
        prompt="Choose.",
        type="multiple_choice",
        options=[],
    )
    private = PrivateMultipleChoiceData(type="multiple_choice")
    with pytest.raises(ValidationError, match="publishing requires valid structure"):
        _record(
            public,
            private,
            activity_type="multiple_choice",
            validation_state="incomplete",
            publication_state="publishable",
            evaluator_compatibility="unsupported",
            policy=UndecidedPolicy(type="undecided"),
        )


def test_integrity_hash_and_required_provenance_are_enforced():
    record = _multiple_choice_record(expected="B.")
    altered = record.model_dump(mode="python")
    altered["integrity"]["public_payload_sha256"] = "0" * 64
    with pytest.raises(ValidationError, match="public payload hash does not match"):
        TypedActivityRecord.model_validate(altered)

    without_provenance = record.model_dump(mode="python")
    without_provenance.pop("provenance")
    with pytest.raises(ValidationError):
        TypedActivityRecord.model_validate(without_provenance)


def test_real_14d_inventory_preserves_143_candidates_358_blockers_and_five_reviews():
    _, outcomes = _real_inventory()
    counts = Counter(item.conversion_status for item in outcomes)
    types = Counter(item.activity_type for item in outcomes)

    assert len(outcomes) == 506
    assert counts == {
        "converted_candidate": 143,
        "blocked_alternatives": 347,
        "blocked_gabarito": 11,
        "unscored_review_pending": 5,
    }
    assert sum(counts[item] for item in ("blocked_alternatives", "blocked_gabarito")) == 358
    assert types == {
        "multiple_choice": 155,
        "short_answer": 314,
        "discursive": 23,
        "matching": 4,
        "ordering": 4,
        "review": 6,
    }
    assert sum(item.publication_state in {"publishable", "published"} for item in outcomes) == 0
    assert all(item.publishable == "no" for item in outcomes)


def test_all_143_previous_candidates_remain_backend_compatible_and_separate_from_public_keys():
    _, outcomes = _real_inventory()
    previous = list(csv.DictReader(BASELINE_14C.read_text(encoding="utf-8").splitlines()))
    previous_candidate_ids = {
        (int(row["phase"]), row["quiz_ref"])
        for row in previous
        if row["conversion_status"] == "converted_candidate"
    }
    current_candidate_ids = {
        (item.phase, item.activity_ref)
        for item in outcomes
        if item.conversion_status == "converted_candidate"
    }
    assert len(previous_candidate_ids) == 142
    assert previous_candidate_ids <= current_candidate_ids
    assert len(current_candidate_ids) == 143

    for item in outcomes:
        if item.conversion_status != "converted_candidate":
            continue
        assert item.validation_state == "valid"
        assert item.publication_state == "structurally_validated"
        assert item.evaluator_compatibility == "compatible"
        assert isinstance(item.activity.evaluation_policy, ObjectiveQuizPolicy)
        public = json.dumps(item.activity.public_payload(), ensure_ascii=False)
        assert "correct_option_id" not in public
        assert "answer_key_ref" not in public
        grade_quiz_questions([item.activity.backend_grader_record()], [])


def test_all_source_prompts_and_501_answer_material_records_are_preserved_exactly():
    bundle, outcomes = _real_inventory()
    quizzes = {
        block.ref: block
        for phase in bundle.phases
        for block in phase.contract.blocks
        if getattr(block, "type", None) == "quiz"
    }
    keys = {
        block.ref: block
        for phase in bundle.phases
        for block in phase.contract.blocks
        if isinstance(block, AnswerKeyBlock)
    }
    assert len(quizzes) == 506
    assert len(keys) == 501
    for outcome in outcomes:
        quiz = quizzes[outcome.activity_ref]
        assert outcome.activity.source_markdown == quiz.prompt
        assert outcome.activity.provenance == quiz.provenance
        material = getattr(outcome.activity.private, "answer_material", None)
        if quiz.answer_key_required:
            source_key = keys[quiz.answer_key_ref]
            assert material is not None
            assert material.answer_key_ref == source_key.ref
            assert material.question_ref == source_key.question_ref
            assert material.correct_option_ref == source_key.correct_option_ref
            assert material.expected_answer == source_key.expected_answer
            assert material.accepted_answers == source_key.accepted_answers
            assert material.explanation == source_key.explanation
            assert material.source_markdown == source_key.source_markdown
            public = json.dumps(outcome.activity.public_payload(), ensure_ascii=False)
            if source_key.expected_answer:
                assert source_key.expected_answer not in public
            if source_key.explanation:
                assert source_key.explanation not in public
        else:
            assert outcome.source_id in {"R1", "R2", "R3", "R4", "R5"}
            assert outcome.activity.private is None


def test_358_blocked_items_keep_individual_ids_diagnostics_and_no_objective_policy():
    _, outcomes = _real_inventory()
    blocked = [
        item
        for item in outcomes
        if item.conversion_status in {"blocked_alternatives", "blocked_gabarito"}
    ]
    assert len(blocked) == 358
    assert len({item.activity_ref for item in blocked}) == 358
    assert all(item.activity.diagnostics and item.diagnostic_code for item in blocked)
    assert all(
        not isinstance(item.activity.evaluation_policy, ObjectiveQuizPolicy) for item in blocked
    )


def test_real_r1_to_r5_remain_unscored_reviews_without_private_keys():
    _, outcomes = _real_inventory()
    reviews = [item for item in outcomes if item.conversion_status == "unscored_review_pending"]
    assert len(reviews) == 5
    assert {item.source_id for item in reviews} == {"R1", "R2", "R3", "R4", "R5"}
    assert all(item.activity_type == "review" for item in reviews)
    assert all(item.activity.private is None for item in reviews)
    assert all(isinstance(item.activity.evaluation_policy, UnscoredPolicy) for item in reviews)


def test_deterministic_conversion_and_csv_are_independent_of_input_order():
    bundle, forward = _real_inventory()
    previous = previous_statuses_from_csv(BASELINE_14C.read_text(encoding="utf-8"))
    reversed_bundle = bundle.model_copy(update={"phases": list(reversed(bundle.phases))})
    reverse_outcomes = analyze_bundle_quizzes(reversed_bundle)
    reverse_audit = audit_quiz_items(reversed_bundle, reverse_outcomes, previous, REPO_ROOT)
    backward = convert_bundle_activities(reversed_bundle, reverse_audit)

    assert typed_activity_csv(forward) == typed_activity_csv(backward)
    assert [canonical_activity_json(item) for item in forward] == [
        canonical_activity_json(item) for item in backward
    ]


def test_typed_inventory_csv_has_no_prompts_answers_or_private_explanations():
    _, outcomes = _real_inventory()
    text = typed_activity_csv(outcomes)
    assert len(list(csv.DictReader(io.StringIO(text)))) == 506
    assert PRIVATE_SENTINEL not in text
    assert "PRIVATE_TYPED_EXPLANATION_SENTINEL" not in text
    assert "expected_answer" not in text
    assert "explanation" not in text
    assert "correct_option_id" not in text
    assert "Múltipla escolha" not in text
    assert all(row["publishable"] == "no" for row in csv.DictReader(io.StringIO(text)))


def test_all_original_hashes_are_unchanged_and_not_written_by_conversion():
    _, outcomes = _real_inventory()
    assert len(outcomes) == 506
    assert hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest() == EXPECTED_BUNDLE_SHA256
    assert hashlib.sha256(BASELINE_14C.read_bytes()).hexdigest() == EXPECTED_14C_SHA256
    assert hashlib.sha256(CLASSIFICATION_14D.read_bytes()).hexdigest() == EXPECTED_14D_SHA256
