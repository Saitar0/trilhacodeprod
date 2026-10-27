from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from types import MethodType

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase1 as engine
import _migrar_fase4 as f4
import _migrar_fase6 as f6

MANIFEST = ROOT / "docs/migracao/mapa_de_migracao_fase7.yml"
DEST = "docs/courses/trilhacode/Conteudos_migrado/Fase_7"
BASE = "53956919fc145e897f5ac7763513812b03f04dba"
ORDER = ["32.1", "32.2", "33.1", "34.1", "35.1", "36.1", "36.2"]
TREE_COUNTS = {1: 221, 2: 144, 3: 313, 4: 395, 5: 483, 6: 449}
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"


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


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"unsafe relative path: {value!r}")
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True, encoding="utf-8"
    ).strip()


def snapshot_tree(path: Path) -> dict[str, str]:
    result = {}
    if path.exists():
        for item in path.rglob("*"):
            if item.is_file():
                result[item.relative_to(ROOT).as_posix()] = file_hash(item)
    return result


def prior_tree_snapshot() -> dict[str, str]:
    result = {}
    for number, expected in TREE_COUNTS.items():
        base = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        paths = [path for path in base.rglob("*") if path.is_file()]
        if not base.is_dir() or len(paths) != expected:
            raise ValueError(f"Fase {number}: expected {expected} files, found {len(paths)}")
        result.update({path.relative_to(ROOT).as_posix(): file_hash(path) for path in paths})
    if len(result) != 2005:
        raise ValueError(f"expected 2,005 prior files, found {len(result)}")
    return result


def input_snapshot() -> dict[str, str]:
    result = snapshot_tree(ROOT / "docs/courses/trilhacode/Conteudos")
    protected = [
        JSON_REL,
        "docs/courses/trilhacode/Fase_7_Infra_Deploy_e_Cloud.md",
        "docs/courses/trilhacode/Fase_8_Infra_Operacao.md",
        "docs/courses/trilhacode/Referencias_Fase_7.md",
        "docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",
        "docs/migracao/PLANEJAMENTO_FASE5.md",
        "docs/migracao/PLANEJAMENTO_FASE6.md",
        "docs/migracao/PLANEJAMENTO_FASE7.md",
        "docs/migracao/mapa_de_migracao_fase7.yml",
    ]
    for rel in protected:
        path = ROOT / Path(*safe_rel(rel).parts)
        if not path.is_file():
            raise ValueError(f"protected input missing: {rel}")
        result[rel] = file_hash(path)
    return result


def prior_ids() -> set[str]:
    result = set()
    for number in TREE_COUNTS:
        base = ROOT / "docs/courses/trilhacode/Conteudos_migrado" / f"Fase_{number}"
        for path in base.rglob("*.md"):
            _, fields, _ = engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in result:
                raise ValueError(f"missing/duplicate prior arquivo_id: {path}")
            result.add(ident)
    if len(result) != 2005:
        raise ValueError(f"expected 2,005 prior IDs, found {len(result)}")
    return result


def load_manifest() -> dict:
    manifest = yaml.load(MANIFEST.read_text(encoding="utf-8-sig"), Loader=UniqueKeyLoader)
    if (
        manifest.get("fase") != "Fase_7"
        or manifest.get("base_commit") != BASE
        or manifest.get("id_prefix") != "f7"
        or manifest.get("destino_raiz") != DEST
        or manifest.get("ordem_unidades") != ORDER
        or list(manifest.get("unidades", {})) != ORDER
    ):
        raise ValueError("Fase 7 manifest identity/order differs from the approved input")
    return manifest


