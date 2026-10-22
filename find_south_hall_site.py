import json, math

ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
lon_m = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
lat_m = 111040.0

with open(r'C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_campus_buildings.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
nodes = {e['id']: (e['lat'], e['lon']) for e in d['elements'] if e['type'] == 'node'}

print("Searching near Hillenbrand Hall:")
for w in d['elements']:
    if w.get('type') == 'way':
        pts = [nodes[nid] for nid in w.get('nodes', []) if nid in nodes]
        if pts:
            avg_lat = sum(p[0] for p in pts) / len(pts)
            avg_lon = sum(p[1] for p in pts) / len(pts)
            if 40.4245 <= avg_lat <= 40.4275 and -86.9280 <= avg_lon <= -86.9240:
                x = (avg_lon - ORIGIN_LON) * lon_m
                y = (avg_lat - ORIGIN_LAT) * lat_m
                name = w.get('tags', {}).get('name', 'Unnamed')
                print(f"  {name:35s} -> X: {x:7.1f}m, Y: {y:7.1f}m, ID: {w['id']}")
