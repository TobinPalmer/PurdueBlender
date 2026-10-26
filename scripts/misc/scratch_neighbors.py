import json

with open('audit/official_building_references.json', 'r', encoding='utf-8') as f:
    official_data = json.load(f)

for b in official_data['buildings']:
    cx, cy = b['official_polygon_center_xy_m']
    dx = cx - (-57.6)
    dy = cy - (-96.6)
    dist = (dx*dx + dy*dy)**0.5
    if dist < 160:
        print(f"{b['code']:6s} {b['name'][:35]:35s} dist={dist:5.1f}m dx={dx:6.1f} dy={dy:6.1f}")
