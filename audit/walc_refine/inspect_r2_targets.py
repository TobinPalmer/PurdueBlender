import bpy, json
from pathlib import Path
from mathutils import Vector
asset=bpy.data.collections['Asset_walc']
keys=('wall','band','window','glass','brick','limestone','roof','facade','ribbon','plaza','entry','mullion','roof')
items=[]
for o in sorted(asset.all_objects,key=lambda x:x.name):
 if not any(k in o.name.lower() for k in keys): continue
 if o.type not in {'MESH','CURVE','FONT'}: continue
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(corner) for corner in o.bound_box]
  bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
 else:
  bounds=None
 mats=[s.material.name if s.material else None for s in o.material_slots]
 items.append({'name':o.name,'type':o.type,'bounds_local_m':bounds,'dimensions':list(o.dimensions),'materials':mats,'collections':[c.name for c in o.users_collection]})
out=Path(__file__).with_name('inspect_r2_targets.json')
out.write_text(json.dumps(items,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'object_count':len(items),'report':str(out)}))
