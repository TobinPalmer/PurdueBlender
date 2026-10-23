import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for o in bpy.data.objects:
 if any(w in o.name.lower() for w in ('footprint','reference','outline','overlay','gold')):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];print(o.name,o.type,'hide_render',o.hide_render,'hide_set',o.hide_get(),'bounds',lo,hi,'mats',[m.name for m in o.data.materials] if o.type=='MESH' else '')
