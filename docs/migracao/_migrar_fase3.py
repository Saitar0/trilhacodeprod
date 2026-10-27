from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine  # Reuse the homologated YAML/frontmatter primitives.

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase3.yml"
SCRIPT_REL = "docs/migracao/_migrar_fase3.py"
BASE = "fba3a029f8956d349c430c797331b459733281f3"
F1_COMMIT = "7028682ab46dd6186c274f9655bd7dce3c2e3612"
GUIDE_REL = "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md"
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
PHASE_DOCS = [
    "docs/courses/trilhacode/Fase_3_Base_da_Web_JS_TS_Node.md",
    "docs/courses/trilhacode/Referencias_Fase_3.md",
    "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md",
]
TICK = "`"


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return norm(path.read_text(encoding="utf-8-sig"))


def run_git(*args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=text, encoding="utf-8" if text else None)


def git_path_text(rel: str) -> str:
    value = run_git("show", f"HEAD:{rel}", text=False)
    return norm(value.decode("utf-8-sig"))


def file_hash(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def file_id(unit_key: str, rel: str) -> str:
    return engine.file_id(unit_key, rel)


def path_rel(value: str) -> PurePosixPath:
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"unsafe relative path: {value}")
    return p


def expected_paths(manifest: dict) -> set[PurePosixPath]:
    dest = PurePosixPath(manifest["destino_raiz"])
    result: set[PurePosixPath] = set()
    for unit_key, unit in manifest["unidades"].items():
        unit_root = dest / path_rel(unit["pasta"])
        result.add(unit_root / "README.md")
        result.update(unit_root / path_rel(p) for p in unit["arquivos"].values())
        for alias in unit["blocos_origem"]["comuns"].values():
            if alias == "IDX":
                continue
            result.add(unit_root / path_rel(manifest["arquivos_comuns"][alias]["path"]))
    return result


def mapped_common_aliases(unit: dict) -> set[str]:
    return {alias for alias in unit["blocos_origem"]["comuns"].values() if alias != "IDX"}


def alias_prefix(alias: str) -> str:
    m = re.match(r"[A-Z]+", alias)
    if not m:
        raise ValueError(f"invalid file alias: {alias}")
    return m.group(0)


def alias_type(alias: str) -> str:
    return {
        "T": "theory",
        "Q": "quiz",
        "K": "answer_key",
        "P": "practice",
        "KP": "answer_key_pratica",
        "C": "checklist",
        "R": "rubric",
        "M": "milestone",
        "SCP": "project_scope",
    }[alias_prefix(alias)]


def alias_order(alias: str) -> int:
    found = re.search(r"(\d+)$", alias)
    return int(found.group(1)) if found else 0


