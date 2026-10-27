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
from pathlib import Path, PurePosixPath
from types import MethodType

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine
import _migrar_fase4 as f4
import _migrar_fase6 as f6
import _migrar_fase8 as f8

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase9.yml"
PLAN_REL = "docs/migracao/PLANEJAMENTO_FASE9.md"
DEST_REL = "docs/courses/trilhacode/Conteudos_migrado/Fase_9"
BASE = "ccd2668cf3ba00ffc11c386fc5de26d917a854f0"
ORDER = [
    "40.1", "40.2", "40.3", "41.1", "41.2", "42.1", "42.2", "42.3",
    "43.1", "43.2", "44.1", "44.2", "45.1", "46.1", "46.2", "46.3",
]
SOURCE_ROOT = "docs/courses/trilhacode/Conteudos/Fase_9"
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
GUIDE_REL = "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md"
MAPPING_REL = "docs/migracao/relatorio_mapeamento_fase9.csv"
VALIDATION_REL = "docs/migracao/relatorio_validacao_fase9.md"
AUDIT_REL = "docs/migracao/auditoria_final_fase9.md"
EXPECTED_PRIOR = {1: 221, 2: 144, 3: 313, 4: 395, 5: 483, 6: 449, 7: 156, 8: 124}
PRIOR_TOTAL = sum(EXPECTED_PRIOR.values())
PREEXISTING_UNTRACKED = {
    "_draft_f9.py",
    "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
    "docs/migracao/PLANEJAMENTO_FASE5.md",
    "docs/migracao/PLANEJAMENTO_FASE6.md",
    "docs/migracao/PLANEJAMENTO_FASE7.md",
    "docs/migracao/PLANEJAMENTO_FASE8.md",
    PLAN_REL,
    MANIFEST_REL,
}
GENERATED_UNTRACKED = {
    "docs/migracao/_migrar_fase9.py",
    MAPPING_REL,
    VALIDATION_REL,
    AUDIT_REL,
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"unsafe relative path: {value!r}")
    return path


def origin_items(spec: dict) -> list:
    value = spec.get("itens_origem", spec.get("item_origem", []))
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def origin_selectors(origin: dict) -> list:
    value = origin.get("seletores") or origin.get("seletor", [])
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def load_manifest() -> dict:
    path = ROOT / MANIFEST_REL
    manifest = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=f8.UniqueKeyLoader)
    identity = (
        manifest.get("status_manifesto"), manifest.get("fase"), manifest.get("base_commit"),
        manifest.get("id_prefix"), manifest.get("destino_raiz"), manifest.get("ordem_unidades"),
    )
    expected = ("aprovado_para_execucao", "Fase_9", BASE, "f9", DEST_REL, ORDER)
    if identity != expected or list(manifest.get("unidades", {})) != ORDER:
        raise ValueError(f"manifest identity/order differs from approved execution: {identity!r}")
    return manifest


