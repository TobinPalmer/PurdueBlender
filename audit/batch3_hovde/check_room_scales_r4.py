import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for n in ['HOVD_Pres_Floor','HOVD_Board_Floor','HOVD_Pres_Room_Wall_W','HOVD_Pres_Wainscot_N','HOVD_Pres_Fireplace_Mantel']:
 o=bpy.data.objects[n];print(n,'scale',tuple(o.scale),'dims',tuple(o.dimensions),'loc',tuple(o.location))
