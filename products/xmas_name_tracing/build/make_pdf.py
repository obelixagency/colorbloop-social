"""Editable Christmas Name Tracing Worksheets (Colorbloop). Pictures: Noto Emoji (Apache 2.0). Static art via reportlab, form fields via pikepdf.
usage: make_pdf.py DL_DIR FONT_DIR OUT.pdf [sample_name]   (env XPNG = dir with tree.png, santa.png ...)
If sample_name is given, field values are pre-filled (for listing previews) with our own appearance streams.
"""
import sys, json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import os
PAGE = A4 if os.environ.get('PAGESIZE') == 'A4' else letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTT
from reportlab.lib.colors import HexColor, white
import pikepdf
from fontTools.ttLib import TTFont

DL, FD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SAMPLE = sys.argv[4] if len(sys.argv) > 4 else ''
W, H = PAGE
M = 36
pdfmetrics.registerFont(RLTT('FB', f'{DL}/Fredoka-Bold.ttf'))
pdfmetrics.registerFont(RLTT('FM', f'{DL}/Fredoka-Medium.ttf'))
PURPLE = HexColor('#C8283B'); INK = HexColor('#2B2B3A'); CREAM = HexColor('#FFF8EC')
RAINBOW = ['#C8283B', '#2A9D58', '#E0A526', '#C8283B', '#2A9D58', '#E0A526', '#C8283B']
LINE = HexColor('#9AA0B4'); MID = HexColor('#F08CA8'); SKY = HexColor('#9ED6B0')
GREEN = HexColor('#2A9D58'); MINT = HexColor('#EAF7EE')
XP = os.environ.get('XPNG', '.')

def pic(c, n, x, y, s): c.drawImage(f'{XP}/{n}.png', x, y, s, s, mask='auto')


# font metrics (units per em) for field sizing
FONTS = {
    'Trace': (f'{FD}/ColorbloopTrace.ttf', 'ColorbloopTrace'),
    'Outline': (f'{FD}/ColorbloopOutline.ttf', 'ColorbloopOutline'),
    'Solid': (f'{FD}/ColorbloopPrint.ttf', 'ColorbloopPrint'),
}
CAP = {k: TTFont(p)['OS/2'].sCapHeight / TTFont(p)['head'].unitsPerEm for k, (p, _) in FONTS.items()}
# Ascent/Descent we write into each FontDescriptor (per 1000 em). Field rect height = (ASC-DESC)*fs/1000.
ASC, DESC = 800, -300

fields = []  # (page_index, font_key, fs, rect)


def rainbow_text(c, x, y, text, font, size, center=False):
    w = pdfmetrics.stringWidth(text, font, size)
    if center: x = x - w / 2
    i = 0
    for ch in text:
        if ch != ' ':
            c.setFillColor(HexColor(RAINBOW[i % len(RAINBOW)])); i += 1
        c.setFont(font, size); c.drawString(x, y, ch); x += pdfmetrics.stringWidth(ch, font, size)


def header(c, title, subtitle):
    c.setFillColor(CREAM); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(white); c.roundRect(M - 8, M - 8, W - 2 * M + 16, H - 2 * M + 16, 18, stroke=0, fill=1)
    c.setFillColor(PURPLE); c.roundRect(M, H - M - 58, W - 2 * M, 58, 16, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('FB', 28); c.drawCentredString(W / 2, H - M - 38, title)
    c.setFillColor(INK); c.setFont('FM', 12); c.drawCentredString(W / 2, H - M - 78, subtitle)
    footer(c)


def footer(c):
    rainbow_text(c, W / 2, M + 4, 'colorbloop', 'FB', 13, center=True)
    pic(c, 'snowflake', M + 6, H - M - 50, 40); pic(c, 'snowflake', W - M - 46, H - M - 50, 40)
    c.setFillColor(LINE); c.setFont('FM', 7.5)
    c.drawCentredString(W / 2, M - 6, 'For personal and classroom use only. Please do not resell or share the file.')


def writing_row(c, x0, x1, base, h):
    """3-line handwriting row: top (solid), midline at x-height (dashed), baseline (solid)."""
    c.setLineWidth(1.2); c.setStrokeColor(LINE)
    c.line(x0, base + h, x1, base + h)
    c.setStrokeColor(MID); c.setDash(5, 4); c.setLineWidth(1)
    c.line(x0, base + h * 0.63, x1, base + h * 0.63)
    c.setDash(); c.setStrokeColor(SKY); c.setLineWidth(1.8)
    c.line(x0, base, x1, base)


def name_field(page, key, h, x, base, width):
    fs = h / CAP[key]
    rh = (ASC - DESC) * fs / 1000
    y0 = base + DESC * fs / 1000 - 1.5  # rect bottom so that baseline lands on `base` when text sits at descent
    fields.append((page, key, fs, [x, y0, x + width, y0 + rh]))


def star(c, x, y, r, color):
    import math
    p = c.beginPath()
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); c.setFillColor(HexColor(color)); c.drawPath(p, stroke=0, fill=1)


