import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in bpy.context.scene.objects:
 if any(c==C for c in o.users_collection) or o.type in {'CAMERA','LIGHT'}:continue
 if o.type not in {'MESH','CURVE','FONT'}: continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 print(o.name,o.type,tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma),o.hide_render)
