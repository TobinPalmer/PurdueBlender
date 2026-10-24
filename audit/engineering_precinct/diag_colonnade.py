import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'audit/engineering_precinct/engineering_mall_candidate_preview.blend')
cam=bpy.context.scene.camera
for o in bpy.data.objects:
 if 'Inferred_Hovde' in o.name:
  print(o.name,tuple(round(v,1) for v in o.location),tuple(round(v,3) for v in world_to_camera_view(bpy.context.scene,cam,o.matrix_world.translation)))
