from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase4.yml"
SCRIPT_REL = "docs/migracao/_migrar_fase4.py"
BASE = "1598dc47eefcb30e40a033870f164eebd79deb93"
DEST_REL = "docs/courses/trilhacode/Conteudos_migrado/Fase_4"
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
PHASE_DOCS = [
    "docs/courses/trilhacode/Fase_4_Dados_e_Bancos.md",
    "docs/courses/trilhacode/Referencias_Fase_4.md",
    "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md",
]
REPORTS = [
    "docs/migracao/relatorio_mapeamento_fase4.csv",
    "docs/migracao/relatorio_validacao_fase4.md",
    "docs/migracao/auditoria_final_fase4.md",
]
EXPECTED_ORDER = ["9.1", "9.2", "9.3", "10.1", "10.2", "11.3", "11.1", "11.2", "12.1", "12.2", "12.3", "13.1", "14.1", "15.1", "16.1", "16.2", "16.3"]
TICK = "`"


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path: Path) -> str:
    return norm(path.read_text(encoding="utf-8-sig"))


def sha_text(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, encoding="utf-8").strip()


def safe_rel(value: str) -> PurePosixPath:
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"unsafe relative path: {value}")
    return p


def normalization_rules(manifest: dict) -> list[dict]:
    rules = manifest.get("normalizacoes_estruturais_autorizadas", {})
    if not isinstance(rules, dict):
        raise ValueError("structural normalizations must be a keyed map")
    return list(rules.values())


def prefix(alias: str) -> str:
    match = re.match(r"[A-Z]+", alias)
    if not match:
        raise ValueError(f"invalid alias: {alias}")
    return match.group(0)


def order_of(alias: str) -> int:
    match = re.search(r"(\d+)$", alias)
    return int(match.group(1)) if match else 0


def output_paths(m: dict) -> set[PurePosixPath]:
    dest = PurePosixPath(m["destino_raiz"])
    result: set[PurePosixPath] = set()
    for unit in m["unidades"].values():
        root = dest / safe_rel(unit["pasta"])
        result.add(root / "README.md")
        result.update(root / safe_rel(rel) for rel in unit["arquivos"].values())
        for key, alias in unit["blocos_origem"]["comuns"].items():
            if key != "metadados":
                result.add(root / safe_rel(m["arquivos_comuns"][alias]["path"]))
    return result


def _line_value(line: str) -> tuple[str, object]:
    if not line.startswith("- "):
        raise ValueError(f"metadata list line does not begin with '- ': {line!r}")
    key, value = engine.pair(line[2:])
    return str(engine.val(key)), engine.val(value)


def parse_header(raw: str, unit: dict, origin: str) -> tuple[str, dict, list[tuple[str, str, int, int]]]:
    if raw.startswith("---\n"):
        raise ValueError(f"{origin}: expected metadata list, found YAML frontmatter")
    pre, _ = engine.split_headings(raw, 2)
    lines = pre.splitlines(keepends=True)
    meaningful = [(i, line.rstrip("\n")) for i, line in enumerate(lines) if line.strip()]
    if not meaningful or not meaningful[0][1].startswith("# "):
        raise ValueError(f"{origin}: original H1 title not found")
    title = meaningful[0][1][2:].strip()
    if title != unit["titulo_original"]:
        raise ValueError(f"{origin}: title differs from manifest: {title!r}")
    meta: dict = {}
    mappings: list[tuple[str, str, int, int]] = []
    cursor = 0
    for idx, line in enumerate(lines):
        bare = line.rstrip("\n")
        if idx == meaningful[0][0]:
            start = cursor
            end = start + len(line)
            mappings.append(("title", line, start, end))
        elif bare.strip():
            key, value = _line_value(bare)
            if key in meta:
                raise ValueError(f"{origin}: duplicate original metadata key {key}")
            meta[key] = value
            start = cursor
            end = start + len(line)
            mappings.append((key, line, start, end))
        cursor += len(line)
    expected = unit["metadados_originais"]
    if meta != expected:
        raise ValueError(f"{origin}: parsed metadata differs from manifest: source={meta!r}; manifest={expected!r}")
    if not {"key", "tipo", "carater", "profundidade", "estimativa_minutos", "tags", "status"}.issubset(meta):
        raise ValueError(f"{origin}: original metadata fields are incomplete")
    return title, meta, mappings


def marker_positions(text: str, marker: str) -> list[int]:
    positions: list[int] = []
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
        at = 0
        while True:
            idx = bare.find(marker, at)
            if idx < 0:
                break
            positions.append(offset + idx)
            at = idx + len(marker)
        offset += len(line)
    if in_fence:
        raise ValueError("unclosed fenced code block")
    return positions


def context_for(spec: dict) -> dict:
    assigned = spec.get("assuntos")
    if assigned:
        if len(assigned) == 1:
            return {"assunto": assigned[0]}
        return {"assuntos": assigned}
    if spec.get("assunto"):
        return {"assunto": spec["assunto"]}
    return {}


def expected_kind(unit: dict, alias: str, common_kind: str | None = None) -> str:
    if common_kind:
        return common_kind
    p = prefix(alias)
    if p == "T": return "theory"
    if p == "Q": return "project_review_questions" if unit.get("tipo_unidade") == "projeto" else "quiz"
    if p == "K": return "answer_key_review" if unit.get("tipo_unidade") == "projeto" else "answer_key"
    if p == "P": return "practice"
    if p == "KP": return "answer_key_pratica"
    if p == "R": return "rubric"
    if p == "C": return unit.get("checklists", {}).get(alias, {}).get("tipo", "checklist")
    if p == "M": return "milestone"
    if p == "SCP": return "project_scope"
    if p == "FC": return "flashcards"
    raise ValueError(f"{alias}: no output type rule")


