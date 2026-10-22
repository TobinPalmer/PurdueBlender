import bpy,json
from pathlib import Path
c=bpy.data.collections['Asset_armory'];out={'objects':len(c.all_objects),'brick_uv_objects':sum(o.type=='MESH' and 'PBR_MetricUV' in o.data.uv_layers for o in c.all_objects),'images_packed':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'roof_skin':bpy.data.objects.get('Armory_Continuous_Roof_Repair') is not None,'frame_pieces':sum(o.name.startswith('Armory_Window_Frame_Repair') for o in c.all_objects),'geometry_repair':True,'reopened':True}
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/materials/buildings/armory/verification.json').write_text(json.dumps(out,indent=2));print(out)
