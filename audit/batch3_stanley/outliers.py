import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
root=bpy.data.collections['Asset_stanley_coulter_hall']
for o in root.all_objects:
 if o.type=='MESH':
  bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
  lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]
  if max(hi[0]-lo[0],hi[1]-lo[1])>35 or min(lo[0],lo[1])<-35 or max(hi[0],hi[1])>35:
   print(o.name,tuple(round(x,2) for x in lo),tuple(round(x,2) for x in hi),'dims',tuple(round(x,2) for x in o.dimensions))
print('asset objs',len(root.all_objects))