c = canvas.Canvas(OUT + '.base.pdf', pagesize=PAGE)
c.setTitle('My Christmas Name Tracing Pages - Colorbloop'); c.setAuthor('Colorbloop')

# ---- Page 1: start here
header(c, 'My Christmas Name Pages', 'Type your child’s name once — it fills in on every page!')
c.setFillColor(INK); c.setFont('FB', 16); c.drawString(M + 20, H - 165, '1.  Type the name here:')
c.setStrokeColor(PURPLE); c.setLineWidth(2.5); c.setDash(6, 4)
box_y = H - 270
c.roundRect(M + 20, box_y, W - 2 * M - 40, 80, 14, stroke=1, fill=0); c.setDash()
name_field(0, 'Solid', 40, M + 40, box_y + 22, W - 2 * M - 80)
y = H - 315
for n, t in [('2.', 'Every page updates with the name automatically.'), ('3.', 'Print as many copies as you like and start tracing!')]:
    c.setFont('FB', 16); c.drawString(M + 20, y, n); c.setFont('FM', 14); c.drawString(M + 50, y, t); y -= 30
c.setFillColor(MINT); c.roundRect(M + 20, 250, W - 2 * M - 40, 140, 14, stroke=0, fill=1)
c.setFillColor(GREEN); c.setFont('FB', 15); c.drawString(M + 40, 360, 'Good to know')
c.setFillColor(INK); c.setFont('FM', 11.5)
tips = [
    '•  Easiest on a computer: open it in the free Adobe Acrobat Reader and type the name.',
    '•  iPhone / iPad / Android: use the free Adobe Acrobat Reader app. Apple Files, Books',
    '    and most browser previews may show plain letters instead of the tracing dots.',
    '•  Works best for names up to about 12 letters. Use a capital first letter: Emma',
    '•  New name? Type over it and print again. Great for siblings & classes.',
]
y = 336
for t in tips: c.drawString(M + 40, y, t); y -= 19
for i, n in enumerate(['tree', 'santa', 'gift', 'snowman', 'reindeer']): pic(c, n, W / 2 - 150 + i * 62, 150, 52)
c.setFillColor(INK); c.setFont('FM', 10.5)
c.drawCentredString(W / 2, 120, 'Inside: Trace my name • Trace & write • Letter to Santa • Color my name • Gift tags • I can write it!')
c.showPage()

# ---- Page 2: trace my name (big)
header(c, 'Trace My Name', 'Follow the dots. Start at the top!')
h = 52; base = H - 200; gap = 92
for i in range(6):
    writing_row(c, M + 14, W - M - 14, base, h); name_field(1, 'Trace', h, M + 22, base, W - 2 * M - 44); base -= gap
pic(c, 'tree', M + 14, M + 22, 50); pic(c, 'gift', W - M - 64, M + 22, 50)
c.showPage()

