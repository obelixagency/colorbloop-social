"""Build two derived fonts (SIL OFL 1.1, renamed per Reserved Font Name rules):
 - ColorbloopTrace  : dotted centerline letters from Andika (for tracing)
 - ColorbloopOutline: hollow outline letters from Fredoka Bold (for coloring)
"""
import sys, math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.fontBuilder import FontBuilder
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity

DL = sys.argv[1]
OUT = sys.argv[2]
CHARS = [chr(c) for c in range(0x20, 0x7F)]


class FlatPen(BasePen):
    def __init__(self, gs, steps=12):
        super().__init__(gs); self.contours = []; self.cur = None; self.steps = steps
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps; mt = 1 - t
            self.cur.append((mt**3*p0[0]+3*mt*mt*t*p1[0]+3*mt*t*t*p2[0]+t**3*p3[0],
                             mt**3*p0[1]+3*mt*mt*t*p1[1]+3*mt*t*t*p2[1]+t**3*p3[1]))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps; mt = 1 - t
            self.cur.append((mt*mt*p0[0]+2*mt*t*p1[0]+t*t*p2[0], mt*mt*p0[1]+2*mt*t*p1[1]+t*t*p2[1]))
    def _closePath(self):
        if self.cur and len(self.cur) >= 3: self.contours.append(self.cur)
        self.cur = None
    _endPath = _closePath


def glyph_geom(font, ch):
    gs = font.getGlyphSet(); name = font.getBestCmap().get(ord(ch))
    if name is None: return None, 0
    pen = FlatPen(gs); gs[name].draw(pen)
    fills, holes = [], []
    for c in pen.contours:
        ring = Polygon(c)
        if ring.exterior.is_ccw: holes.append(ring.buffer(0))
        else: fills.append(ring.buffer(0))
    geom = unary_union(fills) if fills else Polygon()
    if holes: geom = geom.difference(unary_union(holes))
    return geom, gs[name].width


def polys(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]


def draw_geom(g, glyphset_like=None):
    pen = TTGlyphPen(None)
    for p in polys(g):
        rings = [list(p.exterior.coords)[:-1]]
        # TrueType: outer clockwise, holes counter-clockwise
        ext = p.exterior
        if ext.is_ccw: rings[0] = rings[0][::-1]
        for h in p.interiors:
            pts = list(h.coords)[:-1]
            if not h.is_ccw: pts = pts[::-1]
            rings.append(pts)
        for r in rings:
            r = [(round(x), round(y)) for x, y in r]
            # dedupe consecutive
            rr = [r[0]] + [q for i, q in enumerate(r[1:]) if q != r[i]]
            if len(rr) < 3: continue
            pen.moveTo(rr[0])
            for q in rr[1:]: pen.lineTo(q)
            pen.closePath()
    return pen.glyph()


def dotted(geom, half_stroke, dot_r, spacing):
    kept = []
    for hs in (half_stroke, half_stroke * 0.72, half_stroke * 0.5):
        core = geom.buffer(-hs, join_style=1)
        for p in polys(core):
            for ring in [p.exterior] + list(p.interiors):
                L = ring.length
                n = max(1, int(L / (spacing / 6)))
                for i in range(n):
                    pt = ring.interpolate(i * L / n)
                    if all((pt.x-q.x)**2 + (pt.y-q.y)**2 >= (spacing*0.85)**2 for q in kept):
                        kept.append(pt)
    dots = [Point(q.x, q.y).buffer(dot_r, quad_segs=5) for q in kept]
    if not dots: return Polygon()
    return unary_union(dots).simplify(4)


def hollow(geom, t):
    inner = geom.buffer(-t, join_style=1)
    return geom.difference(inner).simplify(3)


def build(src, family, transform, out, upm_src):
    f = TTFont(src)
    cmap = {}; glyphs = {'.notdef': TTGlyphPen(None).glyph()}; metrics = {'.notdef': (500, 0)}
    order = ['.notdef']
    for ch in CHARS:
        geom, adv = glyph_geom(f, ch)
        if geom is None: continue
        gname = 'space' if ch == ' ' else f'uni{ord(ch):04X}'
        g = transform(geom) if not geom.is_empty else Polygon()
        glyphs[gname] = draw_geom(g)
        b = g.bounds if not g.is_empty else (0, 0, 0, 0)
        metrics[gname] = (adv, int(b[0]))
        cmap[ord(ch)] = gname; order.append(gname)
    fb = FontBuilder(upm_src, isTTF=True)
    fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap); fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    asc, desc = round(0.80 * upm_src), round(-0.30 * upm_src)
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    ps = family.replace(' ', '')
    fb.setupNameTable({
        'familyName': family, 'styleName': 'Regular', 'uniqueFontIdentifier': ps + '-Regular-1.0',
        'fullName': family, 'psName': ps + '-Regular', 'version': 'Version 1.000',
        'copyright': src_copyright(f),
        'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1.',
        'licenseInfoURL': 'https://openfontlicense.org',
    })
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, usWinAscent=asc, usWinDescent=-desc,
                sxHeight=f['OS/2'].sxHeight, sCapHeight=f['OS/2'].sCapHeight, fsType=0, achVendID='CBLP')
    fb.setupPost(); fb.save(out)
    print('saved', out, len(order))


def src_copyright(f):
    return (f['name'].getDebugName(0) or '') + ' Modified by Colorbloop, 2026.'


if __name__ == '__main__':
    # Andika: stems ~ 170 units @2048
    build(f'{DL}/Andika-Regular.ttf', 'Colorbloop Trace',
          lambda g: dotted(g, 80, 46, 165), f'{OUT}/ColorbloopTrace.ttf', 2048)
    fb = TTFont(f'{DL}/Fredoka-Bold.ttf')
    build(f'{DL}/Fredoka-Bold.ttf', 'Colorbloop Outline',
          lambda g: hollow(g, 22), f'{OUT}/ColorbloopOutline.ttf', fb['head'].unitsPerEm)


def rename_copy(src, out, family, upm_ratio=(0.80, -0.30)):
    """Andika with normalized vertical metrics, renamed per OFL RFN rules."""
    f = TTFont(src); upm = f['head'].unitsPerEm
    asc, desc = round(upm_ratio[0] * upm), round(upm_ratio[1] * upm)
    f['hhea'].ascent, f['hhea'].descent, f['hhea'].lineGap = asc, desc, 0
    o = f['OS/2']; o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap = asc, desc, 0
    o.usWinAscent, o.usWinDescent, o.fsType = asc, -desc, 0
    ps = family.replace(' ', '')
    n = f['name']
    for rec in list(n.names):
        if rec.nameID in (1, 3, 4, 6, 16, 17, 21, 22): n.removeNames(nameID=rec.nameID)
    n.setName(family, 1, 3, 1, 0x409); n.setName('Regular', 2, 3, 1, 0x409)
    n.setName(ps + '-Regular-1.0', 3, 3, 1, 0x409); n.setName(family, 4, 3, 1, 0x409)
    n.setName(ps + '-Regular', 6, 3, 1, 0x409)
    n.setName((n.getDebugName(0) or '') + ' Modified by Colorbloop, 2026.', 0, 3, 1, 0x409)
    for t in ('GSUB', 'GPOS', 'GDEF', 'Feat', 'Silf', 'Sill', 'Glat', 'Gloc', 'DSIG'):
        if t in f: del f[t]
    f.save(out); print('saved', out)

rename_copy(f'{DL}/Andika-Regular.ttf', f'{OUT}/ColorbloopPrint.ttf', 'Colorbloop Print')
