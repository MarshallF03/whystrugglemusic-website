#!/usr/bin/env python3
"""Build the Why Struggle Music website.

Reads site.json, the files under content/ and the files under assets/, and
writes a complete static website into _site/. There is no server-side code:
the result is plain HTML, CSS and one small script, hosted free on GitHub Pages.

Run it with:

    python3 build.py

Optionally pass --base /some/path when the site is served from a sub-folder
rather than the root of a domain (GitHub project pages do this).

Where things live:

    content/pages/*.md          Home, About, Services and the other fixed pages
    content/roster/<slug>.json  An artist's details, songs and links
    content/roster/<slug>.md    That artist's full bio
    content/records-news/*.md   Label news posts
    content/resources/*.md      Music business articles

Write [TO COME] anywhere in the text to mark something still to be written.
The build lists every page that still has one.
"""

import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path

PLACEHOLDER = "[TO COME]"

# ---------------------------------------------------------------------------
# Markdown. The "markdown" package gives the best result; if it is missing we
# fall back to a small converter that handles paragraphs, headings, lists,
# links, bold and italics, which is all the content on this site needs.
# ---------------------------------------------------------------------------
try:
    import markdown as _markdown

    def md(text: str) -> str:
        return _markdown.markdown(text)

except ImportError:  # pragma: no cover

    def _inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        return s

    def md(text: str) -> str:
        out = []
        for block in re.split(r"\n\s*\n", text.strip()):
            lines = block.strip().splitlines()
            if not lines:
                continue
            m = re.match(r"^(#{1,6})\s+(.*)$", lines[0])
            if m and len(lines) == 1:
                level = len(m.group(1))
                out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            elif all(re.match(r"^\s*[-*]\s+", l) for l in lines):
                items = "".join(f"<li>{_inline(re.sub(r'^\s*[-*]\s+', '', l))}</li>" for l in lines)
                out.append(f"<ul>{items}</ul>")
            else:
                out.append(f"<p>{_inline(' '.join(l.strip() for l in lines))}</p>")
        return "\n".join(out)


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


# ---------------------------------------------------------------------------
# Content loading
# ---------------------------------------------------------------------------
def load_entry(path: Path, *, dated: bool = True) -> dict:
    """Read a Markdown file with a simple front matter block.

    The block sits between two lines of three dashes and holds "key: value"
    lines. Everything after it is the body, in Markdown.
    """
    text = path.read_text(encoding="utf-8")
    meta: dict = {}
    body = text
    if text.lstrip().startswith("---"):
        parts = text.lstrip().split("---", 2)
        if len(parts) == 3:
            _, front, body = parts
            for line in front.strip().splitlines():
                if ":" in line and not line.lstrip().startswith("#"):
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
    meta["body"] = body.strip()
    meta["file"] = path.name
    if "title" not in meta:
        sys.exit(f"{path.name}: needs a 'title:' line in its front matter")
    # Slug: from the title, so the web address matches what people see.
    meta["slug"] = re.sub(r"[^a-z0-9]+", "-", meta["title"].lower()).strip("-")
    if dated:
        if "date" not in meta:
            sys.exit(f"{path.name}: needs a 'date:' line in its front matter")
        try:
            meta["date_obj"] = datetime.date.fromisoformat(meta["date"])
        except ValueError:
            sys.exit(f"{path.name}: the date must look like 2026-10-25, not {meta['date']!r}")
    return meta


def load_folder(folder: Path) -> list:
    if not folder.exists():
        return []
    return [load_entry(p) for p in sorted(folder.glob("*.md"))]


def load_roster(folder: Path) -> list:
    artists = []
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["slug"] = path.stem
        bio = path.with_suffix(".md")
        data["bio"] = bio.read_text(encoding="utf-8").strip() if bio.exists() else ""
        for key in ("members", "releases", "links"):
            data.setdefault(key, [])
        artists.append(data)
    return sorted(artists, key=lambda a: (a.get("order", 99), a["name"]))


def nice_date(d: datetime.date) -> str:
    """15 October 2026, with no leading zero on the day."""
    return f"{d.day} {d.strftime('%B %Y')}"


def excerpt(body: str) -> str:
    """The first paragraph of a Markdown body, as HTML."""
    first = re.split(r"\n\s*\n", body.strip())[0]
    return md(first)


