import bpy,json
from mathutils import Vector
obs=list(bpy.data.collections['Asset_armory'].all_objects)
bounds=[o.matrix_world@Vector(c) for o in obs if o.type=='MESH' for c in o.bound_box]
print('BOUNDS',[[min(v[i] for v in bounds),max(v[i] for v in bounds)] for i in range(3)])
for m in bpy.data.materials:
 if m.users: print('MAT',m.name,m.diffuse_color[:],m.use_nodes)
for o in obs:
 print('OBJ',o.name,o.type,tuple(round(x,3) for x in o.dimensions),[s.material.name if s.material else None for s in o.material_slots])
