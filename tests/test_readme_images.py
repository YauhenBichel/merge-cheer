"""Every picture the README points at has to exist and be renderable.

The README is the shop window twice over: GitHub shows it on the repository
page, and the Marketplace listing renders the same file.

The hero was `![Merge Cheer demo](docs/merge-cheer-demo.mp4)`. The file was
there, so nothing that only checks for missing files would have caught it, but
markdown turns `![...]()` into an `<img>` and an MP4 in an `<img>` never plays.
Visitors got a broken-image icon above the fold, with a caption describing
something they could not see. GitHub's sanitiser strips `<video>` outright, so
a still linked to the site demo is the only thing that works here.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_HTML_SRC = re.compile(r'src="([^"]+)"')
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

# What a browser will actually draw inside an <img>.
RENDERABLE = {".png", ".gif", ".jpg", ".jpeg", ".svg", ".webp", ".avif"}


def _local_images(text: str) -> list[str]:
    found = _HTML_SRC.findall(text) + _MD_IMAGE.findall(text)
    return [
        p
        for p in found
        if not p.startswith(("http://", "https://", "data:", "#", "mailto:"))
    ]


class ReadmeImagesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = (ROOT / "README.md").read_text()
        self.images = _local_images(self.readme)

    def test_the_readme_actually_references_images(self) -> None:
        """Guard against the checks below passing because nothing matched."""
        self.assertGreater(len(self.images), 0)

    def test_every_local_image_exists(self) -> None:
        missing = [p for p in self.images if not (ROOT / p).exists()]
        self.assertEqual(missing, [], f"README points at files that do not exist: {missing}")

    def test_every_local_image_is_something_a_browser_can_draw(self) -> None:
        unrenderable = [p for p in self.images if Path(p).suffix.lower() not in RENDERABLE]
        self.assertEqual(
            unrenderable,
            [],
            "these are in an image position but a browser cannot draw them; "
            f"link a still to the video instead: {unrenderable}",
        )

    def test_no_video_element_which_github_strips(self) -> None:
        self.assertNotIn("<video", self.readme.lower())


if __name__ == "__main__":
    unittest.main()
