"""Normalize brand logos: any color / any background -> solid black on transparent,
trimmed and centered in a square PNG.  usage: python3 tools/make_logos.py SRC_DIR OUT_DIR [size=600]
Puma ships as SVG; it is rasterized with Playwright's Chromium first."""
import sys, os, io, asyncio
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 600
os.makedirs(OUT, exist_ok=True)

def rasterize_svg(path):
    from playwright.sync_api import sync_playwright
    import base64
    svg = base64.b64encode(open(path, 'rb').read()).decode()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 800})
        pg.set_content(f'<body style="margin:0;background:#fff"><img src="data:image/svg+xml;base64,{svg}" style="width:1600px"></body>')
        pg.wait_for_timeout(200); png = pg.screenshot(full_page=True); b.close()
    return Image.open(io.BytesIO(png))

def load(path):
    im = rasterize_svg(path) if path.endswith('.svg') else Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    return im.convert('RGB')

def to_black(im):
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    corners = np.stack([a[2, 2], a[2, w-3], a[h-3, 2], a[h-3, w-3]])
    bg = np.median(corners, axis=0)
    if bg.mean() < 128:                       # light logo on dark field -> invert
        a = 255 - a; bg = 255 - bg
    diff = np.abs(a - bg).max(axis=2).astype(np.float32)   # distance from background
    solid = np.percentile(diff[diff > 40], 90) if (diff > 40).any() else 255
    alpha = np.clip(diff / solid * 255, 0, 255)
    alpha[alpha < 24] = 0                     # kill jpeg/webp noise in the background
    alpha = alpha.astype(np.uint8)
    out = np.zeros((h, w, 4), np.uint8); out[..., 3] = alpha
    return Image.fromarray(out, 'RGBA')

def square(im):
    bbox = im.getchannel('A').point(lambda p: 255 if p > 20 else 0).getbbox()
    im = im.crop(bbox)
    s = SIZE / max(im.size)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
    return canvas

for f in sorted(os.listdir(SRC)):
    slug = f.rsplit('.', 1)[0]
    img = square(to_black(load(os.path.join(SRC, f))))
    img.save(os.path.join(OUT, slug + '.png'), optimize=True)
    print(f'{slug:14s} ok')
