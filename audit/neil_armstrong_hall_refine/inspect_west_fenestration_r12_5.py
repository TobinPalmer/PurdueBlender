import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]; mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
 if mn[0]<-8 and mx[0]>-64 and mn[1]<-2 and mx[1]>-5 and mn[2]<21 and mx[2]>2:
  rows.append({'n':o.name,'min':[round(v,2) for v in mn],'max':[round(v,2) for v in mx],'mats':[m.name for m in o.data.materials if m]})
print(json.dumps(rows,indent=2))
