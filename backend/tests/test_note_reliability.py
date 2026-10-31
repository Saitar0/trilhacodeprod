"""Integration coverage for private, versioned student notes."""

import uuid

from database import db

API = "/api"


def _first_node(student, track):
    response = student.get(f"{API}/tracks/{track['id']}/tree")
    assert response.status_code == 200
    return response.json()["nodes"][0]


def test_note_versions_detect_conflicts_and_keep_delete_tombstones(
    fresh_student, seeded_track,
):
    node = _first_node(fresh_student, seeded_track)
    created = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "rascunho inicial", "expected_version": 0,
    })
    assert created.status_code == 200, created.text
    assert created.json()["version"] == 1

    updated = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "versão atual", "expected_version": 1,
    })
    assert updated.status_code == 200, updated.text
    assert updated.json()["version"] == 2

    stale = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "edição de outro dispositivo", "expected_version": 1,
    })
    assert stale.status_code == 409
    assert stale.json()["error"]["details"]["code"] == "note_version_conflict"
    assert stale.json()["error"]["details"]["current"]["body"] == "versão atual"
    assert stale.json()["error"]["details"]["current"]["version"] == 2

    deleted = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "   ", "expected_version": 2,
    })
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": True, "version": 3}
    assert fresh_student.get(f"{API}/notes", params={"node_id": node["id"]}).json() == []

    tombstone = fresh_student.get(
        f"{API}/notes", params={"node_id": node["id"], "include_deleted": "true"},
    ).json()
    assert len(tombstone) == 1
    assert tombstone[0]["deleted"] is True
    assert tombstone[0]["version"] == 3

    stale_restore = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "edição antiga", "expected_version": 2,
    })
    assert stale_restore.status_code == 409
    restored = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "anotação restaurada", "expected_version": 3,
    })
    assert restored.status_code == 200
    assert restored.json()["version"] == 4
    assert restored.json()["deleted"] is False


def test_note_updates_are_scoped_to_the_authenticated_user(
    fresh_student, seeded_track, session_factory, create_verified_user, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    owner_note = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "nota privada", "expected_version": 0,
    })
    assert owner_note.status_code == 200

    other = session_factory()
    other_email = f"note_reader_{uuid.uuid4().hex}@example.com"
    create_verified_user(other, other_email)
    other_user_id = other.get(f"{API}/auth/me").json()["id"]
    other_user_notes = other.get(f"{API}/notes", params={"node_id": node["id"]}).json()
    assert other_user_notes == []

    other_note = other.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "outra nota", "expected_version": 0,
    })
    assert other_note.status_code == 200
    assert event_loop.run_until_complete(db.notes.count_documents({
        "user_id": other_user_id, "node_id": node["id"], "body": "outra nota",
    })) == 1
    owner_notes = fresh_student.get(f"{API}/notes", params={"node_id": node["id"]}).json()
    assert len(owner_notes) == 1
    assert owner_notes[0]["body"] == "nota privada"


def test_legacy_note_without_version_can_be_upgraded_and_note_size_is_limited(
    fresh_student, seeded_track, event_loop,
):
    node = _first_node(fresh_student, seeded_track)
    user = fresh_student.get(f"{API}/auth/me").json()
    event_loop.run_until_complete(db.notes.insert_one({
        "user_id": user["id"], "node_id": node["id"], "block_id": None,
        "track_id": node["track_id"], "body": "nota anterior",
    }))

    upgrade = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "nota anterior atualizada", "expected_version": 0,
    })
    assert upgrade.status_code == 200, upgrade.text
    assert upgrade.json()["version"] == 1

    too_large = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "x" * 50_001, "expected_version": 1,
    })
    assert too_large.status_code == 422


def test_note_write_without_version_does_not_overwrite_versioned_note(
    fresh_student, seeded_track,
):
    node = _first_node(fresh_student, seeded_track)
    fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "servidor", "expected_version": 0,
    })
    response = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "cliente antigo sem versão",
    })
    assert response.status_code == 409
    assert response.json()["error"]["details"]["current"]["body"] == "servidor"


def test_note_updates_reject_stale_device_versions(
    fresh_student, seeded_track, session_factory,
):
    node = _first_node(fresh_student, seeded_track)
    owner = fresh_student.get(f"{API}/auth/me").json()
    second_device = session_factory()
    login = second_device.post(f"{API}/auth/login", json={
        "email": owner["email"], "password": "Test@1234",
    })
    assert login.status_code == 200

    initial = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "v1", "expected_version": 0,
    })
    assert initial.status_code == 200
    updated = fresh_student.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "v2", "expected_version": 1,
    })
    stale_device = second_device.put(f"{API}/notes", json={
        "node_id": node["id"], "body": "conteúdo local v1", "expected_version": 1,
    })
    assert updated.status_code == 200
    assert stale_device.status_code == 409
    assert stale_device.json()["error"]["details"]["current"]["body"] == "v2"
