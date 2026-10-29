"""Seed a synthetic-only two-unit learner fixture after the Beta 7 host gate."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any, cast

from pymongo import MongoClient

from test_support.beta7_internal_target import connect_internal_verified_target


def _expect(response, expected: int, action: str) -> dict:
    if response.status_code != expected:
        raise RuntimeError(f"Fixture Beta 7 falhou em {action}: HTTP {response.status_code}")
    return response.json() if response.content else {}


async def _seed() -> dict[str, str]:
    target, ownership = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    try:
        owner_collection = f"_{target.phase}_test_owner"
        collections = set(cast(Any, ownership)[target.database].list_collection_names())
        if collections - {owner_collection}:
            raise RuntimeError("Fixture Beta 7 recusou banco não vazio após regressões")
    finally:
        cast(Any, ownership).close()

    from database import client, db
    from indexes import ensure_indexes
    from migrations import migrate
    from security import hash_password
    from seed import BLOCK_TYPES, SUBMITTABLE, TAXONOMIES

    await db.command("ping")
    await ensure_indexes()
    users = [
        ("admin", "admin@example.com", os.environ["E2E_ADMIN_PASSWORD"], "Beta 7 Synthetic Admin"),
        ("student", "student@example.com", os.environ["E2E_STUDENT_PASSWORD"], "Beta 7 Synthetic Student"),
        ("editor", "reviewer@example.com", os.environ["E2E_REVIEWER_PASSWORD"], "Beta 7 Synthetic Reviewer"),
        ("editor", "unscoped@example.com", os.environ["E2E_UNSCOPED_PASSWORD"], "Beta 7 Synthetic Unscoped"),
    ]
    await db.users.insert_many([{
        "email": email, "name": name, "password_hash": hash_password(password),
        "role": role, "email_verified": True, "is_active": True,
        "profile": {"bio": "", "goals": "", "preferences": {}},
    } for role, email, password, name in users])
    for index, (group, key, label, description, color) in enumerate(TAXONOMIES):
        await db.taxonomies.insert_one({
            "group": group, "key": key, "label": label, "description": description,
            "color": color, "order": index,
        })
    for index, (key, label, category, icon, fields) in enumerate(BLOCK_TYPES):
        await db.block_types.insert_one({
            "key": key, "label": label, "category": category, "icon": icon, "fields": fields,
            "description": "", "enabled": True,
            "capabilities": ["submission"] if key in SUBMITTABLE else [], "order": index,
        })
    await migrate()

    import requests

    api_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:18000")
    session = requests.Session()
    session.headers["Origin"] = "http://localhost:3000"
    login = session.post(f"{api_url}/api/auth/login", json={
        "email": "admin@example.com", "password": os.environ["E2E_ADMIN_PASSWORD"],
    }, timeout=10)
    _expect(login, 200, "admin login")

    suffix = uuid.uuid4().hex[:12]
    track = _expect(session.post(f"{api_url}/api/tracks", json={
        "title": f"Beta 7 — fixture sintética multiunidade {suffix}",
        "slug": f"beta7-synthetic-learning-{suffix}", "status": "draft", "visibility": "public",
    }, timeout=10), 200, "track create")
    phase = _expect(session.post(f"{api_url}/api/nodes", json={
        "track_id": track["id"], "kind": "phase", "title": "Fase sintética Beta 7", "status": "draft",
    }, timeout=10), 200, "phase create")
    module = _expect(session.post(f"{api_url}/api/nodes", json={
        "track_id": track["id"], "parent_id": phase["id"], "kind": "module",
        "title": "Módulo sintético Beta 7", "status": "draft",
    }, timeout=10), 200, "module create")

    nodes: list[dict[str, str]] = []
    quiz_ids: list[str] = []
    for unit_id in ("1.1", "1.2"):
        node = _expect(session.post(f"{api_url}/api/nodes", json={
            "track_id": track["id"], "parent_id": module["id"], "kind": "topic",
            "title": f"Unidade {unit_id} — aula sintética", "summary": "Conteúdo criado somente para teste.",
            "status": "draft",
        }, timeout=10), 200, f"unit {unit_id} create")
        nodes.append(node)
        _expect(session.post(f"{api_url}/api/blocks", json={
            "node_id": node["id"], "type": "theory_text", "title": "Leitura", "status": "draft",
            "data": {"body": f"# Unidade {unit_id}\n\nConteúdo sintético de navegação Beta 7."},
        }, timeout=10), 200, f"unit {unit_id} theory")
        quiz = _expect(session.post(f"{api_url}/api/blocks", json={
            "node_id": node["id"], "type": "quiz", "title": f"Quiz {unit_id}", "status": "draft",
            "data": {
                "activity_schema_version": 1,
                "prompt": f"Pergunta sintética da unidade {unit_id}: selecione a opção correta.",
                "options": [
                    {"id": "wrong", "label": "Alternativa incorreta."},
                    {"id": "right", "label": "Alternativa correta."},
                ],
                "correct_option_id": "right",
                "feedback": {"correct": "Resposta correta.", "incorrect": "Revise a aula."},
                "completion_policy": "responded", "max_attempts": 2,
            },
        }, timeout=10), 200, f"unit {unit_id} quiz")
        quiz_ids.append(quiz["id"])

    exercise = _expect(session.post(f"{api_url}/api/blocks", json={
        "node_id": nodes[0]["id"], "type": "exercise_open", "title": "Prática sintética 1.1",
        "status": "draft", "data": {
            "prompt": "Explique em texto sua resposta à atividade sintética.", "allow_resubmit": True,
            "criteria": ["A resposta explica o raciocínio."],
            "rubric": "RUBRICA RESTRITA — fixture Beta 7.",
            "answer": "RESPOSTA PRIVADA — fixture Beta 7.",
        },
    }, timeout=10), 200, "manual exercise create")
    _expect(session.post(f"{api_url}/api/tracks/{track['id']}/publish", json={
        "note": "Somente fixture sintética no banco descartável Beta 7", "publish_children": True,
    }, timeout=10), 200, "synthetic-only fixture availability")

    reviewer_record = await db.users.find_one({"email": "reviewer@example.com"})
    if not reviewer_record:
        raise RuntimeError("Avaliador sintético Beta 7 ausente")
    reviewer = cast(dict[str, Any], reviewer_record)
    await db.learning_review_scopes.insert_one({
        "_id": f"{reviewer['_id']}:{track['id']}", "user_id": str(reviewer["_id"]),
        "track_id": track["id"], "operations": ["submissions.read", "submissions.grade"],
        "state": "active", "source": "beta7_synthetic_fixture",
    })
    await client.close()
    session.close()
    return {
        "track_id": track["id"], "track_slug": track["slug"],
        "first_node_id": nodes[0]["id"], "second_node_id": nodes[1]["id"],
        "first_quiz_id": quiz_ids[0], "second_quiz_id": quiz_ids[1], "exercise_id": exercise["id"],
    }


def main() -> int:
    print(json.dumps(asyncio.run(_seed()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
