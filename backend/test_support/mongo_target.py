"""Build a disposable test MongoDB URL without allowing remote targets."""

import ipaddress
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TEST_DATABASE = re.compile(r"test_[0-9a-f]{32}\Z")


def make_disposable_mongo_url(source_url: str, database_name: str) -> str:
    """Return a URL for a uniquely named database on a local MongoDB only.

    Backend tests drop their database at teardown, so accepting a remote host
    here could destroy real data when MONGO_URL_TEST is misconfigured. Tests
    use a direct local connection so replica-set discovery cannot redirect
    database operations to hosts advertised by a local MongoDB instance.
    """
    if not isinstance(source_url, str):
        raise ValueError("MONGO_URL_TEST must target a local MongoDB instance")

    try:
        parts = urlsplit(source_url)
        hostname = parts.hostname
        # Accessing .port also validates malformed port values.
        _ = parts.port
    except ValueError as exc:
        raise ValueError("MONGO_URL_TEST must target a local MongoDB instance") from exc

    if parts.scheme != "mongodb" or not hostname or "," in parts.netloc:
        raise ValueError("MONGO_URL_TEST must target a local MongoDB instance")

    try:
        local_host = hostname.lower() == "localhost" or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        local_host = hostname.lower() == "localhost"

    if not local_host:
        raise ValueError("MONGO_URL_TEST must target a local MongoDB instance")
    if not _TEST_DATABASE.fullmatch(database_name):
        raise ValueError("Disposable test database name is invalid")

    options = parse_qsl(parts.query, keep_blank_values=True)
    option_values = {key.lower(): value.lower() for key, value in options}
    if "replicaset" in option_values or option_values.get("loadbalanced") == "true":
        raise ValueError("MONGO_URL_TEST cannot enable MongoDB topology discovery")
    if option_values.get("directconnection") == "false":
        raise ValueError("MONGO_URL_TEST must use a direct MongoDB connection")

    options = [(key, value) for key, value in options if key.lower() != "directconnection"]
    options.append(("directConnection", "true"))
    return urlunsplit((parts.scheme, parts.netloc, f"/{database_name}", urlencode(options), parts.fragment))
