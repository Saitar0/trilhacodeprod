# ruff: noqa: EXE002
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from constants import DEFAULT_HIERARCHY, DEFAULT_LABELS


class TrackIn(BaseModel):
    title: str
    slug: Optional[str] = None
    subtitle: str = ""
    description: str = ""
    cover_url: str = ""
    status: str = "draft"
    visibility: str = "public"
    audience: list[str] = []
    difficulty: str = ""
    tag_ids: list[str] = []
    hierarchy: list[str] = DEFAULT_HIERARCHY
    level_labels: dict = DEFAULT_LABELS
    settings: dict = {}
    meta: dict = {}


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    audience: Optional[list[str]] = None
    difficulty: Optional[str] = None
    tag_ids: Optional[list[str]] = None
    hierarchy: Optional[list[str]] = None
    level_labels: Optional[dict] = None
    settings: Optional[dict] = None
    meta: Optional[dict] = None


class NodeIn(BaseModel):
    track_id: str
    parent_id: Optional[str] = None
    kind: str
    title: str
    summary: str = ""
    description: str = ""
    notes: str = ""
    guidance: str = ""
    pedagogical_type: str = ""
    requirement: str = ""
    depth: str = ""
    status: str = "draft"
    estimated_minutes: int = 0
    tag_ids: list[str] = []
    release: dict = {}
    meta: dict = {}


class NodeUpdate(BaseModel):
    parent_id: Optional[str] = None
    kind: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    guidance: Optional[str] = None
    pedagogical_type: Optional[str] = None
    requirement: Optional[str] = None
    depth: Optional[str] = None
    status: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tag_ids: Optional[list[str]] = None
    release: Optional[dict] = None
    meta: Optional[dict] = None


class BlockIn(BaseModel):
    node_id: str
    type: str
    title: str = ""
    data: dict = {}
    status: str = "published"


class BlockUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[dict] = None
    status: Optional[str] = None


class RelationUpdate(BaseModel):
    enforced: Optional[bool] = None
    note: Optional[str] = None
    prerequisite_kind: Literal["content_completed", "quiz_passed"] | None = None


class RelationIn(BaseModel):
    node_id: str
    target_id: str
    type: str
    enforced: bool = False
    note: str = ""
    prerequisite_kind: Literal["content_completed", "quiz_passed"] | None = None


class ReorderIn(BaseModel):
    ordered_ids: list[str]


class PublishIn(BaseModel):
    note: str = ""
    publish_children: bool = True


class APIModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class TrackOut(APIModel):
    id: str


class NodeOut(APIModel):
    id: str


class BlockOut(APIModel):
    id: str


class RelationOut(APIModel):
    id: str


class SearchResultOut(NodeOut):
    track_title: str = ""


class HistoryOut(APIModel):
    id: str


class VersionOut(APIModel):
    id: str


class OkOut(BaseModel):
    ok: bool
    deleted: int | None = None


class StatsOut(BaseModel):
    tracks: dict[str, int]
    nodes: dict[str, int]
    node_status: dict[str, int]
    blocks: dict[str, int]
    users: dict[str, int]
    relations: int
    versions: int


class AncestorOut(BaseModel):
    id: str
    title: str
    kind: str


class TrackTreeOut(BaseModel):
    track: TrackOut
    nodes: list[NodeOut]
    relations: list[RelationOut]
    block_counts: dict[str, int]


class NodeDetailOut(BaseModel):
    node: NodeOut
    blocks: list[BlockOut]
    relations: list[RelationOut]
    ancestors: list[AncestorOut]
    lock: dict | bool | None = None
