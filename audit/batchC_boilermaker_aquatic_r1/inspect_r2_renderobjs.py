import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
a=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
for o in a.all_objects:
 if any(k in o.name.lower() for k in ['roof','truss','purdue','sign','mezzanine','spectator','grandstand']): print(o.name, [c.name for c in o.users_collection],o.hide_render)
