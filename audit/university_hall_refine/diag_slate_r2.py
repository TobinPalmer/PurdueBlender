import bpy
m=bpy.data.materials['Univ_Slate_Roof']
for n in m.node_tree.nodes:
 print(n.name,n.type, 'input',n.inputs.get('Base Color').default_value if n.type=='BSDF_PRINCIPLED' else '')
 if n.type=='VALTORGB': print([(e.position,tuple(e.color)) for e in n.color_ramp.elements])
for l in m.node_tree.links: print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
