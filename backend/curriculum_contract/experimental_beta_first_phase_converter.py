"""Experimental batch conversion of the reviewed first-phase source tree.

The converter is read-only with respect to its source.  It reuses Beta 3's
strict pedagogical value objects and emits only the existing C16 import shape.
Instructor material and project milestones stay in the intermediate model and
are deliberately omitted from import payloads until an ACL-backed destination
exists.  This module is not wired into application startup or routes.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from curriculum_contract.experimental_beta_curriculum_fidelity import (
    CompletionCriterion,
    CurricularRelation,
    FieldDisposition,
    ManualExercise,
    QuizOption,
    QuizQuestion,
    ReferenceItem,
    SourceProvenance,
    TheorySegment,
    TheoryTopic,
)

CONVERTER_VERSION = "beta4-first-phase-batch/1.1"
CONTRACT_VERSION = "trilhacode.beta4.first-phase/1.0"
IMPORT_SHAPE = "track/options/nodes/relations"
APPROVED_BETA3_MONOLITH_SHA256 = (
    "db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4"
)
SOURCE_RELATIVE = PurePosixPath(
    "docs/courses/trilhacode/Conteudos_migrado/Fase_1"
)
MONOLITH_RELATIVE = PurePosixPath(
    "docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md"
)
KNOWN_ARTIFACT_TYPES = {
    "objetivo", "resumo", "criterio", "conexoes", "referencias", "topic_index",
    "theory", "quiz", "answer_key", "practice", "answer_key_pratica",
    "rubric", "checklist", "project_brief", "milestone",
}
_FRONTMATTER = re.compile(r"\A---\s*\r?\n(?P<meta>.*?)\r?\n---\s*\r?\n(?P<body>.*)\Z", re.S)
_HEADING = re.compile(r"(?m)^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
_WIKILINK = re.compile(r"\[\[(?P<target>[^\]|]+)(?:\|(?P<label>[^\]]+))?\]\]")
_RELATION = re.compile(
    r"^\s*-\s*(?P<kind>Complementar|Relacionado|Pré-requisito|Pré-requisitos|Projeto acumulado):\s*(?P<links>.+?)\s*$",
    re.I,
)
_UNIT_DIRECTORY = re.compile(r"^(?P<phase>\d+)\.(?P<unit>\d+)_")
_ITEM = re.compile(r"^(?P<prefix>[QPM])(?P<number>\d+)$", re.I)
_QUESTION_LINE = re.compile(r"^\s*(?P<number>\d+)\.\s+(?P<text>.+)$")
_OPTION_LINE = re.compile(r"^\s*-\s*(?P<letter>[A-H])\.\s+(?P<text>.+)$")
_ANSWER_LINE = re.compile(r"^\s*(?P<number>\d+)\.\s+\*\*(?P<letter>[A-H])\.\*\*\s*(?P<text>.*)$")
_INLINE_OPTION = re.compile(r"\*\*(?P<letter>[A-H])[.)]\*\*")
_COMPACT_ANSWER = re.compile(
    r"^\s*(?:(?P<number>\d+)\.\s*)?\*\*(?:Resposta:\s*)?(?P<letter>[A-H])(?:\.)?\*\*\s*(?P<text>.*)$",
    re.I,
)
_RELATION_KEYS = {
    "Complementar": "complement",
    "Relacionado": "related",
    "Pré-requisito": "prerequisite",
    "Pré-requisitos": "prerequisite",
}
RelationKind = Literal["Complementar", "Relacionado", "Pré-requisito", "Pré-requisitos"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate frontmatter keys."""


def _construct_unique_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"chave YAML duplicada: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping,
)


class SourceArtifact(_StrictModel):
    artifact_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    relative_path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    sha256_lf: str = Field(pattern=r"^[0-9a-f]{64}$")
    order: int | None = Field(default=None, ge=0)
    topic_key: str | None = None
    item_ids: tuple[str, ...] = ()
    title: str | None = None
    metadata: dict[str, Any]
    body: str

    def public_manifest(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "kind": self.kind,
            "path": self.relative_path,
            "sha256": self.sha256,
            "sha256_lf": self.sha256_lf,
            "order": self.order,
            "topic_key": self.topic_key,
            "item_ids": list(self.item_ids),
        }


class RestrictedMaterial(_StrictModel):
    artifact_id: str = Field(min_length=1)
    associated_item_id: str | None = None
    kind: Literal["answer_key", "answer_key_pratica", "rubric", "checklist"]
    relative_path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content: str
    data_classification: Literal["restricted_instructor", "visibility_pending"]


class ProjectMaterial(_StrictModel):
    artifact_id: str = Field(min_length=1)
    kind: Literal["project_brief", "milestone", "rubric", "checklist", "theory"]
    order: int = Field(ge=0)
    relative_path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content: str
    source_item_ids: tuple[str, ...] = ()


RestrictedKind = Literal["answer_key", "answer_key_pratica", "rubric", "checklist"]
ProjectKind = Literal["project_brief", "milestone", "rubric", "checklist", "theory"]


