"""Bring tier lists from the Tier List Editor into data/game.json (TIER_LIST).

    python3 tools/import_tiers.py inbox/tiers.json [--add-missing] [--dry-run]

The file is what the editor's "Copy for the guide" button gives: {"tiers": [...], "lists": [...]}.
- Replaces TIER_LIST with it. A list whose placements changed gets `updated` = today; unchanged lists keep their date.
- Every placed name must be a character in data/game.json. Missing ones stop the import, unless --add-missing adds
  them as empty characters (name, slug, today's date): nothing else about them is invented.
- Prints what changed per list (who moved where), so it can be checked with David before committing.
Then: python3 tools/check_all.py (the first lists or characters change the data shape: AGENTS.md golden rule 4).
Only ratings agreed with David are imported (AGENTS.md data rule 2): the editor is his.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / 'data' / 'game.json'


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def placements(lst):
    return {name: tier for tier, names in lst.get('rows', {}).items() for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file', type=Path)
    parser.add_argument('--add-missing', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='show the changes, write nothing')
    a = parser.parse_args()
    new = json.loads(a.file.read_text(encoding='utf-8'))
    new = new.get('TIER_LIST', new)
    if not isinstance(new.get('tiers'), list) or not isinstance(new.get('lists'), list):
        sys.exit('Not an editor export: expected {"tiers": [...], "lists": [...]}')
    game = json.loads(GAME.read_text(encoding='utf-8'))
    today = date.today().isoformat()

    names = {c['name'] for c in game['CHARACTERS']}
    placed = {n for lst in new['lists'] for n in placements(lst)}
    missing = sorted(placed - names)
    if missing and not a.add_missing:
        sys.exit('Not characters in data/game.json yet: ' + ', '.join(missing) + '\nCheck the spelling, or rerun with --add-missing.')
    slugs = {c.get('slug') for c in game['CHARACTERS']}
    for name in missing:
        slug = slugify(name)
        while slug in slugs:
            slug += '-2'
        slugs.add(slug)
        game['CHARACTERS'].append({'name': name, 'slug': slug, 'updated': today})
        print(f'+ character {name} (/characters/{slug})')

    old_lists = {lst['id']: lst for lst in game['TIER_LIST'].get('lists', [])}
    lists = []
    for lst in new['lists']:
        entry = {'id': lst['id'], 'label': lst['label']}
        if lst.get('about'):
            entry['about'] = lst['about']
        entry['rows'] = {tier: names_ for tier, names_ in lst.get('rows', {}).items() if names_}
        old = old_lists.get(lst['id'])
        before, after = placements(old or {}), placements(entry)
        changes = [f'  {n}: {before.get(n, "-")} -> {after.get(n, "-")}' for n in sorted(set(before) | set(after)) if before.get(n) != after.get(n)]
        order_changed = old is not None and old.get('rows') != entry['rows'] and not changes
        if old is None or changes or order_changed:
            entry['updated'] = today
            print(f'{"New" if old is None else "Changed"} list {entry["label"]} ({entry["id"]})' + (' (order inside tiers)' if order_changed else ''))
            if changes:
                print('\n'.join(changes))
        elif old.get('updated'):
            entry['updated'] = old['updated']
        lists.append(entry)
    for gone in set(old_lists) - {lst['id'] for lst in lists}:
        print(f'Removed list {old_lists[gone]["label"]} ({gone})')

    if game['TIER_LIST'].get('tiers') != new['tiers']:
        print('Tiers: ' + ', '.join(f'{t["name"]} {t["color"]}' for t in new['tiers']))
    game['TIER_LIST'] = {'tiers': new['tiers'], 'lists': lists}
    if a.dry_run:
        print('Dry run: nothing written.')
        return
    game['meta']['updated'] = today
    GAME.write_text(json.dumps(game, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_routes.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'validate_data.py')])
    print('Imported. Next: python3 tools/check_all.py')


if __name__ == '__main__':
    main()
