import bpy

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

print("="*60)
print("CAMPUS BUILDINGS MASSING OBJECTS:")
print("="*60)

massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
if massing_col:
    for obj in massing_col.objects:
        print(f"Name: {obj.name:40s} | Loc: ({obj.location.x:7.1f}, {obj.location.y:7.1f}, {obj.location.z:7.1f}) | Dim: ({obj.dimensions.x:6.1f}, {obj.dimensions.y:6.1f}, {obj.dimensions.z:6.1f})")
else:
    print("02_Campus_Buildings_Massing not found!")

print("\nALL COLLECTIONS:")
for c in bpy.data.collections:
    print(f"Collection: {c.name:45s} | Objects: {len(c.objects)}")
