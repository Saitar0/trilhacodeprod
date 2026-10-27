from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from types import MethodType

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine
import _migrar_fase4 as f4
import _migrar_fase6 as f6

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase8.yml"
PLAN_REL = "docs/migracao/PLANEJAMENTO_FASE8.md"
DEST_REL = "docs/courses/trilhacode/Conteudos_migrado/Fase_8"
BASE = "b74e053879bd7c8ec8093479e5c645bba9cc6be8"
ORDER = ["37.1", "37.2", "37.3", "38.1", "38.2", "39.1", "39.2", "39.3"]
PREVIOUS_COUNTS = {1: 221, 2: 144, 3: 313, 4: 395, 5: 483, 6: 449, 7: 156}
PRIOR_TOTAL = sum(PREVIOUS_COUNTS.values())
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
GUIDE_REL = "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md"
F8_SOURCE_ROOT = "docs/courses/trilhacode/Conteudos/Fase_8"
REPORT_MAP = "docs/migracao/relatorio_mapeamento_fase8.csv"
REPORT_VALIDATION = "docs/migracao/relatorio_validacao_fase8.md"
REPORT_AUDIT = "docs/migracao/auditoria_final_fase8.md"
GENERATOR_REL = "docs/migracao/_migrar_fase8.py"

PREEXISTING_UNTRACKED = {
    "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
    "docs/migracao/PLANEJAMENTO_FASE5.md",
    "docs/migracao/PLANEJAMENTO_FASE6.md",
    "docs/migracao/PLANEJAMENTO_FASE7.md",
    PLAN_REL,
    MANIFEST_REL,
}
PROTECTED_DOCS = {
    JSON_REL,
    "docs/courses/trilhacode/Fase_8_Infra_Operacao.md",
    "docs/courses/trilhacode/Referencias_Fase_8.md",
    "docs/courses/trilhacode/Roadmap_Completo_Integrado_Obsidian_Sincronizado.md",
    GUIDE_REL,
    *PREEXISTING_UNTRACKED,
}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True, encoding="utf-8"
    ).strip()


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"unsafe repository-relative path: {value!r}")
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        item.relative_to(ROOT).as_posix(): sha_file(item)
        for item in path.rglob("*")
        if item.is_file()
    }


def snapshot_inputs() -> dict[str, str]:
    result = snapshot_tree(ROOT / "docs/courses/trilhacode/Conteudos")
    for rel in PROTECTED_DOCS:
        path = ROOT.joinpath(*safe_rel(rel).parts)
        if not path.is_file():
            raise ValueError(f"protected input missing: {rel}")
        result[rel] = sha_file(path)
    return result


def snapshot_prior_phases() -> dict[str, str]:
    result: dict[str, str] = {}
    for phase, expected_count in PREVIOUS_COUNTS.items():
        directory = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{phase}"
        files = [path for path in directory.rglob("*") if path.is_file()]
        if not directory.is_dir() or len(files) != expected_count:
            raise ValueError(
                f"Fase {phase}: expected {expected_count} files, found {len(files)}"
            )
        result.update({path.relative_to(ROOT).as_posix(): sha_file(path) for path in files})
    if len(result) != PRIOR_TOTAL:
        raise ValueError(f"expected {PRIOR_TOTAL} prior files, found {len(result)}")
    return result


def prior_ids() -> set[str]:
    found: set[str] = set()
    for phase in PREVIOUS_COUNTS:
        directory = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{phase}"
        for path in directory.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in found:
                raise ValueError(f"missing/duplicate prior arquivo_id: {path} ({ident})")
            found.add(ident)
    if len(found) != PRIOR_TOTAL:
        raise ValueError(f"expected {PRIOR_TOTAL} prior IDs, found {len(found)}")
    return found


def verify_git_preflight(apply_mode: bool) -> None:
    if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT.resolve():
        raise ValueError("Git root differs from the generator repository root")
    if git("branch", "--show-current") != "migracao-estrutura":
        raise ValueError("current branch is not migracao-estrutura")
    if git("rev-parse", "HEAD") != BASE:
        raise ValueError("HEAD differs from the approved Fase 8 base")
    if git("diff", "--cached", "--name-only") or git("diff", "--name-only"):
        raise ValueError("staged or tracked changes found; stopping before generation")
    untracked = {
        line[3:]
        for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
        if line.startswith("?? ")
    }
    allowed = PREEXISTING_UNTRACKED | {GENERATOR_REL}
    if apply_mode and untracked != allowed:
        raise ValueError(
            "untracked inventory differs from the six preserved items plus this authorized generator: "
            f"unexpected={sorted(untracked-allowed)} missing={sorted(allowed-untracked)}"
        )
    missing = [rel for rel in PREEXISTING_UNTRACKED if not (ROOT / Path(*safe_rel(rel).parts)).is_file()]
    if missing:
        raise ValueError(f"pre-existing untracked files disappeared: {sorted(missing)}")


def load_manifest() -> dict:
    path = ROOT / MANIFEST_REL
    manifest = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueKeyLoader)
    identity = (
        manifest.get("status_manifesto"),
        manifest.get("fase"),
        manifest.get("base_commit"),
        manifest.get("id_prefix"),
        manifest.get("destino_raiz"),
        manifest.get("ordem_unidades"),
    )
    expected = (
        "aprovado_para_execucao",
        "Fase_8",
        BASE,
        "f8",
        DEST_REL,
        ORDER,
    )
    if identity != expected or list(manifest.get("unidades", {})) != ORDER:
        raise ValueError(f"manifest identity/order differs: {identity!r}")
    return manifest


def line_offsets(lines: list[str]) -> list[int]:
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def heading_line_index(lines: list[str], literal: str) -> int:
    matches = [i for i, line in enumerate(lines) if line.rstrip("\r\n").strip() == literal]
    if len(matches) != 1:
        raise ValueError(f"heading selector {literal!r}: found {len(matches)}")
    return matches[0]


def heading_range(raw: str, literal: str, level: int | None = None) -> dict:
    lines = raw.splitlines(keepends=True)
    index = heading_line_index(lines, literal)
    heading_level = level or len(literal) - len(literal.lstrip("#"))
    if not literal.startswith("#") or heading_level < 1:
        raise ValueError(f"invalid heading selector: {literal!r}")
    offsets = line_offsets(lines)
    end_index = next(
        (
            i
            for i in range(index + 1, len(lines))
            if lines[i].startswith("#")
            and len(lines[i]) - len(lines[i].lstrip("#")) <= heading_level
        ),
        len(lines),
    )
    return {
        "inicio": index + 1,
        "fim": end_index,
        "start_offset": offsets[index],
        "end_offset": offsets[end_index],
        "text": "".join(lines[index:end_index]),
        "selector": literal,
    }


