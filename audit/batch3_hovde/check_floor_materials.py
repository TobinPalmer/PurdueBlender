import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for n in ['HOVD_Pres_Floor','HOVD_Board_Floor','HOVD_Inferred_Hipped_Roof','HOVD_Roof_Slab']:
 o=bpy.data.objects[n];print(n, 'hide',o.hide_render, 'mat', [m.name for m in o.data.materials], 'loc',tuple(o.matrix_world.translation))