# ---- Page 3: trace & write
header(c, 'Trace & Write', 'Trace the name, then write it yourself on the next line.')
h = 44; base = H - 190; gap = 72
for i in range(8):
    writing_row(c, M + 14, W - M - 14, base, h)
    if i % 2 == 0: name_field(2, 'Trace', h, M + 22, base, W - 2 * M - 44)
    else: pic(c, ['star', 'bell', 'cookie', 'snowflake'][i // 2], M + 16, base + h - 6, 18)
    base -= gap
c.showPage()

# ---- Page 4: letter to Santa
header(c, 'My Letter to Santa', 'Trace your name, then tell Santa your wishes!')
pic(c, 'santa', W - M - 120, H - 230, 96)
c.setFillColor(INK); c.setFont('FB', 22); c.drawString(M + 24, H - 160, 'Dear Santa,')
c.setFont('FM', 15); c.drawString(M + 24, H - 196, 'My name is')
h = 40; base = H - 262
writing_row(c, M + 14, W - M - 130, base, h); name_field(3, 'Trace', h, M + 22, base, W - 2 * M - 160)
c.setFont('FM', 15); c.setFillColor(INK)
c.drawString(M + 24, base - 40, 'This year I was very  kind  /  helpful  /  good   (circle one)')
c.drawString(M + 24, base - 76, 'For Christmas I wish for:')
yy = base - 110
for i in range(3):
    c.setStrokeColor(LINE); c.setLineWidth(1.2); c.line(M + 40, yy, W - M - 40, yy)
    pic(c, 'gift', M + 16, yy - 2, 18); yy -= 40
c.setStrokeColor(GREEN); c.setLineWidth(2.5); c.setDash(8, 5)
box_top = yy - 10; box_bot = 150
c.roundRect(M + 20, box_bot, W - 2 * M - 40, box_top - box_bot, 14, stroke=1, fill=0); c.setDash()
c.setFillColor(GREEN); c.setFont('FB', 13); c.drawCentredString(W / 2, box_top - 22, 'Draw your wish here!')
c.setFillColor(INK); c.setFont('FB', 16); c.drawString(M + 24, 112, 'Love,')
name_field(3, 'Solid', 22, M + 80, 111, W - 2 * M - 120)
c.showPage()

# ---- Page 5: color my name
header(c, 'Color My Name', 'Color in the letters with Christmas colors!')
name_field(4, 'Outline', 78, M + 20, H - 250, W - 2 * M - 40)
c.setStrokeColor(GREEN); c.setLineWidth(2.5); c.setDash(8, 5)
c.roundRect(M + 20, 120, W - 2 * M - 40, 330, 16, stroke=1, fill=0); c.setDash()
c.setFillColor(GREEN); c.setFont('FB', 16); c.drawCentredString(W / 2, 425, 'Draw and decorate your Christmas tree!')
pic(c, 'star', W / 2 - 22, 360, 44)
c.setFillColor(INK); c.setFont('FM', 14); c.drawString(M + 30, 475, 'My name has ______ letters.')
for i, n in enumerate(['bell', 'snowflake', 'star']): pic(c, n, W - M - 80 - i * 34, 470, 26)
c.showPage()

# ---- Page 6: gift tags
header(c, 'My Name Gift Tags', 'Cut out the tags and put them on the presents you give!')
tw = (W - 2 * M - 40) / 2; th = 150; gx = 20
icons = ['gift', 'tree', 'snowman', 'santa', 'reindeer', 'bell']
for i in range(6):
    r, col = divmod(i, 2)
    x = M + 10 + col * (tw + gx); y = H - M - 110 - th - r * (th + 18)
    c.setStrokeColor(HexColor('#B9BECF')); c.setLineWidth(0.8); c.setDash(4, 3)
    c.roundRect(x - 4, y - 4, tw + 8, th + 8, 16, stroke=1, fill=0); c.setDash()
    c.setFillColor(MINT if i % 2 == 0 else HexColor('#FDECEE')); c.setStrokeColor(GREEN if i % 2 == 0 else PURPLE); c.setLineWidth(3)
    c.roundRect(x, y, tw, th, 14, stroke=1, fill=1)
    c.setFillColor(white); c.circle(x + 20, y + th - 20, 7, stroke=1, fill=1)  # string hole
    pic(c, icons[i], x + tw - 70, y + th - 70, 58)
    c.setFillColor(INK); c.setFont('FB', 16); c.drawString(x + 16, y + 74, 'To:')
    c.setStrokeColor(LINE); c.setLineWidth(1.2); c.line(x + 52, y + 72, x + tw - 80, y + 72)
    c.drawString(x + 16, y + 30, 'From:')
    name_field(5, 'Solid', 17, x + 70, y + 30, tw - 86)
c.showPage()

# ---- Page 7: I can write my name
header(c, 'I Can Write My Name!', 'Look at the name, then write it all by yourself.')
c.setFillColor(MINT); c.roundRect(M + 14, H - 205, W - 2 * M - 28, 82, 14, stroke=0, fill=1)
name_field(6, 'Solid', 44, M + 34, H - 186, W - 2 * M - 68)
h = 44; base = H - 290; gap = 80
for i in range(5):
    writing_row(c, M + 14, W - M - 14, base, h); pic(c, ['star', 'tree', 'gift', 'bell', 'snowflake'][i], M + 16, base + h - 6, 18); base -= gap
c.setFillColor(INK); c.setFont('FB', 15); c.drawCentredString(W / 2, 82, 'Great job! Merry Christmas!')
for i in range(5): pic(c, 'star', W / 2 - 70 + i * 30, 100, 24)
c.setFillColor(LINE); c.setFont('FM', 6.5); c.drawRightString(W - M - 4, M + 6, 'Pictures: Noto Emoji (Apache License 2.0)')
c.showPage()
c.save()

# ---------------- form fields with pikepdf ----------------
pdf = pikepdf.open(OUT + '.base.pdf')


def font_obj(key):
    path, ps = FONTS[key]
    tt = TTFont(path); upm = tt['head'].unitsPerEm; cmap = tt.getBestCmap(); hmtx = tt['hmtx']
    widths = [round(hmtx[cmap[c]][0] * 1000 / upm) if c in cmap else 0 for c in range(32, 127)]
    data = open(path, 'rb').read()
    ff = pdf.make_stream(data); ff.Length1 = len(data)
    desc = pikepdf.Dictionary(Type=pikepdf.Name.FontDescriptor, FontName=pikepdf.Name('/' + ps), Flags=32,
                              FontBBox=[-200, DESC, 1200, ASC], ItalicAngle=0, Ascent=ASC, Descent=DESC,
                              CapHeight=round(CAP[key] * 1000), StemV=80, FontFile2=ff)
    return pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Font, Subtype=pikepdf.Name.TrueType, BaseFont=pikepdf.Name('/' + ps),
        FirstChar=32, LastChar=126, Widths=widths, Encoding=pikepdf.Name.WinAnsiEncoding,
        FontDescriptor=pdf.make_indirect(desc))), widths


