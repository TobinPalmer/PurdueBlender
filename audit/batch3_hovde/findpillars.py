import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if o.type=='MESH' and o.dimensions.z>4 and o.dimensions.x<2 and o.dimensions.y<2: print(o.name,o.location[:],o.dimensions[:])
