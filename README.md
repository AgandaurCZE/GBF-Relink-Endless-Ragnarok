# Granblue Fantasy: Relink - Endless Ragnarok, a fan-made guide

Tier list, guides and tools for **Granblue Fantasy: Relink - Endless Ragnarok** (Cygames; PC / Steam, PS5, PS4, Switch 2).

**Open the guide:** https://agandaurcze.github.io/GBF-Relink-Endless-Ragnarok/

What's inside (being built):

- **Tier list** and **character** pages
- **Guides** and **tools**
- **News** and **Patch Notes**, refreshed automatically from the official Steam announcements

Fan-made guide. Not affiliated with or endorsed by Cygames. Granblue Fantasy: Relink and all game assets belong to their respective owners.

---

## Working on this repository

AI assistants start with [`AGENTS.md`](AGENTS.md): the rules, starting with the checks that must pass before every commit. Everyone else can start with the notes library, [`docs/README.md`](docs/README.md).

| Folder | What it holds | Who edits it |
|---|---|---|
| `data/` | The guide's content as JSON. `game.json` holds everything the site shows. `steam-news.json` is refreshed automatically. `research.json` holds measurements the site doesn't show. | AI, from your screenshots and notes |
| `assets/` | Pictures and fonts the site shows (`.webp` preferred), one subfolder per kind: `characters/`, `weapons/`, `sigils/`, `items/`, `enemies/`, `icons/`, `ui/`, `fonts/` | Both |
| `inbox/` | **Your drop folder.** Screenshots, notes and numbers for the AI to process. Not published on the site. | You |
| `sources/` | Screenshots and other evidence behind the data, kept after processing. Not published on the site. | AI |
| `docs/` | The notes library: where things stand, decisions, data reference, how to work together | Both |
| `src/` | The website code: `index.html`, `css/`, `js/` | AI |
| `routes/` | One generated entry page per address (`/tierlist`, `/news` …). Never edited by hand. | Generated |
| `tools/` | Python tools: building, checks, the Steam news fetcher | AI |
| `.github/workflows/` | Publishing after the checks pass, and the twice-hourly Steam news refresh | AI |
| `AGENTS.md`, `CLAUDE.md`, `CHATGPT.md` | Rules and notes for AI assistants | AI, with your OK |

Run the site locally with `python3 tools/serve_site.py`. Run all checks with `python3 tools/check_all.py`.
