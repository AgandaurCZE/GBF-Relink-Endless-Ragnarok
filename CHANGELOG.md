# Changelog

Every change, newest first: what changed from what into what, the date, the checks run and their result.

## 17 Nov 2026: repository foundation (Claude)
David asked for the project's foundation, organised like the DragonSword: Awakening guide but not necessarily identical, with the JSON, AI, owner and picture areas kept apart. Starting point: GitHub's initial commit `37e17d8` (README only).

- **Folders:** `data/` (`game.json` for all site content, `research.json` for measurements the site doesn't show, `steam-news.json` written automatically), `assets/` (pictures and fonts by kind: characters, weapons, sigils, items, enemies, icons, ui, fonts), `inbox/` (David's drop folder), `sources/` (evidence kept behind the data), `docs/` (notes library), `src/` (site code), `routes/` (generated page entries), `tools/`.
- **Site:** a static site with Home, Tier List, Characters, Guides, Tools, News and Patch Notes, built from `SITE.pages` in `data/game.json`, with clean addresses (`/tierlist`, `/news` …) and a phone menu. Pages without content show "coming soon".
- **Checks:** `tools/check_all.py` (data rules, data shape, route pages, file rules, JS syntax, cache numbers, browser check on desktop and phone, formatting). Tried with broken data and a broken script: both caught.
- **Publishing:** `.github/workflows/deploy.yml` publishes to GitHub Pages only when every check passes.
- **Steam news:** `tools/steam_news.py` and `.github/workflows/steam-news.yml` refresh News and Patch Notes from the official Steam announcements (app 881020) twice an hour. The fetcher couldn't be run from the setup machine (no access to Steam there); it was tested with a saved sample response. Its first real run is on GitHub.
- **Notes:** `AGENTS.md` (rules for every AI, golden rules carried over from DragonSword), `CLAUDE.md`, `CHATGPT.md`, `docs/README.md`, `docs/DATA_REFERENCE.md`, `docs/library/` (STATUS, WORKING_WITH_DAVID carried over from DragonSword, DECISIONS, DONE, SITE).
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.
