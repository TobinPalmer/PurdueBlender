import bpy, json, os
from mathutils import Vector

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'neil_armstrong_hall.blend')
OUT = os.path.join(ROOT, 'audit', 'complete_neil_armstrong', 'roof_slab_faces_r10.json')
bpy.ops.wm.open_mainfile(filepath=ASSET)
result = {}
for name in ('ARMS_East_Roof_Slab', 'ARMS_West_Roof_Slab'):
    obj = bpy.data.objects[name]
    rows = []
    for poly in obj.data.polygons:
        if poly.normal.z > 0.75:
            rows.append({
                'face_index': poly.index,
                'centroid_local_xy': [float((obj.matrix_world @ poly.center).x), float((obj.matrix_world @ poly.center).y)],
                'normal_local_z': float(poly.normal.z),
            })
    result[name] = rows
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({k: len(v) for k, v in result.items()}))
