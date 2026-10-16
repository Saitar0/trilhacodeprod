"""Scale check: import ~2.5k nodes / 5k blocks, publish, compare, delete."""
import re
import time

import requests

U = re.search(r"VITE_BACKEND_URL=(\S+)", open("/app/frontend/.env").read()).group(1) + "/api"
A = requests.Session(); A.post(f"{U}/auth/login", json={"email": "admin@trilhacode.dev", "password": "Admin@123"})
body = "Lorem ipsum dolor sit amet, texto de teoria placeholder. " * 60
nodes = [{"ref": f"f{f}", "kind": "phase", "title": f"Fase {f}", "status": "published", "children": [
    {"ref": f"f{f}m{m}", "kind": "module", "title": f"Módulo {f}.{m}", "status": "published", "children": [
        {"ref": f"f{f}m{m}t{t}", "kind": "topic", "title": f"Tópico {f}.{m}.{t}", "status": "published", "depth": "media",
         "blocks": [{"ref": "b1", "type": "theory_text", "data": {"body": body}}, {"ref": "b2", "type": "summary", "data": {"body": body}}]}
        for t in range(20)]} for m in range(12)]} for f in range(10)]
rels = [{"from": f"f{f}m{m}t{t}", "to": f"f{f}m{m}t{t-1}", "type": "prerequisite", "enforced": True}
        for f in range(10) for m in range(12) for t in range(1, 20)]
p = {"track": {"slug": "test-scale", "title": "TEST Scale"}, "nodes": nodes, "relations": rels}
t = time.time(); r = A.post(f"{U}/import/track?dry_run=true", json=p, timeout=300).json(); print("dry", r["ok"], r["summary"], f"{time.time()-t:.1f}s")
t = time.time(); r = A.post(f"{U}/import/track?dry_run=false", json=p, timeout=300).json(); tid = r["track"]["id"]; print("import", f"{time.time()-t:.1f}s")
t = time.time(); A.post(f"{U}/tracks/{tid}/publish", json={"note": "v1"}, timeout=300); print("publish", f"{time.time()-t:.1f}s")
v = A.get(f"{U}/tracks/{tid}/versions").json()[0]; print("version", v["stats"], v["raw_bytes"], "->", v["packed_bytes"], "chunks", v["chunks"])
t = time.time(); d = A.get(f"{U}/tracks/{tid}/compare", params={"base": v["id"], "target": "current"}, timeout=300).json(); print("compare", d["total_changes"], f"{time.time()-t:.1f}s")
t = time.time(); A.get(f"{U}/tracks/{tid}/tree", timeout=300); print("tree", f"{time.time()-t:.1f}s")
A.delete(f"{U}/tracks/{tid}", timeout=300); print("deleted")
