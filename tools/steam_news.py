"""Refresh data/steam-news.json from the official Steam announcements of Granblue Fantasy: Relink.

Endless Ragnarok is sold on Steam as an upgrade of the base game, so its announcements and update notes are posted
on the base game's page (app 881020). Posts whose title carries a version ("Ver. 2.0.6 Update Information") go to
`patches`, everything else to `posts`.

The GitHub workflow .github/workflows/steam-news.yml runs this twice an hour and commits any change.
    python3 tools/steam_news.py                     fetch from Steam (needs internet)
    python3 tools/steam_news.py --input saved.json  replay a saved Steam API response (for testing)

When Steam doesn't answer (network, timeout, 429, 5xx) it retries three times, then leaves the feed as it is and ends
with a warning, not an error: the next run tries again. A changed or broken feed, or a feed suddenly much shorter
than the one we have, still fails, so it shows up red on the Actions tab.

Later, when the guide knows the characters, this is the place to read balance changes out of the update notes
(the DragonSword guide does this in tools/apply_patch_skills.py).
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
APP = 881020
CHANNEL = 'steam_community_announcements'
API = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/'
VERSION = re.compile(r'\bVer(?:sion)?\.?\s*(\d+\.\d+\.\d+)\b', re.I)
SOURCES = {'steamstore-a.akamaihd.net', 'store.steampowered.com', 'steamcommunity.com', 'clan.akamai.steamstatic.com'}


class SteamUnavailable(Exception):
    """Steam did not answer (network, timeout, 429 or 5xx) even after retrying: try again at the next run."""


def get_page(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=30) as response:
                return json.load(response)['appnews']
        except HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
            error = e
        except (URLError, TimeoutError, ConnectionError) as e:
            error = e
        time.sleep(10 * (attempt + 1))
    raise SteamUnavailable(str(error))


def fetch():
    posts, cursor = {}, None
    for _ in range(40):
        query = dict(appid=APP, feeds=CHANNEL, count=50, maxlength=0)
        if cursor is not None:
            query['enddate'] = cursor
        result = get_page(f'{API}?{urlencode(query)}')
        if int(result['appid']) != APP:
            raise ValueError('Steam answered for a different app')
        page = result['newsitems']
        posts.update((item['gid'], item) for item in page)
        if len(page) < 50:
            return list(posts.values())
        before = min(item['date'] for item in page) + 1   # same paging as the DragonSword guide; repeats are merged
        if cursor is not None and before >= cursor:
            break
        cursor = before
    raise ValueError('Steam pagination did not finish')


def make_feed(items):
    """One patch per version. When several posts name the same version ("Important Notice (Ver. 2.0.3)" and
    "Ver. 2.0.3 Update Information"), the one whose title says "Update" is the patch note; the rest are news."""
    news, patches, versions = [], [], set()
    is_update = lambda x: bool(re.search(r'\bupdate\b', x['title'], re.I))
    for item in sorted(items, key=lambda x: (is_update(x), x['date'], str(x['gid'])), reverse=True):
        if int(item['appid']) != APP or item.get('feedname') != CHANNEL:
            continue
        ident, title, body = str(item['gid']), item['title'].strip(), item['contents'].strip()
        if not ident.isdecimal() or not title or not body:
            raise ValueError(f'Steam post {ident!r} is missing its ID, title or body')
        if urlsplit(item['url']).scheme != 'https' or urlsplit(item['url']).netloc not in SOURCES:
            raise ValueError(f'Unexpected source URL in the official Steam feed: {item["url"]}')
        post = dict(id=ident, title=title, date=datetime.fromtimestamp(item['date'], timezone.utc).date().isoformat(),
                    url=item['url'], body=body)
        match = VERSION.search(title)
        if match and match[1] not in versions:
            versions.add(match[1])
            patches.append(dict(post, version=match[1]))
        else:
            news.append(post)
    if not news and not patches:
        raise ValueError('Steam returned no announcements')
    newest = lambda x: (x['date'], int(x['id']))
    return dict(posts=sorted(news, key=newest, reverse=True), patches=sorted(patches, key=newest, reverse=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Replay a saved Steam API response')
    parser.add_argument('--output', type=Path, default=ROOT / 'data' / 'steam-news.json')
    options = parser.parse_args()
    try:
        items = json.loads(options.input.read_text(encoding='utf-8'))['appnews']['newsitems'] if options.input else fetch()
    except SteamUnavailable as e:
        # A Steam outage is not our error: keep the current feed, show a warning on the run, and try at the next run.
        print(f'::warning::Steam did not answer ({e}); the news feed was left as it is.')
        sys.exit(0)
    feed = make_feed(items)
    if options.output.exists():
        old = json.loads(options.output.read_text(encoding='utf-8'))
        before, after = len(old.get('posts', [])) + len(old.get('patches', [])), len(feed['posts']) + len(feed['patches'])
        if after < before - 5:
            raise ValueError(f'Steam returned {after} posts, {before - after} fewer than the {before} we have: not overwriting. '
                             'Check the feed by hand; if posts were really removed, delete data/steam-news.json once and rerun.')
    temporary = options.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(feed, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
    temporary.replace(options.output)
    print(f"Steam feed: {len(feed['posts'])} news posts and {len(feed['patches'])} patches")


if __name__ == '__main__':
    main()
