# Project library: start here

The index of every note in the repository. A new chat (Claude, ChatGPT, Codex or anyone) reads this file first, then only the files the task needs. **The repository is the only source of truth**: if two notes disagree, `data/game.json` wins, then the newer note. Fix the older one.

## Read first, every new chat

| File | What it holds |
|---|---|
| [`../AGENTS.md`](../AGENTS.md) | The rules, starting with the **golden rules**: run `python3 tools/check_all.py` before every commit, the site is published only when GitHub passes the same checks, never weaken a check. Then the main-only workflow, folders, data rules. Binding. |
| [`library/WORKING_WITH_DAVID.md`](library/WORKING_WITH_DAVID.md) | How David likes to work, his permissions, mistakes to avoid |
| [`library/STATUS.md`](library/STATUS.md) | **Where things stand right now**: current task, next steps, open questions |

## Reference

| Topic | File |
|---|---|
| Every data key, its shape and which page shows it | [`DATA_REFERENCE.md`](DATA_REFERENCE.md) |
| The site: how pages, routing and data loading work; the checks and publishing; Steam news | [`library/SITE.md`](library/SITE.md) |
| Agreed decisions: tier rules, ratings and the reasoning behind them | [`library/DECISIONS.md`](library/DECISIONS.md) |
| Notes for ChatGPT / Codex | [`../CHATGPT.md`](../CHATGPT.md) |

## History

| File | What it holds |
|---|---|
| [`library/DONE.md`](library/DONE.md) | Finished tasks and answered questions: nothing there needs doing again |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Every change, newest first |

## Keeping the library current
- A new note file gets a line in this index and a "Back to the library" line at its top.
- Update [STATUS.md](library/STATUS.md) and `CHANGELOG.md` as you go, not only at the end; move finished tasks to [DONE.md](library/DONE.md).
- When a topic grows (game mechanics, test results, a big guide), give it its own file in `library/` and list it here.
