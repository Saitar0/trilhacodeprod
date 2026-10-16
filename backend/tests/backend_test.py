"""Trilha Code - Backend regression tests (pytest).

Covers: auth (login/me/logout/refresh/brute force), permissions, tracks CRUD/publish/duplicate/versions,
nodes hierarchy/reorder/duplicate, blocks, relations, progress (visit/set/overview), meta/taxonomy.
"""
import uuid

import pytest

API = "/api"


# ---------- Health & root ----------
def test_root(session_factory):
    r = session_factory().get(f"{API}/")
    assert r.status_code == 200 and r.json().get("ok") is True


# ---------- Auth ----------
class TestAuth:
    def test_login_sets_cookies(self, login):
        s = login("admin@example.com")
        data = s.get(f"{API}/auth/me").json()
        assert data["email"] == "admin@example.com"
        assert data["role"] == "admin"
        assert "access_token" in s.cookies
        assert "refresh_token" in s.cookies

    def test_me_authenticated(self, admin_session):
        r = admin_session.get(f"{API}/auth/me")
        assert r.status_code == 200
        assert r.json()["role"] == "admin"
        assert "content.write" in r.json()["permissions"]

    def test_me_unauthenticated(self, session_factory):
        r = session_factory().get(f"{API}/auth/me")
        assert r.status_code == 401

    def test_logout_clears_cookies(self, login):
        s = login("student@example.com")
        r = s.post(f"{API}/auth/logout")
        assert r.status_code == 200
        r2 = s.get(f"{API}/auth/me")
        assert r2.status_code == 401

    def test_refresh(self, login):
        s = login("student@example.com")
        r = s.post(f"{API}/auth/refresh")
        assert r.status_code == 200

    def test_register_creates_student(self, session_factory):
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        s = session_factory()
        r = s.post(f"{API}/auth/register", json={"name": "Test User", "email": email, "password": "Test@1234"})
        assert r.status_code == 200
        assert r.json()["role"] == "student"
        assert r.json()["email"] == email

    def test_brute_force_lockout(self, session_factory):
        email = f"bf_{uuid.uuid4().hex[:6]}@example.com"
        statuses = []
        for _ in range(6):
            r = session_factory().post(f"{API}/auth/login", json={"email": email, "password": "wrong"})
            statuses.append(r.status_code)
        assert 429 in statuses, f"expected 429 after 5 tries, got {statuses}"


# ---------- Permissions ----------
class TestPermissions:
    def test_student_cannot_create_track(self, student_session):
        r = student_session.post(f"{API}/tracks", json={"title": "x"})
        assert r.status_code == 403

    def test_student_cannot_create_node(self, student_session, seeded_track):
        r = student_session.post(f"{API}/nodes", json={
            "track_id": seeded_track["id"], "kind": "phase", "title": "x"})
        assert r.status_code == 403

    def test_student_cannot_list_users(self, student_session):
        r = student_session.get(f"{API}/users")
        assert r.status_code == 403

    def test_editor_cannot_list_users(self, editor_session):
        r = editor_session.get(f"{API}/users")
        assert r.status_code == 403

    def test_editor_cannot_create_taxonomy(self, editor_session):
        r = editor_session.post(f"{API}/taxonomies", json={
            "group": "pedagogical_type", "key": f"test_{uuid.uuid4().hex[:4]}", "label": "x"})
        assert r.status_code == 403

    def test_editor_can_create_track(self, editor_session):
        r = editor_session.post(f"{API}/tracks", json={"title": "TEST_editor_track"})
        assert r.status_code == 200
        editor_session.delete(f"{API}/tracks/{r.json()['id']}")

    def test_student_only_sees_published(self, student_session, admin_session):
        # Admin creates a draft track
        r = admin_session.post(f"{API}/tracks", json={"title": "TEST_draft_unseen"})
        tid = r.json()["id"]
        try:
            tracks = student_session.get(f"{API}/tracks").json()
            assert not any(t["id"] == tid for t in tracks)
            r2 = student_session.get(f"{API}/tracks/{tid}")
            assert r2.status_code == 404
        finally:
            admin_session.delete(f"{API}/tracks/{tid}")


