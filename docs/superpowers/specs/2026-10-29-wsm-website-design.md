# Why Struggle Music website: design

## Intent

Why Struggle Music (WSM) is Bradley McKnight's music business: a record label (Why Struggle Records), a hub of plain-English articles about the music business, and support for blind and visually impaired (BVI) musicians. Bradley is totally blind, and so are many of the people the site is for. **Accessibility comes first**: if a feature can't be made to work well with a screen reader and a keyboard, it doesn't ship.

Source: Bradley's structure sheet (kept outside the repo) and Marshall's brief of 29 October 2026.

## Goals

- Pages from the structure sheet: Home, About, Services, Why Struggle Records (label, roster, label news), Music business resources hub, Improving accessibility in music, Contact.
- Each roster artist has their own page. The Records page lists them with a heading that links to that page and a short description below it.
- Embedded Spotify players for each artist's chosen songs, each with a text link fallback.
- The resources hub has keyword search and category filtering, and works with a screen reader.
- Label news posts on the Records page and on each artist's page.
- All copy is British English, enforced by an automated check that runs before every deploy.

## Non-goals (for now)

- Shop, terms and conditions, and licence agreements. They aren't ready, so they don't go in the navigation yet.
- Real articles. The hub ships empty and Marshall adds test articles later.
- About and Services copy. The text is arriving this evening, so these pages get clearly marked placeholders.
- Going live. DNS stays pointed at Fasthosts until Marshall says otherwise.

## Anti-goals

- Anything that only works with a mouse or with sight: hover-only menus, colour-only meaning, unlabelled players, carousels, autoplay.
- A content system Bradley or Marshall can't maintain by editing a text file.

## Constraints

- Free hosting on GitHub Pages from the public repo MarshallF03/whystrugglemusic-website.
- Built the same way as littletreesnotts.com (Marshall's band site): `build.py` turns `site.json` and Markdown in `content/` into static HTML in `_site/`, and GitHub Actions deploys it. No server-side code.
- The page language is `en-GB`.

## Decided content

| Artist | Songs (Spotify track IDs) | Links |
|---|---|---|
| Bradley McKnight | Rising Up `4cak5oHY8c7UIqo0n6DcAa`, Met You In The Dark `4Hj7aTGWGzqK2sNqyQVe3K`, All I Need `1dcourmGXrHxkwAq3L3de8` | Spotify artist `23a1ZUG3LCo13NavR0404J`, Apple Music, YouTube @BradleyMcknight, Instagram, Facebook, TikTok (bradleymcknightofficial) |
| Little Trees | Stronger `2KDkhha2xBXhtxRgeFYOCv`, So Now You Want Me (album `1ByHAhnxv1CqaOetglOmTf`) | littletreesnotts.com, Spotify, Apple Music, YouTube @littletreesband, Instagram @littletreeshq |
| Huskinson | Alien `47Komok3dCypkRILbHYffc`, Mary Jane `5oylkyh3mGvXnK07xU04ot` | Spotify artist `0ZLEbe7TedLkaaK9DNjIyR`, Apple Music, YouTube @huskinsonofficial, Instagram @huskinsonband |

Bios: Bradley and Huskinson come from their YouTube channel descriptions, and Little Trees from their website. All three are edited into British English.

Resource categories, from the structure sheet: Distribution; Copyright; Music publishing; Royalties; PROs (PRS, PPL and others); Social media and monetisation; YouTube channel management.

## Builder's calls (Claude)

- Navigation: Home, About, Services, Records, Resources, Accessibility, Contact.
- Visual style: black on off-white, taken from the logo, with one blue accent for links and focus. Contrast is at least 4.5:1 in light and dark mode.
- Search: a `role="search"` GET form (`?q=` and `?category=`), so a filtered view can be shared as a link. JavaScript filters the list as you type, and a polite live region says how many articles match. Without JavaScript, every article is listed, grouped by category.
- Placeholders: any text containing `[TO COME]` is shown as is, and the build prints a reminder listing the pages that still have it.
- Contact lists the four addresses from the structure sheet as `mailto:` links. They only work once the email is set up at Fasthosts.