class ConvertedUnit(_StrictModel):
    schema_version: Literal[1] = 1
    converter_version: str = CONVERTER_VERSION
    provenance: SourceProvenance
    module_id: str = Field(min_length=1)
    module_order: int = Field(ge=1)
    unit_order: int = Field(ge=1)
    title: str = Field(min_length=1)
    pedagogical_type: str = Field(min_length=1)
    requirement: str = Field(min_length=1)
    depth: str = Field(min_length=1)
    estimated_minutes: int | None = Field(default=None, ge=0)
    tags: tuple[str, ...] = ()
    objective: str = Field(min_length=1)
    topics: tuple[TheoryTopic, ...] = ()
    summary: str = ""
    quiz_questions: tuple[QuizQuestion, ...] = ()
    manual_exercises: tuple[ManualExercise, ...] = ()
    completion_criterion: CompletionCriterion | None = None
    relations: tuple[CurricularRelation, ...] = ()
    references: tuple[ReferenceItem, ...] = ()
    private_materials: tuple[RestrictedMaterial, ...] = ()
    project_materials: tuple[ProjectMaterial, ...] = ()
    source_artifacts: tuple[SourceArtifact, ...]
    unresolved_connection_lines: tuple[str, ...] = ()
    field_dispositions: tuple[FieldDisposition, ...]
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_identities_and_orders(self) -> ConvertedUnit:
        refs: list[str] = []
        for topic in self.topics:
            refs.append(topic.ref)
            refs.extend(segment.ref for segment in topic.segments)
        refs.extend(question.ref for question in self.quiz_questions)
        refs.extend(exercise.ref for exercise in self.manual_exercises)
        refs.extend(reference.ref for reference in self.references)
        if len(refs) != len(set(refs)):
            raise ValueError("IDs curriculares duplicados na unidade")
        for values, label in (
            ([topic.order for topic in self.topics], "tópicos"),
            ([question.order for question in self.quiz_questions], "questões"),
            ([exercise.order for exercise in self.manual_exercises], "exercícios"),
            ([reference.order for reference in self.references], "referências"),
        ):
            if values and values != list(range(1, len(values) + 1)):
                raise ValueError(f"ordem de {label} não é contínua")
        primary_ids = [
            item for artifact in self.source_artifacts
            if artifact.kind in {"quiz", "practice"}
            for item in artifact.item_ids
        ]
        if len(primary_ids) != len(set(primary_ids)):
            raise ValueError("IDs de questão/prática duplicados nos artefatos")
        return self

    @property
    def block_count(self) -> int:
        return (
            sum(len(topic.segments) for topic in self.topics)
            + bool(self.summary)
            + len(self.quiz_questions)
            + len(self.manual_exercises)
            + len(self.references)
        )

    @property
    def conversion_status(self) -> str:
        blocked = any(item.status == "UNSUPPORTED" for item in self.field_dispositions)
        if blocked:
            return "CONVERSION_BLOCKED"
        if any(item.status in {"REQUIRES_ADAPTER", "NOT_VERIFIED"} for item in self.field_dispositions):
            return "CONVERSION_SUCCESS_WITH_WARNINGS"
        return "CONVERSION_SUCCESS"

    def to_import_payload(self) -> dict[str, Any]:
        """Project safe existing fields into the versioned import schema.

        Restricted exercise material, completion criteria, project milestones,
        and reference descriptions are intentionally not sent to the writer.
        Quiz keys remain only in draft blocks and require the existing
        publication/read projections before student access is possible.
        """
        unit_token = _token(self.provenance.source_id)
        unit_ref = f"unit-{unit_token}"
        root_ref = "phase-1"
        module_ref = f"module-{self.module_id}"
        nodes: list[dict[str, Any]] = [{
            "ref": root_ref,
            "kind": "phase",
            "title": "Fase 1",
            "status": "draft",
            "children": [{
                "ref": module_ref,
                "kind": "module",
                "title": f"Módulo {self.module_id}",
                "status": "draft",
                "children": [],
            }],
        }]
        module_node = nodes[0]["children"][0]
        unit_node: dict[str, Any] = {
            "ref": unit_ref,
            "kind": "submodule",
            "title": self.title,
            "description": self.objective,
            "status": "draft",
            "pedagogical_type": self.pedagogical_type,
            "requirement": self.requirement,
            "depth": self.depth,
            "tags": list(self.tags),
            "blocks": [],
            "children": [],
        }
        if self.estimated_minutes is not None:
            unit_node["estimated_minutes"] = self.estimated_minutes
        module_node["children"].append(unit_node)

        for topic in self.topics:
            topic_node: dict[str, Any] = {
                "ref": topic.ref,
                "kind": "topic",
                "title": topic.title,
                "status": "draft",
                "blocks": [],
            }
            for segment in topic.segments:
                topic_node["blocks"].append({
                    "ref": segment.ref,
                    "type": "theory_text",
                    "title": segment.source_heading,
                    "status": "draft",
                    "data": {"body": segment.markdown_body},
                })
            questions = [question for question in self.quiz_questions if question.topic_ref == topic.ref]
            for question in questions:
                topic_node["blocks"].append(_quiz_block(question))
            unit_node["children"].append(topic_node)

        for question in self.quiz_questions:
            if question.topic_ref is None:
                unit_node["blocks"].append(_quiz_block(question))
        if self.summary:
            unit_node["blocks"].append({
                "ref": f"{unit_token}-summary-001", "type": "summary", "title": "Resumo",
                "status": "draft", "data": {"body": self.summary},
            })
        for exercise in self.manual_exercises:
            unit_node["blocks"].append({
                "ref": exercise.ref, "type": "exercise_open", "title": exercise.title,
                "status": "draft", "data": {"prompt": exercise.student_prompt, "grading": "manual"},
            })
        for reference in self.references:
            unit_node["blocks"].append({
                "ref": reference.ref, "type": "reference", "title": reference.title,
                "status": "draft", "data": {"citation": reference.title, "url": reference.url},
            })

        refs = _all_node_refs(nodes)
        relations: list[dict[str, Any]] = []
        for relation in self.relations:
            target_id = _target_unit_id(relation.target_path)
            source_ref = unit_ref
            target_ref = f"unit-{_token(target_id)}" if target_id else ""
            relation_type = _RELATION_KEYS.get(relation.source_kind)
            if target_ref in refs and relation_type:
                relations.append({
                    "from": source_ref,
                    "to": target_ref,
                    "type": relation_type,
                    "enforced": False,
                    "note": relation.display_label or relation.target_path,
                })
        return {
            "track": {
                "title": "[Beta 4 isolada] Fase 1 revisada",
                "slug": "beta4-first-phase-curriculum",
                "description": "Importação experimental, privada e em rascunho.",
                "visibility": "private",
                "hierarchy": ["phase", "module", "submodule", "topic"],
            },
            "options": {"create_missing_tags": True},
            "nodes": nodes,
            "relations": relations,
        }

    def to_manifest(self) -> dict[str, Any]:
        payload = self.to_import_payload()
        blocks = _collect_blocks(payload["nodes"])
        count_by_type: dict[str, int] = {}
        for block in blocks:
            count_by_type[block["type"]] = count_by_type.get(block["type"], 0) + 1
        return {
            "manifest_schema": "trilhacode.beta4.unit-manifest/1.0",
            "unit_id": self.provenance.source_id,
            "title": self.title,
            "module_id": self.module_id,
            "module_order": self.module_order,
            "unit_order": self.unit_order,
            "source": self.provenance.model_dump(),
            "source_artifacts": [artifact.public_manifest() for artifact in self.source_artifacts],
            "counts": {
                "topics": len(self.topics),
                "theory_segments": sum(len(topic.segments) for topic in self.topics),
                "quiz_files": sum(artifact.kind == "quiz" for artifact in self.source_artifacts),
                "quiz_questions": len(self.quiz_questions),
                "manual_exercises": len(self.manual_exercises),
                "project_materials": len(self.project_materials),
                "references": len(self.references),
                "relations": len(self.relations),
                "persisted_blocks": len(blocks),
            },
            "generated_ids": [block["ref"] for block in blocks]
            + [node["ref"] for node in _flatten_nodes(payload["nodes"])
               if node["ref"].startswith(f"unit-{_token(self.provenance.source_id)}")],
            "field_dispositions": [item.model_dump() for item in self.field_dispositions],
            "unresolved_connection_line_count": len(self.unresolved_connection_lines),
            "warnings": list(self.warnings),
            "conversion_status": self.conversion_status,
            "private_source_bodies_in_manifest": False,
        }


