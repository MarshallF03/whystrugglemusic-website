# Why Struggle Music website

Website for Why Struggle Music (WSM), run by Bradley McKnight. It will be published by GitHub Pages at www.whystrugglemusic.com. The domain isn't pointed here yet: see [GOING-LIVE.md](GOING-LIVE.md).

Accessibility comes first. Many of the people this site is for, Bradley included, use a screen reader. Every page must work with a keyboard and a screen reader before it goes up.

## How it works

- `build.py` turns `site.json` and the files in `content/` into a complete website in `_site/`.
- Anything pushed to the `main` branch is checked, built and published automatically by GitHub Actions, usually within two minutes. See the Actions tab for progress.
- If the spelling check or the tests fail, nothing is published.

To build and preview on your own computer:

```
pip install markdown
python3 build.py
python3 -m http.server 8765 --directory _site
```

Then open http://localhost:8765.

## British English only

All text on the site uses British English (colour, organise, centre, licence as a noun, catalogue, and so on). `check_spelling.py` checks for common American spellings and blocks the deploy if it finds any. Run it yourself with `python3 check_spelling.py`.

## Where things live

| What | Where |
|---|---|
| Home, About, Services, Records intro, Resources intro, Accessibility, Contact | `content/pages/*.md` |
| Email addresses, resource topics | `site.json` |
| An artist on the label | `content/roster/<name>.json` (details, songs, links) and `content/roster/<name>.md` (full bio) |
| Label news posts | `content/records-news/*.md` |
| Music business articles | `content/resources/*.md` |
| Pictures | `assets/images/` |

Write `[TO COME]` anywhere to mark text still to be written. It shows on the page as a yellow "To come:" label, and the build lists every page that still has one.

## Adding a music business article

Create a file in `content/resources/`, for example `2026-11-01-register-a-work-with-prs.md`:

```
---
title: How to register a work with PRS
date: 2026-11-01
category: pros
summary: A step by step guide to registering your songs with PRS for Music.
tags: PRS, songwriter royalties, registration
---
The article itself, in Markdown. Use ## for section headings.
```

`category` must be one of: `distribution`, `copyright`, `publishing`, `royalties`, `pros`, `social-media`, `youtube`. To add or rename a topic, edit `resource_categories` in `site.json`. Search looks at the title, summary, tags and topic, so add tags for words people might search for.

## Adding a label news post

Create a file in `content/records-news/`, for example `2026-11-14-new-single-from-huskinson.md`:

```
---
title: New single from Huskinson
date: 2026-11-14
artist: huskinson
---
The post, in Markdown.
```

`artist` is optional. When set, it must match an artist's file name (`bradley-mcknight`, `little-trees` or `huskinson`), and the post then appears on that artist's page too. Add `image:` and `image_alt:` for a picture.

## Adding an artist or a song

Copy one of the files in `content/roster/` and change the details. Each song needs `title`, `spotify_type` (`track` or `album`) and `spotify_id` (the code after `/track/` in the Spotify link). `apple`, `youtube`, `image` and `image_alt` are optional. Every picture needs `image_alt` describing it for screen reader users, unless it is purely decorative.

## Not built yet

Shop (planned for shop.whystrugglemusic.com), terms and conditions, licence agreements, and the WSM social media links.
