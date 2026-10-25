import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
rows=[]
for o in bpy.data.objects:
 if any(k in o.name.lower() for k in ['window','glass_bay','clerestory','ribbon','vision','glazing']):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  rows.append({'n':o.name,'type':o.type,'min':[round(min(p[i] for p in pts),2) for i in range(3)],'max':[round(max(p[i] for p in pts),2) for i in range(3)],'mats':[m.name for m in o.data.materials if m] if o.type=='MESH' else []})
print(json.dumps(rows,indent=2))
