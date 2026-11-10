"""Thankful Turkey cut-color-paste craft (Colorbloop). Vector art drawn here with reportlab; small pictures: Noto Emoji (Apache 2.0).
usage: [PAGESIZE=A4] make_pdf.py FREDOKA_DIR COLORBLOOP_FONT_DIR PNG_DIR OUT.pdf
"""
import sys, os, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

DL, FD, XP, OUT = sys.argv[1:5]
PAGE = A4 if os.environ.get('PAGESIZE') == 'A4' else letter
W, H = PAGE
M = 30
pdfmetrics.registerFont(TTFont('FB', f'{DL}/Fredoka-Bold.ttf'))
pdfmetrics.registerFont(TTFont('FM', f'{DL}/Fredoka-Medium.ttf'))
pdfmetrics.registerFont(TTFont('TR', f'{FD}/ColorbloopTrace.ttf'))
pdfmetrics.registerFont(TTFont('OL', f'{FD}/ColorbloopOutline.ttf'))

INK = HexColor('#2B2B3A'); GREY = HexColor('#9AA0B4'); LIGHT = HexColor('#C9CDD8')
ORANGE = HexColor('#E5732B'); CREAMBAR = HexColor('#FFF1E0')
BODY = HexColor('#9C6B3F'); BELLY = HexColor('#EBC896'); BEAK = HexColor('#F5A93B'); WATTLE = HexColor('#D9393E')
FEATHERS = ['#D9393E', '#E5732B', '#F2B632', '#5B9E3F', '#2E8C9A', '#7B4FA0']
RAINBOW = ['#D9393E', '#E5732B', '#F2B632', '#5B9E3F', '#2E8C9A', '#7B4FA0']
LW = 3.2  # cut-outline width


def pic(c, n, x, y, s): c.drawImage(f'{XP}/{n}.png', x, y, s, s, mask='auto')


def rainbow_text(c, x, y, text, font, size):
    w = pdfmetrics.stringWidth(text, font, size); x -= w / 2; i = 0
    for ch in text:
        if ch != ' ': c.setFillColor(HexColor(RAINBOW[i % 6])); i += 1
        c.setFont(font, size); c.drawString(x, y, ch); x += pdfmetrics.stringWidth(ch, font, size)


