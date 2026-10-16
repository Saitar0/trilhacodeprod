"""Central application configuration loaded from environment variables."""

from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        return self.is_production

    def trusts_proxy(self, peer_ip: str | None) -> bool:
        if not peer_ip:
            return False
        try:
            address = ip_address(peer_ip)
            return any(address in ip_network(item, strict=False) for item in self.trusted_proxy_ips)
        except ValueError:
            return False

    def validate_runtime(self) -> None:
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
            problems = []
            mongo = urlsplit(self.mongo_url)
            if (mongo.scheme not in {"mongodb", "mongodb+srv"} or not mongo.hostname
                    or mongo.hostname in {"localhost", "127.0.0.1", "::1"}
                    or not mongo.username or not mongo.password):
                problems.append("MONGO_URL deve apontar para MongoDB remoto com usuário e senha")
            if not self.db_name or self.db_name == "trilhacode_dev":
                problems.append("DB_NAME deve ser definido para production")
            if self.cookie_secure is False:
                problems.append("COOKIE_SECURE deve ser true")
            if self.effective_cookie_samesite == "none" and not self.effective_cookie_secure:
                problems.append("SameSite=None exige cookies Secure")
            if not self.cookie_domain or not self.cookie_domain.startswith("."):
                problems.append("COOKIE_DOMAIN deve ser definido como .<dominio>")
            elif ".invalid" in self.cookie_domain.lower():
                problems.append("COOKIE_DOMAIN ainda usa o domínio fictício de exemplo")
            if not self.frontend_url.startswith("https://"):
                problems.append("FRONTEND_URL deve usar HTTPS")
            elif ".invalid" in self.frontend_url.lower():
                problems.append("FRONTEND_URL ainda usa o domínio fictício de exemplo")
            if any(not origin.startswith("https://") for origin in self.effective_cors_origins):
                problems.append("CORS_ORIGINS/FRONTEND_URL devem usar HTTPS")
            if (not self.admin_email or self.admin_email.endswith(".invalid") or not self.admin_password
                    or len(self.admin_password) < 16 or self.admin_password.lower().startswith(("replace_", "example_", "your_"))):
                problems.append("ADMIN_EMAIL e ADMIN_PASSWORD (mínimo 16 caracteres) são obrigatórios")
            if problems:
                raise RuntimeError("Configuração insegura para production: " + "; ".join(problems) + ".")


settings = Settings()
settings.validate_runtime()