class FirstPhaseBatch(_StrictModel):
    schema_version: Literal[1] = 1
    contract_version: str = CONTRACT_VERSION
    converter_version: str = CONVERTER_VERSION
    source_revision: str = Field(min_length=1)
    phase_id: Literal[1] = 1
    units: tuple[ConvertedUnit, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_complete_phase(self) -> FirstPhaseBatch:
        ids = [unit.provenance.source_id for unit in self.units]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de unidade duplicados no lote")
        expected = sorted(ids, key=_unit_sort_key)
        if ids != expected:
            raise ValueError("unidades fora da ordem curricular")
        return self

    @property
    def conversion_status(self) -> str:
        if any(unit.conversion_status == "CONVERSION_BLOCKED" for unit in self.units):
            return "CONVERSION_BLOCKED"
        if any(unit.conversion_status == "CONVERSION_SUCCESS_WITH_WARNINGS" for unit in self.units):
            return "CONVERSION_SUCCESS_WITH_WARNINGS"
        return "CONVERSION_SUCCESS"

    def to_import_payload(self) -> dict[str, Any]:
        """Aggregate all units into one private import request.

        Validation is completed before this method is called by the batch API;
        callers still must run the real importer's dry-run before persistence.
        """
        payload: dict[str, Any] = {
            "track": {
                "title": "[Beta 4 isolada] Fase 1 revisada",
                "slug": "beta4-first-phase-curriculum",
                "description": "Importação experimental, privada e em rascunho.",
                "visibility": "private",
                "hierarchy": ["phase", "module", "submodule", "topic"],
            },
            "options": {"create_missing_tags": True},
            "nodes": [{
                "ref": "phase-1", "kind": "phase", "title": "Fase 1", "status": "draft",
                "children": [],
            }],
            "relations": [],
        }
        modules: dict[str, dict[str, Any]] = {}
        all_unit_refs = {f"unit-{_token(unit.provenance.source_id)}" for unit in self.units}
        for unit in self.units:
            module_ref = f"module-{unit.module_id}"
            module: dict[str, Any] | None = modules.get(module_ref)
            if module is None:
                module = {
                    "ref": module_ref, "kind": "module", "title": f"Módulo {unit.module_id}",
                    "status": "draft", "children": [],
                }
                modules[module_ref] = module
                payload["nodes"][0]["children"].append(module)
            unit_payload = unit.to_import_payload()
            source_unit_node = _find_node(unit_payload["nodes"], f"unit-{_token(unit.provenance.source_id)}")
            module["children"].append(source_unit_node)
            for relation in unit.relations:
                target_id = _target_unit_id(relation.target_path)
                target_ref = f"unit-{_token(target_id)}" if target_id else ""
                relation_type = _RELATION_KEYS.get(relation.source_kind)
                if target_ref in all_unit_refs and relation_type:
                    payload["relations"].append({
                        "from": f"unit-{_token(unit.provenance.source_id)}",
                        "to": target_ref,
                        "type": relation_type,
                        "enforced": False,
                        "note": relation.display_label or relation.target_path,
                    })
        # Stable ordering does not depend on filesystem traversal.
        payload["nodes"][0]["children"].sort(key=lambda item: int(item["ref"].split("-")[-1]))
        payload["relations"].sort(key=lambda item: (item["from"], item["to"], item["type"]))
        return payload

    def to_manifest(self) -> dict[str, Any]:
        unit_manifests = [unit.to_manifest() for unit in self.units]
        counts = {
            key: sum(item["counts"][key] for item in unit_manifests)
            for key in (
                "topics", "theory_segments", "quiz_files", "quiz_questions",
                "manual_exercises", "project_materials", "references", "relations",
                "persisted_blocks",
            )
        }
        all_ids = [ref for item in unit_manifests for ref in item["generated_ids"]]
        duplicate_ids = sorted(ref for ref in set(all_ids) if all_ids.count(ref) > 1)
        payload = self.to_import_payload()
        payload_bytes = _canonical_json(payload)
        manifest = {
            "manifest_schema": "trilhacode.beta4.first-phase-manifest/1.0",
            "phase_id": 1,
            "source_revision": self.source_revision,
            "contract_version": self.contract_version,
            "converter_version": self.converter_version,
            "unit_count": len(self.units),
            "module_count": len({unit.module_id for unit in self.units}),
            "counts": counts,
            "units": unit_manifests,
            "aggregate_status": self.conversion_status,
            "duplicate_generated_ids": duplicate_ids,
            "payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
            "canonical_manifest_sha256": "",
            "private_content_in_manifest": False,
            "all_sources_read_only": True,
            "draft_and_private_only": True,
        }
        manifest["canonical_manifest_sha256"] = hashlib.sha256(
            _canonical_json({key: value for key, value in manifest.items() if key != "canonical_manifest_sha256"})
        ).hexdigest()
        return manifest


def convert_first_phase(
    repository_root: Path,
    *,
    source_revision: str = "migration@147dc68:tracked-clean-first-phase-files",
    verify_beta3_pilot_hash: bool = True,
) -> FirstPhaseBatch:
    """Discover and convert every unit in the reviewed segmented first phase."""
    repository_root = repository_root.resolve(strict=True)
    phase_dir = (repository_root / Path(*SOURCE_RELATIVE.parts)).resolve(strict=True)
    if not phase_dir.is_dir() or phase_dir.parent != (repository_root / "docs/courses/trilhacode/Conteudos_migrado").resolve():
        raise ValueError("diretório da Fase 1 não corresponde à fonte experimental esperada")
    if verify_beta3_pilot_hash:
        monolith = repository_root / Path(*MONOLITH_RELATIVE.parts)
        if not monolith.is_file():
            raise ValueError("fonte monolítica autorizada da unidade 1.1 não foi localizada")
        digest = hashlib.sha256(monolith.read_bytes()).hexdigest()
        if digest != APPROVED_BETA3_MONOLITH_SHA256:
            raise ValueError("SHA-256 da fonte monolítica 1.1 diverge do manifesto Beta 3")
    unit_dirs = sorted((path for path in phase_dir.iterdir() if path.is_dir()), key=lambda path: _unit_sort_key(_unit_id(path.name)))
    if not unit_dirs:
        raise ValueError("nenhuma unidade encontrada na fonte da Fase 1")
    units = tuple(
        _convert_unit(repository_root, phase_dir, unit_dir, source_revision)
        for unit_dir in unit_dirs
    )
    batch = FirstPhaseBatch(source_revision=source_revision, units=units)
    payload = batch.to_import_payload()
    _validate_payload_refs(payload)
    return batch


def _convert_unit(repository_root: Path, phase_dir: Path, unit_dir: Path, revision: str) -> ConvertedUnit:
    unit_id = _unit_id(unit_dir.name)
    module_id = unit_id.split(".", 1)[0]
    module_order = int(module_id)
    unit_order = int(unit_id.split(".", 1)[1])
    artifacts = tuple(_read_artifact(repository_root, phase_dir, path) for path in sorted(unit_dir.rglob("*.md")))
    by_kind: dict[str, list[SourceArtifact]] = {}
    for artifact in artifacts:
        by_kind.setdefault(artifact.kind, []).append(artifact)
    unknown = [artifact for artifact in artifacts if artifact.kind not in KNOWN_ARTIFACT_TYPES]
    if unknown:
        raise ValueError(f"tipos desconhecidos em {unit_id}: {[item.kind for item in unknown]}")
    index = _one(by_kind, "topic_index", unit_id)
    index_meta = _artifact_metadata(repository_root / Path(*PurePosixPath(index.relative_path).parts))
    objective = _one(by_kind, "objetivo", unit_id)
    summary = _optional_one(by_kind, "resumo", unit_id)
    criterion = _optional_one(by_kind, "criterio", unit_id)
    connection_artifact = _optional_one(by_kind, "conexoes", unit_id)
    references_artifact = _optional_one(by_kind, "referencias", unit_id)
    title = str(index_meta.get("title") or "").strip()
    if not title:
        raise ValueError(f"título ausente no índice da unidade {unit_id}")
    for field in ("tipo", "carater", "profundidade"):
        if not isinstance(index_meta.get(field), str) or not index_meta[field].strip():
            raise ValueError(f"metadado {field} ausente em {unit_id}")
    tags_value = index_meta.get("tags", [])
    if not isinstance(tags_value, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags_value):
        raise ValueError(f"tags inválidas em {unit_id}")
    estimated = index_meta.get("estimativa_minutos")
    if estimated is not None and (not isinstance(estimated, int) or isinstance(estimated, bool) or estimated < 0):
        raise ValueError(f"estimativa de duração inválida em {unit_id}")
    topics = _convert_topics(unit_id, by_kind.get("theory", []))
    questions, quiz_warnings = _convert_quizzes(unit_id, topics, by_kind)
    exercises, exercise_warnings = _convert_exercises(unit_id, by_kind)
    private_materials = _restricted_materials(by_kind)
    project_materials = _project_materials(by_kind)
    relations, unresolved = _convert_relations(connection_artifact.body if connection_artifact else "")
    references = _convert_references(unit_id, references_artifact)
    file_hashes = [
        {"path": artifact.relative_path, "sha256": artifact.sha256}
        for artifact in artifacts
    ]
    file_hashes_lf = [
        {"path": artifact.relative_path, "sha256": artifact.sha256_lf}
        for artifact in artifacts
    ]
    unit_source_hash = hashlib.sha256(_canonical_json(file_hashes)).hexdigest()
    unit_source_hash_lf = hashlib.sha256(_canonical_json(file_hashes_lf)).hexdigest()
    source_path = unit_dir.relative_to(repository_root).as_posix()
    provenance = SourceProvenance(
        source_id=unit_id,
        source_path=source_path,
        source_revision=revision,
        source_status=str(index_meta.get("status", "unknown")),
        source_sha256=unit_source_hash,
        source_sha256_lf=unit_source_hash_lf,
        converter_version=CONVERTER_VERSION,
    )
    has_quiz = bool(questions)
    has_practice_answers = any(
        artifact.kind in {"answer_key_pratica", "rubric"} for artifact in artifacts
    )
    has_checklists = bool(by_kind.get("checklist"))
    fields = [
        FieldDisposition(
            source="Objetivo e corpo teórico/resumo",
            destination="nodes.description/content_blocks",
            status="SUPPORTED_WITH_TRANSFORMATION",
            privacy="public",
            reason="Blocos e nós ficam em draft/private; hierarquia derivada dos IDs da Fase 1.",
        ),
        FieldDisposition(
            source="Gabarito e explicação do quiz",
            destination="draft quiz.data + projeção de publicação existente",
            status="SUPPORTED_WITH_TRANSFORMATION" if has_quiz else "SOURCE_ABSENT",
            privacy="restricted" if has_quiz else "metadata",
            reason=(
                "Persistido apenas no banco descartável; publicação e endpoint real não foram exercitados."
                if has_quiz else "A fonte desta unidade não contém questões de quiz."
            ),
        ),
        FieldDisposition(
            source="Critério de conclusão",
            destination=None,
            status="REQUIRES_ADAPTER",
            privacy="public",
            reason="O importador não possui destino semântico para o critério; mantido no contrato intermediário.",
        ),
        FieldDisposition(
            source="Respostas de referência e rubricas de exercícios manuais",
            destination=None,
            status="REQUIRES_ADAPTER" if has_practice_answers else "SOURCE_ABSENT",
            privacy="restricted" if has_practice_answers else "metadata",
            reason=(
                "Não há ACL operacional comprovada para persistir esse material; excluído do payload."
                if has_practice_answers else "A fonte não contém gabarito ou rubrica de exercício manual."
            ),
        ),
        FieldDisposition(
            source="Checklists e critérios de aceite",
            destination=None,
            status="REQUIRES_ADAPTER" if has_checklists else "SOURCE_ABSENT",
            privacy="pending_policy" if has_checklists else "metadata",
            reason=(
                "Classificação aluno/instrutor não está declarada de forma consistente; conteúdo mantido fora do payload."
                if has_checklists else "A fonte não contém checklists."
            ),
        ),
        FieldDisposition(
            source="Descrição de referências",
            destination=None,
            status="REQUIRES_ADAPTER" if references else "SOURCE_ABSENT",
            privacy="public" if references else "metadata",
            reason="O tipo reference aceita citation/url, sem campo tipado de descrição.",
        ),
        FieldDisposition(
            source="Conexões externas ou não resolvidas",
            destination="contract intermediate only",
            status="REQUIRES_ADAPTER" if unresolved else (
                "SUPPORTED_WITH_TRANSFORMATION" if relations else "SOURCE_ABSENT"
            ),
            privacy="metadata",
            reason="Relações internas são não-enforced; alvos externos permanecem textuais e não são importados.",
        ),
        FieldDisposition(
            source="Brief, marcos e rubricas de projeto",
            destination=None,
            status="REQUIRES_ADAPTER" if project_materials else "SOURCE_ABSENT",
            privacy="restricted",
            reason="Não existe contrato operacional de projeto por marcos no importador C16.",
        ),
    ]
    warnings = tuple(quiz_warnings + exercise_warnings + (["materiais de projeto aguardam adaptador"] if project_materials else []))
    return ConvertedUnit(
        provenance=provenance,
        module_id=module_id,
        module_order=module_order,
        unit_order=unit_order,
        title=title,
        pedagogical_type=str(index_meta["tipo"]),
        requirement=str(index_meta["carater"]),
        depth=str(index_meta["profundidade"]),
        estimated_minutes=estimated,
        tags=tuple(tags_value),
        objective=_body_without_leading_heading(objective.body),
        topics=topics,
        summary=_body_without_leading_heading(summary.body) if summary else "",
        quiz_questions=questions,
        manual_exercises=exercises,
        completion_criterion=(
            CompletionCriterion(source_text=_body_without_leading_heading(criterion.body))
            if criterion else None
        ),
        relations=relations,
        references=references,
        private_materials=private_materials,
        project_materials=project_materials,
        source_artifacts=artifacts,
        unresolved_connection_lines=unresolved,
        field_dispositions=tuple(fields),
        warnings=warnings,
    )


def _read_artifact(repository_root: Path, phase_dir: Path, path: Path) -> SourceArtifact:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="strict")
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"frontmatter ausente ou malformado: {path.relative_to(phase_dir)}")
    metadata = yaml.load(match.group("meta"), Loader=_UniqueKeyLoader)
    if not isinstance(metadata, dict):
        raise ValueError(f"frontmatter deve ser mapa: {path.relative_to(phase_dir)}")
    artifact_id = metadata.get("arquivo_id")
    kind = metadata.get("tipo_arquivo")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise ValueError(f"arquivo_id ausente: {path.relative_to(phase_dir)}")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError(f"tipo_arquivo ausente: {path.relative_to(phase_dir)}")
    order = metadata.get("ordem")
    if order is not None and (not isinstance(order, int) or isinstance(order, bool) or order < 0):
        raise ValueError(f"ordem inválida: {path.relative_to(phase_dir)}")
    item_ids = metadata.get("itens_origem", [])
    if item_ids is None:
        item_ids = []
    if not isinstance(item_ids, list) or any(not isinstance(item, str) or not item for item in item_ids):
        raise ValueError(f"itens_origem inválido: {path.relative_to(phase_dir)}")
    topic_key = metadata.get("assunto")
    if topic_key is not None and not isinstance(topic_key, str):
        raise ValueError(f"assunto inválido: {path.relative_to(phase_dir)}")
    title = metadata.get("titulo_marco") or metadata.get("title")
    relative = path.relative_to(repository_root).as_posix()
    return SourceArtifact(
        artifact_id=artifact_id,
        kind=kind,
        relative_path=relative,
        sha256=hashlib.sha256(raw).hexdigest(),
        sha256_lf=hashlib.sha256(
            text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        ).hexdigest(),
        order=order,
        topic_key=topic_key,
        item_ids=tuple(item_ids),
        title=title if isinstance(title, str) else None,
        metadata=metadata,
        body=match.group("body").strip(),
    )


