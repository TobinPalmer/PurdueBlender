import bpy,json
for m in bpy.data.materials:
 if m.name.startswith('VBS_'):
  p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  print(m.name,tuple(p.inputs['Base Color'].default_value), [(l.from_node.type,l.to_node.type) for l in m.node_tree.links])
