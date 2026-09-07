#!/usr/bin/env python3
"""Pick a merge GIF and comment it on the pull request. Stdlib only."""

from __future__ import annotations

import html
import json
import os
import random
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Comments show the 280px GIF at 2×. Rebuilding at 560px blows the 180 KB cap.
GIF_DISPLAY_WIDTH = 560

# Public group names. Users pass these as `topic`.
GROUPS = (
    "ship",
    "fix",
    "docs",
    "tests",
    "cleanup",
    "celebration",
    "welcome",
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
)

# Extra spellings that resolve to a group. `auto` and `title` are not aliases.
ALIASES = {
    "ship": "ship",
    "launch": "ship",
    "ship-it": "ship",
    "ship it": "ship",
    "fix": "fix",
    "nailed-it": "fix",
    "nailed it": "fix",
    "docs": "docs",
    "doc": "docs",
    "nice-work": "docs",
    "nice work": "docs",
    "tests": "tests",
    "test": "tests",
    "ci": "tests",
    "high-five": "tests",
    "high five": "tests",
    "cleanup": "cleanup",
    "refactor": "cleanup",
    "clean": "cleanup",
    "celebration": "celebration",
    "welcome": "welcome",
    "first": "welcome",
    "first-contribution": "welcome",
    "party": "party",
    "congrats": "party",
    "woo": "party",
    "hooray": "party",
    "space": "space",
    "cosmos": "space",
    "galaxy": "space",
    "magic": "magic",
    "sparkle": "magic",
    "coffee": "coffee",
    "latte": "coffee",
    "robot": "robot",
    "bot": "robot",
    "comic": "comic",
    "kapow": "comic",
    "sunny": "sunny",
    "sunshine": "sunny",
    "game": "game",
    "level-up": "game",
    "levelup": "game",
    "combo": "game",
    "sticker": "sticker",
    "stickers": "sticker",
    "yeah": "yeah",
    "lets-go": "yeah",
    "let's-go": "yeah",
    "fist-pump": "yeah",
    "devops": "devops",
    "k8s": "devops",
    "kubernetes": "devops",
    "docker": "devops",
    "terraform": "devops",
    "sre": "sre",
    "oncall": "sre",
    "on-call": "sre",
    "qa": "qa",
    "testing": "qa",
    "sdet": "qa",
    "design": "design",
    "ux": "design",
    "ui": "design",
    "figma": "design",
    "architecture": "architecture",
    "arch": "architecture",
    "adr": "architecture",
    "engineering": "engineering",
    "swe": "engineering",
    "software-engineering": "engineering",
    "backend": "backend",
    "back-end": "backend",
    "frontend": "frontend",
    "front-end": "frontend",
    "javascript": "frontend",
    "typescript": "frontend",
    "js": "frontend",
    "react": "frontend",
    "java": "java",
    "jdk": "java",
    "jvm": "java",
    "python": "python",
    "py": "python",
    "cpp": "cpp",
    "c++": "cpp",
    "cplusplus": "cpp",
    "cxx": "cpp",
    "golang": "golang",
    "go": "golang",
    "gopher": "golang",
}

# Giphy search text when a key is set.
GIPHY_TAG = {
    "ship": "ship it",
    "fix": "nailed it",
    "docs": "nice work",
    "tests": "high five",
    "cleanup": "cleanup",
    "celebration": "celebration",
    "welcome": "high five",
    "party": "celebration",
    "space": "stars",
    "magic": "magic",
    "coffee": "coffee",
    "robot": "robot",
    "comic": "comic",
    "sunny": "sunny",
    "game": "level up",
    "sticker": "sticker",
    "yeah": "yeah",
    "devops": "devops",
    "sre": "sre",
    "qa": "testing",
    "design": "design",
    "architecture": "architecture",
    "engineering": "engineering",
    "backend": "backend",
    "frontend": "frontend",
    "java": "java",
    "python": "python",
    "cpp": "c++",
    "golang": "golang",
}

# Alt text for the posted image.
LABEL = {
    "ship": "ship it",
    "fix": "nailed it",
    "docs": "nice work",
    "tests": "high five",
    "cleanup": "cleanup",
    "celebration": "celebration",
    "welcome": "welcome",
    "party": "party",
    "space": "space",
    "magic": "magic",
    "coffee": "coffee",
    "robot": "robot",
    "comic": "comic",
    "sunny": "sunny",
    "game": "game",
    "sticker": "sticker",
    "yeah": "yeah",
    "devops": "devops",
    "sre": "sre",
    "qa": "qa",
    "design": "design",
    "architecture": "architecture",
    "engineering": "engineering",
    "backend": "backend",
    "frontend": "frontend",
    "java": "java",
    "python": "python",
    "cpp": "c++",
    "golang": "golang",
}