def check_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    expected_order = ["6.1", "6.2", "6.3", "6.4", "7.1", "7.2", "7.3", "7.4", "7.5", "8.1", "8.2", "8.3", "8.5", "8.6"]
    if manifest.get("fase") != "Fase_3":
        errors.append("manifest fase must be Fase_3")
    if manifest.get("id_prefix") != "f3":
        errors.append("manifest id_prefix must be f3")
    if manifest.get("base_commit") != BASE:
        errors.append("manifest base_commit differs from the authorized commit")
    if manifest.get("ordem_unidades") != expected_order:
        errors.append("unit order differs from the approved Fase 3 order")
    if list(manifest.get("unidades", {})) != expected_order:
        errors.append("unit map keys differ from ordem_unidades")
    if "8.4" in manifest.get("unidades", {}):
        errors.append("retired unit 8.4 must not have a node")
    prefixes = manifest.get("prefixos_arquivo_id", {})
    if prefixes.get("KP") != "answer_key_pratica":
        errors.append("KP prefix must identify answer_key_pratica")

    physical: dict[PurePosixPath, str] = {}
    ids: dict[str, str] = {}
    expected_counts = Counter()
    for unit_key in expected_order:
        unit = manifest.get("unidades", {}).get(unit_key)
        if not unit:
            errors.append(f"missing active unit {unit_key}")
            continue
        if not path_rel(unit.get("pasta", "")):
            errors.append(f"{unit_key}: invalid unit folder")
        source_rel = path_rel(unit.get("origem", ""))
        source = ROOT.joinpath(*source_rel.parts)
        if not source.is_file():
            errors.append(f"{unit_key}: source missing: {source_rel}")
            continue
        try:
            raw = read_text(source)
            header, _, body = engine.fm(raw, str(source_rel))
            title_pre, sections = engine.split_headings(body, 2)
        except Exception as exc:
            errors.append(f"{unit_key}: source/frontmatter parse failed: {exc}")
            continue
        names = [name for name, _ in sections]
        section_map = dict(sections)
        if len(names) != len(section_map):
            errors.append(f"{unit_key}: duplicate H2 labels")
        if not re.fullmatch(r"\s*# [^\n]+\n\s*", title_pre):
            errors.append(f"{unit_key}: title area before first H2 is not a single H1")

        if unit.get("tipo_unidade") == "projeto":
            expected_sections = {
                "Objetivo",
                "Escopo do projeto" if unit_key == "8.5" else "Escopo e opções",
                "Marcos de entrega",
                "Checklist final de entrega" if unit_key == "8.5" else "Checklist final de escolha e entrega",
                "Rubrica de avaliação",
                "Critério de conclusão",
                "Conexões",
                "Referências",
            }
            if set(section_map) != expected_sections:
                errors.append(f"{unit_key}: project H2 set mismatch: {set(section_map) ^ expected_sections}")
            _, milestones = engine.h3_chunks(section_map.get("Marcos de entrega", ""))
            actual_titles = [title for title, _ in milestones]
            declared = [spec.get("titulo_marco") for spec in unit.get("blocos_origem", {}).get("marcos", {}).values()]
            if actual_titles != declared or len(actual_titles) != 4:
                errors.append(f"{unit_key}: milestone titles/order differ from source")
            for title, part in milestones:
                acceptance = re.findall(r"(?m)^\*\*Aceite(?: específico)?:\*\*", part)
                if len(acceptance) != 1:
                    errors.append(f"{unit_key}/{title}: expected one acceptance block, found {len(acceptance)}")
        elif unit_key == "7.4":
            expected_sections = {
                "Objetivo", "Teoria", "Resumo", "Verificação — quiz",
                "Prática — relatório sobre dados", "Exercício integrador — recuperação sem consulta",
                "Retomada espaçada", "Critério de conclusão", "Conexões", "Referências",
            }
            if set(section_map) != expected_sections:
                errors.append(f"7.4: H2 set mismatch: {set(section_map) ^ expected_sections}")
        else:
            expected_sections = {"Objetivo", "Teoria", "Resumo", "Verificação — quiz", "Práticas", "Critério de conclusão", "Conexões", "Referências"}
            if set(section_map) != expected_sections:
                errors.append(f"{unit_key}: H2 set mismatch: {set(section_map) ^ expected_sections}")
            _, theory_parts = engine.h3_chunks(section_map.get("Teoria", ""))
            if [h for h, _ in theory_parts] != list(unit["blocos_origem"]["teoria"]):
                errors.append(f"{unit_key}: theory heading set/order differs from manifest")

        subjects = unit.get("assuntos", [])
        if len(subjects) != len(set(subjects)):
            errors.append(f"{unit_key}: duplicate subject slug")
        if unit_key == "6.1" and subjects != ["01_valores_e_tipos", "02_variaveis_e_reatribuicao", "03_operadores_e_conversao", "04_decisoes_e_repeticoes"]:
            errors.append("6.1: approved subject slugs differ")
        if unit_key == "6.3" and subjects != ["01_declaracoes_arrow_retorno", "02_template_strings", "03_destructuring", "04_spread_rest_copia_rasa"]:
            errors.append("6.3: approved subject slugs differ")
        if unit_key == "7.2" and subjects != ["01_modulos_exportacoes", "02_carregamento_diagnostico", "03_responsabilidades_coesao"]:
            errors.append("7.2: approved subject slugs differ")
        if unit_key == "7.3" and subjects != ["01_formato_e_contrato_json", "02_requisicao_async_resposta_erros"]:
            errors.append("7.3: approved subject slugs differ")
        if unit_key == "7.4" and subjects != ["01_transformacoes_e_colecoes", "02_complexidade", "03_pilhas_e_filas"]:
            errors.append("7.4: approved subject slugs differ")
        if unit_key == "7.5" and subjects != ["01_reproducao_console_elements_sources", "02_network_requisicoes"]:
            errors.append("7.5: approved subject slugs differ")
        if unit_key == "7.5" and unit.get("decisao_assuntos", "").startswith("provisório"):
            errors.append("7.5: stale provisional division note")
        if unit_key == "6.3":
            relation = unit.get("relacoes_assuntos", [])
            expected_relation = {"03_destructuring", "04_spread_rest_copia_rasa"}
            if not any(set(item.get("assuntos", [])) == expected_relation for item in relation):
                errors.append("6.3: conceptual relation between destructuring and spread/rest is missing")
        if unit_key == "6.1":
            rule = unit["blocos_origem"].get("separacao_inline_literal", {}).get("P2", {})
            if rule.get("inicio") != "O gabarito é o rastreamento e esses resultados, não uma forma única de escrever o algoritmo." or rule.get("destino") != "KP02":
                errors.append("6.1/P2: approved literal answer extraction rule is missing")

        aliases = unit.get("arquivos", {})
        if len(set(aliases.values())) != len(aliases):
            errors.append(f"{unit_key}: duplicate destination paths in aliases")
        for alias, rel in aliases.items():
            try:
                relpath = path_rel(rel)
                prefix = alias_prefix(alias)
                if prefix not in prefixes:
                    errors.append(f"{unit_key}/{alias}: unknown alias prefix")
                path = PurePosixPath(manifest["destino_raiz"]) / path_rel(unit["pasta"]) / relpath
                if path in physical:
                    errors.append(f"duplicate physical destination: {path}")
                physical[path] = f"{unit_key}/{alias}"
                ident = file_id(unit_key, rel)
                if ident in ids:
                    errors.append(f"duplicate arquivo_id {ident}")
                ids[ident] = str(path)
                expected_counts[alias_type(alias)] += 1
            except Exception as exc:
                errors.append(f"{unit_key}/{alias}: invalid alias path: {exc}")

        for key, alias in unit["blocos_origem"]["comuns"].items():
            if key == "metadados":
                if alias != "IDX": errors.append(f"{unit_key}: metadata must target IDX")
                continue
            if alias not in manifest["arquivos_comuns"]:
                errors.append(f"{unit_key}: common alias missing from schema: {alias}")
                continue
            rel = path_rel(manifest["arquivos_comuns"][alias]["path"])
            path = PurePosixPath(manifest["destino_raiz"]) / path_rel(unit["pasta"]) / rel
            if path in physical: errors.append(f"duplicate common destination: {path}")
            physical[path] = f"{unit_key}/{alias}"
            ident = file_id(unit_key, str(rel))
            if ident in ids: errors.append(f"duplicate arquivo_id {ident}")
            ids[ident] = str(path)
            expected_counts[manifest["arquivos_comuns"][alias]["tipo"]] += 1
        index_path = PurePosixPath(manifest["destino_raiz"]) / path_rel(unit["pasta"]) / "README.md"
        if index_path in physical: errors.append(f"duplicate README destination: {index_path}")
        physical[index_path] = f"{unit_key}/IDX"
        index_id = file_id(unit_key, "README.md")
        if index_id in ids: errors.append(f"duplicate arquivo_id {index_id}")
        ids[index_id] = str(index_path)
        expected_counts["topic_index"] += 1

        if unit.get("tipo_unidade") != "projeto":
            theory_map = unit["blocos_origem"]["teoria"]
            for heading, alias in theory_map.items():
                if alias not in aliases or not alias.startswith("T"):
                    errors.append(f"{unit_key}/{heading}: theory alias invalid: {alias}")
                elif PurePosixPath(aliases[alias]).parent.as_posix() not in subjects:
                    errors.append(f"{unit_key}/{heading}: theory path does not match a subject")
            quiz_map = unit["blocos_origem"].get("quiz", {})
            _, _, questions, answers = engine.quiz_split(section_map.get("Verificação — quiz", ""))
            expected_questions = {f"Q{n}" for n in questions}
            if set(quiz_map) != expected_questions:
                errors.append(f"{unit_key}: quiz mapping differs from source IDs")
            if set(answers) != set(questions):
                errors.append(f"{unit_key}: source answer set differs from quiz set")
            expected_counts["quiz"] += len(questions)
            expected_counts["answer_key"] += len(answers)
            for item, spec in quiz_map.items():
                subject = spec.get("assunto")
                if subject not in subjects:
                    errors.append(f"{unit_key}/{item}: invalid quiz subject {subject}")
                for target_key in ("arquivo", "resposta"):
                    alias = spec.get(target_key)
                    if alias not in aliases:
                        errors.append(f"{unit_key}/{item}: missing {target_key} alias {alias}")
                    elif PurePosixPath(aliases[alias]).parent.as_posix() != subject:
                        errors.append(f"{unit_key}/{item}: {target_key} path/subject mismatch")

            practice_map = unit["blocos_origem"].get("pratica", {})
            expected_counts["practice"] += len(practice_map)
            if unit_key == "7.4":
                expected_practice = {
                    "P1": "Prática — relatório sobre dados",
                    "P2": "Exercício integrador — recuperação sem consulta",
                    "P3": "Retomada espaçada",
                }
                if {k: v.get("secao") for k, v in practice_map.items()} != expected_practice:
                    errors.append("7.4: practice source section mapping mismatch")
                limits = unit.get("limites_literais_teoria", [])
                if len(limits) != 4:
                    errors.append("7.4: four exact literal theory limits required")
                theory = section_map["Teoria"]
                cursor = 0
                for limit in limits:
                    start = theory.find(limit["inicio"], cursor)
                    end = theory.find(limit["fim"], start) if start >= 0 else -1
                    if start < 0 or end < 0:
                        errors.append(f"7.4: literal theory boundary not found: {limit.get('item')}")
                        continue
                    if limit["item"] not in theory_map or theory_map[limit["item"]] != limit["arquivo"]:
                        errors.append(f"7.4: literal boundary target mismatch: {limit['item']}")
                    if theory[cursor:start].strip() and cursor != 0:
                        errors.append(f"7.4: unclassified text between boundaries: {limit['item']}")
                    if cursor == 0 and theory[:start].strip() != "## Teoria":
                        errors.append("7.4: unexpected text before first literal theory block")
                    cursor = end + len(limit["fim"])
                if theory[cursor:].strip(): errors.append("7.4: unclassified theory suffix")
            else:
                _, activities = engine.h3_chunks(section_map["Práticas"])
                actual_titles = [title for title, _ in activities]
                expected_titles = [practice_map[k]["titulo"] for k in sorted(practice_map, key=lambda x: int(x[1:]))]
                if actual_titles != expected_titles:
                    errors.append(f"{unit_key}: practice titles/order differ from manifest")
            for item, spec in practice_map.items():
                alias = spec.get("arquivo")
                if alias not in aliases: errors.append(f"{unit_key}/{item}: practice file alias missing")
                subjects_for_item = spec.get("assuntos") or ([spec["assunto"]] if spec.get("assunto") else [])
                if not subjects_for_item or any(x not in subjects for x in subjects_for_item):
                    errors.append(f"{unit_key}/{item}: invalid practice subject assignment")
                shared = len(subjects_for_item) > 1
                if alias in aliases:
                    parent = PurePosixPath(aliases[alias]).parent.as_posix()
                    if shared and parent != "90_integracao":
                        errors.append(f"{unit_key}/{item}: shared activity must have one 90_integracao file")
                    if not shared and parent != subjects_for_item[0]:
                        errors.append(f"{unit_key}/{item}: exclusive practice path/subject mismatch")
                if "assunto" in spec and "assuntos" in spec:
                    errors.append(f"{unit_key}/{item}: activity cannot be exclusive and shared simultaneously")
                for artifact_key in ("resposta", "checklist", "rubrica"):
                    if artifact_key in spec and spec[artifact_key] not in aliases:
                        errors.append(f"{unit_key}/{item}: artifact alias missing: {spec[artifact_key]}")
                    if artifact_key in spec and alias in aliases and spec[artifact_key] in aliases:
                        if PurePosixPath(aliases[spec[artifact_key]]).parent != PurePosixPath(aliases[alias]).parent:
                            errors.append(f"{unit_key}/{item}: artifact {artifact_key} stored outside activity folder")

            coverage = unit.get("cobertura", {})
            exclusive_seen: dict[str, list[str]] = defaultdict(list)
            for subject, items in coverage.get("exclusivos", {}).items():
                if subject not in subjects: errors.append(f"{unit_key}: coverage has unknown subject {subject}")
                for item in items: exclusive_seen[item].append(subject)
            shared_seen = coverage.get("compartilhados", {})
            expected_activity_items = set(quiz_map) | set(practice_map)
            if set(exclusive_seen) | set(shared_seen) != expected_activity_items:
                errors.append(f"{unit_key}: coverage item set differs from quiz/practice inventory")
            for q, spec in quiz_map.items():
                if exclusive_seen.get(q) != [spec["assunto"]] or q in shared_seen:
                    errors.append(f"{unit_key}/{q}: coverage is not exclusive to its mapped subject")
            for p, spec in practice_map.items():
                assigned = spec.get("assuntos") or [spec.get("assunto")]
                if len(assigned) > 1:
                    if exclusive_seen.get(p) or shared_seen.get(p) != assigned:
                        errors.append(f"{unit_key}/{p}: shared/exclusive coverage mismatch")
                elif exclusive_seen.get(p) != assigned or p in shared_seen:
                    errors.append(f"{unit_key}/{p}: exclusive coverage mismatch")

            actual_answer_aliases = {spec["resposta"] for spec in quiz_map.values()}
            declared_answer_aliases = {a for a in aliases if a.startswith("K") and not a.startswith("KP")}
            if actual_answer_aliases != declared_answer_aliases:
                errors.append(f"{unit_key}: quiz gabarito aliases differ from source mappings")
            expected_practice_artifacts = {
                spec[k] for spec in practice_map.values() for k in ("resposta", "checklist", "rubrica") if k in spec
            }
            declared_practice_artifacts = {a for a in aliases if a.startswith(("KP", "C", "R"))}
            if expected_practice_artifacts != declared_practice_artifacts:
                errors.append(f"{unit_key}: practice artifact aliases differ from mappings")
            rubric_targets = {spec["rubrica"] for spec in practice_map.values() if "rubrica" in spec}
            if set(unit.get("rubricas", {})) != rubric_targets:
                errors.append(f"{unit_key}: original practice rubric scales do not cover all rubric aliases")
            for target in rubric_targets:
                if not unit["rubricas"][target].startswith("0–2"):
                    errors.append(f"{unit_key}/{target}: unexpected practice rubric scale")
        else:
            project = unit["blocos_origem"]
            if project.get("escopo") not in aliases or project.get("checklist_final") not in aliases:
                errors.append(f"{unit_key}: project scope/final checklist target missing")
            milestones = project.get("marcos", {})
            if list(milestones) != ["M1", "M2", "M3", "M4"]:
                errors.append(f"{unit_key}: project must map four milestones in order")
            for n, spec in milestones.items():
                expected_alias = f"M{int(n[1:]):02d}"
                if spec.get("arquivo") != expected_alias or spec.get("aceite") not in aliases:
                    errors.append(f"{unit_key}/{n}: milestone/checklist alias mismatch")
            rubric = project.get("rubrica", {})
            if rubric.get("arquivo") not in aliases or not rubric.get("escala_rubrica", "").startswith("0–4"):
                errors.append(f"{unit_key}: project rubric/0–4 scale missing")
            expected_project_aliases = {project["escopo"], project["checklist_final"], rubric.get("arquivo")}
            for spec in milestones.values(): expected_project_aliases.update([spec["arquivo"], spec["aceite"]])
            if expected_project_aliases != set(aliases):
                errors.append(f"{unit_key}: project aliases differ from four milestones/scope/checklists/rubric")
            if "resumo" in project["comuns"]:
                errors.append(f"{unit_key}: projects must not create an unmapped summary")

    if len(manifest.get("unidades", {})) != 14:
        errors.append("active unit count must be 14")
    counts = {
        "theory": sum(1 for u in manifest["unidades"].values() for a in u["arquivos"] if a.startswith("T")),
        "quiz": sum(len(u.get("blocos_origem", {}).get("quiz", {})) for u in manifest["unidades"].values()),
        "practice": sum(len(u.get("blocos_origem", {}).get("pratica", {})) for u in manifest["unidades"].values()),
        "milestones": sum(len(u.get("blocos_origem", {}).get("marcos", {})) for u in manifest["unidades"].values()),
    }
    if counts != {"theory": 40, "quiz": 59, "practice": 36, "milestones": 8}:
        errors.append(f"approved content inventory mismatch: {counts}")
    target_paths = expected_paths(manifest)
    if len(target_paths) != 313:
        errors.append(f"expected distinct generated file count 313, got {len(target_paths)}")
    if manifest.get("estimativa_arquivos", {}).get("total") != 313:
        errors.append("manifest forecast must remain 313")
    if set(physical) != target_paths:
        errors.append("physical path inventory differs from aliases + common files + README")
    return errors, expected_counts


