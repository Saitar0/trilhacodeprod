"""Typed, loss-accounted representation of the isolated Beta 3 pilot unit.

This module composes the bounded Beta 2 parser. It does not replace the
migration contract or write to the operational database. Its import payload is
for an explicitly disposable test harness only.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .experimental_beta_curriculum_converter import (
    CONVERTER_VERSION as BETA2_CONVERTER_VERSION,
)
from .experimental_beta_curriculum_converter import (
    CurriculumConversionError,
    PilotUnit,
    convert_markdown_unit,
)

FIDELITY_CONVERTER_VERSION = "beta3-fidelity-adapter/1.0"
IMPORT_SHAPE = "track/options/nodes/relations"
_SHA256 = r"^[0-9a-f]{64}$"
_H3 = re.compile(r"(?m)^###\s+(?P<title>.+?)\s*$")
_WIKILINK = re.compile(r"\[\[(?P<target>[^\]|]+)(?:\|(?P<label>[^\]]+))?\]\]")
_CONNECTION_PREFIX = re.compile(r"^\s*-\s*(?P<kind>Complementar|Relacionado|Pré-requisito|Pré-requisitos):\s*(?P<link>.+?)\s*$", re.I)
_RELATION_KIND_MAP: dict[str, Literal["Complementar", "Relacionado", "Pré-requisito", "Pré-requisitos"]] = {
    "complementar": "Complementar",
    "relacionado": "Relacionado",
    "pré-requisito": "Pré-requisito",
    "pré-requisitos": "Pré-requisitos",
}

# The source Markdown has eight H3 sections. The migration's five-topic outline
# groups them without deleting or rewriting any source section.
TOPIC_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("topic-01-problema-programa", "Do problema ao programa", ("Do problema ao programa",)),
    (
        "topic-02-aplicacoes-locais-web-camadas",
        "Aplicações locais e aplicações web",
        ("Aplicações locais e aplicações web", "Frontend, backend e banco de dados"),
    ),
    (
        "topic-03-cliente-servidor-fluxo-pagina",
        "Cliente e servidor",
        ("Cliente e servidor", "O que acontece ao abrir uma página"),
    ),
    ("topic-04-http", "Requisição e resposta HTTP", ("Requisição e resposta HTTP",)),
    (
        "topic-05-api-visao-integrada",
        "APIs: uma interface de comunicação",
        ("APIs: uma interface de comunicação", "Uma visão integrada"),
    ),
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
    )


class SourceProvenance(_StrictModel):
    source_id: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    source_revision: str = Field(min_length=1)
    source_status: str = Field(min_length=1)
    source_sha256: str = Field(pattern=_SHA256)
    source_sha256_lf: str = Field(pattern=_SHA256)
    converter_version: str = Field(min_length=1)


class TheorySegment(_StrictModel):
    ref: str = Field(min_length=1)
    source_heading: str = Field(min_length=1)
    order: int = Field(ge=1)
    markdown_body: str
    source_markdown: str = Field(min_length=1)
    source_sha256: str = Field(pattern=_SHA256)


class TheoryTopic(_StrictModel):
    ref: str = Field(min_length=1)
    title: str = Field(min_length=1)
    order: int = Field(ge=1)
    segments: tuple[TheorySegment, ...] = Field(min_length=1)


class QuizOption(_StrictModel):
    id: str = Field(min_length=1)
    source_letter: str = Field(min_length=1, max_length=1)
    label: str = Field(min_length=1)


class QuizQuestion(_StrictModel):
    ref: str = Field(min_length=1)
    source_number: int = Field(ge=1)
    order: int = Field(ge=1)
    topic_ref: str | None = None
    activity_schema_version: Literal[1] = 1
    prompt: str = Field(min_length=1)
    options: tuple[QuizOption, ...] = Field(min_length=2, max_length=8)
    correct_option_id: str = Field(min_length=1)
    explanation: str

    @model_validator(mode="after")
    def validate_options(self) -> QuizQuestion:
        ids = [option.id for option in self.options]
        letters = [option.source_letter for option in self.options]
        if len(ids) != len(set(ids)) or len(letters) != len(set(letters)):
            raise ValueError("alternativas duplicadas")
        if self.correct_option_id not in ids:
            raise ValueError("gabarito não corresponde a uma alternativa")
        return self

    def student_projection(self) -> dict[str, Any]:
        """Return only fields appropriate before an assessment is corrected."""
        return {
            "id": self.ref,
            "order": self.order,
            "prompt": self.prompt,
            "options": [{"id": option.id, "label": option.label} for option in self.options],
        }

    def restricted_projection(self) -> dict[str, Any]:
        """Authoring/grading view; callers must enforce an external ACL."""
        return {
            **self.student_projection(),
            "correct_option_id": self.correct_option_id,
            "explanation": self.explanation,
        }


class ManualExercise(_StrictModel):
    ref: str = Field(min_length=1)
    source_number: int = Field(ge=1)
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    student_prompt: str = Field(min_length=1)
    grader_reference: str | None = None
    grader_criteria: tuple[str, ...] = ()
    grader_data_classification: Literal["restricted_pending_policy"] = "restricted_pending_policy"
    source_sha256: str = Field(pattern=_SHA256)

    def student_projection(self) -> dict[str, Any]:
        return {"id": self.ref, "order": self.order, "title": self.title, "prompt": self.student_prompt}

    def restricted_projection(self) -> dict[str, Any]:
        """Instructor-only data; this model does not itself enforce an ACL."""
        return {
            **self.student_projection(),
            "reference_answer": self.grader_reference,
            "criteria": list(self.grader_criteria),
        }


class CompletionCriterion(_StrictModel):
    source_text: str = Field(min_length=1)
    interpretation: Literal["unstructured_text"] = "unstructured_text"
    automated_rule: None = None
    requires_human_policy_decision: Literal[True] = True


class CurricularRelation(_StrictModel):
    source_kind: Literal["Complementar", "Relacionado", "Pré-requisito", "Pré-requisitos"]
    target_path: str = Field(min_length=1)
    target_anchor: str | None = None
    display_label: str | None = None
    target_node_ref: None = None
    enforced: Literal[False] = False
    source_line: str = Field(min_length=1)


class ReferenceItem(_StrictModel):
    ref: str = Field(min_length=1)
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    description: str
    source_markdown: str = Field(min_length=1)
    description_destination: Literal["requires_adapter"] = "requires_adapter"


class FieldDisposition(_StrictModel):
    source: str = Field(min_length=1)
    destination: str | None = None
    status: Literal[
        "SUPPORTED_EXACT",
        "SUPPORTED_WITH_TRANSFORMATION",
        "REQUIRES_ADAPTER",
        "UNSUPPORTED",
        "SOURCE_ABSENT",
        "NOT_VERIFIED",
    ]
    privacy: Literal["public", "restricted", "metadata", "pending_policy"]
    reason: str = Field(min_length=1)


class CurriculumFidelityUnit(_StrictModel):
    schema_version: Literal[1] = 1
    converter_version: str = FIDELITY_CONVERTER_VERSION
    provenance: SourceProvenance
    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    pedagogical_type: str = Field(min_length=1)
    requirement: str = Field(min_length=1)
    depth: str = Field(min_length=1)
    tags: tuple[str, ...] = ()
    estimated_minutes: int | None = Field(default=None, ge=0)
    topics: tuple[TheoryTopic, ...] = Field(min_length=1)
    summary: str = Field(min_length=1)
    quiz_questions: tuple[QuizQuestion, ...] = Field(min_length=1)
    manual_exercises: tuple[ManualExercise, ...] = Field(min_length=1)
    completion_criterion: CompletionCriterion
    relations: tuple[CurricularRelation, ...] = ()
    references: tuple[ReferenceItem, ...] = ()
    source_section_order: tuple[str, ...]
    unmapped_sections: tuple[tuple[str, str], ...] = ()
    field_dispositions: tuple[FieldDisposition, ...]

    @model_validator(mode="after")
    def validate_stable_identity_and_order(self) -> CurriculumFidelityUnit:
        topic_refs = [topic.ref for topic in self.topics]
        if len(topic_refs) != len(set(topic_refs)):
            raise ValueError("IDs de tópico duplicados")
        if [topic.order for topic in self.topics] != list(range(1, len(self.topics) + 1)):
            raise ValueError("ordem de tópicos deve ser contínua")
        segment_refs = [segment.ref for topic in self.topics for segment in topic.segments]
        all_refs = segment_refs + [q.ref for q in self.quiz_questions]
        all_refs += [exercise.ref for exercise in self.manual_exercises]
        all_refs += [reference.ref for reference in self.references]
        if len(all_refs) != len(set(all_refs)):
            raise ValueError("IDs de conteúdo duplicados")
        if [question.order for question in self.quiz_questions] != list(
            range(1, len(self.quiz_questions) + 1)
        ):
            raise ValueError("ordem de questões deve preservar a sequência da fonte")
        if [exercise.order for exercise in self.manual_exercises] != list(
            range(1, len(self.manual_exercises) + 1)
        ):
            raise ValueError("ordem de exercícios deve preservar a sequência da fonte")
        if len({question.source_number for question in self.quiz_questions}) != len(self.quiz_questions):
            raise ValueError("números de questão duplicados")
        if len({exercise.source_number for exercise in self.manual_exercises}) != len(self.manual_exercises):
            raise ValueError("números de exercício duplicados")
        normalized_tags = [tag.strip().casefold() for tag in self.tags]
        if any(not tag for tag in normalized_tags) or len(normalized_tags) != len(set(normalized_tags)):
            raise ValueError("tags vazias ou duplicadas")
        for question in self.quiz_questions:
            if question.topic_ref is not None and question.topic_ref not in topic_refs:
                raise ValueError("questão referencia tópico inexistente")
        return self

    @property
    def unsupported_destinations(self) -> tuple[str, ...]:
        return tuple(
            f"{field.source}: {field.reason}"
            for field in self.field_dispositions
            if field.status in {"REQUIRES_ADAPTER", "UNSUPPORTED", "NOT_VERIFIED"}
        )

    def to_import_payload(self) -> dict[str, Any]:
        """Project only fields supported by the C16 import schema.

        Private exercise answers/rubrics, completion automation and unresolved
        links are deliberately excluded. Quiz secrets remain in draft content
        documents and rely on the existing reader/publication projections.
        """
        token = _stable_token(self.provenance.source_id)
        blocks: list[dict[str, Any]] = []
        for topic in self.topics:
            for segment in topic.segments:
                blocks.append({
                    "ref": segment.ref,
                    "type": "theory_text",
                    "title": segment.source_heading,
                    "status": "draft",
                    "data": {"body": segment.markdown_body},
                })
        blocks.append({
            "ref": f"{token}-summary-001",
            "type": "summary",
            "title": "Resumo",
            "status": "draft",
            "data": {"body": self.summary},
        })
        for question in self.quiz_questions:
            blocks.append({
                "ref": question.ref,
                "type": "quiz",
                "title": f"Questão {question.source_number}",
                "status": "draft",
                "data": {
                    "activity_schema_version": question.activity_schema_version,
                    "prompt": question.prompt,
                    "options": [{"id": option.id, "label": option.label} for option in question.options],
                    "correct_option_id": question.correct_option_id,
                    "feedback": {"correct": question.explanation, "incorrect": question.explanation},
                },
            })
        for exercise in self.manual_exercises:
            blocks.append({
                "ref": exercise.ref,
                "type": "exercise_open",
                "title": exercise.title,
                "status": "draft",
                "data": {"prompt": exercise.student_prompt, "grading": "manual"},
            })
        for reference in self.references:
            blocks.append({
                "ref": reference.ref,
                "type": "reference",
                "title": reference.title,
                "status": "draft",
                "data": {"citation": reference.title, "url": reference.url},
            })

        node: dict[str, Any] = {
            "ref": f"{token}-unit",
            "kind": "submodule",
            "title": self.title,
            "status": "draft",
            "description": self.objective,
            "pedagogical_type": self.pedagogical_type,
            "requirement": self.requirement,
            "depth": self.depth,
            "tags": list(self.tags),
            "blocks": blocks,
        }
        if self.estimated_minutes is not None:
            node["estimated_minutes"] = self.estimated_minutes
        return {
            "track": {
                "title": f"[Beta 3 isolada] {self.title}",
                "slug": f"beta3-pilot-{token}",
                "description": "Unidade sintética em rascunho para teste de fidelidade e recuperação.",
                "visibility": "private",
                "hierarchy": ["phase", "module", "submodule", "topic"],
            },
            "options": {"create_missing_tags": True},
            "nodes": [node],
            "relations": [],
        }

    def to_manifest(self) -> dict[str, Any]:
        payload = self.to_import_payload()
        block_counts: dict[str, int] = {}
        for block in payload["nodes"][0]["blocks"]:
            block_counts[block["type"]] = block_counts.get(block["type"], 0) + 1
        canonical_payload = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        return {
            "manifest_schema": "trilhacode.beta3.curriculum-fidelity/1.0",
            "source": self.provenance.model_dump(),
            "converter_versions": {
                "beta2_parser": BETA2_CONVERTER_VERSION,
                "fidelity_adapter": self.converter_version,
            },
            "source_counts": {
                "topics": len(self.topics),
                "theory_segments": sum(len(topic.segments) for topic in self.topics),
                "quiz_questions": len(self.quiz_questions),
                "manual_exercises": len(self.manual_exercises),
                "relations": len(self.relations),
                "references": len(self.references),
            },
            "source_section_order": list(self.source_section_order),
            "unmapped_sections": [
                {
                    "name": name,
                    "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "character_count": len(text),
                    "included_in_import_payload": False,
                }
                for name, text in self.unmapped_sections
            ],
            "destination": {
                "import_shape": IMPORT_SHAPE,
                "track_slug": payload["track"]["slug"],
                "node_ref": payload["nodes"][0]["ref"],
                "block_counts": block_counts,
                "block_refs": [block["ref"] for block in payload["nodes"][0]["blocks"]],
                "status": "draft",
                "visibility": "private",
                "node_metadata": {
                    "tags": list(self.tags),
                    "estimated_minutes": self.estimated_minutes,
                    "pedagogical_type": self.pedagogical_type,
                    "requirement": self.requirement,
                    "depth": self.depth,
                },
                "payload_sha256": hashlib.sha256(canonical_payload).hexdigest(),
            },
            "theory_topics": [
                {
                    "ref": topic.ref,
                    "order": topic.order,
                    "title": topic.title,
                    "segments": [segment.ref for segment in topic.segments],
                }
                for topic in self.topics
            ],
            "field_dispositions": [field.model_dump() for field in self.field_dispositions],
            "unsupported_destinations": list(self.unsupported_destinations),
            "private_content_in_manifest": False,
            "no_source_write": True,
            "no_publication": True,
        }


def convert_fidelity_unit(
    source: bytes | str,
    *,
    source_path: str,
    source_revision: str,
    expected_source_sha256: str,
) -> CurriculumFidelityUnit:
    """Parse the approved-for-isolated-experiment source and fail on drift."""
    parsed: PilotUnit = convert_markdown_unit(
        source,
        source_path=source_path,
        source_revision=source_revision,
    )
    if parsed.source_id != "1.1":
        raise CurriculumConversionError("o piloto Beta 3 exige a unidade de origem 1.1")
    if parsed.source_sha256 != expected_source_sha256:
        raise CurriculumConversionError("SHA-256 da fonte difere do manifesto Beta 2")

    topics = _parse_topics(parsed)
    tags_value = parsed.frontmatter.get("tags", [])
    if not isinstance(tags_value, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags_value):
        raise CurriculumConversionError("frontmatter.tags deve ser uma lista de rótulos não vazios")
    estimated_minutes = _parse_optional_nonnegative_int(
        parsed.frontmatter.get("estimativa_minutos"), "frontmatter.estimativa_minutos",
    )
    questions = tuple(
        QuizQuestion(
            ref=question.stable_ref,
            source_number=question.source_number,
            order=index,
            topic_ref=None,
            prompt=question.prompt,
            options=tuple(
                QuizOption(
                    id=f"{question.stable_ref}-option-{letter.lower()}",
                    source_letter=letter,
                    label=label,
                )
                for letter, label in question.options
            ),
            correct_option_id=(
                f"{question.stable_ref}-option-{question.correct_letter.lower()}"
            ),
            explanation=question.explanation,
        )
        for index, question in enumerate(parsed.quiz, 1)
    )
    if len(questions) != 5:
        raise CurriculumConversionError(f"esperadas cinco questões; encontradas {len(questions)}")
    if len(parsed.exercises) != 3:
        raise CurriculumConversionError(
            f"esperados três exercícios manuais; encontrados {len(parsed.exercises)}"
        )
    exercises = tuple(
        ManualExercise(
            ref=exercise.stable_ref,
            source_number=exercise.source_number,
            order=index,
            title=exercise.title,
            student_prompt=exercise.student_prompt,
            grader_reference=exercise.instructor_reference,
            grader_criteria=exercise.criteria,
            source_sha256=hashlib.sha256(exercise.student_prompt.encode("utf-8")).hexdigest(),
        )
        for index, exercise in enumerate(parsed.exercises, 1)
    )
    references = tuple(
        ReferenceItem(
            ref=reference.stable_ref,
            order=index,
            title=reference.title,
            url=reference.url,
            description=reference.description,
            source_markdown=reference.raw,
        )
        for index, reference in enumerate(parsed.references, 1)
    )
    relations = _parse_relations(parsed.connections)

    return CurriculumFidelityUnit(
        provenance=SourceProvenance(
            source_id=parsed.source_id,
            source_path=parsed.source_path,
            source_revision=parsed.source_revision,
            source_status=_required_frontmatter_text(parsed.frontmatter, "status"),
            source_sha256=parsed.source_sha256,
            source_sha256_lf=parsed.source_sha256_lf,
            converter_version=BETA2_CONVERTER_VERSION,
        ),
        title=parsed.title,
        objective=parsed.objective,
        pedagogical_type=_required_frontmatter_text(parsed.frontmatter, "tipo"),
        requirement=_required_frontmatter_text(parsed.frontmatter, "carater"),
        depth=_required_frontmatter_text(parsed.frontmatter, "profundidade"),
        tags=tuple(tags_value),
        estimated_minutes=estimated_minutes,
        topics=topics,
        summary=parsed.summary,
        quiz_questions=questions,
        manual_exercises=exercises,
        completion_criterion=CompletionCriterion(source_text=parsed.completion_criteria),
        relations=relations,
        references=references,
        source_section_order=tuple(parsed.raw_sections),
        unmapped_sections=tuple(
            (name, text) for name, text in parsed.raw_sections.items()
            if name not in {
                "Objetivo", "Teoria", "Resumo", "Verificação — quiz",
                "Prática — três níveis", "Critério de conclusão", "Conexões", "Referências",
            }
        ),
        field_dispositions=_field_dispositions(parsed),
    )


def _parse_topics(parsed: PilotUnit) -> tuple[TheoryTopic, ...]:
    matches = list(_H3.finditer(parsed.theory))
    found: dict[str, tuple[int, str, str]] = {}
    for index, match in enumerate(matches):
        heading = match.group("title").strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(parsed.theory)
        raw = parsed.theory[match.start():end]
        body = parsed.theory[match.end():end]
        if heading in found:
            raise CurriculumConversionError(f"subtítulo teórico duplicado: {heading}")
        found[heading] = (index + 1, body, raw)

    expected = [heading for _, _, group in TOPIC_GROUPS for heading in group]
    if set(found) != set(expected) or len(found) != len(expected):
        missing = sorted(set(expected) - set(found))
        unknown = sorted(set(found) - set(expected))
        raise CurriculumConversionError(
            f"segmentação teórica difere do mapa aprovado; ausentes={missing}, desconhecidos={unknown}"
        )

    topics: list[TheoryTopic] = []
    flattened_order: list[int] = []
    for topic_order, (slug, title, headings) in enumerate(TOPIC_GROUPS, 1):
        segments = []
        for local_order, heading in enumerate(headings, 1):
            source_order, body, raw = found[heading]
            flattened_order.append(source_order)
            segment_slug = _stable_token(heading)
            segments.append(TheorySegment(
                ref=f"unit-1-1-{slug}-segment-{local_order:02d}-{segment_slug}",
                source_heading=heading,
                order=local_order,
                markdown_body=body,
                source_markdown=raw,
                source_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            ))
        topics.append(TheoryTopic(
            ref=f"unit-1-1-{slug}",
            title=title,
            order=topic_order,
            segments=tuple(segments),
        ))
    if flattened_order != sorted(flattened_order):
        raise CurriculumConversionError("o agrupamento de teoria alteraria a ordem da fonte")
    if "".join(segment.source_markdown for topic in topics for segment in topic.segments) != parsed.theory:
        raise CurriculumConversionError("a segmentação não recompõe exatamente a teoria da fonte")
    return tuple(topics)


def _parse_relations(text: str) -> tuple[CurricularRelation, ...]:
    relations: list[CurricularRelation] = []
    for line in text.splitlines():
        prefix = _CONNECTION_PREFIX.match(line)
        if not prefix:
            continue
        link = _WIKILINK.search(prefix.group("link"))
        if not link:
            continue
        target = link.group("target").strip()
        path, separator, anchor = target.partition("#")
        relations.append(CurricularRelation(
            source_kind=_RELATION_KIND_MAP[prefix.group("kind").casefold()],
            target_path=path.strip(),
            target_anchor=anchor.strip() if separator else None,
            display_label=(link.group("label") or "").strip() or None,
            source_line=line,
        ))
    return tuple(relations)


def _field_dispositions(parsed: PilotUnit) -> tuple[FieldDisposition, ...]:
    dispositions = [
        FieldDisposition(source="frontmatter.key", destination="provenance.source_id", status="SUPPORTED_EXACT", privacy="metadata", reason="Chave identificadora preservada como identidade de origem; refs de destino são derivadas deterministicamente."),
        FieldDisposition(source="frontmatter.title", destination="nodes.title", status="SUPPORTED_EXACT", privacy="public", reason="Título preservado sem reescrita."),
        FieldDisposition(source="frontmatter.status", destination="track/node/blocks.status=draft", status="SUPPORTED_WITH_TRANSFORMATION", privacy="metadata", reason="Estado da fonte fica no contrato; destino permanece rascunho privado independentemente do estado de origem."),
        FieldDisposition(source="frontmatter.tipo/carater/profundidade", destination="nodes.pedagogical_type/requirement/depth", status="SUPPORTED_EXACT", privacy="metadata", reason="Valores da fonte são preservados e validados pelo importador contra taxonomia disponível."),
        FieldDisposition(source="frontmatter.tags", destination="nodes.tags", status="SUPPORTED_EXACT", privacy="metadata", reason="Rótulos e ordem são preservados; o importador pode criar tags sintéticas ausentes no banco descartável."),
        FieldDisposition(source="frontmatter.estimativa_minutos", destination="nodes.estimated_minutes", status="SUPPORTED_EXACT", privacy="metadata", reason="Duração é parseada como inteiro não negativo e validada pelo contrato do importador."),
        FieldDisposition(source="Teoria / cinco tópicos e oito segmentos H3", destination="content_blocks.theory_text", status="SUPPORTED_WITH_TRANSFORMATION", privacy="public", reason="Cada segmento é um bloco ordenado no mesmo nó; a associação ao tópico fica no import_ref estável, pois o destino não possui campo de agrupamento."),
        FieldDisposition(source="Objetivo", destination="nodes.description", status="SUPPORTED_EXACT", privacy="public", reason="Texto preservado sem reescrita."),
        FieldDisposition(source="Resumo", destination="content_blocks.summary.data.body", status="SUPPORTED_EXACT", privacy="public", reason="Texto preservado sem reescrita."),
        FieldDisposition(source="Quiz / enunciados e alternativas", destination="content_blocks.quiz.data", status="SUPPORTED_WITH_TRANSFORMATION", privacy="public", reason="Uma questão por bloco com schema de atividade v1; ordem preservada no nó."),
        FieldDisposition(source="Quiz / gabaritos e explicações", destination="content_blocks.quiz.data.correct_option_id/feedback", status="SUPPORTED_WITH_TRANSFORMATION", privacy="restricted", reason="Persistidos apenas em draft; projeções reais public_activity e _student_block omitem esses campos; publicação não foi exercitada."),
        FieldDisposition(source="Exercícios / enunciados", destination="content_blocks.exercise_open.data.prompt", status="SUPPORTED_EXACT", privacy="public", reason="Somente o texto destinado ao aluno é enviado ao importador."),
        FieldDisposition(source="Exercícios / referências e critérios do corretor", destination=None, status="REQUIRES_ADAPTER", privacy="restricted", reason="O schema de bloco não fornece ACL separada e o leitor não oculta rubric/criteria; conteúdo mantido somente no contrato restrito."),
        FieldDisposition(source="Critério de conclusão", destination=None, status="REQUIRES_ADAPTER", privacy="public", reason="Texto preservado; nenhum campo operacional define sua semântica ou separa progresso de domínio."),
        FieldDisposition(source="Conexões curriculares", destination=None, status="REQUIRES_ADAPTER", privacy="metadata", reason="Alvos são links editoriais sem IDs de nó resolvidos no escopo piloto; relação não é inventada."),
        FieldDisposition(source="Referências / título e URL", destination="content_blocks.reference.data.citation/url", status="SUPPORTED_WITH_TRANSFORMATION", privacy="public", reason="Título e URL persistem em campos aceitos pelo schema atual."),
        FieldDisposition(source="Referências / descrição", destination=None, status="REQUIRES_ADAPTER", privacy="public", reason="O bloco reference atual declara apenas citation e url; a descrição permanece no contrato intermediário."),
        FieldDisposition(source="Proveniência / caminho, revisão e hash", destination="manifesto Beta 3", status="SUPPORTED_WITH_TRANSFORMATION", privacy="metadata", reason="Manifesto reproduzível; o importador legado não grava hash/revisão nos documentos."),
    ]
    represented_sections = {
        "Objetivo", "Teoria", "Resumo", "Verificação — quiz",
        "Prática — três níveis", "Critério de conclusão", "Conexões", "Referências",
    }
    dispositions.extend(
        FieldDisposition(
            source=f"Seção não mapeada: {name}", destination=None,
            status="REQUIRES_ADAPTER", privacy="pending_policy",
            reason="A seção é mantida no contrato intermediário e no manifesto apenas por hash; não é importada.",
        )
        for name in parsed.raw_sections if name not in represented_sections
    )
    return tuple(dispositions)


def _stable_token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    token = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return token or "unit"


def _parse_optional_nonnegative_int(value: Any, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise CurriculumConversionError(f"{field_name} deve ser um inteiro não negativo")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise CurriculumConversionError(f"{field_name} deve ser um inteiro não negativo") from exc
    if parsed < 0 or str(parsed) != str(value).strip():
        raise CurriculumConversionError(f"{field_name} deve ser um inteiro não negativo")
    return parsed


def _required_frontmatter_text(frontmatter: dict[str, Any], key: str) -> str:
    value = frontmatter.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CurriculumConversionError(f"frontmatter.{key} ausente ou inválido")
    return value
