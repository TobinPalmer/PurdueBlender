import bpy,json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=p)
a=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
out=[]
for o in a.all_objects:
 if o.type=='MESH':
  b=[o.matrix_world@Vector(c) for c in o.bound_box]
  out.append({'name':o.name,'collection':[c.name for c in o.users_collection], 'bounds':[[round(min(v[i] for v in b),2),round(max(v[i] for v in b),2)] for i in range(3)],'material':[m.name if m else None for m in o.data.materials]})
open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_r1\object_inventory_saved_r2_pre.json','w').write(json.dumps(out,indent=2))
print('objects',len(out))
