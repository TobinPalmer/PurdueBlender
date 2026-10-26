import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend');m=bpy.data.materials['Historic_Slate_Roof_Procedural'];n=m.node_tree.nodes['Mix'];print(n.bl_idname,n.data_type,n.blend_type,n.clamp_factor,n.clamp_result)
for i,s in enumerate(n.inputs):print('IN',i,s.name,s.type,getattr(s,'default_value',None))
for i,s in enumerate(n.outputs):print('OUT',i,s.name,s.type)
for l in m.node_tree.links: print('LINK',l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)
