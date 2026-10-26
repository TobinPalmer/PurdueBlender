import bpy
from mathutils import Vector
for o in bpy.data.collections['Asset_walc'].all_objects:
 if any(k in o.name.lower() for k in ['door','entry','entrance','canopy','portal','facade']):
  if o.type=='MESH':
   ps=[o.matrix_world@Vector(c) for c in o.bound_box]
   b=[[round(min(p[i] for p in ps),1),round(max(p[i] for p in ps),1)] for i in range(3)]
  else: b=''
  print(o.name,o.type,b)
