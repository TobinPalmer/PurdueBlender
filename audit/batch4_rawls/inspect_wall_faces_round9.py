import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/rawls_hall.blend'));w=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];rows=[]
for i in [74,75]:
 p=w.data.polygons[i];pts=[w.matrix_world@w.data.vertices[j].co for j in p.vertices];rows.append({'face':i,'indices':list(p.vertices),'normal':list((w.matrix_world.to_3x3()@p.normal).normalized()),'vertices':[[round(v,4) for v in q] for q in pts]})
print(json.dumps(rows,indent=2))
