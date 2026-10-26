import bpy

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

print("EXISTING MATERIALS:")
for mat in bpy.data.materials:
    if any(k in mat.name for k in ["Brick", "Stone", "Concrete", "Glass", "Oak", "Terrazzo", "Carpet", "Bronze", "Gold", "Steel"]):
        print(f"  - {mat.name}")
