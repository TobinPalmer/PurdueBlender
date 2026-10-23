import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['HOVD_Penthouse','HOVD_Penthouse_Louvers','HOVD_Pres_Floor','HOVD_Board_Floor','HOVD_Pres_Room_Wall_W','HOVD_Board_Room_Wall_W','HOVD_Inferred_Hipped_Roof','HOVD_Window_Sash_Detail']:
 o=bpy.data.objects[n];print(n,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions),tuple(round(x,2) for x in o.matrix_world.translation))
