# Project library: start here

The index of every note in the repository. A new chat (Claude, ChatGPT, Codex or anyone) reads this file first, then only the files the task needs. **The repository is the only source of truth**: if two notes disagree, `data/game.json` wins, then the newer note. Fix the older one.

## Read first, every new chat

| File | What it holds |
|---|---|
| [`../AGENTS.md`](../AGENTS.md) | The rules, starting with the **golden rules**: run `python3 tools/check_all.py` before every commit, the site is published only when GitHub passes the same checks, never weaken a check. Then the main-only workflow, folders, data rules. Binding. |
| [`library/WORKING_WITH_DAVID.md`](library/WORKING_WITH_DAVID.md) | How David likes to work, his permissions, mistakes to avoid |
| [`library/STATUS.md`](library/STATUS.md) | **Where things stand right now**: current task, next steps, open questions |
| [`library/GETTING_STARTED.md`](library/GETTING_STARTED.md) | For David: how a content session works, from `inbox/` to the live site |

## Reference

| Topic | File |
|---|---|
| Every data key, its shape and which page shows it | [`DATA_REFERENCE.md`](DATA_REFERENCE.md) |
| The site: how pages, routing and data loading work; the checks and publishing; Steam news | [`library/SITE.md`](library/SITE.md) |
| Agreed decisions: tier rules, ratings and the reasoning behind them | [`library/DECISIONS.md`](library/DECISIONS.md) |
| Notes for ChatGPT / Codex | [`../CHATGPT.md`](../CHATGPT.md) |

## Tools outside the repository

| Tool | Live link | Page source | Data copies |
|---|---|---|---|
| Test Notebook: David's measurements while playing. He defines each test (fields, units, what an entry is about) and adds entries; data is saved in the artifact's own database, only he can write. | https://claude.ai/artifact/3TRUSLHHo3JA7FLkcD8EPX (slug `13e2b288-3fa0-4547-8987-a694e9fb02e6`) | [`testkit/relink-test-notebook.html`](testkit/relink-test-notebook.html) | `testkit/notebook-<date>.json` (none yet) |
| Tier List Editor: David builds the tier lists (tiers, several lists, drag or tap characters into place, order inside a tier). Only he can write. | https://claude.ai/artifact/NcqRc5BJkia6KCAPyz2pVN (slug `af10c94a-9fc4-4445-a1ed-11ff2b2580c1`) | [`testkit/relink-tier-editor.html`](testkit/relink-tier-editor.html) | the site's `TIER_LIST` itself |

- **Tier lists, editor → site:** David presses "Copy for the guide" and drops the text into `inbox/tiers.json` (or the chat). Run `python3 tools/import_tiers.py inbox/tiers.json --dry-run`, show him who moved where, then import for real, run the checks, commit. Only ratings he agreed (AGENTS.md data rule 2).
- **Characters into the editor:** when `CHARACTERS` changes, write each character into the editor's database (`db_write` on the slug above, path `roster/<slug>`, body `{name, order}` in the guide's order), so he can place them. Names must match `data/game.json` exactly.
- **Backup routine (carried over from DragonSword):** at the end of a session that used the notebook's data, export it (`db_list` on `tests` and `entries` with the slug above) into `testkit/notebook-<YYYY-MM-DD>.json`, and delete the previous dated copy once the new one contains it (git keeps the history). David can also press "Copy as JSON" on a test and paste it into `inbox/`.
- After changing the notebook page, edit `testkit/relink-test-notebook.html` and publish it to the same artifact (`publish_files`, slug above). Entries are not stored in the page, so republishing keeps them.
- Measurements from the notebook that the guide uses go into `data/research.json` (working numbers) and `data/game.json` (what the site shows).

## History

| File | What it holds |
|---|---|
| [`library/DONE.md`](library/DONE.md) | Finished tasks and answered questions: nothing there needs doing again |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Every change, newest first |

## Keeping the library current
- A new note file gets a line in this index and a "Back to the library" line at its top.
- Update [STATUS.md](library/STATUS.md) and `CHANGELOG.md` as you go, not only at the end; move finished tasks to [DONE.md](library/DONE.md).
- When a topic grows (game mechanics, test results, a big guide), give it its own file in `library/` and list it here.