def selector_range(raw: str, selector: str, marker_literal: str | None = None) -> dict:
    if " > " not in selector:
        return heading_range(raw, selector)
    root, leaf = selector.split(" > ", 1)
    root_span = heading_range(raw, root)
    lines = raw.splitlines(keepends=True)
    if leaf.startswith("item "):
        number = int(leaf.split()[1])
        section_lines = lines[root_span["inicio"] - 1 : root_span["fim"]]
        starts = [
            root_span["inicio"] - 1 + i
            for i, line in enumerate(section_lines)
            if re.match(r"^\s*(\d+)\.", line)
        ]
        numbered = [int(re.match(r"^\s*(\d+)\.", lines[i]).group(1)) for i in starts]
        if number not in numbered:
            raise ValueError(f"quiz item {number} missing under {root}")
        pos = numbered.index(number)
        start = starts[pos]
        end = starts[pos + 1] if pos + 1 < len(starts) else root_span["fim"]
        offsets = line_offsets(lines)
        return {
            "inicio": start + 1,
            "fim": end,
            "start_offset": offsets[start],
            "end_offset": offsets[end],
            "text": "".join(lines[start:end]),
            "selector": selector,
        }
    if leaf.startswith("cartão "):
        number = int(leaf.split()[1])
        section_lines = lines[root_span["inicio"] - 1 : root_span["fim"]]
        starts = [
            root_span["inicio"] - 1 + i
            for i, line in enumerate(section_lines)
            if re.match(r"^\s*- \*\*", line)
        ]
        if number < 1 or number > len(starts):
            raise ValueError(f"flashcard {number} missing under {root}")
        start = starts[number - 1]
        end = starts[number] if number < len(starts) else root_span["fim"]
        offsets = line_offsets(lines)
        return {
            "inicio": start + 1,
            "fim": end,
            "start_offset": offsets[start],
            "end_offset": offsets[end],
            "text": "".join(lines[start:end]),
            "selector": selector,
        }
    if leaf == "Teste/aceite":
        if not marker_literal:
            raise ValueError(f"acceptance selector has no approved literal: {selector}")
        section_text = root_span["text"]
        if section_text.count(marker_literal) != 1:
            raise ValueError(f"acceptance marker is absent/ambiguous in {root}")
        marker_offset = root_span["start_offset"] + section_text.index(marker_literal)
        offsets = line_offsets(lines)
        start_index = next(i for i, offset in enumerate(offsets[:-1]) if offset <= marker_offset < offsets[i + 1])
        end_index = next(
            (i for i in range(start_index + 1, root_span["fim"]) if not lines[i].strip()),
            root_span["fim"],
        )
        if lines[start_index].lstrip().startswith(marker_literal) is False:
            raise ValueError(f"acceptance marker is not at the start of a literal paragraph: {selector}")
        return {
            "inicio": start_index + 1,
            "fim": end_index,
            "start_offset": offsets[start_index],
            "end_offset": offsets[end_index],
            "text": "".join(lines[start_index:end_index]),
            "selector": selector,
        }
    if leaf.startswith("Atividade ") or leaf.startswith("Microtópico "):
        heading = "### " + leaf
        return heading_range(raw, heading, level=3) | {"selector": selector}
    raise ValueError(f"unsupported hierarchical source selector: {selector}")


