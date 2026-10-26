import bpy
from mathutils import Vector
p=max([o for o in bpy.data.collections['Asset_walc'].all_objects if o.name=='WALC_R4_Masonry_Bay_Fields'][0].data.vertices,key=lambda v:v.co.x).co
for e in bpy.data.collections['Asset_walc'].all_objects:
 if e.name.startswith('WALC_Source906_Edge_') and e.type=='MESH' and e.name.endswith('_Band4'):
  q=[e.matrix_world@v.co for v in e.data.vertices]
  d=min((p.x-v.x)**2+(p.y-v.y)**2 for v in q)**.5
  if d<3: print(round(d,3),e.name,[[round(min(v[i] for v in q),2),round(max(v[i] for v in q),2)] for i in range(3)])
