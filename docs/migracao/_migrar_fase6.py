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

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine
import _migrar_fase4 as f4

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase6.yml"
DEST_REL = "docs/courses/trilhacode/Conteudos_migrado/Fase_6"
BASE = "a229795d9296b71ab7d1adca1d71a9a3baaaf36a"
ORDER = [
    "25.1", "25.2", "26.1", "26.2", "27.1", "27.2", "27.3", "27.4",
    "28.1", "28.2", "28.3", "29.1", "29.2", "30.1", "30.2", "31.1",
    "31.2", "31.3", "31.4", "31.5",
]
EXPECTED_TREE_COUNTS = {1: 221, 2: 144, 3: 313, 4: 395, 5: 483}
REPORTS = [
    "docs/migracao/relatorio_mapeamento_fase6.csv",
    "docs/migracao/relatorio_validacao_fase6.md",
    "docs/migracao/auditoria_final_fase6.md",
]
PHASE_DOCS = [
    "docs/courses/trilhacode/Fase_6_Frontend_Moderno.md",
    "docs/courses/trilhacode/Referencias_Fase_6.md",
]
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
PRESERVE_UNTRACKED = {
    "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
    "docs/migracao/PLANEJAMENTO_FASE5.md",
    "docs/migracao/PLANEJAMENTO_FASE6.md",
    MANIFEST_REL,
    "docs/migracao/_migrar_fase6.py",
}


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return norm(path.read_text(encoding="utf-8-sig"))


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"caminho relativo inseguro: {value!r}")
    return path


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True, encoding="utf-8"
    ).strip()


def line_offsets(lines: list[str]) -> list[int]:
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def slice_lines(raw: str, start: int, end: int) -> tuple[str, int, int]:
    lines = raw.splitlines(keepends=True)
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"faixa de linhas inválida {start}-{end}/{len(lines)}")
    offsets = line_offsets(lines)
    a, b = offsets[start - 1], offsets[end]
    return raw[a:b], a, b


def heading_span(raw: str, literal: str, level: int = 2) -> tuple[str, int, int]:
    lines = raw.splitlines(keepends=True)
    offsets = line_offsets(lines)
    matches = [i for i, line in enumerate(lines) if line.rstrip("\r\n").strip() == literal]
    if len(matches) != 1:
        raise ValueError(f"seletor de heading {literal!r}: encontrados {len(matches)}")
    start = matches[0]
    prefix = "#" * level + " "
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith(prefix) and not lines[i].startswith(prefix + "#")),
        len(lines),
    )
    a, b = offsets[start], offsets[end]
    return raw[a:b], a, b


def full_source_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    content_root = ROOT / "docs/courses/trilhacode/Conteudos"
    for path in content_root.rglob("*"):
        if path.is_file():
            result[path.relative_to(ROOT).as_posix()] = sha_file(path)
    for rel in PHASE_DOCS + [JSON_REL]:
        path = ROOT / Path(*safe_rel(rel).parts)
        if not path.is_file():
            raise ValueError(f"fonte protegida ausente: {rel}")
        result[rel] = sha_file(path)
    for rel in PRESERVE_UNTRACKED - {MANIFEST_REL, "docs/migracao/_migrar_fase6.py"}:
        path = ROOT / Path(*safe_rel(rel).parts)
        if path.is_file():
            result[rel] = sha_file(path)
    return result


def previous_tree_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    for number, expected in EXPECTED_TREE_COUNTS.items():
        base = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        if not base.is_dir():
            raise ValueError(f"árvore homologada ausente: Fase_{number}")
        paths = [p for p in base.rglob("*") if p.is_file()]
        if len(paths) != expected:
            raise ValueError(f"Fase_{number}: esperado {expected} arquivos, encontrado {len(paths)}")
        for path in paths:
            result[path.relative_to(ROOT).as_posix()] = sha_file(path)
    if len(result) != 1556:
        raise ValueError(f"esperados 1.556 arquivos anteriores, encontrados {len(result)}")
    return result


def previous_ids() -> set[str]:
    result: set[str] = set()
    for number in EXPECTED_TREE_COUNTS:
        base = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        for path in base.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in result:
                raise ValueError(f"arquivo_id anterior ausente ou repetido: {path} ({ident})")
            result.add(ident)
    if len(result) != 1556:
        raise ValueError(f"esperados 1.556 IDs anteriores, encontrados {len(result)}")
    return result


def git_preflight(mode: str) -> list[str]:
    errors: list[str] = []
    root = git("rev-parse", "--show-toplevel").replace("\\", "/").casefold()
    if root != str(ROOT).replace("\\", "/").casefold():
        errors.append("raiz Git diferente do worktree autorizado")
    if git("branch", "--show-current") != "migracao-estrutura":
        errors.append("branch diferente de migracao-estrutura")
    if git("rev-parse", "HEAD") != BASE:
        errors.append("HEAD diferente da base homologada da Fase 5")
    if git("diff", "--cached", "--name-only"):
        errors.append("índice Git não está vazio")
    if git("diff", "--name-only"):
        errors.append("há alterações em arquivos rastreados")
    for line in git("status", "--porcelain").splitlines():
        path = line[3:].replace("\\", "/")
        if path in PRESERVE_UNTRACKED:
            continue
        if mode in ("dry-run", "audit-existing", "repair-links") and (
            path.startswith(DEST_REL + "/") or path in REPORTS
        ):
            continue
        errors.append(f"entrada Git não prevista: {line}")
    dest = ROOT / Path(*safe_rel(DEST_REL).parts)
    if mode == "apply" and dest.exists():
        errors.append("a árvore Fase_6 já existe; não sobrescrever")
    if mode == "apply":
        for rel in REPORTS:
            if (ROOT / Path(*safe_rel(rel).parts)).exists():
                errors.append(f"relatório de destino já existe: {rel}")
    if mode == "repair-links":
        if not dest.is_dir():
            errors.append("árvore existente da Fase 6 ausente para normalização autorizada")
        for rel in REPORTS:
            if not (ROOT / Path(*safe_rel(rel).parts)).is_file():
                errors.append(f"relatório existente ausente: {rel}")
    return errors


