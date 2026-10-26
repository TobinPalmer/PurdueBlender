import bpy, math
from mathutils import Vector
from pathlib import Path
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(Path(bpy.data.filepath).parent.parent.parent/'audit'/'winifred_parker_hall'/'baseline_exterior.png')
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
scene.view_settings.exposure=0
scene.view_settings.gamma=1
world=bpy.data.worlds.new('WPH_AuditWorld') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.18,0.23,0.32,1); bg.inputs['Strength'].default_value=0.45
# Lighting and camera are temporary; file will not be saved.
def area(name,loc,power,size,color):
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
 o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
 o.rotation_euler=(Vector((-18,8,8))-o.location).to_track_quat('-Z','Y').to_euler()
area('Audit_Key',(30,-30,55),9000,35,(1,.82,.65))
area('Audit_Fill',(-45,20,35),5500,40,(.65,.78,1))
area('Audit_Rim',(5,65,45),7000,30,(1,.93,.79))
camd=bpy.data.cameras.new('AuditCam'); cam=bpy.data.objects.new('AuditCam',camd); scene.collection.objects.link(cam); scene.camera=cam
cam.location=(75,-88,64); target=Vector((-18,8,10)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=55
bpy.ops.render.render(write_still=True)
print('Wrote',scene.render.filepath)