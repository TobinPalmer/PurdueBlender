import bpy,json
from mathutils import Vector
p='modular/buildings/felix_haas_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
C=bpy.data.collections['Asset_felix_haas_hall']
def b(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(q[i] for q in ps),3) for i in range(3)],[round(max(q[i] for q in ps),3) for i in range(3)]]
rows=[]
for o in C.objects:
 if any(x in o.name.lower() for x in ['brick_wall_east','blue','projection','pavilion','limestone','inlay','window']):
  rows.append((o.name,o.type,b(o),list(o.data.materials) and [m.name for m in o.data.materials] if o.type=='MESH' else ''))
print(json.dumps(rows,indent=2))
