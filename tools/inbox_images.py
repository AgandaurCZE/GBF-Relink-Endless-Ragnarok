"""Turn pictures from inbox/ into site pictures, and file the originals as sources.

    python3 tools/inbox_images.py list
        every picture waiting in inbox/, with its size in pixels and on disk

    python3 tools/inbox_images.py asset inbox/shot.png assets/characters/katalina.webp [--crop L,T,R,B] [--width N] [--lossy Q]
        save a picture for the site: optional crop (pixel box: left, top, right, bottom), optional resize to N pixels
        wide (never larger than the original), as .webp. Lossless by default, because picture quality comes before
        file size; --lossy 90 makes a smaller file at quality 90. Prints the result's size; refuses files over 5 MB.

    python3 tools/inbox_images.py archive inbox/shot.png katalina-skills [--folder screenshots/characters]
        move an original into sources/ as <name>-<YYYY-MM-DD>.<ext> (the date the file was last changed),
        then remove empty folders left in inbox/

Needs Pillow: pip install pillow
"""
import argparse
from datetime import date
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
INBOX, SOURCES, ASSETS = ROOT / 'inbox', ROOT / 'sources', ROOT / 'assets'
PICTURES = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tif', '.tiff'}
MAX_MB = 5
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def image_lib():
    try:
        from PIL import Image
        return Image
    except ImportError:
        sys.exit('Pillow is missing: pip install pillow')


def inside(path, folder):
    path = path.resolve()
    if folder.resolve() not in path.parents:
        sys.exit(f'{path} is not inside {folder.relative_to(ROOT)}/')
    return path


def cmd_list(_):
    Image = image_lib()
    found = sorted(p for p in INBOX.rglob('*') if p.suffix.lower() in PICTURES)
    if not found:
        print('inbox/ has no pictures.')
    for p in found:
        with Image.open(p) as im:
            print(f'{p.relative_to(ROOT)}  {im.width}x{im.height}  {p.stat().st_size / 1024:.0f} KB')


def cmd_asset(a):
    Image = image_lib()
    src = inside(Path(a.source), ROOT)
    out = inside(Path(a.output), ASSETS)
    if out.suffix != '.webp':
        sys.exit('Site pictures are saved as .webp: end the output name with .webp')
    if not NAME.fullmatch(out.stem):
        sys.exit(f'Use a lowercase name with hyphens, e.g. katalina-portrait.webp (got {out.name})')
    with Image.open(src) as im:
        im.load()
        im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') or 'transparency' in im.info else im.convert('RGB')
        if a.crop:
            box = tuple(int(v) for v in a.crop.split(','))
            if len(box) != 4 or not (0 <= box[0] < box[2] <= im.width and 0 <= box[1] < box[3] <= im.height):
                sys.exit(f'--crop must be L,T,R,B inside the picture ({im.width}x{im.height})')
            im = im.crop(box)
        if a.width and a.width < im.width:
            im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
        out.parent.mkdir(parents=True, exist_ok=True)
        options = dict(quality=a.lossy, method=6) if a.lossy else dict(lossless=True, quality=100, method=6)
        im.save(out, 'WEBP', **options)
    size = out.stat().st_size
    if size > MAX_MB * 1024 * 1024:
        out.unlink()
        sys.exit(f'The result is over {MAX_MB} MB; use --width or --lossy 92')
    print(f'Saved {out.relative_to(ROOT)}  {im.width}x{im.height}  {size / 1024:.0f} KB')


def cmd_archive(a):
    src = inside(Path(a.source), INBOX)
    if not NAME.fullmatch(a.name):
        sys.exit('Use a lowercase name with hyphens, e.g. katalina-skills')
    folder = inside(SOURCES / a.folder / 'x', SOURCES).parent
    day = date.fromtimestamp(src.stat().st_mtime).isoformat()
    target = folder / f'{a.name}-{day}{src.suffix.lower()}'
    n = 2
    while target.exists():
        target = folder / f'{a.name}-{day}-{n}{src.suffix.lower()}'
        n += 1
    folder.mkdir(parents=True, exist_ok=True)
    shutil.move(src, target)
    for parent in src.parents:
        if parent == INBOX or any(parent.iterdir()):
            break
        parent.rmdir()
    print(f'Moved to {target.relative_to(ROOT)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list').set_defaults(run=cmd_list)
    p = sub.add_parser('asset')
    p.add_argument('source')
    p.add_argument('output')
    p.add_argument('--crop')
    p.add_argument('--width', type=int)
    p.add_argument('--lossy', type=int, metavar='QUALITY')
    p.set_defaults(run=cmd_asset)
    p = sub.add_parser('archive')
    p.add_argument('source')
    p.add_argument('name')
    p.add_argument('--folder', default='screenshots')
    p.set_defaults(run=cmd_archive)
    a = parser.parse_args()
    a.run(a)


if __name__ == '__main__':
    main()
