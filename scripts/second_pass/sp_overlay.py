"""Overlay a local-frame footprint (and optional wing rectangles) on a registered Web-Mercator aerial.
python sp_overlay.py aerial.png aerial_export.json origin_x origin_y footprint.json out.png [wings.json]
footprint.json: list of polygons [[x,y],...] in asset-local metres."""
import sys, json, math
from PIL import Image, ImageDraw
img, meta, ox, oy, fp, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6]
wings = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else []
m = json.load(open(meta)); e = m['extent']
im = Image.open(img).convert('RGB'); W, H = im.size
R = 6378137.0
def merc_to_ll(x, y):
    return math.degrees(math.atan(math.sinh(y / R))), math.degrees(x / R)
LAT0, LON0 = 40.4274, -86.9137
def ll_to_xy(lat, lon):
    return (lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)), (lat - LAT0) * 111040.0
def xy_to_ll(x, y):
    return y / 111040.0 + LAT0, x / (111412.84 * math.cos(math.radians(LAT0))) + LON0
def ll_to_px(lat, lon):
    mx = math.radians(lon) * R; my = R * math.asinh(math.tan(math.radians(lat)))
    return (mx - e['xmin']) / (e['xmax'] - e['xmin']) * W, (e['ymax'] - my) / (e['ymax'] - e['ymin']) * H
def loc_px(x, y):
    return ll_to_px(*xy_to_ll(x + ox, y + oy))
d = ImageDraw.Draw(im)
for poly in json.load(open(fp)):
    pts = [loc_px(*p) for p in poly]
    d.line(pts + [pts[0]], fill=(255, 0, 0), width=2)
for w in wings:
    pts = [loc_px(*p) for p in w['pts']]
    d.line(pts + [pts[0]], fill=tuple(w.get('color', (0, 255, 255))), width=2)
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    d.text((cx, cy), w['name'], fill=(255, 255, 0))
# local grid every 10 m
for gx in range(-80, 90, 10):
    a = loc_px(gx, -60); b = loc_px(gx, 80); d.line([a, b], fill=(0, 90, 255) if gx else (0, 255, 0), width=1)
    d.text(loc_px(gx, -58), str(gx), fill=(0, 200, 255))
for gy in range(-60, 90, 10):
    a = loc_px(-80, gy); b = loc_px(90, gy); d.line([a, b], fill=(0, 90, 255) if gy else (0, 255, 0), width=1)
    d.text(loc_px(-78, gy), str(gy), fill=(0, 200, 255))
im.save(out)
print('px per m approx', abs(loc_px(10, 0)[0] - loc_px(0, 0)[0]) / 10)