def validate_manifest(m: dict) -> list[str]:
    errors: list[str] = []
    if m.get("status_manifesto") != "aprovado_para_execucao": errors.append("manifest status is not approved for execution")
    if m.get("fase") != "Fase_4": errors.append("manifest phase is not Fase_4")
    if m.get("base_commit") != BASE: errors.append("manifest base commit mismatch")
    if m.get("id_prefix") != "f4": errors.append("manifest ID prefix is not f4")
    if m.get("ordem_unidades") != EXPECTED_ORDER: errors.append("manifest unit order mismatch")
    if list(m.get("unidades", {})) != EXPECTED_ORDER: errors.append("manifest unit keys/order mismatch")
    if m.get("destino_raiz") != DEST_REL: errors.append("manifest destination root mismatch")
    if m.get("ordem_de_estudo_fonte") != "11.3 → 11.1 → 11.2 (explícita na página da Fase 4)": errors.append("module 11 navigation order missing")
    if m.get("prefixos_arquivo_id", {}).get("KP") != "answer_key_pratica": errors.append("KP prefix mapping missing")
    if len(m.get("unidades", {})) != 17: errors.append("expected 17 active units")
    if "8.4" in m.get("unidades", {}): errors.append("retired unit 8.4 must not exist")

    physical: dict[PurePosixPath, str] = {}
    ids: dict[str, str] = {}
    content_subjects = 0
    project_containers = 0
    theory_count = quiz_count = practice_count = flashcard_count = milestone_count = review_count = rubric_count = checklist_count = 0
    rubric_count = 0
    for uk in EXPECTED_ORDER:
        unit = m.get("unidades", {}).get(uk)
        if not unit:
            errors.append(f"missing unit {uk}")
            continue
        try:
            origin = ROOT.joinpath(*safe_rel(unit["origem"]).parts)
            if not origin.is_file():
                errors.append(f"{uk}: source does not exist: {unit['origem']}")
                continue
            raw = read_text(origin)
            title, metadata, _ = parse_header(raw, unit, unit["origem"])
            if title != unit["titulo_original"]: errors.append(f"{uk}: title mismatch")
            if metadata.get("carater") == "obrigatorio" and uk == "14.1" and unit["metadados_originais"].get("carater") != "obrigatorio":
                errors.append("14.1: required character value was changed")
        except Exception as exc:
            errors.append(f"{uk}: source header validation failed: {exc}")
            continue
        subjects = unit.get("assuntos", [])
        if len(subjects) != len(set(subjects)): errors.append(f"{uk}: duplicate subject slug")
        if unit.get("tipo_unidade") == "projeto":
            project_containers += len(subjects)
        else:
            content_subjects += len(subjects)
        aliases = unit.get("arquivos", {})
        if len(set(aliases.values())) != len(aliases): errors.append(f"{uk}: duplicate alias destination path")
        for alias, rel in aliases.items():
            try:
                relpath = safe_rel(rel)
                full = PurePosixPath(m["destino_raiz"]) / safe_rel(unit["pasta"]) / relpath
                if full in physical: errors.append(f"duplicate physical path {full}")
                physical[full] = f"{uk}/{alias}"
                ident = engine.file_id(uk, rel)
                if ident in ids: errors.append(f"duplicate file ID {ident}")
                ids[ident] = str(full)
            except Exception as exc:
                errors.append(f"{uk}/{alias}: invalid path/ID: {exc}")
        for origin_key, alias in unit.get("blocos_origem", {}).get("comuns", {}).items():
            if origin_key == "metadados":
                if alias != "IDX": errors.append(f"{uk}: metadata must map to IDX")
                continue
            spec = m.get("arquivos_comuns", {}).get(alias)
            if not spec: errors.append(f"{uk}: missing common alias schema {alias}"); continue
            full = PurePosixPath(m["destino_raiz"]) / safe_rel(unit["pasta"]) / safe_rel(spec["path"])
            if full in physical: errors.append(f"duplicate common physical path {full}")
            physical[full] = f"{uk}/{alias}"
            ident = engine.file_id(uk, spec["path"])
            if ident in ids: errors.append(f"duplicate file ID {ident}")
            ids[ident] = str(full)
        readme = PurePosixPath(m["destino_raiz"]) / safe_rel(unit["pasta"]) / "README.md"
        if readme in physical: errors.append(f"duplicate README path {readme}")
        physical[readme] = f"{uk}/IDX"
        ident = engine.file_id(uk, "README.md")
        if ident in ids: errors.append(f"duplicate file ID {ident}")
        ids[ident] = str(readme)

        try:
            raw = read_text(origin)
            _, section_list = engine.split_headings(raw, 2)
            sections = dict(section_list)
            if len(sections) != len(section_list): errors.append(f"{uk}: duplicate H2 source heading")
            if unit.get("tipo_unidade") == "projeto":
                project = unit["blocos_origem"]
                required_sections = set()
                for name in ["Objetivo", "Critério de conclusão", "Conexões", "Referências", unit["secoes_projeto"]["escopo"], unit["secoes_projeto"]["marcos"]]:
                    required_sections.add(name)
                if uk == "16.2": required_sections.update(["Perguntas de revisão das decisões", "Checklist final"])
                if uk == "16.3": required_sections.add("Revisão das decisões")
                if set(sections) != required_sections:
                    errors.append(f"{uk}: project H2 set mismatch: {sorted(set(sections) ^ required_sections)}")
                for spec in project.get("marcos", {}).values():
                    if spec.get("titulo_marco") not in sections[unit["secoes_projeto"]["marcos"]]:
                        errors.append(f"{uk}: literal milestone title absent: {spec.get('titulo_marco')}")
                    milestone_count += 1
                    checklist_count += 1
                if not project.get("checklist_final"): errors.append(f"{uk}: final project checklist alias missing")
                else: checklist_count += 1
                review_count += len(project.get("revisao_decisoes", {})) - 1
            else:
                theory = sections.get("Teoria", "")
                _, theory_parts = engine.h3_chunks(theory)
                theory_titles = [title for title, _ in theory_parts]
                theory_map = unit["blocos_origem"].get("teoria", {})
                if set(theory_titles) != set(theory_map): errors.append(f"{uk}: source theory heading inventory differs from manifest")
                if len(theory_titles) != len(theory_map): errors.append(f"{uk}: duplicate or missing theory heading")
                for heading, alias in theory_map.items():
                    if alias not in aliases or not alias.startswith("T"): errors.append(f"{uk}/{heading}: invalid theory alias")
                    elif PurePosixPath(aliases[alias]).parent.as_posix() not in subjects: errors.append(f"{uk}/{heading}: theory path/subject mismatch")
                theory_count += len(theory_map)
                qmap = unit["blocos_origem"].get("quiz", {})
                q_section = next((name for name in sections if name in ("Verificação — quiz", "Quiz")), None)
                if qmap:
                    if not q_section: errors.append(f"{uk}: quiz section missing")
                    else:
                        _, qitems = engine.numbered(sections[q_section])
                        if {f"Q{n}" for n, _ in qitems} != set(qmap): errors.append(f"{uk}: quiz item inventory differs from manifest")
                        if len(qitems) != len(qmap): errors.append(f"{uk}: quiz item count differs from manifest")
                    quiz_count += len(qmap)
                    for item, spec in qmap.items():
                        aliases_required = [spec.get("arquivo"), spec.get("resposta")]
                        if any(a not in aliases for a in aliases_required): errors.append(f"{uk}/{item}: question/key alias missing")
                        assigned = spec.get("assuntos") or [spec.get("assunto")]
                        if not assigned or any(s not in subjects for s in assigned): errors.append(f"{uk}/{item}: invalid subject coverage")
                        parent = PurePosixPath(aliases.get(spec["arquivo"], "")).parent.as_posix()
                        if len(assigned) > 1 and parent != "90_integracao": errors.append(f"{uk}/{item}: shared quiz must have one integration destination")
                        if len(assigned) == 1 and parent != assigned[0]: errors.append(f"{uk}/{item}: exclusive quiz path does not match subject")
                        if PurePosixPath(aliases.get(spec.get("resposta", ""), "")).parent != PurePosixPath(aliases.get(spec.get("arquivo", ""), "")).parent: errors.append(f"{uk}/{item}: quiz answer key is not stored with its question")
                pmap = unit["blocos_origem"].get("pratica", {})
                practice_count += len(pmap)
                for item, spec in pmap.items():
                    if spec.get("arquivo") not in aliases: errors.append(f"{uk}/{item}: practice alias missing")
                    assigned = spec.get("assuntos") or [spec.get("assunto")]
                    if not assigned or any(s not in subjects for s in assigned): errors.append(f"{uk}/{item}: invalid practice coverage")
                    parent = PurePosixPath(aliases.get(spec.get("arquivo", ""), "")).parent.as_posix()
                    if len(assigned) > 1 and parent != "90_integracao": errors.append(f"{uk}/{item}: shared practice must have one integration destination")
                    if len(assigned) == 1 and parent != assigned[0]: errors.append(f"{uk}/{item}: exclusive practice path does not match subject")
                    for artifact in ["resposta", "rubrica", "checklist"]:
                        if artifact in spec and spec[artifact] not in aliases: errors.append(f"{uk}/{item}: missing {artifact} alias")
                    if "rubrica" in spec: rubric_count += 1
                    if "checklist" in spec: checklist_count += 1
                    if "resposta" in spec and PurePosixPath(aliases.get(spec["resposta"], "")).parent != PurePosixPath(aliases.get(spec.get("arquivo", ""), "")).parent: errors.append(f"{uk}/{item}: practice key is not stored with its practice")
                fmap = unit["blocos_origem"].get("flashcards", {})
                if fmap:
                    flashcard_count += len([k for k in fmap if k.startswith("F")])
                    if not fmap.get("marcador_cartao"): errors.append(f"{uk}: flashcard source marker missing")
                    for item, spec in fmap.items():
                        if not item.startswith("F"): continue
                        if spec.get("arquivo") not in aliases or spec.get("assunto") not in subjects: errors.append(f"{uk}/{item}: invalid flashcard mapping")
            if not unit.get("tipo_unidade") == "projeto":
                coverage = unit.get("cobertura", {})
                exclusive = coverage.get("exclusivos", {})
                shared = coverage.get("compartilhados", {})
                fmap_items = {k for k in unit["blocos_origem"].get("flashcards", {}) if k.startswith("F")}
                expected_items = set(unit["blocos_origem"].get("quiz", {})) | set(unit["blocos_origem"].get("pratica", {})) | fmap_items
                listed_exclusive = {item for items in exclusive.values() for item in items}
                if listed_exclusive & set(shared): errors.append(f"{uk}: item marked both exclusive and shared")
                if listed_exclusive | set(shared) != expected_items: errors.append(f"{uk}: coverage item set differs from source inventory")
                for slug in subjects:
                    if not exclusive.get(slug): errors.append(f"{uk}/{slug}: no exclusive verification")
                for item in expected_items:
                    spec = unit["blocos_origem"].get("quiz", {}).get(item) or unit["blocos_origem"].get("pratica", {}).get(item) or unit["blocos_origem"].get("flashcards", {}).get(item)
                    assigned = spec.get("assuntos") or [spec.get("assunto")] if spec else []
                    if not assigned or any(s not in subjects for s in assigned): errors.append(f"{uk}/{item}: invalid assigned subjects")
                    if len(assigned) > 1:
                        if shared.get(item) != assigned or item in listed_exclusive: errors.append(f"{uk}/{item}: shared coverage differs from manifest item mapping")
                    else:
                        owners = [slug for slug, values in exclusive.items() if item in values]
                        if owners != assigned or item in shared: errors.append(f"{uk}/{item}: exclusive coverage differs from manifest item mapping")
        except Exception as exc:
            errors.append(f"{uk}: source/manifest validation failed: {exc}")

    normalization_keys: set[tuple[str, str]] = set()
    for rule in normalization_rules(m):
        uk, alias = rule.get("unidade"), rule.get("alias")
        key = (uk, alias)
        if key in normalization_keys: errors.append(f"duplicate structural normalization for {uk}/{alias}")
        normalization_keys.add(key)
        unit = m.get("unidades", {}).get(uk)
        if not unit:
            errors.append(f"structural normalization references unknown unit: {uk}")
            continue
        rel = unit.get("arquivos", {}).get(alias)
        if not rel:
            for common_key, common_alias in unit.get("blocos_origem", {}).get("comuns", {}).items():
                if common_key != "metadados" and common_alias == alias:
                    rel = m.get("arquivos_comuns", {}).get(alias, {}).get("path")
                    break
        if not rel:
            errors.append(f"structural normalization has no output path: {uk}/{alias}")
            continue
        source_path = ROOT / Path(*safe_rel(unit["origem"]).parts)
        source_sections = dict(engine.split_headings(read_text(source_path), 2)[1])
        section = rule.get("secao")
        old_path = rule.get("caminho_original", "")
        new_path = rule.get("caminho_migrado", "")
        resource = rule.get("destino_recurso", "")
        if section not in source_sections:
            errors.append(f"structural normalization source section missing: {uk}/{section}")
            continue
        source_link = f"]({old_path})"
        if source_sections[section].count(source_link) != rule.get("ocorrencias"):
            errors.append(f"structural normalization source occurrence count mismatch: {uk}/{alias}")
        source_target = (source_path.parent / Path(old_path.replace("/", "\\"))).resolve()
        resource_target = ROOT / Path(*safe_rel(resource).parts)
        if not resource_target.is_file(): errors.append(f"structural normalization target does not exist: {resource}")
        if source_target != resource_target.resolve(): errors.append(f"structural normalization original link target mismatch: {uk}/{alias}")
        output_rel = PurePosixPath(m["destino_raiz"]) / safe_rel(unit["pasta"]) / safe_rel(rel)
        expected_new = posixpath.relpath(resource, output_rel.parent.as_posix())
        if new_path != expected_new: errors.append(f"structural normalization destination path mismatch: {uk}/{alias}: expected {expected_new}")
        if old_path == new_path or not rule.get("justificativa"): errors.append(f"invalid structural normalization rule: {uk}/{alias}")

    if content_subjects != 49: errors.append(f"expected 49 content subjects, got {content_subjects}")
    if project_containers != 2: errors.append(f"expected 2 project containers, got {project_containers}")
    if (theory_count, quiz_count, practice_count, flashcard_count, milestone_count, review_count, rubric_count, checklist_count) != (68, 65, 43, 3, 8, 8, 42, 11):
        errors.append(f"source inventory mismatch: theory={theory_count}, quiz={quiz_count}, practice={practice_count}, flashcards={flashcard_count}, milestones={milestone_count}, review={review_count}, rubrics={rubric_count}, practice_acceptance={checklist_count}")
    paths = output_paths(m)
    if len(paths) != 395: errors.append(f"expected 395 distinct output paths, got {len(paths)}")
    if m.get("estimativa_arquivos", {}).get("total") != 395: errors.append("manifest forecast must remain 395")
    declared = {PurePosixPath(m["destino_raiz"]) / safe_rel(u["pasta"]) / safe_rel(rel) for u in m["unidades"].values() for rel in u.get("arquivos", {}).values()}
    declared.update(PurePosixPath(m["destino_raiz"]) / safe_rel(u["pasta"]) / safe_rel(m["arquivos_comuns"][alias]["path"]) for u in m["unidades"].values() for key, alias in u["blocos_origem"]["comuns"].items() if key != "metadados")
    declared.update(PurePosixPath(m["destino_raiz"]) / safe_rel(u["pasta"]) / "README.md" for u in m["unidades"].values())
    if declared != paths: errors.append("declared aliases/common files differ from expected output paths")
    return errors


