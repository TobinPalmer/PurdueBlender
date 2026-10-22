import json
import math

with open(r'C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_campus_buildings.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Origin: Bell Tower (40.42722, -86.91404)
ORIGIN_LAT = 40.42722
ORIGIN_LON = -86.91404
METERS_PER_DEG_LAT = 111139.0
METERS_PER_DEG_LON = 111139.0 * math.cos(math.radians(ORIGIN_LAT))

targets = ['union', 'hovde', 'mackey', 'msee', 'krannert', 'armstrong']
found = []

# Collect nodes if needed
nodes = {}
for el in data.get('elements', []):
    if el.get('type') == 'node':
        nodes[el['id']] = (el.get('lat'), el.get('lon'))

for el in data.get('elements', []):
    tags = el.get('tags', {})
    name = tags.get('name', '')
    for t in targets:
        if t in name.lower():
            coords = []
            if 'nodes' in el:
                for nid in el['nodes']:
                    if nid in nodes:
                        lat, lon = nodes[nid]
                        x = (lon - ORIGIN_LON) * METERS_PER_DEG_LON
                        y = (lat - ORIGIN_LAT) * METERS_PER_DEG_LAT
                        coords.append((x, y))
            min_x = min([c[0] for c in coords]) if coords else 0
            max_x = max([c[0] for c in coords]) if coords else 0
            min_y = min([c[1] for c in coords]) if coords else 0
            max_y = max([c[1] for c in coords]) if coords else 0
            cx = (min_x + max_x) / 2
            cy = (min_y + max_y) / 2
            w = max_x - min_x
            d = max_y - min_y
            found.append({
                'id': el.get('id'),
                'name': name,
                'levels': tags.get('building:levels'),
                'height': tags.get('height'),
                'center': (round(cx, 2), round(cy, 2)),
                'size': (round(w, 2), round(d, 2)),
                'tags': tags
            })

for item in found:
    print(f"Name: {item['name']} (ID: {item['id']}) | Center: {item['center']} | Size: {item['size']} | Levels: {item['levels']} | Height: {item['height']}")
