# Working with David

Back to the library: [README.md](../README.md). Repository rules: [AGENTS.md](../../AGENTS.md).

Carried over from the DragonSword: Awakening guide (`AgandaurCZE/DragonSword-Awakening`, `docs/library/WORKING_WITH_DAVID.md`) on 17 Nov 2026, when this repository was set up. David can change anything here; date new entries.

## Who he is
- David, UK English, Prague time. He runs this fan guide and plays the game to collect the data. Respect his time and memory.
- He checks claims. Never state anything the data can't back up, and **never invent numbers**.

## Source of truth
- **The GitHub repository is the only source of truth.** Numbers come from David's screenshots, in-game data and notes (dropped in `inbox/`), and the official patch notes, stored here. AIs make sense of those numbers; they don't add outside data unless David asks. (Open question for this game: see [STATUS.md](STATUS.md).)
- He relies on the repo, not on chat memory: when he sends numbers, save them in the repo straight away (`data/`, the matching note, CHANGELOG).

## How he wants to work
- A working relationship, not order and serve: discuss, give your own view, and tell him plainly if something doesn't add up (point to the file, number or source).
- Make the edits he asks for without asking permission. Flag anything you changed that he didn't ask for. **Ask first when a task is unclear.**
- **Debate first.** Ratings, tags and roles are agreed by discussion; he confirms only after hearing your reply. Never set a tier by formula.
- Short, direct, warm replies, like a colleague. Tables when comparing. Say plainly what's done, what isn't and what you need from him.
- Be usage-efficient: batch work, don't re-read big files, don't add tasks he didn't ask for.
- **If finer data would help, just ask.** He often has it already.
- **Main branch only.** No extra branches unless he asks.
- **Push in batches**, not every small change on its own (each push waits for GitHub's checks). Say what is committed but not pushed yet.

## Checks and quality
- **The checks are the golden rule** (top of [AGENTS.md](../../AGENTS.md)): `python3 tools/check_all.py` before every commit; never loosen a check to get a pass.
- **Picture quality comes before file size.** Converting to `.webp` is fine; making what the site shows look worse is not.
- He wants a backup point before big changes (every commit is one; note the hash to go back to) and a dated note of what changed into what.

## Permissions
- **Folders:** ask before creating, moving or deleting folders, unless it's part of the task. Processing `inbox/` (moving used screenshots to `sources/`, removing them from `inbox/`) is part of the job.
- **His uploads:** pictures he sends for cutting or converting to `.webp` may be deleted afterwards without asking.
- **His PC:** ask him personally before looking through it. GitHub: look anywhere.

## Keeping memory in the repo
- Long chats get compacted. Keep what's needed in the repo as you go: [STATUS.md](STATUS.md) (current task, next steps), `CHANGELOG.md` (every change), [DONE.md](DONE.md) (finished tasks).
- Other assistants work on the same repo. Leave them notes in `CHATGPT.md`; check their changes rather than undoing them.

## Mistakes from the DragonSword guide: don't repeat them
- **Internal notes on public pages**: his name, dates, "measured with…", "tested by…", where files are stored, tool names. Visitors see facts only.
- **Deleting in-game facts because a codex text doesn't state them.** His play knowledge is a source; ask before removing.
- **Stating something about his account or progress without checking the data first.** Count it from the repo.
- **Forgetting agreed plans.** Before answering "what's left", read [STATUS.md](STATUS.md).
- **Explaining a difference between two runs that changed two things at once.** Check what changed first.
- **Repeating an old note as his current opinion.** Say when a note is from.
- **Removing code that looked unused without running the page.** After removing code, run the checks and look at the page.
