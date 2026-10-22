"""Build the sunset copy and render previews without overwriting the open project."""
import bpy,json,sys,importlib.util,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
spec=importlib.util.spec_from_file_location('campus_time',ROOT/'campus_time.py')
sky=importlib.util.module_from_spec(spec);spec.loader.exec_module(sky)
sky.build_sky()
scene=bpy.context.scene
scene['campus_time']=18.0
scene.frame_set(scene.frame_current)
scene.render.resolution_x=1440;scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.eevee.taa_render_samples=96
OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
jobs=[('Cam_67_PMU_StateStreet_South_Hero','memorial_union_sunset.png'),('Cam_77_Hovde_South_Hero','hovde_hall_sunset.png'),('Cam_52_University_Hall_East_MemorialMall_StreetView','university_hall_sunset.png')]
state={'status':'rendering','time':18,'renders':[]}
scene.camera=bpy.data.objects[jobs[0][0]]
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'purdue_campus_sunset.blend'))
for camera,file in jobs:
 scene.camera=bpy.data.objects[camera];scene.render.filepath=str(OUT/file)
 bpy.ops.render.render(write_still=True)
 state['renders'].append({'camera':camera,'file':str(OUT/file),'status':'saved'})
 (OUT/'render_status.json').write_text(json.dumps(state,indent=2))
 print('SUNSET_RENDER_SAVED',file,flush=True)
state['status']='complete';(OUT/'render_status.json').write_text(json.dumps(state,indent=2))
scene.camera=bpy.data.objects[jobs[0][0]]
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'purdue_campus_sunset.blend'))
