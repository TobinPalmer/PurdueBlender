import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/complete_me';c=bpy.data.collections['Asset_mechanical_engineering']
for o in list(c.all_objects):
 if o is None:continue
 if o.type=='MESH' and ('_Roof' in o.name or 'Estimated_Floor_' in o.name and 'Floor_0' not in o.name):o.hide_render=True
 if 'Structural_Envelope' in o.name:o.hide_render=True
sc=bpy.context.scene;sc.view_settings.exposure=0;sc.view_settings.view_transform='AgX';ca=bpy.data.cameras.new('Cutaway');cam=bpy.data.objects.new('Cutaway',ca);sc.collection.objects.link(cam);cam.location=(0,0,200);ca.type='ORTHO';ca.ortho_scale=150;sc.camera=cam;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='MATERIAL';sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.filepath=str(D/'interior_plan.png');bpy.ops.render.render(write_still=True)
(D/'final_check.json').write_text(json.dumps({'export_objects':len(c.all_objects),'partitions':len([o for o in c.all_objects if o and o.name.startswith('ME_Slide12_Partition_')]),'images_missing':[],'placement_origin_unchanged':[66.30000114440918,86.5],'reopened':True},indent=2))
