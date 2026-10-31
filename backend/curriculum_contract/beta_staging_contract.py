"""Strict package and record contracts for disconnected Beta 5 staging."""

from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from curriculum_contract.beta_completion_criteria import (
    CompletionRule,
    CriterionKind,
    EvaluationMode,
)
from curriculum_contract.beta_curricular_metadata import (
    CurricularReference,
    CurricularRelation,
    RelationScope,
)
from curriculum_contract.beta_project_contract import (
    ProjectPackage,
    project_package_from_converted_unit,
)
from curriculum_contract.beta_protected_content import DataClassification
from curriculum_contract.experimental_beta_first_phase_converter import (
    CONTRACT_VERSION as BETA4_CONTRACT_VERSION,
)
from curriculum_contract.experimental_beta_first_phase_converter import (
    CONVERTER_VERSION as BETA4_CONVERTER_VERSION,
)
from curriculum_contract.experimental_beta_first_phase_converter import (
    FirstPhaseBatch,
)


class StageState(StrEnum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    FAILED = "FAILED"
    RECOVERABLE = "RECOVERABLE"
    QUARANTINED = "QUARANTINED"


class StagedRecordKind(StrEnum):
    UNIT = "unit"
    THEORY_SEGMENT = "theory_segment"
    QUIZ_QUESTION = "quiz_question"
    MANUAL_EXERCISE = "manual_exercise"
    COMPLETION_CRITERION = "completion_criterion"
    CURRICULAR_RELATION = "curricular_relation"
    REFERENCE = "reference"
    PROJECT_PACKAGE = "project_package"
    PROJECT_ARTIFACT = "project_artifact"
    SOURCE_ARTIFACT = "source_artifact"


class StagingContractError(ValueError):
    """Raised for a package that cannot be safely represented in staging."""


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


_PUBLIC_FIELDS: dict[StagedRecordKind, set[str]] = {
    StagedRecordKind.UNIT: {
        "unit_id", "title", "module_id", "module_order", "unit_order", "objective", "summary",
        "pedagogical_type", "requirement", "depth", "estimated_minutes", "tags",
    },
    StagedRecordKind.THEORY_SEGMENT: {
        "segment_id", "topic_id", "topic_title", "order", "title", "body",
    },
    StagedRecordKind.QUIZ_QUESTION: {
        "question_id", "order", "topic_id", "prompt", "options", "schema_version",
    },
    StagedRecordKind.MANUAL_EXERCISE: {"exercise_id", "order", "title", "prompt"},
    StagedRecordKind.COMPLETION_CRITERION: {
        "criterion_id", "unit_id", "source_text", "kind", "evaluation", "requires_human_review",
    },
    StagedRecordKind.CURRICULAR_RELATION: {
        "relation_id", "source_unit_id", "source_kind", "target_source_path", "target_unit_id",
        "target_anchor", "display_label", "scope", "enforced",
    },
    StagedRecordKind.REFERENCE: {
        "reference_id", "unit_id", "topic_id", "order", "title", "description", "url",
    },
    StagedRecordKind.PROJECT_PACKAGE: set(),
    StagedRecordKind.PROJECT_ARTIFACT: {
        "artifact_id", "kind", "purpose", "order", "source_item_ids", "content",
    },
    StagedRecordKind.SOURCE_ARTIFACT: set(),
}
_RESTRICTED_FIELDS: dict[StagedRecordKind, set[str]] = {
    StagedRecordKind.UNIT: set(),
    StagedRecordKind.THEORY_SEGMENT: set(),
    StagedRecordKind.QUIZ_QUESTION: {
        "correct_option_id", "explanation", "disclosure",
    },
    StagedRecordKind.MANUAL_EXERCISE: {
        "reference_answer", "rubric", "disclosure",
    },
    StagedRecordKind.COMPLETION_CRITERION: set(),
    StagedRecordKind.CURRICULAR_RELATION: set(),
    StagedRecordKind.REFERENCE: set(),
    StagedRecordKind.PROJECT_PACKAGE: set(),
    StagedRecordKind.PROJECT_ARTIFACT: {
        "artifact_id", "kind", "purpose", "order", "source_item_ids", "content",
    },
    StagedRecordKind.SOURCE_ARTIFACT: set(),
}
_SYSTEM_FIELDS = {
    "source_unit_id", "source_path", "source_revision", "source_sha256", "source_lf_sha256",
    "artifact_id", "artifact_kind", "artifact_sha256", "contract_version", "converter_version",
    "classification", "visibility_decision", "field_dispositions", "warnings", "raw_source_body",
    "source_section", "target_resolution", "source_artifact_id", "batch_id",
    "project_contract",
}
_PRIVATE_KEY_FRAGMENTS = (
    "answer", "correct", "solution", "explanation", "feedback", "rubric", "grader",
)


def _check_json(value: Any) -> None:
    json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _nested_keys(value: Any):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _nested_keys(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            yield from _nested_keys(nested)


def _contains_private_key(value: Any) -> bool:
    for key in _nested_keys(value):
        normalized = re.sub(r"[^a-z0-9]", "", key.lower())
        if any(fragment in normalized for fragment in _PRIVATE_KEY_FRAGMENTS):
            return True
    return False


class StagedRecord(_StrictModel):
    record_id: str = Field(min_length=1)
    kind: StagedRecordKind
    student_public: dict[str, Any] = Field(default_factory=dict)
    instructor_restricted: dict[str, Any] = Field(default_factory=dict)
    system_internal: dict[str, Any]

    @model_validator(mode="after")
    def enforce_field_allowlists(self) -> StagedRecord:
        if set(self.student_public) - _PUBLIC_FIELDS[self.kind]:
            raise ValueError("Campos públicos fora da lista permitida para o tipo de registro")
        if set(self.instructor_restricted) - _RESTRICTED_FIELDS[self.kind]:
            raise ValueError("Campos restritos fora da lista permitida para o tipo de registro")
        if set(self.system_internal) - _SYSTEM_FIELDS:
            raise ValueError("Metadados internos fora da lista permitida")
        if set(self.student_public) & set(self.instructor_restricted):
            raise ValueError("Campo classificado simultaneamente como público e restrito")
        if self.kind == StagedRecordKind.PROJECT_PACKAGE and (
            self.student_public or self.instructor_restricted or "project_contract" not in self.system_internal
        ):
            raise ValueError("Contrato de projeto deve permanecer exclusivamente no namespace interno")
        if self.kind == StagedRecordKind.PROJECT_ARTIFACT and self.student_public and (
            self.system_internal.get("visibility_decision") != "APPROVED_FOR_STUDENT"
        ):
            raise ValueError("Material de projeto sem aprovação explícita não pode compor projeção pública")
        if _contains_private_key(self.student_public):
            raise ValueError("Projeção pública contém chave de resposta ou correção restrita")
        if self.kind == StagedRecordKind.QUIZ_QUESTION:
            options = self.student_public.get("options", [])
            if any(
                not isinstance(option, dict)
                or set(option) != {"id", "label"}
                or not isinstance(option.get("id"), str)
                or not isinstance(option.get("label"), str)
                for option in options
            ):
                raise ValueError("Alternativas públicas de quiz devem conter somente id e label textuais")
        _check_json(self.model_dump(mode="json"))
        return self

    def student_projection(self) -> dict[str, Any]:
        """Return only allowlisted student fields; staging itself has no reader."""
        return {"id": self.record_id, "kind": self.kind.value, **self.student_public}


class StagingManifest(_StrictModel):
    schema_version: str = "trilhacode.beta5.staging/1.0"
    batch_id: str = Field(pattern=r"^beta5-[0-9a-f]{32}$")
    source_revision: str = Field(min_length=1)
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    payload_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    contract_version: str = Field(min_length=1)
    converter_version: str = Field(min_length=1)
    unit_ids: tuple[str, ...] = Field(min_length=1)
    record_count: int = Field(ge=1)
    project_artifact_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    private_payloads_in_manifest: bool = False

    @model_validator(mode="after")
    def batch_identity_matches_payload(self) -> StagingManifest:
        if self.batch_id != f"beta5-{self.payload_sha256[:32]}":
            raise ValueError("Identidade do lote deve derivar do hash canônico do payload")
        return self


class StagingPackage(_StrictModel):
    manifest: StagingManifest
    records: tuple[StagedRecord, ...] = Field(min_length=1)
    projects: tuple[ProjectPackage, ...] = ()
    completion_criteria: tuple[CompletionRule, ...] = ()
    references: tuple[CurricularReference, ...] = ()
    relations: tuple[CurricularRelation, ...] = ()
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_manifest_and_identities(self) -> StagingPackage:
        if len(self.records) != self.manifest.record_count:
            raise ValueError("Contagem do manifesto não corresponde aos registros")
        record_ids = [record.record_id for record in self.records]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("IDs de registro duplicados no pacote")
        if len(self.manifest.unit_ids) != len(set(self.manifest.unit_ids)):
            raise ValueError("IDs de unidade duplicados no manifesto")
        staged_units = {
            str(record.student_public["unit_id"])
            for record in self.records
            if record.kind == StagedRecordKind.UNIT and "unit_id" in record.student_public
        }
        if staged_units != set(self.manifest.unit_ids):
            raise ValueError("Unidades do manifesto divergem dos registros de unidade")
        if self.manifest.warning_count != len(self.warnings):
            raise ValueError("Contagem de avisos diverge do manifesto")
        project_count = sum(len(project.artifacts) for project in self.projects)
        if project_count != self.manifest.project_artifact_count:
            raise ValueError("Contagem de artefatos de projeto diverge do manifesto")
        project_records = [record for record in self.records if record.kind == StagedRecordKind.PROJECT_PACKAGE]
        project_record_ids = {
            record.system_internal.get("project_contract", {}).get("project_id") for record in project_records
        }
        if project_record_ids != {project.project_id for project in self.projects}:
            raise ValueError("Contratos de projeto persistíveis divergem dos projetos do pacote")
        expected_artifact_records = {
            f"project:{project.project_id}:{artifact.artifact_id}"
            for project in self.projects for artifact in project.artifacts
        }
        actual_artifact_records = {
            record.record_id for record in self.records if record.kind == StagedRecordKind.PROJECT_ARTIFACT
        }
        if actual_artifact_records != expected_artifact_records:
            raise ValueError("Registros de artefato de projeto divergem do contrato tipado")
        expected_criteria = {rule.criterion_id for rule in self.completion_criteria}
        actual_criteria = {
            record.record_id for record in self.records if record.kind == StagedRecordKind.COMPLETION_CRITERION
        }
        if actual_criteria != expected_criteria:
            raise ValueError("Critérios tipados divergem dos registros de staging")
        expected_references = {
            f"reference:{reference.unit_id}:{reference.reference_id}" for reference in self.references
        }
        actual_references = {
            record.record_id for record in self.records if record.kind == StagedRecordKind.REFERENCE
        }
        if actual_references != expected_references:
            raise ValueError("Referências tipadas divergem dos registros de staging")
        expected_relations = {f"relation:{relation.relation_id}" for relation in self.relations}
        actual_relations = {
            record.record_id for record in self.records if record.kind == StagedRecordKind.CURRICULAR_RELATION
        }
        if actual_relations != expected_relations:
            raise ValueError("Relações tipadas divergem dos registros de staging")
        if self.manifest.private_payloads_in_manifest:
            raise ValueError("Manifesto não pode armazenar payloads privados")
        content_hash = _package_content_hash(
            self.records, self.projects, self.completion_criteria, self.references, self.relations, self.warnings,
        )
        if content_hash != self.manifest.payload_sha256:
            raise ValueError("Hash canônico do pacote diverge do manifesto")
        return self


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _package_content_hash(
    records: tuple[StagedRecord, ...],
    projects: tuple[ProjectPackage, ...],
    completion_criteria: tuple[CompletionRule, ...] = (),
    references: tuple[CurricularReference, ...] = (),
    relations: tuple[CurricularRelation, ...] = (),
    warnings: tuple[str, ...] = (),
) -> str:
    content = {
        "records": [record.model_dump(mode="json") for record in records],
        "projects": [project.model_dump(mode="json") for project in projects],
        "completion_criteria": [item.model_dump(mode="json") for item in completion_criteria],
        "references": [item.model_dump(mode="json") for item in references],
        "relations": [item.model_dump(mode="json") for item in relations],
        "warnings": list(warnings),
    }
    return hashlib.sha256(_canonical_bytes(content)).hexdigest()


def _source_unit_id(path: str) -> str | None:
    match = re.search(r"(?:^|/)(\d+\.\d+)_", path.replace("\\", "/"))
    return match.group(1) if match else None


def _stable_relation_id(unit_id: str, relation_index: int, target_path: str, source_kind: str) -> str:
    raw = f"{unit_id}|{relation_index}|{source_kind}|{target_path}".encode("utf-8")
    return "relation-" + hashlib.sha256(raw).hexdigest()[:24]


def staging_package_from_first_phase(batch: FirstPhaseBatch) -> StagingPackage:
    """Build a loss-accounted staging package from the existing Beta 4 batch."""
    validated = FirstPhaseBatch.model_validate(batch.model_dump(mode="python"))
    if (
        validated.contract_version != BETA4_CONTRACT_VERSION
        or validated.converter_version != BETA4_CONVERTER_VERSION
    ):
        raise StagingContractError("Versão do contrato/conversor curricular não compatível com o staging Beta 5")
    unit_ids = {unit.provenance.source_id for unit in validated.units}
    records: list[StagedRecord] = []
    criteria: list[CompletionRule] = []
    references: list[CurricularReference] = []
    relations: list[CurricularRelation] = []
    projects: list[ProjectPackage] = []

    for unit in validated.units:
        provenance = unit.provenance
        common_system = {
            "source_unit_id": provenance.source_id,
            "source_path": provenance.source_path,
            "source_revision": provenance.source_revision,
            "source_sha256": provenance.source_sha256,
            "contract_version": validated.contract_version,
            "converter_version": validated.converter_version,
        }
        records.append(StagedRecord(
            record_id=f"unit:{provenance.source_id}",
            kind=StagedRecordKind.UNIT,
            student_public={
                "unit_id": provenance.source_id,
                "title": unit.title,
                "module_id": unit.module_id,
                "module_order": unit.module_order,
                "unit_order": unit.unit_order,
                "objective": unit.objective,
                "summary": unit.summary,
                "pedagogical_type": unit.pedagogical_type,
                "requirement": unit.requirement,
                "depth": unit.depth,
                "estimated_minutes": unit.estimated_minutes,
                "tags": list(unit.tags),
            },
            system_internal={**common_system, "field_dispositions": [item.model_dump(mode="json") for item in unit.field_dispositions],
                             "warnings": list(unit.warnings)},
        ))

        for topic in unit.topics:
            for segment in topic.segments:
                records.append(StagedRecord(
                    record_id=f"theory:{provenance.source_id}:{segment.ref}",
                    kind=StagedRecordKind.THEORY_SEGMENT,
                    student_public={
                        "segment_id": segment.ref,
                        "topic_id": topic.ref,
                        "topic_title": topic.title,
                        "order": segment.order,
                        "title": segment.source_heading,
                        "body": segment.markdown_body,
                    },
                    system_internal={**common_system, "source_sha256": segment.source_sha256,
                                     "source_section": segment.source_heading},
                ))

        for question in unit.quiz_questions:
            records.append(StagedRecord(
                record_id=f"quiz:{provenance.source_id}:{question.ref}",
                kind=StagedRecordKind.QUIZ_QUESTION,
                student_public={
                    "question_id": question.ref,
                    "order": question.order,
                    "topic_id": question.topic_ref,
                    "prompt": question.prompt,
                    "options": [{"id": item.id, "label": item.label} for item in question.options],
                    "schema_version": question.activity_schema_version,
                },
                instructor_restricted={
                    "correct_option_id": question.correct_option_id,
                    "explanation": question.explanation,
                    "disclosure": "PENDING_DECISION",
                },
                system_internal={**common_system, "classification": "field_level_split"},
            ))

        for exercise in unit.manual_exercises:
            records.append(StagedRecord(
                record_id=f"exercise:{provenance.source_id}:{exercise.ref}",
                kind=StagedRecordKind.MANUAL_EXERCISE,
                student_public={
                    "exercise_id": exercise.ref,
                    "order": exercise.order,
                    "title": exercise.title,
                    "prompt": exercise.student_prompt,
                },
                instructor_restricted={
                    "reference_answer": exercise.grader_reference,
                    "rubric": list(exercise.grader_criteria),
                    "disclosure": "PENDING_DECISION",
                },
                system_internal={**common_system, "classification": exercise.grader_data_classification},
            ))

        if unit.completion_criterion is not None:
            criterion_id = f"completion:{provenance.source_id}:source"
            rule = CompletionRule(
                criterion_id=criterion_id,
                unit_id=provenance.source_id,
                source_text=unit.completion_criterion.source_text,
                kind=CriterionKind.UNSTRUCTURED,
                evaluation=EvaluationMode.DECISION_REQUIRED,
                requires_human_review=True,
            )
            criteria.append(rule)
            records.append(StagedRecord(
                record_id=criterion_id,
                kind=StagedRecordKind.COMPLETION_CRITERION,
                student_public={
                    "criterion_id": rule.criterion_id,
                    "unit_id": rule.unit_id,
                    "source_text": rule.source_text,
                    "kind": rule.kind.value,
                    "evaluation": rule.evaluation.value,
                    "requires_human_review": rule.requires_human_review,
                },
                system_internal={**common_system, "classification": DataClassification.STUDENT_PUBLIC.value},
            ))

        for index, relation in enumerate(unit.relations, start=1):
            target_id = _source_unit_id(relation.target_path)
            scope = (
                RelationScope.INTERNAL_TO_BATCH if target_id in unit_ids
                else RelationScope.EXTERNAL_NOT_LOADED if target_id
                else RelationScope.UNRESOLVED_SOURCE_REFERENCE
            )
            relation_contract = CurricularRelation(
                relation_id=_stable_relation_id(provenance.source_id, index, relation.target_path, relation.source_kind),
                source_unit_id=provenance.source_id,
                source_kind=relation.source_kind,
                target_source_path=relation.target_path,
                target_unit_id=target_id,
                target_anchor=relation.target_anchor,
                display_label=relation.display_label,
                scope=scope,
                enforced=False,
            )
            relations.append(relation_contract)
            records.append(StagedRecord(
                record_id=f"relation:{relation_contract.relation_id}",
                kind=StagedRecordKind.CURRICULAR_RELATION,
                student_public=relation_contract.model_dump(
                    mode="json", exclude={"provenance_artifact_id"},
                ),
                system_internal={**common_system, "source_artifact_id": next((
                    item.artifact_id for item in unit.source_artifacts if item.kind == "conexoes"
                ), "")},
            ))

        for reference in unit.references:
            reference_contract = CurricularReference(
                reference_id=reference.ref,
                unit_id=provenance.source_id,
                topic_id=None,
                order=reference.order,
                title=reference.title,
                description=reference.description,
                url=reference.url,
                origin=provenance.source_path,
                provenance_sha256=hashlib.sha256(reference.source_markdown.encode("utf-8")).hexdigest(),
            )
            references.append(reference_contract)
            records.append(StagedRecord(
                record_id=f"reference:{provenance.source_id}:{reference.ref}",
                kind=StagedRecordKind.REFERENCE,
                student_public={
                    "reference_id": reference_contract.reference_id,
                    "unit_id": reference_contract.unit_id,
                    "topic_id": reference_contract.topic_id,
                    "order": reference_contract.order,
                    "title": reference_contract.title,
                    "description": reference_contract.description,
                    "url": reference_contract.url,
                },
                system_internal={
                    **common_system,
                    "source_path": reference_contract.origin,
                    "source_sha256": reference_contract.provenance_sha256,
                },
            ))

        if provenance.source_id == "3.5" and unit.project_materials:
            project = project_package_from_converted_unit(unit)
            projects.append(project)
            records.append(StagedRecord(
                record_id=f"project-package:{project.project_id}",
                kind=StagedRecordKind.PROJECT_PACKAGE,
                system_internal={
                    **common_system,
                    "classification": DataClassification.SYSTEM_INTERNAL.value,
                    "visibility_decision": project.visibility_decision,
                    "project_contract": project.model_dump(mode="json"),
                },
            ))
            for artifact in project.artifacts:
                content = artifact.student_content or artifact.restricted_content or artifact.internal_content or ""
                fields = {
                    "artifact_id": artifact.artifact_id,
                    "kind": artifact.kind.value,
                    "purpose": artifact.purpose,
                    "order": artifact.order,
                    "source_item_ids": list(artifact.source_item_ids),
                    "content": content,
                }
                records.append(StagedRecord(
                    record_id=f"project:{project.project_id}:{artifact.artifact_id}",
                    kind=StagedRecordKind.PROJECT_ARTIFACT,
                    student_public={},
                    instructor_restricted=fields if artifact.classification == DataClassification.INSTRUCTOR_RESTRICTED else {},
                    system_internal={
                        **common_system,
                        "artifact_id": artifact.artifact_id,
                        "artifact_kind": artifact.kind.value,
                        "artifact_sha256": artifact.content_sha256,
                        "classification": artifact.classification.value,
                        "visibility_decision": artifact.visibility_decision,
                        **({"raw_source_body": content}
                           if artifact.classification != DataClassification.INSTRUCTOR_RESTRICTED else {}),
                    },
                ))

        for source_artifact in unit.source_artifacts:
            # Raw source is retained only in the internal, non-reader namespace;
            # normalized public and restricted fields above are separate records.
            records.append(StagedRecord(
                record_id=f"source:{provenance.source_id}:{source_artifact.artifact_id}",
                kind=StagedRecordKind.SOURCE_ARTIFACT,
                system_internal={
                    **common_system,
                    "artifact_id": source_artifact.artifact_id,
                    "artifact_kind": source_artifact.kind,
                    "artifact_sha256": source_artifact.sha256,
                    "classification": DataClassification.SYSTEM_INTERNAL.value,
                    "visibility_decision": "RAW_SOURCE_NOT_READER_VISIBLE",
                    "raw_source_body": source_artifact.body,
                },
            ))

    records.sort(key=lambda record: record.record_id)
    projects_tuple = tuple(projects)
    record_tuple = tuple(records)
    criteria_tuple = tuple(criteria)
    references_tuple = tuple(references)
    relations_tuple = tuple(relations)
    warning_tuple = tuple(warning for unit in validated.units for warning in unit.warnings)
    payload_hash = _package_content_hash(
        record_tuple, projects_tuple, criteria_tuple, references_tuple, relations_tuple, warning_tuple,
    )
    source_manifest_hash = hashlib.sha256(
        json.dumps(validated.to_manifest(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    batch_id = f"beta5-{payload_hash[:32]}"
    warning_count = sum(len(unit.warnings) for unit in validated.units)
    manifest = StagingManifest(
        batch_id=batch_id,
        source_revision=validated.source_revision,
        source_manifest_sha256=source_manifest_hash,
        payload_sha256=payload_hash,
        contract_version=validated.contract_version,
        converter_version=validated.converter_version,
        unit_ids=tuple(unit.provenance.source_id for unit in validated.units),
        record_count=len(record_tuple),
        project_artifact_count=sum(len(project.artifacts) for project in projects_tuple),
        warning_count=warning_count,
    )
    return StagingPackage(
        manifest=manifest,
        records=record_tuple,
        projects=projects_tuple,
        completion_criteria=criteria_tuple,
        references=references_tuple,
        relations=relations_tuple,
        warnings=warning_tuple,
    )