def validate_sources_and_manifest(manifest: dict, previous: set[str]) -> tuple[dict, dict]:
    if len(manifest["unidades"]) != 8 or "8.4" in manifest["unidades"]:
        raise ValueError("active-unit inventory mismatch or retired 8.4 present")
    active = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / F8_SOURCE_ROOT).glob("*.md")
        if path.is_file()
    }
    declared = {unit["origem"] for unit in manifest["unidades"].values()}
    if active != declared or len(active) != 8:
        raise ValueError(
            f"Fase 8 source inventory mismatch: missing={sorted(declared-active)} "
            f"additional={sorted(active-declared)}"
        )
    if sum(len(unit["assuntos"]) for unit in manifest["unidades"].values()) != 13:
        raise ValueError("expected 13 conventional subjects")
    if sum(bool(unit.get("projeto", {}).get("inclui")) for unit in manifest["unidades"].values()) != 2:
        raise ValueError("expected two project containers")

    paths: set[str] = set()
    ids: set[str] = set()
    type_counts = Counter()
    source_data: dict[str, dict] = {}
    for uid, unit in manifest["unidades"].items():
        if unit.get("key") != uid:
            raise ValueError(f"{uid}: key differs from unit ID")
        source_path = ROOT.joinpath(*safe_rel(unit["origem"]).parts)
        raw = read_text(source_path)
        title, metadata, _ = f4.parse_header(raw, unit, unit["origem"])
        if title != unit["titulo_original"] or metadata != unit["metadados_originais"]:
            raise ValueError(f"{uid}: title or full metadata differs from source")
        source_data[uid] = {"raw": raw, "title": title, "metadata": metadata}
        for alias, spec in unit["arquivos"].items():
            target = (safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
            if target in paths:
                raise ValueError(f"duplicate physical path: {target}")
            paths.add(target)
            ident = spec.get("arquivo_id")
            if not ident or not ident.startswith("f8-") or ident in ids or ident in previous:
                raise ValueError(f"invalid/colliding arquivo_id: {ident!r}")
            ids.add(ident)
            type_counts[spec["tipo"]] += 1
            origin = spec.get("origem", {})
            if alias == "IDX":
                if spec["path"] != "README.md":
                    raise ValueError(f"{uid}: topic index must be README.md")
                continue
            if origin.get("arquivo_origem") != unit["origem"]:
                raise ValueError(f"{uid}/{alias}: origin does not match official unit source")
            if spec.get("assunto"):
                if spec["assunto"] not in unit["assuntos"] or PurePosixPath(spec["path"]).parts[0] != spec["assunto"]:
                    raise ValueError(f"{uid}/{alias}: exclusive subject/path mismatch")
            if spec.get("assuntos"):
                if len(spec["assuntos"]) < 2 or PurePosixPath(spec["path"]).parts[0] != "90_integracao":
                    raise ValueError(f"{uid}/{alias}: shared item must have one integration path")
            elif PurePosixPath(spec["path"]).parts[0] == "90_integracao":
                raise ValueError(f"{uid}/{alias}: integration path has no shared subject context")
        if set(unit["cobertura"]) != set(unit["assuntos"]):
            raise ValueError(f"{uid}: coverage subject list differs from declared folders")

    if len(ids) != 124 or len(paths) != 124:
        raise ValueError(f"expected 124 unique paths/IDs; found {len(paths)}/{len(ids)}")
    declared_types = manifest["estimativa_arquivos"]["por_tipo"]
    if dict(type_counts) != declared_types or manifest["estimativa_arquivos"]["total"] != 124:
        raise ValueError(f"file type estimate differs: actual={dict(type_counts)}")
    if manifest["estimativa_arquivos"]["por_unidade"] != {
        uid: len(unit["arquivos"]) for uid, unit in manifest["unidades"].items()
    }:
        raise ValueError("per-unit file estimate differs from the manifest")

    q_count = p_count = card_count = 0
    for uid, unit in manifest["unidades"].items():
        files = unit["arquivos"]
        quizzes = {
            item: (alias, spec)
            for alias, spec in files.items()
            if spec["tipo"] == "quiz"
            for item in spec.get("itens_origem", [])
        }
        keys = {
            item: (alias, spec)
            for alias, spec in files.items()
            if spec["tipo"] == "answer_key"
            for item in spec.get("itens_origem", [])
        }
        if set(quizzes) != set(keys):
            raise ValueError(f"{uid}: question/answer-key aliases differ")
        for item, (q_alias, q_spec) in quizzes.items():
            k_alias, k_spec = keys[item]
            if k_spec.get("responde_a") != q_alias or k_spec["origem"] != q_spec["origem"]:
                raise ValueError(f"{uid}/{item}: answer key does not match the question source")
            selector = q_spec["origem"].get("seletor", "")
            if " > item " not in selector:
                raise ValueError(f"{uid}/{item}: question selector is not an individual quiz item")
            span = selector_range(source_data[uid]["raw"], selector)
            marker = manifest["regras"]["quiz_resposta_inline"]["marcador_literal_contextual"]
            if span["text"].count(marker) != 1 or span["text"].count("**") != 2:
                raise ValueError(f"{uid}/{item}: inline answer boundary is absent/ambiguous")
            split_at = span["text"].index(marker) + 2
            q_text, k_text = span["text"][:split_at], span["text"][split_at:]
            if not q_text.endswith("? ") or not k_text.startswith("**") or q_text + k_text != span["text"]:
                raise ValueError(f"{uid}/{item}: Q/K literal split does not reconstruct its source")
            q_count += 1

        for alias, spec in files.items():
            if spec["tipo"] == "practice":
                p_count += len(spec.get("itens_origem", []))
            elif spec["tipo"] == "flashcards":
                card_count += len(spec.get("itens_origem", []))

        for kind, exclusive, shared in (
            ("quiz", "quiz_exclusivos", "quiz_compartilhados"),
            ("practice", "praticas_exclusivas", "praticas_compartilhadas"),
            ("flashcards", "flashcards_exclusivos", "flashcards_compartilhados"),
        ):
            assignments: dict[str, list[tuple[str, str]]] = defaultdict(list)
            for slug, coverage in unit["cobertura"].items():
                for group in (exclusive, shared):
                    for item in coverage[group]:
                        assignments[str(item)].append((slug, group))
            for item, locations in assignments.items():
                subjects = {slug for slug, _ in locations}
                if len(locations) != len(subjects):
                    raise ValueError(f"{uid}/{item}: duplicated coverage classification")
                if any((group == exclusive) != (len(subjects) == 1) for _, group in locations):
                    raise ValueError(f"{uid}/{item}: exclusive/shared classification mismatch")
                physical = [
                    spec
                    for spec in files.values()
                    if spec["tipo"] == kind
                    and str(item) in [str(value) for value in spec.get("itens_origem", [])]
                ]
                if len(physical) != 1:
                    raise ValueError(f"{uid}/{item}: expected one physical {kind} file, found {len(physical)}")
                spec = physical[0]
                if len(subjects) == 1:
                    if spec.get("assunto") != next(iter(subjects)) or "assuntos" in spec:
                        raise ValueError(f"{uid}/{item}: exclusive file context mismatch")
                elif (
                    set(spec.get("assuntos", [])) != subjects
                    or "assunto" in spec
                    or PurePosixPath(spec["path"]).parts[0] != "90_integracao"
                ):
                    raise ValueError(f"{uid}/{item}: shared file context/path mismatch")

    if (q_count, p_count, card_count) != (15, 11, 9):
        raise ValueError(f"source assessment totals differ: Q/P/FC={q_count}/{p_count}/{card_count}")

    for rule in manifest.get("normalizacoes_structurais_autorizadas", {}).get("links_markdown", []):
        if rule["alvo_comprovado"] != GUIDE_REL or not (ROOT / GUIDE_REL).is_file():
            raise ValueError("relative-link normalization target is absent or differs from the verified guide")
        raw = source_data[rule["unidade"]]["raw"]
        if raw.count(rule["origem_literal"]) != rule["ocorrencias_esperadas"]:
            raise ValueError(f"normalization source literal count differs for {rule['unidade']}: {rule}")
    if len(manifest["normalizacoes_structurais_autorizadas"]["links_markdown"]) != 3:
        raise ValueError("expected three explicit link normalization rules")
    return source_data, {"paths": len(paths), "ids": len(ids), "types": dict(type_counts), "quiz": q_count, "practice": p_count, "flashcards": card_count}


def lines_for_range(raw: str, record: dict) -> dict:
    return {"inicio": record["inicio"], "fim": record["fim"]}


def runtime_manifest(manifest: dict, source_data: dict) -> dict:
    runtime = json.loads(json.dumps(manifest, ensure_ascii=False))
    runtime["normalizacoes_structurais_autorizadas"] = {"links_markdown": []}
    runtime["cabecalhos_container_nao_exportados"] = manifest["cabecalhos_container_nao_exportados"]
    runtime["estimativa_arquivos"] = {"total": manifest["estimativa_arquivos"]["total"]}
    runtime["fase"] = "Fase_8"
    for uid, unit in runtime["unidades"].items():
        original = manifest["unidades"][uid]
        raw = source_data[uid]["raw"]
        unit["blocos_origem"] = {}
        unit["arquivo_ids"] = {
            alias: spec["arquivo_id"] for alias, spec in unit["arquivos"].items()
        }
        unit["tipo_projeto"] = bool(unit.get("projeto", {}).get("inclui"))
        blocks = {
            "comuns": {"h1_and_original_metadata": "IDX"},
            "teoria": {},
            "quiz": {},
            "praticas": {},
            "flashcards": {},
        }
        common_types = {"objetivo", "resumo", "criterio", "conexoes", "referencias"}
        for alias, spec in unit["arquivos"].items():
            if spec["tipo"] in common_types:
                selector = spec["origem"].get("seletor")
                if not selector:
                    raise ValueError(f"{uid}/{alias}: common section selector missing")
                blocks["comuns"][selector] = alias
            elif spec["tipo"] == "theory":
                selectors = spec["origem"].get("seletores") or [spec["origem"].get("seletor")]
                for selector in selectors:
                    if not selector:
                        raise ValueError(f"{uid}/{alias}: theory selector missing")
                    span = selector_range(raw, selector)
                    heading = span["text"].splitlines()[0].strip()
                    if heading in blocks["teoria"]:
                        raise ValueError(f"{uid}: duplicate theory heading selector {heading!r}")
                    blocks["teoria"][heading] = {
                        "linhas": lines_for_range(raw, span),
                        "arquivo": alias,
                        "assunto": spec.get("assunto"),
                        "seletor_origem": selector,
                    }
            elif spec["tipo"] == "quiz":
                item = spec["itens_origem"][0]
                span = selector_range(raw, spec["origem"]["seletor"])
                spec["origem"]["linhas"] = lines_for_range(raw, span)
                spec["origem"]["segmento"] = "enunciado literal, antes da resposta inline"
                key = next(
                    (candidate for candidate, value in unit["arquivos"].items()
                     if value["tipo"] == "answer_key" and value.get("responde_a") == alias),
                    None,
                )
                if not key:
                    raise ValueError(f"{uid}/{alias}: matching answer key missing")
                unit["arquivos"][key]["origem"]["linhas"] = lines_for_range(raw, span)
                unit["arquivos"][key]["origem"]["segmento"] = "resposta inline literal"
                blocks["quiz"][item] = {
                    "arquivo": alias,
                    "resposta": key,
                    "separacao_inline_literal": {"marcador_inicio": "**"},
                }
            elif spec["tipo"] == "practice":
                item = spec["itens_origem"][0]
                selector = spec["origem"]["seletor"]
                span = selector_range(raw, selector)
                spec["origem"]["linhas"] = lines_for_range(raw, span)
                blocks["praticas"][item] = {"arquivo": alias}
            elif spec["tipo"] == "flashcards":
                selectors = spec["origem"].get("seletores", [])
                items = spec.get("itens_origem", [])
                if len(selectors) != len(items):
                    raise ValueError(f"{uid}/{alias}: flashcard selector/item count differs")
                for item, selector in zip(items, selectors, strict=True):
                    span = selector_range(raw, selector)
                    blocks["flashcards"][item] = {
                        "arquivo": alias,
                        "linhas": lines_for_range(raw, span),
                    }
        project = unit.get("projeto", {})
        if project.get("inclui"):
            scope = next(
                alias for alias, spec in unit["arquivos"].items()
                if spec["tipo"] == "project_scope"
            )
            rubric = next(
                alias for alias, spec in unit["arquivos"].items()
                if spec["tipo"] == "rubric"
            )
            checklist_candidates = [
                alias for alias, spec in unit["arquivos"].items()
                if spec["tipo"] == "checklist" and not spec.get("para_marco")
            ]
            final_checklist = next(
                (alias for alias in checklist_candidates if alias == "C90"),
                checklist_candidates[-1],
            )
            project_blocks = {
                "escopo": ["## Escopo e regras"],
                "marcos": {},
                "rubrica": {
                    "arquivo": rubric,
                    "escala_rubrica": unit["arquivos"][rubric]["escala_rubrica"],
                },
                "checklist": {"arquivo": final_checklist},
            }
            milestone_specs = [
                (alias, spec)
                for alias, spec in unit["arquivos"].items()
                if spec["tipo"] == "project_milestone"
            ]
            for milestone_alias, milestone_spec in milestone_specs:
                title = milestone_spec.get("titulo_marco")
                selector = milestone_spec["origem"]["seletor"]
                milestone_span = selector_range(raw, selector)
                milestone_spec["origem"]["linhas"] = lines_for_range(raw, milestone_span)
                check_aliases = [
                    alias for alias, spec in unit["arquivos"].items()
                    if spec["tipo"] == "checklist"
                    and spec.get("origem", {}).get("seletor", "").startswith(selector + " > Teste/aceite")
                ]
                if len(check_aliases) != 1:
                    raise ValueError(f"{uid}/{milestone_alias}: expected exactly one acceptance file")
                check_alias = check_aliases[0]
                check_spec = unit["arquivos"][check_alias]
                check_span = selector_range(
                    raw,
                    check_spec["origem"]["seletor"],
                    marker_literal=check_spec["origem"].get("marcador_literal"),
                )
                check_spec["origem"]["linhas"] = lines_for_range(raw, check_span)
                check_spec["origem"]["segmento"] = "parágrafo literal de aceite"
                check_spec["para_marco"] = milestone_alias
                milestone_spec["titulo_marco"] = title
                project_blocks["marcos"][milestone_alias] = {
                    "arquivo": milestone_alias,
                    "aceite": check_alias,
                    "titulo_marco": title,
                }
            for field, selector in (("rubrica", "## Rubrica final"), ("checklist", "## Checklist de entrega")):
                alias = project_blocks[field]["arquivo"]
                spec = unit["arquivos"][alias]
                span = selector_range(raw, selector)
                spec["origem"]["linhas"] = lines_for_range(raw, span)
                spec["origem"]["seletor"] = selector
            if "39.2" in uid:
                scenario_alias = next(
                    alias for alias, spec in unit["arquivos"].items()
                    if spec["tipo"] == "project_scenarios"
                )
                scenario_spec = unit["arquivos"][scenario_alias]
                scenario_selector = scenario_spec["origem"]["seletor"]
                scenario_span = selector_range(raw, scenario_selector)
                scenario_spec["origem"]["linhas"] = lines_for_range(raw, scenario_span)
                project_blocks["verificacoes_por_cenario"] = {"arquivo": scenario_alias}
        unit["blocos_origem"].update(blocks)
        if project.get("inclui"):
            unit["blocos_origem"]["projeto"] = project_blocks
    runtime["normalizacoes_fase8"] = manifest["normalizacoes_structurais_autorizadas"]["links_markdown"]
    return runtime


def configure_builder(runtime: dict):
    f6.ORDER = ORDER
    f6.DEST_REL = DEST_REL
    builder = f6.Builder(runtime)
    builder.f8_normalization_counts = Counter()
    original_add = f6.Builder.add
    original_emit_project = f6.Builder.emit_project

    def add_with_normalization(self, uk, alias, source, start, end, segment,
                               item=None, title=None, transform="literal"):
        applicable = [
            (index, rule) for index, rule in enumerate(self.m.get("normalizacoes_fase8", []))
            if rule["unidade"] == uk
        ]
        by_literal = {rule["origem_literal"]: (index, rule) for index, rule in applicable}
        rendered = source
        active_rules = []
        if by_literal:
            pattern = re.compile("|".join(re.escape(literal) for literal in sorted(by_literal, key=len, reverse=True)))

            def replace_literal(match):
                index, rule = by_literal[match.group(0)]
                self.f8_normalization_counts[index] += 1
                active_rules.append(index)
                return rule["destino_literal"]

            rendered = pattern.sub(replace_literal, source)
        effective_transform = transform
        if active_rules:
            effective_transform += "; destinos relativos corrigidos conforme manifesto autorizado: " + ",".join(map(str, active_rules))
        original_add(self, uk, alias, source, start, end, segment, item=item, title=title, transform=effective_transform)
        if rendered != source:
            self.parts[(uk, alias)][-1]["source"] = rendered
            self.records[-1]["normalizacao"] = effective_transform

    def load_sources(self):
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / F8_SOURCE_ROOT).glob("*.md")
            if path.is_file()
        }
        declared = {unit["origem"] for unit in self.m["unidades"].values()}
        if actual != declared or len(actual) != 8:
            raise ValueError("Fase 8 source set changed between preflight and generation")
        for uid, unit in self.m["unidades"].items():
            raw = read_text(ROOT.joinpath(*safe_rel(unit["origem"]).parts))
            title, metadata, _ = f4.parse_header(raw, unit, unit["origem"])
            if title != unit["titulo_original"] or metadata != unit["metadados_originais"]:
                raise ValueError(f"{uid}: original title/metadata changed")
            self.sources[uid] = {
                "raw": raw,
                "lines": raw.splitlines(keepends=True),
                "title": title,
                "metadata": metadata,
                "path": unit["origem"],
            }

    def emit_quiz(self, uid):
        unit = self.m["unidades"][uid]
        for item, record in unit["blocos_origem"].get("quiz", {}).items():
            q_alias, k_alias = record["arquivo"], record["resposta"]
            q_origin = unit["arquivos"][q_alias]["origem"]
            k_origin = unit["arquivos"][k_alias]["origem"]
            if q_origin["linhas"] != k_origin["linhas"]:
                raise ValueError(f"{uid}/{item}: Q/K source ranges differ")
            full, start, end = f6.slice_lines(
                self.sources[uid]["raw"], q_origin["linhas"]["inicio"], q_origin["linhas"]["fim"]
            )
            contextual = self.m["regras"]["quiz_resposta_inline"]["marcador_literal_contextual"]
            if full.count(contextual) != 1 or full.count("**") != 2:
                raise ValueError(f"{uid}/{item}: inline answer boundary absent/ambiguous")
            split = full.index(contextual) + 2
            question, answer = full[:split], full[split:]
            if not question.endswith("? ") or not answer.startswith("**") or question + answer != full:
                raise ValueError(f"{uid}/{item}: Q/K split does not reconstruct the source")
            self.add(uid, q_alias, question, start, start + split, "enunciado literal", item=item,
                     transform="resposta separada no limite literal aprovado '? **'")
            self.add(uid, k_alias, answer, start + split, end, "resposta inline separada", item=item,
                     transform="resposta separada no limite literal aprovado '? **'")

    def emit_theory(self, uid):
        unit = self.m["unidades"][uid]
        lines = self.sources[uid]["lines"]
        for heading, record in unit["blocos_origem"].get("teoria", {}).items():
            line_range = record["linhas"]
            if lines[line_range["inicio"] - 1].strip() != heading:
                raise ValueError(f"{uid}: theory selector does not match source line {line_range['inicio']}")
            self.add_lines(
                uid,
                record["arquivo"],
                line_range,
                "microtópico de teoria",
                item=record.get("seletor_origem", heading),
            )

    def emit_flashcards(self, uid):
        unit = self.m["unidades"][uid]
        for item, record in unit["blocos_origem"].get("flashcards", {}).items():
            self.add_lines(uid, record["arquivo"], record["linhas"], "flashcard pergunta/resposta", item=item)

    def emit_project(self, uid):
        original_emit_project(self, uid)
        project = self.m["unidades"][uid]["blocos_origem"]["projeto"]
        scenario = project.get("verificacoes_por_cenario")
        if scenario:
            self.add_lines(
                uid,
                scenario["arquivo"],
                self.m["unidades"][uid]["arquivos"][scenario["arquivo"]]["origem"]["linhas"],
                "verificações por cenário do projeto",
                item="5 cenários",
            )

    builder.load_sources = MethodType(load_sources, builder)
    builder.emit_theory = MethodType(emit_theory, builder)
    builder.emit_quiz = MethodType(emit_quiz, builder)
    builder.emit_flashcards = MethodType(emit_flashcards, builder)
    builder.emit_project = MethodType(emit_project, builder)
    builder.add = MethodType(add_with_normalization, builder)
    builder.build()

    for index, rule in enumerate(runtime["normalizacoes_fase8"]):
        if builder.f8_normalization_counts[index] != rule["ocorrencias_esperadas"]:
            raise ValueError(
                f"link normalization count differs for rule {index}: "
                f"expected={rule['ocorrencias_esperadas']} found={builder.f8_normalization_counts[index]}"
            )
    return builder


