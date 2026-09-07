"""Merge Cheer must pick a GIF for every group and never shell the title."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / "action.yml"
SCRIPT = ROOT / "src" / "celebrate.py"
GIFS = ROOT / "gifs"
STILLS = ROOT / "stills"


def _load():
    spec = importlib.util.spec_from_file_location("celebrate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CelebrateTest(unittest.TestCase):
    def test_every_group_has_a_gif(self) -> None:
        celebrate = _load()
        for group in celebrate.GROUPS:
            names = list((GIFS / group).glob("*.gif"))
            self.assertTrue(names, f"{group} has no GIF")

    def test_a_group_can_hold_several_gifs(self) -> None:
        celebrate = _load()
        counts = [len(list((GIFS / group).glob("*.gif"))) for group in celebrate.GROUPS]
        self.assertGreaterEqual(max(counts), 2)

    def test_mood_groups_have_two_owned_gifs(self) -> None:
        for group in (
            "party",
            "space",
            "magic",
            "coffee",
            "robot",
            "comic",
            "sunny",
            "game",
            "sticker",
            "yeah",
            "devops",
            "sre",
            "qa",
            "design",
            "architecture",
            "engineering",
            "backend",
            "frontend",
            "java",
            "python",
            "cpp",
            "golang",
        ):
            names = list((GIFS / group).glob("*.gif"))
            self.assertGreaterEqual(len(names), 2, group)

    def test_comic_has_a_third_gif(self) -> None:
        names = {path.name for path in (GIFS / "comic").glob("*.gif")}
        self.assertEqual(names, {"burst.gif", "pop.gif", "alt.gif"})

    def test_no_gif_is_unused(self) -> None:
        celebrate = _load()
        allowed = set(celebrate.GROUPS)
        leftovers = [path.name for path in GIFS.glob("*.gif")]
        leftovers.extend(
            str(path.relative_to(GIFS))
            for path in GIFS.rglob("*.gif")
            if path.parent != GIFS and path.parent.name not in allowed
        )
        self.assertEqual(leftovers, [])

    def test_gifs_are_small_enough_for_a_comment(self) -> None:
        oversized = [
            f"{path.relative_to(GIFS)} {path.stat().st_size // 1024} KB"
            for path in GIFS.rglob("*.gif")
            if path.stat().st_size > 180 * 1024
        ]
        self.assertEqual(oversized, [])

    def test_rebuild_stills_exist(self) -> None:
        for name in (
            "celebration",
            "celebration-burst",
            "ship-it",
            "ship-boost",
            "nailed-it",
            "fix-spark",
            "nice-work",
            "docs-glow",
            "high-five",
            "cleanup",
            "cleanup-sweep",
            "party-confetti",
            "party-toast",
            "space-planet",
            "space-comet",
            "magic-wand",
            "magic-sparkles",
            "coffee-mug",
            "coffee-night",
            "robot-wave",
            "robot-dance",
            "comic-burst",
            "comic-pop",
            "sunny-sun",
            "sunny-rainbow",
            "game-levelup",
            "game-combo",
            "sticker-star",
            "sticker-thumb",
            "yeah-pump",
            "yeah-jump",
            "devops-loop",
            "devops-pipeline",
            "sre-lighthouse",
            "sre-pager",
            "qa-lens",
            "qa-pass",
            "design-palette",
            "design-frames",
            "architecture-blocks",
            "architecture-blueprint",
            "engineering-wrench",
            "engineering-build",
            "backend-db",
            "backend-server",
            "frontend-browser",
            "frontend-cursor",
            "java-mug",
            "python-snake",
            "python-coil",
            "cpp-plus",
            "cpp-gear",
            "golang-gopher",
            "golang-wave",
        ):
            self.assertTrue((STILLS / f"{name}.png").is_file(), name)

    def test_title_picks_the_group(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.pick_from_title("fix: leak"), "fix")
        self.assertEqual(celebrate.pick_from_title("feat: add login"), "ship")
        self.assertEqual(celebrate.pick_from_title("docs: readme"), "docs")
        self.assertEqual(celebrate.pick_from_title("test: cover ci"), "tests")
        self.assertEqual(celebrate.pick_from_title("build: webpack"), "tests")
        self.assertEqual(celebrate.pick_from_title("build lockfile"), "tests")
        self.assertEqual(celebrate.pick_from_title("refactor: clean path"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore: bump"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("welcome first contrib"), "welcome")
        self.assertEqual(celebrate.pick_from_title("party time"), "party")
        self.assertEqual(celebrate.pick_from_title("congrats team"), "party")
        self.assertEqual(celebrate.pick_from_title("woo hooray"), "party")
        self.assertEqual(celebrate.pick_from_title("chore: orbit cosmos"), "space")
        self.assertEqual(celebrate.pick_from_title("chore: magic wand"), "magic")
        self.assertEqual(celebrate.pick_from_title("chore: coffee"), "coffee")
        self.assertEqual(celebrate.pick_from_title("chore: robot helper"), "robot")
        self.assertEqual(celebrate.pick_from_title("chore: comic kapow"), "comic")
        self.assertEqual(celebrate.pick_from_title("chore: sunny day"), "sunny")
        self.assertEqual(celebrate.pick_from_title("chore: level-up combo"), "game")
        self.assertEqual(celebrate.pick_from_title("chore: sticker pack"), "sticker")
        self.assertEqual(celebrate.pick_from_title("chore: yeah let's go"), "yeah")
        self.assertEqual(celebrate.pick_from_title("chore: kubernetes helm"), "devops")
        self.assertEqual(celebrate.pick_from_title("chore: on-call slo"), "sre")
        self.assertEqual(celebrate.pick_from_title("chore: qa sdet"), "qa")
        self.assertEqual(celebrate.pick_from_title("chore: figma mockup"), "design")
        self.assertEqual(celebrate.pick_from_title("chore: architecture adr"), "architecture")
        self.assertEqual(celebrate.pick_from_title("chore: swe: helper"), "engineering")
        self.assertEqual(celebrate.pick_from_title("chore: backend graphql"), "backend")
        self.assertEqual(celebrate.pick_from_title("chore: javascript react"), "frontend")
        self.assertEqual(celebrate.pick_from_title("chore: python django"), "python")
        self.assertEqual(celebrate.pick_from_title("chore: cpp: move"), "cpp")
        self.assertEqual(celebrate.pick_from_title("chore: golang gopher"), "golang")
        self.assertEqual(celebrate.pick_from_title("chore: java: streams"), "java")
        self.assertEqual(celebrate.pick_from_title("perf: speed up query"), "ship")
        self.assertEqual(celebrate.pick_from_title("revert: bad merge"), "fix")
        self.assertEqual(celebrate.pick_from_title("deps: bump requests"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("docs: perfect the wording"), "docs")

    def test_mood_keywords_do_not_steal_conventional_types(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.pick_from_title("feat: add party mode"), "ship")
        self.assertEqual(celebrate.pick_from_title("fix: magic number"), "fix")
        self.assertEqual(celebrate.pick_from_title("docs: coffee guide"), "docs")
        self.assertEqual(celebrate.pick_from_title("namespace cleanup"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("feat: add comic mode"), "ship")
        self.assertEqual(celebrate.pick_from_title("fix: combo overflow"), "fix")
        self.assertEqual(celebrate.pick_from_title("docs: sticker pack"), "docs")
        self.assertEqual(celebrate.pick_from_title("test: sunny path"), "tests")
        self.assertEqual(celebrate.pick_from_title("refactor: yeah helper"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore: power"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore: game night"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("feat: add chore mode"), "ship")
        self.assertEqual(celebrate.pick_from_title("choreography notes"), "celebration")
        self.assertEqual(celebrate.pick_from_title("feat: add python client"), "ship")
        self.assertEqual(celebrate.pick_from_title("fix: java null"), "fix")
        self.assertEqual(celebrate.pick_from_title("test: frontend grid"), "tests")
        self.assertEqual(celebrate.pick_from_title("docs: devops runbook"), "docs")
        self.assertEqual(celebrate.pick_from_title("feat: add build mode"), "ship")
        self.assertEqual(celebrate.pick_from_title("rebuild the cache"), "celebration")
        self.assertEqual(celebrate.pick_from_title("chore: build image"), "cleanup")

    def test_first_timer_generic_title_is_welcome(self) -> None:
        celebrate = _load()
        self.assertEqual(
            celebrate.pick_from_title("chore: bump", "FIRST_TIME_CONTRIBUTOR"),
            "cleanup",
        )
        self.assertEqual(
            celebrate.pick_from_title("misc tweaks", "FIRST_TIME_CONTRIBUTOR"),
            "welcome",
        )
        self.assertEqual(celebrate.pick_from_title("fix: leak", "FIRST_TIMER"), "fix")

    def test_auto_topic_picks_a_shipped_group(self) -> None:
        celebrate = _load()
        for topic in ("auto", ""):
            group = celebrate.resolve_group("feat: add login", topic, seed="12")
            self.assertIn(group, celebrate.GROUPS)

    def test_auto_topic_ignores_title_keywords(self) -> None:
        celebrate = _load()
        from_feat = celebrate.resolve_group("feat: add login", "auto", seed="12")
        from_fix = celebrate.resolve_group("fix: leak", "auto", seed="12")
        from_chore = celebrate.resolve_group("chore: bump", "auto", seed="12")
        self.assertEqual(from_feat, from_fix)
        self.assertEqual(from_fix, from_chore)
        self.assertIn(from_feat, celebrate.GROUPS)

    def test_auto_topic_can_vary_by_pr_number(self) -> None:
        celebrate = _load()
        groups = {
            celebrate.resolve_group("chore: bump", "auto", seed=str(number))
            for number in range(1, 80)
        }
        self.assertGreater(len(groups), 1)
        self.assertTrue(groups <= set(celebrate.GROUPS))

    def test_title_topic_uses_the_title(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.resolve_group("feat: add login", "title"), "ship")
        self.assertEqual(celebrate.resolve_group("fix: leak", "title"), "fix")

    def test_explicit_topic_selects_that_group(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.resolve_group("fix: leak", "ship"), "ship")
        self.assertEqual(celebrate.resolve_group("fix: leak", "launch"), "ship")
        self.assertEqual(celebrate.resolve_group("chore: bump", "welcome"), "welcome")
        self.assertEqual(celebrate.resolve_group("chore: bump", "nailed-it"), "fix")
        self.assertEqual(celebrate.resolve_group("chore: bump", "party"), "party")
        self.assertEqual(celebrate.resolve_group("chore: bump", "congrats"), "party")
        self.assertEqual(celebrate.resolve_group("chore: bump", "space"), "space")
        self.assertEqual(celebrate.resolve_group("chore: bump", "magic"), "magic")
        self.assertEqual(celebrate.resolve_group("chore: bump", "coffee"), "coffee")
        self.assertEqual(celebrate.resolve_group("chore: bump", "bot"), "robot")
        self.assertEqual(celebrate.resolve_group("chore: bump", "comic"), "comic")
        self.assertEqual(celebrate.resolve_group("chore: bump", "kapow"), "comic")
        self.assertEqual(celebrate.resolve_group("chore: bump", "sunny"), "sunny")
        self.assertEqual(celebrate.resolve_group("chore: bump", "level-up"), "game")
        self.assertEqual(celebrate.resolve_group("chore: bump", "sticker"), "sticker")
        self.assertEqual(celebrate.resolve_group("chore: bump", "yeah"), "yeah")
        self.assertEqual(celebrate.resolve_group("chore: bump", "lets-go"), "yeah")
        self.assertEqual(celebrate.resolve_group("chore: bump", "devops"), "devops")
        self.assertEqual(celebrate.resolve_group("chore: bump", "k8s"), "devops")
        self.assertEqual(celebrate.resolve_group("chore: bump", "testing"), "qa")
        self.assertEqual(celebrate.resolve_group("chore: bump", "python"), "python")
        self.assertEqual(celebrate.resolve_group("chore: bump", "go"), "golang")
        self.assertEqual(celebrate.resolve_group("chore: bump", "c++"), "cpp")
        self.assertEqual(celebrate.resolve_group("chore: bump", "javascript"), "frontend")

    def test_unknown_topic_falls_back_to_celebration(self) -> None:
        celebrate = _load()
        buf = io.StringIO()
        with redirect_stderr(buf):
            group = celebrate.resolve_group("fix: leak", "party-mode")
        self.assertEqual(group, "celebration")
        self.assertIn("party-mode", buf.getvalue())
        self.assertIn("ship", buf.getvalue())
        self.assertIn("welcome", buf.getvalue())

    def test_gif_pick_is_stable_for_a_seed(self) -> None:
        celebrate = _load()
        names = ["a.gif", "b.gif", "c.gif"]
        first = celebrate.pick_gif_name(names, "12:ship")
        second = celebrate.pick_gif_name(names, "12:ship")
        self.assertEqual(first, second)
        self.assertIn(first, names)

    def test_bundled_url_strips_ref_prefixes(self) -> None:
        celebrate = _load()
        url = celebrate.bundled_url(
            "YauhenBichel/merge-cheer", "refs/tags/v1", "ship", "ship-it.gif"
        )
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/YauhenBichel/merge-cheer/v1/gifs/ship/ship-it.gif",
        )

    def test_bundled_url_falls_back_when_action_repo_is_empty(self) -> None:
        celebrate = _load()
        url = celebrate.bundled_url("", "v1.5.0", "ship", "ship-it.gif")
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/YauhenBichel/merge-cheer/v1.5.0/gifs/ship/ship-it.gif",
        )
        blank = celebrate.bundled_url("   ", "main", "comic", "burst.gif")
        self.assertEqual(
            blank,
            "https://raw.githubusercontent.com/YauhenBichel/merge-cheer/main/gifs/comic/burst.gif",
        )

    def test_comment_mentions_the_author(self) -> None:
        celebrate = _load()
        body = celebrate.comment_body(
            "Merged — thank you @{author}.",
            "alice",
            "ship it",
            "https://example.test/ship/ship-it.gif",
        )
        self.assertIn("@alice", body)
        self.assertIn("ship-it.gif", body)
        self.assertIn('width="280"', body)
        self.assertIn("<img ", body)
        self.assertIn("<!-- merge-cheer:merge -->", body)
        self.assertNotIn("<!-- merge-cheer -->\n", body)
        self.assertNotIn("First contribution — welcome.", body)

    def test_comment_appends_a_safe_note(self) -> None:
        celebrate = _load()
        body = celebrate.comment_body(
            "Merged — thank you @{author}.",
            "alice",
            "ship it",
            "https://example.test/ship/ship-it.gif",
            note="Come hang out on Discord — https://discord.gg/your-invite",
        )
        self.assertIn("Merged — thank you @alice.", body)
        self.assertIn("Come hang out on Discord — https://discord.gg/your-invite", body)
        self.assertLess(
            body.index("Merged — thank you @alice."),
            body.index("Come hang out on Discord"),
        )
        self.assertLess(
            body.index("Come hang out on Discord"),
            body.index("<img "),
        )
        unsafe = celebrate.comment_body(
            "Merged — thank you @{author}.",
            "alice",
            "ship it",
            "https://example.test/ship/ship-it.gif",
            note="nsfw party in Discord",
        )
        self.assertNotIn("nsfw", unsafe)
        self.assertEqual(celebrate.clean_note(""), "")
        self.assertEqual(
            celebrate.clean_note("Join us\n\non Discord."),
            "Join us on Discord.",
        )

    def test_custom_gifs_are_https_images(self) -> None:
        celebrate = _load()
        urls = celebrate.parse_custom_gifs(
            "https://example.test/a.gif, http://insecure.test/b.gif\n"
            "https://example.test/c.webp javascript:alert(1)\n"
            "https://example.test/nsfw.gif"
        )
        self.assertEqual(urls, ["https://example.test/a.gif", "https://example.test/c.webp"])
        self.assertEqual(
            celebrate.pick_custom_gif(
                ["https://example.test/a.gif", "https://example.test/c.webp"],
                "12",
            ),
            celebrate.pick_custom_gif(
                ["https://example.test/a.gif", "https://example.test/c.webp"],
                "12",
            ),
        )
        self.assertTrue(celebrate.gifs_path_ok(".github/merge-cheer"))
        self.assertFalse(celebrate.gifs_path_ok("../secrets"))
        self.assertEqual(celebrate.list_repo_gif_urls("", "org/repo", ".github/merge-cheer"), [])
        celebrate._http_json = lambda *_a, **_k: [  # type: ignore[method-assign]
            {
                "type": "file",
                "name": "ship.gif",
                "download_url": "https://raw.githubusercontent.com/org/repo/main/.github/merge-cheer/ship.gif",
            },
            {"type": "file", "name": "readme.md", "download_url": "https://example.test/readme.md"},
            {"type": "dir", "name": "nested"},
        ]
        self.assertEqual(
            celebrate.list_repo_gif_urls("token", "org/repo", ".github/merge-cheer", "main"),
            [
                "https://raw.githubusercontent.com/org/repo/main/.github/merge-cheer/ship.gif"
            ],
        )

    def test_comment_tags_the_author_for_a_notification(self) -> None:
        celebrate = _load()
        from_placeholder = celebrate.comment_body(
            "Login help still needs a pass — thanks {author}.",
            "alice",
            "ship it",
            "https://example.test/ship/ship-it.gif",
        )
        self.assertIn("thanks @alice.", from_placeholder)
        self.assertNotIn("thanks alice.", from_placeholder)
        from_name = celebrate.comment_body(
            "Cheers to YauhenBichel for keeping model cheers.",
            "YauhenBichel",
            "celebration",
            "https://example.test/celebration.gif",
        )
        self.assertIn("@YauhenBichel", from_name)
        self.assertNotIn("to YauhenBichel ", from_name)
        missing = celebrate.comment_body(
            "Shipped the login help.",
            "alice",
            "ship it",
            "https://example.test/ship/ship-it.gif",
        )
        self.assertIn("@alice", missing)

    def test_comment_welcomes_a_first_timer(self) -> None:
        celebrate = _load()
        body = celebrate.comment_body(
            "Merged — thank you @{author}.",
            "alice",
            "welcome",
            "https://example.test/welcome/high-five.gif",
            association="FIRST_TIME_CONTRIBUTOR",
        )
        self.assertIn("@alice", body)
        self.assertIn("First contribution — welcome.", body)
        again = celebrate.comment_body(
            "First contribution — welcome.\nMerged — thank you @{author}.",
            "alice",
            "welcome",
            "https://example.test/welcome/high-five.gif",
            association="FIRST_TIMER",
        )
        self.assertEqual(again.count("First contribution — welcome."), 1)
        ja = celebrate.comment_body(
            "マージしました — ありがとう @{author}。",
            "alice",
            "welcome",
            "https://example.test/welcome/high-five.gif",
            association="FIRST_TIME_CONTRIBUTOR",
            locale="ja",
        )
        self.assertIn("初めてのコントリビューション — ようこそ。", ja)
        self.assertNotIn("First contribution — welcome.", ja)
        self.assertEqual(
            celebrate.first_timer_line("zz"),
            "First contribution — welcome.",
        )
        for code in celebrate.LOCALES:
            self.assertIn(code, celebrate.FIRST_TIMER_LINES)

    def test_action_never_checkouts_the_pull_request(self) -> None:
        text = ACTION.read_text(encoding="utf-8")
        script = (ROOT / "src" / "celebrate.py").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertNotIn("actions/checkout", text)
        self.assertIn("PR_TITLE: ${{ github.event.pull_request.title }}", text)
        self.assertIn("PR_BODY: ${{ github.event.pull_request.body }}", text)
        self.assertIn("PR_LABELS:", text)
        self.assertIn("TOPIC: ${{ inputs.topic }}", text)
        self.assertIn("LOCALE: ${{ inputs.locale }}", text)
        self.assertIn("CUSTOM_GIFS: ${{ inputs.gifs }}", text)
        self.assertIn("GIFS_PATH: ${{ inputs.gifs-path }}", text)
        self.assertIn("NOTE: ${{ inputs.note }}", text)
        self.assertNotIn(
            "${{ github.event.pull_request.title }}\n      run:",
            text,
        )
        self.assertNotIn("subprocess", script)
        self.assertNotIn("checkout", script)
        self.assertNotIn("git clone", script)
        self.assertIn("security/advisories/new", security)
        self.assertIn("private", security.lower())
        self.assertNotIn(
            "Open a **public** GitHub issue on this repo.",
            security,
        )

    def test_action_documents_every_group(self) -> None:
        celebrate = _load()
        text = ACTION.read_text(encoding="utf-8")
        self.assertIn("topic:", text)
        self.assertIn("random theme", text)
        self.assertIn("title picks from the PR title", text)
        for group in celebrate.GROUPS:
            self.assertIn(group, text)

    def test_contributing_lists_every_group(self) -> None:
        celebrate = _load()
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertNotIn("issues/1", text)
        self.assertNotIn("issues/4", text)
        self.assertIn("open an issue", text)
        self.assertIn("private vulnerability reporting", text)
        for group in celebrate.GROUPS:
            self.assertIn(f"`{group}`", text)

    def test_action_uses_the_stdlib_script(self) -> None:
        text = ACTION.read_text(encoding="utf-8")
        self.assertIn("src/celebrate.py", text)
        self.assertNotIn("github-script", text)

    def test_readme_is_the_live_demo(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Live demo", text)
        self.assertIn("gifs/ship/ship-it.gif", text)
        self.assertIn("gifs/party/confetti.gif", text)
        self.assertIn("gifs/space/planet.gif", text)
        self.assertIn("gifs/magic/wand.gif", text)
        self.assertIn("gifs/coffee/mug.gif", text)
        self.assertIn("gifs/robot/wave.gif", text)
        self.assertIn("gifs/comic/burst.gif", text)
        self.assertIn("gifs/sunny/sun.gif", text)
        self.assertIn("gifs/game/levelup.gif", text)
        self.assertIn("gifs/sticker/star.gif", text)
        self.assertIn("gifs/yeah/pump.gif", text)
        self.assertIn("gifs/devops/loop.gif", text)
        self.assertIn("gifs/python/snake.gif", text)
        self.assertIn("gifs/golang/gopher.gif", text)
        self.assertIn("![Merge Cheer demo](docs/merge-cheer-demo.mp4)", text)
        self.assertIn("**What.**", text)
        self.assertIn("**Why.**", text)
        self.assertIn("**Where.**", text)
        self.assertIn("**How.**", text)
        self.assertIn("`locale`", text)
        self.assertIn("reviewers", text)
        self.assertIn("closed or change-requested MR", text)
        self.assertIn("declined or change-requested PR", text)
        self.assertIn("Catalog row is not live", text)
        self.assertIn("Docker Hub pipe is not public", text)
        self.assertNotIn("No merge comment exists yet", text)
        self.assertIn("MoleCare and this account", text)
        self.assertIn(".github/workflows/celebrate.yml", text)
        dogfood = (ROOT / ".github" / "workflows" / "celebrate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("uses: ./", dogfood)
        self.assertIn("First-time authors get a welcome line.", dogfood)
        self.assertIn("model: gpt-4o-mini", dogfood)
        self.assertIn("secrets.OPENAI_API_KEY", dogfood)
        self.assertIn("github.event.repository.default_branch", dogfood)
        self.assertNotIn("pull_request.head", dogfood)

    def test_pages_site_is_public_and_searchable(self) -> None:
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        pages = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("<title>Merge Cheer", html)
        self.assertIn("GIF on merge", html)
        self.assertIn("What happens on merge", html)
        self.assertIn("Merged — thank you @alice", html)
        self.assertIn("random theme", html)
        self.assertIn("random theme", readme)
        self.assertIn("topic: title", readme)
        self.assertIn("First contribution — welcome.", html)
        self.assertIn("First contribution — welcome.", readme)
        self.assertIn("topic: auto", html)
        self.assertIn("topic: comic", html)
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", html)
        self.assertIn("releases/tag/v1.7.0", html)
        self.assertIn("no-cheer", html)
        self.assertIn("reviewers", html)
        self.assertIn("closed without merge, or changes requested when the job can see that request", html)
        self.assertIn("closed or change-requested MR", html)
        self.assertIn("declined or change-requested PR", html)
        self.assertIn("Catalog row is not live", html)
        self.assertIn("Docker Hub pipe is not public", html)
        self.assertIn("MoleCare and this account", html)
        self.assertIn("build:</code> maps to tests", html)
        self.assertNotIn("pinned to <code>@v1.6.0</code>.", html)
        self.assertIn("locale", html)
        self.assertIn("model-api-key", html)
        self.assertIn("merge-cheer-demo.mp4", html)
        self.assertIn("merge-cheer-demo-poster.png", html)
        self.assertIn("id=\"demo\"", html)
        self.assertIn("<strong>What.</strong>", html)
        self.assertIn("<strong>Why.</strong>", html)
        self.assertIn("<strong>Where.</strong>", html)
        self.assertIn("<strong>How.</strong>", html)
        self.assertIn("<video", html)
        self.assertIn("gifs/comic/pop.gif", html)
        self.assertIn("gifs/sunny/sun.gif", html)
        self.assertIn("gifs/game/levelup.gif", html)
        self.assertIn("gifs/sticker/star.gif", html)
        self.assertIn("gifs/devops/loop.gif", html)
        self.assertIn("gifs/python/snake.gif", html)
        self.assertIn("gifs/frontend/browser.gif", html)
        self.assertIn("gifs/golang/gopher.gif", html)
        self.assertIn("min(560px, 100%)", html)
        self.assertIn("minmax(21rem, 1fr)", html)
        self.assertIn("topic: python", html)
        self.assertIn("cp docs/merge-cheer-demo.mp4 _site/merge-cheer-demo.mp4", pages)
        self.assertTrue((ROOT / "docs" / "merge-cheer-demo.mp4").is_file())
        self.assertTrue((ROOT / "docs" / "merge-cheer-demo-poster.png").is_file())
        self.assertIn("MoleCare/molecare-mcp", html)
        self.assertIn("YauhenBichel/py-harness", html)
        self.assertIn("YauhenBichel/readme-contributors", html)
        self.assertNotIn("/Users/", html)
        self.assertNotIn("DevBox/", html)
        self.assertIn("marketplace/actions/merge-cheer", html)
        self.assertIn("marketplace/actions/merge-cheer", readme)
        self.assertNotIn("<script", html)
        self.assertIn("https://yauhenbichel.github.io/merge-cheer/", readme)
        self.assertIn("GitLab", html)
        self.assertIn("Bitbucket", html)
        self.assertIn("MARKETPLACES.md", html)
        self.assertIn("examples/gitlab-ci.yml", readme)
        self.assertIn("examples/bitbucket-pipelines.yml", readme)
        self.assertIn("### GitHub", readme)
        self.assertIn("### GitLab", readme)
        self.assertIn("### Bitbucket", readme)
        self.assertIn("GITLAB_TOKEN", html)
        self.assertIn("BITBUCKET_ACCESS_TOKEN", html)
        self.assertIn("id=\"gitlab\"", html)
        self.assertIn("id=\"bitbucket\"", html)
        self.assertIn("id=\"model\"", html)
        self.assertIn("id=\"ai\"", html)
        self.assertIn("id=\"cases\"", html)
        self.assertIn("does not post another GIF", html)
        self.assertIn("does not block the merge cheer", html)
        self.assertIn("does not block the merge cheer", readme)
        self.assertNotIn("A second pipeline can post again", html)
        self.assertIn("8 public repositories", html)
        self.assertIn("8 public repositories", readme)
        self.assertIn("is a random theme", html)
        self.assertIn("is a random theme", readme)
        self.assertIn("Zero-config is still", html)
        self.assertIn("Zero-config is still", readme)
        self.assertIn("merge-cheer-ai-demo.mp4", html)
        self.assertIn("merge-cheer-ai-demo.mp4", pages)
        self.assertIn("merge-cheer-ai-real.png", html)
        self.assertIn("merge-cheer-ai-real.png", pages)
        self.assertIn("The model writes one short line", html)
        self.assertIn("The model writes one short line", readme)
        self.assertTrue((ROOT / "docs" / "merge-cheer-ai-demo.mp4").is_file())
        self.assertTrue((ROOT / "docs" / "merge-cheer-ai-demo-poster.png").is_file())
        self.assertTrue((ROOT / "docs" / "merge-cheer-ai-demo.gif").is_file())
        self.assertTrue((ROOT / "docs" / "merge-cheer-ai-real.png").is_file())
        self.assertIn("id=\"credits\"", html)
        self.assertIn("Keep credits low", html)
        self.assertIn("Keep credits low", readme)
        self.assertIn("examples/celebrate-openai.yml", html)
        self.assertIn("examples/celebrate-openai.yml", readme)
        self.assertIn("examples/celebrate-custom.yml", html)
        self.assertIn("examples/celebrate-custom.yml", readme)
        self.assertIn("gifs-path", html)
        self.assertIn("gifs-path", readme)
        self.assertIn("Come hang out on Discord", html)
        self.assertIn("Come hang out on Discord", readme)
        self.assertIn("examples/celebrate-more-openai.yml", html)
        self.assertIn("examples/celebrate-more-openai.yml", readme)
        self.assertIn("OPENAI_API_KEY", html)
        self.assertNotIn("e183fbc7b8e395506e627ff60600577dfb5f8f45", html)
        self.assertNotIn("e183fbc7b8e395506e627ff60600577dfb5f8f45", readme)
        self.assertIn("model: message=", html)
        self.assertIn("actions/deploy-pages", pages)
        self.assertIn("cp -R gifs _site/gifs", pages)
        medium = (ROOT / "docs" / "medium-merge-cheer.md").read_text(encoding="utf-8")
        self.assertIn("https://yauhenbichel.github.io/merge-cheer/", medium)
        self.assertIn(
            "https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo.mp4",
            medium,
        )
        self.assertIn(
            "https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo-poster.png",
            medium,
        )
        self.assertIn(
            "https://yauhenbichel.github.io/merge-cheer/gifs/comic/pop.gif",
            medium,
        )
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", medium)
        self.assertIn("random theme", medium)
        self.assertIn("marketplace/actions/merge-cheer", medium)
        self.assertNotIn("/Users/", medium)
        self.assertNotIn("DevBox/", medium)

    def test_release_workflow_is_reviewed_not_automatic(self) -> None:
        text = (ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("environment: marketplace", text)
        self.assertIn("needs: test", text)
        self.assertIn("contents: write", text)
        self.assertIn("python3 -m unittest discover -s tests -q", text)
        self.assertIn("gh release create", text)
        self.assertIn("ref: ${{ inputs.version }}", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("pull_request.head", text)
        self.assertNotIn("git tag -f", text)
        self.assertNotIn("--force", text)
        on_block = text.split("permissions:", 1)[0]
        self.assertNotIn("\n  push:", on_block)
        self.assertNotIn("tags:", on_block)
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("uses:"):
                continue
            pin = stripped.split("@", 1)[-1].split()[0]
            self.assertRegex(pin, r"^[0-9a-f]{40}$", stripped)
        notes = (ROOT / "RELEASE.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("environment: marketplace", notes)
        self.assertIn("Required reviewers", notes)
        self.assertIn("releases/edit/", notes)
        self.assertIn("RELEASE.md", readme)
        self.assertNotIn("/Users/", notes)
        self.assertNotIn("DevBox/", notes)
        self.assertIn("marketplace/actions/merge-cheer", notes)
        self.assertIn("marketplace=true", notes)
        self.assertIn("docs/marketplace.png", notes)
        self.assertIn("Settings → Actions", notes)
        self.assertIn("Publish this Action to the GitHub Marketplace", notes)
        shot = ROOT / "docs" / "marketplace.png"
        self.assertTrue(shot.is_file())
        self.assertLess(shot.stat().st_size, 500 * 1024)

    def test_contributors_push_does_not_add_missing_readme_names(self) -> None:
        """Ubuntu git is case-sensitive; `git add` of a missing path exits 128."""
        text = (ROOT / ".github" / "workflows" / "contributors.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("format: html", text)
        self.assertIn("caption: auto", text)
        self.assertIn("secrets.OPENAI_API_KEY", text)
        forbidden = {"README", "readme.md", ".github/contributors.svg"}
        added: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("git add "):
                continue
            added.extend(stripped.split()[2:])
        self.assertIn("README.md", added)
        self.assertIn("[ -d .github/faces ] && git add .github/faces", text)
        self.assertIn(
            "[ -e .github/contributors.svg ] && git add .github/contributors.svg",
            text,
        )
        self.assertEqual([name for name in added if name in forbidden], [])
        self.assertIn("pull-requests: write", text)
        self.assertIn("docs/contributors", text)
        self.assertIn("gh pr create", text)
        self.assertIn("gh pr merge", text)
        self.assertIn('gh pr merge "$NUMBER" --squash --auto || gh pr merge "$NUMBER" --squash', text)
        self.assertNotIn("--jq .number", text)
        self.assertNotIn(
            "GitHub Actions is not permitted to create or approve pull requests",
            text,
        )

    def test_bundled_gif_names_match_the_repo(self) -> None:
        celebrate = _load()
        for group, names in celebrate.BUNDLED_GIFS.items():
            on_disk = {path.name for path in (GIFS / group).glob("*.gif")}
            self.assertEqual(set(names), on_disk, group)
        self.assertEqual(set(celebrate.BUNDLED_GIFS), set(celebrate.GROUPS))

    def test_gif_names_work_without_a_local_tree(self) -> None:
        celebrate = _load()
        names = celebrate.group_gif_names(ROOT / "does-not-exist", "python")
        self.assertIn("snake.gif", names)

    def test_detect_host(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "BITBUCKET_REPO_FULL_NAME",
            )
        }
        try:
            os.environ["GITHUB_ACTIONS"] = "true"
            self.assertEqual(celebrate.detect_host(), "github")
            del os.environ["GITHUB_ACTIONS"]
            os.environ["GITLAB_CI"] = "true"
            self.assertEqual(celebrate.detect_host(), "gitlab")
            del os.environ["GITLAB_CI"]
            os.environ["BITBUCKET_COMMIT"] = "abc"
            self.assertEqual(celebrate.detect_host(), "bitbucket")
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertTrue(celebrate.is_bot_author("dependabot[bot]"))
        self.assertFalse(celebrate.is_bot_author("alice"))

    def test_gitlab_and_bitbucket_adapters_are_shipped(self) -> None:
        component = (ROOT / "templates" / "merge-cheer.yml").read_text(encoding="utf-8")
        gitlab_ci = (ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")
        pipe = (ROOT / "pipe.yml").read_text(encoding="utf-8")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        markets = (ROOT / "MARKETPLACES.md").read_text(encoding="utf-8")
        example_gl = (ROOT / "examples" / "gitlab-ci.yml").read_text(encoding="utf-8")
        example_bb = (ROOT / "examples" / "bitbucket-pipelines.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("spec:", component)
        self.assertIn("inputs:", component)
        self.assertIn("celebrate.py", component)
        self.assertIn("release:", gitlab_ci)
        self.assertIn("python3 -m unittest discover -s tests -q", gitlab_ci)
        self.assertIn("eugenebichel/merge-cheer:1.7.0", pipe)
        self.assertIn("ACTION_REF: v1.7.0", example_gl)
        self.assertIn("ACTION_REF=v1.7.0", example_bb)
        more = (ROOT / "examples" / "celebrate-more.yml").read_text(encoding="utf-8")
        merge = (ROOT / "examples" / "celebrate-merge.yml").read_text(encoding="utf-8")
        custom = (ROOT / "examples" / "celebrate-custom.yml").read_text(encoding="utf-8")
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", more)
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", merge)
        self.assertIn("gifs-path: .github/merge-cheer", custom)
        self.assertIn("note:", custom)
        self.assertIn("discord.gg", custom)
        self.assertNotIn("@v1.5.0", more)
        self.assertNotIn("@v1\n", merge)
        self.assertIn("BITBUCKET_ACCESS_TOKEN", pipe)
        self.assertIn("src/celebrate.py", dockerfile)
        self.assertIn("CI/CD Catalog", markets)
        self.assertIn("official-pipes", markets)
        self.assertNotIn("/Users/", markets)
        self.assertNotIn("DevBox/", markets)
        self.assertIn("celebrate.py", example_gl)
        self.assertIn("BITBUCKET_ACCESS_TOKEN", example_bb)
        self.assertIn("GITLAB_TOKEN", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_should_skip_detects_skip_markers(self) -> None:
        celebrate = _load()
        self.assertTrue(celebrate.should_skip("no-cheer: bump lockfile"))
        self.assertTrue(celebrate.should_skip("[skip cheer] fix login"))
        self.assertTrue(celebrate.should_skip("[SKIP CHEER] fix login"))
        self.assertTrue(celebrate.should_skip("chore: bump deps (no-cheer)"))
        self.assertFalse(celebrate.should_skip("fix: login"))
        self.assertFalse(celebrate.should_skip("feat: add login"))
        self.assertFalse(celebrate.should_skip(""))
        self.assertTrue(celebrate.should_skip("fix: login", "no-cheer"))
        self.assertTrue(celebrate.should_skip("fix: login", "docs, skip-cheer"))
        self.assertFalse(celebrate.should_skip("fix: login", "docs, ready"))

    def test_title_maps_typo_style_lint_without_stealing_feat(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.pick_from_title("typo: comment"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("style: imports"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("lint: unused"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("format: black"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore: bump lockfile"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore bump lockfile"), "cleanup")
        self.assertEqual(celebrate.pick_from_title("chore: coffee"), "coffee")
        self.assertEqual(celebrate.pick_from_title("feat: typo in copy"), "ship")
        self.assertEqual(
            celebrate.pick_from_title("chore: bump", "", "Please lint the extras."),
            "cleanup",
        )
        self.assertEqual(
            celebrate.resolve_group(
                "chore: bump", "title", body="Please format the extras."
            ),
            "cleanup",
        )
        self.assertEqual(celebrate.resolve_group("chore: bump lockfile", "title"), "cleanup")
        self.assertEqual(celebrate.resolve_group("choreography notes", "title"), "celebration")

    def test_coauthors_and_authors_placeholder(self) -> None:
        celebrate = _load()
        self.assertEqual(
            celebrate.parse_coauthors(
                "Thanks\n\nCo-authored-by: Bob <123+bob@users.noreply.github.com>\n"
                "Co-authored-by: dependabot[bot] <bot@users.noreply.github.com>\n"
            ),
            ["bob"],
        )
        self.assertEqual(
            celebrate.format_authors(["alice", "bob", "cara"]),
            "@alice, @bob, and @cara",
        )
        self.assertEqual(
            celebrate.collect_authors(
                "alice",
                "Co-authored-by: Bob <bob@users.noreply.github.com>",
            ),
            ["alice", "bob"],
        )
        body = celebrate.comment_body(
            "Merged — thank you @{author}.",
            "alice",
            "ship it",
            "https://example.test/ship.gif",
            "@alice and @bob",
        )
        self.assertIn("@alice and @bob", body)
        self.assertIn("<!-- merge-cheer:merge -->", body)

    def test_reviewers_join_the_author_list(self) -> None:
        celebrate = _load()
        self.assertEqual(
            celebrate.collect_authors(
                "alice",
                extras=["bob", "alice", "dependabot[bot]"],
            ),
            ["alice", "bob"],
        )
        celebrate._http_json = lambda *_a, **_k: [  # type: ignore[method-assign]
            {"user": {"login": "cara", "type": "User"}},
            {"user": {"login": "github-actions[bot]", "type": "Bot"}},
            {"user": {"login": "cara", "type": "User"}},
            {"user": {"login": "dan", "type": "User"}},
        ]
        self.assertEqual(
            celebrate.list_pr_reviewers("token", "org/repo", "12"),
            ["cara", "dan"],
        )
        self.assertEqual(celebrate.list_pr_reviewers("", "org/repo", "12"), [])

    def test_already_cheered_finds_the_marker(self) -> None:
        celebrate = _load()
        legacy = [{"body": "<!-- merge-cheer -->\nMerged — thank you @alice.\n"}]
        changes = [{"body": "<!-- merge-cheer:changes -->\nA bit more work — you have this @alice.\n"}]
        closed = [{"body": "<!-- merge-cheer:closed -->\nClosed — thank you for the work @alice.\n"}]
        merge = [{"body": "<!-- merge-cheer:merge -->\nMerged — thank you @alice.\n"}]
        self.assertTrue(celebrate.already_cheered(legacy))
        self.assertTrue(celebrate.already_cheered(legacy, "merge"))
        self.assertFalse(celebrate.already_cheered(legacy, "changes"))
        self.assertFalse(celebrate.already_cheered(legacy, "closed"))
        self.assertTrue(celebrate.already_cheered(merge, "merge"))
        self.assertFalse(celebrate.already_cheered(merge, "changes"))
        self.assertTrue(celebrate.already_cheered(changes, "changes"))
        self.assertFalse(celebrate.already_cheered(changes, "merge"))
        self.assertTrue(celebrate.already_cheered(closed, "closed"))
        self.assertFalse(celebrate.already_cheered(closed, "merge"))
        self.assertFalse(celebrate.already_cheered([{"body": "nice work"}]))
        self.assertFalse(celebrate.already_cheered([]))
        self.assertEqual(
            celebrate.cheer_marker("changes"),
            "<!-- merge-cheer:changes -->",
        )
        self.assertIn(
            "<!-- merge-cheer:changes -->",
            celebrate.comment_body(
                "A bit more work — you have this @{author}.",
                "alice",
                "yeah",
                "https://example.test/yeah/pump.gif",
                moment="changes",
            ),
        )

    def test_model_accepts_allowed_group_and_rejects_junk(self) -> None:
        celebrate = _load()
        self.assertEqual(
            celebrate._parse_model_payload(
                '{"group": "ship", "message": "Thanks {author}."}'
            ),
            "Thanks {author}.",
        )
        self.assertEqual(
            celebrate._parse_model_payload(
                '{"message": "README now names the people — thanks {authors}."}'
            ),
            "README now names the people — thanks {authors}.",
        )
        self.assertTrue(celebrate.is_grated("Thanks {author}."))
        self.assertFalse(celebrate.is_grated("nsfw party"))
        saved = {
            key: os.environ.pop(key, None)
            for key in ("MODEL", "MODEL_API_KEY", "MODEL_BASE_URL", "GITHUB_TOKEN")
        }
        try:
            os.environ["MODEL_API_KEY"] = "sk-test"
            os.environ["MODEL"] = "gpt-4o-mini"
            seen: list[dict] = []

            def fake_ok(_url, _token, method="GET", payload=None, headers=None):
                seen.append(payload or {})
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"message": '
                                    '"README now names the people — thanks {authors}."}'
                                )
                            }
                        }
                    ]
                }

            celebrate._http_json = fake_ok  # type: ignore[method-assign]
            self.assertEqual(
                celebrate.ask_model(
                    "merge",
                    "docs: readme",
                    "x" * 400,
                    "alice",
                    "@alice",
                ),
                "README now names the people — thanks {authors}.",
            )
            self.assertEqual(seen[0]["max_tokens"], 60)
            self.assertNotIn("Allowed groups", seen[0]["messages"][0]["content"])
            user = json.loads(seen[0]["messages"][1]["content"])
            self.assertEqual(len(user["body"]), 200)

            def fake_generic(_url, _token, method="GET", payload=None, headers=None):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": '{"group": "docs", "message": "Thanks {authors}."}'
                            }
                        }
                    ]
                }

            celebrate._http_json = fake_generic  # type: ignore[method-assign]
            self.assertIsNone(
                celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice")
            )
            self.assertFalse(
                celebrate.cheer_is_specific("docs: readme", "Thanks {author}.")
            )
            self.assertTrue(
                celebrate.cheer_is_specific(
                    "docs: readme", "README now names the people — thanks {authors}."
                )
            )

            def fake_bad(_url, _token, method="GET", payload=None, headers=None):
                return {
                    "choices": [
                        {"message": {"content": '{"group": "docs", "message": "nsfw"}'}}
                    ]
                }

            celebrate._http_json = fake_bad  # type: ignore[method-assign]
            self.assertIsNone(
                celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice")
            )

            def fake_unknown(_url, _token, method="GET", payload=None, headers=None):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": '{"group": "nope", "message": "Thanks."}'
                            }
                        }
                    ]
                }

            celebrate._http_json = fake_unknown  # type: ignore[method-assign]
            self.assertIsNone(
                celebrate.ask_model("merge", "docs: readme", "", "alice", "@alice")
            )
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_explicit_topic_is_not_overridden_by_defaults(self) -> None:
        celebrate = _load()
        self.assertTrue(celebrate.topic_is_default("merge", "auto"))
        self.assertTrue(celebrate.topic_is_default("closed", "coffee"))
        self.assertFalse(celebrate.topic_is_default("merge", "ship"))
        self.assertFalse(celebrate.topic_is_default("merge", "title"))
        self.assertTrue(
            celebrate.message_is_default("merge", "Merged — thank you @{author}.")
        )
        self.assertFalse(celebrate.message_is_default("merge", "Custom thanks"))

    def test_locale_picks_a_catalog_line_and_falls_back(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.normalize_locale("es-ES"), "es")
        self.assertEqual(celebrate.normalize_locale("it-IT"), "it")
        self.assertEqual(celebrate.normalize_locale("be-BY"), "be")
        self.assertEqual(celebrate.normalize_locale("uk-UA"), "uk")
        self.assertEqual(celebrate.normalize_locale("ja-JP"), "ja")
        self.assertEqual(celebrate.normalize_locale(""), "en")
        self.assertEqual(
            celebrate.localize_message(
                "merge", "Merged — thank you @{author}.", "es"
            ),
            "Fusionado — gracias @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "closed", "Closed — thank you for the work @{author}.", "uk"
            ),
            "Закрито — дякую за роботу @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "merge", "Merged — thank you @{author}.", "it"
            ),
            "Unito — grazie @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "changes",
                "A bit more work — you have this @{author}.",
                "it",
            ),
            "Ancora un po' di lavoro — ce la fai @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "merge", "Merged — thank you @{author}.", "be"
            ),
            "Змерджана — дзякуй @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "closed", "Closed — thank you for the work @{author}.", "be"
            ),
            "Закрыта — дзякуй за працу @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message(
                "merge", "Merged — thank you @{author}.", "ja"
            ),
            "マージしました — ありがとう @{author}。",
        )
        self.assertEqual(
            celebrate.localize_message(
                "changes",
                "A bit more work — you have this @{author}.",
                "ja",
            ),
            "もう少し作業を — いける @{author}。",
        )
        self.assertEqual(
            celebrate.localize_message(
                "merge", "Merged — thank you @{author}.", "zz"
            ),
            "Merged — thank you @{author}.",
        )
        self.assertEqual(
            celebrate.localize_message("merge", "Shipped. Thank you @{author}.", "es"),
            "Shipped. Thank you @{author}.",
        )
        self.assertEqual(celebrate.LOCALES["en"], celebrate.DEFAULT_MESSAGES)
        for code, pack in celebrate.LOCALES.items():
            self.assertEqual(set(pack), set(celebrate.DEFAULT_MESSAGES), code)

    def test_main_uses_locale_when_the_message_is_default(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
                "MESSAGE",
                "LOCALE",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["PR_AUTHOR"] = "alice"
            os.environ["PR_NUMBER"] = "1"
            os.environ["PR_TITLE"] = "fix: login"
            os.environ["LOCALE"] = "es"
            os.environ["MESSAGE"] = "Merged — thank you @{author}."
            celebrate.list_github_comments = lambda *_a, **_k: []  # type: ignore[method-assign]
            celebrate.list_pr_commit_messages = lambda *_a, **_k: []  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("Fusionado — gracias @alice.", buf.getvalue())
            self.assertNotIn("Merged — thank you @alice.", buf.getvalue())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_main_skips_when_title_has_no_cheer(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
                "CUSTOM_GIFS",
                "NOTE",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["PR_AUTHOR"] = "alice"
            os.environ["PR_NUMBER"] = "1"

            os.environ["PR_TITLE"] = "no-cheer: bump lockfile"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip cheer requested", buf.getvalue())
            self.assertNotIn("Merged — thank you", buf.getvalue())

            os.environ["PR_TITLE"] = "[skip cheer] fix login"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip cheer requested", buf.getvalue())
            self.assertNotIn("Merged — thank you", buf.getvalue())

            os.environ["PR_TITLE"] = "fix: login"
            os.environ["PR_LABELS"] = "no-cheer"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip cheer requested", buf.getvalue())

            os.environ.pop("PR_LABELS", None)
            celebrate.list_github_comments = lambda *_a, **_k: [  # type: ignore[method-assign]
                {"body": "<!-- merge-cheer -->\nalready\n"}
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip: already cheered", buf.getvalue())

            celebrate.list_github_comments = lambda *_a, **_k: []  # type: ignore[method-assign]
            celebrate.list_pr_commit_messages = lambda *_a, **_k: []  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("Merged — thank you @alice.", buf.getvalue())
            self.assertIn(".gif", buf.getvalue())
            self.assertIn("<!-- merge-cheer:merge -->", buf.getvalue())

            os.environ["CUSTOM_GIFS"] = "https://example.test/team/ship.gif"
            os.environ["NOTE"] = "Come hang out on Discord — https://discord.gg/your-invite"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("https://example.test/team/ship.gif", buf.getvalue())
            self.assertIn("Come hang out on Discord — https://discord.gg/your-invite", buf.getvalue())
            self.assertIn("Merged — thank you @alice.", buf.getvalue())

            os.environ.pop("CUSTOM_GIFS", None)
            os.environ.pop("NOTE", None)
            celebrate.list_github_comments = lambda *_a, **_k: [  # type: ignore[method-assign]
                {"body": "<!-- merge-cheer:changes -->\nA bit more work — you have this @alice.\n"}
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("Merged — thank you @alice.", buf.getvalue())
            self.assertNotIn("skip: already cheered", buf.getvalue())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_main_skips_already_cheered_on_gitlab_and_bitbucket(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "BITBUCKET_REPO_FULL_NAME",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "GITLAB_TOKEN",
                "CI_PROJECT_ID",
                "BITBUCKET_ACCESS_TOKEN",
                "BITBUCKET_WORKSPACE",
                "BITBUCKET_REPO_SLUG",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        marked = [{"body": "<!-- merge-cheer -->\nalready\n"}]
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["PR_AUTHOR"] = "alice"
            os.environ["PR_NUMBER"] = "1"
            os.environ["PR_TITLE"] = "fix: login"

            os.environ["GITLAB_CI"] = "true"
            celebrate.list_gitlab_notes = lambda *_a, **_k: marked  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip: already cheered", buf.getvalue())

            os.environ.pop("GITLAB_CI", None)
            os.environ["BITBUCKET_COMMIT"] = "abc"
            celebrate.list_bitbucket_comments = lambda *_a, **_k: marked  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip: already cheered", buf.getvalue())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_gitlab_and_bitbucket_can_cheer_a_closed_request(self) -> None:
        celebrate = _load()
        self.assertEqual(celebrate.detect_moment("", "true"), "merge")
        self.assertEqual(celebrate.detect_moment("", "false"), "closed")
        self.assertEqual(celebrate.detect_moment("", ""), "merge")
        celebrate._http_json = lambda *_a, **_k: {  # type: ignore[method-assign]
            "iid": 9,
            "state": "closed",
            "title": "fix: login",
            "author": {"username": "alice"},
            "description": "",
        }
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "CI_PROJECT_ID",
                "CI_MERGE_REQUEST_IID",
                "CI_COMMIT_SHA",
                "BITBUCKET_WORKSPACE",
                "BITBUCKET_REPO_SLUG",
                "BITBUCKET_PR_ID",
                "BITBUCKET_COMMIT",
            )
        }
        try:
            os.environ["CI_PROJECT_ID"] = "1"
            os.environ["CI_MERGE_REQUEST_IID"] = "9"
            found = celebrate.lookup_gitlab_mr("token")
            self.assertEqual(found.get("merged"), "false")
            self.assertEqual(found.get("number"), "9")
            celebrate._http_json = lambda *_a, **_k: {  # type: ignore[method-assign]
                "iid": 9,
                "state": "opened",
                "title": "fix: login",
                "author": {"username": "alice"},
            }
            self.assertEqual(celebrate.lookup_gitlab_mr("token"), {})
            os.environ["BITBUCKET_WORKSPACE"] = "acme"
            os.environ["BITBUCKET_REPO_SLUG"] = "app"
            os.environ["BITBUCKET_PR_ID"] = "3"
            celebrate._http_json = lambda *_a, **_k: {  # type: ignore[method-assign]
                "id": 3,
                "state": "DECLINED",
                "title": "fix: login",
                "author": {"nickname": "alice"},
                "description": "",
            }
            declined = celebrate.lookup_bitbucket_pr("token")
            self.assertEqual(declined.get("merged"), "false")
            self.assertEqual(declined.get("number"), "3")
            celebrate._http_json = lambda *_a, **_k: {  # type: ignore[method-assign]
                "iid": 8,
                "state": "opened",
                "title": "fix: login",
                "author": {"username": "alice"},
                "reviewers": [{"username": "cara", "state": "requested_changes"}],
            }
            os.environ["CI_MERGE_REQUEST_IID"] = "8"
            changed = celebrate.lookup_gitlab_mr("token")
            self.assertEqual(changed.get("review"), "changes_requested")
            self.assertEqual(changed.get("number"), "8")
            celebrate._http_json = lambda *_a, **_k: {  # type: ignore[method-assign]
                "id": 4,
                "state": "OPEN",
                "title": "fix: login",
                "author": {"nickname": "alice"},
                "participants": [
                    {"nickname": "cara", "state": "changes_requested"},
                ],
            }
            os.environ["BITBUCKET_PR_ID"] = "4"
            bb_changes = celebrate.lookup_bitbucket_pr("token")
            self.assertEqual(bb_changes.get("review"), "changes_requested")
            self.assertEqual(bb_changes.get("number"), "4")
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        env = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "BITBUCKET_REPO_FULL_NAME",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "GITHUB_OUTPUT",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["GITLAB_CI"] = "true"
            os.environ["PR_TITLE"] = "fix: login"
            celebrate.lookup_gitlab_mr = lambda *_a, **_k: {  # type: ignore[method-assign]
                "number": "9",
                "title": "fix: login",
                "author": "alice",
                "body": "",
                "association": "",
                "merged": "false",
            }
            celebrate.list_gitlab_notes = lambda *_a, **_k: []  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("Closed — thank you for the work @alice.", buf.getvalue())
            self.assertIn("gifs/coffee/", buf.getvalue())
            self.assertNotIn("Merged — thank you", buf.getvalue())
        finally:
            for key, value in env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_main_uses_yeah_gif_when_gitlab_requests_changes(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "BITBUCKET_REPO_FULL_NAME",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "REVIEW_AUTHOR",
                "GITHUB_OUTPUT",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["GITLAB_CI"] = "true"
            os.environ["PR_TITLE"] = "fix: login"
            celebrate.lookup_gitlab_mr = lambda *_a, **_k: {  # type: ignore[method-assign]
                "number": "8",
                "title": "fix: login",
                "author": "alice",
                "body": "",
                "association": "",
                "merged": "",
                "review": "changes_requested",
            }
            celebrate.list_gitlab_notes = lambda *_a, **_k: []  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("A bit more work — you have this @alice.", buf.getvalue())
            self.assertIn("gifs/yeah/", buf.getvalue())
            self.assertNotIn("Merged — thank you", buf.getvalue())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_main_skip_logs_for_bot_and_non_cheer(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "BITBUCKET_REPO_FULL_NAME",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_AUTHOR_TYPE",
                "PR_NUMBER",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "REVIEW_AUTHOR",
                "REVIEW_AUTHOR_TYPE",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["PR_NUMBER"] = "1"
            os.environ["PR_TITLE"] = "fix: login"

            os.environ["PR_AUTHOR"] = "dependabot[bot]"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip bot author", buf.getvalue())

            os.environ["PR_AUTHOR"] = "alice"
            os.environ["REVIEW_STATE"] = "changes_requested"
            os.environ["REVIEW_AUTHOR"] = "renovate[bot]"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip bot reviewer", buf.getvalue())

            os.environ.pop("REVIEW_AUTHOR", None)
            os.environ["REVIEW_STATE"] = "approved"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            self.assertEqual(code, 0)
            self.assertIn("skip: not a cheer moment", buf.getvalue())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_more_openai_example_is_closed_and_changes(self) -> None:
        text = (ROOT / "examples" / "celebrate-more-openai.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request_review", text)
        self.assertIn("changes_requested", text)
        self.assertIn("model: gpt-4o-mini", text)
        self.assertIn("secrets.OPENAI_API_KEY", text)
        self.assertIn("YauhenBichel/merge-cheer@v1.7.0", text)
        self.assertNotIn("e183fbc7b8e395506e627ff60600577dfb5f8f45", text)
        self.assertIn("closed-topic", text)
        self.assertIn("changes-topic", text)
        self.assertNotIn("github.event.pull_request.merged &&", text)

    def test_main_uses_model_on_closed_and_keeps_coffee_gif(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "REVIEW_AUTHOR",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["EVENT_NAME"] = "pull_request"
            os.environ["PR_MERGED"] = "false"
            os.environ["PR_AUTHOR"] = "alice"
            os.environ["PR_NUMBER"] = "1"
            os.environ["PR_TITLE"] = "docs: login help"
            os.environ["MODEL"] = "gpt-4o-mini"
            os.environ["MODEL_API_KEY"] = "sk-test"
            celebrate.list_github_comments = lambda *_a, **_k: []  # type: ignore[method-assign]
            celebrate.list_pr_commit_messages = lambda *_a, **_k: []  # type: ignore[method-assign]

            def fake_ok(_url, _token, method="GET", payload=None, headers=None):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"message": '
                                    '"Login help still needs a pass — thanks {author}."}'
                                )
                            }
                        }
                    ]
                }

            celebrate._http_json = fake_ok  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            out = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Login help still needs a pass — thanks @alice.", out)
            self.assertIn("gifs/coffee/", out)
            self.assertNotIn("Closed — thank you for the work", out)
            self.assertNotIn("gifs/yeah/", out)
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_main_uses_model_on_changes_and_keeps_yeah_gif(self) -> None:
        celebrate = _load()
        saved = {
            key: os.environ.pop(key, None)
            for key in (
                "GITHUB_ACTIONS",
                "GITLAB_CI",
                "BITBUCKET_COMMIT",
                "EVENT_NAME",
                "PR_MERGED",
                "REVIEW_STATE",
                "REVIEW_AUTHOR",
                "REVIEW_AUTHOR_TYPE",
                "PR_TITLE",
                "PR_BODY",
                "PR_LABELS",
                "DRY_RUN",
                "PR_AUTHOR",
                "PR_NUMBER",
                "GITHUB_OUTPUT",
                "GITHUB_REPOSITORY",
                "GITHUB_TOKEN",
                "MODEL",
                "MODEL_API_KEY",
                "MODEL_BASE_URL",
            )
        }
        try:
            os.environ["DRY_RUN"] = "1"
            os.environ["REVIEW_STATE"] = "changes_requested"
            os.environ["REVIEW_AUTHOR"] = "bob"
            os.environ["PR_AUTHOR"] = "alice"
            os.environ["PR_NUMBER"] = "1"
            os.environ["PR_TITLE"] = "docs: login help"
            os.environ["MODEL"] = "gpt-4o-mini"
            os.environ["MODEL_API_KEY"] = "sk-test"
            celebrate.list_github_comments = lambda *_a, **_k: []  # type: ignore[method-assign]
            celebrate.list_pr_commit_messages = lambda *_a, **_k: []  # type: ignore[method-assign]

            def fake_ok(_url, _token, method="GET", payload=None, headers=None):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"message": '
                                    '"Login help still needs a pass — thanks {author}."}'
                                )
                            }
                        }
                    ]
                }

            celebrate._http_json = fake_ok  # type: ignore[method-assign]
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = celebrate.main()
            out = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Login help still needs a pass — thanks @alice.", out)
            self.assertIn("gifs/yeah/", out)
            self.assertNotIn("A bit more work — you have this", out)
            self.assertNotIn("gifs/coffee/", out)
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
