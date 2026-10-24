import bpy
from mathutils import Vector
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1280;sc.render.resolution_y=960;sc.render.resolution_percentage=100
sc.view_settings.exposure=-0.8
camd=bpy.data.cameras.new('MACK_Audit_ObliqueCamera');cam=bpy.data.objects.new('MACK_Audit_ObliqueCamera',camd);sc.collection.objects.link(cam)
target=Vector((12,22,7));cam.location=(155,143,100);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=205;camd.clip_end=1000;sc.camera=cam
ld=bpy.data.lights.new('MACK_Audit_Oblique_Sun','SUN');lo=bpy.data.objects.new('MACK_Audit_Oblique_Sun',ld);sc.collection.objects.link(lo);ld.energy=1.1;lo.rotation_euler=(0.35,0.24,-0.5)
sc.world.color=(0.08,0.10,0.13)
sc.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\mackey_arena\after_oblique.png'
bpy.ops.render.render(write_still=True)
