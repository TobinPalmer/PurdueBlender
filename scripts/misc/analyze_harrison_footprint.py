import json
import math

with open('audit/official_building_references.json') as f:
    data = json.load(f)

b85 = [b for b in data['buildings'] if b.get('fid') == 85][0]
ring = b85['rings_xy_m'][0]
print(f"Total vertices: {len(ring)}")
print("AABB:", b85['aabb_xy_m'])
print("Center:", b85['official_polygon_center_xy_m'])
print("MinRotRect:", b85['minimum_rotated_rectangle'])

# Analyze vertices and edges
for i in range(len(ring) - 1):
    p1 = ring[i]
    p2 = ring[i+1]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    print(f"Edge {i:02d}->{i+1:02d}: ({p1[0]:.2f}, {p1[1]:.2f}) -> ({p2[0]:.2f}, {p2[1]:.2f}) | len={dist:6.2f}m, dx={dx:6.2f}, dy={dy:6.2f}, deg={angle:6.1f}")