# ---------- Tracks CRUD/publish/duplicate ----------
class TestTracks:
    def test_create_update_publish_versions(self, admin_session):
        r = admin_session.post(f"{API}/tracks", json={"title": "TEST_lifecycle"})
        assert r.status_code == 200
        tid = r.json()["id"]
        try:
            # update level_labels
            u = admin_session.put(f"{API}/tracks/{tid}", json={
                "level_labels": {"phase": "Etapa", "module": "Mod", "submodule": "Sub", "topic": "Top"}})
            assert u.status_code == 200
            assert u.json()["level_labels"]["phase"] == "Etapa"

            # PUT status=published must 400
            bad = admin_session.put(f"{API}/tracks/{tid}", json={"status": "published"})
            assert bad.status_code == 400

            # create a node + block
            n = admin_session.post(f"{API}/nodes", json={
                "track_id": tid, "kind": "phase", "title": "TEST phase"}).json()
            nid = n["id"]
            btypes = admin_session.get(f"{API}/meta").json()["block_types"]
            next(b for b in btypes if b["key"] == "theory_text")
            b = admin_session.post(f"{API}/blocks", json={
                "node_id": nid, "type": "theory_text", "title": "intro",
                "data": {"body": "hi"}, "status": "draft"})
            assert b.status_code == 200

            # Publish
            pub = admin_session.post(f"{API}/tracks/{tid}/publish", json={"note": "v1"})
            assert pub.status_code == 200
            assert pub.json()["version"] == 1
            assert pub.json()["status"] == "published"

            # versions list
            versions = admin_session.get(f"{API}/tracks/{tid}/versions").json()
            assert len(versions) == 1
            vid = versions[0]["id"]
            v = admin_session.get(f"{API}/versions/{vid}")
            assert v.status_code == 200
            assert "snapshot" in v.json()
        finally:
            admin_session.delete(f"{API}/tracks/{tid}")

    def test_duplicate_track_deep(self, admin_session, seeded_track):
        r = admin_session.post(f"{API}/tracks/{seeded_track['id']}/duplicate")
        assert r.status_code == 200
        dup = r.json()
        assert dup["derived_from"] == seeded_track["id"]
        assert dup["status"] == "draft"
        try:
            tree = admin_session.get(f"{API}/tracks/{dup['id']}/tree").json()
            assert len(tree["nodes"]) > 0
            assert len(tree["relations"]) > 0
        finally:
            admin_session.delete(f"{API}/tracks/{dup['id']}")

    def test_reorder_tracks(self, admin_session):
        a = admin_session.post(f"{API}/tracks", json={"title": "TEST_a"}).json()["id"]
        b = admin_session.post(f"{API}/tracks", json={"title": "TEST_b"}).json()["id"]
        try:
            r = admin_session.put(f"{API}/tracks/reorder", json={"ordered_ids": [b, a]})
            assert r.status_code == 200
        finally:
            admin_session.delete(f"{API}/tracks/{a}")
            admin_session.delete(f"{API}/tracks/{b}")

    def test_delete_cascade(self, admin_session):
        tr = admin_session.post(f"{API}/tracks", json={"title": "TEST_cascade"}).json()
        tid = tr["id"]
        n = admin_session.post(f"{API}/nodes", json={"track_id": tid, "kind": "phase", "title": "p"}).json()
        admin_session.post(f"{API}/blocks", json={
            "node_id": n["id"], "type": "theory_text", "data": {"body": "x"}})
        admin_session.delete(f"{API}/tracks/{tid}")
        r = admin_session.get(f"{API}/tracks/{tid}")
        assert r.status_code == 404


# ---------- Nodes ----------
@pytest.fixture(scope="module")
def track(admin):
    tr = admin.post(f"{API}/tracks", json={"title": "TEST_nodes"}).json()
    yield tr
    admin.delete(f"{API}/tracks/{tr['id']}")


class TestNodes:

    def test_hierarchy_validation(self, admin_session, track):
        tid = track["id"]
        topic = admin_session.post(f"{API}/nodes", json={
            "track_id": tid, "kind": "topic", "title": "orphan topic"})
        # Allowed because topic has no parent and kind is in hierarchy
        assert topic.status_code == 200
        # Try to create module as child of topic -> should 400
        bad = admin_session.post(f"{API}/nodes", json={
            "track_id": tid, "kind": "module", "title": "bad", "parent_id": topic.json()["id"]})
        assert bad.status_code == 400

    def test_prevent_cycle(self, admin_session, track):
        tid = track["id"]
        a = admin_session.post(f"{API}/nodes", json={"track_id": tid, "kind": "phase", "title": "A"}).json()
        b = admin_session.post(f"{API}/nodes", json={
            "track_id": tid, "kind": "module", "title": "B", "parent_id": a["id"]}).json()
        # Try move A under B => should fail (cycle)
        r = admin_session.put(f"{API}/nodes/{a['id']}", json={"parent_id": b["id"], "kind": "module"})
        assert r.status_code == 400

    def test_reorder_and_duplicate(self, admin_session, track):
        tid = track["id"]
        p1 = admin_session.post(f"{API}/nodes", json={"track_id": tid, "kind": "phase", "title": "p1"}).json()
        p2 = admin_session.post(f"{API}/nodes", json={"track_id": tid, "kind": "phase", "title": "p2"}).json()
        r = admin_session.post(f"{API}/nodes/reorder", json={"ordered_ids": [p2["id"], p1["id"]]})
        assert r.status_code == 200
        d = admin_session.post(f"{API}/nodes/{p1['id']}/duplicate")
        assert d.status_code == 200
        assert "cópia" in d.json()["title"]


