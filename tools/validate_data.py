"""Data rules: do the names, references, numbers and image paths in data/game.json make sense?

Run from anywhere:   python3 tools/validate_data.py
Exits with 1 and lists every problem if anything is wrong. check_all.py runs it.
Add a rule here whenever a new kind of data arrives (a new cross-reference, a value with a fixed set of options).
"""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
problems = []


def bad(message):
    problems.append(message)


def unique(items, key, where):
    seen = set()
    for item in items:
        value = item.get(key)
        if not value:
            bad(f'{where}: an entry has no {key!r}')
        elif value in seen:
            bad(f'{where}: {key} {value!r} appears twice')
        seen.add(value)
    return seen


def asset_paths(value, where):
    """Every string that looks like a file in assets/ must exist."""
    if isinstance(value, dict):
        for k, v in value.items():
            asset_paths(v, f'{where}.{k}')
    elif isinstance(value, list):
        for i, v in enumerate(value):
            asset_paths(v, f'{where}[{i}]')
    elif isinstance(value, str) and value.startswith('assets/'):
        if not (ROOT / value).is_file():
            bad(f'{where}: missing file {value!r}')


d = json.loads((ROOT / 'data' / 'game.json').read_text(encoding='utf-8'))

# SITE: every page has a unique id and route; the first page is the home page at the root
pages = d['SITE']['pages']
unique(pages, 'id', 'SITE.pages')
routes = [p['route'] for p in pages]
if len(set(routes)) != len(routes):
    bad('SITE.pages: two pages share a route')
if not pages or pages[0]['id'] != 'home' or pages[0]['route'] != '':
    bad('SITE.pages: the first page must be {"id": "home", "route": ""}')
for p in pages:
    if p['route'] and not re.fullmatch(r'[a-z0-9-]+(/[a-z0-9-]+)*', p['route']):
        bad(f'SITE.pages[{p["id"]}]: route {p["route"]!r} may use only lowercase letters, digits, - and /')

# CHARACTERS, tier list, guides, tools
names = unique(d['CHARACTERS'], 'name', 'CHARACTERS')
tiers = unique(d['TIER_LIST']['tiers'], 'name', 'TIER_LIST.tiers')
for name, tier in d['TIER_LIST']['ratings'].items():
    if name not in names:
        bad(f'TIER_LIST.ratings: {name!r} is not in CHARACTERS')
    if tier not in tiers:
        bad(f'TIER_LIST.ratings[{name}]: tier {tier!r} is not in TIER_LIST.tiers')
unique(d['GUIDES'], 'id', 'GUIDES')
unique(d['TOOLS'], 'id', 'TOOLS')

asset_paths(d, 'game.json')

if problems:
    print(f'{len(problems)} problem(s) in data/game.json:\n' + '\n'.join(problems))
    sys.exit(1)
print('Data rules OK.')
