import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend');c=bpy.data.collections['Asset_stanley_coulter_hall']
items=[]
for o in c.all_objects:
 if o.type!='MESH':continue
 p=[o.matrix_world@Vector(q) for q in o.bound_box];lo=[min(q[i] for q in p) for i in range(3)];hi=[max(q[i] for q in p) for i in range(3)]
 if min(lo[0]+28,28-hi[0],lo[1]+25,29-hi[1])< -1 or hi[2]>15.8 or o.name.startswith('SC_Dormer_'):
  items.append((o.name,lo,hi,o.hide_render,o.hide_viewport,o.hide_get()))
for x in sorted(items,key=lambda q:max(abs(q[1][0]),abs(q[2][0]),abs(q[1][1]),abs(q[2][1])),reverse=True)[:120]:print(x)
print('count',len(items),'assetcount',len(c.all_objects),'archive',len(bpy.data.collections['SC_Unverified_Architectural_Options_R5'].all_objects))
