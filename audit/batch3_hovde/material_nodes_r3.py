import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for name in ['Purdue_Red_Brick','Bedford_Indiana_Limestone']:
 m=bpy.data.materials[name];print('\n',name)
 for n in m.node_tree.nodes:print(n.name,n.bl_idname)
 for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
