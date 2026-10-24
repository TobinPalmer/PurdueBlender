import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('KNOY_Ground_TracePartition_'):continue
 p=[o.matrix_world@Vector(c) for c in o.bound_box];mn=[min(v[i] for v in p) for i in range(3)];mx=[max(v[i] for v in p) for i in range(3)]
 if mn[0]<8 and mx[0]>-5 and mn[1]<-15 and mx[1]>-30:
  print(o.name,'loc',tuple(round(v,2) for v in o.location),'dim',tuple(round(v,2) for v in o.dimensions),'yaw',round(o.rotation_euler.z,2),'bounds', [round(v,2) for v in mn[:2]+mx[:2]])
