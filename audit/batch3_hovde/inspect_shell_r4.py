import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and o.type=='MESH' and ('Wall_' in o.name or 'Portico' in o.name):print(o.name,tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions),tuple(round(x,2) for x in o.matrix_world.translation))
