import bpy,json,math
from mathutils import Vector
c=bpy.data.collections['Asset_knoy_hall']
r={'objects':len(c.all_objects),'root':[[float(x) for x in row] for row in bpy.data.objects['AssetRoot_knoy_hall'].matrix_world],'items':[],'materials':[]}
for o in c.all_objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  r['items'].append({'name':o.name,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'mat':[m.name if m else None for m in o.data.materials]})
for m in bpy.data.materials:
 if m.users:
  r['materials'].append({'name':m.name,'diffuse':list(m.diffuse_color),'nodes':m.use_nodes,'nodes_names':[n.name for n in m.node_tree.nodes] if m.use_nodes else []})
print(json.dumps(r,indent=2))
