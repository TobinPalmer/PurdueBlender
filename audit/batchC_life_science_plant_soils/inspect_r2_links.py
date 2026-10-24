import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
m=bpy.data.materials['LSPS | mottled Purdue red-brown brick']; nt=m.node_tree
p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for s in p.inputs:
 if s.name=='Base Color': print('incoming',[(l.from_node.name,l.from_socket.name) for l in s.links])
for l in nt.links: print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