def _artifact_metadata(path: Path) -> dict[str, Any]:
    match = _FRONTMATTER.match(path.read_text(encoding="utf-8-sig"))
    if not match:
        raise ValueError(f"frontmatter ausente: {path}")
    metadata = yaml.load(match.group("meta"), Loader=_UniqueKeyLoader)
    if not isinstance(metadata, dict):
        raise ValueError(f"frontmatter inválido: {path}")
    return metadata


def _convert_topics(unit_id: str, artifacts: list[SourceArtifact]) -> tuple[TheoryTopic, ...]:
    ordered = sorted(artifacts, key=lambda item: (item.order or 0, item.relative_path))
    topics: list[TheoryTopic] = []
    seen_keys: set[str] = set()
    for index, artifact in enumerate(ordered, 1):
        key = artifact.topic_key or artifact.artifact_id
        if key in seen_keys:
            raise ValueError(f"assunto teórico duplicado em {unit_id}: {key}")
        seen_keys.add(key)
        headings = list(_HEADING.finditer(artifact.body))
        candidates = [item for item in headings if item.group("title").strip().casefold() != "teoria"]
        declared = [str(value).strip() for value in _metadata_for_artifact(artifact).get("itens_origem", [])]
        segments: list[TheorySegment] = []
        matched: list[re.Match[str]] = []
        for item_title in declared:
            candidate = next((heading for heading in candidates if heading.group("title").strip() == item_title), None)
            if candidate is None:
                raise ValueError(f"segmento declarado ausente em {artifact.relative_path}: {item_title}")
            matched.append(candidate)
        if declared and len(set(match.start() for match in matched)) != len(matched):
            raise ValueError(f"segmento teórico duplicado em {artifact.relative_path}")
        if not declared:
            if not candidates:
                raise ValueError(f"teoria sem segmentos ou itens_origem: {artifact.relative_path}")
            matched = [candidates[0]]
        matched.sort(key=lambda item: item.start())
        for segment_index, heading in enumerate(matched, 1):
            start = heading.end()
            next_heading = next(
                (candidate for candidate in headings if candidate.start() > heading.start()
                 and len(candidate.group("marks")) <= len(heading.group("marks"))),
                None,
            )
            end = next_heading.start() if next_heading else len(artifact.body)
            body = artifact.body[start:end].strip()
            ref = f"unit-{_token(unit_id)}-topic-{_token(key)}-segment-{segment_index:02d}"
            segments.append(TheorySegment(
                ref=ref,
                source_heading=heading.group("title").strip(),
                order=segment_index,
                markdown_body=body,
                source_markdown=artifact.relative_path,
                source_sha256=artifact.sha256,
            ))
        topics.append(TheoryTopic(
            ref=f"unit-{_token(unit_id)}-topic-{_token(key)}",
            title=segments[0].source_heading,
            order=index,
            segments=tuple(segments),
        ))
    return tuple(topics)


