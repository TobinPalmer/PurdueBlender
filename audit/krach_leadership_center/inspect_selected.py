import bpy, json
from mathutils import Vector
out=[]
for o in bpy.data.objects:
 if o.type!='MESH': continue
 deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh(); pts=[o.matrix_world @ v.co for v in me.vertices]
 if pts: lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
 else: lo=hi=[]
 ev.to_mesh_clear()
 if any(x in o.name.lower() for x in ['shell','floor plate','lobby','roof','stair','canopy','entry walk','planter','foundation','glazing','window','facade']):
  out.append({'name':o.name,'bounds':[lo,hi],'mats':[m.name for m in o.data.materials if m]})
open(r'audit/krach_leadership_center/inspect_selected.json','w').write(json.dumps(out,indent=2))
