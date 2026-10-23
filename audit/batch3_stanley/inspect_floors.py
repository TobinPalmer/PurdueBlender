import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['SC_Shell_Floor_0_Basement','SC_Shell_Floor_1_PianoNobile','SC_Shell_Floor_2','SC_Shell_Floor_3','SC_Shell_Floor_4_Attic','SC_Lobby_Terrazzo_Floor']:
 o=bpy.data.objects[n];ps=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(q[i] for q in ps) for i in range(3)];hi=[max(q[i] for q in ps) for i in range(3)];print(n,lo,hi)
