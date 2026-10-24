import bpy
for p in [r'modular/buildings/hicks_library.blend',r'modular/buildings/lawson_hall.blend',r'modular/buildings/krannert_building.blend']:
 bpy.ops.wm.open_mainfile(filepath=p)
 print('\nFILE',p,'objects',len(bpy.data.objects),'materials',len(bpy.data.materials))
 for m in bpy.data.materials:
  if m.users:
   print('MAT',m.name,'users',m.users,'nodes',m.use_nodes, 'color',tuple(round(x,3) for x in m.diffuse_color[:3]))
