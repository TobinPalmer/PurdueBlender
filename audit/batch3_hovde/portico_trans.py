import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['HOVD_Portico_Entablature','HOVD_Portico_Cornice','HOVD_Portico_Pediment_Base','HOVD_Portico_Pediment_Crown','HOVD_Roof_Slab']:
 o=bpy.data.objects[n];print(n,'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'parent',o.parent.name,'world',tuple(o.matrix_world.translation),'dims',tuple(o.dimensions),'localbounds',tuple(o.dimensions))
