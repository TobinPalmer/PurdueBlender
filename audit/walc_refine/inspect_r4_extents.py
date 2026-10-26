import bpy
from mathutils import Vector
for o in bpy.data.collections['Asset_walc'].all_objects:
 if o.name.startswith('WALC_R4_') and o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  b=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
  far=max(pts,key=lambda p:p.x)
  print(o.name,len(o.data.vertices),[[round(v,3) for v in q] for q in b], 'maxpoint',tuple(round(x,4) for x in far))
