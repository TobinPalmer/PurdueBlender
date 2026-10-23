import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
m=bpy.data.materials['RAWL_CurtainWall_Glass']
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for n in m.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED':print(n.name,n.inputs['Base Color'].default_value[:],n.inputs['Transmission Weight'].default_value,n.inputs['Roughness'].default_value)
