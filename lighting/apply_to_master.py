"""Apply to the latest saved master, retaining a backup and guarding concurrent edits."""
import bpy,shutil,hashlib,sys,json
from pathlib import Path
P=Path(__file__).resolve().parent
target=Path(bpy.data.filepath)
expected=(P/'master_baseline.sha256').read_text().strip()
def digest():return hashlib.sha256(target.read_bytes()).hexdigest().upper()
if digest()!=expected:raise RuntimeError('Master changed since task began; not overwriting newer edits')
shutil.copy2(target,P/'master_before_final_sunset.blend')
addons=Path(bpy.utils.user_resource('SCRIPTS',path='addons',create=True))
shutil.copy2(P/'campus_time.py',addons/'campus_time.py')
sys.path.insert(0,str(addons))
import addon_utils
addon_utils.enable('campus_time',default_set=True,persistent=True)
import campus_time
campus_time.build_sky()
s=bpy.context.scene
s['campus_time']=18.;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
s.eevee.shadow_resolution_scale=.25
if hasattr(s.eevee,'light_threshold'):s.eevee.light_threshold=.1
bpy.data.objects['Campus Twilight Fill'].data.use_shadow=False
s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100
s.eevee.taa_render_samples=96
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.use_scene_world=True
   area.spaces.active.shading.use_scene_lights=True
if digest()!=expected:raise RuntimeError('Master changed during lighting setup; preserving newer file')
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.wm.save_userpref()
(P/'master_applied.json').write_text(json.dumps({'file':str(target),'default_time':s['campus_time'],'backup':str(P/'master_before_final_sunset.blend'),'addon':str(addons/'campus_time.py')},indent=2))
print('MASTER_SUNSET_APPLIED',str(target),flush=True)