FIRST_TIMERS = frozenset({"FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR"})

# Title keywords, first match wins. Conventional types stay above mood
# groups so "feat" / "fix" are not stolen. Keep "ship" and "space" off
# bare substrings ("fellowship", "namespace").
_TITLE_RULES = (
    ("fix", ("fix", "bug", "hotfix", "patch", "revert:", "revert ")),
    ("ship", ("feat", "add ", "added", "new ", "launch", "ship:", "ship ", "perf:", "perf ")),
    ("docs", ("doc", "readme")),
    ("tests", ("test", " ci", "ci:", "ci ", "-ci")),
    (
        "cleanup",
        (
            "refactor",
            "clean",
            "deps:",
            "deps ",
            "typo",
            "style",
            "lint",
            "format",
        ),
    ),
    ("welcome", ("welcome", "first contrib", "good first", "first-time")),
    ("party", ("party", "congrats", "woo", "hooray", "celebrate")),
    ("space", ("cosmos", "galaxy", "orbit", "planet", "outer space")),
    ("magic", ("magic", "sparkle", "wand", "spell")),
    ("coffee", ("coffee", "latte", "caffeine", "espresso")),
    ("robot", ("robot", "android")),
    ("comic", ("comic", "kapow")),
    ("sunny", ("sunny", "sunshine", "sunbeam")),
    ("game", ("level-up", "level up", "combo", "high-score", "high score")),
    ("sticker", ("sticker",)),
    ("yeah", ("yeah", "let's go", "lets go", "fist pump", "fist-pump")),
    ("devops", ("devops", "kubernetes", "k8s", "terraform", "docker", "helm")),
    ("sre", ("sre", "on-call", "oncall", "error budget", "slo")),
    ("qa", (" qa", "qa:", "sdet", "quality")),
    ("design", ("design", "figma", "ux ", " ui:", "mockup")),
    ("architecture", ("architecture", "adr", "system design")),
    ("engineering", ("software engineering", " swe ", "swe:", "swe ")),
    ("backend", ("backend", "back-end", "graphql")),
    ("frontend", ("frontend", "front-end", "javascript", "typescript", "react", "vue")),
    ("python", ("python", "django", "flask")),
    ("cpp", ("c++", "cplusplus", " cpp", "cpp:", "cpp ")),
    ("golang", ("golang", "gopher")),
    ("java", ("java:", "java ", "jdk", "jvm", "spring boot")),
)


def allowed_topics() -> str:
    return ", ".join(("auto", "title") + GROUPS)


def normalize_topic(value: str) -> str:
    raw = (value or "auto").strip().lower().replace("_", "-")
    if raw in ("", "auto"):
        return "auto"
    if raw == "title":
        return "title"
    return ALIASES.get(raw, "")


def _first_title_match(text: str) -> str:
    low = (text or "").lower()
    if not low.strip():
        return ""
    for group, words in _TITLE_RULES:
        if any(word in low for word in words):
            return group
    return ""


def pick_from_title(title: str, association: str = "", body: str = "") -> str:
    matched = _first_title_match(title)
    if matched:
        return matched
    matched = _first_title_match(body)
    if matched:
        return matched
    if association.upper() in FIRST_TIMERS:
        return "welcome"
    return "celebration"


def pick_random_group(seed: str = "") -> str:
    """Seeded by PR number when set; otherwise the clock."""
    return random.Random(seed or None).choice(GROUPS)


def resolve_group(
    title: str,
    topic: str,
    association: str = "",
    seed: str = "",
    body: str = "",
) -> str:
    """Pick a group. Unknown explicit topics fall back to celebration."""
    chosen = normalize_topic(topic)
    if chosen == "auto":
        return pick_random_group(seed)
    if chosen == "title":
        return pick_from_title(title, association, body)
    if not chosen:
        print(
            f"unknown topic {topic!r}; allowed: {allowed_topics()}",
            file=sys.stderr,
        )
        return "celebration"
    return chosen


