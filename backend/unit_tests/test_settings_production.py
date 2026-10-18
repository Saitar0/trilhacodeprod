import pytest

from settings import Settings


BASE = {
    "env": "production",
    "mongo_url": "mongodb://appuser:opaque-test-password@mongo.internal:27017/app?authSource=admin",
    "db_name": "trilhacode_production",
    "jwt_secret": "0123456789abcdef0123456789abcdef",
    "frontend_url": "https://app.trilhacode.com",
    "cors_origins": ["https://app.trilhacode.com"],
    "cookie_domain": ".trilhacode.com",
    "cookie_samesite": "lax",
    "cookie_secure": True,
    "admin_email": "owner@trilhacode.com",
    "admin_password": "opaque-test-only-password",
}


def configured(**overrides):
    return Settings(_env_file=None, **(BASE | overrides))


def test_accepts_valid_production_origin_and_matching_cookie_domain():
    configured().validate_runtime()


@pytest.mark.parametrize("frontend_url,cookie_domain", [
    ("https://app.example.com", ".example.com"),
    ("https://app.example.invalid", ".example.invalid"),
    ("https://localhost", ".localhost"),
    ("https://app.local", ".local"),
])
def test_rejects_reserved_or_example_public_domains(frontend_url, cookie_domain):
    with pytest.raises(RuntimeError, match="reservado/de exemplo"):
        configured(frontend_url=frontend_url, cookie_domain=cookie_domain,
                   cors_origins=[frontend_url]).validate_runtime()


@pytest.mark.parametrize("frontend_url", [
    "https://app.trilhacode.com/login",
    "https://app.trilhacode.com/?next=/",
    "https://user@app.trilhacode.com",
])
def test_rejects_non_origin_frontend_url(frontend_url):
    with pytest.raises(RuntimeError, match="FRONTEND_URL"):
        configured(frontend_url=frontend_url, cors_origins=["https://app.trilhacode.com"]).validate_runtime()


def test_rejects_cookie_domain_unrelated_to_frontend():
    with pytest.raises(RuntimeError, match="COOKIE_DOMAIN deve corresponder"):
        configured(cookie_domain=".other.example.net").validate_runtime()


@pytest.mark.parametrize("mongo_url", [
    "mongodb://appuser:opaque-test-password@mongo.example.invalid:27017/app",
    "mongodb://appuser:opaque-test-password@mongo.example.com:27017/app",
])
def test_rejects_reserved_or_example_mongo_host(mongo_url):
    with pytest.raises(RuntimeError, match="MONGO_URL não pode usar host reservado/de exemplo"):
        configured(mongo_url=mongo_url).validate_runtime()


def test_rejects_reserved_cors_origin():
    with pytest.raises(RuntimeError, match="CORS_ORIGINS/FRONTEND_URL não podem usar hosts reservados/de exemplo"):
        configured(cors_origins=["https://public.example.org"]).validate_runtime()
