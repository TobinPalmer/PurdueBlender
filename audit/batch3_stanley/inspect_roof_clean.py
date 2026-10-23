import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['SC_Roof_and_Dormers'].objects:
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(q[i] for q in pts) for i in range(3)];hi=[max(q[i] for q in pts) for i in range(3)]
 print(o.name,tuple(round(hi[i]-lo[i],2) for i in range(3)), tuple(round((hi[i]+lo[i])/2,2) for i in range(3)),[m.name for m in o.data.materials if m] if o.type=='MESH' else '')
