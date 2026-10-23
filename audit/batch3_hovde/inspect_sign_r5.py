import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/hovde_hall.blend')
for n in ['HOVD_Sign_Plaque','HOVD_Gold_Letters','HOVD_Portico_Entablature','HOVD_Portico_Pediment_Base']:
 o=bpy.data.objects[n]; print(n,'loc',tuple(o.location),'scale',tuple(o.scale),'rot',tuple(o.rotation_euler),'dim',tuple(o.dimensions),'data',o.data.name)
