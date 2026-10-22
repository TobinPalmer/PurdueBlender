import bpy
import bmesh

wall = bpy.data.objects.get("HIKS_Exterior_Masonry_Walls")
if wall:
    bm = bmesh.new()
    bm.from_mesh(wall.data)
    print("Exterior Masonry Walls:")
    print("  Verts:", len(bm.verts))
    print("  Faces:", len(bm.faces))
    # Check wall thickness: find pairs of parallel faces or distance between outer and inner vertices
    verts = [v.co for v in bm.verts]
    xs = sorted(list(set(round(v.x, 3) for v in verts)))
    print("  Distinct X coords:", len(xs), xs[:10])
    # check faces
    print("  Face normals summary:")
    normals = [tuple(round(c, 2) for c in f.normal) for f in bm.faces]
    for n in set(normals):
        print(f"    Normal {n}: count {normals.count(n)}")
    bm.free()
