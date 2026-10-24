import bpy
from mathutils import Vector
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.view_settings.exposure=-0.8
sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
camd=bpy.data.cameras.new('MACK_AuditCamera');cam=bpy.data.objects.new('MACK_AuditCamera',camd);sc.collection.objects.link(cam)
cam.location=(10,30,240);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=255;camd.clip_end=1000;sc.camera=cam
ld=bpy.data.lights.new('MACK_Audit_Sun','SUN');lo=bpy.data.objects.new('MACK_Audit_Sun',ld);sc.collection.objects.link(lo);ld.energy=2.3;lo.rotation_euler=(0.3,0.25,-0.5)
sc.world.color=(0.11,0.12,0.15)
sc.render.image_settings.file_format='PNG';sc.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\mackey_arena\after_top.png'
bpy.ops.render.render(write_still=True)

