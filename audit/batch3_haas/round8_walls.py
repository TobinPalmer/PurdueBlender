import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
def b(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(q[i] for q in ps),3) for i in range(3)],[round(max(q[i] for q in ps),3) for i in range(3)]]
rows=[]
for o in C.objects:
 if o.type=='MESH' and ('wall' in o.name.lower() or 'envelope' in o.name.lower()):
  rows.append((o.name,b(o),len(o.data.polygons),[m.name for m in o.data.materials]))
print(json.dumps(rows,indent=2))
