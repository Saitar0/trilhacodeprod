from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import inspect
import json
import posixpath
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "migracao"))
import _migrar_fase9 as f9

MANIFEST_REL = "docs/migracao/mapa_de_migracao_fase10.yml"
PLAN_REL = "docs/migracao/PLANEJAMENTO_FASE10.md"
DEST_REL = "docs/courses/trilhacode/Conteudos_migrado/Fase_10"
SOURCE_ROOT = "docs/courses/trilhacode/Conteudos/Fase_10"
BASE = "2f3d8977e7d6c7a74e5f11abc4dec7e66660bc4d"
JSON_REL = "docs/courses/trilhacode/trilha-code-bulk-import.json"
GUIDE_REL = "docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md"
PHASE_PAGE = "docs/courses/trilhacode/Fase_10_IA_Aplicada_e_Posicionamento.md"
PHASE_REFS = "docs/courses/trilhacode/Referencias_Fase_10.md"
MAPPING_REL = "docs/migracao/relatorio_mapeamento_fase10.csv"
VALIDATION_REL = "docs/migracao/relatorio_validacao_fase10.md"
AUDIT_REL = "docs/migracao/auditoria_final_fase10.md"
PRIOR_COUNTS = {1: 221, 2: 144, 3: 313, 4: 395, 5: 483, 6: 449, 7: 156, 8: 124, 9: 301}
PRIOR_TOTAL = sum(PRIOR_COUNTS.values())
OFFICIAL_ORDER = [
    "47.1", "48.1", "48.2", "49.1", "50.1", "51.1", "52.1", "52.2",
    "53.1", "53.2", "53.3", "53.4",
]
EXPECTED_TYPES = {
    "topic_index": 12, "objetivo": 12, "resumo": 12, "criterio": 12,
    "conexoes": 12, "referencias": 12, "theory": 40, "quiz": 50,
    "answer_key": 50, "practice": 30, "answer_key_pratica": 30,
    "rubric": 12, "project_scope": 2, "project_milestone": 8, "checklist": 10,
}
REPORT_FILES = (MAPPING_REL, VALIDATION_REL, AUDIT_REL)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def same_source_block(actual: str, declared: str) -> bool:
    # Faixas de linhas incluem o terminador da última linha; o manifesto registra
    # o conteúdo literal sem esse delimitador estrutural.
    if actual == declared:
        return True
    suffix = actual[len(declared):] if actual.startswith(declared) else None
    return suffix in ("\n", "\n\n")


def safe_rel(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"caminho relativo inseguro: {value!r}")
    return path


def load_manifest() -> dict:
    path = ROOT / MANIFEST_REL
    manifest = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=f9.f8.UniqueKeyLoader)
    identity = (
        manifest.get("fase"), manifest.get("status_manifesto"), manifest.get("base_commit"),
        manifest.get("id_prefix"), manifest.get("destino_raiz"), manifest.get("ordem_unidades"),
    )
    expected = (
        "Fase_10", "aprovado_com_ressalvas_para_execucao", BASE, "f10", DEST_REL, OFFICIAL_ORDER,
    )
    if identity != expected or list(manifest.get("unidades", {})) != OFFICIAL_ORDER:
        raise ValueError(f"identidade/ordem do manifesto divergente: {identity!r}")
    return manifest


