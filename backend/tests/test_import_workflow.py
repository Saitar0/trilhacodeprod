import uuid

API = "/api"


def test_import_dry_run_persistence_and_reimport_are_idempotent(admin_session):
    slug = f"qa-import-{uuid.uuid4().hex[:12]}"
    payload = {
        "track": {"slug": slug, "title": "QA Import Persistence"},
        "nodes": [{
            "ref": "phase-1",
            "kind": "phase",
            "title": "Phase 1",
            "children": [{
                "ref": "topic-1",
                "kind": "topic",
                "title": "Topic 1",
                "blocks": [{"ref": "intro", "type": "theory_text", "data": {"body": "QA body"}}],
            }],
        }],
    }
    track_id = None
    try:
        preview = admin_session.post(f"{API}/import/track?dry_run=true", json=payload)
        assert preview.status_code == 200, preview.text
        assert preview.json()["ok"] is True
        assert preview.json()["dry_run"] is True
        assert preview.json()["summary"]["nodes_create"] == 2

        imported = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
        assert imported.status_code == 200, imported.text
        assert imported.json()["dry_run"] is False
        track_id = imported.json()["track"]["id"]

        repeated = admin_session.post(f"{API}/import/track?dry_run=false", json=payload)
        assert repeated.status_code == 200, repeated.text
        assert repeated.json()["summary"]["nodes_update"] == 2

        tree = admin_session.get(f"{API}/tracks/{track_id}/tree")
        assert tree.status_code == 200, tree.text
        assert len(tree.json()["nodes"]) == 2
        assert sum(tree.json()["block_counts"].values()) == 1
    finally:
        if track_id:
            admin_session.delete(f"{API}/tracks/{track_id}")

