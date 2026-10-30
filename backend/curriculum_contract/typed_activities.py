"""Isolated, offline contracts for typed quiz and review activities.

This module does not persist, publish, or import activities. Public payloads
are explicitly allow-listed; private correction material is kept in separate
models and is emitted only through an explicitly private serializer.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass, field
from typing import Annotated, Literal, Union
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, model_validator

from schemas.quizzes import QuizOptionOut, QuizQuestionOut

from .bulk_import import CurriculumImportBundle
from .experimental_quiz_converter import (
    ExperimentalQuizCandidate,
    QuizConversionOutcome,
    _split_options,
    analyze_bundle_quizzes,
)
from .models import (
    AnswerKeyBlock,
    ContractModel,
    NonEmptyText,
    QuizBlock,
    SourceProvenance,
    StableId,
)
from .quiz_structure_audit import QuizStructureAudit

Sha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
TYPED_ACTIVITY_CONTRACT_VERSION: Literal["trilhacode.typed_activities/1.0"] = (
    "trilhacode.typed_activities/1.0"
)
TypedActivityContractVersion = Literal["trilhacode.typed_activities/1.0"]
ActivityVersionRef = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^question-source-sha256:[0-9a-f]{64}$"),
]

ActivityKind = Literal[
    "multiple_choice",
    "short_answer",
    "discursive",
    "matching",
    "ordering",
    "review",
]
ValidationState = Literal["valid", "incomplete", "ambiguous", "pending_review"]
PublicationState = Literal[
    "draft", "pending_review", "structurally_validated", "publishable", "published"
]
EvaluatorCompatibility = Literal["compatible", "unsupported", "blocked", "not_applicable"]


class ActivityReference(ContractModel):
    """A reference attached to an activity without resolving unknown targets."""

    kind: Literal["internal", "external", "obsidian", "editorial"]
    label: str
    target_ref: StableId | None = None
    url: str | None = None
    raw_text: str | None = None

    @model_validator(mode="after")
    def validate_reference_shape(self) -> ActivityReference:
        if self.kind == "internal" and self.target_ref is None:
            raise ValueError("internal references require target_ref")
        if self.kind == "external":
            if self.url is None:
                raise ValueError("external references require url")
            parts = urlsplit(self.url)
            if parts.scheme not in {"http", "https"} or not parts.netloc:
                raise ValueError("external reference URL must be an absolute HTTP(S) URL")
        if self.kind in {"obsidian", "editorial"} and not self.raw_text:
            raise ValueError(f"{self.kind} references require raw_text")
        if self.kind != "internal" and self.target_ref is not None:
            raise ValueError("only internal references may use target_ref")
        if self.kind != "external" and self.url is not None:
            raise ValueError("only external references may use url")
        return self


class ActivityOption(ContractModel):
    option_id: NonEmptyText
    text: NonEmptyText
    source_label: str | None = None


class ActivityItem(ContractModel):
    ref: NonEmptyText
    text: NonEmptyText


class PublicActivityBase(ContractModel):
    activity_ref: StableId
    version_ref: ActivityVersionRef
    title: NonEmptyText
    order: int = Field(strict=True, ge=0)
    prompt: NonEmptyText
    instructions: str | None = None
    references: list[ActivityReference] = Field(default_factory=list)


class PublicMultipleChoiceActivity(PublicActivityBase):
    type: Literal["multiple_choice"]
    options: list[ActivityOption] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_option_identities(self) -> PublicMultipleChoiceActivity:
        ids = [option.option_id for option in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("multiple-choice option IDs must be unique")
        return self


class PublicShortAnswerActivity(PublicActivityBase):
    type: Literal["short_answer"]


class PublicDiscursiveActivity(PublicActivityBase):
    type: Literal["discursive"]


class PublicMatchingActivity(PublicActivityBase):
    type: Literal["matching"]
    left_items: list[ActivityItem] = Field(default_factory=list)
    right_items: list[ActivityItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_item_identities(self) -> PublicMatchingActivity:
        left_refs = [item.ref for item in self.left_items]
        right_refs = [item.ref for item in self.right_items]
        if len(left_refs) != len(set(left_refs)) or len(right_refs) != len(set(right_refs)):
            raise ValueError("matching item IDs must be unique on each side")
        return self


class PublicOrderingActivity(PublicActivityBase):
    type: Literal["ordering"]
    items: list[ActivityItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_item_identities(self) -> PublicOrderingActivity:
        refs = [item.ref for item in self.items]
        if len(refs) != len(set(refs)):
            raise ValueError("ordering item IDs must be unique")
        return self


class PublicReviewActivity(PublicActivityBase):
    type: Literal["review"]


PublicActivity = Annotated[
    Union[
        PublicMultipleChoiceActivity,
        PublicShortAnswerActivity,
        PublicDiscursiveActivity,
        PublicMatchingActivity,
        PublicOrderingActivity,
        PublicReviewActivity,
    ],
    Field(discriminator="type"),
]


class PrivateAnswerMaterial(ContractModel):
    """Exact source answer material; never included in public projections."""

    answer_key_ref: StableId
    question_ref: StableId
    correct_option_ref: str | None = Field(default=None, repr=False)
    expected_answer: str | None = Field(default=None, repr=False)
    accepted_answers: list[str] = Field(default_factory=list, repr=False)
    explanation: str | None = Field(default=None, repr=False)
    source_markdown: str | None = Field(default=None, repr=False)
    provenance: SourceProvenance


class PrivateCorrectionCriterion(ContractModel):
    ref: NonEmptyText
    text: NonEmptyText = Field(repr=False)
    order: int = Field(strict=True, ge=0)


class PrivateMultipleChoiceData(ContractModel):
    type: Literal["multiple_choice"]
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)
    resolved_correct_option_id: str | None = Field(default=None, repr=False)


class PrivateShortAnswerData(ContractModel):
    type: Literal["short_answer"]
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)
    criteria: list[PrivateCorrectionCriterion] = Field(default_factory=list, repr=False)


class PrivateDiscursiveData(ContractModel):
    type: Literal["discursive"]
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)
    rubric_refs: list[StableId] = Field(default_factory=list, repr=False)
    criteria: list[PrivateCorrectionCriterion] = Field(default_factory=list, repr=False)


class PrivateMatchPair(ContractModel):
    left_ref: NonEmptyText
    right_ref: NonEmptyText


class PrivateMatchingData(ContractModel):
    type: Literal["matching"]
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)
    correct_pairs: list[PrivateMatchPair] = Field(default_factory=list, repr=False)


class PrivateOrderingData(ContractModel):
    type: Literal["ordering"]
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)
    correct_order_refs: list[NonEmptyText] = Field(default_factory=list, repr=False)


class PrivateReviewData(ContractModel):
    type: Literal["review"]
    # A source key may be retained privately for provenance, but review items
    # are never routed through the objective grader by this contract.
    answer_material: PrivateAnswerMaterial | None = Field(default=None, repr=False)


PrivateActivity = Annotated[
    Union[
        PrivateMultipleChoiceData,
        PrivateShortAnswerData,
        PrivateDiscursiveData,
        PrivateMatchingData,
        PrivateOrderingData,
        PrivateReviewData,
    ],
    Field(discriminator="type"),
]


class ObjectiveQuizPolicy(ContractModel):
    type: Literal["objective_server_policy"]
    maximum_attempts: Literal[3] = 3
    passing_percent: Literal[70] = 70
    score_basis: Literal["best_valid_attempt"] = "best_valid_attempt"
    reveal_after_attempts: Literal[3] = 3


class UnscoredPolicy(ContractModel):
    type: Literal["unscored"]


class UndecidedPolicy(ContractModel):
    type: Literal["undecided"]


EvaluationPolicy = Annotated[
    Union[ObjectiveQuizPolicy, UnscoredPolicy, UndecidedPolicy],
    Field(discriminator="type"),
]


class ActivityDiagnostic(ContractModel):
    code: NonEmptyText
    severity: Literal["info", "warning", "error"]
    field: NonEmptyText
    message: NonEmptyText


class ActivityIntegrity(ContractModel):
    question_source_sha256: Sha256
    answer_source_sha256: Sha256 | None = Field(default=None, repr=False)
    public_payload_sha256: Sha256
    private_payload_sha256: Sha256 | None = Field(default=None, repr=False)


class TypedActivityRecord(ContractModel):
    """Private in-memory record with explicit, safe public/private projections."""

    contract_version: TypedActivityContractVersion = TYPED_ACTIVITY_CONTRACT_VERSION
    activity_ref: StableId
    activity_type: ActivityKind
    phase: int = Field(strict=True, ge=1, le=10)
    source_id: NonEmptyText
    source_markdown: NonEmptyText = Field(repr=False)
    public: PublicActivity
    private: PrivateActivity | None = Field(default=None, repr=False)
    version_ref: ActivityVersionRef
    validation_state: ValidationState
    publication_state: PublicationState
    evaluator_compatibility: EvaluatorCompatibility
    evaluation_policy: EvaluationPolicy
    provenance: SourceProvenance
    integrity: ActivityIntegrity
    diagnostics: list[ActivityDiagnostic] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_record_consistency(self) -> TypedActivityRecord:
        if self.public.activity_ref != self.activity_ref:
            raise ValueError("public activity identity does not match record identity")
        if self.public.version_ref != self.version_ref:
            raise ValueError("public activity version does not match record version")
        if self.public.type != self.activity_type:
            raise ValueError("public activity type does not match record type")
        if self.private is not None:
            if self.private.type != self.activity_type:
                raise ValueError("private activity type does not match public activity type")
            material = getattr(self.private, "answer_material", None)
            if material is not None and material.question_ref != self.activity_ref:
                raise ValueError("private answer key points to a different activity")
            if material is not None and material.provenance.source_sha256 != (
                self.integrity.answer_source_sha256
            ):
                raise ValueError("answer-key provenance hash does not match integrity metadata")
        elif self.integrity.answer_source_sha256 is not None:
            raise ValueError("answer-key source hash exists without private content")
        if isinstance(self.public, PublicMultipleChoiceActivity) and isinstance(
            self.private, PrivateMultipleChoiceData
        ):
            correct = self.private.resolved_correct_option_id
            if correct is not None and correct not in {
                option.option_id for option in self.public.options
            }:
                raise ValueError("resolved correct option does not exist in public options")
        if isinstance(self.public, PublicMatchingActivity) and isinstance(
            self.private, PrivateMatchingData
        ):
            left_refs = {item.ref for item in self.public.left_items}
            right_refs = {item.ref for item in self.public.right_items}
            pairs = self.private.correct_pairs
            if any(
                pair.left_ref not in left_refs or pair.right_ref not in right_refs for pair in pairs
            ):
                raise ValueError("matching key references an item that does not exist")
            if len({pair.left_ref for pair in pairs}) != len(pairs):
                raise ValueError("matching key repeats a left item")
        if isinstance(self.public, PublicOrderingActivity) and isinstance(
            self.private, PrivateOrderingData
        ):
            public_refs = {item.ref for item in self.public.items}
            answer_refs = self.private.correct_order_refs
            if len(answer_refs) != len(set(answer_refs)) or not set(answer_refs) <= public_refs:
                raise ValueError("private order contains duplicate or unknown items")

        public_hash = _sha256(_canonical_bytes(self.public.model_dump(mode="json")))
        if public_hash != self.integrity.public_payload_sha256:
            raise ValueError("public payload hash does not match")
        private_hash = (
            _sha256(_canonical_bytes(self.private.model_dump(mode="json")))
            if self.private is not None
            else None
        )
        if private_hash != self.integrity.private_payload_sha256:
            raise ValueError("private payload hash does not match")
        if self.provenance.source_sha256 != self.integrity.question_source_sha256:
            raise ValueError("question provenance hash does not match integrity metadata")

        if self.validation_state == "valid":
            self._validate_complete_structure()
        if self.publication_state == "structurally_validated" and self.validation_state != "valid":
            raise ValueError("structurally_validated publication state requires valid structure")
        if (
            self.publication_state in {"publishable", "published"}
            and self.validation_state != "valid"
        ):
            raise ValueError("publishing requires valid structure")

        if isinstance(self.evaluation_policy, ObjectiveQuizPolicy):
            if self.activity_type != "multiple_choice":
                raise ValueError("objective quiz policy is only valid for multiple choice")
            if self.validation_state != "valid" or self.evaluator_compatibility != "compatible":
                raise ValueError("objective policy requires a validated evaluator-compatible item")
            if not isinstance(self.private, PrivateMultipleChoiceData):
                raise ValueError("objective policy requires private multiple-choice data")
            if self.private.resolved_correct_option_id is None:
                raise ValueError("objective policy requires a uniquely resolved answer key")
        if isinstance(self.evaluation_policy, UnscoredPolicy) and self.activity_type != "review":
            raise ValueError("unscored policy is reserved for review activities")
        if self.activity_type == "review" and not isinstance(
            self.evaluation_policy, UnscoredPolicy
        ):
            raise ValueError("review activities must remain unscored")
        return self

    def _validate_complete_structure(self) -> None:
        if self.activity_type == "multiple_choice":
            if not isinstance(self.public, PublicMultipleChoiceActivity):
                raise ValueError("multiple-choice activity has an incompatible public model")
            if len(self.public.options) < 2:
                raise ValueError("validated multiple choice requires at least two options")
            if not isinstance(self.private, PrivateMultipleChoiceData):
                raise ValueError("validated multiple choice requires its private key model")
            correct = self.private.resolved_correct_option_id
            if correct is None or correct not in {item.option_id for item in self.public.options}:
                raise ValueError("validated multiple choice requires one existing correct option")
        elif self.activity_type == "matching":
            if not isinstance(self.public, PublicMatchingActivity):
                raise ValueError("matching activity has an incompatible public model")
            if not self.public.left_items or not self.public.right_items:
                raise ValueError("validated matching requires both public item lists")
            if not isinstance(self.private, PrivateMatchingData) or not self.private.correct_pairs:
                raise ValueError("validated matching requires private correct pairs")
            left_refs = {item.ref for item in self.public.left_items}
            right_refs = {item.ref for item in self.public.right_items}
            pairs = self.private.correct_pairs
            if any(
                pair.left_ref not in left_refs or pair.right_ref not in right_refs for pair in pairs
            ):
                raise ValueError("matching key references an item that does not exist")
            if len({pair.left_ref for pair in pairs}) != len(pairs):
                raise ValueError("matching key repeats a left item")
        elif self.activity_type == "ordering":
            if not isinstance(self.public, PublicOrderingActivity):
                raise ValueError("ordering activity has an incompatible public model")
            if len(self.public.items) < 2:
                raise ValueError("validated ordering requires at least two items")
            if (
                not isinstance(self.private, PrivateOrderingData)
                or not self.private.correct_order_refs
            ):
                raise ValueError("validated ordering requires a private answer order")
            public_refs = [item.ref for item in self.public.items]
            if self.private.correct_order_refs != public_refs and set(
                self.private.correct_order_refs
            ) != set(public_refs):
                raise ValueError("private answer order must be a permutation of public items")

    def public_payload(self) -> dict[str, object]:
        """Serialize only the student-safe allow-listed activity fields."""
        return self.public.model_dump(mode="json")

    def private_payload(self) -> dict[str, object] | None:
        """Explicitly serialize private correction data for trusted internal use only."""
        return self.private.model_dump(mode="json") if self.private is not None else None

    def backend_question(self) -> QuizQuestionOut:
        """Adapt a validated objective item to the current backend question schema."""
        if (
            not isinstance(self.public, PublicMultipleChoiceActivity)
            or self.evaluator_compatibility != "compatible"
            or self.validation_state != "valid"
        ):
            raise ValueError("activity is not compatible with the current objective evaluator")
        return QuizQuestionOut(
            question_id=self.activity_ref,
            order=self.public.order,
            prompt=self.public.prompt,
            options=[
                QuizOptionOut(option_id=option.option_id, text=option.text)
                for option in self.public.options
            ],
        )

    def backend_grader_record(self) -> dict[str, object]:
        """Adapt private data to the current pure grader; never a public payload."""
        question = self.backend_question().model_dump(mode="json")
        if not isinstance(self.private, PrivateMultipleChoiceData):
            raise ValueError("activity has no private multiple-choice key")
        correct = self.private.resolved_correct_option_id
        if correct is None:
            raise ValueError("activity has no unambiguous correct option")
        material = self.private.answer_material
        return {
            **question,
            "correct_option_id": correct,
            "explanation": material.explanation if material else None,
            "answer_key_ref": material.answer_key_ref if material else None,
        }


@dataclass(frozen=True, slots=True)
class TypedActivityOutcome:
    phase: int
    activity_ref: str
    source_id: str
    source_file: str
    source_sha256: str
    activity_type: str
    classification: str
    conversion_status: str
    validation_state: str
    publication_state: str
    evaluator_compatibility: str
    diagnostic_code: str
    activity: TypedActivityRecord = field(repr=False)
    publishable: Literal["no"] = "no"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_activity_json(outcome: TypedActivityOutcome) -> str:
    """Canonical internal serialization; includes private data and must not be logged."""
    return json.dumps(
        outcome.activity.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _activity_kind(classification: str, source_format_signal: str) -> ActivityKind:
    mapping: dict[str, ActivityKind] = {
        "multiple_choice_recoverable": "multiple_choice",
        "multiple_choice_incomplete": "multiple_choice",
        "ambiguous_answer_key": "multiple_choice",
        "open_response": "short_answer",
        "discursive_exercise": "discursive",
        "review_question": "review",
    }
    if classification == "unidentified" and source_format_signal == "matching_unsupported":
        return "matching"
    if classification == "unidentified" and source_format_signal == "ordering_unsupported":
        return "ordering"
    try:
        return mapping[classification]
    except KeyError as exc:
        raise ValueError(f"unsupported or unclassified source activity: {classification}") from exc


def _private_answer_material(answer_key: object | None) -> PrivateAnswerMaterial | None:
    if answer_key is None:
        return None
    if not isinstance(answer_key, AnswerKeyBlock):
        raise TypeError("private answer material must come from a validated AnswerKeyBlock")
    # The source object is already validated by the bundle contract. Keep every
    # answer-bearing field in this private model.
    return PrivateAnswerMaterial(
        answer_key_ref=answer_key.ref,
        question_ref=answer_key.question_ref,
        correct_option_ref=answer_key.correct_option_ref,
        expected_answer=answer_key.expected_answer,
        accepted_answers=list(answer_key.accepted_answers),
        explanation=answer_key.explanation,
        source_markdown=answer_key.source_markdown,
        provenance=answer_key.provenance,
    )


def _public_activity(
    quiz: QuizBlock,
    activity_type: ActivityKind,
    version_ref: str,
    candidate: ExperimentalQuizCandidate | None,
) -> PublicActivity:
    if activity_type == "multiple_choice":
        options: list[ActivityOption] = []
        prompt = quiz.prompt
        if candidate is not None:
            prompt = candidate.public_question.prompt
            options = [
                ActivityOption(
                    option_id=option.option_id,
                    text=option.text,
                    source_label=option.option_id.upper(),
                )
                for option in candidate.public_question.options
            ]
        else:
            stem, extracted, parse_error = _split_options(quiz.prompt)
            if parse_error is None and extracted:
                prompt = stem
                options = [
                    ActivityOption(option_id=label.casefold(), text=text, source_label=label)
                    for label, text in extracted
                ]
        return PublicMultipleChoiceActivity(
            activity_ref=quiz.ref,
            version_ref=version_ref,
            title=quiz.title,
            order=quiz.order,
            type="multiple_choice",
            prompt=prompt,
            instructions=None,
            references=[],
            options=options,
        )
    if activity_type == "short_answer":
        return PublicShortAnswerActivity(
            activity_ref=quiz.ref,
            version_ref=version_ref,
            title=quiz.title,
            order=quiz.order,
            type="short_answer",
            prompt=quiz.prompt,
            instructions=None,
            references=[],
        )
    if activity_type == "discursive":
        return PublicDiscursiveActivity(
            activity_ref=quiz.ref,
            version_ref=version_ref,
            title=quiz.title,
            order=quiz.order,
            type="discursive",
            prompt=quiz.prompt,
            instructions=None,
            references=[],
        )
    if activity_type == "matching":
        # The 14D audit recognized the task verb, but did not prove a structured
        # left/right list. Preserve the exact prompt and leave these lists empty.
        return PublicMatchingActivity(
            activity_ref=quiz.ref,
            version_ref=version_ref,
            title=quiz.title,
            order=quiz.order,
            type="matching",
            prompt=quiz.prompt,
            instructions=None,
            references=[],
        )
    if activity_type == "ordering":
        # Likewise, preserve the text; do not infer items or the correct order.
        return PublicOrderingActivity(
            activity_ref=quiz.ref,
            version_ref=version_ref,
            title=quiz.title,
            order=quiz.order,
            type="ordering",
            prompt=quiz.prompt,
            instructions=None,
            references=[],
        )
    return PublicReviewActivity(
        activity_ref=quiz.ref,
        version_ref=version_ref,
        title=quiz.title,
        order=quiz.order,
        type="review",
        prompt=quiz.prompt,
        instructions=None,
        references=[],
    )


def _private_activity(
    activity_type: ActivityKind,
    answer_material: PrivateAnswerMaterial | None,
    candidate: ExperimentalQuizCandidate | None,
) -> PrivateActivity | None:
    if activity_type == "multiple_choice":
        resolved = candidate.private_answer_key.correct_option_id if candidate is not None else None
        return PrivateMultipleChoiceData(
            type="multiple_choice",
            answer_material=answer_material,
            resolved_correct_option_id=resolved,
        )
    if activity_type == "short_answer":
        return PrivateShortAnswerData(type="short_answer", answer_material=answer_material)
    if activity_type == "discursive":
        return PrivateDiscursiveData(type="discursive", answer_material=answer_material)
    if activity_type == "matching":
        return PrivateMatchingData(type="matching", answer_material=answer_material)
    if activity_type == "ordering":
        return PrivateOrderingData(type="ordering", answer_material=answer_material)
    if answer_material is None:
        return None
    return PrivateReviewData(type="review", answer_material=answer_material)


def _status_for(
    activity_type: ActivityKind,
    classification: str,
    outcome: QuizConversionOutcome,
) -> tuple[ValidationState, PublicationState, EvaluatorCompatibility, EvaluationPolicy]:
    if outcome.status == "converted_candidate" and activity_type == "multiple_choice":
        return (
            "valid",
            "structurally_validated",
            "compatible",
            ObjectiveQuizPolicy(type="objective_server_policy"),
        )
    if activity_type == "review":
        return (
            "valid",
            "pending_review",
            "not_applicable",
            UnscoredPolicy(type="unscored"),
        )
    if activity_type == "multiple_choice" and classification == "ambiguous_answer_key":
        return "ambiguous", "pending_review", "blocked", UndecidedPolicy(type="undecided")
    if activity_type == "multiple_choice":
        return "incomplete", "draft", "unsupported", UndecidedPolicy(type="undecided")
    if activity_type in {"matching", "ordering"}:
        return "incomplete", "pending_review", "unsupported", UndecidedPolicy(type="undecided")
    return "pending_review", "pending_review", "unsupported", UndecidedPolicy(type="undecided")


def _record_for(
    phase: int,
    quiz: QuizBlock,
    answer_key: AnswerKeyBlock | None,
    outcome: QuizConversionOutcome,
    classification: str,
    source_format_signal: str,
) -> TypedActivityOutcome:
    activity_type = _activity_kind(classification, source_format_signal)
    question_sha = quiz.provenance.source_sha256
    version_ref = f"question-source-sha256:{question_sha}"
    candidate = outcome.candidate
    public = _public_activity(quiz, activity_type, version_ref, candidate)
    material = _private_answer_material(answer_key)
    private = _private_activity(activity_type, material, candidate)
    validation, publication, compatibility, policy = _status_for(
        activity_type, classification, outcome
    )
    severity: Literal["info", "warning", "error"]
    if outcome.status == "converted_candidate" or activity_type == "review":
        severity = "info"
    elif validation == "ambiguous":
        severity = "error"
    else:
        severity = "warning"
    message = (
        "Estrutura tipada preservada; nenhuma autorização de publicação foi concedida."
        if candidate is not None
        else "Conteúdo preservado sem inferir campos ausentes nem habilitar correção automática."
    )
    diagnostics = [
        ActivityDiagnostic(
            code=outcome.reason_code,
            severity=severity,
            field="activity",
            message=message,
        )
    ]
    public_dict = public.model_dump(mode="json")
    public_sha = _sha256(_canonical_bytes(public_dict))
    private_dict = private.model_dump(mode="json") if private is not None else None
    private_sha = _sha256(_canonical_bytes(private_dict)) if private_dict is not None else None
    answer_sha = answer_key.provenance.source_sha256 if answer_key is not None else None
    record = TypedActivityRecord(
        activity_ref=quiz.ref,
        activity_type=activity_type,
        phase=phase,
        source_id=quiz.provenance.source_id or quiz.ref,
        source_markdown=quiz.prompt,
        public=public,
        private=private,
        version_ref=version_ref,
        validation_state=validation,
        publication_state=publication,
        evaluator_compatibility=compatibility,
        evaluation_policy=policy,
        provenance=quiz.provenance,
        integrity=ActivityIntegrity(
            question_source_sha256=question_sha,
            answer_source_sha256=answer_sha,
            public_payload_sha256=public_sha,
            private_payload_sha256=private_sha,
        ),
        diagnostics=diagnostics,
    )
    return TypedActivityOutcome(
        phase=phase,
        activity_ref=quiz.ref,
        source_id=quiz.provenance.source_id or quiz.ref,
        source_file=quiz.provenance.source_file,
        source_sha256=question_sha,
        activity_type=activity_type,
        classification=classification,
        conversion_status=outcome.status,
        validation_state=validation,
        publication_state=publication,
        evaluator_compatibility=compatibility,
        diagnostic_code=outcome.reason_code,
        activity=record,
    )


def convert_bundle_activities(
    bundle: CurriculumImportBundle,
    audit_records: list[QuizStructureAudit],
) -> list[TypedActivityOutcome]:
    """Convert the 14D quiz inventory to typed in-memory records, fail closed.

    The caller supplies source-audit records for the 501 keyed questions.
    Five unkeyed R1–R5 items are represented as unscored review activities.
    """
    outcomes = analyze_bundle_quizzes(bundle)
    audit_map = {(item.phase, item.quiz_ref): item for item in audit_records}
    if len(audit_map) != len(audit_records):
        raise ValueError("duplicate source audit records")

    blocks_by_phase: dict[int, dict[str, object]] = {
        entry.phase: {block.ref: block for block in entry.contract.blocks}
        for entry in bundle.phases
    }
    keys_by_phase: dict[int, dict[str, AnswerKeyBlock]] = {
        entry.phase: {
            block.ref: block for block in entry.contract.blocks if isinstance(block, AnswerKeyBlock)
        }
        for entry in bundle.phases
    }
    result: list[TypedActivityOutcome] = []
    seen: set[tuple[int, str]] = set()
    for outcome in sorted(outcomes, key=lambda item: (item.phase, item.quiz_ref)):
        identity = (outcome.phase, outcome.quiz_ref)
        if identity in seen:
            raise ValueError(f"duplicate quiz identity: {outcome.quiz_ref}")
        seen.add(identity)
        quiz = blocks_by_phase.get(outcome.phase, {}).get(outcome.quiz_ref)
        if not isinstance(quiz, QuizBlock):
            raise ValueError(f"quiz source block is missing: {outcome.quiz_ref}")
        key = keys_by_phase.get(outcome.phase, {}).get(quiz.answer_key_ref or "")
        if outcome.status == "unscored_review_pending":
            if quiz.answer_key_required or key is not None:
                raise ValueError(f"unkeyed review unexpectedly has an answer key: {quiz.ref}")
            result.append(
                _record_for(
                    outcome.phase,
                    quiz,
                    None,
                    outcome,
                    "review_question",
                    "unkeyed_review",
                )
            )
            continue

        audit = audit_map.get(identity)
        if audit is None:
            raise ValueError(f"keyed quiz has no 14D source classification: {quiz.ref}")
        if key is None or key.ref != quiz.answer_key_ref or key.question_ref != quiz.ref:
            raise ValueError(f"quiz answer-key relation is invalid: {quiz.ref}")
        if audit.current_status != outcome.status or audit.answer_key_ref != key.ref:
            raise ValueError(f"14D audit does not match current conversion: {quiz.ref}")
        result.append(
            _record_for(
                outcome.phase,
                quiz,
                key,
                outcome,
                audit.classification,
                audit.source_format_signal,
            )
        )
    if len(result) != 506:
        raise ValueError(f"expected 506 activities (501 keyed plus R1–R5), found {len(result)}")
    if len(audit_map) != 501:
        raise ValueError(f"expected 501 keyed source classifications, found {len(audit_map)}")
    return result


def validate_activity_records(
    outcomes: list[TypedActivityOutcome],
    *,
    known_refs: set[str] | None = None,
    allow_multiple_versions: bool = False,
) -> list[ActivityDiagnostic]:
    """Validate collection-level identities and internal activity references."""
    known = set(known_refs or ()) | {item.activity_ref for item in outcomes}
    diagnostics: list[ActivityDiagnostic] = []
    seen_refs: set[str] = set()
    seen_versions: set[tuple[str, str]] = set()
    for item in outcomes:
        version_key = (item.activity_ref, item.activity.version_ref)
        duplicate = version_key in seen_versions or (
            not allow_multiple_versions and item.activity_ref in seen_refs
        )
        if duplicate:
            diagnostics.append(
                ActivityDiagnostic(
                    code="ACTIVITY_ID_DUPLICATED",
                    severity="error",
                    field="activity_ref",
                    message="A identidade curricular da atividade aparece mais de uma vez.",
                )
            )
        seen_refs.add(item.activity_ref)
        seen_versions.add(version_key)
        for reference in item.activity.public.references:
            if reference.kind == "internal" and reference.target_ref not in known:
                diagnostics.append(
                    ActivityDiagnostic(
                        code="ACTIVITY_REFERENCE_UNRESOLVED",
                        severity="error",
                        field="public.references.target_ref",
                        message="A referência curricular não aponta para uma identidade conhecida.",
                    )
                )
        private_rubric_refs = getattr(item.activity.private, "rubric_refs", [])
        for rubric_ref in private_rubric_refs:
            if rubric_ref not in known:
                diagnostics.append(
                    ActivityDiagnostic(
                        code="ACTIVITY_PRIVATE_RUBRIC_UNRESOLVED",
                        severity="error",
                        field="private.rubric_refs",
                        message="A referência privada de rubrica não aponta para uma identidade conhecida.",
                    )
                )
    return diagnostics


def typed_activity_csv(outcomes: list[TypedActivityOutcome]) -> str:
    """Serialize a deterministic inventory without prompts or answer content."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "phase",
            "activity_ref",
            "source_id",
            "source_file",
            "source_sha256",
            "activity_type",
            "classification",
            "conversion_status",
            "validation_state",
            "publication_state",
            "evaluator_compatibility",
            "evaluation_policy",
            "private_material_present",
            "diagnostic_code",
            "publishable",
        ]
    )
    for item in sorted(outcomes, key=lambda row: (row.phase, row.activity_ref)):
        policy_type = item.activity.evaluation_policy.type
        writer.writerow(
            [
                item.phase,
                item.activity_ref,
                item.source_id,
                item.source_file,
                item.source_sha256,
                item.activity_type,
                item.classification,
                item.conversion_status,
                item.validation_state,
                item.publication_state,
                item.evaluator_compatibility,
                policy_type,
                "yes" if item.activity.private is not None else "no",
                item.diagnostic_code,
                item.publishable,
            ]
        )
    return output.getvalue()
