import bpy,json
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if any(t in o.name.lower() for t in ['port','column','roof','pres_','board','stair','pediment','win']):
  print(o.name,o.type,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions), [m.name for m in o.data.materials] if o.type=='MESH' else '')
