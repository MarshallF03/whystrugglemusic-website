# Why Struggle Music website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the WSM site from the structure sheet: label and roster, a searchable resources hub, an accessibility page, and placeholder pages for copy that hasn't arrived yet.

**Architecture:** `build.py` reads `site.json`, `content/` (Markdown with `key: value` front matter, plus one JSON file per artist) and `assets/`, and writes static HTML into `_site/`. One small script (`assets/site.js`) adds search and filtering on top of a list that works without it. GitHub Actions runs the spelling check and tests, builds, and deploys to Pages.

**Tech Stack:** Python 3.12 with `markdown`; `unittest`; plain HTML, CSS and JavaScript; GitHub Actions and Pages.

**Spec:** `docs/superpowers/specs/2026-10-29-wsm-website-design.md`

## Global Constraints

- `<html lang="en-GB">` on every page; British English in all copy, enforced by `check_spelling.py`.
- Every page: a skip link to `#main`, exactly one `<h1>`, `<nav aria-label="Main">`, `aria-current="page"` on the current section.
- Every `<img>` has an `alt` attribute; every `<iframe>` has a `title` and a text link fallback straight after it.
- No colour-only meaning, no hover-only controls, no autoplay. Focus is always visible.
- Shop, terms and licences stay out of the navigation.

## Review Focus

- Search with no matches: the live region says "No articles match", and the empty list is hidden rather than left as an empty `<ul>`.
- Search with odd input (capitals, extra spaces, an apostrophe as in "PRS's"): matching ignores case and trims whitespace; the query is never inserted as HTML.
- No articles at all (the state at launch): the hub page builds, with a friendly "Articles are on the way" message and the filters still labelled.
- An artist JSON file missing an optional link (no TikTok, no website): the page builds and simply leaves that link out.
- A `?category=` value that doesn't exist: it's ignored and all articles are shown.

---

### Task 1: Build engine, layout and shared pages

**Files:** Create `build.py`, `site.json`, `assets/site.css`, `assets/favicon.svg`, `content/pages/{home,about,services,accessibility,contact}.md`, `tests/test_build.py`. Remove the old static `index.html`.

**Interfaces:**
- Produces: `build(root: Path, out: Path, base: str = "") -> dict` (returns counts); `load_entry(path) -> dict`; `Site.layout(title, path, body, description=None, lead=None) -> str`; `Site.spotify_embed(kind, id, title, artist) -> str`.

- [ ] Test `test_every_page_is_accessible_shell`: for every `index.html` under the built output: `lang="en-GB"`, one `<h1`, `href="#main"` skip link, every `<img` has `alt=`, every `<iframe` has `title=`.
- [ ] Test `test_placeholders_reported`: build output counts include `placeholders` listing `about` while `[TO COME]` is present.
- [ ] Implement, then run `python3 -m unittest -v`. Expected: PASS.
- [ ] Commit.

### Task 2: Records, roster and artist pages

**Files:** Create `content/roster/{bradley-mcknight,little-trees,huskinson}.json` and `.md` (bio), `content/records-news/` (empty, with `.gitkeep`), `assets/images/*`.

Artist JSON keys: `name, order, summary, image, image_alt, members[], releases[{title, spotify_type, spotify_id, apple?, youtube?}], links[{name, url, handle?}]`.

- [ ] Test `test_roster_headings_link_to_artist_pages`: `/records/` has `<h3><a href=".../records/huskinson/">Huskinson</a></h3>` for each artist, ordered by `order`.
- [ ] Test `test_artist_page_has_players`: `/records/bradley-mcknight/` has 3 iframes titled `Spotify player: <song> by Bradley McKnight`, and `open.spotify.com/track/4cak5oHY8c7UIqo0n6DcAa` as a link.
- [ ] Test `test_missing_optional_links`: an artist fixture with no `links` builds.
- [ ] Implement; run the tests; commit.

### Task 3: Resources hub with search and filters

**Files:** Create `content/resources/` (`.gitkeep`), `assets/site.js`; modify `build.py`.

Article front matter: `title, date, category, summary, tags` (tags comma-separated). `category` must be one of `site.json` `resource_categories[].slug`; otherwise the build stops with a clear message.

- [ ] Test `test_hub_empty_state`: no articles → page contains "Articles are on the way" and a labelled `<select id="category">`.
- [ ] Test `test_articles_listed_and_indexed`: two fixture articles → each has a page at `/resources/<slug>/` and a list item with `data-category`, `data-search` (lowercased title, summary, tags and category name).
- [ ] Test `test_unknown_category_fails`: a bad category raises `SystemExit` naming the file.
- [ ] JS (checked in the browser): typing filters as you type (300 ms debounce); the live region says "Showing N of M articles" or "No articles match …"; `?q=` and `?category=` are applied on load; a bad category is ignored.
- [ ] Implement; run the tests; commit.

### Task 4: Spelling lock, deploy workflow, docs

**Files:** Create `check_spelling.py`, `.github/workflows/pages.yml`; update `README.md`, `.gitignore` (`_site/`).

- [ ] Test `test_spelling_flags_american`: `check_text("The color center")` returns `color` and `center` with their British replacements; `check_text("colour centre")` returns nothing.
- [ ] Workflow: checkout → Python 3.12 → `pip install markdown` → `python check_spelling.py` → `python -m unittest` → `python build.py --base` → upload → deploy.
- [ ] Switch Pages to `build_type=workflow` with `gh api`.
- [ ] Push; check the Actions run went green and the github.io URL serves the build.
