import bpy,json
from mathutils import Vector
p=r'modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for s in bpy.data.scenes:
 print('SCENE',s.name)
for c in bpy.data.collections:
 if 'massing_forney' in c.name:
  print('COLLECTION',c.name)
  for o in c.all_objects:
   pts=[o.matrix_world@Vector(v) for v in o.bound_box]
   print('OBJECT',o.name,o.type,'loc',tuple(o.location),'dims',tuple(o.dimensions),'bounds',[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)],'mats',[m.name for m in o.data.materials] if o.type=='MESH' else [])
