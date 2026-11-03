import sys, random
import pypdfium2 as p
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DL, OUTD, A, B = sys.argv[1:5]
W, H = 1500, 1875
CREAM = (255, 248, 236); PURPLE = (91, 63, 224); INK = (43, 43, 58)
RAIN = [(230, 57, 70), (244, 162, 97), (233, 196, 106), (42, 157, 143), (58, 134, 255), (131, 56, 236), (255, 93, 162)]
FB = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Bold.ttf', s)
FM = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Medium.ttf', s)


def pages(path, scale=2.2):
    d = p.PdfDocument(path); d.init_forms()
    return [d[i].render(scale=scale, may_draw_forms=True).to_pil().convert('RGB') for i in range(len(d))]


E = pages(A); L = pages(B) if B != '-' else None


def base():
    im = Image.new('RGB', (W, H), CREAM); dr = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(26):
        r = rnd.randint(8, 18)
        if rnd.random() < 0.5: x, y = rnd.choice([rnd.randint(10, 110), rnd.randint(W - 110, W - 10)]), rnd.randint(0, H)
        else: x, y = rnd.randint(0, W), rnd.choice([rnd.randint(5, 50), rnd.randint(H - 150, H - 130)])
        dr.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice(RAIN))
    return im, dr


def ctext(dr, y, s, font, fill=INK, stroke=0, sfill=None):
    w = dr.textlength(s, font=font)
    dr.text(((W - w) / 2, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def rainbow(dr, y, s, font, stroke=6):
    w = dr.textlength(s, font=font); x = (W - w) / 2; i = 0
    for ch in s:
        col = RAIN[i % 7] if ch != ' ' else INK
        dr.text((x, y), ch, font=font, fill=col, stroke_width=stroke, stroke_fill=INK)
        if ch != ' ': i += 1
        x += dr.textlength(ch, font=font)


def pill(dr, y, s, font, fill=PURPLE, color='white', pad=36):
    w = dr.textlength(s, font=font); bb = font.getbbox(s); h = bb[3] - bb[1]
    x0 = (W - w) / 2 - pad
    dr.rounded_rectangle((x0, y, x0 + w + 2 * pad, y + h + 44), radius=(h + 44) // 2, fill=fill, outline=INK, width=5)
    dr.text(((W - w) / 2, y + 22 - bb[1]), s, font=font, fill=color)


def paste_page(im, pg, x, y, w, angle=0):
    pg = pg.resize((w, int(w * pg.height / pg.width)), Image.LANCZOS)
    card = Image.new('RGBA', (pg.width + 60, pg.height + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((36, 40, pg.width + 36, pg.height + 40), fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); card.alpha_composite(sh); card.paste(pg, (30, 30))
    if angle: card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(card, (int(x - card.width / 2), int(y)), card)


def footer(im, dr):
    rainbow(dr, H - 110, 'colorbloop', FB(64), stroke=3)
    ctext(dr, H - 40, 'printables for little hands', FM(26), INK)



TEAL = (42, 157, 143)
# 1 hero
im, dr = base()
rainbow(dr, 60, 'Visual Schedule', FB(140))
ctext(dr, 225, 'Picture Cards for Kids', FB(96), 'white', 7, INK)
pill(dr, 365, '72 cards + morning, day & bedtime charts', FM(44))
paste_page(im, E[1], 400, 560, 640, 6)
paste_page(im, E[12], 1100, 560, 640, -6) if False else paste_page(im, E[10], 1100, 560, 640, -6)
paste_page(im, E[5], 750, 500, 760)
pill(dr, 1640, 'Instant Download  •  Ages 2-8  •  13 Pages', FM(42), fill=(233, 196, 106), color=INK)
im.save(f'{OUTD}/vs_1.jpg', quality=92)

# 2 all 72 cards
im, dr = base()
ctext(dr, 50, '72 picture cards', FB(115), PURPLE, 6, INK)
labels = ['Morning', 'School & Learning', 'Play & Activities', 'Places & People', 'Home & Bedtime', 'Feelings & Helpers']
for k in range(6):
    cx = 270 + (k % 3) * 480; cy = 220 + (k // 3) * 780
    paste_page(im, E[5 + k], cx, cy, 420)
    w = dr.textlength(labels[k], font=FB(38)); dr.text((cx - w / 2, cy + 600), labels[k], font=FB(38), fill=INK)
ctext(dr, 1660, '+ 12 blank cards to draw your own', FM(42), INK)
footer(im, dr)
im.save(f'{OUTD}/vs_2.jpg', quality=92)

# 3 boards
im, dr = base()
ctext(dr, 50, 'Routine charts', FB(120), PURPLE, 6, INK)
for k, (cx, ang) in enumerate([(300, 5), (750, 0), (1200, -5)]):
    paste_page(im, E[1 + k], cx, 260 if k != 1 else 230, 520, ang)
ctext(dr, 1000, 'My Morning  •  My Day  •  My Bedtime', FB(52), INK)
paste_page(im, E[4].crop((0, 0, E[4].width, int(E[4].height * 0.55))), 750, 1090, 760)
footer(im, dr)
im.save(f'{OUTD}/vs_3.jpg', quality=92)

# 4 close-up
im, dr = base()
ctext(dr, 60, 'Big, clear pictures', FB(110), PURPLE, 6, INK)
pg = E[5]
crop = pg.crop((int(pg.width * 0.08), int(pg.height * 0.12), int(pg.width * 0.92), int(pg.height * 0.62)))
paste_page(im, crop, 750, 250, 1180)
pill(dr, 1260, 'Kids can see what comes next!', FM(44), fill=TEAL)
ctext(dr, 1400, 'Great for toddlers, preschool, homeschool & classrooms', FM(42), INK)
footer(im, dr)
im.save(f'{OUTD}/vs_4.jpg', quality=92)

# 5 details
im, dr = base()
ctext(dr, 70, 'What you get', FB(120), PURPLE, 6, INK)
items = ['13-page printable PDF', 'US Letter + A4 sizes included', '72 picture cards in 6 themes + 12 blank',
         'Morning, Day & Bedtime charts', 'First / Then board', 'Print, cut, laminate & add velcro', 'Instant digital download - nothing shipped']
y = 270
for i, t in enumerate(items):
    dr.rounded_rectangle((150, y, W - 150, y + 120), radius=30, fill='white', outline=INK, width=4)
    dr.ellipse((180, y + 30, 240, y + 90), fill=RAIN[i % 7])
    dr.text((270, y + 30), t, font=FM(46), fill=INK); y += 150
footer(im, dr)
im.save(f'{OUTD}/vs_5.jpg', quality=92)
print('ok')
