"""Editable Name Tracing Worksheets (Colorbloop). Static art via reportlab, form fields via pikepdf.
usage: make_pdf.py DL_DIR FONT_DIR OUT.pdf [sample_name]
If sample_name is given, field values are pre-filled (for listing previews) with our own appearance streams.
"""
import sys, json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTT
from reportlab.lib.colors import HexColor, white
import pikepdf
from fontTools.ttLib import TTFont

DL, FD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SAMPLE = sys.argv[4] if len(sys.argv) > 4 else ''
W, H = letter
M = 36
pdfmetrics.registerFont(RLTT('FB', f'{DL}/Fredoka-Bold.ttf'))
pdfmetrics.registerFont(RLTT('FM', f'{DL}/Fredoka-Medium.ttf'))
PURPLE = HexColor('#5B3FE0'); INK = HexColor('#2B2B3A'); CREAM = HexColor('#FFF8EC')
RAINBOW = ['#E63946', '#F4A261', '#E9C46A', '#2A9D8F', '#3A86FF', '#8338EC', '#FF5DA2']
LINE = HexColor('#9AA0B4'); MID = HexColor('#F08CA8'); SKY = HexColor('#BFD7FF')

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


c = canvas.Canvas(OUT + '.base.pdf', pagesize=letter)
c.setTitle('My Name Tracing Worksheets - Colorbloop'); c.setAuthor('Colorbloop')

# ---- Page 1: start here
header(c, 'My Name Tracing Pages', 'Type your child’s name once — it fills in on every page!')
c.setFillColor(INK); c.setFont('FB', 16); c.drawString(M + 20, H - 165, '1.  Type the name here:')
c.setStrokeColor(PURPLE); c.setLineWidth(2.5); c.setDash(6, 4)
box_y = H - 270
c.roundRect(M + 20, box_y, W - 2 * M - 40, 80, 14, stroke=1, fill=0); c.setDash()
name_field(0, 'Solid', 40, M + 40, box_y + 22, W - 2 * M - 80)
steps = [
    ('2.', 'Every page updates with the name automatically.'),
    ('3.', 'Print as many copies as you like and start tracing!'),
]
y = H - 315
for n, t in steps:
    c.setFont('FB', 16); c.drawString(M + 20, y, n); c.setFont('FM', 14); c.drawString(M + 50, y, t); y -= 30
c.setFillColor(HexColor('#F3EFFF')); c.roundRect(M + 20, 250, W - 2 * M - 40, 140, 14, stroke=0, fill=1)
c.setFillColor(PURPLE); c.setFont('FB', 15); c.drawString(M + 40, 360, 'Good to know')
c.setFillColor(INK); c.setFont('FM', 11.5)
tips = [
    '•  Open the PDF in the free Adobe Acrobat Reader (computer, iPhone/iPad or Android).',
    '    Some browser and phone previewers do not show the special tracing letters.',
    '•  Works best for names up to about 12 letters. Use a capital first letter: Emma',
    '•  Want a new name? Just type over it and print again. Great for siblings & classes.',
    '•  Tip: slide a page into a sheet protector and use a dry-erase marker.',
]
y = 336
for t in tips: c.drawString(M + 40, y, t); y -= 19
star(c, W - M - 40, H - 150, 14, '#E9C46A'); star(c, M + 30, 215, 10, '#3A86FF'); star(c, W - M - 60, 215, 12, '#FF5DA2')
c.setFillColor(INK); c.setFont('FM', 11)
c.drawCentredString(W / 2, 180, 'Inside: Trace my name • Trace & write • Practice page • Color my name • I can write it!')
c.showPage()

# ---- Page 2: trace my name (big)
header(c, 'Trace My Name', 'Follow the dots. Start at the top!')
h = 52; base = H - 200; gap = 96
for i in range(6):
    writing_row(c, M + 14, W - M - 14, base, h); name_field(1, 'Trace', h, M + 22, base, W - 2 * M - 44); base -= gap
c.showPage()

# ---- Page 3: trace & write
header(c, 'Trace & Write', 'Trace the name, then write it yourself on the next line.')
h = 44; base = H - 190; gap = 74
for i in range(8):
    writing_row(c, M + 14, W - M - 14, base, h)
    if i % 2 == 0: name_field(2, 'Trace', h, M + 22, base, W - 2 * M - 44)
    else:
        c.setFillColor(HexColor(RAINBOW[i % 7])); c.circle(M + 26, base + h + 2, 3.5, stroke=0, fill=1)
    base -= gap
c.showPage()

# ---- Page 4: practice page (smaller)
header(c, 'Practice Page', 'Trace each name. Can you do it neatly every time?')
h = 32; base = H - 175; gap = 58
for i in range(10):
    writing_row(c, M + 14, W - M - 14, base, h); name_field(3, 'Trace', h, M + 22, base, W - 2 * M - 44); base -= gap
c.showPage()

# ---- Page 5: color my name
header(c, 'Color My Name', 'Color in the letters with your favorite colors!')
name_field(4, 'Outline', 78, M + 20, H - 250, W - 2 * M - 40)
c.setStrokeColor(PURPLE); c.setLineWidth(2.5); c.setDash(8, 5)
c.roundRect(M + 20, 120, W - 2 * M - 40, 330, 16, stroke=1, fill=0); c.setDash()
c.setFillColor(PURPLE); c.setFont('FB', 16); c.drawCentredString(W / 2, 425, 'Draw a picture of yourself!')
c.setFillColor(INK); c.setFont('FM', 14)
c.drawString(M + 30, 475, 'My name has ______ letters.')
for i, col in enumerate(['#E63946', '#3A86FF', '#E9C46A']): star(c, W - M - 60 - i * 34, 482, 11, col)
c.showPage()

# ---- Page 6: I can write my name
header(c, 'I Can Write My Name!', 'Look at the name, then write it all by yourself.')
c.setFillColor(HexColor('#F3EFFF')); c.roundRect(M + 14, H - 205, W - 2 * M - 28, 82, 14, stroke=0, fill=1)
name_field(5, 'Solid', 44, M + 34, H - 186, W - 2 * M - 68)
h = 44; base = H - 290; gap = 80
for i in range(5):
    writing_row(c, M + 14, W - M - 14, base, h)
    c.setFillColor(HexColor(RAINBOW[i])); c.circle(M + 26, base + h + 2, 3.5, stroke=0, fill=1); base -= gap
c.setFillColor(INK); c.setFont('FB', 15); c.drawCentredString(W / 2, 82, 'Great job! You can write your name!')
for i, col in enumerate(RAINBOW[:5]): star(c, W / 2 - 60 + i * 30, 112, 10, col)
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
pdf.docinfo['/Title'] = 'My Name Tracing Worksheets - Colorbloop'
pdf.save(OUT)
import os; os.remove(OUT + '.base.pdf')
print('ok', OUT, len(fields), 'widgets')