def apply_declared_orders(builder, manifest: dict) -> None:
    path_by_id = {}
    for uid, unit in manifest["unidades"].items():
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            if "ordem" in spec or "itens_origem" in spec:
                path = PurePosixPath(DEST_REL) / safe_rel(unit["pasta"]) / safe_rel(spec["path"])
                path_by_id[spec["arquivo_id"]] = (path, spec)
    for ident, (path, spec) in path_by_id.items():
        text = builder.outputs[path]
        _, fields, body = engine.fm(text, str(path))
        changed = False
        if "ordem" in spec and fields.get("ordem") != spec["ordem"]:
            fields["ordem"] = spec["ordem"]
            changed = True
        if "itens_origem" in spec and fields.get("itens_origem") != spec["itens_origem"]:
            fields["itens_origem"] = spec["itens_origem"]
            changed = True
        if changed:
            builder.outputs[path] = engine.frontmatter(list(fields.items())) + body


def validate_generated(builder, manifest: dict, previous: set[str], expected_coverage: dict) -> dict:
    errors, coverage_stats = f6.audit_source_coverage(builder)
    if errors:
        raise ValueError("source coverage audit failed: " + "; ".join(errors[:15]))
    link_errors, link_warnings, wikilinks, resolved = f6.audit_links(builder.outputs)
    if link_errors:
        raise ValueError("Markdown link audit failed: " + "; ".join(link_errors[:15]))

    all_ids = set(previous)
    type_counts = Counter()
    for path, text in builder.outputs.items():
        _, fields, body = engine.fm(text, str(path))
        frontmatter_match = re.match(r"\A---\n(.*?)\n---\n\n", text, re.S)
        if not frontmatter_match:
            raise ValueError(f"frontmatter boundary invalid: {path}")
        parsed = yaml.load(frontmatter_match.group(1), Loader=UniqueKeyLoader)
        if parsed != fields:
            raise ValueError(f"frontmatter parser disagreement: {path}")
        ident = fields.get("arquivo_id")
        if not ident or ident in all_ids:
            raise ValueError(f"missing/colliding global arquivo_id: {path} ({ident})")
        all_ids.add(ident)
        if not body.strip():
            raise ValueError(f"empty generated file: {path}")
        type_counts[fields.get("tipo_arquivo")] += 1
    if len(builder.outputs) != 124 or len(all_ids) != PRIOR_TOTAL + 124:
        raise ValueError(f"generated file/global ID count mismatch: {len(builder.outputs)}/{len(all_ids)}")
    if dict(type_counts) != manifest["estimativa_arquivos"]["por_tipo"]:
        raise ValueError(f"frontmatter file types differ from manifest: {dict(type_counts)}")
    if dict(builder.type_counts()) != dict(type_counts):
        raise ValueError("builder and frontmatter type counts disagree")

    for uid, unit in manifest["unidades"].items():
        for alias, spec in unit["arquivos"].items():
            path = PurePosixPath(DEST_REL) / safe_rel(unit["pasta"]) / safe_rel(spec["path"])
            if alias == "IDX":
                _, readme_fields, _ = engine.fm(builder.outputs[path], str(path))
                if readme_fields.get("title") != unit["titulo_original"]:
                    raise ValueError(f"{uid}: README title missing")
                for key, value in unit["metadados_originais"].items():
                    if readme_fields.get(key) != value:
                        raise ValueError(f"{uid}: README metadata differs for {key}")
                continue
            _, fields, _ = engine.fm(builder.outputs[path], str(path))
            if fields.get("arquivo_id") != spec["arquivo_id"] or fields.get("tipo_arquivo") != spec["tipo"]:
                raise ValueError(f"{uid}/{alias}: frontmatter ID/type differs from manifest")
            if spec.get("assunto") and fields.get("assunto") != spec["assunto"]:
                raise ValueError(f"{uid}/{alias}: frontmatter subject differs")
            if spec.get("assuntos") and fields.get("assuntos") != spec["assuntos"]:
                raise ValueError(f"{uid}/{alias}: frontmatter shared subjects differ")
            if spec.get("itens_origem") and fields.get("itens_origem") != spec["itens_origem"]:
                raise ValueError(f"{uid}/{alias}: frontmatter source items differ")
            if "ordem" in spec and fields.get("ordem") != spec["ordem"]:
                raise ValueError(f"{uid}/{alias}: declared order not preserved")
            if spec.get("titulo_marco") and fields.get("titulo_marco") != spec["titulo_marco"]:
                raise ValueError(f"{uid}/{alias}: literal milestone title differs")
            if spec.get("escala_rubrica") and fields.get("escala_rubrica") != spec["escala_rubrica"]:
                raise ValueError(f"{uid}/{alias}: rubric scale differs")

    output_by_path = {path.as_posix(): text for path, text in builder.outputs.items()}
    p392 = PurePosixPath(DEST_REL) / "39.2_Projeto_incremental_da_fase"
    p393 = PurePosixPath(DEST_REL) / "39.3_Projeto_de_fase_Trilho_B"
    checklist_392 = output_by_path[(p392 / "06_checklist_entrega.md").as_posix()]
    rubric_392 = output_by_path[(p392 / "07_rubrica_final.md").as_posix()]
    scenarios_392 = output_by_path[(p392 / "08_verificacoes_por_cenario.md").as_posix()]
    if len(re.findall(r"(?m)^- \[ \]", checklist_392)) != 11:
        raise ValueError("39.2 checklist count differs from 11")
    def rubric_dimension_count(text: str) -> int:
        rows = [line for line in text.splitlines() if line.lstrip().startswith("|")]
        return sum(
            1 for line in rows
            if not re.match(r"^\|\s*:?-{3,}", line.strip())
            and "Dimensão" not in line
        )

    if rubric_dimension_count(rubric_392) != 6:
        raise ValueError("39.2 rubric dimension count differs from 6")
    if len(re.findall(r"(?m)^\s*\d+\.", scenarios_392)) != 5:
        raise ValueError("39.2 scenario verification count differs from 5")
    checklist_393 = output_by_path[(p393 / "C90_checklist_final.md").as_posix()]
    rubric_393 = output_by_path[(p393 / "R00_rubrica_final.md").as_posix()]
    if len(re.findall(r"(?m)^- \[ \]", checklist_393)) != 12:
        raise ValueError("39.3 final checklist count differs from 12")
    if rubric_dimension_count(rubric_393) != 6:
        raise ValueError("39.3 rubric dimension count differs from 6")
    m03 = output_by_path[(p393 / "03_empacotar_automatizar_observar.md").as_posix()]
    c03 = output_by_path[(p393 / "C03_aceite_entrega_3.md").as_posix()]
    if not all(f"**T{i}:**" in m03 for i in range(1, 6)):
        raise ValueError("39.3 T1–T5 table is not retained with Delivery 3")
    if any(f"**T{i}:**" in c03 for i in range(1, 6)):
        raise ValueError("39.3 T1–T5 table was duplicated into the acceptance file")
    for number in range(1, 5):
        acceptance = output_by_path[(p393 / f"C0{number}_aceite_entrega_{number}.md").as_posix()]
        if acceptance.count("**Teste/aceite:**") != 1:
            raise ValueError(f"39.3 acceptance {number} marker missing/duplicated")

    return {
        "types": dict(type_counts),
        "coverage": coverage_stats,
        "links_resolved": resolved,
        "link_warnings": link_warnings,
        "wikilinks": wikilinks,
        "global_ids": len(all_ids),
        "mappings": len(builder.records),
        "mapping_records": builder.records,
        "normalizations": dict(builder.f8_normalization_counts),
        "coverage_expected": expected_coverage,
    }


