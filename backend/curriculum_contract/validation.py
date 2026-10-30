"""Pure validation and future change-classification helpers for the intermediate contract."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, Mapping
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, ValidationError

from .models import (
    AcceptanceCriteriaBlock,
    AnswerKeyBlock,
    ChecklistBlock,
    CompletionCriteriaBlock,
    CurriculumNode,
    FeedbackBlock,
    FlashcardBlock,
    IntermediateContract,
    PracticeBlock,
    ProjectDecisionBlock,
    ProjectDelivery,
    ProjectMilestone,
    ProjectReviewBlock,
    ProjectScenarioBlock,
    QuizBlock,
    ReferenceBlock,
    RubricBlock,
    SolutionBlock,
    SourceProvenance,
)

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class DiagnosticSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Diagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str
    severity: DiagnosticSeverity
    source_file: str | None = None
    entity_ref: str | None = None
    field: str | None = None
    reference: str | None = None
    message: str
    remediation: str


@dataclass(frozen=True)
class ValidationReport:
    contract: IntermediateContract | None
    diagnostics: tuple[Diagnostic, ...]

    @property
    def ok(self) -> bool:
        return not any(item.severity == DiagnosticSeverity.ERROR for item in self.diagnostics)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "diagnostics": [item.model_dump(mode="json") for item in self.diagnostics],
        }


def _raw_entity_context(value: Any, location: tuple[Any, ...]) -> dict[str, Any]:
    if not isinstance(value, dict) or not location:
        return {}
    collection = location[0]
    if collection in {
        "nodes",
        "blocks",
        "relations",
        "shared_placements",
        "projects",
        "editorial_pendings",
    }:
        if len(location) > 1 and isinstance(location[1], int):
            items = value.get(collection)
            if (
                isinstance(items, list)
                and location[1] < len(items)
                and isinstance(items[location[1]], dict)
            ):
                return items[location[1]]
    return {}


def _schema_diagnostics(error: ValidationError, value: Any) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    for issue in error.errors(include_url=False):
        location = tuple(issue.get("loc", ()))
        context = _raw_entity_context(value, location)
        provenance = context.get("provenance") or context.get("source") or {}
        source_file = provenance.get("source_file") if isinstance(provenance, dict) else None
        entity_ref = context.get("ref") or context.get("unit_ref")
        field = ".".join(str(part) for part in location) or None
        issue_type = str(issue.get("type", ""))
        last = str(location[-1]) if location else ""
        if "union_tag" in issue_type:
            code = "UNKNOWN_BLOCK_TYPE"
            remediation = "Map the source block to an explicit supported contract type; do not coerce it to theory."
        elif last in {"source", "provenance"} and issue_type == "missing":
            code = "SOURCE_METADATA_MISSING"
            remediation = (
                "Provide path, SHA-256, manifest reference, and source role for this entity."
            )
        elif last in {"sha256", "source_sha256", "manifest_sha256"}:
            code = "INVALID_SHA256"
            remediation = "Provide the lowercase 64-character SHA-256 digest of the corresponding source bytes."
        elif (
            last in {"ref", "parent_ref", "owner_ref", "target_ref", "question_ref", "practice_ref"}
            and "string_pattern" in issue_type
        ):
            code = "INVALID_ENTITY_ID"
            remediation = "Use a stable, globally unique ID with the f1–f10 phase prefix."
        elif last in {"source_file", "manifest_path"} and "value_error" in issue_type:
            code = "SOURCE_PATH_INVALID"
            remediation = "Use a normalized repository-relative POSIX path without drive letters or parent segments."
        else:
            code = "SCHEMA_INVALID"
            remediation = "Correct the field according to the versioned intermediate contract."
        diagnostics.append(
            Diagnostic(
                code=code,
                severity=DiagnosticSeverity.ERROR,
                source_file=source_file,
                entity_ref=entity_ref,
                field=field,
                message=str(issue.get("msg", "Invalid contract value")),
                remediation=remediation,
            )
        )
    return tuple(diagnostics)


def _walk_entities(contract: IntermediateContract) -> list[tuple[str, str, str | None]]:
    entities: list[tuple[str, str, str | None]] = []
    for node in contract.nodes:
        entities.append((node.ref, "node", node.provenance.source_file))
    for block in contract.blocks:
        entities.append((block.ref, "block", block.provenance.source_file))
    for relation in contract.relations:
        entities.append((relation.ref, "relation", relation.provenance.source_file))
    for placement in contract.shared_placements:
        entities.append((placement.ref, "placement", placement.provenance.source_file))
    for project in contract.projects:
        entities.append((project.ref, "project", project.provenance.source_file))
        for delivery in project.deliveries:
            entities.append((delivery.ref, "delivery", delivery.provenance.source_file))
        for milestone in project.milestones:
            entities.append((milestone.ref, "milestone", milestone.provenance.source_file))
        for variant in project.variants:
            entities.append((variant.ref, "project_variant", variant.provenance.source_file))
    for pending in contract.editorial_pendings:
        entities.append((pending.ref, "editorial_pending", pending.provenance.source_file))
    return entities


def _all_provenance(contract: IntermediateContract) -> list[tuple[str, SourceProvenance]]:
    result: list[tuple[str, SourceProvenance]] = []
    for node in contract.nodes:
        result.append((node.ref, node.provenance))
    for block in contract.blocks:
        result.append((block.ref, block.provenance))
    for relation in contract.relations:
        result.append((relation.ref, relation.provenance))
    for placement in contract.shared_placements:
        result.append((placement.ref, placement.provenance))
    for project in contract.projects:
        result.append((project.ref, project.provenance))
        result.extend((delivery.ref, delivery.provenance) for delivery in project.deliveries)
        result.extend((milestone.ref, milestone.provenance) for milestone in project.milestones)
        result.extend((variant.ref, variant.provenance) for variant in project.variants)
    result.extend((pending.ref, pending.provenance) for pending in contract.editorial_pendings)
    return result


def _duplicate_order(
    diagnostics: list[Diagnostic],
    occupied: dict[tuple[str, int], tuple[str, str | None]],
    owner_ref: str,
    order: int,
    entity_ref: str,
    source_file: str | None,
    field: str,
) -> None:
    key = (owner_ref, order)
    if key in occupied:
        other_ref, _ = occupied[key]
        diagnostics.append(
            Diagnostic(
                code="DUPLICATE_ORDER",
                severity=DiagnosticSeverity.ERROR,
                source_file=source_file,
                entity_ref=entity_ref,
                field=field,
                reference=other_ref,
                message=f"Order {order} is already used by {other_ref} in context {owner_ref}.",
                remediation="Assign a distinct explicit order within this parent or subject context.",
            )
        )
    else:
        occupied[key] = (entity_ref, source_file)


def _find_cycles(graph: Mapping[str, list[str]]) -> list[list[str]]:
    state: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[list[str]] = []
    cycle_keys: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for target in graph.get(node, []):
            if state.get(target, 0) == 0:
                visit(target)
            elif state.get(target) == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                key = tuple(sorted(set(cycle[:-1])))
                if key not in cycle_keys:
                    cycle_keys.add(key)
                    cycles.append(cycle)
        stack.pop()
        state[node] = 2

    for node in graph:
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def _semantic_diagnostics(contract: IntermediateContract) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []

    def add(
        code: str,
        severity: DiagnosticSeverity,
        message: str,
        *,
        source_file: str | None = None,
        entity_ref: str | None = None,
        field: str | None = None,
        reference: str | None = None,
        remediation: str,
    ) -> None:
        diagnostics.append(
            Diagnostic(
                code=code,
                severity=severity,
                source_file=source_file,
                entity_ref=entity_ref,
                field=field,
                reference=reference,
                message=message,
                remediation=remediation,
            )
        )

    entities = _walk_entities(contract)
    entity_sources: dict[str, str | None] = {}
    entity_kinds: dict[str, str] = {}
    for ref, kind, source_file in entities:
        if ref in entity_kinds:
            add(
                "DUPLICATE_ID",
                DiagnosticSeverity.ERROR,
                f"ID {ref} is used by more than one entity ({entity_kinds[ref]} and {kind}).",
                source_file=source_file,
                entity_ref=ref,
                field="ref",
                reference=ref,
                remediation="Assign a globally unique stable ID; do not derive identity from mutable order or title.",
            )
        else:
            entity_kinds[ref] = kind
            entity_sources[ref] = source_file

    for source_ref, provenance in _all_provenance(contract):
        if not SHA256_PATTERN.fullmatch(provenance.source_sha256):
            add(
                "INVALID_SHA256",
                DiagnosticSeverity.ERROR,
                "Source SHA-256 must be 64 lowercase hexadecimal characters.",
                source_file=provenance.source_file,
                entity_ref=source_ref,
                field="provenance.source_sha256",
                remediation="Recompute SHA-256 from the exact source bytes and update the provenance record.",
            )
    if not SHA256_PATTERN.fullmatch(contract.source.manifest_sha256):
        add(
            "INVALID_SHA256",
            DiagnosticSeverity.ERROR,
            "Manifest SHA-256 must be 64 lowercase hexadecimal characters.",
            source_file=contract.source.manifest_path,
            field="source.manifest_sha256",
            remediation="Recompute SHA-256 from the approved manifest bytes.",
        )

    try:
        json.dumps(contract.model_dump(mode="json"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        add(
            "NON_JSON_METADATA",
            DiagnosticSeverity.ERROR,
            "Contract values must be serializable as strict JSON.",
            remediation="Replace unsupported metadata values with JSON scalars, arrays, or objects without dropping source values.",
        )

    node_by_ref = {node.ref: node for node in contract.nodes}
    expected_parent = {"module": "phase", "submodule": "module", "topic": "submodule"}
    sibling_orders: dict[tuple[str, int], tuple[str, str | None]] = {}
    for node in contract.nodes:
        if node.kind == "phase":
            if node.parent_ref is not None:
                add(
                    "INVALID_HIERARCHY",
                    DiagnosticSeverity.ERROR,
                    "A phase node must be a root node.",
                    source_file=node.provenance.source_file,
                    entity_ref=node.ref,
                    field="parent_ref",
                    reference=node.parent_ref,
                    remediation="Place phase nodes at the root; do not invent a parent level.",
                )
        elif node.parent_ref is None:
            add(
                "PARENT_MISSING",
                DiagnosticSeverity.ERROR,
                f"A {node.kind} node requires a parent.",
                source_file=node.provenance.source_file,
                entity_ref=node.ref,
                field="parent_ref",
                remediation=f"Attach the node to an existing {expected_parent[node.kind]} node.",
            )
        elif node.parent_ref not in node_by_ref:
            add(
                "PARENT_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Parent {node.parent_ref} does not exist in the contract.",
                source_file=node.provenance.source_file,
                entity_ref=node.ref,
                field="parent_ref",
                reference=node.parent_ref,
                remediation="Add the source-backed parent node or correct the reference; do not create a fictitious unit.",
            )
        elif node_by_ref[node.parent_ref].kind != expected_parent[node.kind]:
            add(
                "INVALID_HIERARCHY",
                DiagnosticSeverity.ERROR,
                f"{node.kind} must be a child of {expected_parent[node.kind]}, not {node_by_ref[node.parent_ref].kind}.",
                source_file=node.provenance.source_file,
                entity_ref=node.ref,
                field="parent_ref",
                reference=node.parent_ref,
                remediation="Use phase → module → submodule → topic and preserve source-backed nodes only.",
            )
        if node.parent_ref is not None:
            _duplicate_order(
                diagnostics,
                sibling_orders,
                node.parent_ref,
                node.order,
                node.ref,
                node.provenance.source_file,
                "order",
            )

    for node in contract.nodes:
        seen: set[str] = set()
        current: CurriculumNode | None = node
        while current is not None and current.parent_ref in node_by_ref:
            if current.ref in seen:
                add(
                    "HIERARCHY_CYCLE",
                    DiagnosticSeverity.ERROR,
                    "A cycle was found in parent_ref relationships.",
                    source_file=node.provenance.source_file,
                    entity_ref=node.ref,
                    field="parent_ref",
                    reference=current.ref,
                    remediation="Remove the cyclic parent assignment while retaining the source hierarchy.",
                )
                break
            seen.add(current.ref)
            current = node_by_ref.get(current.parent_ref) if current.parent_ref else None

    blocks_by_ref = {block.ref: block for block in contract.blocks}
    projects_by_ref = {project.ref: project for project in contract.projects}
    delivery_by_ref: dict[str, ProjectDelivery] = {
        delivery.ref: delivery for project in contract.projects for delivery in project.deliveries
    }
    milestone_by_ref = {
        milestone.ref: milestone
        for project in contract.projects
        for milestone in project.milestones
    }
    known_owner_refs = (
        set(node_by_ref) | set(projects_by_ref) | set(delivery_by_ref) | set(milestone_by_ref)
    )
    known_entity_refs = {ref for ref, _, _ in _walk_entities(contract)}
    shared_placements_by_block: dict[str, list[Any]] = {}
    display_orders: dict[tuple[str, int], tuple[str, str | None]] = {}

    for block in contract.blocks:
        if block.shared:
            if block.owner_ref is not None:
                add(
                    "SHARED_BLOCK_HAS_OWNER",
                    DiagnosticSeverity.ERROR,
                    "A canonical shared block must not be assigned to one subject as its sole owner.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="owner_ref",
                    reference=block.owner_ref,
                    remediation="Leave the canonical block unattached and represent each context through a placement.",
                )
        else:
            if block.owner_ref is None:
                add(
                    "BLOCK_OWNER_MISSING",
                    DiagnosticSeverity.ERROR,
                    "A non-shared block requires an owner node, project, or delivery.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="owner_ref",
                    remediation="Attach the block to its source-backed curricular context.",
                )
            elif block.owner_ref not in known_owner_refs:
                add(
                    "BLOCK_OWNER_NOT_FOUND",
                    DiagnosticSeverity.ERROR,
                    f"Block owner {block.owner_ref} does not exist.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="owner_ref",
                    reference=block.owner_ref,
                    remediation="Correct the owner reference or include its source-backed entity.",
                )
            else:
                _duplicate_order(
                    diagnostics,
                    display_orders,
                    block.owner_ref,
                    block.order,
                    block.ref,
                    block.provenance.source_file,
                    "order",
                )
        if isinstance(block, QuizBlock):
            option_refs = [option.ref for option in block.options]
            if len(option_refs) != len(set(option_refs)):
                add(
                    "DUPLICATE_QUIZ_OPTION_ID",
                    DiagnosticSeverity.ERROR,
                    "Quiz option references must be unique within the question.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="options",
                    remediation="Give each option a distinct stable local reference.",
                )
            if block.format == "multiple_choice" and len(block.options) < 2:
                add(
                    "QUIZ_OPTIONS_INVALID",
                    DiagnosticSeverity.ERROR,
                    "A multiple-choice quiz requires at least two options.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="options",
                    remediation="Preserve the alternatives present in the source or change the declared format.",
                )
            if block.format == "true_false" and len(block.options) != 2:
                add(
                    "QUIZ_OPTIONS_INVALID",
                    DiagnosticSeverity.ERROR,
                    "A true/false quiz requires exactly two options.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="options",
                    remediation="Represent the two source alternatives explicitly.",
                )

    quiz_by_ref = {block.ref: block for block in contract.blocks if isinstance(block, QuizBlock)}
    answer_keys = {
        block.ref: block for block in contract.blocks if isinstance(block, AnswerKeyBlock)
    }
    answer_keys_by_question: dict[str, list[AnswerKeyBlock]] = {}
    for key in answer_keys.values():
        answer_keys_by_question.setdefault(key.question_ref, []).append(key)
        quiz = quiz_by_ref.get(key.question_ref)
        if quiz is None:
            add(
                "ANSWER_KEY_QUESTION_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Answer key points to missing quiz {key.question_ref}.",
                source_file=key.provenance.source_file,
                entity_ref=key.ref,
                field="question_ref",
                reference=key.question_ref,
                remediation="Point the key to its original quiz item; do not duplicate or infer questions.",
            )
            continue
        if quiz.answer_key_ref != key.ref:
            add(
                "ANSWER_KEY_ASSOCIATION_MISMATCH",
                DiagnosticSeverity.ERROR,
                f"Quiz {quiz.ref} does not reference answer key {key.ref}.",
                source_file=key.provenance.source_file,
                entity_ref=key.ref,
                field="question_ref",
                reference=quiz.ref,
                remediation="Make the quiz and answer key references reciprocal and unambiguous.",
            )
        answer_forms = sum(
            [
                key.correct_option_ref is not None,
                bool(key.accepted_answers),
                key.expected_answer is not None,
            ]
        )
        if answer_forms != 1:
            add(
                "ANSWER_KEY_CONTENT_INVALID",
                DiagnosticSeverity.ERROR,
                "Answer key must contain exactly one answer representation.",
                source_file=key.provenance.source_file,
                entity_ref=key.ref,
                field="correct_option_ref",
                remediation="Preserve the source answer in one typed field without adding alternatives.",
            )
        if key.correct_option_ref is not None and key.correct_option_ref not in {
            item.ref for item in quiz.options
        }:
            add(
                "ANSWER_KEY_OPTION_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Correct option {key.correct_option_ref} does not exist on quiz {quiz.ref}.",
                source_file=key.provenance.source_file,
                entity_ref=key.ref,
                field="correct_option_ref",
                reference=key.correct_option_ref,
                remediation="Use the exact option reference from the associated quiz.",
            )
    for quiz in quiz_by_ref.values():
        keys = answer_keys_by_question.get(quiz.ref, [])
        if len(keys) > 1:
            add(
                "QUIZ_ANSWER_KEY_AMBIGUOUS",
                DiagnosticSeverity.ERROR,
                f"Quiz {quiz.ref} has more than one answer key.",
                source_file=quiz.provenance.source_file,
                entity_ref=quiz.ref,
                field="answer_key_ref",
                remediation="Associate exactly one original answer key with this quiz.",
            )
        if quiz.answer_key_required:
            matched_key = answer_keys.get(quiz.answer_key_ref or "")
            if matched_key is None:
                add(
                    "QUIZ_ANSWER_KEY_MISSING",
                    DiagnosticSeverity.ERROR,
                    f"Quiz {quiz.ref} requires an answer key that is absent.",
                    source_file=quiz.provenance.source_file,
                    entity_ref=quiz.ref,
                    field="answer_key_ref",
                    reference=quiz.answer_key_ref,
                    remediation="Map the existing answer key, or record that the source does not require one.",
                )
            elif matched_key.question_ref != quiz.ref:
                add(
                    "ANSWER_KEY_ASSOCIATION_MISMATCH",
                    DiagnosticSeverity.ERROR,
                    f"Quiz {quiz.ref} points to a key for question {matched_key.question_ref}.",
                    source_file=quiz.provenance.source_file,
                    entity_ref=quiz.ref,
                    field="answer_key_ref",
                    reference=matched_key.question_ref,
                    remediation="Correct the reciprocal references using the original question/key pairing.",
                )

    practice_by_ref = {
        block.ref: block for block in contract.blocks if isinstance(block, PracticeBlock)
    }
    for block in contract.blocks:
        if (
            isinstance(block, (AnswerKeyBlock, FlashcardBlock))
            and block.source_markdown is None
            and contract.schema_version != "trilhacode.intermediate/1.0"
        ):
            add(
                "SOURCE_MARKDOWN_MISSING",
                DiagnosticSeverity.ERROR,
                f"Contract 1.1 {block.type} must retain its literal source Markdown.",
                source_file=block.provenance.source_file,
                entity_ref=block.ref,
                field="source_markdown",
                remediation="Populate source_markdown from the exact source segment while retaining parsed fields.",
            )
        if isinstance(block, SolutionBlock) and block.practice_ref not in practice_by_ref:
            add(
                "SOLUTION_PRACTICE_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Solution points to missing practice {block.practice_ref}.",
                source_file=block.provenance.source_file,
                entity_ref=block.ref,
                field="practice_ref",
                reference=block.practice_ref,
                remediation="Associate the solution only with its originating practice.",
            )
        if isinstance(block, FeedbackBlock) and block.target_ref not in blocks_by_ref:
            add(
                "FEEDBACK_TARGET_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Feedback target {block.target_ref} does not exist.",
                source_file=block.provenance.source_file,
                entity_ref=block.ref,
                field="target_ref",
                reference=block.target_ref,
                remediation="Reference the existing quiz or practice that this feedback belongs to.",
            )
        if isinstance(block, ChecklistBlock):
            item_refs = [item.ref for item in block.items]
            if len(item_refs) != len(set(item_refs)):
                add(
                    "DUPLICATE_CHECKLIST_ITEM_ID",
                    DiagnosticSeverity.ERROR,
                    "Checklist item references must be unique within the checklist.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="items",
                    remediation="Assign a distinct local reference to each original checklist item.",
                )
            if (
                block.source_markdown is None
                and contract.schema_version != "trilhacode.intermediate/1.0"
            ):
                add(
                    "CHECKLIST_SOURCE_MARKDOWN_MISSING",
                    DiagnosticSeverity.ERROR,
                    "Contract 1.1 checklist must retain its literal source Markdown.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="source_markdown",
                    remediation="Populate source_markdown from the exact source block while retaining parsed checklist items.",
                )
        if (
            isinstance(block, AcceptanceCriteriaBlock)
            and block.body is None
            and contract.schema_version != "trilhacode.intermediate/1.0"
        ):
            add(
                "ACCEPTANCE_SOURCE_BODY_MISSING",
                DiagnosticSeverity.ERROR,
                "Contract 1.1 acceptance criteria must retain their literal source body.",
                source_file=block.provenance.source_file,
                entity_ref=block.ref,
                field="body",
                remediation="Populate body from the exact acceptance block; keep the parsed items as a secondary view.",
            )
        if isinstance(
            block,
            (
                AcceptanceCriteriaBlock,
                CompletionCriteriaBlock,
                ProjectDecisionBlock,
                ProjectScenarioBlock,
                ProjectReviewBlock,
            ),
        ):
            for related_ref in block.related_refs:
                if related_ref not in known_entity_refs:
                    add(
                        "CONTENT_RELATION_NOT_FOUND",
                        DiagnosticSeverity.ERROR,
                        f"Content relation points to missing entity {related_ref}.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="related_refs",
                        reference=related_ref,
                        remediation="Keep only explicit references to entities present in the same contract package.",
                    )
        if isinstance(block, RubricBlock):
            if (
                block.source_markdown is None
                and contract.schema_version != "trilhacode.intermediate/1.0"
            ):
                add(
                    "RUBRIC_SOURCE_MARKDOWN_MISSING",
                    DiagnosticSeverity.ERROR,
                    "Contract 1.1 rubric must retain its literal source Markdown.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="source_markdown",
                    remediation="Populate source_markdown from the exact source block; retain typed dimensions alongside it.",
                )
            targets = block.target_refs or [block.target_ref]
            if len(targets) != len(set(targets)):
                add(
                    "RUBRIC_TARGET_DUPLICATE",
                    DiagnosticSeverity.ERROR,
                    "Rubric target references must be unique.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="target_refs",
                    remediation="Preserve each source target exactly once and do not duplicate its association.",
                )
            if contract.schema_version != "trilhacode.intermediate/1.0":
                if not block.target_refs:
                    add(
                        "RUBRIC_TARGETS_MISSING",
                        DiagnosticSeverity.ERROR,
                        "Contract 1.1 rubric must explicitly represent its complete target list.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="target_refs",
                        remediation="Populate target_refs from explicit source labels; do not infer omitted targets.",
                    )
                elif block.target_refs[0] != block.target_ref:
                    add(
                        "RUBRIC_PRIMARY_TARGET_MISMATCH",
                        DiagnosticSeverity.ERROR,
                        "Legacy primary target_ref must match the first ordered target_refs entry.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="target_ref",
                        reference=block.target_refs[0],
                        remediation="Keep target_ref as the first item for legacy readers and target_refs as the canonical ordered list.",
                    )
            for target_ref in targets:
                if target_ref not in known_owner_refs | set(blocks_by_ref):
                    add(
                        "RUBRIC_TARGET_NOT_FOUND",
                        DiagnosticSeverity.ERROR,
                        f"Rubric target {target_ref} does not exist.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="target_refs" if block.target_refs else "target_ref",
                        reference=target_ref,
                        remediation="Associate the rubric only with source-backed practices, projects, deliveries, or milestones.",
                    )
            if block.scale is None:
                if block.threshold is not None:
                    add(
                        "RUBRIC_THRESHOLD_WITHOUT_SCALE",
                        DiagnosticSeverity.ERROR,
                        "A numeric threshold cannot be validated when the rubric has no numeric scale.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="threshold",
                        remediation="Preserve the source's non-numeric rubric without inventing a threshold.",
                    )
            else:
                if block.scale.minimum >= block.scale.maximum:
                    add(
                        "RUBRIC_SCALE_INVALID",
                        DiagnosticSeverity.ERROR,
                        "Rubric scale minimum must be lower than its maximum.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="scale",
                        remediation="Record the scale endpoints exactly as in the source.",
                    )
                if not block.dimensions:
                    add(
                        "RUBRIC_DIMENSIONS_MISSING",
                        DiagnosticSeverity.ERROR,
                        "A numeric rubric requires at least one dimension.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="dimensions",
                        remediation="Map the original rubric dimensions without adding criteria.",
                    )
                dimension_refs = [dimension.ref for dimension in block.dimensions]
                if len(dimension_refs) != len(set(dimension_refs)):
                    add(
                        "DUPLICATE_RUBRIC_DIMENSION_ID",
                        DiagnosticSeverity.ERROR,
                        "Rubric dimension references must be unique.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="dimensions",
                        remediation="Assign unique stable references to the original dimensions.",
                    )
                minimum_total = sum(block.scale.minimum * item.weight for item in block.dimensions)
                maximum_total = sum(block.scale.maximum * item.weight for item in block.dimensions)
                for dimension in block.dimensions:
                    if dimension.weight <= 0:
                        add(
                            "RUBRIC_WEIGHT_INVALID",
                            DiagnosticSeverity.ERROR,
                            "Rubric dimension weight must be greater than zero.",
                            source_file=block.provenance.source_file,
                            entity_ref=block.ref,
                            field=f"dimensions.{dimension.ref}.weight",
                            remediation="Preserve an existing positive weight or omit weighting when the source has none.",
                        )
                    for descriptor_score in dimension.descriptors:
                        try:
                            numeric_score = int(descriptor_score)
                        except ValueError:
                            add(
                                "RUBRIC_DESCRIPTOR_SCORE_INVALID",
                                DiagnosticSeverity.ERROR,
                                f"Descriptor score {descriptor_score!r} is not an integer.",
                                source_file=block.provenance.source_file,
                                entity_ref=block.ref,
                                field=f"dimensions.{dimension.ref}.descriptors",
                                remediation="Use source score labels or numeric values consistent with the rubric scale.",
                            )
                            continue
                        if not block.scale.minimum <= numeric_score <= block.scale.maximum:
                            add(
                                "RUBRIC_DESCRIPTOR_OUT_OF_RANGE",
                                DiagnosticSeverity.ERROR,
                                f"Descriptor score {numeric_score} falls outside the rubric scale.",
                                source_file=block.provenance.source_file,
                                entity_ref=block.ref,
                                field=f"dimensions.{dimension.ref}.descriptors",
                                remediation="Keep descriptor levels within the original scale endpoints.",
                            )
                if (
                    block.threshold is not None
                    and not minimum_total <= block.threshold <= maximum_total
                ):
                    add(
                        "RUBRIC_THRESHOLD_OUT_OF_RANGE",
                        DiagnosticSeverity.ERROR,
                        f"Threshold {block.threshold} is outside the achievable score range {minimum_total:g}–{maximum_total:g}.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="threshold",
                        remediation="Copy the original threshold and rubric dimensions accurately; do not adjust either to make them fit.",
                    )
        if isinstance(block, AcceptanceCriteriaBlock):
            targets = [
                target_ref
                for target_ref in (
                    block.delivery_ref,
                    block.milestone_ref,
                    block.practice_ref,
                )
                if target_ref is not None
            ]
            if len(targets) != 1:
                add(
                    "ACCEPTANCE_TARGET_INVALID",
                    DiagnosticSeverity.ERROR,
                    "Acceptance criteria must point to exactly one practice, delivery, or formal milestone.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="practice_ref/delivery_ref/milestone_ref",
                    remediation="Preserve exactly one source-backed practice, delivery, or milestone association.",
                )
            elif block.delivery_ref is not None and block.delivery_ref not in delivery_by_ref:
                add(
                    "ACCEPTANCE_DELIVERY_NOT_FOUND",
                    DiagnosticSeverity.ERROR,
                    f"Acceptance criteria point to missing delivery {block.delivery_ref}.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="delivery_ref",
                    reference=block.delivery_ref,
                    remediation="Link the criteria only to a formal delivery present in the source.",
                )
            elif block.milestone_ref is not None and block.milestone_ref not in milestone_by_ref:
                add(
                    "ACCEPTANCE_MILESTONE_NOT_FOUND",
                    DiagnosticSeverity.ERROR,
                    f"Acceptance criteria point to missing milestone {block.milestone_ref}.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="milestone_ref",
                    reference=block.milestone_ref,
                    remediation="Link the criteria only to a formal milestone present in the source.",
                )
            elif block.practice_ref is not None and block.practice_ref not in practice_by_ref:
                add(
                    "ACCEPTANCE_PRACTICE_NOT_FOUND",
                    DiagnosticSeverity.ERROR,
                    f"Acceptance criteria point to missing practice {block.practice_ref}.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="practice_ref",
                    reference=block.practice_ref,
                    remediation="Link practice acceptance only to the exact source-backed practice identified by its source label.",
                )
            elif block.practice_ref is not None:
                target_practice = practice_by_ref[block.practice_ref]
                if block.shared != target_practice.shared:
                    add(
                        "ACCEPTANCE_PRACTICE_SHARING_MISMATCH",
                        DiagnosticSeverity.ERROR,
                        "Practice acceptance and its target practice must use the same shared-context classification.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="shared",
                        reference=target_practice.ref,
                        remediation="Preserve the source-backed shared or exclusive classification of the practice and its acceptance block.",
                    )
        if isinstance(block, ReferenceBlock):
            if block.target_kind == "external":
                parsed = urlsplit(block.url or "")
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    add(
                        "EXTERNAL_REFERENCE_INVALID",
                        DiagnosticSeverity.ERROR,
                        "External references require an absolute HTTP or HTTPS URL.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="url",
                        reference=block.url,
                        remediation="Preserve the source URL or record it as an editorial pending item if no destination is known.",
                    )
            elif block.target_kind == "internal":
                if block.target_ref is None or block.target_ref not in entity_kinds:
                    add(
                        "INTERNAL_REFERENCE_NOT_FOUND",
                        DiagnosticSeverity.ERROR,
                        "Internal reference has no existing destination.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="target_ref",
                        reference=block.target_ref,
                        remediation="Resolve through an approved manifest reference; do not invent a destination.",
                    )
            elif block.target_kind == "obsidian":
                if not block.raw_text:
                    add(
                        "OBSIDIAN_RAW_LINK_MISSING",
                        DiagnosticSeverity.ERROR,
                        "An Obsidian reference must preserve its literal source text.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="raw_text",
                        remediation="Copy the literal wikilink from the source without rewriting it.",
                    )
                if block.target_ref is not None and block.target_ref not in entity_kinds:
                    add(
                        "INTERNAL_REFERENCE_NOT_FOUND",
                        DiagnosticSeverity.ERROR,
                        "Resolved Obsidian target does not exist in the contract.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="target_ref",
                        reference=block.target_ref,
                        remediation="Use a verified destination or leave the wikilink unresolved and documented.",
                    )
                if block.target_ref is None and not block.pending_ref:
                    add(
                        "EDITORIAL_PENDING_REQUIRED",
                        DiagnosticSeverity.ERROR,
                        "Unresolved wikilink requires an explicit editorial pending record.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="pending_ref",
                        remediation="Record the unknown vault root or unresolved destination without inventing a link.",
                    )
            elif block.target_kind == "editorial":
                if not block.raw_text or not block.pending_ref:
                    add(
                        "EDITORIAL_PENDING_REQUIRED",
                        DiagnosticSeverity.ERROR,
                        "Editorial references without a destination require literal text and a pending record.",
                        source_file=block.provenance.source_file,
                        entity_ref=block.ref,
                        field="pending_ref",
                        remediation="Preserve the literal reference and link it to an explicit editorial pending item.",
                    )

    for block in contract.blocks:
        if isinstance(block, AcceptanceCriteriaBlock):
            acceptance_context_ref: str | None
            if block.delivery_ref is not None or block.milestone_ref is not None:
                acceptance_context_ref = block.delivery_ref or block.milestone_ref
            elif block.practice_ref is not None:
                practice = practice_by_ref.get(block.practice_ref)
                acceptance_context_ref = practice.owner_ref if practice else None
            else:
                acceptance_context_ref = None
            if acceptance_context_ref is not None and block.owner_ref != acceptance_context_ref:
                add(
                    "ACCEPTANCE_TARGET_MISMATCH",
                    DiagnosticSeverity.ERROR,
                    "Acceptance criteria owner must match the target's curricular context.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="owner_ref",
                    reference=acceptance_context_ref,
                    remediation="Keep practice acceptance with the practice's context and project acceptance with its delivery or milestone.",
                )

    for project in contract.projects:
        unit = node_by_ref.get(project.unit_ref)
        if unit is None or unit.kind != "submodule":
            add(
                "PROJECT_UNIT_INVALID",
                DiagnosticSeverity.ERROR,
                f"Project unit {project.unit_ref} must reference an existing submodule.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="unit_ref",
                reference=project.unit_ref,
                remediation="Attach the project spec to the source-backed project unit.",
            )
        if not project.has_formal_deliveries and project.deliveries:
            add(
                "PROJECT_DELIVERIES_NOT_IN_SOURCE",
                DiagnosticSeverity.ERROR,
                "Project declares no formal deliveries but contains delivery records.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="deliveries",
                remediation="Keep support topics/checklists as source blocks; do not infer formal milestones.",
            )
        if project.has_formal_deliveries and not project.deliveries:
            add(
                "PROJECT_DELIVERIES_MISSING",
                DiagnosticSeverity.ERROR,
                "Project declares formal deliveries but none are represented.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="deliveries",
                remediation="Map each literal source delivery or mark the project as having no formal deliveries.",
            )
        if not project.has_formal_milestones and project.milestones:
            add(
                "PROJECT_MILESTONES_NOT_IN_SOURCE",
                DiagnosticSeverity.ERROR,
                "Project declares no formal milestones but contains milestone records.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="milestones",
                remediation="Keep only formal milestones that are explicitly present in the source.",
            )
        if project.has_formal_milestones and not project.milestones:
            add(
                "PROJECT_MILESTONES_MISSING",
                DiagnosticSeverity.ERROR,
                "Project declares formal milestones but none are represented.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="milestones",
                remediation="Map each literal source milestone or mark the project as having none.",
            )
        if (
            project.stack_selected is not None
            and project.stack_selected not in project.stack_options
        ):
            add(
                "PROJECT_STACK_INVALID",
                DiagnosticSeverity.ERROR,
                "Selected stack is not one of the source-backed project options.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="stack_selected",
                reference=project.stack_selected,
                remediation="Preserve the available options and leave selection unset unless the source records a choice.",
            )
        if len(project.stack_options) != len(set(project.stack_options)):
            add(
                "PROJECT_STACK_OPTION_DUPLICATE",
                DiagnosticSeverity.ERROR,
                "Project stack options contain duplicates.",
                source_file=project.provenance.source_file,
                entity_ref=project.ref,
                field="stack_options",
                remediation="List each source-backed option once.",
            )
        project_step_orders: dict[tuple[str, int], tuple[str, str | None]] = {}
        project_steps_for_order: list[ProjectDelivery | ProjectMilestone] = [
            *project.deliveries,
            *project.milestones,
        ]
        for project_step in project_steps_for_order:
            _duplicate_order(
                diagnostics,
                project_step_orders,
                project.ref,
                project_step.order,
                project_step.ref,
                project_step.provenance.source_file,
                "order",
            )
            if (
                project_step.body is None
                and contract.schema_version != "trilhacode.intermediate/1.0"
            ):
                add(
                    "PROJECT_STEP_BODY_MISSING",
                    DiagnosticSeverity.ERROR,
                    "Contract 1.1 project steps must retain their literal source body.",
                    source_file=project_step.provenance.source_file,
                    entity_ref=project_step.ref,
                    field="body",
                    remediation="Store the exact Markdown body on the delivery or milestone itself; do not convert it to a generic practice block.",
                )
        variant_orders: set[int] = set()
        for variant in project.variants:
            if variant.order in variant_orders:
                add(
                    "PROJECT_VARIANT_ORDER_DUPLICATE",
                    DiagnosticSeverity.ERROR,
                    f"Project variant order {variant.order} is duplicated.",
                    source_file=variant.provenance.source_file,
                    entity_ref=variant.ref,
                    field="order",
                    remediation="Retain the explicit source order with a unique position for each project variation.",
                )
            variant_orders.add(variant.order)
            if (
                variant.stack_option is not None
                and variant.stack_option not in project.stack_options
            ):
                add(
                    "PROJECT_VARIANT_STACK_INVALID",
                    DiagnosticSeverity.ERROR,
                    "Project variant refers to a stack option not listed by its project.",
                    source_file=variant.provenance.source_file,
                    entity_ref=variant.ref,
                    field="stack_option",
                    reference=variant.stack_option,
                    remediation="Preserve only source-backed stack alternatives and keep an unselected option unset.",
                )
            for delivery_ref in variant.delivery_refs:
                if delivery_ref not in {delivery.ref for delivery in project.deliveries}:
                    add(
                        "PROJECT_VARIANT_DELIVERY_NOT_FOUND",
                        DiagnosticSeverity.ERROR,
                        f"Project variant points to missing delivery {delivery_ref}.",
                        source_file=variant.provenance.source_file,
                        entity_ref=variant.ref,
                        field="delivery_refs",
                        reference=delivery_ref,
                        remediation="Associate a variant only with deliveries belonging to the same project.",
                    )
        for rubric_ref in project.rubric_refs:
            rubric = blocks_by_ref.get(rubric_ref)
            if not isinstance(rubric, RubricBlock) or project.ref not in (
                rubric.target_refs or [rubric.target_ref]
            ):
                add(
                    "PROJECT_RUBRIC_REFERENCE_INVALID",
                    DiagnosticSeverity.ERROR,
                    f"Rubric {rubric_ref} is not a rubric targeted at project {project.ref}.",
                    source_file=project.provenance.source_file,
                    entity_ref=project.ref,
                    field="rubric_refs",
                    reference=rubric_ref,
                    remediation="Associate only the original rubric with its project or delivery.",
                )
        for checklist_ref in project.checklist_refs:
            checklist = blocks_by_ref.get(checklist_ref)
            if not isinstance(checklist, ChecklistBlock) or checklist.owner_ref != project.ref:
                add(
                    "PROJECT_CHECKLIST_REFERENCE_INVALID",
                    DiagnosticSeverity.ERROR,
                    f"Checklist {checklist_ref} is not attached to project {project.ref}.",
                    source_file=project.provenance.source_file,
                    entity_ref=project.ref,
                    field="checklist_refs",
                    reference=checklist_ref,
                    remediation="Link the existing checklist to its source project without converting it to an acceptance rubric.",
                )
        project_steps: list[ProjectDelivery | ProjectMilestone] = [
            *project.deliveries,
            *project.milestones,
        ]
        for delivery in project_steps:
            step_kind = "delivery" if isinstance(delivery, ProjectDelivery) else "milestone"
            references: list[tuple[str, type[BaseModel], str]] = []
            references.extend(
                (ref, AcceptanceCriteriaBlock, "acceptance_refs")
                for ref in delivery.acceptance_refs
            )
            references.extend(
                (ref, ChecklistBlock, "checklist_refs") for ref in delivery.checklist_refs
            )
            references.extend((ref, RubricBlock, "rubric_refs") for ref in delivery.rubric_refs)
            for ref, expected_type, field in references:
                referenced_block = blocks_by_ref.get(ref)
                if not isinstance(referenced_block, expected_type):
                    add(
                        "PROJECT_STEP_BLOCK_REFERENCE_INVALID",
                        DiagnosticSeverity.ERROR,
                        f"Project {step_kind} references missing or incorrectly typed block {ref}.",
                        source_file=delivery.provenance.source_file,
                        entity_ref=delivery.ref,
                        field=field,
                        reference=ref,
                        remediation="Keep acceptance, checklist, and rubric blocks linked to the correct original delivery.",
                    )
                elif isinstance(referenced_block, AcceptanceCriteriaBlock) and (
                    referenced_block.delivery_ref != delivery.ref
                    if step_kind == "delivery"
                    else referenced_block.milestone_ref != delivery.ref
                ):
                    add(
                        "ACCEPTANCE_TARGET_MISMATCH",
                        DiagnosticSeverity.ERROR,
                        f"Acceptance block {ref} targets another project {step_kind}.",
                        source_file=referenced_block.provenance.source_file,
                        entity_ref=referenced_block.ref,
                        field="delivery_ref" if step_kind == "delivery" else "milestone_ref",
                        reference=delivery.ref,
                        remediation="Restore the literal project-step-to-acceptance association from the source.",
                    )
                elif isinstance(referenced_block, RubricBlock) and delivery.ref not in (
                    referenced_block.target_refs or [referenced_block.target_ref]
                ):
                    add(
                        "RUBRIC_TARGET_MISMATCH",
                        DiagnosticSeverity.ERROR,
                        f"Rubric {ref} does not list this project {step_kind} as a target.",
                        source_file=referenced_block.provenance.source_file,
                        entity_ref=referenced_block.ref,
                        field="target_refs",
                        reference=delivery.ref,
                        remediation="Keep project step rubric references consistent with the rubric's explicit target list.",
                    )
            for content_ref in delivery.content_refs:
                content_block = blocks_by_ref.get(content_ref)
                if content_block is None or content_block.owner_ref != delivery.ref:
                    add(
                        "DELIVERY_CONTENT_REFERENCE_INVALID",
                        DiagnosticSeverity.ERROR,
                        f"Delivery content {content_ref} is missing or owned by another entity.",
                        source_file=delivery.provenance.source_file,
                        entity_ref=delivery.ref,
                        field="content_refs",
                        reference=content_ref,
                        remediation="Attach only source-backed content to the delivery that contains it.",
                    )

    for block in contract.blocks:
        if isinstance(block, ReferenceBlock) and block.pending_ref is not None:
            if block.pending_ref not in {pending.ref for pending in contract.editorial_pendings}:
                add(
                    "EDITORIAL_PENDING_NOT_FOUND",
                    DiagnosticSeverity.ERROR,
                    f"Pending reference {block.pending_ref} does not exist.",
                    source_file=block.provenance.source_file,
                    entity_ref=block.ref,
                    field="pending_ref",
                    reference=block.pending_ref,
                    remediation="Add the corresponding documented pending item; do not substitute an invented target.",
                )

    for placement in contract.shared_placements:
        shared_block = blocks_by_ref.get(placement.block_ref)
        if shared_block is None or not shared_block.shared:
            add(
                "SHARED_BLOCK_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Placement points to missing or non-shared block {placement.block_ref}.",
                source_file=placement.provenance.source_file,
                entity_ref=placement.ref,
                field="block_ref",
                reference=placement.block_ref,
                remediation="Reference one canonical block marked shared; do not copy its content into the placement.",
            )
            continue
        subject = node_by_ref.get(placement.subject_ref)
        if subject is None or subject.kind != "topic":
            add(
                "SHARED_SUBJECT_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Placement consumer {placement.subject_ref} is not an existing topic.",
                source_file=placement.provenance.source_file,
                entity_ref=placement.ref,
                field="subject_ref",
                reference=placement.subject_ref,
                remediation="Place shared content only in source-backed subject nodes.",
            )
        placements_for_block = shared_placements_by_block.setdefault(placement.block_ref, [])
        if any(item.subject_ref == placement.subject_ref for item in placements_for_block):
            add(
                "DUPLICATE_PLACEMENT",
                DiagnosticSeverity.ERROR,
                f"Block {placement.block_ref} is placed more than once in subject {placement.subject_ref}.",
                source_file=placement.provenance.source_file,
                entity_ref=placement.ref,
                field="subject_ref",
                reference=placement.subject_ref,
                remediation="Keep one placement per canonical block and subject.",
            )
        else:
            placements_for_block.append(placement)
        _duplicate_order(
            diagnostics,
            display_orders,
            placement.subject_ref,
            placement.order,
            placement.ref,
            placement.provenance.source_file,
            "order",
        )
        if placement.progress_scope == "undecided":
            add(
                "SHARED_PROGRESS_SCOPE_UNDECIDED",
                DiagnosticSeverity.INFO,
                "Progress behavior for this shared placement remains a product decision.",
                source_file=placement.provenance.source_file,
                entity_ref=placement.ref,
                field="progress_scope",
                reference=placement.block_ref,
                remediation="Choose per-context or shared progress only after an explicit product decision.",
            )
    for canonical_block in contract.blocks:
        if canonical_block.shared and not shared_placements_by_block.get(canonical_block.ref):
            add(
                "SHARED_BLOCK_WITHOUT_PLACEMENT",
                DiagnosticSeverity.ERROR,
                "Canonical shared block has no subject placements.",
                source_file=canonical_block.provenance.source_file,
                entity_ref=canonical_block.ref,
                field="shared",
                remediation="Add the source-approved consumer placements or do not mark this block shared.",
            )

    relation_graph: dict[str, list[str]] = {}
    for relation in contract.relations:
        if relation.source_ref not in node_by_ref or relation.target_ref not in node_by_ref:
            missing = (
                relation.source_ref
                if relation.source_ref not in node_by_ref
                else relation.target_ref
            )
            add(
                "RELATION_TARGET_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Relation endpoint {missing} does not exist as a curriculum node.",
                source_file=relation.provenance.source_file,
                entity_ref=relation.ref,
                field="source_ref" if missing == relation.source_ref else "target_ref",
                reference=missing,
                remediation="Use existing node references from the manifest.",
            )
        if relation.source_ref == relation.target_ref:
            add(
                "RELATION_SELF_REFERENCE",
                DiagnosticSeverity.ERROR,
                "A curriculum relation cannot point from a node to itself.",
                source_file=relation.provenance.source_file,
                entity_ref=relation.ref,
                field="target_ref",
                reference=relation.target_ref,
                remediation="Correct the relation endpoints from the original connections map.",
            )
        if (
            relation.kind == "prerequisite"
            and relation.source_ref in node_by_ref
            and relation.target_ref in node_by_ref
        ):
            relation_graph.setdefault(relation.source_ref, []).append(relation.target_ref)
    for cycle in _find_cycles(relation_graph):
        add(
            "PREREQUISITE_CYCLE",
            DiagnosticSeverity.ERROR,
            "Prerequisite relations contain a cycle: " + " → ".join(cycle),
            entity_ref=cycle[0],
            field="relations",
            reference=" → ".join(cycle),
            remediation="Review the source ordering and remove only the relation that creates the cycle.",
        )

    for pending in contract.editorial_pendings:
        if pending.source_file != pending.provenance.source_file:
            add(
                "PENDING_PROVENANCE_MISMATCH",
                DiagnosticSeverity.ERROR,
                "Editorial pending path differs from its provenance path.",
                source_file=pending.source_file,
                entity_ref=pending.ref,
                field="provenance.source_file",
                reference=pending.provenance.source_file,
                remediation="Keep one exact repository-relative source path in both pending metadata fields.",
            )
        if pending.entity_ref is not None and pending.entity_ref not in entity_kinds:
            add(
                "PENDING_ENTITY_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Editorial pending entity {pending.entity_ref} does not exist.",
                source_file=pending.source_file,
                entity_ref=pending.ref,
                field="entity_ref",
                reference=pending.entity_ref,
                remediation="Associate the pending note with a source-backed entity or leave entity_ref unset.",
            )
        if pending.destination_ref is not None and pending.destination_ref not in entity_kinds:
            add(
                "PENDING_DESTINATION_NOT_FOUND",
                DiagnosticSeverity.ERROR,
                f"Editorial pending destination {pending.destination_ref} does not exist.",
                source_file=pending.source_file,
                entity_ref=pending.ref,
                field="destination_ref",
                reference=pending.destination_ref,
                remediation="Use only a verified destination; unresolved references remain null.",
            )
        if pending.blocking:
            add(
                "EDITORIAL_PENDING_BLOCKING",
                DiagnosticSeverity.ERROR,
                pending.note,
                source_file=pending.source_file,
                entity_ref=pending.entity_ref or pending.ref,
                field="destination_ref",
                reference=pending.reference_text,
                remediation="Resolve through an editorial decision; the validator will not invent a destination.",
            )
        else:
            severity = (
                DiagnosticSeverity.WARNING
                if pending.kind == "obsidian_vault_root_unknown"
                else DiagnosticSeverity.INFO
            )
            code = (
                "OBSIDIAN_ROOT_UNCONFIRMED"
                if pending.kind == "obsidian_vault_root_unknown"
                else "EDITORIAL_PENDING_RECORDED"
            )
            add(
                code,
                severity,
                pending.note,
                source_file=pending.source_file,
                entity_ref=pending.entity_ref or pending.ref,
                field="destination_ref",
                reference=pending.reference_text,
                remediation="Preserve the original reference and wait for an approved destination or editorial decision.",
            )
    if not contract.vault_root_confirmed and not any(
        pending.kind == "obsidian_vault_root_unknown" for pending in contract.editorial_pendings
    ):
        add(
            "OBSIDIAN_ROOT_UNCONFIRMED",
            DiagnosticSeverity.WARNING,
            "The Obsidian vault root has not been confirmed.",
            field="vault_root_confirmed",
            remediation="Keep wikilinks literal until the vault root is confirmed; do not rewrite them.",
        )

    return tuple(diagnostics)


def validate_contract(value: IntermediateContract | Mapping[str, Any]) -> ValidationReport:
    """Parse and semantically validate a package without file or database access."""
    try:
        contract = (
            value
            if isinstance(value, IntermediateContract)
            else IntermediateContract.model_validate(value)
        )
    except ValidationError as error:
        raw_value = dict(value) if isinstance(value, Mapping) else value
        return ValidationReport(None, _schema_diagnostics(error, raw_value))
    return ValidationReport(contract, _semantic_diagnostics(contract))


def verify_source_hash(
    provenance: SourceProvenance,
    source_bytes: bytes,
    *,
    entity_ref: str | None = None,
) -> tuple[Diagnostic, ...]:
    """Verify supplied bytes against recorded provenance; does not read paths or write files."""
    actual = hashlib.sha256(source_bytes).hexdigest()
    if not SHA256_PATTERN.fullmatch(provenance.source_sha256):
        return (
            Diagnostic(
                code="INVALID_SHA256",
                severity=DiagnosticSeverity.ERROR,
                source_file=provenance.source_file,
                entity_ref=entity_ref,
                field="provenance.source_sha256",
                message="Recorded source digest is not a lowercase SHA-256 value.",
                remediation="Compute SHA-256 from the exact source bytes before constructing the contract.",
            ),
        )
    if actual != provenance.source_sha256:
        return (
            Diagnostic(
                code="SOURCE_HASH_MISMATCH",
                severity=DiagnosticSeverity.ERROR,
                source_file=provenance.source_file,
                entity_ref=entity_ref,
                field="provenance.source_sha256",
                reference=actual,
                message="Source bytes do not match the recorded SHA-256.",
                remediation="Recheck the selected source segment and its manifest mapping; do not overwrite either automatically.",
            ),
        )
    return ()


class ChangeState(StrEnum):
    NEW = "new"
    UNCHANGED = "unchanged"
    MODIFIED = "modified"
    CONFLICT = "conflict"
    ABSENT = "absent"


class BaselineFingerprint(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    last_applied_sha256: str
    current_sha256: str


class ChangeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    ref: str
    state: ChangeState
    candidate_sha256: str | None
    last_applied_sha256: str | None
    current_sha256: str | None
    deletion_authorized: Literal[False] = False


def classify_changes(
    candidate_hashes: Mapping[str, str],
    baseline: Mapping[str, BaselineFingerprint],
) -> tuple[ChangeRecord, ...]:
    """Classify supplied snapshots only; performs no Mongo lookup or automatic deletion."""
    records: list[ChangeRecord] = []
    for ref in sorted(set(candidate_hashes) | set(baseline)):
        candidate_hash = candidate_hashes.get(ref)
        previous = baseline.get(ref)
        if candidate_hash is None:
            records.append(
                ChangeRecord(
                    ref=ref,
                    state=ChangeState.ABSENT,
                    candidate_sha256=None,
                    last_applied_sha256=previous.last_applied_sha256 if previous else None,
                    current_sha256=previous.current_sha256 if previous else None,
                    deletion_authorized=False,
                )
            )
            continue
        if not SHA256_PATTERN.fullmatch(candidate_hash):
            raise ValueError(f"candidate hash for {ref} is not a lowercase SHA-256")
        if previous is None:
            state = ChangeState.NEW
        elif not SHA256_PATTERN.fullmatch(
            previous.last_applied_sha256
        ) or not SHA256_PATTERN.fullmatch(previous.current_sha256):
            raise ValueError(f"baseline hash for {ref} is not a lowercase SHA-256")
        elif previous.current_sha256 != previous.last_applied_sha256:
            state = ChangeState.CONFLICT
        elif candidate_hash == previous.last_applied_sha256:
            state = ChangeState.UNCHANGED
        else:
            state = ChangeState.MODIFIED
        records.append(
            ChangeRecord(
                ref=ref,
                state=state,
                candidate_sha256=candidate_hash,
                last_applied_sha256=previous.last_applied_sha256 if previous else None,
                current_sha256=previous.current_sha256 if previous else None,
                deletion_authorized=False,
            )
        )
    return tuple(records)