def _convert_quizzes(
    unit_id: str,
    topics: tuple[TheoryTopic, ...],
    by_kind: dict[str, list[SourceArtifact]],
) -> tuple[tuple[QuizQuestion, ...], list[str]]:
    quizzes = sorted(by_kind.get("quiz", []), key=lambda item: (item.order or 0, item.relative_path))
    answer_keys = by_kind.get("answer_key", [])
    topic_refs = {artifact.topic_key: topic.ref for artifact, topic in zip(
        sorted(by_kind.get("theory", []), key=lambda item: (item.order or 0, item.relative_path)), topics,
    ) if artifact.topic_key}
    question_models: list[QuizQuestion] = []
    warnings: list[str] = []
    seen_source_ids: set[str] = set()
    for quiz in quizzes:
        item_ids = list(quiz.item_ids)
        if not item_ids:
            raise ValueError(f"quiz sem itens_origem: {quiz.relative_path}")
        candidates = [key for key in answer_keys if _same_assessment_group(quiz, key)]
        if len(candidates) != 1:
            raise ValueError(f"gabarito não identificado univocamente para {quiz.relative_path}")
        answer = candidates[0]
        if tuple(answer.item_ids) != tuple(item_ids):
            raise ValueError(f"questões e gabarito divergem em {quiz.relative_path}")
        parsed = _parse_segmented_quiz(quiz.body, answer.body, quiz.relative_path)
        if len(parsed) != len(item_ids):
            raise ValueError(f"quantidade de itens Q diverge do parser em {quiz.relative_path}")
        topic_key = quiz.topic_key
        topic_ref = topic_refs.get(topic_key) if topic_key else None
        if topic_key and topic_ref is None:
            raise ValueError(f"quiz referencia assunto sem tópico teórico em {quiz.relative_path}")
        for item_id, parsed_question in zip(item_ids, parsed, strict=True):
            item_match = _ITEM.fullmatch(item_id)
            if not item_match or not item_id.upper().startswith("Q"):
                raise ValueError(f"ID de questão inválido em {quiz.relative_path}: {item_id}")
            if item_id in seen_source_ids:
                raise ValueError(f"ID de questão duplicado em {unit_id}: {item_id}")
            seen_source_ids.add(item_id)
            order = len(question_models) + 1
            ref = f"unit-{_token(unit_id)}-quiz-{_token(item_id)}"
            question_models.append(QuizQuestion(
                ref=ref,
                source_number=int(item_match.group("number")),
                order=order,
                topic_ref=topic_ref,
                prompt=parsed_question["prompt"],
                options=tuple(QuizOption(
                    id=f"{ref}-option-{letter.lower()}", source_letter=letter, label=label,
                ) for letter, label in parsed_question["options"]),
                correct_option_id=f"{ref}-option-{parsed_question['correct_letter'].lower()}",
                explanation=parsed_question["explanation"],
            ))
        if not topic_ref:
            warnings.append(f"quiz integrador sem assunto teórico: {quiz.relative_path}")
    if len({item.ref for item in question_models}) != len(question_models):
        raise ValueError(f"IDs de questão convertidos duplicados em {unit_id}")
    return tuple(question_models), warnings


