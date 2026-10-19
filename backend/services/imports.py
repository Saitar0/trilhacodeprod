# ruff: noqa: EXE002
import re

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from audit import audit
from constants import DEFAULT_HIERARCHY, DEFAULT_LABELS, STATUSES
from core_utils import now
from database import db
from import_payload import NODE_TAX, has_valid_parent_kind, validate_import_shape
from learning import find_cycles
from serialization import oid, ser

NODE_TEXT = ["summary", "description", "guidance", "notes"]
TRACK_FIELDS = ["title", "subtitle", "description", "cover_url", "visibility", "audience", "difficulty", "level_labels", "settings"]
MAX_NODES = 20000

async def _plan(payload: dict):
    errors, warnings = [], []
    track_in = payload.get("track") or {}
    slug = track_in.get("slug", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug or ""):
        errors.append({"path": "track.slug", "message": "slug obrigatório (minúsculas, números e hífens)"})
    if not str(track_in.get("title", "")).strip():
        errors.append({"path": "track.title", "message": "título obrigatório"})
    track = await db.tracks.find_one({"slug": slug}) if slug else None
    hierarchy = (track or {}).get("hierarchy") or track_in.get("hierarchy") or DEFAULT_HIERARCHY
    if track and track_in.get("hierarchy") and track_in["hierarchy"] != track.get("hierarchy"):
        errors.append({"path": "track.hierarchy", "message": "não é possível alterar a hierarquia de uma trilha existente via importação"})

    tax = {}
    for t in await db.taxonomies.find({}).to_list(2000):
        tax.setdefault(t["group"], set()).add(t["key"])
    btypes = {b["key"]: b for b in await db.block_types.find({}).to_list(500)}
    tags = {t["name"].lower(): str(t["_id"]) for t in await db.tags.find({}).to_list(5000)}
    create_tags = (payload.get("options") or {}).get("create_missing_tags", True)
    missing_tags = set()

    existing = {}
    if track:
        for n in await db.nodes.find({"track_id": str(track["_id"]), "meta.import_ref": {"$exists": True}}).to_list(MAX_NODES):
            existing[n["meta"]["import_ref"]] = n
    flat, refs = [], set()

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
            elif ref in refs:
                errors.append({"path": f"{p}.ref", "message": f"ref duplicado: {ref}"})
            refs.add(ref)
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
            for tg in n.get("tags", []) or []:
                if str(tg).lower() not in tags:
                    (missing_tags.add(str(tg)) if create_tags else errors.append({"path": f"{p}.tags", "message": f"tag inexistente: {tg}"}))
            for j, b in enumerate(n.get("blocks", []) or []):
                bp = f"{p}.blocks[{j}]"
                bt = btypes.get((b or {}).get("type"))
                if not bt:
                    errors.append({"path": f"{bp}.type", "message": f"tipo de bloco inexistente: {(b or {}).get('type')}"})
                    continue
                if not bt.get("enabled", True):
                    warnings.append({"path": bp, "message": f"tipo '{bt['key']}' está desativado"})
                unknown = set((b.get("data") or {}).keys()) - {f["name"] for f in bt.get("fields", [])}
                if unknown:
                    warnings.append({"path": f"{bp}.data", "message": f"campos desconhecidos serão guardados mas não editáveis: {sorted(unknown)}"})
                if not b.get("ref") and ref in existing:
                    warnings.append({"path": bp, "message": "bloco sem ref em item já existente será ignorado (evita duplicar em reimportação)"})
            flat.append({**n, "_parent": parent_ref, "_order": i, "_path": p})
            walk(n.get("children", []) or [], ref, kind, f"{p}.children")

    walk(payload.get("nodes", []), None, None, "nodes")
    if len(flat) > MAX_NODES:
        errors.append({"path": "nodes", "message": f"máximo de {MAX_NODES} itens por importação"})

    parent_of = {n["ref"]: n["_parent"] for n in flat if isinstance(n.get("ref"), str)}

    def lineage(r):
        out, cur = set(), parent_of.get(r)
        while cur:
            out.add(cur)
            cur = parent_of.get(cur)
        return out
    rels = []
    for i, r in enumerate(payload.get("relations", []) or []):
        p = f"relations[{i}]"
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
        rels.append({"node_id": a, "target_id": b, "type": t, "enforced": bool(r.get("enforced")), "note": r.get("note", "")})
    for c in find_cycles(rels):
        errors.append({"path": "relations", "message": "ciclo de pré-requisitos: " + " → ".join(c)})

    summary = {
        "track": "atualizar" if track else "criar",
        "nodes_create": sum(1 for n in flat if n.get("ref") not in existing),
        "nodes_update": sum(1 for n in flat if n.get("ref") in existing),
        "nodes_untouched": len(set(existing) - refs),
        "blocks": sum(len(n.get("blocks", []) or []) for n in flat),
        "relations": len(rels),
        "tags_create": sorted(missing_tags),
    }
    if summary["nodes_untouched"]:
        warnings.append({"path": "nodes", "message": f"{summary['nodes_untouched']} item(ns) importados antes não estão no arquivo e serão mantidos como estão"})
    return {"ok": not errors, "errors": errors, "warnings": warnings, "summary": summary,
            "_ctx": {"track": track, "flat": flat, "rels": rels, "existing": existing, "tags": tags, "missing_tags": missing_tags,
                     "hierarchy": hierarchy}}

