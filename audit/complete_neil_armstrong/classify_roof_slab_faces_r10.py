import json, math
from pathlib import Path
from PIL import Image

root = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_neil_armstrong')
faces = json.load(open(root / 'roof_slab_faces_r10.json', encoding='utf-8'))
image = Image.open(root / 'sources' / 'indiana_current_ortho_neil_extent.png').convert('RGB')
w, h = image.size
xmin, ymin, xmax, ymax = (-9675473.17973648, 4928688.31898462, -9675190.20021127, 4928833.11569478)
lat0, lon0 = 40.4274, -86.9137
ox, oy = -109.0, 400.1893310546875
R = 6378137.0
def merc(x, y):
    x += ox; y += oy
    lat = lat0 + y / 111040.0
    lon = lon0 + x / (111412.84 * math.cos(math.radians(lat0)))
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def pixel(x, y):
    mx, my = merc(x, y)
    return (max(0, min(w - 1, int((mx - xmin) / (xmax - xmin) * w))),
            max(0, min(h - 1, int((ymax - my) / (ymax - ymin) * h))))

result = {}
for name, rows in faces.items():
    out = []
    for row in rows:
        xy = row['centroid_local_xy']
        p = pixel(*xy)
        rgb = image.getpixel(p)
        r, g, b = rgb
        # Keep red ACM only for a clear red-family image sample; treat shadow/neutral samples as pale neutral roof appearance.
        material = 'red' if r > g * 1.12 and r > b * 1.10 and r > 80 else 'pale'
        out.append({**row, 'pixel': list(p), 'rgb': list(rgb), 'material_class': material})
    result[name] = out
with open(root / 'roof_slab_material_samples_r10.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({name: {'faces': len(rows), 'pale': sum(r['material_class'] == 'pale' for r in rows), 'red': sum(r['material_class'] == 'red' for r in rows)} for name, rows in result.items()}, indent=2))
