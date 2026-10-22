import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parent
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.cycles.adaptive_threshold=0.06
s.render.resolution_x=1200;s.render.resolution_y=750
s.render.resolution_percentage=100
jobs=[('Cam_67_PMU_StateStreet_South_Hero','memorial_union_sunset.png'),('Cam_77_Hovde_South_Hero','hovde_hall_sunset.png'),('Cam_52_University_Hall_East_MemorialMall_StreetView','university_hall_sunset.png')]
for camera,file in jobs:
 s.camera=bpy.data.objects[camera];s.render.filepath=str(P/'renders'/file)
 bpy.ops.render.render(write_still=True)
 print('FINAL_RENDER_SAVED',file,flush=True)
s.camera=bpy.data.objects[jobs[0][0]]
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
(P/'renders'/'final_settings.json').write_text(json.dumps({'engine':s.render.engine,'time':s['campus_time'],'exposure':s.view_settings.exposure,'resolution':[1200,750],'samples':32,'denoising':True},indent=2))
