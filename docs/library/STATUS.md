# Status: where things stand

Back to the library: [README.md](../README.md).

## Now · 17 Nov 2026
- The repository was created and the foundation built: folders, an empty site with Home, Tier List, Characters, Guides, Tools, News and Patch Notes, the checks, publishing to GitHub Pages, and the twice-hourly Steam news refresh. No game content yet.
- **Next:** David starts the game and sends the first material (screenshots, notes) through `inbox/`. The first characters define the shape of `CHARACTERS` (see [DATA_REFERENCE.md](../DATA_REFERENCE.md)).

## Tools ready · 17 Nov 2026
- **Test Notebook** for measurements while playing: https://claude.ai/artifact/3TRUSLHHo3JA7FLkcD8EPX (details in [docs/README.md](../README.md)).
- **Character pages** (`/characters/<slug>`, tabs from blocks): waiting for the first character.
- **`tools/inbox_images.py`** for screenshots from `inbox/`.
- Search, 404 page, share image and sitemap on the site.

## Open questions for David
- **Which pages matter first** (tier list, character builds, sigils, weapons, quests, a damage calculator …), so `SITE.pages` and the data grow in that order.
- **What the tier list rates**: overall, by content (e.g. Chaos difficulty, solo/co-op), by role? The tier rules go into [DECISIONS.md](DECISIONS.md).

## Setup
- GitHub Pages: Source = "GitHub Actions" (David set it on 17 Nov 2026).
