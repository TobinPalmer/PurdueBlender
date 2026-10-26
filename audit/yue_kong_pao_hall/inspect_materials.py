import bpy
for mn in ['Purdue_Red_Brick','PAO | charcoal standing-seam roof','PAO | blue-gray reflective glazing']:
 m=bpy.data.materials[mn]
 print(m.name,[(n.type,dict((i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if i.name in ('Base Color','Roughness','Metallic','Transmission Weight'))) for n in m.node_tree.nodes],[(l.from_node.type,l.to_node.type) for l in m.node_tree.links])
