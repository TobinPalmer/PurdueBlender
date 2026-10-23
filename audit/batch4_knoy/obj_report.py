import bpy,json
from mathutils import Vector
c=bpy.data.collections['Asset_knoy_hall']
r=[]
for o in c.all_objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  r.append([o.name,[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)],len(o.data.polygons),[m.name for m in o.data.materials]])
open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_knoy\objects.json','w').write(json.dumps(r,indent=2))
