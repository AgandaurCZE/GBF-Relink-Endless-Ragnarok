# The site: how it works, checks and publishing

Back to the library: [README.md](../README.md). Rules: [AGENTS.md](../../AGENTS.md).

## How a page is drawn
1. GitHub Pages serves `routes/<route>/index.html`, a generated copy of `src/index.html` whose `<base>` points back to the site root. The small script right after `<base>` freezes that base, so `css/`, `js/`, `assets/` and `data/` always resolve.
2. The scripts load in their numbered order and share one global scope:

| File | Holds |
|---|---|
| `src/js/01-core.js` | Globals (`GAME`, `NEWS`, `PAGES`) and helpers (`$`, `esc`, `emptyState`, `formatDate`) |
| `src/js/02-pages.js` | Home, Tier List, Characters, Guides, Tools |
| `src/js/03-news.js` | News and Patch Notes; `steamText()` turns Steam BBCode into safe HTML |
| `src/js/09-startup.js` | Loads the data, builds the menu from `SITE.pages`, routing (`pageForPath`, `go`, Back/Forward), the phone menu |

3. `09-startup.js` loads `data/game.json` and `data/steam-news.json`, builds the menu, then calls `PAGES[page.id]()`, which returns the page's HTML. Menu clicks change the address with `history.pushState` instead of reloading.

**Escape everything** that comes from data with `esc()` before it goes into HTML.

## Adding a page
1. Add `{id, route, label, group}` to `SITE.pages` in `data/game.json`, in menu order.
2. Write `PAGES.<id> = () => '...html...'` in the matching `src/js/` file (or a new numbered file, added to `src/index.html`).
3. `python3 tools/build_routes.py`, prettier, new `?v=`, `python3 tools/check_all.py`.

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
| browser (`tools/check_site.py`) | on any page at desktop or phone size: a console error, a file that fails to load, a wrong title, menu navigation or Back broken, the news renderer not working with a sample post, visible text with "David", "TODO", "undefined", "NaN" | Fix the page |
| formatting (prettier) | warning only: src/js or src/css not formatted | `npx --yes prettier@3.9.10 --write src/js src/css` |

On every push to `main`, `.github/workflows/deploy.yml` runs the same script on GitHub, then assembles the site with `tools/build_site.py` and publishes it to GitHub Pages, **only if every check passed**. The run's summary page shows the check output.

Published: `routes/`, `src/js` and `src/css` (as `/js`, `/css`), `assets/`, `data/`. Not published: `docs/`, `inbox/`, `sources/`, `tools/` and the notes (they're still visible on GitHub, because the repository is public).

## Steam news
`.github/workflows/steam-news.yml` runs `tools/steam_news.py` at :23 and :53 every hour. It reads the official announcements of Granblue Fantasy: Relink on Steam (app 881020; Endless Ragnarok is an upgrade of that game on Steam, so its posts appear there), writes `data/steam-news.json`, commits a change to `main` and starts the publish run. Titles with a version ("Ver. 2.0.6 Update Information") go to Patch Notes.

Later, the guide can read balance changes out of the update notes and apply them to the character data automatically, the way the DragonSword guide's `tools/apply_patch_skills.py` does. That needs the character data first.