def validate_manifest(manifest: dict, previous_ids: set[str]) -> Counter:
    paths, ids, types = set(), set(), Counter()
    subjects = theory = quizzes = practices = shared_quizzes = shared_practices = 0
    for unit_key, unit in manifest["unidades"].items():
        if unit["key"] != unit_key:
            raise ValueError(f"{unit_key}: key mismatch")
        subjects += len(unit["assuntos"])
        for slug in unit["assuntos"]:
            if not re.fullmatch(r"\d{2}_[a-z0-9_]+", slug):
                raise ValueError(f"invalid subject slug: {unit_key}/{slug}")
        for alias, spec in unit["arquivos"].items():
            path = (safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
            ident = spec["arquivo_id"]
            if path in paths:
                raise ValueError(f"duplicate physical path: {path}")
            if not ident.startswith("f7-") or ident in ids or ident in previous_ids:
                raise ValueError(f"invalid/colliding arquivo_id: {ident}")
            paths.add(path)
            ids.add(ident)
            types[spec["tipo"]] += 1
            if alias == "IDX":
                if spec["path"] != "README.md":
                    raise ValueError(f"{unit_key}: IDX must target README.md")
                continue
            if "origem" not in spec:
                raise ValueError(f"{unit_key}/{alias}: missing source mapping")
            if spec.get("assunto"):
                if spec["assunto"] not in unit["assuntos"] or PurePosixPath(spec["path"]).parts[0] != spec["assunto"]:
                    raise ValueError(f"{unit_key}/{alias}: exclusive subject/path mismatch")
            if spec.get("assuntos"):
                if len(spec["assuntos"]) < 2 or PurePosixPath(spec["path"]).parts[0] != "90_integracao":
                    raise ValueError(f"{unit_key}/{alias}: shared item lacks unique integration path")
            elif PurePosixPath(spec["path"]).parts[0] == "90_integracao":
                raise ValueError(f"{unit_key}/{alias}: integration path without shared subjects")
            if spec["tipo"] == "theory":
                theory += len(spec["origem"])
            elif spec["tipo"] == "quiz":
                quizzes += 1
            elif spec["tipo"] == "practice":
                practices += 1
                shared_practices += bool(spec.get("assuntos"))
            elif spec["tipo"] == "answer_key" and not spec.get("responde_a"):
                raise ValueError(f"{unit_key}/{alias}: answer key has no question reference")

        coverage = {
            slug: {
                "quiz_exclusivos": [], "quiz_compartilhados": [],
                "praticas_exclusivas": [], "praticas_compartilhadas": [],
                "flashcards_exclusivos": [], "flashcards_compartilhados": [],
            }
            for slug in unit["assuntos"]
        }
        for alias, spec in unit["arquivos"].items():
            if spec["tipo"] not in ("quiz", "practice"):
                continue
            item = spec["itens_origem"][0]
            assigned = spec.get("assuntos") or ([spec["assunto"]] if spec.get("assunto") else [])
            if not assigned:
                raise ValueError(f"{unit_key}/{item}: no subject assignment")
            shared = len(assigned) > 1
            if spec["tipo"] == "quiz":
                field = "quiz_compartilhados" if shared else "quiz_exclusivos"
                shared_quizzes += shared
            else:
                field = "praticas_compartilhadas" if shared else "praticas_exclusivas"
            for slug in assigned:
                coverage[slug][field].append(item)
        if coverage != unit["cobertura"]:
            raise ValueError(f"{unit_key}: coverage table differs from file assignments")

    if (subjects, theory, quizzes, practices, shared_quizzes, shared_practices) != (23, 28, 35, 21, 1, 11):
        raise ValueError("manifest totals differ from the approved Fase 7 inventory")
    if len(paths) != 156 or manifest["estimativa_arquivos"]["total"] != 156:
        raise ValueError("manifest path count differs from 156")
    return types


def runtime_manifest(source: dict, types: Counter) -> dict:
    manifest = copy.deepcopy(source)
    manifest["normalizacoes_estruturais_autorizadas"] = {"links_markdown": []}
    manifest["estimativa_arquivos"] = {"total": 156, **dict(types)}
    for unit in manifest["unidades"].values():
        unit["arquivo_ids"] = {alias: spec["arquivo_id"] for alias, spec in unit["arquivos"].items()}
        blocks = {"comuns": {"h1_and_original_metadata": "IDX"}, "teoria": {}, "quiz": {}, "praticas": {}, "flashcards": {}}
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            if spec["tipo"] in ("objetivo", "resumo", "criterio", "conexoes", "referencias"):
                blocks["comuns"][spec["origem"]["seletor"]] = alias
            elif spec["tipo"] == "theory":
                for block in spec["origem"]:
                    blocks["teoria"][block["seletor"]] = {
                        "linhas": block["linhas"], "arquivo": alias, "assunto": spec["assunto"]
                    }
        for alias, spec in unit["arquivos"].items():
            if spec["tipo"] == "quiz":
                answer = next(
                    (key for key, candidate in unit["arquivos"].items()
                     if candidate["tipo"] == "answer_key" and candidate.get("responde_a") == alias), None
                )
                if not answer:
                    raise ValueError(f"{alias}: matching answer key missing")
                item = spec["itens_origem"][0]
                blocks["quiz"][item] = {
                    "arquivo": alias, "resposta": answer,
                    "assuntos": spec.get("assuntos") or [spec["assunto"]],
                    "classificacao": spec["classificacao"],
                    "separacao_inline_literal": {"marcador_inicio": "**Resposta esperada:**"},
                }
            elif spec["tipo"] == "practice":
                blocks["praticas"][spec["itens_origem"][0]] = {"arquivo": alias}
        unit["blocos_origem"] = blocks
    return manifest


def builder_for(manifest: dict):
    f6.ORDER = ORDER
    f6.DEST_REL = DEST
    runtime = runtime_manifest(manifest, Counter(
        spec["tipo"] for unit in manifest["unidades"].values() for spec in unit["arquivos"].values()
    ))
    builder = f6.Builder(runtime)

    def load_sources(self):
        active = {unit["origem"] for unit in self.m["unidades"].values()}
        auxiliary = {item["origem"] for item in self.m["fontes_auxiliares_nao_migradas"]}
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "docs/courses/trilhacode/Conteudos/Fase_7").glob("*.md")
        }
        if len(active) != 7 or len(auxiliary) != 2 or actual != active | auxiliary:
            raise ValueError("Fase 7 source inventory differs from manifest")
        for unit_key, unit in self.m["unidades"].items():
            raw = read_text(ROOT / Path(*safe_rel(unit["origem"]).parts))
            title, metadata, _ = f4.parse_header(raw, unit, unit["origem"])
            if title != unit["titulo_original"] or metadata != unit["metadados_originais"]:
                raise ValueError(f"{unit_key}: source title/metadata mismatch")
            self.sources[unit_key] = {
                "raw": raw, "lines": raw.splitlines(keepends=True),
                "title": title, "metadata": metadata, "path": unit["origem"],
            }

    builder.load_sources = MethodType(load_sources, builder)
    builder.build()
    return builder


