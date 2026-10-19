"""Small shared utilities that do not depend on application services."""

from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)