def tree_hashes(directory: Path) -> dict[str, str]:
    if not directory.is_dir():
        raise ValueError(f"diretório ausente: {directory}")
    return {
        path.relative_to(directory).as_posix(): sha_file(path)
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def prior_tree_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    root = ROOT / "docs/courses/trilhacode/Conteudos_migrado"
    for number, expected in PRIOR_COUNTS.items():
        current = tree_hashes(root / f"Fase_{number}")
        if len(current) != expected:
            raise ValueError(f"Fase {number}: esperados {expected} arquivos, encontrados {len(current)}")
        result.update({f"Fase_{number}/{path}": value for path, value in current.items()})
    if len(result) != PRIOR_TOTAL:
        raise ValueError(f"total anterior divergente: {len(result)} != {PRIOR_TOTAL}")
    return result


def prior_ids() -> set[str]:
    found: set[str] = set()
    root = ROOT / "docs/courses/trilhacode/Conteudos_migrado"
    for number in PRIOR_COUNTS:
        for path in (root / f"Fase_{number}").rglob("*.md"):
            _, fields, _ = f9.engine.fm(read_text(path), str(path))
            ident = fields.get("arquivo_id")
            if not ident or ident in found:
                raise ValueError(f"arquivo_id anterior ausente/duplicado: {path}: {ident!r}")
            found.add(ident)
    if len(found) != PRIOR_TOTAL:
        raise ValueError(f"esperados {PRIOR_TOTAL} IDs anteriores, encontrados {len(found)}")
    return found


def untracked_hashes() -> dict[str, str]:
    paths = [p for p in git("ls-files", "--others", "--exclude-standard").splitlines() if p]
    return {path.replace("\\", "/"): sha_file(ROOT / Path(path)) for path in paths if (ROOT / Path(path)).is_file()}


def protected_snapshot() -> dict[str, str]:
    source_root = ROOT / "docs/courses/trilhacode/Conteudos"
    result = {
        path.relative_to(ROOT).as_posix(): sha_file(path)
        for path in sorted(source_root.rglob("*")) if path.is_file()
    }
    for rel in (JSON_REL, GUIDE_REL, PHASE_PAGE, PHASE_REFS):
        path = ROOT / Path(*safe_rel(rel).parts)
        if not path.is_file():
            raise ValueError(f"fonte protegida ausente: {rel}")
        result[rel] = sha_file(path)
    return result


def preflight(mode: str) -> None:
    top = Path(git("rev-parse", "--show-toplevel")).resolve()
    if top != ROOT.resolve():
        raise ValueError(f"raiz de worktree incorreta: {top}")
    if git("branch", "--show-current") != "migracao-estrutura":
        raise ValueError("branch diferente de migracao-estrutura")
    if git("rev-parse", "HEAD") != BASE:
        raise ValueError(f"HEAD diferente da base aprovada {BASE}")
    if git("diff", "--cached", "--name-only") or git("diff", "--name-only"):
        raise ValueError("há alterações staged ou rastreadas; geração interrompida")
    destination = ROOT / DEST_REL
    if mode == "apply" and any((ROOT / rel).exists() for rel in REPORT_FILES):
        raise ValueError("um ou mais relatórios Fase 10 já existem; não sobrescrever")


def source_data_and_validate(manifest: dict, prior: set[str]) -> tuple[dict, dict]:
    active = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / SOURCE_ROOT).glob("*.md") if path.is_file()
    }
    declared = {unit["origem"] for unit in manifest["unidades"].values()}
    if active != declared or len(active) != 12:
        raise ValueError(f"fontes oficiais divergentes: faltam={sorted(declared-active)}, extras={sorted(active-declared)}")
    if len(manifest["unidades"]) != 12 or manifest["ordem_unidades"] != OFFICIAL_ORDER:
        raise ValueError("o manifesto não contém as 12 unidades oficiais na ordem aprovada")

    data: dict[str, dict] = {}
    all_paths: set[str] = set()
    all_ids = set(prior)
    types: Counter[str] = Counter()
    conventional_subjects = 0
    quizzes = practices = flashcards = 0
    for uid, unit in manifest["unidades"].items():
        if unit.get("key") != uid:
            raise ValueError(f"{uid}: key do manifesto não corresponde ao ID")
        source_rel = safe_rel(unit["origem"]).as_posix()
        source_path = ROOT.joinpath(*safe_rel(source_rel).parts)
        raw = read_text(source_path)
        if sha_file(source_path) != unit.get("sha256_origem"):
            raise ValueError(f"{uid}: SHA-256 da fonte difere do manifesto")
        title, metadata, _ = f9.f4.parse_header(raw, unit, source_rel)
        if title != unit.get("titulo_original") or metadata != unit.get("metadados_originais"):
            raise ValueError(f"{uid}: título/metadados originais divergentes")
        data[uid] = {"raw": raw, "title": title, "metadata": metadata, "path": source_rel}

        subjects = unit.get("assuntos", [])
        if any(not isinstance(item, dict) or not item.get("slug") for item in subjects) and uid not in ("52.1", "52.2"):
            raise ValueError(f"{uid}: assunto sem slug/título no manifesto")
        conventional_subjects += len(subjects)
        coverage = unit.get("cobertura", {}).get("por_assunto", {})
        slugs = {item["slug"] for item in subjects if isinstance(item, dict)}
        if set(coverage) != slugs:
            raise ValueError(f"{uid}: slugs de cobertura não correspondem às pastas de assunto")

        files = unit.get("arquivos", {})
        for alias, spec in files.items():
            if not spec.get("path") or not spec.get("arquivo_id"):
                raise ValueError(f"{uid}/{alias}: arquivo sem path/arquivo_id")
            path = (safe_rel(unit["pasta"]) / safe_rel(spec["path"])).as_posix()
            if path in all_paths:
                raise ValueError(f"caminho físico repetido: {path}")
            all_paths.add(path)
            ident = spec["arquivo_id"]
            if not ident.startswith("f10-") or ident in all_ids:
                raise ValueError(f"arquivo_id ausente, prefixo incorreto ou colisão: {ident}")
            all_ids.add(ident)
            types[spec["tipo"]] += 1
            if alias == "IDX":
                if spec["path"] != "README.md" or spec["tipo"] != "topic_index":
                    raise ValueError(f"{uid}: IDX precisa ser README.md/topic_index")
                continue
            origin = spec.get("origem", {})
            if origin.get("arquivo_origem") != source_rel:
                raise ValueError(f"{uid}/{alias}: caminho de origem divergente")
            if spec["tipo"] in ("quiz", "answer_key"):
                quizzes += spec["tipo"] == "quiz"
            elif spec["tipo"] == "practice":
                practices += 1
            elif spec["tipo"] == "flashcards":
                flashcards += len(spec.get("itens_origem", []))
            subject = spec.get("assunto")
            shared = spec.get("assuntos")
            first = PurePosixPath(spec["path"]).parts[0]
            if subject:
                if subject not in slugs or first != subject or shared:
                    raise ValueError(f"{uid}/{alias}: assunto exclusivo não corresponde ao caminho")
            if shared:
                if len(shared) < 2 or first != "90_integracao" or any(value not in slugs for value in shared):
                    raise ValueError(f"{uid}/{alias}: item compartilhado precisa de um destino 90_integracao e assuntos válidos")
            if first == "90_integracao" and not shared and spec["tipo"] not in ("rubric",):
                raise ValueError(f"{uid}/{alias}: arquivo de integração sem assuntos declarados")

        # Associa cada quiz/prática a exatamente um par físico Q/K ou P/feedback.
        aliases_by_item: dict[tuple[str, str], list[str]] = {}
        for alias, spec in files.items():
            kind = spec["tipo"]
            item = spec.get("item_origem")
            if item and kind in ("quiz", "answer_key", "practice", "answer_key_pratica"):
                aliases_by_item.setdefault((kind, str(item)), []).append(alias)
        for question in unit.get("questoes", []):
            qid, kid = question["id"], question["resposta_id"]
            q_alias = next((a for a, s in files.items() if s["tipo"] == "quiz" and s.get("item_origem") == qid), None)
            k_alias = next((a for a, s in files.items() if s["tipo"] == "answer_key" and s.get("item_origem") == qid), None)
            if not q_alias or not k_alias or files[k_alias].get("responde_a") != q_alias:
                raise ValueError(f"{uid}/{qid}: quiz/gabarito não formam par único")
            expected_shared = len(question["assuntos"]) > 1
            for alias in (q_alias, k_alias):
                spec = files[alias]
                if spec.get("assunto") and spec["assunto"] not in question["assuntos"]:
                    raise ValueError(f"{uid}/{qid}: assunto exclusivo contradiz o registro de cobertura")
                if expected_shared and (spec.get("assuntos") != question["assuntos"] or not spec["path"].startswith("90_integracao/")):
                    raise ValueError(f"{uid}/{qid}: item compartilhado sem destino único/contexto aprovado")
            if len(aliases_by_item.get(("quiz", qid), [])) != 1 or len(aliases_by_item.get(("answer_key", qid), [])) != 1:
                raise ValueError(f"{uid}/{qid}: item físico duplicado")
        for practice in unit.get("praticas", []):
            pid, feedback_id = practice["id"], practice["feedback_id"]
            p_alias = next((a for a, s in files.items() if s["tipo"] == "practice" and s.get("item_origem") == pid), None)
            f_alias = next((a for a, s in files.items() if s["tipo"] == "answer_key_pratica" and s.get("item_origem") == pid), None)
            if not p_alias or not f_alias or files[f_alias].get("responde_a") != p_alias:
                raise ValueError(f"{uid}/{pid}: prática/feedback não formam par único")
            if len(practice["assuntos"]) > 1:
                for alias in (p_alias, f_alias):
                    if files[alias].get("assuntos") != practice["assuntos"] or not files[alias]["path"].startswith("90_integracao/"):
                        raise ValueError(f"{uid}/{pid}: item compartilhado duplicado ou com caminho/contexto incorreto")
            if len(aliases_by_item.get(("practice", pid), [])) != 1 or len(aliases_by_item.get(("answer_key_pratica", pid), [])) != 1:
                raise ValueError(f"{uid}/{pid}: prática/feedback físico duplicado")

        if "projeto" in unit:
            project = unit["projeto"]
            if len(project.get("marcos", [])) != 4:
                raise ValueError(f"{uid}: projeto precisa preservar quatro entregas")
            for milestone in project["marcos"]:
                if milestone["id"] not in files or milestone["aceite_id"] not in files:
                    raise ValueError(f"{uid}: alias de entrega/aceite ausente")
            checklist = files[project["checklist_final"]]
            if checklist.get("quantidade_itens") != project.get("checklist_itens"):
                raise ValueError(f"{uid}: contagem do checklist final diverge")
            rubric = files[project["rubrica"]]
            if rubric.get("escala_rubrica") != "0–2":
                raise ValueError(f"{uid}: escala original do projeto não é 0–2")

    if conventional_subjects != 40:
        raise ValueError(f"esperados 40 assuntos convencionais, encontrados {conventional_subjects}")
    if dict(types) != EXPECTED_TYPES or len(all_paths) != 304:
        raise ValueError(f"tipos/caminhos diferem do manifesto aprovado: {dict(types)}, {len(all_paths)}")
    if len(all_ids) != PRIOR_TOTAL + 304:
        raise ValueError(f"colisão/ausência de IDs: total {len(all_ids)}")
    if quizzes != 50 or practices != 30 or flashcards != 0:
        raise ValueError(f"avaliações diferem das fontes: Q={quizzes}, P={practices}, cards={flashcards}")
    if len([p for p in (ROOT / "docs/courses/trilhacode/Conteudos").rglob("*") if p.is_file()]) != 133:
        raise ValueError("o inventário das 133 fontes protegidas mudou; revalidar o escopo")
    q49 = next(q for q in manifest["unidades"]["49.1"]["questoes"] if q["id"] == "Q02")
    if q49["assuntos"] != ["02_embeddings_e_recuperacao"]:
        raise ValueError("49.1/Q02 deixou de pertencer a recuperação e filtros de busca")
    totals = Counter()
    for unit in manifest["unidades"].values():
        totals.update(unit.get("cobertura", {}).get("E_S_N", {}))
    if (totals["E"], totals["S"], totals["N"]) != (36, 4, 0):
        raise ValueError(f"cobertura E/S/N divergente: {totals['E']}/{totals['S']}/{totals['N']}")
    if manifest.get("estimativa_arquivos", {}).get("total") != 304:
        raise ValueError("estimativa aprovada não é 304")
    if manifest["estimativa_arquivos"].get("por_tipo") != dict(types):
        raise ValueError("estimativa por tipo não corresponde aos arquivos declarados")
    if manifest["estimativa_arquivos"].get("por_unidade") != {uid: len(unit["arquivos"]) for uid, unit in manifest["unidades"].items()}:
        raise ValueError("estimativa por unidade não corresponde aos aliases declarados")

    expected_s_only = {
        ("51.1", "01_ativos_fronteiras_confianca"),
        ("53.1", "04_selecao_apresentacao_evidencias"),
        ("53.3", "01_requisitos_e_delimitacao"),
        ("53.4", "01_entender_problema_antes_codificar"),
    }
    actual_s_only = {
        (uid, slug)
        for uid, unit in manifest["unidades"].items()
        for slug, value in unit.get("cobertura", {}).get("por_assunto", {}).items() if value == "S"
    }
    if actual_s_only != expected_s_only:
        raise ValueError(f"assuntos S-only divergentes: {actual_s_only}")
    for uid, expected_dimensions in (("52.1", 8), ("52.2", 6)):
        project = manifest["unidades"][uid]["projeto"]
        rubric = manifest["unidades"][uid]["arquivos"][project["rubrica"]]
        checklist = manifest["unidades"][uid]["arquivos"][project["checklist_final"]]
        if rubric.get("dimensoes") != expected_dimensions or checklist.get("quantidade_itens") != (10 if uid == "52.1" else 8):
            raise ValueError(f"{uid}: dimensões da rubrica ou checklist divergem da fonte")
        if uid == "52.1" and "13/16" not in rubric.get("origem", {}).get("texto_literal", ""):
            raise ValueError("52.1: limiar 13/16 não foi preservado")
        if uid == "52.2":
            if len(project.get("variacoes", [])) != 3:
                raise ValueError("52.2: as três variações T6 não foram preservadas")
            if "10/12" not in rubric.get("origem", {}).get("texto_literal", ""):
                raise ValueError("52.2: limiar 10/12 não foi preservado")
    return data, {"paths": len(all_paths), "ids": 304, "types": dict(types), "E_S_N": dict(totals)}


