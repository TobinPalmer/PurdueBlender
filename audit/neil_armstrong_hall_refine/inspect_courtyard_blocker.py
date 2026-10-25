import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
cam=Vector((-19.1,-14.9,1.7)); target=Vector((0,15,5))
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH': continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 mn=[min(p[i] for p in pts) for i in range(3)]; mx=[max(p[i] for p in pts) for i in range(3)]
 if mn[0]<cam.x+20 and mx[0]>cam.x-20 and mn[1]<target.y+10 and mx[1]>cam.y-10:
  mats=[m.name for m in o.data.materials if m]
  rows.append({'name':o.name,'min':[round(v,2) for v in mn],'max':[round(v,2) for v in mx],'mats':mats})
print(json.dumps(rows,indent=2))
