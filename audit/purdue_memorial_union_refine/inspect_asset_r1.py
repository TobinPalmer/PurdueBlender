import bpy, json, hashlib
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
col=bpy.data.collections.get('Asset_purdue_memorial_union')
print('COLLECTION',col.name,'OBJECTS',len(col.all_objects))
for o in col.all_objects:
    if o.type not in {'MESH','CURVE','FONT'}: continue
    if not any(k in o.name.lower() for k in ('window','glazing','arch','south','roof','portal','dormer','entry','portico')): continue
    pts=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    bounds=[[round(min(v[i] for v in pts),2),round(max(v[i] for v in pts),2)] for i in range(3)]
    mats=[m.name if m else None for m in o.data.materials]
    print(o.name, o.type, bounds, 'mats=',mats[:3])
