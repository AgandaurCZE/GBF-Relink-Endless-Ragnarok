"""Data shape: is every key in the data files one the site knows, at the right place, with the right type?

tools/validate_data.py checks that values make sense. This check catches what it can't: a misspelt key ("teir"),
a key at the wrong level, a field every other entry has but this one lacks, a number typed as text.

    python3 tools/check_shape.py             compare the data files with the recorded shape (tools/data_shape.json)
    python3 tools/check_shape.py --update    record the current shape, after you added or changed a key ON PURPOSE

Rule for --update: read the differences it prints. Every line must be a change you meant and documented in
docs/DATA_REFERENCE.md. Never run --update just to make an error go away.
Adding entries (one more character, guide, patch) needs no update. The first entry of an empty list defines its
shape, so record it with --update.

How the shape is written (tools/data_shape.json, generated; don't edit by hand):
    {"types": [...]}            allowed JSON types: string, number, bool, null
    {"record": {"req", "opt"}}  an object with fixed keys: `req` must be there, `opt` may be, anything else is an error
    {"map": shape}              an object whose keys are data (character names ...): every value has this shape
    {"list": shape}             a list whose items all have this shape; {"list": null} = no items recorded yet
"""
import difflib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SHAPE_FILE = ROOT / 'tools' / 'data_shape.json'
FILES = ['data/game.json', 'data/steam-news.json']   # every data file the site reads
MAPS = {'TIER_LIST.lists[].rows'}                   # objects whose keys are data, not field names


def kind(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'bool'
    if isinstance(v, (int, float)):
        return 'number'
    if isinstance(v, str):
        return 'string'
    return 'list' if isinstance(v, list) else 'object'


def merge(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if 'types' in a and 'types' in b:
        return {'types': sorted(set(a['types']) | set(b['types']))}
    if 'list' in a and 'list' in b:
        return {'list': merge(a['list'], b['list'])}
    if 'map' in a and 'map' in b:
        return {'map': merge(a['map'], b['map'])}
    if 'record' in a and 'record' in b:
        ka = {**a['record']['req'], **a['record']['opt']}
        kb = {**b['record']['req'], **b['record']['opt']}
        req = {k: merge(ka[k], kb[k]) for k in a['record']['req'] if k in b['record']['req']}
        opt = {k: merge(ka.get(k), kb.get(k)) for k in sorted(set(ka) | set(kb)) if k not in req}
        return {'record': {'req': req, 'opt': opt}}
    raise ValueError(f'Mixed kinds in one place: {json.dumps(a)[:80]} vs {json.dumps(b)[:80]}')


def infer(value, path):
    k = kind(value)
    if k == 'list':
        shape = None
        for i, item in enumerate(value):
            shape = merge(shape, infer(item, f'{path}[]'))
        return {'list': shape}
    if k == 'object':
        if path in MAPS:
            shape = None
            for item in value.values():
                shape = merge(shape, infer(item, f'{path}{{}}'))
            return {'map': shape}
        return {'record': {'req': {key: infer(v, f'{path}.{key}'.lstrip('.')) for key, v in value.items()}, 'opt': {}}}
    return {'types': [k]}


def check(value, shape, path, errors):
    k = kind(value)
    where = path or '(top level)'
    if shape is None:
        return
    if 'types' in shape:
        if k not in shape['types']:
            errors.append(f'{where}: is {k}, expected {" or ".join(shape["types"])}')
    elif 'list' in shape:
        if k != 'list':
            errors.append(f'{where}: is {k}, expected a list')
        elif shape['list'] is None and value:
            errors.append(f'{where}[]: first entries in a list with no recorded shape; check them, then run --update')
        else:
            for item in value:
                check(item, shape['list'], f'{path}[]', errors)
    elif 'map' in shape:
        if k != 'object':
            errors.append(f'{where}: is {k}, expected an object')
        else:
            for item in value.values():
                check(item, shape['map'], f'{path}{{}}', errors)
    else:
        if k != 'object':
            return errors.append(f'{where}: is {k}, expected an object')
        req, opt = shape['record']['req'], shape['record']['opt']
        for key in req:
            if key not in value:
                errors.append(f'{where}: missing key {key!r}')
        for key, v in value.items():
            if key not in req and key not in opt:
                errors.append(f'{where}: unknown key {key!r} (misspelt, misplaced, or new: then --update)')
            else:
                check(v, req.get(key, opt.get(key)), f'{path}.{key}'.lstrip('.'), errors)


def current():
    return {f: infer(json.loads((ROOT / f).read_text(encoding='utf-8')), '') for f in FILES}


def main():
    recorded = json.loads(SHAPE_FILE.read_text(encoding='utf-8')) if SHAPE_FILE.exists() else {}
    if '--update' in sys.argv:
        new = current()
        merged = {f: (merge(recorded.get(f), new[f]) if '--fresh' not in sys.argv else new[f]) for f in FILES}
        old_text = json.dumps(recorded, indent=1, sort_keys=True).splitlines()
        new_text = json.dumps(merged, indent=1, sort_keys=True).splitlines()
        diff = [l for l in difflib.unified_diff(old_text, new_text, 'recorded', 'new', lineterm='', n=1)]
        SHAPE_FILE.write_text(json.dumps(merged, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
        print('\n'.join(diff) if diff else 'No shape changes.')
        print('Recorded. Read every line above: each must be a change you meant.')
        return 0
    errors = []
    for f in FILES:
        if f not in recorded:
            errors.append(f'{f}: not in tools/data_shape.json yet (new data file: run --update)')
            continue
        check(json.loads((ROOT / f).read_text(encoding='utf-8')), recorded[f], '', file_errors := [])
        errors += [f'{f}: {e}' for e in file_errors]
    if errors:
        print('Data shape differs from tools/data_shape.json:\n' + '\n'.join(errors))
        return 1
    print('Data shape OK.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
