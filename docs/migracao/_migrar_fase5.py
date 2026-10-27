from __future__ import annotations
import argparse, copy, csv, hashlib, json, posixpath, re, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine
import _migrar_fase4 as f4

MANIFEST = "docs/migracao/mapa_de_migracao_fase5.yml"
SCRIPT = "docs/migracao/_migrar_fase5.py"
BASE = "36247635f007de44deb064573101a09a6ac10a7c"
DEST = "docs/courses/trilhacode/Conteudos_migrado/Fase_5"
JSON = "docs/courses/trilhacode/trilha-code-bulk-import.json"
PHASE_DOCS = [
    "docs/courses/trilhacode/Fase_5_Backend_e_Arquitetura.md",
    "docs/courses/trilhacode/Referencias_Fase_5.md",
    "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md",
]
REPORTS = [
    "docs/migracao/relatorio_mapeamento_fase5.csv",
    "docs/migracao/relatorio_validacao_fase5.md",
    "docs/migracao/auditoria_final_fase5.md",
]
ALLOW = {
    "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
    "docs/migracao/PLANEJAMENTO_FASE5.md",
    MANIFEST,
    SCRIPT,
}
ORDER = [
    "17.1", "17.2", "18.1", "18.2", "18.3", "19.1", "19.2",
    "20.1", "20.2", "20.3", "21.1", "22.1", "22.2",
    "23.1", "23.2", "23.3", "24.1", "24.2", "24.3", "24.4",
]


def norm(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(norm(s).encode("utf-8")).hexdigest()


def read_text(p: Path) -> str:
    return norm(p.read_text(encoding="utf-8-sig"))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True, encoding="utf-8"
    ).strip()


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe relative path {value!r}")
    return path


def section_name(value: str) -> str:
    return value.removeprefix("## ").strip()


def practice_selector(value: str) -> tuple[str, str]:
    parts = value.split(" > ", 1)
    if len(parts) != 2 or not parts[0].startswith("## ") or not parts[1].startswith("### "):
        raise ValueError(f"practice selector must name a literal H2 and H3: {value!r}")
    return section_name(parts[0]), parts[1].removeprefix("### ").strip()


