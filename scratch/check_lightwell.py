import bpy

obj = bpy.data.objects.get("HIKS_Sunken_Lightwells_Retaining")
if obj:
    print("HIKS_Sunken_Lightwells_Retaining:")
    print("  Verts:", len(obj.data.vertices))
    for v in obj.data.vertices:
        print("   ", v.co)
    print("  Faces:", len(obj.data.polygons))
    for f in obj.data.polygons:
        print("    Face verts:", list(f.vertices))