def _convert_exercises(
    unit_id: str, by_kind: dict[str, list[SourceArtifact]],
) -> tuple[tuple[ManualExercise, ...], list[str]]:
    practices = sorted(by_kind.get("practice", []), key=lambda item: (item.order or 0, item.relative_path))
    exercises: list[ManualExercise] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for index, practice in enumerate(practices, 1):
        if not practice.item_ids:
            raise ValueError(f"prática sem itens_origem: {practice.relative_path}")
        if len(practice.item_ids) != 1:
            raise ValueError(f"prática com cardinalidade não suportada: {practice.relative_path}")
        item_id = practice.item_ids[0]
        item_match = _ITEM.fullmatch(item_id)
        if not item_match or not item_id.upper().startswith("P"):
            raise ValueError(f"ID de prática inválido: {practice.relative_path}")
        if item_id in seen:
            raise ValueError(f"ID de prática duplicado em {unit_id}: {item_id}")
        seen.add(item_id)
        heading = next((item.group("title").strip() for item in _HEADING.finditer(practice.body)
                        if not item.group("title").strip().casefold().startswith("prática")), None)
        title = heading or item_id
        exercises.append(ManualExercise(
            ref=f"unit-{_token(unit_id)}-exercise-{_token(item_id)}",
            source_number=int(item_match.group("number")),
            order=index,
            title=title,
            student_prompt=practice.body,
            grader_reference=None,
            grader_criteria=(),
            source_sha256=practice.sha256,
        ))
    return tuple(exercises), warnings