def validate_literals(manifest: dict, sources: dict) -> dict:
    for uid, unit in manifest["unidades"].items():
        raw = sources[uid]["raw"]
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            origin = spec.get("origem", {})
            start = origin.get("linha_inicio")
            end = origin.get("linha_fim")
            if start and end:
                text, _, _ = f9.f6.slice_lines(raw, start, end)
                literal = origin.get("texto_literal")
                if literal is not None and not same_source_block(text, literal):
                    raise ValueError(f"{uid}/{alias}: texto_literal difere das linhas de origem")
            kind = spec["tipo"]
            if kind == "rubric" and uid not in ("52.1", "52.2"):
                if not origin.get("texto_literal") or not start:
                    raise ValueError(f"{uid}/{alias}: rubrica prática sem bloco literal")
                continue
            if kind in ("objetivo", "resumo", "criterio", "conexoes", "referencias", "project_scope", "rubric"):
                selector = origin.get("seletor_literal") or origin.get("seletor")
                if not selector:
                    raise ValueError(f"{uid}/{alias}: seletor de seção ausente")
                span = f9.f8.heading_range(raw, selector)
                if start and (span["inicio"], span["fim"]) != (start, end):
                    raise ValueError(f"{uid}/{alias}: limites da seção divergem do manifesto")
            elif kind == "theory":
                selector = origin.get("seletor_literal") or origin.get("seletor")
                span = f9.resolve_theory_selector(raw, selector)
                if start and (span["inicio"], span["fim"]) != (start, end):
                    raise ValueError(f"{uid}/{alias}: limites de teoria divergem do seletor literal")
            elif kind in ("quiz", "answer_key"):
                selector = origin["seletor"]
                span = f9.selector_range(raw, selector)
                if not same_source_block(span["text"], origin.get("texto_literal", "")):
                    raise ValueError(f"{uid}/{alias}: texto integral de questão/gabarito diverge")
                marker = origin["separacao_resposta"]["marcador_literal"]
                if span["text"].count(marker) != 1:
                    raise ValueError(f"{uid}/{alias}: marcador de resposta ausente/ambíguo")
            elif kind == "practice":
                span = f9.selector_range(raw, origin["seletor"])
                if not span["text"].strip():
                    raise ValueError(f"{uid}/{alias}: bloco de prática vazio")
            elif kind == "answer_key_pratica":
                if not origin.get("texto_literal"):
                    raise ValueError(f"{uid}/{alias}: feedback sem literal de origem")
            elif kind == "project_milestone":
                selector = origin["seletor"]
                source_lines = raw.splitlines(keepends=True)
                expected_title = re.sub(r"^###\s+Entrega\s+[1-4]\s+—\s+", "", selector)
                if (not start or source_lines[start - 1].strip() != selector
                        or expected_title != origin.get("titulo_marco_literal")
                        or spec.get("titulo_marco") != origin.get("titulo_marco_literal")):
                    raise ValueError(f"{uid}/{alias}: entrega/título literal diverge da fonte")
            elif kind == "checklist":
                if spec.get("marco_ref"):
                    if not origin.get("texto_literal", "").startswith("**Critérios de aceite:**"):
                        raise ValueError(f"{uid}/{alias}: aceite de projeto diverge do marcador literal")
                else:
                    selector = origin.get("seletor_literal") or origin.get("seletor")
                    span = f9.f8.heading_range(raw, selector)
                    if not same_source_block(span["text"], origin.get("texto_literal", "")):
                        raise ValueError(f"{uid}/{alias}: checklist final difere da fonte")

        for question in unit.get("questoes", []):
            alias = next(a for a, spec in unit["arquivos"].items() if spec["tipo"] == "quiz" and spec.get("item_origem") == question["id"])
            origin = unit["arquivos"][alias]["origem"]
            full = f9.selector_range(raw, origin["seletor"])["text"]
            marker = origin["separacao_resposta"]["marcador_literal"]
            at = full.index(marker)
            answer_at = at + len(marker) - 2 if marker.startswith("? ") else at
            answer_block = full[answer_at:].rstrip("\r\n")
            if marker.startswith("? "):
                if answer_block != question["resposta_literal"]:
                    raise ValueError(f"{uid}/{question['id']}: resposta sem rótulo diverge do manifesto")
            else:
                suffix = answer_block[len(marker):]
                if not suffix.startswith(" ") or suffix[1:] != question["resposta_literal"]:
                    raise ValueError(f"{uid}/{question['id']}: resposta inline diverge do manifesto")
            question_prefix = full[:answer_at]
            if question_prefix.endswith(" "):
                question_prefix = question_prefix[:-1]
            question_prefix = re.sub(r"^\d+\.\s+", "", question_prefix)
            if question_prefix != question["enunciado"]:
                raise ValueError(f"{uid}/{question['id']}: enunciado não corresponde ao segmento literal")
    return {"questions": sum(len(u.get("questoes", [])) for u in manifest["unidades"].values())}


