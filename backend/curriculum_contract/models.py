"""Pydantic models for a future import package; isolated from production schemas."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

LEGACY_CONTRACT_VERSION = "trilhacode.intermediate/1.0"
CONTRACT_VERSION: Literal["trilhacode.intermediate/1.2"] = "trilhacode.intermediate/1.2"

StableId = Annotated[
    str,
    StringConstraints(
        strict=True,
        pattern=r"^f(?:[1-9]|10)-[a-z0-9]+(?:-[a-z0-9]+)*$",
        min_length=5,
    ),
]
NonEmptyText = Annotated[str, StringConstraints(strict=True, min_length=1)]
NonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
Slug = Annotated[str, StringConstraints(strict=True, pattern=r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")]


def _validate_repo_relative_posix_path(value: str) -> str:
    if (
        value.startswith(("/", "\\"))
        or "\\" in value
        or (len(value) > 1 and value[1] == ":")
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError("path must be normalized repository-relative POSIX")
    return value


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourceManifest(ContractModel):
    manifest_path: NonEmptyText
    manifest_sha256: str
    source_revision: NonEmptyText
    converter_version: NonEmptyText

    @field_validator("manifest_path")
    @classmethod
    def manifest_path_is_repository_relative(cls, value: str) -> str:
        return _validate_repo_relative_posix_path(value)


class SourceProvenance(ContractModel):
    source_file: NonEmptyText
    source_sha256: str
    manifest_ref: NonEmptyText
    source_role: NonEmptyText
    source_id: str | None = None

    @field_validator("source_file")
    @classmethod
    def source_file_is_repository_relative(cls, value: str) -> str:
        return _validate_repo_relative_posix_path(value)


NodeKind = Literal["phase", "module", "submodule", "topic"]
RelationKind = Literal["prerequisite", "complement", "revisit", "related"]
BlockStatus = Literal["draft", "published", "archived"]
ReferenceKind = Literal["external", "internal", "obsidian", "editorial"]
ProgressScope = Literal["undecided", "per_context", "shared_global"]


class CurriculumNode(ContractModel):
    ref: StableId
    kind: NodeKind
    parent_ref: StableId | None
    title: NonEmptyText
    order: NonNegativeInt
    status: BlockStatus
    estimated_minutes: NonNegativeInt | None
    source_metadata: dict[str, Any]
    tags: list[NonEmptyText]
    provenance: SourceProvenance


class CurriculumRelation(ContractModel):
    ref: StableId
    source_ref: StableId
    target_ref: StableId
    kind: RelationKind
    enforced: bool
    note: str
    provenance: SourceProvenance


class BlockBase(ContractModel):
    ref: StableId
    type: str
    owner_ref: StableId | None
    order: NonNegativeInt
    title: str
    status: BlockStatus
    shared: bool
    provenance: SourceProvenance


class ObjectiveBlock(BlockBase):
    type: Literal["objective"]
    body: NonEmptyText


class SummaryBlock(BlockBase):
    type: Literal["summary"]
    body: NonEmptyText


class ConclusionBlock(BlockBase):
    type: Literal["conclusion"]
    body: NonEmptyText


class TheoryBlock(BlockBase):
    type: Literal["theory"]
    body: NonEmptyText
    microtopic: str | None


class QuizOption(ContractModel):
    ref: Slug
    text: NonEmptyText


class QuizBlock(BlockBase):
    type: Literal["quiz"]
    prompt: NonEmptyText
    format: Literal[
        "multiple_choice", "true_false", "short_answer", "ordering", "fill_code", "other"
    ]
    options: list[QuizOption]
    answer_key_required: bool
    answer_key_ref: StableId | None


class AnswerKeyBlock(BlockBase):
    type: Literal["answer_key"]
    question_ref: StableId
    correct_option_ref: Slug | None
    accepted_answers: list[NonEmptyText]
    expected_answer: str | None
    explanation: str | None
    source_markdown: str | None = None


class PracticeBlock(BlockBase):
    type: Literal["practice"]
    prompt: NonEmptyText
    language: str | None
    starter_code: str | None
    acceptance: list[NonEmptyText]


class SolutionBlock(BlockBase):
    type: Literal["solution"]
    practice_ref: StableId
    body: NonEmptyText
    reveal_policy: Literal["not_decided", "instructor_only", "after_attempt"]


class FeedbackBlock(BlockBase):
    type: Literal["feedback"]
    target_ref: StableId
    body: NonEmptyText


class InstructorNoteBlock(BlockBase):
    type: Literal["instructor_note"]
    audience: Literal["instructor_only"]
    body: NonEmptyText


class FlashcardBlock(BlockBase):
    type: Literal["flashcard"]
    front: NonEmptyText
    back: NonEmptyText
    source_markdown: str | None = None


class ChecklistItem(ContractModel):
    ref: Slug
    text: NonEmptyText
    checked: bool | None = None


class ChecklistBlock(BlockBase):
    type: Literal["checklist"]
    items: list[ChecklistItem]
    source_markdown: str | None = None
    source_item_labels: list[str] = Field(default_factory=list)


class AcceptanceCriteriaBlock(BlockBase):
    type: Literal["acceptance_criteria"]
    delivery_ref: StableId | None
    milestone_ref: StableId | None
    practice_ref: StableId | None = None
    items: list[ChecklistItem]
    body: str | None = None
    source_item_labels: list[str] = Field(default_factory=list)
    related_refs: list[StableId] = Field(default_factory=list)


class CompletionCriteriaBlock(BlockBase):
    type: Literal["completion_criteria"]
    body: NonEmptyText
    source_item_labels: list[str] = Field(default_factory=list)
    related_refs: list[StableId] = Field(default_factory=list)


class ProjectDecisionBlock(BlockBase):
    type: Literal["project_decision"]
    body: NonEmptyText
    source_item_labels: list[str] = Field(default_factory=list)
    related_refs: list[StableId] = Field(default_factory=list)


class ProjectScenarioBlock(BlockBase):
    type: Literal["project_scenario"]
    body: NonEmptyText
    source_item_labels: list[str] = Field(default_factory=list)
    related_refs: list[StableId] = Field(default_factory=list)


class ProjectReviewBlock(BlockBase):
    type: Literal["project_review"]
    body: NonEmptyText
    source_item_labels: list[str] = Field(default_factory=list)
    related_refs: list[StableId] = Field(default_factory=list)


class ScoreScale(ContractModel):
    minimum: int
    maximum: int


class RubricDimension(ContractModel):
    ref: Slug
    title: NonEmptyText
    weight: float
    descriptors: dict[str, NonEmptyText]


class RubricBlock(BlockBase):
    type: Literal["rubric"]
    target_ref: StableId
    target_refs: list[StableId] = Field(default_factory=list)
    scale: ScoreScale | None
    dimensions: list[RubricDimension]
    threshold: float | None
    source_markdown: str | None = None
    source_item_labels: list[str] = Field(default_factory=list)


class ReferenceBlock(BlockBase):
    type: Literal["reference"]
    target_kind: ReferenceKind
    label: str
    citation: str
    url: str | None
    target_ref: StableId | None
    raw_text: str | None
    pending_ref: StableId | None


ContentBlock = Annotated[
    Union[
        ObjectiveBlock,
        SummaryBlock,
        ConclusionBlock,
        TheoryBlock,
        QuizBlock,
        AnswerKeyBlock,
        PracticeBlock,
        SolutionBlock,
        FeedbackBlock,
        InstructorNoteBlock,
        FlashcardBlock,
        ChecklistBlock,
        AcceptanceCriteriaBlock,
        CompletionCriteriaBlock,
        ProjectDecisionBlock,
        ProjectScenarioBlock,
        ProjectReviewBlock,
        RubricBlock,
        ReferenceBlock,
    ],
    Field(discriminator="type"),
]


class SharedPlacement(ContractModel):
    ref: StableId
    block_ref: StableId
    subject_ref: StableId
    order: NonNegativeInt
    progress_scope: ProgressScope
    provenance: SourceProvenance


class ProjectDelivery(ContractModel):
    ref: StableId
    title: NonEmptyText
    body: str | None = None
    order: NonNegativeInt
    acceptance_refs: list[StableId]
    checklist_refs: list[StableId]
    rubric_refs: list[StableId]
    content_refs: list[StableId]
    provenance: SourceProvenance


class ProjectMilestone(ContractModel):
    ref: StableId
    title: NonEmptyText
    body: str | None = None
    order: NonNegativeInt
    acceptance_refs: list[StableId]
    checklist_refs: list[StableId]
    rubric_refs: list[StableId]
    content_refs: list[StableId]
    provenance: SourceProvenance


class ProjectVariant(ContractModel):
    ref: StableId
    title: NonEmptyText
    order: NonNegativeInt
    description: str
    delivery_refs: list[StableId]
    stack_option: NonEmptyText | None
    provenance: SourceProvenance


class ProjectSpec(ContractModel):
    ref: StableId
    unit_ref: StableId
    title: NonEmptyText
    scope: str
    has_formal_deliveries: bool
    deliveries: list[ProjectDelivery]
    has_formal_milestones: bool
    milestones: list[ProjectMilestone]
    variants: list[ProjectVariant]
    checklist_refs: list[StableId]
    rubric_refs: list[StableId]
    stack_options: list[NonEmptyText]
    stack_selected: NonEmptyText | None
    source_metadata: dict[str, Any]
    provenance: SourceProvenance


PendingKind = Literal[
    "unresolved_reference",
    "obsidian_vault_root_unknown",
    "editorial_transfer",
    "source_version_conflict",
]


class EditorialPending(ContractModel):
    ref: StableId
    kind: PendingKind
    source_file: NonEmptyText
    entity_ref: StableId | None
    reference_text: NonEmptyText
    destination_ref: StableId | None
    blocking: bool
    note: NonEmptyText
    provenance: SourceProvenance


class IntermediateContract(ContractModel):
    schema_version: Literal[
        "trilhacode.intermediate/1.0",
        "trilhacode.intermediate/1.1",
        "trilhacode.intermediate/1.2",
    ]
    source: SourceManifest
    nodes: list[CurriculumNode]
    blocks: list[ContentBlock]
    relations: list[CurriculumRelation]
    shared_placements: list[SharedPlacement]
    projects: list[ProjectSpec]
    editorial_pendings: list[EditorialPending]
    vault_root_confirmed: bool


class QuizPresentation(ContractModel):
    ref: StableId
    type: Literal["quiz"]
    title: str
    order: NonNegativeInt
    prompt: NonEmptyText
    format: Literal[
        "multiple_choice", "true_false", "short_answer", "ordering", "fill_code", "other"
    ]
    options: list[QuizOption]


def student_quiz_view(quiz: QuizBlock) -> QuizPresentation:
    """Project only author-approved prompt fields; never return answer-key references."""
    return QuizPresentation(
        ref=quiz.ref,
        type="quiz",
        title=quiz.title,
        order=quiz.order,
        prompt=quiz.prompt,
        format=quiz.format,
        options=quiz.options,
    )


def json_schema() -> dict[str, Any]:
    """Return the Pydantic-generated JSON Schema for the versioned package."""
    return IntermediateContract.model_json_schema()


def canonical_json(contract: IntermediateContract) -> str:
    """Serialize deterministically while respecting explicit curriculum order."""
    payload = contract.model_dump(mode="json")
    kind_order = {"phase": 0, "module": 1, "submodule": 2, "topic": 3}
    node_map = {node["ref"]: node for node in payload["nodes"]}

    def node_depth(ref: str) -> int:
        depth = 0
        visited: set[str] = set()
        current = node_map.get(ref)
        while current and current.get("parent_ref") in node_map:
            parent_ref = current["parent_ref"]
            if parent_ref in visited:
                break
            visited.add(parent_ref)
            depth += 1
            current = node_map[parent_ref]
        return depth

    payload["nodes"].sort(
        key=lambda item: (
            node_depth(item["ref"]),
            item.get("parent_ref") or "",
            kind_order[item["kind"]],
            item["order"],
            item["ref"],
        )
    )
    payload["blocks"].sort(
        key=lambda item: (item.get("owner_ref") or "", item["order"], item["ref"])
    )
    payload["relations"].sort(key=lambda item: item["ref"])
    payload["shared_placements"].sort(
        key=lambda item: (item["subject_ref"], item["order"], item["ref"])
    )
    payload["projects"].sort(key=lambda item: item["ref"])
    for project in payload["projects"]:
        project["deliveries"].sort(key=lambda item: (item["order"], item["ref"]))
        project["milestones"].sort(key=lambda item: (item["order"], item["ref"]))
        project["variants"].sort(key=lambda item: (item["order"], item["ref"]))
    payload["editorial_pendings"].sort(key=lambda item: item["ref"])
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
