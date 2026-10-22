"""Run in the live Blender Python session after installing the sky."""
import bpy, json, os, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders'
OUT.mkdir(exist_ok=True)
JOBS=[('Cam_67_PMU_StateStreet_South_Hero','memorial_union_sunset.png'),('Cam_77_Hovde_South_Hero','hovde_hall_sunset.png'),('Cam_52_University_Hall_East_MemorialMall_StreetView','university_hall_sunset.png')]
scene=bpy.context.scene
scene.render.resolution_x=1440
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.eevee.taa_render_samples=96
state={'status':'running','started':time.time(),'renders':[]}
def save_state():
 (OUT/'render_status.json').write_text(json.dumps(state,indent=2))
def render_next():
 try:
  i=len(state['renders'])
  if i>=len(JOBS):
   state['status']='complete';save_state();return None
  camera,filename=JOBS[i]
  scene.camera=bpy.data.objects[camera]
  scene.render.filepath=str(OUT/filename)
  bpy.ops.render.render(write_still=True)
  state['renders'].append({'camera':camera,'file':str(OUT/filename),'status':'saved'})
  save_state()
  return 1.0
 except Exception:
  state['status']='failed';state['error']=traceback.format_exc();save_state();return None
save_state()
bpy.app.timers.register(render_next,first_interval=2.0)
print('Scheduled three sunset building renders',str(OUT))
