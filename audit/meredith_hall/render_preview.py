"""Render exterior and top-down evidence views of the saved Meredith asset."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'meredith_hall'
obj=bpy.data.objects['Meredith Hall']
center=Vector((-816.5,-121.0,7.5))
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=32
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(0.75,0.75,0.75)
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=-1.0
scene.view_settings.gamma=1

def aim(camera,target):
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
# Camera/light helpers are transient and are not saved back into the library.
def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; aim(ob,center); return ob
area('Audit_Key',(-760,-175,105),3000,75)
area('Audit_Fill',(-885,-50,65),1000,65)
camdata=bpy.data.cameras.new('Audit_Camera'); cam=bpy.data.objects.new('Audit_Camera',camdata); scene.collection.objects.link(cam); scene.camera=cam
camdata.type='ORTHO'; camdata.ortho_scale=150
cam.location=Vector((-680,-40,104)); aim(cam,center)
scene.render.filepath=str(AUDIT/'preview_exterior.png'); bpy.ops.render.render(write_still=True)
camdata.ortho_scale=135; cam.location=Vector((-816.5,-121.0,230)); aim(cam,(-816.5,-121.0,0))
scene.render.filepath=str(AUDIT/'preview_plan.png'); bpy.ops.render.render(write_still=True)




