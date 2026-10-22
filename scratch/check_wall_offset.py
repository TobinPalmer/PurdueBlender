import bpy

wall = bpy.data.objects.get("HIKS_Exterior_Masonry_Walls")
if wall:
    verts = [v.co for v in wall.data.vertices]
    # Check Z heights of wall verts
    zs = sorted(list(set(round(v.z, 4) for v in verts)))
    print("Wall Z levels:", zs)
    # Check min/max distance between inner and outer wall faces
    # For a corner, compare outer corner to inner corner
    p0_outer = min(verts, key=lambda v: (v.x - 72.699)**2 + (v.y - -308.547)**2)
    print("Outer corner near (72.699, -308.547):", p0_outer)
