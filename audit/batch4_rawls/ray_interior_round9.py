import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass'];rows=[]
for p in g.data.polygons:
 pts=[g.matrix_world@g.data.vertices[i].co for i in p.vertices];c=sum(pts,Vector())/len(pts);n=(g.matrix_world.to_3x3()@p.normal).normalized();start=c-n*.2;hit,loc,norm,fi,o,ma=s.ray_cast(dg,start,-n,distance=30);rows.append({'poly':p.index,'center':[round(v,2) for v in c],'hit':o.name if o else None,'distance':round((loc-start).length,2) if hit else None,'hit_loc':[round(v,2) for v in loc] if hit else None})
print(json.dumps(rows,indent=2))
