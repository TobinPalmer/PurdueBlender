import bpy, json
from mathutils import Vector
from pathlib import Path

c = bpy.data.collections['Asset_niswonger_aviation_tech']
objs = []
for o in c.all_objects:
    if o.type != 'MESH':
        continue
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    objs.append({
        'name': o.name,
        'loc': [round(v, 3) for v in o.location],
        'dim': [round(v, 3) for v in o.dimensions],
        'bounds': [[round(v, 3) for v in lo], [round(v, 3) for v in hi]],
        'mats': [m.name if m else None for m in o.data.materials],
    })
Path('audit/batch4_niswonger/object_inventory.json').write_text(json.dumps({
    'filepath': bpy.data.filepath, 'collection': c.name,
    'objects': len(c.all_objects), 'mesh_objects': len(objs), 'meshes': objs,
    'materials': [m.name for m in bpy.data.materials if m.name.startswith('NISW_')],
}, indent=2))
