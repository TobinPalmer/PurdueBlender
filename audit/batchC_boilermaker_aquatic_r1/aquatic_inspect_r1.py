import bpy,json
from mathutils import Vector
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
terms=('shell','roof','wall','glazing bay','Purdue gold sign','entrance','gable','facade bay','roof truss')
out=[]
for o in asset.all_objects:
 if any(t.lower() in o.name.lower() for t in terms):
  if o.type=='MESH':
   bb=[o.matrix_world@Vector(c) for c in o.bound_box]
   bounds=[[round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)] for i in range(3)]
  else: bounds=None
  out.append({'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],'bounds':bounds,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []})
open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_object_inventory_r1.json','w').write(json.dumps(out,indent=2))
for x in out:
 if x['name'].startswith('AQUA |') and any(t.lower() in x['name'].lower() for t in ('shell','roof','wall','Purdue gold sign','entrance','gable','facade bay')): print(x)
