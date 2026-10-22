import json
import math

with open('audit/official_building_references.json', 'r', encoding='utf-8') as f:
    official_data = json.load(f)
official_buildings = official_data['buildings']

with open('modular/manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

# Collect all manifest asset objects and their bounding boxes
assets = manifest['assets']

# Check for each official building:
# 1) Name / Code match in manifest ID or object names
# 2) Spatial overlap with any manifest asset bounding box

results = []

for ob in official_buildings:
    code = ob['code'].lower()
    name = ob['name'].lower()
    fid = ob['fid']
    cx, cy = ob['official_polygon_center_xy_m']
    ox1, oy1, ox2, oy2 = ob['aabb_xy_m']
    
    # Check text matches
    matched_by_text = []
    for a in assets:
        aid = a['id'].lower()
        if code in aid or any(word in aid for word in name.split() if len(word) > 4):
            matched_by_text.append(a['id'])
            
    # Check spatial overlap
    overlapping_assets = []
    for a in assets:
        # a['bounds_world_m'] is [[min_x, max_x], [min_y, max_y], [min_z, max_z]]
        bx1, bx2 = a['bounds_world_m'][0]
        by1, by2 = a['bounds_world_m'][1]
        
        # Check if bounding boxes overlap
        if not (ox2 < bx1 or ox1 > bx2 or oy2 < by1 or oy1 > by2):
            # Compute overlap area
            ix1 = max(ox1, bx1)
            ix2 = min(ox2, bx2)
            iy1 = max(oy1, by1)
            iy2 = min(oy2, by2)
            if ix1 < ix2 and iy1 < iy2:
                overlap_area = (ix2 - ix1) * (iy2 - iy1)
                overlapping_assets.append((a['id'], a['kind'], overlap_area, a['object_count']))
                
    results.append({
        'fid': fid,
        'code': ob['code'],
        'name': ob['name'],
        'center': [cx, cy],
        'aabb': [ox1, oy1, ox2, oy2],
        'matched_by_text': matched_by_text,
        'overlapping_assets': overlapping_assets
    })

print(f"Total official buildings: {len(results)}")
completely_missing = [r for r in results if len(r['overlapping_assets']) == 0]
print(f"Completely missing (zero spatial overlap with ANY manifest asset): {len(completely_missing)}")

print("\n--- Top completely missing official buildings (by size or notable name) ---")
for r in completely_missing[:40]:
    width = r['aabb'][2] - r['aabb'][0]
    depth = r['aabb'][3] - r['aabb'][1]
    print(f"FID {r['fid']}: [{r['code']}] {r['name']} | Size: {width:.1f}m x {depth:.1f}m | Center: ({r['center'][0]:.1f}, {r['center'][1]:.1f})")
