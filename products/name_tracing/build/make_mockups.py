import sys, random
import pypdfium2 as p
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DL, OUTD, EMMA, LIAM = sys.argv[1:5]
W, H = 1500, 1875
CREAM = (255, 248, 236); PURPLE = (91, 63, 224); INK = (43, 43, 58)
RAIN = [(230, 57, 70), (244, 162, 97), (233, 196, 106), (42, 157, 143), (58, 134, 255), (131, 56, 236), (255, 93, 162)]
FB = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Bold.ttf', s)
FM = lambda s: ImageFont.truetype(f'{DL}/Fredoka-Medium.ttf', s)


def pages(path, scale=2.2):
    d = p.PdfDocument(path); d.init_forms()
    return [d[i].render(scale=scale, may_draw_forms=True).to_pil().convert('RGB') for i in range(len(d))]


E = pages(EMMA); L = pages(LIAM)


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


# 1 hero
im, dr = base()
rainbow(dr, 70, 'Name Tracing', FB(150))
ctext(dr, 245, 'Editable Worksheets', FB(96), 'white', 7, INK)
pill(dr, 375, 'Type the name once - it fills every page!', FM(46))
paste_page(im, E[3], 400, 560, 640, 6)
paste_page(im, E[2], 1100, 560, 640, -6)
paste_page(im, E[1], 750, 500, 760)
pill(dr, 1640, 'Instant Download  •  Ages 3-6  •  6 Pages', FM(42), fill=(233, 196, 106), color=INK)
im.save(f'{OUTD}/name_1.jpg', quality=92)

# 2 how it works
im, dr = base()
ctext(dr, 70, 'How it works', FB(120), PURPLE, 6, INK)
steps = [('1', 'Open the PDF in free Adobe Acrobat Reader'), ('2', 'Type your child’s name once'), ('3', 'Every page fills in - print & trace!')]
y = 250
for n, t in steps:
    dr.ellipse((150, y, 240, y + 90), fill=RAIN[int(n) * 2], outline=INK, width=5)
    dr.text((195, y + 45), n, font=FB(60), fill='white', anchor='mm')
    dr.text((270, y + 18), t, font=FM(50), fill=INK); y += 125
crop = E[0].crop((0, 0, E[0].width, int(E[0].height * 0.42)))
paste_page(im, crop, 750, 660, 1100)
ctext(dr, 1290, 'Same file works for every child in the family or class', FM(44), INK)
paste_page(im, L[1].crop((0, 0, L[1].width, int(L[1].height * 0.32))), 750, 1360, 820, 2)
footer(im, dr)
im.save(f'{OUTD}/name_2.jpg', quality=92)

# 3 all pages
im, dr = base()
ctext(dr, 60, '6 fun name pages', FB(120), PURPLE, 6, INK)
labels = ['Start here', 'Trace my name', 'Trace & write', 'Practice page', 'Color my name', 'I can write it!']
for k in range(6):
    cx = 270 + (k % 3) * 480; cy = 260 + (k // 3) * 800
    paste_page(im, E[k], cx, cy, 420)
    w = dr.textlength(labels[k], font=FB(40))
    dr.text((cx - w / 2, cy + 600), labels[k], font=FB(40), fill=INK)
footer(im, dr)
im.save(f'{OUTD}/name_3.jpg', quality=92)

# 4 color + write closeup
im, dr = base()
ctext(dr, 60, 'Color it. Write it.', FB(115), PURPLE, 6, INK)
paste_page(im, E[4], 400, 240, 700, -4)
paste_page(im, E[5], 1100, 240, 700, 4)
pill(dr, 1490, 'Builds name recognition & fine motor skills', FM(44))
footer(im, dr)
im.save(f'{OUTD}/name_4.jpg', quality=92)

# 5 details
im, dr = base()
ctext(dr, 70, 'What you get', FB(120), PURPLE, 6, INK)
items = ['Editable PDF, 6 pages', 'US Letter + A4 sizes included', 'Dotted tracing letters + coloring letters',
         'Reuse for siblings, classes & daycare', 'Instant digital download - nothing shipped', 'Fill in free Adobe Acrobat Reader',
         'Names up to about 12 letters']
y = 270
for i, t in enumerate(items):
    dr.rounded_rectangle((150, y, W - 150, y + 120), radius=30, fill='white', outline=INK, width=4)
    dr.ellipse((180, y + 30, 240, y + 90), fill=RAIN[i % 7])
    dr.text((270, y + 30), t, font=FM(46), fill=INK); y += 150
footer(im, dr)
im.save(f'{OUTD}/name_5.jpg', quality=92)
print('ok')
