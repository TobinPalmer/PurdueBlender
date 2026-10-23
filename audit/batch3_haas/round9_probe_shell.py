import bpy
from mathutils import Vector
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
S.render.engine='CYCLES';S.cycles.samples=4;S.render.resolution_x=1000;S.render.resolution_y=700;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-2.6
for o in C.objects:
 keep=o.name in ['HAAS_Corrected_GIS_Wall_Envelope','HAAS_Brick_Wall_East','HAAS_Brick_Wall_South','HAAS_Brick_Wall_West','HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']
 o.hide_render=not keep
ld=bpy.data.lights.new('probeTop','AREA');ld.energy=3000;ld.shape='DISK';ld.size=80;lo=bpy.data.objects.new('probeTop',ld);S.collection.objects.link(lo);lo.location=(0,0,80);lo.rotation_euler=(Vector((-6,0,5))-lo.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('probeCam');co=bpy.data.objects.new('probeCam',cd);S.collection.objects.link(co);cd.type='ORTHO';cd.ortho_scale=68;co.location=(-6,72,19);co.rotation_euler=(Vector((-6,0,5))-co.location).to_track_quat('-Z','Y').to_euler();S.camera=co;S.render.filepath='audit/batch3_haas/north_probe_shell.png';bpy.ops.render.render(write_still=True)
