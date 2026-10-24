import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend')
print('MATERIALS')
for n in ['KRAN_DrawingRoom_BlueFabric','KRAN_DrawingRoom_LimeFabric','KRAN_Photo_Oak','KRAN_Parrish_Warm_Oak','KRAN_Parrish_Oak_Edge','KRAN_Parrish_Counter_Laminate','KRAN_Interior_Dark_Bronze']:
 m=bpy.data.materials.get(n)
 if m:
  print(n, 'users',m.users,'nodes',[(x.name,x.type) for x in m.node_tree.nodes] if m.use_nodes else None)
print('objects',len(bpy.data.collections['Asset_krannert_building'].objects))
