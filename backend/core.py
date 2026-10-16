"""Compatibility facade for shared backend infrastructure.

New code should import from the focused modules. Existing imports from ``core``
remain supported during the incremental migration.
"""

from audit import audit
from constants import (
    DEFAULT_HIERARCHY,
    DEFAULT_LABELS,
    JWT_ALGORITHM,
    PERMISSIONS,
    PROGRESS_STATUSES,
    ROLES,
    STATUSES,
)
from core_utils import now
from database import client, db
from permissions import is_staff, require
from security import (
    create_access_token,
    create_refresh_token,
    current_user,
    decode_token,
    hash_password,
    verify_password,
)
from serialization import oid, ser

__all__ = [
    "DEFAULT_HIERARCHY", "DEFAULT_LABELS", "JWT_ALGORITHM", "PERMISSIONS",
    "PROGRESS_STATUSES", "ROLES", "STATUSES", "audit", "client",
    "create_access_token", "create_refresh_token", "current_user", "db",
    "decode_token", "hash_password", "is_staff", "now", "oid", "require",
    "ser", "verify_password",
]
