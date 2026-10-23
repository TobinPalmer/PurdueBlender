import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for o in sorted(bpy.data.objects,key=lambda o:o.name):
 if o.name.startswith(('HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_')) or o.name in ['HOVD_Portico_Entablature','HOVD_Portico_Pediment_Base','HOVD_Sign_Plaque','HOVD_Gold_Letters']:
  print(o.name,'loc',tuple(round(x,3) for x in o.location),'dim',tuple(round(x,3) for x in o.dimensions),'scale',tuple(round(x,3) for x in o.scale),'rot',tuple(round(x,3) for x in o.rotation_euler))
