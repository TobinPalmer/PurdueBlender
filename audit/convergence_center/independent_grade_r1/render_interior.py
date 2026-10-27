import bpy
from mathutils import Vector
from pathlib import Path
out=Path(__file__).with_name('interior_detail_independent_2.png')
scene=bpy.context.scene
camd=bpy.data.cameras.new('Independent interior review camera'); cam=bpy.data.objects.new('Independent interior review camera',camd); scene.collection.objects.link(cam)
camd.lens=38
cam.location=Vector((5.0,10.5,2.5)); target=Vector((-13.0,11.6,2.5)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); scene.camera=cam
scene.render.resolution_x=1000; scene.render.resolution_y=700; scene.render.resolution_percentage=100; scene.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
print(out)

