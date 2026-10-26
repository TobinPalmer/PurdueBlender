import bpy
from mathutils import Vector
from pathlib import Path
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(Path(bpy.data.filepath).parent/'gis_shell_exterior.png')
scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'
world=bpy.data.worlds.new('WPH_GIS_AuditWorld') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.18,0.23,0.32,1); bg.inputs['Strength'].default_value=.45
def area(name,loc,power,size,color):
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
 o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
 o.rotation_euler=(Vector((-18,8,8))-o.location).to_track_quat('-Z','Y').to_euler()
area('Audit_Key',(30,-30,55),9000,35,(1,.82,.65)); area('Audit_Fill',(-45,20,35),5500,40,(.65,.78,1)); area('Audit_Rim',(5,65,45),7000,30,(1,.93,.79))
camd=bpy.data.cameras.new('AuditCam'); cam=bpy.data.objects.new('AuditCam',camd); scene.collection.objects.link(cam); scene.camera=cam
cam.location=(75,-88,64); cam.rotation_euler=(Vector((-18,8,10))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=55
bpy.ops.render.render(write_still=True)
print('Wrote',scene.render.filepath)
