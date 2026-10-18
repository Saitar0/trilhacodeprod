"""Small synchronous SMTP/local delivery adapters for account emails."""

import asyncio
import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4

from settings import settings

log = logging.getLogger(__name__)


def _deliver(subject: str, recipient: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email or "trilhacode@localhost"
    message["To"] = recipient
    message.set_content(body)

    if settings.email_transport == "local":
        directory = Path(settings.local_email_dir)
        directory.mkdir(parents=True, exist_ok=True)
        try:
            directory.chmod(0o700)
        except OSError:
            pass
        path = directory / f"{uuid4().hex}.eml"
        path.write_bytes(message.as_bytes())
        try:
            path.chmod(0o600)
        except OSError:
            pass
        log.info("Account email saved to local disposable mailbox (%s)", path.name)
        return

    if settings.email_transport != "smtp" or not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("Email transport is not configured")
    if settings.smtp_ssl:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            _smtp_login(server)
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.ehlo()
            if settings.smtp_starttls:
                server.starttls()
                server.ehlo()
            _smtp_login(server)
            server.send_message(message)


def _smtp_login(server) -> None:
    if settings.smtp_username:
        if not settings.smtp_password:
            raise RuntimeError("SMTP_PASSWORD is required when SMTP_USERNAME is set")
        server.login(settings.smtp_username, settings.smtp_password)


async def send_email(subject: str, recipient: str, body: str) -> None:
    await asyncio.to_thread(_deliver, subject, recipient, body)
