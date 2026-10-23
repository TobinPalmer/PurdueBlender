import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for n in ('SC_Portico_Column_Plinth_0','SC_Portico_Column_Shaft_0','SC_Portico_Column_Capital_0','SC_Portico_Column_Plinth_3','SC_Portico_Column_Shaft_3','SC_Portico_Column_Capital_3'):
 o=bpy.data.objects.get(n); pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];print(n,lo,hi)
