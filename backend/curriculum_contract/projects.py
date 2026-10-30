"""Offline, read-only projections of source-backed curricular projects.

This module reuses the intermediate contract's ProjectSpec, delivery, milestone,
variant, and typed block models. It does not create operational project state or
perform filesystem, database, API, publication, submission, grading, or progress
writes.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .models import (
    AcceptanceCriteriaBlock,
    ChecklistBlock,
    ContentBlock,
    IntermediateContract,
    ProjectDelivery,
    ProjectMilestone,
    ProjectSpec,
    RubricBlock,
)
from .validation import Diagnostic, DiagnosticSeverity, validate_contract


class ProjectProjectionValidationError(ValueError):
    """A project projection validation failure without source body content."""

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        self.diagnostics = diagnostics
        codes = sorted({item.code for item in diagnostics})
        super().__init__("Project projection is invalid: " + ", ".join(codes))


class ProjectReferenceError(ValueError):
    """A requested project or owner unit is missing or has the wrong kind."""

    def __init__(self, code: str, reference: str) -> None:
        self.code = code
        self.reference = reference
        super().__init__(f"{code}: {reference}")


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError("Project projection contains a non-JSON value")


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class ProjectInternalProjection:
    """Immutable full-fidelity snapshot for audit/editorial tooling only."""

    contract_schema_version: str
    source_manifest: Mapping[str, Any]
    project: Mapping[str, Any]
    owner_unit: Mapping[str, Any]
    referenced_blocks: Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True)
class PublicProjectStep:
    """Source-backed instructional fields allowlisted for a project step."""

    ref: str
    title: str
    body: str | None
    order: int


@dataclass(frozen=True)
class PublicProjectProjection:
    """Conservative presentation view; contains no assessment attachments."""

    project_ref: str
    unit_ref: str
    title: str
    scope: str
    deliveries: tuple[PublicProjectStep, ...]
    milestones: tuple[PublicProjectStep, ...]


@dataclass(frozen=True)
class ProjectIndex:
    """Read-only project lookup built from one or more validated contracts."""

    _projects: Mapping[str, ProjectInternalProjection]
    _projects_by_unit: Mapping[str, tuple[str, ...]]
    _submodule_refs: frozenset[str]

    @property
    def project_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._projects))

    @property
    def project_count(self) -> int:
        return len(self._projects)

    def for_project(self, project_ref: str) -> ProjectInternalProjection:
        projection = self._projects.get(project_ref)
        if projection is None:
            raise ProjectReferenceError("PROJECT_NOT_FOUND", project_ref)
        return projection

    def for_unit(self, unit_ref: str) -> tuple[ProjectInternalProjection, ...]:
        if unit_ref not in self._submodule_refs:
            raise ProjectReferenceError("PROJECT_UNIT_NOT_SUBMODULE", unit_ref)
        return tuple(self._projects[ref] for ref in self._projects_by_unit.get(unit_ref, ()))


def _issue(
    code: str,
    *,
    source_file: str | None,
    entity_ref: str,
    field: str,
    reference: str | None = None,
    message: str,
    remediation: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        source_file=source_file,
        entity_ref=entity_ref,
        field=field,
        reference=reference,
        message=message,
        remediation=remediation,
    )


def _as_contracts(
    value: IntermediateContract
    | Mapping[str, Any]
    | Iterable[IntermediateContract | Mapping[str, Any]],
) -> tuple[IntermediateContract, ...]:
    if isinstance(value, (IntermediateContract, Mapping)):
        candidates: tuple[IntermediateContract | Mapping[str, Any], ...] = (value,)
    else:
        candidates = tuple(value)

    parsed_contracts: list[IntermediateContract] = []
    diagnostics: list[Diagnostic] = []
    for candidate in candidates:
        report = validate_contract(candidate)
        diagnostics.extend(
            item for item in report.diagnostics if item.severity == DiagnosticSeverity.ERROR
        )
        if report.contract is not None and report.ok:
            # The index is a snapshot: subsequent caller mutations cannot alter it.
            parsed_contracts.append(
                IntermediateContract.model_validate(report.contract.model_dump(mode="json"))
            )
    if diagnostics:
        raise ProjectProjectionValidationError(tuple(diagnostics))
    return tuple(parsed_contracts)


def _project_steps(project: ProjectSpec) -> list[ProjectDelivery | ProjectMilestone]:
    steps: list[ProjectDelivery | ProjectMilestone] = list(project.deliveries)
    steps.extend(project.milestones)
    return steps


def _entity_refs(contract: IntermediateContract) -> Iterable[tuple[str, str, str]]:
    for collection_name in (
        "nodes",
        "blocks",
        "relations",
        "shared_placements",
        "projects",
        "editorial_pendings",
    ):
        for item in getattr(contract, collection_name):
            yield item.ref, collection_name, item.provenance.source_file
    for project in contract.projects:
        for collection_name in ("deliveries", "milestones", "variants"):
            for item in getattr(project, collection_name):
                yield item.ref, collection_name, item.provenance.source_file


def _project_block_refs(
    project: ProjectSpec,
) -> Iterable[tuple[str, type[Any] | None, str, str]]:
    """Yield (ref, expected type, role, owning project-step ref) records."""
    for ref in project.checklist_refs:
        yield ref, ChecklistBlock, "project_checklist", project.ref
    for ref in project.rubric_refs:
        yield ref, RubricBlock, "project_rubric", project.ref
    for step in _project_steps(project):
        for ref in step.acceptance_refs:
            yield ref, AcceptanceCriteriaBlock, "step_acceptance", step.ref
        for ref in step.checklist_refs:
            yield ref, ChecklistBlock, "step_checklist", step.ref
        for ref in step.rubric_refs:
            yield ref, RubricBlock, "step_rubric", step.ref
        for ref in step.content_refs:
            # content_refs is deliberately the contract's generic typed-content
            # relation; the concrete ContentBlock subtype remains unchanged.
            yield ref, None, "step_content", step.ref


def _reference_issues(
    project: ProjectSpec, blocks_by_ref: Mapping[str, ContentBlock]
) -> tuple[Diagnostic, ...]:
    issues: list[Diagnostic] = []
    lists: list[tuple[str, list[str], str]] = [
        ("checklist_refs", project.checklist_refs, "project_checklist"),
        ("rubric_refs", project.rubric_refs, "project_rubric"),
    ]
    steps = _project_steps(project)
    for step in steps:
        lists.extend(
            (
                (f"{step.ref}.acceptance_refs", step.acceptance_refs, "step_acceptance"),
                (f"{step.ref}.checklist_refs", step.checklist_refs, "step_checklist"),
                (f"{step.ref}.rubric_refs", step.rubric_refs, "step_rubric"),
                (f"{step.ref}.content_refs", step.content_refs, "step_content"),
            )
        )

    for field, refs, role in lists:
        if len(refs) != len(set(refs)):
            issues.append(
                _issue(
                    "PROJECT_REFERENCE_DUPLICATE",
                    source_file=project.provenance.source_file,
                    entity_ref=project.ref,
                    field=field,
                    message="A project reference list contains a duplicate block identity.",
                    remediation="Retain each source-backed block reference once in its role list.",
                )
            )

    step_by_ref: dict[str, ProjectDelivery | ProjectMilestone] = {step.ref: step for step in steps}
    for ref, expected_type, role, owner_ref in _project_block_refs(project):
        block = blocks_by_ref.get(ref)
        if block is None:
            issues.append(
                _issue(
                    "PROJECT_BLOCK_REFERENCE_NOT_FOUND",
                    source_file=project.provenance.source_file,
                    entity_ref=project.ref,
                    field=role,
                    reference=ref,
                    message="A project reference points to a block absent from its contract.",
                    remediation="Keep the original reference unresolved or correct it only from verified source evidence.",
                )
            )
            continue
        if expected_type is not None and not isinstance(block, expected_type):
            issues.append(
                _issue(
                    "PROJECT_BLOCK_REFERENCE_TYPE_MISMATCH",
                    source_file=project.provenance.source_file,
                    entity_ref=project.ref,
                    field=role,
                    reference=ref,
                    message="A project reference targets a block of an incompatible typed role.",
                    remediation="Use only the typed block required by the original reference role.",
                )
            )
            continue

        if role in {"project_checklist", "step_checklist", "step_content"}:
            if block.owner_ref != owner_ref:
                issues.append(
                    _issue(
                        "PROJECT_BLOCK_OWNER_MISMATCH",
                        source_file=project.provenance.source_file,
                        entity_ref=project.ref,
                        field=role,
                        reference=ref,
                        message="A referenced project block is owned by a different curricular entity.",
                        remediation="Preserve the source-backed owner and reference association; do not reassign automatically.",
                    )
                )
        elif role == "project_rubric":
            rubric = block
            assert isinstance(rubric, RubricBlock)
            targets = rubric.target_refs or [rubric.target_ref]
            if project.ref not in targets:
                issues.append(
                    _issue(
                        "PROJECT_RUBRIC_TARGET_MISMATCH",
                        source_file=project.provenance.source_file,
                        entity_ref=project.ref,
                        field=role,
                        reference=ref,
                        message="A project-level rubric does not declare this project as a target.",
                        remediation="Preserve only explicit source-backed rubric targets.",
                    )
                )
        elif role == "step_acceptance":
            acceptance = block
            assert isinstance(acceptance, AcceptanceCriteriaBlock)
            step = step_by_ref[owner_ref]
            target_ref = (
                acceptance.delivery_ref
                if isinstance(step, ProjectDelivery)
                else acceptance.milestone_ref
            )
            if target_ref != step.ref or acceptance.owner_ref != step.ref:
                issues.append(
                    _issue(
                        "PROJECT_ACCEPTANCE_TARGET_MISMATCH",
                        source_file=project.provenance.source_file,
                        entity_ref=project.ref,
                        field=role,
                        reference=ref,
                        message="Acceptance criteria do not target the referencing project step.",
                        remediation="Keep acceptance criteria attached only to the delivery or milestone named by the source.",
                    )
                )
        elif role == "step_rubric":
            rubric = block
            assert isinstance(rubric, RubricBlock)
            targets = rubric.target_refs or [rubric.target_ref]
            if owner_ref not in targets:
                issues.append(
                    _issue(
                        "PROJECT_STEP_RUBRIC_TARGET_MISMATCH",
                        source_file=project.provenance.source_file,
                        entity_ref=project.ref,
                        field=role,
                        reference=ref,
                        message="A project-step rubric does not declare the referencing step as a target.",
                        remediation="Preserve only explicit source-backed rubric targets.",
                    )
                )

    return tuple(issues)


def _sorted_project_dump(project: ProjectSpec) -> dict[str, Any]:
    payload = project.model_dump(mode="json")
    for field in ("deliveries", "milestones", "variants"):
        payload[field] = sorted(payload[field], key=lambda item: (item["order"], item["ref"]))
    return payload


def build_project_index(
    contracts: IntermediateContract
    | Mapping[str, Any]
    | Iterable[IntermediateContract | Mapping[str, Any]],
) -> ProjectIndex:
    """Validate and snapshot project data from one or more phase contracts."""
    parsed_contracts = _as_contracts(contracts)
    global_refs: dict[str, tuple[str, str]] = {}
    global_issues: list[Diagnostic] = []
    for contract in parsed_contracts:
        for ref, kind, source_file in _entity_refs(contract):
            if ref in global_refs:
                first_kind, first_source = global_refs[ref]
                global_issues.append(
                    _issue(
                        "PROJECT_PACKAGE_ENTITY_ID_DUPLICATE",
                        source_file=source_file,
                        entity_ref=ref,
                        field="ref",
                        reference=first_source,
                        message=f"An entity identity is duplicated across the supplied contracts ({first_kind}/{kind}).",
                        remediation="Use the bundle's existing globally unique curricular identities; do not generate replacements here.",
                    )
                )
            else:
                global_refs[ref] = (kind, source_file)
    if global_issues:
        raise ProjectProjectionValidationError(tuple(global_issues))

    projections: dict[str, ProjectInternalProjection] = {}
    projects_by_unit: dict[str, list[str]] = {}
    submodule_refs: set[str] = set()
    for contract in parsed_contracts:
        nodes = {node.ref: node for node in contract.nodes}
        blocks = {block.ref: block for block in contract.blocks}
        for node in contract.nodes:
            if node.kind == "submodule":
                submodule_refs.add(node.ref)
        for project in contract.projects:
            unit = nodes.get(project.unit_ref)
            if unit is None or unit.kind != "submodule":
                raise ProjectProjectionValidationError(
                    (
                        _issue(
                            "PROJECT_UNIT_NOT_SUBMODULE",
                            source_file=project.provenance.source_file,
                            entity_ref=project.ref,
                            field="unit_ref",
                            reference=project.unit_ref,
                            message="The project owner must be an existing submodule node.",
                            remediation="Keep the source-backed project-to-unit relation; do not create a substitute node.",
                        ),
                    )
                )

            reference_issues = _reference_issues(project, blocks)
            if reference_issues:
                raise ProjectProjectionValidationError(reference_issues)

            referenced_refs = sorted({item[0] for item in _project_block_refs(project)})
            referenced_blocks = {
                ref: _freeze_json(blocks[ref].model_dump(mode="json")) for ref in referenced_refs
            }
            snapshot = ProjectInternalProjection(
                contract_schema_version=contract.schema_version,
                source_manifest=_freeze_json(contract.source.model_dump(mode="json")),
                project=_freeze_json(_sorted_project_dump(project)),
                owner_unit=_freeze_json(unit.model_dump(mode="json")),
                referenced_blocks=MappingProxyType(referenced_blocks),
            )
            if project.ref in projections:
                raise ProjectProjectionValidationError(
                    (
                        _issue(
                            "PROJECT_ID_DUPLICATE",
                            source_file=project.provenance.source_file,
                            entity_ref=project.ref,
                            field="ref",
                            message="A project identity occurs more than once in the supplied contracts.",
                            remediation="Retain one source-backed project record per stable identity.",
                        ),
                    )
                )
            projections[project.ref] = snapshot
            projects_by_unit.setdefault(project.unit_ref, []).append(project.ref)

    frozen_by_unit = {
        unit_ref: tuple(sorted(project_refs)) for unit_ref, project_refs in projects_by_unit.items()
    }
    return ProjectIndex(
        _projects=MappingProxyType(projections),
        _projects_by_unit=MappingProxyType(frozen_by_unit),
        _submodule_refs=frozenset(submodule_refs),
    )


def internal_project_payload(projection: ProjectInternalProjection) -> dict[str, Any]:
    """Return full source data for internal audit; never use as a student payload."""
    return {
        "contract_schema_version": projection.contract_schema_version,
        "source_manifest": _thaw_json(projection.source_manifest),
        "project": _thaw_json(projection.project),
        "owner_unit": _thaw_json(projection.owner_unit),
        "referenced_blocks": [
            _thaw_json(projection.referenced_blocks[ref])
            for ref in sorted(projection.referenced_blocks)
        ],
    }


def serialize_internal_project(projection: ProjectInternalProjection) -> str:
    """Serialize a full-fidelity internal snapshot deterministically."""
    return json.dumps(
        internal_project_payload(projection),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def serialize_project_index(index: ProjectIndex) -> str:
    """Serialize all project snapshots by stable reference for offline auditing."""
    return json.dumps(
        {
            "projects": [
                internal_project_payload(index.for_project(ref)) for ref in index.project_refs
            ]
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _public_step(value: Mapping[str, Any]) -> PublicProjectStep:
    # This positive allowlist intentionally excludes attached assessment blocks,
    # source metadata, editorial state, provenance, and any learner state.
    return PublicProjectStep(
        ref=str(value["ref"]),
        title=str(value["title"]),
        body=value.get("body"),
        order=int(value["order"]),
    )


def public_project_projection(
    projection: ProjectInternalProjection,
) -> PublicProjectProjection:
    """Build a conservative presentation view from explicitly selected fields."""
    project = projection.project
    deliveries = tuple(_public_step(item) for item in project["deliveries"])
    milestones = tuple(_public_step(item) for item in project["milestones"])
    return PublicProjectProjection(
        project_ref=str(project["ref"]),
        unit_ref=str(project["unit_ref"]),
        title=str(project["title"]),
        scope=str(project["scope"]),
        deliveries=deliveries,
        milestones=milestones,
    )


def public_project_payload(projection: PublicProjectProjection) -> dict[str, Any]:
    """Return only the allowlisted title/scope and literal instructional steps."""
    return {
        "project_ref": projection.project_ref,
        "unit_ref": projection.unit_ref,
        "title": projection.title,
        "scope": projection.scope,
        "deliveries": [
            {"ref": item.ref, "title": item.title, "body": item.body, "order": item.order}
            for item in projection.deliveries
        ],
        "milestones": [
            {"ref": item.ref, "title": item.title, "body": item.body, "order": item.order}
            for item in projection.milestones
        ],
    }


def serialize_public_project(projection: PublicProjectProjection) -> str:
    """Serialize the conservative public view without generic model serialization."""
    return json.dumps(
        public_project_payload(projection),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
