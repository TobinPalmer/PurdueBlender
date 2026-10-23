import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend')
for o in sorted(bpy.data.objects,key=lambda x:x.name):
 if 'Portico' in o.name or 'Column' in o.name or 'Door' in o.name:
  print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions))
