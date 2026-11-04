# Why Struggle Music website: notes for Claude

This is the live website for www.whystrugglemusic.com. Anything pushed to `main` is published within about two minutes, so check before pushing.

## Rules

- **British English only.** Colour, organise, centre, licence (noun), programme (TV or event), and so on. Run `python3 check_spelling.py`; the deploy is blocked if it finds American spellings.
- **Accessibility comes first.** Bradley and many visitors use screen readers. Keep one `h1` per page, real headings, a text alternative for every image (short alt text plus a full description where it helps), a `title` on every iframe, visible focus, and nothing that only works with a mouse or only by colour.
- **Correct spelling in text Bradley sends, but keep his wording and voice.** Tell him every change that goes beyond spelling.
- Write `[TO COME]` for text still to be written; the build lists every page that has one.

## How to work

- New to this project? `SETUP.md` explains how to install everything.
- Read `README.md` first: it says where every kind of content lives and how to add articles, news and artists.
- Before every push, run all three and make sure they pass:
  - `python3 check_spelling.py`
  - `python3 -m unittest`
  - `python3 build.py`
- Preview locally with `python3 -m http.server 8765 --directory _site`, then open http://localhost:8765.
- After pushing, check the run passed: `gh run list -L 1`.
- Never change the custom domain or Pages settings, and never touch the DNS, unless asked to.
