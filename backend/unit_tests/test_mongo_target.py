import pytest

from test_support.mongo_target import make_disposable_mongo_url


@pytest.mark.parametrize(
    "url",
    [
        "mongodb://localhost:27017",
        "mongodb://127.0.0.1:27017/old?authSource=admin",
        "mongodb://[::1]:27017/?retryWrites=true",
    ],
)
def test_disposable_url_preserves_local_connection_options(url):
    result = make_disposable_mongo_url(url, "test_0123456789abcdef0123456789abcdef")

    assert result.endswith("/test_0123456789abcdef0123456789abcdef") or "/test_0123456789abcdef0123456789abcdef?" in result
    if "authSource" in url:
        assert "authSource=admin" in result
    if "retryWrites" in url:
        assert "retryWrites=true" in result
    assert "directConnection=true" in result


@pytest.mark.parametrize(
    "url",
    [
        "mongodb://staging.example.com:27017",
        "mongodb+srv://cluster.example.com",
        "mongodb://localhost:27017,staging.example.com:27017",
        "mongodb://localhost:27017/?replicaSet=rs0",
        "mongodb://localhost:27017/?loadBalanced=true",
        "mongodb://localhost:27017/?directConnection=false",
        "not-a-mongodb-url",
    ],
)
def test_disposable_url_rejects_non_local_or_ambiguous_targets(url):
    with pytest.raises(ValueError, match="MONGO_URL_TEST"):
        make_disposable_mongo_url(url, "test_0123456789abcdef0123456789abcdef")


def test_disposable_url_rejects_database_names_outside_generated_format():
    with pytest.raises(ValueError, match="database name"):
        make_disposable_mongo_url("mongodb://localhost:27017", "trilhacode")
