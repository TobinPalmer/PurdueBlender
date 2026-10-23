import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
for o in bpy.data.objects:
 o.hide_render=not o.name.startswith('POTR_2016_StairCore1_Level1') and not o.name.startswith('POTR_Evidence_')
ld=bpy.data.lights.new('POTR_Evidence_Stair_Key','AREA');lo=bpy.data.objects.new('POTR_Evidence_Stair_Key',ld);s.collection.objects.link(lo);lo.location=(48,-3,9);ld.energy=950;ld.shape='DISK';ld.size=5;lo.rotation_euler=(Vector((50,1,3))-lo.location).to_track_quat('-Z','Y').to_euler()
ld2=bpy.data.lights.new('POTR_Evidence_Stair_Fill','AREA');lo2=bpy.data.objects.new('POTR_Evidence_Stair_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(53,5,8);ld2.energy=550;ld2.size=4;lo2.rotation_euler=(Vector((50,1,3))-lo2.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('POTR_Evidence_Stair_Camera');cam=bpy.data.objects.new('POTR_Evidence_Stair_Camera',camd);s.collection.objects.link(cam);tar=Vector((50,1,3));cam.location=tar+Vector((5,-8,4));cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=9;s.camera=cam;s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=85;s.render.filepath=str(D/'stair_core_current.png');s.view_settings.exposure=-.55;bpy.ops.render.render(write_still=True)