def _restricted_materials(by_kind: dict[str, list[SourceArtifact]]) -> tuple[RestrictedMaterial, ...]:
    kinds = {"answer_key", "answer_key_pratica", "rubric", "checklist"}
    rows = [artifact for kind in kinds for artifact in by_kind.get(kind, [])]
    return tuple(RestrictedMaterial(
        artifact_id=artifact.artifact_id,
        associated_item_id=artifact.item_ids[0] if artifact.item_ids else None,
        kind=cast(RestrictedKind, artifact.kind),
        relative_path=artifact.relative_path, sha256=artifact.sha256,
        content=artifact.body,
        data_classification=(
            "visibility_pending" if artifact.kind == "checklist" else "restricted_instructor"
        ),
    ) for artifact in sorted(rows, key=lambda item: (item.order or 0, item.relative_path)))


def _project_materials(by_kind: dict[str, list[SourceArtifact]]) -> tuple[ProjectMaterial, ...]:
    rows = list(by_kind.get("project_brief", [])) + list(by_kind.get("milestone", []))
    for kind in ("rubric", "checklist"):
        rows.extend(
            artifact for artifact in by_kind.get(kind, [])
            if any(item.startswith("M") or item in {"rubrica_comum", "revisao_final"}
                   for item in artifact.item_ids)
        )
    return tuple(ProjectMaterial(
        artifact_id=artifact.artifact_id,
        kind=cast(ProjectKind, artifact.kind),
        order=artifact.order or 0,
        relative_path=artifact.relative_path,
        sha256=artifact.sha256,
        content=artifact.body,
        source_item_ids=artifact.item_ids,
    ) for artifact in sorted(rows, key=lambda item: (item.order or 0, item.relative_path)))


def _convert_relations(text: str) -> tuple[tuple[CurricularRelation, ...], tuple[str, ...]]:
    relations: list[CurricularRelation] = []
    unresolved: list[str] = []
    for line in text.splitlines():
        match = _RELATION.match(line)
        if not match:
            if "[[" in line:
                unresolved.append(line.strip())
            continue
        kind = match.group("kind")
        if kind.casefold() == "projeto acumulado":
            unresolved.append(line.strip())
            continue
        relation_kind = next(
            (item for item in _RELATION_KEYS if item.casefold() == kind.casefold()), None,
        )
        if relation_kind is None:
            unresolved.append(line.strip())
            continue
        links = list(_WIKILINK.finditer(match.group("links")))
        if not links:
            unresolved.append(line.strip())
            continue
        for link in links:
            raw_target = link.group("target").strip()
            page, _, anchor = raw_target.partition("#")
            label = (link.group("label") or anchor or page).strip()
            relations.append(CurricularRelation(
                source_kind=cast(RelationKind, relation_kind), target_path=raw_target,
                target_anchor=anchor or None, display_label=label,
                target_node_ref=None, enforced=False, source_line=line.strip(),
            ))
        outside_text = _WIKILINK.sub("", match.group("links")).strip()
        if outside_text and outside_text not in {"e", "and"}:
            unresolved.append(line.strip())
    unique: dict[tuple[str, str, str], CurricularRelation] = {}
    for relation in relations:
        unique[(relation.source_kind, relation.target_path, relation.source_line)] = relation
    return tuple(unique.values()), tuple(unresolved)