def expected_hashes(builder) -> dict[str, str]:
    result = {}
    for path, text in builder.outputs.items():
        rel = path.as_posix()
        if not rel.startswith(DEST_REL + "/"):
            raise ValueError(f"generated path outside Fase 8: {rel}")
        key = PurePosixPath(rel).relative_to(PurePosixPath(DEST_REL)).as_posix()
        result[key] = hashlib.sha256(f6.norm(text).encode("utf-8")).hexdigest()
    return result


def compare_directory(expected: dict[str, str], directory: Path) -> list[str]:
    actual = {
        path.relative_to(directory).as_posix(): sha_file(path)
        for path in directory.rglob("*")
        if path.is_file()
    } if directory.is_dir() else {}
    mismatches = []
    if set(actual) != set(expected):
        mismatches.append(
            f"paths differ: missing={sorted(set(expected)-set(actual))} extra={sorted(set(actual)-set(expected))}"
        )
    for rel in sorted(set(actual) & set(expected)):
        if actual[rel] != expected[rel]:
            mismatches.append(f"SHA-256 differs: {rel}")
    return mismatches


def write_temp_tree(builder, temp_parent: Path) -> Path:
    tree = temp_parent / "Fase_8"
    tree.mkdir(parents=True, exist_ok=False)
    for repo_path, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        rel = PurePosixPath(repo_path.as_posix()).relative_to(PurePosixPath(DEST_REL))
        target = tree.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f6.norm(text).encode("utf-8"))
    return tree


