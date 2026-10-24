import bpy, importlib.util, json, os
from pathlib import Path
P=Path(__file__).resolve().parent.parent
MOD=P/'lighting'/'campus_time.py'
spec=importlib.util.spec_from_file_location('campus_time_preview',MOD)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
mod.build_sky()
s=bpy.context.scene
camera_name='Cam_77_Hovde_South_Hero'
camera=bpy.data.objects.get(camera_name)
if camera is None: camera=next(o for o in bpy.data.objects if o.type=='CAMERA')
keep={camera}
for name in ('Placement_hovde_hall','Campus Sunset Sun','Campus Twilight Fill'):
    ob=bpy.data.objects.get(name)
    if ob: keep.add(ob)
site=bpy.data.collections.get('Asset_campus_site')
if site: keep.update(site.all_objects)
hidden=0
for ob in bpy.data.objects:
    if ob not in keep:
        ob.hide_render=True; hidden+=1
s['campus_time']=18.0; s.frame_set(s.frame_current); bpy.context.view_layer.update()
s.camera=camera
s.render.engine='BLENDER_EEVEE'
s.render.resolution_x=1440; s.render.resolution_y=900; s.render.resolution_percentage=48
s.render.image_settings.file_format='PNG'; s.render.filepath=str(P/'lighting'/'renders'/'sunset_cloud_preview.png')
s.eevee.taa_render_samples=8
s.view_settings.exposure=-0.45
print('PREVIEW_META',json.dumps({'camera':camera.name,'objects':len(bpy.data.objects),'hidden':hidden,'site_objects':len(site.all_objects) if site else 0,'world':s.world.name,'libraries':len(bpy.data.libraries),'missing':[l.filepath for l in bpy.data.libraries if not os.path.exists(bpy.path.abspath(l.filepath))]}),flush=True)
bpy.ops.render.render(write_still=True)
print('PREVIEW_RENDER_DONE',s.render.filepath,flush=True)
bpy.ops.wm.quit_blender()