def _convert_references(unit_id: str, artifact: SourceArtifact | None) -> tuple[ReferenceItem, ...]:
    if artifact is None:
        return ()
    rows: list[ReferenceItem] = []
    pattern = re.compile(r"^\s*-\s+\*\*(?P<title>.+?)\*\*\s*·\s*(?P<url>https?://\S+)\s*·\s*(?P<desc>.*)$")
    for line in artifact.body.splitlines():
        if not line.strip().startswith("-"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError(f"referência não reconhecida em {artifact.relative_path}")
        order = len(rows) + 1
        rows.append(ReferenceItem(
            ref=f"unit-{_token(unit_id)}-reference-{order:03d}",
            order=order,
            title=match.group("title").strip(),
            url=match.group("url").rstrip(".,)"),
            description=match.group("desc").strip(),
            source_markdown=artifact.relative_path,
        ))
    return tuple(rows)


def _metadata_for_artifact(artifact: SourceArtifact) -> dict[str, Any]:
    return artifact.metadata


def _same_assessment_group(quiz: SourceArtifact, answer: SourceArtifact) -> bool:
    return (
        quiz.topic_key == answer.topic_key
        and quiz.order == answer.order
        and quiz.item_ids == answer.item_ids
    )


def _parse_segmented_quiz(
    question_document: str, answer_document: str, source_path: str,
) -> list[dict[str, Any]]:
    """Parse the split source pair without changing either source document."""
    question_section = _section_or_document(question_document, "Questões")
    answer_section = _section_or_document(answer_document, "Gabarito comentado")
    parsed: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active_option: str | None = None
    for line in question_section.splitlines():
        question = _QUESTION_LINE.match(line)
        option = _OPTION_LINE.match(line)
        if question:
            if current:
                parsed.append(current)
            text = question.group("text")
            inline = list(_INLINE_OPTION.finditer(text))
            current = {"number": int(question.group("number")), "prompt": [], "options": []}
            active_option = None
            if inline:
                current["prompt"].append(text[:inline[0].start()].strip())
                for index, marker in enumerate(inline):
                    end = inline[index + 1].start() if index + 1 < len(inline) else len(text)
                    current["options"].append([marker.group("letter"), text[marker.end():end].strip()])
                active_option = inline[-1].group("letter")
            else:
                current["prompt"].append(text)
        elif option and current:
            current["options"].append([option.group("letter"), option.group("text")])
            active_option = option.group("letter")
        elif current and line.strip():
            if active_option:
                current["options"][-1][1] += "\n" + line.strip()
            else:
                current["prompt"].append(line.strip())
    if current:
        parsed.append(current)
    answers: dict[int, tuple[str, str]] = {}
    active_answer: int | None = None
    answer_sequence = 0
    for line in answer_section.splitlines():
        answer = _ANSWER_LINE.match(line)
        compact = _COMPACT_ANSWER.match(line)
        if answer or compact:
            match = answer or compact
            assert match is not None
            if match.group("number"):
                number = int(match.group("number"))
            else:
                if answer_sequence >= len(parsed):
                    raise ValueError(f"resposta sem questão correspondente em {source_path}")
                number = parsed[answer_sequence]["number"]
            answer_sequence += 1
            if number in answers:
                raise ValueError(f"resposta duplicada em {source_path}")
            answers[number] = (match.group("letter").upper(), match.group("text").strip())
            active_answer = number
        elif active_answer is not None and line.strip():
            letter, explanation = answers[active_answer]
            answers[active_answer] = (letter, (explanation + "\n" + line.strip()).strip())
    numbers = [item["number"] for item in parsed]
    if not parsed or len(numbers) != len(set(numbers)) or set(numbers) != set(answers):
        raise ValueError(f"questões e gabarito não correspondem exatamente em {source_path}")
    result: list[dict[str, Any]] = []
    for item in parsed:
        options = [(letter, text.strip()) for letter, text in item["options"]]
        correct, explanation = answers[item["number"]]
        letters = [letter for letter, _ in options]
        if len(options) < 2 or len(letters) != len(set(letters)) or correct not in letters:
            raise ValueError(f"alternativas/gabarito incompatíveis em {source_path}")
        result.append({
            "source_number": item["number"],
            "prompt": "\n".join(item["prompt"]).strip(),
            "options": tuple(options),
            "correct_letter": correct,
            "explanation": explanation,
        })
    return result


def _section_body(document: str, title: str) -> str:
    headings = list(_HEADING.finditer(document))
    target = next((heading for heading in headings if heading.group("title").strip() == title), None)
    if target is None:
        raise ValueError(f"seção {title} ausente")
    end_heading = next(
        (heading for heading in headings if heading.start() > target.start()
         and len(heading.group("marks")) <= len(target.group("marks"))),
        None,
    )
    return document[target.end():(end_heading.start() if end_heading else len(document))].strip()


def _section_or_document(document: str, title: str) -> str:
    if any(heading.group("title").strip() == title for heading in _HEADING.finditer(document)):
        return _section_body(document, title)
    # Several migrated files intentionally omit a wrapper heading and start
    # directly with the numbered item. Preserve that body verbatim.
    return document.strip()


def _body_without_leading_heading(text: str) -> str:
    match = _HEADING.match(text)
    return text[match.end():].strip() if match else text.strip()


def _one(by_kind: dict[str, list[SourceArtifact]], kind: str, unit_id: str) -> SourceArtifact:
    values = by_kind.get(kind, [])
    if len(values) != 1:
        raise ValueError(f"esperado exatamente um artefato {kind} em {unit_id}; encontrado {len(values)}")
    return values[0]


def _optional_one(by_kind: dict[str, list[SourceArtifact]], kind: str, unit_id: str) -> SourceArtifact | None:
    values = by_kind.get(kind, [])
    if len(values) > 1:
        raise ValueError(f"artefato {kind} duplicado em {unit_id}")
    return values[0] if values else None


def _unit_id(folder_name: str) -> str:
    match = _UNIT_DIRECTORY.match(folder_name)
    if not match:
        raise ValueError(f"diretório de unidade fora do padrão: {folder_name}")
    return f"{match.group('phase')}.{match.group('unit')}"


def _unit_sort_key(unit_id: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)", unit_id)
    if not match:
        raise ValueError(f"identificador de unidade inválido: {unit_id}")
    return int(match.group(1)), int(match.group(2))


def _token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    token = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    if not token:
        raise ValueError("valor não pode gerar ID estável vazio")
    return token


def _target_unit_id(target_path: str) -> str | None:
    match = re.search(r"(?<!\d)(\d+\.\d+)(?!\d)", target_path)
    return match.group(1) if match else None


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _all_node_refs(nodes: list[dict[str, Any]]) -> set[str]:
    return {node["ref"] for node in _flatten_nodes(nodes)}


def _flatten_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for node in nodes:
        result.append(node)
        result.extend(_flatten_nodes(node.get("children", [])))
    return result


def _collect_blocks(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for node in _flatten_nodes(nodes):
        blocks.extend(node.get("blocks", []))
    return blocks


def _quiz_block(question: QuizQuestion) -> dict[str, Any]:
    return {
        "ref": question.ref,
        "type": "quiz",
        "title": f"Questão {question.order}",
        "status": "draft",
        "data": {
            "activity_schema_version": question.activity_schema_version,
            "prompt": question.prompt,
            "options": [{"id": option.id, "label": option.label} for option in question.options],
            "correct_option_id": question.correct_option_id,
            "feedback": {"correct": question.explanation, "incorrect": question.explanation},
        },
    }


def _find_node(nodes: list[dict[str, Any]], ref: str) -> dict[str, Any]:
    for node in nodes:
        if node["ref"] == ref:
            return node
        try:
            return _find_node(node.get("children", []), ref)
        except LookupError:
            pass
    raise LookupError(ref)


def _validate_payload_refs(payload: dict[str, Any]) -> None:
    nodes = _flatten_nodes(payload["nodes"])
    node_refs = [node["ref"] for node in nodes]
    if len(node_refs) != len(set(node_refs)):
        raise ValueError("payload contém refs de nó duplicados")
    block_refs = [block["ref"] for block in _collect_blocks(payload["nodes"])]
    if len(block_refs) != len(set(block_refs)):
        raise ValueError("payload contém refs de bloco duplicados")
    if set(node_refs) & set(block_refs):
        raise ValueError("refs de nó e bloco colidem")
    node_ref_set = set(node_refs)
    for relation in payload["relations"]:
        if relation["from"] not in node_ref_set or relation["to"] not in node_ref_set:
            raise ValueError("relação aponta para nó fora do payload")