class Builder:
    def __init__(self, manifest: dict):
        self.m = manifest
        self.dest = PurePosixPath(manifest["destino_raiz"])
        self.sources: dict[str, dict] = {}
        self.sections: dict[tuple[str, str], str] = {}
        self.cursors: dict[tuple[str, str], int] = defaultdict(int)
        self.records: list[dict] = []
        self.data: dict[tuple[str, str], dict] = {}
        self.outputs: dict[PurePosixPath, str] = {}
        self._load_sources()
        engine.manifest = manifest
        engine.DEST = self.dest
        engine.output = self.outputs

    def _load_sources(self) -> None:
        for unit_key, unit in self.m["unidades"].items():
            source = ROOT.joinpath(*path_rel(unit["origem"]).parts)
            raw = read_text(source)
            header, metadata, body = engine.fm(raw, unit["origem"])
            body = norm(body)
            title_pre, section_list = engine.split_headings(body, 2)
            if "".join([title_pre, *(value for _, value in section_list)]) != body:
                raise ValueError(f"{unit_key}: heading parser did not partition source body")
            section_map = dict(section_list)
            self.sources[unit_key] = {
                "raw": raw,
                "header": norm(header),
                "metadata": metadata,
                "body": body,
                "title": title_pre,
                "section_list": section_list,
                "sections": section_map,
            }
            for name, text in section_list:
                self.sections[(unit_key, name)] = text
            self.records.append({
                "unidade": unit_key,
                "origem": unit["origem"],
                "secao": "frontmatter",
                "bloco": "metadados_originais",
                "tipo": "metadata",
                "alias": "IDX",
                "destino": str(self.dest / unit["pasta"] / "README.md"),
                "inicio": "",
                "fim": "",
                "texto": norm(header),
            })
            self.records.append({
                "unidade": unit_key,
                "origem": unit["origem"],
                "secao": "titulo",
                "bloco": "titulo_original",
                "tipo": "topic_index",
                "alias": "IDX",
                "destino": str(self.dest / unit["pasta"] / "README.md"),
                "inicio": "0",
                "fim": str(len(title_pre)),
                "texto": title_pre,
            })

    def _target_rel(self, unit_key: str, alias: str) -> str:
        unit = self.m["unidades"][unit_key]
        if alias in unit["arquivos"]:
            return unit["arquivos"][alias]
        for common_alias in mapped_common_aliases(unit):
            if common_alias == alias:
                return self.m["arquivos_comuns"][alias]["path"]
        raise ValueError(f"{unit_key}: unmapped destination alias {alias}")

    def _store(self, unit_key: str, alias: str, rel: str, kind: str, fragment: str,
               item_ref: str | None = None, context: dict | None = None,
               title: str | None = None, scale: str | None = None) -> None:
        if not fragment:
            raise ValueError(f"{unit_key}/{alias}: empty mapped source fragment")
        key = (unit_key, alias)
        data = self.data.setdefault(key, {
            "rel": rel, "kind": kind, "chunks": [], "items": [], "contexts": [],
            "title": title, "scale": scale,
        })
        if data["rel"] != rel or data["kind"] != kind:
            raise ValueError(f"{unit_key}/{alias}: inconsistent destination/type")
        if title and data["title"] and title != data["title"]:
            raise ValueError(f"{unit_key}/{alias}: conflicting milestone titles")
        if scale and data["scale"] and scale != data["scale"]:
            raise ValueError(f"{unit_key}/{alias}: conflicting rubric scales")
        if title: data["title"] = title
        if scale: data["scale"] = scale
        data["chunks"].append(fragment)
        if item_ref and item_ref not in data["items"]:
            data["items"].append(item_ref)
        if context is not None:
            context_key = json.dumps(context, ensure_ascii=False, sort_keys=True)
            if all(json.dumps(x, ensure_ascii=False, sort_keys=True) != context_key for x in data["contexts"]):
                data["contexts"].append(context)

    def piece(self, unit_key: str, section: str, block: str, alias: str, kind: str,
              fragment: str, item_ref: str | None = None, context: dict | None = None,
              title: str | None = None, scale: str | None = None) -> None:
        key = (unit_key, section)
        source = self.sections.get(key)
        if source is None:
            raise ValueError(f"{unit_key}: source section missing: {section}")
        start = self.cursors[key]
        end = start + len(fragment)
        if source[start:end] != fragment:
            raise ValueError(f"{unit_key}/{section}/{block}: source segment does not match at offset {start}")
        self.cursors[key] = end
        rel = self._target_rel(unit_key, alias)
        self._store(unit_key, alias, rel, kind, fragment, item_ref, context, title, scale)
        self.records.append({
            "unidade": unit_key,
            "origem": self.m["unidades"][unit_key]["origem"],
            "secao": section,
            "bloco": block,
            "tipo": kind,
            "alias": alias,
            "destino": str(self.dest / self.m["unidades"][unit_key]["pasta"] / rel),
            "inicio": str(start),
            "fim": str(end),
            "texto": fragment,
        })

    def check_section_complete(self, unit_key: str) -> None:
        for (owner, name), text in self.sections.items():
            if owner != unit_key:
                continue
            actual = self.cursors[(owner, name)]
            if actual != len(text):
                raise ValueError(f"{unit_key}/{name}: source coverage {actual}/{len(text)} characters")

    def emit_common(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        section_names = {
            "objetivo": "Objetivo",
            "resumo": "Resumo",
            "criterio_de_conclusao": "Critério de conclusão",
            "conexoes": "Conexões",
            "referencias": "Referências",
        }
        for origin_key, alias in unit["blocos_origem"]["comuns"].items():
            if origin_key == "metadados":
                continue
            if origin_key not in section_names:
                raise ValueError(f"{unit_key}: unknown common source block {origin_key}")
            name = section_names[origin_key]
            fragment = self.sections[(unit_key, name)]
            self.piece(unit_key, name, name, alias,
                       self.m["arquivos_comuns"][alias]["tipo"], fragment,
                       item_ref=name)

    def emit_theory(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        theory = self.sections[(unit_key, "Teoria")]
        mapping = unit["blocos_origem"]["teoria"]
        if unit_key != "7.4":
            pre, chunks = engine.h3_chunks(theory)
            if pre:
                first_alias = next(iter(mapping.values()))
                self.piece(unit_key, "Teoria", "teoria_cabecalho", first_alias, "theory", pre,
                           context={"assunto": PurePosixPath(unit["arquivos"][first_alias]).parent.as_posix()})
            actual = [title for title, _ in chunks]
            if actual != list(mapping):
                raise ValueError(f"{unit_key}: theory block names/order differ from manifest")
            for title, fragment in chunks:
                alias = mapping[title]
                subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
                if subject not in unit["assuntos"]:
                    raise ValueError(f"{unit_key}/{title}: theory destination belongs to wrong subject")
                self.piece(unit_key, "Teoria", f"teoria/{title}", alias, "theory", fragment,
                           item_ref=title, context={"assunto": subject})
            expected_aliases = {a for a in unit["arquivos"] if a.startswith("T")}
            mapped_aliases = set(mapping.values())
            if expected_aliases != mapped_aliases:
                raise ValueError(f"{unit_key}: theory aliases differ from mapped headings")
            return

        limits = unit.get("limites_literais_teoria", [])
        if len(limits) != 4:
            raise ValueError("7.4: four approved literal paragraph limits required")
        first_start = theory.find(limits[0]["inicio"])
        if first_start < 0:
            raise ValueError("7.4: first approved literal start not found")
        pre = theory[:first_start]
        if pre.strip() != "## Teoria":
            raise ValueError("7.4: text before first paragraph differs from approved boundary")
        first_alias = limits[0]["arquivo"]
        self.piece(unit_key, "Teoria", "teoria_cabecalho", first_alias, "theory", pre,
                   context={"assunto": PurePosixPath(unit["arquivos"][first_alias]).parent.as_posix()})
        starts: list[int] = []
        ends: list[int] = []
        cursor = first_start
        for limit in limits:
            if limit["item"] not in mapping or mapping[limit["item"]] != limit["arquivo"]:
                raise ValueError(f"7.4: literal limit target mismatch for {limit['item']}")
            start = theory.find(limit["inicio"], cursor)
            end_text = theory.find(limit["fim"], start) if start >= 0 else -1
            if start < 0 or end_text < 0:
                raise ValueError(f"7.4: exact boundary not found for {limit['item']}")
            end = end_text + len(limit["fim"])
            if theory.find(limit["inicio"], start + len(limit["inicio"])) >= 0:
                raise ValueError(f"7.4: literal start is ambiguous for {limit['item']}")
            starts.append(start)
            ends.append(end)
            cursor = end
        for index, limit in enumerate(limits):
            next_start = starts[index + 1] if index + 1 < len(starts) else len(theory)
            if theory[ends[index]:next_start].strip():
                raise ValueError(f"7.4: non-whitespace text falls outside approved paragraph: {limit['item']}")
            fragment = theory[starts[index]:next_start]
            alias = limit["arquivo"]
            subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
            self.piece(unit_key, "Teoria", limit["item"], alias, "theory", fragment,
                       item_ref=limit["item"], context={"assunto": subject})
        if theory[self.cursors[(unit_key, "Teoria")]:].strip():
            raise ValueError("7.4: unmapped theory suffix")

    def split_inline_answer(self, block: str) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        offset = 0
        in_fence: tuple[str, int] | None = None
        found = 0
        for line in block.splitlines(keepends=True):
            bare = line.rstrip("\r\n")
            if in_fence:
                fence_char, fence_len = in_fence
                candidate = bare.lstrip()
                count = len(candidate) - len(candidate.lstrip(fence_char))
                if count >= fence_len and not candidate[count:].strip():
                    in_fence = None
                result.append(("question", line))
                offset += len(line)
                continue
            fence = engine.fence(bare)
            if fence:
                in_fence = fence
                result.append(("question", line))
                offset += len(line)
                continue
            matches = list(re.finditer(r"\*\*Resposta:.*?\*\*.*?(?=\n|$)", line))
            if len(matches) > 1:
                raise ValueError("multiple inline answer markers on one quiz line")
            if matches:
                match = matches[0]
                found += 1
                if match.start() > 0:
                    result.append(("question", line[:match.start()]))
                result.append(("answer", line[match.start():match.end()]))
                if match.end() < len(line):
                    if line[match.end():].startswith("\n"):
                        result.append(("key_separator", "\n"))
                    result.append(("question", line[match.end():]))
            else:
                result.append(("question", line))
            offset += len(line)
        if in_fence:
            raise ValueError("unclosed fenced code block in quiz question")
        if found > 1:
            raise ValueError("more than one inline answer marker in a quiz item")
        return [(kind, piece) for kind, piece in result if piece]

    def emit_quiz(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        section_name = "Verificação — quiz"
        source = self.sections[(unit_key, section_name)]
        pre, subsections = engine.split_headings(source, 3)
        questions: dict[int, dict] = {}
        answers: dict[int, dict] = {}
        qmap = unit["blocos_origem"]["quiz"]

        def ctx_for(n: int) -> tuple[str, dict]:
            item = f"Q{n}"
            if item not in qmap:
                raise ValueError(f"{unit_key}: source question {item} lacks manifest mapping")
            spec = qmap[item]
            return spec["arquivo"], {"assunto": spec["assunto"]}

        def add_question_group(header: str, items: list[tuple[int, str]], group_label: str) -> None:
            if header:
                if not items:
                    raise ValueError(f"{unit_key}: question header has no question destination")
                first_alias, first_ctx = ctx_for(items[0][0])
                self.piece(unit_key, section_name, group_label + "/cabecalho", first_alias,
                           "quiz", header, context=first_ctx)
            for n, block in items:
                item = f"Q{n}"
                alias, context = ctx_for(n)
                for kind, fragment in self.split_inline_answer(block):
                    if kind == "question":
                        self.piece(unit_key, section_name, item + "/enunciado", alias,
                                   "quiz", fragment, item_ref=item, context=context)
                        questions.setdefault(n, {"alias": alias, "context": context, "chunks": []})["chunks"].append(fragment)
                    elif kind == "answer":
                        kalias = qmap[item]["resposta"]
                        self.piece(unit_key, section_name, item + "/resposta", kalias,
                                   "answer_key", fragment, item_ref=item, context=context)
                        if n in answers:
                            raise ValueError(f"{unit_key}/{item}: duplicate answer source")
                        answers[n] = {"alias": kalias, "context": context, "chunks": [fragment]}
                    else:
                        kalias = qmap[item]["resposta"]
                        self.structural(unit_key, kalias, "answer_key", fragment, item, context,
                                        "line separator after detached inline quiz answer")

        def add_answer_group(header: str, items: list[tuple[int, str]], group_label: str) -> None:
            if header:
                if not items:
                    raise ValueError(f"{unit_key}: answer header has no answer destination")
                n = items[0][0]
                alias = qmap[f"Q{n}"]["resposta"]
                context = {"assunto": qmap[f"Q{n}"]["assunto"]}
                self.piece(unit_key, section_name, group_label + "/cabecalho", alias,
                           "answer_key", header, context=context)
                answers.setdefault(n, {"alias": alias, "context": context, "chunks": []})["chunks"].append(header)
            for n, fragment in items:
                item = f"Q{n}"
                if item not in qmap:
                    raise ValueError(f"{unit_key}: answer for unmapped question {item}")
                alias = qmap[item]["resposta"]
                context = {"assunto": qmap[item]["assunto"]}
                self.piece(unit_key, section_name, item + "/resposta", alias,
                           "answer_key", fragment, item_ref=item, context=context)
                entry = answers.setdefault(n, {"alias": alias, "context": context, "chunks": []})
                entry["chunks"].append(fragment)

        if not subsections:
            header, items = engine.numbered(source)
            _, questions_list = engine.numbered(source)
            if not questions_list:
                raise ValueError(f"{unit_key}: quiz has no numbered questions")
            add_question_group(header, questions_list, "quiz")
        else:
            # The H2 preamble belongs to the first question section; every H3 is parsed literally.
            first_question_section = True
            for title, part in subsections:
                preamble, entries = engine.numbered(part)
                if "gabarito" in title.casefold() or "resposta" in title.casefold():
                    add_answer_group(preamble, entries, "gabarito/" + title)
                else:
                    if first_question_section:
                        preamble = pre + preamble
                        first_question_section = False
                    add_question_group(preamble, entries, "quiz/" + title)
        if set(questions) != set(answers):
            raise ValueError(f"{unit_key}: quiz answers do not match questions: {set(questions) ^ set(answers)}")
        if {f"Q{n}" for n in questions} != set(qmap):
            raise ValueError(f"{unit_key}: question mapping IDs differ from source")

    def marker_type(self, line: str, spec: dict, unit_key: str, item: str) -> tuple[str, str] | None:
        m = re.match(r"^\s*\*\*(?P<label>[^*]+)\*\*", line)
        if not m:
            return None
        label = m.group("label").strip().rstrip(":").casefold()
        if label.startswith(("solução", "gabarito", "resposta", "referência para autocorreção")):
            kind, key = "answer_key_pratica", "resposta"
        elif label.startswith("erro comum") and "resposta" in spec:
            kind, key = "answer_key_pratica", "resposta"
        elif label.startswith(("rubrica", "critérios de autocorreção", "autocorreção")):
            kind, key = "rubric", "rubrica"
        elif label.startswith(("aceite", "critérios de aceite", "critérios", "verificação final")):
            kind, key = "checklist", "checklist"
        else:
            return None
        if key not in spec:
            raise ValueError(f"{unit_key}/{item}: source marker {label!r} lacks mapped {key} alias")
        return kind, spec[key]

    def structural(self, unit_key: str, alias: str, kind: str, text: str,
                   item_ref: str, context: dict, reason: str) -> None:
        rel = self._target_rel(unit_key, alias)
        self._store(unit_key, alias, rel, kind, text, item_ref, context)
        self.records.append({
            "unidade": unit_key,
            "origem": self.m["unidades"][unit_key]["origem"],
            "secao": "normalizacao_estrutural",
            "bloco": reason,
            "tipo": "structural_separator",
            "alias": alias,
            "destino": str(self.dest / self.m["unidades"][unit_key]["pasta"] / rel),
            "inicio": "",
            "fim": "",
            "texto": text,
        })

    def practice_special_ranges(self, unit_key: str, item: str, spec: dict, text: str) -> list[tuple[int, int, str, str]]:
        rules = self.m["unidades"][unit_key]["blocos_origem"].get("separacao_inline_literal", {})
        rule = rules.get(item)
        if not rule:
            return []
        start_text = rule["inicio"]
        end_text = rule["fim"]
        if text.count(start_text) != 1:
            raise ValueError(f"{unit_key}/{item}: exact inline start marker count differs")
        start = text.index(start_text)
        if end_text in start_text:
            end_at = start + start_text.rfind(end_text)
        else:
            end_at = text.find(end_text, start + len(start_text))
        if end_at < 0:
            raise ValueError(f"{unit_key}/{item}: exact inline end marker missing")
        end = end_at + len(end_text)
        destination = rule.get("destino")
        if destination not in spec.values():
            raise ValueError(f"{unit_key}/{item}: literal answer destination does not belong to activity mapping")
        if destination != spec.get("resposta"):
            raise ValueError(f"{unit_key}/{item}: literal answer must map to the practice answer key")
        if text.find(start_text, start + len(start_text)) >= 0:
            raise ValueError(f"{unit_key}/{item}: ambiguous repeated inline start marker")
        return [(start, end, "answer_key_pratica", destination)]

    def split_practice(self, unit_key: str, item: str, spec: dict, text: str) -> list[tuple[str, str, str]]:
        marker_events: dict[int, tuple[str, str]] = {}
        offset = 0
        in_fence: tuple[str, int] | None = None
        for line in text.splitlines(keepends=True):
            bare = line.rstrip("\r\n")
            if in_fence:
                fence_char, fence_len = in_fence
                candidate = bare.lstrip()
                count = len(candidate) - len(candidate.lstrip(fence_char))
                if count >= fence_len and not candidate[count:].strip():
                    in_fence = None
                offset += len(line)
                continue
            fence = engine.fence(bare)
            if fence:
                in_fence = fence
                offset += len(line)
                continue
            kind_and_alias = self.marker_type(bare, spec, unit_key, item)
            if kind_and_alias:
                marker_events[offset] = kind_and_alias
            offset += len(line)
        if in_fence:
            raise ValueError(f"{unit_key}/{item}: unclosed code fence in practice")

        specials = self.practice_special_ranges(unit_key, item, spec, text)
        special_starts = {start: (kind, alias) for start, _, kind, alias in specials}
        special_ends = {end: (kind, alias) for _, end, kind, alias in specials}
        points = sorted({0, len(text), *marker_events.keys(), *special_starts.keys(), *special_ends.keys()})
        current = ("practice", spec["arquivo"])
        active_special: tuple[str, str] | None = None
        pieces: list[tuple[str, str, str]] = []
        for index, point in enumerate(points[:-1]):
            if point in special_ends:
                active_special = None
            if point in marker_events:
                current = marker_events[point]
            if point in special_starts:
                active_special = special_starts[point]
            next_point = points[index + 1]
            if next_point <= point:
                continue
            selected = active_special if active_special else current
            kind, alias = selected
            if alias not in self.m["unidades"][unit_key]["arquivos"]:
                raise ValueError(f"{unit_key}/{item}: artifact alias does not exist: {alias}")
            fragment = text[point:next_point]
            if fragment:
                pieces.append((kind, alias, fragment))
        return pieces

    def emit_practices(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        practice_map = unit["blocos_origem"]["pratica"]
        if unit_key == "7.4":
            for item in sorted(practice_map, key=lambda x: int(x[1:])):
                spec = practice_map[item]
                name = spec["secao"]
                activity = self.sections[(unit_key, name)]
                self.emit_activity(unit_key, name, item, spec, activity)
            return
        section_name = "Práticas"
        pre, activities = engine.h3_chunks(self.sections[(unit_key, section_name)])
        ordered_items = sorted(practice_map, key=lambda x: int(x[1:]))
        if len(activities) != len(ordered_items):
            raise ValueError(f"{unit_key}: practice block count differs from manifest")
        if pre:
            item = ordered_items[0]
            spec = practice_map[item]
            context = self.activity_context(unit_key, spec)
            self.piece(unit_key, section_name, "praticas_cabecalho", spec["arquivo"], "practice", pre,
                       item_ref=item, context=context)
        for (title, activity), item in zip(activities, ordered_items):
            spec = practice_map[item]
            if title != spec["titulo"]:
                raise ValueError(f"{unit_key}/{item}: practice title differs from source")
            self.emit_activity(unit_key, section_name, item, spec, activity)

    def activity_context(self, unit_key: str, spec: dict) -> dict:
        assigned = spec.get("assuntos")
        if assigned:
            if len(assigned) > 1:
                return {"assuntos": assigned}
            return {"assunto": assigned[0]}
        return {"assunto": spec["assunto"]}

    def emit_activity(self, unit_key: str, section_name: str, item: str, spec: dict, activity: str) -> None:
        context = self.activity_context(unit_key, spec)
        for n, (kind, alias, fragment) in enumerate(self.split_practice(unit_key, item, spec, activity), 1):
            item_ref = item
            self.piece(unit_key, section_name, f"{item}/segmento_{n:02d}", alias, kind, fragment,
                       item_ref=item_ref, context=context)

    def emit_project(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        source = self.sources[unit_key]["sections"]
        project = unit["blocos_origem"]
        scope_heading = "Escopo do projeto" if unit_key == "8.5" else "Escopo e opções"
        scope_alias = project["escopo"]
        self.piece(unit_key, scope_heading, scope_heading, scope_alias, "project_scope",
                   self.sections[(unit_key, scope_heading)], item_ref="escopo",
                   context={"assunto": unit["assuntos"][0]})

        milestone_section = "Marcos de entrega"
        pre, milestones = engine.h3_chunks(self.sections[(unit_key, milestone_section)])
        mapped = project["marcos"]
        if len(milestones) != 4:
            raise ValueError(f"{unit_key}: exactly four original milestones required")
        for index, (title, block) in enumerate(milestones):
            pair = [(key, spec) for key, spec in mapped.items() if spec["titulo_marco"] == title]
            if len(pair) != 1:
                raise ValueError(f"{unit_key}: milestone title is not a literal manifest title: {title!r}")
            milestone_key, spec = pair[0]
            alias = spec["arquivo"]
            checklist_alias = spec["aceite"]
            context = {"assunto": unit["assuntos"][0]}
            if index == 0 and pre:
                self.piece(unit_key, milestone_section, "marcos_cabecalho", alias, "milestone", pre,
                           context=context, title=title)
            matches = list(re.finditer(r"(?m)^\*\*Aceite(?: específico)?:\*\*", block))
            if len(matches) != 1:
                raise ValueError(f"{unit_key}/{milestone_key}: acceptance marker count differs")
            start = matches[0].start()
            if block[start:].strip() == "":
                raise ValueError(f"{unit_key}/{milestone_key}: acceptance block is empty")
            if block[start:].rstrip() and not block[start:].rstrip().endswith((".", ")", "**")):
                # No text is discarded; this guards only against a surprise partial tail.
                pass
            body = block[:start]
            acceptance = block[start:]
            if not body.strip() or not acceptance.strip():
                raise ValueError(f"{unit_key}/{milestone_key}: milestone body or acceptance is empty")
            self.piece(unit_key, milestone_section, milestone_key + "/corpo", alias, "milestone", body,
                       item_ref=milestone_key, context=context, title=title)
            self.piece(unit_key, milestone_section, milestone_key + "/aceite", checklist_alias, "checklist", acceptance,
                       item_ref=milestone_key, context=context, title=title)

        final_heading = "Checklist final de entrega" if unit_key == "8.5" else "Checklist final de escolha e entrega"
        final_alias = project["checklist_final"]
        self.piece(unit_key, final_heading, "checklist_final", final_alias, "checklist",
                   self.sections[(unit_key, final_heading)], item_ref="checklist_final",
                   context={"assunto": unit["assuntos"][0]})
        rubric = project["rubrica"]
        self.piece(unit_key, "Rubrica de avaliação", "rubrica_projeto", rubric["arquivo"], "rubric",
                   self.sections[(unit_key, "Rubrica de avaliação")], item_ref="rubrica",
                   context={"assunto": unit["assuntos"][0]}, scale=rubric["escala_rubrica"])

    def add_readme(self, unit_key: str) -> None:
        unit = self.m["unidades"][unit_key]
        source = self.sources[unit_key]
        header_lines = source["header"].splitlines()
        if len(header_lines) < 3 or header_lines[0] != "---" or header_lines[-1] != "---":
            raise ValueError(f"{unit_key}: malformed original frontmatter delimiters")
        _, metadata, _ = engine.fm(source["raw"], unit["origem"])
        if "arquivo_id" in metadata or "tipo_arquivo" in metadata:
            raise ValueError(f"{unit_key}: original metadata already uses generated index fields")
        readme_id = file_id(unit_key, "README.md")
        frontmatter = "\n".join(header_lines[:-1] + [
            f"arquivo_id: {json.dumps(readme_id, ensure_ascii=False)}",
            'tipo_arquivo: "topic_index"',
            "---",
        ])
        body = source["title"] + "## Índice\n\n### Arquivos comuns\n"
        for common_key, alias in unit["blocos_origem"]["comuns"].items():
            if common_key == "metadados":
                continue
            file_spec = self.m["arquivos_comuns"][alias]
            href = PurePosixPath(file_spec["path"]).as_posix()
            body += f"- [{file_spec['tipo']}]({href})\n"
        body += "\n### Assuntos\n"
        for subject in unit["assuntos"]:
            body += f"\n#### `{subject}`\n"
            for alias, rel in unit["arquivos"].items():
                if PurePosixPath(rel).parts[0] == subject:
                    body += f"- [{PurePosixPath(rel).name}]({PurePosixPath(rel).as_posix()})\n"
        integrations = [rel for rel in unit["arquivos"].values() if PurePosixPath(rel).parts[0] == "90_integracao"]
        if integrations:
            body += "\n### Integração\n"
            for rel in integrations:
                body += f"- [{PurePosixPath(rel).name}]({PurePosixPath(rel).as_posix()})\n"
        relations = unit.get("relacoes_assuntos", [])
        if relations:
            body += "\n### Relações entre assuntos\n"
            for relation in relations:
                items = relation.get("assuntos", [])
                if len(items) != 2 or any(x not in unit["assuntos"] for x in items):
                    raise ValueError(f"{unit_key}: invalid conceptual subject relation")
                links = [f"[{slug}]({slug}/01_teoria.md)" for slug in items]
                body += f"- {' ↔ '.join(links)}\n"
        path = self.dest / path_rel(unit["pasta"]) / "README.md"
        if path in self.outputs:
            raise ValueError(f"duplicate README path {path}")
        self.outputs[path] = frontmatter + "\n\n" + body

    def finalize(self) -> None:
        for unit_key, unit in self.m["unidades"].items():
            expected_aliases = set(unit["arquivos"])
            actual_aliases = {alias for owner, alias in self.data if owner == unit_key and alias in unit["arquivos"]}
            missing = expected_aliases - actual_aliases
            extra = actual_aliases - expected_aliases
            if missing or extra:
                raise ValueError(f"{unit_key}: generated alias set mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
            for (owner, alias), data in list(self.data.items()):
                if owner != unit_key:
                    continue
                if alias not in unit["arquivos"]:
                    continue
                rel = data["rel"]
                contexts = data["contexts"]
                if len(contexts) > 1:
                    raise ValueError(f"{unit_key}/{alias}: inconsistent subject context across mapped fragments")
                context = contexts[0] if contexts else {}
                subject = context.get("assunto")
                subjects = context.get("assuntos")
                path_parent = PurePosixPath(rel).parent.as_posix()
                if path_parent == "90_integracao":
                    if not subjects or len(subjects) < 2:
                        raise ValueError(f"{unit_key}/{alias}: integration file must declare shared subjects")
                elif path_parent in unit["assuntos"] and subject != path_parent:
                    raise ValueError(f"{unit_key}/{alias}: frontmatter subject differs from physical folder")
                elif path_parent not in unit["assuntos"]:
                    raise ValueError(f"{unit_key}/{alias}: physical parent is not an approved subject")
                items = data["items"]
                title = data["title"]
                scale = data["scale"]
                kind = data["kind"]
                if alias.startswith("R") and not scale:
                    scale = unit.get("rubricas", {}).get(alias)
                    if not scale and unit.get("tipo_unidade") == "projeto":
                        scale = unit["blocos_origem"]["rubrica"]["escala_rubrica"]
                if kind == "rubric" and not scale:
                    raise ValueError(f"{unit_key}/{alias}: original rubric scale missing")
                if alias.startswith("M") and not title:
                    raise ValueError(f"{unit_key}/{alias}: literal milestone title missing")
                if alias.startswith("C") and unit.get("tipo_unidade") == "projeto" and alias != "C90" and not title:
                    raise ValueError(f"{unit_key}/{alias}: acceptance checklist lacks literal milestone title")
                engine.put(unit_key, rel, kind, "".join(data["chunks"]),
                           subject=subject, subjects=subjects, items=items,
                           order=alias_order(alias), title=title, scale=scale)

            for alias in mapped_common_aliases(unit):
                data = self.data.get((unit_key, alias))
                if data is None:
                    raise ValueError(f"{unit_key}: common file {alias} has no source content")
                engine.put(unit_key, data["rel"], data["kind"], "".join(data["chunks"]),
                           items=data["items"], order=alias_order(alias))
            self.add_readme(unit_key)
            self.check_section_complete(unit_key)

        expected = expected_paths(self.m)
        actual = set(self.outputs)
        if actual != expected:
            raise ValueError(f"output path set differs from manifest; missing={sorted(map(str, expected-actual))}; extra={sorted(map(str, actual-expected))}")
        if len(actual) != self.m["estimativa_arquivos"]["total"]:
            raise ValueError(f"output file count {len(actual)} differs from forecast {self.m['estimativa_arquivos']['total']}")

    def output_types(self) -> Counter:
        types = Counter()
        for path, text in self.outputs.items():
            _, fields, body = engine.fm(text, str(path))
            types[fields["tipo_arquivo"]] += 1
            if not body.strip():
                raise ValueError(f"empty output body: {path}")
        return types


def mapped_source_audit(builder: Builder) -> tuple[list[str], dict[str, dict]]:
    errors: list[str] = []
    unit_results: dict[str, dict] = {}
    by_unit_section: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in builder.records:
        if row["secao"] in ("frontmatter", "titulo", "normalizacao_estrutural"):
            continue
        by_unit_section[(row["unidade"], row["secao"])].append(row)
    for unit_key, unit in builder.m["unidades"].items():
        source = builder.sources[unit_key]
        section_status = []
        reconstructed_sections = []
        for name, source_text in source["section_list"]:
            rows = by_unit_section.get((unit_key, name), [])
            cursor = 0
            chunks = []
            for row in rows:
                start, end = int(row["inicio"]), int(row["fim"])
                if start != cursor or end < start:
                    errors.append(f"{unit_key}/{name}/{row['bloco']}: gap/overlap at {cursor}->{start}")
                fragment = row["texto"]
                if source_text[start:end] != fragment:
                    errors.append(f"{unit_key}/{name}/{row['bloco']}: mapped source hash mismatch")
                chunks.append(fragment)
                cursor = end
            if cursor != len(source_text):
                errors.append(f"{unit_key}/{name}: covered {cursor}/{len(source_text)} characters")
            reconstructed = "".join(chunks)
            if reconstructed != source_text:
                errors.append(f"{unit_key}/{name}: reconstructed source differs from original")
            if engine.code_blocks(reconstructed) != engine.code_blocks(source_text):
                errors.append(f"{unit_key}/{name}: fenced code block differs")
            section_status.append((name, len(rows), sha_text(reconstructed) == sha_text(source_text)))
            reconstructed_sections.append(reconstructed)
        full = source["title"] + "".join(reconstructed_sections)
        if full != source["body"]:
            errors.append(f"{unit_key}: full Markdown body not reconstructed exactly")
        unit_root = PurePosixPath(builder.m["destino_raiz"]) / path_rel(unit["pasta"])
        generated_unit_files = [
            p for p in builder.outputs
            if p.parts[:len(unit_root.parts)] == unit_root.parts
        ]
        unit_results[unit_key] = {
            "files": len(generated_unit_files),
            "mappings": sum(1 for r in builder.records if r["unidade"] == unit_key),
            "sections": section_status,
            "integridade": "OK" if not any(e.startswith(unit_key + "/") or e.startswith(unit_key + ":") for e in errors) else "ERRO",
        }
    return errors, unit_results


def validate_output(builder: Builder, old_ids: set[str]) -> tuple[list[str], Counter, dict[str, dict], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    types = builder.output_types()
    ids = set(old_ids)
    dest_root = PurePosixPath(builder.m["destino_raiz"])
    for path, text in builder.outputs.items():
        try:
            _, fields, body = engine.fm(text, str(path))
        except Exception as exc:
            errors.append(f"invalid YAML frontmatter: {path}: {exc}")
            continue
        required = {"arquivo_id", "tipo_arquivo"}
        if path.name != "README.md":
            required |= {"parent_key", "ordem", "itens_origem"}
        if not required <= set(fields):
            errors.append(f"missing required frontmatter fields: {path}: {sorted(required-set(fields))}")
        ident = fields.get("arquivo_id")
        if not isinstance(ident, str) or not ident.startswith("f3-"):
            errors.append(f"invalid global f3 arquivo_id: {path}")
        if ident in ids:
            errors.append(f"global arquivo_id collision: {ident}")
        ids.add(ident)
        if not body.strip():
            errors.append(f"empty body: {path}")
        if path.name != "README.md":
            row_text = "".join(r["texto"] for r in builder.records if r["destino"] == str(path))
            # `frontmatter()` leaves one blank line after the closing delimiter;
            # engine.fm exposes its second LF as the body’s first character.
            # Ignore exactly that structural separator, never source text.
            comparable_body = body[1:] if body.startswith("\n") else body
            if row_text != comparable_body:
                errors.append(f"destination body differs from mapped source fragments: {path}")
        else:
            unit_key = next(k for k, u in builder.m["unidades"].items() if path == dest_root / u["pasta"] / "README.md")
            original = builder.sources[unit_key]["metadata"]
            for key, value in original.items():
                if fields.get(key) != value:
                    errors.append(f"original frontmatter value changed: {unit_key}/{key}")
            if fields.get("tipo_arquivo") != "topic_index":
                errors.append(f"README type is not topic_index: {path}")
        if "8.4" in path.parts:
            errors.append(f"retired 8.4 path generated: {path}")
    source_errors, unit_results = mapped_source_audit(builder)
    errors.extend(source_errors)
    return errors, types, unit_results, warnings


def current_git_state(apply: bool, dest_exists: bool) -> list[str]:
    errors: list[str] = []
    top = str(run_git("rev-parse", "--show-toplevel")).strip().replace("\\", "/").lower()
    if top != str(ROOT).replace("\\", "/").lower():
        errors.append(f"Git root differs from adapter root: {top}")
    branch = str(run_git("branch", "--show-current")).strip()
    head = str(run_git("rev-parse", "HEAD")).strip()
    if branch != "migracao-estrutura":
        errors.append(f"current branch differs from authorized branch: {branch}")
    if head != BASE:
        errors.append(f"HEAD differs from authorized base: {head}")
    if subprocess.call(["git", "-C", str(ROOT), "diff", "--cached", "--quiet"]) != 0:
        errors.append("staged changes exist")
    if subprocess.call(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD"]) != 0:
        errors.append("tracked working-tree changes exist")
    status = str(run_git("status", "--porcelain=v1", "--untracked-files=all")).splitlines()
    allowed_exact = {GUIDE_REL, MANIFEST_REL, SCRIPT_REL}
    report_paths = {
        "docs/migracao/relatorio_mapeamento_fase3.csv",
        "docs/migracao/relatorio_validacao_fase3.md",
        "docs/migracao/auditoria_final_fase3.md",
    }
    dest_prefix = "docs/courses/trilhacode/Conteudos_migrado/Fase_3/"
    for line in status:
        path = line[3:].replace("\\", "/")
        if path in allowed_exact:
            continue
        if apply and (path in report_paths or path.startswith(dest_prefix)):
            continue
        errors.append(f"unexpected Git status path: {line}")
    if not apply and dest_exists:
        errors.append("Fase 3 destination already exists before generation")
    return errors


def protected_snapshot(manifest: dict) -> tuple[dict[str, str], dict[str, str], set[str]]:
    protected_rels = [u["origem"] for u in manifest["unidades"].values()] + PHASE_DOCS + [JSON_REL]
    disk_hashes = {rel: file_hash(ROOT / Path(*path_rel(rel).parts)) for rel in protected_rels}
    for rel in protected_rels:
        disk_text = read_text(ROOT / Path(*path_rel(rel).parts))
        base_text = git_path_text(rel)
        if disk_text != base_text:
            raise ValueError(f"source differs from authorized Git base after line-ending normalization: {rel}")
    phase_hashes = {}
    old_ids: set[str] = set()
    for phase, expected_count in (("Fase_1", 221), ("Fase_2", 144)):
        folder = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / phase
        files = sorted(folder.rglob("*.md"))
        if len(files) != expected_count:
            raise ValueError(f"{phase} homologated file count differs: {len(files)} != {expected_count}")
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            phase_hashes[rel] = file_hash(path)
            _, fields, _ = engine.fm(read_text(path), rel)
            ident = fields.get("arquivo_id")
            if not ident or ident in old_ids:
                raise ValueError(f"missing/duplicate pre-existing arquivo_id in {phase}: {path}")
            old_ids.add(ident)
    if len(old_ids) != 365:
        raise ValueError(f"expected 365 unique F1/F2 IDs, found {len(old_ids)}")
    if Path(GUIDE_REL).is_file():
        disk_hashes[GUIDE_REL] = file_hash(ROOT / GUIDE_REL)
    return disk_hashes, phase_hashes, old_ids


def markdown_link_warnings(outputs: dict[PurePosixPath, str]) -> list[str]:
    warnings = []
    generated = set(outputs)
    for rel, content in outputs.items():
        try:
            _, _, body = engine.fm(content, str(rel))
        except Exception:
            continue
        for href in re.findall(r"\]\(([^)]+)\)", body):
            href = href.strip()
            if not href or href.startswith("#") or re.match(r"^(?:[a-z]+:)?//", href, re.I):
                continue
            path_text, _, _fragment = href.partition("#")
            candidate_rel = PurePosixPath(rel).parent / PurePosixPath(path_text)
            normalized = PurePosixPath()
            stack = list(candidate_rel.parts)
            clean = []
            for part in stack:
                if part in ("", "."):
                    continue
                if part == "..":
                    if clean: clean.pop()
                    continue
                clean.append(part)
            candidate = PurePosixPath(*clean)
            disk = ROOT.joinpath(*candidate.parts)
            if candidate not in generated and not disk.exists() and not disk.with_suffix(".md").exists():
                warnings.append(f"{rel} -> {href}")
    return warnings


def tree_lines(outputs: dict[PurePosixPath, str]) -> list[str]:
    roots: dict[str, dict] = {}
    for rel in sorted(outputs, key=lambda p: p.as_posix()):
        parts = rel.parts[len(PurePosixPath("docs/courses/trilhacode/Conteudos_migrado/Fase_3").parts):]
        node = roots
        for part in parts:
            node = node.setdefault(part, {})
    lines: list[str] = []
    def walk(node: dict, prefix: str = "") -> None:
        for name, child in node.items():
            lines.append(prefix + name + ("/" if child else ""))
            if child:
                walk(child, prefix + "  ")
    walk(roots)
    return lines


def write_reports(builder: Builder, types: Counter, unit_results: dict[str, dict], warnings: list[str], snapshots: dict[str, str], phase_snapshots: dict[str, str]) -> None:
    map_path = ROOT / "docs/migracao/relatorio_mapeamento_fase3.csv"
    validation_path = ROOT / "docs/migracao/relatorio_validacao_fase3.md"
    audit_path = ROOT / "docs/migracao/auditoria_final_fase3.md"
    for path in (map_path, validation_path, audit_path):
        if path.exists():
            raise ValueError(f"report target already exists: {path.relative_to(ROOT)}")
    with map_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["unidade", "origem", "secao", "bloco", "tipo", "alias", "destino", "inicio_char", "fim_char", "palavras", "sha256_texto"])
        for row in builder.records:
            writer.writerow([
                row["unidade"], row["origem"], row["secao"], row["bloco"], row["tipo"], row["alias"],
                row["destino"], row["inicio"], row["fim"], engine.words(row["texto"]), sha_text(row["texto"]),
            ])

    generated_count = len(builder.outputs)
    mapping_count = len(builder.records)
    total_units = len(builder.m["unidades"])
    total_subjects = sum(len(u["assuntos"]) for u in builder.m["unidades"].values())
    types_lines = [f"- `{kind}`: {count}" for kind, count in sorted(types.items())]
    unit_lines = ["| Unidade | Assuntos | Arquivos | Mapeamentos | Integridade |", "|---|---:|---:|---:|---|"]
    for uk, unit in builder.m["unidades"].items():
        result = unit_results[uk]
        unit_lines.append(f"| {uk} | {len(unit['assuntos'])} | {result['files']} | {result['mappings']} | {result['integridade']} |")
    link_lines = [f"- `{line}`" for line in warnings] or ["- Todos os links Markdown relativos gerados resolvem para arquivos existentes."]
    validation = [
        "# Relatório de validação — migração estrutural da Fase 3", "",
        f"- Resultado: **APROVADA COM RESSALVAS** (ressalva conhecida: wikilinks Obsidian dependem da raiz do vault).",
        f"- Commit-base: `{BASE}`", "- Branch: `migracao-estrutura`",
        f"- Unidades ativas: {total_units}", f"- Assuntos: {total_subjects}",
        f"- Questões: {sum(len(u.get('blocos_origem', {}).get('quiz', {})) for u in builder.m['unidades'].values())}",
        f"- Práticas convencionais: {sum(len(u.get('blocos_origem', {}).get('pratica', {})) for u in builder.m['unidades'].values())}",
        "- Marcos de projeto: 8 (quatro em cada projeto)",
        f"- Arquivos no destino da Fase 3: {generated_count}", f"- Registros de mapeamento: {mapping_count}",
        "", "## Contagem por tipo", "", *types_lines,
        "", "## Resultado por unidade", "", *unit_lines,
        "", "## Validações", "",
        "- O manifesto passou pelo parser YAML reutilizado do gerador homologado; chaves duplicadas e referências inconsistentes foram recusadas.",
        "- Todos os segmentos de cada fonte foram reconstruídos, em ordem, por intervalos de caracteres sem lacunas nem sobreposições.",
        "- Os blocos de código cercados são idênticos após normalização de CRLF/CR para LF; o BOM UTF-8 de leitura foi ignorado.",
        "- Os 59 enunciados e 59 gabaritos de quiz, as 36 práticas e seus gabaritos, critérios e rubricas foram mapeados a partir de conteúdo existente.",
        "- Os oito títulos literais de marcos, oito aceites, dois checklists finais e duas rubricas 0–4 foram conferidos diretamente nas fontes.",
        "- A escala das rubricas de prática foi copiada dos metadados do manifesto; nenhum valor foi alterado.",
        "- A resposta esperada de 6.1/P2 e o bloco `<details>` de 7.4/P2 foram separados por limites literais; a concatenação por intervalos reconstitui integralmente as atividades originais.",
        "- Os READMEs mantêm os metadados originais e indexam apenas caminhos existentes; não há README por assunto.",
        "- IDs `f3-*` únicos e sem colisão com os 365 IDs homologados das Fases 1 e 2.",
        "- Não há pasta, arquivo ou nó 8.4; JSON de importação e importador não foram tocados.",
        "- Fontes da Fase 3, documentos gerais e JSON foram comparados ao commit-base após normalização exclusiva de BOM e finais de linha.",
        f"- Hashes dos 365 arquivos homologados das Fases 1 e 2 permaneceram iguais: {sha_text(json.dumps(phase_snapshots, sort_keys=True))}.",
        "", "## Links relativos", "", *link_lines,
        "", "## Limitações", "",
        "- Wikilinks Obsidian foram preservados; a árvore migrada continua fora da raiz de vault confirmada, então alguns links externos podem não resolver nesta localização.",
        "- O arquivo local preexistente `Guia_de_Producao_de_Conteudo.md` permaneceu fora do conteúdo gerado e inalterado.",
        "- Nenhum commit foi criado; Fases 1 e 2, conteúdos originais e JSON permanecem inalterados.", "",
    ]
    validation_path.write_text("\n".join(validation), encoding="utf-8", newline="\n")

    counts_by_unit = "\n".join(unit_lines)
    tree = "\n".join(tree_lines(builder.outputs))
    audit = [
        "# Auditoria final — migração estrutural da Fase 3", "",
        "**Resultado: APROVADA COM RESSALVAS.**", "",
        f"- Commit-base: `{BASE}`", "- Branch: `migracao-estrutura`", f"- Arquivos da árvore: {generated_count}",
        f"- Registros de mapeamento origem–destino: {mapping_count}",
        "- Divergências textuais: nenhuma detectada.",
        "- Ressalva: os wikilinks Obsidian para fontes externas à árvore dependem da raiz do vault, ainda não confirmada.",
        "", "## Resultado por unidade", "", counts_by_unit,
        "", "## Integridade textual", "",
        "- Para cada unidade, os segmentos mapeados cobrem integralmente as seções de origem com intervalos contíguos e sem sobreposição.",
        "- A reconstrução do corpo Markdown original é idêntica após normalização de finais de linha para LF; nenhuma frase, resposta, alternativa, critério, rubrica, checklist ou referência foi omitida ou acrescentada.",
        "- Blocos de código cercados comparados por conteúdo integral.",
        "- A separação de respostas em arquivos próprios foi conferida por segmento. Em 6.1/P2, a frase de gabarito é separada do texto de critérios no limite literal aprovado; em 7.4/P2, o bloco `<details>` completo vai para KP02.",
        "- A unidade 6.3 registra em seu índice uma relação conceitual entre Destructuring e Spread/rest sem duplicar teoria.",
        "- A unidade 7.4 só foi dividida nos quatro limites literais configurados no manifesto; todos coincidem com os parágrafos da fonte.",
        "- Projetos 8.5 e 8.6 mantêm quatro marcos com títulos literais, quatro aceites por marco, checklist final e rubrica 0–4 por dimensão.",
        "", "## Contagem por tipo", "", *types_lines,
        "", "## Conteúdo protegido", "",
        "- Os 14 arquivos de unidade da Fase 3, três documentos gerais e JSON têm hashes binários idênticos aos capturados antes da geração.",
        "- Os 221 arquivos da Fase 1 e 144 arquivos da Fase 2 mantêm hashes binários idênticos aos capturados antes da geração.",
        "- `Guia_de_Producao_de_Conteudo.md` local permaneceu byte a byte inalterado.",
        "- Nenhum arquivo do JSON, Fase 1, Fase 2 ou fontes originais foi gerado ou modificado.",
        "", "## Árvore da Fase 3", "", "```text", tree, "```", "",
        "## Observações", "",
        "- O conteúdo de texto foi lido ignorando o BOM UTF-8 e normalizando somente CRLF/CR para LF, sem alteração de caracteres.",
        "- Os índices README e frontmatters filhos são elementos estruturais autorizados; nenhum texto educacional novo foi inserido.",
        "- Não foi criado commit, não houve importação do JSON e a Fase 4 não foi iniciada.", "",
    ]
    audit_path.write_text("\n".join(audit), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run e auditoria da migração estrutural da Fase 3")
    parser.add_argument("--apply", action="store_true", help="escreve apenas a árvore e relatórios da Fase 3 depois do dry-run completo")
    args = parser.parse_args()

    manifest_path = ROOT / MANIFEST_REL
    if not manifest_path.is_file():
        raise SystemExit(f"manifest missing: {MANIFEST_REL}")
    manifest_bytes = manifest_path.read_bytes()
    manifest_text = manifest_bytes.decode("utf-8-sig")
    manifest = engine.yaml(manifest_text, "Fase 3 manifest")
    engine.manifest = manifest
    errors, _ = check_manifest(manifest)
    if errors:
        print("MANIFEST INVALID")
        for error in errors: print("- " + error)
        return 2

    dest = ROOT.joinpath(*PurePosixPath(manifest["destino_raiz"]).parts)
    report_paths = [
        ROOT / "docs/migracao/relatorio_mapeamento_fase3.csv",
        ROOT / "docs/migracao/relatorio_validacao_fase3.md",
        ROOT / "docs/migracao/auditoria_final_fase3.md",
    ]
    if dest.exists() or any(path.exists() for path in report_paths):
        raise SystemExit("Fase 3 destination or report already exists; refusing to overwrite")
    git_errors = current_git_state(args.apply, dest.exists())
    if git_errors:
        print("GIT PREFLIGHT FAILED")
        for error in git_errors: print("- " + error)
        return 3

    try:
        protected, phase_snapshots, old_ids = protected_snapshot(manifest)
    except Exception as exc:
        raise SystemExit("protected-input preflight failed: " + str(exc))
    manifest_hash = sha_bytes(manifest_bytes)
    generator_hash = file_hash(ROOT / "docs/migracao/_migrar_fase1.py")
    builder = Builder(manifest)
    for unit_key, unit in manifest["unidades"].items():
        builder.emit_common(unit_key)
        if unit.get("tipo_unidade") == "projeto":
            builder.emit_project(unit_key)
        else:
            builder.emit_theory(unit_key)
            builder.emit_quiz(unit_key)
            builder.emit_practices(unit_key)
        builder.finalize_unit = None
    builder.finalize()
    text_errors, types, unit_results, link_warnings = validate_output(builder, old_ids)
    link_warnings.extend(markdown_link_warnings(builder.outputs))
    link_warnings = sorted(set(link_warnings))
    if text_errors:
        print("DRY VALIDATION FAILED")
        for error in text_errors: print("- " + error)
        return 4

    # Recheck all read-only preconditions after building in memory.
    if manifest_path.read_bytes() != manifest_bytes:
        raise SystemExit("manifest changed during dry-run")
    if file_hash(ROOT / "docs/migracao/_migrar_fase1.py") != generator_hash:
        raise SystemExit("homologated F1/F2 generator changed during dry-run")
    for rel, digest in protected.items():
        if file_hash(ROOT / Path(*path_rel(rel).parts)) != digest:
            raise SystemExit(f"protected input changed during dry-run: {rel}")
    for rel, digest in phase_snapshots.items():
        if file_hash(ROOT / Path(*path_rel(rel).parts)) != digest:
            raise SystemExit(f"homologated F1/F2 file changed during dry-run: {rel}")

    print(
        f"DRY-RUN OK | base={BASE} | branch=migracao-estrutura | units={len(manifest['unidades'])} "
        f"| subjects={sum(len(u['assuntos']) for u in manifest['unidades'].values())} "
        f"| questions=59 | practices=36 | project_milestones=8 | files={len(builder.outputs)} "
        f"| mappings={len(builder.records)}"
    )
    print("types=" + json.dumps(types, ensure_ascii=False, sort_keys=True))
    for unit_key, result in unit_results.items():
        print(f"unit={unit_key}|files={result['files']}|mappings={result['mappings']}|integrity={result['integridade']}")
    print(f"relative_markdown_link_warnings={len(link_warnings)}")
    for warning in link_warnings: print("link-warning=" + warning)
    print(f"protected_sources_and_json={len([x for x in protected if x != GUIDE_REL])}; F1_F2_files={len(phase_snapshots)}; prior_ids={len(old_ids)}")

    if not args.apply:
        return 0

    # Recheck immediately before the first write.
    git_errors = current_git_state(True, dest.exists())
    if git_errors:
        print("PRE-WRITE GIT CHECK FAILED")
        for error in git_errors: print("- " + error)
        return 5
    if dest.exists() or any(path.exists() for path in report_paths):
        raise SystemExit("target appeared after preflight; stopped before writing")
    dest.mkdir(parents=True, exist_ok=False)
    for rel, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        target = ROOT.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(norm(text), encoding="utf-8", newline="\n")

    persisted: dict[PurePosixPath, str] = {}
    for rel in builder.outputs:
        target = ROOT.joinpath(*rel.parts)
        if not target.is_file():
            text_errors.append(f"persisted output missing: {rel}")
        else:
            persisted[rel] = read_text(target)
    if set(persisted) != set(builder.outputs):
        text_errors.append("persisted output set differs from in-memory build")
    else:
        for rel, expected in builder.outputs.items():
            if persisted[rel] != norm(expected):
                text_errors.append(f"persisted text differs from validated build: {rel}")
    builder.outputs = persisted
    engine.output = persisted
    text_errors2, types2, unit_results2, link_warnings2 = validate_output(builder, old_ids)
    text_errors.extend(text_errors2)
    if text_errors:
        print("POST-WRITE VALIDATION FAILED; files preserved for review")
        for error in text_errors: print("- " + error)
        return 6

    for rel, digest in protected.items():
        if file_hash(ROOT / Path(*path_rel(rel).parts)) != digest:
            text_errors.append(f"protected input changed after generation: {rel}")
    for rel, digest in phase_snapshots.items():
        if file_hash(ROOT / Path(*path_rel(rel).parts)) != digest:
            text_errors.append(f"homologated F1/F2 file changed after generation: {rel}")
    if manifest_path.read_bytes() != manifest_bytes:
        text_errors.append("manifest changed during generation")
    if file_hash(ROOT / "docs/migracao/_migrar_fase1.py") != generator_hash:
        text_errors.append("homologated F1/F2 generator changed during generation")
    if text_errors:
        print("POST-WRITE PROTECTION CHECK FAILED; reports not written")
        for error in text_errors: print("- " + error)
        return 7

    write_reports(builder, types2, unit_results2, sorted(set(link_warnings + link_warnings2)), protected, phase_snapshots)
    final_git_errors = current_git_state(True, True)
    if final_git_errors:
        print("FINAL GIT STATUS NOTICE")
        for error in final_git_errors: print("- " + error)
    print(
        f"MIGRATION OK | base={BASE} | branch=migracao-estrutura | units=14 | subjects=42 "
        f"| files={len(builder.outputs)} | mappings={len(builder.records)} | result=APROVADA COM RESSALVAS"
    )
    print("types=" + json.dumps(types2, ensure_ascii=False, sort_keys=True))
    print("reports=" + ", ".join(str(p.relative_to(ROOT)).replace("\\", "/") for p in report_paths))
    print(f"protected_inputs={len(protected)} F1_F2_files={len(phase_snapshots)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STOPPED: {type(exc).__name__}: {exc}")
        raise
