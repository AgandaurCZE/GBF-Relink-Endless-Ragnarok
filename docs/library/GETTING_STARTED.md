# Getting started: your first content sessions

Back to the library: [README.md](../README.md). Written for David, 17 Nov 2026. Everything here already works; nothing needs setting up.

## The loop
1. **Play and collect.** Screenshots, notes, numbers. Drop them into `inbox/` (any names, a folder per session helps: `inbox/2026-11-20 Katalina/`). A chat message works too.
2. **Measure in the Test Notebook** (https://claude.ai/artifact/3TRUSLHHo3JA7FLkcD8EPX). Make a test once ("Skill damage", fields `Skill`, `Damage`, `Cooldown [s]`), then add an entry each time you measure, by typing or by voice ("Katalina, skill 1, damage 12345, cooldown 12, save"). The summary under the table gives lowest, average and highest per character.
3. **Ask an AI to process it.** Something like "process the inbox" or "add Katalina from the inbox". It reads `AGENTS.md`, saves the numbers, makes the pictures (`tools/inbox_images.py`), builds the character or guide page (`tools/scaffold.py`), runs the checks and pushes. Nothing goes live unless GitHub's checks pass.
4. **Rate in the Tier List Editor** (https://claude.ai/artifact/NcqRc5BJkia6KCAPyz2pVN) once we've discussed the ratings. "Copy for the guide", paste it into the chat or `inbox/tiers.json`; the AI shows who moved where before importing.

## What to decide first (open questions in [STATUS.md](STATUS.md))
- Which pages matter most, so the first data goes there.
- What the tier list rates: one overall list, or several (by difficulty, solo/co-op, role). The editor and the site already handle several.

## Good to know
- **The site:** https://agandaurcze.github.io/GBF-Relink-Endless-Ragnarok/. On a phone: Android shows "Install app"; on iPhone use Safari → Share → "Add to Home Screen". It works offline once opened.
- **News and Patch Notes** update themselves from Steam twice an hour. Each character page lists the official posts that mention them.
- **Search:** press `/` anywhere on the site.
- **If a publish is red** on the Actions tab, the live site stays on the last good version; ask an AI to fix it.
- **Undo** is always possible: every change is a commit (`git revert`), and the CHANGELOG says what changed.
