import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
 if mn[0]<5 and mx[0]>-35 and mn[1]<20 and mx[1]>-20 and mn[2]<18 and mx[2]>0 and ('wall' in o.name.lower() or any(m and ('glass' in m.name.lower() or 'blue' in m.name.lower() or 'curtain' in m.name.lower()) for m in o.data.materials)):
  rows.append({'n':o.name,'min':[round(x,2) for x in mn],'max':[round(x,2) for x in mx],'mats':[m.name for m in o.data.materials if m]})
print(json.dumps(rows,indent=2))
