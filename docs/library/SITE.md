# The site: how it works, checks and publishing

Back to the library: [README.md](../README.md). Rules: [AGENTS.md](../../AGENTS.md).

## Titles and link previews
`tools/build_routes.py` gives every generated page its own `<title>`, description, canonical address and link preview (`og:*`): pages from `SITE.pages` (`label`, `description`), characters (`name`, `summary`, and their `image` as the preview picture) and guides (`title`, `summary`). So a link to `/characters/katalina` posted on Discord shows Katalina, not the site's general title. Rerun it after changing any of these.

## How a page is drawn
1. GitHub Pages serves `routes/<route>/index.html`, a generated copy of `src/index.html` whose `<base>` points back to the site root. The small script right after `<base>` freezes that base, so `css/`, `js/`, `assets/` and `data/` always resolve.
2. The scripts load in their numbered order and share one global scope:

| File | Holds |
|---|---|
| `src/js/01-core.js` | Globals (`GAME`, `NEWS`, `PAGES`) and helpers (`$`, `esc`, `emptyState`, `formatDate`) |
| `src/js/02-pages.js` | Home, Tier List, Characters, Tools |
| `src/js/03-news.js` | News and Patch Notes; `steamText()` turns Steam BBCode into safe HTML; post links (`/patch-notes#v2-0-6`, `/news#post-<id>`), "Copy link", the newest patch opened by default, "New" marks since the visitor's last look (kept in their browser) |
| `src/js/04-blocks.js` | The content blocks (`blocksHtml`) shared by character tabs and guides |
| `src/js/05-characters.js` | Each character's own page (`/characters/<slug>`) and its tabs |
| `src/js/06-guides.js` | The Guides list and each guide's own page (`/guides/<id>`) with a contents list |
| `src/js/07-search.js` | The search box: pages, characters (name, summary, tab text), guides, tools, news and patch notes (title and text) |
| `src/js/09-startup.js` | Loads the data, builds the menu from `SITE.pages`, routing (`pageForPath`, `go`, Back/Forward), the phone menu |

3. `09-startup.js` loads `data/game.json` and `data/steam-news.json`, builds the menu, then calls `PAGES[page.id]()`, which returns the page's HTML. Menu clicks change the address with `history.pushState` instead of reloading.

**Escape everything** that comes from data with `esc()` before it goes into HTML.

## Adding a page
1. Add `{id, route, label, group}` to `SITE.pages` in `data/game.json`, in menu order.
2. Write `PAGES.<id> = () => '...html...'` in the matching `src/js/` file (or a new numbered file, added to `src/index.html`).
3. `python3 tools/build_routes.py`, prettier, new `?v=`, `python3 tools/check_all.py`.

## Installable app and offline
`src/manifest.webmanifest` (name, colours, icons) and `src/sw.js` (the offline worker) are published at the site root. The worker fetches pages and data fresh when online and keeps a copy for offline; css, js and pictures come from its cache and refresh in the background (their `?v=` changes when they do). When changing how `sw.js` caches, change its `CACHE` name so visitors' old caches are cleared.

Installing: Android/Chrome/Edge show "Install app" in the menu (or the browser's own install prompt). iPhone/iPad: Safari → Share → "Add to Home Screen" (Safari has no install button for sites); the `apple-*` tags in `src/index.html` give it its name, icon and status bar.

## Adding content quickly
`python3 tools/scaffold.py character "Name" --tabs "Overview,Skills,Build"` or `python3 tools/scaffold.py guide "Title" --summary "…"` adds an empty entry to `data/game.json` (name and address only, nothing invented), sets `meta.updated` to today and regenerates the page addresses. Empty tabs show "More coming soon"; a guide without blocks is listed as "Coming soon".

## Running it locally
`python3 tools/serve_site.py` builds the site into a temporary folder and serves it at http://127.0.0.1:8000/. Restart it after an edit. `file://` doesn't work (the page fetches its data).

## Checks and publishing
`python3 tools/check_all.py` runs, in order:

| Check | Fails when | Fix |
|---|---|---|
| data rules (`tools/validate_data.py`) | a duplicate id or name, a rating for an unknown character or tier, a missing `assets/` file, a bad route | Fix the data |
| data shape (`tools/check_shape.py`) | an unknown, missing or misplaced key, a wrong type, first entries in an empty list | Fix a typo; or, for an intended change, document it and run `--update` |
| clean URLs (`tools/build_routes.py --check`) | a route page is missing or outdated | `python3 tools/build_routes.py` |
| file rules | CRLF line endings, badly formatted JSON, a css/js file without `?v=` or not loaded, a non-picture in `assets/`, a picture over 5 MB, an `.html` file in the top folder | As the message says |
| JS syntax (`node --check`) | a script doesn't parse | Fix the script |
| cache numbers | a css/js file changed but kept its `?v=` | New `?v=` in `src/index.html` |
| browser (`tools/check_site.py`) | on any page at desktop or phone size: a console error, a file that fails to load, a wrong title, an in-site link or contents link that leads nowhere, menu navigation or Back broken, the news renderer not working with a sample post, visible text with "David", "TODO", "undefined", "NaN"; an accessibility problem (axe-core, WCAG 2 A/AA: contrast, labels …) on any page in light or dark mode | Fix the page (for contrast: the colour variables at the top of `site.css`) |
| formatting (prettier) | warning only: src/js or src/css not formatted | `npx --yes prettier@3.9.10 --write src/js src/css` |

On every push to `main`, `.github/workflows/deploy.yml` runs the same script on GitHub, then assembles the site with `tools/build_site.py` and publishes it to GitHub Pages, **only if every check passed**. The run's summary page shows the check output.

Also generated: `routes/404.html` (GitHub Pages shows it for any unknown address; its `<base>` is the absolute site path, `SITE_PATH` in `tools/build_routes.py`), and `sitemap.xml` at publishing (every page, for search engines; submit `https://agandaurcze.github.io/GBF-Relink-Endless-Ragnarok/sitemap.xml` in Google Search Console if wanted). The share image for links is `assets/ui/og-image.jpg` (1200×630, no game art).

Published: `routes/`, `src/js` and `src/css` (as `/js`, `/css`), `assets/`, `data/`. Not published: `docs/`, `inbox/`, `sources/`, `tools/` and the notes (they're still visible on GitHub, because the repository is public).

## Steam news
`.github/workflows/steam-news.yml` runs `tools/steam_news.py` at :23 and :53 every hour. A Steam outage ends in a warning (feed unchanged, retried next run); a broken feed, or one suddenly much shorter than ours, fails red. It reads the official announcements of Granblue Fantasy: Relink on Steam (app 881020; Endless Ragnarok is an upgrade of that game on Steam, so its posts appear there), writes `data/steam-news.json`, commits a change to `main` and starts the publish run. Titles with a version ("Ver. 2.0.6 Update Information") go to Patch Notes.

Later, the guide can read balance changes out of the update notes and apply them to the character data automatically, the way the DragonSword guide's `tools/apply_patch_skills.py` does. That needs the character data first.
