from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from seed import _EMAIL, _seed_user


@pytest.mark.parametrize("email", [
    "admin.qa@example.com",
    "editor.qa@example.com",
    "student.qa@example.com",
])
def test_seed_emails_are_accepted_by_emailstr(email):
    assert str(_EMAIL.validate_python(email)) == email


def test_seed_rejects_reserved_invalid_domain():
    with pytest.raises(ValidationError):
        _EMAIL.validate_python("admin.qa@example.invalid")


def test_seed_rejects_invalid_email_before_lookup(monkeypatch, event_loop):
    import seed

    class Users:
        async def find_one(self, _query):
            pytest.fail("invalid seed email reached the database")

    monkeypatch.setattr(seed, "db", SimpleNamespace(users=Users()))
    with pytest.raises(ValidationError):
        event_loop.run_until_complete(
            _seed_user("admin.qa@example.invalid", "unused", "Admin", "admin")
        )


def test_seed_normalizes_valid_email_before_lookup(monkeypatch, event_loop):
    import seed

    class Users:
        email = None

        async def find_one(self, query):
            self.email = query["email"]
            return {"email": self.email}

    users = Users()
    monkeypatch.setattr(seed, "db", SimpleNamespace(users=users))
    event_loop.run_until_complete(_seed_user(" Admin.QA@Example.com ", "unused", "Admin", "admin"))

    assert users.email == "admin.qa@example.com"
