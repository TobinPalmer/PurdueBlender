import bpy
import json
from collections import Counter

def obj_bounds(obj):
    coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[round(min(v[i] for v in coords), 4), round(max(v[i] for v in coords), 4)] for i in range(3)]

rows = []
for obj in bpy.data.collections['Asset_mccutcheon_hall'].all_objects:
    if any(k in obj.name for k in ('Tower_', 'Tower', 'Window', 'Glass', 'Spandrel', 'Frame', 'Penthouse', 'PH_', 'Roof_Deck')):
        row = {'name': obj.name, 'type': obj.type}
        if obj.type == 'MESH':
            row['bounds'] = obj_bounds(obj)
            zs = sorted({round((obj.matrix_world @ v.co).z, 3) for v in obj.data.vertices})
            row['z_levels'] = zs if len(zs) < 80 else []
            row['unique_z_count'] = len(zs)
        rows.append(row)
print('MCUT_R4_GEOMETRY=' + json.dumps(rows, indent=2))
