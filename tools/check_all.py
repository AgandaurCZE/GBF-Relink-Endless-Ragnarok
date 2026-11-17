"""Run every check. THE command to run before every commit.

    python3 tools/check_all.py                 everything (under a minute)
    python3 tools/check_all.py --no-browser    skip the browser check (data-only work on a machine without Playwright)
    python3 tools/check_all.py --base REF      compare the ?v= cache numbers against REF instead of the last commit

GitHub runs this same script on every push to main (.github/workflows/deploy.yml) and publishes the site only if it
passes. A commit that fails here does not go live: fix it, don't work around it.

What runs, in order (most are also scripts you can run alone):
  1. data rules        tools/validate_data.py      names, references and image paths in data/game.json make sense
  2. data shape        tools/check_shape.py        no misspelt, misplaced or missing keys; right types
  3. clean URLs        tools/build_routes.py       every page has its generated entry in routes/
  4. file rules        (here)                      LF line endings, JSON format, every css/js file loaded with ?v=,
                                                   files in the right folders, image types and sizes
  5. JS syntax         node --check                every js file parses
  6. cache numbers     (here)                      a changed css/js file has a new ?v= in src/index.html
  7. browser           tools/check_site.py         every page on desktop and phone: no errors, no missing files
  8. formatting        prettier --check            src/js and src/css in the agreed format (a warning, not a failure)

Exit codes: 0 = all passed; 1 = something failed; 2 = everything that ran passed, but a check could not run.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTIER = 'prettier@3.9.10'   # one version for everyone, so the format never flips between machines
JSON_FILES = ['data/game.json', 'data/research.json']   # hand-edited: 1-space indent, real characters
IMAGE_TYPES = {'.webp', '.png', '.jpg', '.jpeg', '.svg', '.gif'}
FONT_TYPES = {'.woff2'}
MAX_ASSET_MB = 5
os.chdir(ROOT)
results = []


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def indent(text, limit=60):
    lines = text.splitlines()
    more = f'\n          ... {len(lines) - limit} more lines' if len(lines) > limit else ''
    return '\n'.join('          ' + l for l in lines[:limit]) + more


def step(name, status, detail=''):
    results.append((name, status))
    print(f'[{status:^7}] {name}' + (f'\n{detail}' if detail and status != 'ok' else ''))


def script(name, args):
    r = run([sys.executable] + args)
    step(name, 'ok' if r.returncode == 0 else 'FAIL', indent((r.stdout + r.stderr).strip()))


def site_files():
    """(path, version) for every stylesheet and script src/index.html loads."""
    html = open('src/index.html', encoding='utf-8').read()
    return re.findall(r'(?:href|src)="((?:css|js)/[^"?]+)(?:\?v=([^"]*))?"', html)


def tracked_files():
    r = run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'])
    return r.stdout.splitlines() if r.returncode == 0 else []


def file_rules():
    bad = []
    files = tracked_files()
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_TYPES | FONT_TYPES or not os.path.isfile(f):
            continue
        try:
            if b'\r' in open(f, 'rb').read():
                bad.append(f'{f}: has CRLF line endings; every text file uses LF')
        except OSError:
            pass
    for f in JSON_FILES:
        raw = open(f, encoding='utf-8').read()
        try:
            if json.dumps(json.loads(raw), ensure_ascii=False, indent=1) + '\n' != raw:
                bad.append(f'{f}: not in the agreed format. Rewrite it with json.dump(d, f, ensure_ascii=False, indent=1) plus a final newline')
        except ValueError as e:
            bad.append(f'{f}: not valid JSON: {e}')
    try:
        json.load(open('data/steam-news.json', encoding='utf-8'))
    except ValueError as e:
        bad.append(f'data/steam-news.json: not valid JSON: {e}')
    linked = site_files()
    for path, version in linked:
        if not os.path.exists('src/' + path):
            bad.append(f'src/index.html loads {path}, which does not exist')
        if not version:
            bad.append(f'src/index.html loads {path} without ?v=')
    listed = [p for p, _ in linked]
    for f in sorted(glob.glob('src/js/*.js')) + sorted(glob.glob('src/css/*.css')):
        if f.replace(os.sep, '/').removeprefix('src/') not in listed:
            bad.append(f'{f} exists but src/index.html does not load it (delete it or add it)')
    scripts = [p for p in listed if p.startswith('js/')]
    if scripts != sorted(scripts):
        bad.append('src/index.html: the js/ files are not loaded in their numbered order')
    for f in files:
        top, ext = f.split('/')[0], os.path.splitext(f)[1].lower()
        if top == 'assets' and os.path.basename(f) not in ('.gitkeep', 'README.md'):
            if ext not in IMAGE_TYPES | FONT_TYPES:
                bad.append(f'{f}: assets/ holds only pictures and fonts the site shows (other files: data/, sources/ or docs/)')
            elif os.path.isfile(f) and os.path.getsize(f) > MAX_ASSET_MB * 1024 * 1024:
                bad.append(f'{f}: larger than {MAX_ASSET_MB} MB; the site would load slowly. Convert it to .webp')
        if '/' not in f and f.endswith('.html'):
            bad.append(f'{f}: pages belong in src/index.html (edited) and routes/ (generated), not the top folder')
    step('file rules', 'FAIL' if bad else 'ok', indent('\n'.join(bad)))


def js_syntax():
    if not shutil.which('node'):
        return step('JS syntax', 'not run', '          node is not installed')
    bad = [r.stderr.strip() for r in (run(['node', '--check', f]) for f in sorted(glob.glob('src/js/*.js'))) if r.returncode]
    step('JS syntax', 'FAIL' if bad else 'ok', indent('\n'.join(bad)))


def cache_numbers(base):
    """A changed css/js file needs a new ?v=, or returning visitors keep the old copy for a while."""
    if run(['git', 'cat-file', '-e', f'{base}^{{commit}}']).returncode:
        return step('cache numbers', 'not run', f'          git cannot read commit {base!r} here (shallow clone?)')
    old_html = run(['git', 'show', f'{base}:src/index.html'])
    if old_html.returncode:
        return step('cache numbers', 'ok')   # the site didn't exist at that commit: nothing to compare yet
    old = dict(re.findall(r'(?:href|src)="((?:css|js)/[^"?]+)\?v=([^"]*)"', old_html.stdout))
    bad = []
    for path, version in site_files():
        previous = run(['git', 'show', f'{base}:src/{path}'])
        if previous.returncode == 0 and previous.stdout != open('src/' + path, encoding='utf-8').read() and old.get(path) == version:
            bad.append(f'{path} changed since {base}, but its ?v= is still {version}: give it a new value in src/index.html')
    step('cache numbers', 'FAIL' if bad else 'ok', indent('\n'.join(bad)))


def browser():
    if '--no-browser' in sys.argv:
        return step('browser', 'not run', '          skipped with --no-browser; GitHub runs it before publishing')
    r = run([sys.executable, 'tools/check_site.py'])
    step('browser', {0: 'ok', 2: 'not run'}.get(r.returncode, 'FAIL'), indent((r.stdout + r.stderr).strip()))


def formatting():
    npx = shutil.which('npx')
    if not npx:
        return step('formatting', 'not run', '          npx is not installed')
    r = run([npx, '--yes', PRETTIER, '--check', 'src/js', 'src/css'])
    if r.returncode == 0:
        return step('formatting', 'ok')
    files = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith('[warn]')]
    step('formatting', 'warn', indent('\n'.join(files) + f'\nFix: npx --yes {PRETTIER} --write src/js src/css'))


def main():
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'HEAD'
    script('data rules', ['tools/validate_data.py'])
    script('data shape', ['tools/check_shape.py'])
    script('clean URLs', ['tools/build_routes.py', '--check'])
    file_rules()
    js_syntax()
    cache_numbers(base)
    browser()
    formatting()
    failed = [n for n, s in results if s == 'FAIL']
    skipped = [n for n, s in results if s == 'not run']
    print()
    if failed:
        print(f'CHECKS FAILED: {", ".join(failed)}. Do not commit until they pass.')
        return 1
    if skipped:
        print(f'Passed, but NOT RUN: {", ".join(skipped)}. GitHub runs them all before publishing; check the result of your push.')
        return 2
    print('ALL CHECKS PASSED.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
