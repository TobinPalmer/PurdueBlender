import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Interior_Shell']:
 c=bpy.data.collections[cn];print('\n###',cn)
 for o in c.objects:
  if cn=='SC_Interior_Shell' and not (o.name.startswith('SC_Shell_Floor_') or o.name.startswith('SC_Lobby')): continue
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(q[i] for q in pts) for i in range(3)];hi=[max(q[i] for q in pts) for i in range(3)]
  mats=[m.name for m in o.data.materials if m] if o.type=='MESH' else []
  print(o.name, 'size',tuple(round(hi[i]-lo[i],2) for i in range(3)), 'at',tuple(round((lo[i]+hi[i])/2,2) for i in range(3)), 'mats',mats[:3])
