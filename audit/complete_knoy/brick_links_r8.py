import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
m=bpy.data.materials['KNOY_Purdue_Red_Brick']
for l in m.node_tree.links: print(l.from_node.type,l.from_socket.name,'->',l.to_node.type,l.to_socket.name)
