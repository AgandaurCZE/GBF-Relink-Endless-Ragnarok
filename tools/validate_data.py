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
BLOCKS = {'text': {'text'}, 'list': {'items'}, 'table': {'columns', 'rows'}, 'stats': {'items'}, 'note': {'text'}, 'image': {'src', 'alt'}}
NAME = r'[a-z0-9]+(-[a-z0-9]+)*'


def blocks(items, at):
    for i, b in enumerate(items):
        where = f'{at}.blocks[{i}]'
        if b.get('type') not in BLOCKS:
            bad(f'{where}: type {b.get("type")!r} is not one of {sorted(BLOCKS)}')
        elif not BLOCKS[b['type']] <= set(b):
            bad(f'{where}: a {b["type"]} block needs {sorted(BLOCKS[b["type"]])}')
        elif b['type'] == 'table' and any(len(r) != len(b['columns']) for r in b['rows']):
            bad(f'{where}: every table row needs {len(b["columns"])} cells, one per column')
        elif b['type'] == 'note' and b.get('tone', 'tip') not in ('tip', 'warning'):
            bad(f'{where}: tone must be "tip" or "warning"')
        elif b['type'] == 'image' and (not str(b['src']).startswith('assets/') or not str(b['alt']).strip()):
            bad(f'{where}: an image needs src in assets/ and an alt text describing it')


slugs = set()
for c in d['CHARACTERS']:
    where = f'CHARACTERS[{c.get("name")}]'
    slug = c.get('slug')
    if slug is not None:
        if not re.fullmatch(NAME, slug):
            bad(f'{where}: slug {slug!r} must be lowercase letters and digits with hyphens (katalina, sandalphon-alt)')
        if slug in slugs:
            bad(f'{where}: slug {slug!r} is used twice')
        slugs.add(slug)
    tab_ids = set()
    for t in c.get('tabs', []):
        if t.get('id') in tab_ids or not re.fullmatch(NAME, t.get('id', '')):
            bad(f'{where}: tab id {t.get("id")!r} is missing, repeated or not lowercase-with-hyphens')
        tab_ids.add(t.get('id'))
        blocks(t.get('blocks', []), f'{where}.tabs[{t.get("id")}]')
for g in d['GUIDES']:
    if not re.fullmatch(NAME, str(g.get('id', ''))):
        bad(f'GUIDES[{g.get("id")}]: id must be lowercase letters and digits with hyphens (it is the address /guides/<id>)')
    if g.get('updated') and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', g['updated']):
        bad(f'GUIDES[{g.get("id")}]: updated must be a date YYYY-MM-DD')
    blocks(g.get('blocks', []), f'GUIDES[{g.get("id")}]')
unique(d['GUIDES'], 'id', 'GUIDES')
unique(d['TOOLS'], 'id', 'TOOLS')

asset_paths(d, 'game.json')

if problems:
    print(f'{len(problems)} problem(s) in data/game.json:\n' + '\n'.join(problems))
    sys.exit(1)
print('Data rules OK.')
