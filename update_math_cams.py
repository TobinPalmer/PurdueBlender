"""
Test camera rotations for Cam_92, Cam_93, Cam_94, Cam_95, Cam_96
"""
import bpy
import math

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

cams = {
    "Cam_92_MATH_UniversitySt_Hero": ((-232.0, -135.0, 9.5), (math.radians(77), 0, math.radians(-68)), 20.0),
    "Cam_93_MATH_175_LectureHall_Interior": ((-185.62, -134.79, 3.6), (math.radians(105), 0, math.radians(180)), 19.0),
    "Cam_94_MATH_Library_Study_Interior": ((-187.12, -114.29, 12.6), (math.radians(76), 0, math.radians(-55)), 18.0),
    "Cam_95_MATH_10thFloor_SkyLounge_Interior": ((-185.12, -133.79, 31.2), (math.radians(75), 0, math.radians(-38)), 19.0),
    "Cam_96_MATH_Precinct_Aerial": ((-115.0, -210.0, 68.0), (math.radians(56), 0, math.radians(35)), 24.0)
}

for name, (loc, rot, lens) in cams.items():
    cam = bpy.data.objects.get(name)
    if cam:
        cam.location = loc
        cam.rotation_euler = rot
        cam.data.lens = lens
        print(f"Updated {name}: loc={loc}, rot={rot}, lens={lens}")

bpy.ops.wm.save_mainfile(filepath=blend_path)
print("Saved blend file with updated camera settings!")
