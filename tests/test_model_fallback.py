"""A broken, slow, or strange model must never fail the job or leak the key."""

from __future__ import annotations

import http.client
import importlib.util
import io
import os
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "celebrate.py"
KEY = "sk-test-not-a-real-key-123"
GOOD = {
    "choices": [
        {"message": {"content": '{"message": "The readme glow-up landed, thanks @{author}."}'}}
    ]
}


def _load():
    spec = importlib.util.spec_from_file_location("celebrate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _model_env(**extra: str) -> dict[str, str]:
    env = {"MODEL": "gpt-4o-mini", "MODEL_API_KEY": KEY, "MODEL_BASE_URL": ""}
    env.update(extra)
    return env


class ModelFallbackTest(unittest.TestCase):
    def _ask(self, celebrate) -> tuple[object, str]:
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            line = celebrate.ask_model("merge", "docs: readme glow-up", "", "alice", "@alice")
        return line, err.getvalue()

    def test_any_request_error_falls_back_without_the_key(self) -> None:
        errors = [
            http.client.IncompleteRead(b'{"choices":', 489),
            http.client.BadStatusLine("NOT-HTTP garbage"),
            http.client.RemoteDisconnected("closed"),
            ValueError(f"Invalid header value b'Bearer {KEY}'"),
            UnicodeEncodeError("latin-1", KEY, 3, 4, "ordinal not in range(256)"),
            RuntimeError("anything else"),
        ]
        for exc in errors:
            with self.subTest(exc=type(exc).__name__):
                celebrate = _load()

                def boom(*_a, _exc=exc, **_k):
                    raise _exc

                celebrate._http_json = boom  # type: ignore[method-assign]
                with mock.patch.dict(os.environ, _model_env(), clear=False):
                    line, err = self._ask(celebrate)
                self.assertIsNone(line)
                self.assertIn("model skipped", err)
                self.assertNotIn(KEY, err)

    def test_odd_response_shapes_fall_back(self) -> None:
        for data in ({"choices": {"a": 1}}, {"choices": "x"}, [1, 2], None, {"choices": [None]}):
            with self.subTest(data=data):
                celebrate = _load()
                celebrate._http_json = lambda *_a, _d=data, **_k: _d  # type: ignore[method-assign]
                with mock.patch.dict(os.environ, _model_env(), clear=False):
                    line, _err = self._ask(celebrate)
                self.assertIsNone(line)

    def test_bad_base_url_or_key_skips_before_any_request(self) -> None:
        for env in (
            _model_env(MODEL_BASE_URL="api.openai.com/v1"),
            _model_env(MODEL_API_KEY="sk-a\nb"),
            _model_env(MODEL_API_KEY="sk-–dash"),
        ):
            with self.subTest(env=env):
                celebrate = _load()
                calls: list[str] = []
                real = celebrate._http_json

                def spy(url, *a, **k):
                    calls.append(url)
                    return real(url, *a, **k)

                celebrate._http_json = spy  # type: ignore[method-assign]
                with mock.patch.dict(os.environ, env, clear=False):
                    line, err = self._ask(celebrate)
                self.assertIsNone(line)
                self.assertEqual(calls, [])
                self.assertNotIn(env["MODEL_API_KEY"], err)

    def test_model_call_has_a_total_deadline(self) -> None:
        celebrate = _load()
        celebrate.MODEL_DEADLINE_SECONDS = 0.2

        def slow(*_a, **_k):
            time.sleep(2)
            return GOOD

        celebrate._http_json = slow  # type: ignore[method-assign]
        with mock.patch.dict(os.environ, _model_env(), clear=False):
            started = time.monotonic()
            line, err = self._ask(celebrate)
            elapsed = time.monotonic() - started
        self.assertIsNone(line)
        self.assertLess(elapsed, 1.5)
        self.assertIn("model skipped", err)

    def test_a_working_model_is_unchanged(self) -> None:
        celebrate = _load()
        celebrate._http_json = lambda *_a, **_k: GOOD  # type: ignore[method-assign]
        with mock.patch.dict(os.environ, _model_env(), clear=False):
            line, _err = self._ask(celebrate)
        self.assertEqual(line, "The readme glow-up landed, thanks @{author}.")

    def test_main_posts_the_default_thank_you_when_the_model_breaks(self) -> None:
        celebrate = _load()

        def boom(url, *_a, **_k):
            if "chat/completions" in url:
                raise http.client.IncompleteRead(b"", 10)
            return []

        celebrate._http_json = boom  # type: ignore[method-assign]
        env = _model_env(
            DRY_RUN="1",
            PR_AUTHOR="alice",
            PR_NUMBER="7",
            PR_MERGED="true",
            EVENT_NAME="pull_request_target",
            PR_TITLE="docs: readme glow-up",
            GITHUB_TOKEN="",
            GITHUB_REPOSITORY="",
            GITHUB_OUTPUT="",
            MESSAGE="",
        )
        out = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False), redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = celebrate.main()
        self.assertEqual(code, 0)
        self.assertIn("thank you @alice.", out.getvalue())


if __name__ == "__main__":
    unittest.main()
