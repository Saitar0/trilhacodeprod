"""Create a synthetic, disposable-only learning fixture after the host gate."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any, cast

from pymongo import MongoClient

from test_support.beta6_1_internal_target import connect_internal_verified_target


def _require(response, expected: int, action: str) -> dict:
    if response.status_code != expected:
        raise RuntimeError(f"Fixture setup failed at {action}: HTTP {response.status_code}")
    return response.json() if response.content else {}


async def _seed_database() -> dict:
    target, ownership_client = connect_internal_verified_target(
        os.environ,
        lambda uri: MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=2000),
    )
    verified_client = cast(Any, ownership_client)
    try:
        expected_owner = f"_{target.phase}_test_owner"
        collections = set(verified_client[target.database].list_collection_names())
        if collections - {expected_owner}:
            raise RuntimeError("Beta 6.1 fixture refuses to reuse a non-empty test database")
    finally:
        verified_client.close()

    from database import client, db
    from indexes import ensure_indexes
    from migrations import migrate
    from security import hash_password
    from seed import BLOCK_TYPES, SUBMITTABLE, TAXONOMIES

    await db.command("ping")
    await ensure_indexes()
    users = [
        ("admin", "admin@example.com", os.environ["E2E_ADMIN_PASSWORD"], "Synthetic Beta 6.1 Admin"),
        ("student", "student@example.com", os.environ["E2E_STUDENT_PASSWORD"], "Synthetic Beta 6.1 Student"),
        ("editor", "reviewer@example.com", os.environ["E2E_REVIEWER_PASSWORD"], "Synthetic Beta 6.1 Reviewer"),
        ("editor", "unscoped@example.com", os.environ["E2E_UNSCOPED_PASSWORD"], "Synthetic Beta 6.1 Unscoped"),
    ]
    await db.users.insert_many([
        {
            "email": email,
            "name": name,
            "password_hash": hash_password(password),
            "role": role,
            "email_verified": True,
            "is_active": True,
            "profile": {"bio": "", "goals": "", "preferences": {}},
        }
        for role, email, password, name in users
    ])
    for index, (group, key, label, description, color) in enumerate(TAXONOMIES):
        await db.taxonomies.insert_one({
            "group": group, "key": key, "label": label, "description": description,
            "color": color, "order": index,
        })
    for index, (key, label, category, icon, fields) in enumerate(BLOCK_TYPES):
        await db.block_types.insert_one({
            "key": key, "label": label, "category": category, "icon": icon,
            "fields": fields, "description": "", "enabled": True,
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
    _require(login, 200, "admin login")

    suffix = uuid.uuid4().hex[:10]
    track = _require(session.post(f"{api_url}/api/tracks", json={
        "title": f"Trilha Code Beta 6.1 {suffix}",
        "slug": f"beta6-1-jornada-{suffix}",
        "status": "draft",
        "visibility": "public",
    }, timeout=10), 200, "track creation")
    phase = _require(session.post(f"{api_url}/api/nodes", json={
        "track_id": track["id"], "kind": "phase", "title": "Fase sintética", "status": "draft",
    }, timeout=10), 200, "phase creation")
    module = _require(session.post(f"{api_url}/api/nodes", json={
        "track_id": track["id"], "parent_id": phase["id"], "kind": "module",
        "title": "Módulo sintético", "status": "draft",
    }, timeout=10), 200, "module creation")
    node = _require(session.post(f"{api_url}/api/nodes", json={
        "track_id": track["id"], "parent_id": module["id"], "kind": "topic",
        "title": "Aula Beta 6.1", "summary": "Conteúdo sintético para validação HTTP e navegador.",
        "status": "draft",
    }, timeout=10), 200, "topic creation")

    theory = _require(session.post(f"{api_url}/api/blocks", json={
        "node_id": node["id"], "type": "theory_text", "title": "Conteúdo da aula", "status": "draft",
        "data": {"body": "# Aula de teste\n\nConteúdo didático **sintético** da Beta 6.1."},
    }, timeout=10), 200, "theory creation")
    summary = _require(session.post(f"{api_url}/api/blocks", json={
        "node_id": node["id"], "type": "summary", "title": "Resumo", "status": "draft",
        "data": {"body": "Resumo sintético."},
    }, timeout=10), 200, "summary creation")
    quiz = _require(session.post(f"{api_url}/api/blocks", json={
        "node_id": node["id"], "type": "quiz", "title": "Quiz Beta 6.1", "status": "draft",
        "data": {
            "activity_schema_version": 1,
            "prompt": "Qual alternativa descreve uma variável?",
            "options": [
                {"id": "wrong", "label": "Um comentário sem valor."},
                {"id": "right", "label": "Um nome associado a um valor."},
            ],
            "correct_option_id": "right",
            "feedback": {"correct": "Correto.", "incorrect": "Revise a definição."},
            "completion_policy": "responded",
            "max_attempts": 2,
        },
    }, timeout=10), 200, "quiz creation")
    exercise = _require(session.post(f"{api_url}/api/blocks", json={
        "node_id": node["id"], "type": "exercise_open", "title": "Exercício Beta 6.1", "status": "draft",
        "data": {
            "prompt": "Explique em suas palavras como uma variável armazena um valor.",
            "allow_resubmit": True,
            "criteria": ["Explica o vínculo entre nome e valor."],
            "rubric": "RUBRICA RESTRITA BETA 6.1.",
            "answer": "RESPOSTA PRIVADA BETA 6.1.",
        },
    }, timeout=10), 200, "exercise creation")
    _require(session.post(f"{api_url}/api/tracks/{track['id']}/publish", json={
        "note": "Fixture sintética do ambiente descartável Beta 6.1", "publish_children": True,
    }, timeout=10), 200, "synthetic fixture availability")

    reviewer = await db.users.find_one({"email": "reviewer@example.com"})
    if not reviewer:
        raise RuntimeError("Synthetic reviewer was not created")
    await db.learning_review_scopes.insert_one({
        "_id": f"{reviewer['_id']}:{track['id']}",
        "user_id": str(reviewer["_id"]),
        "track_id": track["id"],
        "operations": ["submissions.read", "submissions.grade"],
        "state": "active",
        "source": "beta6_1_synthetic_fixture",
    })
    await client.close()
    session.close()
    return {
        "track_id": track["id"], "track_slug": track["slug"], "node_id": node["id"],
        "theory_id": theory["id"], "summary_id": summary["id"],
        "quiz_id": quiz["id"], "exercise_id": exercise["id"],
    }


def main() -> int:
    fixture = asyncio.run(_seed_database())
    print(json.dumps(fixture, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
