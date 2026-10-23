import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
s=bpy.context.scene
s.render.engine='BLENDER_WORKBENCH'
s.display.shading.light='STUDIO'
s.display.shading.color_type='MATERIAL'
s.display.shading.show_shadows=True
s.view_settings.view_transform='Standard'
s.view_settings.exposure=0
s.view_settings.gamma=1
s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100
cd=bpy.data.cameras.new('CompletionReview');cam=bpy.data.objects.new('CompletionReview',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO'
for bid in ['elliott_hall_of_music','felix_haas_hall','math_sciences','hovde_hall','stanley_coulter_hall']:
    marker=bpy.data.objects['Placement_'+bid]
    target=Vector((marker.location.x,marker.location.y,7))
    cam.location=target+Vector((110,-140,130));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=180
    s.render.filepath=str(ROOT/'audit/batch3_master'/f'{bid}_assembled.png')
    bpy.ops.render.render(write_still=True)
cam.location=(20,-10,650);cam.rotation_euler=(0,0,0);cd.ortho_scale=560
s.render.filepath=str(ROOT/'audit/batch3_master/overview.png');bpy.ops.render.render(write_still=True)
# Review cameras/settings are temporary, never save them into the master.