# ---------- Blocks & Relations ----------
@pytest.fixture(scope="module")
def ctx(admin):
    tr = admin.post(f"{API}/tracks", json={"title": "TEST_blocks"}).json()
    n1 = admin.post(f"{API}/nodes", json={"track_id": tr["id"], "kind": "phase", "title": "n1"}).json()
    n2 = admin.post(f"{API}/nodes", json={"track_id": tr["id"], "kind": "phase", "title": "n2"}).json()
    yield {"track": tr, "n1": n1, "n2": n2}
    admin.delete(f"{API}/tracks/{tr['id']}")


class TestBlocksRelations:

    def test_block_crud_and_unknown_type(self, admin_session, ctx):
        bad = admin_session.post(f"{API}/blocks", json={
            "node_id": ctx["n1"]["id"], "type": "totally_fake_type", "data": {}})
        assert bad.status_code == 400
        b = admin_session.post(f"{API}/blocks", json={
            "node_id": ctx["n1"]["id"], "type": "theory_text", "data": {"body": "hi"}}).json()
        upd = admin_session.put(f"{API}/blocks/{b['id']}", json={"data": {"body": "updated"}})
        assert upd.status_code == 200 and upd.json()["data"]["body"] == "updated"
        d = admin_session.delete(f"{API}/blocks/{b['id']}")
        assert d.status_code == 200

    def test_relations_rules(self, admin_session, ctx):
        n1, n2 = ctx["n1"]["id"], ctx["n2"]["id"]
        # self relation
        r = admin_session.post(f"{API}/relations", json={
            "node_id": n1, "target_id": n1, "type": "prerequisite"})
        assert r.status_code == 400
        ok = admin_session.post(f"{API}/relations", json={
            "node_id": n1, "target_id": n2, "type": "prerequisite"})
        assert ok.status_code == 200
        # duplicate
        dup = admin_session.post(f"{API}/relations", json={
            "node_id": n1, "target_id": n2, "type": "prerequisite"})
        assert dup.status_code == 400
        # cross-track
        tr2 = admin_session.post(f"{API}/tracks", json={"title": "TEST_other"}).json()
        n3 = admin_session.post(f"{API}/nodes", json={
            "track_id": tr2["id"], "kind": "phase", "title": "n3"}).json()
        cross = admin_session.post(f"{API}/relations", json={
            "node_id": n1, "target_id": n3["id"], "type": "prerequisite"})
        assert cross.status_code == 400
        admin_session.delete(f"{API}/tracks/{tr2['id']}")
        # delete relation
        d = admin_session.delete(f"{API}/relations/{ok.json()['id']}")
        assert d.status_code == 200


# ---------- Progress ----------
class TestProgress:
    def test_visit_and_complete(self, fresh_student, seeded_track):
        tree = fresh_student.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
        topic = next((n for n in tree["nodes"] if n["kind"] == "topic"), None)
        assert topic
        v = fresh_student.post(f"{API}/progress/visit", json={"node_id": topic["id"]})
        assert v.status_code == 200
        p = fresh_student.post(f"{API}/progress", json={
            "node_id": topic["id"], "status": "completed"})
        assert p.status_code == 200 and p.json()["status"] == "completed"

        tp = fresh_student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
        assert topic["id"] in tp["nodes"]
        assert tp["state"]["last_node_id"] == topic["id"]

        ov = fresh_student.get(f"{API}/progress/overview").json()
        assert "states" in ov and "completed" in ov


# ---------- Meta/taxonomies ----------
class TestMeta:
    def test_meta(self, student_session):
        r = student_session.get(f"{API}/meta")
        assert r.status_code == 200
        d = r.json()
        for k in ("taxonomies", "block_types", "tags", "statuses", "roles"):
            assert k in d
        assert any(b["key"] == "theory_text" for b in d["block_types"])

    def test_admin_taxonomy_crud(self, admin_session):
        key = f"test_{uuid.uuid4().hex[:6]}"
        r = admin_session.post(f"{API}/taxonomies", json={
            "group": "pedagogical_type", "key": key, "label": "TestLabel"})
        assert r.status_code == 200
        tid = r.json()["id"]
        u = admin_session.put(f"{API}/taxonomies/{tid}", json={"label": "Updated"})
        assert u.status_code == 200 and u.json()["label"] == "Updated"
        admin_session.delete(f"{API}/taxonomies/{tid}")
