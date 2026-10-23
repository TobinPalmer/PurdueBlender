import bpy, json, math
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend')
bpy.ops.wm.open_mainfile(filepath=str(P)); c=bpy.data.collections['Asset_potter_engineering']
res=[]
for o in c.all_objects:
 if any(t in o.name for t in ['Level3_Flight','Level3_UpperLanding','Penthouse_Landing','Room401_Penthouse_Massing','Room401A','4S04_Enclosure','Official_864_Roof']):
  bb=[o.matrix_world@__import__('mathutils').Vector(corner) for corner in o.bound_box]
  res.append({'name':o.name,'bounds':[[round(min(v[i] for v in bb),3) for i in range(3)],[round(max(v[i] for v in bb),3) for i in range(3)]],'hide_render':o.hide_render})
print(json.dumps(res,indent=2))
