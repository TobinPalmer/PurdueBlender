import bpy
from mathutils import Vector
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
for o in asset.all_objects:
 if o.type=='MESH' and ('facade bay' in o.name or 'vertical glazing mullion' in o.name or 'glazing sill' in o.name):
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  top=max(v.y for v in bb); bot=min(v.y for v in bb)
  if (bot+top)/2 > 48:
   print(o.name, 'center',round(sum(v.x for v in bb)/8,2),round((bot+top)/2,2),'bbox',[[round(min(v[i] for v in bb),2),round(max(v[i] for v in bb),2)] for i in range(3)])
