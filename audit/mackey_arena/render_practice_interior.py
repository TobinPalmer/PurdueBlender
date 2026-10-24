import bpy
from mathutils import Vector
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.view_settings.exposure=-1.0
sc.render.resolution_x=1280;sc.render.resolution_y=960;sc.render.resolution_percentage=100
# Hide the roof surfaces only in this render so the practice space can be inspected.
for obj in bpy.data.objects:
    if obj.name=='MACK_SDAC_Roof_Slab' or (obj.name.startswith('MACK_PERIM_') and obj.name.endswith('_Roof')):
        obj.hide_render=True
camd=bpy.data.cameras.new('MACK_Audit_InteriorCamera');cam=bpy.data.objects.new('MACK_Audit_InteriorCamera',camd);sc.collection.objects.link(cam)
cam.location=(56.5,108.0,4.2);target=Vector((37.0,88.5,5.1));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.lens=36;camd.clip_end=250;sc.camera=cam
ld=bpy.data.lights.new('MACK_Audit_Interior_Area','AREA');lo=bpy.data.objects.new('MACK_Audit_Interior_Area',ld);sc.collection.objects.link(lo);ld.energy=1700;ld.shape='DISK';ld.size=18;lo.location=(45,98,12);lo.rotation_euler=(Vector((44,96,1))-lo.location).to_track_quat('-Z','Y').to_euler()
ld2=bpy.data.lights.new('MACK_Audit_Interior_Fill','AREA');lo2=bpy.data.objects.new('MACK_Audit_Interior_Fill',ld2);sc.collection.objects.link(lo2);ld2.energy=900;ld2.shape='DISK';ld2.size=14;lo2.location=(30,75,10);lo2.rotation_euler=(Vector((35,83,2))-lo2.location).to_track_quat('-Z','Y').to_euler()
sc.world.color=(0.16,0.19,0.24)
sc.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\mackey_arena\after_practice_interior.png'
bpy.ops.render.render(write_still=True)
