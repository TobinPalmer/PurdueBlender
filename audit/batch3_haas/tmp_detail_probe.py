import bpy
from mathutils import Vector
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
S.render.engine='CYCLES';S.cycles.samples=4;S.render.resolution_x=900;S.render.resolution_y=650;S.render.resolution_percentage=100
for o in C.objects:
 o.hide_render=o.name in ['HAAS_Corrected_GIS_Wall_Envelope','HAAS_Brick_Wall_East','HAAS_Brick_Wall_South','HAAS_Brick_Wall_West','HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']
for n in ['HAAS_R9_Key','HAAS_R9_Fill','HAAS Round9 QA Camera']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new('probeTop2','AREA');ld.energy=3000;ld.shape='DISK';ld.size=80;lo=bpy.data.objects.new('probeTop2',ld);S.collection.objects.link(lo);lo.location=(0,0,80)
cd=bpy.data.cameras.new('probeCam2');co=bpy.data.objects.new('probeCam2',cd);S.collection.objects.link(co);cd.type='ORTHO';cd.ortho_scale=68;co.location=(-6,72,19);co.rotation_euler=(Vector((-6,0,5))-co.location).to_track_quat('-Z','Y').to_euler();S.camera=co;S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/north_probe_details.png';bpy.ops.render.render(write_still=True)
