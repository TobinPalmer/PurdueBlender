import bpy
from mathutils import Vector
scene=bpy.context.scene
from pathlib import Path
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_national_soil_erosion\nsel_revision_r2_hydraulics_cutaway.png')
allowed=('SOIL | R2 flume','SOIL | R2 overhead instrument','SOIL | R2 adjustable instrument','SOIL | R2 instrument gantry')
for o in bpy.data.objects:
 o.hide_render=not (o.name.startswith(allowed) or (o.type=='LIGHT' and o.name.startswith('SOIL Preview')))
print('visible',[(o.name,o.hide_render,[c.name for c in o.users_collection]) for o in bpy.data.objects if o.name.startswith(allowed)][:5])
data=bpy.data.cameras.new('testcam');cam=bpy.data.objects.new('testcam',data);scene.collection.objects.link(cam)
cam.location=(-45,-23,23);cam.rotation_euler=(Vector((-25.4,0,1.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=38;scene.camera=cam
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
bpy.context.view_layer.update()
scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
