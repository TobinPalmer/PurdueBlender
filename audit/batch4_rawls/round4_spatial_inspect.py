import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects.get(n); print('\nOBJ',n,'loc',tuple(o.location),'dims',tuple(o.dimensions),'mat',[(m.name if m else None) for m in o.data.materials]);
 for v in o.bound_box[:]: pass
 print('bounds',[(min((o.matrix_world@Vector(c))[i] for c in o.bound_box),max((o.matrix_world@Vector(c))[i] for c in o.bound_box)) for i in range(3)])
center=Vector((10,20.5,12))
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bb=[o.matrix_world@Vector(c) for c in o.bound_box]
 mn=[min(v[i] for v in bb) for i in range(3)];mx=[max(v[i] for v in bb) for i in range(3)]
 if mn[0]<11 and mx[0]>9 and mn[1]<21.4 and mx[1]>19.5 and mn[2]<12.8 and mx[2]>11.2:
  print(o.name,'bounds',mn,mx,'mats',[m.name if m else None for m in o.data.materials])
