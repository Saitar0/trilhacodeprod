"""Central application configuration loaded from environment variables."""

from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_RESERVED_PUBLIC_HOSTS = {
    "example.com", "example.net", "example.org", "example.edu", "example", "localhost",
    "invalid", "test", "local",
}


def _hostname(value: str) -> str | None:
    try:
        return (urlsplit(value).hostname or "").rstrip(".").lower() or None
    except ValueError:
        return None


def _is_reserved_public_host(host: str | None) -> bool:
    if not host:
        return True
    if host in _RESERVED_PUBLIC_HOSTS:
        return True
    return any(host.endswith(suffix) for suffix in (
        ".example", ".example.com", ".example.net", ".example.org", ".example.edu",
        ".invalid", ".test", ".localhost", ".local",
    ))


def _is_https_origin(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.path
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )

    env: Literal["development", "staging", "production"] = "development"
    mongo_url: str = "mongodb://localhost:27017"
    db_name: str = "trilhacode_dev"
    jwt_secret: str = "dev-only-change-this-secret"
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = []
    cookie_domain: str | None = None
    cookie_samesite: Literal["lax", "strict", "none"] | None = None
    cookie_secure: bool | None = None
    trusted_proxy_ips: list[str] = []
    sentry_dsn: str | None = None
    sentry_environment: str | None = None
    sentry_release: str | None = None
    email_transport: Literal["smtp", "local"] = "local"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_starttls: bool = True
    smtp_ssl: bool = False
    local_email_dir: str = ".local-emails"

    admin_email: str | None = None
    admin_password: str | None = None
    editor_email: str | None = None
    editor_password: str | None = None
    student_email: str | None = None
    student_password: str | None = None

    @field_validator("env", mode="before")
    @classmethod
    def normalize_env(cls, value):
        return value.lower() if isinstance(value, str) else value

    @field_validator("cookie_samesite", mode="before")
    @classmethod
    def normalize_samesite(cls, value):
        if isinstance(value, str):
            return value.lower() or None
        return value

    @field_validator("cookie_domain", "admin_email", "admin_password", "editor_email", "editor_password",
                     "student_email", "student_password", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value):
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("cookie_secure", mode="before")
    @classmethod
    def normalize_optional_bool(cls, value):
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("cors_origins", "trusted_proxy_ips", mode="before")
    @classmethod
    def parse_csv(cls, value):
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def effective_cors_origins(self) -> list[str]:
        origins = list(self.cors_origins)
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    @property
    def effective_cookie_samesite(self) -> Literal["lax", "strict", "none"]:
        if self.cookie_samesite:
            return self.cookie_samesite
        return "lax"

    @property
    def effective_cookie_secure(self) -> bool:
        if self.cookie_secure is not None:
            return self.cookie_secure
        return self.env in {"staging", "production"}

    def trusts_proxy(self, peer_ip: str | None) -> bool:
        if not peer_ip:
            return False
        try:
            address = ip_address(peer_ip)
            return any(address in ip_network(item, strict=False) for item in self.trusted_proxy_ips)
        except ValueError:
            return False

    def _email_configuration_problems(self) -> list[str]:
        problems = []
        if (self.email_transport != "smtp" or not self.smtp_host or not self.smtp_from_email
                or (not self.smtp_starttls and not self.smtp_ssl)):
            problems.append("EMAIL_TRANSPORT=smtp e SMTP_HOST/SMTP_FROM_EMAIL com TLS são obrigatórios")
        if self.smtp_host and self.smtp_host.lower().endswith(".invalid"):
            problems.append("SMTP_HOST ainda usa o domínio fictício de exemplo")
        if self.smtp_from_email and (".invalid" in self.smtp_from_email.lower()
                                     or "@example.com" in self.smtp_from_email.lower()):
            problems.append("SMTP_FROM_EMAIL ainda usa um endereço fictício de exemplo")
        if self.smtp_starttls and self.smtp_ssl:
            problems.append("SMTP_STARTTLS e SMTP_SSL não podem ser usados juntos")
        if bool(self.smtp_username) != bool(self.smtp_password):
            problems.append("SMTP_USERNAME e SMTP_PASSWORD devem ser definidos juntos")
        return problems

    def validate_runtime(self) -> None:
        if self.env == "staging" and self.cookie_secure is False:
            raise RuntimeError("Configuração inválida: COOKIE_SECURE deve ser true em staging.")
        if self.env == "staging" and self.email_transport != "local":
            email_problems = self._email_configuration_problems()
            if email_problems:
                raise RuntimeError("Configuração inválida para staging: " + "; ".join(email_problems) + ".")
        if self.is_production and (
            len(self.jwt_secret) < 32
            or self.jwt_secret.lower() in {
                "dev-only-change-this-secret",
                "change-me",
                "change-this-secret",
                "secret",
            }
            or self.jwt_secret.lower().startswith(("replace_", "example_", "your_"))
        ):
            raise RuntimeError(
                "Configuração inválida: em production, JWT_SECRET deve ter pelo menos 32 caracteres "
                "e não pode ser um segredo de exemplo/desenvolvimento."
            )
        if self.is_production:
            problems = self._email_configuration_problems()
            mongo = urlsplit(self.mongo_url)
            mongo_host = mongo.hostname.rstrip(".").lower() if mongo.hostname else None
            if (mongo.scheme not in {"mongodb", "mongodb+srv"} or not mongo.hostname
                    or mongo.hostname in {"localhost", "127.0.0.1", "::1"}
                    or not mongo.username or not mongo.password):
                problems.append("MONGO_URL deve apontar para MongoDB remoto com usuário e senha")
            if _is_reserved_public_host(mongo_host):
                problems.append("MONGO_URL não pode usar host reservado/de exemplo")
            if not self.db_name or self.db_name == "trilhacode_dev":
                problems.append("DB_NAME deve ser definido para production")
            if self.cookie_secure is False:
                problems.append("COOKIE_SECURE deve ser true")
            if self.effective_cookie_samesite == "none" and not self.effective_cookie_secure:
                problems.append("SameSite=None exige cookies Secure")
            if not self.cookie_domain or not self.cookie_domain.startswith("."):
                problems.append("COOKIE_DOMAIN deve ser definido como .<dominio>")
            else:
                cookie_host = self.cookie_domain[1:].rstrip(".").lower()
                frontend_host = _hostname(self.frontend_url)
                if _is_reserved_public_host(cookie_host):
                    problems.append("COOKIE_DOMAIN não pode usar domínio reservado/de exemplo")
                if frontend_host and not (
                    frontend_host == cookie_host or frontend_host.endswith("." + cookie_host)
                ):
                    problems.append("COOKIE_DOMAIN deve corresponder ao host de FRONTEND_URL")
            if not _is_https_origin(self.frontend_url):
                problems.append("FRONTEND_URL deve ser uma origem HTTPS sem caminho, query ou fragmento")
            elif _is_reserved_public_host(_hostname(self.frontend_url)):
                problems.append("FRONTEND_URL não pode usar host reservado/de exemplo")
            if any(not _is_https_origin(origin) for origin in self.effective_cors_origins):
                problems.append("CORS_ORIGINS/FRONTEND_URL devem ser origens HTTPS sem caminho")
            elif any(_is_reserved_public_host(_hostname(origin)) for origin in self.effective_cors_origins):
                problems.append("CORS_ORIGINS/FRONTEND_URL não podem usar hosts reservados/de exemplo")
            if (not self.admin_email or self.admin_email.endswith(".invalid") or not self.admin_password
                    or len(self.admin_password) < 16 or self.admin_password.lower().startswith(("replace_", "example_", "your_"))):
                problems.append("ADMIN_EMAIL e ADMIN_PASSWORD (mínimo 16 caracteres) são obrigatórios")
            if problems:
                raise RuntimeError("Configuração insegura para production: " + "; ".join(problems) + ".")


settings = Settings()
settings.validate_runtime()
