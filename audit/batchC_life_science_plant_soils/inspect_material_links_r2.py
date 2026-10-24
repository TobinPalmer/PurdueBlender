import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for name in ['LSPS | schematic clear facade glazing','LSPS | greenhouse clear glazing']:
 m=bpy.data.materials[name]
 print('\n',name)
 for n in m.node_tree.nodes:
  print(n.name,n.type,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if i.name in ['Base Color','Alpha','Roughness','Metallic','Color1','Color2','Fac']])
 for l in m.node_tree.links: print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
