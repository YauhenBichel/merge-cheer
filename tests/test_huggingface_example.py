"""Exercise the documented router configuration without live credentials."""

import io
import json
import os
import unittest
import urllib.error
from contextlib import redirect_stderr
from unittest.mock import patch

from test_celebrate import ROOT, _load


class HuggingFaceExampleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.example = (ROOT / "examples/celebrate-huggingface.yml").read_text(
            encoding="utf-8"
        )
        self.inputs = dict(
            line.strip().split(": ", 1)
            for line in self.example.splitlines()
            if line.strip().startswith(("model: ", "model-base-url: ", "model-api-key: "))
        )

    def test_example_is_pinned_and_does_not_need_an_openai_secret(self) -> None:
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", self.example)
        self.assertEqual(self.inputs["model-api-key"], "${{ secrets.HF_TOKEN }}")
        self.assertEqual(self.inputs["model-base-url"], "https://router.huggingface.co/v1")
        self.assertNotIn("OPENAI_API_KEY", self.example)
        self.assertNotIn("actions/checkout", self.example)
        self.assertNotIn("run:", self.example)
        for path in (ROOT / "README.md", ROOT / "docs/index.html"):
            self.assertIn(
                "examples/celebrate-huggingface.yml", path.read_text(encoding="utf-8")
            )

    def test_router_uses_the_example_model_and_token(self) -> None:
        celebrate = _load()
        env = {
            "MODEL": self.inputs["model"],
            "MODEL_BASE_URL": self.inputs["model-base-url"],
            "MODEL_API_KEY": "fixture-token",
        }
        line = "README now explains routing — thanks {authors}."
        response = {"choices": [{"message": {"content": json.dumps({"message": line})}}]}
        with patch.dict(os.environ, env, clear=True), patch.object(
            celebrate, "_http_json", return_value=response
        ) as http, redirect_stderr(io.StringIO()):
            self.assertEqual(
                celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice"),
                line,
            )
        self.assertEqual(
            http.call_args.args,
            ("https://router.huggingface.co/v1/chat/completions", "fixture-token"),
        )
        self.assertEqual(http.call_args.kwargs["payload"]["model"], self.inputs["model"])

    def test_router_failure_or_unsafe_reply_returns_to_default_path(self) -> None:
        celebrate = _load()
        env = {
            "MODEL": self.inputs["model"],
            "MODEL_BASE_URL": self.inputs["model-base-url"],
            "MODEL_API_KEY": "fixture-token",
        }
        for result in (
            urllib.error.URLError("fixture failure"),
            {"choices": [{"message": {"content": '{"message": "nsfw"}'}}]},
        ):
            with (
                self.subTest(result=result),
                patch.dict(os.environ, env, clear=True),
                patch.object(celebrate, "_http_json") as http,
                redirect_stderr(io.StringIO()),
            ):
                if isinstance(result, Exception):
                    http.side_effect = result
                else:
                    http.return_value = result
                self.assertIsNone(
                    celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice")
                )
