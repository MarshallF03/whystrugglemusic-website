"""Tests for build.py and check_spelling.py. Run with: python3 -m unittest -v"""

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import check_spelling  # noqa: E402


def make_project(articles: dict | None = None, extra_artist: dict | None = None) -> Path:
    """Copy the real project into a temp folder, optionally adding fixture content."""
    tmp = Path(tempfile.mkdtemp())
    for name in ("site.json", "content", "assets"):
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, tmp / name)
        else:
            shutil.copy(src, tmp / name)
    # Tests use their own articles only, not whatever is on the site right now.
    for existing in (tmp / "content" / "resources").glob("*.md"):
        existing.unlink()
    for filename, text in (articles or {}).items():
        (tmp / "content" / "resources" / filename).write_text(text, encoding="utf-8")
    if extra_artist:
        slug = extra_artist["slug"]
        data = {k: v for k, v in extra_artist.items() if k != "slug"}
        (tmp / "content" / "roster" / f"{slug}.json").write_text(json.dumps(data), encoding="utf-8")
        (tmp / "content" / "roster" / f"{slug}.md").write_text("A test bio.", encoding="utf-8")
    return tmp


def read(out: Path, path: str) -> str:
    return (out / path.strip("/") / "index.html").read_text(encoding="utf-8")


ARTICLE_A = """---
title: How to register a work with PRS
date: 2026-10-01
category: pros
summary: A step by step guide to registering your songs with PRS for Music.
tags: PRS, songwriter royalties, registration
---
Body text about PRS.
"""

ARTICLE_B = """---
title: Choosing a distributor
date: 2026-10-02
category: distribution
summary: What to look for when picking a digital distributor.
tags: DistroKid, streaming
---
Body text about distribution.
"""


