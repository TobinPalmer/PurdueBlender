import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'));c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if not o:continue
 o.hide_render=True
 include=o.name=='HOVD_Pres_Floor' or o.name.startswith(('HOVD_Pres_Desk_','HOVD_Pres_Lamp_','HOVD_Pres_Chair_','HOVD_Pres_Guest_','HOVD_Chesterfield_Chair_','HOVD_Pres_Rug','HOVD_Pres_Interpretive_','HOVD_Pres_Credenza_','HOVD_Pres_Bookcase_','HOVD_Pres_Book_Spine_','HOVD_Pres_Fireplace','HOVD_Pres_Firebox','HOVD_Pres_Embers','HOVD_Pres_Mantel_Clock'))
 if include and abs(o.location.x)<=5.6 and abs(o.location.y+25)<=5.7 and 3.3<=o.location.z<=8.4:o.hide_render=False
 if o.name=='HOVD_Pres_Floor':o.hide_render=False
print('root hide',bpy.data.objects['HOVD_Root'].hide_render)
for n in ['HOVD_Pres_Floor','HOVD_Pres_Desk_Top','HOVD_Pres_Chair_Seat','HOVD_Pres_Interpretive_Bookcase_Carcass','HOVD_Pres_Fireplace_Mantel']:
 o=bpy.data.objects[n];print(n,'hide',o.hide_render,'loc',tuple(o.location),'material',[m.name for m in o.data.materials])
