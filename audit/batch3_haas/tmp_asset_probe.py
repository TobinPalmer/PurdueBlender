import bpy
from mathutils import Vector
S=bpy.context.scene;C=bpy.data.collections['Asset_felix_haas_hall']
for o in bpy.data.objects:
 o.hide_render=not any(col==C for col in o.users_collection)
for n in ['probeTop2','probeCam2','HAAS_R9_Key','HAAS_R9_Fill','HAAS Round9 QA Camera']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new('qaTop','AREA');ld.energy=3000;ld.shape='DISK';ld.size=80;lo=bpy.data.objects.new('qaTop',ld);S.collection.objects.link(lo);lo.location=(0,0,80)
cd=bpy.data.cameras.new('qaCam');co=bpy.data.objects.new('qaCam',cd);S.collection.objects.link(co);cd.type='ORTHO';cd.ortho_scale=68;co.location=(-6,72,19);co.rotation_euler=(Vector((-6,0,5))-co.location).to_track_quat('-Z','Y').to_euler();S.camera=co;S.render.resolution_x=900;S.render.resolution_y=650;S.cycles.samples=4;S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/north_probe_asset.png';bpy.ops.render.render(write_still=True)
