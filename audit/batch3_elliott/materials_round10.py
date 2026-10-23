import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for n in ['ELLT_Exterior_Red_Brick_Bond_Estimated','ELLT_Exterior_Indiana_Limestone','ELLT_R8_Door_Glass_Estimated','ELLT_B3_Stage_Oak_Grain','ELLT_B3_Theatre_Seat_Brown_Fabric']:
 m=bpy.data.materials.get(n); print('\n',n, 'color',tuple(m.diffuse_color))
 if m.use_nodes:
  for node in m.node_tree.nodes:
   print(node.name,node.type,[(inp.name,tuple(round(v,3) for v in inp.default_value) if hasattr(inp.default_value,'__len__') and not isinstance(inp.default_value,str) else inp.default_value) for inp in node.inputs if inp.name in ('Base Color','Roughness','Metallic','Transmission Weight','Specular IOR Level','Alpha')])
