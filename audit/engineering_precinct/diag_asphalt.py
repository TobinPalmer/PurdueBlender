import bpy
bpy.ops.wm.open_mainfile(filepath=r'audit/engineering_precinct/engineering_mall_foliage_library_review.blend')
m=bpy.data.materials['asphalt_01']
for n in m.node_tree.nodes:
 print(n.name,n.type,[(i.name,tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value')])
for l in m.node_tree.links: print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
