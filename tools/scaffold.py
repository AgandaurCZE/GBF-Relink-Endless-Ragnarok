"""Add an empty character or guide to data/game.json, ready to be filled. No numbers or text are made up: it only
creates the entry with its name, address and (optionally) empty tabs, then regenerates the page addresses.

    python3 tools/scaffold.py character "Katalina" [--slug katalina] [--image assets/characters/katalina.webp]
                                                    [--tabs "Overview,Skills,Build"]
    python3 tools/scaffold.py guide "Early game route" [--id early-game-route] [--summary "One line for the list"]

Then fill the entry (docs/DATA_REFERENCE.md, "Blocks"), and run python3 tools/check_all.py.
The FIRST character or guide with a new set of keys changes the data shape: the checks will say so; read
AGENTS.md golden rule 4 and run python3 tools/check_shape.py --update once the entry is filled in.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('kind', choices=['character', 'guide'])
    parser.add_argument('name')
    parser.add_argument('--slug', help='character address: /characters/<slug>')
    parser.add_argument('--id', help='guide address: /guides/<id>')
    parser.add_argument('--image')
    parser.add_argument('--tabs', help='comma-separated tab names, e.g. "Overview,Skills,Build"')
    parser.add_argument('--summary', default='')
    a = parser.parse_args()
    game = json.loads(GAME.read_text(encoding='utf-8'))
    if a.kind == 'character':
        slug = a.slug or slugify(a.name)
        if any(c['name'] == a.name or c.get('slug') == slug for c in game['CHARACTERS']):
            sys.exit(f'A character named {a.name!r} or with the slug {slug!r} already exists.')
        entry = {'name': a.name, 'slug': slug}
        if a.image:
            if not (ROOT / a.image).is_file():
                sys.exit(f'No such picture: {a.image} (make one with tools/inbox_images.py asset)')
            entry['image'] = a.image
        if a.summary:
            entry['summary'] = a.summary
        if a.tabs:
            entry['tabs'] = [{'id': slugify(t), 'label': t.strip(), 'blocks': []} for t in a.tabs.split(',') if t.strip()]
        game['CHARACTERS'].append(entry)
        where = f'/characters/{slug}'
    else:
        gid = a.id or slugify(a.name)
        if any(g['id'] == gid for g in game['GUIDES']):
            sys.exit(f'A guide with the id {gid!r} already exists.')
        game['GUIDES'].append({'id': gid, 'title': a.name, 'summary': a.summary, 'updated': date.today().isoformat()})
        where = f'/guides/{gid} (it gets its own page once it has blocks)'
    game['meta']['updated'] = date.today().isoformat()
    GAME.write_text(json.dumps(game, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_routes.py')], check=True)
    print(f'Added {a.kind} {a.name!r}: {where}. Fill it in data/game.json, then run python3 tools/check_all.py.')


if __name__ == '__main__':
    main()
