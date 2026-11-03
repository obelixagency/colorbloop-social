"""Extract Noto Emoji (Apache 2.0) SVGs from the @svgmoji/noto sprite and render PNGs.
usage: emoji_png.py SPRITE OUTDIR SIZE name=CODE [name=CODE ...]   (CODE like 1F9B7 or 1F468-200D-1F373)"""
import sys, os, cairosvg
import xml.etree.ElementTree as ET
sprite, out, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS); ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
root = ET.parse(sprite).getroot()
idx = {e.get('id'): e for e in root if e.tag == f'{{{NS}}}svg'}
os.makedirs(out, exist_ok=True)
bad = []
for arg in sys.argv[4:]:
    name, code = arg.split('=')
    e = idx.get(code) or idx.get(code + '-FE0F')
    if e is None: bad.append(arg); continue
    s = ET.tostring(e, encoding='unicode')
    cairosvg.svg2png(bytestring=s.encode(), write_to=f'{out}/{name}.png', output_width=size, output_height=size)
print('missing:', bad)
