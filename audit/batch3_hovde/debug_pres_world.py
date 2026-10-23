import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for n in ['HOVD_Root','HOVD_Pres_Floor','HOVD_Pres_Desk_Top','HOVD_Pres_Chair_Seat']:
 o=bpy.data.objects[n];print(n,'loc',tuple(o.location),'world',tuple(o.matrix_world.translation),'bounds',[(round((o.matrix_world@__import__('mathutils').Vector(v))[0],2),round((o.matrix_world@__import__('mathutils').Vector(v))[1],2),round((o.matrix_world@__import__('mathutils').Vector(v))[2],2)) for v in o.bound_box][:2])
