import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall']
for ob in c.all_objects:
 if not ob:continue
 if ob.name.startswith('HOVD_Chair_'):
  fac=.72;ob.location.x*=fac;ob.location.y=25+(ob.location.y-25)*fac;ob.location.z=4.4+(ob.location.z-4.4)*fac
  if ob.type=='MESH':ob.scale*=fac
 if ob.name.startswith('HOVD_Chesterfield_Chair_'):
  fac=.72;ob.location.x*=fac;ob.location.y=-25+(ob.location.y+25)*fac;ob.location.z=4.4+(ob.location.z-4.4)*fac
  if ob.type=='MESH':ob.scale*=fac
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('scaled unprefixed board and guest chair objects')
