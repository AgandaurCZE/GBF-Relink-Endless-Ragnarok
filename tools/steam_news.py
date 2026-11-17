"""Refresh data/steam-news.json from the official Steam announcements of Granblue Fantasy: Relink.

Endless Ragnarok is sold on Steam as an upgrade of the base game, so its announcements and update notes are posted
on the base game's page (app 881020). Posts whose title carries a version ("Ver. 2.0.6 Update Information") go to
`patches`, everything else to `posts`.

The GitHub workflow .github/workflows/steam-news.yml runs this twice an hour and commits any change.
    python3 tools/steam_news.py                     fetch from Steam (needs internet)
    python3 tools/steam_news.py --input saved.json  replay a saved Steam API response (for testing)

Later, when the guide knows the characters, this is the place to read balance changes out of the update notes
(the DragonSword guide does this in tools/apply_patch_skills.py).
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
APP = 881020
CHANNEL = 'steam_community_announcements'
API = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/'
VERSION = re.compile(r'\bVer(?:sion)?\.?\s*(\d+\.\d+\.\d+)\b', re.I)
SOURCES = {'steamstore-a.akamaihd.net', 'store.steampowered.com', 'steamcommunity.com', 'clan.akamai.steamstatic.com'}


def fetch():
    posts, cursor = {}, None
    for _ in range(40):
        query = dict(appid=APP, feeds=CHANNEL, count=50, maxlength=0)
        if cursor is not None:
            query['enddate'] = cursor
        with urlopen(f'{API}?{urlencode(query)}', timeout=30) as response:
            result = json.load(response)['appnews']
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
    items = json.loads(options.input.read_text(encoding='utf-8'))['appnews']['newsitems'] if options.input else fetch()
    feed = make_feed(items)
    temporary = options.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(feed, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
    temporary.replace(options.output)
    print(f"Steam feed: {len(feed['posts'])} news posts and {len(feed['patches'])} patches")


if __name__ == '__main__':
    main()
