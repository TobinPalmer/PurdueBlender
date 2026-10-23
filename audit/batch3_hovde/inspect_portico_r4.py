import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o and any(k in o.name for k in ['Portico','Classical_Column','Column_Base','Column_Capital']):print(o.name,'loc',tuple(round(x,3) for x in o.location),'dim',tuple(round(x,3) for x in o.dimensions),'rot',tuple(round(x,3) for x in o.rotation_euler),'world',tuple(round(x,3) for x in o.matrix_world.translation),'parent',o.parent.name if o.parent else '-')
