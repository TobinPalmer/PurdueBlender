import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
c=bpy.data.collections['Asset_elliott_hall_of_music']
for n in ['ELLT_B3_stage','ELLT_Official_Footprint_Exterior_Walls','ELLT_Official_Footprint_Roof_Estimated_22_5m']:
 o=bpy.data.objects[n]; vs=[o.matrix_world@Vector(v) for v in o.bound_box]
 print(n,'bbox',[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)],'center',tuple(round(sum(v[i] for v in vs)/8,2) for i in range(3)))
