"""Amazon A+ Content images for the live KDP paperbacks (Christmas Activity, ABC).
Modules: Standard Image Header (970x600), Standard Four Image & Text (4 squares), Comparison Chart (covers 300x600)."""
import os, sys, random
import pymupdf
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/cb")
from mockups import f, pages, paste_page, text_c, LOGO

OUT = "/tmp/claude-0/-home-claude-colorbloop-social/6a6c98f6-d6a1-5a0a-aa7f-84cf36a28643/scratchpad/aplus/out"
os.makedirs(OUT, exist_ok=True)
D = "/home/claude/cb/dist"
S = 2  # supersample, saved at 2x of Amazon minimums (970x600 -> 1940x1200)

BOOKS = {
    "xmascoloring": dict(interior="/mnt/user-data/uploads/Colorbloop_Etsy/_kdp/01_xmascoloring/xmascoloring-interior.pdf", cover="/mnt/user-data/uploads/Colorbloop_Etsy/_kdp/01_xmascoloring/xmascoloring-full-cover.pdf",
                 bg="#eef7ee", dots="#d3ebd3", acc="#1b7a3a",
                 fan=[4, 14, 46], squares=[(4, ""), (16, ""), (36, ""), (2, "")]),
    "thanksgiving": dict(interior="/mnt/user-data/uploads/Colorbloop_Etsy/_kdp/02_thanksgiving/thanksgiving-interior.pdf", cover="/mnt/user-data/uploads/Colorbloop_Etsy/_kdp/02_thanksgiving/thanksgiving-full-cover.pdf",
                bg="#fff4e3", dots="#fbe2bd", acc="#d9480f",
                fan=[4, 8, 22], squares=[(4, ""), (8, ""), (28, ""), (54, "")]),
}

def front_cover(pdf, width):
    d = pymupdf.open(pdf); p = d[0]; r = p.rect
    clip = pymupdf.Rect(r.x0 + r.width / 2 + 0.07 * 72, r.y0, r.x1, r.y1)   # right half = front (skip spine)
    z = width / clip.width
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def canvas(w, h, c, dots):
    bg = Image.new("RGBA", (w, h), c); d = ImageDraw.Draw(bg); r = random.Random(7)
    for _ in range(int(w * h / 9000)):
        x, y, s = r.randint(0, w), r.randint(0, h), r.randint(5, 13)
        d.ellipse((x - s, y - s, x + s, y + s), fill=dots)
    return bg


def header(k, b):
    W, H = 970 * S, 600 * S
    bg = canvas(W, H, b["bg"], b["dots"])
    cov = front_cover(b["cover"], 720)
    paste_page(bg, cov, 90, (H - cov.height * 760 // 720) // 2, 760, rot=3)
    pg = pages(b["interior"], b["fan"], 430)
    for i, im in enumerate(pg):
        paste_page(bg, im, 930 + i * 245, 150 + (60 if i == 1 else 0), 430, rot=(5 - i * 5), border=10)
    lg = LOGO.resize((420, int(LOGO.height * 420 / LOGO.width)))
    bg.alpha_composite(lg, (W - 460, H - lg.height - 40))
    p = f"{OUT}/{k}_header_970x600.jpg"; bg.convert("RGB").save(p, quality=92); return p


def squares(k, b):
    out = []
    for i, (idx, label) in enumerate(b["squares"]):
        W = 600
        bg = canvas(W, W, b["bg"], b["dots"])
        im = pages(b["interior"], [idx], 470)[0]
        crop = im.crop((0, 0, im.width, int(im.width * 0.95)))
        paste_page(bg, crop, 65, 35, 470, border=6)
        out.append(f"{OUT}/{k}_sq{i + 1}_600.jpg"); bg.convert("RGB").save(out[-1], quality=92)
    return out


def chart_cover(k, b):
    W, H = 300 * S, 600 * S
    bg = Image.new("RGBA", (W, H), "#ffffff")
    cov = front_cover(b["cover"], 520)
    paste_page(bg, cov, 30, (H - cov.height) // 2 - 20, 520, shadow=True)
    p = f"{OUT}/{k}_chart_300x600.jpg"; bg.convert("RGB").save(p, quality=92); return p


if __name__ == "__main__":
    for k, b in BOOKS.items():
        print(header(k, b)); print(*squares(k, b), sep="\n"); print(chart_cover(k, b))
