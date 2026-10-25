import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
rows=[]
for o in bpy.data.objects:
 if 'Win_' in o.name or 'Window' in o.name:
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]; mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
  rows.append({'n':o.name,'min':[round(v,2) for v in mn],'max':[round(v,2) for v in mx],'mats':[m.name for m in o.data.materials if m]})
print(json.dumps(rows,indent=2))