def validate_outputs(builder, previous_ids: set[str]) -> tuple[list[str], list[str], dict]:
    errors, warnings = [], []
    coverage_errors, builder.coverage_stats = f6.audit_source_coverage(builder)
    errors.extend(coverage_errors)
    link_errors, link_warnings, wikilinks, resolved = f6.audit_links(builder.outputs)
    errors.extend(link_errors)
    warnings.extend(link_warnings)
    builder.link_stats = {"markdown_relativos_resolvidos": resolved, "wikilinks_preservados": wikilinks}
    output_ids = set(previous_ids)
    types = Counter()
    for path, text in builder.outputs.items():
        try:
            _, fields, body = engine.fm(text, str(path))
            match = re.match(r"\A---\n(.*?)\n---\n\n", text, re.S)
            if not match:
                raise ValueError("missing frontmatter")
            parsed = yaml.load(match.group(1), Loader=UniqueKeyLoader)
            if parsed != fields:
                raise ValueError("frontmatter parsers disagree")
        except Exception as exc:
            errors.append(f"invalid YAML in {path}: {exc}")
            continue
        ident = fields.get("arquivo_id")
        if not ident or ident in output_ids:
            errors.append(f"missing/duplicate/global ID in {path}: {ident}")
        else:
            output_ids.add(ident)
        if not body.strip():
            errors.append(f"empty file: {path}")
        types[fields.get("tipo_arquivo")] += 1
    if len(builder.outputs) != 156 or len(output_ids) != 2161:
        errors.append("output file/ID count mismatch")
    if len(builder.records) != 210:
        errors.append(f"expected 210 mapping records, found {len(builder.records)}")
    return errors, warnings, dict(types)


