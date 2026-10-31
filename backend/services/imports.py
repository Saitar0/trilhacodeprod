# ruff: noqa: EXE002
import asyncio
import hashlib
import json
import logging
import re
import secrets
from datetime import timedelta

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from constants import DEFAULT_HIERARCHY, DEFAULT_LABELS, STATUSES
from core_utils import now
from database import db
from import_payload import (
    MAX_IMPORT_BLOCKS,
    MAX_IMPORT_NODES,
    MAX_IMPORT_RELATIONS,
    NODE_TAX,
    has_valid_parent_kind,
    validate_import_shape,
)
from integrity import save_version
from learning import find_cycles
from permissions import has_permission
from serialization import oid, ser
from services.versions import snapshot_track

NODE_TEXT = ["summary", "description", "guidance", "notes"]
TRACK_FIELDS = ["title", "subtitle", "description", "cover_url", "visibility", "audience", "difficulty", "level_labels", "settings"]
MAX_NODES = MAX_IMPORT_NODES
IMPORT_LEASE = timedelta(minutes=15)
IMPORTABLE_TOP_LEVEL = {"track", "options", "nodes", "relations"}
IMPORTABLE_TRACK_FIELDS = set(TRACK_FIELDS) | {"slug", "hierarchy"}
IMPORTABLE_NODE_FIELDS = set(NODE_TEXT) | set(NODE_TAX) | {
    "ref", "kind", "title", "status", "estimated_minutes", "tags", "children", "blocks",
}
IMPORTABLE_BLOCK_FIELDS = {"ref", "type", "title", "data", "status"}
IMPORTABLE_RELATION_FIELDS = {"from", "to", "type", "enforced", "note"}
log = logging.getLogger("content.import")


