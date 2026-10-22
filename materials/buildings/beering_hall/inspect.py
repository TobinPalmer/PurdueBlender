import bpy,json
from mathutils import Vector
c=bpy.data.collections.get('Asset_beering_hall')
obs=list(c.all_objects)
print('OBJECTS',len(obs))
for m in bpy.data.materials:
 print('MAT',m.name,list(m.diffuse_color),[(n.type,n.name) for n in m.node_tree.nodes] if m.node_tree else [])
print('SAMPLE',[(o.name,list(o.dimensions),[m.name for m in o.data.materials]) for o in obs if o.type=='MESH'][:65])
p=[o.matrix_world@Vector(v) for o in obs if o.type=='MESH' for v in o.bound_box]
print('BOUNDS',[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)])
