import bpy,json,os
from mathutils import Vector
root=os.path.abspath('.')
path=os.path.join(root,'modular','buildings','life_science_plant_and_soils_laboratory.blend')
bpy.ops.wm.open_mainfile(filepath=path)
c=bpy.data.collections.get('Asset_life_science_plant_and_soils_laboratory')
items=[]
for child in c.children:
 for o in child.objects:
  if o.type!='MESH': continue
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  mins=[min(v[i] for v in bb) for i in range(3)]; maxs=[max(v[i] for v in bb) for i in range(3)]
  if mins[1] < -17.804 or 'greenhouse' in o.name.lower() or 'apron' in o.name.lower() or 'service' in o.name.lower():
   items.append({'collection':child.name,'name':o.name,'bounds':[[round(x,3) for x in mins],[round(x,3) for x in maxs]]})
print(json.dumps(items,indent=2))
