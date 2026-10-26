import bpy,json
from pathlib import Path
col=bpy.data.collections.get('ZTA_Schematic_Interior')
objs=[]
if col:
 for o in col.all_objects:
  if o.type=='MESH':
   coords=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
   bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
   objs.append({'name':o.name,'bounds':bounds,'materials':[m.name for m in o.data.materials if m]})
out={'collection':col.name if col else None,'count':len(objs),'objects':objs}
Path(__file__).with_name('independent_grade_r2_interior.json').write_text(json.dumps(out,indent=2),encoding='utf-8'); print(json.dumps({'collection':out['collection'],'count':len(objs),'sample':objs[:15]},indent=2))
