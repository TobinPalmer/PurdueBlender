import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for o in bpy.data.collections['SC_Portico_and_Entrances'].objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
  print(o.name,[round(q,2) for q in lo],[round(q,2) for q in hi],'parent',o.parent.name if o.parent else None,'mats',[m.name for m in o.data.materials])
