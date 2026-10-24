import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/materials_science_and_electrical_engineering_msee.blend'))
c=next(x for x in bpy.data.collections if x.name.startswith('Asset_'))
for o in c.all_objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[0]<10 and hi[0]>-25 and lo[1]<13 and hi[1]>-5 and hi[2]>1 and hi[2]<15:
  print(o.name,[[round(lo[i],2) for i in range(3)],[round(hi[i],2) for i in range(3)]])
