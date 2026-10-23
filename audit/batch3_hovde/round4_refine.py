import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');f=P/'modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections['Asset_hovde_hall']
# Tighten the portico across the facade and keep its six columns centered underneath.
for n,factor in [('HOVD_Portico_Entablature',.82),('HOVD_Portico_Cornice',.82),('HOVD_Portico_Pediment_Base',.90),('HOVD_Portico_Pediment_Crown',.82)]:
 o=bpy.data.objects[n];o.scale.x*=factor
yc=-.255
for i in range(1,7):
 for prefix in ['HOVD_Classical_Column_','HOVD_Column_Base_','HOVD_Column_Capital_','HOVD_Column_FluteCollar_Base_','HOVD_Column_FluteCollar_Capital_']:
  o=bpy.data.objects.get(prefix+str(i))
  if o:o.location.y=yc+(o.location.y-yc)*.82
# Keep executive records furniture clear of the office doorway.
for n,x in [('HOVD_Pres_Interpretive_Records_Credenza',-3.25),('HOVD_Pres_Credenza_Drawer_1',-3.68),('HOVD_Pres_Credenza_Drawer_2',-3.25),('HOVD_Pres_Credenza_Drawer_3',-2.82)]:
 o=bpy.data.objects[n];o.location.x=x
bpy.ops.wm.save_as_mainfile(filepath=str(f));print('narrowed portico stone panels and aligned support spacing; moved office credenza clear of entry')
