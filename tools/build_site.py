"""Assemble the publishable site into an empty folder, exactly as GitHub Pages will serve it.

Published: routes/ (the pages), src/js and src/css (as /js and /css), assets/ and data/.
Not published: docs/, inbox/, sources/, tools/ and the Markdown notes (they stay in the repository only).
Usage: python3 tools/build_site.py --output /tmp/relink-site
"""
import argparse
from pathlib import Path
import shutil
from build_routes import SITE_URL, entries

ROOT = Path(__file__).resolve().parent.parent
SKIP = shutil.ignore_patterns('.gitkeep', '__pycache__', '*.pyc')


def build(output):
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Build outside the repository, so generated files never end up in a commit')
    if output.exists() and any(output.iterdir()):
        raise ValueError(f'Output must be empty: {output}')
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'routes', output, dirs_exist_ok=True, ignore=SKIP)
    for name in ('js', 'css'):
        shutil.copytree(ROOT / 'src' / name, output / name, ignore=SKIP)
    for name in ('assets', 'data'):
        shutil.copytree(ROOT / name, output / name, ignore=SKIP)
    (output / '.nojekyll').write_text('')
    # Every page for search engines (the address to give Google Search Console: <site>/sitemap.xml)
    routes = sorted(p.parent.relative_to(ROOT / 'routes').as_posix() for p, _ in entries() if p.name == 'index.html')
    urls = [SITE_URL + ('' if r == '.' else r + '/') for r in routes]
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                        + ''.join(f' <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
    print(f'Site assembled: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    build(parser.parse_args().output)