class BuildTests(unittest.TestCase):
    def build(self, **kwargs):
        root = make_project(**kwargs)
        self.addCleanup(shutil.rmtree, root)
        out = root / "_site"
        result = build.build(root, out)
        return out, result

    def test_every_page_is_accessible_shell(self):
        out, _ = self.build(articles={"2026-10-01-prs.md": ARTICLE_A})
        pages = list(out.rglob("index.html")) + [out / "404.html"]
        self.assertGreater(len(pages), 8)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=str(page.relative_to(out))):
                self.assertIn('<html lang="en-GB">', text)
                self.assertEqual(len(re.findall(r"<h1[ >]", text)), 1)
                self.assertIn('href="#main"', text)
                self.assertIn('<nav aria-label="Main">', text)
                for img in re.findall(r"<img [^>]*>", text):
                    self.assertIn("alt=", img)
                for frame in re.findall(r"<iframe [^>]*>", text):
                    self.assertIn("title=", frame)

    def test_shop_not_in_navigation(self):
        out, _ = self.build()
        nav = re.search(r'<nav aria-label="Main">.*?</nav>', read(out, "/"), re.S).group(0)
        self.assertNotIn("Shop", nav)
        self.assertIn('aria-current="page"', nav)

    def test_placeholders_reported(self):
        _, result = self.build()
        self.assertIn("records", result["placeholders"])

    def test_roster_headings_link_to_artist_pages(self):
        out, _ = self.build()
        page = read(out, "/records/").split('id="roster-heading"')[1]
        names = re.findall(r'<h3><a href="/records/([a-z-]+)/">([^<]+)</a></h3>', page)
        self.assertEqual([n[0] for n in names], ["bradley-mcknight", "little-trees", "huskinson"])
        self.assertEqual(names[2][1], "Huskinson")

    def test_artist_page_has_players(self):
        out, _ = self.build()
        page = read(out, "/records/bradley-mcknight/")
        titles = re.findall(r'<iframe title="([^"]+)"', page)
        self.assertEqual(titles, [
            "Spotify player: Rising Up by Bradley McKnight",
            "Spotify player: Met You In The Dark by Bradley McKnight",
            "Spotify player: All I Need by Bradley McKnight",
        ])
        self.assertIn('href="https://open.spotify.com/track/4cak5oHY8c7UIqo0n6DcAa"', page)

    def test_full_picture_descriptions(self):
        out, _ = self.build()
        page = read(out, "/records/bradley-mcknight/")
        self.assertIn('<details class="image-description"><summary>Full picture description'
                      '<span class="visually-hidden">: photo of Bradley McKnight</span></summary>', page)
        self.assertIn("Full picture description<span class=\"visually-hidden\">: Rising Up artwork</span>", page)
        self.assertEqual(page.count('<details class="image-description">'), 4)

    def test_upcoming_release_countdown_and_tracklist(self):
        import datetime
        future = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        out, _ = self.build(extra_artist={
            "slug": "test-act", "name": "Test Act", "order": 9, "summary": "A test act.",
            "upcoming": {"title": "Debut", "type": "EP", "date": future, "tracks": ["One", "Two"],
                         "preorder": [{"name": "Apple Music", "url": "https://example.com/pre"}]},
        })
        page = read(out, "/records/test-act/")
        self.assertIn('<h2 id="upcoming-heading">Coming soon: Debut EP</h2>', page)
        self.assertIn(f'data-countdown="{future}">That is 10 days from now.</p>', page)
        self.assertIn("<ol><li>One</li><li>Two</li></ol>", page)
        self.assertIn(">Pre-order Debut EP on Apple Music</a>", page)
        self.assertIn('<a href="/records/test-act/">Test Act: Debut EP</a>', read(out, "/records/"))
        self.assertIn('<a href="/records/test-act/">Test Act: Debut EP</a>', read(out, "/"))

    def test_past_upcoming_release_is_dropped(self):
        out, _ = self.build(extra_artist={
            "slug": "test-act", "name": "Test Act", "order": 9, "summary": "A test act.",
            "upcoming": {"title": "Old", "type": "EP", "date": "2020-01-01"},
        })
        self.assertNotIn("Coming soon: Old", read(out, "/records/test-act/"))

    def test_previous_releases_table(self):
        out, _ = self.build()
        page = read(out, "/records/little-trees/")
        self.assertIn('<h2 id="previous-heading">Previously released</h2>', page)
        rows = re.findall(r'<tr><th scope="row">([^<]+)', page)
        self.assertEqual(rows, ["So Now You Want Me", "Stronger"])
        self.assertIn('<time datetime="2026-08-28">28 August 2026</time>', page)
        self.assertIn("Dean Jackson the first time it was submitted", page)

    def test_accessibility_page_renamed(self):
        out, _ = self.build()
        self.assertIn("<h1>Developing accessibility in music</h1>", read(out, "/accessibility/"))
        self.assertIn('<a href="/accessibility/">Developing accessibility in music</a>', read(out, "/"))

    def test_accessibility_products_marked_coming_soon(self):
        out, _ = self.build()
        page = read(out, "/accessibility/")
        self.assertIn("<h2>Coming soon: presets and templates</h2>", page)
        self.assertIn("nothing below is available to download", page)
        self.assertIn("We are not affiliated with Spectre Digital.", page)

    def test_missing_optional_links(self):
        out, _ = self.build(extra_artist={
            "slug": "test-act", "name": "Test Act", "order": 9, "summary": "A test act.",
            "image": "", "image_alt": "", "releases": [],
        })
        self.assertIn("Test Act", read(out, "/records/test-act/"))

    def test_hub_empty_state(self):
        out, _ = self.build()
        page = read(out, "/resources/")
        self.assertIn("Articles are on the way", page)
        self.assertIn('<label for="category">', page)
        self.assertIn('<select id="category" name="category">', page)
        self.assertIn('role="search"', page)

    def test_articles_listed_and_indexed(self):
        out, _ = self.build(articles={"2026-10-01-prs.md": ARTICLE_A, "2026-10-02-distributor.md": ARTICLE_B})
        page = read(out, "/resources/")
        self.assertIn('href="/resources/how-to-register-a-work-with-prs/"', page)
        item = re.search(r'<li class="article"[^>]*data-category="pros"[^>]*>', page)
        self.assertIsNotNone(item)
        self.assertIn("songwriter royalties", item.group(0))
        self.assertIn("prs for music", item.group(0))
        self.assertIn("Body text about PRS.", read(out, "/resources/how-to-register-a-work-with-prs/"))

    def test_unknown_category_fails(self):
        bad = ARTICLE_A.replace("category: pros", "category: nonsense")
        with self.assertRaises(SystemExit) as ctx:
            self.build(articles={"2026-10-01-bad.md": bad})
        self.assertIn("2026-10-01-bad.md", str(ctx.exception))


class SpellingTests(unittest.TestCase):
    def test_spelling_flags_american(self):
        found = check_spelling.check_text("The color center")
        self.assertEqual(found, [("color", "colour"), ("center", "centre")])

    def test_spelling_accepts_british(self):
        self.assertEqual(check_spelling.check_text("The colour centre, organised and recognised."), [])

    def test_spelling_ignores_urls(self):
        self.assertEqual(check_spelling.check_text("See https://example.com/color-center for more."), [])

    def test_project_content_is_british(self):
        self.assertEqual(check_spelling.check_project(ROOT), [])


if __name__ == "__main__":
    unittest.main()
