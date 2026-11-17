"""Browser check: open every page of the assembled site in a real browser, on desktop and phone sizes.

Fails on: a console error or uncaught exception, a file that fails to load, a page showing the wrong title,
in-site navigation that doesn't change the address, or visible text that must never be public (VISIBLE_RULES).
The site is served under /GBF-Relink-Endless-Ragnarok/, the same sub-path GitHub Pages uses.
News, Patch Notes and a character page are also drawn with sample data (a Steam post, a character with every block
type), so those renderers are tested before real content arrives.

    python3 tools/check_site.py
Exit codes: 0 = passed, 1 = failed, 2 = could not run (Playwright or a browser is missing).
"""
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import build  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUBPATH = 'GBF-Relink-Endless-Ragnarok'
VIEWPORTS = {'desktop': dict(width=1280, height=900), 'phone': dict(width=390, height=844)}
# Words a visitor must never see: internal notes belong in docs/ or in a `note` field the page doesn't print.
VISIBLE_RULES = [(re.compile(r'\bDavid\b'), 'the owner\'s name'), (re.compile(r'\bTODO\b'), 'a TODO note'),
                 (re.compile(r'\bundefined\b|\bNaN\b|\[object Object\]'), 'a broken value')]
SAMPLE_POST = dict(id='1', title='Sample announcement', date='2026-01-01', url='https://store.steampowered.com/news/app/881020',
                   body='[h2]Heading[/h2]\n[b]Bold[/b] text [url=https://example.com]link[/url]\n[list][*]one[*]two[/list]\n'
                        '[img]{STEAM_CLAN_IMAGE}/x.png[/img]<script>alert(1)</script>')
SAMPLE_CHARACTER = dict(name='Sample Hero', slug='sample-hero', summary='A sample <b>character</b>.', tabs=[
    dict(id='overview', label='Overview', blocks=[dict(type='text', text='First paragraph.\n\nSecond <script>alert(1)</script>'),
                                                  dict(type='stats', title='Stats', items=[dict(label='HP', value='100')])]),
    dict(id='skills', label='Skills', blocks=[dict(type='table', title='Skills', columns=['Skill', 'Cooldown'], rows=[['Slash', '5 s']]),
                                              dict(type='list', items=['One', 'Two'])])])


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def launch(playwright):
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    try:
        return playwright.chromium.launch()
    except Exception:
        if not chrome:
            raise
        return playwright.chromium.launch(executable_path=chrome)


