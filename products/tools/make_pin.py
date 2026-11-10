"""2:3 Pinterest pin (1000x1500) from a 1080x1350 carousel cover image.
usage: make_pin.py FONT_DIR SRC OUT "Line 1" "Line 2" "facts" "bottom tag" """
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD, SRC, OUT, L1, L2, FACTS, TAG = sys.argv[1:8]
TOP = int(sys.argv[8]) if len(sys.argv) > 8 else 175
FB = lambda s: ImageFont.truetype(f'{FD}/Fredoka-Bold.ttf', s)
INK = (43, 43, 58); YEL = (247, 201, 72)
src = Image.open(SRC).convert('RGB'); W, H = src.size
bg = src.getpixel((5, H // 2))
dark = sum(bg) < 400
im = Image.new('RGB', (1000, 1500), bg); dr = ImageDraw.Draw(im)
def fit(s, maxw, size):
    while dr.textlength(s, font=FB(size)) > maxw: size -= 2
    return FB(size)
def ctext(y, s, f, fill):
    w = dr.textlength(s, font=f); dr.text(((1000 - w) / 2, y), s, font=f, fill=fill, stroke_width=6, stroke_fill=INK if dark else 'white')
ctext(50, L1, fit(L1, 920, 92), 'white' if dark else (200, 40, 59))
ctext(158, L2, fit(L2, 900, 64), YEL if dark else (42, 130, 80))
cover = src.crop((60, TOP, W - 60, 1125)); s = 960 / cover.width
cover = cover.resize((960, int(cover.height * s)), Image.LANCZOS)
if cover.height > 960: cover = cover.crop((0, 0, 960, 960))
im.paste(cover, (20, 255))
def pill(y, s, f, fill, color):
    w = dr.textlength(s, font=f); bb = f.getbbox(s); h = bb[3] - bb[1]; x0 = (1000 - w) / 2 - 36
    dr.rounded_rectangle((x0, y, x0 + w + 72, y + h + 40), radius=(h + 40) // 2, fill=fill, outline=INK, width=4)
    dr.text(((1000 - w) / 2, y + 20 - bb[1]), s, font=f, fill=color)
y = 255 + cover.height + 18
pill(y, FACTS, fit(FACTS, 820, 40), 'white', INK)
pill(min(y + 92, 1500 - 110), TAG, fit(TAG, 760, 46), YEL, INK)
im.save(OUT, quality=92)