def frame(c, title, subtitle):
    c.setStrokeColor(ORANGE); c.setLineWidth(2); c.roundRect(M - 10, M - 10, W - 2 * M + 20, H - 2 * M + 20, 16, stroke=1, fill=0)
    c.setFillColor(ORANGE); c.roundRect(M, H - M - 50, W - 2 * M, 50, 14, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('FB', 26); c.drawCentredString(W / 2, H - M - 34, title)
    pic(c, 'leaf', M + 8, H - M - 44, 38); pic(c, 'leaf', W - M - 46, H - M - 44, 38)
    c.setFillColor(INK); c.setFont('FM', 12); c.drawCentredString(W / 2, H - M - 70, subtitle)
    rainbow_text(c, W / 2, M + 2, 'colorbloop', 'FB', 12)
    c.setFillColor(GREY); c.setFont('FM', 7); c.drawCentredString(W / 2, M - 7, 'For personal and classroom use only. Please do not resell or share the file.')


def scissors_note(c, y):
    pic(c, 'scissors', M + 6, y - 4, 18)
    c.setFillColor(GREY); c.setFont('FM', 9); c.drawString(M + 28, y, 'Cut along the thick outlines.')


# ---------- shapes (origin = given point, s = scale) ----------
def feather_path(c, w, h):
    p = c.beginPath()
    p.moveTo(-w * 0.10, 0)
    p.curveTo(w * 0.62, h * 0.22, w * 0.56, h * 0.97, 0, h)
    p.curveTo(-w * 0.56, h * 0.97, -w * 0.62, h * 0.22, -w * 0.10, 0)
    p.close(); return p


def feather(c, x, y, w, h, color=None, angle=0, spine=True):
    c.saveState(); c.translate(x, y); c.rotate(angle)
    c.setStrokeColor(INK); c.setLineWidth(LW); c.setLineJoin(1)
    c.setFillColor(HexColor(color) if color else white)
    c.drawPath(feather_path(c, w, h), stroke=1, fill=1)
    if spine:
        c.setLineWidth(1.4); c.setStrokeColor(INK if color is None else HexColor('#00000000'))
        if color is None:
            c.setStrokeColor(LIGHT)
        else:
            c.setStrokeColorRGB(1, 1, 1, alpha=0.55)
        c.line(0, h * 0.04, 0, h * 0.16)
    c.restoreState()


def foot(c, x, y, s, colored, flip=False):
    c.saveState(); c.translate(x, y); c.scale(-s if flip else s, s)
    c.setStrokeColor(INK); c.setLineWidth(LW / s); c.setLineJoin(1); c.setLineCap(1)
    c.setFillColor(BEAK if colored else white)
    p = c.beginPath()
    p.moveTo(-8, 60); p.lineTo(-8, 26)
    p.curveTo(-30, 18, -46, 4, -44, -6); p.curveTo(-40, -14, -30, -10, -22, -2)
    p.curveTo(-18, -16, -8, -22, 0, -22); p.curveTo(8, -22, 18, -16, 22, -2)
    p.curveTo(30, -10, 40, -14, 44, -6); p.curveTo(46, 4, 30, 18, 8, 26)
    p.lineTo(8, 60); p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def body(c, cx, cy, s, colored):
    """Body + head as one piece. cy = centre of body ellipse."""
    bw, bh, hr = 118 * s, 128 * s, 74 * s
    hx, hy = cx, cy + bh * 0.92
    c.setStrokeColor(INK); c.setLineJoin(1)
    # outer outline (double width, then fill covers inner half -> union outline)
    c.setLineWidth(LW * 2)
    c.ellipse(cx - bw, cy - bh, cx + bw, cy + bh, stroke=1, fill=0)
    c.circle(hx, hy, hr, stroke=1, fill=0)
    c.setFillColor(BODY if colored else white)
    c.ellipse(cx - bw, cy - bh, cx + bw, cy + bh, stroke=0, fill=1)
    c.circle(hx, hy, hr, stroke=0, fill=1)
    # inner details (thin lines - not cut lines)
    c.setLineWidth(2)
    c.setFillColor(BELLY if colored else white)
    c.ellipse(cx - bw * 0.62, cy - bh * 0.82, cx + bw * 0.62, cy + bh * 0.42, stroke=1, fill=1)
    # wings
    for sgn in (-1, 1):
        p = c.beginPath()
        x0 = cx + sgn * bw * 0.68
        p.moveTo(x0, cy + bh * 0.35)
        p.curveTo(x0 + sgn * bw * 0.34, cy + bh * 0.1, x0 + sgn * bw * 0.26, cy - bh * 0.5, x0 + sgn * bw * 0.02, cy - bh * 0.62)
        p.curveTo(x0 - sgn * bw * 0.10, cy - bh * 0.3, x0 - sgn * bw * 0.10, cy + bh * 0.1, x0, cy + bh * 0.35)
        c.setFillColor(HexColor('#7E5230') if colored else white)
        c.drawPath(p, stroke=1, fill=1)
    # eyes
    for sgn in (-1, 1):
        ex, ey = hx + sgn * hr * 0.36, hy + hr * 0.22
        c.setFillColor(white); c.circle(ex, ey, hr * 0.2, stroke=1, fill=1)
        c.setFillColor(INK); c.circle(ex + sgn * hr * 0.04, ey - hr * 0.02, hr * 0.1, stroke=0, fill=1)
        c.setFillColor(white); c.circle(ex + sgn * hr * 0.07, ey + hr * 0.03, hr * 0.035, stroke=0, fill=1)
    # beak
    p = c.beginPath(); by = hy - hr * 0.12
    p.moveTo(hx - hr * 0.22, by + hr * 0.05); p.lineTo(hx + hr * 0.22, by + hr * 0.05); p.lineTo(hx, by - hr * 0.32); p.close()
    c.setFillColor(BEAK if colored else white); c.drawPath(p, stroke=1, fill=1)
    # wattle
    p = c.beginPath(); wx, wy = hx + hr * 0.16, by - hr * 0.12
    p.moveTo(wx, wy); p.curveTo(wx + hr * 0.2, wy - hr * 0.1, wx + hr * 0.2, wy - hr * 0.5, wx + hr * 0.07, wy - hr * 0.55)
    p.curveTo(wx - hr * 0.05, wy - hr * 0.5, wx - hr * 0.05, wy - hr * 0.2, wx, wy)
    c.setFillColor(WATTLE if colored else white); c.drawPath(p, stroke=1, fill=1)
    # cheeks
    if colored:
        c.setFillColorRGB(0.95, 0.5, 0.55, alpha=0.6)
        for sgn in (-1, 1): c.circle(hx + sgn * hr * 0.6, hy - hr * 0.2, hr * 0.11, stroke=0, fill=1)
    # belly text
    c.setFillColor(INK if not colored else HexColor('#7E5230'))
    fs = 30 * s
    if colored:
        c.setFont('FB', fs)
    else:
        c.setFont('OL', fs)
    c.drawCentredString(cx, cy - bh * 0.30, 'Thankful')
    c.setFont('FM', 11 * s); c.setFillColor(INK)
    c.drawCentredString(cx, cy - bh * 0.56, 'Name:')
    c.setStrokeColor(GREY); c.setLineWidth(1.2)
    c.line(cx - bw * 0.42, cy - bh * 0.66, cx + bw * 0.42, cy - bh * 0.66)
    return hy + hr  # top


def writing_lines(c, x0, x1, y, n, gap):
    for i in range(n):
        yy = y - i * gap
        c.setStrokeColor(GREY); c.setLineWidth(1.1); c.setDash(); c.line(x0, yy, x1, yy)
        c.setStrokeColor(LIGHT); c.setDash(3, 3); c.setLineWidth(0.9); c.line(x0, yy + gap * 0.42, x1, yy + gap * 0.42); c.setDash()


# ---------- feather grids ----------
def feather_grid(c, content, colors=None):
    """3x2 feathers; content(c, i, fx, fy_bottom, fw, fh) draws inside each."""
    top = H - M - 92; bottom = M + 28
    fh = (top - bottom - 18) / 2; fw = (W - 2 * M - 30) / 3 * 0.98
    for i in range(6):
        col, row = i % 3, i // 3
        fx = M + 15 + fw / 2 + col * (W - 2 * M - 30) / 3
        fy = top - (row + 1) * fh - row * 18
        feather(c, fx, fy, fw, fh, colors[i] if colors else None)
        content(c, i, fx, fy, fw, fh)


def thankful_content(colored):
    def f(c, i, fx, fy, fw, fh):
        c.setFillColor(white if colored else INK)
        c.setFont('FB', 13); c.drawCentredString(fx, fy + fh * 0.74, 'I am')
        c.drawCentredString(fx, fy + fh * 0.74 - 16, 'thankful for')
        if colored:
            c.setFillColor(white)
            p = c.beginPath(); bw = fw * 0.34
            c.roundRect(fx - bw, fy + fh * 0.30, 2 * bw, fh * 0.30, 10, stroke=0, fill=1)
            writing_lines(c, fx - bw + 8, fx + bw - 8, fy + fh * 0.52, 3, fh * 0.085)
        else:
            bw = fw * 0.30
            writing_lines(c, fx - bw, fx + bw, fy + fh * 0.53, 3, fh * 0.085)
    return f


WORDS = [('family', 'family'), ('friends', 'friends'), ('food', 'pie'), ('home', 'home'), ('pets', 'pet'), ('toys', 'toys')]


def trace_content(c, i, fx, fy, fw, fh):
    word, img = WORDS[i]
    c.setFillColor(INK); c.setFont('FB', 12); c.drawCentredString(fx, fy + fh * 0.78, 'I am thankful for')
    s = fw * 0.40; pic(c, img, fx - s / 2, fy + fh * 0.44, s)
    fs = 34 if len(word) <= 5 else 28
    c.setFont('TR', fs); c.setFillColor(INK); c.drawCentredString(fx, fy + fh * 0.30, word)
    c.setStrokeColor(GREY); c.setLineWidth(1); c.line(fx - fw * 0.30, fy + fh * 0.30, fx + fw * 0.30, fy + fh * 0.30)


def draw_content(c, i, fx, fy, fw, fh):
    c.setFillColor(INK); c.setFont('FB', 12); c.drawCentredString(fx, fy + fh * 0.80, 'Draw what you')
    c.drawCentredString(fx, fy + fh * 0.80 - 14, 'are thankful for')
    c.setStrokeColor(LIGHT); c.setLineWidth(1.2); c.setDash(4, 3)
    bw = fw * 0.30; c.roundRect(fx - bw, fy + fh * 0.30, 2 * bw, fh * 0.38, 10, stroke=1, fill=0); c.setDash()


# ---------- assembled turkey ----------
def assembled(c, cx, cy, s, colored, write=False):
    n = 6 if write else 7
    fw, fh = (118 * s, 250 * s) if write else (92 * s, 250 * s)
    for k in range(n):
        a = (-64 + k * 128 / (n - 1)) if not write else (-62 + k * 124 / (n - 1))
        col = FEATHERS[k % 6] if colored else None
        bx = cx + math.sin(math.radians(-a)) * 0  # all from same base
        feather(c, cx, cy + 20 * s, fw, fh, col, angle=a, spine=False)
        if write:
            c.saveState(); c.translate(cx, cy + 20 * s); c.rotate(a)
            writing_lines(c, -fw * 0.26, fw * 0.26, fh * 0.80, 2, 20 * s)
            c.restoreState()
    foot(c, cx - 40 * s, cy - 150 * s, 0.75 * s, colored)
    foot(c, cx + 40 * s, cy - 150 * s, 0.75 * s, colored)
    body(c, cx, cy - 40 * s, 0.82 * s, colored)


# ---------- pages ----------
c = canvas.Canvas(OUT, pagesize=PAGE)
c.setTitle('Thankful Turkey Craft - Colorbloop'); c.setAuthor('Colorbloop')

# 1 cover / how-to
frame(c, 'Thankful Turkey Craft', 'Color, cut, write & glue  -  a Thanksgiving craft for ages 3-7')
assembled(c, W / 2, H * 0.52, 0.95, True)
y = H * 0.25
c.setFillColor(CREAMBAR); c.roundRect(M + 10, M + 24, W - 2 * M - 20, y - M - 12, 14, stroke=0, fill=1)
steps = [('crayon', '1. Color the turkey and the feathers.'), ('scissors', '2. Cut out every piece.'),
         ('book', '3. Write or draw what you are thankful for.'), ('glue', '4. Glue the feathers behind the turkey, then add the feet.')]
c.setFont('FM', 12.5)
for k, (img, t) in enumerate(steps):
    yy = y - 22 - k * 27
    pic(c, img, M + 26, yy - 5, 20); c.setFillColor(INK); c.drawString(M + 54, yy, t)
c.setFillColor(GREY); c.setFont('FM', 9.5)
c.drawString(M + 26, M + 34, 'You need: crayons, safety scissors, a glue stick. Tip: print the turkey on card stock or glue it to a paper plate.')
c.showPage()

# 2 body + feet (to color)
frame(c, 'Turkey Body', 'Color your turkey, then cut it out')
scissors_note(c, H - M - 96)
top = body(c, W / 2, H * 0.47, 1.25, False)
foot(c, W / 2 - 120, M + 80, 1.15, False); foot(c, W / 2 + 120, M + 80, 1.15, False, flip=True)
c.showPage()

# 3 feathers - write
frame(c, 'Thankful Feathers', 'Write what you are thankful for, color, then cut')
feather_grid(c, thankful_content(False)); c.showPage()
# 4 feathers - trace
frame(c, 'Trace & Color Feathers', 'Trace the word, color the feather, then cut')
feather_grid(c, trace_content); c.showPage()
# 5 feathers - draw
frame(c, 'Draw & Color Feathers', 'For little ones: draw a picture instead of writing')
feather_grid(c, draw_content); c.showPage()
# 6 colored body
frame(c, 'Turkey Body (in color)', 'No time to color? Print in color and just cut')
scissors_note(c, H - M - 96)
body(c, W / 2, H * 0.47, 1.25, True)
foot(c, W / 2 - 120, M + 80, 1.15, True); foot(c, W / 2 + 120, M + 80, 1.15, True, flip=True)
c.showPage()
# 7 colored feathers
frame(c, 'Thankful Feathers (in color)', 'Write what you are thankful for, then cut')
feather_grid(c, thankful_content(True), FEATHERS); c.showPage()
# 8 coloring page (no cutting)
frame(c, 'Thankful Turkey Coloring Page', 'No scissors needed: color the turkey and write what you are thankful for on each feather')
assembled(c, W / 2, H * 0.37, 1.12, False, write=True)
c.showPage()
c.save()
print('ok', OUT)
