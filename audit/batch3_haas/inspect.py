import bpy,json
from pathlib import Path
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall'];r=[]
for o in c.all_objects:
 if o.type=='MESH':
  v=[o.matrix_world@Vector(x) for x in o.bound_box];r.append({'name':o.name,'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]})
Path('audit/batch3_haas/geometry.json').write_text(json.dumps(r,indent=2))