def visit(page, url, errors, label):
    """Open url; problems found now or later on this page are added to errors."""
    page.on('console', lambda m: m.type == 'error' and errors.append(f'{label}: console error: {m.text}'))
    page.on('pageerror', lambda e: errors.append(f'{label}: uncaught: {e}'))
    page.on('response', lambda r: r.status >= 400 and errors.append(f'{label}: HTTP {r.status}: {r.url}'))
    page.goto(url, wait_until='networkidle')
    page.wait_for_function("document.querySelector('#pageBody') && !/Loading/.test(document.querySelector('#pageBody').textContent)")
    text = page.inner_text('body')
    for pattern, what in VISIBLE_RULES:
        if pattern.search(text):
            errors.append(f'{label}: visible text contains {what}: {pattern.search(text)[0]!r}')
    return text


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT RUN: Playwright is not installed (pip install playwright).')
        return 2
    pages = json.loads((ROOT / 'data' / 'game.json').read_text(encoding='utf-8'))['SITE']['pages']
    errors = []
    with TemporaryDirectory(prefix='relink_check_') as tmp:
        build(Path(tmp) / SUBPATH)
        sample_dir = Path(tmp) / 'sample' / SUBPATH
        build(sample_dir)
        (sample_dir / 'data' / 'steam-news.json').write_text(json.dumps(
            dict(posts=[SAMPLE_POST], patches=[dict(SAMPLE_POST, id='2', title='Ver. 9.9.9 Update Information', version='9.9.9')])))
        game = json.loads((sample_dir / 'data' / 'game.json').read_text(encoding='utf-8'))
        game['CHARACTERS'] = [SAMPLE_CHARACTER]
        (sample_dir / 'data' / 'game.json').write_text(json.dumps(game))
        entry = (ROOT / 'src' / 'index.html').read_text(encoding='utf-8').replace('<base href="./">', '<base href="../../">', 1)
        (sample_dir / 'characters' / 'sample-hero').mkdir(parents=True)
        (sample_dir / 'characters' / 'sample-hero' / 'index.html').write_text(entry, encoding='utf-8')
        server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=tmp))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                try:
                    browser = launch(p)
                except Exception as e:
                    print(f'NOT RUN: no browser could start ({e}).')
                    return 2
                for size, viewport in VIEWPORTS.items():
                    for spec in pages:
                        page = browser.new_page(viewport=viewport)
                        url = f'{base}/{SUBPATH}/{spec["route"]}'
                        visit(page, url, errors, f'{size} /{spec["route"]}')
                        title = page.inner_text('#pageTitle')
                        expected = spec['label'] if spec['id'] != 'home' else None
                        if expected and title != expected:
                            errors.append(f'{size} /{spec["route"]}: shows {title!r}, expected {expected!r}')
                        page.close()
                # In-site navigation: clicking a menu item changes the address without reloading
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/{SUBPATH}/', errors, 'navigation')
                for spec in pages[1:]:
                    page.click(f'.nav-item[data-page="{spec["id"]}"]')
                    if not page.url.rstrip('/').endswith(f'/{SUBPATH}/{spec["route"]}'.rstrip('/')):
                        errors.append(f'navigation: clicking {spec["label"]} went to {page.url}')
                page.go_back()
                if page.inner_text('#pageTitle') != pages[-2]['label']:
                    errors.append('navigation: the Back button did not return to the previous page')
                page.close()
                # News renderer with a sample post: tags become HTML, scripts never run
                for route in ('news', 'patch-notes'):
                    page = browser.new_page(viewport=VIEWPORTS['desktop'])
                    page.on('dialog', lambda d: (errors.append('sample post: a script inside a post ran'), d.dismiss()))
                    visit(page, f'{base}/sample/{SUBPATH}/{route}', errors, f'sample /{route}')
                    page.click('.post summary')
                    if not page.query_selector('.post-body b') or not page.query_selector('.post-body li'):
                        errors.append(f'sample /{route}: BBCode was not turned into HTML')
                    if page.query_selector('.post-body script'):
                        errors.append(f'sample /{route}: a <script> from a post reached the page')
                    page.close()
                # Not-found page (GitHub Pages serves 404.html for any unknown address)
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/{SUBPATH}/404.html', errors, 'not found')
                if page.inner_text('#pageTitle') != 'Page not found' or not page.query_selector('.nav-item'):
                    errors.append('not found: 404.html does not show the "Page not found" page with the menu')
                page.close()
                # Search: finds the sample character and news, opens a result, clears the box
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/sample/{SUBPATH}/', errors, 'search')
                for query, expected in (('sample hero', {'Character'}), ('heading bold', {'News', 'Patch notes'})):
                    page.fill('#search', query)
                    kinds = page.eval_on_selector_all('.result .muted', 'els => els.map(e => e.textContent)')
                    if not expected <= set(kinds):
                        errors.append(f'search: {query!r} should find {sorted(expected)}; found {kinds}')
                page.fill('#search', 'zzzz-nothing')
                if 'Nothing found' not in page.inner_text('#pageBody'):
                    errors.append('search: a search with no results does not say so')
                page.fill('#search', 'sample hero')
                page.click('.result')
                if page.inner_text('#pageTitle') != 'Sample Hero' or page.input_value('#search'):
                    errors.append('search: opening a result did not open the page and clear the box')
                page.fill('#search', '')
                if page.inner_text('#pageTitle') != 'Sample Hero':
                    errors.append('search: clearing the box did not bring back the page')
                page.close()
                # Character page: the card opens it, tabs switch and land in the address, a direct link opens a tab
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/sample/{SUBPATH}/characters', errors, 'sample character')
                page.click('.character')
                if not page.url.endswith('/characters/sample-hero') or page.inner_text('#pageTitle') != 'Sample Hero':
                    errors.append(f'sample character: the card did not open the character page ({page.url})')
                page.click('.profile-tab[data-tab="skills"]')
                if not page.url.endswith('#skills') or not page.is_visible('.profile-panel[data-tab="skills"] table'):
                    errors.append('sample character: the Skills tab did not open')
                if page.query_selector('.profile-panel script, .profile-head b'):
                    errors.append('sample character: HTML from the data reached the page unescaped')
                page.click('.back-link')
                if page.inner_text('#pageTitle') != 'Characters':
                    errors.append('sample character: "All characters" did not go back')
                page.close()
                for size, viewport in VIEWPORTS.items():
                    page = browser.new_page(viewport=viewport)
                    visit(page, f'{base}/sample/{SUBPATH}/characters/sample-hero#skills', errors, f'sample character {size}')
                    if not page.is_visible('.profile-panel[data-tab="skills"] .stats, .profile-panel[data-tab="skills"] li'):
                        errors.append(f'sample character {size}: a direct link to #skills did not open that tab')
                    page.close()
                browser.close()
        finally:
            server.shutdown()
    if errors:
        print('Browser check failed:\n' + '\n'.join(errors))
        return 1
    print(f'Browser check OK: {len(pages)} pages on {len(VIEWPORTS)} screen sizes, navigation, the news renderer, a character page, search and 404.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
