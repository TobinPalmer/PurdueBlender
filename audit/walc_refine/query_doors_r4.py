import bpy
from mathutils import Vector
for o in bpy.data.collections['Asset_walc'].all_objects:
 if o.type!='MESH':continue
 if 'Classroom oak door' in o.name:
  ps=[o.matrix_world@Vector(c) for c in o.bound_box]
  b=[[round(min(p[i] for p in ps),2),round(max(p[i] for p in ps),2)] for i in range(3)]
  if b[1][0]<-35 or b[1][1]>40:print(o.name,b)
