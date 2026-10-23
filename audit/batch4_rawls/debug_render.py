import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
s=bpy.context.scene
cam=bpy.data.objects.new('debugcam',bpy.data.cameras.new('debugcam'));s.collection.objects.link(cam);s.camera=cam
cam.location=(42.8,6.2,1.68);cam.rotation_euler=(Vector((30.3,-2.8,1.55))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43
prefixes=("RAWL_Masonry_Exterior_Walls","RAWL_Basement_Foundation_Walls","RAWL_Limestone_Base_Plinth","RAWL_Limestone_BeltCourse","RAWL_Limestone_Parapet","RAWL_NW_Rotunda","RAWL_North_Windows","RAWL_SE_Diagonal","RAWL_South_Windows","RAWL_West_Windows","RAWL_East_Windows","RAWL_Roof","RAWL_Rooftop","RAWL_Site_Sidewalk_Apron")
for o in bpy.data.objects:
 if o.name.startswith(prefixes) or (o.name.startswith('RAWL_FloorSlab_L') and o.name!='RAWL_FloorSlab_L1_Ground'):
  o.hide_render=True
print('CAM',tuple(cam.location),tuple(cam.rotation_euler))
for n in ['RAWL_FloorSlab_L1_Ground','RAWL_2026_1086_Desk','RAWL_2026_DeskLeg','RAWL_2026_Plan1086_00_00','RAWL_2026_Plan1086_Jamb_05_A']:
 o=bpy.data.objects.get(n)
 if o:print('OBJ',n,'hide',o.hide_render,'bboxworld',[list(o.matrix_world@Vector(c)) for c in o.bound_box[:2]],'proj',tuple(round(v,3) for v in world_to_camera_view(s,cam,o.matrix_world.translation)))
print('VIS',[(o.name,o.hide_render) for o in bpy.data.objects if o.name.startswith('RAWL_2026_Plan1086')][:20])
