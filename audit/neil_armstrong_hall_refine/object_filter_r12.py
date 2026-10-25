import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
rows=[]
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['roof','canopy','wing','atrium','entrance','glass']):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box] if False else [o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
  rows.append({'n':o.name,'type':o.type,'min':[round(min(p[i] for p in pts),2) for i in range(3)],'max':[round(max(p[i] for p in pts),2) for i in range(3)],'parent':o.parent.name if o.parent else None})
print(json.dumps(rows,indent=2))
