import json, math
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
raw = (root / 'roof_slab_top_polys_r9.json').read_text(encoding='utf-8-sig')
line = next(line for line in reversed(raw.splitlines()) if line.startswith('{'))
polys = json.loads(line)
img = Image.open(root / 'sources' / 'indiana_current_ortho_neil_extent.png').convert('RGBA')
w, h = img.size
xmin, ymin, xmax, ymax = (-9675473.17973648, 4928688.31898462, -9675190.20021127, 4928833.11569478)
lat0, lon0 = 40.4274, -86.9137
ox, oy = -109.0, 400.1893310546875
def local_to_merc(x, y):
    x += ox; y += oy
    lat = lat0 + y / 111040.0
    lon = lon0 + x / (111412.84 * math.cos(math.radians(lat0)))
    return 6378137.0 * math.radians(lon), 6378137.0 * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def pix(x, y):
    return ((x - xmin) / (xmax - xmin) * w, (ymax - y) / (ymax - ymin) * h)

draw = ImageDraw.Draw(img)
colors = {'ARMS_East_Roof_Slab': (0, 255, 255, 255), 'ARMS_West_Roof_Slab': (255, 70, 230, 255)}
for name, faces in polys.items():
    pts = []
    for face in faces:
        for x, y, _z in face:
            pts.append(pix(*local_to_merc(x, y)))
    # The repeated top-face vertices describe a tiled, continuous surface; draw each face edge.
    for face in faces:
        q = [pix(*local_to_merc(v[0], v[1])) for v in face]
        draw.line(q + [q[0]], fill=colors[name], width=2)
img.save(root / 'roof_slab_footprints_ortho_r9.png')
print('wrote roof_slab_footprints_ortho_r9.png; cyan=east slab, magenta=west slab')
