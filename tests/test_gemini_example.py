"""Check the Gemini example without live API calls or credentials."""

import io
import json
import os
import unittest
import urllib.error
from contextlib import redirect_stderr
from unittest.mock import patch

from test_celebrate import ROOT, _load


class GeminiExampleTest(unittest.TestCase):
    def setUp(self):
        self.example = (ROOT / "examples/celebrate-gemini.yml").read_text("utf-8")
        self.inputs = dict(
            line.strip().split(": ", 1)
            for line in self.example.splitlines()
            if line.strip().startswith(
                ("model: ", "model-base-url: ", "model-api-key: ")
            )
        )

    def test_example_configuration_and_documentation(self):
        self.assertEqual(
            self.inputs,
            {
                "model": "gemini-2.5-flash-lite",
                "model-base-url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "model-api-key": "${{ secrets.GEMINI_API_KEY }}",
            },
        )
        for required in (
            "@v1.7.0",
            "pull_request_target:",
            "types: [closed]",
            "github.event.pull_request.merged",
            "pull-requests: write",
        ):
            self.assertIn(required, self.example)
        for forbidden in ("OPENAI_API_KEY", "actions/checkout", "run:"):
            self.assertNotIn(forbidden, self.example)
        for name in ("README.md", "docs/index.html"):
            self.assertIn(
                "examples/celebrate-gemini.yml", (ROOT / name).read_text("utf-8")
            )

    def test_chat_request_and_fallbacks(self):
        celebrate = _load()
        line = "README now explains routing — thanks {authors}."
        good = {"choices": [{"message": {"content": json.dumps({"message": line})}}]}
        unsafe = {"choices": [{"message": {"content": '{"message": "nsfw"}'}}]}
        env = {
            "MODEL": self.inputs["model"],
            "MODEL_BASE_URL": self.inputs["model-base-url"],
            "MODEL_API_KEY": "fixture-gemini-token",
        }
        failures = [
            urllib.error.HTTPError("fixture", 429, "rate limit", {}, None),
            TimeoutError("fixture timeout"),
            unsafe,
            {},
        ]
        for response, expected in [(good, line)] + [(item, None) for item in failures]:
            with (
                self.subTest(response=response),
                patch.dict(os.environ, env, clear=True),
                patch.object(celebrate, "_http_json") as http,
                redirect_stderr(io.StringIO()),
            ):
                if isinstance(response, Exception):
                    http.side_effect = response
                else:
                    http.return_value = response
                self.assertEqual(
                    celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice"),
                    expected,
                )
                self.assertEqual(
                    http.call_args.args,
                    (
                        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                        "fixture-gemini-token",
                    ),
                )
                self.assertEqual(http.call_args.kwargs["method"], "POST")
                self.assertEqual(
                    http.call_args.kwargs["payload"]["model"], self.inputs["model"]
                )
