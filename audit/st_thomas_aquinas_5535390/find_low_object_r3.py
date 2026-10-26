import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]; c=bpy.data.collections.get("Asset_massing_st_thomas_aquinas_5535390")
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in c.all_objects:
 if o.type!="MESH":continue
 e=o.evaluated_get(dg);m=e.to_mesh()
 try:
  z=[(e.matrix_world@v.co).z for v in m.vertices]
  if z and min(z)<-0.05:rows.append({"name":o.name,"min_z":min(z),"max_z":max(z),"loc":list(o.location),"parent":o.parent.name if o.parent else None})
 finally:e.to_mesh_clear()
(Path(__file__).resolve().parent/"low_object_scan_r3.json").write_text(json.dumps(rows,indent=2)+"\n")
print(json.dumps(rows,indent=2))
