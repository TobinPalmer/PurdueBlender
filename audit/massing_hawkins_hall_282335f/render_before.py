import bpy
from mathutils import Vector
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'
# center the camera on the extant massing in campus coordinates
cx,cy,cz=174.3,-509.4,21.3
camd=bpy.data.cameras.new('Hawkins audit preview camera'); cam=bpy.data.objects.new('Hawkins audit preview camera',camd); scene.collection.objects.link(cam)
cam.location=(cx-142,cy-128,92); target=Vector((cx,cy,20)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=52; scene.camera=cam
ld=bpy.data.lights.new('Hawkins audit softbox','AREA'); ld.energy=5500; ld.shape='DISK'; ld.size=90
light=bpy.data.objects.new('Hawkins audit softbox',ld); scene.collection.objects.link(light); light.location=(cx-48,cy-24,112); light.rotation_euler=(Vector((cx,cy,16))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.42,.5,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
scene.render.filepath='audit/massing_hawkins_hall_282335f/preview_before.png'
bpy.ops.render.render(write_still=True)
