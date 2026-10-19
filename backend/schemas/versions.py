# ruff: noqa: EXE002
from pydantic import BaseModel


class RestoreIn(BaseModel):
    confirm: str
    note: str = ""


class VersionCompareOut(BaseModel):
    base: str
    target: str
    track: list[dict]
    nodes: dict
    blocks: dict
    relations: dict
    total_changes: int


class DeletedOut(BaseModel):
    deleted: bool


class ValidationIssueOut(BaseModel):
    model_config = {"extra": "allow"}
    level: str
    code: str
    message: str


class TrackValidationOut(BaseModel):
    ok: bool
    issues: list[ValidationIssueOut]


class ImportReportOut(BaseModel):
    model_config = {"extra": "allow"}
    ok: bool
    errors: list[dict]
    warnings: list[dict]
    summary: dict
    dry_run: bool
