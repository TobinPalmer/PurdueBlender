import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
c=bpy.data.collections['Asset_potter_engineering']
rows=[]
for o in c.objects:
 if any(k in o.name for k in ('Plan53','Plan54','Plan55','StairCore','Interior_Slab','Roof','Penthouse')):
  co=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'type':o.type,'loc':list(o.location),'dims':list(o.dimensions),'bounds':[[min(p[i] for p in co) for i in range(3)],[max(p[i] for p in co) for i in range(3)]]})
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter/inventory_interior.json').write_text(json.dumps(rows,indent=2))