def action_root() -> Path:
    override = os.environ.get("ACTION_PATH", "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1]


# Filenames the Action ships. Used when gifs/ is not on disk (GitLab /
# Bitbucket curl the script only). Keep in sync with scripts/make_gifs.py.
BUNDLED_GIFS = {
    "ship": ("ship-it.gif", "alt.gif", "boost.gif"),
    "fix": ("nailed-it.gif", "alt.gif", "spark.gif"),
    "docs": ("nice-work.gif", "alt.gif", "glow.gif"),
    "tests": ("high-five.gif", "alt.gif"),
    "cleanup": ("cleanup.gif", "alt.gif", "sweep.gif"),
    "celebration": ("celebration.gif", "alt.gif", "burst.gif"),
    "welcome": ("high-five.gif", "celebration.gif"),
    "party": ("confetti.gif", "toast.gif"),
    "space": ("planet.gif", "comet.gif"),
    "magic": ("wand.gif", "sparkles.gif"),
    "coffee": ("mug.gif", "night.gif"),
    "robot": ("wave.gif", "dance.gif"),
    "comic": ("burst.gif", "pop.gif"),
    "sunny": ("sun.gif", "rainbow.gif"),
    "game": ("levelup.gif", "combo.gif"),
    "sticker": ("star.gif", "thumb.gif"),
    "yeah": ("pump.gif", "jump.gif"),
    "devops": ("loop.gif", "pipeline.gif"),
    "sre": ("lighthouse.gif", "pager.gif"),
    "qa": ("lens.gif", "pass.gif"),
    "design": ("palette.gif", "frames.gif"),
    "architecture": ("blocks.gif", "blueprint.gif"),
    "engineering": ("wrench.gif", "build.gif"),
    "backend": ("db.gif", "server.gif"),
    "frontend": ("browser.gif", "cursor.gif"),
    "java": ("mug.gif", "steam.gif"),
    "python": ("snake.gif", "coil.gif"),
    "cpp": ("plus.gif", "gear.gif"),
    "golang": ("gopher.gif", "wave.gif"),
}


def group_gif_names(root: Path, group: str) -> list[str]:
    folder = root / "gifs" / group
    names = [path.name for path in sorted(folder.glob("*.gif"))]
    if names:
        return names
    return list(BUNDLED_GIFS.get(group, ()))


def pick_gif_name(names: list[str], seed: str) -> str:
    if not names:
        return ""
    return names[random.Random(seed).randrange(len(names))]


def choose_gif(root: Path, group: str, seed: str) -> tuple[str, str]:
    names = group_gif_names(root, group)
    if not names and group != "celebration":
        group = "celebration"
        names = group_gif_names(root, group)
    return group, pick_gif_name(names, f"{seed}:{group}")


def slug(tag: str) -> str:
    return tag.replace(" ", "-")


def normalize_ref(ref: str) -> str:
    value = (ref or "main").strip() or "main"
    for prefix in ("refs/heads/", "refs/tags/"):
        if value.startswith(prefix):
            return value[len(prefix) :]
    return value


DEFAULT_ACTION_REPO = "YauhenBichel/merge-cheer"


def bundled_url(action_repo: str, action_ref: str, group: str, name: str) -> str:
    if not name:
        return ""
    repo = (action_repo or "").strip() or DEFAULT_ACTION_REPO
    return (
        f"https://raw.githubusercontent.com/{repo}/"
        f"{normalize_ref(action_ref)}/gifs/{group}/{name}"
    )


def giphy_url(key: str, tag: str, rating: str) -> str:
    if not key:
        return ""
    query = urllib.parse.urlencode(
        {"api_key": key, "tag": tag, "rating": rating or "g"}
    )
    request = urllib.request.Request(
        f"https://api.giphy.com/v1/gifs/random?{query}",
        headers={"User-Agent": "merge-cheer"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"giphy skipped: {exc}", file=sys.stderr)
        return ""
    images = (payload.get("data") or {}).get("images") or {}
    return str(
        (images.get("downsized") or {}).get("url")
        or (images.get("original") or {}).get("url")
        or ""
    )


CHEER_MARKER = "<!-- merge-cheer -->"
SKIP_LABELS = frozenset({"no-cheer", "skip-cheer"})
_COAUTHOR_LINE = re.compile(r"(?im)^[ \t]*co-authored-by:[ \t]+(.+)$")
_GITHUB_NOREPLY = re.compile(
    r"(?:(?P<id>\d+)\+)?(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)"
    r"@users\.noreply\.github\.com$",
    re.I,
)
_LOGIN_TOKEN = re.compile(
    r"^@?(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)\b"
)
GITHUB_MODELS_URL = "https://models.github.ai/inference"
AZURE_MODELS_URL = "https://models.inference.ai.azure.com"
_UNSAFE = (
    "nsfw",
    "porn",
    "sex",
    "nude",
    "xxx",
    "kill yourself",
    "kys",
    "suicide",
    "slur",
)


def comment_body(
    message: str,
    author: str,
    tag: str,
    gif: str,
    authors: str = "",
) -> str:
    who = (author or "").lstrip("@")
    named = authors or (f"@{who}" if who else "")
    text = message or "Merged — thank you @{author}."
    text = text.replace("{authors}", named)
    if "@{author}" in text:
        text = text.replace("{author}", named.lstrip("@") if named else who)
    else:
        text = text.replace("{author}", who)
    if not text.endswith("\n"):
        text += "\n"
    if gif:
        src = html.escape(gif, quote=True)
        alt = html.escape(tag or "celebration", quote=True)
        text += f'\n<img src="{src}" alt="{alt}" width="{GIF_DISPLAY_WIDTH}" />\n'
    return f"{CHEER_MARKER}\n{text}"


DEFAULT_MESSAGES = {
    "merge": "Merged — thank you @{author}.",
    "closed": "Closed — thank you for the work @{author}.",
    "changes": "A bit more work — you have this @{author}.",
}

# Static catalog for `locale`. Unknown codes fall back to English.
# A pinned message / closed-message / changes-message still wins.
LOCALES = {
    "en": DEFAULT_MESSAGES,
    "es": {
        "merge": "Fusionado — gracias @{author}.",
        "closed": "Cerrado — gracias por el trabajo @{author}.",
        "changes": "Un poco más de trabajo — tú puedes @{author}.",
    },
    "de": {
        "merge": "Gemerged — danke @{author}.",
        "closed": "Geschlossen — danke für die Arbeit @{author}.",
        "changes": "Noch etwas Arbeit — du schaffst das @{author}.",
    },
    "fr": {
        "merge": "Fusionné — merci @{author}.",
        "closed": "Fermé — merci pour le travail @{author}.",
        "changes": "Encore un peu de travail — tu vas y arriver @{author}.",
    },
    "pt": {
        "merge": "Mesclado — obrigado @{author}.",
        "closed": "Fechado — obrigado pelo trabalho @{author}.",
        "changes": "Um pouco mais de trabalho — você consegue @{author}.",
    },
    "uk": {
        "merge": "Змерджено — дякую @{author}.",
        "closed": "Закрито — дякую за роботу @{author}.",
        "changes": "Ще трохи роботи — у тебе вийде @{author}.",
    },
}


def normalize_locale(raw: str) -> str:
    code = (raw or "").strip().lower().replace("_", "-")
    if not code:
        return "en"
    return code.split("-", 1)[0]


def localize_message(moment: str, message: str, locale: str) -> str:
    text = (message or "").strip()
    if text != DEFAULT_MESSAGES.get(moment, ""):
        return message
    pack = LOCALES.get(normalize_locale(locale)) or LOCALES["en"]
    return pack.get(moment) or DEFAULT_MESSAGES.get(moment, text)

DEFAULT_TOPICS = {
    "merge": "auto",
    "closed": "coffee",
    "changes": "yeah",
}


def _flag(raw: str) -> bool:
    return (raw or "").strip().lower() in {"1", "true", "yes"}


def detect_moment(
    event_name: str = "",
    merged: str = "",
    review_state: str = "",
) -> str | None:
    """Which comment to post. None means skip (approve, comment, …)."""
    state = (review_state or "").strip().lower()
    if state:
        if state == "changes_requested":
            return "changes"
        return None
    name = (event_name or "").strip().lower()
    if _flag(merged):
        return "merge"
    if name in {"", "pull_request", "pull_request_target"}:
        if name == "" and merged == "":
            return "merge"
        return "closed"
    return None


def moment_topic(
    moment: str,
    topic: str = "auto",
    closed_topic: str = "",
    changes_topic: str = "",
) -> str:
    if moment == "closed":
        return (closed_topic or "").strip() or DEFAULT_TOPICS["closed"]
    if moment == "changes":
        return (changes_topic or "").strip() or DEFAULT_TOPICS["changes"]
    return (topic or "").strip() or DEFAULT_TOPICS["merge"]


def moment_message(
    moment: str,
    message: str = "",
    closed_message: str = "",
    changes_message: str = "",
) -> str:
    if moment == "closed":
        return (closed_message or "").strip() or DEFAULT_MESSAGES["closed"]
    if moment == "changes":
        return (changes_message or "").strip() or DEFAULT_MESSAGES["changes"]
    return (message or "").strip() or DEFAULT_MESSAGES["merge"]


def detect_host() -> str:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github"
    if os.environ.get("GITLAB_CI") == "true":
        return "gitlab"
    if os.environ.get("BITBUCKET_COMMIT") or os.environ.get("BITBUCKET_REPO_FULL_NAME"):
        return "bitbucket"
    return "github"


SKIP_MARKERS = ("no-cheer", "[skip cheer]")


def parse_labels(raw: str) -> list[str]:
    names: list[str] = []
    for part in (raw or "").replace("\n", ",").split(","):
        name = part.strip()
        if name:
            names.append(name)
    return names


def should_skip(title: str, labels: str = "") -> bool:
    low = (title or "").lower()
    if any(marker in low for marker in SKIP_MARKERS):
        return True
    return any(name.lower() in SKIP_LABELS for name in parse_labels(labels))


def parse_coauthors(*texts: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    blob = "\n".join(text or "" for text in texts)
    for match in _COAUTHOR_LINE.finditer(blob):
        login = _coauthor_login(match.group(1))
        key = login.lower()
        if not login or key in seen or is_bot_author(login):
            continue
        seen.add(key)
        found.append(login)
    return found


def _coauthor_login(rest: str) -> str:
    raw = (rest or "").strip()
    name_part = raw.split("<", 1)[0].strip()
    if is_bot_author(name_part):
        return ""
    email_match = re.search(r"<([^>]+)>", raw)
    if email_match:
        email = email_match.group(1).strip()
        noreply = _GITHUB_NOREPLY.search(email)
        if noreply:
            return noreply.group("login")
        return ""
    token = _LOGIN_TOKEN.match(raw)
    return token.group("login") if token else ""


def format_authors(logins: list[str]) -> str:
    tagged = [f"@{login.lstrip('@')}" for login in logins if login.strip()]
    if not tagged:
        return ""
    if len(tagged) == 1:
        return tagged[0]
    if len(tagged) == 2:
        return f"{tagged[0]} and {tagged[1]}"
    return f"{', '.join(tagged[:-1])}, and {tagged[-1]}"


def collect_authors(author: str, *texts: str) -> list[str]:
    people: list[str] = []
    seen: set[str] = set()

    def add(login: str) -> None:
        name = (login or "").strip().lstrip("@")
        key = name.lower()
        if not name or key in seen or is_bot_author(name):
            return
        seen.add(key)
        people.append(name)

    add(author)
    for login in parse_coauthors(*texts):
        add(login)
    return people


def already_cheered(comments: object) -> bool:
    if not isinstance(comments, list):
        return False
    for item in comments:
        if isinstance(item, dict) and CHEER_MARKER in str(item.get("body") or ""):
            return True
    return False


def is_grated(text: str) -> bool:
    low = (text or "").lower()
    if not low.strip():
        return False
    return not any(word in low for word in _UNSAFE)


def is_bot_author(author: str, kind: str = "") -> bool:
    if (kind or "").lower() == "bot":
        return True
    low = (author or "").lower()
    if not low:
        return False
    return (
        low.endswith("[bot]")
        or low.endswith("_bot")
        or low.endswith("-bot")
        or "dependabot" in low
        or low in {"ghost", "renovate-bot", "bitbucket-pipelines"}
    )


def _http_json(
    url: str, token: str, method: str = "GET", payload: dict | None = None, headers: dict | None = None
) -> object:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers=headers
        or {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "merge-cheer",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        print(f"{method} {response.status}")
        if not raw:
            return {}
        return json.loads(raw)


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "merge-cheer",
        "Content-Type": "application/json",
    }


def post_github_comment(token: str, repo: str, number: str, body: str) -> None:
    if not token or not repo or not number:
        raise SystemExit("GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER are required")
    _http_json(
        f"https://api.github.com/repos/{repo}/issues/{number}/comments",
        token,
        method="POST",
        payload={"body": body},
        headers=_github_headers(token),
    )


def list_github_comments(token: str, repo: str, number: str) -> list:
    if not token or not repo or not number:
        return []
    try:
        data = _http_json(
            f"https://api.github.com/repos/{repo}/issues/{number}/comments?per_page=100",
            token,
            headers=_github_headers(token),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"comments lookup skipped: {exc}", file=sys.stderr)
        return []
    return data if isinstance(data, list) else []


def list_pr_commit_messages(token: str, repo: str, number: str) -> list[str]:
    if not token or not repo or not number:
        return []
    try:
        data = _http_json(
            f"https://api.github.com/repos/{repo}/pulls/{number}/commits?per_page=100",
            token,
            headers=_github_headers(token),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"commits lookup skipped: {exc}", file=sys.stderr)
        return []
    if not isinstance(data, list):
        return []
    messages: list[str] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        commit = row.get("commit")
        if isinstance(commit, dict) and commit.get("message"):
            messages.append(str(commit["message"]))
    return messages


def model_settings() -> tuple[str, str, str] | None:
    """Return (api_key, model, base_url) when a model call is allowed."""
    name = os.environ.get("MODEL", "").strip()
    key = os.environ.get("MODEL_API_KEY", "").strip()
    base = os.environ.get("MODEL_BASE_URL", "").strip().rstrip("/")
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    low = name.lower()
    githubish = (
        "models.github.ai" in base
        or "models.inference.ai.azure.com" in base
        or low in {"github", "github-models"}
    )
    if githubish:
        if not (key or token):
            return None
        model = name if name and low not in {"github", "github-models"} else "openai/gpt-4o-mini"
        return (key or token, model, base or GITHUB_MODELS_URL)
    if not key:
        return None
    return (key, name or "gpt-4o-mini", base or "https://api.openai.com/v1")


_GENERIC_CHEER = re.compile(
    r"^(?:(?:merged\s*[—\-]?\s*)?thank(?:s| you)"
    r"(?:\s+for(?:\s+the)?\s+(?:work|pr|help))?|thanks?)"
    r"[\s.,!]*"
    r"(?:\{authors?\}|@\{author\}|@\w+)?"
    r"[\s.,!]*$",
    re.I,
)
_TITLE_STOP = frozenset(
    {
        "a",
        "an",
        "and",
        "the",
        "for",
        "from",
        "with",
        "this",
        "that",
        "into",
        "onto",
        "chore",
        "docs",
        "doc",
        "feat",
        "fix",
        "ci",
        "test",
        "tests",
        "merge",
        "merged",
        "pr",
        "pull",
        "request",
        "add",
        "added",
        "update",
        "updated",
        "bump",
    }
)


def title_tokens(title: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{4,}", (title or "").lower())
    return {word for word in words if word not in _TITLE_STOP}


def cheer_is_specific(title: str, message: str) -> bool:
    line = (message or "").strip()
    if not is_grated(line):
        return False
    if any(line.lower() == default.lower() for default in DEFAULT_MESSAGES.values()):
        return False
    stripped = re.sub(r"\{authors?\}|@\{author\}", "", line).strip()
    if _GENERIC_CHEER.match(line) or _GENERIC_CHEER.match(stripped):
        return False
    tokens = title_tokens(title)
    if not tokens:
        return True
    low = line.lower()
    return any(token in low for token in tokens)


def _parse_model_payload(raw: str) -> str | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    message = str(data.get("message") or "").strip()
    return message or None


def ask_model(
    moment: str,
    title: str,
    body: str,
    author: str,
    authors: str,
) -> str | None:
    cfg = model_settings()
    if not cfg:
        return None
    key, model, base = cfg
    excerpt = (body or "")[:200]
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    system = (
        "You write one G-rated pull-request thank-you that is about "
        "what just landed. "
        'Reply with JSON only: {"message": "<one short line>"}. '
        "The message must mention something from the title. "
        "Do not write a generic thanks. "
        "Use {author} or {authors} placeholders. "
        "No slurs, no adult content, no violence."
    )
    user = json.dumps(
        {
            "moment": moment,
            "repository": repo,
            "title": title,
            "body": excerpt,
            "author": author,
            "authors": authors,
        }
    )
    url = f"{base.rstrip('/')}/chat/completions"
    try:
        data = _http_json(
            url,
            key,
            method="POST",
            payload={
                "model": model,
                "temperature": 0.4,
                "max_tokens": 60,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"model skipped: {exc}", file=sys.stderr)
        return None
    content = ""
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices and isinstance(choices[0], dict):
            message = (choices[0].get("message") or {}) if isinstance(
                choices[0].get("message"), dict
            ) else {}
            content = str(message.get("content") or "")
    line = _parse_model_payload(content)
    if not line or not cheer_is_specific(title, line):
        print("model skipped: generic or unsafe", file=sys.stderr)
        return None
    print(f"model: message={line}", file=sys.stderr)
    return line


def topic_is_default(moment: str, topic: str) -> bool:
    chosen = normalize_topic(topic)
    if chosen in {"", "auto"}:
        return True
    default = normalize_topic(DEFAULT_TOPICS.get(moment, "auto"))
    return moment != "merge" and chosen == default


def message_is_default(moment: str, message: str) -> bool:
    return (message or "").strip() == DEFAULT_MESSAGES.get(moment, "")


def gitlab_headers(token: str) -> dict[str, str]:
    job = os.environ.get("CI_JOB_TOKEN", "").strip()
    if job and token == job:
        return {
            "JOB-TOKEN": token,
            "User-Agent": "merge-cheer",
            "Content-Type": "application/json",
        }
    return {
        "PRIVATE-TOKEN": token,
        "User-Agent": "merge-cheer",
        "Content-Type": "application/json",
    }


def gitlab_api_root() -> str:
    explicit = os.environ.get("CI_API_V4_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    host = os.environ.get("CI_SERVER_URL", "https://gitlab.com").rstrip("/")
    return f"{host}/api/v4"


def post_gitlab_note(token: str, project: str, iid: str, body: str) -> None:
    if not token or not project or not iid:
        raise SystemExit("GITLAB_TOKEN, CI_PROJECT_ID, and merge request iid are required")
    encoded = urllib.parse.quote(str(project), safe="")
    _http_json(
        f"{gitlab_api_root()}/projects/{encoded}/merge_requests/{iid}/notes",
        token,
        method="POST",
        payload={"body": body},
        headers=gitlab_headers(token),
    )


def list_gitlab_notes(token: str, project: str, iid: str) -> list:
    if not token or not project or not iid:
        return []
    encoded = urllib.parse.quote(str(project), safe="")
    try:
        data = _http_json(
            f"{gitlab_api_root()}/projects/{encoded}/merge_requests/{iid}/notes?per_page=100",
            token,
            headers=gitlab_headers(token),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"notes lookup skipped: {exc}", file=sys.stderr)
        return []
    if not isinstance(data, list):
        return []
    notes = []
    for item in data:
        if isinstance(item, dict):
            notes.append({"body": str(item.get("body") or "")})
    return notes


def lookup_gitlab_mr(token: str) -> dict[str, str]:
    project = os.environ.get("CI_PROJECT_ID", "").strip()
    iid = os.environ.get("CI_MERGE_REQUEST_IID", "").strip()
    sha = os.environ.get("CI_COMMIT_SHA", "").strip()
    if not token or not project:
        return {}
    encoded = urllib.parse.quote(project, safe="")
    data: object
    if iid:
        data = _http_json(
            f"{gitlab_api_root()}/projects/{encoded}/merge_requests/{iid}",
            token,
            headers=gitlab_headers(token),
        )
    elif sha:
        data = _http_json(
            f"{gitlab_api_root()}/projects/{encoded}/repository/commits/{sha}/merge_requests",
            token,
            headers=gitlab_headers(token),
        )
        if isinstance(data, list):
            data = data[0] if data else {}
    else:
        return {}
    if not isinstance(data, dict) or not data:
        return {}
    if str(data.get("state") or "") not in {"merged", ""}:
        if iid and str(data.get("state") or "") != "merged":
            return {}
    user = data.get("author") or {}
    return {
        "number": str(data.get("iid") or iid),
        "title": str(data.get("title") or ""),
        "author": str(user.get("username") or ""),
        "body": str(data.get("description") or ""),
        "association": "FIRST_TIME_CONTRIBUTOR"
        if data.get("first_contribution")
        else "",
    }


def post_bitbucket_comment(token: str, workspace: str, slug: str, number: str, body: str) -> None:
    if not token or not workspace or not slug or not number:
        raise SystemExit(
            "BITBUCKET_ACCESS_TOKEN, BITBUCKET_WORKSPACE, BITBUCKET_REPO_SLUG, and PR id are required"
        )
    _http_json(
        f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/pullrequests/{number}/comments",
        token,
        method="POST",
        payload={"content": {"raw": body}},
    )


def list_bitbucket_comments(token: str, workspace: str, slug: str, number: str) -> list:
    if not token or not workspace or not slug or not number:
        return []
    try:
        data = _http_json(
            f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/pullrequests/{number}/comments?pagelen=100",
            token,
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"comments lookup skipped: {exc}", file=sys.stderr)
        return []
    values = data.get("values") if isinstance(data, dict) else data
    if not isinstance(values, list):
        return []
    comments = []
    for item in values:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or {}
        raw = content.get("raw") if isinstance(content, dict) else ""
        comments.append({"body": str(raw or "")})
    return comments


def lookup_bitbucket_pr(token: str) -> dict[str, str]:
    workspace = os.environ.get("BITBUCKET_WORKSPACE", "").strip()
    slug = os.environ.get("BITBUCKET_REPO_SLUG", "").strip()
    number = os.environ.get("BITBUCKET_PR_ID", "").strip()
    commit = os.environ.get("BITBUCKET_COMMIT", "").strip()
    if not token or not workspace or not slug:
        return {}
    data: object
    if number:
        data = _http_json(
            f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/pullrequests/{number}",
            token,
        )
    elif commit:
        data = _http_json(
            f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/commit/{commit}/pullrequests",
            token,
        )
        values = data.get("values") if isinstance(data, dict) else None
        data = values[0] if values else {}
    else:
        return {}
    if not isinstance(data, dict) or not data:
        return {}
    state = str(data.get("state") or "").upper()
    if state and state != "MERGED":
        return {}
    author = ((data.get("author") or {}).get("nickname") or "")
    return {
        "number": str(data.get("id") or number),
        "title": str(data.get("title") or ""),
        "author": str(author),
        "body": str(data.get("description") or ""),
        "association": "",
    }


def post_comment(token: str, repo: str, number: str, body: str) -> None:
    post_github_comment(token, repo, number, body)


def write_output(path: str, values: dict[str, str]) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    host = detect_host()
    title = os.environ.get("PR_TITLE", "")
    pr_body = os.environ.get("PR_BODY", "")
    labels = os.environ.get("PR_LABELS", "")
    topic = os.environ.get("TOPIC", "auto")
    association = os.environ.get("PR_AUTHOR_ASSOCIATION", "")
    author = os.environ.get("PR_AUTHOR", "").strip()
    number = os.environ.get("PR_NUMBER", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if host == "gitlab" and not number:
        found = lookup_gitlab_mr(
            (
                os.environ.get("GITLAB_TOKEN")
                or os.environ.get("CI_JOB_TOKEN")
                or ""
            ).strip()
        )
        title = title or found.get("title", "")
        author = author or found.get("author", "")
        number = found.get("number", "")
        association = association or found.get("association", "")
        pr_body = pr_body or found.get("body", "")
    if host == "bitbucket" and not number:
        found = lookup_bitbucket_pr(
            os.environ.get("BITBUCKET_ACCESS_TOKEN", "").strip()
        )
        title = title or found.get("title", "")
        author = author or found.get("author", "")
        number = found.get("number", "")
        pr_body = pr_body or found.get("body", "")
    moment = detect_moment(
        os.environ.get("EVENT_NAME", ""),
        os.environ.get("PR_MERGED", ""),
        os.environ.get("REVIEW_STATE", ""),
    )
    if moment is None:
        print("skip: not a cheer moment")
        return 0
    if is_bot_author(author, os.environ.get("PR_AUTHOR_TYPE", "")):
        print("skip bot author")
        return 0
    if moment == "changes" and is_bot_author(
        os.environ.get("REVIEW_AUTHOR", ""),
        os.environ.get("REVIEW_AUTHOR_TYPE", ""),
    ):
        print("skip bot reviewer")
        return 0
    if host in {"gitlab", "bitbucket"} and not number:
        print("skip: no merged merge request")
        return 0
    if should_skip(title, labels):
        print("skip cheer requested")
        return 0
    existing = []
    if host == "github":
        existing = list_github_comments(token, repo, number)
    elif host == "gitlab":
        existing = list_gitlab_notes(
            (
                os.environ.get("GITLAB_TOKEN")
                or os.environ.get("CI_JOB_TOKEN")
                or ""
            ).strip(),
            os.environ.get("CI_PROJECT_ID", "").strip(),
            number,
        )
    elif host == "bitbucket":
        existing = list_bitbucket_comments(
            os.environ.get("BITBUCKET_ACCESS_TOKEN", "").strip(),
            os.environ.get("BITBUCKET_WORKSPACE", "").strip(),
            os.environ.get("BITBUCKET_REPO_SLUG", "").strip(),
            number,
        )
    if existing and already_cheered(existing):
        print("skip: already cheered")
        return 0
    topic = moment_topic(
        moment,
        topic,
        os.environ.get("CLOSED_TOPIC", ""),
        os.environ.get("CHANGES_TOPIC", ""),
    )
    message = moment_message(
        moment,
        os.environ.get("MESSAGE", ""),
        os.environ.get("CLOSED_MESSAGE", ""),
        os.environ.get("CHANGES_MESSAGE", ""),
    )
    commit_text = ""
    if host == "github":
        commit_text = "\n".join(list_pr_commit_messages(token, repo, number))
    logins = collect_authors(author, pr_body, commit_text)
    authors = format_authors(logins)
    group = resolve_group(title, topic, association, number, pr_body)
    if message_is_default(moment, message):
        hinted = ask_model(moment, title, pr_body, author, authors)
        if hinted:
            message = hinted
        else:
            message = localize_message(
                moment, message, os.environ.get("LOCALE", "")
            )
    root = action_root()
    group, name = choose_gif(root, group, number)
    gif = giphy_url(
        os.environ.get("GIPHY_API_KEY", "").strip(),
        GIPHY_TAG[group],
        os.environ.get("GIPHY_RATING", "g").strip() or "g",
    )
    if not gif:
        gif = bundled_url(
            os.environ.get("ACTION_REPO", "").strip(),
            os.environ.get("ACTION_REF", "main"),
            group,
            name,
        )
    label = LABEL[group]
    body = comment_body(message, author, label, gif, authors)
    write_output(
        os.environ.get("GITHUB_OUTPUT", ""),
        {
            "url": gif,
            "tag": label,
            "group": group,
            "body": body.replace("\n", "%0A"),
        },
    )
    if os.environ.get("DRY_RUN") == "1":
        print(body)
        return 0
    if host == "gitlab":
        post_gitlab_note(
            (
                os.environ.get("GITLAB_TOKEN")
                or os.environ.get("CI_JOB_TOKEN")
                or ""
            ).strip(),
            os.environ.get("CI_PROJECT_ID", "").strip(),
            number,
            body,
        )
        return 0
    if host == "bitbucket":
        post_bitbucket_comment(
            os.environ.get("BITBUCKET_ACCESS_TOKEN", "").strip(),
            os.environ.get("BITBUCKET_WORKSPACE", "").strip(),
            os.environ.get("BITBUCKET_REPO_SLUG", "").strip(),
            number,
            body,
        )
        return 0
    post_github_comment(
        os.environ.get("GITHUB_TOKEN", "").strip(),
        os.environ.get("GITHUB_REPOSITORY", "").strip(),
        number,
        body,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