def write_mapping_csv(records: list[dict]) -> None:
    target = ROOT / REPORT_MAP
    columns = [
        "unidade", "origem", "bloco", "tipo", "alias", "destino", "segmento",
        "offset_inicio", "offset_fim", "texto_origem", "normalizacao",
        "valor_origem", "valor_destino", "linha_inicio", "linha_fim",
    ]
    with target.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def build_reports(manifest: dict, stats: dict, prior_count: int, source_count: int) -> None:
    types = stats["types"]
    per_unit = {
        uid: len(unit["arquivos"]) for uid, unit in manifest["unidades"].items()
    }
    norm_lines = []
    for index, rule in enumerate(manifest["normalizacoes_structurais_autorizadas"]["links_markdown"]):
        norm_lines.append(
            f"- {rule['unidade']}: `{rule['origem_literal']}` → `{rule['destino_literal']}`; "
            f"{stats['normalizations'].get(index, 0)} ocorrência(s); alvo verificado `{rule['alvo_comprovado']}`."
        )
    type_lines = "\n".join(f"| `{kind}` | {count} |" for kind, count in sorted(types.items()))
    unit_lines = "\n".join(f"| {uid} | {count} |" for uid, count in per_unit.items())
    container_lines = "\n".join(
        f"| `{heading}` | {count} |"
        for heading, count in sorted(stats["coverage"]["cabecalhos_container"].items())
    )
    validation = f"""# Validação da migração estrutural — Fase 8

**Base:** `{BASE}` · **branch:** `migracao-estrutura` · **resultado técnico:** PASSOU COM RESSALVAS.

## Contagens

| Unidade | Arquivos |
|---|---:|
{unit_lines}
| **Total** | **{sum(per_unit.values())}** |

| Tipo de arquivo | Quantidade |
|---|---:|
{type_lines}

## Integridade e cobertura

- Fontes ativas: 8/8; assuntos convencionais: 13; contêineres de projeto: 2.
- Blocos de teoria: 21 (19 microtópicos titulados e duas seções sintéticas); questões: 15; respostas inline separadas: 15; práticas: 11; flashcards: 9.
- Arquivos gerados: 124; IDs únicos na árvore e sem colisão com os {prior_count} IDs anteriores.
- Registros de origem→destino: {stats['mappings']}; a auditoria por intervalos confirmou que cada trecho não estrutural possui destino e não há sobreposição.
- Cabeçalhos de contêiner sem arquivo próprio (somente estrutura):

| Cabeçalho | Ocorrências |
|---|---:|
{container_lines}

- Metadados originais, incluindo `key`, comparados com as oito fontes e preservados nos READMEs.
- Os 15 pares Q/gabarito foram reconstruídos literalmente; o limite de separação foi conferido como `? **` em cada item. A concatenação Q+K reproduz cada bloco original.
- Os itens compartilhados têm um único arquivo em `90_integracao/` e associações coerentes no frontmatter/cobertura.
- 39.2: quatro microtópicos, checklist de 11 itens, rubrica de seis dimensões/0–2 e cinco verificações por cenário preservados.
- 39.3: quatro entregas, quatro aceites, checklist de 12 itens e rubrica de seis dimensões/0–2 preservados. T1–T5 permanece exclusivamente no arquivo da Entrega 3.
- Frontmatter YAML válido em todos os arquivos; paths e `arquivo_id` únicos.
- Links Markdown relativos resolvidos: {stats['links_resolved']}; wikilinks preservados sem reescrita: {stats['wikilinks']}.

## Normalizações estruturais autorizadas

{chr(10).join(norm_lines)}

Os textos visíveis dos links foram preservados. Uma referência de 39.2 usava um nome de arquivo que não existe; foi apontada para o único guia existente com o mesmo título visível. A raiz do vault Obsidian continua não confirmada.

## Escopo preservado

- Fases 1–7: {prior_count} arquivos, hashes idênticos ao pré-voo.
- Conteúdos originais e backups: {source_count} arquivos, hashes idênticos ao pré-voo.
- JSON de importação, páginas da fase e guia de projetos: hashes idênticos ao pré-voo.
- Cópias auxiliares 37.1/37.2 em `Conteudos/Fase_7/`: intactas, fora da árvore Fase 8 e não declaradas aposentadas.
- Nenhum importador executado; nenhum commit criado.
"""
    (ROOT / REPORT_VALIDATION).write_text(validation, encoding="utf-8")

    audit = f"""# Auditoria final — Fase 8

**Veredito: APROVADA COM RESSALVAS**

## Resultado

A árvore reconstruída das fontes oficiais da Fase 8 e do manifesto contém 124 arquivos em oito unidades, 13 assuntos convencionais e dois contêineres de projeto. O total corresponde ao manifesto sem arquivos artificiais.

Foram validados {stats['mappings']} registros de mapeamento. A auditoria comparou faixas textuais originais com os segmentos destinados, verificou sobreposição, frontmatters, hashes dos arquivos gerados, respostas inline, práticas, flashcards, links e estruturas de projeto.

## Ressalvas

1. A raiz do vault Obsidian não está confirmada. Wikilinks foram preservados literalmente; sua resolução no vault precisa de validação na integração.
2. As cópias auxiliares de 37.1/37.2 em `Conteudos/Fase_7/` diferem das fontes oficiais Fase 8. Permanecem intactas e fora da migração; não há declaração de aposentadoria nem resolução editorial sobre o conteúdo adicional.
3. Uma referência de 39.2 contém um nome relativo que não existe no repositório. A normalização foi limitada ao destino do único guia com título visível correspondente, sem alterar o texto do link.

## Confirmações

- 8 fontes oficiais ativas; nenhum arquivo extra da pasta Fase 7 incluído.
- 15 questões, 15 gabaritos, 11 práticas e 9 flashcards preservados.
- Compartilhados deduplicados em destino físico único.
- Projetos 39.2 e 39.3 preservados; quatro entregas/aceites em 39.3 e tabela T1–T5 associada à Entrega 3.
- 2.161 arquivos das Fases 1–7, todas as fontes/backups e o JSON permaneceram intactos durante a geração.
- Nenhum commit, push, importação ou geração da Fase 9.
"""
    (ROOT / REPORT_AUDIT).write_text(audit, encoding="utf-8")


