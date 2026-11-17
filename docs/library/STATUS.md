# Status: where things stand

Back to the library: [README.md](../README.md).

## Now · 17 Nov 2026
- The repository was created and the foundation built: folders, an empty site with Home, Tier List, Characters, Guides, Tools, News and Patch Notes, the checks, publishing to GitHub Pages, and the twice-hourly Steam news refresh. No game content yet.
- **Next:** David starts the game and sends the first material (screenshots, notes) through `inbox/`. The first characters define the shape of `CHARACTERS` (see [DATA_REFERENCE.md](../DATA_REFERENCE.md)).

## Tools ready · 17 Nov 2026
- **Test Notebook** for measurements while playing, with voice entry, sorting, per-subject summary and CSV/JSON copy: https://claude.ai/artifact/3TRUSLHHo3JA7FLkcD8EPX (details in [docs/README.md](../README.md)).
- **Character pages** (`/characters/<slug>`, tabs) and **guide pages** (`/guides/<id>`, contents list), both built from blocks (text, list, table, stats, note, image): waiting for content.
- **Tier List Editor**: https://claude.ai/artifact/NcqRc5BJkia6KCAPyz2pVN; results come into the site with `tools/import_tiers.py`. The site shows several lists as tabs.
- **`tools/scaffold.py`** adds an empty character or guide; **`tools/inbox_images.py`** turns screenshots from `inbox/` into site pictures.
- Site: search (`/` key), 404 page, share image, sitemap, post links and "New" marks on News/Patch Notes, back to top, skip link.
- The checks cover all of it, including broken in-site links.

## Open questions for David
- **Which pages matter first** (tier list, character builds, sigils, weapons, quests, a damage calculator …), so `SITE.pages` and the data grow in that order.
- **What the tier list rates**: overall, by content (e.g. Chaos difficulty, solo/co-op), by role? The tier rules go into [DECISIONS.md](DECISIONS.md).

## Setup
- GitHub Pages: Source = "GitHub Actions" (David set it on 17 Nov 2026).
