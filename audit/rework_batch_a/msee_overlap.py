import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\materials_science_and_electrical_engineering_msee.blend')
for o in bpy.data.objects:
 if not o.name.startswith('MSEE'):continue
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[0]<-6.4 and hi[0]>-20.6 and lo[1]<-2.4 and hi[1]>-19.8 and hi[2]>1 and lo[2]<15:
  print(o.name,[[round(lo[i],2) for i in range(3)],[round(hi[i],2) for i in range(3)]])
