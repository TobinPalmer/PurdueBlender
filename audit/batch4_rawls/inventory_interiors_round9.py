import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).with_name('rawls_hall_r9_candidate.blend')))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ('floor','slab','atrium','stair','rail','desk','chair','plan1086','plan1054')):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  rows.append({'name':o.name,'bounds':[[round(min(p[i] for p in pts),2),round(max(p[i] for p in pts),2)] for i in range(3)],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'hide_render':o.hide_render})
print(json.dumps(rows,indent=2))
