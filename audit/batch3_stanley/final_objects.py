import bpy
from mathutils import Vector
p=r'modular/buildings/stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['SC_Portico_3D_Text','SC_Portico_Rectangular_Stone_Portal_Surround','SC_Portico_Entablature','SC_Portico_Flat_Stone_Canopy']:
 o=bpy.data.objects.get(n);bb=[o.matrix_world@Vector(c) for c in o.bound_box];print(n,'loc',list(o.location),'rot',list(o.rotation_euler),'scale',list(o.scale),'bounds',[list(min(v[i] for v in bb) for i in range(3)),list(max(v[i] for v in bb) for i in range(3))])
