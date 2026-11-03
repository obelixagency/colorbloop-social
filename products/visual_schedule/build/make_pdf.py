"""Visual Schedule Cards for Toddlers & Kids (Colorbloop).
usage: PAGESIZE=A4|LETTER make_pdf.py FONT_DIR PNG_DIR OUT.pdf
Pictures: Noto Emoji (Apache License 2.0), rendered from SVG.
"""
import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from cards import SHEETS, EXTRA

FD, PNG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PAGE = A4 if os.environ.get('PAGESIZE') == 'A4' else letter
W, H = PAGE
M = 34
pdfmetrics.registerFont(TTFont('FB', f'{FD}/Fredoka-Bold.ttf'))
pdfmetrics.registerFont(TTFont('FM', f'{FD}/Fredoka-Medium.ttf'))
PURPLE = HexColor('#5B3FE0'); INK = HexColor('#2B2B3A'); CREAM = HexColor('#FFF8EC'); GREY = HexColor('#9AA0B4')
RAINBOW = ['#E63946', '#F4A261', '#E9C46A', '#2A9D8F', '#3A86FF', '#8338EC', '#FF5DA2']
BORDERS = ['#F7C948', '#F58BA8', '#8EC5FF', '#8FD18B']  # yellow, pink, blue, green
TINT = ['#FFF6D6', '#FFE9EF', '#E8F3FF', '#EAF8E8']


def img(code): return f'{PNG}/{code}.png'


def rainbow_text(c, x, y, text, font, size):
    w = pdfmetrics.stringWidth(text, font, size); x -= w / 2; i = 0
    for ch in text:
        if ch != ' ':
            c.setFillColor(HexColor(RAINBOW[i % 7])); i += 1
        c.setFont(font, size); c.drawString(x, y, ch); x += pdfmetrics.stringWidth(ch, font, size)


