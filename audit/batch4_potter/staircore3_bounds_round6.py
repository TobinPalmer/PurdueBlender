import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
c=bpy.data.collections['Asset_potter_engineering'];rows=[]
for o in c.all_objects:
 if 'StairCore3_' in o.name and ('Level' in o.name or 'Basement' in o.name or '4S04' in o.name):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'loc':list(o.location),'bounds':[[round(min(p[i] for p in pts),4) for i in range(3)],[round(max(p[i] for p in pts),4) for i in range(3)]],'dims':[round(d,4) for d in o.dimensions]})
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter/staircore3_bounds_round6.json').write_text(json.dumps(rows,indent=2))
