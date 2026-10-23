import bpy,json
from mathutils import Vector
c=bpy.data.collections['Asset_niswonger_aviation_tech']
r=[]
for o in c.all_objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];r.append(dict(name=o.name,bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],materials=[m.name for m in o.data.materials if m]))
json.dump(r,open('audit/batch2_niswonger/inspection.json','w'),indent=2)
