import bpy, json
from mathutils import Vector
asset=bpy.data.collections['Asset_walc']
for o in sorted(asset.all_objects,key=lambda o:o.name):
 if o.name.startswith('WALC_Source906_Edge_0_'):
  ps=[o.matrix_world@Vector(c) for c in o.bound_box]
  b=[[round(min(p[i] for p in ps),2),round(max(p[i] for p in ps),2)] for i in range(3)]
  print(o.name, 'bounds', b, 'mats', [s.material.name if s.material else None for s in o.material_slots])
print('Materials:')
for m in bpy.data.materials:
 if m.name.startswith('WALC_Reference') or m.name.startswith('Bronze'):
  print(m.name,tuple(round(x,3) for x in m.diffuse_color),[(n.type, getattr(n,'inputs',{}).get('Base Color').default_value[:] if n.type=='BSDF_PRINCIPLED' else None) for n in m.node_tree.nodes] if m.use_nodes else None)
