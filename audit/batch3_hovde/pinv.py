import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['HOVD_Root','HOVD_Pres_Floor','HOVD_Pres_Desk_Top','HOVD_Col_Shaft_1','HOVD_Wall_E_0','HOVD_Pres_Room_Wall_W','HOVD_Classical_Column_1']:
 o=bpy.data.objects.get(n)
 if o:print(n,'parentinv',[[round(v,2) for v in row] for row in o.matrix_parent_inverse])
