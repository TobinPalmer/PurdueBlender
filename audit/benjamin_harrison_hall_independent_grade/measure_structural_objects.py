from pathlib import Path
import bpy,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];ASSET=ROOT/"modular/buildings/benjamin_harrison_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); col=bpy.data.collections["Asset_benjamin_harrison_hall"]
names=["HARR_Ground_Plinth_Base","HARR_North_Tower_Brick_Core","HARR_South_Tower_Brick_Core","HARR_Center_Pavilion_Main_Brick","HARR_Center_Pavilion_East_Block","HARR_Center_West_Pavilion_S","HARR_Center_West_Entrance_Bay","HARR_Center_West_Courtyard_Core","HARR_Center_West_North_Transition"]
deps=bpy.context.evaluated_depsgraph_get();out=[]
for name in names:
 o=col.objects.get(name)
 if not o: continue
 ev=o.evaluated_get(deps); mesh=ev.to_mesh(); pts=[ev.matrix_world@v.co for v in mesh.vertices]; zs=[p.z for p in pts]; z0=min(zs)
 base=[p for p in pts if abs(p.z-z0)<1e-4]
 base_ids={i for i,v in enumerate(mesh.vertices) if abs((ev.matrix_world@v.co).z-z0)<1e-4}
 edges=[[[float((ev.matrix_world@mesh.vertices[a].co).x),float((ev.matrix_world@mesh.vertices[a].co).y)],[float((ev.matrix_world@mesh.vertices[b].co).x),float((ev.matrix_world@mesh.vertices[b].co).y)]] for edge in mesh.edges for a,b in [edge.vertices] if a in base_ids and b in base_ids]
 out.append({"name":name,"bounds":[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],"base_z":z0,"base_xy":[[p.x,p.y] for p in base],"base_edges":edges})
 ev.to_mesh_clear()
path=Path(__file__).resolve().parent/"structural_object_measurements.json";path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps([{k:v for k,v in x.items() if k!="base_xy"} for x in out],indent=2))
