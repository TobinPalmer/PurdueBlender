import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
m=bpy.data.materials['Historic_Slate_Roof_Procedural']
print('mat',m.name,'diffuse',list(m.diffuse_color))
for n in m.node_tree.nodes:
 print(n.name,n.type,{k:(tuple(v.default_value) if hasattr(v,'default_value') and hasattr(v.default_value,'__len__') else v.default_value) for k,v in n.inputs.items() if hasattr(v,'default_value') and (isinstance(v.default_value,float) or isinstance(v.default_value,int) or hasattr(v.default_value,'__len__'))})
 for out in n.outputs:
  print(' OUT',out.name,[(l.to_node.name,l.to_socket.name) for l in out.links])
