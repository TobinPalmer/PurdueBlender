import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
c=bpy.data.collections['SC_Interior_Shell']
for prefix in ['SC_GradHub','SC_Lobby','SC_Research']:
 o=[x for x in c.objects if x.name.startswith(prefix) and x.type=='MESH']
 pts=[x.matrix_world@Vector(c) for x in o for c in x.bound_box]
 print(prefix,len(o),[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)])
