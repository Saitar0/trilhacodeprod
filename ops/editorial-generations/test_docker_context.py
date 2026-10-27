"""Unit tests for the local-only Docker context gate."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

import verify_docker_context as context_guard


class DockerContextGuardTests(unittest.TestCase):
    def _run_with_endpoint(
        self, endpoint: str, *, platform: str = "linux", os_type: str = "linux"
    ):
        responses = [
            "default",
            json.dumps({"Host": endpoint}),
            f"27.0.0|{os_type}",
        ]
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(context_guard.sys, "platform", platform),
            patch.object(context_guard, "_run", side_effect=responses) as run,
        ):
            result = context_guard.verify()
        return result, run

    def test_accepts_only_linux_engine_on_local_linux_socket(self):
        result, run = self._run_with_endpoint("unix:///var/run/docker.sock")
        self.assertEqual(result, ("default", "27.0.0"))
        self.assertEqual(run.call_count, 3)

    def test_accepts_local_docker_desktop_linux_pipe_on_windows(self):
        result, _ = self._run_with_endpoint(
            "npipe:////./pipe/dockerDesktopLinuxEngine",
            platform="win32",
        )
        self.assertEqual(result, ("default", "27.0.0"))

    def test_rejects_remote_ssh_and_tcp_endpoints_before_engine_access(self):
        for endpoint in ("ssh://builder@remote", "tcp://10.0.0.8:2376"):
            with self.subTest(endpoint=endpoint):
                with (
                    patch.dict(os.environ, {}, clear=True),
                    patch.object(context_guard.sys, "platform", "linux"),
                    patch.object(
                        context_guard,
                        "_run",
                        side_effect=["remote", json.dumps({"Host": endpoint})],
                    ) as run,
                    self.assertRaises(context_guard.DockerContextError),
                ):
                    context_guard.verify()
                self.assertEqual(run.call_count, 2)

    def test_rejects_non_linux_docker_desktop_pipe(self):
        with self.assertRaises(context_guard.DockerContextError):
            self._run_with_endpoint(
                "npipe:////./pipe/docker_engine",
                platform="win32",
            )

    def test_rejects_remote_named_pipe_with_docker_desktop_engine_name(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(context_guard.sys, "platform", "win32"),
            patch.object(
                context_guard,
                "_run",
                side_effect=[
                    "desktop-linux",
                    json.dumps({"Host": "npipe:////buildhost/pipe/dockerDesktopLinuxEngine"}),
                ],
            ) as run,
            self.assertRaises(context_guard.DockerContextError),
        ):
            context_guard.verify()
        self.assertEqual(run.call_count, 2)

    def test_rejects_docker_environment_overrides(self):
        with (
            patch.dict(os.environ, {"DOCKER_HOST": "tcp://remote"}, clear=True),
            patch.object(context_guard, "_run") as run,
            self.assertRaises(context_guard.DockerContextError),
        ):
            context_guard.verify()
        run.assert_not_called()

    def test_rejects_non_linux_engine_type(self):
        responses = [
            "default",
            json.dumps({"Host": "unix:///var/run/docker.sock"}),
            "27.0.0|windows",
        ]
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(context_guard.sys, "platform", "linux"),
            patch.object(context_guard, "_run", side_effect=responses),
            self.assertRaises(context_guard.DockerContextError),
        ):
            context_guard.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
