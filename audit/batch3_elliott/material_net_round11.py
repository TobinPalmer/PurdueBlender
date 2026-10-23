import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for name in ['ELLT_B3_Theatre_Seat_Brown_Fabric','ELLT_B3_Stage_Curtain_Red_Velour','ELLT_B3_Stage_Oak_Grain','ELLT_Exterior_Red_Brick_Bond_Estimated','ELLT_Roof_Red_Clay_Tile_Estimated']:
 m=bpy.data.materials.get(name);print('\n',name,tuple(round(x,3) for x in m.diffuse_color))
 for node in m.node_tree.nodes:
  print(node.name,node.type, 'props',[(k,round(v,3) if isinstance(v,(int,float)) else v) for k,v in node.items()])
 print('links',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
