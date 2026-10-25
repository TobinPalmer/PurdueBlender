import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
col=bpy.data.collections['Asset_purdue_memorial_union']
for o in col.all_objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(c) for c in o.bound_box]; b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 if b[1][0]<-43 and b[1][1]<-37 and b[2][1]>13 and b[2][0]<25:
  print(o.name,[[round(q,2) for q in r] for r in b],[(m.name,tuple(round(c,2) for c in m.diffuse_color)) for m in o.data.materials if m])