def _operation_id(payload: dict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _job_id(slug: str, operation_id: str) -> str:
    return hashlib.sha256(f"{slug}:{operation_id}".encode("utf-8")).hexdigest()


def _version_id(job_id: str, purpose: str) -> str:
    return hashlib.sha256(f"{job_id}:{purpose}".encode("ascii")).hexdigest()[:24]


def _append_unknown_warnings(value: dict, supported: set[str], path: str, warnings: list[dict]) -> None:
    unknown = sorted(set(value) - supported)
    if unknown:
        warnings.append({
            "path": path,
            "message": f"campos não reconhecidos serão ignorados pelo importador: {unknown}",
        })


def _import_conflict(message: str) -> None:
    raise HTTPException(status_code=409, detail=message)


async def _acquire_import_lock(
    slug: str, job_id: str, operation_id: str, track_id: str | None, user: dict,
) -> str:
    owner = secrets.token_hex(16)
    current_time = now()
    job = await db.import_jobs.find_one({"_id": job_id})
    if job and job.get("status") == "completed":
        return "completed"

    for _ in range(5):
        lock = await db.import_locks.find_one({"_id": slug})
        lease = current_time + IMPORT_LEASE
        replacement = {
            "operation_id": operation_id,
            "job_id": job_id,
            "track_id": track_id,
            "actor_id": user["id"],
            "status": "running",
            "lease_owner": owner,
            "lease_until": lease,
            "updated_at": current_time,
        }
        if lock is None:
            try:
                await db.import_locks.insert_one({"_id": slug, **replacement, "created_at": current_time})
                break
            except DuplicateKeyError:
                continue

        state = lock.get("status")
        same_operation = lock.get("job_id") == job_id
        if state == "running" and lock.get("lease_until") and lock["lease_until"] > current_time:
            _import_conflict("Já existe uma importação em andamento para esta trilha; tente novamente depois.")
        if state in {"running", "interrupted"} and not same_operation:
            _import_conflict("Há uma importação interrompida. Reenvie o mesmo payload para recuperá-la antes de iniciar outra.")
        if state not in {"running", "interrupted", "completed"}:
            _import_conflict("Estado de importação desconhecido; intervenção administrativa necessária.")

        selector = {"_id": slug, "status": state}
        if state in {"running", "interrupted"}:
            selector["job_id"] = job_id
            if state == "running":
                selector["lease_until"] = {"$lte": current_time}
        result = await db.import_locks.update_one(selector, {"$set": replacement})
        if result.matched_count:
            break
    else:
        _import_conflict("Não foi possível reservar a trilha para importação concorrente; tente novamente.")

    await db.import_jobs.update_one(
        {"_id": job_id},
        {"$setOnInsert": {
            "slug": slug,
            "operation_id": operation_id,
            "track_id": track_id,
            "actor_id": user["id"],
            "created_at": current_time,
        }, "$set": {
            "status": "running", "phase": "reserved", "updated_at": current_time,
            "attempts": (job or {}).get("attempts", 0) + 1,
        }},
        upsert=True,
    )
    return owner


async def _set_import_phase(slug: str, job_id: str, owner: str, phase: str) -> None:
    current_time = now()
    result = await db.import_locks.update_one(
        {"_id": slug, "job_id": job_id, "lease_owner": owner, "status": "running"},
        {"$set": {"lease_until": current_time + IMPORT_LEASE, "updated_at": current_time, "phase": phase}},
    )
    if not result.matched_count:
        raise HTTPException(status_code=409, detail="A reserva da importação foi perdida; reenvie o mesmo payload após conferir o estado.")
    await db.import_jobs.update_one({"_id": job_id}, {"$set": {"phase": phase, "updated_at": current_time}})


async def _heartbeat_import(slug: str, job_id: str, owner: str) -> None:
    while True:
        await asyncio.sleep(30)
        current_time = now()
        result = await db.import_locks.update_one(
            {"_id": slug, "job_id": job_id, "lease_owner": owner, "status": "running"},
            {"$set": {"lease_until": current_time + IMPORT_LEASE, "updated_at": current_time}},
        )
        if not result.matched_count:
            return
        await db.import_jobs.update_one(
            {"_id": job_id, "status": "running"}, {"$set": {"heartbeat_at": current_time}},
        )


async def _mark_import_interrupted(slug: str, job_id: str, owner: str, error_code: str) -> None:
    current_time = now()
    job = await db.import_jobs.find_one({"_id": job_id})
    await db.import_jobs.update_one({"_id": job_id, "status": {"$ne": "completed"}}, {"$set": {
        "status": "interrupted", "error_code": error_code, "updated_at": current_time,
    }})
    if job and job.get("track_id"):
        await db.tracks.update_one(
            {"_id": oid(job["track_id"]), "_import_state.job_id": job_id},
            {"$set": {"_import_state.status": "interrupted", "_import_state.interrupted_at": current_time}},
        )
    await db.import_locks.update_one(
        {"_id": slug, "job_id": job_id, "lease_owner": owner},
        {"$set": {"status": "interrupted", "lease_until": current_time, "updated_at": current_time}},
    )


async def _save_import_snapshot(track_id: str, version: int, kind: str, job_id: str, purpose: str,
                                note: str, user: dict) -> None:
    snapshot_id = _version_id(job_id, purpose)
    snapshot_oid = oid(snapshot_id)
    existing = await db.track_versions.find_one({"_id": snapshot_oid, "track_id": track_id})
    if existing and existing.get("snapshot_complete") is True and existing.get("operation_id") == job_id:
        return
    snapshot = await snapshot_track(track_id)
    snapshot["track"].pop("_import_state", None)
    snapshot["track"].pop("_last_import_operation", None)
    snapshot["track"]["version"] = version
    await save_version(
        track_id, version, kind, note, user, snapshot,
        extra={"operation_id": job_id, "purpose": purpose}, version_id=snapshot_id,
    )


async def _record_import_audit(user: dict, track_id: str, job_id: str, summary: dict) -> None:
    await db.edit_history.update_one(
        {"import_operation_id": job_id},
        {"$setOnInsert": {
            "entity": "track", "entity_id": track_id, "action": "imported", "track_id": track_id,
            "summary": f"{summary['nodes_create']} criados, {summary['nodes_update']} atualizados, "
                       f"{summary['relations']} relações",
            "user_id": user["id"], "user_name": user.get("name", ""), "at": now(),
            "import_operation_id": job_id,
        }},
        upsert=True,
    )


def _node_values(node: dict, track_id: str, parent_id: str | None, tag_ids: list[str], old: dict | None) -> dict:
    return {
        "track_id": track_id,
        "parent_id": parent_id,
        "kind": node["kind"],
        "title": node["title"].strip(),
        "slug": node["title"].strip().lower(),
        "order": node["_order"],
        "status": node.get("status", (old or {}).get("status", "draft")),
        "estimated_minutes": int(node.get("estimated_minutes") or 0),
        "tag_ids": tag_ids,
        **{field: node.get(field, "") for field in NODE_TEXT},
        **{field: node.get(field, "") for field in NODE_TAX},
    }


def _block_values(block: dict, node_id: str, track_id: str, order: int, old: dict | None) -> dict:
    return {
        "node_id": node_id,
        "track_id": track_id,
        "type": block["type"],
        "title": block.get("title", ""),
        "data": block.get("data") or {},
        "status": block.get("status", (old or {}).get("status", "published")),
        "order": order,
    }


def _same_fields(old: dict | None, values: dict) -> bool:
    return old is not None and all(old.get(key) == value for key, value in values.items())


async def _plan(payload: dict, resume_job_id: str | None = None):
    errors, warnings = [], []
    _append_unknown_warnings(payload, IMPORTABLE_TOP_LEVEL, "payload", warnings)
    track_in = payload.get("track") or {}
    _append_unknown_warnings(track_in, IMPORTABLE_TRACK_FIELDS, "track", warnings)
    slug = track_in.get("slug", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug or ""):
        errors.append({"path": "track.slug", "message": "slug obrigatório (minúsculas, números e hífens)"})
    if not str(track_in.get("title", "")).strip():
        errors.append({"path": "track.title", "message": "título obrigatório"})
    matching_tracks = await db.tracks.find({"slug": slug}).limit(2).to_list(2) if slug else []
    if len(matching_tracks) > 1:
        errors.append({"path": "track.slug", "message": "há mais de uma trilha com este slug; reconcilie os registros antes de importar"})
    track = matching_tracks[0] if matching_tracks else None
    if track and track.get("_import_state") and track["_import_state"].get("job_id") != resume_job_id:
        errors.append({"path": "track", "message": "a trilha está bloqueada por uma importação interrompida ou em andamento"})
    hierarchy = (track or {}).get("hierarchy") or track_in.get("hierarchy") or DEFAULT_HIERARCHY
    if track_in.get("hierarchy") is not None and (
        not track_in["hierarchy"] or len(set(track_in["hierarchy"])) != len(track_in["hierarchy"])
    ):
        errors.append({"path": "track.hierarchy", "message": "a hierarquia deve conter tipos únicos e ao menos um nível"})
    if track and track_in.get("hierarchy") and track_in["hierarchy"] != track.get("hierarchy"):
        errors.append({"path": "track.hierarchy", "message": "não é possível alterar a hierarquia de uma trilha existente via importação"})

    tax = {}
    for t in await db.taxonomies.find({}).to_list(2000):
        tax.setdefault(t["group"], set()).add(t["key"])
    btypes = {b["key"]: b for b in await db.block_types.find({}).to_list(500)}
    tags = {}
    tag_rows = await db.tags.find({}).to_list(5001)
    if len(tag_rows) > 5000:
        errors.append({"path": "tags", "message": "há mais de 5.000 tags; revisão administrativa necessária"})
    for tag in tag_rows:
        normalized_name = tag["name"].lower()
        if normalized_name in tags:
            errors.append({"path": "tags", "message": f"há tags legadas ambíguas para o nome '{tag['name']}'"})
        else:
            tags[normalized_name] = str(tag["_id"])
    create_tags = (payload.get("options") or {}).get("create_missing_tags", True)
    missing_tags = {}

    existing = {}
    existing_blocks = {}
    existing_relations = {}
    if track:
        node_rows = await db.nodes.find({
            "track_id": str(track["_id"]), "meta.import_ref": {"$type": "string"},
        }).to_list(MAX_NODES + 1)
        if len(node_rows) > MAX_NODES:
            errors.append({"path": "track", "message": "há mais de 20.000 nós importados registrados; revisão administrativa necessária"})
        for node in node_rows:
            ref = node["meta"]["import_ref"]
            if ref in existing:
                errors.append({"path": "track", "message": f"import_ref legado duplicado em nós: {ref}"})
            else:
                existing[ref] = node
        blocks = await db.content_blocks.find({
            "track_id": str(track["_id"]), "meta.import_ref": {"$type": "string"},
        }).to_list(MAX_IMPORT_BLOCKS + 1)
        if len(blocks) > MAX_IMPORT_BLOCKS:
            errors.append({"path": "track", "message": "há mais de 50.000 blocos importados registrados; revisão administrativa necessária"})
        for block in blocks:
            ref = block["meta"]["import_ref"]
            if ref in existing_blocks:
                errors.append({"path": "track", "message": f"import_ref legado duplicado em blocos: {ref}"})
            else:
                existing_blocks[ref] = block
        relations = await db.relations.find({"track_id": str(track["_id"])}).to_list(MAX_IMPORT_RELATIONS + 1)
        if len(relations) > MAX_IMPORT_RELATIONS:
            errors.append({"path": "track", "message": "há mais de 50.000 relações; revisão administrativa necessária"})
        for relation in relations:
            key = (relation.get("node_id"), relation.get("target_id"), relation.get("type"))
            if key in existing_relations:
                errors.append({"path": "track", "message": "há relações duplicadas; reconcilie os registros antes de importar"})
            else:
                existing_relations[key] = relation

    flat, refs = [], set()
    incoming_block_refs = set()

    def walk(items, parent_ref, parent_kind, path):
        if not isinstance(items, list):
            errors.append({"path": path, "message": "deve ser uma lista"})
            return
        for i, n in enumerate(items):
            p = f"{path}[{i}]"
            if not isinstance(n, dict):
                errors.append({"path": p, "message": "item inválido"})
                continue
            ref, kind = n.get("ref"), n.get("kind")
            if not isinstance(ref, str) or not ref.strip():
                errors.append({"path": f"{p}.ref", "message": "ref obrigatório (identificador estável, ex: 'f1-m2-t3')"})
                continue
            elif ref in refs:
                errors.append({"path": f"{p}.ref", "message": f"ref duplicado: {ref}"})
                continue
            elif len(ref) > 512:
                errors.append({"path": f"{p}.ref", "message": "máximo de 512 caracteres"})
                continue
            refs.add(ref)
            _append_unknown_warnings(n, IMPORTABLE_NODE_FIELDS, p, warnings)
            if kind not in hierarchy:
                errors.append({"path": f"{p}.kind", "message": f"kind deve ser um de {hierarchy}"})
            elif parent_kind and not has_valid_parent_kind(parent_kind, hierarchy):
                errors.append({"path": f"{p}.kind", "message": "não é possível validar a hierarquia porque o tipo do item pai é inválido"})
            elif parent_kind and hierarchy.index(kind) <= hierarchy.index(parent_kind):
                errors.append({"path": f"{p}.kind", "message": f"'{kind}' não pode ficar dentro de '{parent_kind}'"})
            if not str(n.get("title", "")).strip():
                errors.append({"path": f"{p}.title", "message": "título obrigatório"})
            if n.get("status", "draft") not in STATUSES:
                errors.append({"path": f"{p}.status", "message": f"status deve ser um de {STATUSES}"})
            for field, group in NODE_TAX.items():
                if n.get(field) and n[field] not in tax.get(group, set()):
                    errors.append({"path": f"{p}.{field}", "message": f"chave '{n[field]}' não existe em {group}"})
            seen_tags = set()
            for tg in n.get("tags", []) or []:
                normalized = str(tg).lower()
                if normalized in seen_tags:
                    errors.append({"path": f"{p}.tags", "message": f"tag repetida: {tg}"})
                    continue
                seen_tags.add(normalized)
                if normalized not in tags:
                    if create_tags:
                        missing_tags.setdefault(normalized, str(tg))
                    else:
                        errors.append({"path": f"{p}.tags", "message": f"tag inexistente: {tg}"})
            local_block_refs = set()
            for j, b in enumerate(n.get("blocks", []) or []):
                bp = f"{p}.blocks[{j}]"
                if isinstance(b, dict):
                    _append_unknown_warnings(b, IMPORTABLE_BLOCK_FIELDS, bp, warnings)
                    block_ref = b.get("ref")
                    if isinstance(block_ref, str) and block_ref:
                        if block_ref in local_block_refs:
                            errors.append({"path": f"{bp}.ref", "message": f"ref de bloco duplicado neste nó: {block_ref}"})
                        local_block_refs.add(block_ref)
                        full_ref = f"{ref}/{block_ref}"
                        if full_ref in incoming_block_refs:
                            errors.append({"path": f"{bp}.ref", "message": f"ref de bloco duplicado: {full_ref}"})
                        incoming_block_refs.add(full_ref)
                bt = btypes.get((b or {}).get("type"))
                if not bt:
                    errors.append({"path": f"{bp}.type", "message": f"tipo de bloco inexistente: {(b or {}).get('type')}"})
                    continue
                if not bt.get("enabled", True):
                    warnings.append({"path": bp, "message": f"tipo '{bt['key']}' está desativado"})
                unknown = set((b.get("data") or {}).keys()) - {f["name"] for f in bt.get("fields", [])}
                if unknown:
                    warnings.append({"path": f"{bp}.data", "message": f"campos desconhecidos serão guardados mas não editáveis: {sorted(unknown)}"})
                old_node = existing.get(ref)
                if not b.get("ref"):
                    if old_node and old_node.get("meta", {}).get("import_block_ref_mode") != 1:
                        warnings.append({"path": bp, "message": "bloco sem ref em nó legado será preservado e ignorado; adicione ref estável para atualizá-lo"})
                    else:
                        warnings.append({"path": bp, "message": "bloco sem ref usa identidade posicional; reordenação pode associar o histórico a outro bloco. Adicione ref estável"})
            flat.append({**n, "_parent": parent_ref, "_order": i, "_path": p})
            walk(n.get("children", []) or [], ref, kind, f"{p}.children")

    walk(payload.get("nodes", []), None, None, "nodes")

    parent_of = {n["ref"]: n["_parent"] for n in flat if isinstance(n.get("ref"), str)}

    def lineage(r):
        out, cur = set(), parent_of.get(r)
        while cur:
            out.add(cur)
            cur = parent_of.get(cur)
        return out
    rels = []
    incoming_relations = set()
    for i, r in enumerate(payload.get("relations", []) or []):
        p = f"relations[{i}]"
        _append_unknown_warnings(r, IMPORTABLE_RELATION_FIELDS, p, warnings)
        a, b, t = r.get("from"), r.get("to"), r.get("type")
        if a not in refs or b not in refs:
            errors.append({"path": p, "message": f"from/to devem ser refs de itens deste arquivo ({a} → {b})"})
            continue
        if t not in tax.get("relation_type", set()):
            errors.append({"path": f"{p}.type", "message": f"tipo de relação inexistente: {t}"})
        if a == b:
            errors.append({"path": p, "message": "item não pode se relacionar consigo mesmo"})
        if t == "prerequisite" and (b in lineage(a) or a in lineage(b)):
            errors.append({"path": p, "message": f"pré-requisito entre pai e filho causa bloqueio impossível ({a} → {b})"})
        relation_key = (a, b, t)
        if relation_key in incoming_relations:
            errors.append({"path": p, "message": "relação duplicada no payload"})
        incoming_relations.add(relation_key)
        rels.append({"node_id": a, "target_id": b, "type": t, "enforced": bool(r.get("enforced")), "note": r.get("note", "")})
    for c in find_cycles(rels):
        errors.append({"path": "relations", "message": "ciclo de pré-requisitos: " + " → ".join(c)})

    track_values = {key: track_in[key] for key in TRACK_FIELDS if key in track_in}
    track_changed = not track or any(track.get(key) != value for key, value in track_values.items())
    node_counts = {"create": 0, "update": 0, "unchanged": 0}
    id_by_ref = {ref: str(node["_id"]) for ref, node in existing.items()}
    for node in flat:
        old = existing.get(node["ref"])
        if old is None:
            node_counts["create"] += 1
            continue
        tag_ids = [tags[str(tag).lower()] for tag in node.get("tags", []) or [] if str(tag).lower() in tags]
        parent_id = id_by_ref.get(node["_parent"]) if node.get("_parent") else None
        values = _node_values(node, str(track["_id"]), parent_id, tag_ids, old)
        changed = bool(missing_tags) or not _same_fields(old, values)
        if changed:
            node_counts["update"] += 1
        else:
            node_counts["unchanged"] += 1

    block_counts = {"create": 0, "update": 0, "unchanged": 0, "ignored_legacy": 0}
    for node in flat:
        old_node = existing.get(node["ref"])
        node_id = id_by_ref.get(node["ref"])
        for index, block in enumerate(node.get("blocks", []) or []):
            block_ref = block.get("ref")
            if block_ref:
                import_ref = f"{node['ref']}/{block_ref}"
            elif old_node is None or old_node.get("meta", {}).get("import_block_ref_mode") == 1:
                import_ref = f"{node['ref']}/__position_{index}"
            else:
                block_counts["ignored_legacy"] += 1
                continue
            old_block = existing_blocks.get(import_ref)
            if old_block is None:
                block_counts["create"] += 1
                continue
            values = _block_values(block, node_id or str(old_node["_id"]), str(track["_id"]), index, old_block)
            if _same_fields(old_block, values):
                block_counts["unchanged"] += 1
            else:
                block_counts["update"] += 1

    relation_counts = {"create": 0, "update": 0, "unchanged": 0}
    for relation in rels:
        source = id_by_ref.get(relation["node_id"])
        target = id_by_ref.get(relation["target_id"])
        old_relation = existing_relations.get((source, target, relation["type"])) if source and target else None
        if old_relation is None:
            relation_counts["create"] += 1
        elif old_relation.get("enforced", False) == relation["enforced"] and old_relation.get("note", "") == relation["note"]:
            relation_counts["unchanged"] += 1
        else:
            relation_counts["update"] += 1

    has_changes = bool(
        not track or track_changed or node_counts["create"] or node_counts["update"]
        or block_counts["create"] or block_counts["update"] or relation_counts["create"]
        or relation_counts["update"] or missing_tags
    )
    published_change = bool(track and track.get("status") == "published" and has_changes)
    summary = {
        "track": "atualizar" if track else "criar",
        "track_changed": track_changed,
        "nodes_create": node_counts["create"],
        "nodes_update": node_counts["update"],
        "nodes_unchanged": node_counts["unchanged"],
        "nodes_untouched": len(set(existing) - refs),
        "blocks": sum(len(n.get("blocks", []) or []) for n in flat),
        "blocks_create": block_counts["create"],
        "blocks_update": block_counts["update"],
        "blocks_unchanged": block_counts["unchanged"],
        "blocks_ignored_legacy": block_counts["ignored_legacy"],
        "relations": len(rels),
        "relations_create": relation_counts["create"],
        "relations_update": relation_counts["update"],
        "relations_unchanged": relation_counts["unchanged"],
        "tags_create": sorted(missing_tags.values()),
        "published_version_after_import": int(track.get("version", 0)) + int(published_change)
        if track else 0,
        "will_create_published_backup": published_change,
        "changes": has_changes,
        "published_track": bool(track and track.get("status") == "published"),
    }
    if block_counts["ignored_legacy"]:
        warnings.append({"path": "nodes", "message": f"{block_counts['ignored_legacy']} bloco(s) sem ref de nós legados foram preservados e não serão atualizados"})
    if summary["nodes_untouched"]:
        warnings.append({"path": "nodes", "message": f"{summary['nodes_untouched']} item(ns) importados antes não estão no arquivo e serão mantidos como estão"})
    return {"ok": not errors, "errors": errors, "warnings": warnings, "summary": summary,
            "_ctx": {
                "track": track, "flat": flat, "rels": rels, "existing": existing,
                "existing_blocks": existing_blocks, "existing_relations": existing_relations,
                "tags": tags, "missing_tags": missing_tags, "hierarchy": hierarchy,
            }}

async def _execute(payload, plan, user, job_id: str, operation_id: str, owner: str) -> str:
    ctx = plan["_ctx"]
    track_input = payload["track"]
    track = ctx["track"]
    slug = track_input["slug"]
    fields = {key: track_input[key] for key in TRACK_FIELDS if key in track_input}
    started_at = now()

    if track:
        track_id = str(track["_id"])
        marker = {"job_id": job_id, "operation_id": operation_id, "status": "applying", "started_at": started_at}
        selector = {"_id": track["_id"], "$or": [
            {"_import_state": {"$exists": False}}, {"_import_state.job_id": job_id},
        ]}
        if track.get("updated_at") is not None:
            selector["updated_at"] = track["updated_at"]
        result = await db.tracks.update_one(selector, {"$set": {"_import_state": marker}})
        if not result.matched_count:
            _import_conflict("A trilha mudou após a validação; execute novamente a simulação antes de importar.")
    else:
        last = await db.tracks.find({}).sort("order", -1).limit(1).to_list(1)
        document = {
            "title": "", "subtitle": "", "description": "", "cover_url": "", "visibility": "public",
            "audience": [], "difficulty": "", "tag_ids": [], "level_labels": DEFAULT_LABELS,
            "settings": {"enforce_prerequisites": False}, "meta": {}, **fields,
            "slug": slug, "hierarchy": ctx["hierarchy"], "status": "draft", "version": 0,
            "derived_from": None, "order": (last[0].get("order", -1) + 1) if last else 0,
            "created_by": user["id"], "created_at": started_at, "updated_at": started_at,
            "published_at": None,
            "_import_state": {"job_id": job_id, "operation_id": operation_id, "status": "applying", "started_at": started_at},
        }
        try:
            created = await db.tracks.insert_one(document)
        except DuplicateKeyError as exc:
            raise HTTPException(status_code=409, detail="Já existe uma trilha com este slug; simule novamente antes de importar.") from exc
        track_id = str(created.inserted_id)

    await db.import_jobs.update_one({"_id": job_id}, {"$set": {"track_id": track_id}})
    job = await db.import_jobs.find_one({"_id": job_id})
    target_version = int(job["target_version"])
    published = bool(job.get("published_change"))

    if published:
        await _set_import_phase(slug, job_id, owner, "backup")
        await _save_import_snapshot(track_id, target_version - 1, "backup", job_id, "before",
                                    "Backup automático antes da importação", user)

    await _set_import_phase(slug, job_id, owner, "track")
    if track and any(track.get(key) != value for key, value in fields.items()):
        await db.tracks.update_one({"_id": oid(track_id), "_import_state.job_id": job_id},
                                   {"$set": {**fields, "updated_at": now()}})

    tags = dict(ctx["tags"])
    for name, display_name in ctx["missing_tags"].items():
        tag_slug = display_name.lower().replace(" ", "-")
        document = {"name": display_name, "slug": tag_slug, "color": "slate", "created_at": now()}
        try:
            await db.tags.update_one({"slug": tag_slug}, {"$setOnInsert": document}, upsert=True)
        except DuplicateKeyError:
            # A parallel taxonomy writer may have won the unique slug race.
            pass
        tag = await db.tags.find_one({"slug": tag_slug})
        if not tag:
            raise RuntimeError("A tag upsert não pôde ser confirmada")
        tags[name] = str(tag["_id"])

    await _set_import_phase(slug, job_id, owner, "nodes")
    ids = {ref: str(document["_id"]) for ref, document in ctx["existing"].items()}
    writes_since_heartbeat = 0

    async def refresh_lease(phase: str) -> None:
        nonlocal writes_since_heartbeat
        writes_since_heartbeat += 1
        if writes_since_heartbeat >= 100:
            await _set_import_phase(slug, job_id, owner, phase)
            writes_since_heartbeat = 0

    for index, node in enumerate(ctx["flat"]):
        ref = node["ref"]
        old = ctx["existing"].get(ref)
        parent_id = ids.get(node["_parent"]) if node.get("_parent") else None
        tag_ids = [tags[str(tag).lower()] for tag in node.get("tags", []) or []]
        values = _node_values(node, track_id, parent_id, tag_ids, old)
        imported_blocks = node.get("blocks", []) or []
        has_positional_blocks = any(not block.get("ref") for block in imported_blocks)
        positional_mode = not old or old.get("meta", {}).get("import_block_ref_mode") == 1
        node_selector = {"track_id": track_id, "meta.import_ref": ref}
        if old:
            node_selector["_id"] = old["_id"]
        set_values = {**values, "updated_at": now()}
        if not old or not _same_fields(old, values):
            update = {"$set": {**set_values, "meta.import_ref": ref}}
            if has_positional_blocks and positional_mode:
                update["$set"]["meta.import_block_ref_mode"] = 1
            if not old:
                update["$setOnInsert"] = {"release": {}, "created_by": user["id"], "created_at": now()}
            try:
                result = await db.nodes.update_one(node_selector, update, upsert=not bool(old))
            except DuplicateKeyError:
                # Another writer inserted this stable identity between planning and write.
                result = None
            if result and result.upserted_id:
                ids[ref] = str(result.upserted_id)
            elif old:
                ids[ref] = str(old["_id"])
            else:
                persisted = await db.nodes.find_one(node_selector)
                if not persisted:
                    raise RuntimeError(f"Não foi possível confirmar a persistência do nó {ref}")
                ids[ref] = str(persisted["_id"])
        else:
            ids[ref] = str(old["_id"])

        for block_index, block in enumerate(imported_blocks):
            block_ref = block.get("ref")
            if not block_ref and old and old.get("meta", {}).get("import_block_ref_mode") != 1:
                continue
            identity = f"{ref}/{block_ref}" if block_ref else f"{ref}/__position_{block_index}"
            previous = ctx["existing_blocks"].get(identity)
            block_values = _block_values(block, ids[ref], track_id, block_index, previous)
            if previous and _same_fields(previous, block_values):
                continue
            selector = {"track_id": track_id, "meta.import_ref": identity}
            if previous:
                selector["_id"] = previous["_id"]
            update = {"$set": {**block_values, "updated_at": now(), "meta.import_ref": identity},
                      "$setOnInsert": {"schema_version": 1, "created_at": now()}}
            try:
                await db.content_blocks.update_one(selector, update, upsert=not bool(previous))
            except DuplicateKeyError as exc:
                raise RuntimeError("Colisão de identidade estável ao gravar bloco") from exc
            await refresh_lease("nodes")

        if index and index % 50 == 0:
            await _set_import_phase(slug, job_id, owner, "nodes")

    await _set_import_phase(slug, job_id, owner, "relations")
    for relation in ctx["rels"]:
        key = {"track_id": track_id, "node_id": ids[relation["node_id"]],
               "target_id": ids[relation["target_id"]], "type": relation["type"]}
        old_relation = ctx["existing_relations"].get(
            (key["node_id"], key["target_id"], key["type"])
        )
        if old_relation and old_relation.get("enforced", False) == relation["enforced"] and old_relation.get("note", "") == relation["note"]:
            continue
        try:
            await db.relations.update_one(
                key,
                {"$set": {"enforced": relation["enforced"], "note": relation["note"]},
                 "$setOnInsert": {"created_at": now()}},
                upsert=True,
            )
        except DuplicateKeyError as exc:
            raise RuntimeError("Colisão de identidade ao gravar relação") from exc
        await refresh_lease("relations")

    await _set_import_phase(slug, job_id, owner, "snapshot")
    if published:
        await db.tracks.update_one({"_id": oid(track_id), "_import_state.job_id": job_id},
                                   {"$set": {"version": target_version, "updated_at": now()}})
        await _save_import_snapshot(track_id, target_version, "import", job_id, "after",
                                    "Importação de conteúdo", user)

    await _record_import_audit(user, track_id, job_id, plan["summary"])
    await _set_import_phase(slug, job_id, owner, "finalizing")
    finalized = await db.tracks.update_one(
        {"_id": oid(track_id), "_import_state.job_id": job_id},
        {"$set": {"_last_import_operation": job_id, "updated_at": now()}, "$unset": {"_import_state": ""}},
    )
    if not finalized.matched_count:
        current = await db.tracks.find_one({"_id": oid(track_id)})
        if not current or current.get("_last_import_operation") != job_id:
            raise RuntimeError("A importação terminou sem conseguir liberar o marcador de publicação")
    return track_id


async def run_import(payload: dict, dry_run: bool, user: dict) -> dict:
    if not has_permission(user, "content.write"):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    shape_errors = validate_import_shape(payload)
    if shape_errors:
        raise HTTPException(status_code=422, detail={"message": "Formato de importação inválido", "errors": shape_errors})
    slug = payload["track"].get("slug", "")
    operation_id = _operation_id(payload)
    job_id = _job_id(slug, operation_id)
    plan = await _plan(payload, resume_job_id=None if dry_run else job_id)
    report = {key: value for key, value in plan.items() if key != "_ctx"}
    report["dry_run"] = True
    existing_track = plan["_ctx"]["track"]
    marker = (existing_track or {}).get("_import_state")
    if not dry_run and marker and marker.get("job_id") != job_id:
        _import_conflict("Há uma importação interrompida ou em andamento; retome o payload original antes de iniciar outra.")
    if dry_run or not plan["ok"]:
        return report

    track = plan["_ctx"]["track"]
    track_id = str(track["_id"]) if track else None
    if track_id and await db.restore_jobs.find_one({"track_id": track_id, "status": "running"}):
        raise HTTPException(status_code=409, detail="Restauração em andamento nesta trilha")

    acquired = await _acquire_import_lock(slug, job_id, operation_id, track_id, user)
    if acquired == "completed":
        job = await db.import_jobs.find_one({"_id": job_id})
        if job and job.get("response"):
            return {**job["response"], "idempotent_replay": True}
        current_track = await db.tracks.find_one({"slug": slug})
        if current_track and current_track.get("_last_import_operation") == job_id:
            completed_report = {**report, "dry_run": False, "idempotent_replay": True,
                                "track": ser(current_track)}
            await db.import_jobs.update_one({"_id": job_id}, {"$set": {"response": completed_report}})
            return completed_report
        _import_conflict("O registro da importação está concluído, mas a trilha não confirma o resultado; intervenção administrativa necessária.")

    owner = acquired
    heartbeat_task = asyncio.create_task(_heartbeat_import(slug, job_id, owner))
    # Replan inside the lock to avoid applying a plan based on a stale pre-lock read.
    try:
        plan = await _plan(payload, resume_job_id=job_id)
        report = {key: value for key, value in plan.items() if key != "_ctx"}
        report["dry_run"] = False
        if not plan["ok"]:
            await db.import_jobs.update_one({"_id": job_id}, {"$set": {
                "status": "rejected", "errors": plan["errors"], "updated_at": now(),
            }})
            await db.import_locks.delete_one({"_id": slug, "job_id": job_id, "lease_owner": owner})
            return {**report, "dry_run": True}
        track = plan["_ctx"]["track"]
        planned_job = await db.import_jobs.find_one({"_id": job_id})
        if not planned_job.get("plan_initialized"):
            target_version = int((track or {}).get("version", 0)) + int(bool(
                track and track.get("status") == "published" and plan["summary"]["changes"]
            ))
            await db.import_jobs.update_one(
                {"_id": job_id, "plan_initialized": {"$ne": True}},
                {"$set": {
                    "plan_initialized": True,
                    "target_version": target_version,
                    "published_change": bool(
                        track and track.get("status") == "published" and plan["summary"]["changes"]
                    ),
                    "planned_summary": plan["summary"],
                    "planned_warnings": plan["warnings"],
                    "track_id": str(track["_id"]) if track else None,
                }},
            )
            planned_job = await db.import_jobs.find_one({"_id": job_id})
        # A resumed job must retain the original plan: some of its rows may already have
        # been applied before the failure, so replanning alone would undercount the operation.
        plan["summary"] = planned_job["planned_summary"]
        plan["warnings"] = planned_job.get("planned_warnings", plan["warnings"])
        report = {key: value for key, value in plan.items() if key != "_ctx"}
        report["dry_run"] = False
        track = plan["_ctx"]["track"]
        if track and track.get("_last_import_operation") == job_id:
            current_track = await db.tracks.find_one({"_id": track["_id"]})
            current_track.pop("_last_import_operation", None)
            response = {**report, "idempotent_replay": True, "track": ser(current_track)}
            await db.import_jobs.update_one({"_id": job_id}, {"$set": {
                "status": "completed", "response": response, "finished_at": now(), "updated_at": now(),
            }})
            await db.import_locks.update_one({"_id": slug, "job_id": job_id, "lease_owner": owner},
                                             {"$set": {"status": "completed", "updated_at": now()}})
            return response
        track_id = await _execute(payload, plan, user, job_id, operation_id, owner)
        final_track = await db.tracks.find_one({"_id": oid(track_id)})
        if not final_track or final_track.get("_import_state"):
            raise RuntimeError("A importação não confirmou a liberação da trilha")
        final_track.pop("_last_import_operation", None)
        response = {**report, "dry_run": False, "track": ser(final_track)}
        current_time = now()
        await db.import_jobs.update_one({"_id": job_id}, {"$set": {
            "status": "completed", "phase": "completed", "response": response,
            "finished_at": current_time, "updated_at": current_time,
        }})
        await db.import_locks.update_one({"_id": slug, "job_id": job_id, "lease_owner": owner},
                                         {"$set": {"status": "completed", "updated_at": current_time},
                                          "$unset": {"lease_owner": "", "lease_until": ""}})
        return response
    except Exception as exc:
        try:
            await _mark_import_interrupted(slug, job_id, owner, type(exc).__name__)
        except Exception:
            log.exception("Falha ao registrar importação interrompida", extra={"job_id": job_id, "slug": slug})
        raise
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

