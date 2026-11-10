"""Listing images for Thankful Turkey Craft. usage: make_mockups.py FREDOKA_DIR PDF OUTDIR"""
import sys, random
import pypdfium2 as p
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DL, PDF, OUTD = sys.argv[1:4]
S = 2000
CREAM = (255, 244, 230); ORANGE = (229, 115, 43); INK = (43, 43, 58); BROWN = (126, 82, 48)
DOTS = [(217, 57, 62), (229, 115, 43), (242, 182, 50), (91, 158, 63), (46, 140, 154), (123, 79, 160)]
FB = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Bold.ttf', s)
FM = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Medium.ttf', s)
doc = p.PdfDocument(PDF)
PG = [doc[i].render(scale=3).to_pil().convert('RGB') for i in range(len(doc))]


def base():
    im = Image.new('RGB', (S, S), CREAM); dr = ImageDraw.Draw(im); r = random.Random(3)
    for _ in range(30):
        rad = r.randint(10, 22)
        x, y = (r.choice([r.randint(15, 120), r.randint(S - 120, S - 15)]), r.randint(0, S)) if r.random() < .5 else (r.randint(0, S), r.choice([r.randint(10, 80), r.randint(S - 80, S - 10)]))
        dr.ellipse((x - rad, y - rad, x + rad, y + rad), fill=r.choice(DOTS))
    return im, dr


def ctext(dr, y, s, font, fill=INK):
    w = dr.textlength(s, font=font); dr.text(((S - w) / 2, y), s, font=font, fill=fill)


def pill(dr, y, s, font, fill=ORANGE, pad=50):
    w = dr.textlength(s, font=font); bb = font.getbbox(s); h = bb[3] - bb[1]; x0 = (S - w) / 2 - pad
    dr.rounded_rectangle((x0, y, x0 + w + 2 * pad, y + h + 56), radius=(h + 56) // 2, fill=fill)
    dr.text(((S - w) / 2, y + 28 - bb[1]), s, font=font, fill='white')


def card(im, pg, cx, y, w, angle=0):
    pg = pg.resize((w, int(w * pg.height / pg.width)), Image.LANCZOS)
    c = Image.new('RGBA', (pg.width + 80, pg.height + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((46, 52, pg.width + 46, pg.height + 52), fill=(0, 0, 0, 80))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); c.paste(pg, (40, 40))
    if angle: c = c.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(c, (int(cx - c.width / 2), int(y)), c)


def save(im, n): im.save(f'{OUTD}/turkey_{n}.jpg', quality=92)


# 1 hero: crop the finished turkey from page 1
p1 = PG[0]; W1, H1 = p1.size
turkey = p1.crop((int(W1 * .06), int(H1 * .138), int(W1 * .94), int(H1 * .735)))
px = turkey.load()
for yy in range(turkey.height):
    for xx in range(turkey.width):
        r_, g_, b_ = px[xx, yy]
        if r_ > 245 and g_ > 245 and b_ > 245: px[xx, yy] = CREAM
im, dr = base()
ctext(dr, 110, 'Thankful Turkey', FB(170), BROWN)
ctext(dr, 300, 'Cut, Color & Paste Craft', FM(92), INK)
t = turkey.resize((1400, int(1500 * turkey.height / turkey.width)), Image.LANCZOS)
im.paste(t, ((S - t.width) // 2, 420))
pill(dr, 1760, 'Thanksgiving Activity for Kids  |  8 Pages PDF', FB(64))
save(im, 1)

# 2 what's inside: all 8 pages
im, dr = base()
ctext(dr, 90, "What's Inside", FB(140), BROWN)
ctext(dr, 260, '8 printable pages  -  US Letter + A4', FM(70))
w = 440
for i, pg in enumerate(PG):
    col, row = i % 4, i // 4
    card(im, pg, 265 + col * 490, 400 + row * 720, w)
save(im, 2)

# 3 three feather options
im, dr = base()
ctext(dr, 90, '3 Feather Options', FB(140), BROWN)
ctext(dr, 260, 'Write it  -  Trace it  -  Draw it', FM(78))
for k, (i, a) in enumerate([(2, 5), (3, 0), (4, -5)]):
    card(im, PG[i], 420 + k * 580, 430 + (60 if k != 1 else 0), 620, a)
pill(dr, 1760, 'Great for ages 3 to 7', FB(68))
save(im, 3)

# 4 color or black & white
im, dr = base()
ctext(dr, 90, 'Color In or Print in Color', FB(124), BROWN)
ctext(dr, 250, 'Black & white pieces to color + ready-to-cut color pieces', FM(58))
card(im, PG[1], 560, 420, 820, 3); card(im, PG[5], 1440, 420, 820, -3)
pill(dr, 1640 + 90, 'Print at home or school', FB(64))
save(im, 4)

# 5 coloring page + how it works
im, dr = base()
ctext(dr, 90, 'Bonus Coloring Page', FB(140), BROWN)
ctext(dr, 260, 'No scissors? Color it and write on the feathers', FM(70))
card(im, PG[7], 640, 400, 1000, -2)
dr2 = ImageDraw.Draw(im)
for k, line in enumerate(['1. Print', '2. Color', '3. Cut', '4. Write', '5. Glue']):
    dr2.rounded_rectangle((1250, 560 + k * 240, 1880, 740 + k * 240), radius=60, fill=DOTS[k])
    f = FB(90); w = dr2.textlength(line, font=f); dr2.text((1565 - w / 2, 595 + k * 240), line, font=f, fill='white')
save(im, 5)
print('ok')
