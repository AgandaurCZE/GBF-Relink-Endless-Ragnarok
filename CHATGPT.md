# Notes for ChatGPT / Codex

Hello from Claude. David works with several assistants on this repository. This file is yours; the shared rules are in [`AGENTS.md`](AGENTS.md) and bind all of us. Start with them, then the library index [`docs/README.md`](docs/README.md).

## The short version (17 Nov 2026)
1. **Before every commit: `python3 tools/check_all.py`.** Commit only on `ALL CHECKS PASSED`.
2. **GitHub runs the same checks on every push to `main` and publishes the site only if they pass.** A red run on the Actions tab means your commit is not live. Fix it with a new commit; never loosen a check.
3. **Work on `main` only**; `git pull --rebase` before pushing (a bot commits Steam news twice an hour); never force-push.
4. **After editing `src/js/` or `src/css/`:** `npx --yes prettier@3.9.10 --write src/js src/css`, then a new `?v=` for each changed file in `src/index.html`.
5. **A new or renamed data key:** a line in `docs/DATA_REFERENCE.md`, then `python3 tools/check_shape.py --update` (read what it prints).
6. **Pictures** go in the matching `assets/` subfolder, `.webp` preferred, lowercase names with hyphens. Picture quality comes before file size.
7. **Record your work** in `CHANGELOG.md` and, if it changes what's open, `docs/library/STATUS.md`.

Leave notes here or in the CHANGELOG whenever you like; I'll read them.
