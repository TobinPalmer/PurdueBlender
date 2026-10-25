import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\purdue_memorial_union_independent_grade\structural_bounds.json')
bpy.ops.wm.open_mainfile(filepath=str(asset)); col=bpy.data.collections['Asset_purdue_memorial_union']
rows=[]
for o in col.all_objects:
 if any(t in o.name for t in ('PMU_Base','PMU_Wall','PMU_Roof','EastWing_Wall','WestWing_Wall','Tower_Wall','EastWing_Roof')):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  rows.append({'name':o.name,'type':o.type,'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]})
out.write_text(json.dumps({'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'structural_objects':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))
