import bpy
from mathutils import Vector
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.view_settings.exposure=-0.8
camd=bpy.data.cameras.new('MACK_SDAC_Facade_Study_Camera');cam=bpy.data.objects.new('MACK_SDAC_Facade_Study_Camera',camd);sc.collection.objects.link(cam)
target=Vector((46,80,7));cam.location=(95,30,31);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=88;camd.clip_end=500;sc.camera=cam
ld=bpy.data.lights.new('MACK_SDAC_Facade_Study_Sun','SUN');lo=bpy.data.objects.new('MACK_SDAC_Facade_Study_Sun',ld);sc.collection.objects.link(lo);ld.energy=1.1;lo.rotation_euler=(0.35,0.24,-0.5)
sc.world.color=(0.08,0.10,0.13)
sc.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\mackey_arena\after_facade_detail.png'
bpy.ops.render.render(write_still=True)
