import bpy
from pathlib import Path
from mathutils import Vector
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\horticulture_building.blend')
bpy.ops.wm.open_mainfile(filepath=str(p)); a=bpy.data.collections['Asset_horticulture_building']
for o in a.all_objects:
 if o.get('revision_batch')=='building_detail_revision_2026-10-24' and any(s in o.name.lower() for s in ['vestibule','walk','planter','entry name','lettering','sash window']):
  pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
  print(o.name,'loc',tuple(round(x,2) for x in o.location),'bounds',[(round(min(c[i] for c in pts),2),round(max(c[i] for c in pts),2)) for i in range(3)])