def page_base(c, title, subtitle, band=PURPLE):
    c.setFillColor(CREAM); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(white); c.roundRect(M - 10, M - 10, W - 2 * M + 20, H - 2 * M + 20, 18, stroke=0, fill=1)
    c.setFillColor(band); c.roundRect(M, H - M - 52, W - 2 * M, 52, 16, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('FB', 26); c.drawCentredString(W / 2, H - M - 35, title)
    if subtitle:
        c.setFillColor(INK); c.setFont('FM', 11.5); c.drawCentredString(W / 2, H - M - 70, subtitle)
    rainbow_text(c, W / 2, M + 2, 'colorbloop', 'FB', 12)
    c.setFillColor(GREY); c.setFont('FM', 7)
    c.drawCentredString(W / 2, M - 8, 'For personal and single-classroom use. Please do not resell or share the file.')


def fit_label(text, maxw, size):
    while pdfmetrics.stringWidth(text, 'FB', size) > maxw and size > 8: size -= 0.5
    return size


def card(c, x, y, s, label, code, k):
    # dashed cut line
    c.setStrokeColor(HexColor('#B9BECF')); c.setLineWidth(0.8); c.setDash(4, 3)
    c.roundRect(x - 5, y - 5, s + 10, s + 10, 12, stroke=1, fill=0); c.setDash()
    c.setFillColor(white); c.setStrokeColor(HexColor(BORDERS[k % 4])); c.setLineWidth(4)
    c.roundRect(x, y, s, s, 10, stroke=1, fill=1)
    if code:
        isz = s * 0.58
        c.drawImage(img(code), x + (s - isz) / 2, y + s * 0.3, isz, isz, mask='auto')
    if label:
        c.setFillColor(INK); fs = fit_label(label, s - 14, 15); c.setFont('FB', fs)
        c.drawCentredString(x + s / 2, y + s * 0.11, label)
    else:  # blank card: write-on line
        c.setStrokeColor(HexColor('#D5D8E3')); c.setLineWidth(1)
        c.line(x + 14, y + s * 0.16, x + s - 14, y + s * 0.16)


CARD = 140; GAP = 16


def card_grid(c, items, k0=0):
    gw = 3 * CARD + 2 * GAP; x0 = (W - gw) / 2
    top = H - M - 92
    for i, (label, code) in enumerate(items):
        r, col = divmod(i, 3)
        card(c, x0 + col * (CARD + GAP), top - CARD - r * (CARD + GAP), CARD, label, code, k0 + r + col)


def slot(c, x, y, s, n=None, color='#8EC5FF'):
    c.setFillColor(HexColor('#F6F7FB')); c.setStrokeColor(HexColor(color)); c.setLineWidth(2.5); c.setDash(7, 5)
    c.roundRect(x, y, s, s, 14, stroke=1, fill=1); c.setDash()
    c.setFillColor(HexColor('#D5D8E3')); c.circle(x + s / 2, y + s / 2, 9, stroke=0, fill=1)  # velcro dot
    if n is not None:
        c.setFillColor(HexColor(color)); c.circle(x + 4, y + s - 4, 15, stroke=0, fill=1)
        c.setFillColor(white); c.setFont('FB', 16); c.drawCentredString(x + 4, y + s - 10, str(n))


def check_box(c, x, y):
    c.setStrokeColor(HexColor('#2A9D8F')); c.setLineWidth(2.2); c.setFillColor(white)
    c.roundRect(x, y, 30, 30, 7, stroke=1, fill=1)


def board(c, title, sub, icon, color):
    page_base(c, title, sub)
    s = 148; gx = 54; gy = 20
    total_w = 2 * (s + 12 + 30) + gx
    x0 = (W - total_w) / 2
    top = H - M - 100
    n = 1
    for r in range(3):
        for col in range(2):
            x = x0 + col * (s + 42 + gx); y = top - s - r * (s + gy)
            slot(c, x, y, s, n, color); check_box(c, x + s + 10, y + s / 2 - 15); n += 1
    # all done strip
    y = M + 26
    c.setFillColor(HexColor('#EAF8E8')); c.roundRect(M + 10, y, W - 2 * M - 20, 74, 14, stroke=0, fill=1)
    c.drawImage(img(EXTRA['star']), M + 26, y + 13, 48, 48, mask='auto')
    c.drawImage(img(EXTRA['star']), W - M - 74, y + 13, 48, 48, mask='auto')
    c.setFillColor(HexColor('#2A9D8F')); c.setFont('FB', 22); c.drawCentredString(W / 2, y + 40, 'All done! Great job!')
    c.setFillColor(INK); c.setFont('FM', 10.5); c.drawCentredString(W / 2, y + 20, 'Tick the box or move the card here when a step is finished.')
    c.drawImage(img(icon), W - M - 58, H - M - 47, 42, 42, mask='auto')
    c.drawImage(img(icon), M + 16, H - M - 47, 42, 42, mask='auto')


c = canvas.Canvas(OUT, pagesize=PAGE)
c.setTitle('Visual Schedule Cards for Kids - Colorbloop'); c.setAuthor('Colorbloop')

# 1. start page
page_base(c, 'Visual Schedule Cards', 'Picture cards and charts to help little ones know what comes next')
y = H - M - 120
c.setFillColor(INK); c.setFont('FB', 16); c.drawString(M + 24, y, 'What’s inside'); y -= 24
inside = ['3 schedule boards: My Morning, My Day, My Bedtime (6 numbered steps each)',
          '1 First / Then board',
          '72 picture cards in 6 sheets: Morning, School & Learning, Play & Activities,',
          '      Places & People, Home & Bedtime, Feelings & Helpers',
          '12 blank cards to write or draw your own']
c.setFont('FM', 12)
for t in inside:
    c.drawString(M + 30, y, ('•  ' if not t.startswith(' ') else '') + t.strip()); y -= 20
y -= 14
c.setFont('FB', 16); c.drawString(M + 24, y, 'How to use'); y -= 24
steps = ['Print on card stock (choose "Fit to page"). Laminate for longer life.',
         'Cut out the cards along the dashed lines.',
         'Add a velcro dot to each card and to each grey dot on the boards.',
         'Pick the steps for the routine and stick them on the board in order.',
         'Show your child the next step. When it’s done, tick it or move it to "All done".']
c.setFont('FM', 12)
for i, t in enumerate(steps, 1):
    c.setFillColor(HexColor(RAINBOW[(i + 2) % 7])); c.circle(M + 36, y + 4, 9, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('FB', 11); c.drawCentredString(M + 36, y, str(i))
    c.setFillColor(INK); c.setFont('FM', 12); c.drawString(M + 54, y, t); y -= 24
# sample cards row
items = [SHEETS[0][1][3], SHEETS[0][1][5], SHEETS[2][1][4], SHEETS[4][1][11]]
s = 104; gw = 4 * s + 3 * 18; x0 = (W - gw) / 2
for i, (l, cd) in enumerate(items):
    card(c, x0 + i * (s + 18), M + 70, s, l, cd, i)
c.setFillColor(GREY); c.setFont('FM', 9.5)
c.drawCentredString(W / 2, M + 40, 'No velcro? Use a magnetic board, a pocket chart, or simply tape the cards in a row.')
c.showPage()

# 2-4. boards
board(c, 'My Morning', 'First this, then that! Put the morning steps in order.', EXTRA['sun'], '#F7C948')
c.showPage()
board(c, 'My Day', 'Here’s what we’re doing today.', EXTRA['house'], '#8EC5FF')
c.showPage()
board(c, 'My Bedtime', 'Time to get cozy! Follow the steps to bed.', EXTRA['moon'], '#B59CFF')
c.showPage()

# 5. first / then
page_base(c, 'First / Then', 'Put a card in each box. First we do this, then we do that!')
s = 220; gap = 40; x0 = (W - 2 * s - gap) / 2; y = H - M - 120 - s - 30
for i, (word, col) in enumerate([('First', '#F58BA8'), ('Then', '#8FD18B')]):
    x = x0 + i * (s + gap)
    c.setFillColor(HexColor(col)); c.roundRect(x, y + s + 8, s, 44, 12, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('FB', 26); c.drawCentredString(x + s / 2, y + s + 20, word)
    slot(c, x, y, s, None, col)
c.setFillColor(HexColor('#B9BECF'))
ax = W / 2; ay = y + s / 2
p = c.beginPath(); p.moveTo(ax - 14, ay + 14); p.lineTo(ax + 10, ay); p.lineTo(ax - 14, ay - 14); p.close(); c.drawPath(p, stroke=0, fill=1)
y2 = y - 50
c.setFillColor(HexColor('#F3EFFF')); c.roundRect(M + 10, M + 26, W - 2 * M - 20, y2 - M - 26, 14, stroke=0, fill=1)
c.setFillColor(PURPLE); c.setFont('FB', 15); c.drawString(M + 30, y2 - 30, 'Tips for grown-ups')
c.setFillColor(INK); c.setFont('FM', 11.5)
tips = ['Put the less-liked task under "First" and something fun under "Then".',
        'Keep it short and simple: two cards, a few calm words.',
        'Point to each card as you say it: "First shoes on, then park!"',
        'Celebrate when the "First" card is done, then enjoy the "Then"!']
yy = y2 - 56
for t in tips: c.drawString(M + 30, yy, '•  ' + t); yy -= 20
c.showPage()

# 6-11. card sheets
for si, (title, items) in enumerate(SHEETS, 1):
    page_base(c, title + ' Cards', f'Sheet {si} of 6  •  Cut along the dashed lines')
    card_grid(c, items, si)
    c.showPage()

# 12. blank cards
page_base(c, 'Make Your Own Cards', 'Draw a picture and write the word for anything else in your day')
card_grid(c, [('', None)] * 12)
c.showPage()

# 13. thank you
page_base(c, 'Thank You!', '')
c.setFillColor(INK); c.setFont('FB', 20); c.drawCentredString(W / 2, H / 2 + 120, 'Thank you for choosing Colorbloop!')
c.setFont('FM', 13)
for i, t in enumerate(['We hope these cards make your days a little smoother.',
                       'If you have a moment, a review on Etsy helps our small shop a lot.',
                       'Questions? Message us on Etsy - we’re happy to help.']):
    c.drawCentredString(W / 2, H / 2 + 80 - i * 24, t)
for i, cd in enumerate([EXTRA['star'], '1F917', EXTRA['star']]):
    c.drawImage(img(cd), W / 2 - 110 + i * 80, H / 2 - 60, 60, 60, mask='auto')
c.setFillColor(GREY); c.setFont('FM', 8)
c.drawCentredString(W / 2, M + 40, 'Pictures: Noto Emoji by Google, used under the Apache License 2.0 (apache.org/licenses/LICENSE-2.0).')
c.drawCentredString(W / 2, M + 28, '© Colorbloop. Layout and design for personal and single-classroom use.')
c.showPage()
c.save()
print('ok', OUT)