def plain(html_text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html_text)).strip()


# ---------------------------------------------------------------------------
# HTML pieces
# ---------------------------------------------------------------------------
NAV = [
    ("Home", "/"),
    ("About", "/about/"),
    ("Services", "/services/"),
    ("Record label", "/records/"),
    ("Music business hub", "/resources/"),
    ("Accessibility", "/accessibility/"),
    ("Contact", "/contact/"),
]


class Site:
    def __init__(self, config: dict, base: str):
        self.c = config
        self.base = base.rstrip("/")
        self.placeholders: list = []
        self.categories = {c["slug"]: c["name"] for c in config.get("resource_categories", [])}

    def text(self, markdown_text: str, page: str) -> str:
        """Markdown to HTML, marking and recording any [TO COME] placeholders."""
        if PLACEHOLDER in markdown_text and page not in self.placeholders:
            self.placeholders.append(page)
        out = md(markdown_text)
        return out.replace(PLACEHOLDER, '<span class="placeholder">To come:</span>')

    def rebase(self, page: str) -> str:
        """Point every site-relative link at the base path (for sub-folder hosting)."""
        if not self.base:
            return page
        return re.sub(r'((?:href|src|action)=")/(?!/)', rf"\1{self.base}/", page)

    def layout(self, *, title: str, path: str, body: str, description: str | None = None,
               lead: str | None = None, image: str | None = None) -> str:
        site_title = self.c["title"]
        full_title = site_title if path == "/" else f"{title} - {site_title}"
        desc = esc(description or self.c["description"])
        nav_items = []
        for label, href in NAV:
            current = ' aria-current="page"' if href == path or (href != "/" and path.startswith(href)) else ""
            nav_items.append(f'<li><a href="{href}"{current}>{label}</a></li>')
        lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
        site_url = self.c.get("site_url", "").rstrip("/")
        page_url = f"{site_url}{path}" if site_url else ""
        img = image or self.c["share_image"]
        og_image = f'<meta property="og:image" content="{site_url}{img}">' if site_url else ""
        logo = self.c["logo"]
        year = datetime.date.today().year
        email = esc(self.c["footer_email"])
        return self.rebase(f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="description" content="{desc}">
  <title>{esc(full_title)}</title>
  <link rel="canonical" href="{page_url}">
  <meta property="og:site_name" content="{esc(site_title)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(full_title)}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{page_url}">
  {og_image}
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png">
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <p class="site-name"><a href="/"><img src="{logo['src']}" alt="{esc(logo['alt'])}" width="264" height="100"></a></p>
    <nav aria-label="Main">
      <ul>
        {''.join(nav_items)}
      </ul>
    </nav>
  </header>
  <main id="main" tabindex="-1">
    <h1>{esc(title)}</h1>
    {lead_html}
    {body}
  </main>
  <footer class="site-footer">
    <p>Get in touch: <a href="mailto:{email}">{email}</a></p>
    <p>&copy; {year} {esc(site_title)}.</p>
  </footer>
  <script src="/assets/site.js" defer></script>
</body>
</html>
""")

    # -- Players and links ----------------------------------------------------
    def spotify_embed(self, kind: str, spotify_id: str, title: str, artist: str) -> str:
        label = esc(f"Spotify player: {title} by {artist}")
        src = f"https://open.spotify.com/embed/{kind}/{spotify_id}?theme=0"
        link = f"https://open.spotify.com/{kind}/{spotify_id}"
        height = 352 if kind == "album" else 152
        return (
            f'<div class="embed">'
            f'<iframe title="{label}" src="{src}" width="100%" height="{height}" '
            f'allow="encrypted-media; clipboard-write; fullscreen; picture-in-picture" loading="lazy"></iframe>'
            f'<p class="embed-fallback"><a href="{link}">Listen to {esc(title)} on Spotify</a></p>'
            f'</div>'
        )

    @staticmethod
    def link_list(links: list, about: str = "") -> str:
        items = []
        for l in links:
            label = esc(l["name"])
            if about:
                label += f'<span class="visually-hidden"> for {esc(about)}</span>'
            if l.get("handle"):
                label += f' <span class="handle">({esc(l["handle"])})</span>'
            items.append(f'<li><a href="{esc(l["url"])}">{label}</a></li>')
        return f'<ul class="inline">{"".join(items)}</ul>' if items else ""

    @staticmethod
    def describe(description: str, about: str) -> str:
        """A full picture description, closed until someone opens it.

        The image's alt text stays short so screen reader users are not made to
        sit through a paragraph every time; the detail is here for anyone who wants it.
        """
        if not description:
            return ""
        return (f'<details class="image-description"><summary>Full picture description'
                f'<span class="visually-hidden">: {esc(about)}</span></summary>'
                f'<p>{esc(description)}</p></details>')

    @classmethod
    def figure(cls, src: str, alt: str, css: str, caption: str = "", description: str = "", about: str = "") -> str:
        if not src:
            return ""
        cap = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
        return (f'<figure class="{css}"><img src="{src}" alt="{esc(alt)}" loading="lazy">{cap}'
                f'{cls.describe(description, about)}</figure>')

    # -- Roster -----------------------------------------------------------
    def roster_list(self, artists: list, heading_level: int = 3) -> str:
        h = f"h{heading_level}"
        items = []
        for a in artists:
            href = f"/records/{a['slug']}/"
            items.append(
                f'<li class="card">'
                f'{self.figure(a.get("image", ""), "", "card-image")}'
                f'<{h}><a href="{href}">{esc(a["name"])}</a></{h}>'
                f'<p>{esc(a.get("summary", ""))}</p>'
                f'</li>'
            )
        return f'<ul class="cards">{"".join(items)}</ul>'

    def artist_page(self, a: dict, posts: list) -> str:
        name = a["name"]
        parts = [self.figure(a.get("image", ""), a.get("image_alt", ""), "artist-photo",
                             description=a.get("image_description", ""), about=f"photo of {name}")]
        parts.append(f'<section aria-labelledby="bio-heading"><h2 id="bio-heading">About {esc(name)}</h2>'
                     f'{self.text(a["bio"], a["slug"])}')
        if a["members"]:
            members = "".join(f'<li><strong>{esc(m["name"])}</strong>, {esc(m["role"])}</li>' for m in a["members"])
            parts.append(f"<h3>Line-up</h3><ul>{members}</ul>")
        parts.append("</section>")
        if a["releases"]:
            rel = []
            for r in a["releases"]:
                rid = f"song-{re.sub(r'[^a-z0-9]+', '-', r['title'].lower()).strip('-')}"
                extra = []
                if r.get("apple"):
                    extra.append(f'<a href="{esc(r["apple"])}">{esc(r["title"])} on Apple Music</a>')
                if r.get("youtube"):
                    extra.append(f'<a href="{esc(r["youtube"])}">{esc(r["title"])} on YouTube</a>')
                extra_html = f'<p>{" &middot; ".join(extra)}</p>' if extra else ""
                rel.append(
                    f'<li class="release" aria-labelledby="{rid}">'
                    f'{self.figure(r.get("image", ""), r.get("image_alt", ""), "artwork")}'
                    f'<div><h3 id="{rid}">{esc(r["title"])}</h3>'
                    f'{self.describe(r.get("image_description", ""), r["title"] + " artwork")}'
                    f'{self.spotify_embed(r["spotify_type"], r["spotify_id"], r["title"], name) if r.get("spotify_id") else ""}'
                    f'{extra_html}</div></li>'
                )
            parts.append(f'<section aria-labelledby="listen-heading"><h2 id="listen-heading">Listen</h2>'
                         f'<ul class="releases">{"".join(rel)}</ul></section>')
        if a["links"]:
            parts.append(f'<section aria-labelledby="links-heading"><h2 id="links-heading">Find {esc(name)} online</h2>'
                         f'{self.link_list(a["links"])}</section>')
        own = [p for p in posts if p.get("artist") == a["slug"]]
        if own:
            parts.append(f'<section aria-labelledby="news-heading"><h2 id="news-heading">News</h2>'
                         f'{self.news_list(own)}</section>')
        parts.append('<p><a href="/records/">Back to Why Struggle Records</a></p>')
        return "\n".join(parts)

    # -- Label news -------------------------------------------------------
    def news_list(self, posts: list, heading_level: int = 3, limit: int | None = None) -> str:
        posts = sorted(posts, key=lambda p: p["date_obj"], reverse=True)[:limit]
        h = f"h{heading_level}"
        items = [
            f'<li class="post"><{h}><a href="/records/news/{p["slug"]}/">{esc(p["title"])}</a></{h}>'
            f'<p><time datetime="{p["date_obj"].isoformat()}">{nice_date(p["date_obj"])}</time></p>'
            f'{excerpt(p["body"])}</li>'
            for p in posts
        ]
        return f'<ul class="posts">{"".join(items)}</ul>' if items else "<p>No label news yet.</p>"

    # -- Resources hub ----------------------------------------------------
    def article_item(self, a: dict, heading_level: int = 2) -> str:
        h = f"h{heading_level}"
        cat = self.categories[a["category"]]
        search = " ".join([a["title"], a.get("summary", ""), a.get("tags", ""), cat]).lower()
        return (
            f'<li class="article" data-category="{esc(a["category"])}" data-search="{esc(search)}">'
            f'<{h}><a href="/resources/{a["slug"]}/">{esc(a["title"])}</a></{h}>'
            f'<p class="meta">{esc(cat)} &middot; '
            f'<time datetime="{a["date_obj"].isoformat()}">{nice_date(a["date_obj"])}</time></p>'
            f'<p>{esc(a.get("summary", ""))}</p></li>'
        )

    def resources_hub(self, articles: list) -> str:
        options = "".join(f'<option value="{esc(slug)}">{esc(name)}</option>' for slug, name in self.categories.items())
        items = "".join(self.article_item(a) for a in articles)
        empty = "" if articles else '<p class="empty-state">Articles are on the way. Check back soon.</p>'
        return f"""<form class="search" role="search" aria-labelledby="search-heading" action="/resources/" method="get">
  <h2 id="search-heading">Find a guide</h2>
  <div class="field">
    <label for="q">Search by keyword</label>
    <input type="search" id="q" name="q" autocomplete="off" aria-describedby="q-hint">
    <p class="hint" id="q-hint">Results update as you type.</p>
  </div>
  <div class="field">
    <label for="category">Topic</label>
    <select id="category" name="category"><option value="">All topics</option>{options}</select>
  </div>
  <p><button type="submit" class="button">Search</button></p>
</form>
<h2 id="articles-heading">Guides</h2>
<p id="results-status" class="status" role="status" aria-live="polite"></p>
{empty}
<ul class="articles" id="articles" aria-labelledby="articles-heading"{' hidden' if not articles else ''}>{items}</ul>"""

    def article_page(self, a: dict) -> str:
        cat = self.categories[a["category"]]
        tags = [t.strip() for t in a.get("tags", "").split(",") if t.strip()]
        tags_html = f'<p class="meta">Tags: {esc(", ".join(tags))}</p>' if tags else ""
        return (
            f'<p class="meta">Topic: <a href="/resources/?category={esc(a["category"])}">{esc(cat)}</a> &middot; '
            f'<time datetime="{a["date_obj"].isoformat()}">{nice_date(a["date_obj"])}</time></p>'
            f'{self.text(a["body"], "resources/" + a["slug"])}'
            f'{tags_html}'
            f'<p><a href="/resources/?category={esc(a["category"])}">More guides on the topic {esc(cat)}</a></p>'
            f'<p><a href="/resources/">Back to all guides</a></p>'
        )

    # -- Contact ----------------------------------------------------------
    def email_list(self) -> str:
        items = "".join(
            f'<li><h2>{esc(e["purpose"])}</h2><p><a href="mailto:{esc(e["address"])}">{esc(e["address"])}</a></p></li>'
            for e in self.c.get("emails", [])
        )
        return f'<ul class="emails">{items}</ul>'


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def write(out: Path, path: str, content: str) -> None:
    target = out / path.strip("/") / "index.html" if not path.endswith(".html") else out / path.strip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build(root: Path, out: Path, base: str = "") -> dict:
    content = root / "content"
    config = json.loads((root / "site.json").read_text(encoding="utf-8"))
    site = Site(config, base)
    pages = {p.stem: load_entry(p, dated=False) for p in sorted((content / "pages").glob("*.md"))}
    artists = load_roster(content / "roster")
    posts = load_folder(content / "records-news")
    articles = sorted(load_folder(content / "resources"), key=lambda a: a["date_obj"], reverse=True)
    for a in articles:
        if a.get("category") not in site.categories:
            sys.exit(f"{a['file']}: 'category:' must be one of {', '.join(site.categories)} "
                     f"(see resource_categories in site.json), not {a.get('category')!r}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(root / "assets", out / "assets")
    (out / ".nojekyll").write_text("")

    def page(key: str, path: str, body_after: str = "", body_before: str = "") -> None:
        p = pages[key]
        body = body_before + site.text(p["body"], key) + body_after
        write(out, path, site.layout(title=p["title"], path=path, body=body, lead=p.get("lead")))

    # Home ------------------------------------------------------------------
    home_extra = f"""
<section aria-labelledby="artists-heading">
  <h2 id="artists-heading">Our artists</h2>
  {site.roster_list(artists)}
  <p><a href="/records/">More about Why Struggle Records</a></p>
</section>"""
    if posts:
        home_extra += f"""
<section aria-labelledby="home-news-heading">
  <h2 id="home-news-heading">Latest from the label</h2>
  {site.news_list(posts, limit=3)}
</section>"""
    if articles:
        home_extra += f"""
<section aria-labelledby="home-guides-heading">
  <h2 id="home-guides-heading">Latest guides</h2>
  <ul class="articles">{''.join(site.article_item(a, 3) for a in articles[:3])}</ul>
  <p><a href="/resources/">All music business guides</a></p>
</section>"""
    page("home", "/", home_extra)

    # Simple pages ----------------------------------------------------------
    page("about", "/about/")
    page("services", "/services/")
    page("accessibility", "/accessibility/")
    page("contact", "/contact/", site.email_list())

    # Records ---------------------------------------------------------------
    page("records", "/records/", f"""
<section aria-labelledby="roster-heading">
  <h2 id="roster-heading">Our artists</h2>
  {site.roster_list(artists)}
</section>
<section aria-labelledby="label-news-heading">
  <h2 id="label-news-heading">Label news</h2>
  {site.news_list(posts)}
</section>""")
    for a in artists:
        write(out, f"/records/{a['slug']}/", site.layout(
            title=a["name"], path="/records/", body=site.artist_page(a, posts),
            description=a.get("summary"), lead=a.get("summary"), image=a.get("image")))
    for p in posts:
        artist = next((a for a in artists if a["slug"] == p.get("artist")), None)
        back = f'<p><a href="/records/{artist["slug"]}/">More about {esc(artist["name"])}</a></p>' if artist else ""
        body = (f'<p><time datetime="{p["date_obj"].isoformat()}">{nice_date(p["date_obj"])}</time></p>'
                f'{site.figure(p.get("image", ""), p.get("image_alt", ""), "post-photo", description=p.get("image_description", ""), about=p["title"])}'
                f'{site.text(p["body"], "records/news/" + p["slug"])}{back}'
                f'<p><a href="/records/">Back to Why Struggle Records</a></p>')
        write(out, f"/records/news/{p['slug']}/", site.layout(
            title=p["title"], path="/records/", body=body, description=plain(excerpt(p["body"]))[:160]))

    # Resources -------------------------------------------------------------
    page("resources", "/resources/", site.resources_hub(articles))
    for a in articles:
        write(out, f"/resources/{a['slug']}/", site.layout(
            title=a["title"], path="/resources/", body=site.article_page(a),
            description=a.get("summary"), lead=a.get("summary")))

    # 404 ---------------------------------------------------------------------
    write(out, "/404.html", site.layout(title="Page not found", path="/404/",
                                        body='<p>That page does not exist. Try the <a href="/">home page</a>.</p>'))

    return {
        "pages": sum(1 for _ in out.rglob("index.html")),
        "artists": len(artists),
        "posts": len(posts),
        "articles": len(articles),
        "placeholders": site.placeholders,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    base = args[args.index("--base") + 1] if "--base" in args else ""
    root = Path(__file__).resolve().parent
    result = build(root, root / "_site", base)
    print(f"built {result['pages']} pages into _site/ ({result['artists']} artists, "
          f"{result['posts']} label news posts, {result['articles']} articles)")
    if result["placeholders"]:
        print("still to write ([TO COME]): " + ", ".join(result["placeholders"]))
