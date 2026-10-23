import bpy,json
p=bpy.data.filepath;items=[]
for o in bpy.data.objects:
 if o.name.startswith('HAAS_Cupola_') and any(col.name=='Asset_felix_haas_hall' for col in o.users_collection):
  o.location.z-=3.7;items.append(o.name)
bpy.ops.wm.save_as_mainfile(filepath=p)
open('C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/cupola_fix.json','w').write(json.dumps({'shifted_export_cupola_objects':items,'vertical_delta_m':-3.7,'new_base_bottom_z_m':14.0,'height_status':'estimated alignment with hipped roof ridge'},indent=2))
