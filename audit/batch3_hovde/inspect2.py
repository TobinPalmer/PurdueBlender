import bpy
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if 'Portico' in o.name or 'Col' in o.name or 'Roof' in o.name or o.name.startswith('HOVD_Pres_') or o.name.startswith('HOVD_Board_'):
  print(o.name,o.type,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions))