async def _execute(payload, plan, user):
    ctx = plan["_ctx"]
    t_in = payload["track"]
    fields = {k: t_in[k] for k in TRACK_FIELDS if k in t_in}
    if ctx["track"]:
        track_id = str(ctx["track"]["_id"])
        await db.tracks.update_one({"_id": ctx["track"]["_id"]}, {"$set": {**fields, "updated_at": now()}})
    else:
        last = await db.tracks.find({}).sort("order", -1).limit(1).to_list(1)
        res = await db.tracks.insert_one({
            "title": "", "subtitle": "", "description": "", "cover_url": "", "visibility": "public", "audience": [], "difficulty": "",
            "tag_ids": [], "level_labels": DEFAULT_LABELS, "settings": {"enforce_prerequisites": False}, "meta": {}, **fields,
            "slug": t_in["slug"], "hierarchy": ctx["hierarchy"], "status": "draft", "version": 0, "derived_from": None,
            "order": (last[0]["order"] + 1) if last else 0, "created_by": user["id"], "created_at": now(), "updated_at": now(),
            "published_at": None})
        track_id = str(res.inserted_id)
    tags = dict(ctx["tags"])
    for name in ctx["missing_tags"]:
        slug = name.lower().replace(" ", "-")
        document = {"name": name, "slug": slug, "color": "slate", "created_at": now()}
        try:
            await db.tags.update_one({"slug": slug}, {"$setOnInsert": document}, upsert=True)
        except DuplicateKeyError:
            # Another import may have inserted the same slug after this upsert's lookup.
            pass
        tag = await db.tags.find_one({"slug": slug})
        tags[name.lower()] = str(tag["_id"])
    ids = {}
    for n in ctx["flat"]:
        doc = {"track_id": track_id, "parent_id": ids.get(n["_parent"]), "kind": n["kind"], "title": n["title"].strip(),
               "slug": n["title"].strip().lower(), "order": n["_order"], "status": n.get("status", "draft"),
               "estimated_minutes": int(n.get("estimated_minutes") or 0),
               "tag_ids": [tags[str(t).lower()] for t in n.get("tags", []) or []], "updated_at": now(),
               **{k: n.get(k, "") for k in NODE_TEXT}, **{k: n.get(k, "") for k in NODE_TAX}}
        old = ctx["existing"].get(n["ref"])
        if old:
            await db.nodes.update_one({"_id": old["_id"]}, {"$set": doc})
            ids[n["ref"]] = str(old["_id"])
        else:
            res = await db.nodes.insert_one({**doc, "release": {}, "meta": {"import_ref": n["ref"]}, "created_by": user["id"],
                                             "created_at": now()})
            ids[n["ref"]] = str(res.inserted_id)
        for j, b in enumerate(n.get("blocks", []) or []):
            bdoc = {"node_id": ids[n["ref"]], "track_id": track_id, "type": b["type"], "title": b.get("title", ""),
                    "data": b.get("data") or {}, "status": b.get("status", "published"), "order": j, "updated_at": now()}
            if b.get("ref"):
                key = f"{n['ref']}/{b['ref']}"
                await db.content_blocks.update_one({"track_id": track_id, "meta.import_ref": key}, {
                    "$set": bdoc, "$setOnInsert": {"meta": {"import_ref": key}, "schema_version": 1, "created_at": now()}}, upsert=True)
            elif not old:
                await db.content_blocks.insert_one({**bdoc, "meta": {}, "schema_version": 1, "created_at": now()})
    for r in ctx["rels"]:
        key = {"track_id": track_id, "node_id": ids[r["node_id"]], "target_id": ids[r["target_id"]], "type": r["type"]}
        await db.relations.update_one(key, {"$set": {"enforced": r["enforced"], "note": r["note"]},
                                            "$setOnInsert": {"created_at": now()}}, upsert=True)
    s = plan["summary"]
    await audit(user, "track", track_id, "imported", track_id,
                f"{s['nodes_create']} criados, {s['nodes_update']} atualizados, {s['relations']} relações")
    return track_id

async def run_import(payload: dict, dry_run: bool, user: dict) -> dict:
    shape_errors = validate_import_shape(payload)
    if shape_errors:
        raise HTTPException(status_code=422, detail={"message": "Formato de importação inválido", "errors": shape_errors})
    plan = await _plan(payload)
    report = {key: value for key, value in plan.items() if key != "_ctx"}
    if dry_run or not plan["ok"]:
        return {**report, "dry_run": True}
    track_id = str((plan["_ctx"]["track"] or {}).get("_id"))
    if await db.restore_jobs.find_one({"track_id": track_id, "status": "running"}):
        raise HTTPException(status_code=409, detail="Restauração em andamento nesta trilha")
    track_id = await _execute(payload, plan, user)
    return {**report, "dry_run": False, "track": ser(await db.tracks.find_one({"_id": oid(track_id)}))}

