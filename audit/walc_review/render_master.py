import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=bpy.context.scene
cd=bpy.data.cameras.new('WALC_Review');cam=bpy.data.objects.new('WALC_Review',cd);s.collection.objects.link(cam)
cam.location=(20,-10,650);cd.type='ORTHO';cd.ortho_scale=560;s.camera=cam
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True
s.render.resolution_x=1300;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.render.filepath=str(ROOT/'audit/walc_review/master_after_top.png')
bpy.ops.render.render(write_still=True)
missing=[lib.filepath for lib in bpy.data.libraries if not Path(bpy.path.abspath(lib.filepath)).exists()]
duplicates=['massing_potter_engineering_center_potr_89c4c33','massing_mechanical_engineering_me_8940174','massing_max_w_maileen_brown_family_hall_of_electrical_engineering_bhee_078fbfb','massing_house_1033674920_dcd3b76','massing_house_860822250_df21db0','massing_knoy_hall_knoy_f598616']
still=[a for a in duplicates if any(c.name=='Asset_'+a for c in s.collection.children)]
result={'missing_libraries':missing,'duplicate_collections_still_linked':still,'placement_instances':sum(o.instance_type=='COLLECTION' for o in s.objects),'scene_objects':len(s.objects)}
(ROOT/'audit/walc_review/master_reopen_check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
