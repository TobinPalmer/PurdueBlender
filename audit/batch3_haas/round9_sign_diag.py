import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if 'Sign' in o.name or 'sign' in o.name:
  p=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type=='MESH' else []
  b=[[round(min(q[i] for q in p),2) for i in range(3)],[round(max(q[i] for q in p),2) for i in range(3)]] if p else []
  print(o.name,o.type,b,[m.name for m in o.data.materials] if o.type=='MESH' else '', getattr(o.data,'body','') if o.type=='FONT' else '')