class Builder:
    def __init__(self, manifest: dict):
        self.m = manifest
        self.dest = PurePosixPath(manifest["destino_raiz"])
        self.outputs: dict[PurePosixPath, str] = {}
        self.records: list[dict] = []
        self.parts: dict[tuple[str, str], list[dict]] = defaultdict(list)
        self.sources: dict[str, dict] = {}
        self.types: Counter = Counter()
        self.normalization_counts: Counter = Counter()
        self.normalization_paths: dict[PurePosixPath, str] = {}
        self.coverage_stats: dict = {}
        self.link_stats: dict = {}
        engine.manifest = manifest
        engine.DEST = self.dest
        engine.output = self.outputs

    def add(self, uk: str, alias: str, source: str, start: int, end: int,
            segment: str, item: str | None = None, title: str | None = None,
            transform: str = "literal") -> None:
        unit = self.m["unidades"][uk]
        spec = unit["arquivos"].get(alias)
        if not spec:
            raise ValueError(f"{uk}/{alias}: alias sem arquivo")
        if end < start or len(source) != end - start:
            raise ValueError(f"{uk}/{alias}: faixa/fragmento inconsistente ({start}:{end})")
        context: dict = {}
        if spec.get("assunto"):
            context["assunto"] = spec["assunto"]
        elif spec.get("assuntos"):
            context["assuntos"] = spec["assuntos"]
        if context.get("assunto") and context["assunto"] not in unit.get("assuntos", []):
            raise ValueError(f"{uk}/{alias}: assunto fora do mapa")
        if context.get("assuntos") and any(x not in unit.get("assuntos", []) for x in context["assuntos"]):
            raise ValueError(f"{uk}/{alias}: assunto compartilhado fora do mapa")
        rendered = source
        normalizations = self.m.get("normalizacoes_estruturais_autorizadas", {}).get("links_markdown", [])
        for rule in normalizations:
            if rule["unidade"] != uk:
                continue
            count = rendered.count(rule["origem_literal"])
            if count:
                rendered = rendered.replace(rule["origem_literal"], rule["destino_literal"])
                self.normalization_counts[uk] += count
                self.normalization_paths[self.dest / safe_rel(unit["pasta"]) / safe_rel(spec["path"])] = uk
                transform += "; normalização estrutural de link relativo aprovada"
        self.parts[(uk, alias)].append({
            "source": rendered, "start": start, "end": end, "segment": segment,
            "item": item, "title": title, "transform": transform, "context": context,
        })
        self.records.append({
            "unidade": uk, "origem": unit["origem"], "bloco": item or segment,
            "tipo": spec["tipo"], "alias": alias,
            "destino": (self.dest / safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix(),
            "segmento": segment, "offset_inicio": start, "offset_fim": end,
            "texto_origem": source, "normalizacao": transform,
        })

    def add_lines(self, uk: str, alias: str, line_range: dict,
                  segment: str, item: str | None = None,
                  title: str | None = None, transform: str = "literal") -> tuple[str, int, int]:
        raw = self.sources[uk]["raw"]
        text, start, end = slice_lines(raw, line_range["inicio"], line_range["fim"])
        self.add(uk, alias, text, start, end, segment, item=item, title=title, transform=transform)
        return text, start, end

    def load_sources(self) -> None:
        source_root = ROOT / "docs/courses/trilhacode/Conteudos/Fase_6"
        actual_sources = {p.relative_to(ROOT).as_posix() for p in source_root.rglob("*.md")}
        declared_sources = {u["origem"] for u in self.m["unidades"].values()}
        if len(actual_sources) != 20 or actual_sources != declared_sources:
            raise ValueError(
                f"inventário ativo diverge do manifesto: ativos={len(actual_sources)} "
                f"faltam={sorted(declared_sources-actual_sources)} adicionais={sorted(actual_sources-declared_sources)}"
            )
        for uk, unit in self.m["unidades"].items():
            source_path = ROOT / Path(*safe_rel(unit["origem"]).parts)
            raw = read_text(source_path)
            title, metadata, _ = f4.parse_header(raw, unit, unit["origem"])
            if title != unit["titulo_original"] or metadata != unit["metadados_originais"]:
                raise ValueError(f"{uk}: título/metadados não correspondem à fonte")
            self.sources[uk] = {
                "raw": raw, "lines": raw.splitlines(keepends=True),
                "title": title, "metadata": metadata, "path": unit["origem"],
            }

    def emit_metadata_records(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        raw = self.sources[uk]["raw"]
        title, metadata, mappings = f4.parse_header(raw, unit, unit["origem"])
        readme = (self.dest / safe_rel(unit["pasta"]) / "README.md").as_posix()
        lines = raw.splitlines(keepends=True)
        offsets = line_offsets(lines)
        for key, line, char_start, char_end in mappings:
            line_index = raw[:char_start].count("\n") + 1
            source_value = title if key == "title" else metadata[key]
            self.records.append({
                "unidade": uk, "origem": unit["origem"], "bloco": key,
                "tipo": "topic_index" if key == "title" else "metadata_conversion",
                "alias": "IDX", "destino": readme,
                "segmento": "H1_para_title_e_indice" if key == "title" else "lista_para_frontmatter",
                "offset_inicio": char_start, "offset_fim": char_end,
                "texto_origem": line, "normalizacao": "metadado estrutural convertido para YAML; valor preservado",
                "valor_origem": json.dumps(source_value, ensure_ascii=False),
                "valor_destino": json.dumps(source_value, ensure_ascii=False),
                "linha_inicio": line_index, "linha_fim": line_index,
            })

    def emit_common(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        raw = self.sources[uk]["raw"]
        for selector, alias in unit["blocos_origem"]["comuns"].items():
            if selector == "h1_and_original_metadata":
                continue
            source, start, end = heading_span(raw, selector, level=2)
            self.add(uk, alias, source, start, end, selector, item=selector.removeprefix("## "))

    def emit_theory(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        raw = self.sources[uk]["raw"]
        lines = self.sources[uk]["lines"]
        mapping = unit["blocos_origem"].get("teoria", {})
        aliases_by_range: set[tuple[int, int]] = set()
        for selector, record in mapping.items():
            lr = record["linhas"]
            if lines[lr["inicio"] - 1].strip() != selector.strip():
                raise ValueError(f"{uk}: seletor teórico não bate na linha {lr['inicio']}: {selector}")
            if record["arquivo"] not in unit["arquivos"]:
                raise ValueError(f"{uk}: alias teórico inexistente {record['arquivo']}")
            if record.get("assunto") != unit["arquivos"][record["arquivo"]].get("assunto"):
                raise ValueError(f"{uk}: assunto teórico e destino divergem em {selector}")
            if (lr["inicio"], lr["fim"]) in aliases_by_range:
                raise ValueError(f"{uk}: bloco teórico repetido {selector}")
            aliases_by_range.add((lr["inicio"], lr["fim"]))
            self.add_lines(uk, record["arquivo"], lr, "microtópico de teoria", item=selector)

    def emit_quiz(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        lines = self.sources[uk]["lines"]
        for item, record in unit["blocos_origem"].get("quiz", {}).items():
            q_alias = record["arquivo"]
            k_alias = record["resposta"]
            q_origin = unit["arquivos"][q_alias]["origem"]
            k_origin = unit["arquivos"][k_alias]["origem"]
            if q_origin["linhas"] != k_origin["linhas"]:
                raise ValueError(f"{uk}/{item}: Q e K não apontam para o mesmo bloco de origem")
            lr = q_origin["linhas"]
            full, start, end = slice_lines(self.sources[uk]["raw"], lr["inicio"], lr["fim"])
            boundary = record.get("separacao_inline_literal", {}).get("marcador_inicio")
            if not boundary or full.count(boundary) != 1:
                raise ValueError(f"{uk}/{item}: marcador literal de resposta ausente/ambíguo")
            split = full.index(boundary)
            question, answer = full[:split], full[split:]
            if not question.strip() or not answer.strip() or question + answer != full:
                raise ValueError(f"{uk}/{item}: divisão Q/K vazia ou não reconstrutiva")
            if q_origin.get("segmento") != "enunciado" or "resposta" not in k_origin.get("segmento", ""):
                raise ValueError(f"{uk}/{item}: descrição de origem Q/K incompatível")
            self.add(uk, q_alias, question, start, start + split, "enunciado", item=item)
            self.add(uk, k_alias, answer, start + split, end, "resposta inline separada", item=item,
                     transform="segmentação por marcador literal aprovado na fonte")

    def emit_practices(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        block_map = unit["blocos_origem"].get("praticas", {})
        for item, record in block_map.items():
            if not item.startswith("P"):
                # Rubricas comuns às atividades são blocos independentes da fonte.
                alias = record["arquivo"]
                lr = record["limite_origem"]
                if alias != item:
                    raise ValueError(f"{uk}/{item}: alias de rubrica comum inconsistente")
                self.add_lines(
                    uk, alias, lr, "rubrica comum das práticas",
                    item=",".join(record.get("aplica_a", [])) or item,
                    transform="bloco literal de rubrica compartilhada entre atividades",
                )
                continue
            alias = record["arquivo"]
            origin = unit["arquivos"][alias]["origem"]
            lr = origin["linhas"]
            full, start, end = slice_lines(self.sources[uk]["raw"], lr["inicio"], lr["fim"])
            solution_alias = record.get("solucao")
            rubric_alias = record.get("rubrica")
            if solution_alias or rubric_alias:
                solution_marker = "**Solução de referência:**"
                rubric_marker = "**Rubrica:**"
                solution_at = f4.marker_positions(full, solution_marker) if solution_alias else []
                rubric_at = f4.marker_positions(full, rubric_marker) if rubric_alias else []
                if solution_alias and len(solution_at) != 1:
                    raise ValueError(f"{uk}/{item}: marcador de solução não é único")
                if rubric_alias and len(rubric_at) != 1:
                    raise ValueError(f"{uk}/{item}: marcador de rubrica não é único")
                p_end = solution_at[0] if solution_alias else rubric_at[0]
                kp_start = solution_at[0] if solution_alias else None
                if solution_alias and rubric_alias:
                    if rubric_at[0] <= solution_at[0]:
                        raise ValueError(f"{uk}/{item}: ordem solução/rubrica inválida")
                    kp_end = rubric_at[0]
                    r_start = rubric_at[0]
                elif solution_alias:
                    kp_end = len(full)
                    r_start = None
                else:
                    kp_end = None
                    r_start = rubric_at[0]
                if p_end:
                    self.add(uk, alias, full[:p_end], start, start + p_end, "enunciado da prática", item=item)
                if solution_alias:
                    key_text = full[kp_start:kp_end]
                    if not key_text.strip():
                        raise ValueError(f"{uk}/{item}: solução vazia")
                    self.add(uk, solution_alias, key_text, start + kp_start, start + kp_end,
                             "solução inline separada", item=item,
                             transform="segmentação por marcador literal de solução")
                if rubric_alias:
                    rubric_text = full[r_start:]
                    if not rubric_text.strip():
                        raise ValueError(f"{uk}/{item}: rubrica vazia")
                    self.add(uk, rubric_alias, rubric_text, start + r_start, end,
                             "rubrica inline separada", item=item,
                             transform="segmentação por marcador literal de rubrica")
                reconstructed = full[:p_end]
                if solution_alias:
                    reconstructed += full[kp_start:kp_end]
                if rubric_alias:
                    reconstructed += full[r_start:]
                if reconstructed != full:
                    raise ValueError(f"{uk}/{item}: separação da prática não reconstrói a origem")
            else:
                self.add(uk, alias, full, start, end, "enunciado integral da prática", item=item)

    def emit_flashcards(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        for item, record in unit["blocos_origem"].get("flashcards", {}).items():
            alias = record["arquivo"]
            origin = unit["arquivos"][alias]["origem"]
            self.add_lines(uk, alias, origin["linhas"], "flashcard pergunta/resposta", item=item)

    def emit_project(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        raw = self.sources[uk]["raw"]
        project = unit["blocos_origem"]["projeto"]
        scope_alias = next((a for a, f in unit["arquivos"].items() if f["tipo"] == "project_scope"), None)
        if not scope_alias:
            raise ValueError(f"{uk}: arquivo de escopo do projeto ausente")
        for selector in project["escopo"]:
            text, start, end = heading_span(raw, selector, level=2)
            self.add(uk, scope_alias, text, start, end, "escopo/regras do projeto", item=selector.removeprefix("## "))
        for milestone, record in project["marcos"].items():
            m_alias, c_alias = record["arquivo"], record["aceite"]
            m_origin = unit["arquivos"][m_alias]["origem"]
            c_origin = unit["arquivos"][c_alias]["origem"]
            m_full, m_start, m_end = slice_lines(raw, m_origin["linhas"]["inicio"], m_origin["linhas"]["fim"])
            c_text, c_start, c_end = slice_lines(raw, c_origin["linhas"]["inicio"], c_origin["linhas"]["fim"])
            title = record["titulo_marco"]
            milestone_selector = m_origin.get("seletor", "")
            literal_title = re.sub(r"^#{1,6}\s+", "", milestone_selector)
            if not m_full.startswith(milestone_selector) or literal_title != title or title not in c_origin["seletor"]:
                raise ValueError(f"{uk}/{milestone}: título literal não corresponde à origem")
            if m_full.count(c_text) != 1:
                raise ValueError(f"{uk}/{milestone}: aceite não ocorre uma única vez no marco")
            local = m_full.index(c_text)
            before, after = m_full[:local], m_full[local + len(c_text):]
            if before:
                self.add(uk, m_alias, before, m_start, m_start + len(before), "marco", item=milestone, title=title)
            self.add(uk, c_alias, c_text, c_start, c_end, "critério de aceite", item=milestone, title=title)
            if after:
                after_start = m_start + local + len(c_text)
                self.add(uk, m_alias, after, after_start, m_end, "marco após aceite", item=milestone, title=title)
            if before + c_text + after != m_full:
                raise ValueError(f"{uk}/{milestone}: marco/aceite não reconstrói o bloco original")
        for field in ("rubrica", "checklist"):
            record = project.get(field)
            if not record:
                continue
            alias = record["arquivo"]
            origin = unit["arquivos"][alias]["origem"]
            text, start, end = slice_lines(raw, origin["linhas"]["inicio"], origin["linhas"]["fim"])
            if field == "rubrica":
                scale = record.get("escala_rubrica")
                declared_scale = unit["arquivos"][alias].get("escala_rubrica", "")
                scores = set(re.findall(r"(?m)^\|\s*(\d+)\s*\|", text))
                expected_scores = {"0", "1", "2", "3", "4"} if scale == "0–4" else None
                if not scale or scale not in declared_scale or (expected_scores and scores != expected_scores):
                    raise ValueError(f"{uk}: escala/descritores de rubrica não correspondem à fonte")
            self.add(uk, alias, text, start, end, "rubrica do projeto" if field == "rubrica" else "checklist final",
                     item=field, transform="bloco literal do projeto")

    def add_readme(self, uk: str) -> None:
        unit = self.m["unidades"][uk]
        title = self.sources[uk]["title"]
        fields = [
            ("title", title), *unit["metadados_originais"].items(),
            ("arquivo_id", unit["arquivo_ids"]["IDX"]), ("tipo_arquivo", "topic_index"),
        ]
        body = f"# {title}\n\n## Índice\n\n### Arquivos comuns\n"
        for selector, alias in unit["blocos_origem"]["comuns"].items():
            if selector == "h1_and_original_metadata":
                continue
            spec = unit["arquivos"][alias]
            body += f"- [{spec['tipo']}]({spec['path']})\n"
        if unit.get("tipo_projeto"):
            body += "\n### Arquivos do projeto\n"
            common_aliases = set(unit["blocos_origem"]["comuns"].values())
            for alias, spec in unit["arquivos"].items():
                if alias in common_aliases or alias == "IDX":
                    continue
                body += f"- [{spec['tipo']}: {PurePosixPath(spec['path']).name}]({spec['path']})\n"
        else:
            body += "\n### Assuntos\n"
            for subject in unit["assuntos"]:
                body += f"\n#### {subject}\n"
                for alias, spec in unit["arquivos"].items():
                    if alias == "IDX":
                        continue
                    rel = PurePosixPath(spec["path"])
                    if rel.parts and rel.parts[0] == subject:
                        body += f"- [{rel.name}]({rel.as_posix()})\n"
            integrations = [
                PurePosixPath(spec["path"]) for alias, spec in unit["arquivos"].items()
                if alias != "IDX" and PurePosixPath(spec["path"]).parts[0] == "90_integracao"
            ]
            if integrations:
                body += "\n### Integração\n"
                for rel in integrations:
                    body += f"- [{rel.name}]({rel.as_posix()})\n"
        path = self.dest / safe_rel(unit["pasta"]) / "README.md"
        if path in self.outputs:
            raise ValueError(f"{uk}: README duplicado")
        self.outputs[path] = engine.frontmatter(fields) + body

    def finalize(self) -> None:
        for uk, unit in self.m["unidades"].items():
            common_aliases = set(unit["blocos_origem"]["comuns"].values()) - {"IDX"}
            expected_aliases = set(unit["arquivos"]) - {"IDX"}
            actual_aliases = {alias for owner, alias in self.parts if owner == uk}
            if actual_aliases != expected_aliases:
                raise ValueError(
                    f"{uk}: aliases sem bloco/faltantes: ausentes={sorted(expected_aliases-actual_aliases)} "
                    f"extras={sorted(actual_aliases-expected_aliases)}"
                )
            for alias, spec in unit["arquivos"].items():
                if alias == "IDX":
                    continue
                parts = sorted(self.parts[(uk, alias)], key=lambda part: part["start"])
                if not parts:
                    raise ValueError(f"{uk}/{alias}: arquivo sem conteúdo de origem")
                if spec["tipo"] == "answer_key" and not spec.get("responde_a"):
                    raise ValueError(f"{uk}/{alias}: gabarito sem questão de origem")
                if spec["tipo"] == "answer_key_pratica" and not spec.get("responde_a"):
                    raise ValueError(f"{uk}/{alias}: solução sem prática de origem")
                context = {}
                if spec.get("assunto"):
                    context["assunto"] = spec["assunto"]
                elif spec.get("assuntos"):
                    context["assuntos"] = spec["assuntos"]
                items = []
                titles = []
                for part in parts:
                    item = part["item"]
                    if item and item not in items:
                        items.append(item)
                    if part["title"] and part["title"] not in titles:
                        titles.append(part["title"])
                title = spec.get("titulo_marco")
                if not title and spec.get("para_marco"):
                    title = unit["blocos_origem"]["projeto"]["marcos"][spec["para_marco"]]["titulo_marco"]
                if not title and titles:
                    title = titles[0]
                scale = spec.get("escala_rubrica")
                if spec["tipo"] == "rubric" and not scale:
                    raise ValueError(f"{uk}/{alias}: escala da rubrica ausente")
                rel = safe_rel(spec["path"])
                full_path = self.dest / safe_rel(unit["pasta"]) / rel
                body = "".join(part["source"] for part in parts)
                if not body.strip():
                    raise ValueError(f"{uk}/{alias}: saída vazia")
                before = len(self.outputs)
                engine.put(
                    uk, rel.as_posix(), spec["tipo"], body,
                    subject=context.get("assunto"), subjects=context.get("assuntos"),
                    items=items, order=f4.order_of(alias), title=title, scale=scale,
                )
                if len(self.outputs) != before + 1 or full_path not in self.outputs:
                    raise ValueError(f"{uk}/{alias}: saída colidiu com outro caminho")
                expected_engine_id = engine.file_id(uk, rel.as_posix())
                old_field = f"arquivo_id: {json.dumps(expected_engine_id, ensure_ascii=False)}"
                new_field = f"arquivo_id: {json.dumps(spec['arquivo_id'], ensure_ascii=False)}"
                self.outputs[full_path] = self.outputs[full_path].replace(old_field, new_field, 1)
            self.emit_metadata_records(uk)
            self.add_readme(uk)
        expected = set()
        ids = set()
        for uk, unit in self.m["unidades"].items():
            root = self.dest / safe_rel(unit["pasta"])
            for alias, spec in unit["arquivos"].items():
                path = root / safe_rel(spec["path"])
                if path in expected:
                    raise ValueError(f"caminho físico duplicado: {path}")
                expected.add(path)
                if alias == "IDX":
                    continue
                if spec["arquivo_id"] in ids:
                    raise ValueError(f"arquivo_id duplicado: {spec['arquivo_id']}")
                ids.add(spec["arquivo_id"])
            expected.add(root / "README.md")
            ident = unit["arquivo_ids"]["IDX"]
            if ident in ids:
                raise ValueError(f"arquivo_id duplicado: {ident}")
            ids.add(ident)
        for rule in self.m.get("normalizacoes_estruturais_autorizadas", {}).get("links_markdown", []):
            if self.normalization_counts[rule["unidade"]] != rule["ocorrencias_esperadas"]:
                raise ValueError(
                    f"normalização de link {rule['unidade']}: esperadas {rule['ocorrencias_esperadas']}, "
                    f"encontradas {self.normalization_counts[rule['unidade']]}"
                )
        if set(self.outputs) != expected:
            raise ValueError(
                f"paths gerados divergem: faltam={sorted(map(str, expected-set(self.outputs)))} "
                f"extras={sorted(map(str, set(self.outputs)-expected))}"
            )
        forecast = self.m["estimativa_arquivos"]
        if len(self.outputs) != forecast["total"]:
            raise ValueError(f"estimativa {forecast['total']} difere da geração {len(self.outputs)}")

    def build(self) -> None:
        self.load_sources()
        for uk, unit in self.m["unidades"].items():
            self.emit_common(uk)
            self.emit_theory(uk)
            self.emit_quiz(uk)
            self.emit_practices(uk)
            self.emit_flashcards(uk)
            if unit.get("tipo_projeto"):
                self.emit_project(uk)
        self.finalize()

    def type_counts(self) -> Counter:
        counts = Counter()
        for path, content in self.outputs.items():
            _, fields, body = engine.fm(content, str(path))
            if not body.strip():
                raise ValueError(f"arquivo gerado sem corpo: {path}")
            counts[fields["tipo_arquivo"]] += 1
        return counts


def validate_manifest(m: dict) -> None:
    if m.get("status_manifesto") != "aprovado_para_execucao":
        raise ValueError("manifesto não marcado aprovado_para_execucao")
    if m.get("fase") != "Fase_6" or m.get("base_commit") != BASE:
        raise ValueError("fase ou commit-base divergente")
    if m.get("id_prefix") != "f6" or m.get("destino_raiz") != DEST_REL:
        raise ValueError("prefixo ou destino divergente")
    if m.get("ordem_unidades") != ORDER or list(m["unidades"]) != ORDER:
        raise ValueError("ordem de unidades divergente")
    if len(m["unidades"]) != 20:
        raise ValueError("esperadas 20 unidades")
    if "8.4" in m["unidades"]:
        raise ValueError("8.4 aposentado não pode aparecer no manifesto")
    topics = sum(len(u.get("assuntos", [])) for u in m["unidades"].values())
    projects = sum(bool(u.get("tipo_projeto")) for u in m["unidades"].values())
    if topics != 57 or projects != 2:
        raise ValueError(f"esperados 57 assuntos e dois projetos, encontrados {topics}/{projects}")
    physical: set[str] = set()
    ids: set[str] = set()
    totals = Counter()
    for uk, unit in m["unidades"].items():
        if unit["key"] != uk:
            raise ValueError(f"{uk}: key divergente")
        if bool(unit.get("tipo_projeto")) != (uk in ("31.4", "31.5")):
            raise ValueError(f"{uk}: natureza de projeto divergente")
        aliases = unit["arquivos"]
        if set(aliases) != set(unit["arquivo_ids"]):
            raise ValueError(f"{uk}: aliases e arquivo_ids divergem")
        for alias, spec in aliases.items():
            path = (PurePosixPath(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
            if path in physical:
                raise ValueError(f"{uk}/{alias}: caminho físico repetido {path}")
            physical.add(path)
            if spec["arquivo_id"] in ids:
                raise ValueError(f"{uk}/{alias}: ID repetido")
            ids.add(spec["arquivo_id"])
            if spec["arquivo_id"] != unit["arquivo_ids"][alias]:
                raise ValueError(f"{uk}/{alias}: ID no arquivo diverge do mapa")
            totals[spec["tipo"]] += 1
        for subject in unit.get("assuntos", []):
            if not re.fullmatch(r"\d{2}_[a-z0-9_]+", subject):
                raise ValueError(f"{uk}: slug inválido {subject}")
        blocks = unit["blocos_origem"]
        for q, rec in blocks.get("quiz", {}).items():
            if rec["arquivo"] not in aliases or rec["resposta"] not in aliases:
                raise ValueError(f"{uk}/{q}: alias de quiz/gabarito ausente")
            if aliases[rec["resposta"]].get("responde_a") != rec["arquivo"]:
                raise ValueError(f"{uk}/{q}: gabarito não referencia Q correspondente")
            topics_for_item = rec.get("assuntos", [])
            expected_class = "compartilhado" if len(topics_for_item) > 1 else "exclusivo"
            if rec.get("classificacao") != expected_class:
                raise ValueError(f"{uk}/{q}: classificação exclusiva/compartilhada incorreta")
            shared = aliases[rec["arquivo"]].get("assuntos")
            if expected_class == "compartilhado":
                if "90_integracao" not in aliases[rec["arquivo"]]["path"] or shared != topics_for_item:
                    raise ValueError(f"{uk}/{q}: Q compartilhada sem destino/assuntos únicos")
            elif aliases[rec["arquivo"]].get("assunto") != topics_for_item[0]:
                raise ValueError(f"{uk}/{q}: Q exclusiva aponta para outra pasta")
        for item, rec in blocks.get("praticas", {}).items():
            alias = rec["arquivo"]
            if alias not in aliases:
                raise ValueError(f"{uk}/{item}: alias de prática ausente")
            if item.startswith("P"):
                topics_for_item = rec.get("assuntos", [])
                expected_class = "compartilhado" if len(topics_for_item) > 1 else "exclusivo"
                if rec.get("classificacao") != expected_class:
                    raise ValueError(f"{uk}/{item}: classificação de prática incorreta")
                if expected_class == "compartilhado":
                    if "90_integracao" not in aliases[alias]["path"] or aliases[alias].get("assuntos") != topics_for_item:
                        raise ValueError(f"{uk}/{item}: prática compartilhada com destino/assuntos divergentes")
                elif aliases[alias].get("assunto") != topics_for_item[0]:
                    raise ValueError(f"{uk}/{item}: prática exclusiva aponta para outra pasta")
                if rec.get("solucao") and aliases[rec["solucao"]].get("responde_a") != alias:
                    raise ValueError(f"{uk}/{item}: solução sem prática de origem")
        expected_coverage = {s: {
            "quiz_exclusivos": [], "quiz_compartilhados": [],
            "praticas_exclusivas": [], "praticas_compartilhadas": [],
            "flashcards_exclusivos": [], "flashcards_compartilhados": [],
        } for s in unit.get("assuntos", [])}
        for block_name in ("quiz", "praticas", "flashcards"):
            for item, rec in blocks.get(block_name, {}).items():
                if block_name == "praticas" and not item.startswith("P"):
                    continue
                subjects_for_item = rec.get("assuntos", [])
                group = "compartilhados" if len(subjects_for_item) > 1 else "exclusivos"
                if block_name == "quiz":
                    field = f"quiz_{group}"
                elif block_name == "praticas":
                    field = "praticas_compartilhadas" if group == "compartilhados" else "praticas_exclusivas"
                else:
                    field = "flashcards_compartilhados" if group == "compartilhados" else "flashcards_exclusivos"
                for subject in subjects_for_item:
                    if subject not in expected_coverage:
                        raise ValueError(f"{uk}/{item}: assunto de cobertura inexistente {subject}")
                    expected_coverage[subject][field].append(item)
        if unit.get("cobertura", {}) != expected_coverage:
            raise ValueError(f"{uk}: tabela de cobertura diverge dos itens declarados")
    expected_counts = m["estimativa_arquivos"]
    # 449 é uma previsão derivada; nunca completar o total com arquivos vazios.
    if expected_counts.get("total") != 449:
        raise ValueError("estimativa aprovada deveria ser 449")
    if sum(totals.values()) != 449:
        raise ValueError(f"contagem calculada de arquivos declarados não fecha: {sum(totals.values())}")


def audit_source_counts(builder: Builder) -> dict:
    theory = sum(len(u["blocos_origem"].get("teoria", {})) for u in builder.m["unidades"].values())
    quiz = sum(len(u["blocos_origem"].get("quiz", {})) for u in builder.m["unidades"].values())
    practices = sum(sum(1 for item in u["blocos_origem"].get("praticas", {}) if item.startswith("P")) for u in builder.m["unidades"].values())
    flashcards = sum(len(u["blocos_origem"].get("flashcards", {})) for u in builder.m["unidades"].values())
    milestones = sum(len(u["blocos_origem"].get("projeto", {}).get("marcos", {})) for u in builder.m["unidades"].values())
    solutions = sum(1 for u in builder.m["unidades"].values() for item, rec in u["blocos_origem"].get("praticas", {}).items() if item.startswith("P") and rec.get("solucao"))
    practice_rubrics = sum(1 for u in builder.m["unidades"].values() for item, rec in u["blocos_origem"].get("praticas", {}).items() if item.startswith("P") and rec.get("rubrica"))
    common_practice_rubrics = sum(1 for u in builder.m["unidades"].values() for item, rec in u["blocos_origem"].get("praticas", {}).items() if not item.startswith("P") and rec.get("arquivo") in u["arquivos"] and u["arquivos"][rec["arquivo"]]["tipo"] == "rubric")
    project_rubrics = sum(bool(u["blocos_origem"].get("projeto", {}).get("rubrica")) for u in builder.m["unidades"].values())
    checklists = sum(bool(u["blocos_origem"].get("projeto", {}).get("checklist")) for u in builder.m["unidades"].values())
    if (theory, quiz, practices, flashcards, milestones) != (74, 80, 52, 6, 8):
        raise ValueError(f"contagens de blocos de origem divergentes: {theory}/{quiz}/{practices}/{flashcards}/{milestones}")
    if (solutions, practice_rubrics, common_practice_rubrics, project_rubrics, checklists) != (15, 15, 2, 2, 2):
        raise ValueError("soluções/rubricas/checklists dos projetos divergem das fontes")
    return {
        "theory": theory, "quiz": quiz, "practice": practices, "flashcard": flashcards,
        "milestone": milestones, "solution": solutions,
        "practice_rubric_individual": practice_rubrics,
        "practice_rubric_common": common_practice_rubrics,
        "project_rubric": project_rubrics, "project_checklist": checklists,
    }


def audit_source_coverage(builder: Builder) -> tuple[list[str], dict]:
    errors: list[str] = []
    spans: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for row in builder.records:
        raw = builder.sources[row["unidade"]]["raw"]
        start, end = row["offset_inicio"], row["offset_fim"]
        if start < 0 or end < start or end > len(raw):
            errors.append(f"faixa inválida em {row['unidade']}/{row['alias']}: {start}:{end}")
            continue
        if raw[start:end] != row["texto_origem"]:
            errors.append(f"texto mapeado diverge da faixa fonte em {row['unidade']}/{row['alias']}")
        spans[row["unidade"]].append((start, end, row["alias"]))

    container_heads = set(builder.m.get("cabecalhos_container_nao_exportados", []))
    containers = Counter()
    mapped_chars = 0
    source_chars = 0
    for uk in ORDER:
        raw = builder.sources[uk]["raw"]
        covered = bytearray(len(raw))
        ordered = sorted(spans[uk], key=lambda item: (item[0], item[1]))
        last_end = -1
        last_alias = None
        for start, end, alias in ordered:
            if start < last_end:
                errors.append(f"sobreposição de origem em {uk}: {last_alias}/{alias} no offset {start}")
            last_end = max(last_end, end)
            last_alias = alias
            for index in range(start, end):
                covered[index] = 1
        mapped_chars += sum(covered)
        source_chars += len(raw)
        offset = 0
        for line in raw.splitlines(keepends=True):
            end = offset + len(line)
            if line.strip() and not all(covered[offset:end]):
                literal = line.strip()
                if literal in container_heads:
                    containers[literal] += 1
                else:
                    errors.append(f"trecho fonte sem destino em {uk}, linha {raw[:offset].count(chr(10))+1}: {literal[:180]}")
            offset = end
    missing_containers = container_heads - set(containers)
    if missing_containers:
        errors.append(f"cabeçalhos estruturais declarados mas ausentes: {sorted(missing_containers)}")
    return errors, {
        "fontes": len(spans),
        "caracteres_fonte": source_chars,
        "caracteres_com_destino": mapped_chars,
        "cabecalhos_container": dict(containers),
        "cabecalhos_container_total": sum(containers.values()),
    }


def audit_links(outputs: dict[PurePosixPath, str]) -> tuple[list[str], list[str], int, int]:
    errors: list[str] = []
    warnings: list[str] = []
    resolved = 0
    markdown_link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    wikilinks = 0
    normalized_outputs = {path.as_posix(): text for path, text in outputs.items()}
    for rel, text in outputs.items():
        _, fields, body = engine.fm(text, str(rel))
        wikilinks += len(re.findall(r"\[\[[^\]]+\]\]", body))
        for target in markdown_link.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_text, _, _ = target.partition("#")
            if not path_text:
                resolved += 1
                continue
            virtual = PurePosixPath(posixpath.normpath((rel.parent / PurePosixPath(path_text)).as_posix()))
            if virtual.as_posix() in normalized_outputs:
                resolved += 1
                continue
            repo_target = ROOT.joinpath(*virtual.parts)
            if repo_target.is_file():
                resolved += 1
                continue
            if fields.get("tipo_arquivo") == "topic_index":
                errors.append(f"link do índice não resolve: {rel} -> {target}")
                continue
            unit_root = next((u for u in engine.manifest["unidades"].values()
                              if rel.is_relative_to(PurePosixPath(DEST_REL) / safe_rel(u["pasta"]))), None)
            source_target = None
            if unit_root:
                source_target = (ROOT / Path(*safe_rel(unit_root["origem"]).parent.parts) / Path(path_text.replace("/", "\\"))).resolve()
            if source_target and source_target.is_file():
                warnings.append(f"link relativo preservado, mas não relocável sem copiar/alterar fonte: {rel} -> {target}")
            else:
                errors.append(f"link Markdown relativo quebrado: {rel} -> {target}")
    return errors, warnings, wikilinks, resolved


def audit_outputs(builder: Builder, prior_ids: set[str]) -> tuple[list[str], list[str], dict[str, dict]]:
    errors: list[str] = []
    warnings: list[str] = []
    results: dict[str, dict] = {}
    generated_ids: set[str] = set()
    type_counts = builder.type_counts()
    for rel, text in builder.outputs.items():
        try:
            _, fields, body = engine.fm(text, str(rel))
        except Exception as exc:
            errors.append(f"frontmatter YAML inválido em {rel}: {exc}")
            continue
        ident = fields.get("arquivo_id")
        if not ident or ident in generated_ids or ident in prior_ids:
            errors.append(f"arquivo_id ausente/duplicado/globalmente colidente em {rel}: {ident}")
        else:
            generated_ids.add(ident)
        if not body.strip():
            errors.append(f"corpo vazio em {rel}")
        if rel.name == "README.md":
            unit = next(u for u in builder.m["unidades"].values()
                        if (PurePosixPath(DEST_REL) / safe_rel(u["pasta"]) / "README.md") == rel)
            for key, value in unit["metadados_originais"].items():
                if fields.get(key) != value:
                    errors.append(f"metadado {key} mudou em {rel}")
            if fields.get("title") != unit["titulo_original"]:
                errors.append(f"title mudou em {rel}")
        else:
            unit = next(u for u in builder.m["unidades"].values()
                        if rel.is_relative_to(PurePosixPath(DEST_REL) / safe_rel(u["pasta"])))
            spec = next((f for f in unit["arquivos"].values() if f["path"] == rel.relative_to(PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])).as_posix()), None)
            if not spec:
                errors.append(f"arquivo sem declaração no manifesto: {rel}")
            else:
                if fields.get("tipo_arquivo") != spec["tipo"]:
                    errors.append(f"tipo_arquivo diverge do manifesto em {rel}")
                if fields.get("arquivo_id") != spec["arquivo_id"]:
                    errors.append(f"arquivo_id diverge do manifesto em {rel}")
                if spec.get("assunto") and fields.get("assunto") != spec["assunto"]:
                    errors.append(f"assunto diverge do manifesto em {rel}")
                if spec.get("assuntos") and fields.get("assuntos") != spec["assuntos"]:
                    errors.append(f"assuntos divergem do manifesto em {rel}")
                if spec.get("titulo_marco") and fields.get("titulo_marco") != spec["titulo_marco"]:
                    errors.append(f"titulo_marco diverge do literal em {rel}")
        if rel.name == "README.md":
            if fields.get("key") != unit["key"]:
                errors.append(f"key inválida no README em {rel}")
        elif fields.get("parent_key") != unit["key"]:
            errors.append(f"parent_key inválida em {rel}")
    if len(builder.outputs) != 449 or len(generated_ids) != 449:
        errors.append(f"esperados 449 arquivos/IDs gerados; encontrados {len(builder.outputs)}/{len(generated_ids)}")
    if len(prior_ids & generated_ids):
        errors.append("há colisão de IDs com as Fases 1–5")
    for uk, unit in builder.m["unidades"].items():
        root = PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])
        paths = [p for p in builder.outputs if p.parts[:len(root.parts)] == root.parts]
        per_type = Counter()
        for path in paths:
            _, child_fields, _ = engine.fm(builder.outputs[path], str(path))
            per_type[child_fields["tipo_arquivo"]] += 1
        results[uk] = {
            "arquivos": len(paths),
            "mapeamentos": sum(1 for row in builder.records if row["unidade"] == uk),
            "assuntos": len(unit.get("assuntos", [])),
            "projeto": bool(unit.get("tipo_projeto")),
            "tipos": dict(per_type),
        }
    coverage_errors, builder.coverage_stats = audit_source_coverage(builder)
    errors.extend(coverage_errors)
    expected = builder.m["estimativa_arquivos"]
    if dict(type_counts) != {k: v for k, v in expected.items() if k != "total"}:
        errors.append(f"contagem por tipo diverge da estimativa: {dict(type_counts)}")
    link_errors, link_warnings, wikilinks, resolved_links = audit_links(builder.outputs)
    errors.extend(link_errors)
    warnings.extend(link_warnings)
    builder.link_stats = {"markdown_relativos_resolvidos": resolved_links, "wikilinks_preservados": wikilinks}
    if wikilinks:
        warnings.append(f"{wikilinks} wikilinks preservados; resolução depende da raiz do vault Obsidian")
    else:
        warnings.append("raiz do vault Obsidian não confirmada; nenhum wikilink foi reescrito")
    return errors, warnings, results


def write_reports(builder: Builder, counts: dict, unit_results: dict,
                  warnings: list[str], verdict: str) -> None:
    csv_path, validation_path, audit_path = [ROOT / Path(*safe_rel(x).parts) for x in REPORTS]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["unidade", "origem", "bloco", "tipo", "alias", "destino", "segmento",
               "linha_inicio", "linha_fim", "offset_inicio", "offset_fim", "sha256_origem", "normalizacao"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in builder.records:
            source = ROOT / Path(*safe_rel(row["origem"]).parts)
            full = read_text(source)
            start, end = row["offset_inicio"], row["offset_fim"]
            line_start = full[:start].count("\n") + 1
            line_end = full[:end].count("\n") + (0 if end == start else 1)
            writer.writerow({
                "unidade": row["unidade"], "origem": row["origem"], "bloco": row["bloco"],
                "tipo": row["tipo"], "alias": row["alias"], "destino": row["destino"],
                "segmento": row["segmento"], "linha_inicio": line_start, "linha_fim": line_end,
                "offset_inicio": start, "offset_fim": end, "sha256_origem": sha(row["texto_origem"]),
                "normalizacao": row["normalizacao"],
            })
    rows = ["# Validação estrutural — Fase 6", "",
            f"- Base Git: `{BASE}`; branch `migracao-estrutura`.",
            f"- Fontes: 20 unidades ativas; 74 microtópicos, 80 questões, 52 práticas, seis flashcards e oito marcos.",
            f"- Saída: {len(builder.outputs)} arquivos; {len(builder.records)} mapeamentos rastreáveis.",
            f"- Blocos: {json.dumps(counts, ensure_ascii=False, sort_keys=True)}.",
            "- 80 respostas de quiz e 15 soluções práticas foram extraídas apenas por marcadores literais presentes nas fontes.",
            "- 17 rubricas de práticas (15 individuais e duas comuns) e duas rubricas de projeto preservadas; escalas 0–4 mantidas onde existentes.",
            "- 31.4 e 31.5: quatro marcos e quatro aceites por projeto; checklists finais de oito e nove itens.",
            "- Os arquivos ativos não sustentam a contagem histórica de 90 questões/54 práticas; nenhum conteúdo foi adicionado para compensar a diferença.",
            f"- Links Markdown relativos resolvidos: {builder.link_stats.get('markdown_relativos_resolvidos', 0)}; normalizações autorizadas: {sum(builder.normalization_counts.values())} ({dict(builder.normalization_counts)}).",
            "", "## Resultado por unidade", "", "| Unidade | Assuntos | Arquivos | Mapeamentos | Tipo | Contagem por tipo |", "|---|---:|---:|---:|---|---|"]
    for uk, info in unit_results.items():
        rows.append(f"| {uk} | {info['assuntos'] if not info['projeto'] else 'projeto'} | {info['arquivos']} | {info['mapeamentos']} | {'projeto' if info['projeto'] else 'conteúdo'} | `{json.dumps(info['tipos'], ensure_ascii=False, sort_keys=True)}` |")
    rows += ["", "## Integridade", "",
             "- Textos, exemplos e blocos de código foram reconstruídos dos segmentos delimitados no manifesto; a comparação foi por conteúdo, não por contagem de palavras.",
             "- Quebras de linha CRLF/CR foram normalizadas para LF; texto e blocos foram comparados após essa normalização estrutural.",
             "- Metadados em lista Markdown foram convertidos ao frontmatter YAML do README com valores preservados.",
             "- Gabaritos, soluções, rubricas, aceites e checklists só foram separados quando havia bloco correspondente na fonte.",
             "- Compartilhamentos têm um caminho físico em `90_integracao/`; o manifesto associa o item aos assuntos cobertos.",
            f"- Cobertura de origem: {builder.coverage_stats.get('caracteres_com_destino', 0)}/{builder.coverage_stats.get('caracteres_fonte', 0)} caracteres mapeados; apenas {builder.coverage_stats.get('cabecalhos_container_total', 0)} cabeçalhos contêiner ficaram sem arquivo de conteúdo, todos explicitamente listados no manifesto.",
             "- A unidade 8.4 não foi gerada.",
             "- Fases 1–5, fontes originais, backups e JSON foram comparados por SHA-256 e permanecem inalterados.",
             "- Nenhum commit ou execução do importador foi realizado.",
             "", "## Normalizações estruturais registradas", ""]
    for rule in builder.m.get("normalizacoes_estruturais_autorizadas", {}).get("links_markdown", []):
        rows.append(
            f"- {rule['unidade']}: `{rule['origem_literal']}` → `{rule['destino_literal']}` "
            f"({builder.normalization_counts.get(rule['unidade'], 0)}/{rule['ocorrencias_esperadas']} ocorrências); "
            f"destino comprovado `{rule['destino_comprovado']}`. Texto visível preservado."
        )
    rows += ["", "## Avisos", ""]
    rows.extend(f"- {warning}" for warning in warnings)
    validation_path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    audit = ["# Auditoria final — Fase 6", "", f"**Veredito:** {verdict}.",
             f"**Base:** `{BASE}`. **Arquivos:** {len(builder.outputs)}. **Mapeamentos:** {len(builder.records)}.",
             f"**Links Markdown relativos resolvidos:** {builder.link_stats.get('markdown_relativos_resolvidos', 0)}. **Normalizações de link:** {sum(builder.normalization_counts.values())} ({dict(builder.normalization_counts)}).",
             "", "## Contagens das fontes", "",
             "| Tipo | Encontrado |", "|---|---:|",
             *[f"| {k} | {v} |" for k, v in counts.items()],
             "", "## Resultado por unidade", "", "| Unidade | Assuntos | Arquivos | Mapeamentos | Tipo | Por tipo | Status |", "|---|---:|---:|---:|---|---|---|"]
    for uk, info in unit_results.items():
        audit.append(f"| {uk} | {info['assuntos'] if not info['projeto'] else 'projeto'} | {info['arquivos']} | {info['mapeamentos']} | {'projeto' if info['projeto'] else 'conteúdo'} | `{json.dumps(info['tipos'], ensure_ascii=False, sort_keys=True)}` | OK |")
    audit += ["", "## Normalizações estruturais permitidas", "",
              "- Lista de metadados da fonte convertida em YAML no README, com valores idênticos.",
              "- Quebras de linha CRLF/CR normalizadas para LF; nenhuma palavra ou formatação interna de código foi alterada por essa normalização.",
              "- Cabeçalhos contêineres (`Teoria`, `Quiz`, `Atividades`, `Flashcards` e `Entregas`) não duplicados; títulos internos e conteúdo foram mantidos.",
              "- Respostas inline de quiz separadas em gabaritos usando o marcador literal registrado para cada item.",
              "- Soluções e rubricas inline separadas pelos marcadores literais existentes.",
              "- Linhas de aceite dos marcos extraídas para arquivos `acceptance_criteria`; o restante do marco foi preservado sem sobreposição.",
              "- README contém somente metadados originais, links e índice estrutural derivados do manifesto.",
              f"- Auditoria por offsets: {builder.coverage_stats.get('caracteres_com_destino', 0)}/{builder.coverage_stats.get('caracteres_fonte', 0)} caracteres de origem mapeados; cabeçalhos contêiner não exportados: {builder.coverage_stats.get('cabecalhos_container', {})}.",
              *[
                  f"- Link relativo em {rule['unidade']}: `{rule['origem_literal']}` → `{rule['destino_literal']}`; "
                  f"{builder.normalization_counts.get(rule['unidade'], 0)} ocorrências; texto visível preservado."
                  for rule in builder.m.get("normalizacoes_estruturais_autorizadas", {}).get("links_markdown", [])
              ],
              "", "## Ressalvas", ""]
    audit.extend(f"- {warning}" for warning in warnings)
    audit += ["", "O CSV relaciona cada segmento de origem ao destino e inclui offsets e hash do texto de origem."]
    audit_path.write_text("\n".join(audit) + "\n", encoding="utf-8", newline="\n")


def apply_outputs(builder: Builder) -> None:
    root = ROOT / Path(*safe_rel(DEST_REL).parts)
    root.mkdir(parents=True, exist_ok=False)
    for rel, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        target = ROOT.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(norm(text), encoding="utf-8", newline="\n")
    actual = {
        p.relative_to(ROOT).as_posix(): read_text(p)
        for p in root.rglob("*") if p.is_file()
    }
    expected = {p.as_posix(): norm(text) for p, text in builder.outputs.items()}
    if set(actual) != set(expected):
        raise ValueError(f"inventário pós-geração diverge: ausentes={sorted(set(expected)-set(actual))}; extras={sorted(set(actual)-set(expected))}")
    diffs = [path for path in expected if actual[path] != expected[path]]
    if diffs:
        raise ValueError(f"conteúdo pós-geração diverge: {diffs[:20]}")


def apply_link_normalizations(builder: Builder) -> int:
    root = ROOT / Path(*safe_rel(DEST_REL).parts)
    expected = {path.as_posix(): norm(text) for path, text in builder.outputs.items()}
    actual = {p.relative_to(ROOT).as_posix(): read_text(p) for p in root.rglob("*") if p.is_file()}
    if set(actual) != set(expected):
        raise ValueError(f"árvore existente diverge em caminhos: ausentes={sorted(set(expected)-set(actual))}; extras={sorted(set(actual)-set(expected))}")
    changed: list[str] = []
    rules = builder.m.get("normalizacoes_estruturais_autorizadas", {}).get("links_markdown", [])
    for path_text, expected_text in expected.items():
        if actual[path_text] == expected_text:
            continue
        path = PurePosixPath(path_text)
        if path not in builder.normalization_paths:
            raise ValueError(f"diferença não autorizada em arquivo não relacionado a links: {path_text}")
        reverted = expected_text
        unit_key = builder.normalization_paths[path]
        for rule in rules:
            if rule["unidade"] == unit_key:
                reverted = reverted.replace(rule["destino_literal"], rule["origem_literal"])
        if reverted != actual[path_text]:
            raise ValueError(f"arquivo difere além da normalização aprovada: {path_text}")
        target = ROOT.joinpath(*path.parts)
        target.write_text(expected_text, encoding="utf-8", newline="\n")
        changed.append(path_text)
    return len(changed)


def compare_existing(builder: Builder) -> None:
    root = ROOT / Path(*safe_rel(DEST_REL).parts)
    if not root.is_dir():
        raise ValueError("árvore migrada Fase_6 ausente")
    actual = {p.relative_to(ROOT).as_posix(): read_text(p) for p in root.rglob("*") if p.is_file()}
    expected = {p.as_posix(): norm(text) for p, text in builder.outputs.items()}
    if set(actual) != set(expected):
        raise ValueError(f"inventário da árvore diverge: ausentes={sorted(set(expected)-set(actual))}; extras={sorted(set(actual)-set(expected))}")
    diff = [p for p in expected if actual[p] != expected[p]]
    if diff:
        raise ValueError(f"conteúdo persistido diverge em {diff[:20]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Migração estrutural rastreável da Fase 6")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--audit-existing", action="store_true")
    group.add_argument("--apply-link-normalizations", action="store_true")
    args = parser.parse_args()
    mode = "apply" if args.apply else "audit-existing" if args.audit_existing else "repair-links" if args.apply_link_normalizations else "dry-run"
    errors = git_preflight(mode)
    if errors:
        print("PREFLIGHT FAILED")
        for error in errors:
            print("- " + error)
        return 2
    manifest_path = ROOT / Path(*safe_rel(MANIFEST_REL).parts)
    manifest_bytes = manifest_path.read_bytes()
    # The legacy F1 parser only accepts a narrow YAML subset. F6's approved
    # manifest uses nested block sequences, so parse it with PyYAML while
    # rejecting duplicate mapping keys explicitly.
    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def construct_unique_mapping(loader, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"chave YAML duplicada no manifesto: {key!r}")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    UniqueKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
    )
    manifest = yaml.load(manifest_bytes.decode("utf-8-sig"), Loader=UniqueKeyLoader)
    validate_manifest(manifest)
    engine.manifest = manifest
    source_before = full_source_snapshot()
    prior_before = previous_tree_snapshot()
    ids_before = previous_ids()
    if len(ids_before) != 1556:
        raise ValueError("IDs das Fases 1–5 não reconciliam com os 1.556 arquivos")
    builder = Builder(manifest)
    builder.build()
    counts = audit_source_counts(builder)
    audit_errors, warnings, unit_results = audit_outputs(builder, ids_before)
    if audit_errors:
        print("PRE-WRITE AUDIT FAILED")
        for error in audit_errors:
            print("- " + error)
        return 3
    if len(builder.records) == 0:
        raise ValueError("nenhum bloco foi mapeado")
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("manifesto alterou durante a reconstrução")
    if mode == "dry-run":
        print(f"DRY-RUN OK | base={BASE} | unidades=20 | assuntos=57 | arquivos={len(builder.outputs)} | mapeamentos={len(builder.records)}")
        print("fontes=" + json.dumps(counts, ensure_ascii=False, sort_keys=True))
        print("tipos=" + json.dumps(dict(builder.type_counts()), ensure_ascii=False, sort_keys=True))
        print("Nenhum arquivo migrado ou relatório foi gravado.")
        return 0
    if args.apply:
        apply_outputs(builder)
        compare_existing(builder)
        verdict = "APROVADA COM RESSALVAS" if warnings else "APROVADA"
        write_reports(builder, counts, unit_results, warnings, verdict)
    elif args.apply_link_normalizations:
        changed = apply_link_normalizations(builder)
        compare_existing(builder)
        verdict = "APROVADA COM RESSALVAS" if warnings else "APROVADA"
        write_reports(builder, counts, unit_results, warnings, verdict)
        print(f"normalizações aplicadas somente em {changed} arquivo(s) autorizados")
    else:
        compare_existing(builder)
        for rel in REPORTS:
            if not (ROOT / Path(*safe_rel(rel).parts)).is_file():
                raise ValueError(f"relatório ausente para auditoria: {rel}")
        verdict = "APROVADA COM RESSALVAS" if warnings else "APROVADA"
        write_reports(builder, counts, unit_results, warnings, verdict)
    if source_before != full_source_snapshot():
        raise ValueError("fonte original, backup, guia ou JSON foi alterado")
    if prior_before != previous_tree_snapshot():
        raise ValueError("uma das Fases 1–5 mudou durante a migração")
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("manifesto mudou durante a geração/auditoria")
    print(f"MIGRATION {'OK' if args.apply or args.apply_link_normalizations else 'AUDIT OK'} | files={len(builder.outputs)} | mappings={len(builder.records)}")
    print("per_unit=" + json.dumps(unit_results, ensure_ascii=False, sort_keys=True))
    if args.apply or args.apply_link_normalizations:
        print("reports=" + ", ".join(REPORTS))
        print("No commit, importador, JSON, fonte original ou Fase 7 foi alterado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
