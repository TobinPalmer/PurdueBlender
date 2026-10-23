import bpy
from mathutils import Vector

cam = bpy.data.objects.get('Cam_07_Wiley_Hall_StreetView')
print("Cam Wiley:", cam.location, cam.rotation_euler, cam.data.lens, cam.data.sensor_width)

# Find Wiley objects
wiley_objs = [o for o in bpy.data.objects if 'wiley' in o.name.lower()]
print(f"Wiley objects count: {len(wiley_objs)}")
for o in wiley_objs[:10]:
    print(f"  {o.name}: loc={o.matrix_world.translation}")

# Find trees around Wiley
trees = [o for o in bpy.data.objects if 'tree' in o.name.lower() and (-700 < o.matrix_world.translation.x < -500) and (50 < o.matrix_world.translation.y < 250)]
print(f"Trees near Wiley: {len(trees)}")
