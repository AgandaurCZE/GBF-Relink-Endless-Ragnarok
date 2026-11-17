"""Browser check: open every page of the assembled site in a real browser, on desktop and phone sizes.

Fails on: a console error or uncaught exception, a file that fails to load, a page showing the wrong title,
in-site navigation that doesn't change the address, visible text that must never be public (VISIBLE_RULES), or an
accessibility problem (axe-core, WCAG 2 A and AA: contrast, missing labels, ...) on any page in light or dark mode.
The site is served under /GBF-Relink-Endless-Ragnarok/, the same sub-path GitHub Pages uses.
News, Patch Notes and a character page are also drawn with sample data (a Steam post, a character with every block
type), so those renderers are tested before real content arrives.

    python3 tools/check_site.py
Exit codes: 0 = passed, 1 = failed, 2 = could not run (Playwright or a browser is missing).
"""
import functools
import subprocess
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
                   body='[h2]Heading[/h2]\nSample Hero was adjusted.\n[b]Bold[/b] text [url=https://example.com]link[/url]\n[list][*]one[*]two[/list]\n'
                        '[img]{STEAM_CLAN_IMAGE}/x.png[/img]<script>alert(1)</script>')
SAMPLE_CHARACTER = dict(name='Sample Hero', slug='sample-hero', updated='2026-01-02', image='assets/ui/favicon.svg', summary='A sample <b>character</b>.', tabs=[
    dict(id='overview', label='Overview', blocks=[dict(type='text', text='First paragraph.\n\nSecond <script>alert(1)</script>'),
                                                  dict(type='stats', title='Stats', items=[dict(label='HP', value='100')])]),
    dict(id='skills', label='Skills', blocks=[dict(type='table', title='Skills', columns=['Skill', 'Cooldown'], rows=[['Slash', '5 s']]),
                                              dict(type='list', items=['One', 'Two'])]),
    dict(id='build', label='Build', blocks=[])])
SAMPLE_GUIDE = dict(id='sample-guide', title='Sample Guide', summary='A sample guide.', updated='2026-01-01', blocks=[
    dict(type='text', title='First part', text='Text.'), dict(type='note', title='Second part', text='A tip.'),
    dict(type='note', tone='warning', text='A warning.'), dict(type='image', src='assets/ui/og-image.jpg', alt='Sample picture', caption='Caption'),
    dict(type='text', title='Third part', text='More text.')])


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


DEAD_LINKS = """[...document.querySelectorAll('a[data-route]')]
  .map((a) => a.dataset.route)
  .filter((r) => pageForPath(APP_ROOT + r.split('#')[0]).id === 'notfound')
  .concat([...document.querySelectorAll('a[data-anchor]')].map((a) => a.dataset.anchor).filter((id) => !document.getElementById(id)).map((id) => '#' + id))"""


AXE_VERSION = '4.14.1'   # the accessibility checker, installed from npm into a temporary folder for each run


def load_axe(folder):
    """axe-core's script, or None when npm can't install it (then the accessibility part is skipped and said so)."""
    npm = shutil.which('npm')
    if not npm:
        return None
    r = subprocess.run([npm, 'install', '--no-save', '--no-audit', '--no-fund', '--prefix', folder, f'axe-core@{AXE_VERSION}'],
                       capture_output=True, text=True)
    path = Path(folder) / 'node_modules' / 'axe-core' / 'axe.min.js'
    return path.read_text(encoding='utf-8') if r.returncode == 0 and path.exists() else None


def accessibility(page, axe, label, errors):
    page.add_script_tag(content=axe)
    found = page.evaluate("""axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa']}}).then((r) =>
      r.violations.map((v) => `${v.id} (${v.impact}): ${v.help}, at ${v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(' | ')}`))""")
    errors += [f'{label}: accessibility: {f}' for f in found]


