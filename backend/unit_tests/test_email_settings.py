import pytest

from settings import Settings


def _production_settings(**overrides):
    values = {
        "env": "production",
        "mongo_url": "mongodb://app:password@mongo.internal:27017/trilha?authSource=admin",
        "db_name": "trilhacode_production",
        "jwt_secret": "this-is-a-valid-random-production-secret-value",
        "frontend_url": "https://app.trilhacode.com",
        "cors_origins": ["https://app.trilhacode.com"],
        "cookie_domain": ".trilhacode.com",
        "cookie_secure": True,
        "admin_email": "owner@trilhacode.com",
        "admin_password": "valid-administrator-password-12",
        "email_transport": "smtp",
        "smtp_host": "mail.trilhacode.com",
        "smtp_from_email": "no-reply@trilhacode.com",
        "smtp_starttls": True,
    }
    values.update(overrides)
    return Settings(**values)


def _staging_settings(**overrides):
    values = {
        "env": "staging",
        "email_transport": "smtp",
        "smtp_host": "smtp.unit.test",
        "smtp_from_email": "no-reply@unit.test",
        "smtp_starttls": True,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_requires_smtp_delivery():
    with pytest.raises(RuntimeError, match="EMAIL_TRANSPORT=smtp"):
        _production_settings(email_transport="local").validate_runtime()


def test_staging_requires_real_smtp_transport_and_tls():
    with pytest.raises(RuntimeError, match="EMAIL_TRANSPORT=smtp"):
        _staging_settings(email_transport="local").validate_runtime()
    with pytest.raises(RuntimeError, match="com TLS"):
        _staging_settings(smtp_starttls=False, smtp_ssl=False).validate_runtime()
    _staging_settings().validate_runtime()


def test_production_rejects_plaintext_and_conflicting_smtp_security():
    with pytest.raises(RuntimeError, match="com TLS"):
        _production_settings(smtp_starttls=False, smtp_ssl=False).validate_runtime()
    with pytest.raises(RuntimeError, match="não podem ser usados juntos"):
        _production_settings(smtp_ssl=True).validate_runtime()


def test_production_accepts_tls_smtp_without_credentials():
    _production_settings().validate_runtime()


def test_smtp_username_and_password_must_be_configured_together():
    with pytest.raises(RuntimeError, match="SMTP_USERNAME e SMTP_PASSWORD"):
        _production_settings(smtp_username="relay-user").validate_runtime()