def adapt_manifest(manifest: dict, sources: dict) -> dict:
    """Adapta o esquema F10 ao Builder genérico, sem mudar textos de origem."""
    runtime_manifest = copy.deepcopy(manifest)
    runtime_manifest["normalizacoes_estruturais_autorizadas"] = {"links_markdown": []}
    runtime_manifest["estimativa_arquivos"] = {"total": manifest["estimativa_arquivos"]["total"]}
    for rule in runtime_manifest.get("normalizacoes_links_relativos_planejadas", []):
        if rule.get("destino_repositorio") != GUIDE_REL or rule.get("destino_rastreado") is not True:
            raise ValueError(f"normalização do guia sem alvo relativo/rastreado: {rule}")
        if git("ls-files", "--error-unmatch", GUIDE_REL) == "":
            raise ValueError("guia de projetos não está rastreado")
        target = ROOT / GUIDE_REL
        if not target.is_file():
            raise ValueError("destino aprovado do guia não existe")
        source_unit = manifest["unidades"].get(rule["unidade"])
        if not source_unit or source_unit["origem"] != rule["origem"]:
            raise ValueError(f"unidade/origem da normalização divergente: {rule}")
        if rule["href_origem"] not in sources[rule["unidade"]]["raw"]:
            raise ValueError(f"href original ausente: {rule}")
        destination = PurePosixPath(rule["arquivo_destino"])
        if not destination.is_relative_to(PurePosixPath(DEST_REL) / source_unit["pasta"]):
            raise ValueError(f"normalização aponta para arquivo fora da unidade: {rule}")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(rule["arquivo_destino"]), rule["href_destino"]))
        if resolved != GUIDE_REL:
            raise ValueError(f"href migrado não resolve para o guia aprovado: {resolved}")
        runtime_rule = dict(rule)
        runtime_rule["secao_origem"] = rule.get("secao_origem", "## Referências")
        runtime_rule["destino_repositorio"] = GUIDE_REL
        runtime_rule["destino_rastreado"] = True
        runtime_manifest["normalizacoes_estruturais_autorizadas"]["links_markdown"].append({
            "unidade": rule["unidade"], "origem_literal": rule["href_origem"],
            "destino_literal": rule["href_destino"], "ocorrencias_esperadas": 1,
        })
        rule.update(runtime_rule)

    for uid, unit in runtime_manifest["unidades"].items():
        # O adaptador homologado recebe slugs; o manifesto F10 mantém slug e título.
        unit["assuntos"] = [item["slug"] for item in unit.get("assuntos", [])]
        files = unit["arquivos"]
        practice_by_item = {
            spec.get("item_origem"): (alias, spec)
            for alias, spec in files.items() if spec["tipo"] == "practice"
        }
        for alias, spec in files.items():
            origin = spec.get("origem")
            if not isinstance(origin, dict):
                continue
            if "seletor" not in origin and origin.get("seletor_literal"):
                origin["seletor"] = origin["seletor_literal"]
            if spec["tipo"] == "project_scope" and origin.get("linha_inicio") and origin.get("linha_fim"):
                origin["linhas"] = {"inicio": origin["linha_inicio"], "fim": origin["linha_fim"]}
            if spec["tipo"] in ("quiz", "answer_key"):
                separation = origin.get("separacao_resposta", {})
                if separation.get("marcador_literal"):
                    origin["marcador_literal"] = separation["marcador_literal"]
            if spec["tipo"] in ("answer_key_pratica", "rubric") and spec.get("item_origem") in practice_by_item:
                practice_spec = practice_by_item[spec["item_origem"]][1]
                marker = origin.get("marcador_literal") or origin.get("seletor_literal") or origin.get("seletor")
                if not marker:
                    raise ValueError(f"{uid}/{alias}: marcador literal de feedback/rubrica ausente")
                origin["marcador_literal"] = marker
                origin["seletor"] = practice_spec["origem"]["seletor"] + " > " + marker

        if "projeto" in unit:
            project = unit["projeto"]
            for milestone in project["marcos"]:
                milestone_spec = files[milestone["id"]]
                acceptance_spec = files[milestone["aceite_id"]]
                milestone_spec["marco_id"] = milestone["id"]
                # O builder valida a igualdade com o cabeçalho literal; depois remove apenas o prefixo Markdown.
                milestone_spec["titulo_marco"] = milestone_spec["origem"]["seletor"]
                acceptance_spec["marco_id"] = milestone["id"]
                acceptance_spec["titulo_marco"] = milestone["titulo_marco"]
                marker = acceptance_spec["origem"].get("marcador_literal") or acceptance_spec["origem"].get("seletor")
                acceptance_spec["origem"]["marcador_literal"] = marker
                acceptance_spec["origem"]["seletor"] = milestone_spec["origem"]["seletor"] + " > " + marker
    return runtime_manifest


