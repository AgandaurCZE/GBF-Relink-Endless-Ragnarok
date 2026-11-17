# Changelog

Every change, newest first: what changed from what into what, the date, the checks run and their result.

## 17 Nov 2026: site extras (Claude)
- **Page not found:** `routes/404.html` (generated) shows a "Page not found" page with the menu for any unknown address; unknown routes no longer fall back to Home silently.
- **Share image:** `assets/ui/og-image.jpg` (1200×630, drawn from the site's colours and emblem, no game art) and the `og:image` / Twitter tags in `src/index.html`, so links posted on Discord, Reddit etc. show a picture.
- **Search:** a search box in the menu (`src/js/05-search.js`) over pages, characters, guides, tools, and news and patch notes including their text.
- **Sitemap:** `tools/build_site.py` writes `sitemap.xml` with every page at publishing.
- Browser check: new tests for 404 and search (results by kind, no results, opening a result, clearing). The first run caught that search only looked at news titles; fixed by searching the text too.
- Not done: Backup & Restore (the site has no visitor settings to back up yet).
- `?v=`: site.css 3, 05-search.js 1, 09-startup.js 3.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: character page template (Claude)
- New `src/js/04-characters.js`: every character with a `slug` gets a page at `/characters/<slug>` with tabs built from four block types (text, list, table, stats); the open tab is kept in the address (`#skills`). Character cards on Characters and Tier List now link to it. Format in `docs/DATA_REFERENCE.md`.
- `tools/build_routes.py` makes an entry page per character; `tools/validate_data.py` checks slugs, tab ids, block types and table rows; `tools/check_site.py` (new test) draws a sample character: card link, tab switch, direct `#skills` link on desktop and phone, back link, no unescaped HTML. Tried with tab switching broken: caught.
- `?v=`: site.css 2, 02-pages.js 2, 04-characters.js 1, 09-startup.js 2.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: inbox picture tool (Claude)
- New `tools/inbox_images.py`: `list` (pictures waiting in `inbox/`), `asset` (crop, resize, save as `.webp` in `assets/`, lossless unless `--lossy`, names checked, 5 MB limit), `archive` (move an original into `sources/` as `<name>-<date>`, tidy empty inbox folders). Tried on a sample picture. Mentioned in AGENTS.md (inbox row) and `inbox/README.md`.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: Steam news live; patch-note choice fixed (Claude)
- The site is live (publish run 3 passed after David enabled GitHub Pages). The first "Refresh Steam news" run (started by hand) passed and committed 37 news posts and 13 patch notes.
- Fix in `tools/steam_news.py`: "Important Notice (Ver. 2.0.3)" had become the 2.0.3 patch note and "Ver. 2.0.3 Update Information" went to News. A title with "Update" now wins the version; both lists stay newest first. The next automatic run rewrites `data/steam-news.json`.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: source rule confirmed (Claude)
- David: as in DragonSword, he finds everything out himself; the repo is the only source of truth and nothing about the game comes from the internet (only coding, page structure and tools). AGENTS.md data rule 1 changed from "David's data or the official patch notes" into this rule; also WORKING_WITH_DAVID.md, STATUS.md (open question removed, Pages setup done) and DONE.md.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: cache-number check fixed for the first push (Claude)
- The first publish run (`c2e49db`) passed every check but stopped at "cache numbers": it compares `?v=` values with the commit before the push, GitHub's starter commit `37e17d8`, which had no site yet, and reported that as "NOT RUN". Changed `cache_numbers()` in `tools/check_all.py`: a readable commit without `src/index.html` now counts as nothing to compare (ok); an unreadable commit is still "NOT RUN". A bug in the new check, not a loosening.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: repository foundation (Claude)
David asked for the project's foundation, organised like the DragonSword: Awakening guide but not necessarily identical, with the JSON, AI, owner and picture areas kept apart. Starting point: GitHub's initial commit `37e17d8` (README only).

- **Folders:** `data/` (`game.json` for all site content, `research.json` for measurements the site doesn't show, `steam-news.json` written automatically), `assets/` (pictures and fonts by kind: characters, weapons, sigils, items, enemies, icons, ui, fonts), `inbox/` (David's drop folder), `sources/` (evidence kept behind the data), `docs/` (notes library), `src/` (site code), `routes/` (generated page entries), `tools/`.
- **Site:** a static site with Home, Tier List, Characters, Guides, Tools, News and Patch Notes, built from `SITE.pages` in `data/game.json`, with clean addresses (`/tierlist`, `/news` …) and a phone menu. Pages without content show "coming soon".
- **Checks:** `tools/check_all.py` (data rules, data shape, route pages, file rules, JS syntax, cache numbers, browser check on desktop and phone, formatting). Tried with broken data and a broken script: both caught.
- **Publishing:** `.github/workflows/deploy.yml` publishes to GitHub Pages only when every check passes.
- **Steam news:** `tools/steam_news.py` and `.github/workflows/steam-news.yml` refresh News and Patch Notes from the official Steam announcements (app 881020) twice an hour. The fetcher couldn't be run from the setup machine (no access to Steam there); it was tested with a saved sample response. Its first real run is on GitHub.
- **Notes:** `AGENTS.md` (rules for every AI, golden rules carried over from DragonSword), `CLAUDE.md`, `CHATGPT.md`, `docs/README.md`, `docs/DATA_REFERENCE.md`, `docs/library/` (STATUS, WORKING_WITH_DAVID carried over from DragonSword, DECISIONS, DONE, SITE).
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.
