import bpy, json
from pathlib import Path
coll=bpy.data.collections.get('Asset_massing_st_thomas_aquinas_5535390')
deps=bpy.context.evaluated_depsgraph_get(); out=[]
for ob in coll.all_objects:
 if ob.type!='MESH': continue
 ev=ob.evaluated_get(deps); me=ev.to_mesh()
 try:
  if not me.vertices: continue
  pts=[ev.matrix_world @ v.co for v in me.vertices]
  lo=[min(float(p[i]) for p in pts) for i in range(3)]; hi=[max(float(p[i]) for p in pts) for i in range(3)]
  dims=[hi[i]-lo[i] for i in range(3)]
  if dims[2]>2 and min(dims[:2])<.12 and max(dims[:2])<.8:
   out.append({'name':ob.name,'bounds':[[round(x,3) for x in lo],[round(x,3) for x in hi]],'dimensions':[round(x,3) for x in dims],'materials':[s.material.name if s.material else None for s in ob.material_slots]})
 finally: ev.to_mesh_clear()
Path(__file__).resolve().parent.joinpath('rod_scan_r4.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