def build(manifest: dict, sources: dict):
    runtime_manifest = adapt_manifest(manifest, sources)
    # build_runtime usa DEST_REL global; ajuste antes de construir o runtime para
    # evitar que os arquivos da Fase 10 apontem para o diretório da Fase 9.
    f9.ORDER = manifest["ordem_unidades"]
    f9.DEST_REL = manifest["destino_raiz"]
    runtime = f9.build_runtime(runtime_manifest, sources)
    for uid, unit in runtime["unidades"].items():
        declared = manifest["unidades"][uid]
        if "projeto" in declared:
            project = unit["blocos_origem"]["projeto"]
            final_alias = declared["projeto"]["checklist_final"]
            final_spec = runtime_manifest["unidades"][uid]["arquivos"][final_alias]
            selector = final_spec["origem"].get("seletor_literal") or final_spec["origem"].get("seletor")
            span = f9.f8.heading_range(sources[uid]["raw"], selector)
            final_spec["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
            unit["arquivos"][final_alias]["origem"]["linhas"] = {"inicio": span["inicio"], "fim": span["fim"]}
            project["checklist"] = {"arquivo": final_alias, "itens": declared["projeto"]["checklist_itens"]}
        else:
            rubric_alias, rubric = next(
                (alias, spec) for alias, spec in runtime_manifest["unidades"][uid]["arquivos"].items()
                if spec["tipo"] == "rubric"
            )
            lines = {"inicio": rubric["origem"]["linha_inicio"], "fim": rubric["origem"]["linha_fim"]}
            rubric["origem"]["linhas"] = lines
            rubric["itens_origem"] = rubric["aplica_a"]
            unit["arquivos"][rubric_alias]["origem"]["linhas"] = lines
            unit["arquivos"][rubric_alias]["itens_origem"] = rubric["aplica_a"]
            raw = sources[uid]["raw"]
            source_lines = raw.splitlines(keepends=True)
            rubric_start_line, rubric_end_line = lines["inicio"], lines["fim"]
            candidates = [
                (alias, spec) for alias, spec in unit["arquivos"].items()
                if spec["tipo"] == "practice"
                and spec["origem"]["linhas"]["inicio"] <= rubric_start_line <= spec["origem"]["linhas"]["fim"]
            ]
            if len(candidates) != 1:
                raise ValueError(f"{uid}/{rubric_alias}: rubrica não está em exatamente uma prática de origem")
            practice_alias, _ = candidates[0]
            practice_record = unit["blocos_origem"]["praticas"][practice_alias]
            practice_lines = unit["arquivos"][practice_alias]["origem"]["linhas"]
            practice_offset = sum(len(line) for line in source_lines[:practice_lines["inicio"] - 1])
            rubric_offset = sum(len(line) for line in source_lines[:rubric_start_line - 1]) - practice_offset
            rubric_end_offset = sum(len(line) for line in source_lines[:rubric_end_line]) - practice_offset
            full_practice, _, _ = f9.f6.slice_lines(raw, practice_lines["inicio"], practice_lines["fim"])
            rubric_text, _, _ = f9.f6.slice_lines(raw, rubric_start_line, rubric_end_line)
            if full_practice[rubric_offset:rubric_end_offset] != rubric_text:
                raise ValueError(f"{uid}/{rubric_alias}: rubrica não coincide com sua faixa literal dentro da prática")
            containing = [segment for segment in practice_record["segments"] if segment["start"] < rubric_offset < segment["end"]]
            if len(containing) != 1:
                raise ValueError(f"{uid}/{rubric_alias}: marcador de rubrica não divide unicamente os segmentos da prática")
            containing[0]["end"] = rubric_offset
            practice_record["segments"].append({
                "start": rubric_offset, "end": rubric_end_offset, "alias": rubric_alias,
                "type": "rubric", "marker": rubric["origem"]["texto_literal"],
            })
            practice_record["segments"].sort(key=lambda segment: segment["start"])
            practice_record["rubrica"] = rubric_alias

    # O adaptador de Fase 9 só precisa deixar dinâmica a guarda do total de arquivos.
    source = inspect.getsource(f9.configure_builder)
    source = source.replace(
        "def configure_builder(runtime: dict, manifest: dict, source_data: dict):",
        "def configure_builder_f10(runtime: dict, manifest: dict, source_data: dict):", 1,
    )
    old_guard = "if len(builder.outputs) != 301:"
    old_error = 'raise ValueError(f"expected 301 generated files, found {len(builder.outputs)}")'
    if source.count(old_guard) != 1 or source.count(old_error) != 1:
        raise ValueError("a guarda de contagem do adaptador da Fase 9 mudou; revisão manual necessária")
    source = source.replace(old_guard, 'if len(builder.outputs) != manifest["estimativa_arquivos"]["total"]:', 1)
    source = source.replace(old_error, 'raise ValueError("quantidade gerada difere da estimativa do manifesto")', 1)
    exec(compile(source, "<adaptador-fase10>", "exec"), f9.__dict__)
    f9.ORDER = manifest["ordem_unidades"]
    f9.DEST_REL = manifest["destino_raiz"]
    return f9.configure_builder_f10(runtime, runtime_manifest, sources)


def validate_literals_and_mappings(manifest: dict, sources: dict, builder) -> dict:
    for uid, unit in manifest["unidades"].items():
        raw = sources[uid]["raw"]
        for alias, spec in unit["arquivos"].items():
            if alias == "IDX":
                continue
            origin = spec.get("origem", {})
            start, end = origin.get("linha_inicio"), origin.get("linha_fim")
            kind = spec["tipo"]
            if start and end and origin.get("texto_literal") is not None:
                literal, _, _ = f9.f6.slice_lines(raw, start, end)
                if not same_source_block(literal, origin["texto_literal"]):
                    raise ValueError(f"{uid}/{alias}: texto_literal não corresponde à faixa fonte")
            if kind == "theory":
                selector = origin.get("seletor_literal") or origin.get("seletor")
                span = f9.resolve_theory_selector(raw, selector)
                if start and (span["inicio"], span["fim"]) != (start, end):
                    raise ValueError(f"{uid}/{alias}: faixa de microtópico divergente")
            elif kind in ("quiz", "answer_key"):
                full = f9.selector_range(raw, origin["seletor"])["text"]
                if not same_source_block(full, origin.get("texto_literal", "")):
                    raise ValueError(f"{uid}/{alias}: texto de quiz/gabarito não confere com a fonte")
            elif kind in ("practice", "answer_key_pratica"):
                if kind == "practice":
                    if not f9.selector_range(raw, origin["seletor"])["text"].strip():
                        raise ValueError(f"{uid}/{alias}: seletor da prática vazio")
                elif not origin.get("texto_literal"):
                    raise ValueError(f"{uid}/{alias}: feedback/solução sem texto de origem")
            elif kind == "project_milestone":
                lines = raw.splitlines(keepends=True)
                if lines[start - 1].strip() != origin["seletor"]:
                    raise ValueError(f"{uid}/{alias}: texto da entrega diverge da fonte")
            elif kind == "checklist" and spec.get("marco_ref"):
                if not origin.get("texto_literal", "").startswith("**Critérios de aceite:**"):
                    raise ValueError(f"{uid}/{alias}: bloco de aceite diverge da fonte")

        for question in unit.get("questoes", []):
            alias = next(a for a, s in unit["arquivos"].items() if s["tipo"] == "quiz" and s.get("item_origem") == question["id"])
            origin = unit["arquivos"][alias]["origem"]
            full = f9.selector_range(raw, origin["seletor"])["text"]
            marker = origin["separacao_resposta"]["marcador_literal"]
            if full.count(marker) != 1:
                raise ValueError(f"{uid}/{question['id']}: limite de resposta inline não é único")
            index = full.index(marker)
            answer_start = index + len(marker) - 2 if marker.startswith("? ") else index
            question_text = full[:answer_start]
            answer_text = full[answer_start:].rstrip("\r\n")
            # Em itens numerados, o prefixo "N. " é removido do arquivo Q; nenhuma outra palavra muda.
            if question_text.endswith(" "):
                question_text = question_text[:-1]
            question_text = re.sub(r"^\d+\.\s+", "", question_text)
            if question_text != question["enunciado"]:
                raise ValueError(f"{uid}/{question['id']}: enunciado separado diverge do manifesto")
            if marker.startswith("? "):
                if answer_text != question["resposta_literal"]:
                    raise ValueError(f"{uid}/{question['id']}: gabarito sem rótulo diverge")
            else:
                suffix = answer_text[len(marker):]
                if not suffix.startswith(" ") or suffix[1:] != question["resposta_literal"]:
                    raise ValueError(f"{uid}/{question['id']}: gabarito inline diverge")

    coverage = f9.audit_origin_coverage(builder)
    if sum(info["mapping_segments"] for info in coverage.values()) < 300:
        raise ValueError("a auditoria textual cobriu menos segmentos que o inventário de conteúdo")
    return coverage


def validate_outputs(manifest: dict, previous_ids: set[str], builder, sources: dict) -> dict:
    expected = {}
    types: Counter[str] = Counter()
    ids = set(previous_ids)
    per_unit = {}
    for uid, unit in manifest["unidades"].items():
        root = PurePosixPath(DEST_REL) / safe_rel(unit["pasta"])
        for alias, spec in unit["arquivos"].items():
            path = root / safe_rel(spec["path"])
            if path in expected:
                raise ValueError(f"caminho duplicado: {path}")
            expected[path] = (uid, alias, spec)
            if spec["arquivo_id"] in ids:
                raise ValueError(f"colisão global de arquivo_id: {spec['arquivo_id']}")
            ids.add(spec["arquivo_id"])
            types[spec["tipo"]] += 1
        per_unit[uid] = len(unit["arquivos"])
    if set(expected) != set(builder.outputs):
        missing = sorted(str(p) for p in set(expected) - set(builder.outputs))
        extra = sorted(str(p) for p in set(builder.outputs) - set(expected))
        raise ValueError(f"árvore gerada difere do manifesto: ausentes={missing[:8]} extras={extra[:8]}")
    if dict(types) != EXPECTED_TYPES or len(builder.outputs) != 304:
        raise ValueError(f"contagens de arquivos divergentes: {dict(types)}, {len(builder.outputs)}")

    generated_ids = set()
    hashes = {}
    for path, text in builder.outputs.items():
        header, fields, body = f9.engine.fm(text, str(path))
        match = re.fullmatch(r"---\n(.*?)\n---", header, re.S)
        if not match:
            raise ValueError(f"frontmatter sem delimitadores YAML válidos: {path}")
        parsed = yaml.load(match.group(1), Loader=f9.f8.UniqueKeyLoader)
        if not isinstance(parsed, dict) or parsed != fields:
            raise ValueError(f"frontmatter YAML inválido/duplicado: {path}")
        if not body.strip():
            raise ValueError(f"arquivo vazio: {path}")
        ident = fields.get("arquivo_id")
        if not ident or not ident.startswith("f10-") or ident in generated_ids:
            raise ValueError(f"ID de saída ausente/duplicado/incorreto: {path}: {ident}")
        generated_ids.add(ident)
        if path.name == "README.md":
            uid = next(uid for uid, unit in manifest["unidades"].items() if unit["pasta"] == path.parent.name)
            if fields.get("key") != uid or fields.get("title") != sources[uid]["title"]:
                raise ValueError(f"{uid}: README não preserva key/title")
            for name, value in manifest["unidades"][uid]["metadados_originais"].items():
                if fields.get(name) != value:
                    raise ValueError(f"{uid}: metadado {name} diverge no README")
        else:
            uid, alias, spec = expected[path]
            if fields.get("parent_key") != uid or fields.get("tipo_arquivo") != spec["tipo"]:
                raise ValueError(f"{uid}/{alias}: parent_key/tipo_arquivo incorreto")
            if spec.get("assunto") and fields.get("assunto") != spec["assunto"]:
                raise ValueError(f"{uid}/{alias}: assunto do frontmatter incorreto")
            if spec.get("assuntos") and fields.get("assuntos") != spec["assuntos"]:
                raise ValueError(f"{uid}/{alias}: assuntos compartilhados incorretos")
            if spec.get("titulo_marco"):
                milestone_alias = spec.get("marco_ref", alias)
                milestone_spec = manifest["unidades"][uid]["arquivos"][milestone_alias]
                literal_title = re.sub(r"^#{1,6}\s+", "", milestone_spec["origem"].get("seletor", ""))
                if fields.get("titulo_marco") != literal_title:
                    raise ValueError(f"{uid}/{alias}: titulo_marco não corresponde ao título literal da entrega")
            if spec.get("escala_rubrica") and fields.get("escala_rubrica") != spec["escala_rubrica"]:
                raise ValueError(f"{uid}/{alias}: escala_rubrica incorreta")
        hashes[path.as_posix()] = sha_bytes(f9.f6.norm(text).encode("utf-8"))
    if len(generated_ids) != 304:
        raise ValueError("total de IDs gerados não é 304")
    links = f9.validate_links(builder)
    coverage = validate_literals_and_mappings(manifest, sources, builder)
    return {
        "files": 304, "types": dict(types), "per_unit": per_unit,
        "mappings": len(builder.records), "hashes": hashes, "ids": len(generated_ids),
        "links": links, "coverage": coverage,
    }


def compare_hashes(expected: dict[str, str], actual: dict[str, str]) -> list[str]:
    diffs = []
    for path in sorted(set(expected) | set(actual)):
        if path not in expected:
            diffs.append(f"extra: {path}")
        elif path not in actual:
            diffs.append(f"missing: {path}")
        elif expected[path] != actual[path]:
            diffs.append(f"hash differs: {path}")
    return diffs


def output_relative_hashes(stats: dict) -> dict[str, str]:
    prefix = PurePosixPath(DEST_REL)
    return {PurePosixPath(path).relative_to(prefix).as_posix(): digest for path, digest in stats["hashes"].items()}


def check_preserved(before: dict, prior_before: dict, tracked_before: tuple[str, str]) -> None:
    if (git("branch", "--show-current"), git("rev-parse", "HEAD")) != tracked_before:
        raise ValueError("branch/HEAD mudou durante a migração")
    after = protected_snapshot()
    if after != before:
        changed = sorted(set(after) ^ set(before) | {key for key in set(after)&set(before) if after[key] != before[key]})
        raise ValueError(f"fontes/JSON/docs locais foram alterados: {changed[:20]}")
    current_prior = prior_tree_snapshot()
    if current_prior != prior_before:
        changed = sorted(set(current_prior) ^ set(prior_before) | {key for key in set(current_prior)&set(prior_before) if current_prior[key] != prior_before[key]})
        raise ValueError(f"Fases 1–9 foram alteradas: {changed[:20]}")
    if git("diff", "--cached", "--name-only") or git("diff", "--name-only"):
        raise ValueError("surgiram alterações staged/rastreadas")


def backup_inventory() -> tuple[list[str], list[str]]:
    root = ROOT / "docs/courses/trilhacode/Conteudos"
    names = {"arquivo", "arquivos", "backup", "backups", "legado", "legados"}
    directories, files = [], []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_dir() and path.name.casefold() in names:
            directories.append(path.relative_to(ROOT).as_posix())
        elif path.is_file() and any(part.casefold() in names for part in relative.parts[:-1]):
            files.append(path.relative_to(ROOT).as_posix())
    return sorted(directories), sorted(files)


def write_reports(manifest: dict, stats: dict, coverage: dict, backup_dirs: list[str], backup_files: list[str], repro: dict) -> None:
    types = "\n".join(f"| `{name}` | {count} |" for name, count in sorted(stats["types"].items()))
    units = "\n".join(f"| {uid} — {manifest['unidades'][uid]['titulo_original']} | {count} |" for uid, count in stats["per_unit"].items())
    source_covered = sum(row["mapped_chars"] for row in coverage.values())
    source_total = sum(row["source_chars"] for row in coverage.values())
    links = stats["links"]
    repro_text = "idêntica" if repro["identical"] else "divergente"
    backup_text = "\n".join(f"- `{p}`" for p in backup_dirs) or "- Nenhum diretório de backup/legado com nome reconhecido encontrado sob `Conteudos/`."
    backup_file_text = "\n".join(f"- `{p}`" for p in backup_files) or "- Nenhum arquivo separado foi encontrado dentro desses diretórios."
    normalization_text = "\n".join(
        f"- `{rule['unidade']}`: `{rule['href_origem']}` → `{rule['href_destino']}`; alvo `{rule['destino_repositorio']}` rastreado; rótulo visível preservado."
        for rule in manifest["normalizacoes_links_relativos_planejadas"]
    )
    per_unit_types = []
    for uid, unit in manifest["unidades"].items():
        counts = Counter(spec["tipo"] for spec in unit["arquivos"].values())
        per_unit_types.append(f"| {uid} | {len(unit['assuntos']) if uid not in ('52.1','52.2') else 'projeto'} | {len(unit['arquivos'])} | `{json.dumps(dict(sorted(counts.items())), ensure_ascii=False)}` |")
    validation = f"""# Validação da migração estrutural — Fase 10

**Base:** `{BASE}` · **branch:** `migracao-estrutura` · **resultado técnico:** APROVADA COM RESSALVAS.

## Contagens conferidas

| Unidade | Assuntos | Arquivos | Tipos |
|---|---:|---:|---|
{chr(10).join(per_unit_types)}

| Tipo | Quantidade |
|---|---:|
{types}

- 12 fontes oficiais: dez unidades convencionais e projetos 52.1/52.2; 40 assuntos convencionais.
- 50 quizzes com gabaritos separados; 30 práticas com feedback; nenhum flashcard.
- Dez rubricas de prática em escala 0–4; duas rubricas de projeto em escala 0–2; oito entregas/aceites.
- E/S/N: **36/4/0**. Assuntos S-only: 51.1/`01_ativos_fronteiras_confianca`, 53.1/`04_selecao_apresentacao_evidencias`, 53.3/`01_requisitos_e_delimitacao`, 53.4/`01_entender_problema_antes_codificar`.
    - {stats['mappings']} registros de origem/destino: {stats['metadata_mappings']} conversões de metadados e {stats['mappings']-stats['metadata_mappings']} registros de conteúdo. Texto de cada segmento conferido contra offsets da fonte.
- Cobertura auditada: {source_covered:,} de {source_total:,} caracteres fonte; cabeçalhos de seção restantes são contêineres estruturais mapeados por seus descendentes.

## Projetos

- 52.1: quatro entregas/aceites, checklist de 10 itens, rubrica original de oito dimensões/0–2 e limiar **13/16** preservados.
- 52.2: quatro entregas/aceites, três variações T6, checklist de 8 itens, rubrica original de seis dimensões/0–2 e limiar **10/12** preservados; nenhuma stack selecionada.

## Links e referências

- Links Markdown relativos resolvidos: **{links['resolved']}**; avisos: **{len(links['warnings'])}**; wikilinks preservados: **{links['wikilinks']}**.
- Normalizações estruturais autorizadas:
{normalization_text}
- 47.1 menciona 47.2/47.3 em texto simples; não foram encontradas fontes/destinos correspondentes nem links Markdown. A menção foi preservada sem criar unidades fictícias.
- `consultado_em` foi mantido por referência somente quando presente na fonte; nenhuma data foi inferida.

## Integridade protegida

- Fases 1–9: {PRIOR_TOTAL} arquivos com hashes SHA-256 idênticos ao pré-voo.
- `Conteudos/`: {len([x for x in protected_snapshot() if x.startswith('docs/courses/trilhacode/Conteudos/')])} arquivos verificados; JSON, página e referências gerais da Fase 10 e documentos locais preexistentes preservados.
- Diretórios de backup reconhecidos sob `Conteudos/`:
{backup_text}
- Arquivos efetivamente encontrados nesses diretórios:
{backup_file_text}

## Reprodução isolada

- Reconstrução em diretório temporário: **{repro_text}**; {repro['files']} arquivos, caminhos relativos idênticos, conteúdo SHA-256 idêntico.
- O manifesto declara 304 caminhos; não foram criados arquivos artificiais.
"""
    audit = f"""# Auditoria final — Fase 10

**Veredito técnico: APROVADA COM RESSALVAS**

## Integridade textual e cobertura

- As 12 fontes ativas foram validadas por SHA-256 e metadados antes da construção.
- {stats['mappings']} registros têm origem e destino real; o conteúdo foi comparado por segmento e faixa de origem, não apenas por contagens de palavras.
- 40 microtópicos, 50 pares quiz/gabarito, 30 práticas/feedbacks, dez rubricas práticas, duas rubricas de projeto, oito entregas e oito aceites preservados.
- Q/K recompõe a linha original nos itens rotulados como `Resposta` e nos itens 53.2–53.4 cuja resposta começa após o sinal de pergunta; os enunciados, alternativas e respostas permanecem literais.
- Itens compartilhados ocupam um destino físico único em `90_integracao/`; E/S/N permanece 36/4/0.
- Blocos de código e exemplos foram transportados dentro dos segmentos literais, sem reescrita.

## Projetos e links

- 52.1: 4 entregas, 4 aceites, checklist 10, rubrica original 0–2, limiar 13/16.
- 52.2: 4 entregas, 4 aceites, 3 variações T6, checklist 8, rubrica original 0–2, limiar 10/12.
- Links Markdown relativos: {links['resolved']} resolvidos; {len(links['warnings'])} avisos; {links['wikilinks']} wikilinks mantidos.
- 2 hrefs para `Guia_Projetos_e_Rotacao_de_Tipos.md` foram normalizados conforme o manifesto. Texto visível preservado.
- A menção textual a 47.2/47.3 em 47.1 foi preservada; os destinos permanecem sem confirmação editorial.

## Reprodução independente e preservação

- Árvore persistida vs reconstrução isolada: **{repro_text}** por caminho relativo e SHA-256.
- Fases 1–9: {PRIOR_TOTAL} hashes preservados. Fontes, páginas/referências da fase e JSON: hashes preservados.
- Backups: somente os diretórios/arquivos listados no relatório de validação foram efetivamente verificados; ausência não é tratada como integridade.
- Ressalva: a raiz do vault Obsidian não foi confirmada; wikilinks de origem não foram reescritos.
- Nenhum commit, push, importador, modificação de originais ou alteração do JSON foi executado.
"""
    (ROOT / VALIDATION_REL).write_text(validation, encoding="utf-8")
    (ROOT / AUDIT_REL).write_text(audit, encoding="utf-8")


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera e audita a migração estrutural da Fase 10")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    mode = "apply" if args.apply else ("dry-run" if args.dry_run else "reproduce")
    preflight(mode)
    manifest = load_manifest()
    original_untracked = untracked_hashes()
    preserved = protected_snapshot()
    prior = prior_tree_snapshot()
    prior_file_ids = prior_ids()
    tracked_state = (git("branch", "--show-current"), git("rev-parse", "HEAD"))

    sources, source_stats = source_data_and_validate(manifest, prior_file_ids)
    validate_literals(manifest, sources)
    first_builder = build(manifest, sources)
    stats = validate_outputs(manifest, prior_file_ids, first_builder, sources)
    stats["metadata_mappings"] = sum(1 for row in first_builder.records if row.get("tipo") == "metadata_conversion")
    expected = output_relative_hashes(stats)
    destination = ROOT / DEST_REL
    if args.reproduce and not destination.is_dir():
        raise ValueError("árvore persistida da Fase 10 não existe para reprodução")

    with tempfile.TemporaryDirectory(prefix="trilhacode-fase10-auditoria-") as temp_name:
        temp_tree = f9.write_temp_tree(first_builder, Path(temp_name), "Fase_10")
        temp_hashes = tree_hashes(temp_tree)
        first_diffs = compare_hashes(expected, temp_hashes)
        if first_diffs:
            raise ValueError("materialização temporária diverge da saída validada: " + "; ".join(first_diffs[:15]))
        if args.apply:
            if destination.exists():
                persisted = tree_hashes(destination)
                diffs = compare_hashes(expected, persisted)
                if diffs:
                    raise ValueError("árvore persistida existente diverge da reconstrução; não sobrescrita: " + "; ".join(diffs[:20]))
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                temp_tree.rename(destination)
                persisted = tree_hashes(destination)
                diffs = compare_hashes(expected, persisted)
                if diffs:
                    raise ValueError("árvore persistida diverge da reconstrução: " + "; ".join(diffs[:20]))
        elif args.reproduce:
            persisted = tree_hashes(destination)
            diffs = compare_hashes(temp_hashes, persisted)
            if diffs:
                raise ValueError("reprodução isolada difere da árvore persistida: " + "; ".join(diffs[:20]))

    # Segunda reconstrução independente, em outra área temporária, contra a árvore final.
    second_builder = build(manifest, sources)
    second_stats = validate_outputs(manifest, prior_file_ids, second_builder, sources)
    second_expected = output_relative_hashes(second_stats)
    with tempfile.TemporaryDirectory(prefix="trilhacode-fase10-reproducao-") as temp_name:
        second_tree = f9.write_temp_tree(second_builder, Path(temp_name), "Fase_10")
        second_hashes = tree_hashes(second_tree)
    if compare_hashes(expected, second_hashes):
        raise ValueError("duas reconstruções isoladas da Fase 10 diferem")
    identical = True
    if destination.is_dir():
        persisted = tree_hashes(destination)
        if compare_hashes(second_hashes, persisted):
            raise ValueError("segunda reconstrução não confere com a árvore persistida")
    elif not args.dry_run:
        raise ValueError("destino da Fase 10 ausente após geração/reprodução")

    backup_dirs, backup_files = backup_inventory()
    check_preserved(preserved, prior, tracked_state)
    after_untracked = untracked_hashes()
    for path, digest in original_untracked.items():
        if after_untracked.get(path) != digest:
            raise ValueError(f"documento não rastreado preexistente alterado/ausente: {path}")

    if args.apply:
        f9.MAPPING_REL = MAPPING_REL
        write_mapping(first_builder.records)
        write_reports(manifest, stats, stats["coverage"], backup_dirs, backup_files, {"identical": identical, "files": stats["files"]})
    elif args.reproduce:
        if not all((ROOT / rel).is_file() for rel in REPORT_FILES):
            raise ValueError("relatórios da Fase 10 ausentes durante reprodução")

    print(json.dumps({
        "result": "OK", "mode": mode, "base": BASE, "branch": tracked_state[0],
        "units": len(manifest["unidades"]), "subjects": sum(len(u.get("assuntos", [])) for u in manifest["unidades"].values()),
        "project_containers": 2, "files": stats["files"], "mappings": stats["mappings"],
        "types": stats["types"], "E_S_N": {"E": 36, "S": 4, "N": 0},
        "quizzes": 50, "answer_keys": 50, "practices": 30, "practice_feedbacks": 30,
        "practice_rubrics": 10, "project_rubrics": 2, "deliveries": 8,
        "links_resolved": stats["links"]["resolved"], "link_warnings": stats["links"]["warnings"],
        "wikilinks_preserved": stats["links"]["wikilinks"], "reproduction_identical": identical,
        "prior_files_unchanged": len(prior), "source_files": len([p for p in preserved if p.startswith("docs/courses/trilhacode/Conteudos/")]),
        "backup_dirs": backup_dirs, "backup_files": backup_files, "destination": DEST_REL,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
