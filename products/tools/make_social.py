"""Social assets for an Etsy product: story, peek story, 5 carousel slides, 15s reel.
usage: make_social.py KEY FONT_DIR LISTING_IMG_PREFIX PDF BG_HEX "Headline" "pill 1" "pill 2" PAGE_A PAGE_B AUDIO_SRC [sample_pdf]
 - carousel = listing images (1500x1875 -> 1080x1350)
 - story = headline + page A; peek story = page B; reel = pages slideshow with gentle zoom + audio from AUDIO_SRC
"""
import sys, os, subprocess, tempfile, random
import pypdfium2 as P
from PIL import Image, ImageDraw, ImageFont, ImageFilter

KEY, FD, IMGP, PDF, BG, HEAD, PILL1, PILL2, PA, PB, AUDIO = sys.argv[1:12]
ASSETS = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
FB = lambda s: ImageFont.truetype(f'{FD}/Fredoka-Bold.ttf', s)
INK = (43, 43, 58); YEL = (247, 201, 72); BGC = tuple(int(BG[i:i + 2], 16) for i in (1, 3, 5))
DOTS = [(230, 57, 70), (244, 162, 97), (233, 196, 106), (42, 157, 143), (58, 134, 255), (131, 56, 236), (255, 93, 162), (255, 255, 255)]

doc = P.PdfDocument(PDF); doc.init_forms()
pages = [doc[i].render(scale=2.4, may_draw_forms=True).to_pil().convert('RGB') for i in range(len(doc))]


def canvas(w, h, seed):
    im = Image.new('RGB', (w, h), BGC); dr = ImageDraw.Draw(im); r = random.Random(seed)
    for _ in range(40):
        x, y, s = r.randint(0, w), r.randint(0, h), r.randint(6, 16)
        if 330 < y < h - 560 and 120 < x < w - 120: continue
        dr.ellipse((x - s, y - s, x + s, y + s), fill=r.choice(DOTS))
    return im, dr


def ctext(dr, w, y, s, f, fill='white', stroke=7):
    tw = dr.textlength(s, font=f)
    dr.text(((w - tw) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=INK)


def pill(dr, w, y, s, f, fill, color):
    tw = dr.textlength(s, font=f); bb = f.getbbox(s); h = bb[3] - bb[1]; x0 = (w - tw) / 2 - 40
    dr.rounded_rectangle((x0, y, x0 + tw + 80, y + h + 44), radius=(h + 44) // 2, fill=fill, outline=INK, width=5)
    dr.text(((w - tw) / 2, y + 22 - bb[1]), s, font=f, fill=color)


def page_card(im, pg, cx, y, w, angle=0):
    pg = pg.resize((w, int(w * pg.height / pg.width)), Image.LANCZOS)
    card = Image.new('RGBA', (pg.width + 60, pg.height + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((36, 40, pg.width + 36, pg.height + 40), fill=(0, 0, 0, 90))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); card.paste(pg, (30, 30))
    if angle: card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(card, (int(cx - card.width / 2), int(y)), card)


def fit_font(dr, s, maxw, size):
    while dr.textlength(s, font=FB(size)) > maxw: size -= 4
    return FB(size)


def story(name, pg, head, seed):
    im, dr = canvas(1080, 1920, seed)
    ctext(dr, 1080, 150, head, fit_font(dr, head, 1000, 96))
    page_card(im, pg, 540, 330, 760, -2)
    pill(dr, 1080, 1440, PILL1, fit_font(dr, PILL1, 880, 50), (200, 40, 59) if BG.lower() != '#c8283b' else (42, 157, 88), 'white')
    pill(dr, 1080, 1580, PILL2, fit_font(dr, PILL2, 800, 48), 'white', INK)
    pill(dr, 1080, 1720, "Search 'Colorbloop' on Etsy", FB(56), YEL, INK)
    im.save(f'{ASSETS}/{name}', quality=90)


story(f'story_etsy_{KEY}.jpg', pages[int(PA)], HEAD, 1)
story(f'story_etsy_{KEY}_peek.jpg', pages[int(PB)], 'Sneak peek inside!', 2)
for i in range(1, 6):
    Image.open(f'{IMGP}_{i}.jpg').convert('RGB').resize((1080, 1350), Image.LANCZOS).save(f'{ASSETS}/car_etsy_{KEY}_{i}.jpg', quality=90)

# reel: title card + 5 listing images, 2.4s each, slow zoom, crossfade
tmp = tempfile.mkdtemp()
frames = []
im, dr = canvas(1080, 1920, 3)
ctext(dr, 1080, 700, 'NEW on Etsy!', FB(120)); ctext(dr, 1080, 860, HEAD.replace('NEW: ', ''), fit_font(dr, HEAD.replace('NEW: ', ''), 1000, 90))
pill(dr, 1080, 1100, 'Instant download • Print at home', FB(50), YEL, INK)
im.save(f'{tmp}/s0.jpg'); frames.append(f'{tmp}/s0.jpg')
for i in range(1, 6):
    bg, _ = canvas(1080, 1920, 10 + i)
    li = Image.open(f'{IMGP}_{i}.jpg').convert('RGB').resize((1000, 1250), Image.LANCZOS)
    bg.paste(li, (40, 335)); p = f'{tmp}/s{i}.jpg'; bg.save(p); frames.append(p)
end, dr = canvas(1080, 1920, 20)
ctext(dr, 1080, 760, "Search 'Colorbloop'", FB(100)); ctext(dr, 1080, 900, 'on Etsy', FB(100))
pill(dr, 1080, 1100, PILL1, fit_font(dr, PILL1, 880, 50), 'white', INK)
end.save(f'{tmp}/s6.jpg'); frames.append(f'{tmp}/s6.jpg')
D = 2.2; X = 0.4
inputs = []; flt = []
for k, f in enumerate(frames):
    inputs += ['-loop', '1', '-t', str(D + X), '-i', f]
    flt.append(f"[{k}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':d={int((D + X) * 30)}:s=1080x1920:fps=30,format=yuv420p[v{k}]")
chain = '[v0]'; off = D
for k in range(1, len(frames)):
    out = f'[x{k}]'; flt.append(f"{chain}[v{k}]xfade=transition=fade:duration={X}:offset={off:.2f}{out}"); chain = out; off += D
total = off + X
cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-i', AUDIO, '-filter_complex', ';'.join(flt) + f";[{len(frames)}:a]atrim=0:{total:.2f},afade=t=out:st={total - 1:.2f}:d=1[a]",
       '-map', chain, '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-c:a', 'aac', '-b:a', '128k', '-t', f'{total:.2f}', '-movflags', '+faststart',
       f'{ASSETS}/reel_etsy_{KEY}.mp4']
subprocess.run(cmd, check=True)
print('ok', KEY, round(total, 1), 's')
