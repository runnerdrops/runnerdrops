"""Crop a product photo around the shoe and add it to imgs.json.
usage: python3 tools/add_image.py KEY path/to/photo.avif [aspect=1] [maxw=480]
"""
import sys, json, base64, io
from PIL import Image, ImageChops
key, path = sys.argv[1], sys.argv[2]
aspect = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
maxw = int(sys.argv[4]) if len(sys.argv) > 4 else 480
pad = 0.08
im = Image.open(path).convert('RGB')
bgc = im.getpixel((2, 2))
diff = ImageChops.difference(im, Image.new('RGB', im.size, bgc)).convert('L').point(lambda p: 255 if p > 18 else 0)
x0, y0, x1, y1 = diff.getbbox() or (0, 0) + im.size
w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
tw, th = w * (1 + pad), h * (1 + pad)
if tw / th < aspect: tw = th * aspect
else: th = tw / aspect
box = (int(cx - tw / 2), int(cy - th / 2), int(cx + tw / 2), int(cy + th / 2))
canvas = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), bgc)
canvas.paste(im, (-box[0], -box[1]))
if canvas.width > maxw: canvas = canvas.resize((maxw, int(canvas.height * maxw / canvas.width)), Image.LANCZOS)
b = io.BytesIO(); canvas.save(b, 'JPEG', quality=80)
d = json.load(open('imgs.json'))
d[key] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
json.dump(d, open('imgs.json', 'w'))
print(f'added {key} ({canvas.size[0]}x{canvas.size[1]}) — now {len(d)} images')
