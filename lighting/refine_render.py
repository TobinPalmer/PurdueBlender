import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE'
s.view_settings.exposure=-0.65
s.eevee.shadow_resolution_scale=0.25
if hasattr(s.eevee,'light_threshold'):s.eevee.light_threshold=0.1
fill=bpy.data.objects.get('Campus Twilight Fill')
if fill:fill.data.use_shadow=False
opts={i.identifier for i in s.eevee.bl_rna.properties['shadow_pool_size'].enum_items}
if '512' in opts:s.eevee.shadow_pool_size='512'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.use_scene_world=True
   area.spaces.active.shading.use_scene_lights=True
jobs=[('Cam_67_PMU_StateStreet_South_Hero','memorial_union_sunset.png'),('Cam_77_Hovde_South_Hero','hovde_hall_sunset.png'),('Cam_52_University_Hall_East_MemorialMall_StreetView','university_hall_sunset.png')]
for camera,file in jobs:
 s.camera=bpy.data.objects[camera];s.render.filepath=str(P/'renders'/file)
 bpy.ops.render.render(write_still=True)
 print('REFINED_RENDER_SAVED',file,flush=True)
s.camera=bpy.data.objects[jobs[0][0]]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
(P/'renders'/'final_settings.json').write_text(json.dumps({'time':s['campus_time'],'exposure':s.view_settings.exposure,'shadow_pool_mb':s.eevee.shadow_pool_size,'resolution':[s.render.resolution_x,s.render.resolution_y]},indent=2))
