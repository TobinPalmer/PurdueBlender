import bpy, json, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + '/modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
C = bpy.data.collections['Asset_krannert_building']
names = [
    'KRAN_Footprint_Reference_Wire', 'KRAN_Exterior_Masonry_Walls',
    'KRAN_Basement_Foundation_Walls', 'KRAN_Surrounding_Plaza_Paving',
    'KRAN_FloorSlab_SubBasement', 'KRAN_FloorSlab_Ground_L0',
    'KRAN_FloorSlab_Roof_Deck', 'KRAN_Limestone_Parapet_Coping',
    'KRAN_Rooftop_Mechanical_Penthouse',
    'KRAN_FloorSlab_Floor_L1', 'KRAN_FloorSlab_Floor_L2',
    'KRAN_FloorSlab_Floor_L3', 'KRAN_FloorSlab_Floor_L4',
    'KRAN_FloorSlab_Floor_L5', 'KRAN_FloorSlab_Floor_L6',
    'KRAN_FloorSlab_Floor_L7',
]
out = {}
for name in names:
    ob = bpy.data.objects.get(name)
    if not ob:
        continue
    deps = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(deps)
    mesh = ev.to_mesh()
    pts = [ev.matrix_world @ v.co for v in mesh.vertices]
    if pts:
        out[name] = {
            'type': ob.type,
            'location': list(ob.location),
            'dimensions': list(ob.dimensions),
            'vertex_count': len(pts),
            'bounds': [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)],
            'material_names': [m.name if m else None for m in ob.data.materials] if hasattr(ob.data, 'materials') else [],
        }
        if name == 'KRAN_Footprint_Reference_Wire':
            out[name]['vertices_xy'] = [[float(v.co.x), float(v.co.y)] for v in ob.data.vertices]
    ev.to_mesh_clear()
with open(ROOT + '/audit/batch2_krannert/structural_bounds_round3.json', 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
