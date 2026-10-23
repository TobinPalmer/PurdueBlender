import bpy,json
from mathutils import Vector
out=[]
for o in bpy.data.collections['Asset_lawson_hall'].all_objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];out.append({'name':o.name,'bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],'materials':[m.name for m in o.data.materials if m]})
open('audit/batch2_lawson/inspection.json','w').write(json.dumps(out,indent=2))