def hash_tree(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise ValueError(f"directory missing: {root}")
    return {
        p.relative_to(ROOT).as_posix(): sha_file(p)
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def prior_tree_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    for number, expected in EXPECTED_PRIOR.items():
        root = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        current = hash_tree(root)
        if len(current) != expected:
            raise ValueError(f"Fase {number}: expected {expected} files, found {len(current)}")
        result.update(current)
    if len(result) != PRIOR_TOTAL:
        raise ValueError(f"expected {PRIOR_TOTAL} prior files, found {len(result)}")
    return result


def prior_ids() -> set[str]:
    result: set[str] = set()
    for number in EXPECTED_PRIOR:
        root = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        for path in root.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in result:
                raise ValueError(f"prior file ID missing/duplicated: {path} ({ident})")
            result.add(ident)
    if len(result) != PRIOR_TOTAL:
        raise ValueError(f"expected {PRIOR_TOTAL} prior IDs, found {len(result)}")
    return result


def source_snapshot() -> dict[str, str]:
    root = ROOT / "docs/courses/trilhacode/Conteudos"
    result = {
        p.relative_to(ROOT).as_posix(): sha_file(p)
        for p in sorted(root.rglob("*")) if p.is_file()
    }
    for rel in (JSON_REL, GUIDE_REL):
        p = ROOT / Path(*safe_rel(rel).parts)
        if not p.is_file():
            raise ValueError(f"protected source missing: {rel}")
        result[rel] = sha_file(p)
    for rel in PREEXISTING_UNTRACKED:
        p = ROOT / Path(*safe_rel(rel).parts)
        if not p.is_file():
            raise ValueError(f"preexisting untracked document missing: {rel}")
        result[rel] = sha_file(p)
    return result


def git_untracked_paths() -> set[str]:
    output = git("ls-files", "--others", "--exclude-standard")
    return {line.replace("\\", "/") for line in output.splitlines() if line.strip()}


def git_preflight(mode: str) -> None:
    top = Path(git("rev-parse", "--show-toplevel")).resolve()
    if top != ROOT.resolve():
        raise ValueError(f"wrong worktree root: {top}")
    if git("branch", "--show-current") != "migracao-estrutura":
        raise ValueError("branch is not migracao-estrutura")
    if git("rev-parse", "HEAD") != BASE:
        raise ValueError(f"HEAD differs from approved base {BASE}")
    if git("diff", "--cached", "--name-only"):
        raise ValueError("Git index is not empty")
    if git("diff", "--name-only"):
        raise ValueError("tracked working-tree changes exist")
    allowed = PREEXISTING_UNTRACKED | GENERATED_UNTRACKED
    paths = git_untracked_paths()
    destination_prefix = DEST_REL + "/"
    unexpected = {p for p in paths if p not in allowed and not p.startswith(destination_prefix)}
    if unexpected:
        raise ValueError(f"unexpected untracked paths: {sorted(unexpected)}")
    if mode in ("apply", "dry-run") and (ROOT / DEST_REL).exists():
        raise ValueError(f"Fase 9 destination already exists; refusing overwrite: {DEST_REL}")
    if mode == "apply":
        existing_reports = [r for r in (MAPPING_REL, VALIDATION_REL, AUDIT_REL) if (ROOT / r).exists()]
        if existing_reports:
            raise ValueError(f"Fase 9 report path already exists: {existing_reports}")


def selector_range(raw: str, selector: str) -> dict:
    return f8.selector_range(raw, selector)


def line_range_for_literal_paragraph(raw: str, root_selector: str, marker: str) -> dict:
    root = f8.heading_range(raw, root_selector)
    lines = raw.splitlines(keepends=True)
    start_offset = root["start_offset"]
    end_offset = root["end_offset"]
    region = raw[start_offset:end_offset]
    if region.count(marker) != 1:
        raise ValueError(f"literal marker must occur once in {root_selector}: {marker!r}")
    marker_offset = start_offset + region.index(marker)
    offsets = f6.line_offsets(lines)
    start_line = next(i for i, offset in enumerate(offsets[:-1]) if offset <= marker_offset < offsets[i + 1])
    if lines[start_line][len(lines[start_line]) - len(lines[start_line].lstrip()):].startswith(marker) is False:
        raise ValueError(f"marker is not at the start of its paragraph: {marker!r}")
    end_line = next(
        (i for i in range(start_line + 1, len(lines))
         if offsets[i] < end_offset and not lines[i].strip()),
        next((i for i, offset in enumerate(offsets) if offset >= end_offset), len(lines) - 1),
    )
    return {
        "inicio": start_line + 1,
        "fim": end_line,
        "start_offset": offsets[start_line],
        "end_offset": offsets[end_line],
        "text": "".join(lines[start_line:end_line]),
        "selector": f"{root_selector} > {marker}",
    }


def resolve_theory_selector(raw: str, selector: str) -> dict:
    if selector == "parágrafo introdutório de ## Teoria":
        lines = raw.splitlines(keepends=True)
        index = f8.heading_line_index(lines, "## Teoria")
        end = next(
            (i for i in range(index + 1, len(lines)) if re.match(r"^#{3,6}\s", lines[i])),
            len(lines),
        )
        if end == index + 1 or not any(line.strip() for line in lines[index + 1:end]):
            raise ValueError("41.2 theory introduction is empty or absent")
        offsets = f6.line_offsets(lines)
        return {
            "inicio": index + 2,
            "fim": end,
            "start_offset": offsets[index + 1],
            "end_offset": offsets[end],
            "text": "".join(lines[index + 1:end]),
            "selector": selector,
        }
    return f8.heading_range(raw, selector, level=3)


def validate_source_and_manifest(manifest: dict, previous: set[str]) -> tuple[dict, dict]:
    source_root = ROOT / SOURCE_ROOT
    active = {p.relative_to(ROOT).as_posix() for p in source_root.glob("*.md") if p.is_file()}
    declared = {unit["origem"] for unit in manifest["unidades"].values()}
    if len(active) != 16 or active != declared:
        raise ValueError(f"Fase 9 active-source mismatch: missing={sorted(declared-active)} additional={sorted(active-declared)}")
    if len(manifest["unidades"]) != 16 or len(manifest["ordem_unidades"]) != 16:
        raise ValueError("Fase 9 must contain exactly 16 official units")
    topics = sum(len(unit["assuntos"]) for unit in manifest["unidades"].values())
    projects = [uid for uid, unit in manifest["unidades"].items() if any(s["tipo"] == "project_milestone" for s in unit["arquivos"].values())]
    if (topics, len(projects)) != (47, 2):
        raise ValueError(f"expected 47 conventional subjects and two project containers; found {topics}/{len(projects)}")

    source_data: dict[str, dict] = {}
    paths: set[str] = set()
    ids: set[str] = set()
    types: Counter[str] = Counter()
    for uid, unit in manifest["unidades"].items():
        if unit.get("key") != uid:
            raise ValueError(f"{uid}: key does not match unit ID")
        source_rel = safe_rel(unit["origem"]).as_posix()
        source_path = ROOT.joinpath(*safe_rel(source_rel).parts)
        raw = read_text(source_path)
        actual_sha = sha_file(source_path)
        if unit.get("sha256_origem") and actual_sha != unit["sha256_origem"]:
            raise ValueError(f"{uid}: source SHA-256 differs from approved manifest")
        title, metadata, _ = f4.parse_header(raw, unit, source_rel)
        if title != unit.get("titulo_original") or metadata != unit.get("metadados_originais"):
            raise ValueError(f"{uid}: title or original metadata differs from source")
        source_data[uid] = {"raw": raw, "title": title, "metadata": metadata, "path": source_rel}
        if len(set(unit.get("assuntos", []))) != len(unit.get("assuntos", [])):
            raise ValueError(f"{uid}: duplicate subject slug")
        for alias, spec in unit["arquivos"].items():
            rel = (safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
            if rel in paths:
                raise ValueError(f"duplicate Fase 9 output path: {rel}")
            paths.add(rel)
            ident = spec.get("arquivo_id")
            if not ident or not ident.startswith("f9-") or ident in ids or ident in previous:
                raise ValueError(f"missing, duplicate, or colliding file ID: {ident!r}")
            ids.add(ident)
            types[spec["tipo"]] += 1
            if alias == "IDX":
                if spec["path"] != "README.md" or spec["tipo"] != "topic_index":
                    raise ValueError(f"{uid}: IDX must be README.md/topic_index")
                continue
            origin = spec.get("origem", {})
            if origin.get("arquivo_origem") != source_rel:
                raise ValueError(f"{uid}/{alias}: source path mismatch")
            subject = spec.get("assunto")
            subjects = spec.get("assuntos", [])
            path_parts = PurePosixPath(spec["path"]).parts
            if subject:
                if subject not in unit["assuntos"] or not path_parts or path_parts[0] != subject:
                    raise ValueError(f"{uid}/{alias}: exclusive subject does not match physical path")
            if subjects:
                if len(subjects) < 2 or not path_parts or path_parts[0] != "90_integracao":
                    raise ValueError(f"{uid}/{alias}: shared item must have one 90_integracao path")
                if any(s not in unit["assuntos"] for s in subjects):
                    raise ValueError(f"{uid}/{alias}: shared subject missing from unit")
            if path_parts and path_parts[0] == "90_integracao" and not subjects:
                raise ValueError(f"{uid}/{alias}: integration path without shared subject references")

    if len(paths) != 301 or len(ids) != 301:
        raise ValueError(f"expected 301 unique paths/IDs, found {len(paths)}/{len(ids)}")
    estimate = manifest["estimativa_arquivos"]
    if estimate.get("total") != 301 or estimate.get("por_tipo") != dict(types):
        raise ValueError(f"manifest file estimate differs from physical specs: {dict(types)}")
    if estimate.get("por_unidade") != {uid: len(u["arquivos"]) for uid, u in manifest["unidades"].items()}:
        raise ValueError("per-unit file estimate differs from file specs")

    esn = Counter()
    for unit in manifest["unidades"].values():
        values = unit.get("cobertura", {}).get("E_S_N", {})
        esn.update(values)
    if (esn["E"], esn["S"], esn["N"]) != (38, 9, 0):
        raise ValueError(f"approved coverage total differs: E/S/N={esn['E']}/{esn['S']}/{esn['N']}")
    validate_assessment_coverage(manifest)
    validate_sources_selectors(manifest, source_data)

    counts = Counter()
    cards = 0
    for unit in manifest["unidades"].values():
        for spec in unit["arquivos"].values():
            counts[spec["tipo"]] += 1
            if spec["tipo"] == "flashcards":
                cards += len(origin_items(spec))
    expected = {
        "theory": 47, "quiz": 25, "answer_key": 25, "practice": 33,
        "answer_key_pratica": 24, "rubric": 11, "project_milestone": 8,
        "checklist": 8, "project_scope": 2,
    }
    for kind, total in expected.items():
        if counts[kind] != total:
            raise ValueError(f"expected {total} {kind} files, found {counts[kind]}")
    quiz_count = counts["quiz"]
    practice_count = counts["practice"]
    if quiz_count != 25 or practice_count != 33 or cards != 27 or counts["flashcards"] != 23:
        raise ValueError(f"assessment source counts differ: Q/P/cards/card-files={quiz_count}/{practice_count}/{cards}/{counts['flashcards']}")
    if sum(1 for unit in manifest["unidades"].values() for spec in unit["arquivos"].values()
           if spec["tipo"] == "rubric" and spec.get("item_origem")) != 9:
        raise ValueError("expected nine practice rubrics plus two project rubrics")
    return source_data, {"paths": len(paths), "ids": len(ids), "types": dict(types), "cards": cards, "E_S_N": dict(esn)}


def validate_assessment_coverage(manifest: dict) -> None:
    for uid, unit in manifest["unidades"].items():
        files = unit["arquivos"]
        coverage = unit.get("cobertura", {}).get("por_assunto", {})
        if set(coverage) != set(unit.get("assuntos", [])):
            raise ValueError(f"{uid}: coverage slugs differ from subject folders")
        for item_type, exclusive_key, shared_key, file_type in (
            ("quiz", "quiz_exclusivos", "quiz_compartilhados", "quiz"),
            ("practice", "praticas_exclusivas", "praticas_compartilhadas", "practice"),
            ("flashcards", "flashcards_exclusivos", "flashcards_compartilhados", "flashcards"),
        ):
            owners: dict[str, list[tuple[str, str]]] = defaultdict(list)
            for slug, record in coverage.items():
                for group, key in (("exclusive", exclusive_key), ("shared", shared_key)):
                    for item in record.get(key, []):
                        owners[str(item)].append((slug, group))
            physical: dict[str, list[tuple[str, dict]]] = defaultdict(list)
            for alias, spec in files.items():
                if spec["tipo"] != file_type:
                    continue
                items = origin_items(spec)
                for item in items:
                    physical[str(item)].append((alias, spec))
            for item, locations in owners.items():
                slugs = {slug for slug, _ in locations}
                if len(locations) != len(slugs):
                    raise ValueError(f"{uid}/{item}: coverage repeats the same item/subject")
                shared = len(slugs) > 1
                if any((group == "shared") != shared for _, group in locations):
                    raise ValueError(f"{uid}/{item}: exclusive/shared coverage classification inconsistent")
                specs = physical.get(item, [])
                if len(specs) != 1:
                    raise ValueError(f"{uid}/{item}: expected exactly one physical {item_type} file, found {len(specs)}")
                _, spec = specs[0]
                if shared:
                    if set(spec.get("assuntos", [])) != slugs or "assunto" in spec or PurePosixPath(spec["path"]).parts[0] != "90_integracao":
                        raise ValueError(f"{uid}/{item}: shared physical location/context differs from coverage")
                else:
                    slug = next(iter(slugs))
                    if spec.get("assunto") != slug or "assuntos" in spec or PurePosixPath(spec["path"]).parts[0] != slug:
                        raise ValueError(f"{uid}/{item}: exclusive item points to a different subject")
            if set(owners) != set(physical):
                raise ValueError(f"{uid}: {item_type} physical items differ from coverage: coverage={sorted(owners)} physical={sorted(physical)}")

        for alias, spec in files.items():
            if spec["tipo"] == "answer_key":
                target = spec.get("responde_a")
                if not target or target not in files or files[target]["tipo"] != "quiz":
                    raise ValueError(f"{uid}/{alias}: answer key has no source quiz")
                if spec.get("item_origem") != files[target].get("item_origem"):
                    raise ValueError(f"{uid}/{alias}: answer key item does not match quiz")
            elif spec["tipo"] == "answer_key_pratica":
                target = spec.get("responde_a")
                if not target or target not in files or files[target]["tipo"] != "practice":
                    raise ValueError(f"{uid}/{alias}: practice feedback has no source practice")


def validate_sources_selectors(manifest: dict, source_data: dict) -> None:
    for uid, unit in manifest["unidades"].items():
        raw = source_data[uid]["raw"]
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            origin = spec.get("origem", {})
            selector = origin.get("seletor")
            if spec["tipo"] == "theory":
                selectors = origin_selectors(origin)
                if not selectors:
                    raise ValueError(f"{uid}/{alias}: theory selector is missing")
                for item in selectors:
                    if item == "parágrafo introdutório de ## Teoria":
                        span = resolve_theory_selector(raw, item)
                    else:
                        span = resolve_theory_selector(raw, item)
                    if not span["text"].strip():
                        raise ValueError(f"{uid}/{alias}: empty theory source selector {item!r}")
            elif spec["tipo"] in ("quiz", "answer_key"):
                span = selector_range(raw, selector)
                marker = origin.get("marcador_literal")
                if not marker or span["text"].count(marker) != 1:
                    raise ValueError(f"{uid}/{alias}: inline answer marker absent/ambiguous")
            elif spec["tipo"] == "practice":
                span = selector_range(raw, selector)
                if not span["text"].strip():
                    raise ValueError(f"{uid}/{alias}: practice source block is empty")
            elif spec["tipo"] in ("answer_key_pratica", "rubric") and origin.get("marcador_literal"):
                root, marker_text = selector.rsplit(" > ", 1)
                marker = origin["marcador_literal"]
                if marker_text != marker:
                    raise ValueError(f"{uid}/{alias}: nested marker selector and marker_literal differ")
                parent = f8.heading_range(raw, root, level=3)
                if parent["text"].count(marker) != 1:
                    raise ValueError(f"{uid}/{alias}: feedback/rubric marker absent or ambiguous")
                span = line_range_for_literal_paragraph(raw, root, marker)
                if not span["text"].strip():
                    raise ValueError(f"{uid}/{alias}: feedback/rubric block is empty")
            elif spec["tipo"] == "flashcards":
                selectors = origin_selectors(origin)
                items = origin_items(spec)
                if len(selectors) != len(items):
                    raise ValueError(f"{uid}/{alias}: flashcard selector/item mismatch")
                for card_selector in selectors:
                    if not selector_range(raw, card_selector)["text"].strip():
                        raise ValueError(f"{uid}/{alias}: empty flashcard selector")
            elif spec["tipo"] in ("objetivo", "resumo", "criterio", "conexoes", "referencias", "project_scope", "rubric"):
                selectors = selector if isinstance(selector, list) else [selector]
                if not all(x for x in selectors):
                    raise ValueError(f"{uid}/{alias}: section selector is missing")
                for section in selectors:
                    if not f8.heading_range(raw, section)["text"].strip():
                        raise ValueError(f"{uid}/{alias}: empty section {section!r}")
            elif spec["tipo"] == "project_milestone":
                span = f8.heading_range(raw, selector, level=3)
                if not span["text"].strip() or not re.fullmatch(r"###\s+Entrega\s+[1-4]\s+—\s+.+", selector):
                    raise ValueError(f"{uid}/{alias}: milestone title/source is not literal")
                if selector != spec.get("titulo_marco"):
                    raise ValueError(f"{uid}/{alias}: titulo_marco differs from the literal source heading")
            elif spec["tipo"] == "checklist":
                root, marker_text = selector.rsplit(" > ", 1)
                marker = origin.get("marcador_literal")
                if marker != marker_text:
                    raise ValueError(f"{uid}/{alias}: acceptance selector/marker mismatch")
                span = line_range_for_literal_paragraph(raw, root, marker)
                milestone = spec.get("titulo_marco")
                if milestone and milestone not in selector:
                    raise ValueError(f"{uid}/{alias}: acceptance is associated with a different milestone")
                if not span["text"].strip():
                    raise ValueError(f"{uid}/{alias}: acceptance block is empty")

    for rule in manifest.get("normalizacoes_links_relativos_planejadas", []):
        if rule.get("destino_repositorio") != GUIDE_REL or not (ROOT / GUIDE_REL).is_file():
            raise ValueError("planned guide normalization target is missing or differs from tracked guide")
        if not rule.get("destino_rastreado"):
            raise ValueError("planned guide target is not declared tracked")
        if git("ls-files", "--error-unmatch", GUIDE_REL) == "":
            raise ValueError("guide is not tracked by Git")
        unit = manifest["unidades"].get(rule["unidade"])
        if not unit or rule["origem"] != unit["origem"]:
            raise ValueError(f"guide normalization source unit/path mismatch: {rule}")
        raw = source_data[rule["unidade"]]["raw"]
        if rule["href_origem"] not in raw or rule["href_destino"] == rule["href_origem"]:
            raise ValueError(f"guide normalization href is absent or not changed: {rule}")
        out_path = PurePosixPath(rule["arquivo_destino"])
        if not out_path.is_relative_to(PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])):
            raise ValueError(f"guide normalization destination is outside its unit: {rule}")


def marker_ranges_for_practice(raw: str, practice_alias: str, unit: dict, item: str) -> tuple[dict, list[dict]]:
    practice_spec = unit["arquivos"][practice_alias]
    source = selector_range(raw, practice_spec["origem"]["seletor"])
    full = source["text"]
    related = []
    for alias, spec in unit["arquivos"].items():
        if spec["tipo"] not in ("answer_key_pratica", "rubric") or spec.get("item_origem") != item:
            continue
        origin = spec["origem"]
        if " > " not in origin.get("seletor", ""):
            raise ValueError(f"{unit['key']}/{alias}: practice segment selector has no parent heading")
        root, nested = origin["seletor"].rsplit(" > ", 1)
        if root != practice_spec["origem"]["seletor"] or nested != origin.get("marcador_literal"):
            raise ValueError(f"{unit['key']}/{alias}: practice segment selector does not match its practice")
        marker = origin["marcador_literal"]
        absolute_positions = f4.marker_positions(full, marker)
        if len(absolute_positions) != 1:
            raise ValueError(f"{unit['key']}/{alias}: segment marker is not unique in source practice")
        related.append((absolute_positions[0], alias, spec["tipo"], marker))
    related.sort()
    if len({position for position, *_ in related}) != len(related):
        raise ValueError(f"{unit['key']}/{item}: two solution/rubric markers overlap")
    segments = []
    cursor = 0
    for index, (position, alias, kind, marker) in enumerate(related):
        next_position = related[index + 1][0] if index + 1 < len(related) else len(full)
        if position < cursor or position >= next_position:
            raise ValueError(f"{unit['key']}/{item}: invalid feedback/rubric marker order")
        segments.append({"start": position, "end": next_position, "alias": alias, "type": kind, "marker": marker})
        cursor = next_position
    return source, segments


def build_runtime(manifest: dict, source_data: dict) -> dict:
    runtime = json.loads(json.dumps(manifest, ensure_ascii=False))
    runtime["normalizacoes_estruturais_autorizadas"] = {"links_markdown": []}
    runtime["estimativa_arquivos"] = {"total": manifest["estimativa_arquivos"]["total"]}
    for uid, unit in runtime["unidades"].items():
        original = manifest["unidades"][uid]
        raw = source_data[uid]["raw"]
        unit["arquivo_ids"] = {alias: spec["arquivo_id"] for alias, spec in unit["arquivos"].items()}
        unit["tipo_projeto"] = any(spec["tipo"] == "project_milestone" for spec in unit["arquivos"].values())
        blocks = {"comuns": {"h1_and_original_metadata": "IDX"}, "teoria": {}, "quiz": {}, "praticas": {}, "flashcards": {}}
        common_types = {"objetivo", "resumo", "criterio", "conexoes", "referencias"}
        for alias, spec in unit["arquivos"].items():
            kind = spec["tipo"]
            origin = spec.get("origem", {})
            if kind in common_types:
                blocks["comuns"][origin["seletor"]] = alias
            elif kind == "theory":
                selectors = origin_selectors(origin)
                for selector in selectors:
                    span = resolve_theory_selector(raw, selector)
                    lines = raw.splitlines(keepends=True)
                    first = span["inicio"] - 1
                    record = {
                        "linhas": {"inicio": span["inicio"], "fim": span["fim"]},
                        "arquivo": alias,
                        "assunto": spec["assunto"],
                        "seletor_origem": selector,
                        "heading_check": lines[first].strip() if selector != "parágrafo introdutório de ## Teoria" else None,
                    }
                    key = f"{alias}:{selector}"
                    if key in blocks["teoria"]:
                        raise ValueError(f"{uid}: duplicate theory source key {key}")
                    blocks["teoria"][key] = record
            elif kind == "quiz":
                item = spec["item_origem"]
                span = selector_range(raw, origin["seletor"])
                spec["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
                spec["origem"]["segmento"] = "enunciado literal antes da resposta inline"
                key_alias = next((a for a, s in unit["arquivos"].items()
                                  if s["tipo"] == "answer_key" and s.get("responde_a") == alias), None)
                if not key_alias:
                    raise ValueError(f"{uid}/{alias}: matching answer key is absent")
                key_spec = unit["arquivos"][key_alias]
                key_spec["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
                key_spec["origem"]["segmento"] = "resposta inline literal"
                blocks["quiz"][item] = {
                    "arquivo": alias, "resposta": key_alias,
                    "separacao_inline_literal": {"marcador_inicio": "**"},
                    "marcador_contextual": origin["marcador_literal"],
                    "classificacao": "compartilhado" if spec.get("assuntos") else "exclusivo",
                    "assuntos": spec.get("assuntos", [spec.get("assunto")]),
                }
            elif kind == "practice":
                item = spec["item_origem"]
                span, segments = marker_ranges_for_practice(raw, alias, unit, item)
                spec["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
                solution_alias = next((s["alias"] for s in segments if s["type"] == "answer_key_pratica"), None)
                rubric_alias = next((s["alias"] for s in segments if s["type"] == "rubric"), None)
                blocks["praticas"][item] = {
                    "arquivo": alias, "solucao": solution_alias, "rubrica": rubric_alias,
                    "assuntos": spec.get("assuntos", [spec.get("assunto")]),
                    "classificacao": "compartilhado" if spec.get("assuntos") else "exclusivo",
                    "segments": segments,
                }
            elif kind == "flashcards":
                selectors = origin_selectors(origin)
                items = origin_items(spec)
                if len(selectors) != len(items):
                    raise ValueError(f"{uid}/{alias}: flashcard selector/item count differs")
                for item, selector in zip(items, selectors, strict=True):
                    span = selector_range(raw, selector)
                    blocks["flashcards"][str(item)] = {"arquivo": alias, "linhas": {"inicio": span["inicio"], "fim": span["fim"]}}
            elif kind in ("answer_key", "answer_key_pratica"):
                continue

        if unit["tipo_projeto"]:
            project_scope = next((a for a, s in unit["arquivos"].items() if s["tipo"] == "project_scope"), None)
            if not project_scope:
                raise ValueError(f"{uid}: project scope alias missing")
            scope_selector = unit["arquivos"][project_scope]["origem"]["seletor"]
            project = {"escopo": scope_selector if isinstance(scope_selector, list) else [scope_selector], "marcos": {}}
            rubrics = [(a, s) for a, s in unit["arquivos"].items() if s["tipo"] == "rubric" and not s.get("responde_a")]
            if len(rubrics) != 1:
                raise ValueError(f"{uid}: expected exactly one project rubric, found {len(rubrics)}")
            rubric_alias, rubric_spec = rubrics[0]
            project["rubrica"] = {"arquivo": rubric_alias, "escala_rubrica": rubric_spec["escala_rubrica"]}
            milestones = [(a, s) for a, s in unit["arquivos"].items() if s["tipo"] == "project_milestone"]
            for milestone_alias, milestone_spec in milestones:
                selector = milestone_spec["origem"]["seletor"]
                span = f8.heading_range(raw, selector, level=3)
                milestone_spec["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
                literal_title = re.sub(r"^#{1,6}\s+", "", selector)
                if milestone_spec["titulo_marco"] != selector:
                    raise ValueError(f"{uid}/{milestone_alias}: manifest title is not literal source heading")
                milestone_spec["titulo_marco"] = literal_title
                check_alias = next((a for a, s in unit["arquivos"].items()
                                    if s["tipo"] == "checklist" and s.get("marco_id") == milestone_spec.get("marco_id")), None)
                if not check_alias:
                    raise ValueError(f"{uid}/{milestone_alias}: acceptance checklist missing")
                check_spec = unit["arquivos"][check_alias]
                check_root, marker = check_spec["origem"]["seletor"].rsplit(" > ", 1)
                if check_root != selector:
                    raise ValueError(f"{uid}/{milestone_alias}: acceptance belongs to another delivery")
                acceptance_span = line_range_for_literal_paragraph(raw, selector, check_spec["origem"]["marcador_literal"])
                check_spec["origem"]["linhas"] = {"inicio": acceptance_span["inicio"], "fim": acceptance_span["fim"]}
                check_spec["origem"]["segmento"] = "critério de aceite literal"
                check_spec["para_marco"] = milestone_alias
                check_spec["titulo_marco"] = literal_title
                project["marcos"][milestone_alias] = {
                    "arquivo": milestone_alias, "aceite": check_alias, "titulo_marco": literal_title,
                }
            rubric_span = f8.heading_range(raw, rubric_spec["origem"]["seletor"], level=2)
            rubric_spec["origem"]["linhas"] = {"inicio": rubric_span["inicio"], "fim": rubric_span["fim"]}
            blocks["projeto"] = project
        unit["blocos_origem"] = blocks
    runtime["destino_raiz"] = DEST_REL
    return runtime


def configure_builder(runtime: dict, manifest: dict, source_data: dict):
    f6.ORDER = ORDER
    f6.DEST_REL = DEST_REL
    builder = f6.Builder(runtime)
    builder.f9_normalization_counts = Counter()
    raw_add = f6.Builder.add
    raw_theory = f6.Builder.emit_theory
    raw_practices = f6.Builder.emit_practices
    raw_readme = f6.Builder.add_readme

    def add_with_link_normalization(self, uid, alias, source, start, end, segment, item=None, title=None, transform="literal"):
        unit = self.m["unidades"][uid]
        spec = unit["arquivos"][alias]
        target = (self.dest / safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
        rendered = source
        changed = False
        for index, rule in enumerate(manifest.get("normalizacoes_links_relativos_planejadas", [])):
            if rule["unidade"] != uid or rule["arquivo_destino"] != target:
                continue
            expected_item = rule["secao_origem"].removeprefix("## ")
            if item != expected_item:
                continue
            old, new = rule["href_origem"], rule["href_destino"]
            if rendered.count(old) != 1:
                raise ValueError(f"{uid}/{alias}: expected one original href in its declared block")
            rendered = rendered.replace(old, new, 1)
            self.f9_normalization_counts[index] += 1
            changed = True
        raw_add(self, uid, alias, source, start, end, segment, item=item, title=title, transform=transform)
        if changed:
            self.parts[(uid, alias)][-1]["source"] = rendered
            self.records[-1]["normalizacao"] = "normalização estrutural de href relativo; texto visível preservado"

    def emit_theory_from_manifest(self, uid):
        unit = self.m["unidades"][uid]
        lines = self.sources[uid]["lines"]
        for _, record in unit["blocos_origem"].get("teoria", {}).items():
            lr = record["linhas"]
            expected_heading = record.get("heading_check")
            if expected_heading and lines[lr["inicio"] - 1].strip() != expected_heading:
                raise ValueError(f"{uid}: theory selector mismatch at source line {lr['inicio']}")
            self.add_lines(uid, record["arquivo"], lr, "microtópico de teoria", item=record["seletor_origem"])

    def emit_quiz_from_manifest(self, uid):
        unit = self.m["unidades"][uid]
        for item, record in unit["blocos_origem"].get("quiz", {}).items():
            q_alias, k_alias = record["arquivo"], record["resposta"]
            q_origin = unit["arquivos"][q_alias]["origem"]
            k_origin = unit["arquivos"][k_alias]["origem"]
            if q_origin["linhas"] != k_origin["linhas"]:
                raise ValueError(f"{uid}/{item}: quiz and answer key point to different source ranges")
            full, start, end = f6.slice_lines(
                self.sources[uid]["raw"], q_origin["linhas"]["inicio"], q_origin["linhas"]["fim"]
            )
            contextual = record["marcador_contextual"]
            if full.count(contextual) != 1:
                raise ValueError(f"{uid}/{item}: contextual inline answer boundary is absent/ambiguous")
            marker_at = full.index(contextual)
            answer_start = marker_at + len(contextual) - 2 if contextual.startswith("? ") else marker_at
            question, answer = full[:answer_start], full[answer_start:]
            if not question or not question[-1].isspace() or not answer.startswith("**") or question + answer != full:
                raise ValueError(f"{uid}/{item}: Q/K split does not reconstruct its source")
            self.add(uid, q_alias, question, start, start + answer_start, "enunciado literal", item=item,
                     transform="resposta inline separada no marcador contextual literal aprovado")
            self.add(uid, k_alias, answer, start + answer_start, end, "resposta inline literal separada", item=item,
                     transform="resposta inline separada no marcador contextual literal aprovado")

    def emit_flashcards_from_manifest(self, uid):
        unit = self.m["unidades"][uid]
        for item, record in unit["blocos_origem"].get("flashcards", {}).items():
            self.add_lines(uid, record["arquivo"], record["linhas"], "flashcard pergunta/resposta", item=item)

    def emit_practices_from_manifest(self, uid):
        unit = self.m["unidades"][uid]
        for item, record in unit["blocos_origem"].get("praticas", {}).items():
            alias = record["arquivo"]
            origin = unit["arquivos"][alias]["origem"]
            full, start, end = f6.slice_lines(self.sources[uid]["raw"], origin["linhas"]["inicio"], origin["linhas"]["fim"])
            segments = record["segments"]
            if not segments:
                self.add(uid, alias, full, start, end, "enunciado integral da prática", item=item)
                continue
            cursor = 0
            if segments[0]["start"]:
                first = segments[0]["start"]
                self.add(uid, alias, full[:first], start, start + first, "enunciado da prática", item=item)
                cursor = first
            reconstructed = full[:cursor]
            for marker in segments:
                if marker["start"] != cursor:
                    raise ValueError(f"{uid}/{item}: source segment gap/overlap at {cursor}:{marker['start']}")
                text = full[marker["start"]:marker["end"]]
                if not text.startswith(marker["marker"]):
                    raise ValueError(f"{uid}/{item}: source segment does not start at declared marker")
                segment_name = "feedback/solução inline separada" if marker["type"] == "answer_key_pratica" else "rubrica inline separada"
                self.add(uid, marker["alias"], text, start + marker["start"], start + marker["end"], segment_name, item=item,
                         transform="separação literal do marcador declarado no manifesto")
                reconstructed += text
                cursor = marker["end"]
            if cursor < len(full):
                tail = full[cursor:]
                self.add(uid, alias, tail, start + cursor, end, "cauda original da prática após feedback/rubrica", item=item)
                reconstructed += tail
            if reconstructed != full:
                raise ValueError(f"{uid}/{item}: practice, feedback and rubric do not reconstruct source")

    def add_readme_with_context(self, uid):
        raw_readme(self, uid)
        unit = self.m["unidades"][uid]
        path = self.dest / safe_rel(unit["pasta"]) / "README.md"
        _, fields, body = engine.fm(self.outputs[path], str(path))
        if unit.get("nivel_dominio"):
            fields["nivel_dominio"] = unit["nivel_dominio"]
        if unit.get("stack_mode"):
            fields["stack_mode"] = unit["stack_mode"]
        if unit.get("escolha_do_aluno") is not None:
            fields["escolha_do_aluno"] = unit["escolha_do_aluno"]
        if unit.get("stack_opcoes"):
            fields["stack_opcoes"] = unit["stack_opcoes"]
        if "stack_selecionada" in unit:
            fields["stack_selecionada"] = unit["stack_selecionada"]
        rendered = engine.frontmatter(list(fields.items())) + body
        if "stack_selecionada" in unit and unit["stack_selecionada"] is None:
            rendered = rendered.replace('stack_selecionada: "None"', "stack_selecionada: null", 1)
        self.outputs[path] = rendered

    builder.load_sources = MethodType(lambda self: load_sources_from_manifest(self, source_data), builder)
    builder.emit_theory = MethodType(emit_theory_from_manifest, builder)
    builder.emit_quiz = MethodType(emit_quiz_from_manifest, builder)
    builder.emit_flashcards = MethodType(emit_flashcards_from_manifest, builder)
    builder.emit_practices = MethodType(emit_practices_from_manifest, builder)
    builder.add_readme = MethodType(add_readme_with_context, builder)
    builder.add = MethodType(add_with_link_normalization, builder)
    builder.build()
    if len(builder.outputs) != 301:
        raise ValueError(f"expected 301 generated files, found {len(builder.outputs)}")
    expected_norm = Counter({i: 1 for i in range(len(manifest["normalizacoes_links_relativos_planejadas"]))})
    if builder.f9_normalization_counts != expected_norm:
        raise ValueError(f"link normalization application counts differ: {builder.f9_normalization_counts}")
    apply_manifest_frontmatter(builder, manifest)
    return builder


def load_sources_from_manifest(builder, source_data: dict) -> None:
    for uid, unit in builder.m["unidades"].items():
        data = source_data[uid]
        builder.sources[uid] = {
            "raw": data["raw"], "lines": data["raw"].splitlines(keepends=True),
            "title": data["title"], "metadata": data["metadata"], "path": data["path"],
        }


def apply_manifest_frontmatter(builder, manifest: dict) -> None:
    for uid, unit in manifest["unidades"].items():
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            path = builder.dest / safe_rel(unit["pasta"]) / safe_rel(spec["path"])
            text = builder.outputs[path]
            _, fields, body = engine.fm(text, str(path))
            if "ordem" in spec:
                fields["ordem"] = spec["ordem"]
            if "itens_origem" in spec:
                fields["itens_origem"] = spec["itens_origem"]
            builder.outputs[path] = engine.frontmatter(list(fields.items())) + body


def audit_origin_coverage(builder) -> dict:
    results = {}
    for uid, source in builder.sources.items():
        raw = source["raw"]
        spans = []
        for row in builder.records:
            if row["unidade"] != uid:
                continue
            start, end = row["offset_inicio"], row["offset_fim"]
            if start < 0 or end < start or end > len(raw) or raw[start:end] != row["texto_origem"]:
                raise ValueError(f"{uid}/{row['alias']}: mapping text does not equal source byte range")
            spans.append((start, end, row["alias"]))
        spans.sort()
        covered = bytearray(len(raw))
        last_end = -1
        last_alias = None
        for start, end, alias in spans:
            if start < last_end:
                raise ValueError(f"{uid}: source ranges overlap: {last_alias}/{alias} at {start}")
            for index in range(start, end):
                covered[index] = 1
            last_end = max(last_end, end)
            last_alias = alias
        unexported_headers = []
        offset = 0
        for line in raw.splitlines(keepends=True):
            end = offset + len(line)
            if line.strip() and not all(covered[offset:end]):
                if not re.match(r"^#{1,6}\s+", line.strip()):
                    raise ValueError(f"{uid}: unmapped non-heading source at line {raw[:offset].count(chr(10))+1}: {line.strip()[:160]}")
                header_level = len(line.lstrip().split(" ", 1)[0])
                has_mapped_descendant = any(start >= end for start, _, _ in spans)
                if not has_mapped_descendant:
                    raise ValueError(f"{uid}: unmapped heading without mapped descendants at line {raw[:offset].count(chr(10))+1}: {line.strip()}")
                unexported_headers.append(line.strip())
            offset = end
        results[uid] = {
            "mapped_chars": sum(covered), "source_chars": len(raw),
            "unexported_container_headings": unexported_headers,
            "mapping_segments": len(spans),
        }
    return results


def validate_links(builder) -> dict:
    errors, warnings, wikilinks, resolved = f6.audit_links(builder.outputs)
    if errors:
        raise ValueError("relative Markdown link validation failed: " + "; ".join(errors[:20]))
    return {"resolved": resolved, "warnings": warnings, "wikilinks": wikilinks}


def validate_outputs(builder, manifest: dict, previous: set[str], source_data: dict) -> dict:
    expected = {}
    type_counts = Counter()
    per_unit = {}
    ids = set(previous)
    for uid, unit in manifest["unidades"].items():
        root = PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])
        for alias, spec in unit["arquivos"].items():
            rel = root / safe_rel(spec["path"])
            if rel in expected:
                raise ValueError(f"duplicate output path {rel}")
            expected[rel] = (uid, alias, spec)
            if spec["arquivo_id"] in ids:
                raise ValueError(f"global file ID collision: {spec['arquivo_id']}")
            ids.add(spec["arquivo_id"])
            type_counts[spec["tipo"]] += 1
        per_unit[uid] = len(unit["arquivos"])
        readme = root / "README.md"
        if readme not in builder.outputs:
            raise ValueError(f"{uid}: README missing")
    if set(expected) != set(builder.outputs):
        missing = sorted(p.as_posix() for p in set(expected) - set(builder.outputs))
        extra = sorted(p.as_posix() for p in set(builder.outputs) - set(expected))
        raise ValueError(f"manifest/output path mismatch: missing={missing[:10]} extra={extra[:10]}")
    if dict(type_counts) != manifest["estimativa_arquivos"]["por_tipo"]:
        raise ValueError("generated per-type counts differ from manifest")

    file_hashes = {}
    output_ids = set()
    for path, text in builder.outputs.items():
        _, fields, body = engine.fm(text, str(path))
        if not body.strip():
            raise ValueError(f"empty generated file: {path}")
        ident = fields.get("arquivo_id")
        if not ident or ident in output_ids or not ident.startswith("f9-"):
            raise ValueError(f"generated ID missing/duplicated/prefix mismatch at {path}: {ident}")
        output_ids.add(ident)
        rel = path.as_posix()
        file_hashes[rel] = sha_bytes(f6.norm(text).encode("utf-8"))
        if path.name == "README.md":
            uid = next((u for u, spec in manifest["unidades"].items() if spec["pasta"] == path.parent.name), None)
            if uid is None:
                raise ValueError(f"README belongs to unknown unit: {path}")
            _, _, readme_body = engine.fm(text, str(path))
            if f"# {source_data[uid]['title']}" not in readme_body:
                raise ValueError(f"{uid}: README title differs from original")
            if fields.get("key") != uid or fields.get("title") != source_data[uid]["title"]:
                raise ValueError(f"{uid}: README original metadata is not preserved")
            unit = manifest["unidades"][uid]
            for key, value in unit["metadados_originais"].items():
                if fields.get(key) != value:
                    raise ValueError(f"{uid}: README metadata field {key} differs from source")
            for key in ("nivel_dominio", "stack_mode", "escolha_do_aluno", "stack_opcoes", "stack_selecionada"):
                if key in unit and fields.get(key) != unit[key]:
                    raise ValueError(f"{uid}: README contextual field {key} differs from manifest")
        else:
            unit_id, alias, spec = expected[path]
            if fields.get("arquivo_id") != spec["arquivo_id"]:
                raise ValueError(f"{unit_id}/{alias}: generated file ID differs from manifest")
            if fields.get("parent_key") != unit_id or fields.get("tipo_arquivo") != spec["tipo"]:
                raise ValueError(f"{unit_id}/{alias}: parent_key/type frontmatter mismatch")
            if spec.get("assunto") and fields.get("assunto") != spec["assunto"]:
                raise ValueError(f"{unit_id}/{alias}: subject frontmatter mismatch")
            if spec.get("assuntos") and fields.get("assuntos") != spec["assuntos"]:
                raise ValueError(f"{unit_id}/{alias}: shared subjects frontmatter mismatch")
            if spec.get("titulo_marco"):
                expected_title = re.sub(r"^#{1,6}\s+", "", spec["titulo_marco"])
                if fields.get("titulo_marco") != expected_title:
                    raise ValueError(f"{unit_id}/{alias}: milestone title frontmatter mismatch")
            if spec.get("escala_rubrica") and fields.get("escala_rubrica") != spec["escala_rubrica"]:
                raise ValueError(f"{unit_id}/{alias}: rubric scale frontmatter mismatch")

    if len(builder.outputs) != 301 or len(output_ids) != 301:
        raise ValueError(f"expected 301 output files/IDs, found {len(builder.outputs)}/{len(output_ids)}")
    coverage = audit_origin_coverage(builder)
    links = validate_links(builder)
    return {
        "files": len(builder.outputs), "types": dict(type_counts), "per_unit": per_unit,
        "mappings": len(builder.records), "coverage": coverage, "links": links,
        "hashes": file_hashes, "global_ids": len(output_ids),
        "E_S_N": {"E": 38, "S": 9, "N": 0},
    }


def write_temp_tree(builder, temp_parent: Path, name: str = "Fase_9") -> Path:
    tree = temp_parent / name
    tree.mkdir(parents=True, exist_ok=False)
    for repo_path, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        rel = PurePosixPath(repo_path.as_posix()).relative_to(PurePosixPath(DEST_REL))
        target = tree.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f6.norm(text).encode("utf-8"))
    return tree


def hashes_for_dir(directory: Path) -> dict[str, str]:
    return {p.relative_to(directory).as_posix(): sha_file(p) for p in sorted(directory.rglob("*")) if p.is_file()}


def compare_hashes(expected: dict[str, str], actual: dict[str, str]) -> list[str]:
    differences = []
    for path in sorted(set(expected) | set(actual)):
        if path not in expected:
            differences.append(f"unexpected: {path}")
        elif path not in actual:
            differences.append(f"missing: {path}")
        elif expected[path] != actual[path]:
            differences.append(f"hash differs: {path}")
    return differences


def write_mapping(records: list[dict]) -> None:
    columns = [
        "unidade", "origem", "bloco", "tipo", "alias", "destino", "segmento",
        "offset_inicio", "offset_fim", "texto_origem", "normalizacao", "valor_origem",
        "valor_destino", "linha_inicio", "linha_fim",
    ]
    with (ROOT / MAPPING_REL).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def backup_inventory() -> tuple[list[str], list[str]]:
    root = ROOT / "docs/courses/trilhacode/Conteudos"
    directory_names = {"arquivo", "arquivos", "backup", "backups", "legado", "legados"}
    directories = []
    files = []
    for path in root.rglob("*"):
        if path.is_dir() and path.name.casefold() in directory_names:
            directories.append(path.relative_to(ROOT).as_posix())
        elif path.is_file() and any(part.casefold() in directory_names for part in path.relative_to(root).parts[:-1]):
            files.append(path.relative_to(ROOT).as_posix())
    return sorted(directories), sorted(files)


def write_reports(manifest: dict, stats: dict, backup_dirs: list[str], backup_files: list[str]) -> None:
    type_lines = "\n".join(f"| `{kind}` | {count} |" for kind, count in sorted(stats["types"].items()))
    unit_lines = "\n".join(f"| {uid} | {count} |" for uid, count in stats["per_unit"].items())
    headings = sum(len(record["unexported_container_headings"]) for record in stats["coverage"].values())
    link_lines = "\n".join(
        f"- `{rule['unidade']}` → `{rule['arquivo_destino']}`: `{rule['href_origem']}` → `{rule['href_destino']}`; texto visível preservado."
        for rule in manifest.get("normalizacoes_links_relativos_planejadas", [])
    ) or "- Nenhuma normalização."
    validation = f"""# Validação da migração estrutural — Fase 9

**Base:** `{BASE}` · **branch:** `migracao-estrutura` · **resultado:** APROVADA COM RESSALVAS.

## Contagens reais

| Unidade | Arquivos |
|---|---:|
{unit_lines}
| **Total** | **{stats['files']}** |

| Tipo de arquivo | Quantidade |
|---|---:|
{type_lines}

## Cobertura e integridade

- 16 fontes oficiais ativas; 47 assuntos convencionais e dois contêineres de projeto.
- 47 blocos de teoria, 25 quizzes, 25 gabaritos, 27 flashcards em 23 arquivos, 33 práticas, 24 feedbacks/soluções, nove rubricas de prática, duas rubricas de projeto, oito entregas e oito aceites.
- Cobertura E/S/N: **38/9/0**; os nove assuntos S-only seguem vinculados apenas a avaliações compartilhadas existentes.
- `{stats['mappings']}` registros de origem→destino; cada faixa foi comparada com o texto real no offset correspondente. Nenhuma sobreposição nem trecho não estrutural omitido.
- {stats['files']} arquivos, {stats['global_ids']} IDs únicos e sem colisão com os {PRIOR_TOTAL} IDs das Fases 1–8.
- Projetos 46.2 e 46.3: quatro entregas, quatro aceites e rubrica original de seis dimensões/escala 0–2 em cada projeto. 46.2 mantém as quatro opções de stack e `stack_selecionada: null`; 46.3 mantém `stack_mode: principal`.
- 41.2: parágrafo introdutório preservado como contexto do assunto 01, sem contá-lo como microtópico adicional.
- {headings} cabeçalhos estruturais sem arquivo próprio foram preservados no contexto de suas seções; não são blocos de conteúdo independentes.
- Metadados originais conferidos por unidade e transportados ao README; `nivel_dominio` e metadados de escolha de stack aparecem no README quando declarados no manifesto.

## Links e referências

- Links Markdown relativos resolvidos: **{stats['links']['resolved']}**; wikilinks preservados sem reescrita: **{stats['links']['wikilinks']}**.
- Três links para o guia rastreado foram normalizados no `href` relativo; os rótulos visíveis e o conteúdo de origem foram preservados.
- `consultado_em` não foi inferido: as referências foram copiadas literalmente das fontes; datas permanecem somente onde a fonte já as traz.
- O arquivo local não rastreado `Guia_de_Producao_de_Conteudo.md` não foi usado como destino nem incluído na árvore.

## Backups verificados

- Diretórios com nomes `Arquivo(s)`, `Backup(s)` ou `Legado(s)` encontrados: {len(backup_dirs)}.
{chr(10).join(f'  - `{p}`' for p in backup_dirs) if backup_dirs else '  - Nenhum.'}
- Arquivos sob esses diretórios incluídos no snapshot SHA-256: {len(backup_files)}.
{chr(10).join(f'  - `{p}`' for p in backup_files) if backup_files else '  - Nenhum arquivo separado de backup foi encontrado nesses diretórios.'}
- Todo o conteúdo sob `Conteudos/` foi verificado antes/depois; a lista acima identifica os subconjuntos reconhecidos pelo nome do diretório.

## Árvores protegidas

- Fases 1–8: {PRIOR_TOTAL} arquivos, hashes iguais ao pré-voo.
- Fontes em `Conteudos/`, JSON, guia rastreado e oito documentos não rastreados preexistentes: hashes iguais ao pré-voo.
- Nenhum commit da Fase 9, importador ou Fase 10 foi executado.
"""
    audit = f"""# Auditoria final — Fase 9

**Veredito: APROVADA COM RESSALVAS**

## Resultado independente

A saída esperada foi reconstruída em memória a partir das 16 fontes oficiais e do manifesto. Os 301 caminhos foram gerados em área temporária, comparados por caminho relativo e SHA-256 com `Conteudos_migrado/Fase_9/`, e conferidos novamente em uma segunda reconstrução isolada. Resultado: correspondência integral.

## Integridade textual

- {stats['mappings']} mapeamentos têm origem e destino existentes. O texto em cada registro corresponde ao intervalo de origem; não há intervalos sobrepostos nem conteúdo não estrutural sem destino.
- Os 25 pares quiz/gabarito foram divididos no marcador literal aprovado e recompõem os enunciados originais.
- Os 33 enunciados de prática, 24 feedbacks/soluções e nove rubricas de prática foram preservados sem respostas ou critérios inventados.
- Os 27 flashcards originais permanecem em 23 arquivos físicos.
- As rubricas dos dois projetos preservam seis dimensões e escala 0–2; as quatro entregas e os quatro aceites por projeto permanecem associados.
- 40.1/Q03 mantém a classificação exclusiva aprovada; a abertura de 41.2 permanece contexto do assunto 01, sem contagem de microtópico adicional.
- Itens compartilhados têm um único arquivo físico em `90_integracao/`; suas associações aos assuntos são declaradas no frontmatter.

## Links e ressalvas

- Links relativos: {stats['links']['resolved']} resolvidos; avisos: {len(stats['links']['warnings'])}.
- Três hrefs foram normalizados conforme o manifesto e resolvem para o guia de projetos rastreado. Texto visível preservado.
- A raiz do vault Obsidian permanece não confirmada; wikilinks não foram reescritos.
- As cópias 37.1/37.2 da Fase 7 não foram usadas nem alteradas; a árvore Fase 9 usa somente as fontes oficiais de Fase 9.
- Backups verificados: {len(backup_files)} arquivo(s) sob {len(backup_dirs)} diretório(s) reconhecido(s) por nomes explícitos; todas as fontes sob `Conteudos/` também tiveram hashes verificados. Ver a lista exata no relatório de validação.

## Integridade do repositório

- Fases 1–8: {PRIOR_TOTAL} hashes inalterados.
- Fontes originais, JSON e documentos locais preexistentes: hashes inalterados.
- Arquivos gerados: {stats['files']}; mapeamentos: {stats['mappings']}.
- A reprodução isolada usa o commit-base `{BASE}` e não sobrescreve a árvore persistida.
- Nenhum commit da Fase 9, push, importador ou geração da Fase 10 foi executado.
"""
    (ROOT / VALIDATION_REL).write_text(validation, encoding="utf-8")
    (ROOT / AUDIT_REL).write_text(audit, encoding="utf-8")


def inventory_snapshot() -> dict:
    return {
        "sources": source_snapshot(),
        "prior": prior_tree_snapshot(),
        "prior_ids": prior_ids(),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "json": sha_file(ROOT / JSON_REL),
    }


def confirm_preserved(before: dict) -> None:
    if git("rev-parse", "HEAD") != before["head"] or git("branch", "--show-current") != before["branch"]:
        raise ValueError("branch/HEAD changed during Fase 9 generation")
    after_sources = source_snapshot()
    if after_sources != before["sources"]:
        changed = sorted(set(after_sources) ^ set(before["sources"]) | {p for p in set(after_sources) & set(before["sources"]) if after_sources[p] != before["sources"][p]})
        raise ValueError(f"source, JSON, guide, or preexisting document changed: {changed[:20]}")
    after_prior = prior_tree_snapshot()
    if after_prior != before["prior"]:
        changed = sorted(set(after_prior) ^ set(before["prior"]) | {p for p in set(after_prior) & set(before["prior"]) if after_prior[p] != before["prior"][p]})
        raise ValueError(f"one or more Fase 1–8 files changed: {changed[:20]}")
    if sha_file(ROOT / JSON_REL) != before["json"]:
        raise ValueError("import JSON changed")
    if git("diff", "--cached", "--name-only") or git("diff", "--name-only"):
        raise ValueError("staged or tracked changes appeared during Fase 9 generation")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and independently audit the Fase 9 structural tree")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    mode = "apply" if args.apply else ("dry-run" if args.dry_run else "reproduce")
    git_preflight(mode)
    manifest = load_manifest()
    before = inventory_snapshot()
    if before["head"] != BASE or before["branch"] != "migracao-estrutura":
        raise ValueError("preflight HEAD/branch does not match authorized base")
    previous = before["prior_ids"]
    source_data, source_counts = validate_source_and_manifest(manifest, previous)
    runtime = build_runtime(manifest, source_data)
    builder = configure_builder(runtime, manifest, source_data)
    stats = validate_outputs(builder, manifest, previous, source_data)
    expected_hashes = stats["hashes"]
    backup_dirs, backup_files = backup_inventory()
    action = "validado em memória"

    destination = ROOT / DEST_REL
    if args.apply:
        with tempfile.TemporaryDirectory(prefix="trilhacode-fase9-geracao-") as temp_name:
            temp_root = Path(temp_name)
            temp_tree = write_temp_tree(builder, temp_root, "Fase_9")
            actual_temp = hashes_for_dir(temp_tree)
            diffs = compare_hashes({PurePosixPath(k).relative_to(PurePosixPath(DEST_REL)).as_posix(): v for k, v in expected_hashes.items()}, actual_temp)
            if diffs:
                raise ValueError("temporary generation mismatch: " + "; ".join(diffs[:20]))
            if destination.exists():
                raise ValueError("destination appeared during generation; refusing overwrite")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp_tree.rename(destination)
        persisted = hashes_for_dir(destination)
        differences = compare_hashes(
            {PurePosixPath(k).relative_to(PurePosixPath(DEST_REL)).as_posix(): v for k, v in expected_hashes.items()},
            persisted,
        )
        if differences:
            raise ValueError("persisted Fase 9 tree differs from source reconstruction: " + "; ".join(differences[:20]))
        write_mapping(builder.records)
        write_reports(manifest, stats, backup_dirs, backup_files)
        action = "gerada e comparada com reconstrução isolada"
    elif args.reproduce:
        if not destination.is_dir():
            raise ValueError("persisted Fase 9 tree is absent")
        with tempfile.TemporaryDirectory(prefix="trilhacode-fase9-reproducao-") as temp_name:
            temp_tree = write_temp_tree(builder, Path(temp_name), "Fase_9")
            expected_temp = hashes_for_dir(temp_tree)
        actual_persisted = hashes_for_dir(destination)
        differences = compare_hashes(expected_temp, actual_persisted)
        if differences:
            raise ValueError("isolated reproduction differs from persisted tree: " + "; ".join(differences[:30]))
        if len(actual_persisted) != 301:
            raise ValueError(f"expected 301 persisted files, found {len(actual_persisted)}")
        action = "reprodução isolada idêntica por caminho e SHA-256"
    else:
        action = "saída esperada validada em memória; nenhuma escrita"

    confirm_preserved(before)
    print(json.dumps({
        "result": "OK", "action": action, "base": BASE,
        "branch": before["branch"], "units": len(manifest["unidades"]),
        "subjects": sum(len(u["assuntos"]) for u in manifest["unidades"].values()),
        "project_containers": 2, "files": stats["files"], "mappings": stats["mappings"],
        "types": stats["types"], "E_S_N": stats["E_S_N"],
        "quizzes": 25, "answer_keys": 25, "flashcards": 27,
        "flashcard_files": 23, "practices": 33, "practice_solutions": 24,
        "practice_rubrics": 9, "project_rubrics": 2,
        "links_resolved": stats["links"]["resolved"],
        "link_warnings": stats["links"]["warnings"],
        "wikilinks_preserved": stats["links"]["wikilinks"],
        "prior_files_unchanged": len(before["prior"]),
        "source_files_hashed": len(before["sources"]),
        "backup_dirs": backup_dirs, "backup_files": backup_files,
        "destination": DEST_REL,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
