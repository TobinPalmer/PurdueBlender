import bpy,json
from mathutils import Vector
c=bpy.data.collections['Asset_knoy_hall']
r={}
for o in c.all_objects:
 if o.type=='MESH':
  ps=[o.matrix_world@Vector(v) for v in o.bound_box];r[o.name]={'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]}
print(json.dumps(r))
