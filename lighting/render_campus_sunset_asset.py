import bpy,importlib.util,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
MOD=P/'lighting'/'sunset_cloud_world.py'
spec=importlib.util.spec_from_file_location('sunset_cloud_world',MOD)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
s=bpy.context.scene
clouds,puffs=mod.install_campus_sunset(s,(-1800,1800,-1600,1600),spacing=520,seed=19)
# The standalone building preview uses a shorter camera-to-campus scale than
# the master map. Reframe this preview copy of the modeled cloud banks so the
# mesh silhouettes cross the actual camera frustum; master cloud coordinates
# and altitudes remain unchanged.
for v in clouds.data.vertices:
    x,y,z=v.co
    v.co=(-420+x*.35,500+y*.35,220+(z-390)*.27)
clouds.data.update()
bpy.context.view_layer.update();target=Vector((-7,17,70))
def camera(name,loc,aim=target):
 cd=bpy.data.cameras.new(name);co=bpy.data.objects.new(name,cd);s.collection.objects.link(co);co.location=loc;co.rotation_euler=(aim-co.location).to_track_quat('-Z','Y').to_euler();cd.lens=39;return co
cameras=[camera('SunsetCampusPreview_01',(70,-112,38)),camera('SunsetCampusPreview_02',(-900,179,40),Vector((-7,17,190)))]
# Add a second preview bank centered on the opposite camera direction. The
# master uses one campus-wide cloud field, but this small test scene is local.
west_clouds=clouds.copy();west_clouds.data=clouds.data.copy();west_clouds.name='Campus_Sunset_CloudBanks_WestPreview'
for v in west_clouds.data.vertices:
    x,y,z=v.co;v.co=(x+1292,y-645,z)
west_clouds.data.update();clouds.users_collection[0].objects.link(west_clouds)
mat=bpy.data.materials.new('Preview_Turf');mat.diffuse_color=(.12,.19,.105,1);mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.09,.145,.07,1);bs.inputs['Roughness'].default_value=.87
bpy.ops.mesh.primitive_plane_add(size=260,location=(0,0,-5.0));ground=bpy.context.object;ground.name='Preview_Campus_Ground';ground.data.materials.append(mat)
ld=bpy.data.lights.new('Preview_Camera_Fill','AREA');ld.energy=12000;ld.shape='DISK';ld.size=80;ld.color=(1.0,.68,.46)
fill=bpy.data.objects.new('Preview_Camera_Fill',ld);s.collection.objects.link(fill);fill.location=(65,-85,30);fill.rotation_euler=(Vector((-7,17,7))-fill.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=75;s.render.image_settings.file_format='PNG'
preview=P/'lighting'/'purdue_campus_sunset_preview.blend';s.camera=cameras[0];bpy.ops.wm.save_as_mainfile(filepath=str(preview))
for cam,name in zip(cameras,['sunset_cloud_preview.png','sunset_cloud_preview_west.png']):
 s.camera=cam;s.render.filepath=str(P/'lighting'/'renders'/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
print('META',json.dumps({'building_asset':'modular/buildings/hovde_hall.blend','camera_count':len(cameras),'world':s.world.name,'cloud_puffs':puffs,'bounds':[-1800,1800,-1600,1600],'time':s['campus_time']}),flush=True);bpy.ops.wm.quit_blender()
