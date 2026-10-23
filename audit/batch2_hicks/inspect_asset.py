import bpy,json
from mathutils import Vector
c=bpy.data.collections['Asset_hicks_library']
r=[]
for o in c.all_objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];r.append({'name':o.name,'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'mats':[m.name for m in o.data.materials]})
open('audit/batch2_hicks/inspection.json','w').write(json.dumps(r,indent=2))
print(json.dumps(r))
