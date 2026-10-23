import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall'];factor=.72*.70
for o in c.all_objects:
 if not o:continue
 related=o.name.startswith('HOVD_Pres_') or o.name.startswith('HOVD_Board_') or o.name.startswith('HOVD_Chair_') or o.name.startswith('HOVD_Chesterfield_Chair_')
 if not related:continue
 o.location.z=4.4+(o.location.z-4.4)/factor
 if o.type=='MESH':o.scale.z/=factor
 elif o.type=='LIGHT':o.data.energy/=factor
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('restored full room/story heights while retaining compact plan')
