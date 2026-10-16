"""Smoke tests for the hardening pack. Run: python tests/smoke_hardening.py (backend on localhost:8001)."""
import concurrent.futures as cf
import json
import requests

import re
U = re.search(r"VITE_BACKEND_URL=(\S+)", open("/app/frontend/.env").read()).group(1) + "/api"


def login(email, pw):
    s = requests.Session()
    r = s.post(f"{U}/auth/login", json={"email": email, "password": pw})
    assert r.ok, r.text
    return s


A = login("admin@trilhacode.dev", "Admin@123")
S = login("aluno@trilhacode.dev", "Aluno@123")
ok = lambda c, m: print(("PASS " if c else "FAIL ") + m)  # noqa: E731

PAYLOAD = {
    "track": {"slug": "test-import-hardening", "title": "TEST Import", "settings": {"enforce_prerequisites": True}},
    "nodes": [
        {"ref": "f1", "kind": "phase", "title": "Fase 1", "status": "published", "children": [
            {"ref": "f1-m1", "kind": "module", "title": "Módulo A", "status": "published", "children": [
                {"ref": "t1", "kind": "topic", "title": "Tópico 1", "status": "published", "depth": "alta",
                 "requirement": "obrigatorio", "pedagogical_type": "solo", "tags": ["fundamentos", "nova-tag-import"],
                 "blocks": [{"ref": "b1", "type": "theory_text", "data": {"body": "# Olá"}}]},
                {"ref": "t2", "kind": "topic", "title": "Tópico 2", "status": "published"},
                {"ref": "t3", "kind": "topic", "title": "Tópico rascunho", "status": "draft"}]}]},
        {"ref": "f2", "kind": "phase", "title": "Fase 2 rascunho", "status": "draft", "children": [
            {"ref": "t4", "kind": "topic", "title": "Publicado sob rascunho", "status": "published"}]}],
    "relations": [{"from": "t2", "to": "t1", "type": "prerequisite", "enforced": True}],
}

bad = json.loads(json.dumps(PAYLOAD))
bad["nodes"][0]["children"][0]["children"][0]["kind"] = "phase"
bad["relations"].append({"from": "t1", "to": "t2", "type": "prerequisite"})
r = A.post(f"{U}/import/track?dry_run=true", json=bad).json()
ok(not r["ok"] and len(r["errors"]) >= 2, f"import validation catches errors ({len(r['errors'])})")
r = A.post(f"{U}/import/track?dry_run=true", json=PAYLOAD).json()
ok(r["ok"] and r["dry_run"] and r["summary"]["nodes_create"] == 7, f"dry run plan {r['summary']}")
r = A.post(f"{U}/import/track?dry_run=false", json=PAYLOAD).json()
tid = r["track"]["id"]
r2 = A.post(f"{U}/import/track?dry_run=false", json=PAYLOAD).json()
tree = A.get(f"{U}/tracks/{tid}/tree").json()
ok(r2["summary"]["nodes_update"] == 7 and len(tree["nodes"]) == 7 and len(tree["relations"]) == 1
   and sum(tree["block_counts"].values()) == 1, "import is idempotent")
A.post(f"{U}/tracks/{tid}/publish", json={"note": "v1", "publish_children": False})
ids = {n["title"]: n["id"] for n in tree["nodes"]}

# access leaks
code = lambda r: r.status_code  # noqa: E731
ok(code(S.get(f"{U}/nodes/{ids['Publicado sob rascunho']}")) == 404, "student blocked: published node under draft ancestor")
ok(code(S.get(f"{U}/nodes/{ids['Tópico rascunho']}")) == 404, "student blocked: draft node")
ok(code(S.put(f"{U}/notes", json={"node_id": ids["Tópico rascunho"], "body": "x"})) == 404, "student blocked: note on draft")
ok(code(S.post(f"{U}/reviews", json={"node_id": ids["Publicado sob rascunho"], "when": "soon"})) == 404, "student blocked: review on hidden")
srch = S.get(f"{U}/search", params={"q": "Publicado sob"}).json()
ok(not srch, "search hides nodes under draft ancestors")
A.put(f"{U}/tracks/{tid}", json={"visibility": "private"})
ok(code(S.get(f"{U}/nodes/{ids['Tópico 1']}")) == 404 and code(S.get(f"{U}/tracks/{tid}/tree")) == 404, "student blocked: private track")
A.put(f"{U}/tracks/{tid}", json={"visibility": "public"})
ok(code(S.get(f"{U}/nodes/{ids['Tópico 1']}")) == 200, "student allowed on visible node")

# reviews: concurrent schedule -> one pending
with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(lambda _: S.post(f"{U}/reviews", json={"node_id": ids["Tópico 1"], "when": "soon"}), range(6)))
pend = [x for x in S.get(f"{U}/reviews").json() if x["node_id"] == ids["Tópico 1"]]
ok(len(pend) == 1, f"single pending review under concurrency ({len(pend)})")

# submissions: concurrent submit -> one attempt; concurrent claim -> one wins
bt = A.post(f"{U}/blocks", json={"node_id": ids["Tópico 1"], "type": "exercise_open", "data": {"prompt": "?"}}).json()
with cf.ThreadPoolExecutor(6) as ex:
    list(ex.map(lambda _: S.post(f"{U}/submissions/submit", json={"block_id": bt["id"], "answer": {"text": "r"}}), range(6)))
mine = [x for x in S.get(f"{U}/submissions/mine", params={"node_id": ids["Tópico 1"]}).json() if x["block_id"] == bt["id"]]
ok(len(mine) == 1, f"single attempt under concurrent submit ({len(mine)})")
with cf.ThreadPoolExecutor(4) as ex:
    codes = list(ex.map(lambda _: A.post(f"{U}/submissions/{mine[0]['id']}/claim").status_code, range(4)))
ok(codes.count(200) == 1, f"claim race: exactly one wins {codes}")

# versions: compare, restore, orphans
A.post(f"{U}/tracks/{tid}/publish", json={"note": "v2 with exercise"})
vs = A.get(f"{U}/tracks/{tid}/versions").json()
v1 = [v for v in vs if v["version"] == 1][0]
ok(v1.get("storage") == "chunked-zlib" and "snapshot" not in v1, f"chunked storage ({v1.get('packed_bytes')}B packed)")
diff = A.get(f"{U}/tracks/{tid}/compare", params={"base": v1["id"], "target": "current"}).json()
ok(len(diff["blocks"]["added"]) == 1, "compare v1→current shows added exercise")
ok(code(A.post(f"{U}/tracks/{tid}/versions/{v1['id']}/restore", json={"confirm": "v9"})) == 400, "restore needs confirm")
r = A.post(f"{U}/tracks/{tid}/versions/{v1['id']}/restore", json={"confirm": "v1"})
ok(r.ok and r.json()["version"] == 3, "restore creates v3")
mine = [x for x in S.get(f"{U}/submissions/mine").json() if x["block_id"] == bt["id"]]
ok(not mine, "orphaned submission hidden from student after restore")
ok(any(x.get("orphaned") for x in A.get(f"{U}/submissions", params={"status": "in_review"}).json()["items"]), "orphan flagged for staff")

# block types not reset
btypes = A.get(f"{U}/meta").json()["block_types"]
eo = [b for b in btypes if b["key"] == "exercise_open"][0]
A.put(f"{U}/block-types/{eo['id']}", json={"fields": [f for f in eo["fields"] if f["name"] != "max_score"]})
print("NOTE: restart backend then run check_block_type() to confirm persistence")
A.delete(f"{U}/tracks/{tid}")