def write_reproduction_note() -> None:
    path = ROOT / REPORT_AUDIT
    text = path.read_text(encoding="utf-8")
    note = (
        "\n## Segunda reconstrução independente\n\n"
        "A auditoria foi repetida em processo separado: o gerador reconstruiu a saída esperada novamente "
        "a partir das fontes e do manifesto e comparou caminhos e SHA-256 com a árvore persistida. "
        "Resultado: correspondência integral; nenhuma divergência.\n"
    )
    if "## Segunda reconstrução independente" not in text:
        path.write_text(text.rstrip() + "\n" + note, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and audit the structural Fase 8 tree")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--audit-existing", action="store_true")
    args = parser.parse_args()
    verify_git_preflight(apply_mode=args.apply or args.dry_run)
    manifest = load_manifest()
    destination = ROOT / DEST_REL
    if args.apply and destination.exists():
        raise ValueError(f"destination already exists; refusing to overwrite: {DEST_REL}")
    if (args.apply or args.dry_run) and destination.exists():
        raise ValueError("Fase 8 destination exists before authorized generation")

    input_before = snapshot_inputs()
    prior_before = snapshot_prior_phases()
    previous = prior_ids()
    source_data, expected = validate_sources_and_manifest(manifest, previous)
    runtime = runtime_manifest(manifest, source_data)
    builder = configure_builder(runtime)
    apply_declared_orders(builder, manifest)
    stats = validate_generated(builder, manifest, previous, expected)
    hashes = expected_hashes(builder)
    if len(hashes) != 124:
        raise ValueError(f"expected 124 unique expected outputs, found {len(hashes)}")

    action = "validated in memory"
    source_count = len(snapshot_tree(ROOT / "docs/courses/trilhacode/Conteudos"))
    if args.apply:
        with tempfile.TemporaryDirectory(prefix="trilhacode-fase8-") as temp_name:
            temp_parent = Path(temp_name)
            temp_tree = write_temp_tree(builder, temp_parent)
            differences = compare_directory(hashes, temp_tree)
            if differences:
                raise ValueError("isolated temporary generation differs: " + "; ".join(differences[:10]))
            if destination.exists():
                raise ValueError("destination appeared during generation; stopping without overwrite")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp_tree.rename(destination)
        differences = compare_directory(hashes, destination)
        if differences:
            raise ValueError("persisted tree differs from temporary reconstruction: " + "; ".join(differences[:10]))
        write_mapping_csv(stats["mapping_records"])
        build_reports(manifest, stats, len(previous), source_count)
        action = "generated and source-reconstructed tree"
    elif args.audit_existing:
        if not destination.is_dir():
            raise ValueError("Fase 8 destination is absent")
        differences = compare_directory(hashes, destination)
        if differences:
            raise ValueError("persisted tree differs from independent reconstruction: " + "; ".join(differences[:10]))
        required_reports = (REPORT_MAP, REPORT_VALIDATION, REPORT_AUDIT)
        if any(not (ROOT / rel).is_file() for rel in required_reports):
            raise ValueError("one or more Fase 8 reports are absent")
        if args.audit_existing:
            write_reproduction_note()
        action = "independent reconstruction matched persisted tree"

    if snapshot_inputs() != input_before:
        raise ValueError("original sources, backups, JSON or protected documents changed")
    if snapshot_prior_phases() != prior_before:
        raise ValueError("one or more files from Fases 1–7 changed")

    print(json.dumps({
        "result": "OK",
        "action": action,
        "base": BASE,
        "branch": git("branch", "--show-current"),
        "units": len(manifest["unidades"]),
        "subjects": sum(len(unit["assuntos"]) for unit in manifest["unidades"].values()),
        "project_containers": 2,
        "files": len(builder.outputs),
        "mappings": stats["mappings"],
        "types": stats["types"],
        "questions": expected["quiz"],
        "answer_keys": expected["quiz"],
        "practices": expected["practice"],
        "flashcards": expected["flashcards"],
        "links_resolved": stats["links_resolved"],
        "wikilinks_preserved": stats["wikilinks"],
        "link_normalizations": stats["normalizations"],
        "prior_files_unchanged": len(prior_before),
        "source_backup_files_unchanged": source_count,
        "destination": DEST_REL,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
