"""Stable domain constants shared by the API and services."""

STATUSES = ["draft", "published", "archived"]
PROGRESS_STATUSES = ["not_started", "in_progress", "completed"]
ROLES = ["admin", "editor", "student"]
DEFAULT_HIERARCHY = ["phase", "module", "submodule", "topic"]
DEFAULT_LABELS = {"phase": "Fase", "module": "Módulo", "submodule": "Submódulo", "topic": "Tópico"}
JWT_ALGORITHM = "HS256"

PERMISSIONS = {
    "admin": {"content.read", "content.write", "content.publish", "content.delete",
              "taxonomy.manage", "users.manage", "progress.write", "submissions.grade"},
    "editor": {"content.read", "content.write", "content.publish", "content.delete", "progress.write",
               "submissions.grade"},
    "student": {"progress.write"},
}
