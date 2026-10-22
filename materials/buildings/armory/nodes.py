import bpy,json
obs=list(bpy.data.collections['Asset_armory'].all_objects)
print('COUNTS',len(obs))
for m in bpy.data.materials:
 if m.users:
  print(m.name,[(n.type, n.inputs['Base Color'].default_value[:] if n.type=='BSDF_PRINCIPLED' else '') for n in m.node_tree.nodes])
print('ROOFS',[(o.name,tuple(o.location),tuple(o.dimensions)) for o in obs if 'Roof' in o.name][:12])
