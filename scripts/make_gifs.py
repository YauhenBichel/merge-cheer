#!/usr/bin/env python3
"""Turn the owned stills into small looping GIFs for PR comments.

Layout is gifs/<group>/<name>.gif. A group may hold several files; the
Action picks one. Motion is a short brightness pulse plus a tiny zoom.
The `alt` file is the same still with the wave inverted — a cheap extra
option, not new art. Comic mood groups and IT-section groups each use
two original stills, except `java` which reuses one still as `steam`
and `comic` which adds an inverted `pop` as `alt`.
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
STILLS = ROOT / "stills"
GIFS = ROOT / "gifs"
MAX_BYTES = 180 * 1024
DURATION_MS = 110

# still stem, group, output stem, invert the pulse
VARIANTS = (
    ("ship-it", "ship", "ship-it", False),
    ("ship-it", "ship", "alt", True),
    ("ship-boost", "ship", "boost", False),
    ("nailed-it", "fix", "nailed-it", False),
    ("nailed-it", "fix", "alt", True),
    ("fix-spark", "fix", "spark", False),
    ("nice-work", "docs", "nice-work", False),
    ("nice-work", "docs", "alt", True),
    ("docs-glow", "docs", "glow", False),
    ("high-five", "tests", "high-five", False),
    ("high-five", "tests", "alt", True),
    ("cleanup", "cleanup", "cleanup", False),
    ("cleanup", "cleanup", "alt", True),
    ("cleanup-sweep", "cleanup", "sweep", False),
    ("celebration", "celebration", "celebration", False),
    ("celebration", "celebration", "alt", True),
    ("celebration-burst", "celebration", "burst", False),
    ("high-five", "welcome", "high-five", False),
    ("celebration", "welcome", "celebration", False),
    ("party-confetti", "party", "confetti", False),
    ("party-toast", "party", "toast", False),
    ("space-planet", "space", "planet", False),
    ("space-comet", "space", "comet", False),
    ("magic-wand", "magic", "wand", False),
    ("magic-sparkles", "magic", "sparkles", False),
    ("coffee-mug", "coffee", "mug", False),
    ("coffee-night", "coffee", "night", False),
    ("robot-wave", "robot", "wave", False),
    ("robot-dance", "robot", "dance", False),
    ("comic-burst", "comic", "burst", False),
    ("comic-pop", "comic", "pop", False),
    ("comic-pop", "comic", "alt", True),
    ("sunny-sun", "sunny", "sun", False),
    ("sunny-rainbow", "sunny", "rainbow", False),
    ("game-levelup", "game", "levelup", False),
    ("game-combo", "game", "combo", False),
    ("sticker-star", "sticker", "star", False),
    ("sticker-thumb", "sticker", "thumb", False),
    ("yeah-pump", "yeah", "pump", False),
    ("yeah-jump", "yeah", "jump", False),
    ("devops-loop", "devops", "loop", False),
    ("devops-pipeline", "devops", "pipeline", False),
    ("sre-lighthouse", "sre", "lighthouse", False),
    ("sre-pager", "sre", "pager", False),
    ("qa-lens", "qa", "lens", False),
    ("qa-pass", "qa", "pass", False),
    ("design-palette", "design", "palette", False),
    ("design-frames", "design", "frames", False),
    ("architecture-blocks", "architecture", "blocks", False),
    ("architecture-blueprint", "architecture", "blueprint", False),
    ("engineering-wrench", "engineering", "wrench", False),
    ("engineering-build", "engineering", "build", False),
    ("backend-db", "backend", "db", False),
    ("backend-server", "backend", "server", False),
    ("frontend-browser", "frontend", "browser", False),
    ("frontend-cursor", "frontend", "cursor", False),
    ("java-mug", "java", "mug", False),
    ("java-mug", "java", "steam", True),
    ("python-snake", "python", "snake", False),
    ("python-coil", "python", "coil", False),
    ("cpp-plus", "cpp", "plus", False),
    ("cpp-gear", "cpp", "gear", False),
    ("golang-gopher", "golang", "gopher", False),
    ("golang-wave", "golang", "wave", False),
)

# Drop frames, colors, then pixels if a still is too busy for 180 KB.
_PRESETS = (
    (6, 48, 280),
    (6, 40, 260),
    (5, 32, 240),
    (4, 28, 220),
    (4, 24, 200),
)


def _square(src: Path, size: int) -> Image.Image:
    image = Image.open(src).convert("RGB")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (size, size), (18, 20, 26))
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def _frame(
    base: Image.Image, index: int, frames: int, invert: bool, colors: int
) -> Image.Image:
    size = base.width
    wave = math.sin(2 * math.pi * index / frames)
    if invert:
        wave = -wave
    zoomed = 1.0 + (0.028 if invert else 0.018) * (0.5 + 0.5 * wave)
    crop = max(2, int(size * (1 - 1 / zoomed) / 2))
    frame = base.crop((crop, crop, size - crop, size - crop)).resize(
        (size, size), Image.Resampling.LANCZOS
    )
    bright = 1.0 + (0.06 if invert else 0.04) * wave
    frame = ImageEnhance.Brightness(frame).enhance(bright)
    return frame.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


def render(src: Path, dest: Path, invert: bool, frames: int, colors: int, size: int) -> None:
    base = _square(src, size)
    images = [_frame(base, index, frames, invert, colors) for index in range(frames)]
    dest.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        dest,
        save_all=True,
        append_images=images[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


def render_fitting(src: Path, dest: Path, invert: bool) -> int:
    last_size = 0
    for frames, colors, size in _PRESETS:
        render(src, dest, invert, frames, colors, size)
        last_size = dest.stat().st_size
        if last_size <= MAX_BYTES:
            return last_size
    return last_size


def main() -> int:
    needed = sorted({still for still, _, _, _ in VARIANTS})
    missing = [name for name in needed if not (STILLS / f"{name}.png").is_file()]
    if missing:
        print(f"missing stills: {', '.join(missing)}", file=sys.stderr)
        return 1
    for still, group, name, invert in VARIANTS:
        dest = GIFS / group / f"{name}.gif"
        size = render_fitting(STILLS / f"{still}.png", dest, invert)
        print(f"{group}/{dest.name} {size // 1024} KB")
        if size > MAX_BYTES:
            print(f"{group}/{dest.name} is over {MAX_BYTES // 1024} KB", file=sys.stderr)
            return 1
    wanted = {GIFS / group / f"{name}.gif" for _, group, name, _ in VARIANTS}
    for leftover in GIFS.rglob("*.gif"):
        if leftover not in wanted:
            leftover.unlink()
            print(f"removed leftover {leftover.relative_to(GIFS)}")
    for leftover in GIFS.glob("*.gif"):
        leftover.unlink()
        print(f"removed leftover {leftover.name}")
    for child in GIFS.iterdir():
        if child.is_dir() and not any(child.glob("*.gif")):
            shutil.rmtree(child)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
