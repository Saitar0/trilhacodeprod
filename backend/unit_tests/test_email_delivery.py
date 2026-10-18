import asyncio
import logging
from types import SimpleNamespace

import email_delivery
import routes_auth


def _smtp_settings(**overrides):
    values = {
        "email_transport": "smtp",
        "smtp_host": "smtp.unit.test",
        "smtp_port": 587,
        "smtp_username": "smtp-unit-user",
        "smtp_password": "smtp-unit-password",
        "smtp_from_email": "no-reply@unit.test",
        "smtp_starttls": True,
        "smtp_ssl": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_smtp_delivery_authenticates_only_after_starttls(monkeypatch):
    events = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            events.append(("connect", host, port, timeout))

        def __enter__(self):
            events.append("enter")
            return self

        def __exit__(self, *_args):
            events.append("exit")

        def ehlo(self):
            events.append("ehlo")

        def starttls(self):
            events.append("starttls")

        def login(self, username, password):
            events.append(("login", username, password))

        def send_message(self, message):
            events.append(("send", message["To"], message["Subject"], message.get_content()))

    monkeypatch.setattr(email_delivery, "settings", _smtp_settings())
    monkeypatch.setattr(email_delivery.smtplib, "SMTP", FakeSMTP)

    email_delivery._deliver("Confirm account", "student@unit.test", "token=test-token")

    assert events == [
        ("connect", "smtp.unit.test", 587, 10), "enter", "ehlo", "starttls", "ehlo",
        ("login", "smtp-unit-user", "smtp-unit-password"),
        ("send", "student@unit.test", "Confirm account", "token=test-token\n"), "exit",
    ]


def test_smtp_ssl_delivery_does_not_downgrade_to_plain_smtp(monkeypatch):
    events = []

    class FakeSMTPSSL:
        def __init__(self, host, port, timeout):
            events.append(("tls-connect", host, port, timeout))

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def login(self, username, password):
            events.append(("login", username, password))

        def send_message(self, message):
            events.append(("send", message["To"]))

    monkeypatch.setattr(email_delivery, "settings", _smtp_settings(
        smtp_port=465, smtp_starttls=False, smtp_ssl=True,
    ))
    monkeypatch.setattr(email_delivery.smtplib, "SMTP_SSL", FakeSMTPSSL)

    email_delivery._deliver("Reset password", "student@unit.test", "token=test-token")

    assert events == [
        ("tls-connect", "smtp.unit.test", 465, 10),
        ("login", "smtp-unit-user", "smtp-unit-password"),
        ("send", "student@unit.test"),
    ]


def test_account_email_delivery_failure_does_not_log_token_address_or_smtp_error(monkeypatch, caplog):
    sensitive = "verification-token smtp-password student@unit.test"

    async def fail_delivery(*_args):
        raise RuntimeError(sensitive)

    monkeypatch.setattr(routes_auth, "send_email", fail_delivery)
    monkeypatch.setattr(routes_auth, "settings", SimpleNamespace(frontend_url="https://app.unit.test"))

    with caplog.at_level(logging.WARNING, logger="routes_auth"):
        asyncio.run(routes_auth._deliver_account_email(
            "Confirme seu e-mail", "student@unit.test", "verification-token",
        ))

    assert "Account email delivery failed" in caplog.text
    assert sensitive not in caplog.text
    assert "verification-token" not in caplog.text
    assert "student@unit.test" not in caplog.text
