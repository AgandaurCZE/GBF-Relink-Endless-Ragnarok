# Granblue Fantasy: Relink - Endless Ragnarok guide: notes for AI assistants

Read this before changing anything in this repository. It binds every assistant (Claude, ChatGPT, Codex, anyone).
Then read the library index [`docs/README.md`](docs/README.md), [`docs/library/WORKING_WITH_DAVID.md`](docs/library/WORKING_WITH_DAVID.md) and [`docs/library/STATUS.md`](docs/library/STATUS.md).

## Golden rules: the checks come first

1. **Before every commit, run `python3 tools/check_all.py`, and commit only when it ends with `ALL CHECKS PASSED`.** It checks the data rules, the data shape, the generated route pages, file rules (line endings, JSON format, folders, image types and sizes), JS syntax, the `?v=` cache numbers, and every page in a real browser on desktop and phone sizes. If it ends with `NOT RUN` (no browser on your machine), say so in your reply and in CHANGELOG, and treat rule 2 as the check.
2. **A push is published only if GitHub passes the same checks.** The workflow "Check and publish" (`.github/workflows/deploy.yml`) runs `check_all.py` on every push to `main` and publishes only when it passes. After pushing, look at the run for your commit (the Actions tab, or `gh run list -L 3`). Red means **your commit is not live, and nothing pushed after it will be until it's fixed**: fix it with a new commit. If you can't see the result, say you couldn't verify it; don't say it's live.
3. **Never weaken a check to get a pass.** Don't delete, skip, loosen or work around a check. Don't edit `.github/workflows/deploy.yml`, `tools/check_*.py`, `tools/validate_data.py`, `.gitattributes` or `.prettierrc.json` to make a failure go away, and never run `tools/check_shape.py --update` just to silence an error. If a check looks wrong, stop and tell David; change it only with his OK, and record why in CHANGELOG. Adding *new* checks is always welcome.
4. **Changing the structure of the data** (a new, renamed or moved key, a different type, a new data file, the first entry in an empty list): document it in [`docs/DATA_REFERENCE.md`](docs/DATA_REFERENCE.md), update the code that reads it, then run `python3 tools/check_shape.py --update` and read every line it prints. Commit `tools/data_shape.json` with the data. A new data file the page reads goes into `FILES` in `tools/check_shape.py`. Adding entries to a list that already has some needs no update.
5. **Changing code.** After editing `src/js/` or `src/css/`: run `npx --yes prettier@3.9.10 --write src/js src/css`, give every changed file a new `?v=` in `src/index.html` (the check fails otherwise), keep LF line endings. A new script file gets a number and goes into `src/index.html` in its numbered place.
6. **Adding a page.** Add it to `SITE.pages` in `data/game.json`, register its renderer as `PAGES.<id>` in `src/js/`, then run `python3 tools/build_routes.py`. The browser check opens every page in `SITE.pages` by itself; a new kind of view it can't reach that way (a pop-up, a calculator mode) gets a test in `tools/check_site.py` in the same commit.
7. **Look at it.** The checks prove nothing broke, not that the new thing looks right. Open the changed page on `python3 tools/serve_site.py` (desktop and phone width) before committing a visual change.
8. **Write it down as you go:** `CHANGELOG.md` (newest first: what changed from what into what, the date, the checks you ran and their result), `docs/library/STATUS.md`, and finished tasks in `docs/library/DONE.md`.

## Workflow: main only

- Work directly on `main`. No other branches unless David asks.
- Before work, fetch and look at the latest commits and the last publish run. Keep newer data, other assistants' work and the automatic Steam commits. Fetch (`git pull --rebase`) again before pushing. Never force-push; undo with `git revert <commit>`.
- Keep commits small, with clear messages ("Add Katalina's skills"), so one change can be reverted alone. Before a large or risky change, write the current commit hash into the CHANGELOG entry as the point to go back to.
- Push in batches when there's a meaningful set of changes, or when David wants something live. Say what is committed but not pushed yet.

## Folders

| Folder | Rule |
|---|---|
| `data/` | `game.json`: **all** content the site shows; the page reads keys by name. `research.json`: measurements and test results the site doesn't show. `steam-news.json`: written only by `tools/steam_news.py`, never by hand. Hand-edited JSON is UTF-8 with a 1-space indent and a final newline (`json.dump(d, f, ensure_ascii=False, indent=1)`). |
| `assets/` | Only pictures and fonts the site shows, in the subfolder for their kind. Prefer `.webp`; no file over 5 MB. Lowercase file names with hyphens (`assets/characters/katalina.webp`). Other files go elsewhere. |
| `inbox/` | David's drop folder. Process what's there (save numbers into `data/`, notes into `docs/`), move the screenshots you used into `sources/`, then remove them from `inbox/`. Never publish anything from here. `tools/inbox_images.py` does the picture steps: `list`, `asset` (crop, resize, save as lossless `.webp` in `assets/`), `archive` (move the original to `sources/`, dated). |
| `sources/` | Evidence behind the data (screenshots, recordings notes), named so it's clear what they back up. Not published. |
| `src/` | `index.html` (layout only), `css/site.css` (every style), `js/NN-*.js` (the script, in load order). No guide content in code. |
| `routes/` | Generated by `tools/build_routes.py`. Never edit by hand. |
| `tools/` | Python tools. No pages here. `tools/scaffold.py character|guide "Name"` adds an empty entry with its address; `tools/import_tiers.py` brings in tier lists from David's Tier List Editor (docs/README.md). |
| `docs/` | Notes for David and the assistants. Not published. |

## Data rules

1. **The repository is the only source of truth about the game (David, 17 Nov 2026).** David tests and finds everything out himself; game data comes only from his screenshots, in-game data and notes, saved here. **Never look up the game on the internet** (wikis, guides, databases, videos, other tier lists), not even to check a number. The internet is fine for coding, page structure and tools. **Never invent numbers**; if his sources conflict, flag it and ask. The News and Patch Notes pages show the official Steam posts as they are; they are not a source for `data/game.json`.
2. **Tiers are never set by formula.** `TIER_LIST.lists` holds only placements agreed with David (he makes them in the Tier List Editor).
3. **Keep names exact**: character, weapon, sigil and skill names are cross-references between keys.
4. **Nothing a visitor reads may be an internal note**: no David, no "measured", "tested", "not confirmed yet", no TODOs. Internal notes go in a `note` field the page doesn't print, in `data/research.json`, or in `docs/`. The browser check fails on some of these words; the rest is on you.
5. Each data rule that can be checked gets a line in `tools/validate_data.py`.

## How the site works

A static site on GitHub Pages: no framework, no server. `src/js/09-startup.js` loads `data/game.json` and `data/steam-news.json`, builds the menu from `SITE.pages`, and draws the page whose `route` matches the address. Every address has a generated copy of `src/index.html` under `routes/`, so links and reloads work. `tools/build_site.py` assembles what GitHub publishes; `tools/serve_site.py` serves the same thing locally (`file://` doesn't work). Details: [`docs/library/SITE.md`](docs/library/SITE.md).