def compare_tree(expected: dict, directory: Path) -> tuple[list[str], dict[str, str]]:
    actual = {}
    if directory.is_dir():
        for path in directory.rglob("*"):
            if path.is_file():
                actual[path.relative_to(directory).as_posix()] = file_hash(path)
    mismatches = []
    if set(actual) != set(expected):
        mismatches.append(f"paths differ: missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
    for rel in sorted(set(actual) & set(expected)):
        if actual[rel] != expected[rel]:
            mismatches.append(f"SHA-256 differs: {rel}")
    return mismatches, actual


def write_tree(builder, directory: Path, prefix: str) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=False)
    expected = {}
    for repo_path, text in sorted(builder.outputs.items(), key=lambda pair: pair[0].as_posix()):
        full = repo_path.as_posix()
        if not full.startswith(prefix + "/"):
            raise ValueError(f"output outside declared phase root: {full}")
        relative = PurePosixPath(full).relative_to(PurePosixPath(prefix))
        target = directory.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = f6.norm(text).encode("utf-8")
        target.write_bytes(data)
        expected[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate, audit, or reproduce the structural Fase 7 tree")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--audit-existing", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--reproduce-to", type=Path)
    args = parser.parse_args()
    if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT.resolve():
        raise ValueError("Git root differs from this script's repository")
    if git("branch", "--show-current") != "migracao-estrutura" or git("rev-parse", "HEAD") != BASE:
        raise ValueError("branch/HEAD differs from the authorized Fase 7 base")
    if git("diff", "--cached", "--name-only") or git("diff", "--name-only"):
        raise ValueError("staged or tracked changes found")

    input_before = input_snapshot()
    prior_before = prior_tree_snapshot()
    previous_ids = prior_ids()
    manifest = load_manifest()
    declared_types = validate_manifest(manifest, previous_ids)
    builder = builder_for(manifest)
    errors, warnings, types = validate_outputs(builder, previous_ids)
    if errors:
        raise ValueError("output validation failed: " + "; ".join(errors[:12]))
    if dict(builder.type_counts()) != types:
        raise ValueError("file type counts disagree with frontmatter")

    expected = {}
    for repo_path, text in builder.outputs.items():
        relative = repo_path.as_posix().removeprefix(DEST + "/")
        expected[relative] = hashlib.sha256(f6.norm(text).encode("utf-8")).hexdigest()
    if len(expected) != 156:
        raise ValueError(f"expected 156 output paths, found {len(expected)}")

    if args.dry_run:
        action = "validated"
    elif args.audit_existing:
        existing = ROOT / DEST
        mismatches, _ = compare_tree(expected, existing)
        if mismatches:
            raise ValueError("existing tree differs: " + "; ".join(mismatches[:12]))
        action = "audited existing tree"
    elif args.apply:
        destination = ROOT / DEST
        if destination.exists():
            raise ValueError("destination already exists; refusing to overwrite")
        write_tree(builder, destination, DEST)
        mismatches, _ = compare_tree(expected, destination)
        if mismatches:
            raise ValueError("generated tree differs: " + "; ".join(mismatches[:12]))
        action = "generated tree"
    else:
        target = args.reproduce_to.expanduser().resolve()
        if target.exists() or target == ROOT or ROOT in target.parents:
            raise ValueError("reproduction target must be absent and outside the repository")
        write_tree(builder, target, DEST)
        mismatches, actual = compare_tree(expected, target)
        if mismatches:
            raise ValueError("isolated reproduction differs: " + "; ".join(mismatches[:12]))
        action = "isolated reproduction matched"

    if input_snapshot() != input_before or prior_tree_snapshot() != prior_before:
        raise ValueError("protected sources or prior phases changed")
    print(json.dumps({
        "result": "OK", "action": action, "base": BASE,
        "units": len(ORDER), "subjects": sum(len(u["assuntos"]) for u in manifest["unidades"].values()),
        "files": len(builder.outputs), "mappings": len(builder.records),
        "types": types, "links_resolved": builder.link_stats.get("markdown_relativos_resolvidos", 0),
        "wikilinks": builder.link_stats.get("wikilinks_preservados", 0),
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
