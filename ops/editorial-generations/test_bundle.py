"""Synthetic security tests for deterministic packaging and executor controls."""

from __future__ import annotations

import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
TEMPLATE = OPS / "executor-template"
sys.path.insert(0, str(TEMPLATE / "scripts"))
sys.path.insert(0, str(OPS))

import bundle_security as bundle
import prepare_bundle

SOURCE_SHA = "db9482437459330ec3f44f775f2e007c0fefdac9"
FILES = {name: f"synthetic-fixture:{name}".encode() for name in bundle.ALLOWED_FILES}


def _zip(entries: list[tuple[str, bytes, int | None]]) -> bytes:
    output = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, data, mode in entries:
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = ((mode if mode is not None else stat.S_IFREG | 0o644) << 16)
                archive.writestr(info, data)
    return output.getvalue()


class BundleSecurityTests(unittest.TestCase):
    def setUp(self):
        self.archive = bundle.build_archive(FILES, SOURCE_SHA)
        self.sha = bundle.sha256_bytes(self.archive)

    def verify(self, archive: bytes | None = None, source_sha: str = SOURCE_SHA):
        value = self.archive if archive is None else archive
        return bundle.verify_archive(
            value,
            expected_archive_sha256=bundle.sha256_bytes(value),
            expected_source_sha=source_sha,
        )

    def test_package_and_manifest_are_deterministic(self):
        self.assertEqual(self.archive, bundle.build_archive(dict(reversed(list(FILES.items()))), SOURCE_SHA))
        manifest, _ = self.verify()
        self.assertEqual(manifest["source"]["git_sha"], SOURCE_SHA)
        self.assertEqual(manifest["runtime"], {"python": "3.11", "pymongo": "4.18.2", "mongodb_major": 7})
        with zipfile.ZipFile(io.BytesIO(self.archive)) as archive:
            self.assertEqual(archive.namelist(), [*sorted(bundle.ALLOWED_FILES), "manifest.json"])
            self.assertTrue(all(item.date_time == (1980, 1, 1, 0, 0, 0) for item in archive.infolist()))

    def test_external_hash_and_file_hashes_are_checked(self):
        _manifest, payload = self.verify()
        self.assertEqual(set(payload), bundle.ALLOWED_FILES)
        altered = self.archive[:-1] + bytes([self.archive[-1] ^ 1])
        with self.assertRaises(bundle.BundleError):
            bundle.verify_archive(altered, expected_archive_sha256=self.sha, expected_source_sha=SOURCE_SHA)

    def test_manifest_tampering_is_rejected_even_with_matching_external_hash(self):
        entries = []
        with zipfile.ZipFile(io.BytesIO(self.archive)) as source:
            for name in source.namelist():
                data = source.read(name)
                if name == "manifest.json":
                    value = json.loads(data)
                    value["package_id"] = "tampered"
                    data = bundle.canonical_json(value) + b"\n"
                entries.append((name, data, None))
        altered = _zip(entries)
        with self.assertRaises(bundle.BundleError):
            self.verify(altered)

    def test_wrong_source_sha_is_rejected(self):
        with self.assertRaises(bundle.BundleError):
            self.verify(source_sha="a" * 40)

    def test_unexpected_and_missing_files_are_rejected(self):
        entries = [(name, content, None) for name, content in FILES.items()]
        with zipfile.ZipFile(io.BytesIO(self.archive)) as source:
            entries.append(("unexpected.txt", b"x", None))
            entries.append(("manifest.json", source.read("manifest.json"), None))
        with self.assertRaises(bundle.BundleError):
            self.verify(_zip(entries))
        with zipfile.ZipFile(io.BytesIO(self.archive)) as source:
            entries = [(name, source.read(name), None) for name in source.namelist() if name != next(iter(bundle.ALLOWED_FILES))]
        with self.assertRaises(bundle.BundleError):
            self.verify(_zip(entries))

    def test_path_traversal_absolute_and_non_normalized_paths_are_rejected(self):
        for unsafe in ("../escape.py", "/absolute.py", "C:/drive.py", "a//b.py", "a/./b.py", "a\\b.py"):
            malformed = _zip([(unsafe, b"x", None)])
            with self.subTest(unsafe=unsafe), self.assertRaises(bundle.BundleError):
                bundle.verify_archive(
                    malformed,
                    expected_archive_sha256=bundle.sha256_bytes(malformed),
                    expected_source_sha=SOURCE_SHA,
                )

    def test_duplicate_and_case_conflicting_entries_are_rejected(self):
        with zipfile.ZipFile(io.BytesIO(self.archive)) as source:
            name = next(iter(bundle.ALLOWED_FILES))
            entries = [(path, source.read(path), None) for path in source.namelist()]
            entries.append((name, b"duplicate", None))
            entries.append((name.swapcase(), b"case-conflict", None))
        with self.assertRaises(bundle.BundleError):
            self.verify(_zip(entries))

    def test_symlink_and_non_regular_entries_are_rejected(self):
        malformed = _zip([("link", b"target", stat.S_IFLNK | 0o777)])
        with self.assertRaises(bundle.BundleError):
            bundle.verify_archive(
                malformed,
                expected_archive_sha256=bundle.sha256_bytes(malformed),
                expected_source_sha=SOURCE_SHA,
            )

    def test_large_file_and_truncated_archive_are_rejected(self):
        oversized = {**FILES, next(iter(FILES)): b"x" * (bundle.MAX_FILE_BYTES + 1)}
        with self.assertRaises(bundle.BundleError):
            bundle.build_archive(oversized, SOURCE_SHA)
        oversized_zip = _zip(
            [(next(iter(bundle.ALLOWED_FILES)), b"x" * (bundle.MAX_FILE_BYTES + 1), None)]
        )
        with self.assertRaises(bundle.BundleError):
            bundle.verify_archive(
                oversized_zip,
                expected_archive_sha256=bundle.sha256_bytes(oversized_zip),
                expected_source_sha=SOURCE_SHA,
            )
        truncated = self.archive[:-12]
        with self.assertRaises(bundle.BundleError):
            self.verify(truncated)

    def test_safe_extraction_happens_only_after_whole_package_verifies(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "verified"
            manifest = bundle.extract_verified(
                self.archive,
                destination,
                expected_archive_sha256=self.sha,
                expected_source_sha=SOURCE_SHA,
            )
            self.assertEqual(manifest["source"]["git_sha"], SOURCE_SHA)
            self.assertEqual({p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()}, bundle.ALLOWED_FILES)
            with self.assertRaises(bundle.BundleError):
                bundle.extract_verified(self.archive, destination, expected_archive_sha256=self.sha, expected_source_sha=SOURCE_SHA)

    def test_lock_keeps_remote_transport_disabled_and_pins_versions(self):
        default_lock = json.loads((TEMPLATE / "config" / "bundle-lock.json").read_text(encoding="utf-8"))
        self.assertIs(default_lock["transport"]["enabled"], False)
        self.assertEqual(default_lock["package"]["sha256"], "0" * 64)
        source_sha = "a" * 40
        lock_data = {
            "format_version": 1,
            "transport": {
                "enabled": False,
                "executor_repository": "",
                "release_tag": f"editorial-generations-mongodb7-{source_sha[:12]}",
                "asset_name": f"editorial-generations-mongodb7-{source_sha}.zip",
            },
            "package": {
                "source_repository": "Saitar0/trilhacodeprod",
                "source_sha": source_sha,
                "sha256": "0" * 64,
                "python": "3.11",
                "pymongo": "4.18.2",
                "mongodb_major": 7,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            lock_path = Path(temporary) / "lock.json"
            lock_path.write_text(json.dumps(lock_data), encoding="utf-8")
            lock = prepare_bundle.load_lock(lock_path)
        self.assertIs(lock["transport"]["enabled"], False)
        self.assertEqual(lock["package"]["python"], "3.11")
        self.assertEqual(lock["package"]["pymongo"], "4.18.2")
        self.assertEqual(lock["package"]["mongodb_major"], 7)

    def test_disabled_transport_fails_before_network_or_extraction(self):
        source_sha = "b" * 40
        lock_data = {
            "format_version": 1,
            "transport": {
                "enabled": False,
                "executor_repository": "",
                "release_tag": f"editorial-generations-mongodb7-{source_sha[:12]}",
                "asset_name": f"editorial-generations-mongodb7-{source_sha}.zip",
            },
            "package": {
                "source_repository": "Saitar0/trilhacodeprod",
                "source_sha": source_sha,
                "sha256": "0" * 64,
                "python": "3.11",
                "pymongo": "4.18.2",
                "mongodb_major": 7,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            lock_path = Path(temporary) / "lock.json"
            destination = Path(temporary) / "should-not-exist"
            lock_path.write_text(json.dumps(lock_data), encoding="utf-8")
            stderr = io.StringIO()
            with patch("sys.argv", ["prepare_bundle.py", "--lock", str(lock_path), "--destination", str(destination)]), redirect_stderr(stderr):
                result = prepare_bundle.main()
            self.assertEqual(result, 2)
            self.assertFalse(destination.exists())
            self.assertFalse((Path(temporary) / "editorial-generations-download").exists())
            self.assertIn("Transporte está desabilitado", stderr.getvalue())


class SourceAndWorkflowSafetyTests(unittest.TestCase):
    def test_allowlist_excludes_editorial_and_sensitive_file_names(self):
        for name in bundle.ALLOWED_FILES:
            lowered = name.lower()
            self.assertNotIn("docs/courses/trilhacode", lowered)
            self.assertNotIn("docs/migracao", lowered)
            self.assertNotIn(".env", lowered)
            self.assertFalse(name.startswith(".git/"))
        self.assertNotIn("docs/courses/trilhacode/", "/".join(bundle.ALLOWED_FILES))

    def test_workflow_has_only_manual_trigger_and_read_permissions(self):
        workflow = (TEMPLATE / ".github/workflows/mongodb-homologation.yml").read_text(encoding="utf-8")
        self.assertIn("\non:\n  workflow_dispatch:", workflow)
        for trigger in ("push:", "pull_request:", "pull_request_target:", "workflow_run:", "release:", "repository_dispatch:"):
            self.assertNotIn(f"\n  {trigger}", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("secrets.", workflow)
        for forbidden in ("ssh", "deploy", "pull_request_target", "workflow_run", "release:"):
            self.assertNotIn(forbidden, workflow.lower())
        self.assertNotIn("docker/login-action", workflow)
        self.assertNotIn("ghcr.io", workflow.lower())
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("timeout-minutes:", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")
        self.assertRegex(workflow, r"actions/setup-python@[0-9a-f]{40}")

    def test_password_is_masked_before_compose_environment_export(self):
        script = (OPS / "run-ci.sh").read_text(encoding="utf-8")
        self.assertLess(script.index("::add-mask::"), script.index("export EDITORIAL_POC_ROOT_PASSWORD"))
        self.assertNotIn("set -x", script)
        self.assertNotIn("echo $ROOT_PASSWORD", script)
        existing_workflow = (ROOT / ".github/workflows/editorial-generations-mongodb.yml").read_text(encoding="utf-8")
        self.assertLess(existing_workflow.index("::add-mask::"), existing_workflow.index("EDITORIAL_POC_ROOT_PASSWORD=%s"))

    def test_compose_is_standalone_ephemeral_and_unpublished(self):
        compose = (OPS / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("image: mongo:7", compose)
        self.assertIn("internal: true", compose)
        self.assertIn("/data/db", compose)
        self.assertNotRegex(compose, r"(?m)^\s*ports:")
        self.assertNotRegex(compose, r"(?m)^\s*volumes:")
        self.assertNotIn("/var/run/docker.sock", compose)

    def test_resolved_compose_contract_accepts_only_disposable_shape(self):
        run_id = "a" * 32
        labels = {
            "io.trilhacode.editorial-poc.run": run_id,
            "com.docker.compose.project": f"editorial-poc-{run_id}",
        }
        resolved = {
            "services": {
                "mongo": {
                    "image": "mongo:7",
                    "tmpfs": ["/data/db"],
                    "networks": {"editorial_poc": {"aliases": ["mongo"]}},
                    "labels": labels,
                },
                "harness": {
                    "networks": {"editorial_poc": None},
                    "labels": labels,
                    "environment": {
                        "EDITORIAL_POC_MONGO_HOST": "mongo",
                        "EDITORIAL_POC_DISPOSABLE": "1",
                    },
                },
            },
            "networks": {"editorial_poc": {"internal": True}},
        }
        environment = os.environ.copy()
        environment["EDITORIAL_POC_RUN_ID"] = run_id
        valid = subprocess.run(
            [sys.executable, str(OPS / "validate_compose.py")],
            input=json.dumps(resolved),
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        resolved["services"]["mongo"]["ports"] = ["27017:27017"]
        invalid = subprocess.run(
            [sys.executable, str(OPS / "validate_compose.py")],
            input=json.dumps(resolved),
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertNotEqual(invalid.returncode, 0)

    def test_allowlisted_source_has_no_obvious_credential_material(self):
        patterns = (
            rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
            rb"\bAKIA[A-Z0-9]{16}\b",
        )
        for relative in bundle.ALLOWED_FILES:
            content = (ROOT / relative).read_bytes()
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, content), f"credential pattern in {relative}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
