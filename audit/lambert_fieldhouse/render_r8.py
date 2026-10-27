import bpy,json
from pathlib import Path
scene=bpy.context.scene
if scene.camera is None: raise RuntimeError('No saved scene camera')
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
for name,out in [('LAMB | three-quarter preview camera','audit/lambert_fieldhouse/exterior_round8.png'),('LAMB | interior review camera','audit/lambert_fieldhouse/interior_round8.png')]:
 cam=bpy.data.objects.get(name)
 if cam is None: continue
 scene.camera=cam;scene.render.filepath=str(Path(out).resolve());bpy.ops.render.render(write_still=True);print('rendered',out)
