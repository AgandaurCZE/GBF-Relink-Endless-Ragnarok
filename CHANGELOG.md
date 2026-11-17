# Changelog

Every change, newest first: what changed from what into what, the date, the checks run and their result.

## 17 Nov 2026: AGENTS.md data rule 2 updated (Claude)
- Still named the old `TIER_LIST.ratings`; now `TIER_LIST.lists`, placements agreed with David in the Tier List Editor.

## 17 Nov 2026: steadier Steam refresh; getting-started note (Claude)
- `tools/steam_news.py`: when Steam doesn't answer (network, timeout, 429, 5xx) it retries three times, then keeps the current feed and ends with a warning instead of a red run; the next run tries again. New guard: a feed suddenly more than 5 posts shorter than ours is refused (red), so a partial answer can't wipe the News pages. Both tried (simulated outage: three tries then "unavailable"; a 1-post feed against our 50: refused, file untouched).
- New `docs/library/GETTING_STARTED.md` for David: the loop from `inbox/` and the notebook to the live site, what to decide first, how to install the app on each phone. Listed in `docs/README.md`.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: phone install check, accessibility check (Claude)
- Checked the live site: manifest, all three icons and the offline worker load and take over. Added the iPhone home-screen tags (`apple-mobile-web-app-*`, name "Relink Guide") and a stable app `id`; how to install on each phone is in `docs/library/SITE.md`.
- **New check:** `tools/check_site.py` runs axe-core (WCAG 2 A and AA, installed from npm for each run) on every page and the sample character, guide, tier list and Home, in dark and light mode. Skipped (and said so) only where npm is missing.
- It found two real problems in light mode, both fixed: gold text was too faint on white (new `--gold-ink`, darker in light mode, for gold used as text) and links were just under the contrast minimum (light-mode blue `#1673c9` → `#1366b3`, 4.5 → 5.4 : 1). Dark mode had none.
- The sample guide now also has its own page file in the test build, so it can be opened directly.
- `?v=`: site.css 11.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: Tier List Editor and import (Claude)
- New artifact **Relink Tier List Editor** (https://claude.ai/artifact/NcqRc5BJkia6KCAPyz2pVN, source `docs/testkit/relink-tier-editor.html`): David sets the tiers (or starts from S–D), creates lists, adds characters, and places them by dragging (mouse) or tapping (phone); the order inside a tier is kept. Saved in the artifact's database; only he can write. "Copy for the guide" gives `TIER_LIST`.
- New `tools/import_tiers.py`: puts an editor export into `data/game.json`, prints who moved where per list (`--dry-run` first), dates changed lists, refuses names that aren't characters unless `--add-missing`. Tried: missing names refused, added with the flag, an in-tier reorder recognised; test data removed again.
- Both tried in a browser with a stand-in database (tiers, list, three characters, tap and drag moves, export). Routine in `docs/README.md`.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: several tier lists (Claude)
- `TIER_LIST` changed from `{tiers, ratings: {name: tier}}` into `{tiers, lists: [{id, label, about?, updated?, rows: {tier: [names in order]}}]}`, so there can be several lists (tabs, `/tierlist#<id>`) and the order inside a tier is kept. Both were empty, so no ratings moved. `tools/data_shape.json` updated (`ratings` → `lists`; nothing else changed).
- **Fixed my own mistake:** the tier-list rules in `tools/validate_data.py` had been deleted by accident in the guide-pages commit `c45b27b`. They're back in the new form: tier colours, list ids and dates, every placed name is a character, every tier exists, nobody placed twice in one list. Tried with five broken entries: all five reported.
- `tools/check_site.py`: sample lists (tabs only for lists with entries, `#solo` link, switching tabs, no dead links).
- `?v=`: 01-core 2, 02-pages 5, 09-startup 10.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: installable app, offline reading, light mode (Claude)
- **Installable app:** `src/manifest.webmanifest` and app icons (`assets/ui/icon-*.png`, drawn from the site emblem), published at the site root by `tools/build_site.py`; an "Install app" button appears in the menu where the browser offers installing.
- **Offline reading:** `src/sw.js` keeps the last copy of pages and data (always fetched fresh when online) and css/js/pictures; offline, any page opens, even one never visited (via `404.html`).
- **Light mode:** follows the system setting; a "Light mode / Dark mode" button in the menu switches and remembers the choice (set before the page draws, so no flash).
- Checks: `tools/check_all.py` also checks `src/sw.js` syntax and that the manifest's icons exist; `tools/check_site.py` tests the light/dark switch (colours change and are remembered) and offline use (an opened and a never-opened page). Tried with the worker switched off: caught.
- `?v=`: site.css 9, 09-startup 9.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: home dashboard (Claude)
- Home is now a dashboard: a banner (with the game version when `meta.patch` is set), the latest patch (with "New" when unseen), the three newest news posts, "Recently updated" guides and characters (by `updated`), character portraits, and the page shortcuts. Empty sections stay hidden.
- Characters can have `updated` (date); `tools/scaffold.py` sets it, `tools/validate_data.py` checks the format.
- `tools/check_site.py`: Home with sample content shows every section and has no dead links.
- `?v=`: site.css 8, 02-pages 4, 09-startup 7.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: publishing steps updated; patch mentions on character pages (Claude)
- `.github/workflows/deploy.yml`: `configure-pages` v5 → v6, `upload-pages-artifact` v4 → v5, `deploy-pages` v4 → v5 (the Node.js 24 versions; v5 of configure-pages showed a deprecation warning on every run).
- Character pages end with "In the official patch notes and news": every Steam post that names the character (whole word, any case, also `aliases`), newest patches first, linking to the exact post. Only official posts are linked; nothing is copied into the guide data.
- `tools/check_site.py`: the sample post now names the sample character, and its page must list both posts.
- `?v=`: site.css 7, 05-characters 3.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: setup tool and broken-link check (Claude)
- New `tools/scaffold.py`: `character "Name" [--slug] [--image] [--tabs "Overview,Skills"]` and `guide "Title" [--id] [--summary]` add an empty entry (no invented content), set `meta.updated` and regenerate addresses. Tried both, plus a duplicate (refused); test entries removed again.
- Empty character tabs show "More coming soon" instead of nothing.
- `tools/check_site.py`: every in-site link on every page, the sample pages and search results must lead to a real page, and every contents link to a real section; the sample character has an empty tab.
- `?v=`: 05-characters 2.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: keyboard and reading comfort (Claude)
- "/" jumps to the search box from anywhere (on phones it opens the menu), Esc clears the search and closes the menu.
- A round "Back to top" button after scrolling down a screen; a "Skip to content" link for keyboard users; visible focus outlines; animations off for visitors who ask their system for less motion.
- The footer shows "Guide updated <date>" from `meta.updated`: keep it current when the content changes.
- `tools/check_site.py`: "/" and Esc, and "Back to top" on a long page.
- `?v=`: site.css 6, 09-startup 6.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: patch note links and "New" marks (Claude)
- Every post has its own address (`/patch-notes#v2-0-6`, `/news#post-<id>`) and a "Copy link" button; a link opens and scrolls to that post. Patch Notes opens the newest patch by default. Search results open the exact post.
- Posts newer than the visitor's last look at News or Patch Notes show a blue "New" badge (remembered in their own browser; nothing on a first visit).
- `tools/check_site.py`: a post link opens its post; "New" shows for an unseen post and disappears once seen.
- `?v=`: site.css 5, 03-news 3, 07-search 2, 09-startup 5.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: guide pages and two new blocks (Claude)
- Guides with `blocks` get their own page at `/guides/<id>` (`src/js/06-guides.js`), with an "Updated" date and a contents list when three or more blocks have titles; block titles are linkable (`#section`). Search finds text inside guides.
- New block types `note` (tip or warning box) and `image` (picture from `assets/` with alt text and caption). The block code moved into `src/js/04-blocks.js`, shared by characters and guides. Script files renumbered: 05-characters, 06-guides, 07-search.
- `tools/validate_data.py`: guide ids, dates, the new blocks (shared check for characters and guides). `tools/check_site.py`: a sample guide on a phone (link only for guides with blocks, contents jump, every block type).
- `?v=`: site.css 4, 02-pages 3, 04-blocks 1, 05-characters 1, 06-guides 1, 07-search 1, 09-startup 4.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

## 17 Nov 2026: Test Notebook upgrade (Claude)
- **Voice entry** (artifact capability `dictation`, Chrome/Edge or the desktop app): press "Speak" and say e.g. "Katalina, damage 12345, cooldown 12, note first hit, save". Text before the first field name fills the subject; each field name takes the words after it; "save" at the end adds the entry. Numbers like "12,345" are stored as 12345.
- **Sortable columns** (click a heading), **Summary** per subject for the entries shown (lowest · average · highest of each number field), **Copy as CSV** for spreadsheets.
- Tried with a stand-in database and microphone: three spoken entries, sorting, summary; no errors. Republished to the same artifact (entries kept).

## 17 Nov 2026: Test Notebook (Claude)
- New artifact **Relink Test Notebook** (https://claude.ai/artifact/3TRUSLHHo3JA7FLkcD8EPX), page source in `docs/testkit/relink-test-notebook.html`. David creates tests (name, how it's measured, what an entry is about, fields with units) and adds, edits, filters and deletes entries; "Copy as JSON" per test. Data in the artifact's database (`tests/`, `entries/`), readable by whoever he shares it with, writable only by him (`write: owner`). Tried in a browser with a stand-in database: create test, add two entries, edit, filter, delete; no errors.
- `docs/README.md`: new "Tools outside the repository" section with the backup routine (dated `docs/testkit/notebook-<date>.json` exports); STATUS lists the ready tools.
- Checks: `python3 tools/check_all.py`: ALL CHECKS PASSED.

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