def dead_links(page, label, errors):
    """Every in-site link on the page leads to a real page, and every contents link to a real section."""
    for route in page.evaluate(DEAD_LINKS):
        errors.append(f'{label}: link to {route!r} leads to "Page not found"')


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
        game['TIER_LIST'] = dict(tiers=[dict(name='S', color='#f2c45a'), dict(name='A', color='#4fb3ff')], lists=[
            dict(id='overall', label='Overall', about='Sample list.', rows=dict(S=['Sample Hero'], A=[])),
            dict(id='solo', label='Solo', rows=dict(A=['Sample Hero'])), dict(id='empty', label='Empty', rows=dict())])
        game['GUIDES'] = [SAMPLE_GUIDE, dict(id='later', title='Later guide', summary='Not written yet.')]
        (sample_dir / 'data' / 'game.json').write_text(json.dumps(game))
        entry = (ROOT / 'src' / 'index.html').read_text(encoding='utf-8').replace('<base href="./">', '<base href="../../">', 1)
        for route in ('characters/sample-hero', 'guides/sample-guide'):   # direct links to the sample pages
            (sample_dir / route).mkdir(parents=True)
            (sample_dir / route / 'index.html').write_text(entry, encoding='utf-8')
        axe = load_axe(str(Path(tmp) / 'axe'))
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
                        dead_links(page, f'{size} /{spec["route"]}', errors)
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
                # Post links and "New" marks: a link opens its post; posts newer than the last visit are marked
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/sample/{SUBPATH}/patch-notes#v9-9-9', errors, 'post link')
                if not page.eval_on_selector('#v9-9-9', 'e => e.open'):
                    errors.append('post link: /patch-notes#v9-9-9 did not open that patch')
                page.evaluate("localStorage.setItem('seen-news', '2000-01-01')")
                page.goto(f'{base}/sample/{SUBPATH}/news', wait_until='networkidle')
                page.wait_for_selector('.post')
                if not page.query_selector('.badge.new'):
                    errors.append('post link: a post newer than the last visit is not marked "New"')
                page.reload(wait_until='networkidle')
                page.wait_for_selector('.post')
                if page.query_selector('.badge.new'):
                    errors.append('post link: "New" is still shown after the post was seen')
                page.close()
                # Home dashboard with content: latest patch, news, recently updated, characters, and no dead links
                page = browser.new_page(viewport=VIEWPORTS['phone'])
                visit(page, f'{base}/sample/{SUBPATH}/', errors, 'sample home')
                for selector, what in (('.latest', 'the latest patch'), ('.link-list a[data-route^="news#"]', 'the news'),
                                       ('.link-list a[data-route="guides/sample-guide"]', 'a recently updated guide'),
                                       ('.roster .character', 'the character portraits')):
                    if not page.query_selector(selector):
                        errors.append(f'sample home: {what} missing from Home')
                dead_links(page, 'sample home', errors)
                page.close()
                # Light / dark: the switch changes the colours and is remembered after a reload
                page = browser.new_page(viewport=VIEWPORTS['desktop'], color_scheme='dark')
                visit(page, f'{base}/{SUBPATH}/', errors, 'theme')
                background = "getComputedStyle(document.body).backgroundColor"
                dark = page.evaluate(background)
                page.click('#themeBtn')
                light = page.evaluate(background)
                page.reload(wait_until='networkidle')
                if dark == light or page.evaluate(background) != light or page.evaluate('document.documentElement.dataset.theme') != 'light':
                    errors.append('theme: the light/dark switch did not change the colours or was not remembered')
                page.close()
                # Installable app: the worker takes over; offline, an opened page and a never-opened page still work
                context = browser.new_context(viewport=VIEWPORTS['desktop'])
                page = context.new_page()
                visit(page, f'{base}/{SUBPATH}/', errors, 'offline')
                if not page.evaluate("fetch('manifest.webmanifest').then((r) => r.ok)"):
                    errors.append('offline: manifest.webmanifest is not served at the site root')
                ready = "Promise.race([navigator.serviceWorker.ready.then(() => true), new Promise((r) => setTimeout(() => r(false), 8000))])"
                if not page.evaluate(ready):
                    errors.append('offline: the offline worker (sw.js) did not start')
                page.reload(wait_until='networkidle')
                visit(page, f'{base}/{SUBPATH}/characters', errors, 'offline')
                context.set_offline(True)
                for route, title in (('characters', 'Characters'), ('tools', 'Tools')):
                    try:
                        page.goto(f'{base}/{SUBPATH}/{route}', wait_until='load')
                        page.wait_for_function("!/Loading/.test(document.querySelector('#pageBody').textContent)", timeout=5000)
                        if page.inner_text('#pageTitle') != title:
                            errors.append(f'offline: /{route} shows {page.inner_text("#pageTitle")!r} instead of {title!r}')
                    except Exception as e:
                        errors.append(f'offline: /{route} did not open without a connection ({str(e).splitlines()[0]})')
                context.close()
                # Tier list: one tab per list with entries, a tab switches lists, a link opens a list, chips link on
                page = browser.new_page(viewport=VIEWPORTS['phone'])
                visit(page, f'{base}/sample/{SUBPATH}/tierlist#solo', errors, 'sample tier list')
                tabs = page.eval_on_selector_all('.tier-tab', 'els => els.map((e) => e.textContent)')
                if tabs != ['Overall', 'Solo']:
                    errors.append(f'sample tier list: tabs should be Overall and Solo (empty lists hidden); got {tabs}')
                if not page.is_visible('.tier-list[data-list="solo"] .character'):
                    errors.append('sample tier list: /tierlist#solo did not open the Solo list')
                page.click('.tier-tab[data-list="overall"]')
                if not page.url.endswith('#overall') or not page.is_visible('.tier-list[data-list="overall"] .tier-label'):
                    errors.append('sample tier list: the Overall tab did not switch lists')
                dead_links(page, 'sample tier list', errors)
                page.close()
                # Keyboard: "/" focuses search, Esc clears it; "Back to top" shows after scrolling (sample news is long enough)
                page = browser.new_page(viewport=dict(width=1280, height=400))
                visit(page, f'{base}/{SUBPATH}/patch-notes', errors, 'keyboard')
                page.keyboard.press('/')
                if page.evaluate('document.activeElement.id') != 'search':
                    errors.append('keyboard: "/" did not focus the search box')
                page.keyboard.type('ver')
                page.keyboard.press('Escape')
                if page.input_value('#search') or page.inner_text('#pageTitle') != 'Patch Notes':
                    errors.append('keyboard: Esc did not clear the search and bring back the page')
                if page.evaluate('document.body.scrollHeight > 900'):
                    page.evaluate('window.scrollTo(0, 900)')
                    page.wait_for_timeout(300)
                    if not page.is_visible('#toTop'):
                        errors.append('back to top: the button did not appear after scrolling')
                    else:
                        page.click('#toTop')
                        page.wait_for_timeout(800)
                        if page.evaluate('window.scrollY') > 5:
                            errors.append('back to top: the button did not scroll to the top')
                page.close()
                # Accessibility: every page and the sample pages, in dark and light mode
                if axe:
                    routes = [f'{SUBPATH}/{p["route"]}' for p in pages] + [f'sample/{SUBPATH}/{r}' for r in (
                        'characters/sample-hero', 'guides/sample-guide', 'tierlist', '')]
                    for scheme in ('dark', 'light'):
                        for route in routes:
                            page = browser.new_page(viewport=VIEWPORTS['desktop'], color_scheme=scheme)
                            visit(page, f'{base}/{route}', errors, f'{scheme} /{route}')
                            accessibility(page, axe, f'{scheme} /{route}', errors)
                            page.close()
                # Report link: points at the report form with the current page filled in
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/{SUBPATH}/guides', errors, 'report link')
                href = page.get_attribute('#reportLink', 'href')
                if 'template=mistake.yml' not in href or '%2Fguides' not in href:
                    errors.append(f'report link: should open the mistake form for this page; is {href}')
                page.close()
                # Printing: white page, black text, no menu, in both themes
                for scheme in ('dark', 'light'):
                    page = browser.new_page(viewport=VIEWPORTS['desktop'], color_scheme=scheme)
                    visit(page, f'{base}/{SUBPATH}/news', errors, f'print {scheme}')
                    page.emulate_media(media='print')
                    colours = page.evaluate("[getComputedStyle(document.body).backgroundColor, getComputedStyle(document.body).color]")
                    if colours != ['rgb(255, 255, 255)', 'rgb(0, 0, 0)'] or page.is_visible('.sidebar'):
                        errors.append(f'print {scheme}: printing should be black on white without the menu; got {colours}')
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
                dead_links(page, 'search results', errors)
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
                # Guide page: the card opens it, the contents list jumps to a section, every block type draws
                page = browser.new_page(viewport=VIEWPORTS['phone'])
                visit(page, f'{base}/sample/{SUBPATH}/guides', errors, 'sample guide')
                if page.locator('a.card').count() != 1:
                    errors.append('sample guide: only a guide with blocks should link to its own page')
                page.click('a.card')
                if not page.url.endswith('/guides/sample-guide') or page.inner_text('#pageTitle') != 'Sample Guide':
                    errors.append(f'sample guide: the card did not open the guide ({page.url})')
                dead_links(page, 'sample guide', errors)
                page.click('.contents a[data-anchor="third-part"]')
                page.wait_for_timeout(600)
                if not page.url.endswith('#third-part') or not page.locator('#third-part').is_visible():
                    errors.append('sample guide: the contents link did not jump to its section')
                if not (page.query_selector('.note-tip') and page.query_selector('.note-warning') and page.query_selector('figure img[alt="Sample picture"]')):
                    errors.append('sample guide: a note or image block did not draw')
                page.close()
                # Character page: the card opens it, tabs switch and land in the address, a direct link opens a tab
                page = browser.new_page(viewport=VIEWPORTS['desktop'])
                visit(page, f'{base}/sample/{SUBPATH}/characters', errors, 'sample character')
                page.click('.character')
                if not page.url.endswith('/characters/sample-hero') or page.inner_text('#pageTitle') != 'Sample Hero':
                    errors.append(f'sample character: the card did not open the character page ({page.url})')
                dead_links(page, 'sample character', errors)
                if page.locator('.mentions li').count() != 2:
                    errors.append('sample character: the patch note and news post that name the character are not listed')
                page.click('.profile-tab[data-tab="skills"]')
                if not page.url.endswith('#skills') or not page.is_visible('.profile-panel[data-tab="skills"] table'):
                    errors.append('sample character: the Skills tab did not open')
                if page.query_selector('.profile-panel script, .profile-head b'):
                    errors.append('sample character: HTML from the data reached the page unescaped')
                page.click('.profile-tab[data-tab="build"]')
                if 'More coming soon' not in page.inner_text('.profile-panel[data-tab="build"]'):
                    errors.append('sample character: an empty tab does not say "More coming soon"')
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
    a11y = 'accessibility in light and dark' if axe else 'NOT the accessibility part (npm could not install axe-core)'
    print(f'Browser check OK: {len(pages)} pages on {len(VIEWPORTS)} screen sizes, navigation, the news renderer, a character page, a guide, search, 404, {a11y}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
