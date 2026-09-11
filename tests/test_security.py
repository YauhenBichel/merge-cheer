"""Text an attacker controls must not turn the bot into a spammer or a phisher.

A pull request's author writes its title, body and commit messages. A security
review (11 September 2026) proved two ways to abuse that: unlimited @mentions
through Co-authored-by lines, and a model reply with a link posted unchecked.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "celebrate.py"


def _load():
    spec = importlib.util.spec_from_file_location("celebrate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


celebrate = _load()


class CoauthorTest(unittest.TestCase):
    def test_a_bare_login_is_not_a_coauthor(self) -> None:
        # Git's trailer is "Name <email>". A bare login mentioned anyone at all.
        self.assertEqual(celebrate.parse_coauthors("Co-authored-by: torvalds\nCo-authored-by: @gaearon"), [])

    def test_coauthors_are_capped(self) -> None:
        lines = "\n".join(
            f"Co-authored-by: P{i} <{i}+person{i}@users.noreply.github.com>" for i in range(50)
        )
        self.assertEqual(len(celebrate.parse_coauthors(lines)), celebrate.MAX_COAUTHORS)

    def test_only_a_merge_credits_coauthors(self) -> None:
        body = "Co-authored-by: Bob <1+bob@users.noreply.github.com>"
        self.assertEqual(celebrate.people_to_credit("merge", "alice", body, "", ["rev"]), ["alice", "bob", "rev"])
        # A closed or changes-requested pull request is its author's alone: it
        # must not let them make the bot mention anyone else.
        for moment in ("closed", "changes"):
            self.assertEqual(celebrate.people_to_credit(moment, "alice", body, body, []), ["alice"])


class ModelLineTest(unittest.TestCase):
    TITLE = "Fix the parser for nested lists"

    def test_a_plain_specific_line_is_used(self) -> None:
        self.assertTrue(celebrate.model_line_ok(self.TITLE, "Nested lists parse cleanly now, thank you @{author}!"))

    def test_links_markup_and_extra_mentions_are_refused(self) -> None:
        for line in (
            "Parser fixed! Verify your badge: [github.com/settings](https://evil.example/login)",
            "Parser fixed, details at https://evil.example",
            "Parser fixed, see www.evil.example",
            "Parser fixed <img src=x onerror=alert(1)>",
            "Parser fixed ![badge](https://evil.example/a.png)",
            "Parser fixed, thanks @torvalds and @{author}",
            "Parser fixed\nsecond line",
        ):
            self.assertFalse(celebrate.model_line_ok(self.TITLE, line), line)


if __name__ == "__main__":
    unittest.main()
