import bpy, json
from pathlib import Path
p=Path(r'modular/buildings/massing_pierce_hall_prce_e5f59eb.blend').resolve()
with bpy.data.libraries.load(str(p), link=False) as (src,dst):
    print('SCENES',src.scenes)
    print('COLLECTIONS',src.collections)
    print('OBJECTS',src.objects)
    dst.objects=src.objects[:]
print('OBJECT INFO')
for o in bpy.data.objects:
    print(o.name,o.type,'loc',list(o.location),'scale',list(o.scale),'rot',list(o.rotation_euler),'dim',list(o.dimensions),'bound',[[min((o.matrix_world@__import__('mathutils').Vector(c))[i] for c in o.bound_box),max((o.matrix_world@__import__('mathutils').Vector(c))[i] for c in o.bound_box)] for i in range(3)])
    if o.type=='MESH':
       print('mesh',len(o.data.vertices),len(o.data.polygons),'mat',[(m.name if m else None) for m in o.data.materials])
       print('verts sample',[tuple(v.co) for v in list(o.data.vertices)[:20]])
