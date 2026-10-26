import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/rawls_hall.blend'
OUT=Path(__file__).with_name('round9_south_inventory.json')
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 b=bounds(o)
 # either south window related, or overlaps y=-24-ish and main dimensions
 if 'South' in o.name or (b[1][0] < -19 and b[1][1]>-26 and b[0][0] > -25 and b[0][1]<30 and b[2][1]>1):
  rows.append({'name':o.name,'bounds':b,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':sorted({s.material.name for s in o.material_slots if s.material})})
OUT.write_text(json.dumps(rows,indent=2))
print(len(rows),OUT)
