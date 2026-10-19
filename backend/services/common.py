# ruff: noqa: EXE002
import re

from fastapi import HTTPException

from constants import STATUSES
from database import db
from serialization import oid


def slugify(text: str) -> str:
    text = text.lower().strip()
    for source, replacement in [("áàãâä", "a"), ("éèêë", "e"), ("íìîï", "i"), ("óòõôö", "o"),
                               ("úùûü", "u"), ("ç", "c")]:
        text = re.sub(f"[{source}]", replacement, text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "item"


def check_status(status: str | None) -> None:
    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=400, detail="Status inválido")


async def get_document(collection: str, document_id: str) -> dict:
    found = await db[collection].find_one({"_id": oid(document_id)})
    if found is None:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")
    return dict(found)


async def next_order(collection: str, query: dict) -> int:
    last = await db[collection].find(query).sort("order", -1).limit(1).to_list(1)
    return last[0]["order"] + 1 if last else 0


async def ancestors(node: dict) -> list[dict]:
    chain = []
    current = node
    while current.get("parent_id"):
        current = await db.nodes.find_one({"_id": oid(current["parent_id"])})
        if not current:
            break
        chain.insert(0, {"id": str(current["_id"]), "title": current["title"], "kind": current["kind"]})
    return chain


async def descendants(track_id: str, node_id: str) -> list[str]:
    nodes = await db.nodes.find({"track_id": track_id}, {"parent_id": 1}).to_list(10000)
    children = {}
    for node in nodes:
        children.setdefault(node.get("parent_id"), []).append(str(node["_id"]))
    result, stack = [], [node_id]
    while stack:
        current = stack.pop()
        result.append(current)
        stack.extend(children.get(current, []))
    return result