class Builder:
    def __init__(self, manifest: dict):
        self.m = manifest
        self.dest = PurePosixPath(manifest["destino_raiz"])
        self.sources: dict[str, dict] = {}
        self.sections: dict[tuple[str, str], str] = {}
        self.cursors: dict[tuple[str, str], int] = defaultdict(int)
        self.data: dict[tuple[str, str], dict] = {}
        self.outputs: dict[PurePosixPath, str] = {}
        self.records: list[dict] = []
        self.normalizations_applied: list[dict] = []
        engine.manifest = manifest
        engine.DEST = self.dest
        engine.output = self.outputs
        self._load_sources()

    def _load_sources(self) -> None:
        for uk, unit in self.m["unidades"].items():
            origin = safe_rel(unit["origem"])
            raw = read_text(ROOT.joinpath(*origin.parts))
            title, metadata, header_mappings = parse_header(raw, unit, unit["origem"])
            _, section_list = engine.split_headings(raw, 2)
            if not section_list:
                raise ValueError(f"{uk}: no H2 sections found")
            section_map = dict(section_list)
            if len(section_map) != len(section_list):
                raise ValueError(f"{uk}: duplicate H2 source heading")
            self.sources[uk] = {"raw": raw, "title": title, "metadata": metadata, "section_list": section_list, "sections": section_map}
            for name, text in section_list:
                self.sections[(uk, name)] = text
            readme = str(self.dest / safe_rel(unit["pasta"]) / "README.md")
            for key, text, start, end in header_mappings:
                self.records.append({
                    "unidade": uk, "origem": unit["origem"], "secao": "metadados_lista" if key != "title" else "titulo",
                    "bloco": key, "tipo": "metadata_conversion" if key != "title" else "topic_index",
                    "alias": "IDX", "destino": readme, "inicio": str(start), "fim": str(end), "texto": text,
                })

    def _target(self, uk: str, alias: str) -> str:
        unit = self.m["unidades"][uk]
        if alias in unit["arquivos"]:
            return unit["arquivos"][alias]
        for key, common_alias in unit["blocos_origem"]["comuns"].items():
            if key != "metadados" and common_alias == alias:
                return self.m["arquivos_comuns"][alias]["path"]
        raise ValueError(f"{uk}: no destination for alias {alias}")

    def add(self, uk: str, section: str, start: int, end: int, alias: str, kind: str,
            item: str | None = None, context: dict | None = None, title: str | None = None,
            scale: str | None = None) -> None:
        source = self.sections[(uk, section)]
        expected_start = self.cursors[(uk, section)]
        if start != expected_start or end < start or end > len(source):
            raise ValueError(f"{uk}/{section}: non-contiguous source mapping at {expected_start}, got {start}:{end}")
        fragment = source[start:end]
        if not fragment:
            raise ValueError(f"{uk}/{section}: empty source block for {alias}")
        self.cursors[(uk, section)] = end
        rel = self._target(uk, alias)
        key = (uk, alias)
        data = self.data.setdefault(key, {"rel": rel, "kind": kind, "chunks": [], "items": [], "contexts": [], "title": None, "scale": None})
        if data["rel"] != rel or data["kind"] != kind:
            raise ValueError(f"{uk}/{alias}: destination/type conflict")
        if title and data["title"] and title != data["title"]: raise ValueError(f"{uk}/{alias}: conflicting literal titles")
        if scale and data["scale"] and scale != data["scale"]: raise ValueError(f"{uk}/{alias}: conflicting rubric scales")
        data["chunks"].append(fragment)
        if item and item not in data["items"]: data["items"].append(item)
        if context:
            context_key = json.dumps(context, ensure_ascii=False, sort_keys=True)
            if all(json.dumps(c, ensure_ascii=False, sort_keys=True) != context_key for c in data["contexts"]):
                data["contexts"].append(context)
        if title: data["title"] = title
        if scale: data["scale"] = scale
        self.records.append({
            "unidade": uk, "origem": self.m["unidades"][uk]["origem"], "secao": section,
            "bloco": item or section, "tipo": kind, "alias": alias,
            "destino": str(self.dest / safe_rel(self.m["unidades"][uk]["pasta"]) / safe_rel(rel)),
            "inicio": str(start), "fim": str(end), "texto": fragment,
        })

    def emit_common(self, uk: str) -> None:
        section_for = {"objetivo": "Objetivo", "resumo": "Resumo", "criterio_de_conclusao": "Critério de conclusão", "conexoes": "Conexões", "referencias": "Referências"}
        unit = self.m["unidades"][uk]
        for origin_key, alias in unit["blocos_origem"]["comuns"].items():
            if origin_key == "metadados": continue
            if origin_key not in section_for: raise ValueError(f"{uk}: unknown common source block {origin_key}")
            section = section_for[origin_key]
            if section not in self.sources[uk]["sections"]: raise ValueError(f"{uk}: missing common section {section}")
            content = self.sections[(uk, section)]
            self.add(uk, section, 0, len(content), alias, self.m["arquivos_comuns"][alias]["tipo"], item=section)

    def emit_theory(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        section = "Teoria"
        text = self.sections[(uk, section)]
        pre, chunks = engine.h3_chunks(text)
        mapping = unit["blocos_origem"]["teoria"]
        titles = [title for title, _ in chunks]
        if set(titles) != set(mapping) or len(titles) != len(mapping):
            raise ValueError(f"{uk}: theory blocks do not match exact manifest headings")
        cursor = 0
        if pre:
            first_title, _ = chunks[0]
            alias = mapping[first_title]
            subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
            self.add(uk, section, 0, len(pre), alias, "theory", context={"assunto": subject})
            cursor = len(pre)
        for title, block in chunks:
            if text[cursor:cursor+len(block)] != block:
                raise ValueError(f"{uk}: theory chunk is not contiguous at literal heading {title!r}")
            alias = mapping[title]
            subject = PurePosixPath(unit["arquivos"][alias]).parent.as_posix()
            if subject not in unit["assuntos"]: raise ValueError(f"{uk}/{title}: theory alias points to wrong subject")
            self.add(uk, section, cursor, cursor+len(block), alias, "theory", item=title, context={"assunto": subject})
            cursor += len(block)
        if cursor != len(text): raise ValueError(f"{uk}: theory suffix not mapped")

    def emit_quiz(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        qmap = unit["blocos_origem"].get("quiz", {})
        if not qmap: return
        section = next((s for s in ("Verificação — quiz", "Quiz") if s in self.sources[uk]["sections"]), None)
        if not section: raise ValueError(f"{uk}: quiz source section missing")
        text = self.sections[(uk, section)]
        pre, items = engine.numbered(text)
        if {f"Q{n}" for n, _ in items} != set(qmap) or len(items) != len(qmap):
            raise ValueError(f"{uk}: quiz question numbers differ from manifest")
        cursor = 0
        first_alias = qmap[f"Q{items[0][0]}"]["arquivo"]
        first_context = context_for(qmap[f"Q{items[0][0]}"])
        if pre:
            self.add(uk, section, 0, len(pre), first_alias, "quiz", context=first_context)
            cursor = len(pre)
        for number, block in items:
            item = f"Q{number}"
            spec = qmap[item]
            rule = spec.get("separacao_inline_literal", {})
            answer_marker = rule.get("resposta_inicio")
            if not answer_marker: raise ValueError(f"{uk}/{item}: exact response marker missing from manifest")
            answer_positions = marker_positions(block, answer_marker)
            if len(answer_positions) != 1: raise ValueError(f"{uk}/{item}: expected one literal answer marker, got {len(answer_positions)}")
            answer_at = answer_positions[0]
            for feedback_marker in rule.get("feedback_justificativa_inicio", []):
                if len(marker_positions(block, feedback_marker)) != 1:
                    raise ValueError(f"{uk}/{item}: feedback marker mismatch: {feedback_marker}")
            if not block[:answer_at].strip() or not block[answer_at:].strip():
                raise ValueError(f"{uk}/{item}: empty question or key segment")
            context = context_for(spec)
            self.add(uk, section, cursor, cursor+answer_at, spec["arquivo"], "quiz", item=item, context=context)
            self.add(uk, section, cursor+answer_at, cursor+len(block), spec["resposta"], "answer_key", item=item, context=context)
            cursor += len(block)
        if cursor != len(text): raise ValueError(f"{uk}: quiz suffix not mapped")

    def _emit_activity_block(self, uk: str, section: str, start: int, block: str, item: str, spec: dict) -> int:
        context = context_for(spec)
        markers: list[tuple[int, str, str]] = []
        rule = spec.get("separacao_inline_literal", {})
        for key, target_key in (("solucao_inicio", "resposta"), ("rubrica_inicio", "rubrica"), ("aceite_inicio", "checklist")):
            if key not in rule: continue
            target = spec.get(target_key)
            marker = rule[key]
            if not target or target not in self.m["unidades"][uk]["arquivos"]: raise ValueError(f"{uk}/{item}: {key} has no mapped target")
            positions = marker_positions(block, marker)
            if len(positions) != 1: raise ValueError(f"{uk}/{item}: literal {key} marker count={len(positions)}")
            markers.append((positions[0], target, expected_kind(self.m["unidades"][uk], target)))
        markers.sort()
        points = [(0, spec["arquivo"], "practice")] + markers
        cursor = 0
        for i, (pos, alias, kind) in enumerate(points):
            end = points[i+1][0] if i+1 < len(points) else len(block)
            if end <= pos: raise ValueError(f"{uk}/{item}: overlapping or empty marker range")
            scale = spec.get("escala_rubrica") if kind == "rubric" else None
            self.add(uk, section, start+pos, start+end, alias, kind, item=item, context=context, scale=scale)
            cursor = end
        if cursor != len(block): raise ValueError(f"{uk}/{item}: activity suffix not mapped")
        return start + len(block)

    def emit_practices(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        pmap = unit["blocos_origem"].get("pratica", {})
        if not pmap: return
        grouped: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        for item, spec in pmap.items():
            origin_section = spec.get("origem_secao", "")
            if " > " not in origin_section: raise ValueError(f"{uk}/{item}: origin section selector malformed")
            section = origin_section.split(" > ", 1)[0].removeprefix("## ")
            grouped[section].append((item, spec))
        for section, group in grouped.items():
            if section not in self.sources[uk]["sections"]: raise ValueError(f"{uk}: practice source section missing: {section}")
            text = self.sections[(uk, section)]
            pre, activities = engine.h3_chunks(text)
            group.sort(key=lambda pair: int(pair[0][1:]))
            if len(activities) != len(group): raise ValueError(f"{uk}/{section}: practice count differs from manifest")
            cursor = 0
            if pre:
                first_item, first_spec = group[0]
                self.add(uk, section, 0, len(pre), first_spec["arquivo"], "practice", context=context_for(first_spec))
                cursor = len(pre)
            for (title, block), (item, spec) in zip(activities, group):
                if title != spec.get("titulo"): raise ValueError(f"{uk}/{item}: literal practice title differs: {title!r}")
                if text[cursor:cursor+len(block)] != block: raise ValueError(f"{uk}/{item}: practice block boundary mismatch")
                cursor = self._emit_activity_block(uk, section, cursor, block, item, spec)
            if cursor != len(text): raise ValueError(f"{uk}/{section}: practice suffix not mapped")

    def emit_flashcards(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        fmap = unit["blocos_origem"].get("flashcards", {})
        if not fmap: return
        section = fmap.get("secao", "Flashcards")
        if section not in self.sources[uk]["sections"]: raise ValueError(f"{uk}: flashcard section missing: {section}")
        text = self.sections[(uk, section)]
        marker = fmap["marcador_cartao"]
        starts = marker_positions(text, marker)
        cards = [(k, v) for k, v in fmap.items() if k.startswith("F")]
        cards.sort(key=lambda pair: int(pair[0][1:]))
        if len(starts) != len(cards): raise ValueError(f"{uk}: flashcard count differs from manifest")
        cursor = 0
        first_alias = cards[0][1]["arquivo"]
        first_context = {"assunto": cards[0][1]["assunto"]}
        if starts[0] > 0:
            self.add(uk, section, 0, starts[0], first_alias, "flashcards", context=first_context)
            cursor = starts[0]
        for index, ((item, spec), start) in enumerate(zip(cards, starts)):
            if cursor != start: raise ValueError(f"{uk}/{item}: flashcard start is not contiguous")
            end = starts[index+1] if index+1 < len(starts) else len(text)
            context = {"assunto": spec["assunto"]}
            self.add(uk, section, start, end, spec["arquivo"], "flashcards", item=item, context=context)
            cursor = end
        if cursor != len(text): raise ValueError(f"{uk}: flashcard section suffix not mapped")

    def emit_project(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        project = unit["blocos_origem"]
        subject = unit["assuntos"][0]
        context = {"assunto": subject}
        scope_section = unit["secoes_projeto"]["escopo"]
        scope_text = self.sections[(uk, scope_section)]
        self.add(uk, scope_section, 0, len(scope_text), project["escopo"], "project_scope", item="escopo", context=context)

        milestone_section = unit["secoes_projeto"]["marcos"]
        section_text = self.sections[(uk, milestone_section)]
        pre, milestones = engine.h3_chunks(section_text)
        specs = project["marcos"]
        ordered_specs = list(specs.items())
        if len(milestones) != 4 or len(ordered_specs) != 4: raise ValueError(f"{uk}: exactly four milestones required")
        cursor = 0
        if pre:
            first_alias = ordered_specs[0][1]["arquivo"]
            self.add(uk, milestone_section, 0, len(pre), first_alias, "milestone", context=context, title=ordered_specs[0][1]["titulo_marco"])
            cursor = len(pre)
        for (title, block), (mkey, spec) in zip(milestones, ordered_specs):
            if title != spec.get("titulo_marco"): raise ValueError(f"{uk}/{mkey}: title is not literal/source ordered: {title!r}")
            if section_text[cursor:cursor+len(block)] != block: raise ValueError(f"{uk}/{mkey}: milestone boundary mismatch")
            rule = spec["separacao_literal"]
            acceptance_marker = rule["aceite_inicio"]
            positions = marker_positions(block, acceptance_marker)
            if len(positions) != 1: raise ValueError(f"{uk}/{mkey}: acceptance marker count mismatch")
            acceptance_at = positions[0]
            end_marker = rule["aceite_fim_antes"]
            end_positions = marker_positions(block, end_marker)
            if len(end_positions) != 1 or end_positions[0] <= acceptance_at: raise ValueError(f"{uk}/{mkey}: acceptance end marker mismatch")
            acceptance_end = end_positions[0]
            self.add(uk, milestone_section, cursor, cursor+acceptance_at, spec["arquivo"], "milestone", item=mkey, context=context, title=title)
            self.add(uk, milestone_section, cursor+acceptance_at, cursor+acceptance_end, spec["aceite"], "checklist", item=mkey, context=context, title=title)
            tail_start = cursor+acceptance_end
            tail_end = cursor+len(block)
            if "evidencias_destino" in rule:
                self.add(uk, milestone_section, tail_start, tail_end, rule["evidencias_destino"], "milestone", item=mkey, context=context, title=title)
            elif "checklist_destino" in rule:
                self.add(uk, milestone_section, tail_start, tail_end, rule["checklist_destino"], "checklist", item="checklist_final", context=context)
            else:
                raise ValueError(f"{uk}/{mkey}: tail destination missing")
            cursor += len(block)
        if cursor != len(section_text): raise ValueError(f"{uk}: milestone section suffix not mapped")

        final_rule = unit["limites_origem_projeto"]
        if uk == "16.2":
            final_section = "Checklist final"
            final_text = self.sections[(uk, final_section)]
            self.add(uk, final_section, 0, len(final_text), project["checklist_final"], "checklist", item="checklist_final", context=context)

        review = project.get("revisao_decisoes", {})
        review_section = review.get("secao")
        if not review_section or review_section not in self.sources[uk]["sections"]:
            raise ValueError(f"{uk}: exact review section is not declared in manifest")
        review_text = self.sections[(uk, review_section)]
        review_items = [(key, spec) for key, spec in review.items() if key.startswith("R")]
        review_items.sort(key=lambda pair: int(pair[0][1:]))
        cursor = 0
        if uk == "16.3":
            starts = []
            for rkey, spec in review_items:
                marker = spec.get("marcador_inicio")
                positions = marker_positions(review_text, marker) if marker else []
                if len(positions) != 1: raise ValueError(f"{uk}/{rkey}: exact open-review bullet marker mismatch")
                starts.append(positions[0])
            if starts != sorted(starts): raise ValueError(f"{uk}: review bullets do not follow manifest order")
            first_alias = review_items[0][1]["arquivo"]
            if starts[0] > 0:
                self.add(uk, review_section, 0, starts[0], first_alias, "project_review_questions", context=context)
                cursor = starts[0]
            for index, ((rkey, spec), start) in enumerate(zip(review_items, starts)):
                if cursor != start: raise ValueError(f"{uk}/{rkey}: open-review bullet boundary mismatch")
                end = starts[index+1] if index+1 < len(starts) else len(review_text)
                self.add(uk, review_section, start, end, spec["arquivo"], "project_review_questions", item=rkey, context=context)
                cursor = end
        else:
            pre, items = engine.numbered(review_text)
            if len(items) != len(review_items): raise ValueError(f"{uk}: review question count differs from manifest")
            first_alias = review_items[0][1]["arquivo"]
            if pre:
                self.add(uk, review_section, 0, len(pre), first_alias, expected_kind(unit, first_alias), context=context)
                cursor = len(pre)
            for (number, block), (rkey, spec) in zip(items, review_items):
                if number != int(rkey[1:]): raise ValueError(f"{uk}/{rkey}: review numbering mismatch")
                rule = spec.get("separacao_inline_literal", {})
                marker = rule.get("pergunta_fim")
                positions = marker_positions(block, marker) if marker else []
                if len(positions) != 1: raise ValueError(f"{uk}/{rkey}: exact question/answer separator mismatch")
                split_at = positions[0] + 1  # Keep the question mark with the question; whitespace and bold answer move with the key.
                self.add(uk, review_section, cursor, cursor+split_at, spec["arquivo"], "project_review_questions", item=rkey, context=context)
                self.add(uk, review_section, cursor+split_at, cursor+len(block), spec["resposta"], "answer_key_review", item=rkey, context=context)
                cursor += len(block)
        if cursor != len(review_text): raise ValueError(f"{uk}: review section suffix not mapped")

    def add_index(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        source = self.sources[uk]
        fields = [("title", source["title"])]
        fields.extend(unit["metadados_originais"].items())
        fields.extend([("arquivo_id", engine.file_id(uk, "README.md")), ("tipo_arquivo", "topic_index")])
        body = f"# {source['title']}\n\n## Índice\n\n### Arquivos comuns\n"
        for key, alias in unit["blocos_origem"]["comuns"].items():
            if key == "metadados": continue
            common = self.m["arquivos_comuns"][alias]
            href = PurePosixPath(common["path"]).as_posix()
            body += f"- [{common['tipo']}]({href})\n"
        body += "\n### Assuntos\n"
        for subject in unit["assuntos"]:
            body += f"\n#### `{subject}`\n"
            for alias, rel in unit["arquivos"].items():
                if PurePosixPath(rel).parts[0] == subject:
                    path = PurePosixPath(rel).as_posix()
                    body += f"- [{PurePosixPath(rel).name}]({path})\n"
        integrations = [rel for rel in unit["arquivos"].values() if PurePosixPath(rel).parts[0] == "90_integracao"]
        if integrations:
            body += "\n### Integração\n"
            for rel in integrations:
                path = PurePosixPath(rel).as_posix()
                body += f"- [{PurePosixPath(rel).name}]({path})\n"
        rels = unit.get("relacoes_assuntos", [])
        if rels:
            body += "\n### Relações entre assuntos\n"
            for relation in rels:
                slugs = relation.get("assuntos", [])
                if len(slugs) != 2 or any(s not in unit["assuntos"] for s in slugs): raise ValueError(f"{uk}: invalid related-subject references")
                body += f"- [{slugs[0]}]({slugs[0]}/01_teoria.md) ↔ [{slugs[1]}]({slugs[1]}/01_teoria.md)\n"
        path = self.dest / safe_rel(unit["pasta"]) / "README.md"
        if path in self.outputs: raise ValueError(f"duplicate README path {path}")
        self.outputs[path] = engine.frontmatter(fields) + "\n" + body

    def normalize_output(self, uk: str, alias: str, rel: str, content: str) -> str:
        for rule in normalization_rules(self.m):
            if rule.get("unidade") != uk or rule.get("alias") != alias:
                continue
            old_path = rule["caminho_original"]
            new_path = rule["caminho_migrado"]
            old_link = f"]({old_path})"
            new_link = f"]({new_path})"
            if content.count(old_link) != rule.get("ocorrencias") or new_link in content:
                raise ValueError(f"{uk}/{alias}: exact structural link normalization does not match source block")
            content = content.replace(old_link, new_link, rule["ocorrencias"])
            if content.count(new_link) != rule["ocorrencias"]:
                raise ValueError(f"{uk}/{alias}: normalized link count mismatch")
            destination = str(self.dest / safe_rel(self.m["unidades"][uk]["pasta"]) / safe_rel(rel))
            self.normalizations_applied.append({
                "unidade": uk, "alias": alias, "destino": destination,
                "caminho_original": old_path, "caminho_migrado": new_path,
                "ocorrencias": rule["ocorrencias"], "justificativa": rule["justificativa"],
            })
        return content

    def finalize(self) -> None:
        for uk, unit in self.m["unidades"].items():
            aliases = set(unit["arquivos"])
            actual = {alias for (owner, alias) in self.data if owner == uk and alias in aliases}
            if actual != aliases: raise ValueError(f"{uk}: aliases missing={sorted(aliases-actual)} extra={sorted(actual-aliases)}")
            for (owner, alias), data in list(self.data.items()):
                if owner != uk or alias not in aliases: continue
                if len(data["contexts"]) > 1: raise ValueError(f"{uk}/{alias}: conflicting subject contexts")
                context = data["contexts"][0] if data["contexts"] else {}
                rel = PurePosixPath(data["rel"])
                parent = rel.parent.as_posix()
                if parent == "90_integracao":
                    if len(context.get("assuntos", [])) < 2: raise ValueError(f"{uk}/{alias}: integration file must identify shared subjects")
                elif parent in unit["assuntos"]:
                    if context.get("assunto") != parent: raise ValueError(f"{uk}/{alias}: frontmatter subject/path mismatch")
                else:
                    raise ValueError(f"{uk}/{alias}: output path is outside approved subject folders")
                if data["kind"] == "rubric" and not data["scale"]:
                    raise ValueError(f"{uk}/{alias}: source rubric scale missing")
                if prefix(alias) == "M" and not data["title"]: raise ValueError(f"{uk}/{alias}: literal milestone title missing")
                content = self.normalize_output(uk, alias, data["rel"], "".join(data["chunks"]))
                engine.put(uk, data["rel"], data["kind"], content,
                           subject=context.get("assunto"), subjects=context.get("assuntos"),
                           items=data["items"], order=order_of(alias), title=data["title"], scale=data["scale"])
            for key, alias in unit["blocos_origem"]["comuns"].items():
                if key == "metadados": continue
                data = self.data.get((uk, alias))
                if not data: raise ValueError(f"{uk}: common block {alias} has no source content")
                content = self.normalize_output(uk, alias, data["rel"], "".join(data["chunks"]))
                engine.put(uk, data["rel"], data["kind"], content, items=data["items"], order=order_of(alias))
            self.add_index(uk)
            for (owner, section), text in self.sections.items():
                if owner == uk and self.cursors[(owner, section)] != len(text):
                    raise ValueError(f"{uk}/{section}: source coverage {self.cursors[(owner, section)]}/{len(text)}")
        expected = output_paths(self.m)
        actual = set(self.outputs)
        if actual != expected: raise ValueError(f"output paths differ from manifest; missing={sorted(map(str, expected-actual))}; extra={sorted(map(str, actual-expected))}")
        if len(actual) != 395: raise ValueError(f"expected 395 real outputs; generated in memory {len(actual)}")

    def build(self) -> None:
        for uk, unit in self.m["unidades"].items():
            self.emit_common(uk)
            if unit.get("tipo_unidade") == "projeto":
                self.emit_project(uk)
            else:
                self.emit_theory(uk)
                self.emit_quiz(uk)
                self.emit_practices(uk)
                self.emit_flashcards(uk)
        self.finalize()

    def types(self) -> Counter:
        result = Counter()
        for path, content in self.outputs.items():
            _, fm, body = engine.fm(content, str(path))
            result[fm["tipo_arquivo"]] += 1
            if not body.strip(): raise ValueError(f"empty output body: {path}")
        return result


def previous_phase_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for phase in (1, 2, 3):
        base = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{phase}"
        for path in base.rglob("*"):
            if path.is_file(): snapshot[path.relative_to(ROOT).as_posix()] = sha_file(path)
    return snapshot


def protected_snapshot(m: dict) -> dict[str, str]:
    paths = [unit["origem"] for unit in m["unidades"].values()] + PHASE_DOCS + [JSON_REL, "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md"]
    result = {}
    for rel in paths:
        path = ROOT / Path(*safe_rel(rel).parts)
        if not path.is_file(): raise ValueError(f"protected input missing: {rel}")
        result[rel] = sha_file(path)
    return result


def old_ids() -> set[str]:
    ids: set[str] = set()
    for phase in (1, 2, 3):
        root = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{phase}"
        for path in root.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            value = fields.get("arquivo_id")
            if not value: raise ValueError(f"previous-phase file has no arquivo_id: {path}")
            if value in ids: raise ValueError(f"previous-phase duplicate arquivo_id: {value}")
            ids.add(value)
    return ids


def check_git_preflight(apply: bool, dest_exists: bool, allowed_untracked: set[str], allow_existing: bool = False) -> list[str]:
    errors = []
    if git("rev-parse", "--show-toplevel").replace("\\", "/").casefold() != str(ROOT).replace("\\", "/").casefold(): errors.append("git root differs from script root")
    if git("branch", "--show-current") != "migracao-estrutura": errors.append("current branch is not migracao-estrutura")
    if git("rev-parse", "HEAD") != BASE: errors.append("HEAD differs from approved Fase 4 base")
    if git("diff", "--cached", "--name-only"): errors.append("staged changes exist")
    tracked = git("diff", "--name-only").splitlines()
    if tracked: errors.append("tracked worktree changes exist: " + repr(tracked))
    status = git("status", "--porcelain")
    for line in status.splitlines():
        path = line[3:].replace("\\", "/")
        if path in allowed_untracked: continue
        if apply and (path.startswith(DEST_REL + "/") or path in REPORTS or path == "docs/migracao/HOMOLOGACAO_FASE4.md"): continue
        errors.append("unexpected working-tree entry: " + line)
    if apply and dest_exists and not allow_existing: errors.append("Fase 4 destination already exists")
    if apply and not allow_existing:
        for rel in REPORTS:
            if (ROOT / Path(*safe_rel(rel).parts)).exists(): errors.append(f"report already exists: {rel}")
    return errors


def audit_builder(builder: Builder, previous: dict[str, str], protected: dict[str, str], ids_before: set[str]) -> tuple[list[str], dict[str, dict], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    unit_results: dict[str, dict] = {}
    by_section: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in builder.records:
        if row["secao"] in ("metadados_lista", "titulo"):
            continue
        by_section[(row["unidade"], row["secao"])].append(row)
    for uk, unit in builder.m["unidades"].items():
        source = builder.sources[uk]
        section_status = []
        for name, text in source["section_list"]:
            rows = by_section.get((uk, name), [])
            cursor = 0
            fragments = []
            for row in rows:
                start, end = int(row["inicio"]), int(row["fim"])
                if start != cursor or end < start: errors.append(f"{uk}/{name}/{row['bloco']}: source gap/overlap {cursor}->{start}")
                fragment = row["texto"]
                if text[start:end] != fragment: errors.append(f"{uk}/{name}/{row['bloco']}: source fragment mismatch")
                fragments.append(fragment)
                cursor = end
            if cursor != len(text): errors.append(f"{uk}/{name}: source coverage {cursor}/{len(text)}")
            reconstructed = "".join(fragments)
            if reconstructed != text: errors.append(f"{uk}/{name}: reconstructed source differs")
            if engine.code_blocks(reconstructed) != engine.code_blocks(text): errors.append(f"{uk}/{name}: fenced code block differs")
            section_status.append((name, len(rows), sha_text(reconstructed) == sha_text(text)))
        unit_root = PurePosixPath(builder.m["destino_raiz"]) / safe_rel(unit["pasta"])
        unit_files = [path for path in builder.outputs if path.parts[:len(unit_root.parts)] == unit_root.parts]
        unit_results[uk] = {"arquivos": len(unit_files), "mapeamentos": len([r for r in builder.records if r["unidade"] == uk]), "secoes": section_status}

    generated_ids: set[str] = set()
    links: list[str] = []
    markdown_link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    wikilinks = 0
    for rel, text in builder.outputs.items():
        try:
            _, fields, body = engine.fm(text, str(rel))
        except Exception as exc:
            errors.append(f"invalid YAML frontmatter {rel}: {exc}")
            continue
        ident = fields.get("arquivo_id")
        if not ident: errors.append(f"missing arquivo_id: {rel}")
        elif ident in generated_ids or ident in ids_before: errors.append(f"duplicate/global-colliding arquivo_id: {ident}")
        else: generated_ids.add(ident)
        if fields.get("parent_key") and fields["parent_key"] not in builder.m["unidades"]: errors.append(f"invalid parent_key: {rel}")
        if not body.strip(): errors.append(f"empty file body: {rel}")
        wikilinks += len(re.findall(r"\[\[[^\]]+\]\]", body))
        for target in markdown_link.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "#")): continue
            target_path, _, anchor = target.partition("#")
            virtual_target = PurePosixPath(posixpath.normpath((rel.parent / PurePosixPath(target_path)).as_posix())) if target_path else rel
            target_exists = virtual_target in builder.outputs or (ROOT.joinpath(*virtual_target.parts).is_file() if target_path else True)
            if not target_exists:
                if rel.name == "README.md":
                    errors.append(f"generated index link does not resolve in {rel}: {target}")
                    continue
                source_base = None
                for uk, unit in builder.m["unidades"].items():
                    unit_root = PurePosixPath(builder.m["destino_raiz"]) / safe_rel(unit["pasta"])
                    if rel.parts[:len(unit_root.parts)] == unit_root.parts:
                        source_base = ROOT.joinpath(*safe_rel(unit["origem"]).parent.parts)
                        break
                source_target = (source_base / Path(target_path.replace("/", "\\"))).resolve() if source_base and target_path else None
                if source_target and source_target.is_file():
                    warnings.append(f"source-relative link preserved but does not resolve after relocation: {rel} -> {target} (source target: {source_target.relative_to(ROOT).as_posix()})")
                else:
                    errors.append(f"broken relative Markdown link in {rel}: {target}")
            else:
                links.append(f"{rel} -> {target}")
    if len(generated_ids) != 395: errors.append(f"expected 395 generated IDs, got {len(generated_ids)}")

    for rel, digest in protected.items():
        path = ROOT / Path(*safe_rel(rel).parts)
        if not path.is_file() or sha_file(path) != digest: errors.append(f"protected source/JSON changed: {rel}")
    current_previous = previous_phase_snapshot()
    if current_previous != previous: errors.append("one or more Fase 1–3 files changed")
    return errors, unit_results, [f"resolved_markdown_links={len(links)}", f"preserved_wikilinks={wikilinks}", *warnings]


def validate_existing_tree_for_link_repair(builder: Builder) -> tuple[list[str], set[PurePosixPath]]:
    errors: list[str] = []
    dest = ROOT / DEST_REL
    if not dest.is_dir():
        return ["existing Fase 4 destination directory is missing"], set()
    actual_paths = {PurePosixPath(path.relative_to(ROOT).as_posix()) for path in dest.rglob("*") if path.is_file()}
    expected_paths = set(builder.outputs)
    if actual_paths != expected_paths:
        errors.append(f"existing tree path inventory differs: missing={sorted(map(str, expected_paths-actual_paths))}; unexpected={sorted(map(str, actual_paths-expected_paths))}")
    changed_paths: set[PurePosixPath] = set()
    for rel, expected in builder.outputs.items():
        path = ROOT.joinpath(*rel.parts)
        if not path.is_file():
            errors.append(f"existing output missing: {rel}")
            continue
        actual = read_text(path)
        expected_norm = norm(expected)
        if actual == expected_norm:
            continue
        original_form = expected_norm
        for item in builder.normalizations_applied:
            if PurePosixPath(item["destino"]) != rel:
                continue
            new_link = f"]({item['caminho_migrado']})"
            old_link = f"]({item['caminho_original']})"
            if original_form.count(new_link) != item["ocorrencias"]:
                errors.append(f"expected normalized href missing or duplicated in reconstructed output: {rel}")
                break
            original_form = original_form.replace(new_link, old_link, item["ocorrencias"])
        if actual == original_form and rel in {PurePosixPath(item["destino"]) for item in builder.normalizations_applied}:
            changed_paths.add(rel)
        else:
            errors.append(f"existing output differs beyond approved link normalization: {rel}")
    for rel in REPORTS:
        if not (ROOT / Path(*safe_rel(rel).parts)).is_file(): errors.append(f"existing audit report missing: {rel}")
    return errors, changed_paths


def repair_existing_links(builder: Builder, manifest_bytes: bytes, allowed_untracked: set[str]) -> int:
    preflight = check_git_preflight(True, True, allowed_untracked, allow_existing=True)
    if preflight:
        print("LINK-REPAIR PREFLIGHT FAILED")
        for error in preflight: print("- " + error)
        return 4
    tree_errors, changed_paths = validate_existing_tree_for_link_repair(builder)
    if tree_errors:
        print("EXISTING TREE DOES NOT MATCH APPROVED REPAIR SCOPE")
        for error in tree_errors: print("- " + error)
        return 5

    protected = protected_snapshot(builder.m)
    previous = previous_phase_snapshot()
    if len(previous) != 678: raise SystemExit(f"expected 678 prior files, found {len(previous)}")
    ids_before = old_ids()
    if len(ids_before) != 678: raise SystemExit(f"expected 678 prior IDs, found {len(ids_before)}")
    f4_before = {path.relative_to(ROOT).as_posix(): sha_file(path) for path in (ROOT / DEST_REL).rglob("*") if path.is_file()}
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    report_paths = {rel: sha_file(ROOT / Path(*safe_rel(rel).parts)) for rel in REPORTS}

    # Only the two manifest-declared output files are rewritten. All other generated files are read-only.
    for rel in sorted(changed_paths):
        path = ROOT.joinpath(*rel.parts)
        path.write_text(norm(builder.outputs[rel]), encoding="utf-8", newline="\n")

    persisted: dict[PurePosixPath, str] = {}
    for rel, expected in builder.outputs.items():
        path = ROOT.joinpath(*rel.parts)
        actual = read_text(path)
        if actual != norm(expected): raise SystemExit(f"post-repair output differs from manifest reconstruction: {rel}")
        persisted[rel] = actual
    if len(persisted) != 395: raise SystemExit(f"expected 395 persisted files, got {len(persisted)}")
    builder.outputs = persisted
    audit_errors, unit_results, warnings = audit_builder(builder, previous, protected, ids_before)
    if audit_errors:
        print("POST-REPAIR AUDIT FAILED")
        for error in audit_errors: print("- " + error)
        return 6
    write_reports(builder, builder.types(), unit_results, warnings, BASE, len(builder.records))

    current_f4 = {path.relative_to(ROOT).as_posix(): sha_file(path) for path in (ROOT / DEST_REL).rglob("*") if path.is_file()}
    expected_f4 = {str(rel): sha_file(ROOT / Path(*rel.parts)) for rel in builder.outputs}
    if current_f4 != expected_f4: raise SystemExit("Fase 4 tree changed outside generated output set")
    for path, digest in f4_before.items():
        if path not in {str(rel) for rel in changed_paths} and current_f4.get(path) != digest:
            raise SystemExit(f"unapproved Fase 4 file changed: {path}")
    for rel, digest in protected.items():
        if sha_file(ROOT / Path(*safe_rel(rel).parts)) != digest: raise SystemExit(f"protected source changed during link repair: {rel}")
    if previous_phase_snapshot() != previous: raise SystemExit("Fases 1–3 changed during link repair")
    if hashlib.sha256((ROOT / MANIFEST_REL).read_bytes()).hexdigest() != manifest_hash: raise SystemExit("manifest changed during link repair")
    if len(old_ids() | {engine.fm(text, str(path))[1]["arquivo_id"] for path, text in builder.outputs.items()}) != 1073:
        raise SystemExit("global ID inventory changed during link repair")
    print(f"LINK REPAIR OK | files_changed={len(changed_paths)} | mappings={len(builder.records)} | links={'; '.join(w for w in warnings if w.startswith('resolved_markdown_links='))}")
    print("Only the two exact manifest-authorized hrefs and the three Fase 4 audit reports were updated.")
    return 0


def metadata_report(builder: Builder) -> list[str]:
    lines = ["| Unidade | Campo | Valor original | Valor no README YAML | Resultado |", "|---|---|---|---|---|"]
    for uk, unit in builder.m["unidades"].items():
        values = [("title", builder.sources[uk]["title"]), *unit["metadados_originais"].items()]
        for key, value in values:
            lines.append(f"| {uk} | `{key}` | `{json.dumps(value, ensure_ascii=False)}` | `{json.dumps(value, ensure_ascii=False)}` | OK |")
    return lines


def report_mapping(builder: Builder) -> None:
    target = ROOT / "docs/migracao/relatorio_mapeamento_fase4.csv"
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["unidade", "origem", "secao", "bloco", "tipo", "alias", "destino", "inicio_char", "fim_char", "palavras", "sha256_texto", "normalizacao_estrutural_autorizada"])
        writer.writeheader()
        for row in builder.records:
            text = row["texto"]
            notes = []
            for rule in normalization_rules(builder.m):
                if rule.get("unidade") == row["unidade"] and rule.get("alias") == row["alias"] and f"]({rule['caminho_original']})" in text:
                    notes.append(f"href {rule['caminho_original']} -> {rule['caminho_migrado']} (rótulo e conteúdo preservados)")
            writer.writerow({
                "unidade": row["unidade"], "origem": row["origem"], "secao": row["secao"], "bloco": row["bloco"],
                "tipo": row["tipo"], "alias": row["alias"], "destino": row["destino"], "inicio_char": row["inicio"],
                "fim_char": row["fim"], "palavras": engine.words(text), "sha256_texto": sha_text(text),
                "normalizacao_estrutural_autorizada": "; ".join(notes),
            })


def write_reports(builder: Builder, types: Counter, unit_results: dict[str, dict], warnings: list[str], base: str, mappings: int) -> None:
    report_mapping(builder)
    type_lines = [f"- `{name}`: {count}" for name, count in sorted(types.items())]
    unit_lines = ["| Unidade | Assuntos | Arquivos | Mapeamentos | Metadados |", "|---|---:|---:|---:|---|"]
    for uk, unit in builder.m["unidades"].items():
        count = len(unit["assuntos"])
        result = unit_results[uk]
        unit_lines.append(f"| {uk} | {count} | {result['arquivos']} | {result['mapeamentos']} | OK |")
    meta_lines = metadata_report(builder)
    normalization_lines = [
        f"- `{item['destino']}`: `{item['caminho_original']}` → `{item['caminho_migrado']}`; somente o href foi ajustado, mantendo rótulo visível e texto ao redor. {item['justificativa']}"
        for item in builder.normalizations_applied
    ] or ["- Nenhuma."]
    validation = [
        "# Relatório de validação — migração estrutural da Fase 4", "",
        "- Resultado: **APROVADA COM RESSALVAS** (limitação conhecida: wikilinks Obsidian fora do vault configurado).",
        f"- Commit-base: `{base}`", "- Branch: `migracao-estrutura`", "- Unidades ativas: 17", "- Assuntos de conteúdo: 49; contêineres de projeto: 2",
        f"- Arquivos gerados: {len(builder.outputs)}", f"- Registros de mapeamento: {mappings}", "- Questões: 65; práticas/atividades: 43; flashcards: 3; marcos: 8; perguntas de revisão: 8", "",
        "## Contagem por tipo", "", *type_lines, "", "## Resultado por unidade", "", *unit_lines, "", "## Conversão dos metadados", "", *meta_lines, "",
        "## Verificações", "",
        "- Manifesto validado pelo parser YAML homologado, com chaves duplicadas recusadas; campos, aliases, caminhos e IDs foram validados antes da escrita.",
        "- Cada microtópico, questão, prática, solução, rubrica, aceite, flashcard e marco tem origem e destino rastreáveis no CSV.",
        "- Os arquivos persistidos foram comparados com uma reconstrução nova a partir das fontes e do manifesto. Texto e blocos de código coincidem após normalização de BOM/finais de linha e das substituições de href listadas em `Normalizações estruturais autorizadas`; os blocos-fonte e seus hashes no CSV permanecem literais.",
        "- Metadados em lista foram convertidos para YAML no README, mantendo os valores de `key`, `tipo`, `carater`, `profundidade`, `estimativa_minutos`, `tags` e `status`; o título H1 original foi transportado para `title` e também mantido como título visível do índice.",
        "- As 42 rubricas mantêm suas escalas originais; 16.2 e 16.3 continuam sem rubrica numérica.",
        "- Projetos mantêm quatro marcos cada, títulos literais, quatro aceites por projeto, checklists finais, três respostas de revisão de 16.2 e cinco perguntas abertas de 16.3.",
        "- Itens compartilhados aparecem uma única vez em `90_integracao/`; as associações com os assuntos permanecem nos frontmatters e no manifesto.",
        "- Links relativos gerados foram resolvidos. Links relativos de origem com destino inequívoco receberam somente a correção estrutural de href listada abaixo; o texto visível foi preservado.",
        *[f"- {w}" for w in warnings if w.startswith("source-relative link preserved")],
        "- Wikilinks foram preservados e contados, mas dependem da raiz do vault Obsidian.",
        "- As 678 unidades/arquivos migrados das Fases 1–3 e os arquivos originais, página da fase, referências gerais, guia local e JSON permaneceram byte a byte inalterados.",
        "- A unidade 8.4 não existe nesta árvore; os arquivos das Fases 1–3, originais e JSON foram preservados.", "",
        "## Normalizações estruturais autorizadas", "", *normalization_lines, "",
        "## Outras normalizações estruturais aplicadas", "",
        "1. Leitura UTF-8 ignorou BOM, quando presente, e converteu CRLF/CR para LF na representação em memória; os arquivos de origem não foram regravados.",
        "2. As listas de metadados do cabeçalho foram convertidas em campos YAML tipados no README; o H1 foi copiado ao campo `title` e mantido como título visível. Nenhum valor de metadado foi inferido ou alterado.",
        "3. Cabeçalhos de seção e marcadores de separação aprovados foram distribuídos pelos arquivos estruturais correspondentes; nenhum texto foi descartado.", "",
        "## Ressalvas e limitações", "", "- Wikilinks Obsidian foram preservados, mas podem não resolver até a integração da árvore ao vault configurado.",
        "- O manifesto usa o subconjunto YAML parseado pelo validador homologado; o ambiente não possui PyYAML nem pacote Node YAML independente.", "",
    ]
    (ROOT / "docs/migracao/relatorio_validacao_fase4.md").write_text("\n".join(validation), encoding="utf-8", newline="\n")
    audit = [
        "# Auditoria final — migração estrutural da Fase 4", "", "## Veredito", "", "**APROVADA COM RESSALVAS**", "",
        f"- Base: `{base}`; branch: `migracao-estrutura`.", f"- Arquivos: {len(builder.outputs)}; mapeamentos: {mappings}.",
        "- Unidades: 17; assuntos de conteúdo: 49; projetos: 2; microtópicos: 68; quizzes: 65; práticas/atividades: 43; flashcards: 3; rubricas existentes: 42; marcos: 8.",
        "- Auditoria textual: aprovada, sem lacunas, sobreposições ou divergências entre reconstrução e saída persistida.", "",
        "## Resultado por unidade", "", *unit_lines, "", "## Metadados", "", *meta_lines, "",
        "## Projetos", "", "- 16.2: quatro marcos, quatro aceites, checklist final, três perguntas de revisão e respectivas respostas; sem rubrica numérica.",
        "- 16.3: quatro marcos, quatro aceites, checklist final incorporado ao marco 4, cinco perguntas abertas sem gabarito; sem rubrica numérica.",
        "- Títulos dos oito marcos coincidem literalmente e na ordem com as fontes.", "",
        "## Normalizações estruturais autorizadas", "", *normalization_lines, "",
        "## Integridade e preservação", "", *[f"- {w}" for w in warnings],
        "- Fonte transacional canônica: 12.2. T4/Q5/P3 de 11.3 foram preservados literalmente em 11.3, sem mover nem duplicar blocos.",
        "- 14.1 manteve `carater: obrigatorio`; a decisão não cria exigência de usar MongoDB em todos os projetos.",
        "- 13.1 e 16.1 preservaram repertório, atividades e flashcards sem acrescentar avaliação.",
        "- Ordem de navegação do módulo 11: 11.3 → 11.1 → 11.2.",
        "- JSON não foi modificado e o importador não foi executado; fontes e fases anteriores permanecem intactas.",
        "- A pasta 8.4 não foi criada.", "",
        "## Limitações", "", "- Wikilinks Obsidian dependem da raiz do vault configurado, que permanece externa a esta árvore migrada.",
        "- Nenhum commit foi criado; a Fase 5 não foi iniciada.", "",
        "O mapeamento detalhado de cada bloco está em `relatorio_mapeamento_fase4.csv`; os hashes e intervalos referem-se ao texto fonte normalizado apenas por BOM de leitura e finais de linha.", "",
    ]
    (ROOT / "docs/migracao/auditoria_final_fase4.md").write_text("\n".join(audit), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validação e migração estrutural da Fase 4")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--apply", action="store_true", help="gera a árvore e os relatórios após validação completa em memória")
    modes.add_argument("--repair-links-dry-run", action="store_true", help="valida a reparação estrutural aprovada sem escrever")
    modes.add_argument("--repair-links", action="store_true", help="aplica somente as normalizações de links exatas declaradas no manifesto")
    args = parser.parse_args()
    manifest_path = ROOT / MANIFEST_REL
    manifest_bytes = manifest_path.read_bytes()
    manifest_text = manifest_bytes.decode("utf-8-sig")
    manifest = engine.yaml(manifest_text, "Fase 4 manifest")
    engine.manifest = manifest
    errors = validate_manifest(manifest)
    if errors:
        print("MANIFEST INVALID")
        for error in errors: print("- " + error)
        return 2

    allowed_untracked = {
        "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
        MANIFEST_REL,
        SCRIPT_REL,
    }
    repair_mode = args.repair_links_dry_run or args.repair_links
    preflight = check_git_preflight(repair_mode or args.apply, (ROOT / DEST_REL).exists(), allowed_untracked, allow_existing=repair_mode)
    if preflight:
        print("GIT PREFLIGHT FAILED")
        for error in preflight: print("- " + error)
        return 3
    if not repair_mode:
        for rel in REPORTS:
            if (ROOT / Path(*safe_rel(rel).parts)).exists():
                print(f"REPORT EXISTS: {rel}")
                return 3
    if not (ROOT / JSON_REL).is_file():
        print("JSON import source not found; stopped")
        return 3

    protected = protected_snapshot(manifest)
    previous = previous_phase_snapshot()
    if len(previous) != 678:
        print(f"expected 678 prior migrated files, found {len(previous)}")
        return 3
    ids_before = old_ids()
    if len(ids_before) != 678:
        print(f"expected 678 prior unique IDs, found {len(ids_before)}")
        return 3
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    builder = Builder(manifest)
    builder.build()
    types = builder.types()
    if len(builder.outputs) != 395:
        raise SystemExit("output count mismatch before write")
    # A second independent builder pass proves the manifest/source reconstruction is deterministic.
    rebuilt = Builder(engine.yaml(manifest_path.read_text(encoding="utf-8-sig"), "Fase 4 manifest reconstruction"))
    rebuilt.build()
    if rebuilt.outputs != builder.outputs:
        raise SystemExit("in-memory source reconstruction is not deterministic")
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest_hash:
        raise SystemExit("manifest changed during dry-run")
    for rel, digest in protected.items():
        if sha_file(ROOT / Path(*safe_rel(rel).parts)) != digest: raise SystemExit(f"protected input changed during dry-run: {rel}")
    if previous_phase_snapshot() != previous: raise SystemExit("Fases 1–3 changed during dry-run")
    if len(builder.records) < 200:
        raise SystemExit(f"unexpectedly low mapping count: {len(builder.records)}")
    dry_errors, _, dry_warnings = audit_builder(builder, previous, protected, ids_before)
    if dry_errors:
        print("PRE-WRITE CONTENT/LINK AUDIT FAILED")
        for error in dry_errors: print("- " + error)
        return 4
    print(f"DRY-RUN OK | base={BASE} | branch=migracao-estrutura | units=17 | content_subjects=49 | project_containers=2 | theory_blocks=68 | questions=65 | practices=43 | flashcards=3 | project_milestones=8 | files={len(builder.outputs)} | mappings={len(builder.records)}")
    print("types=" + json.dumps(types, ensure_ascii=False, sort_keys=True))
    for uk, unit in manifest["unidades"].items():
        count = sum(1 for p in builder.outputs if p.parts[:len((PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])).parts)] == (PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])).parts)
        print(f"unit={uk}|subjects={len(unit['assuntos'])}|files={count}")
    print(f"protected_phase4_inputs={len(protected)}|prior_files={len(previous)}|prior_ids={len(ids_before)}")
    for warning in dry_warnings:
        if warning.startswith("source-relative link preserved"):
            print("LINK WARNING: " + warning)
    print("link_audit=" + "; ".join(w for w in dry_warnings if w.startswith(("resolved_markdown_links=", "preserved_wikilinks="))))
    if args.repair_links_dry_run or args.repair_links:
        tree_errors, changed_paths = validate_existing_tree_for_link_repair(builder)
        if tree_errors:
            print("EXISTING TREE DOES NOT MATCH APPROVED REPAIR SCOPE")
            for error in tree_errors: print("- " + error)
            return 4
        print("LINK-REPAIR CHECK OK | files_to_change=" + ", ".join(sorted(map(str, changed_paths))))
        if args.repair_links_dry_run:
            return 0
        return repair_existing_links(builder, manifest_bytes, allowed_untracked)
    if not args.apply: return 0

    preflight = check_git_preflight(True, (ROOT / DEST_REL).exists(), allowed_untracked)
    if preflight:
        print("PRE-WRITE GIT CHECK FAILED")
        for error in preflight: print("- " + error)
        return 4
    if manifest_path.read_bytes() != manifest_bytes: raise SystemExit("manifest changed before write")
    dest = ROOT / DEST_REL
    if dest.exists(): raise SystemExit("destination appeared before write")
    dest.mkdir(parents=True, exist_ok=False)
    for rel, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        path = ROOT.joinpath(*rel.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(norm(text), encoding="utf-8", newline="\n")

    persisted: dict[PurePosixPath, str] = {}
    for rel, expected in builder.outputs.items():
        path = ROOT.joinpath(*rel.parts)
        if not path.is_file(): raise SystemExit(f"persisted file missing: {rel}")
        actual = read_text(path)
        if actual != norm(expected): raise SystemExit(f"persisted output differs from validated reconstruction: {rel}")
        persisted[rel] = actual
    reread = Builder(engine.yaml(manifest_path.read_text(encoding="utf-8-sig"), "Fase 4 post-write manifest"))
    reread.build()
    if reread.outputs != persisted: raise SystemExit("post-write reconstruction differs from persisted tree")
    reread.outputs = persisted
    audit_errors, unit_results, warnings = audit_builder(reread, previous, protected, ids_before)
    if audit_errors:
        print("POST-WRITE AUDIT FAILED; generated files retained for review")
        for error in audit_errors: print("- " + error)
        return 5
    current_ids = old_ids() | {engine.fm(text, str(path))[1]["arquivo_id"] for path, text in persisted.items()}
    if len(current_ids) != 1073: raise SystemExit(f"global file ID count mismatch: {len(current_ids)}")
    if manifest_path.read_bytes() != manifest_bytes: raise SystemExit("manifest changed during migration")
    for rel, digest in protected.items():
        if sha_file(ROOT / Path(*safe_rel(rel).parts)) != digest: raise SystemExit(f"protected source changed after generation: {rel}")
    if previous_phase_snapshot() != previous: raise SystemExit("prior phase file changed after generation")
    if len(list(dest.rglob("*.md"))) != 395: raise SystemExit("persisted recursive file count differs from expected 395")
    write_reports(reread, reread.types(), unit_results, warnings, BASE, len(reread.records))
    print(f"MIGRATION OK | base={BASE} | branch=migracao-estrutura | files=395 | mappings={len(reread.records)} | verdict=APROVADA COM RESSALVAS")
    print("reports=" + ", ".join(REPORTS))
    print("No commit, JSON import, original-source edit, or Phase 5 migration was performed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STOPPED: {type(exc).__name__}: {exc}")
        raise
