import bpy

print("--- ENTRANCE PAVILION DETAILS ---")
for name in ["HIKS_Entrance_Bronze_Framing", "HIKS_Entrance_Solar_Glazing", "HIKS_Entrance_Canopy_and_Piers", "HIKS_Entrance_Illuminated_Signage"]:
    obj = bpy.data.objects.get(name)
    if obj:
        print(f"\n{name}:")
        print(f"  Verts: {len(obj.data.vertices)}, Faces: {len(obj.data.polygons)}")
        zs = [v.co.z for v in obj.data.vertices]
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        print(f"  X: [{min(xs):.3f}, {max(xs):.3f}], Y: [{min(ys):.3f}, {max(ys):.3f}], Z: [{min(zs):.3f}, {max(zs):.3f}]")

