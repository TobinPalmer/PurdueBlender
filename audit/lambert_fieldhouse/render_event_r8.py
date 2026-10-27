import bpy
from pathlib import Path
s=bpy.context.scene; cam=bpy.data.objects.get('LAMB | R8 event detail review camera');print('cam',cam.location[:],cam.rotation_euler[:]);s.camera=cam;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(Path('audit/lambert_fieldhouse/interior_event_round8.png').resolve());bpy.ops.render.render(write_still=True)