def source_sections(raw: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    _, items = engine.split_headings(raw, 2)
    sections = dict(items)
    if len(sections) != len(items):
        raise ValueError("duplicate H2 source heading")
    return sections, items


def assignment(spec: dict) -> list[str]:
    values = spec.get("assuntos") or ([spec["assunto"]] if spec.get("assunto") else [])
    if not values or len(values) != len(set(values)):
        raise ValueError("missing or duplicate subject assignment")
    return values


def declared_type(alias: str, spec: dict) -> str:
    if alias == "REV":
        return "project_review"
    if alias.startswith("KP"):
        return "answer_key_pratica"
    if alias.startswith("K"):
        return "answer_key"
    if alias.startswith("Q"):
        return "quiz"
    if alias.startswith("P"):
        return "practice"
    if alias.startswith("T"):
        return "theory"
    if alias.startswith("R"):
        return "rubric"
    if alias.startswith("M"):
        return "milestone"
    if alias.startswith("C"):
        return spec.get("tipo", "acceptance_criteria")
    if alias == "SCP":
        return "project_scope"
    if alias == "DEC":
        return "project_decisions"
    raise ValueError(f"unknown file alias {alias}")


def manifest_paths(m: dict) -> set[PurePosixPath]:
    result = set()
    for unit in m["unidades"].values():
        root = PurePosixPath(m["destino_raiz"]) / safe_rel(unit["pasta"])
        result.add(root / "README.md")
        result.update(root / safe_rel(spec["path"]) for spec in unit["arquivos"].values())
        for key, alias in unit["blocos_origem"]["comuns"].items():
            if key != "metadados":
                result.add(root / safe_rel(m["arquivos_comuns"][alias]["path"]))
    return result


def marker_position(text: str, marker: str, label: str) -> int:
    matches = f4.marker_positions(text, marker)
    if len(matches) != 1:
        raise ValueError(f"{label}: marker {marker!r} count={len(matches)}")
    return matches[0]


def validate_manifest(m: dict) -> list[str]:
    errors: list[str] = []

    def error(value: str) -> None:
        errors.append(value)

    if m.get("status_manifesto") != "aprovado_para_execucao":
        error("manifest is not approved for execution")
    if (m.get("fase"), m.get("base_commit"), m.get("id_prefix"), m.get("destino_raiz")) != (
        "Fase_5", BASE, "f5", DEST
    ):
        error("phase, base, prefix, or destination mismatch")
    if m.get("ordem_unidades") != ORDER or list(m.get("unidades", {})) != ORDER:
        error("unit order mismatch")
    if m.get("prefixos_arquivo_id", {}).get("KP") != "answer_key_pratica":
        error("KP type mapping missing")

    physical: dict[PurePosixPath, str] = {}
    manifest_ids: dict[str, str] = {}
    subject_count = 0
    theory_count = quiz_count = practice_count = practice_rubrics = 0
    project_rubrics = milestones = acceptances = checklists = decisions = reviews = 0

    for unit_key in ORDER:
        unit = m.get("unidades", {}).get(unit_key)
        if not unit:
            error(f"missing unit {unit_key}")
            continue
        try:
            origin = ROOT.joinpath(*safe_rel(unit["origem"]).parts)
            if not origin.is_file():
                error(f"{unit_key}: source missing")
                continue
            raw = read_text(origin)
            title, metadata, _ = f4.parse_header(raw, unit, unit["origem"])
            sections, _ = source_sections(raw)
            if title != unit.get("titulo_original") or metadata != unit.get("metadados_originais"):
                error(f"{unit_key}: title or metadata differs from source")
        except Exception as exc:
            error(f"{unit_key}: source/header parse failed: {exc}")
            continue

        project = bool(unit.get("tipo_projeto"))
        subjects = unit.get("assuntos", [])
        aliases = unit.get("arquivos", {})
        common = unit.get("blocos_origem", {}).get("comuns", {})
        if project and subjects:
            error(f"{unit_key}: project files must be flat, with no subject folder")
        if not project:
            subject_count += len(subjects)
        if len(subjects) != len(set(subjects)):
            error(f"{unit_key}: duplicate subject slug")
        if len({spec.get("path") for spec in aliases.values()}) != len(aliases):
            error(f"{unit_key}: duplicate alias path")

        for alias, spec in aliases.items():
            try:
                path = PurePosixPath(DEST) / safe_rel(unit["pasta"]) / safe_rel(spec["path"])
                if path in physical:
                    error(f"duplicate physical path {path}")
                physical[path] = f"{unit_key}/{alias}"
                if declared_type(alias, spec) != spec.get("tipo"):
                    error(f"{unit_key}/{alias}: file type does not match alias")
            except Exception as exc:
                error(f"{unit_key}/{alias}: invalid path/type: {exc}")

        id_aliases = set(aliases) | set(common.values())
        if set(unit.get("arquivo_ids", {})) != id_aliases:
            error(f"{unit_key}: arquivo_ids aliases differ from output aliases")
        for alias, ident in unit.get("arquivo_ids", {}).items():
            if alias == "IDX":
                rel = "README.md"
            elif alias in m.get("arquivos_comuns", {}):
                rel = m["arquivos_comuns"][alias]["path"]
            elif alias in aliases:
                rel = aliases[alias]["path"]
            else:
                error(f"{unit_key}: unknown ID alias {alias}")
                continue
            expected_id = engine.file_id(unit_key, rel)
            if ident != expected_id:
                error(f"{unit_key}/{alias}: file ID/path mismatch")
            if ident in manifest_ids:
                error(f"duplicate manifest file ID {ident}")
            manifest_ids[ident] = f"{unit_key}/{alias}"

        readme = PurePosixPath(DEST) / safe_rel(unit["pasta"]) / "README.md"
        if readme in physical:
            error(f"{unit_key}: README collides with another path")
        physical[readme] = f"{unit_key}/IDX"

        mapped_common = {}
        for key, alias in common.items():
            if key == "metadados":
                if alias != "IDX":
                    error(f"{unit_key}: metadata must map to IDX")
                continue
            common_spec = m.get("arquivos_comuns", {}).get(alias)
            if not common_spec:
                error(f"{unit_key}: common file schema missing {alias}")
                continue
            source = common_spec.get("origem")
            if isinstance(source, str):
                mapped_common[section_name(source)] = alias
            path = PurePosixPath(DEST) / safe_rel(unit["pasta"]) / safe_rel(common_spec["path"])
            if path in physical:
                error(f"{unit_key}: duplicate common file path {path}")
            physical[path] = f"{unit_key}/{alias}"

        if project:
            blocks = unit["blocos_origem"]
            mapped_sections = set(mapped_common)
            for field in ("escopo_projeto", "decisoes_projeto"):
                for alias, source_list in blocks.get(field, {}).items():
                    if alias not in aliases:
                        error(f"{unit_key}: missing {field} alias {alias}")
                    mapped_sections.update(section_name(s) for s in source_list)
            for alias, source in blocks.get("revisao_projeto", {}).items():
                if alias not in aliases:
                    error(f"{unit_key}: missing review alias {alias}")
                mapped_sections.add(section_name(source))
            milestone_section = unit.get("secoes_projeto", {}).get("marcos")
            if not milestone_section:
                error(f"{unit_key}: milestone section selector missing")
            else:
                mapped_sections.add(milestone_section)
            for alias, spec in blocks.get("rubrica", {}).items():
                if alias not in aliases:
                    error(f"{unit_key}: project rubric alias missing {alias}")
                mapped_sections.add(section_name(spec["origem"]))
                project_rubrics += 1
            for alias, spec in blocks.get("checklists", {}).items():
                if alias not in aliases:
                    error(f"{unit_key}: project checklist alias missing {alias}")
                mapped_sections.add(section_name(spec["origem"]))
                checklists += 1
            if set(sections) != mapped_sections:
                error(
                    f"{unit_key}: project section map mismatch; "
                    f"unmapped={sorted(set(sections) - mapped_sections)}"
                )
            milestone_text = sections.get(milestone_section, "")
            _, source_milestones = engine.h3_chunks(milestone_text)
            specs = list(blocks.get("marcos", {}).items())
            if len(source_milestones) != 4 or len(specs) != 4:
                error(f"{unit_key}: expected four source milestones")
            for (milestone_id, spec), (literal_title, block) in zip(specs, source_milestones):
                milestones += 1
                acceptances += 1
                if literal_title != spec.get("titulo_marco"):
                    error(f"{unit_key}/{milestone_id}: milestone title differs from source")
                if spec.get("arquivo") not in aliases or spec.get("aceite") not in aliases:
                    error(f"{unit_key}/{milestone_id}: milestone/acceptance alias missing")
                try:
                    start = marker_position(
                        block, spec["separacao_literal"]["aceite_inicio"], f"{unit_key}/{milestone_id}"
                    )
                    end = marker_position(
                        block, spec["separacao_literal"]["aceite_fim_antes"], f"{unit_key}/{milestone_id}"
                    )
                    if end <= start:
                        error(f"{unit_key}/{milestone_id}: acceptance boundaries reversed")
                except Exception as exc:
                    error(str(exc))
            for alias, spec in blocks.get("checklists", {}).items():
                if spec.get("itens") and sections[section_name(spec["origem"])].count("- [ ]") != spec["itens"]:
                    error(f"{unit_key}/{alias}: checklist count mismatch")
            decisions += sum(len(v) for v in blocks.get("decisoes_projeto", {}).values())
            reviews += len(blocks.get("revisao_projeto", {}))
        else:
            mapped_sections = set(mapped_common)
            theory_map = unit["blocos_origem"].get("teoria", {})
            theory_format = unit.get("formato_teoria")
            if theory_format == "h3_em_teoria":
                if "Teoria" not in sections:
                    error(f"{unit_key}: Teoria section missing")
                else:
                    mapped_sections.add("Teoria")
                    _, theory = engine.h3_chunks(sections["Teoria"])
                    titles = [title for title, _ in theory]
                    if set(titles) != set(theory_map) or len(titles) != len(theory_map):
                        error(f"{unit_key}: literal H3 theory inventory mismatch")
            elif theory_format == "h2_microtopicos":
                if set(theory_map) - set(sections):
                    error(f"{unit_key}: literal H2 theory selectors missing: {sorted(set(theory_map)-set(sections))}")
                mapped_sections.update(theory_map)
                empty_container = unit.get("teoria_container_vazio")
                if empty_container:
                    if empty_container != "Teoria" or empty_container not in sections:
                        error(f"{unit_key}: empty theory container selector is invalid")
                    elif sections[empty_container].removeprefix("## Teoria").strip():
                        error(f"{unit_key}: theory container unexpectedly has body text")
                    else:
                        mapped_sections.add(empty_container)
            else:
                error(f"{unit_key}: unsupported or missing theory format")
            for title, alias in theory_map.items():
                theory_count += 1
                if alias not in aliases or PurePosixPath(aliases[alias]["path"]).parent.as_posix() not in subjects:
                    error(f"{unit_key}/{title}: theory path/subject mismatch")

            qmap = unit["blocos_origem"].get("quiz", {})
            qsection = next((s for s in ("Verificação — quiz", "Quiz") if s in sections), None)
            if qmap:
                if not qsection:
                    error(f"{unit_key}: quiz section missing")
                else:
                    _, items = engine.numbered(sections[qsection])
                    if {f"Q{n}" for n, _ in items} != set(qmap) or len(items) != len(qmap):
                        error(f"{unit_key}: question inventory mismatch")
                mapped_sections.add(qsection)
            quiz_count += len(qmap)

            pmap = unit["blocos_origem"].get("pratica", {})
            grouped = defaultdict(list)
            for item, spec in pmap.items():
                if not spec.get("origem_secao"):
                    error(f"{unit_key}/{item}: explicit activity section selector missing")
                else:
                    try:
                        selected_section, selected_title = practice_selector(spec["origem_secao"])
                        if selected_title != spec.get("titulo"):
                            error(f"{unit_key}/{item}: practice selector/title differ")
                        grouped[selected_section].append((item, spec))
                    except Exception as exc:
                        error(f"{unit_key}/{item}: {exc}")
            for section, group in grouped.items():
                mapped_sections.add(section)
                _, activities = engine.h3_chunks(sections.get(section, ""))
                if len(activities) != len(group):
                    error(f"{unit_key}/{section}: practice inventory mismatch")
                for (title, block), (item, spec) in zip(
                    activities, sorted(group, key=lambda pair: int(pair[0][1:]))
                ):
                    if title != spec.get("titulo"):
                        error(f"{unit_key}/{item}: activity title mismatch")
                    if block.count("**Solução de referência:**") != 1 or block.count("**Rubrica:**") != 1:
                        error(f"{unit_key}/{item}: solution/rubric boundary mismatch")
                    for field in ("arquivo", "resposta", "rubrica"):
                        if spec.get(field) not in aliases:
                            error(f"{unit_key}/{item}: missing {field} alias")
                    practice_count += 1
                    practice_rubrics += 1
            if set(sections) != mapped_sections:
                error(
                    f"{unit_key}: source section map mismatch; "
                    f"unmapped={sorted(set(sections) - mapped_sections)}"
                )

            for item, spec in qmap.items():
                if spec.get("arquivo") not in aliases or spec.get("resposta") not in aliases:
                    error(f"{unit_key}/{item}: question/key alias missing")
                    continue
                try:
                    owners = assignment(spec)
                except Exception as exc:
                    error(f"{unit_key}/{item}: {exc}")
                    continue
                if any(s not in subjects for s in owners):
                    error(f"{unit_key}/{item}: unknown subject")
                qpath = PurePosixPath(aliases[spec["arquivo"]]["path"]).parent.as_posix()
                kpath = PurePosixPath(aliases[spec["resposta"]]["path"]).parent.as_posix()
                if qpath != kpath:
                    error(f"{unit_key}/{item}: answer key is not beside its question")
                if len(owners) > 1 and qpath != "90_integracao":
                    error(f"{unit_key}/{item}: shared question not in 90_integracao")
                if len(owners) == 1 and qpath != owners[0]:
                    error(f"{unit_key}/{item}: exclusive question points to another subject")
                rule = spec.get("separacao_inline_literal", {})
                if "enunciado_literal" in rule:
                    if not rule.get("resposta_literal") or rule.get("resposta_destino") != spec.get("resposta"):
                        error(f"{unit_key}/{item}: inline answer literal/destination mismatch")
                elif not rule.get("resposta_inicio"):
                    error(f"{unit_key}/{item}: exact answer marker missing")

            for item, spec in pmap.items():
                try:
                    owners = assignment(spec)
                except Exception as exc:
                    error(f"{unit_key}/{item}: {exc}")
                    continue
                ppath = PurePosixPath(aliases[spec["arquivo"]]["path"]).parent.as_posix()
                if len(owners) > 1 and ppath != "90_integracao":
                    error(f"{unit_key}/{item}: shared practice not in 90_integracao")
                if len(owners) == 1 and ppath != owners[0]:
                    error(f"{unit_key}/{item}: exclusive practice points outside subject")
                for field in ("resposta", "rubrica"):
                    if spec.get(field) in aliases and PurePosixPath(aliases[spec[field]]["path"]).parent != PurePosixPath(aliases[spec["arquivo"]]["path"]).parent:
                        error(f"{unit_key}/{item}: {field} is not colocated with practice")

            coverage = unit.get("cobertura", {})
            expected = {
                s: {
                    "quiz_exclusivo": set(), "quiz_compartilhado": set(),
                    "pratica_exclusiva": set(), "pratica_compartilhada": set(),
                }
                for s in subjects
            }
            for item, spec in qmap.items():
                owners = assignment(spec)
                for subject in owners:
                    expected[subject]["quiz_compartilhado" if len(owners) > 1 else "quiz_exclusivo"].add(item)
            for item, spec in pmap.items():
                owners = assignment(spec)
                for subject in owners:
                    expected[subject]["pratica_compartilhada" if len(owners) > 1 else "pratica_exclusiva"].add(item)
            if set(coverage) != set(subjects):
                error(f"{unit_key}: coverage slugs differ from subject folders")
            for subject in subjects:
                found = coverage.get(subject, {})
                for field, wanted in expected[subject].items():
                    if set(found.get(field, [])) != wanted:
                        error(f"{unit_key}/{subject}: coverage {field} differs from block assignments")
                listed = sum(
                    (list(found.get(field, [])) for field in expected[subject]), []
                )
                if len(listed) != len(set(listed)):
                    error(f"{unit_key}/{subject}: item is duplicated between coverage classes")

        for field in ("quiz", "pratica"):
            grouped_items = defaultdict(set)
            for item, spec in unit.get("blocos_origem", {}).get(field, {}).items():
                try:
                    grouped_items[spec["arquivo"]].add(tuple(assignment(spec)))
                except Exception:
                    pass
            for alias, owners in grouped_items.items():
                if len(owners) > 1:
                    error(f"{unit_key}/{alias}: grouped items have different subject ownership")

    if sum(not u.get("tipo_projeto") for u in m["unidades"].values()) != 18:
        error("expected 18 conventional units")
    if sum(bool(u.get("tipo_projeto")) for u in m["unidades"].values()) != 2:
        error("expected two projects")
    if subject_count != 59:
        error(f"expected 59 content subjects, got {subject_count}")
    inventory = (
        theory_count, quiz_count, practice_count, practice_rubrics, project_rubrics,
        milestones, acceptances, checklists, decisions, reviews,
    )
    if inventory != (81, 90, 54, 54, 2, 8, 8, 1, 1, 1):
        error(f"source inventory mismatch: {inventory}")
    all_paths = manifest_paths(m)
    if len(all_paths) != 483:
        error(f"expected 483 distinct paths, got {len(all_paths)}")
    if m.get("estimativa_arquivos", {}).get("total") != len(all_paths):
        error("manifest file forecast differs from physical paths")

    for rule in f4.normalization_rules(m):
        unit = m["unidades"].get(rule.get("unidade"))
        if not unit:
            error(f"normalization unit missing: {rule.get('unidade')}")
            continue
        alias = rule["alias"]
        rel = unit["arquivos"][alias]["path"] if alias in unit["arquivos"] else next(
            (
                m["arquivos_comuns"][a]["path"]
                for k, a in unit["blocos_origem"]["comuns"].items()
                if k != "metadados" and a == alias
            ),
            None,
        )
        if not rel:
            error(f"normalization output alias missing: {rule['unidade']}/{alias}")
            continue
        origin = ROOT.joinpath(*safe_rel(unit["origem"]).parts)
        secs, _ = source_sections(read_text(origin))
        section = rule.get("secao")
        if section not in secs or secs[section].count(f"]({rule['caminho_original']})") != rule["ocorrencias"]:
            error(f"normalization source link mismatch: {rule['unidade']}/{alias}")
            continue
        source_target = (origin.parent / Path(rule["caminho_original"].replace("/", "\\"))).resolve()
        resource = ROOT.joinpath(*safe_rel(rule["destino_recurso"]).parts)
        if not resource.is_file() or source_target != resource.resolve():
            error(f"normalization destination is not source-confirmed: {rule['unidade']}/{alias}")
        wanted = posixpath.relpath(
            rule["destino_recurso"],
            (PurePosixPath(DEST) / safe_rel(unit["pasta"]) / safe_rel(rel)).parent.as_posix(),
        )
        if wanted != rule.get("caminho_migrado"):
            error(f"normalization href mismatch: {rule['unidade']}/{alias}; expected {wanted}")
    return errors


def runtime_manifest(m: dict) -> dict:
    result = copy.deepcopy(m)
    for unit in result["unidades"].values():
        unit["tipos_arquivo"] = {a: spec["tipo"] for a, spec in unit["arquivos"].items()}
        unit["arquivos"] = {a: spec["path"] for a, spec in unit["arquivos"].items()}
    return result


class Builder(f4.Builder):
    def emit_common(self, unit_key: str) -> None:
        section_for = {
            "objetivo": "Objetivo", "resumo": "Resumo",
            "criterio_de_conclusao": "Critério de conclusão",
            "conexoes": "Conexões", "referencias": "Referências",
            "nota_instrutor": "Nota do instrutor",
        }
        unit = self.m["unidades"][unit_key]
        for source_key, alias in unit["blocos_origem"]["comuns"].items():
            if source_key == "metadados":
                continue
            if source_key not in section_for:
                raise ValueError(f"{unit_key}: unknown common block {source_key!r}")
            section = section_for[source_key]
            if section not in self.sources[unit_key]["sections"]:
                raise ValueError(f"{unit_key}: source common section missing: {section}")
            content = self.sections[(unit_key, section)]
            kind = self.m["arquivos_comuns"][alias]["tipo"]
            self.add(unit_key, section, 0, len(content), alias, kind, item=section)

    def emit_theory(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        mapping = unit["blocos_origem"]["teoria"]
        theory_format = unit["formato_teoria"]
        if theory_format == "h3_em_teoria":
            section = "Teoria"
            text = self.sections[(unit_key, section)]
            preamble, chunks = engine.h3_chunks(text)
            if {title for title, _ in chunks} != set(mapping) or len(chunks) != len(mapping):
                raise ValueError(f"{unit_key}: literal H3 theory blocks differ from manifest")
            ordered_aliases = [mapping[title] for title, _ in chunks]
            first_alias = ordered_aliases[0]
            if preamble:
                subject = PurePosixPath(unit["arquivos"][first_alias]).parent.as_posix()
                self.add(
                    unit_key, section, 0, len(preamble), first_alias, "theory",
                    item="theory-container", context={"assunto": subject},
                )
            cursor = len(preamble)
            for title, block in chunks:
                if text[cursor:cursor + len(block)] != block:
                    raise ValueError(f"{unit_key}: non-contiguous literal theory block {title!r}")
                alias = mapping[title]
                subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
                if subject not in unit["assuntos"]:
                    raise ValueError(f"{unit_key}/{title}: theory alias points to another subject")
                self.add(
                    unit_key, section, cursor, cursor + len(block), alias, "theory",
                    item=title, context={"assunto": subject},
                )
                cursor += len(block)
            if cursor != len(text):
                raise ValueError(f"{unit_key}: theory section suffix was not mapped")
            return

        if theory_format != "h2_microtopicos":
            raise ValueError(f"{unit_key}: unsupported theory format {theory_format!r}")
        first_title = next(iter(mapping))
        first_alias = mapping[first_title]
        container = unit.get("teoria_container_vazio")
        if container:
            text = self.sections[(unit_key, container)]
            if text.removeprefix("## Teoria").strip():
                raise ValueError(f"{unit_key}: theory container is not empty")
            subject = PurePosixPath(unit["arquivos"][first_alias]).parent.as_posix()
            self.add(
                unit_key, container, 0, len(text), first_alias, "theory",
                item="theory-container", context={"assunto": subject},
            )
        for title, alias in mapping.items():
            if title not in self.sources[unit_key]["sections"]:
                raise ValueError(f"{unit_key}: literal theory section missing: {title!r}")
            text = self.sections[(unit_key, title)]
            subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
            if subject not in unit["assuntos"]:
                raise ValueError(f"{unit_key}/{title}: theory alias points to another subject")
            self.add(
                unit_key, title, 0, len(text), alias, "theory", item=title,
                context={"assunto": subject},
            )

    def emit_quiz(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        qmap = unit.get("blocos_origem", {}).get("quiz", {})
        if not qmap:
            return
        section = next(
            (s for s in ("Verificação — quiz", "Quiz") if s in self.sources[unit_key]["sections"]),
            None,
        )
        if not section:
            raise ValueError(f"{unit_key}: quiz section missing")
        text = self.sections[(unit_key, section)]
        pre, items = engine.numbered(text)
        if {f"Q{n}" for n, _ in items} != set(qmap) or len(items) != len(qmap):
            raise ValueError(f"{unit_key}: quiz numbering differs from manifest")
        cursor = 0
        if pre:
            first = qmap[f"Q{items[0][0]}"]
            self.add(unit_key, section, 0, len(pre), first["arquivo"], "quiz", context=f4.context_for(first))
            cursor = len(pre)
        for number, block in items:
            item = f"Q{number}"
            spec = qmap[item]
            rule = spec.get("separacao_inline_literal", {})
            context = f4.context_for(spec)
            if "enunciado_literal" in rule:
                question = rule["enunciado_literal"]
                answer = rule.get("resposta_literal", "")
                if not question or not answer or block.count(question) != 1 or block.count(answer) != 1:
                    raise ValueError(f"{unit_key}/{item}: inline literal boundary mismatch")
                qend = block.find(question) + len(question)
                split = block.find(answer)
                if split < qend or block[qend:split].strip() or block[split + len(answer):].strip():
                    raise ValueError(f"{unit_key}/{item}: response is not the exact tail after the question")
                if rule.get("resposta_destino") != spec.get("resposta"):
                    raise ValueError(f"{unit_key}/{item}: answer destination mismatch")
            else:
                markers = rule.get("resposta_inicio")
                markers = [markers] if isinstance(markers, str) else markers
                matches = []
                for marker in markers or []:
                    matches.extend((at, marker) for at in f4.marker_positions(block, marker))
                if len(matches) != 1:
                    raise ValueError(f"{unit_key}/{item}: expected one exact answer marker, got {len(matches)}")
                split, _ = matches[0]
                for marker in rule.get("feedback_justificativa_inicio", []):
                    if len(f4.marker_positions(block, marker)) != 1:
                        raise ValueError(f"{unit_key}/{item}: feedback marker mismatch")
                if rule.get("resposta_destino") and rule["resposta_destino"] != spec.get("resposta"):
                    raise ValueError(f"{unit_key}/{item}: answer destination mismatch")
            if not block[:split].strip() or not block[split:].strip():
                raise ValueError(f"{unit_key}/{item}: empty question or answer segment")
            self.add(unit_key, section, cursor, cursor + split, spec["arquivo"], "quiz", item=item, context=context)
            self.add(unit_key, section, cursor + split, cursor + len(block), spec["resposta"], "answer_key", item=item, context=context)
            cursor += len(block)
        if cursor != len(text):
            raise ValueError(f"{unit_key}: quiz section suffix was not mapped")

    def _emit_activity_block(self, unit_key, section, start, block, item, spec):
        rule = spec.get("separacao_inline_literal", "")
        if not isinstance(rule, str) or "**Solução de referência:**" not in rule or "**Rubrica:**" not in rule:
            raise ValueError(f"{unit_key}/{item}: literal practice boundaries missing")
        solution = marker_position(block, "**Solução de referência:**", f"{unit_key}/{item} solution")
        rubric = marker_position(block, "**Rubrica:**", f"{unit_key}/{item} rubric")
        if rubric <= solution:
            raise ValueError(f"{unit_key}/{item}: solution/rubric order mismatch")
        context = f4.context_for(spec)
        self.add(unit_key, section, start, start + solution, spec["arquivo"], "practice", item=item, context=context)
        self.add(unit_key, section, start + solution, start + rubric, spec["resposta"], "answer_key_pratica", item=item, context=context)
        self.add(unit_key, section, start + rubric, start + len(block), spec["rubrica"], "rubric", item=item, context=context, scale=spec.get("escala_rubrica"))
        return start + len(block)

    def emit_project(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        blocks = unit["blocos_origem"]
        for alias, source_sections in blocks.get("escopo_projeto", {}).items():
            for label in source_sections:
                section = section_name(label)
                text = self.sections[(unit_key, section)]
                self.add(unit_key, section, 0, len(text), alias, "project_scope", item=section)
        for alias, source_sections in blocks.get("decisoes_projeto", {}).items():
            for label in source_sections:
                section = section_name(label)
                text = self.sections[(unit_key, section)]
                self.add(unit_key, section, 0, len(text), alias, "project_decisions", item=section)
        for alias, label in blocks.get("revisao_projeto", {}).items():
            section = section_name(label)
            text = self.sections[(unit_key, section)]
            self.add(unit_key, section, 0, len(text), alias, "project_review", item=section)

        section = unit["secoes_projeto"]["marcos"]
        text = self.sections[(unit_key, section)]
        preamble, chunks = engine.h3_chunks(text)
        specs = list(blocks["marcos"].items())
        if len(chunks) != 4 or len(specs) != 4:
            raise ValueError(f"{unit_key}: expected four milestones")
        cursor = 0
        for (title, block), (milestone_id, spec) in zip(chunks, specs):
            if title != spec.get("titulo_marco"):
                raise ValueError(f"{unit_key}/{milestone_id}: milestone title is not literal")
            rule = spec["separacao_literal"]
            acceptance = marker_position(block, rule["aceite_inicio"], f"{unit_key}/{milestone_id} acceptance")
            ending = marker_position(block, rule["aceite_fim_antes"], f"{unit_key}/{milestone_id} ending")
            if ending <= acceptance:
                raise ValueError(f"{unit_key}/{milestone_id}: acceptance boundaries reversed")
            if cursor == 0 and preamble:
                self.add(unit_key, section, 0, len(preamble), spec["arquivo"], "milestone", title=title)
                cursor = len(preamble)
            if acceptance:
                self.add(unit_key, section, cursor, cursor + acceptance, spec["arquivo"], "milestone", item=milestone_id, title=title)
            self.add(unit_key, section, cursor + acceptance, cursor + ending, spec["aceite"], "acceptance_criteria", item=milestone_id, title=title)
            if ending < len(block):
                self.add(unit_key, section, cursor + ending, cursor + len(block), spec["arquivo"], "milestone", item=milestone_id, title=title)
            cursor += len(block)
        if cursor != len(text):
            raise ValueError(f"{unit_key}: milestone source suffix unmapped")

        for alias, spec in blocks.get("checklists", {}).items():
            section = section_name(spec["origem"])
            text = self.sections[(unit_key, section)]
            self.add(unit_key, section, 0, len(text), alias, "checklist", item="checklist_final")
        for alias, spec in blocks.get("rubrica", {}).items():
            section = section_name(spec["origem"])
            text = self.sections[(unit_key, section)]
            self.add(unit_key, section, 0, len(text), alias, "rubric", item="rubrica", scale=spec.get("escala_rubrica"))

    def add_index(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        source = self.sources[unit_key]
        fields = [
            ("title", source["title"]),
            *unit["metadados_originais"].items(),
            ("arquivo_id", engine.file_id(unit_key, "README.md")),
            ("tipo_arquivo", "topic_index"),
        ]
        body = f"# {source['title']}\n\n## Índice\n\n### Arquivos comuns\n"
        for key, alias in unit["blocos_origem"]["comuns"].items():
            if key == "metadados":
                continue
            common = self.m["arquivos_comuns"][alias]
            body += f"- [{common['tipo']}]({common['path']})\n"
        if unit.get("tipo_projeto"):
            body += "\n### Arquivos do projeto\n"
            for alias, rel in unit["arquivos"].items():
                kind = unit["tipos_arquivo"][alias]
                path = PurePosixPath(rel)
                body += f"- [{kind}: {path.name}]({path.as_posix()})\n"
        else:
            body += "\n### Assuntos\n"
            for subject in unit["assuntos"]:
                body += f"\n#### {subject}\n"
                for rel in unit["arquivos"].values():
                    path = PurePosixPath(rel)
                    if path.parts[0] == subject:
                        body += f"- [{path.name}]({path.as_posix()})\n"
            integration = [
                PurePosixPath(rel) for rel in unit["arquivos"].values()
                if PurePosixPath(rel).parts[0] == "90_integracao"
            ]
            if integration:
                body += "\n### Integração\n"
                for path in integration:
                    body += f"- [{path.name}]({path.as_posix()})\n"
        path = self.dest / safe_rel(unit["pasta"]) / "README.md"
        if path in self.outputs:
            raise ValueError(f"{unit_key}: duplicate README")
        self.outputs[path] = engine.frontmatter(fields) + "\n" + body

    def finalize(self) -> None:
        for unit_key, unit in self.m["unidades"].items():
            aliases = set(unit["arquivos"])
            actual = {alias for (owner, alias) in self.data if owner == unit_key and alias in aliases}
            if actual != aliases:
                raise ValueError(f"{unit_key}: missing output aliases {sorted(aliases - actual)}")
            for (owner, alias), data in list(self.data.items()):
                if owner != unit_key or alias not in aliases:
                    continue
                if len(data["contexts"]) > 1:
                    raise ValueError(f"{unit_key}/{alias}: conflicting frontmatter contexts")
                context = data["contexts"][0] if data["contexts"] else {}
                parent = PurePosixPath(data["rel"]).parent.as_posix()
                if unit.get("tipo_projeto"):
                    if parent != "." or context.get("assunto") or context.get("assuntos"):
                        raise ValueError(f"{unit_key}/{alias}: project files must be flat and subject-free")
                elif parent == "90_integracao":
                    if len(context.get("assuntos", [])) < 2:
                        raise ValueError(f"{unit_key}/{alias}: shared file lacks subject references")
                elif parent in unit["assuntos"]:
                    if context.get("assunto") != parent:
                        raise ValueError(f"{unit_key}/{alias}: path/subject mismatch")
                else:
                    raise ValueError(f"{unit_key}/{alias}: output outside approved subject folder")
                if data["kind"] == "rubric" and not data["scale"]:
                    raise ValueError(f"{unit_key}/{alias}: rubric scale missing")
                if alias.startswith("M") and not data["title"]:
                    raise ValueError(f"{unit_key}/{alias}: literal milestone title missing")
                content = self.normalize_output(unit_key, alias, data["rel"], "".join(data["chunks"]))
                engine.put(
                    unit_key, data["rel"], data["kind"], content,
                    subject=context.get("assunto"), subjects=context.get("assuntos"),
                    items=data["items"], order=f4.order_of(alias),
                    title=data["title"], scale=data["scale"],
                )
            for key, alias in unit["blocos_origem"]["comuns"].items():
                if key == "metadados":
                    continue
                data = self.data.get((unit_key, alias))
                if not data:
                    raise ValueError(f"{unit_key}: common source block missing {alias}")
                content = self.normalize_output(unit_key, alias, data["rel"], "".join(data["chunks"]))
                engine.put(unit_key, data["rel"], data["kind"], content, items=data["items"], order=f4.order_of(alias))
            self.add_index(unit_key)
            for (owner, section), text in self.sections.items():
                if owner == unit_key and self.cursors[(owner, section)] != len(text):
                    raise ValueError(f"{unit_key}/{section}: unmapped source content")
        expected = f4.output_paths(self.m)
        if set(self.outputs) != expected:
            raise ValueError("generated output paths differ from manifest")
        if len(self.outputs) != self.m["estimativa_arquivos"]["total"]:
            raise ValueError("generated output count differs from manifest forecast")

    def build(self) -> None:
        for unit_key, unit in self.m["unidades"].items():
            self.emit_common(unit_key)
            if unit.get("tipo_projeto"):
                self.emit_project(unit_key)
            else:
                self.emit_theory(unit_key)
                self.emit_quiz(unit_key)
                self.emit_practices(unit_key)
                self.emit_flashcards(unit_key)
        self.finalize()


def previous_snapshot() -> dict[str, str]:
    result = {}
    for number in range(1, 5):
        root = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        for path in root.rglob("*"):
            if path.is_file():
                result[path.relative_to(ROOT).as_posix()] = sha_file(path)
    return result


def previous_ids() -> set[str]:
    result = set()
    for number in range(1, 5):
        root = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        for path in root.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in result:
                raise ValueError(f"missing or duplicate earlier file ID in {path}")
            result.add(ident)
    return result


def protected_snapshot(manifest: dict) -> dict[str, str]:
    paths = [u["origem"] for u in manifest["unidades"].values()] + PHASE_DOCS + [
        JSON,
        "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
        "docs/migracao/PLANEJAMENTO_FASE5.md",
    ]
    result = {}
    for rel in paths:
        path = ROOT.joinpath(*safe_rel(rel).parts)
        if not path.is_file():
            raise ValueError(f"protected input missing: {rel}")
        result[rel] = sha_file(path)
    return result


def git_preflight(mode: str) -> list[str]:
    errors = []
    if git("rev-parse", "--show-toplevel").replace("\\", "/").casefold() != str(ROOT).replace("\\", "/").casefold():
        errors.append("worktree root mismatch")
    if git("branch", "--show-current") != "migracao-estrutura":
        errors.append("branch mismatch")
    if git("rev-parse", "HEAD") != BASE:
        errors.append("HEAD mismatch")
    if git("diff", "--cached", "--name-only"):
        errors.append("staged changes exist")
    if git("diff", "--name-only"):
        errors.append("tracked changes exist")
    for line in git("status", "--porcelain").splitlines():
        path = line[3:].replace("\\", "/")
        if path in ALLOW:
            continue
        if mode in ("apply", "audit-existing", "reproduce-temp") and (path.startswith(DEST + "/") or path in REPORTS):
            continue
        errors.append("unexpected worktree entry " + line)
    if mode == "apply" and (ROOT / DEST).exists():
        errors.append("Fase 5 output already exists")
    if mode in ("audit-existing", "reproduce-temp") and not (ROOT / DEST).is_dir():
        errors.append("Fase 5 output does not exist for audit/reproduction")
    if mode == "apply":
        for rel in REPORTS:
            if (ROOT / rel).exists():
                errors.append("report already exists " + rel)
    return errors


def audit(builder: Builder, previous: dict, protected: dict, ids: set[str]):
    errors, warnings, results = [], [], {}
    by_section = defaultdict(list)
    for row in builder.records:
        if row["secao"] in ("metadados_lista", "titulo"):
            continue
        by_section[(row["unidade"], row["secao"])].append(row)
    for unit_key, unit in builder.m["unidades"].items():
        source = builder.sources[unit_key]
        sections = []
        for name, text in source["section_list"]:
            rows = by_section.get((unit_key, name), [])
            cursor, fragments = 0, []
            for row in rows:
                start, end = int(row["inicio"]), int(row["fim"])
                if start != cursor or end < start:
                    errors.append(f"{unit_key}/{name}/{row['bloco']}: gap/overlap")
                if text[start:end] != row["texto"]:
                    errors.append(f"{unit_key}/{name}/{row['bloco']}: source segment mismatch")
                fragments.append(row["texto"])
                cursor = end
            if cursor != len(text):
                errors.append(f"{unit_key}/{name}: coverage {cursor}/{len(text)}")
            reconstructed = "".join(fragments)
            if reconstructed != text:
                errors.append(f"{unit_key}/{name}: reconstructed text differs")
            if engine.code_blocks(reconstructed) != engine.code_blocks(text):
                errors.append(f"{unit_key}/{name}: code blocks differ")
            sections.append((name, len(rows), sha_text(reconstructed) == sha_text(text)))
        unit_root = PurePosixPath(DEST) / safe_rel(unit["pasta"])
        file_count = sum(path.parts[:len(unit_root.parts)] == unit_root.parts for path in builder.outputs)
        results[unit_key] = {
            "arquivos": file_count,
            "mapeamentos": sum(row["unidade"] == unit_key for row in builder.records),
            "secoes": sections,
        }
    generated_ids, resolved, wikilinks = set(), [], 0
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for rel, text in builder.outputs.items():
        try:
            _, fields, body = engine.fm(text, str(rel))
        except Exception as exc:
            errors.append(f"invalid YAML frontmatter {rel}: {exc}")
            continue
        ident = fields.get("arquivo_id")
        if not ident or ident in generated_ids or ident in ids:
            errors.append(f"missing or globally duplicate file ID {ident}")
        else:
            generated_ids.add(ident)
        if fields.get("parent_key") and fields["parent_key"] not in builder.m["unidades"]:
            errors.append(f"invalid parent_key {rel}")
        if not body.strip():
            errors.append(f"empty output {rel}")
        wikilinks += len(re.findall(r"\[\[[^\]]+\]\]", body))
        for target in link_pattern.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path, _, _ = target.partition("#")
            virtual = PurePosixPath(posixpath.normpath((rel.parent / PurePosixPath(target_path)).as_posix())) if target_path else rel
            if virtual in builder.outputs or (target_path and ROOT.joinpath(*virtual.parts).is_file()):
                resolved.append(f"{rel} -> {target}")
                continue
            if rel.name == "README.md":
                errors.append(f"index link unresolved: {rel} -> {target}")
                continue
            source_base = None
            for unit in builder.m["unidades"].values():
                unit_root = PurePosixPath(DEST) / safe_rel(unit["pasta"])
                if rel.parts[:len(unit_root.parts)] == unit_root.parts:
                    source_base = ROOT.joinpath(*safe_rel(unit["origem"]).parent.parts)
                    break
            source_target = (source_base / Path(target_path.replace("/", "\\"))).resolve() if source_base and target_path else None
            if source_target and source_target.is_file():
                warnings.append(f"source-relative link no longer resolves after relocation: {rel} -> {target}")
            else:
                errors.append(f"broken relative Markdown link: {rel} -> {target}")
    for unit_key, unit in builder.m["unidades"].items():
        readme = PurePosixPath(DEST) / safe_rel(unit["pasta"]) / "README.md"
        try:
            _, fields, _ = engine.fm(builder.outputs[readme], str(readme))
            expected_fields = {
                "title": builder.sources[unit_key]["title"],
                **unit["metadados_originais"],
                "arquivo_id": engine.file_id(unit_key, "README.md"),
                "tipo_arquivo": "topic_index",
            }
            for key, expected in expected_fields.items():
                if fields.get(key) != expected:
                    errors.append(f"{unit_key}: README frontmatter field {key!r} differs from source/manifest")
        except Exception as exc:
            errors.append(f"{unit_key}: README metadata audit failed: {exc}")
    if len(generated_ids) != len(builder.outputs):
        errors.append("generated file ID count differs from output count")
    for rel, digest in protected.items():
        path = ROOT.joinpath(*safe_rel(rel).parts)
        if not path.is_file() or sha_file(path) != digest:
            errors.append(f"protected input changed: {rel}")
    if previous_snapshot() != previous:
        errors.append("one or more prior-phase files changed")
    return errors, results, [f"resolved_markdown_links={len(resolved)}", f"preserved_wikilinks={wikilinks}", *warnings]


def directed_coverage_report(builder: Builder) -> list[str]:
    lines = [
        "## Auditoria pedagógica direcionada — 20.1 e 24.2", "",
        "Os trechos entre aspas foram copiados literalmente das fontes; a elipse indica truncamento de exibição. Exclusivo/compartilhado segue a lista de assuntos do manifesto.", "",
    ]
    for unit_key in ("20.1", "24.2"):
        unit = builder.m["unidades"][unit_key]
        raw = read_text(ROOT.joinpath(*safe_rel(unit["origem"]).parts))
        sections, _ = source_sections(raw)
        quiz_section = next(s for s in ("Verificação — quiz", "Quiz") if s in sections)
        _, question_blocks = engine.numbered(sections[quiz_section])
        question_text = {f"Q{number}": block.splitlines()[0].strip() for number, block in question_blocks}
        practice_text = {}
        for item, spec in unit["blocos_origem"].get("pratica", {}).items():
            section, exact_title = practice_selector(spec["origem_secao"])
            _, activity_blocks = engine.h3_chunks(sections[section])
            matches = [(title, block) for title, block in activity_blocks if title == exact_title]
            if len(matches) != 1:
                raise ValueError(f"{unit_key}/{item}: directed evidence could not find exact activity title")
            title, block = matches[0]
            body_lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
            practice_text[item] = body_lines[0] if body_lines else title
        lines.extend([f"### {unit_key}", "", "| Assunto | Microtópicos originais | Cobertura e trechos literais de evidência |", "|---|---|---|"])
        for subject in unit["assuntos"]:
            microtopics = builder.m["auditoria_pedagogica_direcionada"][unit_key]["assuntos"][subject]
            coverage = unit["cobertura"][subject]
            evidence = []
            for kind, texts, exclusive_field, shared_field in (
                ("quiz", question_text, "quiz_exclusivo", "quiz_compartilhado"),
                ("prática", practice_text, "pratica_exclusiva", "pratica_compartilhada"),
            ):
                for classification, field in (("exclusivo", exclusive_field), ("compartilhado", shared_field)):
                    for item in coverage.get(field, []):
                        snippet = texts[item].replace("|", "\\|")
                        if len(snippet) > 210:
                            snippet = snippet[:207].rstrip() + "…"
                        evidence.append(f"**{item} {classification}:** “{snippet}”")
            coverage_text = "<br>".join(evidence) if evidence else "Sem item atribuído."
            lines.append(f"| `{subject}` | {'; '.join(microtopics)} | {coverage_text} |")
        lines.append("")
    lines.extend([
        "#### Conclusão da classificação", "",
        "- 20.1: Q4 é exclusivo de sessão/ciclo de vida porque o cenário avalia a sessão server-side após apagar o cookie; P3 tem como objetivo o ciclo de credenciais e os caminhos de sessão/OAuth são alternativas condicionais no próprio enunciado. Q5 é compartilhado apenas entre tokens/JWT e OAuth/OIDC porque pede relacionar ID Token, access token e refresh token. P1 compara sessão e access token; não exige implementar OAuth/OIDC.",
        "- 24.2: Q1 compara explicitamente o serviço com dublê à constraint ausente na migration e por isso é compartilhado entre planejamento e persistência. Q4 menciona rollback em conexão diferente da usada pelo endpoint e é compartilhado entre persistência e isolamento. Q3 delimita o que a rota HTTP com provider substituído comprova; P2 exige simultaneamente rota de criação e constraint real no PostgreSQL descartável, justificando o assunto integrado de rota/persistência. Q2 e Q5 avaliam ambiente e evidência de persistência real; P1 e P3 permanecem centradas, respectivamente, em teste de serviço e repetibilidade.",
        "- Não foi criada avaliação nem atribuída exclusividade sem apoio no enunciado. Todos os três assuntos de cada unidade possuem item exclusivo; as questões de fronteira permanecem compartilhadas onde a fonte exige dois assuntos.",
        "",
    ])
    return lines


def write_reports(builder: Builder, types: dict, results: dict, warnings: list[str], mappings: int) -> None:
    with (ROOT / REPORTS[0]).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "unidade", "origem", "secao", "bloco", "tipo", "alias", "destino",
            "inicio_char", "fim_char", "palavras", "sha256_texto", "normalizacao_estrutural_autorizada",
        ])
        writer.writeheader()
        for row in builder.records:
            notes = []
            for rule in f4.normalization_rules(builder.m):
                if rule["unidade"] == row["unidade"] and rule["alias"] == row["alias"] and f"]({rule['caminho_original']})" in row["texto"]:
                    notes.append(rule["caminho_original"] + " -> " + rule["caminho_migrado"] + "; visible label preserved")
            writer.writerow({
                "unidade": row["unidade"], "origem": row["origem"], "secao": row["secao"],
                "bloco": row["bloco"], "tipo": row["tipo"], "alias": row["alias"],
                "destino": row["destino"], "inicio_char": row["inicio"], "fim_char": row["fim"],
                "palavras": engine.words(row["texto"]), "sha256_texto": sha_text(row["texto"]),
                "normalizacao_estrutural_autorizada": "; ".join(notes),
            })
    type_lines = [f"- {kind}: {count}" for kind, count in sorted(types.items())]
    unit_lines = ["| Unidade | Assuntos | Arquivos | Mapeamentos | Metadados |", "|---|---:|---:|---:|---|"]
    metadata = ["| Unidade | Campo | Valor original | Valor no README YAML | Resultado |", "|---|---|---|---|---|"]
    for unit_key, unit in builder.m["unidades"].items():
        result = results[unit_key]
        subjects = len(unit["assuntos"]) if not unit.get("tipo_projeto") else "projeto"
        unit_lines.append(f"| {unit_key} | {subjects} | {result['arquivos']} | {result['mapeamentos']} | OK |")
        for key, value in [("title", builder.sources[unit_key]["title"]), *unit["metadados_originais"].items()]:
            encoded = json.dumps(value, ensure_ascii=False)
            metadata.append(f"| {unit_key} | {key} | {encoded} | {encoded} | OK |")
    normalizations = [
        f"- {rule['unidade']}/{rule['alias']}: {rule['caminho_original']} → {rule['caminho_migrado']}; "
        f"{rule['ocorrencias']} ocorrência(s), destino {rule['destino_recurso']}."
        for rule in f4.normalization_rules(builder.m)
    ] or ["- Nenhuma."]
    validation = [
        "# Relatório de validação — migração estrutural da Fase 5", "",
        "- Veredito: APROVADA COM RESSALVAS; wikilinks Obsidian continuam condicionados à raiz do vault.",
        f"- Base: {BASE}; branch migracao-estrutura.",
        "- Inventário: 20 unidades (18 convencionais e 2 projetos); 59 assuntos.",
        f"- Arquivos: {len(builder.outputs)}; mapeamentos: {mappings}.",
        "- Conteúdo: 81 microtópicos; 90 questões; 54 práticas; 54 rubricas de prática; 2 rubricas de projeto; 8 marcos/aceites; 1 checklist final.",
        "", "## Arquivos por tipo", "", *type_lines, "", "## Resultado por unidade", "", *unit_lines,
        "", "## Conversão de metadados", "", *metadata, "",
        "## Auditoria pedagógica direcionada",
        "- 20.1: Q4 e P3 avaliam sessão/ciclo de vida; as alternativas da P3 são condicionais. Q5 cruza JWT/tokens e OAuth/OIDC.",
        "- 24.2: P2 exige rota HTTP e persistência real. Q1 cruza planejamento e persistência; Q4 cruza persistência e isolamento.",
        "- Nenhuma atividade foi criada ou redistribuída contra seu enunciado.",
        "- A previsão inicial de 486 foi reconciliada para 483: os agrupamentos de 20.1 e 24.2 evitam quatro arquivos separados que não correspondem à divisão final; a nota original do instrutor de 23.3 tem um arquivo próprio.",
        "", *directed_coverage_report(builder),
        "", "## Integridade",
        "- Os segmentos reais foram comparados por intervalos, hashes e reconstrução integral de cada seção; blocos de código conferidos separadamente.",
        "- As respostas em linha de 19.1/Q1–Q5 foram divididas com enunciados e respostas literais do manifesto.",
        "- 24.3 preserva quatro marcos, quatro aceites, rubrica 0–4 e checklist final de oito itens.",
        "- 24.4 preserva quatro marcos, quatro aceites, rubrica 0–4 e tabela T1–T5 no Marco 3; nenhum checklist final foi criado.",
        "- Os três hrefs do guia em 24.4 foram ajustados somente para a nova localização; o alvo existe e a normalização está no manifesto.",
        "- Originais, JSON, guia preexistente e 1.073 arquivos das Fases 1–4 permaneceram inalterados.",
        "", "## Normalizações estruturais autorizadas", "", *normalizations, "",
        "## Ressalvas", "", *[f"- {warning}" for warning in warnings],
    ]
    (ROOT / REPORTS[1]).write_text("\n".join(validation) + "\n", encoding="utf-8", newline="\n")
    audit = [
        "# Auditoria final — migração estrutural da Fase 5", "", "## Veredito", "",
        "APROVADA COM RESSALVAS", "", f"- Base: {BASE}; branch migracao-estrutura.",
        f"- Arquivos: {len(builder.outputs)}; mapeamentos: {mappings}; unidades: 20; assuntos: 59; projetos: 2.",
        "- Integridade textual aprovada pela comparação dos segmentos reais; sem lacunas ou sobreposições.",
        "- Respostas: 90; práticas/soluções/rubricas: 54; rubricas de projeto: 2 (0–4).",
        "- 24.3 conserva oito itens no checklist final; 24.4 conserva T1–T5 no aceite do Marco 3 e não tem checklist final.",
        "- 19.1/Q1–Q5 foi separado por limites literais; 24.4 teve três hrefs normalizados.",
        "", "## Resultado por unidade", "", "| Unidade | Arquivos | Mapeamentos | Status |", "|---|---:|---:|---|",
        *[f"| {key} | {value['arquivos']} | {value['mapeamentos']} | OK |" for key, value in results.items()],
        "", "## Preservação", "", *[f"- {warning}" for warning in warnings],
        "- IDs f5 únicos e sem colisão com 1.073 IDs anteriores.",
        "- Fases 1–4, originais e JSON preservados byte a byte.",
        "- Nenhum commit, importador ou migração da Fase 6 foi executado.",
        "", "O CSV contém o mapeamento de cada segmento original para seu destino.",
    ]
    (ROOT / REPORTS[2]).write_text("\n".join(audit) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and structurally migrate Trilha Code Fase 5")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--audit-existing", action="store_true", help="audits an existing generated tree and writes only the three reports")
    mode.add_argument("--reproduce-temp", action="store_true", help="regenerates to a verified temporary directory and compares every file/hash to the persisted tree")
    args = parser.parse_args()
    manifest_path = ROOT / MANIFEST
    manifest_bytes = manifest_path.read_bytes()
    manifest = engine.yaml(manifest_bytes.decode("utf-8-sig"), "Fase 5 manifest")
    engine.manifest = manifest
    errors = validate_manifest(manifest)
    if errors:
        print("MANIFEST INVALID")
        for item in errors:
            print("- " + item)
        return 2
    run_mode = "apply" if args.apply else "audit-existing" if args.audit_existing else "reproduce-temp" if args.reproduce_temp else "dry-run"
    errors = git_preflight(run_mode)
    if errors:
        print("GIT PREFLIGHT FAILED")
        for item in errors:
            print("- " + item)
        return 3
    if not (ROOT / JSON).is_file():
        print("JSON import file missing")
        return 3
    protected = protected_snapshot(manifest)
    previous = previous_snapshot()
    ids = previous_ids()
    if len(previous) != 1073 or len(ids) != 1073:
        print(f"expected 1,073 prior files/IDs, found {len(previous)}/{len(ids)}")
        return 3
    manifest_hash = sha_file(manifest_path)
    runtime = runtime_manifest(manifest)
    engine.manifest = runtime
    builder = Builder(runtime)
    builder.build()
    repeated = Builder(runtime_manifest(engine.yaml(manifest_path.read_text(encoding="utf-8-sig"), "independent rebuild")))
    repeated.build()
    if repeated.outputs != builder.outputs:
        raise SystemExit("independent source reconstruction differs")
    if sha_file(manifest_path) != manifest_hash:
        raise SystemExit("manifest changed during dry run")
    audit_errors, unit_results, warnings = audit(builder, previous, protected, ids)
    if audit_errors:
        print("PRE-WRITE AUDIT FAILED")
        for item in audit_errors:
            print("- " + item)
        return 4
    print(
        f"DRY-RUN OK | base={BASE} | units=20 | conventional=18 | projects=2 | subjects=59 | "
        f"theory=81 | questions=90 | practices=54 | practice_rubrics=54 | project_rubrics=2 | "
        f"milestones=8 | files={len(builder.outputs)} | mappings={len(builder.records)}"
    )
    print("types=" + json.dumps(builder.types(), ensure_ascii=False, sort_keys=True))
    for key, result in unit_results.items():
        print(f"unit={key}|files={result['arquivos']}|mappings={result['mapeamentos']}")
    print("links=" + "; ".join(x for x in warnings if x.startswith(("resolved_markdown_links=", "preserved_wikilinks="))))
    if args.audit_existing:
        destination = ROOT / DEST
        actual = {
            path.relative_to(ROOT).as_posix(): read_text(path)
            for path in destination.rglob("*") if path.is_file()
        }
        expected = {rel.as_posix(): norm(text) for rel, text in builder.outputs.items()}
        if set(actual) != set(expected):
            print(f"EXISTING TREE INVENTORY MISMATCH | actual={len(actual)} expected={len(expected)}")
            print("missing=" + repr(sorted(set(expected) - set(actual))))
            print("unexpected=" + repr(sorted(set(actual) - set(expected))))
            return 5
        differing = [rel for rel in expected if actual[rel] != expected[rel]]
        if differing:
            print("EXISTING TREE CONTENT MISMATCH | " + repr(differing[:30]))
            return 5
        if sha_file(manifest_path) != manifest_hash or previous_snapshot() != previous:
            raise SystemExit("manifest or prior phases changed during existing-tree audit")
        write_reports(builder, builder.types(), unit_results, warnings, len(builder.records))
        print(f"EXISTING TREE AUDITED | files={len(actual)} | mappings={len(builder.records)} | reports written")
        print("No generated content was rewritten.")
        return 0
    if args.reproduce_temp:
        temp_parent = Path(tempfile.gettempdir()).resolve()
        with tempfile.TemporaryDirectory(prefix="trilhacode-f5-repro-", dir=str(temp_parent)) as temp_name:
            temp_root = Path(temp_name).resolve()
            if temp_root.parent != temp_parent or not temp_root.name.startswith("trilhacode-f5-repro-"):
                raise SystemExit("temporary reproduction root failed containment check")
            isolated = temp_root / "Fase_5"
            isolated.mkdir()
            expected_temp = {}
            for rel, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
                relative = safe_rel(rel.relative_to(PurePosixPath(DEST)).as_posix())
                path = isolated.joinpath(*relative.parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                encoded = norm(text).encode("utf-8")
                path.write_bytes(encoded)
                expected_temp[relative.as_posix()] = hashlib.sha256(encoded).hexdigest()
            temporary = {
                path.relative_to(isolated).as_posix(): sha_file(path)
                for path in isolated.rglob("*") if path.is_file()
            }
            existing_root = ROOT / DEST
            existing = {
                path.relative_to(existing_root).as_posix(): sha_file(path)
                for path in existing_root.rglob("*") if path.is_file()
            }
            if len(temporary) != 483 or temporary != expected_temp:
                raise SystemExit("isolated temporary output inventory/hash differs from manifest reconstruction")
            if existing != temporary:
                missing = sorted(set(temporary) - set(existing))
                extra = sorted(set(existing) - set(temporary))
                differing = sorted(path for path in set(existing) & set(temporary) if existing[path] != temporary[path])
                print(f"TEMPORARY REPRODUCTION MISMATCH | missing={missing} | additional={extra} | hash_differences={differing}")
                return 5
            if manifest_path.read_bytes() != manifest_bytes or previous_snapshot() != previous:
                raise SystemExit("manifest or previous phases changed during temporary reproduction")
            print(f"TEMPORARY REPRODUCTION IDENTICAL | files={len(temporary)} | SHA-256 matched for every path")
            print("IDs, frontmatters, relative links, shared-file locations, and structural normalizations are byte-identical.")
        return 0
    if not args.apply:
        return 0
    if manifest_path.read_bytes() != manifest_bytes:
        raise SystemExit("manifest changed before generation")
    destination = ROOT / DEST
    if destination.exists():
        raise SystemExit("Fase 5 destination appeared before generation")
    destination.mkdir(parents=True, exist_ok=False)
    for rel, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        path = ROOT.joinpath(*rel.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(norm(text), encoding="utf-8", newline="\n")
    persisted = {}
    for rel, expected in builder.outputs.items():
        path = ROOT.joinpath(*rel.parts)
        actual = read_text(path)
        if not path.is_file() or actual != norm(expected):
            raise SystemExit(f"persisted output mismatch: {rel}")
        persisted[rel] = actual
    post = Builder(runtime_manifest(engine.yaml(manifest_path.read_text(encoding="utf-8-sig"), "post-write manifest")))
    post.build()
    if post.outputs != persisted:
        raise SystemExit("post-write reconstruction differs from persisted tree")
    post.outputs = persisted
    audit_errors, unit_results, warnings = audit(post, previous, protected, ids)
    if audit_errors:
        print("POST-WRITE AUDIT FAILED")
        for item in audit_errors:
            print("- " + item)
        return 5
    current = {p.relative_to(ROOT).as_posix(): sha_file(p) for p in destination.rglob("*") if p.is_file()}
    expected = {str(p): sha_file(ROOT.joinpath(*p.parts)) for p in persisted}
    if current != expected:
        raise SystemExit("persisted tree inventory/hash mismatch")
    if sha_file(manifest_path) != manifest_hash or previous_snapshot() != previous:
        raise SystemExit("manifest or previous phases changed during generation")
    write_reports(post, post.types(), unit_results, warnings, len(post.records))
    print(f"MIGRATION OK | files={len(persisted)} | mappings={len(post.records)} | verdict=APROVADA COM RESSALVAS")
    print("reports=" + ", ".join(REPORTS))
    print("No commit, JSON import, or Fase 6 migration was performed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STOPPED: {type(exc).__name__}: {exc}")
        raise
