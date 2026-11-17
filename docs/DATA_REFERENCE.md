# Data reference

Back to the library: [README.md](README.md). Rules: [AGENTS.md](../AGENTS.md), golden rule 4 (changing the structure).

Every key the site reads, its shape, and which page shows it. When you add or change a key, update this file in the same commit and run `python3 tools/check_shape.py --update`.

## Files

| File | Who writes it | The site reads it |
|---|---|---|
| `data/game.json` | AI, by hand, from David's material | Yes, at start-up |
| `data/steam-news.json` | Only `tools/steam_news.py` (the "Refresh Steam news" workflow) | Yes, at start-up |
| `data/research.json` | AI, by hand | No. Measurements, test results and working numbers behind the guide. |
| `tools/data_shape.json` | Only `tools/check_shape.py --update` | No. The recorded shape of the files above. |

Hand-edited JSON: UTF-8, 1-space indent, real characters (not `\u` escapes), final newline: `json.dump(d, f, ensure_ascii=False, indent=1)` and a `\n`.

## `data/game.json`

| Key | Shape | Shown on |
|---|---|---|
| `schemaVersion` | number | (none) |
| `meta` | `{game, patch, updated}`. `patch` is the game version the data matches (e.g. `"2.0.6"`); when set, every page header shows it. `updated` is a date `YYYY-MM-DD`. | Page header |
| `SITE.title` | string: the site name in the header and browser tab | Every page |
| `SITE.pages[]` | `{id, route, label, group}`. One entry per page, in menu order. `id` names the renderer `PAGES.<id>` in `src/js/`; `route` is the address (`""` = home, must be first); `label` is the menu and title text; `group` is the menu heading (`""` = none). | Menu, routing |
| `CHARACTERS[]` | `{name, image}` so far: `image` is a path in `assets/characters/`. The list is empty; the first real character defines the full shape. | Characters, Tier List |
| `TIER_LIST.tiers[]` | `{name, color}` in order, best first (`color` is a CSS colour). Empty until agreed with David. | Tier List |
| `TIER_LIST.ratings` | map: character name → tier name. Only ratings agreed with David. | Tier List |
| `GUIDES[]` | `{id, title, summary}` so far | Guides |
| `TOOLS[]` | `{id, title, summary}` so far | Tools |

Checked by `tools/validate_data.py`: unique page ids and routes, home first, routes in lowercase-and-hyphens; unique character names, guide and tool ids; every rating names a real character and tier; every `assets/...` path anywhere in the file exists.

## `data/steam-news.json`

`{posts: [...], patches: [...]}`, newest first. Each item: `{id, title, date, url, body}`; patches also have `version` (`"2.0.6"`), taken from a title like "Ver. 2.0.6 Update Information". `body` is Steam BBCode; `steamText()` in `src/js/03-news.js` turns it into safe HTML.
