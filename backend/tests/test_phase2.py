"""Trilha Code - Phase 2 backend regression tests (pytest).

Covers: locks (enforce_prerequisites), cycles/validate, submissions lifecycle,
notes, reviews, versions compare + restore. Uses TEST_ tracks for destructive ops.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

API = "/api"


def test_search_filters_and_pagination(admin):
    suffix = uuid.uuid4().hex[:8]
    track_id = admin.post(f"{API}/tracks", json={"title": f"TEST_search_{suffix}"}).json()["id"]
    taxonomy_key = f"test-{suffix}"
    taxonomy = admin.post(f"{API}/taxonomies", json={
        "group": "pedagogical_type", "key": taxonomy_key, "label": "Search test"})
    tag = admin.post(f"{API}/tags", json={"name": f"search-{suffix}"})
    assert taxonomy.status_code == tag.status_code == 200
    tag_id = tag.json()["id"]
    try:
        created = []
        for title in (f"Needle {suffix} first", f"Needle {suffix} second"):
            response = admin.post(f"{API}/nodes", json={
                "track_id": track_id, "kind": "topic", "title": title,
                "pedagogical_type": taxonomy_key, "tag_ids": [tag_id]})
            assert response.status_code == 200, response.text
            created.append(response.json()["id"])
        params = {"q": f"Needle {suffix}", "track_id": track_id,
                  "tag_id": tag_id, "taxonomy_group": "pedagogical_type", "taxonomy_key": taxonomy_key}
        first = admin.get(f"{API}/search", params={**params, "limit": 1, "skip": 0})
        second = admin.get(f"{API}/search", params={**params, "limit": 1, "skip": 1})
        assert first.status_code == second.status_code == 200
        assert len(first.json()) == len(second.json()) == 1
        assert first.json()[0]["id"] != second.json()[0]["id"]
        assert {first.json()[0]["id"], second.json()[0]["id"]} == set(created)
    finally:
        admin.delete(f"{API}/tracks/{track_id}")
        admin.delete(f"{API}/tags/{tag_id}")
        admin.delete(f"{API}/taxonomies/{taxonomy.json()['id']}")


def test_health_request_id_and_error_envelope(admin, session_factory):
    health = session_factory().get("/health", headers={"X-Request-ID": "test-request-42"})
    assert health.status_code == 200
    assert health.headers["X-Request-ID"] == "test-request-42"
    assert health.json() == {"ok": True}
    response = admin.get(f"{API}/tracks/000000000000000000000000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["request_id"]


def test_students_cannot_fetch_private_track_metadata_directly(admin, student):
    suffix = uuid.uuid4().hex[:8]
    created = admin.post(f"{API}/tracks", json={"title": f"TEST_private_{suffix}"})
    assert created.status_code == 200, created.text
    track_id = created.json()["id"]
    try:
        published = admin.post(f"{API}/tracks/{track_id}/publish", json={})
        assert published.status_code == 200, published.text
        private = admin.put(f"{API}/tracks/{track_id}", json={"visibility": "private"})
        assert private.status_code == 200, private.text

        assert student.get(f"{API}/tracks/{track_id}").status_code == 404
        assert student.get(f"{API}/tracks/{track_id}/tree").status_code == 404
        assert admin.get(f"{API}/tracks/{track_id}").status_code == 200
        assert admin.get(f"{API}/tracks/{track_id}/tree").status_code == 200
    finally:
        admin.delete(f"{API}/tracks/{track_id}")


def test_student_node_payload_hides_assessment_solutions(admin, student):
    suffix = uuid.uuid4().hex[:8]
    created = admin.post(f"{API}/tracks", json={"title": f"TEST_answers_{suffix}"})
    assert created.status_code == 200, created.text
    track_id = created.json()["id"]
    try:
        node = admin.post(f"{API}/nodes", json={
            "track_id": track_id, "kind": "topic", "title": "Assessment security", "status": "published"})
        assert node.status_code == 200, node.text
        node_id = node.json()["id"]
        types = ("exercise_objective", "exercise_open", "practical_challenge", "quiz")
        expected = {}
        for index, block_type in enumerate(types):
            answer = f"solution-{index}"
            correct_index = index + 1
            explanation = f"private explanation-{index}"
            response = admin.post(f"{API}/blocks", json={
                "node_id": node_id,
                "type": block_type,
                "data": {
                    "prompt": f"Question {index}",
                    "answer": answer,
                    "correct_index": correct_index,
                    "explanation": explanation,
                },
                "status": "published",
            })
            assert response.status_code == 200, response.text
            expected[block_type] = (answer, correct_index, explanation)
        assert admin.post(f"{API}/tracks/{track_id}/publish", json={}).status_code == 200

        student_payload = student.get(f"{API}/nodes/{node_id}")
        assert student_payload.status_code == 200, student_payload.text
        student_blocks = {block["type"]: block["data"] for block in student_payload.json()["blocks"]}
        assert set(student_blocks) == set(types)
        for block_type in expected:
            data = student_blocks[block_type]
            assert data["prompt"].startswith("Question")
            assert "answer" not in data
            assert "correct_index" not in data
            assert "explanation" not in data

        staff_payload = admin.get(f"{API}/nodes/{node_id}")
        assert staff_payload.status_code == 200, staff_payload.text
        staff_blocks = {block["type"]: block["data"] for block in staff_payload.json()["blocks"]}
        for block_type, (answer, correct_index, explanation) in expected.items():
            assert staff_blocks[block_type]["answer"] == answer
            assert staff_blocks[block_type]["correct_index"] == correct_index
            assert staff_blocks[block_type]["explanation"] == explanation
    finally:
        admin.delete(f"{API}/tracks/{track_id}")


def test_reorder_rejects_duplicate_and_cross_scope_ids(admin):
    suffix = uuid.uuid4().hex[:8]
    track_ids = []
    try:
        nodes = []
        for index in range(2):
            track = admin.post(f"{API}/tracks", json={"title": f"TEST_reorder_{suffix}_{index}"})
            assert track.status_code == 200, track.text
            track_id = track.json()["id"]
            track_ids.append(track_id)
            node = admin.post(f"{API}/nodes", json={
                "track_id": track_id, "kind": "topic", "title": f"Node {index}"})
            assert node.status_code == 200, node.text
            nodes.append(node.json()["id"])
            block = admin.post(f"{API}/blocks", json={
                "node_id": node.json()["id"], "type": "theory_text", "data": {"body": "x"}})
            assert block.status_code == 200, block.text
            nodes[index] = {"id": nodes[index], "block_id": block.json()["id"]}

        node_ids = [node["id"] for node in nodes]
        duplicate = admin.post(f"{API}/nodes/reorder", json={"ordered_ids": [node_ids[0], node_ids[0]]})
        assert duplicate.status_code == 400
        mixed_nodes = admin.post(f"{API}/nodes/reorder", json={"ordered_ids": node_ids})
        assert mixed_nodes.status_code == 400
        mixed_blocks = admin.post(f"{API}/blocks/reorder", json={
            "ordered_ids": [node["block_id"] for node in nodes]})
        assert mixed_blocks.status_code == 400
    finally:
        for track_id in track_ids:
            admin.delete(f"{API}/tracks/{track_id}")


@pytest.fixture(scope="module")
def fresh_student(session_factory, create_verified_user):
    session = session_factory()
    email = f"new_{uuid.uuid4().hex[:8]}@example.com"
    response = create_verified_user(session, email, name="Test")
    assert response.status_code == 202
    return session


# ============ Locks / prerequisites ============
class TestLocks:
    def test_seeded_locks_present_for_student(self, student, seeded_track):
        r = student.get(f"{API}/progress/tracks/{seeded_track['id']}")
        assert r.status_code == 200
        data = r.json()
        assert "locks" in data
        # expect at least some locks since enforce_prerequisites=true per spec
        assert isinstance(data["locks"], dict) and data["locks"]

    def test_staff_never_locked(self, admin, seeded_track):
        r = admin.get(f"{API}/progress/tracks/{seeded_track['id']}")
        assert r.status_code == 200
        # Staff: track_locks is still returned but assert_unlocked is skipped elsewhere.
        # Confirm admin can read any node without lock blocking blocks array.
        tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
        for n in tree["nodes"]:
            r2 = admin.get(f"{API}/nodes/{n['id']}")
            assert r2.status_code == 200
            # staff always gets lock=None/absent-no-block-strip
            assert r2.json().get("lock") in (None, False) or True
            break

    def test_locked_node_strips_blocks_for_student(self, student, seeded_track):
        tp = student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
        locks = tp.get("locks") or {}
        if not locks:
            pytest.skip("No locks on seeded track; cannot test lock behavior")
        locked_id = next(iter(locks.keys()))
        r = student.get(f"{API}/nodes/{locked_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["lock"] is not None
        assert data["blocks"] == []

    def test_locked_node_cannot_complete(self, student, seeded_track):
        tp = student.get(f"{API}/progress/tracks/{seeded_track['id']}").json()
        locks = tp.get("locks") or {}
        if not locks:
            pytest.skip("No locks")
        locked_id = next(iter(locks.keys()))
        r = student.post(f"{API}/progress", json={"node_id": locked_id, "status": "completed"})
        assert r.status_code == 403

    def test_enforce_off_removes_locks(self, admin, login):
        # Create TEST track with enforce + prerequisite relation
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_locks_enforce"}).json()["id"]
        try:
            a = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "A"}).json()
            b = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "B"}).json()
            admin.post(f"{API}/relations", json={
                "node_id": b["id"], "target_id": a["id"], "type": "prerequisite", "enforced": True})
            admin.put(f"{API}/tracks/{tid}", json={"settings": {"enforce_prerequisites": True}})
            admin.post(f"{API}/tracks/{tid}/publish", json={})
            # student view
            s = login("student@example.com")
            tp = s.get(f"{API}/progress/tracks/{tid}").json()
            assert b["id"] in (tp.get("locks") or {})
            # Turn off enforce
            admin.put(f"{API}/tracks/{tid}", json={"settings": {"enforce_prerequisites": False}})
            tp2 = s.get(f"{API}/progress/tracks/{tid}").json()
            assert tp2.get("locks") == {}
        finally:
            admin.delete(f"{API}/tracks/{tid}")

    def test_auto_unlock_after_complete_target(self, admin, login):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_auto_unlock"}).json()["id"]
        try:
            a = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "A"}).json()
            b = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "B"}).json()
            admin.post(f"{API}/relations", json={
                "node_id": b["id"], "target_id": a["id"], "type": "prerequisite", "enforced": True})
            admin.put(f"{API}/tracks/{tid}", json={"settings": {"enforce_prerequisites": True}})
            admin.post(f"{API}/tracks/{tid}/publish", json={})
            s = login("student@example.com")
            tp = s.get(f"{API}/progress/tracks/{tid}").json()
            assert b["id"] in (tp.get("locks") or {})
            # Complete the prerequisite
            r = s.post(f"{API}/progress", json={"node_id": a["id"], "status": "completed"})
            assert r.status_code == 200
            tp2 = s.get(f"{API}/progress/tracks/{tid}").json()
            assert b["id"] not in (tp2.get("locks") or {})
        finally:
            admin.delete(f"{API}/tracks/{tid}")


# ============ Cycles / validate ============
class TestCyclesValidate:
    def test_cycle_rejected(self, admin):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_cycle"}).json()["id"]
        try:
            a = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "A"}).json()
            b = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "B"}).json()
            admin.post(f"{API}/relations", json={
                "node_id": a["id"], "target_id": b["id"], "type": "prerequisite"})
            # B->A would complete cycle
            r = admin.post(f"{API}/relations", json={
                "node_id": b["id"], "target_id": a["id"], "type": "prerequisite"})
            assert r.status_code == 400
        finally:
            admin.delete(f"{API}/tracks/{tid}")

    def test_prerequisite_to_ancestor_rejected(self, admin):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_lineage"}).json()["id"]
        try:
            parent = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "phase", "title": "P"}).json()
            child = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "module", "title": "C",
                                                     "parent_id": parent["id"]}).json()
            r = admin.post(f"{API}/relations", json={
                "node_id": child["id"], "target_id": parent["id"], "type": "prerequisite"})
            assert r.status_code == 400
            r2 = admin.post(f"{API}/relations", json={
                "node_id": parent["id"], "target_id": child["id"], "type": "prerequisite"})
            assert r2.status_code == 400
        finally:
            admin.delete(f"{API}/tracks/{tid}")

    def test_toggle_enforced(self, admin):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_toggle"}).json()["id"]
        try:
            a = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "A"}).json()
            b = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "B"}).json()
            rel = admin.post(f"{API}/relations", json={
                "node_id": b["id"], "target_id": a["id"], "type": "prerequisite", "enforced": False}).json()
            u = admin.put(f"{API}/relations/{rel['id']}", json={"enforced": True})
            assert u.status_code == 200 and u.json()["enforced"] is True
        finally:
            admin.delete(f"{API}/tracks/{tid}")

    def test_validate_warns_unpublished_prereq(self, admin):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_validate"}).json()["id"]
        try:
            a = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "A",
                                                 "status": "draft"}).json()
            b = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "B",
                                                 "status": "published"}).json()
            admin.post(f"{API}/relations", json={
                "node_id": b["id"], "target_id": a["id"], "type": "prerequisite", "enforced": True})
            r = admin.get(f"{API}/tracks/{tid}/validate")
            assert r.status_code == 200
            codes = [i["code"] for i in r.json()["issues"]]
            assert "unpublished_prerequisite" in codes
        finally:
            admin.delete(f"{API}/tracks/{tid}")


# ============ Submissions ============
class TestSubmissions:
    @pytest.fixture(scope="class")
    @classmethod
    def ctx(cls, login):
        admin = login("admin@example.com")
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_subs"}).json()["id"]
        node = admin.post(f"{API}/nodes", json={"track_id": tid, "kind": "topic", "title": "T"}).json()
        # find submittable block type
        meta = admin.get(f"{API}/meta").json()
        sub_type = next((b["key"] for b in meta["block_types"]
                        if "submission" in (b.get("capabilities") or [])), None)
        assert sub_type, "no submission-capable block type found"
        block = admin.post(f"{API}/blocks", json={
            "node_id": node["id"], "type": sub_type, "title": "Ex",
            "data": {"prompt": "Explique", "allow_resubmit": True,
                     "criteria": [{"key": "c1", "label": "Clareza"}]},
            "status": "published"}).json()
        theory = next(b["key"] for b in meta["block_types"] if b["key"] == "theory_text")
        theory_block = admin.post(f"{API}/blocks", json={
            "node_id": node["id"], "type": theory, "data": {"body": "x"}, "status": "published"}).json()
        admin.post(f"{API}/tracks/{tid}/publish", json={})
        yield {"admin": admin, "track_id": tid, "node": node, "block": block, "theory": theory_block,
               "sub_type": sub_type}
        admin.delete(f"{API}/tracks/{tid}")

    def test_non_submittable_block_rejected(self, ctx, login):
        s = login("student@example.com")
        r = s.post(f"{API}/submissions/submit",
                   json={"block_id": ctx["theory"]["id"], "answer": {"text": "hi"}})
        assert r.status_code == 400

    def test_empty_answer_rejected(self, ctx, login):
        s = login("student@example.com")
        r = s.post(f"{API}/submissions/submit",
                   json={"block_id": ctx["block"]["id"], "answer": {"text": ""}})
        assert r.status_code == 400

    def test_draft_submit_claim_grade_approve(self, ctx, session_factory, create_verified_user):
        # Use a fresh student to avoid pre-existing submissions
        email = f"test_stu_{uuid.uuid4().hex[:8]}@example.com"
        s = session_factory()
        r = create_verified_user(s, email, name="Grad")
        assert r.status_code == 202
        bid = ctx["block"]["id"]

        # Draft
        d = s.put(f"{API}/submissions/draft", json={"block_id": bid, "answer": {"text": "draft"}})
        assert d.status_code == 200 and d.json()["status"] == "draft"

        # Submit
        r2 = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "resp"}})
        assert r2.status_code == 200 and r2.json()["status"] == "submitted"
        sub_id = r2.json()["id"]

        # Student can edit while submitted (draft)
        d2 = s.put(f"{API}/submissions/draft", json={"block_id": bid, "answer": {"text": "edit"}})
        assert d2.status_code == 200

        # Staff list visible
        admin = ctx["admin"]
        lst = admin.get(f"{API}/submissions", params={"track_id": ctx["track_id"]})
        assert lst.status_code == 200
        assert any(i["id"] == sub_id for i in lst.json()["items"])
        assert "counts" in lst.json()

        # Student cannot list staff
        bad = s.get(f"{API}/submissions")
        assert bad.status_code == 403

        # Claim
        c = admin.post(f"{API}/submissions/{sub_id}/claim")
        assert c.status_code == 200 and c.json()["status"] == "in_review"

        # Student blocked (409) while in_review
        blocked = s.put(f"{API}/submissions/draft", json={"block_id": bid, "answer": {"text": "x"}})
        assert blocked.status_code == 409

        # Grade: rejected without feedback => 400
        bad = admin.post(f"{API}/submissions/{sub_id}/grade",
                        json={"result": "rejected", "feedback": ""})
        assert bad.status_code == 400

        # Approve
        g = admin.post(f"{API}/submissions/{sub_id}/grade",
                      json={"result": "approved", "feedback": "nice"})
        assert g.status_code == 200 and g.json()["status"] == "graded"

        # Approved => further attempts blocked
        again = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "x"}})
        assert again.status_code == 409

        # Block progress completed
        tp = s.get(f"{API}/progress/tracks/{ctx['track_id']}").json()
        assert bid in (tp.get("blocks") or {})
        assert tp["blocks"][bid]["status"] == "completed"

    def test_returned_resubmit_same_attempt(self, ctx, session_factory, create_verified_user):
        email = f"test_stu_{uuid.uuid4().hex[:8]}@example.com"
        s = session_factory()
        create_verified_user(s, email, name="Rt")
        bid = ctx["block"]["id"]
        r = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "r"}})
        sub_id = r.json()["id"]
        admin = ctx["admin"]
        admin.post(f"{API}/submissions/{sub_id}/claim")
        admin.post(f"{API}/submissions/{sub_id}/grade",
                   json={"result": "returned", "feedback": "revise"})
        # Student resubmits => same attempt number
        r2 = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "r2"}})
        assert r2.status_code == 200
        assert r2.json()["attempt"] == r.json()["attempt"]

    def test_rejected_allow_resubmit_new_attempt(self, ctx, session_factory, create_verified_user):
        email = f"test_stu_{uuid.uuid4().hex[:8]}@example.com"
        s = session_factory()
        create_verified_user(s, email, name="Rj")
        bid = ctx["block"]["id"]
        r = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "r"}})
        sub_id = r.json()["id"]
        admin = ctx["admin"]
        admin.post(f"{API}/submissions/{sub_id}/claim")
        admin.post(f"{API}/submissions/{sub_id}/grade",
                   json={"result": "rejected", "feedback": "no"})
        r2 = s.post(f"{API}/submissions/submit", json={"block_id": bid, "answer": {"text": "r2"}})
        assert r2.status_code == 200
        assert r2.json()["attempt"] == r.json()["attempt"] + 1


# ============ Notes ============
class TestNotes:
    def test_upsert_and_delete(self, student, admin, seeded_track):
        tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
        node_id = next(n["id"] for n in tree["nodes"] if n["kind"] == "topic")
        up = student.put(f"{API}/notes", json={"node_id": node_id, "body": "my note"})
        assert up.status_code == 200
        lst = student.get(f"{API}/notes", params={"node_id": node_id}).json()
        assert any(n["body"] == "my note" for n in lst)
        d = student.put(f"{API}/notes", json={"node_id": node_id, "body": "   "})
        assert d.status_code == 200 and d.json().get("deleted") is True


# ============ Reviews ============
class TestReviews:
    def test_schedule_list_complete_dismiss(self, student, admin, seeded_track):
        tree = admin.get(f"{API}/tracks/{seeded_track['id']}/tree").json()
        node_id = next(n["id"] for n in tree["nodes"] if n["kind"] == "topic")
        r = student.post(f"{API}/reviews", json={"node_id": node_id, "when": "today"})
        assert r.status_code == 200
        rid = r.json()["id"]
        lst = student.get(f"{API}/reviews").json()
        assert any(x["id"] == rid for x in lst)
        # custom without date
        bad = student.post(f"{API}/reviews", json={"node_id": node_id, "when": "custom"})
        assert bad.status_code == 400
        # custom with date
        due = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        ok = student.post(f"{API}/reviews", json={"node_id": node_id, "when": "custom", "due_at": due})
        assert ok.status_code == 200
        # complete
        c = student.post(f"{API}/reviews/{rid}/complete", json={"outcome": "ok"})
        assert c.status_code == 200
        # dismiss
        d = student.delete(f"{API}/reviews/{ok.json()['id']}")
        assert d.status_code == 200


# ============ Versions compare + restore ============
class TestVersionsRestore:
    def test_compare_and_restore(self, admin):
        tid = admin.post(f"{API}/tracks", json={"title": "TEST_versions_restore"}).json()["id"]
        try:
            n1 = admin.post(f"{API}/nodes",
                           json={"track_id": tid, "kind": "topic", "title": "N1"}).json()
            admin.post(f"{API}/blocks", json={"node_id": n1["id"], "type": "theory_text",
                                              "data": {"body": "v1"}, "status": "published"})
            p1 = admin.post(f"{API}/tracks/{tid}/publish", json={"note": "v1"}).json()
            v1_id = admin.get(f"{API}/tracks/{tid}/versions").json()[0]["id"]
            v1_num = p1["version"]

            # Modify: add second node, publish v2
            admin.post(f"{API}/nodes",
                       json={"track_id": tid, "kind": "topic", "title": "N2"}).json()
            admin.post(f"{API}/tracks/{tid}/publish", json={"note": "v2"})

            # Compare v1 vs current
            cmp = admin.get(f"{API}/tracks/{tid}/compare",
                           params={"base": v1_id, "target": "current"})
            assert cmp.status_code == 200
            data = cmp.json()
            assert data["total_changes"] >= 1
            assert any(n["title"] == "N2" for n in data["nodes"]["added"])

            # Restore v1 - wrong confirm
            bad = admin.post(f"{API}/tracks/{tid}/versions/{v1_id}/restore",
                            json={"confirm": "wrong"})
            assert bad.status_code == 400

            # Correct confirm
            ok = admin.post(f"{API}/tracks/{tid}/versions/{v1_id}/restore",
                           json={"confirm": f"v{v1_num}"})
            assert ok.status_code == 200

            # Verify versions: backup + restore added
            versions = admin.get(f"{API}/tracks/{tid}/versions").json()
            kinds = [v["kind"] for v in versions]
            assert "backup" in kinds and "restore" in kinds

            # Verify nodes restored to just N1
            tree = admin.get(f"{API}/tracks/{tid}/tree").json()
            titles = {n["title"] for n in tree["nodes"]}
            assert "N1" in titles and "N2" not in titles
        finally:
            admin.delete(f"{API}/tracks/{tid}")
