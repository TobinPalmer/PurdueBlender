import bpy

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

print("=== SCENE OBJECT COUNTS ===")
print("Total objects in scene:", len(bpy.data.objects))
print("Total collections:", len(bpy.data.collections))

math_total = 0
for cname in ["60_Math_Sciences_Exterior", "61_Math_Sciences_Interiors", "62_Math_Sciences_Plaza_and_Site"]:
    col = bpy.data.collections.get(cname)
    if col:
        print(f"Collection {cname}: {len(col.objects)} objects")
        math_total += len(col.objects)

cams_col = bpy.data.collections.get("00_Inspection_Cameras")
print(f"Collection 00_Inspection_Cameras: {len(cams_col.objects)} objects")
print(f"Total Dedicated MATH Objects: {math_total} objects (+ 5 inspection cameras = {math_total + 5})")
