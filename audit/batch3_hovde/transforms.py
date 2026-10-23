import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['HOVD_Root','HOVD_Pres_Floor','HOVD_Pres_Desk_Top','HOVD_Board_Floor','HOVD_Col_Shaft_1','HOVD_Classical_Column_1']:
 o=bpy.data.objects[n];print(n,'parent',o.parent.name if o.parent else None,'loc',tuple(o.location),'world',tuple(o.matrix_world.translation),'rot',tuple(o.rotation_euler))