fobjs = {k: font_obj(k) for k in FONTS}
RES = {'Trace': '/CbTrace', 'Outline': '/CbOutline', 'Solid': '/CbSolid'}
DR = pikepdf.Dictionary(Font=pikepdf.Dictionary({RES[k]: fobjs[k][0] for k in FONTS}))
COLOR = {'Trace': '0.35 0.35 0.42 rg', 'Outline': '0.17 0.17 0.23 rg', 'Solid': '0.17 0.17 0.23 rg'}


def text_width(key, fs, s):
    w = fobjs[key][1]
    return sum(w[ord(ch) - 32] if 32 <= ord(ch) < 127 else 0 for ch in s) * fs / 1000


parent = pdf.make_indirect(pikepdf.Dictionary(FT=pikepdf.Name.Tx, T=pikepdf.String('ChildName'),
                                             V=pikepdf.String(SAMPLE), DA=pikepdf.String('/CbSolid 0 Tf 0 g'),
                                             MaxLen=24, Kids=pikepdf.Array()))
for pi, key, fs, rect in fields:
    x0, y0, x1, y1 = rect
    da = f'{RES[key]} {0 if key == "Outline" else round(fs, 2)} Tf {COLOR[key]}'
    # our own appearance: baseline at -DESC*fs/1000 + 0 from rect bottom, 2pt left pad
    bl = -DESC * fs / 1000
    esc = SAMPLE.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    content = f'/Tx BMC q BT {RES[key]} {fs:.2f} Tf {COLOR[key]} 2 {bl:.2f} Td ({esc}) Tj ET Q EMC' if SAMPLE else '/Tx BMC EMC'
    ap = pdf.make_stream(content.encode('latin-1'))
    ap.Type = pikepdf.Name.XObject; ap.Subtype = pikepdf.Name.Form; ap.BBox = [0, 0, x1 - x0, y1 - y0]
    ap.Resources = pikepdf.Dictionary(Font=pikepdf.Dictionary({RES[key]: fobjs[key][0]}))
    page = pdf.pages[pi]
    w = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget, Rect=[x0, y0, x1, y1], F=4, P=page.obj,
        Parent=parent, DA=pikepdf.String(da), Q=0, MK=pikepdf.Dictionary(),
        AP=pikepdf.Dictionary(N=ap)))
    # page 1 input stays editable; other copies are read-only so kids/parents can't mistype them
    parent.Kids.append(w)
    if '/Annots' not in page.obj: page.obj.Annots = pdf.make_indirect(pikepdf.Array())
    page.obj.Annots.append(w)
pdf.Root.AcroForm = pikepdf.Dictionary(Fields=[parent], DR=DR, DA=pikepdf.String('/CbSolid 0 Tf 0 g'),
                                       NeedAppearances=True)
pdf.docinfo['/Title'] = 'My Christmas Name Tracing Pages - Colorbloop'
pdf.save(OUT)
import os; os.remove(OUT + '.base.pdf')
print('ok', OUT, len(fields), 'widgets')
